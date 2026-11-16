"""
build_botany_trees.py — Parametrischer Blender-Baum-Generator für das ARCHE Botanik-Wald-Kit
==========================================================================================
Erzeugt für alle 6 Baumarten des Vorderen Orients jeweils 15 echte Geometrie-Variationen
über 4 biologische Altersstadien (insgesamt 90 Baum-Varianten + 90 LOD1-Varianten = 180 Meshes):
  - Arten: cedar, cypress, oak, hornbeam, palm, acacia
  - Stadien: sapling (3x, 1.5-4m), young (4x, 5-10m), mature (4x, 11-18m), ancient (4x, 18-26m)
  - Material-Slot 0 = Bark (botany_bark_trim_*), Material-Slot 1 = Foliage (botany_leaf_atlas_*)
  - Vertex Color 'Col_Wind': R=Wind-Biegegewicht, G=Ast-Flatterphase, B=Kronen-AO
  - LOD0 (~1.200-3.200 Tris) & LOD1 (~350-700 Tris, silhouettentreu!)
  - Export: 6 gebündelte .glb in assets/glb/botany/trees_<species>.glb
            6 editierbare .blend in assets/blend/botany/trees_<species>.blend
  - Registry: Aktualisiert assets/manifest.json
  - Preview: Rendert assets/previews/botany_showcase.png (6 Arten x 4 Stadien)

Ausführung:
  blender --background --python assets/scripts/build_botany_trees.py
"""

import os
import sys
import json
import math
import time
import random
import datetime
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler


SPECIES_LIST = [
    "cedar", "cypress", "oak", "hornbeam", "palm", "acacia",
    "olive", "fig", "poplar", "terebinth",
]

# Bark-Trim-Streifen-Index (0..9) passend zu build_botany_atlas.py
BARK_STRIP_INDEX = {
    "cedar": 0,
    "cypress": 1,
    "oak": 2,
    "hornbeam": 3,
    "palm": 4,
    "acacia": 5,
    "olive": 6,
    "fig": 7,
    "poplar": 8,
    "terebinth": 9,
}

# Leaf-Atlas-Zellen (5x4 Raster: col 0..4, row 0..3 von oben links)
LEAF_CELL_MAP = {
    "cedar":     {"young": (0, 0), "mature": (1, 0)},
    "cypress":   {"young": (2, 0), "mature": (3, 0)},
    "oak":       {"young": (4, 0), "mature": (0, 1)},
    "hornbeam":  {"young": (1, 1), "mature": (2, 1)},
    "palm":      {"young": (3, 1), "mature": (4, 1)},
    "acacia":    {"young": (0, 2), "mature": (1, 2)},
    "olive":     {"young": (2, 2), "mature": (3, 2)},
    "fig":       {"young": (4, 2), "mature": (0, 3)},
    "poplar":    {"young": (1, 3), "mature": (2, 3)},
    "terebinth": {"young": (3, 3), "mature": (4, 3)},
}

# SSS-Farben für manifest.json (warmes Laub-Gegenlicht)
SPECIES_SSS = {
    "cedar":     ([0.22, 0.56, 0.14], 0.45),
    "cypress":   ([0.20, 0.52, 0.16], 0.40),
    "oak":       ([0.34, 0.60, 0.14], 0.50),
    "hornbeam":  ([0.36, 0.62, 0.16], 0.52),
    "palm":      ([0.36, 0.62, 0.16], 0.55),
    "acacia":    ([0.38, 0.58, 0.16], 0.50),
    "olive":     ([0.34, 0.48, 0.24], 0.46),
    "fig":       ([0.32, 0.58, 0.14], 0.52),
    "poplar":    ([0.38, 0.62, 0.16], 0.56),
    "terebinth": ([0.34, 0.54, 0.15], 0.50),
}

# 15 Varianten pro Art über 4 biologische Altersstadien
STAGE_SPECS = [
    ("sapling", 3, (1.7, 3.8)),
    ("young",   4, (5.5, 9.6)),
    ("mature",  4, (11.5, 17.5)),
    ("ancient", 4, (18.5, 25.5)),
]


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


def setup_cycles_gpu(scene, samples=32):
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
        scene.cycles.use_denoising = True
        if hasattr(scene.cycles, "denoiser"):
            try:
                scene.cycles.denoiser = "OPENIMAGEDENOISE"
            except Exception:
                pass
        scene.cycles.transparent_max_bounces = 12
    return "CUDA (GPU)" if used_gpu else "CPU"


def _load_image(path, colorspace="sRGB"):
    img = bpy.data.images.load(path, check_existing=True)
    img.colorspace_settings.name = colorspace
    return img


def create_botany_materials(tex_dir):
    """Erstellt die zwei gemeinsamen Master-Materialien: Slot 0 = Bark, Slot 1 = Foliage."""
    # --- Material 0: Bark ---
    mat_bark = bpy.data.materials.new(name="Bark")
    mat_bark.use_nodes = True
    nt_b = mat_bark.node_tree
    nt_b.nodes.clear()

    out_b = nt_b.nodes.new("ShaderNodeOutputMaterial")
    bsdf_b = nt_b.nodes.new("ShaderNodeBsdfPrincipled")
    nt_b.links.new(bsdf_b.outputs["BSDF"], out_b.inputs["Surface"])

    t_bcol = nt_b.nodes.new("ShaderNodeTexImage")
    t_bcol.image = _load_image(os.path.join(tex_dir, "botany_bark_trim_baseColor.png"), "sRGB")
    t_bcol.extension = "REPEAT"
    nt_b.links.new(t_bcol.outputs["Color"], bsdf_b.inputs["Base Color"])

    t_bnrm = nt_b.nodes.new("ShaderNodeTexImage")
    t_bnrm.image = _load_image(os.path.join(tex_dir, "botany_bark_trim_normal.png"), "Non-Color")
    t_bnrm.extension = "REPEAT"
    nrm_b = nt_b.nodes.new("ShaderNodeNormalMap")
    nrm_b.inputs["Strength"].default_value = 0.85
    nt_b.links.new(t_bnrm.outputs["Color"], nrm_b.inputs["Color"])
    nt_b.links.new(nrm_b.outputs["Normal"], bsdf_b.inputs["Normal"])

    t_borm = nt_b.nodes.new("ShaderNodeTexImage")
    t_borm.image = _load_image(os.path.join(tex_dir, "botany_bark_trim_orm.png"), "Non-Color")
    t_borm.extension = "REPEAT"
    sep_borm = nt_b.nodes.new("ShaderNodeSeparateColor")
    nt_b.links.new(t_borm.outputs["Color"], sep_borm.inputs["Color"])
    nt_b.links.new(sep_borm.outputs["Green"], bsdf_b.inputs["Roughness"])
    bsdf_b.inputs["Metallic"].default_value = 0.0

    # --- Material 1: Foliage ---
    mat_fol = bpy.data.materials.new(name="Foliage")
    mat_fol.use_nodes = True
    mat_fol.alpha_threshold = 0.42
    if hasattr(mat_fol, "blend_method"):
        mat_fol.blend_method = "CLIP"
    nt_f = mat_fol.node_tree
    nt_f.nodes.clear()

    out_f = nt_f.nodes.new("ShaderNodeOutputMaterial")
    bsdf_f = nt_f.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_f.inputs["Metallic"].default_value = 0.0
    if "Subsurface Weight" in bsdf_f.inputs:
        bsdf_f.inputs["Subsurface Weight"].default_value = 0.25
    nt_f.links.new(bsdf_f.outputs["BSDF"], out_f.inputs["Surface"])

    t_fcol = nt_f.nodes.new("ShaderNodeTexImage")
    t_fcol.image = _load_image(os.path.join(tex_dir, "botany_leaf_atlas_baseColor.png"), "sRGB")
    t_fcol.extension = "CLIP"

    # Kronen-AO aus Col_Wind.B leicht in BaseColor einmultiplizieren für tiefe Baumkronen
    attr_w = nt_f.nodes.new("ShaderNodeAttribute")
    attr_w.attribute_name = "Col_Wind"
    sep_w = nt_f.nodes.new("ShaderNodeSeparateColor")
    nt_f.links.new(attr_w.outputs["Color"], sep_w.inputs["Color"])

    map_ao = nt_f.nodes.new("ShaderNodeMapRange")
    map_ao.inputs["From Min"].default_value = 0.0
    map_ao.inputs["From Max"].default_value = 1.0
    map_ao.inputs["To Min"].default_value = 0.55
    map_ao.inputs["To Max"].default_value = 1.05
    nt_f.links.new(sep_w.outputs["Blue"], map_ao.inputs["Value"])

    mix_ao = nt_f.nodes.new("ShaderNodeMix")
    mix_ao.data_type = "RGBA"
    mix_ao.blend_type = "MULTIPLY"
    mix_ao.inputs[0].default_value = 0.65
    rgba_ins = [s for s in mix_ao.inputs if s.type == "RGBA"]
    rgba_outs = [s for s in mix_ao.outputs if s.type == "RGBA"]
    nt_f.links.new(t_fcol.outputs["Color"], rgba_ins[0])
    nt_f.links.new(map_ao.outputs["Result"], rgba_ins[1])

    nt_f.links.new(rgba_outs[0], bsdf_f.inputs["Base Color"])
    nt_f.links.new(t_fcol.outputs["Alpha"], bsdf_f.inputs["Alpha"])

    t_fnrm = nt_f.nodes.new("ShaderNodeTexImage")
    t_fnrm.image = _load_image(os.path.join(tex_dir, "botany_leaf_atlas_normal.png"), "Non-Color")
    t_fnrm.extension = "CLIP"
    nrm_f = nt_f.nodes.new("ShaderNodeNormalMap")
    nrm_f.inputs["Strength"].default_value = 0.65
    nt_f.links.new(t_fnrm.outputs["Color"], nrm_f.inputs["Color"])
    nt_f.links.new(nrm_f.outputs["Normal"], bsdf_f.inputs["Normal"])

    t_form = nt_f.nodes.new("ShaderNodeTexImage")
    t_form.image = _load_image(os.path.join(tex_dir, "botany_leaf_atlas_orm.png"), "Non-Color")
    t_form.extension = "CLIP"
    sep_form = nt_f.nodes.new("ShaderNodeSeparateColor")
    nt_f.links.new(t_form.outputs["Color"], sep_form.inputs["Color"])
    nt_f.links.new(sep_form.outputs["Green"], bsdf_f.inputs["Roughness"])

    return mat_bark, mat_fol


