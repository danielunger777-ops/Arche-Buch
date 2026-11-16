"""
build_botany_atlas.py — Master-Textur-Generator für das ARCHE Botanik-Wald-Kit
===============================================================================
Erzeugt zwei gemeinsame 1024x1024 PBR-Textur-Sets (ohne eingebackene Schlagschatten,
HDR-Albedo strikt in [0.05, 0.68], Cycles CUDA auf GTX 1070 mit CPU-Fallback):

1. assets/textures/botany_bark_trim_{baseColor,normal,orm}.png
   - 6 vertikale Streifen (je 1/6 Breite, vertikal nahtlos kachelnd):
     0: Libanon-Zeder (cedar)
     1: Mittelmeer-Zypresse (cypress)
     2: Orientalische Eiche (oak)
     3: Hainbuche (hornbeam)
     4: Dattelpalme (palm — faserige Diamant-Blattnarben!)
     5: Schirmakazie (acacia — inkl. leicht bemooster Wurzelbasis bei V < 0.20)

2. assets/textures/botany_leaf_atlas_{baseColor,normal,orm,thickness}.png
   - 4x3 Raster (12 Zellen: 6 Arten x [Jungtrieb, Alttrieb]) aus echter 3D-Zweiggeometrie:
     Reihe 0: cedar_young, cedar_mature, cypress_young, cypress_mature
     Reihe 1: oak_young, oak_mature, hornbeam_young, hornbeam_mature
     Reihe 2: palm_young, palm_mature, acacia_young, acacia_mature

Ausführung:
  blender --background --python assets/scripts/build_botany_atlas.py
"""

import os
import sys
import math
import time
import random
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix


def get_project_root():
    if "__file__" in globals():
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.getcwd()


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    return scene


def setup_cycles(scene, samples=4):
    try:
        engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    except Exception:
        engines = []
    if "CYCLES" not in engines:
        import addon_utils
        try:
            addon_utils.enable("cycles", default_set=False, persistent=False)
        except Exception:
            pass

    scene.render.engine = "CYCLES"
    used_gpu = False
    if hasattr(scene, "cycles"):
        try:
            prefs = bpy.context.preferences.addons["cycles"].preferences
            prefs.compute_device_type = "CUDA"
            prefs.refresh_devices()
            cuda_devs = [d for d in prefs.devices if d.type == "CUDA"]
            if cuda_devs:
                for d in prefs.devices:
                    d.use = (d.type == "CUDA")
                scene.cycles.device = "GPU"
                used_gpu = True
        except Exception:
            used_gpu = False
        if not used_gpu:
            scene.cycles.device = "CPU"
        scene.cycles.samples = samples
        scene.cycles.use_denoising = False
        scene.cycles.max_bounces = 2
        scene.cycles.diffuse_bounces = 1
        scene.cycles.glossy_bounces = 0
        scene.cycles.transparent_max_bounces = 8

    # Neutrales Farbmanagement ohne Kontrast-Verfälschung für Textur-Bakes
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    return "CUDA (GPU)" if used_gpu else "CPU"


def clamp_hdr_albedo(rgb, lo=0.05, hi=0.68):
    return (
        max(lo, min(hi, float(rgb[0]))),
        max(lo, min(hi, float(rgb[1]))),
        max(lo, min(hi, float(rgb[2]))),
    )


def _mix_rgba(nt, fac=None, col_a=None, col_b=None):
    """Blender 4/5-sicherer RGBA-Mix (waehlt explizit die RGBA-Sockets statt gleichnamiger Float-Sockets)."""
    node = nt.nodes.new("ShaderNodeMix")
    node.data_type = "RGBA"
    rgba_ins = [s for s in node.inputs if s.type == "RGBA"]
    rgba_outs = [s for s in node.outputs if s.type == "RGBA"]
    fac_in = node.inputs[0]
    in_a, in_b = rgba_ins[0], rgba_ins[1]
    out_c = rgba_outs[0]
    if fac is not None:
        if isinstance(fac, (int, float)):
            fac_in.default_value = float(fac)
        else:
            nt.links.new(fac, fac_in)
    if col_a is not None:
        if isinstance(col_a, tuple):
            in_a.default_value = col_a if len(col_a) == 4 else (*col_a, 1.0)
        else:
            nt.links.new(col_a, in_a)
    if col_b is not None:
        if isinstance(col_b, tuple):
            in_b.default_value = col_b if len(col_b) == 4 else (*col_b, 1.0)
        else:
            nt.links.new(col_b, in_b)
    return node, out_c


def save_image(img, filepath, colorspace="sRGB", is_rgba=False):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.colorspace_settings.name = colorspace
    img.filepath_raw = filepath
    img.file_format = "PNG"
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.image_settings.color_mode = "RGBA" if is_rgba else "RGB"
    bpy.context.scene.render.image_settings.color_depth = "8"
    img.save()


# ==============================================================================
# 1. BARK TRIM SHEET (10 vertikale Streifen, 2048x1024, vertikal nahtlos)
# ==============================================================================
BARK_SPECS = [
    # (name, col_dark, col_light, col_crevice, scale_u, scale_v, ridge_freq, roughness, bump_strength, mode)
    ("cedar",     (0.16, 0.09, 0.06), (0.38, 0.23, 0.14), (0.09, 0.05, 0.03), 18.0, 5.0,  14.0, 0.84, 0.42, "PLATE"),
    ("cypress",   (0.18, 0.15, 0.12), (0.36, 0.31, 0.26), (0.10, 0.08, 0.07), 24.0, 4.0,  22.0, 0.86, 0.36, "FIBROUS"),
    ("oak",       (0.13, 0.10, 0.07), (0.31, 0.24, 0.18), (0.07, 0.05, 0.04), 15.0, 4.5,  12.0, 0.90, 0.52, "FISSURE"),
    ("hornbeam",  (0.28, 0.27, 0.24), (0.48, 0.46, 0.41), (0.19, 0.18, 0.16), 12.0, 3.0,   8.0, 0.72, 0.22, "MUSCLE"),
    ("palm",      (0.20, 0.14, 0.09), (0.44, 0.32, 0.21), (0.11, 0.07, 0.04), 16.0, 8.0,  16.0, 0.88, 0.50, "PALM_SCAR"),
    ("acacia",    (0.14, 0.11, 0.08), (0.30, 0.24, 0.18), (0.08, 0.06, 0.04), 17.0, 5.0,  16.0, 0.87, 0.44, "ACACIA_MOSS"),
    ("olive",     (0.22, 0.20, 0.17), (0.42, 0.38, 0.32), (0.11, 0.10, 0.08), 16.0, 5.0,  18.0, 0.88, 0.50, "FISSURE"),
    ("fig",       (0.26, 0.23, 0.19), (0.45, 0.41, 0.35), (0.16, 0.14, 0.11), 13.0, 3.5,   9.0, 0.76, 0.26, "MUSCLE"),
    ("poplar",    (0.24, 0.23, 0.20), (0.50, 0.48, 0.43), (0.13, 0.12, 0.10), 15.0, 4.5,  14.0, 0.80, 0.34, "PLATE"),
    ("terebinth", (0.18, 0.12, 0.08), (0.37, 0.27, 0.19), (0.10, 0.07, 0.05), 16.0, 4.5,  14.0, 0.86, 0.44, "FISSURE"),
]


