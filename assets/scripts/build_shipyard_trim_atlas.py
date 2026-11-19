"""
build_shipyard_trim_atlas.py — Bronzezeitliches 2048x1024 HDR-Werft-, Handwerks- & Fluss-Trim-Sheet
======================================================================================================
Erzeugt und backt 1 gemeinsames 2048x1024 Trim-Sheet (Cycles CUDA GTX 1070 mit CPU-Fallback,
HDR-Albedo strikt [0.05..0.78], 0 eingebackene Schlagschatten):
  - assets/textures/shipyard_trim_atlas_baseColor.png  [sRGB]
  - assets/textures/shipyard_trim_atlas_normal.png     [Linear / Non-Color]
  - assets/textures/shipyard_trim_atlas_orm.png        [Linear: R=AO, G=Roughness, B=Metallic]
  - assets/textures/shipyard_trim_atlas_emissive.png   [sRGB] (fuer Glut in Schmiede/Meiler/Pechofen)

Aufbau entlang V (8 horizontale Baender, nahtlose Kachelung fuer Voll-U-Streifen):
  Band 0 (V 0.000..0.125): Behauener Basalt (Voll-U nahtlos)
  Band 1 (V 0.125..0.250): Feuchtes Quellstein-Mauerwerk mit Moos-/Mineralspuren (Voll-U nahtlos)
  Band 2 (V 0.250..0.375): Stampferde & Holzkohle-Meilererde (Voll-U nahtlos)
  Band 3 (V 0.375..0.500): Gezimmertes Zedernholz / Planken (Voll-U nahtlos)
  Band 4 (V 0.500..0.625): Schweres Eichenholz / Balken (Voll-U nahtlos)
  Band 5 (V 0.625..0.750): Hainbuchenholz (Zahnrad/Stiel) | Saegeschnitt-Stirnholz | Gezapfte Balken
  Band 6 (V 0.750..0.875): Geflochtenes Schilfrohr | Stroh-/Heu-Lage | Gestreiftes Zeltleinen
  Band 7 (V 0.875..1.000): Gedrehtes Hanftauwerk | Zinnbronze (Met=1) | Renneisen (Met=1) | Kopher-Pech | Glut

Aufruf:
  blender --background --python-exit-code 1 --python assets/scripts/build_shipyard_trim_atlas.py
"""

import os
import sys
import time
import math
import bpy
import numpy as np


TEX_W = 2048
TEX_H = 1024

