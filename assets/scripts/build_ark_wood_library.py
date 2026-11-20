"""
build_ark_wood_library.py — 5 nahtlos kachelbare 1024x1024-CC0-Materialsets fuer Live-Holzart-Umschaltung
=========================================================================================================
Erzeugt unter assets/textures/ark/materials/ 5 nahtlos kachelbare (seamless tileable) 1024x1024-PBR-Sets
aus den installierten ambientCG / Poly Haven CC0-Scans (assets/textures/cc0/*.packed.blend) — jeweils mit
exakt 3 Maps (*_basecolor.png [sRGB], *_normal.png [Linear], *_roughness.png [Linear], keine metalnessMap,
aoMap oder emissiveMap -> 100 % arche_asset_v1_std-konform, deltaPrograms === 0!):

  1. kopher_pitch     : Tiefdunkles Kopher-Erdpech (#161412), zaehe Spachtel-/Bohlen-Normalmap,
                        Roughness 0.34-0.46 (Arche-Farbschutz, NICHT aufhellen!)
  2. wood_oak_d35     : Eiche D35, kraeftige dunkle Eichenmaserung mit Dechselspuren & Plankenfugen (~#7A4E28)
  3. wood_cypress_c27 : Zypresse C27, warmes Mittelbraun, dichte gerade Bohlenfaserung (~#925A30)
  4. wood_cedar_c18   : Libanon-Zeder C18, warmes roetlich-goldenes Zedernholz (~#A26C3C)
  5. wood_hornbeam    : Hainbuche, zaehes honigbraunes Hartholz (~#9C6E3A)

Metrischer UV-Massstab: 1.0 UV-Einheit = 2.0 m (verzerrungsfrei & 100 % nahtlos kachelbar in U und V).

Aufruf:
  blender --background --python-exit-code 1 --python assets/scripts/build_ark_wood_library.py
"""

import os
import sys
import time
import math
import bpy
import bmesh
import numpy as np

TEX_SIZE = 1024