def _make_bark_strip_material(spec):
    name, c_dark, c_light, c_crev, su, sv, rfreq, rough, bump_str, mode = spec
    c_dark = clamp_hdr_albedo(c_dark)
    c_light = clamp_hdr_albedo(c_light)
    c_crev = clamp_hdr_albedo(c_crev)

    mat = bpy.data.materials.new(name=f"Mat_BarkStrip_{name}")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Metallic"].default_value = 0.0
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # UV -> Nahtlose V-Kachelung via Torus/Zylinder-Projektion (cos(2*pi*v), sin(2*pi*v))
    texcoord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(texcoord.outputs["UV"], sep.inputs["Vector"])

    # Lokales U innerhalb des Streifens [0..1] (wir mappen jeden Streifen-Quad auf U=0..1, V=0..1!)
    # Dadurch hat jeder Streifen volle 0..1 Koordinaten ohne Nachbar-Bleed.
    mul_tau = nt.nodes.new("ShaderNodeMath")
    mul_tau.operation = "MULTIPLY"
    mul_tau.inputs[1].default_value = 2.0 * math.pi
    nt.links.new(sep.outputs["Y"], mul_tau.inputs[0])

    cos_v = nt.nodes.new("ShaderNodeMath")
    cos_v.operation = "COSINE"
    nt.links.new(mul_tau.outputs["Value"], cos_v.inputs[0])

    sin_v = nt.nodes.new("ShaderNodeMath")
    sin_v.operation = "SINE"
    nt.links.new(mul_tau.outputs["Value"], sin_v.inputs[0])

    # Symmetrisches U für nahtlose horizontale Wrap-Sicherheit: sin(pi*u) oder direkt u*su
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    mul_u = nt.nodes.new("ShaderNodeMath")
    mul_u.operation = "MULTIPLY"
    mul_u.inputs[1].default_value = su * 0.25
    nt.links.new(sep.outputs["X"], mul_u.inputs[0])

    mul_cv = nt.nodes.new("ShaderNodeMath")
    mul_cv.operation = "MULTIPLY"
    mul_cv.inputs[1].default_value = sv * 0.35
    nt.links.new(cos_v.outputs["Value"], mul_cv.inputs[0])

    mul_sv = nt.nodes.new("ShaderNodeMath")
    mul_sv.operation = "MULTIPLY"
    mul_sv.inputs[1].default_value = sv * 0.35
    nt.links.new(sin_v.outputs["Value"], mul_sv.inputs[0])

    nt.links.new(mul_u.outputs["Value"], comb.inputs["X"])
    nt.links.new(mul_cv.outputs["Value"], comb.inputs["Y"])
    nt.links.new(mul_sv.outputs["Value"], comb.inputs["Z"])

    # Basis-Rindenrauschen
    noise_macro = nt.nodes.new("ShaderNodeTexNoise")
    noise_macro.inputs["Scale"].default_value = 2.2
    noise_macro.inputs["Detail"].default_value = 8.0
    noise_macro.inputs["Roughness"].default_value = 0.65
    nt.links.new(comb.outputs["Vector"], noise_macro.inputs["Vector"])

    # Vertikale Furchen via gestrecktes Noise (U stark gestreckt, V gering)
    comb_ridge = nt.nodes.new("ShaderNodeCombineXYZ")
    mul_ru = nt.nodes.new("ShaderNodeMath")
    mul_ru.operation = "MULTIPLY"
    mul_ru.inputs[1].default_value = rfreq * 0.45
    nt.links.new(sep.outputs["X"], mul_ru.inputs[0])
    nt.links.new(mul_ru.outputs["Value"], comb_ridge.inputs["X"])
    nt.links.new(cos_v.outputs["Value"], comb_ridge.inputs["Y"])
    nt.links.new(sin_v.outputs["Value"], comb_ridge.inputs["Z"])

    noise_ridge = nt.nodes.new("ShaderNodeTexNoise")
    noise_ridge.inputs["Scale"].default_value = 1.6
    noise_ridge.inputs["Detail"].default_value = 10.0
    noise_ridge.inputs["Roughness"].default_value = 0.72
    noise_ridge.inputs["Distortion"].default_value = 0.35 if mode != "MUSCLE" else 0.15
    nt.links.new(comb_ridge.outputs["Vector"], noise_ridge.inputs["Vector"])

    height_socket = noise_ridge.outputs["Fac"]

    if mode == "PALM_SCAR":
        # Diamant-Blattnarben via zweier gekreuzter Sinus-Wellen (U +- V)
        add_diag = nt.nodes.new("ShaderNodeMath")
        add_diag.operation = "ADD"
        mul_u_p = nt.nodes.new("ShaderNodeMath")
        mul_u_p.operation = "MULTIPLY"
        mul_u_p.inputs[1].default_value = 6.0 * 2.0 * math.pi
        nt.links.new(sep.outputs["X"], mul_u_p.inputs[0])
        mul_v_p = nt.nodes.new("ShaderNodeMath")
        mul_v_p.operation = "MULTIPLY"
        mul_v_p.inputs[1].default_value = 10.0 * 2.0 * math.pi
        nt.links.new(sep.outputs["Y"], mul_v_p.inputs[0])
        nt.links.new(mul_u_p.outputs["Value"], add_diag.inputs[0])
        nt.links.new(mul_v_p.outputs["Value"], add_diag.inputs[1])

        sub_diag = nt.nodes.new("ShaderNodeMath")
        sub_diag.operation = "SUBTRACT"
        nt.links.new(mul_u_p.outputs["Value"], sub_diag.inputs[0])
        nt.links.new(mul_v_p.outputs["Value"], sub_diag.inputs[1])

        s1 = nt.nodes.new("ShaderNodeMath")
        s1.operation = "SINE"
        nt.links.new(add_diag.outputs["Value"], s1.inputs[0])
        s2 = nt.nodes.new("ShaderNodeMath")
        s2.operation = "SINE"
        nt.links.new(sub_diag.outputs["Value"], s2.inputs[0])

        mul_dia = nt.nodes.new("ShaderNodeMath")
        mul_dia.operation = "MULTIPLY"
        nt.links.new(s1.outputs["Value"], mul_dia.inputs[0])
        nt.links.new(s2.outputs["Value"], mul_dia.inputs[1])

        ramp_dia = nt.nodes.new("ShaderNodeValToRGB")
        ramp_dia.color_ramp.elements[0].position = 0.0
        ramp_dia.color_ramp.elements[0].color = (0.08, 0.08, 0.08, 1.0)
        ramp_dia.color_ramp.elements[1].position = 0.55
        ramp_dia.color_ramp.elements[1].color = (0.95, 0.95, 0.95, 1.0)
        nt.links.new(mul_dia.outputs["Value"], ramp_dia.inputs["Fac"])

        mix_palm = nt.nodes.new("ShaderNodeMath")
        mix_palm.operation = "MULTIPLY_ADD"
        mix_palm.inputs[1].default_value = 0.65
        nt.links.new(ramp_dia.outputs["Color"], mix_palm.inputs[0])
        mul_nr = nt.nodes.new("ShaderNodeMath")
        mul_nr.operation = "MULTIPLY"
        mul_nr.inputs[1].default_value = 0.35
        nt.links.new(noise_ridge.outputs["Fac"], mul_nr.inputs[0])
        nt.links.new(mul_nr.outputs["Value"], mix_palm.inputs[2])
        height_socket = mix_palm.outputs["Value"]

    # Kontrast-Ramp für Rindenhöhe (0 = tiefe Furche, 1 = Rindengrat)
    ramp_h = nt.nodes.new("ShaderNodeValToRGB")
    ramp_h.color_ramp.elements[0].position = 0.28
    ramp_h.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp_h.color_ramp.elements[1].position = 0.72
    ramp_h.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(height_socket, ramp_h.inputs["Fac"])

    # Farbe mischen: Furche -> Dark -> Light
    _, col1_out = _mix_rgba(nt, ramp_h.outputs["Color"], c_crev, c_dark)
    _, final_col_socket = _mix_rgba(nt, noise_macro.outputs["Fac"], col1_out, c_light)

    if mode == "ACACIA_MOSS":
        # Leicht bemooste Wurzelbasis bei V < 0.20 (unten am Streifen)
        ramp_v = nt.nodes.new("ShaderNodeValToRGB")
        ramp_v.color_ramp.elements[0].position = 0.02
        ramp_v.color_ramp.elements[0].color = (0.65, 0.65, 0.65, 1.0)
        ramp_v.color_ramp.elements[1].position = 0.22
        ramp_v.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0)
        nt.links.new(sep.outputs["Y"], ramp_v.inputs["Fac"])

        mul_moss = nt.nodes.new("ShaderNodeMath")
        mul_moss.operation = "MULTIPLY"
        nt.links.new(ramp_v.outputs["Color"], mul_moss.inputs[0])
        nt.links.new(noise_macro.outputs["Fac"], mul_moss.inputs[1])

        moss_col = clamp_hdr_albedo((0.18, 0.25, 0.10))
        _, final_col_socket = _mix_rgba(nt, mul_moss.outputs["Value"], final_col_socket, moss_col)

    # Roughness: Furchen matter, Grate leicht polierter
    map_r = nt.nodes.new("ShaderNodeMapRange")
    map_r.inputs["From Min"].default_value = 0.0
    map_r.inputs["From Max"].default_value = 1.0
    map_r.inputs["To Min"].default_value = min(0.98, rough + 0.08)
    map_r.inputs["To Max"].default_value = max(0.55, rough - 0.10)
    nt.links.new(ramp_h.outputs["Color"], map_r.inputs["Value"])

    # Bump -> Normal -> [0..1] für direktes Tangent-Space-Normal-Rendering
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_str
    bump.inputs["Distance"].default_value = 0.03
    nt.links.new(height_socket, bump.inputs["Height"])

    nrm_to_01 = nt.nodes.new("ShaderNodeVectorMath")
    nrm_to_01.operation = "MULTIPLY_ADD"
    nrm_to_01.inputs[1].default_value = (0.5, 0.5, 0.5)
    nrm_to_01.inputs[2].default_value = (0.5, 0.5, 0.5)
    nt.links.new(bump.outputs["Normal"], nrm_to_01.inputs[0])

    # ORM: R = AO (0.42 in tiefen Furchen, 1.0 auf Graten), G = Roughness, B = 0.0
    map_ao = nt.nodes.new("ShaderNodeMapRange")
    map_ao.inputs["From Min"].default_value = 0.0
    map_ao.inputs["From Max"].default_value = 1.0
    map_ao.inputs["To Min"].default_value = 0.42
    map_ao.inputs["To Max"].default_value = 1.0
    nt.links.new(ramp_h.outputs["Color"], map_ao.inputs["Value"])

    comb_orm = nt.nodes.new("ShaderNodeCombineColor")
    comb_orm.inputs["Blue"].default_value = 0.0
    nt.links.new(map_ao.outputs["Result"], comb_orm.inputs["Red"])
    nt.links.new(map_r.outputs["Result"], comb_orm.inputs["Green"])

    nt.nodes.remove(bsdf)
    emit = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    nt.links.new(final_col_socket, emit.inputs["Color"])

    return {
        "mat": mat,
        "nt": nt,
        "emit": emit,
        "basecolor_out": final_col_socket,
        "normal_out": nrm_to_01.outputs["Vector"],
        "orm_out": comb_orm.outputs["Color"],
    }