# Gemeinsame UV-Regionen (u0, v0, u1, v1) mit Sicherheitsrand gegen Mipmap-Bleed
TRIM_REGIONS = {
    # Voll-U kachelnde Streifen (Bands 0..4)
    "cut_basalt":            (0.000, 0.006, 1.000, 0.119),
    "wet_spring_stone":      (0.000, 0.131, 1.000, 0.244),
    "rammed_earth_charcoal": (0.000, 0.256, 1.000, 0.369),
    "cedar_timber":          (0.000, 0.381, 1.000, 0.494),
    "oak_timber":            (0.000, 0.506, 1.000, 0.619),
    # Band 5: Hainbuche, Stirnholz, Gezapfte Balken
    "hornbeam_timber":       (0.006, 0.631, 0.412, 0.744),
    "timber_endgrain":       (0.432, 0.631, 0.568, 0.744),
    "mortise_joinery":       (0.588, 0.631, 0.994, 0.744),
    # Band 6: Schilfrohr, Stroh, Zeltleinen
    "woven_reed_mat":        (0.006, 0.756, 0.372, 0.869),
    "straw_thatch":          (0.392, 0.756, 0.712, 0.869),
    "tent_linen_striped":    (0.732, 0.756, 0.994, 0.869),
    # Band 7: Hanftauwerk, Zinnbronze, Renneisen, Kopher-Bitumen, Schmiede-/Meilerglut
    "hemp_rope":             (0.006, 0.881, 0.292, 0.994),
    "tin_bronze":            (0.312, 0.881, 0.512, 0.994),
    "bloomery_iron":         (0.532, 0.881, 0.712, 0.994),
    "kopher_bitumen":        (0.732, 0.881, 0.852, 0.994),
    "glowing_embers":        (0.874, 0.883, 0.992, 0.992),
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


def setup_cycles(scene, samples=4, use_oidn=False):
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
        scene.cycles.use_denoising = bool(use_oidn)
        if use_oidn and hasattr(scene.cycles, "denoiser"):
            try:
                scene.cycles.denoiser = "OPENIMAGEDENOISE"
            except Exception:
                pass
        scene.cycles.max_bounces = 2
        scene.cycles.diffuse_bounces = 1
        scene.cycles.glossy_bounces = 0
        scene.cycles.transmission_bounces = 0
        scene.cycles.ao_bounces = 2
        scene.cycles.ao_bounces_render = 2

    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    return "CUDA (GPU)" if used_gpu else "CPU"


# ==============================================================================
# PERIODISCHE NUMPY NOISE- & VORONOI-WERKZEUGE
# ==============================================================================

def _hash2(ix, iy, seed=0):
    n = (ix * 374761393 + iy * 668265263 + seed * 1442695041) & 0x7FFFFFFF
    n = (n ^ (n >> 13)) * 1274126177
    n = n & 0x7FFFFFFF
    return (n & 0xFFFFFF) / float(0x1000000)


def periodic_noise(u, v, pu, pv, seed=0):
    """2D periodisches Value-Noise (pu entlang U, pv entlang V)."""
    px = np.mod(u, 1.0) * pu
    py = np.mod(v, 1.0) * pv
    x0 = np.floor(px).astype(np.int64) % pu
    y0 = np.floor(py).astype(np.int64) % pv
    x1 = (x0 + 1) % pu
    y1 = (y0 + 1) % pv
    fx = px - np.floor(px)
    fy = py - np.floor(py)
    wx = fx * fx * fx * (fx * (fx * 6.0 - 15.0) + 10.0)
    wy = fy * fy * fy * (fy * (fy * 6.0 - 15.0) + 10.0)
    v00 = _hash2(x0, y0, seed)
    v10 = _hash2(x1, y0, seed)
    v01 = _hash2(x0, y1, seed)
    v11 = _hash2(x1, y1, seed)
    return (v00 * (1.0 - wx) + v10 * wx) * (1.0 - wy) + (v01 * (1.0 - wx) + v11 * wx) * wy


def periodic_fbm(u, v, pu, pv, octaves=4, seed=0):
    acc = np.zeros_like(u, dtype=np.float32)
    amp = 0.5
    norm = 0.0
    for o in range(octaves):
        mul = 1 << o
        acc += amp * periodic_noise(u, v, pu * mul, pv * mul, seed + o * 131)
        norm += amp
        amp *= 0.5
    return acc / max(1e-6, norm)


def periodic_voronoi(u, v, pu, pv, jitter=0.42, seed=77):
    """Periodische Voronoi-Zellen fuer Stein, Hammerdellen und Glut-Stuecke."""
    px = np.mod(u, 1.0) * pu
    py = np.mod(v, 1.0) * pv
    ix0 = np.floor(px).astype(np.int64)
    iy0 = np.floor(py).astype(np.int64)

    d1 = np.full_like(u, 1e9, dtype=np.float32)
    d2 = np.full_like(u, 1e9, dtype=np.float32)
    cid = np.zeros_like(u, dtype=np.float32)

    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            cx = (ix0 + dx) % pu
            cy = (iy0 + dy) % pv
            jx = 0.5 + jitter * (_hash2(cx, cy, seed) - 0.5)
            jy = 0.5 + jitter * (_hash2(cx, cy, seed + 503) - 0.5)
            gx = (ix0 + dx) + jx - px
            gy = (iy0 + dy) + jy - py
            dist = np.sqrt(gx * gx + gy * gy)
            cell_val = _hash2(cx, cy, seed + 997)
            m1 = dist < d1
            d2 = np.where(m1, d1, np.minimum(d2, dist))
            d1 = np.where(m1, dist, d1)
            cid = np.where(m1, cell_val, cid)
    edge = np.clip(d2 - d1, 0.0, 1.0)
    return d1, edge, cid


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / np.maximum(1e-6, e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def lerp3(c0, c1, w):
    w3 = w[..., None]
    return c0 * (1.0 - w3) + c1 * w3


def _ashlar_courses(u, vl, rows=3, cols_u=12, seed=100):
    """Erzeugt versetzte Steinreihen mit Fugen-Maske und Block-ID."""
    row_f = vl * rows
    row_id = np.floor(row_f).astype(np.int64)
    fv = row_f - np.floor(row_f)
    offset_u = (row_id % 2) * 0.5
    col_f = u * cols_u + offset_u
    col_id = np.floor(col_f).astype(np.int64) % cols_u
    fu = col_f - np.floor(col_f)

    joint_u = smoothstep(0.0, 0.045, fu) * (1.0 - smoothstep(0.955, 1.0, fu))
    joint_v = smoothstep(0.0, 0.09, fv) * (1.0 - smoothstep(0.91, 1.0, fv))
    stone_mask = joint_u * joint_v
    block_val = _hash2(col_id, row_id, seed=seed)
    return stone_mask, block_val, fu, fv


# ==============================================================================
# PROZEDURALE ERZEUGUNG ALLER 8 BAENDER BEI VOLLER 2048x1024 AUFLOESUNG
# ==============================================================================

def build_trim_buffers(w=TEX_W, h=TEX_H):
    """Erzeugt lineare HDR-Albedo [0.05..0.78], Hoehe [m], Roughness, Metallic, Emissive auf (H, W)."""
    print(f"[SHIPYARD ATLAS] Generiere {w}x{h} prozedurale Werft-/Fluss-Materialfelder...", flush=True)
    u_1d = (np.arange(w, dtype=np.float32) + 0.5) / w
    v_1d = (np.arange(h, dtype=np.float32) + 0.5) / h
    uu, vv = np.meshgrid(u_1d, v_1d, indexing="xy")

    alb = np.zeros((h, w, 3), dtype=np.float32)
    hgt = np.zeros((h, w), dtype=np.float32)
    rgh = np.full((h, w), 0.82, dtype=np.float32)
    met = np.zeros((h, w), dtype=np.float32)
    emi = np.zeros((h, w, 3), dtype=np.float32)

    n_fine = periodic_fbm(uu, vv, 128, 64, octaves=3, seed=17)
    n_med  = periodic_fbm(uu, vv, 36, 18, octaves=4, seed=41)
    n_wide = periodic_fbm(uu, vv, 12,  6, octaves=3, seed=73)
    n_wood_u = periodic_fbm(uu, vv, 10, 96, octaves=4, seed=107)

    # --------------------------------------------------------------------------
    # BAND 0 (V 0.000..0.125): BEHAUENER BASALT (Voll-U nahtlos)
    # --------------------------------------------------------------------------
    m = (vv >= 0.000) & (vv < 0.125)
    vl = np.clip((vv - 0.000) / 0.125, 0.0, 1.0)
    s_mask, b_val, fu, fv = _ashlar_courses(uu, vl, rows=3, cols_u=14, seed=211)
    chisel = periodic_fbm(uu * 2.0, vl * 0.5, 96, 24, octaves=3, seed=223)
    basalt_dark = np.array([0.075, 0.080, 0.090], dtype=np.float32)
    basalt_mid  = np.array([0.145, 0.152, 0.168], dtype=np.float32)
    basalt_col = lerp3(basalt_dark, basalt_mid, np.clip(0.35 * b_val + 0.65 * chisel, 0.0, 1.0))
    # Feine Quarz-Einsprenglinge + heller Kalkmoertel in Fugen
    mortar_col = np.array([0.22, 0.20, 0.17], dtype=np.float32)
    col0 = lerp3(mortar_col, basalt_col, s_mask)
    hgt0 = s_mask * (0.012 + 0.006 * chisel + 0.003 * b_val) + 0.002 * n_fine
    rgh0 = lerp3(np.array([0.92]), np.array([0.74]), np.clip(0.5 * chisel + 0.5 * s_mask, 0.0, 1.0))[..., 0]
    alb = np.where(m[..., None], col0, alb)
    hgt = np.where(m, hgt0, hgt)
    rgh = np.where(m, rgh0, rgh)

    # --------------------------------------------------------------------------
    # BAND 1 (V 0.125..0.250): FEUCHTES QUELLSTEIN-MAUERWERK (Voll-U nahtlos)
    # --------------------------------------------------------------------------
    m = (vv >= 0.125) & (vv < 0.250)
    vl = np.clip((vv - 0.125) / 0.125, 0.0, 1.0)
    s_mask, b_val, _, _ = _ashlar_courses(uu, vl, rows=3, cols_u=12, seed=307)
    # Feuchtigkeitsgradient: unten stark durchnaesst, nach oben feuchte Moosadern
    wet_band = np.clip(1.0 - smoothstep(0.18, 0.68, vl) + 0.35 * (n_med - 0.45), 0.0, 1.0)
    moss = smoothstep(0.56, 0.78, n_med) * (1.0 - 0.55 * s_mask) * smoothstep(0.05, 0.45, 1.0 - vl * 0.7)
    lime_dry = lerp3(np.array([0.28, 0.25, 0.20]), np.array([0.42, 0.38, 0.31]), np.clip(0.5 * b_val + 0.5 * n_fine, 0.0, 1.0))
    lime_wet = lime_dry * np.array([0.52, 0.55, 0.52], dtype=np.float32)
    stone1 = lerp3(lime_dry, lime_wet, wet_band)
    stone1 = lerp3(stone1, np.array([0.10, 0.16, 0.07]), moss * 0.72)
    mortar1 = np.array([0.15, 0.14, 0.11], dtype=np.float32)
    col1 = lerp3(mortar1, stone1, s_mask)
    hgt1 = s_mask * (0.014 + 0.005 * n_med + 0.003 * b_val)
    rgh1 = np.clip(0.84 - 0.50 * wet_band * s_mask + 0.08 * moss, 0.24, 0.94)
    alb = np.where(m[..., None], col1, alb)
    hgt = np.where(m, hgt1, hgt)
    rgh = np.where(m, rgh1, rgh)

    # --------------------------------------------------------------------------
    # BAND 2 (V 0.250..0.375): STAMPFERDE & HOLZKOHLE-MEILERERDE (Voll-U nahtlos)
    # --------------------------------------------------------------------------
    m = (vv >= 0.250) & (vv < 0.375)
    vl = np.clip((vv - 0.250) / 0.125, 0.0, 1.0)
    soot_strata = 0.5 + 0.5 * np.sin(vl * 2.0 * math.pi * 4.0 + 3.0 * n_wide)
    charcoal_grit = smoothstep(0.68, 0.85, n_fine)
    earth_dark = np.array([0.065, 0.058, 0.052], dtype=np.float32)
    earth_warm = np.array([0.195, 0.155, 0.110], dtype=np.float32)
    col2 = lerp3(earth_dark, earth_warm, np.clip(0.55 * soot_strata + 0.45 * n_med, 0.0, 1.0))
    col2 = lerp3(col2, np.array([0.055, 0.055, 0.058]), charcoal_grit * 0.65)
    hgt2 = 0.010 * n_med + 0.006 * n_fine + 0.004 * soot_strata
    rgh2 = np.clip(0.84 + 0.12 * n_fine, 0.78, 0.96)
    alb = np.where(m[..., None], col2, alb)
    hgt = np.where(m, hgt2, hgt)
    rgh = np.where(m, rgh2, rgh)

    # --------------------------------------------------------------------------
    # BAND 3 (V 0.375..0.500): GEZIMMERTES ZEDERNHOLZ / PLANKEN (Voll-U nahtlos)
    # --------------------------------------------------------------------------
    m = (vv >= 0.375) & (vv < 0.500)
    vl = np.clip((vv - 0.375) / 0.125, 0.0, 1.0)
    plank_f = vl * 4.0
    plank_id = np.floor(plank_f).astype(np.int64)
    fpv = plank_f - np.floor(plank_f)
    plank_seam = smoothstep(0.0, 0.075, fpv) * (1.0 - smoothstep(0.925, 1.0, fpv))
    p_var = _hash2(plank_id, np.zeros_like(plank_id), seed=409)
    grain_cedar = 0.5 + 0.5 * np.sin((vl * 36.0 + p_var * 5.0 + n_wood_u * 4.2) * math.pi)
    cedar_lo = np.array([0.21, 0.11, 0.055], dtype=np.float32)
    cedar_hi = np.array([0.44, 0.25, 0.130], dtype=np.float32)
    col3 = lerp3(cedar_lo, cedar_hi, np.clip(0.55 * grain_cedar + 0.25 * n_wood_u + 0.20 * p_var, 0.0, 1.0))
    # Stirnduebel-Punkte alle 0.25 U
    peg_u = (uu * 4.0) % 1.0
    peg_d = np.sqrt((peg_u - 0.5) ** 2 + (fpv - 0.5) ** 2 * 0.25)
    peg_mask = 1.0 - smoothstep(0.035, 0.055, peg_d)
    col3 = lerp3(col3, np.array([0.14, 0.08, 0.04]), peg_mask * 0.75)
    col3 = lerp3(np.array([0.075, 0.045, 0.025]), col3, plank_seam)
    hgt3 = plank_seam * (0.008 + 0.003 * grain_cedar) - peg_mask * 0.002
    rgh3 = np.clip(0.64 + 0.14 * (1.0 - grain_cedar) + 0.16 * (1.0 - plank_seam), 0.55, 0.88)
    alb = np.where(m[..., None], col3, alb)
    hgt = np.where(m, hgt3, hgt)
    rgh = np.where(m, rgh3, rgh)

    # --------------------------------------------------------------------------
    # BAND 4 (V 0.500..0.625): SCHWERES EICHENHOLZ / BALKEN (Voll-U nahtlos)
    # --------------------------------------------------------------------------
    m = (vv >= 0.500) & (vv < 0.625)
    vl = np.clip((vv - 0.500) / 0.125, 0.0, 1.0)
    beam_f = vl * 3.0
    beam_id = np.floor(beam_f).astype(np.int64)
    fbv = beam_f - np.floor(beam_f)
    beam_seam = smoothstep(0.0, 0.08, fbv) * (1.0 - smoothstep(0.92, 1.0, fbv))
    b_var = _hash2(beam_id, np.ones_like(beam_id) * 3, seed=509)
    grain_oak = 0.5 + 0.5 * np.sin((vl * 28.0 + b_var * 4.0 + n_wood_u * 5.0) * math.pi)
    adze_fac = periodic_noise(uu, vl, 24, 9, seed=521)
    oak_lo = np.array([0.11, 0.075, 0.045], dtype=np.float32)
    oak_hi = np.array([0.26, 0.185, 0.115], dtype=np.float32)
    col4 = lerp3(oak_lo, oak_hi, np.clip(0.50 * grain_oak + 0.30 * adze_fac + 0.20 * b_var, 0.0, 1.0))
    col4 = lerp3(np.array([0.06, 0.04, 0.025]), col4, beam_seam)
    hgt4 = beam_seam * (0.010 + 0.004 * adze_fac + 0.002 * grain_oak)
    rgh4 = np.clip(0.70 + 0.16 * (1.0 - grain_oak), 0.60, 0.90)
    alb = np.where(m[..., None], col4, alb)
    hgt = np.where(m, hgt4, hgt)
    rgh = np.where(m, rgh4, rgh)

    # --------------------------------------------------------------------------
    # BAND 5 (V 0.625..0.750): HAINBUCHE | STIRNHOLZ | GEZAPFTE BALKEN
    # --------------------------------------------------------------------------
    m = (vv >= 0.625) & (vv < 0.750)
    vl = np.clip((vv - 0.625) / 0.125, 0.0, 1.0)

    # 5a: Hainbuche (U 0.000..0.422)
    m_hb = m & (uu < 0.422)
    grain_hb = 0.5 + 0.5 * np.sin((vl * 42.0 + n_wood_u * 3.0) * math.pi)
    col_hb = lerp3(np.array([0.38, 0.30, 0.19]), np.array([0.58, 0.48, 0.33]), np.clip(0.65 * grain_hb + 0.35 * n_med, 0.0, 1.0))
    hgt_hb = 0.004 + 0.002 * grain_hb
    rgh_hb = np.clip(0.54 + 0.14 * (1.0 - grain_hb), 0.48, 0.72)

    # 5b: Saegeschnitt-Stirnholz (U 0.422..0.578)
    m_eg = m & (uu >= 0.422) & (uu < 0.578)
    dx_eg = (uu - 0.500) / 0.068
    dy_eg = (vl - 0.500) / 0.44
    r_eg = np.sqrt(dx_eg * dx_eg + dy_eg * dy_eg) + 0.06 * n_med
    ang_eg = np.arctan2(dy_eg, dx_eg)
    rings = 0.5 + 0.5 * np.sin(r_eg * 42.0)
    heartwood = 1.0 - smoothstep(0.25, 0.65, r_eg)
    # Radiale Trocknungsrisse
    crack_val = np.abs(np.sin(ang_eg * 3.0 + 0.8))
    crack = smoothstep(0.965, 0.995, crack_val) * smoothstep(0.10, 0.40, r_eg) * (1.0 - smoothstep(0.85, 1.05, r_eg))
    bark_rim = smoothstep(0.88, 0.98, r_eg)
    col_eg = lerp3(np.array([0.36, 0.25, 0.14]), np.array([0.22, 0.13, 0.065]), np.clip(0.5 * rings + 0.5 * heartwood, 0.0, 1.0))
    col_eg = lerp3(col_eg, np.array([0.11, 0.07, 0.045]), bark_rim)
    col_eg = lerp3(col_eg, np.array([0.06, 0.04, 0.025]), crack)
    hgt_eg = 0.007 * (1.0 - crack) + 0.002 * rings + 0.004 * bark_rim
    rgh_eg = np.clip(0.76 + 0.14 * bark_rim + 0.10 * crack, 0.70, 0.95)

    # 5c: Gezapfte Balken / Schwalbenschwanz-Verbindung (U 0.578..1.000)
    m_mj = m & (uu >= 0.578)
    ul_mj = np.clip((uu - 0.578) / (1.000 - 0.578), 0.0, 1.0)
    # Kreuzbalken + Zapfenrahmen
    frame_border = np.maximum(
        1.0 - smoothstep(0.12, 0.15, vl) + smoothstep(0.85, 0.88, vl),
        1.0 - smoothstep(0.10, 0.13, ul_mj) + smoothstep(0.87, 0.90, ul_mj),
    )
    frame_border = np.clip(frame_border, 0.0, 1.0)
    tenon_seam = np.exp(-((ul_mj - 0.50) / 0.015) ** 2) + np.exp(-((vl - 0.50) / 0.03) ** 2)
    tenon_seam = np.clip(tenon_seam, 0.0, 1.0)
    col_mj = lerp3(np.array([0.25, 0.16, 0.09]), np.array([0.35, 0.22, 0.12]), np.clip(0.6 * grain_cedar + 0.4 * n_med, 0.0, 1.0))
    col_mj = lerp3(col_mj, np.array([0.16, 0.10, 0.055]), frame_border * 0.55)
    col_mj = lerp3(col_mj, np.array([0.07, 0.045, 0.025]), tenon_seam * 0.75)
    hgt_mj = 0.008 + 0.004 * frame_border - 0.005 * tenon_seam
    rgh_mj = np.clip(0.68 + 0.15 * tenon_seam, 0.60, 0.88)

    alb = np.where(m_hb[..., None], col_hb, alb)
    hgt = np.where(m_hb, hgt_hb, hgt)
    rgh = np.where(m_hb, rgh_hb, rgh)
    alb = np.where(m_eg[..., None], col_eg, alb)
    hgt = np.where(m_eg, hgt_eg, hgt)
    rgh = np.where(m_eg, rgh_eg, rgh)
    alb = np.where(m_mj[..., None], col_mj, alb)
    hgt = np.where(m_mj, hgt_mj, hgt)
    rgh = np.where(m_mj, rgh_mj, rgh)

    # --------------------------------------------------------------------------
    # BAND 6 (V 0.750..0.875): SCHILFROHR | STROH/HEU | ZELTLEINEN GESTREIFT
    # --------------------------------------------------------------------------
    m = (vv >= 0.750) & (vv < 0.875)
    vl = np.clip((vv - 0.750) / 0.125, 0.0, 1.0)

    # 6a: Geflochtenes Schilfrohr (U 0.000..0.382)
    m_rd = m & (uu < 0.382)
    reed_rib = 0.5 + 0.5 * np.sin(vl * 2.0 * math.pi * 14.0 + 0.8 * n_med)
    reed_bind = np.exp(-((((uu * 16.0) % 1.0) - 0.5) / 0.12) ** 2)
    col_rd = lerp3(np.array([0.26, 0.21, 0.11]), np.array([0.52, 0.43, 0.24]), np.clip(0.65 * reed_rib + 0.35 * n_fine, 0.0, 1.0))
    col_rd = lerp3(col_rd, np.array([0.16, 0.12, 0.07]), reed_bind * 0.55)
    hgt_rd = 0.009 * reed_rib + 0.004 * reed_bind
    rgh_rd = np.clip(0.80 + 0.12 * (1.0 - reed_rib), 0.74, 0.94)

    # 6b: Stroh-/Heu-Lage (U 0.382..0.722)
    m_st = m & (uu >= 0.382) & (uu < 0.722)
    straw_fib = periodic_fbm(uu * 0.6, vl * 3.5, 48, 8, octaves=4, seed=613)
    straw_wisps = 0.5 + 0.5 * np.sin((uu * 95.0 + straw_fib * 6.0) * math.pi)
    col_st = lerp3(np.array([0.34, 0.26, 0.12]), np.array([0.64, 0.52, 0.25]), np.clip(0.55 * straw_wisps + 0.45 * straw_fib, 0.0, 1.0))
    hgt_st = 0.008 * straw_wisps + 0.005 * straw_fib
    rgh_st = np.clip(0.84 + 0.10 * (1.0 - straw_wisps), 0.78, 0.95)

    # 6c: Gewebtes gestreiftes Zeltleinen (U 0.722..1.000)
    m_tl = m & (uu >= 0.722)
    ul_tl = np.clip((uu - 0.722) / (1.000 - 0.722), 0.0, 1.0)
    weave = 0.5 + 0.25 * np.sin(ul_tl * 2.0 * math.pi * 64.0) + 0.25 * np.sin(vl * 2.0 * math.pi * 32.0)
    stripe_phase = (ul_tl * 5.0) % 1.0
    is_terra = ((stripe_phase > 0.14) & (stripe_phase < 0.28)).astype(np.float32)
    is_ochre = ((stripe_phase > 0.45) & (stripe_phase < 0.80)).astype(np.float32)
    col_tl = np.broadcast_to(np.array([0.66, 0.58, 0.44], dtype=np.float32), alb.shape).copy()
    col_tl = lerp3(col_tl, np.array([0.52, 0.37, 0.18]), is_ochre * 0.85)
    col_tl = lerp3(col_tl, np.array([0.42, 0.16, 0.09]), is_terra * 0.88)
    col_tl *= (0.86 + 0.14 * weave[..., None])
    hgt_tl = 0.003 * weave + 0.002 * n_wide
    rgh_tl = np.clip(0.86 + 0.08 * (1.0 - weave), 0.80, 0.95)

    alb = np.where(m_rd[..., None], col_rd, alb)
    hgt = np.where(m_rd, hgt_rd, hgt)
    rgh = np.where(m_rd, rgh_rd, rgh)
    alb = np.where(m_st[..., None], col_st, alb)
    hgt = np.where(m_st, hgt_st, hgt)
    rgh = np.where(m_st, rgh_st, rgh)
    alb = np.where(m_tl[..., None], col_tl, alb)
    hgt = np.where(m_tl, hgt_tl, hgt)
    rgh = np.where(m_tl, rgh_tl, rgh)

    # --------------------------------------------------------------------------
    # BAND 7 (V 0.875..1.000): HANFSEIL | ZINNBRONZE | RENNEISEN | KOPHER | GLUT
    # --------------------------------------------------------------------------
    m = (vv >= 0.875) & (vv <= 1.000)
    vl = np.clip((vv - 0.875) / 0.125, 0.0, 1.0)

    # 7a: Gedrehtes Hanftauwerk (U 0.000..0.302)
    m_rp = m & (uu < 0.302)
    ul_rp = np.clip(uu / 0.302, 0.0, 1.0)
    coil_id = np.floor(vl * 4.0)
    fcv = (vl * 4.0) % 1.0
    coil_round = np.sqrt(np.maximum(0.0, 1.0 - ((fcv - 0.5) * 2.0) ** 2))
    strand = 0.5 + 0.5 * np.sin((ul_rp * 22.0 + fcv * 1.4 + coil_id * 0.37) * 2.0 * math.pi)
    col_rp = lerp3(np.array([0.27, 0.20, 0.12]), np.array([0.52, 0.42, 0.27]), np.clip(0.55 * strand + 0.25 * coil_round + 0.20 * n_fine, 0.0, 1.0))
    hgt_rp = 0.008 * coil_round + 0.004 * strand
    rgh_rp = np.clip(0.84 + 0.10 * (1.0 - strand), 0.78, 0.95)

    # 7b: Gehaemmerte Zinnbronze (U 0.302..0.522, Metallic = 1.0)
    m_bz = m & (uu >= 0.302) & (uu < 0.522)
    d1_bz, _, cid_bz = periodic_voronoi(uu * 3.0, vl, 14, 10, jitter=0.45, seed=701)
    dimple_bz = np.clip(1.0 - d1_bz * 1.25, 0.0, 1.0)
    col_bz = lerp3(np.array([0.52, 0.36, 0.16]), np.array([0.74, 0.55, 0.26]), np.clip(0.65 * dimple_bz + 0.35 * cid_bz, 0.0, 1.0))
    hgt_bz = 0.005 * dimple_bz + 0.002 * n_fine
    rgh_bz = np.clip(0.24 + 0.14 * (1.0 - dimple_bz) + 0.04 * n_fine, 0.22, 0.42)

    # 7c: Dunkles Rennschmiedeeisen (U 0.522..0.722, Metallic = 1.0)
    m_fe = m & (uu >= 0.522) & (uu < 0.722)
    d1_fe, _, cid_fe = periodic_voronoi(uu * 3.0, vl, 12, 8, jitter=0.45, seed=733)
    dimple_fe = np.clip(1.0 - d1_fe * 1.20, 0.0, 1.0)
    col_fe = lerp3(np.array([0.16, 0.16, 0.17]), np.array([0.30, 0.30, 0.32]), np.clip(0.55 * dimple_fe + 0.45 * n_med, 0.0, 1.0))
    hgt_fe = 0.006 * dimple_fe + 0.003 * n_fine
    rgh_fe = np.clip(0.40 + 0.18 * (1.0 - dimple_fe), 0.36, 0.62)

    # 7d: Kopher-Bitumen-Kesseloberflaeche (U 0.722..0.862, hochglaenzend dunkel)
    m_kp = m & (uu >= 0.722) & (uu < 0.862)
    ul_kp = (uu - 0.722) / (0.862 - 0.722)
    r_kp = np.sqrt((ul_kp - 0.5) ** 2 + (vl - 0.5) ** 2)
    ripples = 0.5 + 0.5 * np.sin(r_kp * 34.0 + n_med * 3.0)
    col_kp = lerp3(np.array([0.052, 0.048, 0.045]), np.array([0.095, 0.080, 0.068]), np.clip(0.6 * ripples + 0.4 * n_fine, 0.0, 1.0))
    hgt_kp = 0.005 * ripples + 0.002 * n_med
    rgh_kp = np.clip(0.14 + 0.12 * (1.0 - ripples), 0.12, 0.28)

    # 7e: Rotgluehende Holzkohlen / Schmiedeglut (U 0.862..1.000, Emissive!)
    m_em = m & (uu >= 0.862)
    ul_em = (uu - 0.862) / (1.000 - 0.862)
    d1_em, edge_em, cid_em = periodic_voronoi(ul_em, vl, 9, 7, jitter=0.45, seed=809)
    # Glut-Spalten zwischen dunklen verkohlten Stuecken + Sicherheitsrand gegen Bleed
    crack_glow = 1.0 - smoothstep(0.02, 0.16, edge_em)
    ember_core = smoothstep(0.45, 0.90, cid_em) * (1.0 - smoothstep(0.15, 0.45, d1_em))
    safe_box = (
        smoothstep(0.03, 0.08, ul_em) * (1.0 - smoothstep(0.92, 0.97, ul_em))
        * smoothstep(0.04, 0.09, vl) * (1.0 - smoothstep(0.91, 0.96, vl))
    )
    glow_w = np.clip((crack_glow * 0.92 + ember_core * 0.55) * (0.65 + 0.35 * n_med), 0.0, 1.0) * safe_box
    col_em = lerp3(np.array([0.055, 0.050, 0.048]), np.array([0.32, 0.11, 0.03]), glow_w)
    emi_col = lerp3(np.array([0.92, 0.14, 0.01]), np.array([1.00, 0.52, 0.09]), glow_w) * glow_w[..., None]
    hgt_em = 0.010 * (1.0 - crack_glow) + 0.003 * n_fine
    rgh_em = np.clip(0.90 - 0.12 * glow_w, 0.74, 0.96)

    alb = np.where(m_rp[..., None], col_rp, alb)
    hgt = np.where(m_rp, hgt_rp, hgt)
    rgh = np.where(m_rp, rgh_rp, rgh)

    alb = np.where(m_bz[..., None], col_bz, alb)
    hgt = np.where(m_bz, hgt_bz, hgt)
    rgh = np.where(m_bz, rgh_bz, rgh)
    met = np.where(m_bz, 1.0, met)

    alb = np.where(m_fe[..., None], col_fe, alb)
    hgt = np.where(m_fe, hgt_fe, hgt)
    rgh = np.where(m_fe, rgh_fe, rgh)
    met = np.where(m_fe, 1.0, met)

    alb = np.where(m_kp[..., None], col_kp, alb)
    hgt = np.where(m_kp, hgt_kp, hgt)
    rgh = np.where(m_kp, rgh_kp, rgh)

    alb = np.where(m_em[..., None], col_em, alb)
    hgt = np.where(m_em, hgt_em, hgt)
    rgh = np.where(m_em, rgh_em, rgh)
    emi = np.where(m_em[..., None], emi_col, emi)

    # Strikter HDR-Albedo-Korridor [0.05..0.78] (keine ausgebrannten Weisse / kein reines Schwarz)
    alb = np.clip(alb, 0.05, 0.78)
    rgh = np.clip(rgh, 0.12, 0.96)
    met = np.clip(met, 0.0, 1.0)
    emi = np.clip(emi, 0.0, 1.0)
    return alb, hgt, rgh, met, emi


# ==============================================================================
# 3D HIGH-POLY RELIEF + CYCLES AO & NORMAL BAKE
# ==============================================================================

def _arr_to_blender_image(name, arr_rgb, colorspace="Non-Color"):
    h, w, _ = arr_rgb.shape
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[:, :, :3] = arr_rgb
    img = bpy.data.images.new(name=name, width=w, height=h, alpha=False, float_buffer=True)
    img.colorspace_settings.name = colorspace
    img.pixels.foreach_set(rgba.ravel())
    return img


def _build_relief_mesh(hgt, nu=960, nv=480, apron_u=0.06):
    print(f"[SHIPYARD ATLAS] Baue 3D High-Poly Relief-Mesh ({nu}x{nv} + U-Schuerze)...", flush=True)
    h_src, w_src = hgt.shape

    u_vals = np.linspace(-apron_u, 1.0 + apron_u, nu + 1, dtype=np.float32)
    v_vals = np.linspace(0.0, 1.0, nv + 1, dtype=np.float32)
    uu, vv = np.meshgrid(u_vals, v_vals, indexing="xy")

    px = np.mod(uu, 1.0) * (w_src - 1)
    py = np.clip(vv, 0.0, 1.0) * (h_src - 1)
    ix = np.round(px).astype(np.int64) % w_src
    iy = np.clip(np.round(py).astype(np.int64), 0, h_src - 1)
    zz = hgt[iy, ix]

    xg = uu * 2.0
    yg = vv * 1.0

    mesh = bpy.data.meshes.new("ShipyardTrimHighPoly")
    verts = np.column_stack([xg.ravel(), yg.ravel(), zz.ravel()]).tolist()
    stride = nu + 1
    ii, jj = np.meshgrid(np.arange(nu), np.arange(nv), indexing="xy")
    v00 = (jj * stride + ii).ravel()
    faces = np.column_stack([v00, v00 + 1, v00 + stride + 1, v00 + stride]).tolist()
    mesh.from_pydata(verts, [], faces)
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))

    uv_layer = mesh.uv_layers.new(name="UVMap")
    uv_u = np.mod(uu, 1.0).ravel()
    uv_v = vv.ravel()
    loop_v = np.empty(len(mesh.loops), dtype=np.int64)
    mesh.loops.foreach_get("vertex_index", loop_v)
    uv_arr = np.column_stack([uv_u[loop_v], uv_v[loop_v]]).astype(np.float32)
    uv_layer.data.foreach_set("uv", uv_arr.ravel())

    obj = bpy.data.objects.new("ShipyardTrimHighPoly", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def _build_target_plane():
    mesh = bpy.data.meshes.new("ShipyardTrimTarget")
    verts = [(0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (2.0, 1.0, 0.0), (0.0, 1.0, 0.0)]
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    uv_layer = mesh.uv_layers.new(name="UVMap")
    for loop, uv in zip(mesh.loops, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]):
        uv_layer.data[loop.index].uv = uv
    obj = bpy.data.objects.new("ShipyardTrimTarget", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def _linear_to_srgb(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1.0 / 2.4) - 0.055)


def save_np_png(arr, filepath, is_srgb=False):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    h, w, _ = arr.shape
    out = _linear_to_srgb(arr) if is_srgb else np.clip(arr, 0.0, 1.0)
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[:, :, :3] = out
    img = bpy.data.images.new("_SaveTmp", width=w, height=h, alpha=False, float_buffer=False)
    img.colorspace_settings.name = "sRGB" if is_srgb else "Non-Color"
    img.pixels.foreach_set(rgba.ravel())
    img.filepath_raw = filepath
    img.file_format = "PNG"
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.image_settings.color_mode = "RGB"
    bpy.context.scene.render.image_settings.color_depth = "8"
    img.save()
    bpy.data.images.remove(img)


def bake_shipyard_trim_atlas():
    t0 = time.time()
    root = get_project_root()
    tex_dir = os.path.join(root, "assets", "textures")
    os.makedirs(tex_dir, exist_ok=True)

    scene = clear_scene()
    dev_label = setup_cycles(scene, samples=4, use_oidn=False)
    print(f"[SHIPYARD ATLAS] Start | Cycles Device: {dev_label}", flush=True)

    alb, hgt, rgh, met, emi = build_trim_buffers(TEX_W, TEX_H)
    hi_obj = _build_relief_mesh(hgt, nu=960, nv=480, apron_u=0.06)
    lo_obj = _build_target_plane()

    hi_mat = bpy.data.materials.new("ShipyardTrimHiMat")
    hi_mat.use_nodes = True
    nt_h = hi_mat.node_tree
    nt_h.nodes.clear()
    out_h = nt_h.nodes.new("ShaderNodeOutputMaterial")
    bsdf_h = nt_h.nodes.new("ShaderNodeBsdfPrincipled")
    nt_h.links.new(bsdf_h.outputs["BSDF"], out_h.inputs["Surface"])

    img_h = _arr_to_blender_image("TmpShipyardHgt2K", np.repeat(hgt[..., None], 3, axis=-1), "Non-Color")
    tex_h = nt_h.nodes.new("ShaderNodeTexImage")
    tex_h.image = img_h
    tex_h.extension = "REPEAT"
    bump = nt_h.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.24
    bump.inputs["Distance"].default_value = 0.012
    nt_h.links.new(tex_h.outputs["Color"], bump.inputs["Height"])
    nt_h.links.new(bump.outputs["Normal"], bsdf_h.inputs["Normal"])
    hi_obj.data.materials.append(hi_mat)

    lo_mat = bpy.data.materials.new("ShipyardTrimLoMat")
    lo_mat.use_nodes = True
    lo_obj.data.materials.append(lo_mat)

    img_nrm = bpy.data.images.new("BakeNrm", width=TEX_W, height=TEX_H, alpha=False, float_buffer=True)
    img_nrm.colorspace_settings.name = "Non-Color"
    img_ao  = bpy.data.images.new("BakeAO", width=TEX_W, height=TEX_H, alpha=False, float_buffer=True)
    img_ao.colorspace_settings.name = "Non-Color"

    tn = lo_mat.node_tree.nodes.new("ShaderNodeTexImage")
    tn.image = img_nrm
    lo_mat.node_tree.nodes.active = tn

    bpy.ops.object.select_all(action="DESELECT")
    hi_obj.select_set(True)
    lo_obj.select_set(True)
    bpy.context.view_layer.objects.active = lo_obj

    scene.render.bake.use_selected_to_active = True
    scene.render.bake.cage_extrusion = 0.12
    scene.render.bake.max_ray_distance = 0.24
    scene.render.bake.margin = 0

    print("[SHIPYARD ATLAS] Bake Normal-Map (4 Samples, Tangent-Space)...", flush=True)
    scene.cycles.samples = 4
    scene.cycles.use_denoising = False
    bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")

    print("[SHIPYARD ATLAS] Bake Ambient Occlusion (16 Samples + OIDN)...", flush=True)
    tn.image = img_ao
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    try:
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    bpy.ops.object.bake(type="AO")

    nrm_arr = np.empty(TEX_W * TEX_H * 4, dtype=np.float32)
    img_nrm.pixels.foreach_get(nrm_arr)
    nrm_rgb = np.clip(nrm_arr.reshape((TEX_H, TEX_W, 4))[:, :, :3], 0.0, 1.0)

    ao_arr = np.empty(TEX_W * TEX_H * 4, dtype=np.float32)
    img_ao.pixels.foreach_get(ao_arr)
    ao_r = np.clip(ao_arr.reshape((TEX_H, TEX_W, 4))[:, :, 0], 0.28, 1.0)

    orm_rgb = np.stack([ao_r, rgh, met], axis=-1)

    p_col = os.path.join(tex_dir, "shipyard_trim_atlas_baseColor.png")
    p_nrm = os.path.join(tex_dir, "shipyard_trim_atlas_normal.png")
    p_orm = os.path.join(tex_dir, "shipyard_trim_atlas_orm.png")
    p_emi = os.path.join(tex_dir, "shipyard_trim_atlas_emissive.png")

    save_np_png(alb, p_col, is_srgb=True)
    save_np_png(nrm_rgb, p_nrm, is_srgb=False)
    save_np_png(orm_rgb, p_orm, is_srgb=False)
    save_np_png(emi, p_emi, is_srgb=True)

    # Naht-Check entlang U=0 / U=1 fuer die 5 kachelnden Baender (V < 0.625)
    k_h = int(0.62 * TEX_H)
    seam_alb = float(np.mean(np.abs(alb[:k_h, 0, :] - alb[:k_h, -1, :])))
    seam_nrm = float(np.mean(np.abs(nrm_rgb[:k_h, 0, :] - nrm_rgb[:k_h, -1, :])))
    dt = time.time() - t0
    print(
        f"[SHIPYARD ATLAS] FERTIG in {dt:.2f}s ({dev_label}) | Albedo=[{alb.min():.3f}..{alb.max():.3f}] | "
        f"AO=[{ao_r.min():.2f}..{ao_r.max():.2f}] | EmissiveMax={emi.max():.2f} | "
        f"U-Seam(Alb={seam_alb:.4f}, Nrm={seam_nrm:.4f})",
        flush=True,
    )
    print(f"  -> {p_col}", flush=True)
    print(f"  -> {p_nrm}", flush=True)
    print(f"  -> {p_orm}", flush=True)
    print(f"  -> {p_emi}", flush=True)
    return p_col, p_nrm, p_orm, p_emi, dt


if __name__ == "__main__":
    bake_shipyard_trim_atlas()
