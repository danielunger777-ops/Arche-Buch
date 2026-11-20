"""
build_temenos_hero_atlas.py — Hero-Temenos 2048x2048 Trim-Sheet (CC0 ambientCG) + 1024x1024 Tempel-Botanik-Atlas
=================================================================================================================
Erzeugt:
  1) 2048x2048 Hero-Temenos-Trim-Sheet (Cycles CUDA GTX 1070 / CPU-Fallback, 5 HDR/AgX-Regeln,
     echte ambientCG CC0 1K-Scans aus assets/textures/cc0/):
     - assets/textures/temenos_hero_trim_baseColor.png  [sRGB, Albedo 0.04..0.82, 0 Sonnenschatten]
     - assets/textures/temenos_hero_trim_normal.png     [Linear / Non-Color]
     - assets/textures/temenos_hero_trim_orm.png        [Linear: R=AO, G=Roughness, B=Metallic]
     - assets/textures/temenos_hero_trim_emissive.png   [sRGB: Gluehende Holzkohle/Glut]
  2) 1024x1024 Tempel-Botanik-Atlas (3x3 Quadrat-Zellen, sauberer Alpha-Cutout):
     - assets/textures/temenos_botany_atlas_baseColor.png  [sRGB RGBA]
     - assets/textures/temenos_botany_atlas_normal.png     [Linear]
     - assets/textures/temenos_botany_atlas_orm.png        [Linear]
     - assets/textures/temenos_botany_atlas_thickness.png  [Linear]

Aufruf:
  blender --background --python assets/scripts/build_temenos_hero_atlas.py
"""

import os
import sys
import time
import math
import bpy
import numpy as np

TRIM_W = 2048
TRIM_H = 2048
BOT_W = 1024
BOT_H = 1024

# Gemeinsame UV-Regionen (u0, v0, u1, v1) mit Padding gegen Mipmap-Bleed
TEMENOS_TRIM_REGIONS = {
    # Band 0: Warmer gebrannter Terrakotta-Ocker-Lehmziegel (Ziggurat Stufe 1 & 3, Mauern, Nebengebaeude)
    "brick_terracotta":     (0.000, 0.005, 1.000, 0.178),
    "brick_terracotta_low": (0.000, 0.005, 1.000, 0.062),
    "brick_terracotta_hi":  (0.000, 0.055, 1.000, 0.178),
    # Band 1: Heller warmer Sand-Lehmziegel (Ziggurat Stufe 2, Innenhoefe)
    "brick_sand":           (0.000, 0.186, 1.000, 0.356),
    # Band 2: Heller Travertin / Kalkstein (Prozessionsplatten, Beckenraender, Altar, Stufen)
    "travertine":           (0.000, 0.365, 1.000, 0.532),
    # Band 3: Glasierter Lapislazuli-Ziegel & Goldener Ischtar-/Nanna-Rosetten-Fries
    "lapis_brick":          (0.000, 0.542, 1.000, 0.616),
    "lapis_rosette_frieze": (0.000, 0.624, 1.000, 0.694),
    # Band 4: Dunkler Fluss-Mosaikstein | Zedernholz | Geflochtene Schilfmatte
    "river_mosaic":         (0.005, 0.703, 0.338, 0.842),
    "cedar_wood":           (0.352, 0.703, 0.662, 0.842),
    "reed_mat":             (0.676, 0.703, 0.995, 0.842),
    # Band 5: Gehaemmerte Zinnbronze | Terrakotta-Kuebel | Feuchte Gartenerde | Gluehende Kohle | Stele-Relief
    "tin_bronze":           (0.005, 0.853, 0.212, 0.995),
    "terracotta_pot":       (0.226, 0.853, 0.412, 0.995),
    "garden_soil":          (0.426, 0.853, 0.612, 0.995),
    "glowing_embers":       (0.626, 0.853, 0.802, 0.995),
    "stele_relief":         (0.816, 0.853, 0.995, 0.995),
}

# 3x3 Botanik-Atlas UV-Zellen (col, row) mit 0=unten .. 2=oben
BOTANY_CELLS = {
    "ivy":          (0, 0),
    "pomegranate":  (1, 0),
    "cypress":      (2, 0),
    "oleander":     (0, 1),
    "fig":          (1, 1),
    "papyrus":      (2, 1),
    "lilypad":      (0, 2),
    "lotus_pink":   (1, 2),
    "lotus_white":  (2, 2),
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


def load_cc0_packs(project_root):
    """Laedt die 9 ambientCG CC0 1K .packed.blend-Scans aus assets/textures/cc0/."""
    cc0_dir = os.path.join(project_root, "assets", "textures", "cc0")
    pack_files = {
        "brick_warm":  "Bricks001_1K-JPG.packed.blend",
        "brick_sand":  "Bricks002_1K-JPG.packed.blend",
        "travertine":  "Travertine001_1K-JPG.packed.blend",
        "mosaic":      "Tiles002_1K-JPG.packed.blend",
        "bronze":      "Metal007_1K-JPG.packed.blend",
        "cedar":       "Wood004_1K-JPG.packed.blend",
        "reed":        "Wicker001_1K-JPG.packed.blend",
        "terracotta":  "Clay001_1K-JPG.packed.blend",
        "soil":        "Ground003_1K-JPG.packed.blend",
    }
    loaded = {}
    for key, fname in pack_files.items():
        fpath = os.path.join(cc0_dir, fname)
        if not os.path.exists(fpath):
            print(f"[TEMENOS ATLAS] WARN: CC0 pack fehlt: {fpath}", flush=True)
            continue
        before = set(bpy.data.images.keys())
        with bpy.data.libraries.load(fpath, link=False) as (data_from, data_to):
            data_to.images = list(data_from.images)
        new_imgs = [bpy.data.images[n] for n in bpy.data.images.keys() if n not in before]
        pack = {}
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
        print(f"[TEMENOS ATLAS] CC0 geladen ({key} <- {fname}): {sorted(pack.keys())}", flush=True)
    return loaded


def _add_tex_node(nodes, img, uv_out, links, scale=(1.0, 1.0), is_color=True):
    mp = nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale[0], scale[1], 1.0)
    links.new(uv_out, mp.inputs["Vector"])
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.extension = "REPEAT"
    links.new(mp.outputs["Vector"], tex.inputs["Vector"])
    return tex