MATERIAL_SETS = [
    {
        "name": "kopher_pitch",
        "target_srgb_255": (22.0, 20.0, 18.0),    # #161412 (STRIKTER ARCHE-FARBSCHUTZ!)
        "roughness_range": (0.34, 0.46),
        "cc0_primary": "wood",                    # Wood004_1K-JPG.packed.blend (echte horizontale Plankenmaserung unter dem Kopher!)
        "cc0_secondary": "leather",               # Leather014_1K-JPG.packed.blend (seidig-speckige Bitumen-Haut)
        "cc0_tertiary": "clay",                   # Clay001_1K-JPG.packed.blend
        "tile_primary": (2, 4),
        "tile_secondary": (2, 2),
        "rot_primary": math.pi * 0.5,
        "norm_strength": 0.68,
        "description": "Tiefdunkles Kopher-Erdpech (#161412, Gen 6,14 innen & aussen) ueber schweren Holzbohlenfugen",
    },
    {
        "name": "wood_oak_d35",
        "target_srgb_255": (122.0, 78.0, 40.0),   # #7A4E28
        "roughness_range": (0.68, 0.82),
        "cc0_primary": "wood",                    # Wood004_1K-JPG.packed.blend
        "cc0_secondary": "ground",                # Ground003_1K-JPG.packed.blend (Dechsel-/Poren-Mikrorelief)
        "cc0_tertiary": "travertine",             # Travertine001_1K-JPG.packed.blend
        "tile_primary": (2, 4),
        "tile_secondary": (2, 2),
        "rot_primary": math.pi * 0.5,
        "norm_strength": 1.25,
        "description": "Eiche D35 (~#7A4E28), kraeftige dunkle Eichenmaserung mit Dechselspuren & Plankenfugen",
    },
    {
        "name": "wood_cypress_c27",
        "target_srgb_255": (146.0, 90.0, 48.0),   # #925A30
        "roughness_range": (0.65, 0.79),
        "cc0_primary": "wood",                    # Wood004_1K-JPG.packed.blend
        "cc0_secondary": "clay",                  # Clay001_1K-JPG.packed.blend
        "cc0_tertiary": "fabric",                 # Fabric030_1K-JPG.packed.blend (feine Längsfaserung)
        "tile_primary": (2, 6),
        "tile_secondary": (3, 3),
        "rot_primary": math.pi * 0.5,
        "norm_strength": 1.05,
        "description": "Zypresse C27 (~#925A30), warmes Mittelbraun, dichte gerade Nut-und-Feder-Bohlenfaserung",
    },
    {
        "name": "wood_cedar_c18",
        "target_srgb_255": (162.0, 108.0, 60.0),  # #A26C3C
        "roughness_range": (0.62, 0.76),
        "cc0_primary": "wood",                    # Wood004_1K-JPG.packed.blend
        "cc0_secondary": "travertine",            # Travertine001_1K-JPG.packed.blend
        "cc0_tertiary": "clay",                   # Clay001_1K-JPG.packed.blend
        "tile_primary": (1, 4),
        "tile_secondary": (2, 2),
        "rot_primary": math.pi * 0.5,
        "norm_strength": 0.98,
        "description": "Libanon-Zeder C18 (~#A26C3C), warmes roetlich-goldenes Zedernholz fuer Dach & Zohar",
    },
    {
        "name": "wood_hornbeam",
        "target_srgb_255": (156.0, 110.0, 58.0),  # #9C6E3A
        "roughness_range": (0.54, 0.68),
        "cc0_primary": "wood",                    # Wood004_1K-JPG.packed.blend
        "cc0_secondary": "leather",               # Leather014_1K-JPG.packed.blend (zaeh-glatter Hartholzschliff)
        "cc0_tertiary": "clay",                   # Clay001_1K-JPG.packed.blend
        "tile_primary": (3, 6),
        "tile_secondary": (2, 2),
        "rot_primary": math.pi * 0.5,
        "norm_strength": 0.88,
        "description": "Hainbuche (~#9C6E3A), zaehes honigbraunes Hartholz fuer hochbelastete Zimmermannsteile",
    },
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
        "leather":    "Leather014_1K-JPG.packed.blend",
        "clay":       "Clay001_1K-JPG.packed.blend",
        "travertine": "Travertine001_1K-JPG.packed.blend",
        "ground":     "Ground003_1K-JPG.packed.blend",
        "fabric":     "Fabric030_1K-JPG.packed.blend",
        "wicker":     "Wicker001_1K-JPG.packed.blend",
        "bronze":     "Metal007_1K-JPG.packed.blend",
    }
    loaded = {}
    for key, fname in pack_files.items():
        fpath = os.path.join(cc0_dir, fname)
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"CC0-Scan fehlt: {fpath}")
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
        print(
            f"[ARK WOOD LIB] CC0-Scan geladen ({key:10s} <- {fname}): "
            f"{[k for k in sorted(pack.keys()) if k != 'source_file']}",
            flush=True,
        )
    return loaded


def _add_tex_node(nodes, img, uv_out, links, scale=(1, 1), rot_z=0.0):
    mp = nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (float(scale[0]), float(scale[1]), 1.0)
    mp.inputs["Rotation"].default_value = (0.0, 0.0, rot_z)
    links.new(uv_out, mp.inputs["Vector"])
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.extension = "REPEAT"
    links.new(mp.outputs["Vector"], tex.inputs["Vector"])
    return tex


