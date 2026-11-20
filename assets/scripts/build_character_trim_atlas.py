"""
build_character_trim_atlas.py — Feines 2048x1024 HDR-Charakter-Trim-Sheet v2 (CC0-Stoff-Scans + MPFB)
=====================================================================================================
Erzeugt und backt genau 1 gemeinsames 2048x1024-Trim-Sheet (Cycles CUDA GTX 1070
mit CPU-Fallback, HDR-Albedo strikt [0.06..0.76], 0 eingebackene Schlagschatten):
  - assets/textures/character_trim_atlas_baseColor.png  [sRGB]
  - assets/textures/character_trim_atlas_normal.png     [Linear / Non-Color]
  - assets/textures/character_trim_atlas_orm.png        [Linear: R=AO, G=Roughness, B=Metallic]
  - assets/textures/character_trim_atlas_thickness.png  [Linear: Thickness-SSS fuer Haut/Ohren/Haende/Leinen]

v2 Qualitaets-Upgrades:
  - Echte CC0 ambientCG Stoff- & Leder-Scans (Fabric001, Fabric019, Fabric030, Leather014)
    fuer feine Leinen- & grobe Woll-Webung (subtile Faden-Normalmap, Roughness 0.78..0.92).
  - KEINE modernen Streifen-T-Shirts! Authentische Fruehbronzezeit-Palette (Ur-Schinar):
    ungebleichtes Naturleinen (warmes Creme/Elfenbein), Ocker, Krapp-Terrakotta, Walnuss-Umbra,
    gedaempftes Waid-Indigo, Kaunakes-Wollfransen & sparsame sumerische Saumborten.
  - 3 lebendige Gen-10-Hauttoene (Semitisch, Hamitisch, Jafetitisch) mit Poren/Wangen-Nuance
    (Roughness 0.42..0.58) & hochglanz-Augen-Panel (Roughness ~0.08).
  - Kontrastreiche straehnige Haar-/Bart-Texturen (Grau-Weiss, Schwarz, Dunkelbraun, Mittelbraun).

Aufruf:
  blender --background --python assets/scripts/build_character_trim_atlas.py
"""

import os
import time
import bpy
import numpy as np


TEX_W = 2048
TEX_H = 1024

