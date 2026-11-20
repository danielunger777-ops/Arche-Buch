"""
build_ark_master_atlas.py — Gemeinsames 2048x2048 Arche-Meister-Trim-Sheet (Welle A, B & C)
===========================================================================================
Erzeugt das hochdetaillierte, wiederverwendbare 2048x2048-Meister-Trim-Sheet ueber
Cycles CUDA (GTX 1070 / CPU-Fallback) unter zwingender Nutzung der installierten
ambientCG / Poly Haven CC0-Material-Scans aus assets/textures/cc0/:

  - assets/textures/ark/ark_master_basecolor.png  [sRGB, 2048x2048, 0 Sonnenschatten]
  - assets/textures/ark/ark_master_normal.png     [Linear / Non-Color, 2048x2048]
  - assets/textures/ark/ark_master_roughness.png  [Linear / Non-Color, 2048x2048]

Shader-Diaet-Kompatibilitaet (arche_asset_v1_std, deltaPrograms === 0):
  Exakt 3 Texturen (BaseColor, Normal, Roughness) — kein metalnessMap, kein aoMap,
  kein emissiveMap, kein Alpha/Transparenz, keine eingebackenen Sonnenschatten.

Strikter Arche-Farbschutz (ark_inventory_audit.md):
  1. Kopher-Erdpech (Bitumen-Verstrich): ~#161412 (sRGB [22, 20, 18]), Roughness 0.34..0.46
  2. Eiche D35 (grob gebeilt / Dechselspuren + Stirnholz + Holzduebel): ~#7A4E28 (sRGB [122, 78, 40])
  3. Zypresse C27 (Schotten & Nut-Feder-Bohlen): ~#925A30 (sRGB [146, 90, 48])
  4. Libanon-Zeder C18 (Zohar, Badgir-Koepfe, Sparren): ~#A26C3C (sRGB [162, 108, 60])
  5. Hainbuche (Sperrbalken, Kammzaehne, Duebel): ~#9C6E3A (sRGB [156, 110, 58])
  6. Vulkanbasalt (~#3E4146), gehaemmerte Zinnbronze CuSn12 (~#BA8640), Hanfseil/Werg (~#A88856),
     Terrakotta/Zeer-Ton (~#AC623E) & Leder/Bienenwachs-Talg-Schmiere (~#8E6030).

Aufruf:
  blender --background --python-exit-code 1 --python assets/scripts/build_ark_master_atlas.py
"""

import os
import sys
import time
import math
import bpy
import bmesh
import numpy as np

ATLAS_W = 2048
ATLAS_H = 2048

# Verbindliche UV-Regionen (u0, v0, u1, v1) mit Sicherheitsabstand gegen Mipmap-Bleeding.
# Baender 0..4 sind voll-U-kachelnd (u0=0.0, u1=1.0) fuer durchgehende Balken, Planken und Bordwaende.
ARK_TRIM_REGIONS = {
    # Band 0 (V 0.000..0.160): Kopher-Erdpech (Bitumen-Verstrich ueber Plankenfugen, ~#161412)
    "kopher_pitch":       (0.000, 0.006, 1.000, 0.154),
    # Band 1 (V 0.160..0.340): Eiche D35 (grob gebeilt / Dechselspuren & Bohlenfugen, ~#7A4E28)
    "oak_d35":            (0.000, 0.166, 1.000, 0.334),
    # Band 2 (V 0.340..0.490): Zypresse C27 (Schotten & Nut-und-Feder-Bohlen, ~#925A30)
    "cypress_c27":        (0.000, 0.346, 1.000, 0.484),
    # Band 3 (V 0.490..0.640): Libanon-Zeder C18 (Zohar, Badgir-Koepfe, Sparren, ~#A26C3C)
    "cedar_c18":          (0.000, 0.496, 1.000, 0.634),
    # Band 4 (V 0.640..0.770): Hainbuche (Sperrbalken, Kammzaehne, Scharnierzapfen, ~#9C6E3A)
    "hornbeam":           (0.000, 0.646, 1.000, 0.764),
    # Band 5 (V 0.770..0.890): Eiche-Stirnholz | Eiche mit Holzduebel-Koepfen (3 Finger / 1 Hand) | Vulkanbasalt
    "oak_endgrain":       (0.006, 0.776, 0.326, 0.884),
    "oak_dowel_heads":    (0.340, 0.776, 0.660, 0.884),
    "volcanic_basalt":    (0.674, 0.776, 0.994, 0.884),
    # Band 6 (V 0.890..1.000): Zinnbronze CuSn12 | Hanfseil/Werg | Terrakotta/Zeer | Leder/Bienenwachs-Talg
    "tin_bronze":         (0.006, 0.896, 0.244, 0.994),
    "hemp_rope":          (0.256, 0.896, 0.504, 0.994),
    "terracotta":         (0.516, 0.896, 0.754, 0.994),
    "leather_wax":        (0.766, 0.896, 0.994, 0.994),
}