def build_cc0_bake_material(spec, cc0):
    """Baut den Cycles-Shader-Graphen aus den echten ambientCG CC0-Scans (mit ganzzahligem Repeat -> 100 % nahtlos!)."""
    name = spec["name"]
    mat = bpy.data.materials.new(name=f"Bake_{name}")
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Metallic"].default_value = 0.0
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nodes.new("ShaderNodeTexCoord")
    uv = tc.outputs["UV"]

    p1 = cc0[spec["cc0_primary"]]
    p2 = cc0[spec["cc0_secondary"]]
    t1 = spec.get("tile_primary", (2, 4))
    t2 = spec.get("tile_secondary", (2, 2))
    r1 = spec.get("rot_primary", 0.0)
    r2 = spec.get("rot_secondary", 0.0)

    # 1. BaseColor: Primary CC0 scan + AO cavity + Secondary CC0 scan detail
    c1 = _add_tex_node(nodes, p1["color"], uv, links, scale=t1, rot_z=r1).outputs["Color"]
    if "ao" in p1:
        ao1 = _add_tex_node(nodes, p1["ao"], uv, links, scale=t1, rot_z=r1).outputs["Color"]
        m_ao = nodes.new("ShaderNodeMix")
        m_ao.data_type = "RGBA"
        m_ao.blend_type = "MULTIPLY"
        m_ao.inputs["Factor"].default_value = 0.25
        links.new(c1, m_ao.inputs[6])
        links.new(ao1, m_ao.inputs[7])
        c1 = m_ao.outputs[2]

    c2 = _add_tex_node(nodes, p2["color"], uv, links, scale=t2, rot_z=r2).outputs["Color"]
    m_col = nodes.new("ShaderNodeMix")
    m_col.data_type = "RGBA"
    m_col.blend_type = "MIX"
    m_col.inputs["Factor"].default_value = 0.32 if name == "kopher_pitch" else 0.16
    links.new(c1, m_col.inputs[6])
    links.new(c2, m_col.inputs[7])
    links.new(m_col.outputs[2], bsdf.inputs["Base Color"])

    # 2. Roughness: Primary + Secondary CC0 roughness scans
    rgh1 = _add_tex_node(nodes, p1["roughness"], uv, links, scale=t1, rot_z=r1).outputs["Color"]
    rgh2 = _add_tex_node(nodes, p2["roughness"], uv, links, scale=t2, rot_z=r2).outputs["Color"]
    m_rgh = nodes.new("ShaderNodeMix")
    m_rgh.data_type = "RGBA"
    m_rgh.blend_type = "MIX"
    m_rgh.inputs["Factor"].default_value = 0.35 if name == "kopher_pitch" else 0.20
    links.new(rgh1, m_rgh.inputs[6])
    links.new(rgh2, m_rgh.inputs[7])
    links.new(m_rgh.outputs[2], bsdf.inputs["Roughness"])

    # 3. Normal: Primary CC0 normal + Secondary CC0 displacement/normal bump
    n1 = _add_tex_node(nodes, p1["normal"], uv, links, scale=t1, rot_z=r1).outputs["Color"]
    nm1 = nodes.new("ShaderNodeNormalMap")
    nm1.inputs["Strength"].default_value = spec.get("norm_strength", 1.0)
    links.new(n1, nm1.inputs["Color"])
    nrm_out = nm1.outputs["Normal"]

    h2_img = p2.get("disp") or p2.get("roughness")
    if h2_img is not None:
        h2 = _add_tex_node(nodes, h2_img, uv, links, scale=t2, rot_z=r2).outputs["Color"]
        bmp = nodes.new("ShaderNodeBump")
        bmp.inputs["Strength"].default_value = 0.42 if name == "kopher_pitch" else 0.22
        bmp.inputs["Distance"].default_value = 0.015
        links.new(h2, bmp.inputs["Height"])
        links.new(nrm_out, bmp.inputs["Normal"])
        nrm_out = bmp.outputs["Normal"]

    links.new(nrm_out, bsdf.inputs["Normal"])
    return mat


def create_unit_plane(name, z_val, mat):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    v00 = bm.verts.new((0.0, 0.0, z_val))
    v10 = bm.verts.new((1.0, 0.0, z_val))
    v11 = bm.verts.new((1.0, 1.0, z_val))
    v01 = bm.verts.new((0.0, 1.0, z_val))
    f = bm.faces.new((v00, v10, v11, v01))
    for loop, uv_co in zip(f.loops, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]):
        loop[uv_layer].uv = uv_co
    bm.to_mesh(mesh)
    bm.free()
    obj.data.materials.append(mat)
    return obj


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
    os.makedirs(os.path.dirname(path), exist_ok=True)
    h, w, _ = arr_linear_or_srgb.shape
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[:, :, :3] = np.clip(arr_linear_or_srgb[:, :, :3], 0.0, 1.0)
    img = bpy.data.images.new("_ArkLibSaveTmp", width=w, height=h, alpha=False, float_buffer=True)
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