# Gemeinsame UV-Regionen (u0, v0, u1, v1) mit Sicherheitsrand gegen Mipmap-Bleed
# (100% kompatibel mit bestehender Pipeline & allen bestehenden Material-Keys!)
TRIM_REGIONS = {
    # Band 0 (V 0.00..0.33): 3 Phaenotyp-Hauttoene, 4 Haar-Bereiche & 1 Hochglanz-Auge
    "skin_semitic":       (0.006, 0.008, 0.174, 0.322),
    "skin_hamitic":       (0.186, 0.008, 0.354, 0.322),
    "skin_japhetic":      (0.366, 0.008, 0.534, 0.322),
    "hair_dark_wavy":     (0.546, 0.008, 0.634, 0.322),
    "hair_curly_dark":    (0.646, 0.008, 0.734, 0.322),
    "hair_brown_wavy":    (0.746, 0.008, 0.834, 0.322),
    "hair_grey":          (0.846, 0.008, 0.914, 0.322),
    "eye_iris":           (0.926, 0.008, 0.994, 0.322),
    # Band 1 (V 0.34..0.67): Echte CC0-Leinen- & Wollgewaender, Priester-Leinen & Kaunakes
    "linen_unbleached":   (0.006, 0.348, 0.194, 0.662),
    "priest_white_lapis": (0.206, 0.348, 0.394, 0.662),
    "kaunakes_fringe":    (0.406, 0.348, 0.594, 0.662),
    "wool_ochre":         (0.606, 0.348, 0.734, 0.662),
    "wool_indigo":        (0.746, 0.348, 0.864, 0.662),
    "wool_brown":         (0.876, 0.348, 0.994, 0.662),
    # Band 2 (V 0.68..1.00): Krapp-Terrakotta+Saumborte, CC0-Leder, Zeder, Bronze, Terrakotta, Korb
    "sumerian_border":    (0.006, 0.688, 0.234, 0.992),
    "leather_worn":       (0.246, 0.688, 0.414, 0.992),
    "cedar_wood":         (0.426, 0.688, 0.574, 0.992),
    "tin_bronze":         (0.586, 0.688, 0.714, 0.992),
    "terracotta":         (0.726, 0.688, 0.854, 0.992),
    "jute_basket":        (0.866, 0.688, 0.994, 0.992),
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
        scene.cycles.use_adaptive_sampling = False
        scene.cycles.use_denoising = False
    return "CUDA (GPU)" if used_gpu else "CPU"


def load_cc0_packs(project_root):
    """Laedt die lokalen ambientCG CC0 .packed.blend-Texturen (Color, NormalGL, Roughness)
    aus assets/textures/cc0/ in ein Dictionary {pack_key: {color, normal, roughness}}.
    """
    cc0_dir = os.path.join(project_root, "assets", "textures", "cc0")
    packs = {}
    targets = {
        "linen":   "Fabric001_1K-JPG.packed.blend",
        "wool_fine": "Fabric030_1K-JPG.packed.blend",
        "wool_coarse": "Fabric019_1K-JPG.packed.blend",
        "leather": "Leather014_1K-JPG.packed.blend",
    }
    for key, fname in targets.items():
        fpath = os.path.join(cc0_dir, fname)
        if not os.path.exists(fpath):
            print(f"[CHAR ATLAS] Hinweis: CC0-Pack fehlt ({fpath}), nutze prozeduralen Fallback.", flush=True)
            continue
        with bpy.data.libraries.load(os.path.abspath(fpath), link=False) as (df, dt):
            wanted = [
                im for im in df.images
                if any(tok in im for tok in ("_Color.", "_NormalGL.", "_Roughness."))
                and not im.endswith(".002")
            ]
            dt.images = wanted
        pack_imgs = {}
        for im in dt.images:
            if im is None:
                continue
            nm = im.name
            if "_Color." in nm and "color" not in pack_imgs:
                im.colorspace_settings.name = "sRGB"
                pack_imgs["color"] = im
            elif "_NormalGL." in nm and "normal" not in pack_imgs:
                im.colorspace_settings.name = "Non-Color"
                pack_imgs["normal"] = im
            elif "_Roughness." in nm and "roughness" not in pack_imgs:
                im.colorspace_settings.name = "Non-Color"
                pack_imgs["roughness"] = im
        if pack_imgs:
            packs[key] = pack_imgs
            print(f"[CHAR ATLAS] CC0-Scan geladen ({key}): {[k for k in pack_imgs.keys()]}", flush=True)
    return packs


def _add_noise(nodes, links, vec_out, scale, detail=6.0, roughness=0.55, distortion=0.0):
    n = nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = roughness
    n.inputs["Distortion"].default_value = distortion
    links.new(vec_out, n.inputs["Vector"])
    return n


def _add_wave(nodes, links, vec_out, wave_type="BANDS", bands_dir="X", scale=18.0, distortion=1.5, detail=2.0):
    w = nodes.new("ShaderNodeTexWave")
    w.wave_type = wave_type
    w.bands_direction = bands_dir
    w.inputs["Scale"].default_value = scale
    w.inputs["Distortion"].default_value = distortion
    w.inputs["Detail"].default_value = detail
    links.new(vec_out, w.inputs["Vector"])
    return w


def _mix_color(nodes, links, fac_out, col_a, col_b):
    m = nodes.new("ShaderNodeMix")
    m.data_type = "RGBA"
    m.clamp_factor = True
    if fac_out is not None:
        links.new(fac_out, m.inputs["Factor"])
    if isinstance(col_a, tuple):
        m.inputs["A"].default_value = (*col_a, 1.0)
    else:
        links.new(col_a, m.inputs["A"])
    if isinstance(col_b, tuple):
        m.inputs["B"].default_value = (*col_b, 1.0)
    else:
        links.new(col_b, m.inputs["B"])
    return m.outputs["Result"]


def _mix_float(nodes, links, fac_out, a, b):
    m = nodes.new("ShaderNodeMix")
    m.data_type = "FLOAT"
    m.clamp_factor = True
    if fac_out is not None:
        links.new(fac_out, m.inputs["Factor"])
    if isinstance(a, (int, float)):
        m.inputs["A"].default_value = float(a)
    else:
        links.new(a, m.inputs["A"])
    if isinstance(b, (int, float)):
        m.inputs["B"].default_value = float(b)
    else:
        links.new(b, m.inputs["B"])
    return m.outputs["Result"]


def _math(nodes, links, op, a, b=None):
    m = nodes.new("ShaderNodeMath")
    m.operation = op
    if isinstance(a, (int, float)):
        m.inputs[0].default_value = float(a)
    else:
        links.new(a, m.inputs[0])
    if b is not None:
        if isinstance(b, (int, float)):
            m.inputs[1].default_value = float(b)
        else:
            links.new(b, m.inputs[1])
    return m.outputs["Value"]


def _sample_cc0_fabric(nodes, links, uv, pack, tile_xy=(5.0, 5.0), tint_dark=(0.55, 0.49, 0.40),
                       tint_light=(0.70, 0.64, 0.54), rgh_lo=0.80, rgh_hi=0.92, norm_strength=0.38):
    """Nutzt echte ambientCG CC0 Stoff-Scans (Color-Luminanz fuer authentisches Webmuster,
    NormalGL fuer echte Faden-Normalmap, Roughness fuer realistischen Stoffglanz).
    """
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (tile_xy[0], tile_xy[1], 1.0)
    links.new(uv, mapping.inputs["Vector"])
    uv_t = mapping.outputs["Vector"]

    # Sanfte organische Makro-Faerbung (handgefaerbte Bronzezeit-Wolle/Leinen)
    n_slub = _add_noise(nodes, links, uv, scale=9.0, detail=4.0, roughness=0.55)
    base_col = _mix_color(nodes, links, n_slub.outputs["Fac"], tint_dark, tint_light)

    if pack and "color" in pack:
        tc = nodes.new("ShaderNodeTexImage")
        tc.image = pack["color"]
        tc.extension = "REPEAT"
        links.new(uv_t, tc.inputs["Vector"])
        # Luminanz des echten Stoff-Scans extrahieren und als feine Web-Modulation einmischen
        bw = nodes.new("ShaderNodeRGBToBW")
        links.new(tc.outputs["Color"], bw.inputs["Color"])
        # Kontrast sanft um 0.5 zentrieren -> subtile Fadenstruktur ohne Flecken
        mr = nodes.new("ShaderNodeMapRange")
        mr.clamp = True
        mr.inputs["From Min"].default_value = 0.25
        mr.inputs["From Max"].default_value = 0.85
        mr.inputs["To Min"].default_value = 0.0
        mr.inputs["To Max"].default_value = 1.0
        links.new(bw.outputs["Val"], mr.inputs["Value"])
        dark_thread = (tint_dark[0] * 0.82, tint_dark[1] * 0.82, tint_dark[2] * 0.82)
        col = _mix_color(nodes, links, _math(nodes, links, "MULTIPLY", _math(nodes, links, "SUBTRACT", 1.0, mr.outputs["Result"]), 0.28),
                         base_col, dark_thread)
    else:
        col = base_col

    if pack and "roughness" in pack:
        tr = nodes.new("ShaderNodeTexImage")
        tr.image = pack["roughness"]
        tr.extension = "REPEAT"
        links.new(uv_t, tr.inputs["Vector"])
        mr_r = nodes.new("ShaderNodeMapRange")
        mr_r.clamp = True
        mr_r.inputs["From Min"].default_value = 0.0
        mr_r.inputs["From Max"].default_value = 1.0
        mr_r.inputs["To Min"].default_value = rgh_lo
        mr_r.inputs["To Max"].default_value = rgh_hi
        links.new(tr.outputs["Color"], mr_r.inputs["Value"])
        rough = mr_r.outputs["Result"]
    else:
        rough = _mix_float(nodes, links, n_slub.outputs["Fac"], rgh_lo, rgh_hi)

    norm_out = None
    if pack and "normal" in pack:
        tn = nodes.new("ShaderNodeTexImage")
        tn.image = pack["normal"]
        tn.extension = "REPEAT"
        links.new(uv_t, tn.inputs["Vector"])
        nmap = nodes.new("ShaderNodeNormalMap")
        nmap.inputs["Strength"].default_value = norm_strength
        links.new(tn.outputs["Color"], nmap.inputs["Color"])
        norm_out = nmap.outputs["Normal"]

    return col, rough, norm_out


def build_strip_material(name, kind, cc0_packs):
    """Erzeugt PBR-Material mit HDR-Albedo [0.06..0.76], CC0-Normal, Roughness, Metallic & SSS-Thickness."""
    mat = bpy.data.materials.new(name=f"MatChar_{name}")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tex_coord = nodes.new("ShaderNodeTexCoord")
    uv = tex_coord.outputs["UV"]
    sep = nodes.new("ShaderNodeSeparateXYZ")
    links.new(uv, sep.inputs["Vector"])

    metallic_val = 0.0
    bump_h = None
    bump_strength = 0.08
    bump_dist = 0.0020
    direct_normal = None
    ao_val = 0.96
    thickness_val = 0.08

    if kind in ("skin_semitic", "skin_hamitic", "skin_japhetic"):
        # Natuerliche Gen-10-Haut: feine Poren, sanfte Durchblutung, Roughness 0.42..0.58
        n_macro = _add_noise(nodes, links, uv, scale=6.5, detail=4.0, roughness=0.50)
        n_blush = _add_noise(nodes, links, uv, scale=13.0, detail=3.0, roughness=0.48)
        n_pores = _add_noise(nodes, links, uv, scale=180.0, detail=7.0, roughness=0.58)
        blush_fac = _math(nodes, links, "MULTIPLY", n_blush.outputs["Fac"], 0.14)
        if kind == "skin_semitic":
            # Semitisch / Vorderorientalisch: warmer oliv-bronzefarbener Ton
            col = _mix_color(nodes, links, n_macro.outputs["Fac"], (0.37, 0.22, 0.135), (0.49, 0.31, 0.195))
            col = _mix_color(nodes, links, blush_fac, col, (0.47, 0.24, 0.155))
            col = _mix_color(nodes, links, _math(nodes, links, "MULTIPLY", n_pores.outputs["Fac"], 0.07), col, (0.31, 0.18, 0.11))
            rough = _mix_float(nodes, links, n_pores.outputs["Fac"], 0.45, 0.56)
            thickness_val = 0.84
        elif kind == "skin_hamitic":
            # Hamitisch / Nordostafrikanisch: warmer tiefer Dunkelbraun-Ton (kein Graustich!)
            col = _mix_color(nodes, links, n_macro.outputs["Fac"], (0.125, 0.074, 0.048), (0.205, 0.118, 0.074))
            col = _mix_color(nodes, links, blush_fac, col, (0.22, 0.112, 0.068))
            col = _mix_color(nodes, links, _math(nodes, links, "MULTIPLY", n_pores.outputs["Fac"], 0.06), col, (0.10, 0.060, 0.042))
            rough = _mix_float(nodes, links, n_pores.outputs["Fac"], 0.42, 0.54)
            thickness_val = 0.66
        else:  # skin_japhetic
            # Jafetitisch / Anatolisch-Europaeisch: warm sonnengebraeunt (kein bleiches Plastik!)
            col = _mix_color(nodes, links, n_macro.outputs["Fac"], (0.54, 0.36, 0.255), (0.67, 0.47, 0.345))
            col = _mix_color(nodes, links, blush_fac, col, (0.65, 0.39, 0.285))
            col = _mix_color(nodes, links, _math(nodes, links, "MULTIPLY", n_pores.outputs["Fac"], 0.06), col, (0.47, 0.30, 0.21))
            rough = _mix_float(nodes, links, n_pores.outputs["Fac"], 0.46, 0.58)
            thickness_val = 0.90
        bump_h = _math(nodes, links, "MULTIPLY", n_pores.outputs["Fac"], 0.20)
        bump_strength = 0.045
        bump_dist = 0.0012
        ao_val = 0.96

    elif kind == "eye_iris":
        # Hochglanz-Auge v2.4 (Roughness ~0.05): weich geglaettete Uebergaenge (kein Treppen-Aliasing!),
        # klare lebendige Iris mit dunklem Limbus, tiefer Pupille & sanftem unteren Lichtreflex!
        dx = _math(nodes, links, "SUBTRACT", sep.outputs["X"], 0.5)
        dy = _math(nodes, links, "SUBTRACT", sep.outputs["Y"], 0.5)
        r2 = _math(nodes, links, "ADD", _math(nodes, links, "MULTIPLY", dx, dx), _math(nodes, links, "MULTIPLY", dy, dy))
        r = _math(nodes, links, "SQRT", r2)
        n_iris = _add_noise(nodes, links, uv, scale=36.0, detail=6.0, roughness=0.58)

        # Sanfte Sclera (warmes Elfenbein-Weiss, am aeussersten Rand leicht schattiert fuer 3D-Tiefe)
        col_sclera_mid = (0.74, 0.72, 0.69)
        col_sclera_edge = (0.56, 0.51, 0.48)
        mr_scl = nodes.new("ShaderNodeMapRange")
        mr_scl.interpolation_type = "SMOOTHSTEP"
        mr_scl.clamp = True
        mr_scl.inputs["From Min"].default_value = 0.42
        mr_scl.inputs["From Max"].default_value = 0.62
        links.new(r, mr_scl.inputs["Value"])
        col_sclera = _mix_color(nodes, links, mr_scl.outputs["Result"], col_sclera_mid, col_sclera_edge)

        # Lebendige dunkelbraun-bernsteinfarbene Iris (unten leicht aufgehellt wie echtes Licht im Auge)
        col_iris_dark = (0.14, 0.082, 0.046)
        col_iris_warm = (0.34, 0.20, 0.105)
        col_iris = _mix_color(nodes, links, n_iris.outputs["Fac"], col_iris_dark, col_iris_warm)
        col_limbus = (0.055, 0.038, 0.028)
        col_pupil = (0.030, 0.030, 0.032)

        def smooth_mask(val_out, edge_lo, edge_hi):
            mr = nodes.new("ShaderNodeMapRange")
            mr.interpolation_type = "SMOOTHSTEP"
            mr.clamp = True
            mr.inputs["From Min"].default_value = edge_lo
            mr.inputs["From Max"].default_value = edge_hi
            mr.inputs["To Min"].default_value = 1.0
            mr.inputs["To Max"].default_value = 0.0
            links.new(val_out, mr.inputs["Value"])
            return mr.outputs["Result"]

        m_limbus = smooth_mask(r, 0.37, 0.415)
        m_iris   = smooth_mask(r, 0.32, 0.365)
        m_pupil  = smooth_mask(r, 0.155, 0.185)

        col = _mix_color(nodes, links, m_limbus, col_sclera, col_limbus)
        col = _mix_color(nodes, links, m_iris, col, col_iris)
        col = _mix_color(nodes, links, m_pupil, col, col_pupil)

        # Hochglanz-Hornhaut (Roughness 0.05 -> klares natuerliches Spitzlicht!)
        rough = _mix_float(nodes, links, m_limbus, 0.09, 0.05)
        bump_h = _math(nodes, links, "MULTIPLY", n_iris.outputs["Fac"], 0.015)
        bump_strength = 0.008
        bump_dist = 0.0004
        thickness_val = 0.15
        ao_val = 0.99

    elif kind in ("hair_dark_wavy", "hair_curly_dark", "hair_brown_wavy", "hair_grey"):
        # Kontrastreiche gestraehnte Haar-/Bart-Textur (kein glatter Knet-Look!)
        mapping = nodes.new("ShaderNodeMapping")
        if kind == "hair_curly_dark":
            mapping.inputs["Scale"].default_value = (18.0, 18.0, 1.0)
            links.new(uv, mapping.inputs["Vector"])
            n_strand = _add_noise(nodes, links, mapping.outputs["Vector"], scale=16.0, detail=10.0, roughness=0.72, distortion=1.4)
            col = _mix_color(nodes, links, n_strand.outputs["Fac"], (0.060, 0.048, 0.042), (0.135, 0.102, 0.082))
            rough = _mix_float(nodes, links, n_strand.outputs["Fac"], 0.52, 0.72)
            bump_strength = 0.32
        else:
            mapping.inputs["Scale"].default_value = (36.0, 2.2, 1.0)
            links.new(uv, mapping.inputs["Vector"])
            n_strand = _add_noise(nodes, links, mapping.outputs["Vector"], scale=12.0, detail=9.0, roughness=0.65, distortion=0.45)
            w_locks = _add_wave(nodes, links, mapping.outputs["Vector"], "BANDS", "X", scale=5.0, distortion=2.2, detail=3.0)
            strand_mix = _math(nodes, links, "ADD",
                               _math(nodes, links, "MULTIPLY", n_strand.outputs["Fac"], 0.65),
                               _math(nodes, links, "MULTIPLY", w_locks.outputs["Fac"], 0.35))
            if kind == "hair_dark_wavy":
                col = _mix_color(nodes, links, strand_mix, (0.062, 0.046, 0.036), (0.165, 0.118, 0.086))
                rough = _mix_float(nodes, links, strand_mix, 0.40, 0.58)
            elif kind == "hair_brown_wavy":
                col = _mix_color(nodes, links, strand_mix, (0.17, 0.105, 0.062), (0.37, 0.245, 0.145))
                rough = _mix_float(nodes, links, strand_mix, 0.42, 0.60)
            else:  # hair_grey
                col = _mix_color(nodes, links, strand_mix, (0.22, 0.21, 0.195), (0.62, 0.60, 0.55))
                rough = _mix_float(nodes, links, strand_mix, 0.44, 0.62)
            n_strand_h = strand_mix
            bump_strength = 0.28
        bump_h = n_strand.outputs["Fac"] if kind == "hair_curly_dark" else n_strand_h
        bump_dist = 0.0028
        thickness_val = 0.12
        ao_val = 0.90

    elif kind == "linen_unbleached":
        # Ungebleichtes Naturleinen (warmes Creme/Elfenbein, CC0 Fabric001)
        col, rough, direct_normal = _sample_cc0_fabric(
            nodes, links, uv, cc0_packs.get("linen"),
            tile_xy=(5.5, 5.5),
            tint_dark=(0.55, 0.49, 0.39), tint_light=(0.69, 0.63, 0.52),
            rgh_lo=0.80, rgh_hi=0.91, norm_strength=0.35
        )
        thickness_val = 0.28
        ao_val = 0.94

    elif kind == "priest_white_lapis":
        # Feines warm-elfenbeinfarbenes Priester-Leinen (CC0 Fabric001) + edle Lapislazuli-Saumborte (V < 0.16)
        col_linen, rough, direct_normal = _sample_cc0_fabric(
            nodes, links, uv, cc0_packs.get("linen"),
            tile_xy=(5.5, 5.5),
            tint_dark=(0.64, 0.60, 0.53), tint_light=(0.74, 0.70, 0.63),
            rgh_lo=0.79, rgh_hi=0.90, norm_strength=0.32
        )
        is_border = _math(nodes, links, "LESS_THAN", sep.outputs["Y"], 0.16)
        is_gold_lo = _math(nodes, links, "LESS_THAN", sep.outputs["Y"], 0.032)
        is_gold_hi = _math(nodes, links, "GREATER_THAN", sep.outputs["Y"], 0.132)
        is_gold_band = _math(nodes, links, "MAXIMUM", is_gold_lo, _math(nodes, links, "MULTIPLY", is_border, is_gold_hi))
        w_lapis = _add_wave(nodes, links, uv, "BANDS", "DIAGONAL", scale=26.0, distortion=0.0, detail=1.0)
        col_lapis = _mix_color(nodes, links, w_lapis.outputs["Fac"], (0.085, 0.155, 0.36), (0.135, 0.24, 0.49))
        col_b = _mix_color(nodes, links, is_gold_band, col_lapis, (0.56, 0.41, 0.18))
        col = _mix_color(nodes, links, is_border, col_linen, col_b)
        thickness_val = 0.30
        ao_val = 0.94

    elif kind == "kaunakes_fringe":
        # Sumerisches Zottengewand: grobe CC0-Schafwolle (Fabric019) + gestaffelte Wollfransen-Reihen
        col_w, rough, direct_normal = _sample_cc0_fabric(
            nodes, links, uv, cc0_packs.get("wool_coarse"),
            tile_xy=(4.5, 4.5),
            tint_dark=(0.46, 0.39, 0.28), tint_light=(0.62, 0.54, 0.41),
            rgh_lo=0.83, rgh_hi=0.92, norm_strength=0.45
        )
        mapping_k = nodes.new("ShaderNodeMapping")
        mapping_k.inputs["Scale"].default_value = (14.0, 3.0, 1.0)
        links.new(uv, mapping_k.inputs["Vector"])
        n_tuft = _add_noise(nodes, links, mapping_k.outputs["Vector"], scale=7.0, detail=5.0, roughness=0.60, distortion=0.35)
        w_tier = _add_wave(nodes, links, uv, "BANDS", "Y", scale=6.5, distortion=0.4, detail=2.0)
        tuft_h = _math(nodes, links, "MULTIPLY", _math(nodes, links, "ADD", w_tier.outputs["Fac"], 0.35), n_tuft.outputs["Fac"])
        col = _mix_color(nodes, links, _math(nodes, links, "MULTIPLY", tuft_h, 0.22), col_w, (0.34, 0.27, 0.19))
        thickness_val = 0.20
        ao_val = 0.92

    elif kind == "wool_ochre":
        # Warmer Natur-Ocker (CC0 Fabric030)
        col, rough, direct_normal = _sample_cc0_fabric(
            nodes, links, uv, cc0_packs.get("wool_fine"),
            tile_xy=(5.0, 5.0),
            tint_dark=(0.43, 0.265, 0.13), tint_light=(0.58, 0.385, 0.205),
            rgh_lo=0.81, rgh_hi=0.92, norm_strength=0.38
        )
        thickness_val = 0.18
        ao_val = 0.94

    elif kind == "wool_indigo":
        # Gedaempftes antikes Waid-Indigo / Schieferblau (CC0 Fabric030)
        col, rough, direct_normal = _sample_cc0_fabric(
            nodes, links, uv, cc0_packs.get("wool_fine"),
            tile_xy=(5.0, 5.0),
            tint_dark=(0.135, 0.18, 0.27), tint_light=(0.22, 0.285, 0.39),
            rgh_lo=0.81, rgh_hi=0.92, norm_strength=0.38
        )
        thickness_val = 0.16
        ao_val = 0.94

    elif kind == "wool_brown":
        # Walnuss- / Umbra-Braun (CC0 Fabric019 grobe Wolle)
        col, rough, direct_normal = _sample_cc0_fabric(
            nodes, links, uv, cc0_packs.get("wool_coarse"),
            tile_xy=(4.8, 4.8),
            tint_dark=(0.20, 0.138, 0.092), tint_light=(0.33, 0.23, 0.15),
            rgh_lo=0.83, rgh_hi=0.92, norm_strength=0.42
        )
        thickness_val = 0.15
        ao_val = 0.93

    elif kind == "sumerian_border":
        # v2 FIX: KEINE modernen rosa-blauen Poloshirt-Streifen!
        # Authentisches Krapp-Terrakotta-Wollgewebe (CC0 Fabric030) mit feiner gewebter
        # sumerischer Ocker-/Naturleinen-Saumborte NUR am unteren Rand (V < 0.18)!
        col_madder, rough, direct_normal = _sample_cc0_fabric(
            nodes, links, uv, cc0_packs.get("wool_fine"),
            tile_xy=(5.0, 5.0),
            tint_dark=(0.39, 0.175, 0.115), tint_light=(0.52, 0.245, 0.155),
            rgh_lo=0.80, rgh_hi=0.91, norm_strength=0.38
        )
        is_border = _math(nodes, links, "LESS_THAN", sep.outputs["Y"], 0.18)
        is_line_lo = _math(nodes, links, "LESS_THAN", sep.outputs["Y"], 0.035)
        is_line_hi = _math(nodes, links, "GREATER_THAN", sep.outputs["Y"], 0.145)
        is_trim = _math(nodes, links, "MAXIMUM", is_line_lo, _math(nodes, links, "MULTIPLY", is_border, is_line_hi))
        w_chev = _add_wave(nodes, links, uv, "BANDS", "DIAGONAL", scale=24.0, distortion=0.0, detail=1.0)
        col_geo = _mix_color(nodes, links, w_chev.outputs["Fac"], (0.24, 0.14, 0.085), (0.60, 0.47, 0.27))
        col_b = _mix_color(nodes, links, is_trim, col_geo, (0.64, 0.56, 0.42))
        col = _mix_color(nodes, links, is_border, col_madder, col_b)
        thickness_val = 0.18
        ao_val = 0.93

    elif kind == "leather_worn":
        # Geoeltes antikes Leder (CC0 Leather014) fuer Guertel, Schuerzen & Sandalenriemen
        col, rough, direct_normal = _sample_cc0_fabric(
            nodes, links, uv, cc0_packs.get("leather"),
            tile_xy=(3.5, 3.5),
            tint_dark=(0.155, 0.092, 0.052), tint_light=(0.295, 0.18, 0.10),
            rgh_lo=0.46, rgh_hi=0.66, norm_strength=0.55
        )
        thickness_val = 0.06
        ao_val = 0.92

    elif kind == "cedar_wood":
        mapping = nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (2.5, 16.0, 1.0)
        links.new(uv, mapping.inputs["Vector"])
        n_wood = _add_noise(nodes, links, mapping.outputs["Vector"], scale=8.0, detail=7.0, roughness=0.58, distortion=0.6)
        col = _mix_color(nodes, links, n_wood.outputs["Fac"], (0.24, 0.14, 0.08), (0.43, 0.275, 0.16))
        rough = _mix_float(nodes, links, n_wood.outputs["Fac"], 0.62, 0.78)
        bump_h = n_wood.outputs["Fac"]
        bump_strength = 0.16
        bump_dist = 0.002
        thickness_val = 0.04
        ao_val = 0.93

    elif kind == "tin_bronze":
        # Warm gehaemmerte Fruehbronzezeit-Zinnbronze (kein dunkler Spiegel-Effekt unter Studio-Himmel!)
        n_ham = _add_noise(nodes, links, uv, scale=28.0, detail=6.0, roughness=0.55)
        col = _mix_color(nodes, links, n_ham.outputs["Fac"], (0.56, 0.40, 0.21), (0.74, 0.56, 0.33))
        rough = _mix_float(nodes, links, n_ham.outputs["Fac"], 0.34, 0.46)
        metallic_val = 0.72
        bump_h = n_ham.outputs["Fac"]
        bump_strength = 0.10
        bump_dist = 0.0015
        thickness_val = 0.02
        ao_val = 0.96

    elif kind == "terracotta":
        n_clay = _add_noise(nodes, links, uv, scale=20.0, detail=7.0, roughness=0.62)
        w_wheel = _add_wave(nodes, links, uv, "BANDS", "Y", scale=32.0, distortion=0.4, detail=2.0)
        col = _mix_color(nodes, links, n_clay.outputs["Fac"], (0.42, 0.20, 0.12), (0.58, 0.31, 0.19))
        rough = _mix_float(nodes, links, n_clay.outputs["Fac"], 0.72, 0.86)
        bump_h = _math(nodes, links, "ADD", _math(nodes, links, "MULTIPLY", n_clay.outputs["Fac"], 0.65),
                       _math(nodes, links, "MULTIPLY", w_wheel.outputs["Fac"], 0.35))
        bump_strength = 0.11
        bump_dist = 0.0018
        thickness_val = 0.05
        ao_val = 0.93

    else:  # jute_basket
        n_reed = _add_noise(nodes, links, uv, scale=45.0, detail=6.0, roughness=0.6)
        w_x = _add_wave(nodes, links, uv, "BANDS", "X", scale=28.0, distortion=0.7, detail=2.0)
        w_y = _add_wave(nodes, links, uv, "BANDS", "Y", scale=28.0, distortion=0.7, detail=2.0)
        weave = _math(nodes, links, "MULTIPLY", _math(nodes, links, "ADD", w_x.outputs["Fac"], w_y.outputs["Fac"]), 0.5)
        col = _mix_color(nodes, links, weave, (0.37, 0.28, 0.17), (0.56, 0.44, 0.28))
        col = _mix_color(nodes, links, _math(nodes, links, "MULTIPLY", n_reed.outputs["Fac"], 0.20), col, (0.30, 0.22, 0.13))
        rough = _mix_float(nodes, links, weave, 0.84, 0.94)
        bump_h = weave
        bump_strength = 0.16
        bump_dist = 0.0022
        thickness_val = 0.10
        ao_val = 0.90

    links.new(col, bsdf.inputs["Base Color"])
    links.new(rough, bsdf.inputs["Roughness"])
    bsdf.inputs["Metallic"].default_value = metallic_val

    if direct_normal is not None:
        links.new(direct_normal, bsdf.inputs["Normal"])
    elif bump_h is not None:
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = bump_strength
        bump.inputs["Distance"].default_value = bump_dist
        links.new(bump_h, bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    mat["arche_ao"] = float(ao_val)
    mat["arche_thickness"] = float(thickness_val)
    return mat


def create_atlas_board(cc0_packs):
    """Erstellt ein flaches 2x1 m Atlas-Board mit 2 UV-Layern:
    - UVMap (aktiv fuer Bake-Ziel im Atlas-Raum 0..1)
    - UVLocal (0..1 pro Panel fuer Material-Shader wie eye_iris & Saumborten)
    """
    mesh = bpy.data.meshes.new("CharacterTrimBoard")
    obj = bpy.data.objects.new("CharacterTrimBoard", mesh)
    bpy.context.collection.objects.link(obj)

    verts = []
    faces = []
    uvs_atlas = []
    uvs_local = []
    mat_indices = []

    panel_boxes = {
        k: (max(0.0, u0 - 0.005), max(0.0, v0 - 0.007), min(1.0, u1 + 0.005), min(1.0, v1 + 0.007))
        for k, (u0, v0, u1, v1) in TRIM_REGIONS.items()
    }

    for idx, (key, (u0, v0, u1, v1)) in enumerate(panel_boxes.items()):
        mat = build_strip_material(key, key, cc0_packs)
        uv_node = mat.node_tree.nodes.new("ShaderNodeUVMap")
        uv_node.uv_map = "UVLocal"
        for node in mat.node_tree.nodes:
            if node.type == "TEX_COORD":
                for link in list(mat.node_tree.links):
                    if link.from_node == node and link.from_socket.name == "UV":
                        to_sock = link.to_socket
                        mat.node_tree.links.remove(link)
                        mat.node_tree.links.new(uv_node.outputs["UV"], to_sock)

        obj.data.materials.append(mat)
        base = len(verts)
        verts.extend([
            (u0 * 2.0, v0 * 1.0, 0.0),
            (u1 * 2.0, v0 * 1.0, 0.0),
            (u1 * 2.0, v1 * 1.0, 0.0),
            (u0 * 2.0, v1 * 1.0, 0.0),
        ])
        faces.append((base, base + 1, base + 2, base + 3))
        uvs_atlas.append([(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
        uvs_local.append([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)])
        mat_indices.append(idx)

    mesh.from_pydata(verts, [], faces)
    uv_atlas = mesh.uv_layers.new(name="UVMap")
    uv_local = mesh.uv_layers.new(name="UVLocal")
    uv_atlas.active = True
    uv_atlas.active_render = True
    for poly_i, poly in enumerate(mesh.polygons):
        poly.material_index = mat_indices[poly_i]
        for loop_off, loop_idx in enumerate(poly.loop_indices):
            uv_atlas.data[loop_idx].uv = uvs_atlas[poly_i][loop_off]
            uv_local.data[loop_idx].uv = uvs_local[poly_i][loop_off]
    mesh.update()
    return obj


def _attach_bake_target(obj, img):
    for mat in obj.data.materials:
        nodes = mat.node_tree.nodes
        tex = nodes.get("_BakeTarget")
        if tex is None:
            tex = nodes.new("ShaderNodeTexImage")
            tex.name = "_BakeTarget"
        tex.image = img
        for n in nodes:
            n.select = False
        tex.select = True
        nodes.active = tex


def _bake_pass(scene, obj, bake_type, img, pass_filter=None):
    _attach_bake_target(obj, img)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    scene.render.bake.margin = 4
    scene.render.bake.use_clear = True
    kwargs = {"type": bake_type}
    if pass_filter is not None:
        kwargs["pass_filter"] = pass_filter
    bpy.ops.object.bake(**kwargs)


def bake_character_atlas():
    t0 = time.time()
    root = get_project_root()
    tex_dir = os.path.join(root, "assets", "textures")
    os.makedirs(tex_dir, exist_ok=True)

    scene = clear_scene()
    dev = setup_cycles(scene, samples=4)
    print(f"[CHAR ATLAS v2] Starte 2048x1024 Bake auf {dev}...", flush=True)

    cc0_packs = load_cc0_packs(root)
    board = create_atlas_board(cc0_packs)

    # 1. BaseColor [sRGB] (HDR-Albedo strikt [0.06..0.76], 0 eingebackene Schlagschatten!)
    img_bc = bpy.data.images.new("char_bc", width=TEX_W, height=TEX_H, alpha=False, float_buffer=False)
    img_bc.colorspace_settings.name = "sRGB"
    _bake_pass(scene, board, "DIFFUSE", img_bc, pass_filter={"COLOR"})
    px = np.array(img_bc.pixels[:], dtype=np.float32).reshape((TEX_H, TEX_W, 4))
    px[:, :, :3] = np.clip(px[:, :, :3], 0.03, 0.76)
    img_bc.pixels.foreach_set(px.ravel())
    bc_path = os.path.join(tex_dir, "character_trim_atlas_baseColor.png")
    img_bc.filepath_raw = bc_path
    img_bc.file_format = "PNG"
    img_bc.save()
    print(f"[CHAR ATLAS v2] BaseColor gespeichert ({time.time() - t0:.2f}s): {bc_path}", flush=True)

    # 2. Normal [Linear / Non-Color]
    img_nrm = bpy.data.images.new("char_nrm", width=TEX_W, height=TEX_H, alpha=False, float_buffer=False)
    img_nrm.colorspace_settings.name = "Non-Color"
    _bake_pass(scene, board, "NORMAL", img_nrm)
    nrm_path = os.path.join(tex_dir, "character_trim_atlas_normal.png")
    img_nrm.filepath_raw = nrm_path
    img_nrm.file_format = "PNG"
    img_nrm.save()
    print(f"[CHAR ATLAS v2] Normal gespeichert ({time.time() - t0:.2f}s): {nrm_path}", flush=True)

    # 3. Roughness [Linear]
    img_rgh = bpy.data.images.new("char_rgh", width=TEX_W, height=TEX_H, alpha=False, float_buffer=False)
    img_rgh.colorspace_settings.name = "Non-Color"
    _bake_pass(scene, board, "ROUGHNESS", img_rgh)
    rgh_px = np.array(img_rgh.pixels[:], dtype=np.float32).reshape((TEX_H, TEX_W, 4))[:, :, 0]

    # 4. Metallic + AO + Thickness-SSS ueber schnelle Emission-Bakes
    def bake_scalar_channel(prop_name, default_val):
        saved_links = []
        for mat in board.data.materials:
            nt = mat.node_tree
            out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
            bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
            em = nt.nodes.new("ShaderNodeEmission")
            val = float(mat.get(prop_name, default_val))
            em.inputs["Color"].default_value = (val, val, val, 1.0)
            saved_links.append((nt, out, bsdf, em))
            nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
        img_tmp = bpy.data.images.new(f"char_{prop_name}", width=TEX_W, height=TEX_H, alpha=False, float_buffer=False)
        img_tmp.colorspace_settings.name = "Non-Color"
        _bake_pass(scene, board, "EMIT", img_tmp)
        arr = np.array(img_tmp.pixels[:], dtype=np.float32).reshape((TEX_H, TEX_W, 4))[:, :, 0]
        for nt, out, bsdf, em in saved_links:
            nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
            nt.nodes.remove(em)
        bpy.data.images.remove(img_tmp)
        return arr

    for mat in board.data.materials:
        bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        mat["arche_metallic"] = float(bsdf.inputs["Metallic"].default_value)

    ao_px = bake_scalar_channel("arche_ao", 0.92)
    met_px = bake_scalar_channel("arche_metallic", 0.0)
    sss_px = bake_scalar_channel("arche_thickness", 0.08)

    # ORM packen (R=AO, G=Roughness, B=Metallic)
    orm_arr = np.ones((TEX_H, TEX_W, 4), dtype=np.float32)
    orm_arr[:, :, 0] = np.clip(ao_px, 0.0, 1.0)
    orm_arr[:, :, 1] = np.clip(rgh_px, 0.04, 1.0)
    orm_arr[:, :, 2] = np.clip(met_px, 0.0, 1.0)
    img_orm = bpy.data.images.new("char_orm", width=TEX_W, height=TEX_H, alpha=False, float_buffer=False)
    img_orm.colorspace_settings.name = "Non-Color"
    img_orm.pixels.foreach_set(orm_arr.ravel())
    orm_path = os.path.join(tex_dir, "character_trim_atlas_orm.png")
    img_orm.filepath_raw = orm_path
    img_orm.file_format = "PNG"
    img_orm.save()
    print(f"[CHAR ATLAS v2] ORM gespeichert ({time.time() - t0:.2f}s): {orm_path}", flush=True)

    # Thickness-SSS speichern
    sss_arr = np.ones((TEX_H, TEX_W, 4), dtype=np.float32)
    sss_arr[:, :, 0] = np.clip(sss_px, 0.0, 1.0)
    sss_arr[:, :, 1] = np.clip(sss_px, 0.0, 1.0)
    sss_arr[:, :, 2] = np.clip(sss_px, 0.0, 1.0)
    img_sss = bpy.data.images.new("char_sss", width=TEX_W, height=TEX_H, alpha=False, float_buffer=False)
    img_sss.colorspace_settings.name = "Non-Color"
    img_sss.pixels.foreach_set(sss_arr.ravel())
    sss_path = os.path.join(tex_dir, "character_trim_atlas_thickness.png")
    img_sss.filepath_raw = sss_path
    img_sss.file_format = "PNG"
    img_sss.save()

    total_s = time.time() - t0
    print(f"[CHAR ATLAS v2] Thickness-SSS gespeichert ({total_s:.2f}s): {sss_path}", flush=True)
    print(f"[CHAR ATLAS v2] FERTIG in {total_s:.2f}s ({dev}).", flush=True)


if __name__ == "__main__":
    bake_character_atlas()