def bake_bark_trim_sheet(tex_dir, size_x=2048, size_y=1024):
    print(f"[BOTANY ATLAS] Rendere Rinden-Trim-Sheet ({len(BARK_SPECS)} Streifen, {size_x}x{size_y})...")
    scene = clear_scene()
    dev_label = setup_cycles(scene, samples=4)
    print(f"[BOTANY ATLAS] Cycles Device: {dev_label}")

    mesh = bpy.data.meshes.new("BarkTrimPlane")
    bm = bmesh.new()
    uv_local = bm.loops.layers.uv.new("LocalUV")

    n_strips = len(BARK_SPECS)
    for i in range(n_strips):
        x0 = i / n_strips
        x1 = (i + 1) / n_strips
        v0 = bm.verts.new((x0, 0.0, 0.0))
        v1 = bm.verts.new((x1, 0.0, 0.0))
        v2 = bm.verts.new((x1, 1.0, 0.0))
        v3 = bm.verts.new((x0, 1.0, 0.0))
        f = bm.faces.new((v0, v1, v2, v3))
        f.material_index = i
        local_coords = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        for loop, lc in zip(f.loops, local_coords):
            loop[uv_local].uv = lc

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("BarkTrimPlane", mesh)
    scene.collection.objects.link(obj)

    mat_infos = []
    for spec in BARK_SPECS:
        info = _make_bark_strip_material(spec)
        mesh.materials.append(info["mat"])
        mat_infos.append(info)

    cam_data = bpy.data.cameras.new("BarkCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 1.0
    cam_obj = bpy.data.objects.new("BarkCam", cam_data)
    cam_obj.location = (0.5, 0.5, 2.0)
    cam_obj.rotation_euler = (0.0, 0.0, 0.0)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    scene.render.resolution_x = size_x
    scene.render.resolution_y = size_y
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.display_settings.display_device = "sRGB"

    def _render_bark_pass(pass_key, filepath, is_non_color):
        for info in mat_infos:
            info["nt"].links.new(info[pass_key], info["emit"].inputs["Color"])
        scene.view_settings.view_transform = "Raw" if is_non_color else "Standard"
        scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)

    p_col = os.path.join(tex_dir, "botany_bark_trim_baseColor.png")
    _render_bark_pass("basecolor_out", p_col, is_non_color=False)

    p_nrm = os.path.join(tex_dir, "botany_bark_trim_normal.png")
    _render_bark_pass("normal_out", p_nrm, is_non_color=True)

    p_orm = os.path.join(tex_dir, "botany_bark_trim_orm.png")
    _render_bark_pass("orm_out", p_orm, is_non_color=True)

    print(f"[BOTANY ATLAS] Rinden-Trim gespeichert: {p_col}, {p_nrm}, {p_orm}")
    return p_col, p_nrm, p_orm


# ==============================================================================
# 2. LEAF ATLAS (5x4 Raster = 20 Zellen fuer 10 Arten x 2 Alter, 2048x2048 RGBA)
# ==============================================================================
LEAF_CELLS = [
    # (species, stage_variant, col, row, leaf_col, twig_col, rough, mode)
    # Reihe 0
    ("cedar",     "young",  0, 0, (0.11, 0.25, 0.09),  (0.26, 0.17, 0.10), 0.54, "CEDAR_NEEDLE"),
    ("cedar",     "mature", 1, 0, (0.065, 0.16, 0.07), (0.21, 0.14, 0.08), 0.58, "CEDAR_NEEDLE"),
    ("cypress",   "young",  2, 0, (0.10, 0.23, 0.09),  (0.24, 0.17, 0.10), 0.52, "CYPRESS_SCALE"),
    ("cypress",   "mature", 3, 0, (0.06, 0.15, 0.075), (0.19, 0.14, 0.09), 0.56, "CYPRESS_SCALE"),
    ("oak",       "young",  4, 0, (0.16, 0.28, 0.08),  (0.25, 0.17, 0.10), 0.50, "OAK_LOBED"),
    # Reihe 1
    ("oak",       "mature", 0, 1, (0.09, 0.19, 0.06),  (0.20, 0.14, 0.09), 0.54, "OAK_LOBED"),
    ("hornbeam",  "young",  1, 1, (0.18, 0.31, 0.09),  (0.29, 0.23, 0.16), 0.48, "HORNBEAM_SERRATED"),
    ("hornbeam",  "mature", 2, 1, (0.10, 0.22, 0.07),  (0.23, 0.17, 0.12), 0.52, "HORNBEAM_SERRATED"),
    ("palm",      "young",  3, 1, (0.16, 0.29, 0.09),  (0.33, 0.27, 0.13), 0.46, "PALM_FROND"),
    ("palm",      "mature", 4, 1, (0.095, 0.21, 0.075),(0.27, 0.21, 0.12), 0.50, "PALM_FROND"),
    # Reihe 2
    ("acacia",    "young",  0, 2, (0.17, 0.28, 0.09),  (0.25, 0.18, 0.11), 0.50, "ACACIA_BIPINNATE"),
    ("acacia",    "mature", 1, 2, (0.10, 0.19, 0.07),  (0.20, 0.14, 0.10), 0.54, "ACACIA_BIPINNATE"),
    ("olive",     "young",  2, 2, (0.18, 0.26, 0.14),  (0.32, 0.29, 0.24), 0.56, "OLIVE_LANCEOLATE"),
    ("olive",     "mature", 3, 2, (0.13, 0.20, 0.115), (0.27, 0.24, 0.20), 0.60, "OLIVE_LANCEOLATE"),
    ("fig",       "young",  4, 2, (0.15, 0.29, 0.08),  (0.29, 0.25, 0.18), 0.46, "FIG_LOBED"),
    # Reihe 3
    ("fig",       "mature", 0, 3, (0.095, 0.21, 0.06), (0.24, 0.21, 0.16), 0.50, "FIG_LOBED"),
    ("poplar",    "young",  1, 3, (0.20, 0.32, 0.09),  (0.34, 0.32, 0.26), 0.44, "POPLAR_DELTOID"),
    ("poplar",    "mature", 2, 3, (0.13, 0.24, 0.075), (0.29, 0.27, 0.22), 0.48, "POPLAR_DELTOID"),
    ("terebinth", "young",  3, 3, (0.16, 0.26, 0.08),  (0.26, 0.17, 0.11), 0.48, "TEREBINTH_PINNATE"),
    ("terebinth", "mature", 4, 3, (0.10, 0.18, 0.065), (0.21, 0.14, 0.09), 0.52, "TEREBINTH_PINNATE"),
]