# ==============================================================================
# GEOMETRIE-BAUSTEINE (STAMM, WURZELANLÄUFE, ÄSTE, FOLIAGE-CARDS)
# ==============================================================================
def _get_bark_u_bounds(species):
    idx = BARK_STRIP_INDEX[species]
    w = 1.0 / 10.0
    pad = w * 0.06  # 6% Randabstand gegen Streifen-Bleed
    return idx * w + pad, (idx + 1) * w - pad


def _get_leaf_uv_bounds(species, is_young):
    col, row = LEAF_CELL_MAP[species]["young" if is_young else "mature"]
    cw = 1.0 / 5.0
    ch = 1.0 / 4.0
    u0 = col * cw + cw * 0.03
    u1 = (col + 1) * cw - cw * 0.03
    v1 = 1.0 - row * ch - ch * 0.02
    v0 = 1.0 - (row + 1) * ch + ch * 0.02
    return u0, u1, v0, v1


def _add_tube(
    bm,
    pts,
    radii,
    sides,
    uv_layer,
    col_layer,
    species,
    tree_height,
    phase_val,
    root_flare=0.0,
    flare_lobes=5,
    rng=None,
):
    """Erzeugt einen verjüngten Ast-/Stammabschnitt mit ping-pong UV im Rindenstreifen & Col_Wind."""
    u_min, u_max = _get_bark_u_bounds(species)
    n_pts = len(pts)
    if n_pts < 2:
        return

    rings = []
    v_acc = 0.0
    v_vals = [0.0]
    for i in range(1, n_pts):
        v_acc += (pts[i] - pts[i - 1]).length * 0.45
        v_vals.append(v_acc)

    prev_side = None
    for i in range(n_pts):
        p = pts[i]
        r = radii[i]
        if i < n_pts - 1:
            tang = (pts[i + 1] - p)
        else:
            tang = (p - pts[i - 1])
        if tang.length < 1e-6:
            tang = Vector((0.0, 0.0, 1.0))
        tang.normalize()

        if prev_side is None:
            ref = Vector((1.0, 0.0, 0.0)) if abs(tang.x) < 0.85 else Vector((0.0, 1.0, 0.0))
            side = tang.cross(ref).normalized()
        else:
            side = prev_side - tang * prev_side.dot(tang)
            if side.length < 1e-5:
                ref = Vector((1.0, 0.0, 0.0)) if abs(tang.x) < 0.85 else Vector((0.0, 1.0, 0.0))
                side = tang.cross(ref)
            side.normalize()
        prev_side = side
        ortho = tang.cross(side).normalized()

        ring = []
        t_len = i / max(1, n_pts - 1)
        for s in range(sides):
            ang = 2.0 * math.pi * s / sides
            r_mod = r
            if root_flare > 0.0 and p.z < tree_height * 0.16:
                flare_t = max(0.0, 1.0 - p.z / max(0.25, tree_height * 0.16))
                lobe = 0.5 + 0.5 * math.cos(ang * flare_lobes + 0.4)
                r_mod *= 1.0 + root_flare * (flare_t ** 1.7) * (0.35 + 0.85 * lobe)

            pos = p + (side * math.cos(ang) + ortho * math.sin(ang)) * r_mod
            if p.z < 0.0:
                pos.z = 0.0
            v = bm.verts.new(pos)
            ring.append(v)
        rings.append(ring)

    for i in range(n_pts - 1):
        ra = rings[i]
        rb = rings[i + 1]
        va = v_vals[i]
        vb = v_vals[i + 1]
        za = pts[i].z
        zb = pts[i + 1].z
        wa = min(1.0, max(0.0, (za / max(0.5, tree_height)) ** 1.35))
        wb = min(1.0, max(0.0, (zb / max(0.5, tree_height)) ** 1.35))
        ao_a = 0.42 + 0.35 * min(1.0, za / max(0.5, tree_height))
        ao_b = 0.42 + 0.35 * min(1.0, zb / max(0.5, tree_height))

        for s in range(sides):
            sn = (s + 1) % sides
            # Ping-Pong U innerhalb des Rinden-Streifens -> nahtlos ohne Bleed!
            f0 = s / sides
            f1 = (s + 1) / sides
            u0 = u_min + (u_max - u_min) * (1.0 - abs(2.0 * f0 - 1.0))
            u1 = u_min + (u_max - u_min) * (1.0 - abs(2.0 * f1 - 1.0))

            f = bm.faces.new((ra[s], ra[sn], rb[sn], rb[s]))
            f.material_index = 0
            f.smooth = True

            uvs = [(u0, va), (u1, va), (u1, vb), (u0, vb)]
            winds = [wa, wa, wb, wb]
            aos = [ao_a, ao_a, ao_b, ao_b]
            for loop, uv_c, w_c, ao_c in zip(f.loops, uvs, winds, aos):
                loop[uv_layer].uv = uv_c
                loop[col_layer] = (w_c, phase_val, ao_c, 1.0)


