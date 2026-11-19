"""
build_city_trim_atlas.py — Mesopotamischer 2048x1024 HDR Architektur- & Strassen-Trim-Sheet-Baker
==================================================================================================
Erzeugt und backt 1 gemeinsames 2048x1024 Trim-Sheet (Cycles CUDA GTX 1070 mit CPU-Fallback,
HDR-Albedo strikt [0.06..0.72], 0 eingebackene Schlagschatten):
  - assets/textures/city_trim_atlas_baseColor.png  [sRGB]
  - assets/textures/city_trim_atlas_normal.png     [Linear / Non-Color]
  - assets/textures/city_trim_atlas_orm.png        [Linear: R=AO, G=Roughness, B=Metallic]

Aufbau entlang V (6 horizontale Baender, nahtlos kachelnd entlang U):
  Band 0 (V 0.000..0.166): Wohngassen & Vorstadt-Wege (Lehmboden, Randstein-Kante, Entwaesserungsrinne)
  Band 1 (V 0.166..0.354): Koenigs-/Prozessionsstrasse (Kalkstein-/Basaltplatten, Karren-Spurrillen, Sandrand)
  Band 2 (V 0.354..0.524): Verwitterter Lehmziegel-Putz (horizontale Fugen, Strohmagerung, Putzschaeden)
  Band 3 (V 0.524..0.694): Gebrannter mesopotamischer Ziegel & abgeschrägte Sockel-Feuchte
  Band 4 (V 0.694..0.850): Zedernbalken | Vigas-Stirn | Geschnitzte Tueren | Zinnbronze | Schilf-Pergola
  Band 5 (V 0.850..1.000): Ocker-/Terrakotta-/Leinen-Markise | Gips-Tempelpilaster | Lapislazuli-Fries

Aufruf:
  blender --background --python assets/scripts/build_city_trim_atlas.py
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
    # Band 0: Wohngassen & Vorstadt-Wege (kachelt frei entlang U)
    "alley_mud_road":      (0.000, 0.005, 1.000, 0.161),
    # Band 1: Koenigs-/Prozessionsstrasse (kachelt frei entlang U)
    "royal_stone_road":    (0.000, 0.171, 1.000, 0.349),
    # Band 2: Verwitterter Lehmziegel-Putz (kachelt frei entlang U)
    "mudbrick_plaster":    (0.000, 0.359, 1.000, 0.519),
    # Band 3: Gebrannter Ziegel + Sockelfeuchte (unteres Drittel = Sockelfeuchte)
    "fired_brick_plinth":  (0.000, 0.529, 1.000, 0.689),
    "fired_brick_upper":   (0.000, 0.585, 1.000, 0.689),
    "damp_plinth":         (0.000, 0.529, 1.000, 0.582),
    # Band 4: Holz, Vigas, Tueren, Zinnbronze, Schilf-Pergolen
    "cedar_timber":        (0.005, 0.699, 0.265, 0.845),
    "vigas_log_end":       (0.282, 0.702, 0.358, 0.842),
    "carved_door":         (0.374, 0.700, 0.576, 0.844),
    "tin_bronze":          (0.592, 0.700, 0.668, 0.844),
    "reed_pergola":        (0.684, 0.699, 0.996, 0.845),
    # Band 5: Markisen, Gips-Tempelfries, Lapislazuli-Fries
    "woven_awning":        (0.005, 0.855, 0.338, 0.995),
    "gypsum_temple":       (0.354, 0.855, 0.658, 0.995),
    "lapis_frieze":        (0.674, 0.855, 0.996, 0.995),
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
    """Periodische Voronoi-Zellen fuer Kalkstein-/Basaltplatten und Randsteine."""
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


# ==============================================================================
# PROZEDURALE ERZEUGUNG ALLER 6 STREIFEN BEI VOLLER 2048x1024 AUFLOESUNG
# ==============================================================================

def build_trim_buffers(w=TEX_W, h=TEX_H):
    """Erzeugt lineare HDR-Albedo [0.06..0.72], Hoehe [m], Roughness und Metallic auf (H, W)."""
    print(f"[TRIM ATLAS] Generiere {w}x{h} prozedurale Relief-, Albedo- & Material-Felder...", flush=True)
    u_1d = (np.arange(w, dtype=np.float32) + 0.5) / w
    v_1d = (np.arange(h, dtype=np.float32) + 0.5) / h
    uu, vv = np.meshgrid(u_1d, v_1d, indexing="xy")

    alb = np.zeros((h, w, 3), dtype=np.float32)
    hgt = np.zeros((h, w), dtype=np.float32)
    rgh = np.full((h, w), 0.85, dtype=np.float32)
    met = np.zeros((h, w), dtype=np.float32)

    # Gemeinsames periodisches Mikro-Rauschen
    n_fine = periodic_fbm(uu, vv, 96, 48, octaves=3, seed=11)
    n_med  = periodic_fbm(uu, vv, 32, 16, octaves=4, seed=29)
    n_wide = periodic_fbm(uu, vv, 12,  6, octaves=3, seed=53)

    # --------------------------------------------------------------------------
    # BAND 0 (V 0.000..0.166): WOHNGASSEN & VORSTADT-WEGE (Strip 6)
    # --------------------------------------------------------------------------
    m = (vv >= 0.000) & (vv < 0.166)
    vl = np.clip((vv - 0.000) / 0.166, 0.0, 1.0)

    # Randstein-Kanten oben & unten (0..0.18 und 0.82..1.0)
    curb_mask = np.maximum(1.0 - smoothstep(0.14, 0.20, vl), smoothstep(0.80, 0.86, vl))
    # Randstein-Steinquader entlang U (24 Bloecke)
    curb_u = uu * 24.0
    curb_id = np.floor(curb_u).astype(np.int64) % 24
    curb_fu = curb_u - np.floor(curb_u)
    curb_joint = smoothstep(0.0, 0.07, curb_fu) * (1.0 - smoothstep(0.93, 1.0, curb_fu))
    curb_var = _hash2(curb_id, np.zeros_like(curb_id), seed=401)

    # Entwaesserungsrinne bei vl ~ 0.27
    gutter = np.exp(-((vl - 0.27) / 0.055) ** 2)
    # Gestaffelte Fuss- & Karrenspuren in Lehmmitte
    foot_track = np.exp(-((vl - 0.56) / 0.14) ** 2) * (0.65 + 0.35 * np.sin(uu * 2.0 * math.pi * 10.0))

    # Lehmfarbe (warm ocker-braun) + Stroh/Steinchen
    straw_speck = (periodic_noise(uu, vv, 180, 90, seed=419) > 0.88).astype(np.float32)
    mud_col = lerp3(np.array([0.23, 0.17, 0.11]), np.array([0.36, 0.28, 0.19]), n_med)
    mud_col = lerp3(mud_col, np.array([0.46, 0.38, 0.24]), straw_speck * 0.45)
    # Feuchtere Rinne
    mud_col = lerp3(mud_col, np.array([0.13, 0.10, 0.07]), gutter * 0.65)
    # Randsteine (heller Kalk-Sandstein)
    stone_col = lerp3(np.array([0.32, 0.28, 0.22]), np.array([0.46, 0.41, 0.33]), curb_var * 0.6 + n_fine * 0.4)
    stone_col = lerp3(np.array([0.16, 0.13, 0.09]), stone_col, curb_joint)

    b0_col = lerp3(mud_col, stone_col, curb_mask)
    b0_hgt = (0.008 * n_med + 0.003 * n_fine - 0.024 * gutter - 0.007 * foot_track) * (1.0 - curb_mask) \
           + curb_mask * (0.026 * curb_joint + 0.005 * n_fine - 0.004)
    b0_rgh = 0.91 - 0.18 * gutter - 0.12 * curb_mask + 0.04 * n_fine

    alb[m] = b0_col[m]
    hgt[m] = b0_hgt[m]
    rgh[m] = b0_rgh[m]

    # --------------------------------------------------------------------------
    # BAND 1 (V 0.166..0.354): KOENIGS- / PROZESSIONSSTRASSE (Strip 5)
    # --------------------------------------------------------------------------
    m = (vv >= 0.166) & (vv < 0.354)
    vl = np.clip((vv - 0.166) / 0.188, 0.0, 1.0)

    # Unregelmaessige polygonale Platten (periodisch entlang U=18, V=6)
    _, edge, cid = periodic_voronoi(uu, vl * 0.999, 18, 6, jitter=0.38, seed=511)
    slab = smoothstep(0.035, 0.115, edge)
    is_basalt = (cid < 0.26).astype(np.float32)

    lime_slab = lerp3(np.array([0.33, 0.29, 0.23]), np.array([0.50, 0.44, 0.35]), (cid - 0.26) / 0.74 * 0.65 + n_fine * 0.35)
    basalt_slab = lerp3(np.array([0.10, 0.10, 0.11]), np.array([0.19, 0.18, 0.18]), n_fine * 0.6 + cid * 0.4)
    slab_col = lerp3(lime_slab, basalt_slab, is_basalt)
    # Moertelfugen mit Sandstaub
    joint_col = np.array([0.22, 0.18, 0.12])
    b1_col = lerp3(joint_col, slab_col, slab)

    # Zwei parallele Karren-Spurrillen entlang U bei vl=0.36 und vl=0.64
    rut1 = np.exp(-((vl - 0.36) / 0.065) ** 2)
    rut2 = np.exp(-((vl - 0.64) / 0.065) ** 2)
    ruts = np.maximum(rut1, rut2) * (0.78 + 0.22 * periodic_noise(uu, vl, 16, 4, seed=541))
    b1_col = lerp3(b1_col, b1_col * 0.84 + np.array([0.04, 0.03, 0.02]), ruts * 0.55)

    # Sandverwehung am oberen und unteren Rand
    sand_edge = np.maximum(1.0 - smoothstep(0.06, 0.20, vl), smoothstep(0.80, 0.94, vl))
    sand_drift = np.clip(sand_edge * (0.65 + 0.55 * n_med), 0.0, 1.0)
    sand_col = lerp3(np.array([0.40, 0.32, 0.20]), np.array([0.54, 0.44, 0.28]), n_fine)
    b1_col = lerp3(b1_col, sand_col, sand_drift)

    b1_hgt = (0.022 * slab + 0.005 * (cid - 0.5) * slab + 0.004 * n_fine - 0.020 * ruts) * (1.0 - 0.65 * sand_drift) \
           + sand_drift * (0.010 + 0.005 * np.sin(uu * 2.0 * math.pi * 12.0 + vl * 8.0))
    b1_rgh = 0.78 - 0.22 * ruts * slab + 0.15 * sand_drift + 0.06 * (1.0 - slab)

    alb[m] = b1_col[m]
    hgt[m] = b1_hgt[m]
    rgh[m] = b1_rgh[m]

    # --------------------------------------------------------------------------
    # BAND 2 (V 0.354..0.524): VERWITTERTER LEHMZIEGEL-PUTZ (Strip 1)
    # --------------------------------------------------------------------------
    m = (vv >= 0.354) & (vv < 0.524)
    vl = np.clip((vv - 0.354) / 0.170, 0.0, 1.0)

    # Horizontale Putzlagen-Fugen (1:1 Weltproportion fuer 2048x174 px Streifen)
    n_plaster_med = periodic_fbm(uu, vv, 72, 12, octaves=4, seed=607)
    n_plaster_fine = periodic_fbm(uu, vv, 192, 32, octaves=3, seed=611)
    trowel_wave = 0.03 * np.sin(uu * 2.0 * math.pi * 12.0)
    course_v = (vl * 5.0 + trowel_wave) % 1.0
    course_seam = np.exp(-((course_v - 0.5) / 0.10) ** 2) * 0.18

    # Dezente, warme Putzschaeden legen darunterliegende Lehmziegel leicht frei (horizontale Ziegel-Proportion)
    damage_noise = periodic_fbm(uu, vl, 24, 10, octaves=3, seed=613)
    damage_mask = smoothstep(0.70, 0.80, damage_noise) * 0.62
    row_i = np.floor(vl * 8.0).astype(np.int64)
    brick_u = (uu * 24.0 + (row_i % 2) * 0.5) % 1.0
    brick_v = (vl * 8.0) % 1.0
    brick_mortar = smoothstep(0.04, 0.11, brick_u) * (1.0 - smoothstep(0.89, 0.96, brick_u)) \
                 * smoothstep(0.06, 0.15, brick_v) * (1.0 - smoothstep(0.85, 0.94, brick_v))

    # Strohmagerung (feine kurze goldene Halme)
    chaff = (periodic_noise(uu, vl, 320, 48, seed=631) > 0.90).astype(np.float32)

    plaster_col = lerp3(np.array([0.39, 0.31, 0.21]), np.array([0.52, 0.43, 0.31]), n_plaster_med * 0.65 + n_plaster_fine * 0.35)
    plaster_col = lerp3(plaster_col, np.array([0.58, 0.49, 0.33]), chaff * 0.42)
    plaster_col *= (1.0 - 0.08 * course_seam[..., None])

    under_brick = lerp3(np.array([0.30, 0.22, 0.14]), np.array([0.38, 0.29, 0.19]), n_plaster_fine)
    under_brick = lerp3(np.array([0.25, 0.19, 0.12]), under_brick, brick_mortar)

    b2_col = lerp3(plaster_col, under_brick, damage_mask)
    b2_hgt = 0.011 * (1.0 - damage_mask) + 0.004 * n_plaster_med + 0.002 * n_plaster_fine - 0.003 * course_seam \
           + damage_mask * (0.006 * brick_mortar)
    b2_rgh = 0.89 + 0.05 * damage_mask + 0.03 * n_plaster_fine

    alb[m] = b2_col[m]
    hgt[m] = b2_hgt[m]
    rgh[m] = b2_rgh[m]

    # --------------------------------------------------------------------------
    # BAND 3 (V 0.524..0.694): GEBRANNTER ZIEGEL & SOCKEL-FEUCHTE (Strip 2)
    # --------------------------------------------------------------------------
    m = (vv >= 0.524) & (vv < 0.694)
    vl = np.clip((vv - 0.524) / 0.170, 0.0, 1.0)

    n_rows = 6
    n_cols = 32
    row_f = vl * n_rows
    row_i = np.floor(row_f).astype(np.int64)
    bu_raw = uu * n_cols + (row_i % 2) * 0.5
    col_i = np.floor(bu_raw).astype(np.int64) % n_cols
    bu = bu_raw - np.floor(bu_raw)
    bv = row_f - np.floor(row_f)

    # Flache mesopotamische Ziegel (2:1 Proportion) mit klarer Fuge
    br_mask = smoothstep(0.03, 0.09, bu) * (1.0 - smoothstep(0.91, 0.97, bu)) \
            * smoothstep(0.06, 0.14, bv) * (1.0 - smoothstep(0.86, 0.94, bv))
    br_id = _hash2(col_i, row_i, seed=709)

    brick_warm = lerp3(np.array([0.28, 0.17, 0.11]), np.array([0.46, 0.29, 0.18]), br_id * 0.72 + n_plaster_fine * 0.28)
    mortar_col = np.array([0.29, 0.24, 0.18])
    b3_col = lerp3(mortar_col, brick_warm, br_mask)

    # Sockel-Feuchte im unteren Drittel (vl < 0.34, mit wolkiger Kapillarlinie + Salzausbluehung)
    cap_line = 0.30 + 0.05 * np.sin(uu * 2.0 * math.pi * 10.0) + 0.04 * (n_plaster_med - 0.5)
    damp_mask = 1.0 - smoothstep(cap_line - 0.08, cap_line + 0.06, vl)
    salt_eff = smoothstep(0.70, 0.86, n_plaster_fine) * np.exp(-((vl - cap_line) / 0.045) ** 2)
    bitumen_base = 1.0 - smoothstep(0.04, 0.13, vl)

    b3_col = lerp3(b3_col, b3_col * 0.46 + np.array([0.03, 0.025, 0.02]), damp_mask * 0.82)
    b3_col = lerp3(b3_col, np.array([0.09, 0.08, 0.07]), bitumen_base * 0.72)
    b3_col = lerp3(b3_col, np.array([0.52, 0.48, 0.41]), salt_eff * 0.40)

    b3_hgt = 0.015 * br_mask + 0.003 * n_plaster_fine + 0.003 * br_id * br_mask
    b3_rgh = 0.85 - 0.16 * damp_mask - 0.10 * bitumen_base + 0.05 * (1.0 - br_mask)

    alb[m] = b3_col[m]
    hgt[m] = b3_hgt[m]
    rgh[m] = b3_rgh[m]

    # --------------------------------------------------------------------------
    # BAND 4 (V 0.694..0.850): ZEDERNHOLZ | VIGAS | TUEREN | BRONZE | SCHILF
    # --------------------------------------------------------------------------
    m_b4 = (vv >= 0.694) & (vv < 0.850)
    vl4 = np.clip((vv - 0.694) / 0.156, 0.0, 1.0)

    # 4A: Zedernholz-Balken (U 0.000..0.272)
    m = m_b4 & (uu < 0.272)
    ul = np.clip(uu / 0.272, 0.0, 1.0)
    plank_v = (vl4 * 4.0) % 1.0
    plank_seam = smoothstep(0.02, 0.06, plank_v) * (1.0 - smoothstep(0.94, 0.98, plank_v))
    plank_id = _hash2(np.zeros_like(uu, dtype=np.int64), np.floor(vl4 * 4.0).astype(np.int64), seed=811)
    wood_grain = 0.5 + 0.5 * np.sin((vl4 * 36.0 + 2.2 * periodic_fbm(ul, vl4, 6, 12, seed=821)) * math.pi)
    cedar_col = lerp3(np.array([0.14, 0.08, 0.05]), np.array([0.29, 0.17, 0.10]), wood_grain * 0.65 + plank_id * 0.25 + n_fine * 0.10)
    cedar_col *= (0.55 + 0.45 * plank_seam[..., None])
    alb[m] = cedar_col[m]
    hgt[m] = (0.012 * plank_seam + 0.003 * wood_grain)[m]
    rgh[m] = (0.74 - 0.08 * wood_grain + 0.12 * (1.0 - plank_seam))[m]

    # 4B: Vigas-Balkenstirn / Jahresringe (U 0.272..0.366)
    m = m_b4 & (uu >= 0.272) & (uu < 0.366)
    ul = (uu - 0.272) / (0.366 - 0.272)
    dx = (ul - 0.5) * 2.0
    dy = (vl4 - 0.5) * 2.0
    rad = np.sqrt(dx * dx + dy * dy)
    ang = np.arctan2(dy, dx)
    rings = 0.5 + 0.5 * np.sin((rad * 18.0 + 0.6 * n_med) * math.pi)
    crack = np.exp(-((np.abs(ang - 0.4) / 0.06) ** 2)) * smoothstep(0.15, 0.85, rad)
    bark_rim = smoothstep(0.78, 0.90, rad)
    vigas_col = lerp3(np.array([0.22, 0.13, 0.07]), np.array([0.38, 0.25, 0.14]), rings)
    vigas_col = lerp3(vigas_col, np.array([0.09, 0.05, 0.03]), np.maximum(crack * 0.8, bark_rim * 0.75))
    alb[m] = vigas_col[m]
    hgt[m] = (0.015 * (1.0 - bark_rim * 0.4) - 0.014 * crack + 0.003 * rings)[m]
    rgh[m] = (0.76 + 0.14 * bark_rim)[m]

    # 4C: Geschnitzte Zedernholz-Tuer (U 0.366..0.584)
    m = m_b4 & (uu >= 0.366) & (uu < 0.584)
    ul = (uu - 0.366) / (0.584 - 0.366)
    # Tuer-Rahmen & Querriegel + vertikale Bretter
    frame_outer = np.maximum(
        np.maximum(1.0 - smoothstep(0.08, 0.13, ul), smoothstep(0.87, 0.92, ul)),
        np.maximum(1.0 - smoothstep(0.08, 0.14, vl4), smoothstep(0.86, 0.92, vl4)),
    )
    cross_rail = np.exp(-((vl4 - 0.50) / 0.07) ** 2) + np.exp(-((vl4 - 0.24) / 0.05) ** 2) + np.exp(-((vl4 - 0.76) / 0.05) ** 2)
    cross_rail = np.clip(cross_rail, 0.0, 1.0)
    panel_planks = smoothstep(0.03, 0.09, (ul * 6.0) % 1.0) * (1.0 - smoothstep(0.91, 0.97, (ul * 6.0) % 1.0))
    # Eingeschnitztes Rauten-Ornament in den Tuerfeldern
    carve_d = np.abs(((ul - 0.5) * 4.0) % 1.0 - 0.5) + np.abs(((vl4 - 0.5) * 4.0) % 1.0 - 0.5)
    carve_groov = 1.0 - smoothstep(0.28, 0.36, carve_d)
    door_struct = np.maximum(frame_outer, cross_rail * 0.9)
    door_col = lerp3(np.array([0.13, 0.07, 0.04]), np.array([0.26, 0.15, 0.08]),
                     0.5 * panel_planks + 0.35 * door_struct + 0.15 * n_fine)
    door_col = lerp3(door_col, np.array([0.33, 0.21, 0.12]), carve_groov * (1.0 - door_struct) * 0.45)
    alb[m] = door_col[m]
    hgt[m] = (0.016 * door_struct + 0.008 * panel_planks + 0.005 * carve_groov * (1.0 - door_struct))[m]
    rgh[m] = (0.72 - 0.08 * door_struct + 0.05 * n_fine)[m]

    # 4D: Zinnbronze-Beschlag mit Nieten (U 0.584..0.676)
    m = m_b4 & (uu >= 0.584) & (uu < 0.676)
    ul = (uu - 0.584) / (0.676 - 0.584)
    # 3x5 Nieten-Raster
    ru = ((ul * 3.0) % 1.0) - 0.5
    rv = ((vl4 * 5.0) % 1.0) - 0.5
    r_dist = np.sqrt(ru * ru + rv * rv)
    rivet = 1.0 - smoothstep(0.14, 0.24, r_dist)
    bronze_col = lerp3(np.array([0.28, 0.18, 0.08]), np.array([0.48, 0.32, 0.14]), 0.4 + 0.45 * rivet + 0.15 * n_fine)
    alb[m] = bronze_col[m]
    hgt[m] = (0.006 + 0.016 * rivet + 0.002 * n_fine)[m]
    rgh[m] = (0.42 - 0.10 * rivet + 0.08 * n_fine)[m]
    met[m] = (0.86 + 0.08 * rivet)[m]

    # 4E: Geflochtene Schilf-Pergolen & Mudhif-Schilfbuendel (U 0.676..1.000)
    m = m_b4 & (uu >= 0.676)
    ul = (uu - 0.676) / (1.000 - 0.676)
    # Gebuendelte Schilfrohre entlang V + geflochtene Querbaender
    stalk = np.abs(np.sin(ul * math.pi * 22.0)) ** 0.55
    weft_band = np.exp(-((((vl4 * 6.0) % 1.0) - 0.5) / 0.14) ** 2)
    reed_var = periodic_noise(ul, vl4, 24, 8, seed=859)
    reed_col = lerp3(np.array([0.26, 0.19, 0.10]), np.array([0.47, 0.37, 0.21]), stalk * 0.65 + reed_var * 0.35)
    reed_col = lerp3(reed_col, np.array([0.20, 0.14, 0.07]), weft_band * 0.40)
    alb[m] = reed_col[m]
    hgt[m] = (0.018 * stalk + 0.008 * weft_band + 0.002 * n_fine)[m]
    rgh[m] = (0.86 - 0.06 * stalk)[m]

    # --------------------------------------------------------------------------
    # BAND 5 (V 0.850..1.000): MARKISEN | GIPS-TEMPELFRIES | LAPISLAZULI-FRIES
    # --------------------------------------------------------------------------
    m_b5 = (vv >= 0.850) & (vv <= 1.000)
    vl5 = np.clip((vv - 0.850) / 0.150, 0.0, 1.0)

    # 5A: Gewebte Ocker-/Terrakotta-/Leinen-Markisen (U 0.000..0.346)
    m = m_b5 & (uu < 0.346)
    ul = uu / 0.346
    # Webstruktur (Kette & Schuss)
    warp = 0.5 + 0.5 * np.sin(ul * 2.0 * math.pi * 64.0)
    weft = 0.5 + 0.5 * np.sin(vl5 * 2.0 * math.pi * 40.0)
    weave = 0.5 * warp + 0.5 * weft
    # Streifenmuster: Ocker, Terrakotta, Naturleinen
    stripe_idx = np.floor(ul * 9.0).astype(np.int64) % 3
    c_linen = np.array([0.52, 0.45, 0.33])
    c_ochre = np.array([0.48, 0.31, 0.12])
    c_terra = np.array([0.38, 0.14, 0.09])
    aw_col = np.where(stripe_idx[..., None] == 0, c_linen, np.where(stripe_idx[..., None] == 1, c_ochre, c_terra))
    # Zier-Borte unten
    hem = 1.0 - smoothstep(0.08, 0.14, vl5)
    aw_col = lerp3(aw_col, c_terra * 0.85, hem * 0.6)
    aw_col = aw_col * (0.86 + 0.18 * weave[..., None]) * (0.92 + 0.14 * n_fine[..., None])
    alb[m] = aw_col[m]
    hgt[m] = (0.008 * weave + 0.006 * hem + 0.004 * n_med)[m]
    rgh[m] = (0.90 + 0.05 * weave)[m]

    # 5B: Gips-Tempelpilaster & gekalkter Djuss-Putz (U 0.346..0.666)
    m = m_b5 & (uu >= 0.346) & (uu < 0.666)
    ul = (uu - 0.346) / (0.666 - 0.346)
    # Sumerische Nischenpilaster (abgetreppte senkrechte Kanneluren)
    pil_u = (ul * 6.0) % 1.0
    niche = smoothstep(0.18, 0.24, pil_u) * (1.0 - smoothstep(0.76, 0.82, pil_u))
    inner_niche = smoothstep(0.32, 0.38, pil_u) * (1.0 - smoothstep(0.62, 0.68, pil_u))
    relief_z = 0.022 * (1.0 - 0.55 * niche - 0.45 * inner_niche)
    # Gekalkter Gipsputz (warmes Kalkcreme, strictly <= 0.62 Albedo!)
    gypsum_col = lerp3(np.array([0.46, 0.41, 0.32]), np.array([0.59, 0.53, 0.42]), n_med * 0.6 + n_fine * 0.4)
    gypsum_col *= (1.0 - 0.14 * inner_niche[..., None] - 0.08 * niche[..., None])
    alb[m] = gypsum_col[m]
    hgt[m] = (relief_z + 0.003 * n_fine)[m]
    rgh[m] = (0.82 + 0.08 * n_fine)[m]

    # 5C: Lapislazuli-Glasurziegel-Fries mit goldenen Rosetten (U 0.666..1.000)
    m = m_b5 & (uu >= 0.666)
    ul = (uu - 0.666) / (1.000 - 0.666)
    # Ziegelraster im Lapislazuli-Feld
    lz_u = (ul * 12.0 + (np.floor(vl5 * 6.0) % 2) * 0.5) % 1.0
    lz_v = (vl5 * 6.0) % 1.0
    lz_brick = smoothstep(0.03, 0.09, lz_u) * (1.0 - smoothstep(0.91, 0.97, lz_u)) \
             * smoothstep(0.05, 0.13, lz_v) * (1.0 - smoothstep(0.87, 0.95, lz_v))
    # Ocker-Gold-Bordueren oben und unten + 8-blaettrige sumerische Rosetten
    border_band = np.maximum(1.0 - smoothstep(0.14, 0.19, vl5), smoothstep(0.81, 0.86, vl5))
    ros_u = ((ul * 4.0) % 1.0) - 0.5
    ros_v = (vl5 - 0.5) * 1.45
    ros_r = np.sqrt(ros_u * ros_u + ros_v * ros_v)
    ros_a = np.arctan2(ros_v, ros_u)
    petal_r = 0.24 + 0.08 * np.cos(ros_a * 8.0)
    rosette = (1.0 - smoothstep(petal_r - 0.04, petal_r + 0.02, ros_r)) * (1.0 - border_band)
    ros_core = 1.0 - smoothstep(0.07, 0.11, ros_r)

    lapis_blue = lerp3(np.array([0.065, 0.13, 0.36]), np.array([0.11, 0.23, 0.56]), lz_brick * 0.7 + n_fine * 0.3)
    gold_ochre = np.array([0.58, 0.42, 0.14])
    cream_glaze = np.array([0.62, 0.56, 0.44])
    lapis_col = lerp3(lapis_blue, cream_glaze, rosette * 0.90)
    lapis_col = lerp3(lapis_col, gold_ochre, np.maximum(border_band * 0.88, ros_core))

    alb[m] = lapis_col[m]
    hgt[m] = (0.012 * lz_brick + 0.010 * rosette + 0.012 * border_band + 0.008 * ros_core)[m]
    rgh[m] = (0.34 - 0.06 * lz_brick + 0.08 * (1.0 - lz_brick))[m]

    # Strikter HDR-Albedo-Clamp [0.06 .. 0.72]
    alb = np.clip(alb, 0.06, 0.72)
    rgh = np.clip(rgh, 0.20, 0.96)
    met = np.clip(met, 0.0, 1.0)

    print(
        f"[TRIM ATLAS] Felder fertig | Albedo=[{alb.min():.3f}..{alb.max():.3f}] | "
        f"Hgt=[{hgt.min():.3f}..{hgt.max():.3f}]m | Rgh=[{rgh.min():.2f}..{rgh.max():.2f}]",
        flush=True,
    )
    return alb, hgt, rgh, met


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
    """
    Erzeugt eine hochaufloesende 3D-Relief-Flaeche (X in [-2*apron_u .. 2+2*apron_u], Y in [0..1])
    mit nahtlosem U-Wrap-Around fuer kantenfreien Cycles-AO- und Normal-Bake.
    """
    print(f"[TRIM ATLAS] Baue 3D High-Poly Relief-Mesh ({nu}x{nv} + U-Schuerze)...", flush=True)
    h_src, w_src = hgt.shape

    u_vals = np.linspace(-apron_u, 1.0 + apron_u, nu + 1, dtype=np.float32)
    v_vals = np.linspace(0.0, 1.0, nv + 1, dtype=np.float32)
    uu, vv = np.meshgrid(u_vals, v_vals, indexing="xy")

    # Periodisches Sampling in U, clamped in V
    px = np.mod(uu, 1.0) * (w_src - 1)
    py = np.clip(vv, 0.0, 1.0) * (h_src - 1)
    ix = np.round(px).astype(np.int64) % w_src
    iy = np.clip(np.round(py).astype(np.int64), 0, h_src - 1)
    zz = hgt[iy, ix]

    xg = uu * 2.0  # Breite 2.0 m fuer 2048x1024 (2:1)
    yg = vv * 1.0  # Hoehe 1.0 m

    mesh = bpy.data.meshes.new("TrimHighPoly")
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

    obj = bpy.data.objects.new("TrimHighPoly", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def _build_target_plane():
    mesh = bpy.data.meshes.new("TrimTargetPlane")
    verts = [(0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (2.0, 1.0, 0.0), (0.0, 1.0, 0.0)]
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    uv_layer = mesh.uv_layers.new(name="UVMap")
    for loop, uv in zip(mesh.loops, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]):
        loop_uv = uv_layer.data[loop.index]
        loop_uv.uv = uv
    obj = bpy.data.objects.new("TrimTargetPlane", mesh)
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


def bake_city_trim_atlas():
    t0 = time.time()
    root = get_project_root()
    tex_dir = os.path.join(root, "assets", "textures")
    os.makedirs(tex_dir, exist_ok=True)

    scene = clear_scene()
    dev_label = setup_cycles(scene, samples=4, use_oidn=False)
    print(f"[TRIM ATLAS] Start | Cycles Device: {dev_label}", flush=True)

    alb, hgt, rgh, met = build_trim_buffers(TEX_W, TEX_H)
    hi_obj = _build_relief_mesh(hgt, nu=960, nv=480, apron_u=0.06)
    lo_obj = _build_target_plane()

    # High-Poly Material mit Mikro-Bump aus dem Hoehenfeld
    hi_mat = bpy.data.materials.new("TrimHiMat")
    hi_mat.use_nodes = True
    nt_h = hi_mat.node_tree
    nt_h.nodes.clear()
    out_h = nt_h.nodes.new("ShaderNodeOutputMaterial")
    bsdf_h = nt_h.nodes.new("ShaderNodeBsdfPrincipled")
    nt_h.links.new(bsdf_h.outputs["BSDF"], out_h.inputs["Surface"])

    # Zusaetzlicher hochfrequenter Mikro-Bump im Shader fuer 2048x1024 Knackschaerfe
    img_h = _arr_to_blender_image("TmpHgt2K", np.repeat(hgt[..., None], 3, axis=-1), "Non-Color")
    tex_h = nt_h.nodes.new("ShaderNodeTexImage")
    tex_h.image = img_h
    tex_h.extension = "REPEAT"
    bump = nt_h.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.22
    bump.inputs["Distance"].default_value = 0.012
    nt_h.links.new(tex_h.outputs["Color"], bump.inputs["Height"])
    nt_h.links.new(bump.outputs["Normal"], bsdf_h.inputs["Normal"])
    hi_obj.data.materials.append(hi_mat)

    # Low-Poly Bake-Ziel
    lo_mat = bpy.data.materials.new("TrimLoMat")
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

    print("[TRIM ATLAS] Bake Normal-Map (4 Samples, Tangent-Space)...", flush=True)
    scene.cycles.samples = 4
    scene.cycles.use_denoising = False
    bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")

    print("[TRIM ATLAS] Bake Ambient Occlusion (16 Samples + OIDN)...", flush=True)
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

    # ORM packen: R = AO, G = Roughness, B = Metallic
    orm_rgb = np.stack([ao_r, rgh, met], axis=-1)

    p_col = os.path.join(tex_dir, "city_trim_atlas_baseColor.png")
    p_nrm = os.path.join(tex_dir, "city_trim_atlas_normal.png")
    p_orm = os.path.join(tex_dir, "city_trim_atlas_orm.png")

    save_np_png(alb, p_col, is_srgb=True)
    save_np_png(nrm_rgb, p_nrm, is_srgb=False)
    save_np_png(orm_rgb, p_orm, is_srgb=False)

    # Naht-Check entlang U=0 / U=1 fuer kachelnde Baender (V < 0.694)
    k_h = int(0.68 * TEX_H)
    seam_alb = float(np.mean(np.abs(alb[:k_h, 0, :] - alb[:k_h, -1, :])))
    seam_nrm = float(np.mean(np.abs(nrm_rgb[:k_h, 0, :] - nrm_rgb[:k_h, -1, :])))
    dt = time.time() - t0
    print(
        f"[TRIM ATLAS] FERTIG in {dt:.2f}s ({dev_label}) | Albedo=[{alb.min():.3f}..{alb.max():.3f}] | "
        f"AO=[{ao_r.min():.2f}..{ao_r.max():.2f}] | U-Seam(Alb={seam_alb:.4f}, Nrm={seam_nrm:.4f})",
        flush=True,
    )
    print(f"  -> {p_col}", flush=True)
    print(f"  -> {p_nrm}", flush=True)
    print(f"  -> {p_orm}", flush=True)
    return p_col, p_nrm, p_orm


if __name__ == "__main__":
    bake_city_trim_atlas()