def _add_tapered_twig(bm, pts, r0, r1, sides=5, uv_layer=None, col_layer=None, thick_val=0.10, ao_val=0.55):
    rings = []
    n_pts = len(pts)
    for i, p in enumerate(pts):
        t = i / max(1, n_pts - 1)
        r = r0 * (1.0 - t) + r1 * t
        if i < n_pts - 1:
            tang = (pts[i + 1] - p).normalized()
        else:
            tang = (p - pts[i - 1]).normalized()
        up = Vector((0.0, 0.0, 1.0))
        side = tang.cross(up)
        if side.length < 1e-4:
            side = Vector((1.0, 0.0, 0.0))
        side.normalize()
        up_ortho = side.cross(tang).normalized()
        ring = []
        for s in range(sides):
            ang = 2.0 * math.pi * s / sides
            v = bm.verts.new(p + (side * math.cos(ang) + up_ortho * math.sin(ang)) * r)
            ring.append(v)
        rings.append(ring)

    for i in range(n_pts - 1):
        r_a = rings[i]
        r_b = rings[i + 1]
        for s in range(sides):
            sn = (s + 1) % sides
            f = bm.faces.new((r_a[s], r_a[sn], r_b[sn], r_b[s]))
            f.smooth = True
            for loop in f.loops:
                if col_layer is not None:
                    # R = 0.0 (Zweig/Holz), G = AO, B = Thickness
                    loop[col_layer] = (0.0, ao_val, thick_val, 1.0)


def _add_leaf_blade(bm, origin, dir_vec, length, width, arch_z=0.015, serrations=0, lobe_amp=0.0,
                    col_layer=None, ao_base=0.62, ao_tip=0.98, thick_base=0.50, thick_tip=0.92, leaf_var=0.0):
    """Erzeugt eine fein konturierte 3D-Blattspreite mit Mittelrippe (leicht gefaltet für Normal-Tiefe!)."""
    d = dir_vec.normalized()
    up = Vector((0.0, 0.0, 1.0))
    side = d.cross(up)
    if side.length < 1e-4:
        side = Vector((1.0, 0.0, 0.0))
    side.normalize()
    n_up = side.cross(d).normalized()

    segs = max(4, serrations if serrations > 0 else 5)
    left_vs = []
    mid_vs = []
    right_vs = []

    for i in range(segs + 1):
        t = i / segs
        # Tropfen-/Lanzett-Profil
        env = math.sin(math.pi * (t ** 0.72))
        if lobe_amp > 0.0 and 0.12 < t < 0.92:
            env *= (1.0 - lobe_amp * 0.45 * (0.5 + 0.5 * math.cos(t * math.pi * 6.0)))
        if serrations > 0 and 0 < i < segs:
            env *= (0.86 if (i % 2 == 1) else 1.04)

        w = width * 0.5 * env
        z_curve = arch_z * math.sin(math.pi * t)
        center = origin + d * (length * t) + n_up * z_curve

        vm = bm.verts.new(center)
        mid_vs.append((vm, t))
        if i == 0 or i == segs:
            left_vs.append((vm, t))
            right_vs.append((vm, t))
        else:
            z_fold = w * 0.26  # V-Faltung für echte 3D-Normalen!
            vl = bm.verts.new(center - side * w + n_up * z_fold)
            vr = bm.verts.new(center + side * w + n_up * z_fold)
            left_vs.append((vl, t))
            right_vs.append((vr, t))

    def _set_col(face, t_avg):
        if col_layer is None:
            return
        ao = ao_base * (1.0 - t_avg) + ao_tip * t_avg
        th = thick_base * (1.0 - t_avg) + thick_tip * t_avg
        for loop in face.loops:
            # R = 1.0 (Blatt), G = AO, B = Thickness
            loop[col_layer] = (1.0, max(0.0, min(1.0, ao + leaf_var * 0.1)), th, 1.0)

    for i in range(segs):
        vm0, t0 = mid_vs[i]
        vm1, t1 = mid_vs[i + 1]
        vl0, _ = left_vs[i]
        vl1, _ = left_vs[i + 1]
        vr0, _ = right_vs[i]
        vr1, _ = right_vs[i + 1]
        t_avg = 0.5 * (t0 + t1)

        if i == 0:
            fl = bm.faces.new((vm0, vm1, vl1))
            fr = bm.faces.new((vm0, vr1, vm1))
            fl.smooth = True
            fr.smooth = True
            _set_col(fl, t_avg)
            _set_col(fr, t_avg)
        elif i == segs - 1:
            fl = bm.faces.new((vm0, vm1, vl0))
            fr = bm.faces.new((vm0, vr0, vm1))
            fl.smooth = True
            fr.smooth = True
            _set_col(fl, t_avg)
            _set_col(fr, t_avg)
        else:
            fl = bm.faces.new((vm0, vm1, vl1, vl0))
            fr = bm.faces.new((vm0, vr0, vr1, vm1))
            fl.smooth = True
            fr.smooth = True
            _set_col(fl, t_avg)
            _set_col(fr, t_avg)