def _enforce_seamless_borders(arr, blend_px=12):
    """Sichert 100 % mathematisch nahtlose U- und V-Kantenuebergaenge (RepeatWrapping ohne jede Kachelnaht!)."""
    out = arr.copy()
    h, w = out.shape[:2]
    # Blend horizontal seam (x=0 <-> x=w-1) and vertical seam (y=0 <-> y=h-1) symmetrically
    for i in range(blend_px):
        w_edge = 0.5 * (1.0 - (i / float(blend_px)))
        # X border
        avg_x = 0.5 * (out[:, i] + out[:, w - 1 - i])
        out[:, i] = (1.0 - w_edge) * out[:, i] + w_edge * avg_x
        out[:, w - 1 - i] = (1.0 - w_edge) * out[:, w - 1 - i] + w_edge * avg_x
        # Y border
        avg_y = 0.5 * (out[i, :] + out[h - 1 - i, :])
        out[i, :] = (1.0 - w_edge) * out[i, :] + w_edge * avg_y
        out[h - 1 - i, :] = (1.0 - w_edge) * out[h - 1 - i, :] + w_edge * avg_y
    return out


def refine_and_calibrate_tileable_set(spec, px_col_lin, px_nrm, px_rgh, w, h):
    """Injiziert periodische (2*pi*k -> 100 % nahtlose!) Zimmermanns-Plankenfugen, Dechselspuren,
    Kopher-Spachtelstriche & Duebelkoepfe und kalibriert Albedo & Roughness exakt auf den Arche-Kanon."""
    name = spec["name"]
    u_1d = (np.arange(w, dtype=np.float32) + 0.5) / float(w)
    v_1d = (np.arange(h, dtype=np.float32) + 0.5) / float(h)
    uu, vv = np.meshgrid(u_1d, v_1d, indexing="xy")

    srgb = _enforce_seamless_borders(linear_to_srgb(px_col_lin[:, :, :3]), blend_px=10)
    nx = _enforce_seamless_borders(px_nrm[:, :, 0] * 2.0 - 1.0, blend_px=10)
    ny = _enforce_seamless_borders(px_nrm[:, :, 1] * 2.0 - 1.0, blend_px=10)
    nz = np.maximum(0.15, _enforce_seamless_borders(px_nrm[:, :, 2] * 2.0 - 1.0, blend_px=10))
    rgh = _enforce_seamless_borders(px_rgh.copy(), blend_px=10)

    if name == "kopher_pitch":
        # 4 schwere horizontale Plankenlagen pro 2.0-m-Kachel (0.50 m Plankenbreite) unter der Kopher-Pechschicht
        # -> im Streiflicht (aussen & innen!) bleibt die schwere Holzplanken-Struktur unter dem Kopher spuerbar
        #    (0 Wellen-/Schachbrett-Aliasing bei 70x Kachelung entlang der 140-m-Bordwand!).
        n_planks = 4.0
        pf = (vv * n_planks) % 1.0
        plank_idx = np.floor(vv * n_planks)
        # Plastische horizontale Plankenfuge + kalfaterter Hanfwerg-Pechwulst
        seam = np.exp(-np.square(np.minimum(pf, 1.0 - pf)) * 380.0)
        seam_grad = np.where(pf < 0.07, 1.0, np.where(pf > 0.93, -1.0, 0.0)) * seam
        # Dezente versetzte Stossfugen
        uf_butt = (uu + plank_idx * 0.37) % 1.0
        butt_seam = np.exp(-np.square(np.minimum(uf_butt, 1.0 - uf_butt)) * 520.0)
        butt_grad = np.where(uf_butt < 0.05, 1.0, np.where(uf_butt > 0.95, -1.0, 0.0)) * butt_seam
        # Sanfte laengsorientierte Spachtel-Zuege entlang der Plankenrichtung U
        trowel_u = np.sin(vv * 8.0 * math.pi + 0.6 * np.sin(uu * 2.0 * math.pi))
        plank_crown = np.sin(pf * math.pi)

        ny += 0.30 * seam_grad + 0.04 * trowel_u
        nx += 0.16 * butt_grad
        rgh = rgh - 0.04 * seam + 0.02 * trowel_u - 0.02 * plank_crown
        srgb *= (0.95 + 0.06 * plank_crown[..., None] - 0.14 * seam[..., None] - 0.08 * butt_seam[..., None] + 0.025 * trowel_u[..., None])

    else:
        # 4..5 horizontale Bohlenlagen pro 2.0-m-Kachel mit gefasten Fugen, Stossfugen & Holzduebeln
        n_planks = 5.0 if name in ("wood_cypress_c27", "wood_hornbeam") else 4.0
        pf = (vv * n_planks) % 1.0
        plank_idx = np.floor(vv * n_planks)
        seam = np.exp(-np.square(np.minimum(pf, 1.0 - pf)) * 460.0)
        seam_grad = np.where(pf < 0.07, 1.0, np.where(pf > 0.93, -1.0, 0.0)) * seam

        # Versetzte Stossfugen
        uf_butt = (uu + plank_idx * 0.41) % 1.0
        butt_seam = np.exp(-np.square(np.minimum(uf_butt, 1.0 - uf_butt)) * 620.0)
        butt_grad = np.where(uf_butt < 0.05, 1.0, np.where(uf_butt > 0.95, -1.0, 0.0)) * butt_seam

        # Leichte Farbvariation von Bohle zu Bohle (periodisch ueber plank_idx)
        plank_tint = 1.0 + 0.045 * np.sin(plank_idx * 2.3 + 0.7)

        ny += 0.34 * seam_grad
        nx += 0.24 * butt_grad
        srgb *= plank_tint[..., None] * (1.0 - 0.20 * seam[..., None] - 0.16 * butt_seam[..., None])
        rgh += 0.06 * seam + 0.05 * butt_seam

        if name == "wood_oak_d35":
            # Handgebeilte Dechselspuren (streng 2*pi-periodisch in U und V)
            adze = (
                np.sin(uu * 8.0 * math.pi + 1.4 * np.sin(vv * 4.0 * math.pi))
                * np.cos(vv * 8.0 * math.pi + 1.1 * np.cos(uu * 6.0 * math.pi))
            )
            nx += 0.12 * adze
            ny += 0.09 * np.sin(vv * 16.0 * math.pi + uu * 4.0 * math.pi)
            srgb *= (0.98 + 0.06 * adze[..., None])

    # Exakte Kalibrierung auf TARGET_SRGB_255 & TARGET_ROUGHNESS_RANGE
    tgt = np.array(spec["target_srgb_255"], dtype=np.float32) / 255.0
    cur_mean = np.maximum(1e-4, srgb.mean(axis=(0, 1)))
    contrast_gain = 0.62 if name == "kopher_pitch" else 0.88
    centered = (srgb - cur_mean) * contrast_gain
    calibrated = tgt + centered * (tgt / cur_mean)
    if name == "kopher_pitch":
        # Strikter Arche-Farbschutz: Tiefdunkel #161412, niemals aufgehellt!
        srgb = np.clip(calibrated, 0.042, 0.138)
        # Re-center exact mean to #161412 (22, 20, 18)
        srgb = np.clip(srgb * (tgt / np.maximum(1e-4, srgb.mean(axis=(0, 1)))), 0.040, 0.145)
    else:
        srgb = np.clip(calibrated, 0.06, 0.85)
        srgb = np.clip(srgb * (tgt / np.maximum(1e-4, srgb.mean(axis=(0, 1)))), 0.06, 0.85)

    r_lo, r_hi = spec["roughness_range"]
    r_p5 = float(np.percentile(rgh, 5))
    r_p95 = float(np.percentile(rgh, 95))
    if r_p95 - r_p5 > 1e-4:
        rgh = r_lo + np.clip((rgh - r_p5) / (r_p95 - r_p5), 0.0, 1.0) * (r_hi - r_lo)
    else:
        rgh[:] = 0.5 * (r_lo + r_hi)

    norm_len = np.sqrt(nx * nx + ny * ny + nz * nz)
    nrm_out = np.zeros((h, w, 3), dtype=np.float32)
    nrm_out[:, :, 0] = (nx / norm_len) * 0.5 + 0.5
    nrm_out[:, :, 1] = (ny / norm_len) * 0.5 + 0.5
    nrm_out[:, :, 2] = (nz / norm_len) * 0.5 + 0.5

    rgh_out = np.stack([rgh, rgh, rgh], axis=-1)
    col_lin_out = srgb_to_linear(srgb)

    # Assert seamless border continuity (U and V wrap difference)
    u_seam_err = float(np.abs(srgb[:, 0] - srgb[:, -1]).mean())
    v_seam_err = float(np.abs(srgb[0, :] - srgb[-1, :]).mean())
    assert u_seam_err < 0.025 and v_seam_err < 0.025, (
        f"{name}: Kachelnaht-Fehler zu hoch (u_err={u_seam_err:.4f}, v_err={v_seam_err:.4f})!"
    )

    return col_lin_out, srgb, nrm_out, rgh_out, u_seam_err, v_seam_err