def _add_foliage_cluster(
    bm,
    center,
    aim_dir,
    size_w,
    size_h,
    uv_layer,
    col_layer,
    species,
    is_young,
    tree_height,
    crown_center,
    crown_radius,
    phase_val,
    rng,
    lod_level=0,
    arch_drop=0.22,
):
    """
    Erzeugt gewölbte 3D-Blatt-Karten-Büschel über alle 4 LODs:
    - LOD0: 2×2-Segment geschwungene Micro-Blattkarten (feiner, 5×+ höher aufgelöst!)
    - LOD1: 2 gekreuzte gebogene 2-Segment-Karten
    - LOD2: 2 gekreuzte 1-Quad-Karten
    - LOD3: 2 gekreuzte Makro-Silhouetten-Karten für Horizont (650-3000m)
    """
    u0, u1, v0, v1 = _get_leaf_uv_bounds(species, is_young)
    d = aim_dir.normalized()
    up = Vector((0.0, 0.0, 1.0))
    side = d.cross(up)
    if side.length < 1e-4:
        side = Vector((1.0, 0.0, 0.0))
    side.normalize()
    ortho = side.cross(d).normalized()

    dist_c = (center - crown_center).length
    ao_val = min(1.0, max(0.26, 0.32 + 0.68 * (dist_c / max(0.5, crown_radius))))
    wind_w = min(1.0, max(0.15, (center.z / max(0.5, tree_height)) ** 1.15))

    if lod_level == 0:
        size_w *= 0.58
        size_h *= 0.58
        card_angles = (0.0, 1.32)
    elif lod_level == 1:
        size_w *= 0.78
        size_h *= 0.78
        card_angles = (0.0, 1.24)
    elif lod_level == 2:
        size_w *= 1.24
        size_h *= 1.20
        card_angles = (0.0, 1.35)
    else:
        size_w *= 1.75
        size_h *= 1.65
        card_angles = (0.0, 1.57)

    for rot_a in card_angles:
        ca = math.cos(rot_a)
        sa = math.sin(rot_a)
        c_side = (side * ca + ortho * sa).normalized()
        c_norm = d.cross(c_side).normalized()

        arch = size_h * arch_drop
        hw = size_w * 0.5
        p_bot = center - d * (size_h * 0.14)
        p_mid = center + d * (size_h * 0.46) + c_norm * arch
        p_top = center + d * (size_h * 0.96) - c_norm * (arch * 0.42)

        if lod_level == 0:
            # 2x2 Gitter mit mittiger Quer-Wölbung (8 Tris pro Karte -> 24 Tris pro Spray!)
            um = 0.5 * (u0 + u1)
            vmid = 0.5 * (v0 + v1)
            cup = hw * 0.16
            v00 = bm.verts.new(p_bot - c_side * hw)
            v01 = bm.verts.new(p_bot + c_norm * (cup * 0.5))
            v02 = bm.verts.new(p_bot + c_side * hw)
            v10 = bm.verts.new(p_mid - c_side * (hw * 1.04))
            v11 = bm.verts.new(p_mid + c_norm * cup)
            v12 = bm.verts.new(p_mid + c_side * (hw * 1.04))
            v20 = bm.verts.new(p_top - c_side * (hw * 0.84))
            v21 = bm.verts.new(p_top + c_norm * (cup * 0.4))
            v22 = bm.verts.new(p_top + c_side * (hw * 0.84))
            grid = [
                ((v00, v01, v11, v10), [(u0, v0), (um, v0), (um, vmid), (u0, vmid)], wind_w * 0.92, wind_w),
                ((v01, v02, v12, v11), [(um, v0), (u1, v0), (u1, vmid), (um, vmid)], wind_w * 0.92, wind_w),
                ((v10, v11, v21, v20), [(u0, vmid), (um, vmid), (um, v1), (u0, v1)], wind_w, min(1.0, wind_w * 1.08)),
                ((v11, v12, v22, v21), [(um, vmid), (u1, vmid), (u1, v1), (um, v1)], wind_w, min(1.0, wind_w * 1.08)),
            ]
            for verts, uvs, w_a, w_b in grid:
                f = bm.faces.new(verts)
                f.material_index = 1
                f.smooth = True
                for loop, uvc, wc in zip(f.loops, uvs, (w_a, w_a, w_b, w_b)):
                    loop[uv_layer].uv = uvc
                    loop[col_layer] = (min(1.0, wc), phase_val, ao_val, 1.0)
        elif lod_level == 1:
            # LOD1: 2 vertikale Segmente (4 Tris pro Karte)
            v00 = bm.verts.new(p_bot - c_side * hw)
            v01 = bm.verts.new(p_bot + c_side * hw)
            v10 = bm.verts.new(p_mid - c_side * (hw * 1.05))
            v11 = bm.verts.new(p_mid + c_side * (hw * 1.05))
            v20 = bm.verts.new(p_top - c_side * (hw * 0.85))
            v21 = bm.verts.new(p_top + c_side * (hw * 0.85))
            vmid = 0.5 * (v0 + v1)
            for verts, uvs, w_list in [
                ((v00, v01, v11, v10), [(u0, v0), (u1, v0), (u1, vmid), (u0, vmid)], [wind_w * 0.9, wind_w * 0.9, wind_w, wind_w]),
                ((v10, v11, v21, v20), [(u0, vmid), (u1, vmid), (u1, v1), (u0, v1)], [wind_w, wind_w, min(1.0, wind_w * 1.08), min(1.0, wind_w * 1.08)]),
            ]:
                f = bm.faces.new(verts)
                f.material_index = 1
                f.smooth = True
                for loop, uvc, wc in zip(f.loops, uvs, w_list):
                    loop[uv_layer].uv = uvc
                    loop[col_layer] = (min(1.0, wc), phase_val, ao_val, 1.0)
        else:
            # LOD2 / LOD3: 1 Quad = 2 Tris pro Karte
            vb0 = bm.verts.new(p_bot - c_side * hw)
            vb1 = bm.verts.new(p_bot + c_side * hw)
            vt1 = bm.verts.new(p_top + c_side * (hw * 0.9))
            vt0 = bm.verts.new(p_top - c_side * (hw * 0.9))
            f = bm.faces.new((vb0, vb1, vt1, vt0))
            f.material_index = 1
            f.smooth = True
            for loop, uvc in zip(f.loops, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]):
                loop[uv_layer].uv = uvc
                loop[col_layer] = (wind_w, phase_val, ao_val, 1.0)


def _add_palm_frond_card(
    bm,
    base,
    yaw,
    pitch,
    length,
    width,
    droop,
    uv_layer,
    col_layer,
    is_young,
    tree_height,
    phase_val,
    lod_level=0,
):
    """Erzeugt einen gebogenen Palmen-Fächerwedel mit V-Querschnitt."""
    u0, u1, v0, v1 = _get_leaf_uv_bounds("palm", is_young)
    segs = {0: 6, 1: 3, 2: 2, 3: 1}.get(lod_level, 2)
    fwd = Vector((math.cos(yaw) * math.cos(pitch), math.sin(yaw) * math.cos(pitch), math.sin(pitch))).normalized()
    side = Vector((-math.sin(yaw), math.cos(yaw), 0.0)).normalized()

    rows = []
    for i in range(segs + 1):
        t = i / segs
        p = base + fwd * (length * t) + Vector((0.0, 0.0, -droop * (t ** 2.1)))
        w = width * 0.5 * (0.45 + 0.65 * math.sin(math.pi * (t ** 0.75)))
        v_z = -w * 0.22
        vl = bm.verts.new(p - side * w + Vector((0.0, 0.0, v_z)))
        vm = bm.verts.new(p)
        vr = bm.verts.new(p + side * w + Vector((0.0, 0.0, v_z)))
        rows.append((vl, vm, vr, t))

    for i in range(segs):
        vl0, vm0, vr0, t0 = rows[i]
        vl1, vm1, vr1, t1 = rows[i + 1]
        vt0 = v0 + (v1 - v0) * t0
        vt1 = v0 + (v1 - v0) * t1
        um = 0.5 * (u0 + u1)
        w0 = min(1.0, 0.70 + 0.30 * t0)
        w1 = min(1.0, 0.70 + 0.30 * t1)
        ao0 = 0.45 + 0.45 * t0
        ao1 = 0.45 + 0.45 * t1

        fl = bm.faces.new((vl0, vm0, vm1, vl1))
        fl.material_index = 1
        fl.smooth = True
        for loop, uvc, wc, aoc in zip(fl.loops, [(u0, vt0), (um, vt0), (um, vt1), (u0, vt1)], [w0, w0, w1, w1], [ao0, ao0, ao1, ao1]):
            loop[uv_layer].uv = uvc
            loop[col_layer] = (wc, phase_val, aoc, 1.0)

        fr = bm.faces.new((vm0, vr0, vr1, vm1))
        fr.material_index = 1
        fr.smooth = True
        for loop, uvc, wc, aoc in zip(fr.loops, [(um, vt0), (u1, vt0), (u1, vt1), (um, vt1)], [w0, w0, w1, w1], [ao0, ao0, ao1, ao1]):
            loop[uv_layer].uv = uvc
            loop[col_layer] = (wc, phase_val, aoc, 1.0)