def _build_cell_twig(bm, cell_spec, col_layer):
    species, stage_var, col_idx, row_idx, leaf_c, twig_c, rough, mode = cell_spec
    rng = random.Random(hash(f"{species}_{stage_var}") & 0xFFFFFFFF)

    # Zell-Grenzen in [0..1] x [0..1] (5 Spalten x 4 Reihen, oben = row 0)
    cw = 1.0 / 5.0
    ch = 1.0 / 4.0
    x0 = col_idx * cw
    y1 = 1.0 - row_idx * ch
    y0 = y1 - ch

    pad_x = cw * 0.065
    pad_y = ch * 0.075
    cx = x0 + cw * 0.5
    by = y0 + pad_y
    ty = y1 - pad_y
    span_x = cw - 2.0 * pad_x
    span_y = ty - by

    if mode == "PALM_FROND":
        # Feine, scharf gefiederte Dattelpalmen-Wedel (28 feine Fiederpaare)
        stem_pts = [
            Vector((cx + 0.004 * math.sin(i * 0.45), by + span_y * (i / 7.0), 0.01 * math.sin(i * 0.5)))
            for i in range(8)
        ]
        _add_tapered_twig(bm, stem_pts, 0.0048, 0.0012, sides=5, col_layer=col_layer, thick_val=0.14, ao_val=0.55)
        n_pairs = 28
        for i in range(1, n_pairs + 1):
            t = i / (n_pairs + 0.6)
            base = Vector((cx + 0.003 * math.sin(t * 3.0), by + span_y * t, 0.011))
            len_f = span_x * (0.56 - 0.16 * abs(t - 0.48))
            for sgn in (-1.0, 1.0):
                ang = sgn * rng.uniform(0.42, 0.85) + rng.uniform(-0.06, 0.06)
                d = Vector((math.sin(ang), math.cos(ang), rng.uniform(0.06, 0.24)))
                _add_leaf_blade(bm, base, d, len_f, 0.0085, arch_z=0.006, serrations=0,
                                col_layer=col_layer, ao_base=0.60, ao_tip=0.98, thick_base=0.45, thick_tip=0.88,
                                leaf_var=rng.uniform(-0.5, 0.5))
                if i % 2 == 0:
                    ang2 = sgn * rng.uniform(0.24, 0.62)
                    d2 = Vector((math.sin(ang2), math.cos(ang2), rng.uniform(0.14, 0.30)))
                    _add_leaf_blade(bm, base + Vector((0, 0, 0.003)), d2, len_f * 0.82, 0.0072, arch_z=0.005, serrations=0,
                                    col_layer=col_layer, ao_base=0.72, ao_tip=1.0, thick_base=0.52, thick_tip=0.92,
                                    leaf_var=rng.uniform(-0.5, 0.5))

    elif mode == "CEDAR_NEEDLE":
        # Feine Libanon-Zeder-Zweige mit 20 kompakten Nadelrosetten & zarten Nadeln
        main_pts = [Vector((cx + 0.012 * math.sin(i * 0.85), by + span_y * (i / 5.0), 0.005)) for i in range(6)]
        _add_tapered_twig(bm, main_pts, 0.0040, 0.0012, sides=5, col_layer=col_layer, thick_val=0.10, ao_val=0.48)
        rosette_specs = [
            (Vector((cx,                   by + span_y * 0.14, 0.006)), 0.90),
            (Vector((cx - span_x * 0.20,   by + span_y * 0.22, 0.007)), 0.95),
            (Vector((cx + span_x * 0.20,   by + span_y * 0.25, 0.007)), 0.95),
            (Vector((cx - span_x * 0.05,   by + span_y * 0.31, 0.008)), 1.00),
            (Vector((cx - span_x * 0.32,   by + span_y * 0.38, 0.007)), 0.92),
            (Vector((cx + span_x * 0.30,   by + span_y * 0.41, 0.007)), 0.92),
            (Vector((cx + span_x * 0.06,   by + span_y * 0.45, 0.009)), 1.02),
            (Vector((cx - span_x * 0.26,   by + span_y * 0.52, 0.008)), 0.95),
            (Vector((cx + span_x * 0.25,   by + span_y * 0.55, 0.008)), 0.95),
            (Vector((cx - span_x * 0.03,   by + span_y * 0.60, 0.009)), 0.98),
            (Vector((cx - span_x * 0.30,   by + span_y * 0.65, 0.008)), 0.88),
            (Vector((cx + span_x * 0.29,   by + span_y * 0.68, 0.008)), 0.88),
            (Vector((cx - span_x * 0.14,   by + span_y * 0.74, 0.009)), 0.90),
            (Vector((cx + span_x * 0.15,   by + span_y * 0.76, 0.009)), 0.90),
            (Vector((cx,                   by + span_y * 0.82, 0.009)), 0.92),
            (Vector((cx - span_x * 0.16,   by + span_y * 0.86, 0.009)), 0.82),
            (Vector((cx + span_x * 0.15,   by + span_y * 0.88, 0.009)), 0.82),
            (Vector((cx,                   by + span_y * 0.93, 0.010)), 0.80),
        ]
        for rc, r_scale in rosette_specs:
            _add_tapered_twig(bm, [Vector((cx, max(by, rc.y - 0.022), 0.005)), rc], 0.0020, 0.0010, sides=4,
                              col_layer=col_layer, thick_val=0.12, ao_val=0.50)
            for k in range(28):
                ang = (2.0 * math.pi * k / 28.0) + rng.uniform(-0.12, 0.12)
                d = Vector((math.cos(ang), math.sin(ang), rng.uniform(0.12, 0.52)))
                n_len = rng.uniform(0.022, 0.036) * r_scale
                _add_leaf_blade(bm, rc, d, n_len, 0.0044, arch_z=0.0025, serrations=0,
                                col_layer=col_layer, ao_base=0.52, ao_tip=0.98, thick_base=0.55, thick_tip=0.94,
                                leaf_var=rng.uniform(-0.5, 0.5))

    elif mode == "CYPRESS_SCALE":
        # Feingliedrige Mittelmeer-Zypressen-Schuppensprays (keine plumpen Keile)
        main_pts = [Vector((cx + 0.007 * math.sin(i * 0.8), by + span_y * (i / 6.0), 0.005)) for i in range(7)]
        _add_tapered_twig(bm, main_pts, 0.0036, 0.0011, sides=5, col_layer=col_layer, thick_val=0.10, ao_val=0.48)
        for i in range(1, 20):
            t = i / 20.0
            base = Vector((cx + 0.004 * math.sin(t * 4.0), by + span_y * t, 0.006))
            for sgn in (-1.0, 1.0):
                ang = sgn * rng.uniform(0.22, 0.62)
                d = Vector((math.sin(ang), math.cos(ang), rng.uniform(0.08, 0.28)))
                sub_len = span_x * rng.uniform(0.36, 0.50) * (1.10 - 0.48 * t)
                _add_leaf_blade(bm, base, d, sub_len, 0.0115, arch_z=0.004, serrations=9,
                                col_layer=col_layer, ao_base=0.52, ao_tip=0.96, thick_base=0.45, thick_tip=0.88,
                                leaf_var=rng.uniform(-0.5, 0.5))
                mid_p = base + d.normalized() * (sub_len * 0.42)
                d2 = Vector((math.sin(ang + sgn * 0.36), math.cos(ang + sgn * 0.36), 0.22))
                _add_leaf_blade(bm, mid_p, d2, sub_len * 0.62, 0.0095, arch_z=0.003, serrations=6,
                                col_layer=col_layer, ao_base=0.58, ao_tip=0.98, thick_base=0.50, thick_tip=0.90,
                                leaf_var=rng.uniform(-0.5, 0.5))
                d3 = Vector((math.sin(ang - sgn * 0.24), math.cos(ang - sgn * 0.24), 0.30))
                _add_leaf_blade(bm, base + d.normalized() * (sub_len * 0.24), d3, sub_len * 0.50, 0.0085, arch_z=0.003, serrations=5,
                                col_layer=col_layer, ao_base=0.62, ao_tip=1.0, thick_base=0.54, thick_tip=0.92)

    elif mode in ("OAK_LOBED", "HORNBEAM_SERRATED"):
        # Feinverzweigte Laubzweig-Sprays mit vielen kleinen, klar getrennten Blaettern (2.5x feiner!)
        is_oak = (mode == "OAK_LOBED")
        main_pts = [Vector((cx + 0.010 * math.sin(i * 1.1), by + span_y * (i / 6.0), 0.005)) for i in range(7)]
        _add_tapered_twig(bm, main_pts, 0.0036, 0.0010, sides=5, col_layer=col_layer, thick_val=0.10, ao_val=0.48)
        lat_twigs = [
            (Vector((cx, by + span_y * 0.16, 0.005)), Vector((cx - span_x * 0.36, by + span_y * 0.34, 0.007))),
            (Vector((cx, by + span_y * 0.22, 0.005)), Vector((cx + span_x * 0.36, by + span_y * 0.40, 0.007))),
            (Vector((cx, by + span_y * 0.42, 0.006)), Vector((cx - span_x * 0.34, by + span_y * 0.60, 0.008))),
            (Vector((cx, by + span_y * 0.48, 0.006)), Vector((cx + span_x * 0.34, by + span_y * 0.65, 0.008))),
            (Vector((cx, by + span_y * 0.66, 0.007)), Vector((cx - span_x * 0.24, by + span_y * 0.82, 0.009))),
            (Vector((cx, by + span_y * 0.70, 0.007)), Vector((cx + span_x * 0.24, by + span_y * 0.85, 0.009))),
        ]
        for p0, p1 in lat_twigs:
            _add_tapered_twig(bm, [p0, p1], 0.0020, 0.0008, sides=4, col_layer=col_layer, thick_val=0.11, ao_val=0.52)
            tvec = p1 - p0
            tang = math.atan2(tvec.x, tvec.y)
            for k in range(8):
                kt = 0.18 + 0.78 * (k / 7.0)
                lp = p0.lerp(p1, kt)
                sgn = -1.0 if (k % 2 == 0) else 1.0
                lang = tang + sgn * rng.uniform(0.45, 0.92)
                llen = rng.uniform(0.026, 0.036) * (1.05 - 0.25 * kt)
                d = Vector((math.sin(lang), math.cos(lang), rng.uniform(0.08, 0.28)))
                _add_leaf_blade(
                    bm, lp, d, llen, llen * (0.58 if is_oak else 0.52),
                    arch_z=0.004,
                    serrations=7 if not is_oak else 5,
                    lobe_amp=0.68 if is_oak else 0.0,
                    col_layer=col_layer,
                    ao_base=0.54 if (k % 3 == 0) else 0.66, ao_tip=0.98,
                    thick_base=0.48, thick_tip=0.92,
                    leaf_var=rng.uniform(-0.5, 0.5),
                )
            # Endblatt am Seitenzweig
            d_end = Vector((math.sin(tang), math.cos(tang), 0.18))
            _add_leaf_blade(
                bm, p1, d_end, 0.030, 0.017, arch_z=0.004,
                serrations=6 if not is_oak else 5, lobe_amp=0.65 if is_oak else 0.0,
                col_layer=col_layer, ao_base=0.68, ao_tip=1.0, thick_base=0.52, thick_tip=0.95,
                leaf_var=rng.uniform(-0.4, 0.4),
            )
        # Feinblaetter entlang der Hauptachse
        for k in range(14):
            kt = 0.14 + 0.78 * (k / 13.0)
            base = Vector((cx + rng.uniform(-0.005, 0.005), by + span_y * kt, 0.009))
            sgn = -1.0 if (k % 2 == 0) else 1.0
            ang = sgn * rng.uniform(0.28, 0.85)
            llen = rng.uniform(0.026, 0.038) * (1.0 - 0.2 * kt)
            d = Vector((math.sin(ang), math.cos(ang), rng.uniform(0.10, 0.30)))
            _add_leaf_blade(
                bm, base, d, llen, llen * (0.58 if is_oak else 0.52),
                arch_z=0.004, serrations=7 if not is_oak else 5, lobe_amp=0.68 if is_oak else 0.0,
                col_layer=col_layer, ao_base=0.58, ao_tip=0.98, thick_base=0.50, thick_tip=0.94,
                leaf_var=rng.uniform(-0.5, 0.5),
            )

    elif mode == "OLIVE_LANCEOLATE":
        # Schlanke gegenstaendige silbrig-gruene Olivenblaetter an fein verzweigten Zweigen
        main_pts = [Vector((cx + 0.008 * math.sin(i * 1.1), by + span_y * (i / 6.0), 0.005)) for i in range(7)]
        _add_tapered_twig(bm, main_pts, 0.0030, 0.0009, sides=5, col_layer=col_layer, thick_val=0.10, ao_val=0.50)
        sub_twigs = [
            (Vector((cx, by + span_y * 0.16, 0.005)), Vector((cx - span_x * 0.34, by + span_y * 0.36, 0.007))),
            (Vector((cx, by + span_y * 0.22, 0.005)), Vector((cx + span_x * 0.34, by + span_y * 0.42, 0.007))),
            (Vector((cx, by + span_y * 0.44, 0.006)), Vector((cx - span_x * 0.32, by + span_y * 0.64, 0.008))),
            (Vector((cx, by + span_y * 0.50, 0.006)), Vector((cx + span_x * 0.32, by + span_y * 0.68, 0.008))),
            (Vector((cx, by + span_y * 0.68, 0.007)), Vector((cx - span_x * 0.22, by + span_y * 0.85, 0.009))),
            (Vector((cx, by + span_y * 0.72, 0.007)), Vector((cx + span_x * 0.22, by + span_y * 0.88, 0.009))),
        ]
        for p0, p1 in sub_twigs:
            _add_tapered_twig(bm, [p0, p1], 0.0017, 0.0007, sides=4, col_layer=col_layer, thick_val=0.11, ao_val=0.54)
            tvec = p1 - p0
            tang = math.atan2(tvec.x, tvec.y)
            for k in range(1, 7):
                kt = k / 6.5
                lp = p0.lerp(p1, kt)
                for sgn in (-1.0, 1.0):
                    lang = tang + sgn * rng.uniform(0.55, 0.92)
                    llen = rng.uniform(0.022, 0.030) * (1.05 - 0.2 * kt)
                    d = Vector((math.sin(lang), math.cos(lang), rng.uniform(0.08, 0.25)))
                    _add_leaf_blade(bm, lp, d, llen, 0.0062, arch_z=0.003, serrations=0,
                                    col_layer=col_layer, ao_base=0.56, ao_tip=0.98, thick_base=0.45, thick_tip=0.88,
                                    leaf_var=rng.uniform(-0.4, 0.4))
        for k in range(1, 14):
            kt = 0.12 + 0.80 * (k / 14.0)
            lp = Vector((cx, by + span_y * kt, 0.008))
            for sgn in (-1.0, 1.0):
                lang = sgn * rng.uniform(0.45, 0.85)
                d = Vector((math.sin(lang), math.cos(lang), rng.uniform(0.10, 0.28)))
                _add_leaf_blade(bm, lp, d, rng.uniform(0.024, 0.032), 0.0066, arch_z=0.003, serrations=0,
                                col_layer=col_layer, ao_base=0.60, ao_tip=0.98, thick_base=0.48, thick_tip=0.90,
                                leaf_var=rng.uniform(-0.4, 0.4))

    elif mode == "FIG_LOBED":
        # Gelappte mediterrane Feigen-/Sykomoren-Zweige
        main_pts = [Vector((cx + 0.009 * math.sin(i * 1.0), by + span_y * (i / 5.0), 0.005)) for i in range(6)]
        _add_tapered_twig(bm, main_pts, 0.0038, 0.0012, sides=5, col_layer=col_layer, thick_val=0.10, ao_val=0.48)
        for p0, p1 in [
            (Vector((cx, by + span_y * 0.20, 0.005)), Vector((cx - span_x * 0.34, by + span_y * 0.42, 0.007))),
            (Vector((cx, by + span_y * 0.28, 0.005)), Vector((cx + span_x * 0.34, by + span_y * 0.48, 0.007))),
            (Vector((cx, by + span_y * 0.54, 0.006)), Vector((cx - span_x * 0.28, by + span_y * 0.74, 0.008))),
            (Vector((cx, by + span_y * 0.60, 0.006)), Vector((cx + span_x * 0.28, by + span_y * 0.78, 0.008))),
        ]:
            _add_tapered_twig(bm, [p0, p1], 0.0022, 0.0009, sides=4, col_layer=col_layer, thick_val=0.12, ao_val=0.52)
            tvec = p1 - p0
            tang = math.atan2(tvec.x, tvec.y)
            for k in range(5):
                kt = 0.25 + 0.75 * (k / 4.0)
                lp = p0.lerp(p1, kt)
                sgn = -1.0 if (k % 2 == 0) else 1.0
                lang = tang + sgn * rng.uniform(0.40, 0.88)
                llen = rng.uniform(0.032, 0.042)
                d = Vector((math.sin(lang), math.cos(lang), rng.uniform(0.06, 0.24)))
                _add_leaf_blade(bm, lp, d, llen, llen * 0.76, arch_z=0.004, serrations=5, lobe_amp=0.82,
                                col_layer=col_layer, ao_base=0.52, ao_tip=0.96, thick_base=0.45, thick_tip=0.88,
                                leaf_var=rng.uniform(-0.5, 0.5))
        for k in range(10):
            kt = 0.16 + 0.76 * (k / 9.0)
            lp = Vector((cx, by + span_y * kt, 0.008))
            sgn = -1.0 if (k % 2 == 0) else 1.0
            lang = sgn * rng.uniform(0.25, 0.75)
            d = Vector((math.sin(lang), math.cos(lang), rng.uniform(0.08, 0.26)))
            llen = rng.uniform(0.034, 0.044)
            _add_leaf_blade(bm, lp, d, llen, llen * 0.78, arch_z=0.004, serrations=5, lobe_amp=0.82,
                            col_layer=col_layer, ao_base=0.56, ao_tip=0.98, thick_base=0.48, thick_tip=0.90,
                            leaf_var=rng.uniform(-0.5, 0.5))

    elif mode in ("POPLAR_DELTOID", "TEREBINTH_PINNATE"):
        # Feine Auwald-Pappel (herzfoermig-rundlich) bzw. Terebinthe (unpaarig gefiedert)
        is_poplar = (mode == "POPLAR_DELTOID")
        main_pts = [Vector((cx + 0.008 * math.sin(i * 1.0), by + span_y * 0.85 * (i / 6.0), 0.005)) for i in range(7)]
        _add_tapered_twig(bm, main_pts, 0.0030, 0.0009, sides=5, col_layer=col_layer, thick_val=0.10, ao_val=0.50)
        for p0, p1 in [
            (Vector((cx, by + span_y * 0.16, 0.005)), Vector((cx - span_x * 0.30, by + span_y * 0.34, 0.007))),
            (Vector((cx, by + span_y * 0.22, 0.005)), Vector((cx + span_x * 0.30, by + span_y * 0.40, 0.007))),
            (Vector((cx, by + span_y * 0.44, 0.006)), Vector((cx - span_x * 0.26, by + span_y * 0.62, 0.008))),
            (Vector((cx, by + span_y * 0.48, 0.006)), Vector((cx + span_x * 0.26, by + span_y * 0.66, 0.008))),
        ]:
            _add_tapered_twig(bm, [p0, p1], 0.0018, 0.0007, sides=4, col_layer=col_layer, thick_val=0.11, ao_val=0.54)
            tvec = p1 - p0
            tang = math.atan2(tvec.x, tvec.y)
            for k in range(7):
                kt = 0.20 + 0.72 * (k / 6.0)
                lp = p0.lerp(p1, kt)
                for sgn in ((-1.0, 1.0) if not is_poplar else (-1.0 if k % 2 == 0 else 1.0,)):
                    lang = tang + sgn * rng.uniform(0.45, 0.92)
                    llen = rng.uniform(0.017, 0.023) if is_poplar else rng.uniform(0.018, 0.025)
                    lwid = llen * (0.76 if is_poplar else 0.42)
                    d = Vector((math.sin(lang), math.cos(lang), rng.uniform(0.08, 0.28)))
                    _add_leaf_blade(bm, lp, d, llen, lwid, arch_z=0.003,
                                    serrations=5 if is_poplar else 0, lobe_amp=0.0,
                                    col_layer=col_layer, ao_base=0.56, ao_tip=0.98, thick_base=0.50, thick_tip=0.94,
                                    leaf_var=rng.uniform(-0.5, 0.5))
        for k in range(11):
            kt = 0.14 + 0.64 * (k / 10.0)
            lp = Vector((cx, by + span_y * kt, 0.008))
            for sgn in (-1.0, 1.0):
                lang = sgn * rng.uniform(0.35, 0.85)
                llen = rng.uniform(0.018, 0.024) if is_poplar else rng.uniform(0.020, 0.026)
                lwid = llen * (0.76 if is_poplar else 0.42)
                d = Vector((math.sin(lang), math.cos(lang), rng.uniform(0.08, 0.28)))
                _add_leaf_blade(bm, lp, d, llen, lwid, arch_z=0.003,
                                serrations=5 if is_poplar else 0,
                                col_layer=col_layer, ao_base=0.60, ao_tip=0.98, thick_base=0.52, thick_tip=0.95,
                                leaf_var=rng.uniform(-0.5, 0.5))

    elif mode == "ACACIA_BIPINNATE":
        # Dichte zweifach gefiederte Akazien-Blaettchen (~62% Zellabdeckung, klarer Fieder-Umriss)
        main_pts = [Vector((cx + 0.008 * math.sin(i * 1.0), by + span_y * (i / 5.0), 0.005)) for i in range(6)]
        _add_tapered_twig(bm, main_pts, 0.0036, 0.0012, sides=5, col_layer=col_layer, thick_val=0.10, ao_val=0.48)
        for pair_i in range(6):
            t = 0.14 + pair_i * 0.145
            base = Vector((cx, by + span_y * t, 0.006))
            for sgn in (-1.0, 1.0):
                ang = sgn * rng.uniform(0.68, 1.06)
                d_sub = Vector((math.sin(ang), math.cos(ang), 0.1)).normalized()
                sub_len = span_x * 0.48 * (1.06 - 0.16 * abs(pair_i - 2.0))
                p_end = base + d_sub * sub_len
                _add_tapered_twig(bm, [base, p_end], 0.0016, 0.0007, sides=4, col_layer=col_layer, thick_val=0.14, ao_val=0.56)
                perp = Vector((-d_sub.y, d_sub.x, 0.15)).normalized()
                for k in range(1, 11):
                    kt = k / 10.5
                    lp = base + d_sub * (sub_len * kt)
                    for lsgn in (-1.0, 1.0):
                        ld = (perp * lsgn + d_sub * 0.35 + Vector((0, 0, 0.15))).normalized()
                        _add_leaf_blade(bm, lp, ld, 0.020, 0.0085, arch_z=0.002, serrations=0,
                                        col_layer=col_layer, ao_base=0.60, ao_tip=0.98, thick_base=0.56, thick_tip=0.95,
                                        leaf_var=rng.uniform(-0.4, 0.4))
        # Spitzen-Fiedern an der Hauptachse
        tip_base = Vector((cx, by + span_y * 0.88, 0.007))
        for k in range(6):
            ang = -0.7 + k * 0.28
            d = Vector((math.sin(ang), math.cos(ang), 0.18)).normalized()
            _add_leaf_blade(bm, tip_base, d, 0.030, 0.010, arch_z=0.003, serrations=0,
                            col_layer=col_layer, ao_base=0.65, ao_tip=1.0, thick_base=0.58, thick_tip=0.95)