def _tint_cc0_color(nodes, links, color_out, mult_rgb, add_rgb=(0.0, 0.0, 0.0), sat_val=(1.0, 1.0)):
    """Tont eine CC0-BaseColor sanft in den sumerischen HDR-Korridor (0.04..0.82)."""
    hsv = nodes.new("ShaderNodeHueSaturation")
    hsv.inputs["Saturation"].default_value = sat_val[0]
    hsv.inputs["Value"].default_value = sat_val[1]
    links.new(color_out, hsv.inputs["Color"])

    mul = nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    mul.inputs[7].default_value = (mult_rgb[0], mult_rgb[1], mult_rgb[2], 1.0)
    links.new(hsv.outputs["Color"], mul.inputs[6])

    if any(abs(c) > 1e-4 for c in add_rgb):
        add = nodes.new("ShaderNodeMix")
        add.data_type = "RGBA"
        add.blend_type = "ADD"
        add.inputs["Factor"].default_value = 1.0
        add.inputs[7].default_value = (add_rgb[0], add_rgb[1], add_rgb[2], 1.0)
        links.new(mul.outputs[2], add.inputs[6])
        return add.outputs[2]
    return mul.outputs[2]


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
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(uv, sep.inputs["Vector"])

    # Defaults
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.78
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.45

    def apply_cc0_pack(pack_key, tile, mult_rgb, add_rgb, sat_val, r_range, norm_str=1.0, metallic=0.0):
        pack = cc0.get(pack_key, {})
        bsdf.inputs["Metallic"].default_value = metallic
        col_out = None
        if "color" in pack:
            t_col = _add_tex_node(nodes, pack["color"], uv, links, scale=tile, is_color=True)
            col_out = _tint_cc0_color(nodes, links, t_col.outputs["Color"], mult_rgb, add_rgb, sat_val)
            # Bake subtle AO into albedo (only 25% so no dark shadows, pure crevice richness)
            if "ao" in pack:
                t_ao = _add_tex_node(nodes, pack["ao"], uv, links, scale=tile, is_color=False)
                ao_mix = nodes.new("ShaderNodeMix")
                ao_mix.data_type = "RGBA"
                ao_mix.blend_type = "MULTIPLY"
                ao_mix.inputs["Factor"].default_value = 0.28
                links.new(col_out, ao_mix.inputs[6])
                links.new(t_ao.outputs["Color"], ao_mix.inputs[7])
                col_out = ao_mix.outputs[2]
            links.new(col_out, bsdf.inputs["Base Color"])
        if "roughness" in pack:
            t_r = _add_tex_node(nodes, pack["roughness"], uv, links, scale=tile, is_color=False)
            links.new(_remap_rough(nodes, links, t_r.outputs["Color"], r_range[0], r_range[1]), bsdf.inputs["Roughness"])
        else:
            bsdf.inputs["Roughness"].default_value = 0.5 * (r_range[0] + r_range[1])
        if "normal" in pack:
            t_n = _add_tex_node(nodes, pack["normal"], uv, links, scale=tile, is_color=False)
            nm = nodes.new("ShaderNodeNormalMap")
            nm.inputs["Strength"].default_value = norm_str
            links.new(t_n.outputs["Color"], nm.inputs["Color"])
            links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
        return col_out

    if kind == "brick_terracotta":
        # Warmer gebrannter sumerischer Terrakotta-Ocker-Ziegel + leichte Sockelfeuchte unten (V < 0.28)
        col = apply_cc0_pack(
            "brick_warm", tile=(8.0, 2.0),
            mult_rgb=(1.05, 0.78, 0.55), add_rgb=(0.06, 0.025, 0.01),
            sat_val=(1.15, 0.92), r_range=(0.74, 0.92), norm_str=1.15
        )
        # Subtle damp darkening near bottom edge of band (local V in [0..0.28])
        if col is not None:
            mr = nodes.new("ShaderNodeMapRange")
            mr.inputs["From Min"].default_value = 0.0
            mr.inputs["From Max"].default_value = 0.30
            mr.inputs["To Min"].default_value = 0.68
            mr.inputs["To Max"].default_value = 1.0
            mr.clamp = True
            links.new(sep.outputs["Y"], mr.inputs["Value"])
            dm = nodes.new("ShaderNodeMix")
            dm.data_type = "RGBA"
            dm.blend_type = "MULTIPLY"
            dm.inputs["Factor"].default_value = 1.0
            links.new(col, dm.inputs[6])
            comb = nodes.new("ShaderNodeCombineColor")
            links.new(mr.outputs["Result"], comb.inputs["Red"])
            links.new(mr.outputs["Result"], comb.inputs["Green"])
            links.new(mr.outputs["Result"], comb.inputs["Blue"])
            links.new(comb.outputs["Color"], dm.inputs[7])
            links.new(dm.outputs[2], bsdf.inputs["Base Color"])

    elif kind == "brick_sand":
        # Heller warmer Sand-Lehmziegel (Stufe 2 — sonnig-goldener Sandton, kein steriles Grau!)
        apply_cc0_pack(
            "brick_sand", tile=(8.0, 2.0),
            mult_rgb=(1.12, 0.94, 0.68), add_rgb=(0.08, 0.055, 0.025),
            sat_val=(1.08, 1.02), r_range=(0.76, 0.93), norm_str=1.05
        )

    elif kind == "travertine":
        # Heller Travertin / Kalkstein fuer Prozessionsplatten, Beckenraender, Altar
        apply_cc0_pack(
            "travertine", tile=(6.0, 1.5),
            mult_rgb=(1.04, 0.97, 0.84), add_rgb=(0.05, 0.04, 0.025),
            sat_val=(0.88, 1.02), r_range=(0.62, 0.84), norm_str=0.85
        )

    elif kind == "lapis_brick":
        # Glasierte tiefblaue Lapislazuli-Ziegel mit feinen Pyrit-Goldsprenkeln (Roughness 0.24..0.32)
        pack = cc0.get("brick_warm", {})
        # Brick normal from CC0
        if "normal" in pack:
            t_n = _add_tex_node(nodes, pack["normal"], uv, links, scale=(10.0, 1.2), is_color=False)
            nm = nodes.new("ShaderNodeNormalMap")
            nm.inputs["Strength"].default_value = 0.80
            links.new(t_n.outputs["Color"], nm.inputs["Color"])
            links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
        # Rich lapis color variation + mortar + gold pyrite flecks
        n_var = nodes.new("ShaderNodeTexNoise")
        n_var.inputs["Scale"].default_value = 18.0
        n_var.inputs["Detail"].default_value = 6.0
        links.new(uv, n_var.inputs["Vector"])
        cr = nodes.new("ShaderNodeValToRGB")
        cr.color_ramp.elements[0].position = 0.25
        cr.color_ramp.elements[0].color = (0.045, 0.11, 0.34, 1.0)
        cr.color_ramp.elements[1].position = 0.78
        cr.color_ramp.elements[1].color = (0.095, 0.23, 0.56, 1.0)
        links.new(n_var.outputs["Fac"], cr.inputs["Fac"])
        # Subtle gold pyrite flecks
        vor = nodes.new("ShaderNodeTexVoronoi")
        vor.inputs["Scale"].default_value = 85.0
        links.new(uv, vor.inputs["Vector"])
        gt = nodes.new("ShaderNodeMath")
        gt.operation = "LESS_THAN"
        gt.inputs[1].default_value = 0.08
        links.new(vor.outputs["Distance"], gt.inputs[0])
        mix_g = nodes.new("ShaderNodeMix")
        mix_g.data_type = "RGBA"
        mix_g.inputs[7].default_value = (0.68, 0.52, 0.18, 1.0)
        links.new(gt.outputs["Value"], mix_g.inputs["Factor"])
        links.new(cr.outputs["Color"], mix_g.inputs[6])
        links.new(mix_g.outputs[2], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.27
        if "Coat Weight" in bsdf.inputs:
            bsdf.inputs["Coat Weight"].default_value = 0.45
            bsdf.inputs["Coat Roughness"].default_value = 0.18

    elif kind == "lapis_rosette_frieze":
        # Glasierter Lapislazuli-Fries mit wiederkehrenden goldenen 8-strahliger Ischtar/Nanna-Rosetten
        # Procedural math in UV space: 12 rosettes along U, top/bottom gold borders
        # Local U in [0..1], V in [0..1]
        # Gold border at V < 0.14 or V > 0.86
        v_low = nodes.new("ShaderNodeMath"); v_low.operation = "LESS_THAN"; v_low.inputs[1].default_value = 0.13
        links.new(sep.outputs["Y"], v_low.inputs[0])
        v_hi = nodes.new("ShaderNodeMath"); v_hi.operation = "GREATER_THAN"; v_hi.inputs[1].default_value = 0.87
        links.new(sep.outputs["Y"], v_hi.inputs[0])
        border = nodes.new("ShaderNodeMath"); border.operation = "MAXIMUM"
        links.new(v_low.outputs["Value"], border.inputs[0])
        links.new(v_hi.outputs["Value"], border.inputs[1])

        # Rosette grid: 16 cells along U
        u_mul = nodes.new("ShaderNodeMath"); u_mul.operation = "MULTIPLY"; u_mul.inputs[1].default_value = 16.0
        links.new(sep.outputs["X"], u_mul.inputs[0])
        u_fr = nodes.new("ShaderNodeMath"); u_fr.operation = "FRACT"
        links.new(u_mul.outputs["Value"], u_fr.inputs[0])
        dx = nodes.new("ShaderNodeMath"); dx.operation = "SUBTRACT"; dx.inputs[1].default_value = 0.5
        links.new(u_fr.outputs["Value"], dx.inputs[0])
        dy = nodes.new("ShaderNodeMath"); dy.operation = "SUBTRACT"; dy.inputs[1].default_value = 0.5
        links.new(sep.outputs["Y"], dy.inputs[0])
        dx2 = nodes.new("ShaderNodeMath"); dx2.operation = "MULTIPLY"; links.new(dx.outputs["Value"], dx2.inputs[0]); links.new(dx.outputs["Value"], dx2.inputs[1])
        dy2 = nodes.new("ShaderNodeMath"); dy2.operation = "MULTIPLY"; links.new(dy.outputs["Value"], dy2.inputs[0]); links.new(dy.outputs["Value"], dy2.inputs[1])
        r2 = nodes.new("ShaderNodeMath"); r2.operation = "ADD"; links.new(dx2.outputs["Value"], r2.inputs[0]); links.new(dy2.outputs["Value"], r2.inputs[1])
        rad = nodes.new("ShaderNodeMath"); rad.operation = "SQRT"; links.new(r2.outputs["Value"], rad.inputs[0])

        ang = nodes.new("ShaderNodeMath"); ang.operation = "ARCTAN2"
        links.new(dy.outputs["Value"], ang.inputs[0]); links.new(dx.outputs["Value"], ang.inputs[1])
        a8 = nodes.new("ShaderNodeMath"); a8.operation = "MULTIPLY"; a8.inputs[1].default_value = 8.0
        links.new(ang.outputs["Value"], a8.inputs[0])
        c8 = nodes.new("ShaderNodeMath"); c8.operation = "COSINE"
        links.new(a8.outputs["Value"], c8.inputs[0])
        # Petal radius = 0.22 + 0.11 * cos(8 * theta)
        p_amp = nodes.new("ShaderNodeMath"); p_amp.operation = "MULTIPLY"; p_amp.inputs[1].default_value = 0.11
        links.new(c8.outputs["Value"], p_amp.inputs[0])
        p_rad = nodes.new("ShaderNodeMath"); p_rad.operation = "ADD"; p_rad.inputs[1].default_value = 0.21
        links.new(p_amp.outputs["Value"], p_rad.inputs[0])
        in_petal = nodes.new("ShaderNodeMath"); in_petal.operation = "LESS_THAN"
        links.new(rad.outputs["Value"], in_petal.inputs[0]); links.new(p_rad.outputs["Value"], in_petal.inputs[1])
        in_core = nodes.new("ShaderNodeMath"); in_core.operation = "LESS_THAN"; in_core.inputs[1].default_value = 0.10
        links.new(rad.outputs["Value"], in_core.inputs[0])

        # Gold mask = border OR core; ivory/gold petals = in_petal
        gold_mask = nodes.new("ShaderNodeMath"); gold_mask.operation = "MAXIMUM"
        links.new(border.outputs["Value"], gold_mask.inputs[0])
        links.new(in_core.outputs["Value"], gold_mask.inputs[1])
        orn_mask = nodes.new("ShaderNodeMath"); orn_mask.operation = "MAXIMUM"
        links.new(gold_mask.outputs["Value"], orn_mask.inputs[0])
        links.new(in_petal.outputs["Value"], orn_mask.inputs[1])

        # Base lapis -> ivory-cream petals -> rich gold border/center
        m1 = nodes.new("ShaderNodeMix"); m1.data_type = "RGBA"
        m1.inputs[6].default_value = (0.048, 0.125, 0.38, 1.0)
        m1.inputs[7].default_value = (0.74, 0.64, 0.42, 1.0)
        links.new(in_petal.outputs["Value"], m1.inputs["Factor"])

        m2 = nodes.new("ShaderNodeMix"); m2.data_type = "RGBA"
        m2.inputs[7].default_value = (0.72, 0.54, 0.16, 1.0)
        links.new(gold_mask.outputs["Value"], m2.inputs["Factor"])
        links.new(m1.outputs[2], m2.inputs[6])
        links.new(m2.outputs[2], bsdf.inputs["Base Color"])

        # Metallic on gold border/center
        m_met = nodes.new("ShaderNodeMath"); m_met.operation = "MULTIPLY"; m_met.inputs[1].default_value = 0.80
        links.new(gold_mask.outputs["Value"], m_met.inputs[0])
        links.new(m_met.outputs["Value"], bsdf.inputs["Metallic"])

        # Glossy glaze roughness ~0.24..0.30
        bsdf.inputs["Roughness"].default_value = 0.25
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.55
        bump.inputs["Distance"].default_value = 0.015
        links.new(orn_mask.outputs["Value"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    elif kind == "river_mosaic":
        # Dunkler geaederter Fluss-Mosaikstein fuer den tiefen Abzu-Beckenboden
        apply_cc0_pack(
            "mosaic", tile=(3.0, 2.0),
            mult_rgb=(0.24, 0.34, 0.36), add_rgb=(0.02, 0.035, 0.042),
            sat_val=(1.10, 0.85), r_range=(0.26, 0.42), norm_str=1.05
        )

    elif kind == "cedar_wood":
        apply_cc0_pack(
            "cedar", tile=(2.0, 2.0),
            mult_rgb=(0.95, 0.68, 0.46), add_rgb=(0.03, 0.012, 0.005),
            sat_val=(1.12, 0.88), r_range=(0.56, 0.76), norm_str=0.95
        )

    elif kind == "reed_mat":
        apply_cc0_pack(
            "reed", tile=(3.5, 2.0),
            mult_rgb=(1.08, 0.92, 0.62), add_rgb=(0.04, 0.03, 0.012),
            sat_val=(1.05, 0.96), r_range=(0.76, 0.92), norm_str=1.10
        )

    elif kind == "tin_bronze":
        apply_cc0_pack(
            "bronze", tile=(2.0, 2.0),
            mult_rgb=(0.88, 0.64, 0.34), add_rgb=(0.08, 0.045, 0.015),
            sat_val=(1.15, 0.95), r_range=(0.24, 0.42), norm_str=0.80, metallic=0.92
        )

    elif kind == "terracotta_pot":
        apply_cc0_pack(
            "terracotta", tile=(2.0, 2.0),
            mult_rgb=(1.12, 0.62, 0.38), add_rgb=(0.07, 0.022, 0.01),
            sat_val=(1.22, 0.95), r_range=(0.66, 0.82), norm_str=0.75
        )

    elif kind == "garden_soil":
        apply_cc0_pack(
            "soil", tile=(2.5, 2.5),
            mult_rgb=(0.42, 0.34, 0.26), add_rgb=(0.02, 0.014, 0.01),
            sat_val=(0.95, 0.72), r_range=(0.78, 0.94), norm_str=1.20
        )

    elif kind == "glowing_embers":
        # Dunkle Holzkohle + glühende orange-rote Glut in Emissive!
        vor = nodes.new("ShaderNodeTexVoronoi")
        vor.feature = "DISTANCE_TO_EDGE"
        vor.inputs["Scale"].default_value = 14.0
        links.new(uv, vor.inputs["Vector"])
        noi = nodes.new("ShaderNodeTexNoise")
        noi.inputs["Scale"].default_value = 24.0
        noi.inputs["Detail"].default_value = 5.0
        links.new(uv, noi.inputs["Vector"])

        cr_col = nodes.new("ShaderNodeValToRGB")
        cr_col.color_ramp.elements[0].position = 0.04
        cr_col.color_ramp.elements[0].color = (0.45, 0.14, 0.02, 1.0)
        cr_col.color_ramp.elements[1].position = 0.20
        cr_col.color_ramp.elements[1].color = (0.055, 0.045, 0.042, 1.0)
        links.new(vor.outputs["Distance"], cr_col.inputs["Fac"])
        links.new(cr_col.outputs["Color"], bsdf.inputs["Base Color"])

        cr_em = nodes.new("ShaderNodeValToRGB")
        cr_em.color_ramp.elements[0].position = 0.00
        cr_em.color_ramp.elements[0].color = (1.0, 0.42, 0.05, 1.0)
        e_mid = cr_em.color_ramp.elements.new(0.11)
        e_mid.color = (0.85, 0.16, 0.01, 1.0)
        cr_em.color_ramp.elements[2].position = 0.24
        cr_em.color_ramp.elements[2].color = (0.0, 0.0, 0.0, 1.0)
        links.new(vor.outputs["Distance"], cr_em.inputs["Fac"])
        if "Emission Color" in bsdf.inputs:
            links.new(cr_em.outputs["Color"], bsdf.inputs["Emission Color"])
            bsdf.inputs["Emission Strength"].default_value = 1.0
        bsdf.inputs["Roughness"].default_value = 0.88
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.85
        links.new(noi.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    elif kind == "stele_relief":
        # Kalkstein-Stele mit eingraviertem Keilschrift- & Mondsichel-Relief (Nanna)
        apply_cc0_pack(
            "travertine", tile=(1.5, 1.5),
            mult_rgb=(1.02, 0.94, 0.80), add_rgb=(0.04, 0.032, 0.02),
            sat_val=(0.88, 0.98), r_range=(0.64, 0.84), norm_str=0.55
        )
        # Add carved horizontal cuneiform register lines + crescent emblem
        wave = nodes.new("ShaderNodeTexWave")
        wave.wave_type = "BANDS"
        wave.bands_direction = "Y"
        wave.inputs["Scale"].default_value = 14.0
        wave.inputs["Distortion"].default_value = 1.6
        wave.inputs["Detail"].default_value = 4.0
        links.new(uv, wave.inputs["Vector"])
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.55
        bump.inputs["Distance"].default_value = 0.012
        links.new(wave.outputs["Fac"], bump.inputs["Height"])
        # Chain with existing normal if present
        if bsdf.inputs["Normal"].is_linked:
            orig_n = bsdf.inputs["Normal"].links[0].from_socket
            links.new(orig_n, bump.inputs["Normal"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    return mat


def create_atlas_plane(cc0):
    """Erstellt ein 1x1-m-Mesh mit exakt zugeordneten Material-Streifen fuer den 2048x2048-Bake."""
    import bmesh
    mesh = bpy.data.meshes.new("TemenosAtlasSource")
    obj = bpy.data.objects.new("TemenosAtlasSource", mesh)
    bpy.context.collection.objects.link(obj)

    strips = [
        ("brick_terracotta",     0.000, 0.000, 1.000, 0.182),
        ("brick_sand",           0.000, 0.182, 1.000, 0.360),
        ("travertine",           0.000, 0.360, 1.000, 0.538),
        ("lapis_brick",          0.000, 0.538, 1.000, 0.620),
        ("lapis_rosette_frieze", 0.000, 0.620, 1.000, 0.698),
        ("river_mosaic",         0.000, 0.698, 0.345, 0.848),
        ("cedar_wood",           0.345, 0.698, 0.670, 0.848),
        ("reed_mat",             0.670, 0.698, 1.000, 0.848),
        ("tin_bronze",           0.000, 0.848, 0.220, 1.000),
        ("terracotta_pot",       0.220, 0.848, 0.420, 1.000),
        ("garden_soil",          0.420, 0.848, 0.620, 1.000),
        ("glowing_embers",       0.620, 0.848, 0.810, 1.000),
        ("stele_relief",         0.810, 0.848, 1.000, 1.000),
    ]

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    for idx, (kind, u0, v0, u1, v1) in enumerate(strips):
        mat = build_strip_material(f"Mat_Temenos_{kind}", kind, cc0)
        obj.data.materials.append(mat)
        v00 = bm.verts.new((u0, v0, 0.0))
        v10 = bm.verts.new((u1, v0, 0.0))
        v11 = bm.verts.new((u1, v1, 0.0))
        v01 = bm.verts.new((u0, v1, 0.0))
        f = bm.faces.new((v00, v10, v11, v01))
        f.material_index = idx
        # Local UV [0..1] per strip so every CC0 texture fills its strip cleanly!
        uvs = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        for loop, uv_co in zip(f.loops, uvs):
            loop[uv_layer].uv = uv_co

    bm.to_mesh(mesh)
    bm.free()
    return obj


def create_bake_target():
    import bmesh
    mesh = bpy.data.meshes.new("TemenosAtlasTarget")
    obj = bpy.data.objects.new("TemenosAtlasTarget", mesh)
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

    mat = bpy.data.materials.new("Mat_BakeTarget")
    mat.use_nodes = True
    obj.data.materials.append(mat)
    return obj, mat


def bake_pass(src_obj, dst_obj, dst_mat, bake_type, img_name, width, height, is_srgb=True):
    img = bpy.data.images.new(img_name, width=width, height=height, alpha=False, float_buffer=False)
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


def bake_metallic_via_emit(src_obj, dst_obj, dst_mat, width, height):
    """Backt Metallic-Werte sauber ueber temporaere Emission-Umschaltung."""
    saved = []
    for mat in src_obj.data.materials:
        nt = mat.node_tree
        bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
        orig_link = out.inputs["Surface"].links[0].from_socket
        em = nt.nodes.new("ShaderNodeEmission")
        met_in = bsdf.inputs["Metallic"]
        if met_in.is_linked:
            nt.links.new(met_in.links[0].from_socket, em.inputs["Color"])
        else:
            v = met_in.default_value
            em.inputs["Color"].default_value = (v, v, v, 1.0)
        nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
        saved.append((nt, out, orig_link, em))

    img = bake_pass(src_obj, dst_obj, dst_mat, "EMIT", "Bake_Metallic", width, height, is_srgb=False)

    for nt, out, orig_link, em in saved:
        nt.links.new(orig_link, out.inputs["Surface"])
        nt.nodes.remove(em)
    return img


def bake_basecolor_unmetallic(src_obj, dst_obj, dst_mat, width, height):
    """Backt BaseColor sauber ohne Cycles-Metallic-Abdunklung (glTF PBR erwartet volle Albedo auf Metallen!)."""
    saved = []
    for mat in src_obj.data.materials:
        nt = mat.node_tree
        bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        met_in = bsdf.inputs["Metallic"]
        if met_in.is_linked:
            src_sock = met_in.links[0].from_socket
            nt.links.remove(met_in.links[0])
            met_in.default_value = 0.0
            saved.append((nt, met_in, src_sock, None))
        elif met_in.default_value > 0.0:
            saved.append((nt, met_in, None, met_in.default_value))
            met_in.default_value = 0.0

    img = bake_pass(src_obj, dst_obj, dst_mat, "DIFFUSE", "Temenos_BaseColor", width, height, is_srgb=True)

    for nt, met_in, src_sock, old_val in saved:
        if src_sock is not None:
            nt.links.new(src_sock, met_in)
        elif old_val is not None:
            met_in.default_value = old_val
    return img


def save_np_png(arr, path, is_srgb=True, has_alpha=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    h, w, ch = arr.shape
    rgba = np.ones((h, w, 4), dtype=np.float32)
    if ch == 4:
        rgba[:] = np.clip(arr, 0.0, 1.0)
    else:
        rgba[:, :, :3] = np.clip(arr, 0.0, 1.0)
    img = bpy.data.images.new("_SaveTmp", width=w, height=h, alpha=has_alpha, float_buffer=False)
    img.colorspace_settings.name = "sRGB" if is_srgb else "Non-Color"
    img.pixels.foreach_set(rgba.ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    scene = bpy.context.scene
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA" if has_alpha else "RGB"
    scene.render.image_settings.color_depth = "8"
    img.save()
    bpy.data.images.remove(img)


def read_img_np(img, w, h):
    buf = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(buf)
    return buf.reshape((h, w, 4))


def _linear_to_srgb(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(np.maximum(x, 0.0031308), 1.0 / 2.4) - 0.055)


def build_temenos_trim_sheet(project_root):
    t0 = time.time()
    print("[TEMENOS ATLAS] Starte 2048x2048 Hero-Temenos-Trim-Sheet (CC0 ambientCG)...", flush=True)
    scene = clear_scene()
    dev = setup_cycles(scene, samples=4)
    print(f"[TEMENOS ATLAS] Cycles Device: {dev}", flush=True)

    cc0 = load_cc0_packs(project_root)
    src_obj = create_atlas_plane(cc0)
    dst_obj, dst_mat = create_bake_target()

    tex_dir = os.path.join(project_root, "assets", "textures")
    os.makedirs(tex_dir, exist_ok=True)

    # 1) BaseColor (Diffuse Color, 0 sun shadows, un-darkened metallic albedo!)
    print("[TEMENOS ATLAS] Backe BaseColor [sRGB]...", flush=True)
    img_col = bake_basecolor_unmetallic(src_obj, dst_obj, dst_mat, TRIM_W, TRIM_H)
    px_col = read_img_np(img_col, TRIM_W, TRIM_H)
    px_col[:, :, :3] = np.clip(px_col[:, :, :3], 0.04, 0.82)
    print(f"[TEMENOS ATLAS] BaseColor stats: min={px_col[:,:,:3].min():.3f}, mean={px_col[:,:,:3].mean():.3f}, max={px_col[:,:,:3].max():.3f}", flush=True)
    p_col = os.path.join(tex_dir, "temenos_hero_trim_baseColor.png")
    save_np_png(px_col[:, :, :3], p_col, is_srgb=True, has_alpha=False)
    print(f"[TEMENOS ATLAS] Gespeichert: {p_col}", flush=True)

    # 2) Normal (Tangent-Space, Linear)
    print("[TEMENOS ATLAS] Backe Normal [Linear]...", flush=True)
    img_nrm = bake_pass(src_obj, dst_obj, dst_mat, "NORMAL", "Temenos_Normal", TRIM_W, TRIM_H, is_srgb=False)
    px_nrm = read_img_np(img_nrm, TRIM_W, TRIM_H)
    p_nrm = os.path.join(tex_dir, "temenos_hero_trim_normal.png")
    save_np_png(px_nrm[:, :, :3], p_nrm, is_srgb=False, has_alpha=False)
    print(f"[TEMENOS ATLAS] Gespeichert: {p_nrm}", flush=True)

    # 3) Roughness + Metallic -> ORM (R=AO, G=Roughness, B=Metallic)
    print("[TEMENOS ATLAS] Backe Roughness & Metallic -> ORM [Linear]...", flush=True)
    img_rgh = bake_pass(src_obj, dst_obj, dst_mat, "ROUGHNESS", "Temenos_Roughness", TRIM_W, TRIM_H, is_srgb=False)
    img_met = bake_metallic_via_emit(src_obj, dst_obj, dst_mat, TRIM_W, TRIM_H)

    px_rgh = read_img_np(img_rgh, TRIM_W, TRIM_H)[:, :, 0]
    px_met = read_img_np(img_met, TRIM_W, TRIM_H)[:, :, 0]
    nz = np.clip(px_nrm[:, :, 2] * 2.0 - 1.0, 0.0, 1.0)
    ao = np.clip(0.76 + 0.24 * nz, 0.72, 1.0)

    orm = np.ones((TRIM_H, TRIM_W, 3), dtype=np.float32)
    orm[:, :, 0] = ao
    orm[:, :, 1] = np.clip(px_rgh, 0.14, 0.96)
    orm[:, :, 2] = np.clip(px_met, 0.0, 1.0)
    p_orm = os.path.join(tex_dir, "temenos_hero_trim_orm.png")
    save_np_png(orm, p_orm, is_srgb=False, has_alpha=False)
    print(f"[TEMENOS ATLAS] Gespeichert: {p_orm}", flush=True)

    # 4) Emissive (gluehende Holzkohle / Glut)
    print("[TEMENOS ATLAS] Backe Emissive [sRGB]...", flush=True)
    img_emi = bake_pass(src_obj, dst_obj, dst_mat, "EMIT", "Temenos_Emissive", TRIM_W, TRIM_H, is_srgb=True)
    px_emi = read_img_np(img_emi, TRIM_W, TRIM_H)
    p_emi = os.path.join(tex_dir, "temenos_hero_trim_emissive.png")
    save_np_png(px_emi[:, :, :3], p_emi, is_srgb=True, has_alpha=False)
    print(f"[TEMENOS ATLAS] Gespeichert: {p_emi} ({time.time() - t0:.1f}s)", flush=True)


# ==============================================================================
# 2) 1024x1024 TEMPEL-BOTANIK-ATLAS (3x3 Quadrat-Zellen, Alpha-Cutout)
# ==============================================================================

def _draw_leaf(buf_col, buf_a, buf_h, cx, cy, length, width, angle, col_base, col_tip, vein_str=0.14, notch=False):
    """Zeichnet ein scharfes, organisch geadertes Blatt mit Alpha & Hoehenprofil."""
    H, W = buf_a.shape
    rad = int(max(length, width) * 1.25) + 4
    x0, x1 = max(0, int(cx - rad)), min(W, int(cx + rad + 1))
    y0, y1 = max(0, int(cy - rad)), min(H, int(cy + rad + 1))
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx = xx - cx
    dy = yy - cy
    ca, sa = math.cos(-angle), math.sin(-angle)
    lx = dx * ca - dy * sa  # along leaf axis [0..length]
    ly = dx * sa + dy * ca  # across leaf [-width..width]

    if notch:
        # Round water-lily pad centered at (cx, cy) with V-notch on one side
        r = np.sqrt(lx * lx + ly * ly) / max(1.0, length)
        th = np.arctan2(ly, lx)
        mask = (r <= 1.0) & ~((lx > 0) & (np.abs(th) < 0.28))
        edge_aa = np.clip((1.0 - r) * 14.0, 0.0, 1.0)
        edge_aa = np.where((lx > 0) & (np.abs(th) < 0.28), 0.0, edge_aa)
        t_grad = np.clip(r, 0.0, 1.0)
        veins = 0.5 + 0.5 * np.cos(th * 14.0)
        h_val = (1.0 - 0.35 * r * r) + 0.12 * veins * (1.0 - r)
    else:
        u = lx / max(1.0, length)  # 0 at stem, 1 at tip
        # Organic pointed leaf silhouette
        w_env = np.maximum(0.0, np.sin(np.clip(u, 0.0, 1.0) * math.pi)) ** 0.72 * (1.0 - 0.25 * np.clip(u, 0.0, 1.0))
        v_norm = np.abs(ly) / np.maximum(1.0, width * w_env)
        inside = (u >= 0.0) & (u <= 1.0) & (v_norm <= 1.0)
        edge_aa = np.where(inside, np.clip((1.0 - v_norm) * 6.0, 0.0, 1.0) * np.clip(u * 12.0, 0.0, 1.0) * np.clip((1.0 - u) * 10.0, 0.0, 1.0), 0.0)
        t_grad = np.clip(u, 0.0, 1.0)
        midrib = np.exp(-((ly / max(1.0, width * 0.14)) ** 2))
        lat_vein = 0.5 + 0.5 * np.sin((u * 9.0 - np.abs(ly) / max(1.0, width) * 3.5) * math.pi)
        veins = np.clip(midrib * 0.8 + lat_vein * 0.35, 0.0, 1.0)
        h_val = (1.0 - 0.55 * np.clip(v_norm, 0.0, 1.0) ** 2) + 0.18 * midrib + 0.08 * lat_vein

    alpha = edge_aa
    if not np.any(alpha > 0.01):
        return
    c0 = np.array(col_base, dtype=np.float32)
    c1 = np.array(col_tip, dtype=np.float32)
    col = c0[None, None, :] * (1.0 - t_grad[:, :, None]) + c1[None, None, :] * t_grad[:, :, None]
    col = col * (1.0 + vein_str * (veins[:, :, None] - 0.5))
    col = np.clip(col, 0.04, 0.82)

    # Alpha composite over existing cell
    old_a = buf_a[y0:y1, x0:x1]
    out_a = alpha + old_a * (1.0 - alpha)
    safe_a = np.maximum(out_a, 1e-5)
    for ch in range(3):
        buf_col[y0:y1, x0:x1, ch] = (col[:, :, ch] * alpha + buf_col[y0:y1, x0:x1, ch] * old_a * (1.0 - alpha)) / safe_a
    buf_a[y0:y1, x0:x1] = np.clip(out_a, 0.0, 1.0)
    buf_h[y0:y1, x0:x1] = np.where(alpha > 0.35, np.maximum(buf_h[y0:y1, x0:x1], h_val * 0.85), buf_h[y0:y1, x0:x1])


def _draw_stem(buf_col, buf_a, buf_h, x0, y0, x1, y1, thickness, col_rgb):
    H, W = buf_a.shape
    pad = int(thickness) + 3
    bx0, bx1 = max(0, int(min(x0, x1) - pad)), min(W, int(max(x0, x1) + pad + 1))
    by0, by1 = max(0, int(min(y0, y1) - pad)), min(H, int(max(y0, y1) + pad + 1))
    if bx0 >= bx1 or by0 >= by1:
        return
    yy, xx = np.mgrid[by0:by1, bx0:bx1].astype(np.float32)
    vx, vy = x1 - x0, y1 - y0
    l2 = max(1e-4, vx * vx + vy * vy)
    t = np.clip(((xx - x0) * vx + (yy - y0) * vy) / l2, 0.0, 1.0)
    px, py = x0 + t * vx, y0 + t * vy
    dist = np.sqrt((xx - px) ** 2 + (yy - py) ** 2)
    alpha = np.clip((thickness - dist) * 1.8, 0.0, 1.0)
    old_a = buf_a[by0:by1, bx0:bx1]
    out_a = alpha + old_a * (1.0 - alpha)
    safe_a = np.maximum(out_a, 1e-5)
    for ch in range(3):
        buf_col[by0:by1, bx0:bx1, ch] = (col_rgb[ch] * alpha + buf_col[by0:by1, bx0:bx1, ch] * old_a * (1.0 - alpha)) / safe_a
    buf_a[by0:by1, bx0:bx1] = np.clip(out_a, 0.0, 1.0)
    buf_h[by0:by1, bx0:bx1] = np.where(alpha > 0.35, np.maximum(buf_h[by0:by1, bx0:bx1], 0.55), buf_h[by0:by1, bx0:bx1])


def _draw_fruit_or_center(buf_col, buf_a, buf_h, cx, cy, radius, col_rgb, hi_rgb):
    H, W = buf_a.shape
    r_i = int(radius) + 3
    x0, x1 = max(0, int(cx - r_i)), min(W, int(cx + r_i + 1))
    y0, y1 = max(0, int(cy - r_i)), min(H, int(cy + r_i + 1))
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx, dy = (xx - cx) / max(1.0, radius), (yy - cy) / max(1.0, radius)
    d = np.sqrt(dx * dx + dy * dy)
    alpha = np.clip((1.0 - d) * 6.0, 0.0, 1.0)
    sh = np.clip(1.0 - 0.55 * np.sqrt((dx + 0.25) ** 2 + (dy - 0.25) ** 2), 0.0, 1.0)
    c0, c1 = np.array(col_rgb, np.float32), np.array(hi_rgb, np.float32)
    col = c0[None, None, :] * (1.0 - sh[:, :, None]) + c1[None, None, :] * sh[:, :, None]
    old_a = buf_a[y0:y1, x0:x1]
    out_a = alpha + old_a * (1.0 - alpha)
    safe_a = np.maximum(out_a, 1e-5)
    for ch in range(3):
        buf_col[y0:y1, x0:x1, ch] = (col[:, :, ch] * alpha + buf_col[y0:y1, x0:x1, ch] * old_a * (1.0 - alpha)) / safe_a
    buf_a[y0:y1, x0:x1] = np.clip(out_a, 0.0, 1.0)
    buf_h[y0:y1, x0:x1] = np.where(alpha > 0.35, np.maximum(buf_h[y0:y1, x0:x1], np.sqrt(np.clip(1.0 - d * d, 0.0, 1.0))), buf_h[y0:y1, x0:x1])


def build_temenos_botany_atlas(project_root):
    t0 = time.time()
    print("[TEMENOS ATLAS] Erzeuge 1024x1024 Tempel-Botanik-Atlas (3x3 Zellen)...", flush=True)
    col = np.zeros((BOT_H, BOT_W, 3), dtype=np.float32)
    alp = np.zeros((BOT_H, BOT_W), dtype=np.float32)
    hgt = np.zeros((BOT_H, BOT_W), dtype=np.float32)
    rng = np.random.default_rng(2026)

    def cell_box(cname):
        c, r = BOTANY_CELLS[cname]
        cw = BOT_W / 3.0
        ch = BOT_H / 3.0
        return c * cw, r * ch, cw, ch

    # 1) IVY (0,0): Cascading ivy vine with glossy heart/pointed leaves
    x0, y0, cw, ch = cell_box("ivy")
    cx = x0 + cw * 0.5
    pts = [(cx + math.sin(i * 0.7) * 24, y0 + 22 + i * (ch - 44) / 7.0) for i in range(8)]
    for i in range(len(pts) - 1):
        _draw_stem(col, alp, hgt, pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], 4.2, (0.14, 0.22, 0.08))
    for i in range(18):
        t = (i + 0.5) / 18.0
        px = cx + math.sin(t * 5.0) * 28 + rng.uniform(-18, 18)
        py = y0 + 30 + t * (ch - 60)
        ang = (0.45 if i % 2 == 0 else math.pi - 0.45) + rng.uniform(-0.45, 0.45)
        L = rng.uniform(52, 78)
        W = L * rng.uniform(0.46, 0.62)
        _draw_leaf(col, alp, hgt, px, py, L, W, ang, (0.09, 0.24, 0.08), (0.19, 0.40, 0.13))

    # 2) POMEGRANATE (1,0): Olive-emerald lance leaves + bright ruby-red pomegranates
    x0, y0, cw, ch = cell_box("pomegranate")
    cx, cy = x0 + cw * 0.5, y0 + 30
    _draw_stem(col, alp, hgt, cx, cy, cx, y0 + ch - 42, 4.5, (0.26, 0.17, 0.10))
    for side in (-1, 1):
        _draw_stem(col, alp, hgt, cx, y0 + ch * 0.35, cx + side * 78, y0 + ch * 0.65, 3.2, (0.26, 0.17, 0.10))
        _draw_stem(col, alp, hgt, cx, y0 + ch * 0.58, cx + side * 62, y0 + ch * 0.84, 2.8, (0.26, 0.17, 0.10))
    for i in range(28):
        t = rng.uniform(0.15, 0.92)
        bx = cx + rng.uniform(-76, 76)
        by = y0 + t * (ch - 50) + 20
        ang = math.atan2(by - (y0 + ch * 0.3), bx - cx) + rng.uniform(-0.5, 0.5)
        _draw_leaf(col, alp, hgt, bx, by, rng.uniform(44, 68), rng.uniform(15, 22), ang, (0.14, 0.31, 0.10), (0.26, 0.46, 0.16))
    for fx, fy, fr in [(cx - 42, y0 + ch * 0.56, 22), (cx + 46, y0 + ch * 0.48, 24), (cx + 8, y0 + ch * 0.74, 20)]:
        _draw_fruit_or_center(col, alp, hgt, fx, fy, fr, (0.58, 0.09, 0.07), (0.78, 0.24, 0.14))

    # 3) CYPRESS (2,0): Dense upright Mediterranean cypress needle plumes
    x0, y0, cw, ch = cell_box("cypress")
    cx = x0 + cw * 0.5
    _draw_stem(col, alp, hgt, cx, y0 + 18, cx, y0 + ch - 30, 5.0, (0.20, 0.14, 0.09))
    for i in range(44):
        t = i / 43.0
        spread = (1.0 - 0.65 * t) * 76.0
        px = cx + rng.uniform(-spread, spread)
        py = y0 + 26 + t * (ch - 64)
        ang = math.pi * 0.5 + rng.uniform(-0.45, 0.45)
        _draw_leaf(col, alp, hgt, px, py, rng.uniform(42, 68), rng.uniform(14, 22), ang, (0.07, 0.18, 0.10), (0.15, 0.31, 0.17))

    # 4) OLEANDER (0,1): Narrow deep-green leaves + vibrant rose-pink blossoms
    x0, y0, cw, ch = cell_box("oleander")
    cx = x0 + cw * 0.5
    for i in range(26):
        ang = math.pi * 0.5 + rng.uniform(-1.15, 1.15)
        bx = cx + rng.uniform(-42, 42)
        by = y0 + 48 + rng.uniform(0, ch * 0.48)
        _draw_leaf(col, alp, hgt, bx, by, rng.uniform(70, 108), rng.uniform(13, 19), ang, (0.10, 0.26, 0.11), (0.18, 0.38, 0.16))
    for bx, by in [(cx - 52, y0 + ch * 0.68), (cx + 48, y0 + ch * 0.64), (cx, y0 + ch * 0.78), (cx - 18, y0 + ch * 0.54)]:
        for p in range(5):
            pa = p * (2.0 * math.pi / 5.0) + 0.2
            _draw_leaf(col, alp, hgt, bx, by, 30, 14, pa, (0.72, 0.24, 0.36), (0.80, 0.46, 0.54), vein_str=0.06)
        _draw_fruit_or_center(col, alp, hgt, bx, by, 7, (0.74, 0.56, 0.16), (0.82, 0.72, 0.32))

    # 5) FIG / HERB CLUSTER (1,1): Broad warm Mediterranean fig & myrtle leaves
    x0, y0, cw, ch = cell_box("fig")
    cx, cy = x0 + cw * 0.5, y0 + ch * 0.48
    for i in range(18):
        ang = rng.uniform(0, 2.0 * math.pi)
        r = rng.uniform(12, 65)
        px, py = cx + math.cos(ang) * r, cy + math.sin(ang) * r
        _draw_leaf(col, alp, hgt, px, py, rng.uniform(62, 92), rng.uniform(34, 48), ang, (0.13, 0.29, 0.09), (0.28, 0.46, 0.15))

    # 6) PAPYRUS / CYPERUS (2,1): Tall green stalks + radiating feathery umbels
    x0, y0, cw, ch = cell_box("papyrus")
    for sx, top_y in [(x0 + cw * 0.30, y0 + ch * 0.78), (x0 + cw * 0.52, y0 + ch * 0.86), (x0 + cw * 0.72, y0 + ch * 0.74)]:
        _draw_stem(col, alp, hgt, x0 + cw * 0.50, y0 + 14, sx, top_y, 5.2, (0.16, 0.34, 0.12))
        for k in range(14):
            a = -0.35 + k * (math.pi + 0.70) / 13.0
            _draw_leaf(col, alp, hgt, sx, top_y, rng.uniform(44, 62), 5.5, a, (0.18, 0.38, 0.12), (0.38, 0.52, 0.18), vein_str=0.05)

    # 7) WATER LILY PAD (0,2): Round notched deep emerald lily pad
    x0, y0, cw, ch = cell_box("lilypad")
    _draw_leaf(col, alp, hgt, x0 + cw * 0.5, y0 + ch * 0.5, cw * 0.42, cw * 0.42, 0.35, (0.09, 0.27, 0.11), (0.18, 0.39, 0.14), vein_str=0.16, notch=True)

    # 8) PINK SACRED LOTUS (1,2): Multi-layered pink-to-cream lotus blossom
    x0, y0, cw, ch = cell_box("lotus_pink")
    cx, cy = x0 + cw * 0.5, y0 + ch * 0.5
    for layer, (n_p, L, W, c_in, c_out) in enumerate([
        (10, 128, 42, (0.68, 0.26, 0.38), (0.80, 0.52, 0.60)),
        (8,  96,  34, (0.74, 0.34, 0.46), (0.82, 0.64, 0.70)),
        (6,  64,  24, (0.78, 0.48, 0.56), (0.82, 0.74, 0.76)),
    ]):
        for p in range(n_p):
            a = p * (2.0 * math.pi / n_p) + layer * 0.32
            _draw_leaf(col, alp, hgt, cx, cy, L, W, a, c_in, c_out, vein_str=0.08)
    _draw_fruit_or_center(col, alp, hgt, cx, cy, 24, (0.76, 0.58, 0.14), (0.82, 0.74, 0.30))

    # 9) WHITE SACRED LOTUS (2,2): Multi-layered creamy-white lotus blossom
    x0, y0, cw, ch = cell_box("lotus_white")
    cx, cy = x0 + cw * 0.5, y0 + ch * 0.5
    for layer, (n_p, L, W, c_in, c_out) in enumerate([
        (10, 128, 42, (0.68, 0.65, 0.54), (0.80, 0.78, 0.72)),
        (8,  96,  34, (0.74, 0.72, 0.62), (0.82, 0.81, 0.76)),
        (6,  64,  24, (0.78, 0.76, 0.66), (0.82, 0.82, 0.78)),
    ]):
        for p in range(n_p):
            a = p * (2.0 * math.pi / n_p) + layer * 0.32
            _draw_leaf(col, alp, hgt, cx, cy, L, W, a, c_in, c_out, vein_str=0.08)
    _draw_fruit_or_center(col, alp, hgt, cx, cy, 24, (0.76, 0.58, 0.14), (0.82, 0.74, 0.30))

    # Dilate RGB color into transparent margin to avoid dark mipmap fringes!
    rgb_pad = col.copy()
    mask = alp > 0.05
    for _ in range(8):
        for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            sh_m = np.roll(np.roll(mask, dy, axis=0), dx, axis=1)
            sh_c = np.roll(np.roll(rgb_pad, dy, axis=0), dx, axis=1)
            fill = (~mask) & sh_m
            rgb_pad[fill] = sh_c[fill]
            mask = mask | fill

    # Normal map from height gradient (Sobel-like)
    gx = np.roll(hgt, -1, axis=1) - np.roll(hgt, 1, axis=1)
    gy = np.roll(hgt, -1, axis=0) - np.roll(hgt, 1, axis=0)
    strength = 2.4
    nx = -gx * strength
    ny = -gy * strength
    nz = np.ones_like(hgt)
    inv_l = 1.0 / np.sqrt(nx * nx + ny * ny + nz * nz)
    nrm = np.ones((BOT_H, BOT_W, 4), dtype=np.float32)
    nrm[:, :, 0] = nx * inv_l * 0.5 + 0.5
    nrm[:, :, 1] = ny * inv_l * 0.5 + 0.5
    nrm[:, :, 2] = nz * inv_l * 0.5 + 0.5

    # ORM (R=AO, G=Roughness 0.42..0.62 for waxy foliage, B=0)
    orm = np.ones((BOT_H, BOT_W, 4), dtype=np.float32)
    orm[:, :, 0] = np.clip(0.74 + 0.26 * hgt, 0.70, 1.0)
    orm[:, :, 1] = np.clip(0.58 - 0.14 * hgt, 0.38, 0.65)
    orm[:, :, 2] = 0.0

    # Thickness (SSS)
    thk = np.ones((BOT_H, BOT_W, 4), dtype=np.float32)
    t_val = np.clip(0.85 - 0.45 * hgt, 0.25, 0.90)
    thk[:, :, 0] = t_val
    thk[:, :, 1] = t_val
    thk[:, :, 2] = t_val

    tex_dir = os.path.join(project_root, "assets", "textures")
    os.makedirs(tex_dir, exist_ok=True)

    rgba = np.zeros((BOT_H, BOT_W, 4), dtype=np.float32)
    rgba[:, :, :3] = _linear_to_srgb(np.clip(rgb_pad, 0.04, 0.82))
    rgba[:, :, 3] = np.clip(alp, 0.0, 1.0)
    print(f"[TEMENOS ATLAS] Botany stats: alpha_cov={(alp > 0.35).mean()*100:.1f}%, rgb_mean={rgba[:,:,:3].mean():.3f}", flush=True)

    save_np_png(rgba,           os.path.join(tex_dir, "temenos_botany_atlas_baseColor.png"), is_srgb=True,  has_alpha=True)
    save_np_png(nrm[:, :, :3],  os.path.join(tex_dir, "temenos_botany_atlas_normal.png"),    is_srgb=False, has_alpha=False)
    save_np_png(orm[:, :, :3],  os.path.join(tex_dir, "temenos_botany_atlas_orm.png"),       is_srgb=False, has_alpha=False)
    save_np_png(thk[:, :, :3],  os.path.join(tex_dir, "temenos_botany_atlas_thickness.png"), is_srgb=False, has_alpha=False)
    print(f"[TEMENOS ATLAS] 1024x1024 Tempel-Botanik-Atlas fertig ({time.time() - t0:.1f}s)!", flush=True)


def main():
    root = get_project_root()
    build_temenos_trim_sheet(root)
    build_temenos_botany_atlas(root)
    print("[TEMENOS ATLAS] ALLES ERFOLGREICH GEBACKEN!", flush=True)


if __name__ == "__main__":
    main()