# ==============================================================================
# ARTTYPISCHE PARAMETRISCHE ARCHITEKTUREN (6 ARTEN x 4 ALTERSSTADIEN)
# ==============================================================================
def _spline_pts(p0, p1, bend_vec, n_segs):
    pts = []
    for i in range(n_segs + 1):
        t = i / n_segs
        p = p0.lerp(p1, t) + bend_vec * math.sin(math.pi * t)
        pts.append(p)
    return pts


def generate_tree_bmesh(species, stage, var_idx, height, seed, lod_level=0):
    rng = random.Random(seed)
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    col_layer = bm.loops.layers.color.new("Col_Wind")

    stage_idx = {"sapling": 0, "young": 1, "mature": 2, "ancient": 3}[stage]
    young_prob = {0: 0.85, 1: 0.60, 2: 0.30, 3: 0.20}[stage_idx]
    root_flare = {0: 0.15, 1: 0.35, 2: 0.65, 3: 1.10}[stage_idx]

    # --- LOD3: Ultra-kompakter Horizont-Proxy (40-120 Tris fuer 680..3000m!) ---
    if lod_level == 3:
        r_b = height * (0.028 if species in ("palm", "cypress", "poplar") else 0.044)
        lean_v = Vector((rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), 0.0)) * (height * 0.08)
        t_h = height * (0.82 if species == "palm" else 0.72)
        t_pts = [Vector((0.0, 0.0, 0.0)), lean_v * 0.4 + Vector((0.0, 0.0, t_h * 0.5)), lean_v + Vector((0.0, 0.0, t_h))]
        _add_tube(bm, t_pts, [r_b, r_b * 0.62, r_b * 0.22], 3, uv_layer, col_layer, species, height, 0.15, rng=rng)
        c_top = t_pts[-1]
        if species == "palm":
            for k in range(6):
                ang = k * (math.pi / 3.0) + var_idx * 0.4
                _add_palm_frond_card(bm, c_top, ang, 0.18, height * 0.28, height * 0.16, height * 0.11,
                                     uv_layer, col_layer, (k % 2 == 0), height, 0.5, lod_level=3)
        else:
            c_z = height * (0.58 if species in ("cypress", "poplar") else 0.72)
            c_w = height * (0.19 if species in ("cypress", "poplar") else (0.48 if species in ("acacia", "fig", "cedar") else 0.36))
            c_h = height * (0.46 if species in ("cypress", "poplar") else 0.26)
            n_m = 3 if species in ("cedar", "oak", "fig", "acacia", "terebinth") else 2
            for mi in range(n_m):
                mang = (2.0 * math.pi * mi / n_m) + rng.uniform(-0.2, 0.2)
                off_r = c_w * (0.28 if n_m > 2 else 0.12)
                c_pos = Vector((lean_v.x + math.cos(mang) * off_r, lean_v.y + math.sin(mang) * off_r, c_z + mi * height * 0.04))
                _add_foliage_cluster(
                    bm, c_pos, Vector((math.cos(mang) * 0.2, math.sin(mang) * 0.2, 0.95)),
                    c_w, c_h, uv_layer, col_layer, species, (mi % 2 == 0), height,
                    Vector((0, 0, c_z)), c_w, rng.random(), rng, lod_level=3, arch_drop=0.14,
                )
        return bm

    trunk_sides = {0: 10, 1: 7, 2: 5}.get(lod_level, 5)
    branch_sides = {0: 6, 1: 5, 2: 3}.get(lod_level, 4)

    # --- PALME (gebogener Stamm + feine Faecherwedel in 4 LODs) ---
    if species == "palm":
        r_base = height * (0.024 if stage_idx == 0 else 0.028)
        lean_ang = rng.uniform(0.0, 2.0 * math.pi)
        lean_amt = height * rng.uniform(0.06, 0.22)
        curve_dir = Vector((math.cos(lean_ang), math.sin(lean_ang), 0.0))

        segs = {0: 18, 1: 10, 2: 6}.get(lod_level, 6)
        p_sides = {0: 10, 1: 7, 2: 5}.get(lod_level, 5)
        pts, radii = [], []
        for i in range(segs + 1):
            t = i / segs
            offset = curve_dir * (lean_amt * (t ** 1.4) + 0.12 * lean_amt * math.sin(t * math.pi))
            pts.append(Vector((offset.x, offset.y, height * 0.82 * t)))
            radii.append(r_base * (1.0 - 0.48 * (t ** 0.7)))

        _add_tube(bm, pts, radii, p_sides, uv_layer, col_layer, "palm", height, 0.15,
                  root_flare=root_flare * 0.65, flare_lobes=6, rng=rng)

        crown_top = pts[-1]
        n_fronds = ({0: 72, 1: 38, 2: 18}[lod_level]) if stage_idx < 2 else ({0: 88, 1: 46, 2: 22}[lod_level])
        frond_len = height * (0.30 if stage_idx == 0 else 0.26)
        for i in range(n_fronds):
            ring_t = i / max(1, n_fronds - 1)
            yaw = i * 2.39996 + rng.uniform(-0.12, 0.12)
            pitch = rng.uniform(-0.10, 0.88) if ring_t > 0.25 else rng.uniform(-0.48, -0.10)
            flen = frond_len * rng.uniform(0.84, 1.22) * (1.0 - 0.18 * max(0.0, pitch))
            fwid = flen * ({0: 0.22, 1: 0.30, 2: 0.42}[lod_level])
            droop = flen * rng.uniform(0.28, 0.55)
            _add_palm_frond_card(
                bm, crown_top, yaw, pitch, flen, fwid, droop,
                uv_layer, col_layer, (rng.random() < young_prob or pitch > 0.45),
                height, rng.uniform(0.1, 0.95), lod_level=lod_level,
            )
        n_heart = {0: 18, 1: 10, 2: 5}[lod_level]
        for k in range(n_heart):
            yaw = k * (2.0 * math.pi / n_heart) + 0.2
            _add_foliage_cluster(
                bm, crown_top + Vector((math.cos(yaw) * 0.25, math.sin(yaw) * 0.25, 0.18)),
                Vector((math.cos(yaw), math.sin(yaw), 0.40)),
                frond_len * 0.68, frond_len * 0.92, uv_layer, col_layer, "palm",
                True, height, crown_top, frond_len, rng.random(), rng, lod_level=lod_level, arch_drop=0.25,
            )
        return bm

    # --- ALLGEMEINE STAMM- & AST-ARCHITEKTUR FUER ALLE 9 KRONENARTEN ---
    if species == "cypress":
        r_base = height * 0.025
        trunk_h = height * 0.92
        lean = Vector((rng.uniform(-0.15, 0.15), rng.uniform(-0.15, 0.15), 0.0))
    elif species == "poplar":
        r_base = height * 0.029
        trunk_h = height * 0.88
        lean = Vector((rng.uniform(-0.35, 0.35), rng.uniform(-0.35, 0.35), 0.0))
    elif species == "cedar":
        r_base = height * (0.036 if stage_idx < 2 else 0.048)
        trunk_h = height * (0.86 if stage_idx < 2 else 0.82)
        lean = Vector((rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), 0.0))
    elif species == "oak":
        r_base = height * (0.040 if stage_idx < 2 else 0.056)
        trunk_h = height * (0.58 if stage_idx >= 2 else 0.72)
        lean = Vector((rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8), 0.0))
    elif species == "fig":
        r_base = height * (0.046 if stage_idx < 2 else 0.064)
        trunk_h = height * 0.46
        lean = Vector((rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), 0.0))
    elif species == "olive":
        r_base = height * (0.044 if stage_idx < 2 else 0.062)
        trunk_h = height * 0.48
        lean = Vector((rng.uniform(-0.7, 0.7), rng.uniform(-0.7, 0.7), 0.0))
    elif species == "terebinth":
        r_base = height * (0.038 if stage_idx < 2 else 0.052)
        trunk_h = height * 0.62
        lean = Vector((rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), 0.0))
    elif species == "hornbeam":
        r_base = height * 0.032
        trunk_h = height * 0.68
        lean = Vector((rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), 0.0))
    else:  # acacia
        r_base = height * (0.034 if stage_idx < 2 else 0.044)
        trunk_h = height * (0.60 if stage_idx >= 2 else 0.70)
        lean = Vector((rng.uniform(-0.9, 0.9), rng.uniform(-0.9, 0.9), 0.0))

    n_stems = 1
    if species in ("hornbeam", "olive") and stage_idx >= 1 and (var_idx % 2 == 1 or species == "olive"):
        n_stems = 2 if stage_idx == 1 else 3
    elif species in ("acacia", "fig") and stage_idx >= 2 and var_idx % 2 == 0:
        n_stems = 2

    branch_tips = []  # (pos, dir, card_w, card_h, phase)
    trunk_segs = {0: 12, 1: 8, 2: 5}.get(lod_level, 5)

    for st_i in range(n_stems):
        st_yaw = (2.0 * math.pi * st_i / max(1, n_stems)) + rng.uniform(-0.3, 0.3)
        st_spread = (0.0 if n_stems == 1 else height * (0.18 if species in ("olive", "fig") else 0.14))
        st_top = Vector((
            lean.x + math.cos(st_yaw) * st_spread,
            lean.y + math.sin(st_yaw) * st_spread,
            trunk_h * (1.0 if st_i == 0 else rng.uniform(0.82, 0.94)),
        ))
        st_bend = Vector((rng.uniform(-0.28, 0.28), rng.uniform(-0.28, 0.28), 0.0)) * (height * (0.18 if species == "olive" else 0.12))
        if species in ("cypress", "poplar"):
            st_bend *= 0.25

        t_pts = _spline_pts(Vector((0.0, 0.0, 0.0)), st_top, st_bend, trunk_segs)
        st_r0 = r_base * (1.0 if st_i == 0 else 0.74)
        t_radii = [st_r0 * (1.0 - 0.84 * (i / trunk_segs) ** 0.8) for i in range(trunk_segs + 1)]
        _add_tube(bm, t_pts, t_radii, trunk_sides, uv_layer, col_layer, species, height, 0.1,
                  root_flare=root_flare if st_i == 0 else 0.2, flare_lobes=6 if lod_level == 0 else 5, rng=rng)

        if species == "cedar":
            n_tiers = ({0: 9, 1: 7, 2: 5}[lod_level]) if stage_idx < 2 else ({0: 11, 1: 8, 2: 6}[lod_level])
            for ti in range(n_tiers):
                tt = 0.28 + 0.68 * (ti / max(1, n_tiers - 1))
                p_orig = t_pts[min(len(t_pts) - 1, int(tt * trunk_segs))]
                tier_rad = height * ((0.28 + 0.16 * math.sin(tt * math.pi * 0.85)) if stage_idx >= 2 else (0.34 * (1.0 - 0.65 * tt)))
                branches_in_tier = {0: 5, 1: 4, 2: 3}[lod_level]
                for bi in range(branches_in_tier):
                    ang = (2.0 * math.pi * bi / branches_in_tier) + ti * 0.7 + rng.uniform(-0.25, 0.25)
                    b_len = tier_rad * rng.uniform(0.75, 1.15)
                    z_rise = b_len * (0.28 if stage_idx < 2 else rng.uniform(-0.05, 0.14))
                    b_end = p_orig + Vector((math.cos(ang) * b_len, math.sin(ang) * b_len, z_rise))
                    b_pts = _spline_pts(p_orig, b_end, Vector((0.0, 0.0, -b_len * 0.08)), {0: 4, 1: 3, 2: 2}[lod_level])
                    br0 = st_r0 * 0.32 * (1.0 - 0.4 * tt)
                    _add_tube(bm, b_pts, [br0 * (1.0 - 0.75 * (k / (len(b_pts) - 1))) for k in range(len(b_pts))],
                              branch_sides, uv_layer, col_layer, species, height, rng.random(), rng=rng)
                    ph = rng.random()
                    n_pads = {0: 4, 1: 3, 2: 2}[lod_level]
                    for pi in range(n_pads):
                        pt = 0.42 + 0.58 * (pi / max(1, n_pads - 1))
                        cp = p_orig.lerp(b_end, pt) + Vector((0.0, 0.0, 0.14))
                        if lod_level == 0 and pi >= 1:
                            # Tertiaerer Zweiggabel-Ansatz fuer echte Nahbereichs-Detailtiefe
                            tw_ang = ang + (0.45 if pi % 2 == 0 else -0.45)
                            tw_end = cp + Vector((math.cos(tw_ang), math.sin(tw_ang), 0.12)) * (b_len * 0.28)
                            _add_tube(bm, [cp, tw_end], [br0 * 0.24, br0 * 0.08], 4, uv_layer, col_layer, species, height, ph, rng=rng)
                            cp = tw_end
                        cw = height * ({0: 0.13, 1: 0.15, 2: 0.18}[lod_level])
                        branch_tips.append((cp, Vector((math.cos(ang), math.sin(ang), 0.18)), cw, cw * 0.85, ph))

        elif species in ("cypress", "poplar"):
            is_pop = (species == "poplar")
            n_whorls = ({0: 18, 1: 12, 2: 8}[lod_level]) if stage_idx < 2 else ({0: 22, 1: 14, 2: 9}[lod_level])
            max_rad = height * ((0.22 if is_pop else 0.12) if stage_idx < 2 else (0.25 if is_pop else 0.14))
            for wi in range(n_whorls):
                wt = 0.15 + 0.82 * (wi / max(1, n_whorls - 1))
                p_orig = t_pts[min(len(t_pts) - 1, int(wt * trunk_segs))]
                w_rad = max_rad * math.sin(math.pi * (wt ** 0.65))
                n_b = {0: 6, 1: 4, 2: 3}[lod_level]
                for bi in range(n_b):
                    ang = (2.0 * math.pi * bi / n_b) + wi * 0.85 + rng.uniform(-0.2, 0.2)
                    b_end = p_orig + Vector((math.cos(ang) * w_rad, math.sin(ang) * w_rad, height * (0.18 if is_pop else 0.14)))
                    if lod_level <= 1:
                        _add_tube(bm, [p_orig, b_end], [st_r0 * 0.22, st_r0 * 0.06], 4 if lod_level == 0 else 3,
                                  uv_layer, col_layer, species, height, rng.random(), rng=rng)
                    cw = max(0.50, w_rad * ({0: 1.25, 1: 1.45, 2: 1.95}[lod_level]))
                    ch = height * ({0: 0.13, 1: 0.15, 2: 0.19}[lod_level])
                    branch_tips.append((b_end, Vector((math.cos(ang) * 0.30, math.sin(ang) * 0.30, 1.0)), cw, ch, rng.random()))
            branch_tips.append((st_top, Vector((0.0, 0.0, 1.0)), max_rad * 1.1, height * 0.16, 0.9))

        elif species in ("oak", "fig", "terebinth", "olive"):
            # Breite mediterrane Laubbaeume: Olea niedrig-knorrig, Ficus tief-ausladend, Eiche/Terebinthe maechtig
            is_olive = (species == "olive")
            is_fig = (species == "fig")
            base_limbs = ({0: 9, 1: 7, 2: 5}[lod_level]) if stage_idx < 2 else ({0: 11, 1: 8, 2: 6}[lod_level])
            n_limbs = max(4, int(round(base_limbs / math.sqrt(max(1, n_stems)))))
            spread_k = 0.56 if is_fig else (0.50 if is_olive else 0.44)
            for li in range(n_limbs):
                lt = (0.35 if (is_fig or is_olive) else 0.45) + 0.54 * (li / max(1, n_limbs - 1))
                p_orig = t_pts[min(len(t_pts) - 1, int(lt * trunk_segs))]
                ang = (2.0 * math.pi * li / n_limbs) + st_i * 1.2 + rng.uniform(-0.35, 0.35)
                limb_len = height * rng.uniform(spread_k * 0.78, spread_k * 1.15) * (1.0 - 0.20 * lt)
                pitch = rng.uniform(0.16, 0.52) if is_fig else rng.uniform(0.25, 0.70)
                b_end = p_orig + Vector((math.cos(ang) * math.cos(pitch), math.sin(ang) * math.cos(pitch), math.sin(pitch))) * limb_len
                knar_bend = Vector((rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), rng.uniform(0.08, 0.28))) * limb_len
                b_pts = _spline_pts(p_orig, b_end, knar_bend, {0: 5, 1: 3, 2: 2}[lod_level])
                lr0 = st_r0 * 0.45 * (1.0 - 0.32 * lt)
                _add_tube(bm, b_pts, [lr0 * (1.0 - 0.72 * (k / (len(b_pts) - 1))) for k in range(len(b_pts))],
                          branch_sides, uv_layer, col_layer, species, height, rng.random(), rng=rng)

                n_sub = {0: 4, 1: 3, 2: 2}[lod_level]
                for si in range(n_sub):
                    sang = ang + rng.uniform(-0.85, 0.85)
                    sp_orig = b_pts[max(1, len(b_pts) - 2 + (si % 2))]
                    s_len = limb_len * rng.uniform(0.42, 0.65)
                    s_end = sp_orig + Vector((math.cos(sang) * 0.85, math.sin(sang) * 0.85, rng.uniform(0.18, 0.55))).normalized() * s_len
                    if lod_level <= 1:
                        _add_tube(bm, [sp_orig, s_end], [lr0 * 0.35, lr0 * 0.12], 5 if lod_level == 0 else 4,
                                  uv_layer, col_layer, species, height, rng.random(), rng=rng)
                    cw = height * ({0: 0.17, 1: 0.21, 2: 0.27}[lod_level])
                    if lod_level == 0:
                        for ti in (-1, 0, 1):
                            tang = sang + ti * 0.52
                            t_end = s_end + Vector((math.cos(tang), math.sin(tang), rng.uniform(0.1, 0.45))).normalized() * (s_len * 0.36)
                            _add_tube(bm, [s_end, t_end], [lr0 * 0.14, lr0 * 0.05], 4,
                                      uv_layer, col_layer, species, height, rng.random(), rng=rng)
                            branch_tips.append((t_end, (t_end - s_end).normalized() + Vector((0, 0, 0.30)), cw * 0.88, cw * 0.88, rng.random()))
                    else:
                        branch_tips.append((s_end, (s_end - sp_orig).normalized() + Vector((0, 0, 0.35)), cw, cw, rng.random()))
                        branch_tips.append((sp_orig.lerp(s_end, 0.55), Vector((math.cos(sang), math.sin(sang), 0.55)), cw * 0.95, cw * 0.95, rng.random()))
                cw_main = height * ({0: 0.19, 1: 0.23, 2: 0.29}[lod_level])
                branch_tips.append((b_end, Vector((math.cos(ang), math.sin(ang), 0.45)), cw_main, cw_main, rng.random()))

        elif species == "hornbeam":
            n_limbs = ({0: 9, 1: 7, 2: 5}[lod_level]) if stage_idx == 0 else ({0: 11, 1: 8, 2: 6}[lod_level])
            for li in range(n_limbs):
                lt = 0.38 + 0.58 * (li / max(1, n_limbs - 1))
                p_orig = t_pts[min(len(t_pts) - 1, int(lt * trunk_segs))]
                ang = (2.0 * math.pi * li / n_limbs) + st_i * 1.1 + rng.uniform(-0.3, 0.3)
                limb_len = height * rng.uniform(0.26, 0.40) * (1.05 - 0.32 * lt)
                b_end = p_orig + Vector((math.cos(ang) * 0.65, math.sin(ang) * 0.65, 0.76)).normalized() * limb_len
                b_pts = _spline_pts(p_orig, b_end, Vector((0.0, 0.0, limb_len * 0.12)), {0: 4, 1: 3, 2: 2}[lod_level])
                lr0 = st_r0 * 0.36 * (1.0 - 0.3 * lt)
                _add_tube(bm, b_pts, [lr0 * (1.0 - 0.78 * (k / (len(b_pts) - 1))) for k in range(len(b_pts))],
                          branch_sides, uv_layer, col_layer, species, height, rng.random(), rng=rng)
                n_sub = {0: 4, 1: 3, 2: 2}[lod_level]
                for si in range(n_sub):
                    sp = p_orig.lerp(b_end, 0.35 + 0.62 * (si / max(1, n_sub - 1)))
                    if lod_level == 0:
                        sang = ang + (0.45 if si % 2 == 0 else -0.45)
                        sp2 = sp + Vector((math.cos(sang), math.sin(sang), 0.55)).normalized() * (limb_len * 0.32)
                        _add_tube(bm, [sp, sp2], [lr0 * 0.25, lr0 * 0.08], 4, uv_layer, col_layer, species, height, rng.random(), rng=rng)
                        sp = sp2
                    cw = height * ({0: 0.16, 1: 0.19, 2: 0.24}[lod_level])
                    branch_tips.append((sp, Vector((math.cos(ang) * 0.5, math.sin(ang) * 0.5, 0.75)), cw, cw * 1.10, rng.random()))

        elif species == "acacia":
            n_limbs = ({0: 9, 1: 7, 2: 5}[lod_level]) if stage_idx < 2 else ({0: 12, 1: 9, 2: 6}[lod_level])
            crown_z = height * (0.86 if stage_idx >= 2 else 0.80)
            umbrella_r = height * (0.38 if stage_idx < 2 else 0.56)
            for li in range(n_limbs):
                ang = (2.0 * math.pi * li / n_limbs) + st_i * 0.9 + rng.uniform(-0.22, 0.22)
                p_orig = t_pts[max(1, int(trunk_segs * rng.uniform(0.65, 0.96)))]
                rad = umbrella_r * rng.uniform(0.75, 1.12)
                b_end = Vector((
                    st_top.x + math.cos(ang) * rad,
                    st_top.y + math.sin(ang) * rad,
                    crown_z + rng.uniform(-0.04, 0.05) * height,
                ))
                b_pts = _spline_pts(p_orig, b_end, Vector((math.cos(ang), math.sin(ang), 0.3)) * (height * 0.06), {0: 4, 1: 3, 2: 2}[lod_level])
                lr0 = st_r0 * 0.38
                _add_tube(bm, b_pts, [lr0 * (1.0 - 0.76 * (k / (len(b_pts) - 1))) for k in range(len(b_pts))],
                          branch_sides, uv_layer, col_layer, species, height, rng.random(), rng=rng)
                n_pads = {0: 4, 1: 3, 2: 2}[lod_level]
                for pi in range(n_pads):
                    pt = 0.40 + 0.60 * (pi / max(1, n_pads - 1))
                    cp = p_orig.lerp(b_end, pt)
                    cp.z = crown_z + rng.uniform(-0.03, 0.04) * height
                    cw = height * ({0: 0.18, 1: 0.22, 2: 0.28}[lod_level])
                    branch_tips.append((cp, Vector((math.cos(ang), math.sin(ang), 0.12)), cw, cw * 0.80, rng.random()))

    # Kronen-Zentrum & -Radius für AO-Berechnung
    if branch_tips:
        c_sum = Vector((0.0, 0.0, 0.0))
        for pos, _, _, _, _ in branch_tips:
            c_sum += pos
        crown_center = c_sum / len(branch_tips)
        crown_radius = max(0.8, max((pos - crown_center).length for pos, _, _, _, _ in branch_tips))
    else:
        crown_center = Vector((0.0, 0.0, height * 0.75))
        crown_radius = height * 0.3

    # Feine innere Kronen-Büschel
    if species in ("oak", "hornbeam", "cedar", "acacia", "cypress", "olive", "fig", "poplar", "terebinth"):
        n_core = {0: 5, 1: 4, 2: 3}[lod_level]
        core_w = height * (0.16 if species in ("cypress", "poplar") else (0.19 if species == "cedar" else 0.22))
        if lod_level >= 1:
            core_w *= (1.15 if lod_level == 1 else 1.35)
        core_h = core_w * (1.30 if species in ("cypress", "poplar") else (0.68 if species in ("cedar", "acacia") else 0.90))
        for ci in range(n_core):
            c_ang = (2.0 * math.pi * ci / max(1, n_core)) + rng.uniform(-0.35, 0.35)
            c_off = Vector((math.cos(c_ang) * crown_radius * 0.22, math.sin(c_ang) * crown_radius * 0.22,
                            rng.uniform(-0.14, 0.16) * crown_radius))
            _add_foliage_cluster(
                bm, crown_center + c_off,
                Vector((math.cos(c_ang) * 0.35, math.sin(c_ang) * 0.35, 0.85)),
                core_w, core_h, uv_layer, col_layer,
                species, False, height, crown_center, crown_radius,
                rng.random(), rng, lod_level=lod_level, arch_drop=0.18,
            )

    # Foliage-Cards platzieren (bei LOD0 luftige gestaffelte Zweig-Sprays fuer klare Durchsicht!)
    for pos, aim, cw, ch, ph in branch_tips:
        n_cards = 1 if lod_level >= 2 else 2
        for ci in range(n_cards):
            jitter = Vector((rng.uniform(-0.34, 0.34), rng.uniform(-0.34, 0.34), rng.uniform(-0.16, 0.16))) * cw if ci > 0 else Vector((0, 0, 0))
            c_sc = 0.86 if ci > 0 else 0.96
            _add_foliage_cluster(
                bm, pos + jitter, aim, cw * c_sc, ch * c_sc, uv_layer, col_layer,
                species, (rng.random() < young_prob), height, crown_center, crown_radius,
                ph, rng, lod_level=lod_level, arch_drop=0.20,
            )

    return bm