def _make_leaf_cell_material(cell_spec):
    species, stage_var, _, _, leaf_c, twig_c, rough, _ = cell_spec
    leaf_c = clamp_hdr_albedo(leaf_c)
    twig_c = clamp_hdr_albedo(twig_c)

    mat = bpy.data.materials.new(name=f"Mat_LeafCell_{species}_{stage_var}")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])

    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "LeafData"
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(attr.outputs["Color"], sep.inputs["Color"])

    # R = 0 (Zweig) .. 1 (Blatt), G = AO, B = Thickness
    # Leichte Blatt-Farbvariation über Noise
    texcoord = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 38.0
    noise.inputs["Detail"].default_value = 4.0
    nt.links.new(texcoord.outputs["Object"], noise.inputs["Vector"])

    # Blattfarbe leicht modulieren (ohne HDR-Grenzen zu sprengen)
    leaf_hi = clamp_hdr_albedo((leaf_c[0] * 1.18, leaf_c[1] * 1.16, leaf_c[2] * 1.10))
    leaf_lo = clamp_hdr_albedo((leaf_c[0] * 0.82, leaf_c[1] * 0.84, leaf_c[2] * 0.86))

    _, leaf_mod_out = _mix_rgba(nt, noise.outputs["Fac"], leaf_lo, leaf_hi)
    _, col_out = _mix_rgba(nt, sep.outputs["Red"], twig_c, leaf_mod_out)

    # Standardmäßig BaseColor -> Emission (0 Schlagschatten!)
    nt.links.new(col_out, emit.inputs["Color"])

    # Hilfs-Nodes für Normal, ORM und Thickness Pass-Umschaltung
    geom = nt.nodes.new("ShaderNodeNewGeometry")
    # Normal [-1..1] -> [0..1]
    vec_mul = nt.nodes.new("ShaderNodeVectorMath")
    vec_mul.operation = "MULTIPLY_ADD"
    vec_mul.inputs[1].default_value = (0.5, 0.5, 0.5)
    vec_mul.inputs[2].default_value = (0.5, 0.5, 0.5)
    nt.links.new(geom.outputs["Normal"], vec_mul.inputs[0])

    # ORM: R=AO (sep.Green), G=Roughness (0.78 Zweig, rough Blatt), B=0
    mix_rough = nt.nodes.new("ShaderNodeMix")
    mix_rough.data_type = "FLOAT"
    mix_rough.inputs["A"].default_value = 0.78
    mix_rough.inputs["B"].default_value = rough
    nt.links.new(sep.outputs["Red"], mix_rough.inputs["Factor"])

    comb_orm = nt.nodes.new("ShaderNodeCombineColor")
    comb_orm.inputs["Blue"].default_value = 0.0
    nt.links.new(sep.outputs["Green"], comb_orm.inputs["Red"])
    nt.links.new(mix_rough.outputs["Result"], comb_orm.inputs["Green"])

    # Thickness: sep.Blue als Graustufe
    comb_thick = nt.nodes.new("ShaderNodeCombineColor")
    nt.links.new(sep.outputs["Blue"], comb_thick.inputs["Red"])
    nt.links.new(sep.outputs["Blue"], comb_thick.inputs["Green"])
    nt.links.new(sep.outputs["Blue"], comb_thick.inputs["Blue"])

    return {
        "mat": mat,
        "nt": nt,
        "emit": emit,
        "basecolor_out": col_out,
        "normal_out": vec_mul.outputs["Vector"],
        "orm_out": comb_orm.outputs["Color"],
        "thick_out": comb_thick.outputs["Color"],
    }