# Physische Streifen-Rechtecke auf der 1x1-m-Bake-Plane (lückenlos von 0..1)
ATLAS_STRIPS = [
    ("kopher_pitch",    0.000, 0.000, 1.000, 0.160),
    ("oak_d35",         0.000, 0.160, 1.000, 0.340),
    ("cypress_c27",     0.000, 0.340, 1.000, 0.490),
    ("cedar_c18",       0.000, 0.490, 1.000, 0.640),
    ("hornbeam",        0.000, 0.640, 1.000, 0.770),
    ("oak_endgrain",    0.000, 0.770, 0.333, 0.890),
    ("oak_dowel_heads", 0.333, 0.770, 0.667, 0.890),
    ("volcanic_basalt", 0.667, 0.770, 1.000, 0.890),
    ("tin_bronze",      0.000, 0.890, 0.250, 1.000),
    ("hemp_rope",       0.250, 0.890, 0.510, 1.000),
    ("terracotta",      0.510, 0.890, 0.760, 1.000),
    ("leather_wax",     0.760, 0.890, 1.000, 1.000),
]

# Verbindliche Kanon-Zielwerte im sRGB-Farbraum [0..255] zur automatischen Kalibrierung & Verifikation
TARGET_SRGB_255 = {
    "kopher_pitch":    (22.0,  20.0,  18.0),   # #161412 (STRENG: Tiefdunkel, NICHT aufhellen!)
    "oak_d35":         (122.0, 78.0,  40.0),   # #7A4E28 (Eiche D35 grob gebeilt)
    "cypress_c27":     (146.0, 90.0,  48.0),   # #925A30 (Zypresse C27 Schotten/Bohlen)
    "cedar_c18":       (162.0, 108.0, 60.0),   # #A26C3C (Libanon-Zeder C18)
    "hornbeam":        (156.0, 110.0, 58.0),   # #9C6E3A (Hainbuche)
    "oak_endgrain":    (114.0, 72.0,  37.0),   # #724825 (Eiche Stirnholz mit Jahresringen)
    "oak_dowel_heads": (128.0, 84.0,  44.0),   # #80542C (Eiche + Hainbuchen-Holzduebel)
    "volcanic_basalt": (62.0,  65.0,  70.0),   # #3E4146 (Vulkanbasalt)
    "tin_bronze":      (186.0, 134.0, 64.0),   # #BA8640 (Gehaemmerte Zinnbronze CuSn12)
    "hemp_rope":       (168.0, 136.0, 86.0),   # #A88856 (Gedrehtes Hanftauwerk / Werg)
    "terracotta":      (172.0, 98.0,  62.0),   # #AC623E (Gebrannte Terrakotta / Zeer-Ton)
    "leather_wax":     (142.0, 96.0,  48.0),   # #8E6030 (Leder / Bienenwachs-Talg-Schmiere)
}

TARGET_ROUGHNESS_RANGE = {
    "kopher_pitch":    (0.34, 0.46),  # Seidig-speckiger Bitumen-Verstrich (~0.36-0.44)
    "oak_d35":         (0.68, 0.82),  # Grob gebeiltes Eichenholz
    "cypress_c27":     (0.66, 0.80),  # Dichte Zypressenbohlen
    "cedar_c18":       (0.64, 0.78),  # Gehobelte Libanon-Zeder
    "hornbeam":        (0.54, 0.70),  # Zaeh-glattes Hainbuchen-Hartholz
    "oak_endgrain":    (0.74, 0.88),  # Offenes Stirnholz
    "oak_dowel_heads": (0.62, 0.78),  # Gezimmerte Eiche mit polierten Duebelkoepfen
    "volcanic_basalt": (0.82, 0.93),  # Poriger Vulkanbasalt
    "tin_bronze":      (0.24, 0.38),  # Gehaemmerte Zinnbronze CuSn12
    "hemp_rope":       (0.78, 0.92),  # Faseriges Hanfseil / Werg
    "terracotta":      (0.68, 0.84),  # Poroeser gebrannter Ton
    "leather_wax":     (0.30, 0.46),  # Speckiger Bienenwachs-Talg & Leder
}


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
        scene.cycles.transmission_bounces = 0
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    return "CUDA (GPU)" if used_gpu else "CPU"


def srgb_to_linear(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.04045, c / 12.92, np.power((c + 0.055) / 1.055, 2.4))


def linear_to_srgb(c):
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(np.maximum(c, 0.0031308), 1.0 / 2.4) - 0.055)