def create_tree_object(name, species, stage, var_idx, height, seed, mat_bark, mat_fol, lod_level=0):
    bm = generate_tree_bmesh(species, stage, var_idx, height, seed, lod_level=lod_level)

    # Bodenkontakt exakt bei Z = 0.0 & exakte biologische Sollhöhe sichern
    min_z = min((v.co.z for v in bm.verts), default=0.0)
    max_z = max((v.co.z for v in bm.verts), default=height)
    cur_h = max(0.2, max_z - min_z)
    h_scale = height / cur_h
    for v in bm.verts:
        v.co.x *= h_scale
        v.co.y *= h_scale
        v.co.z = (v.co.z - min_z) * h_scale

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    mesh.materials.append(mat_bark)
    mesh.materials.append(mat_fol)

    # Aktive Color Attribute für glTF COLOR_0 Export sichern
    if "Col_Wind" in mesh.color_attributes:
        mesh.color_attributes.active_color = mesh.color_attributes["Col_Wind"]
        mesh.color_attributes.render_color_index = mesh.color_attributes.find("Col_Wind")

    obj = bpy.data.objects.new(name, mesh)
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)

    tri_count = sum(max(1, len(p.vertices) - 2) for p in mesh.polygons)
    return obj, tri_count


def export_species_glb(objs, glb_path):
    os.makedirs(os.path.dirname(glb_path), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]

    rna_props = set(bpy.ops.export_scene.gltf.get_rna_type().properties.keys())
    desired = {
        "filepath": glb_path,
        "export_format": "GLB",
        "use_selection": True,
        "export_yup": True,
        "export_apply": True,
        "export_normals": True,
        "export_tangents": False,
        "export_texcoords": True,
        "export_colors": True,
        "export_vertex_color": "ACTIVE",
        "export_all_vertex_colors": True,
        "export_materials": "EXPORT",
        "export_image_format": "AUTO",
        "export_jpeg_quality": 85,
    }
    safe = {k: v for k, v in desired.items() if k in rna_props}
    bpy.ops.export_scene.gltf(**safe)
    return os.path.getsize(glb_path) / 1024.0