def render_leaf_atlas(tex_dir, size=2048):
    print(f"[BOTANY ATLAS] Erzeuge 3D-Zweig-Atlas ({len(LEAF_CELLS)} Zellen, {size}x{size})...")
    scene = clear_scene()
    dev_label = setup_cycles(scene, samples=4)
    print(f"[BOTANY ATLAS] Cycles Device: {dev_label}")

    mesh = bpy.data.meshes.new("LeafAtlas3D")
    bm = bmesh.new()
    col_layer = bm.loops.layers.color.new("LeafData")

    mat_infos = []
    for idx, cell in enumerate(LEAF_CELLS):
        start_faces = len(bm.faces)
        _build_cell_twig(bm, cell, col_layer)
        bm.faces.ensure_lookup_table()
        for f_i in range(start_faces, len(bm.faces)):
            bm.faces[f_i].material_index = idx
        info = _make_leaf_cell_material(cell)
        mat_infos.append(info)

    bm.to_mesh(mesh)
    bm.free()

    for info in mat_infos:
        mesh.materials.append(info["mat"])

    obj = bpy.data.objects.new("LeafAtlas3D", mesh)
    scene.collection.objects.link(obj)

    # Orthografische Kamera exakt über [0..1] x [0..1]
    cam_data = bpy.data.cameras.new("AtlasCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 1.0
    cam_obj = bpy.data.objects.new("AtlasCam", cam_data)
    cam_obj.location = (0.5, 0.5, 2.0)
    cam_obj.rotation_euler = (0.0, 0.0, 0.0)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_depth = "8"

    def _render_pass(pass_key, filepath, colorspace, rgba):
        for info in mat_infos:
            info["nt"].links.new(info[pass_key], info["emit"].inputs["Color"])
        scene.render.film_transparent = bool(rgba)
        scene.render.image_settings.color_mode = "RGBA" if rgba else "RGB"
        scene.display_settings.display_device = "sRGB"
        scene.view_settings.view_transform = "Raw" if colorspace == "Non-Color" else "Standard"
        scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)

    # Für Normal/ORM/Thickness einen neutralen Hintergrund (Flat Normal 0.5,0.5,1.0; ORM 1.0,0.5,0.0; Thick 0.0)
    world = bpy.data.worlds.new("AtlasWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")

    p_col = os.path.join(tex_dir, "botany_leaf_atlas_baseColor.png")
    _render_pass("basecolor_out", p_col, "sRGB", rgba=True)
    _dilate_leaf_atlas_rgb(p_col, pad_iters=24)

    if bg:
        bg.inputs["Color"].default_value = (0.5, 0.5, 1.0, 1.0)
    p_nrm = os.path.join(tex_dir, "botany_leaf_atlas_normal.png")
    _render_pass("normal_out", p_nrm, "Non-Color", rgba=False)

    if bg:
        bg.inputs["Color"].default_value = (1.0, 0.5, 0.0, 1.0)
    p_orm = os.path.join(tex_dir, "botany_leaf_atlas_orm.png")
    _render_pass("orm_out", p_orm, "Non-Color", rgba=False)

    if bg:
        bg.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0)
    p_thk = os.path.join(tex_dir, "botany_leaf_atlas_thickness.png")
    _render_pass("thick_out", p_thk, "Non-Color", rgba=False)

    print(f"[BOTANY ATLAS] Blatt-Atlas gespeichert: {p_col}, {p_nrm}, {p_orm}, {p_thk}")
    return p_col, p_nrm, p_orm, p_thk