def load_cc0_packs(project_root):
    """Laedt die installierten ambientCG CC0 1K .packed.blend-Scans aus assets/textures/cc0/."""
    cc0_dir = os.path.join(project_root, "assets", "textures", "cc0")
    pack_files = {
        "wood":       "Wood004_1K-JPG.packed.blend",
        "wicker":     "Wicker001_1K-JPG.packed.blend",
        "fabric":     "Fabric030_1K-JPG.packed.blend",
        "bronze":     "Metal007_1K-JPG.packed.blend",
        "leather":    "Leather014_1K-JPG.packed.blend",
        "clay":       "Clay001_1K-JPG.packed.blend",
        "brick":      "Bricks001_1K-JPG.packed.blend",
        "travertine": "Travertine001_1K-JPG.packed.blend",
        "ground":     "Ground003_1K-JPG.packed.blend",
    }
    loaded = {}
    for key, fname in pack_files.items():
        fpath = os.path.join(cc0_dir, fname)
        if not os.path.exists(fpath):
            print(f"[ARK ATLAS] WARN: CC0-Scan fehlt: {fpath}", flush=True)
            continue
        before = set(bpy.data.images.keys())
        with bpy.data.libraries.load(fpath, link=False) as (data_from, data_to):
            data_to.images = list(data_from.images)
        new_imgs = [bpy.data.images[n] for n in bpy.data.images.keys() if n not in before]
        pack = {"source_file": fname}
        for img in new_imgs:
            nl = img.name.lower()
            if "color" in nl:
                img.colorspace_settings.name = "sRGB"
                pack["color"] = img
            elif "normalgl" in nl or ("normal" in nl and "dx" not in nl):
                img.colorspace_settings.name = "Non-Color"
                pack["normal"] = img
            elif "roughness" in nl:
                img.colorspace_settings.name = "Non-Color"
                pack["roughness"] = img
            elif "ambientocclusion" in nl or "_ao" in nl:
                img.colorspace_settings.name = "Non-Color"
                pack["ao"] = img
            elif "displacement" in nl:
                img.colorspace_settings.name = "Non-Color"
                pack["disp"] = img
        loaded[key] = pack
        print(f"[ARK ATLAS] CC0-Scan geladen ({key:10s} <- {fname}): {[k for k in sorted(pack.keys()) if k != 'source_file']}", flush=True)
    return loaded


def _add_tex_node(nodes, img, uv_out, links, scale=(1.0, 1.0), rot_z=0.0):
    mp = nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale[0], scale[1], 1.0)
    mp.inputs["Rotation"].default_value = (0.0, 0.0, rot_z)
    links.new(uv_out, mp.inputs["Vector"])
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.extension = "REPEAT"
    links.new(mp.outputs["Vector"], tex.inputs["Vector"])
    return tex


def _remap_rough(nodes, links, r_out, r_min, r_max):
    mr = nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 1.0
    mr.inputs["To Min"].default_value = r_min
    mr.inputs["To Max"].default_value = r_max
    mr.clamp = True
    links.new(r_out, mr.inputs["Value"])
    return mr.outputs["Result"]