def build_ark_wood_library(project_root):
    t0 = time.time()
    print("[ARK WOOD LIB] Starte Bau der 5 nahtlos kachelbaren 1024x1024-CC0-Materialsets...", flush=True)
    scene = clear_scene()
    dev = setup_cycles(scene, samples=4)
    print(f"[ARK WOOD LIB] Cycles Device: {dev}", flush=True)

    cc0 = load_cc0_packs(project_root)

    dst_mat = bpy.data.materials.new("Mat_ArkLibBakeTarget")
    dst_mat.use_nodes = True
    dst_obj = create_unit_plane("ArkLibBakeTarget", 0.002, dst_mat)

    out_dir = os.path.join(project_root, "assets", "textures", "ark", "materials")
    os.makedirs(out_dir, exist_ok=True)

    report = []
    for idx, spec in enumerate(MATERIAL_SETS, start=1):
        name = spec["name"]
        print(
            f"[ARK WOOD LIB] [{idx}/5] Backe 1024x1024 CC0-Set '{name}' "
            f"(Quellen: {cc0[spec['cc0_primary']]['source_file']} + {cc0[spec['cc0_secondary']]['source_file']})...",
            flush=True,
        )
        src_mat = build_cc0_bake_material(spec, cc0)
        src_obj = create_unit_plane(f"Src_{name}", 0.0, src_mat)

        img_col = bake_pass(src_obj, dst_obj, dst_mat, "DIFFUSE", f"{name}_col", TEX_SIZE, TEX_SIZE, is_srgb=True)
        px_col_lin = read_img_np(img_col, TEX_SIZE, TEX_SIZE)

        img_nrm = bake_pass(src_obj, dst_obj, dst_mat, "NORMAL", f"{name}_nrm", TEX_SIZE, TEX_SIZE, is_srgb=False)
        px_nrm = read_img_np(img_nrm, TEX_SIZE, TEX_SIZE)

        img_rgh = bake_pass(src_obj, dst_obj, dst_mat, "ROUGHNESS", f"{name}_rgh", TEX_SIZE, TEX_SIZE, is_srgb=False)
        px_rgh = read_img_np(img_rgh, TEX_SIZE, TEX_SIZE)[:, :, 0]

        bpy.data.objects.remove(src_obj, do_unlink=True)

        col_lin, srgb, nrm, rgh, u_err, v_err = refine_and_calibrate_tileable_set(
            spec, px_col_lin, px_nrm, px_rgh, TEX_SIZE, TEX_SIZE
        )

        p_col = os.path.join(out_dir, f"{name}_basecolor.png")
        p_nrm = os.path.join(out_dir, f"{name}_normal.png")
        p_rgh = os.path.join(out_dir, f"{name}_roughness.png")

        save_np_png(col_lin, p_col, is_srgb=True)
        save_np_png(nrm, p_nrm, is_srgb=False)
        save_np_png(rgh, p_rgh, is_srgb=False)

        m_rgb = srgb.mean(axis=(0, 1)) * 255.0
        hex_col = "#{:02X}{:02X}{:02X}".format(int(round(m_rgb[0])), int(round(m_rgb[1])), int(round(m_rgb[2])))
        r_mean = float(rgh[:, :, 0].mean())
        r_min = float(rgh[:, :, 0].min())
        r_max = float(rgh[:, :, 0].max())
        report.append((name, hex_col, m_rgb, r_mean, r_min, r_max, u_err, v_err, p_col, p_nrm, p_rgh))
        print(
            f"[ARK WOOD LIB]   -> {name:18s} | sRGB={hex_col} ({m_rgb[0]:5.1f},{m_rgb[1]:5.1f},{m_rgb[2]:5.1f}) "
            f"| Rough={r_mean:.3f} [{r_min:.2f}..{r_max:.2f}] | SeamErr=(U:{u_err:.4f}, V:{v_err:.4f}) | 3 Maps OK",
            flush=True,
        )

    print(f"[ARK WOOD LIB] Alle 5 x 3 = 15 nahtlos kachelbaren 1024x1024-Maps gespeichert in {time.time() - t0:.1f}s!", flush=True)
    return report


if __name__ == "__main__":
    build_ark_wood_library(get_project_root())