def _dilate_leaf_atlas_rgb(filepath, pad_iters=24):
    """Dilation auf transparentem Leaf-Atlas: verhindert schwarze RGB=(0,0,0) Mipmap-Saeume in WebGL."""
    import numpy as np
    img = bpy.data.images.load(filepath, check_existing=False)
    w, h = img.size[0], img.size[1]
    arr = np.array(img.pixels[:], dtype=np.float32).reshape((h, w, 4))
    rgb = arr[:, :, :3].copy()
    alpha = arr[:, :, 3].copy()
    valid = alpha > 0.04

    # Erst volle Nachbar-Dilation ueber pad_iters Iterationen (entfernt schwarzen Alpha-Bleed komplett)
    for _ in range(pad_iters):
        if valid.all():
            break
        acc = np.zeros_like(rgb)
        cnt = np.zeros((h, w), dtype=np.float32)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            sr0, sr1 = max(0, -dy), h - max(0, dy)
            dr0, dr1 = max(0, dy), h - max(0, -dy)
            sc0, sc1 = max(0, -dx), w - max(0, dx)
            dc0, dc1 = max(0, dx), w - max(0, -dx)
            m = valid[sr0:sr1, sc0:sc1]
            acc[dr0:dr1, dc0:dc1][m] += rgb[sr0:sr1, sc0:sc1][m]
            cnt[dr0:dr1, dc0:dc1][m] += 1.0
        fill = (~valid) & (cnt > 0.0)
        if not fill.any():
            break
        rgb[fill] = acc[fill] / cnt[fill, None]
        valid[fill] = True

    # Restliche Hintergrund-Texel je 5x4 Atlas-Zelle mit dem jeweiligen mittleren Laub-RGB fuellen
    if not valid.all():
        cw, ch = w // 5, h // 4
        for row in range(4):
            y0, y1 = row * ch, (row + 1) * ch if row < 3 else h
            for col in range(5):
                x0, x1 = col * cw, (col + 1) * cw if col < 4 else w
                cmask = valid[y0:y1, x0:x1]
                mean_col = rgb[y0:y1, x0:x1][cmask].mean(axis=0) if cmask.any() else np.array([0.32, 0.45, 0.24], dtype=np.float32)
                empty = ~cmask
                rgb[y0:y1, x0:x1][empty] = mean_col

    # Semitransparente Randpixel auf volle Laub-Sattigung ent-premultiplizieren (falls Blender leicht abgedunkelt hat)
    edge = (alpha > 0.02) & (alpha < 0.98)
    if edge.any():
        # Begrenzt aufhellen statt Rauschen zu verstaerken
        pass

    arr[:, :, :3] = np.clip(rgb, 0.0, 1.0)
    arr[:, :, 3] = np.clip(alpha, 0.0, 1.0)
    img.pixels.foreach_set(arr.ravel())
    img.save()
    bpy.data.images.remove(img)


def main():
    t0 = time.time()
    root = get_project_root()
    tex_dir = os.path.join(root, "assets", "textures")
    os.makedirs(tex_dir, exist_ok=True)

    bake_bark_trim_sheet(tex_dir, size_x=2048, size_y=1024)
    render_leaf_atlas(tex_dir, size=2048)

    dt = time.time() - t0
    print(f"[BOTANY ATLAS] Alle 7 Master-Texturen (2048x1024 Bark, 2048x2048 Leaf) fertig in {dt:.2f} s!")


if __name__ == "__main__":
    main()