def build_all_species(root):
    tex_dir = os.path.join(root, "assets", "textures")
    glb_dir = os.path.join(root, "assets", "glb", "botany")
    blend_dir = os.path.join(root, "assets", "blend", "botany")
    os.makedirs(glb_dir, exist_ok=True)
    os.makedirs(blend_dir, exist_ok=True)

    summary = {}
    showcase_picks = {}  # (species, stage) -> obj_name

    for sp_idx, species in enumerate(SPECIES_LIST):
        t_sp = time.time()
        scene = clear_scene()
        mat_bark, mat_fol = create_botany_materials(tex_dir)

        created_objs = []
        lod_tris = {0: [], 1: [], 2: [], 3: []}
        variant_meta = []

        for stage, count, (h_min, h_max) in STAGE_SPECS:
            if species == "olive":
                h_min, h_max = h_min * 0.55, h_max * 0.48
            for vi in range(count):
                frac = (vi + 0.5) / count
                height = h_min + (h_max - h_min) * frac
                seed = (sp_idx + 1) * 10000 + hash(stage) % 1000 + vi * 73

                base_name = f"{species}_{stage}_{vi + 1:02d}"
                t_row = {}
                for lod_i in (0, 1, 2, 3):
                    obj_l, t_l = create_tree_object(f"{base_name}_LOD{lod_i}", species, stage, vi, height, seed, mat_bark, mat_fol, lod_level=lod_i)
                    scene.collection.objects.link(obj_l)
                    created_objs.append(obj_l)
                    lod_tris[lod_i].append(t_l)
                    t_row[f"lod{lod_i}Tris"] = t_l
                variant_meta.append({"name": base_name, "stage": stage, "heightM": round(height, 2), **t_row})

                if vi == min(1, count - 1):
                    showcase_picks[(species, stage)] = f"{base_name}_LOD0"

        # Speichere editierbare .blend (mit vollstaendigen Textur-Nodes für Cycles-Showcase)
        blend_path = os.path.join(blend_dir, f"trees_{species}.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)

        # Fuer kompakte .glb-Exporte schwere PNGs aus Material-Nodes loesen (Three.js bindet die Master-Texturen einmalig!)
        for _m, _base in ((mat_bark, (0.30, 0.22, 0.15, 1.0)), (mat_fol, (0.18, 0.36, 0.12, 1.0))):
            if _m and _m.node_tree:
                nt_m = _m.node_tree
                nt_m.nodes.clear()
                out_m = nt_m.nodes.new("ShaderNodeOutputMaterial")
                bsdf_m = nt_m.nodes.new("ShaderNodeBsdfPrincipled")
                bsdf_m.inputs["Base Color"].default_value = _base
                bsdf_m.inputs["Metallic"].default_value = 0.0
                bsdf_m.inputs["Roughness"].default_value = 0.72
                nt_m.links.new(bsdf_m.outputs["BSDF"], out_m.inputs["Surface"])

        # Exportiere kompaktes gebündeltes .glb
        glb_path = os.path.join(glb_dir, f"trees_{species}.glb")
        size_kb = export_species_glb(created_objs, glb_path)

        dt_sp = time.time() - t_sp
        summary[species] = {
            "variants": len(variant_meta),
            "lod0_min": min(lod_tris[0]), "lod0_max": max(lod_tris[0]),
            "lod1_min": min(lod_tris[1]), "lod1_max": max(lod_tris[1]),
            "lod2_min": min(lod_tris[2]), "lod2_max": max(lod_tris[2]),
            "lod3_min": min(lod_tris[3]), "lod3_max": max(lod_tris[3]),
            "glb_kb": round(size_kb, 1),
            "time_s": round(dt_sp, 2),
            "variant_list": variant_meta,
        }
        print(
            f"[BOTANY] {species:9s}: {len(variant_meta)} Var | "
            f"L0 {min(lod_tris[0])}-{max(lod_tris[0])} | "
            f"L1 {min(lod_tris[1])}-{max(lod_tris[1])} | "
            f"L2 {min(lod_tris[2])}-{max(lod_tris[2])} | "
            f"L3 {min(lod_tris[3])}-{max(lod_tris[3])} | "
            f"{size_kb:.1f} KB ({dt_sp:.2f}s)"
        )

    return summary, showcase_picks


def update_manifest_botany(root, summary):
    manifest_path = os.path.join(root, "assets", "manifest.json")
    if os.path.isfile(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    else:
        manifest = {"version": "2.0.0", "categories": {}, "slots": {}}

    cats = manifest.setdefault("categories", {})
    botany_grp = cats.setdefault("botany", {
        "blendDir": "assets/blend/botany",
        "glbDir": "assets/glb/botany",
        "requiredTag": "Col_Wind",
        "items": {},
    })
    items = botany_grp.setdefault("items", {})

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for species, info in summary.items():
        sss_col, sss_str = SPECIES_SSS[species]
        slot_id = f"trees_{species}"
        items[slot_id] = {
            "enabled": True,
            "url": f"assets/glb/botany/trees_{species}.glb",
            "blend": f"assets/blend/botany/trees_{species}.blend",
            "category": "botany",
            "species": species,
            "instanced": True,
            "wind": True,
            "variantsCount": info["variants"],
            "stages": ["sapling", "young", "mature", "ancient"],
            "lods": ["LOD0", "LOD1", "LOD2", "LOD3"],
            "lod0TrisRange": [info["lod0_min"], info["lod0_max"]],
            "lod1TrisRange": [info["lod1_min"], info["lod1_max"]],
            "lod2TrisRange": [info["lod2_min"], info["lod2_max"]],
            "lod3TrisRange": [info["lod3_min"], info["lod3_max"]],
            "materials": 2,
            "hasRequiredTag": True,
            "sharedTextures": {
                "bark": [
                    "assets/textures/botany_bark_trim_baseColor.png",
                    "assets/textures/botany_bark_trim_normal.png",
                    "assets/textures/botany_bark_trim_orm.png",
                ],
                "foliage": [
                    "assets/textures/botany_leaf_atlas_baseColor.png",
                    "assets/textures/botany_leaf_atlas_normal.png",
                    "assets/textures/botany_leaf_atlas_orm.png",
                    "assets/textures/botany_leaf_atlas_thickness.png",
                ],
            },
            "sssColor": sss_col,
            "sssStrength": sss_str,
            "glbSizeKB": info["glb_kb"],
            "exportedAt": now_str,
        }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"[BOTANY] manifest.json aktualisiert ({len(summary)} Art-Pakete registriert).")


def render_showcase(root, showcase_picks):
    print("[BOTANY] Rendere Kontroll-Tableau assets/previews/botany_showcase.png...")
    scene = clear_scene()
    dev = setup_cycles_gpu(scene, samples=32)
    print(f"[BOTANY] Showcase Cycles Device: {dev}")

    blend_dir = os.path.join(root, "assets", "blend", "botany")
    preview_path = os.path.join(root, "assets", "previews", "botany_showcase.png")
    os.makedirs(os.path.dirname(preview_path), exist_ok=True)

    # 10 Reihen (Arten) x 4 Spalten (Sapling -> Young -> Mature -> Ancient) ohne Überlappung!
    stages_order = ["sapling", "young", "mature", "ancient"]
    col_x = [-42.0, -16.0, 12.0, 44.0]
    row_y = [225.0, 175.0, 125.0, 75.0, 25.0, -25.0, -75.0, -125.0, -175.0, -225.0]

    for r_i, species in enumerate(SPECIES_LIST):
        bpath = os.path.join(blend_dir, f"trees_{species}.blend")
        wanted = {showcase_picks[(species, st)]: st for st in stages_order}
        with bpy.data.libraries.load(bpath, link=False) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects if name in wanted]

        for obj in data_to.objects:
            if obj is None:
                continue
            st = wanted[obj.name]
            c_i = stages_order.index(st)
            scene.collection.objects.link(obj)
            obj.location = (col_x[c_i], row_y[r_i], 0.0)

    # Heller, sauberer Boden bei Z = 0.0 zur Kontrolle des Wurzelansatzes
    bpy.ops.mesh.primitive_plane_add(size=650.0, location=(0.0, 0.0, 0.0))
    ground = bpy.context.active_object
    mat_g = bpy.data.materials.new("ShowcaseGround")
    mat_g.use_nodes = True
    bsdf_g = mat_g.node_tree.nodes.get("Principled BSDF")
    if bsdf_g:
        bsdf_g.inputs["Base Color"].default_value = (0.48, 0.42, 0.32, 1.0)
        bsdf_g.inputs["Roughness"].default_value = 0.92
    ground.data.materials.append(mat_g)

    # Warmes Sonnenlicht + Himmels-Umgebung
    world = bpy.data.worlds.new("ShowcaseWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.58, 0.68, 0.82, 1.0)
        bg.inputs["Strength"].default_value = 0.9

    sun_data = bpy.data.lights.new("Sun", type="SUN")
    sun_data.energy = 3.6
    sun_data.color = (1.0, 0.95, 0.86)
    sun_obj = bpy.data.objects.new("Sun", sun_data)
    sun_obj.rotation_euler = (math.radians(52), math.radians(15), math.radians(-35))
    scene.collection.objects.link(sun_obj)

    # Schräg-Frontale Übersichtskamera (alle 6 Reihen x 4 Spalten klar getrennt & lesbar!)
    cam_data = bpy.data.cameras.new("ShowcaseCam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 345.0
    cam_obj = bpy.data.objects.new("ShowcaseCam", cam_data)
    cam_obj.location = (2.0, -320.0, 168.0)
    direction = Vector((1.0, 0.0, 8.0)) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    scene.render.resolution_x = 2200
    scene.render.resolution_y = 2200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX" if "AgX" in [e.identifier for e in scene.view_settings.bl_rna.properties["view_transform"].enum_items] else "Standard"
    scene.render.filepath = preview_path
    bpy.ops.render.render(write_still=True)
    print(f"[BOTANY] Showcase gespeichert: {preview_path}")


def main():
    t0 = time.time()
    root = get_project_root()
    summary, showcase_picks = build_all_species(root)
    update_manifest_botany(root, summary)
    render_showcase(root, showcase_picks)
    dt = time.time() - t0
    print(f"[BOTANY] GESAMTDAUER (150 Varianten x 4 LODs = 600 Meshes + 10 GLBs + Showcase): {dt:.2f} s")


if __name__ == "__main__":
    main()