def build_strip_material(name, kind, cc0):
    """Erstellt einen Cycles-Shader-Node-Graphen mit echten CC0-Scans + prozeduralem Zimmermanns-Relief."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nodes.new("ShaderNodeTexCoord")
    uv = tc.outputs["UV"]

    # Wichtig: Metallic bleibt beim Bake auf 0.0, damit Cycles DIFFUSE die volle Albedo backt!
    bsdf.inputs["Metallic"].default_value = 0.0
    r_min, r_max = TARGET_ROUGHNESS_RANGE[kind]

    def attach_cc0_base(pack_key, tile, norm_str=1.0, rot_z=0.0, extra_bump_socket=None, extra_bump_str=0.35):
        pack = cc0.get(pack_key, {})
        col_sock = None
        if "color" in pack:
            t_col = _add_tex_node(nodes, pack["color"], uv, links, scale=tile, rot_z=rot_z)
            col_sock = t_col.outputs["Color"]
            if "ao" in pack:
                t_ao = _add_tex_node(nodes, pack["ao"], uv, links, scale=tile, rot_z=rot_z)
                ao_mix = nodes.new("ShaderNodeMix")
                ao_mix.data_type = "RGBA"
                ao_mix.blend_type = "MULTIPLY"
                ao_mix.inputs["Factor"].default_value = 0.22
                links.new(col_sock, ao_mix.inputs[6])
                links.new(t_ao.outputs["Color"], ao_mix.inputs[7])
                col_sock = ao_mix.outputs[2]
            links.new(col_sock, bsdf.inputs["Base Color"])
        if "roughness" in pack:
            t_r = _add_tex_node(nodes, pack["roughness"], uv, links, scale=tile, rot_z=rot_z)
            links.new(_remap_rough(nodes, links, t_r.outputs["Color"], r_min, r_max), bsdf.inputs["Roughness"])
        else:
            bsdf.inputs["Roughness"].default_value = 0.5 * (r_min + r_max)

        nrm_out = None
        if "normal" in pack:
            t_n = _add_tex_node(nodes, pack["normal"], uv, links, scale=tile, rot_z=rot_z)
            nm = nodes.new("ShaderNodeNormalMap")
            nm.inputs["Strength"].default_value = norm_str
            links.new(t_n.outputs["Color"], nm.inputs["Color"])
            nrm_out = nm.outputs["Normal"]
        if extra_bump_socket is not None:
            bump = nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value = extra_bump_str
            bump.inputs["Distance"].default_value = 0.015
            links.new(extra_bump_socket, bump.inputs["Height"])
            if nrm_out is not None:
                links.new(nrm_out, bump.inputs["Normal"])
            nrm_out = bump.outputs["Normal"]
        if nrm_out is not None:
            links.new(nrm_out, bsdf.inputs["Normal"])
        return col_sock

    if kind == "kopher_pitch":
        # Kopher-Erdpech: CC0 Leather014 + Wood004 Untergrund + organische Spachtel-/Pinselstruktur
        noi = nodes.new("ShaderNodeTexNoise")
        noi.inputs["Scale"].default_value = 14.0
        noi.inputs["Detail"].default_value = 6.0
        noi.inputs["Distortion"].default_value = 1.4
        links.new(uv, noi.inputs["Vector"])
        attach_cc0_base("leather", tile=(4.0, 2.0), norm_str=0.75, extra_bump_socket=noi.outputs["Fac"], extra_bump_str=0.32)

    elif kind == "oak_d35":
        # Eiche D35: CC0 Wood004 (um 90° gedreht -> Faser laeuft horizontal entlang U!)
        noi = nodes.new("ShaderNodeTexNoise")
        noi.inputs["Scale"].default_value = 18.0
        noi.inputs["Detail"].default_value = 5.0
        links.new(uv, noi.inputs["Vector"])
        attach_cc0_base("wood", tile=(1.5, 4.0), norm_str=1.25, rot_z=math.pi * 0.5, extra_bump_socket=noi.outputs["Fac"], extra_bump_str=0.18)

    elif kind == "cypress_c27":
        # Zypresse C27: CC0 Wood004 (horizontal entlang U)
        attach_cc0_base("wood", tile=(1.8, 5.0), norm_str=1.05, rot_z=math.pi * 0.5)

    elif kind == "cedar_c18":
        # Libanon-Zeder C18: CC0 Wood004 feine rötlich-goldene Maserung (horizontal entlang U)
        attach_cc0_base("wood", tile=(1.6, 4.5), norm_str=0.95, rot_z=math.pi * 0.5)

    elif kind == "hornbeam":
        # Hainbuche: CC0 Wood004 dichte Hartholz-Faser (horizontal entlang U)
        attach_cc0_base("wood", tile=(2.0, 6.0), norm_str=0.85, rot_z=math.pi * 0.5)

    elif kind == "oak_endgrain":
        # Eiche Jahresring-Stirnholz: CC0 Wood004 + konzentrische Jahresringe
        wave = nodes.new("ShaderNodeTexWave")
        wave.wave_type = "RINGS"
        wave.rings_direction = "Z"
        wave.inputs["Scale"].default_value = 12.0
        wave.inputs["Distortion"].default_value = 2.4
        wave.inputs["Detail"].default_value = 5.0
        links.new(uv, wave.inputs["Vector"])
        attach_cc0_base("wood", tile=(2.5, 2.5), norm_str=1.10, extra_bump_socket=wave.outputs["Fac"], extra_bump_str=0.45)

    elif kind == "oak_dowel_heads":
        # Eiche D35 mit Holzduebel-Raster (Faser horizontal entlang U)
        attach_cc0_base("wood", tile=(1.5, 3.0), norm_str=1.05, rot_z=math.pi * 0.5)

    elif kind == "volcanic_basalt":
        # Vulkanbasalt: CC0 Travertine001 + Ground003 Basalt-Poren
        vor = nodes.new("ShaderNodeTexVoronoi")
        vor.inputs["Scale"].default_value = 55.0
        links.new(uv, vor.inputs["Vector"])
        attach_cc0_base("travertine", tile=(3.0, 2.0), norm_str=1.25, extra_bump_socket=vor.outputs["Distance"], extra_bump_str=0.48)

    elif kind == "tin_bronze":
        # Gehaemmerte Zinnbronze CuSn12: CC0 Metal007 + Hammerschlag-Dellen
        vor = nodes.new("ShaderNodeTexVoronoi")
        vor.inputs["Scale"].default_value = 38.0
        links.new(uv, vor.inputs["Vector"])
        attach_cc0_base("bronze", tile=(2.5, 2.0), norm_str=0.95, extra_bump_socket=vor.outputs["Distance"], extra_bump_str=0.36)

    elif kind == "hemp_rope":
        # Hanfseil / Werg: CC0 Wicker001 + Fabric030
        attach_cc0_base("wicker", tile=(4.0, 2.5), norm_str=1.30)

    elif kind == "terracotta":
        # Terrakotta / Zeer-Ton: CC0 Clay001 + Bricks001
        attach_cc0_base("clay", tile=(3.0, 2.0), norm_str=0.95)

    elif kind == "leather_wax":
        # Leder / Bienenwachs-Talg-Schmiere: CC0 Leather014
        attach_cc0_base("leather", tile=(3.0, 2.0), norm_str=0.85)

    return mat


def create_atlas_plane(cc0):
    mesh = bpy.data.meshes.new("ArkMasterAtlasSource")
    obj = bpy.data.objects.new("ArkMasterAtlasSource", mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    for idx, (kind, u0, v0, u1, v1) in enumerate(ATLAS_STRIPS):
        mat = build_strip_material(f"Mat_Ark_{kind}", kind, cc0)
        obj.data.materials.append(mat)
        v00 = bm.verts.new((u0, v0, 0.0))
        v10 = bm.verts.new((u1, v0, 0.0))
        v11 = bm.verts.new((u1, v1, 0.0))
        v01 = bm.verts.new((u0, v1, 0.0))
        f = bm.faces.new((v00, v10, v11, v01))
        f.material_index = idx
        for loop, uv_co in zip(f.loops, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]):
            loop[uv_layer].uv = uv_co

    bm.to_mesh(mesh)
    bm.free()
    return obj


def create_bake_target():
    mesh = bpy.data.meshes.new("ArkMasterAtlasTarget")
    obj = bpy.data.objects.new("ArkMasterAtlasTarget", mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    v00 = bm.verts.new((0.0, 0.0, 0.002))
    v10 = bm.verts.new((1.0, 0.0, 0.002))
    v11 = bm.verts.new((1.0, 1.0, 0.002))
    v01 = bm.verts.new((0.0, 1.0, 0.002))
    f = bm.faces.new((v00, v10, v11, v01))
    for loop, uv_co in zip(f.loops, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]):
        loop[uv_layer].uv = uv_co
    bm.to_mesh(mesh)
    bm.free()

    mat = bpy.data.materials.new("Mat_ArkBakeTarget")
    mat.use_nodes = True
    obj.data.materials.append(mat)
    return obj, mat


def bake_pass(src_obj, dst_obj, dst_mat, bake_type, img_name, width, height, is_srgb=True):
    img = bpy.data.images.new(img_name, width=width, height=height, alpha=False, float_buffer=True)
    img.colorspace_settings.name = "sRGB" if is_srgb else "Non-Color"
    nt = dst_mat.node_tree
    tex_node = nt.nodes.new("ShaderNodeTexImage")
    tex_node.image = img
    nt.nodes.active = tex_node

    bpy.ops.object.select_all(action="DESELECT")
    src_obj.select_set(True)
    dst_obj.select_set(True)
    bpy.context.view_layer.objects.active = dst_obj

    bpy.context.scene.render.bake.use_selected_to_active = True
    bpy.context.scene.render.bake.cage_extrusion = 0.05
    bpy.context.scene.render.bake.max_ray_distance = 0.1
    bpy.context.scene.render.bake.margin = 4
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.context.scene.render.bake.use_pass_color = True

    bpy.ops.object.bake(type=bake_type)
    nt.nodes.remove(tex_node)
    return img


def read_img_np(img, w, h):
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    return buf.reshape((h, w, 4))


def save_np_png(arr_linear_or_srgb, path, is_srgb=True):
    """Speichert ein 3-Kanal-Float-Array [0..1] deterministisch nach PNG.
    Bei is_srgb=True erwartet Blender in img.pixels LINEARE Float-Werte und
    wandelt diese beim Speichern als sRGB-PNG exakt in sRGB-Bytes [0..255] um!
    Bei is_srgb=False (Non-Color) werden die Float-Werte 1:1 linear gespeichert."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    h, w, ch = arr_linear_or_srgb.shape
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[:, :, :3] = np.clip(arr_linear_or_srgb[:, :, :3], 0.0, 1.0)
    img = bpy.data.images.new("_ArkSaveTmp", width=w, height=h, alpha=False, float_buffer=True)
    img.colorspace_settings.name = "sRGB" if is_srgb else "Non-Color"
    img.pixels.foreach_set(rgba.ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    scene = bpy.context.scene
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    img.save()
    bpy.data.images.remove(img)


def _inject_carpentry_micro_details(px_col_lin, px_nrm, px_rgh, w, h):
    """Veredelt die gebackenen CC0-Scans mit hochpraezisen bronzezeitlichen Zimmermanns-Details
    (Plankenfugen, Dechsel-Kerben, Nut-und-Feder-Streifen, Jahresring-Stirnholz, plastischen
    3-Finger-/1-Hand-Holzduebel-Koepfen, Kopher-Spachtelstrichen & gedrehten Hanfseil-Kardelen)
    und kalibriert jedes Band exakt auf den Farbschutz-Kanon aus ark_inventory_audit.md."""
    u_1d = (np.arange(w, dtype=np.float32) + 0.5) / w
    v_1d = (np.arange(h, dtype=np.float32) + 0.5) / h
    uu, vv = np.meshgrid(u_1d, v_1d, indexing="xy")

    # Convert baked linear color to sRGB [0..1] for exact canonical color calibration
    srgb = linear_to_srgb(px_col_lin[:, :, :3])

    # Unpack normal [-1..+1]
    nx = px_nrm[:, :, 0] * 2.0 - 1.0
    ny = px_nrm[:, :, 1] * 2.0 - 1.0
    nz = np.maximum(0.15, px_nrm[:, :, 2] * 2.0 - 1.0)

    # 1. Add procedural carpentry normal & roughness features per strip
    for kind, u0, v0, u1, v1 in ATLAS_STRIPS:
        ix0, ix1 = int(round(u0 * w)), int(round(u1 * w))
        iy0, iy1 = int(round(v0 * h)), int(round(v1 * h))
        lu = (uu[iy0:iy1, ix0:ix1] - u0) / max(1e-5, u1 - u0)
        lv = (vv[iy0:iy1, ix0:ix1] - v0) / max(1e-5, v1 - v0)
        sub_srgb = srgb[iy0:iy1, ix0:ix1]
        sub_nx = nx[iy0:iy1, ix0:ix1]
        sub_ny = ny[iy0:iy1, ix0:ix1]
        sub_rgh = px_rgh[iy0:iy1, ix0:ix1]

        if kind == "kopher_pitch":
            # Organischer Kopher-Bitumen-Spachtelverstrich ueber kalfaterten Plankenfugen (ohne Streifen-Aliasing!)
            seam_groove = np.exp(-np.square(np.sin(lv * 2.0 * math.pi)) * 45.0)
            trowel = np.sin(lu * 6.0 * math.pi + np.cos(lv * 5.0 * math.pi) * 2.2) * np.cos(lv * 4.0 * math.pi + np.sin(lu * 8.0 * math.pi))
            sub_ny += 0.14 * np.sin(lv * 4.0 * math.pi) * seam_groove + 0.08 * trowel
            sub_nx += 0.08 * np.cos(lu * 6.0 * math.pi + lv * 4.0)
            sub_rgh = np.clip(sub_rgh - 0.03 * seam_groove + 0.03 * trowel, 0.36, 0.45)
            sub_srgb *= (1.0 - 0.12 * seam_groove[..., None] + 0.05 * trowel[..., None])

        elif kind in ("oak_d35", "cypress_c27", "cedar_c18", "hornbeam"):
            # Dezente Laengs-Bohlenfugen (Nut-und-Feder bei Zypresse, gefaste Bohlen bei Eiche/Zeder)
            n_planks = 2.0 if kind != "cypress_c27" else 3.0
            pf = (lv * n_planks) % 1.0
            seam = np.exp(-np.square(np.minimum(pf, 1.0 - pf)) * 520.0)
            seam_grad = np.where(pf < 0.06, 1.0, np.where(pf > 0.94, -1.0, 0.0)) * seam
            sub_ny += 0.28 * seam_grad
            sub_srgb *= (1.0 - 0.16 * seam[..., None])
            sub_rgh = np.clip(sub_rgh + 0.06 * seam, 0.20, 0.95)

            if kind == "oak_d35":
                # Organische, langgezogene Dechsel-Hiebe entlang der echten CC0-Eichenmaserung (0 Kachel-Raster!)
                adze_wave = (
                    np.sin(lu * 10.0 * math.pi + 1.7 * np.sin(lv * 4.0 * math.pi))
                    * np.cos(lv * 6.0 * math.pi + 1.3 * np.cos(lu * 6.0 * math.pi))
                )
                sub_nx += 0.10 * adze_wave
                sub_ny += 0.08 * np.sin(lv * 12.0 * math.pi + lu * 4.0 * math.pi)
                sub_srgb *= (0.97 + 0.06 * adze_wave[..., None])

        elif kind == "oak_endgrain":
            # Jahresring-Stirnholz mit Markstrahlen und feinen Trocknungsrissen
            dx = lu - 0.5
            dy = lv - 0.5
            rad = np.sqrt(dx * dx + dy * dy) * 2.2
            ang = np.arctan2(dy, dx)
            rings = 0.5 + 0.5 * np.sin(rad * 18.0 * math.pi + 0.35 * np.sin(ang * 5.0))
            rays = np.exp(-np.square(np.sin(ang * 12.0)) * 28.0) * np.clip(rad, 0.1, 1.0)
            sub_nx += 0.32 * np.cos(rad * 18.0 * math.pi) * (dx / np.maximum(0.05, rad))
            sub_ny += 0.32 * np.cos(rad * 18.0 * math.pi) * (dy / np.maximum(0.05, rad))
            sub_srgb *= (0.84 + 0.28 * rings[..., None] - 0.15 * rays[..., None])

        elif kind == "oak_dowel_heads":
            # 4x3 Raster plastisch erhabener Hartholz-Duebelkoepfe (3 Finger / 1 Hand) mit Stirnholz-Ringen
            gu = (lu * 4.0) % 1.0 - 0.5
            gv = (lv * 3.0) % 1.0 - 0.5
            dr = np.sqrt(gu * gu + gv * gv)
            in_peg = dr < 0.28
            in_chamfer = (dr >= 0.20) & (dr < 0.28)
            in_ring = (dr >= 0.28) & (dr < 0.33)
            # Normal bevel on dowel head
            peg_nx = np.where(in_chamfer, -gu / np.maximum(0.01, dr) * 0.75, 0.0)
            peg_ny = np.where(in_chamfer, -gv / np.maximum(0.01, dr) * 0.75, 0.0)
            sub_nx += peg_nx
            sub_ny += peg_ny
            # Concentric endgrain rings on dowel head
            peg_rings = 0.5 + 0.5 * np.sin(dr * 45.0 * math.pi)
            sub_srgb = np.where(in_peg[..., None], sub_srgb * (0.95 + 0.18 * peg_rings[..., None]), sub_srgb)
            sub_srgb = np.where(in_ring[..., None], sub_srgb * 0.72, sub_srgb)
            sub_rgh = np.where(in_peg, np.clip(sub_rgh - 0.08, 0.52, 0.75), sub_rgh)

        elif kind == "hemp_rope":
            # 3-schaeftig geschlagenes Hanfseil mit plastischen Kardelen-Windungen
            strand_v = (lv * 6.0) % 1.0
            twist = np.sin(lu * 28.0 * math.pi + strand_v * 2.0 * math.pi)
            rope_groove = np.exp(-np.square(np.minimum(strand_v, 1.0 - strand_v)) * 180.0)
            sub_nx += 0.38 * np.cos(lu * 28.0 * math.pi + strand_v * 2.0 * math.pi)
            sub_ny += 0.35 * np.sin(strand_v * 2.0 * math.pi)
            sub_srgb *= (0.90 + 0.16 * twist[..., None] - 0.20 * rope_groove[..., None])

        # 2. Exakte Kalibrierung des Mittelwerts auf den Farbschutz-Kanon (TARGET_SRGB_255)
        tgt = np.array(TARGET_SRGB_255[kind], dtype=np.float32) / 255.0
        # Innere 80% des Streifens messen (ohne Rand-Padding)
        cy0, cy1 = max(0, int(0.1 * (iy1 - iy0))), min(iy1 - iy0, int(0.9 * (iy1 - iy0)))
        cx0, cx1 = max(0, int(0.1 * (ix1 - ix0))), min(ix1 - ix0, int(0.9 * (ix1 - ix0)))
        cur_mean = np.maximum(1e-4, sub_srgb[cy0:cy1, cx0:cx1].mean(axis=(0, 1)))
        # Skaliere mit Bewahrung der lokalen CC0-Textur-Dynamik (Kontrast-Spreizung um den Zielwert)
        centered = (sub_srgb - cur_mean) * (0.55 if kind == "kopher_pitch" else 0.88)
        calibrated = tgt + centered * (tgt / cur_mean)
        if kind == "kopher_pitch":
            # Kopher-Pech-Schutz: Tiefdunkel ~#161412, niemals ausgewaschen grau!
            sub_srgb[:] = np.clip(calibrated, 0.045, 0.135)
        else:
            sub_srgb[:] = np.clip(calibrated, 0.06, 0.85)

        # Roughness exakt in den Zielkorridor spreizen
        r_lo, r_hi = TARGET_ROUGHNESS_RANGE[kind]
        r_cur_min = float(np.percentile(sub_rgh[cy0:cy1, cx0:cx1], 5))
        r_cur_max = float(np.percentile(sub_rgh[cy0:cy1, cx0:cx1], 95))
        if r_cur_max - r_cur_min > 1e-4:
            sub_rgh[:] = r_lo + np.clip((sub_rgh - r_cur_min) / (r_cur_max - r_cur_min), 0.0, 1.0) * (r_hi - r_lo)
        else:
            sub_rgh[:] = 0.5 * (r_lo + r_hi)

        srgb[iy0:iy1, ix0:ix1] = sub_srgb
        nx[iy0:iy1, ix0:ix1] = sub_nx
        ny[iy0:iy1, ix0:ix1] = sub_ny
        px_rgh[iy0:iy1, ix0:ix1] = sub_rgh

    # Re-normalize Tangent-Space Normal Map (OpenGL +Y Up convention)
    norm_len = np.sqrt(nx * nx + ny * ny + nz * nz)
    nrm_out = np.zeros((h, w, 3), dtype=np.float32)
    nrm_out[:, :, 0] = (nx / norm_len) * 0.5 + 0.5
    nrm_out[:, :, 1] = (ny / norm_len) * 0.5 + 0.5
    nrm_out[:, :, 2] = (nz / norm_len) * 0.5 + 0.5

    rgh_out = np.stack([px_rgh, px_rgh, px_rgh], axis=-1)
    col_lin_out = srgb_to_linear(srgb)
    return col_lin_out, srgb, nrm_out, rgh_out


def build_ark_master_trim_sheet(project_root):
    t0 = time.time()
    print("[ARK ATLAS] Starte 2048x2048 Arche-Meister-Trim-Sheet Bake (Cycles CUDA + CC0 Scans)...", flush=True)
    scene = clear_scene()
    dev = setup_cycles(scene, samples=4)
    print(f"[ARK ATLAS] Cycles Device: {dev}", flush=True)

    cc0 = load_cc0_packs(project_root)
    src_obj = create_atlas_plane(cc0)
    dst_obj, dst_mat = create_bake_target()

    tex_dir = os.path.join(project_root, "assets", "textures", "ark")
    os.makedirs(tex_dir, exist_ok=True)

    print("[ARK ATLAS] 1/3 Backe BaseColor [sRGB]...", flush=True)
    img_col = bake_pass(src_obj, dst_obj, dst_mat, "DIFFUSE", "Ark_BaseColor", ATLAS_W, ATLAS_H, is_srgb=True)
    px_col_lin = read_img_np(img_col, ATLAS_W, ATLAS_H)

    print("[ARK ATLAS] 2/3 Backe Normal [Linear]...", flush=True)
    img_nrm = bake_pass(src_obj, dst_obj, dst_mat, "NORMAL", "Ark_Normal", ATLAS_W, ATLAS_H, is_srgb=False)
    px_nrm = read_img_np(img_nrm, ATLAS_W, ATLAS_H)

    print("[ARK ATLAS] 3/3 Backe Roughness [Linear]...", flush=True)
    img_rgh = bake_pass(src_obj, dst_obj, dst_mat, "ROUGHNESS", "Ark_Roughness", ATLAS_W, ATLAS_H, is_srgb=False)
    px_rgh = read_img_np(img_rgh, ATLAS_W, ATLAS_H)[:, :, 0]

    print("[ARK ATLAS] Veredele Zimmermanns-Details & kalibriere Arche-Farbschutz...", flush=True)
    col_lin_out, srgb_out, nrm_out, rgh_out = _inject_carpentry_micro_details(
        px_col_lin, px_nrm, px_rgh, ATLAS_W, ATLAS_H
    )

    p_col = os.path.join(tex_dir, "ark_master_basecolor.png")
    p_nrm = os.path.join(tex_dir, "ark_master_normal.png")
    p_rgh = os.path.join(tex_dir, "ark_master_roughness.png")

    save_np_png(col_lin_out, p_col, is_srgb=True)
    save_np_png(nrm_out, p_nrm, is_srgb=False)
    save_np_png(rgh_out, p_rgh, is_srgb=False)

    print("[ARK ATLAS] --- FARBSCHUTZ- & ROUGHNESS-VERIFIKATION (2048x2048) ---", flush=True)
    for kind, u0, v0, u1, v1 in ATLAS_STRIPS:
        ix0, ix1 = int((u0 + 0.02) * ATLAS_W), int((u1 - 0.02) * ATLAS_W)
        iy0, iy1 = int((v0 + 0.01) * ATLAS_H), int((v1 - 0.01) * ATLAS_H)
        m_rgb = srgb_out[iy0:iy1, ix0:ix1].mean(axis=(0, 1)) * 255.0
        m_rgh = rgh_out[iy0:iy1, ix0:ix1, 0].mean()
        r_min = rgh_out[iy0:iy1, ix0:ix1, 0].min()
        r_max = rgh_out[iy0:iy1, ix0:ix1, 0].max()
        hex_col = "#{:02X}{:02X}{:02X}".format(int(round(m_rgb[0])), int(round(m_rgb[1])), int(round(m_rgb[2])))
        print(
            f"[ARK ATLAS]   {kind:16s} | sRGB={hex_col} ({m_rgb[0]:5.1f}, {m_rgb[1]:5.1f}, {m_rgb[2]:5.1f}) "
            f"| Roughness={m_rgh:.3f} [{r_min:.2f}..{r_max:.2f}]",
            flush=True,
        )

    print(f"[ARK ATLAS] Gespeichert (exakt 3 Maps fuer arche_asset_v1_std):", flush=True)
    print(f"[ARK ATLAS]   1) {p_col} ({os.path.getsize(p_col)/1024.0:.1f} KB)", flush=True)
    print(f"[ARK ATLAS]   2) {p_nrm} ({os.path.getsize(p_nrm)/1024.0:.1f} KB)", flush=True)
    print(f"[ARK ATLAS]   3) {p_rgh} ({os.path.getsize(p_rgh)/1024.0:.1f} KB)", flush=True)
    print(f"[ARK ATLAS] FERTIG in {time.time() - t0:.1f}s!", flush=True)


if __name__ == "__main__":
    build_ark_master_trim_sheet(get_project_root())
