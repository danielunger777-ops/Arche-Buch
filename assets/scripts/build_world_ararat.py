"""
build_world_ararat.py — Blender-Master-Welt B: Ararat-Hochgebirgsmassiv (3.000 x 3.000 m)
==========================================================================================
Erzeugt:
  - assets/blend/worlds/ararat_world_master.blend   (komplette, editierbare Ararat-Welt)
  - assets/worlds/ararat_terrain.glb                (reines Gebirgs-Terrain + Schmelzwasser/Wasserfaelle)
  - assets/worlds/ararat_heightmap.png & .json      (512x512 16-Bit Hoehenkarte fuer Physik & Kamera)
  - assets/worlds/ararat_splatmap.png               (2048x2048 Fels-/Schotter-/Schnee-/Moos-Splatmap)
  - assets/worlds/ararat_layout.json                (alle platzierten Instanzen mit Transform & Tint)
  - assets/previews/world_ararat_summit.png

Aufruf:
  blender --background --python-exit-code 1 --python assets/scripts/build_world_ararat.py
"""

import os
import sys
import json
import math
import time
import random
import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import world_builder_utils as wbu  # noqa: E402


WORLD_SIZE = 3000.0
HALF_SPAN = 1500.0
TERRAIN_GRID_N = 400   # 400x400 = 320.000 Tris fuer scharfe Grate, Schluchten & Felskanzel
HEIGHTMAP_RES = 512
SPLATMAP_RES = 2048

POOL_ANCHORS = [
    (-35.0, -26.5, 5.2),
    ( 22.0, -25.0, 4.8),
    (-38.0,  42.0, 5.4),
    (-54.0, -68.0, 5.8),
    ( 52.0, -64.0, 5.6),
]


def _sm_np(a, b, v):
    t = np.clip((v - a) / np.maximum(1e-6, (b - a)), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def _hash2_np(ix, iy, seed=0):
    """Vektorisierter deterministischer 2D-Hash -> [0, 1)."""
    n = (ix.astype(np.int64) * 374761393 + iy.astype(np.int64) * 668265263 + int(seed) * 1442695041) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0x00FFFFFF).astype(np.float64) / 16777216.0


def _vnoise2d_np(x, y, seed=0):
    """Glattes 2D-Value-Noise in [-1, 1]."""
    ix = np.floor(x).astype(np.int64)
    iy = np.floor(y).astype(np.int64)
    fx = x - ix
    fy = y - iy
    ux = fx * fx * (3.0 - 2.0 * fx)
    uy = fy * fy * (3.0 - 2.0 * fy)
    v00 = _hash2_np(ix, iy, seed)
    v10 = _hash2_np(ix + 1, iy, seed)
    v01 = _hash2_np(ix, iy + 1, seed)
    v11 = _hash2_np(ix + 1, iy + 1, seed)
    vx0 = v00 + (v10 - v00) * ux
    vx1 = v01 + (v11 - v01) * ux
    return (vx0 + (vx1 - vx0) * uy) * 2.0 - 1.0


def _fbm2d_np(x, y, octaves=4, lacunarity=2.05, gain=0.5, seed=11):
    val = np.zeros_like(x, dtype=np.float64)
    amp = 0.5
    px, py = x, y
    for oi in range(octaves):
        val += amp * _vnoise2d_np(px, py, seed + oi * 37)
        # Leichte Rotation pro Oktave gegen Achsen-Artefakte
        px_n = (px * 0.8 - py * 0.6) * lacunarity
        py_n = (px * 0.6 + py * 0.8) * lacunarity
        px, py = px_n, py_n
        amp *= gain
    return val


def _ridged_mf_np(x, y, octaves=4, lacunarity=2.12, gain=0.52, seed=101):
    """Scharfes Ridged-Multifractal-Noise in [0, ~1.5] fuer zerklueftete Vulkan-Grate."""
    total = np.zeros_like(x, dtype=np.float64)
    weight = np.ones_like(x, dtype=np.float64)
    amp = 0.55
    px, py = x, y
    for oi in range(octaves):
        n = 1.0 - np.abs(_vnoise2d_np(px, py, seed + oi * 53))
        n = n * n * weight
        weight = np.clip(n * 1.85, 0.0, 1.0)
        total += n * amp
        px_n = (px * 0.8 - py * 0.6) * lacunarity
        py_n = (px * 0.6 + py * 0.8) * lacunarity
        px, py = px_n, py_n
        amp *= gain
    return total


def _voronoi_cliff_np(x, y, scale=0.02, seed=307):
    """Vektorisiertes 2D-Voronoi (F1, F2-F1) fuer kantige Basalt-Klippen & Bruchlinien."""
    sx = x * scale
    sy = y * scale
    ix = np.floor(sx).astype(np.int64)
    iy = np.floor(sy).astype(np.int64)
    fx = sx - ix
    fy = sy - iy
    f1 = np.full_like(sx, 99.0, dtype=np.float64)
    f2 = np.full_like(sx, 99.0, dtype=np.float64)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            cx = ix + dx
            cy = iy + dy
            ox = dx + 0.15 + 0.70 * _hash2_np(cx, cy, seed)
            oy = dy + 0.15 + 0.70 * _hash2_np(cx, cy, seed + 911)
            d = np.hypot(ox - fx, oy - fy)
            m1 = d < f1
            f2 = np.where(m1, f1, np.minimum(f2, d))
            f1 = np.where(m1, d, f1)
    return f1, np.maximum(0.0, f2 - f1)


def eval_gorge_center_x_np(side, y):
    """Organisch geschwungene Mittellinie der westlichen & oestlichen Wasserfall-Schlucht."""
    if side == "W":
        return -114.0 + 9.5 * np.sin(y * 0.028) + 4.5 * np.cos(y * 0.062) - 5.0 * _sm_np(30.0, -110.0, y)
    return 124.0 - 9.0 * np.sin(y * 0.026 + 0.8) - 4.0 * np.cos(y * 0.058) + 5.0 * _sm_np(30.0, -110.0, y)


def eval_ararat_core_np(x, y):
    """Schroffes Vulkan-Basaltmassiv mit Ridged-Multifractal, Voronoi-Klippen, Lavabaenken, Talus & Felskanzel."""
    crown_z = 0.045 * np.cos((np.minimum(70.0, np.abs(x)) / 70.0) * math.pi * 0.85)

    south_blend = _sm_np(-16.0, -165.0, y)
    far_south = _sm_np(-90.0, -430.0, y)
    x_wing_drop = np.power(_sm_np(68.0, 380.0, np.abs(x)), 1.55) * 14.0
    valley_floor_z = (
        -42.0 * south_blend
        - 12.0 * far_south
        - x_wing_drop * (0.45 + 0.55 * south_blend)
        + (2.4 * _fbm2d_np(x * 0.014, y * 0.014, octaves=3, seed=21)) * (0.25 + 0.75 * south_blend)
    )

    lat_west_peak = 116.0 * np.exp(-np.power(np.hypot((x + 315.0) / 150.0, (y - 38.0) / 140.0), 1.65))
    lat_east_peak = 110.0 * np.exp(-np.power(np.hypot((x - 328.0) / 150.0, (y - 28.0) / 140.0), 1.65))
    sw_shoulder = 78.0 * np.exp(-np.power(np.hypot((x + 425.0) / 170.0, (y + 135.0) / 160.0), 1.65))
    se_shoulder = 74.0 * np.exp(-np.power(np.hypot((x - 435.0) / 170.0, (y + 145.0) / 160.0), 1.65))

    north_weight = _sm_np(-20.0, 195.0, y)
    d_big = np.hypot(x + 95.0, y - 280.0)
    ang_big = np.arctan2(y - 280.0, x + 95.0)
    rib_big_fade = 1.0 - np.exp(-d_big / 32.0)
    h_big_caldera = 16.0 * np.exp(-((d_big / 25.0) ** 2))
    # Scharfe vulkanische Grate statt weicher Knet-Glocke
    h_big_base = 302.0 * np.exp(-np.power(d_big / 218.0, 1.52)) * (
        1.0 + (0.13 * np.abs(np.sin(ang_big * 3.0 + d_big * 0.011)) - 0.05) * rib_big_fade
    ) - h_big_caldera

    d_small = np.hypot(x - 155.0, y - 250.0)
    ang_small = np.arctan2(y - 250.0, x - 155.0)
    rib_small_fade = 1.0 - np.exp(-d_small / 28.0)
    h_small_base = 222.0 * np.exp(-np.power(d_small / 164.0, 1.54)) * (
        1.0 + (0.12 * np.abs(np.cos(ang_small * 3.5 - d_small * 0.013)) - 0.04) * rib_small_fade
    )

    pass_ridge = 50.0 * np.exp(-((y - 265.0) / 115.0) ** 2) * np.exp(-((x / 340.0) ** 2))
    north_rim_spur = (
        98.0 * np.exp(-np.power(np.hypot(x + 345.0, y - 215.0) / 140.0, 1.6))
        + 92.0 * np.exp(-np.power(np.hypot(x - 360.0, y - 200.0) / 140.0, 1.6))
    )

    # Mehrstufiges Ridged-Multifractal & Voronoi-Klippen-Displacement
    ridged_macro = _ridged_mf_np(x * 0.0085, y * 0.0085, octaves=4, seed=101)
    ridged_meso = _ridged_mf_np(x * 0.026, y * 0.026, octaves=3, seed=211)
    vor_f1, vor_edge = _voronoi_cliff_np(x, y, scale=0.019, seed=307)
    vor_fine_f1, vor_fine_edge = _voronoi_cliff_np(x, y, scale=0.048, seed=409)

    mtn_mask = _sm_np(8.0, 95.0, h_big_base + h_small_base + lat_west_peak + lat_east_peak + north_rim_spur)
    # Scharfe Grate und kantige Klippenbruchkanten
    ridge_disp = (
        (ridged_macro - 0.48) * 44.0
        + (ridged_meso - 0.42) * 13.5
        + (0.42 - np.minimum(vor_f1, 0.85)) * 18.0
        + (np.minimum(vor_edge, 0.28) - 0.14) * 26.0
        + (0.35 - np.minimum(vor_fine_f1, 0.7)) * 5.2
    ) * (0.20 + 0.80 * mtn_mask) * north_weight

    # Auch auf Schultern & Suedhaengen schroffe Basaltrippen
    shoulder_crags = (
        (ridged_meso - 0.45) * 9.5 + (0.38 - np.minimum(vor_fine_f1, 0.75)) * 4.5
    ) * (1.0 - north_weight * 0.6) * _sm_np(18.0, 85.0, np.hypot(x, y))

    z_mtn_raw = (h_big_base + h_small_base + pass_ridge + north_rim_spur) * north_weight + ridge_disp

    # Horizontale Basalt-Lavabaenke / Felsstufen an Steilhaengen
    strata_warp = _fbm2d_np(x * 0.011, y * 0.011, octaves=2, seed=73) * 4.2
    strata_phase = (z_mtn_raw + strata_warp) * 0.24
    lava_benches = (np.sin(strata_phase) + 0.38 * np.sin(strata_phase * 2.0)) * 2.6 * mtn_mask * north_weight

    # Schuttkegel (Talus) am Fuss der Steilwaende (y ~ 18..90)
    talus_band = np.exp(-(((y - 48.0) / 36.0) ** 2)) * _sm_np(55.0, 150.0, np.abs(x))
    talus_fans = (0.5 + 0.5 * _ridged_mf_np(x * 0.032, y * 0.014, octaves=2, seed=503)) * 8.5 * talus_band

    # Eingekerbte Wasserfall-Felsrinnen / Schluchten mit gestuften Kaskaden
    cx_gorge_w = eval_gorge_center_x_np("W", y)
    cx_gorge_e = eval_gorge_center_x_np("E", y)
    gorge_along = _sm_np(-120.0, -35.0, y) * (1.0 - _sm_np(130.0, 210.0, y))
    dw = np.abs(x - cx_gorge_w)
    de = np.abs(x - cx_gorge_e)
    # Aeusserer Canyon + scharfe innere Kerbschlucht
    gorge_west = (13.0 * np.exp(-((dw / 17.0) ** 2)) + 14.5 * np.exp(-((dw / 5.8) ** 2))) * gorge_along
    gorge_east = (12.5 * np.exp(-((de / 17.0) ** 2)) + 14.0 * np.exp(-((de / 5.8) ** 2))) * gorge_along
    # Gestufte Fels-Kaskaden in den Schluchten
    cascade_steps_w = 2.6 * np.sin(y * 0.22) * np.exp(-((dw / 6.5) ** 2)) * gorge_along
    cascade_steps_e = 2.6 * np.sin(y * 0.22 + 0.9) * np.exp(-((de / 6.5) ** 2)) * gorge_along

    pool_bowls = 4.6 * (
        np.exp(-(((x + 120.5) ** 2 + (y + 46.0) ** 2) / (18.0 ** 2)))
        + np.exp(-(((x - 130.5) ** 2 + (y + 44.0) ** 2) / (18.0 ** 2)))
    )

    macro_z = (
        valley_floor_z
        + lat_west_peak
        + lat_east_peak
        + sw_shoulder
        + se_shoulder
        + z_mtn_raw
        + lava_benches
        + talus_fans
        + shoulder_crags
        - gorge_west
        - gorge_east
        + cascade_steps_w
        + cascade_steps_e
        - pool_bowls
    )

    # Exakt ebener 220-Ellen-Kielsattel (140 x 23.3 m Rumpfauflage: |x|<=71, |y|<=12.2)
    dx_keel = np.maximum(0.0, np.abs(x) - 71.0)
    dy_keel = np.maximum(0.0, np.abs(y) - 12.2)
    d_keel_norm = np.hypot(dx_keel / 34.0, dy_keel / 22.0)
    w_keel = np.exp(-np.power(d_keel_norm, 2.4))
    z_out = macro_z * (1.0 - w_keel) + crown_z * w_keel

    # Natuerliche, gestufte Basalt-Felskanzel vor dem Seitentor (Altar + Lager auf Z = +4.18 m)
    dx_plat = np.where(x < -21.0, -21.0 - x, np.where(x > 2.5, x - 2.5, 0.0))
    dy_plat = np.where(y < -28.0, -28.0 - y, np.where(y > -19.5, y + 19.5, 0.0))
    # Kantige Fels-Verzerrung statt rundem Huegel
    kanzel_warp = _fbm2d_np(x * 0.085, y * 0.085, octaves=3, seed=613) * 3.8
    d_plat = np.maximum(np.abs(dx_plat) * 0.85, np.abs(dy_plat) * 1.10) + 0.35 * np.hypot(dx_plat, dy_plat) + kanzel_warp
    # 3 gestufte Basalt-Felsbaenke vom Plateau (0 m) bis Kanzel-Krone (4.18 m)
    u_k = np.clip(1.0 - np.maximum(0.0, d_plat) / 14.5, 0.0, 1.0)
    step1 = _sm_np(0.06, 0.24, u_k) * 0.34
    step2 = _sm_np(0.36, 0.54, u_k) * 0.33
    step3 = _sm_np(0.68, 0.86, u_k) * 0.33
    w_terr = (step1 + step2 + step3) * _sm_np(12.5, 17.5, -y)
    # Zusaetzliche Felsriff-Stufe an den Kanzelraendern (nicht auf der ebenen Altarflaeche)
    kanzel_rim_crag = (0.5 + 0.5 * _ridged_mf_np(x * 0.14, y * 0.14, octaves=2, seed=719)) * 0.85 * _sm_np(0.1, 0.45, u_k) * (1.0 - _sm_np(0.70, 0.92, u_k))
    z_final = z_out * (1.0 - w_terr) + 4.18 * w_terr + kanzel_rim_crag

    # Saubere eingetiefte Schmelzwasser-Becken (NACH Terrasse/Kielsattel -> 0% schwebende Wasserkanten!)
    for px, py, pr in POOL_ANCHORS:
        dp = np.hypot(x - px, y - py)
        basin = np.exp(-np.power(dp / (pr * 1.15), 2.8))
        z_final -= 1.65 * basin
    return z_final


def eval_ararat_z_np(x_in, y_in):
    """Volles 3000x3000 m Ararat-Hochgebirgsrelief inkl. ferner Bergketten & Suedtal-Auslauf."""
    x = np.asarray(x_in, dtype=np.float64)
    y = np.asarray(y_in, dtype=np.float64)

    cx_edge = np.clip(x, -699.0, 699.0)
    cy_edge = np.clip(y, -699.0, 699.0)
    z_core = eval_ararat_core_np(cx_edge, cy_edge)

    # Uebergang jenseits +-699 m bis +-1500 m zu alpinen Nachbarketten
    d_box = np.maximum(np.abs(x) - 640.0, np.abs(y) - 640.0)
    u_far = np.clip(d_box / 860.0, 0.0, 1.0)
    sm_far = u_far * u_far * (3.0 - 2.0 * u_far)

    north_alp = np.clip((y + 420.0) / 2200.0, 0.0, 1.0)
    ridge_far = _ridged_mf_np(x * 0.0022, y * 0.0022, octaves=3, seed=809)
    crag_far = 22.0 * (_ridged_mf_np(x * 0.0065, y * 0.0065, octaves=2, seed=821) - 0.35)
    valley_s = -56.0 * (1.0 - north_alp) * (1.0 - 0.55 * u_far)
    alpine_chains = (28.0 + 225.0 * north_alp) * np.power(np.clip(u_far + 0.12, 0.0, 1.0), 1.05) * (0.35 + 0.65 * ridge_far)
    far_rim = 58.0 * np.power(u_far, 1.35) * (0.45 + 0.55 * ridge_far)
    z_far = valley_s + alpine_chains + far_rim + crag_far * sm_far

    in_core = np.maximum(np.abs(x), np.abs(y)) <= 640.0
    return np.where(in_core, z_core, z_core * (1.0 - sm_far) + z_far * sm_far)


def eval_ara_z(x, y):
    return float(eval_ararat_z_np(np.array([x]), np.array([y]))[0])


# ==============================================================================
# 1. HEIGHTMAP (512x512) & SPLATMAP (2048x2048)
# ==============================================================================

def build_ararat_heightmap_and_splatmap():
    t0 = time.time()
    print("[1/5] Berechne 512x512 Heightmap & 2048x2048 Splatmap (Ararat)...", flush=True)

    xs_h = np.linspace(-HALF_SPAN, HALF_SPAN, HEIGHTMAP_RES, dtype=np.float64)
    ys_h = np.linspace(HALF_SPAN, -HALF_SPAN, HEIGHTMAP_RES, dtype=np.float64)
    gx_h, gy_h = np.meshgrid(xs_h, ys_h)
    z_h = eval_ararat_z_np(gx_h, gy_h)
    z_min = float(np.min(z_h))
    z_max = float(np.max(z_h))
    z_span = max(1e-4, z_max - z_min)
    z_u16 = np.clip(np.round(((z_h - z_min) / z_span) * 65535.0), 0, 65535).astype(np.uint16)

    hm_png = os.path.join(wbu.WORLDS_OUT_DIR, "ararat_heightmap.png")
    hm_json = os.path.join(wbu.WORLDS_OUT_DIR, "ararat_heightmap.json")
    wbu.write_png_uint16_gray(hm_png, z_u16)
    with open(hm_json, "w", encoding="utf-8") as f:
        json.dump({
            "scene": "ararat",
            "width": HEIGHTMAP_RES,
            "height": HEIGHTMAP_RES,
            "worldSizeMeters": WORLD_SIZE,
            "halfSpanMeters": HALF_SPAN,
            "xMin": -HALF_SPAN,
            "xMax": HALF_SPAN,
            "yMin": -HALF_SPAN,
            "yMax": HALF_SPAN,
            "zMin": round(z_min, 4),
            "zMax": round(z_max, 4),
            "encoding": "uint16_grayscale_top_to_bottom_y_plus_to_minus",
            "formula": "z = zMin + (pixel_u16 / 65535.0) * (zMax - zMin)",
        }, f, indent=2)

    # 2048x2048 Splatmap:
    #   Base = Vulkanischer Schotter/Basaltkies (Scree)
    #   R    = Steile tektonische Basaltfelsen & Schluchtwaende
    #   G    = Sparsames Pioniermoos & Berggras (um Schmelzwassertuempel & tiefe Talmulden)
    #   B    = Hochalpiner Gletscherschnee & Firn (ab ~58..110 m auf maessigen Haengen)
    xs_s = np.linspace(-HALF_SPAN, HALF_SPAN, SPLATMAP_RES, dtype=np.float64)
    ys_s = np.linspace(HALF_SPAN, -HALF_SPAN, SPLATMAP_RES, dtype=np.float64)
    gx, gy = np.meshgrid(xs_s, ys_s)
    gz = eval_ararat_z_np(gx, gy)

    dz_dx = np.gradient(gz, WORLD_SIZE / (SPLATMAP_RES - 1), axis=1)
    dz_dy = np.gradient(gz, WORLD_SIZE / (SPLATMAP_RES - 1), axis=0)
    slope = np.hypot(dz_dx, dz_dy)

    # Konkavitaet (Mulden & Rinnen sammeln Schnee; exponierte Grate bleiben nackter Basaltfels)
    gz_pad = np.pad(gz, 4, mode="edge")
    gz_avg = (
        gz_pad[0:-8, 4:-4] + gz_pad[8:, 4:-4] + gz_pad[4:-4, 0:-8] + gz_pad[4:-4, 8:]
    ) * 0.25
    concavity = np.clip((gz_avg - gz) * 0.35, -1.0, 1.0)

    n_mac = _fbm2d_np(gx * 0.018, gy * 0.018, octaves=3, seed=901)
    n_det = _fbm2d_np(gx * 0.075, gy * 0.075, octaves=2, seed=919)

    # Wasserfall-Schluchten: nasser dunkler Basalt ohne Schnee
    cx_gw = eval_gorge_center_x_np("W", gy)
    cx_ge = eval_gorge_center_x_np("E", gy)
    in_gorge_y = (gy >= -52.0) & (gy <= 145.0)
    in_gorge = in_gorge_y & ((np.abs(gx - cx_gw) < 10.5) | (np.abs(gx - cx_ge) < 10.5))

    # R: Steiler dunkel-schiefergrauer Basaltfels + Schluchtwaende + Kammrippen (> 45° bricht schroff hervor!)
    rock_w = _sm_np(0.32, 0.72, slope + n_mac * 0.08 - concavity * 0.12)
    ridge_rock = _sm_np(14.0, 48.0, gz) * _sm_np(0.22, 0.48, slope)
    r_f = np.clip(np.maximum(rock_w, ridge_rock * 0.90), 0.0, 1.0)
    r_f = np.where(in_gorge, np.maximum(r_f, 0.95), r_f)

    # B: Geologische Hangneigungs-Schneemaske (< 42°-45° Hangneigung in Mulden/Hochlagen, steile Grate > 45° nackter Basalt!)
    snow_line = gz + n_mac * 18.0 + n_det * 7.5 + concavity * 28.0
    snow_alt = _sm_np(72.0, 96.0, snow_line)
    # In Hochlagen-Mulden & Rinnen sammelt sich Firn; steile Felswaende (> 45°) brechen dunkel-anthrazit hervor
    gully_relief = np.maximum(0.0, concavity) * 0.24 + _sm_np(165.0, 250.0, gz) * 0.10
    slope_eff = slope - gully_relief + n_det * 0.04
    snow_slope = 1.0 - _sm_np(0.86, 1.06, slope_eff)
    b_f = np.clip(snow_alt * snow_slope, 0.0, 1.0)
    b_f = np.where(in_gorge, 0.0, b_f)

    # G: Dezentes olivgruenes Pioniermoos um Tuempel, Altar-Felskanzel & tiefe Talmulden
    pool_moist = np.zeros_like(gx)
    for px, py, pr in POOL_ANCHORS:
        dp = np.hypot(gx - px, gy - py)
        pool_moist = np.maximum(pool_moist, np.exp(-((dp / (pr * 2.1)) ** 2)))
    altar_moss = np.exp(-(((gx + 18.0) ** 2 + (gy + 24.0) ** 2) / (11.5 ** 2))) * (0.45 + 0.55 * n_det)
    valley_moss = _sm_np(12.0, -32.0, gz) * (1.0 - _sm_np(0.25, 0.52, slope)) * np.clip(0.32 + 0.68 * n_mac, 0.0, 1.0)
    g_f = np.clip(np.maximum(np.maximum(pool_moist * 0.65, altar_moss * 0.48), valley_moss * 0.50) * (1.0 - b_f) * (1.0 - r_f * 0.78), 0.0, 1.0)

    # Kielsattel: harter Vulkanschotter/Basalt ohne Schnee & Moos
    in_keel = (np.abs(gx) <= 72.0) & (np.abs(gy) <= 13.0)
    b_f = np.where(in_keel, 0.0, b_f)
    g_f = np.where(in_keel, 0.0, g_f)

    tot = r_f + g_f + b_f
    safe_tot = np.where(tot > 1.0, tot, 1.0)
    r_f = r_f / safe_tot
    g_f = g_f / safe_tot
    b_f = b_f / safe_tot

    splat = np.empty((SPLATMAP_RES, SPLATMAP_RES, 4), dtype=np.uint8)
    splat[..., 0] = np.clip(np.round(r_f * 255.0), 0, 255).astype(np.uint8)
    splat[..., 1] = np.clip(np.round(g_f * 255.0), 0, 255).astype(np.uint8)
    splat[..., 2] = np.clip(np.round(b_f * 255.0), 0, 255).astype(np.uint8)
    splat[..., 3] = 255

    splat_png = os.path.join(wbu.WORLDS_OUT_DIR, "ararat_splatmap.png")
    wbu.write_png_rgba8(splat_png, splat)
    print(f"    -> Ararat Heightmap & Splatmap geschrieben in {time.time() - t0:.2f}s (Z=[{z_min:.2f}, {z_max:.2f}])", flush=True)
    return splat_png, hm_png


# ==============================================================================
# 2. TERRAIN- & WASSER-GEOMETRIE + CYCLES-ATLAS-SHADER
# ==============================================================================

def _build_ararat_terrain_material(splat_png_path):
    mat = bpy.data.materials.new("Mat_Ararat_World_Terrain")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord")
    splat_img = bpy.data.images.load(os.path.abspath(splat_png_path))
    splat_img.colorspace_settings.name = "Non-Color"
    n_splat = nt.nodes.new("ShaderNodeTexImage")
    n_splat.image = splat_img
    n_splat.extension = "EXTEND"
    nt.links.new(tc.outputs["UV"], n_splat.inputs["Vector"])

    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(n_splat.outputs["Color"], sep.inputs["Color"])

    alb_img = wbu.load_image_cached("terrain_ararat_atlas_albedo.png", "sRGB")
    nrm_img = wbu.load_image_cached("terrain_ararat_atlas_normal.png", "Non-Color")
    orm_img = wbu.load_image_cached("terrain_ararat_atlas_orm.png", "Non-Color")

    # Anti-Tiling Multi-Scale UV (kombiniert feine 160x & makro 44x gedrehte Samples ueber Noise-Maske!)
    n_break = nt.nodes.new("ShaderNodeTexNoise")
    n_break.inputs["Scale"].default_value = 32.0
    n_break.inputs["Detail"].default_value = 6.0
    nt.links.new(tc.outputs["UV"], n_break.inputs["Vector"])

    def build_tiled_uv(scale_xy, rot_rad=0.0):
        mp = nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (scale_xy, scale_xy, 1.0)
        mp.inputs["Rotation"].default_value = (0.0, 0.0, rot_rad)
        nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])
        vmod = nt.nodes.new("ShaderNodeVectorMath")
        vmod.operation = "MODULO"
        vmod.inputs[1].default_value = (1.0, 1.0, 1.0)
        nt.links.new(mp.outputs["Vector"], vmod.inputs[0])
        vqs = nt.nodes.new("ShaderNodeVectorMath")
        vqs.operation = "MULTIPLY"
        vqs.inputs[1].default_value = (0.46, 0.46, 1.0)
        nt.links.new(vmod.outputs["Vector"], vqs.inputs[0])
        return vqs.outputs["Vector"]

    uv_fine = build_tiled_uv(150.0, 0.0)
    uv_macro = build_tiled_uv(42.0, 0.67)

    def sample_quadrant(off_u, off_v):
        va1 = nt.nodes.new("ShaderNodeVectorMath"); va1.operation = "ADD"; va1.inputs[1].default_value = (off_u, off_v, 0.0)
        nt.links.new(uv_fine, va1.inputs[0])
        va2 = nt.nodes.new("ShaderNodeVectorMath"); va2.operation = "ADD"; va2.inputs[1].default_value = (off_u, off_v, 0.0)
        nt.links.new(uv_macro, va2.inputs[0])

        ta1 = nt.nodes.new("ShaderNodeTexImage"); ta1.image = alb_img
        nt.links.new(va1.outputs["Vector"], ta1.inputs["Vector"])
        ta2 = nt.nodes.new("ShaderNodeTexImage"); ta2.image = alb_img
        nt.links.new(va2.outputs["Vector"], ta2.inputs["Vector"])
        ma = nt.nodes.new("ShaderNodeMix"); ma.data_type = "RGBA"
        nt.links.new(n_break.outputs["Fac"], ma.inputs["Factor"])
        nt.links.new(ta1.outputs["Color"], ma.inputs["A"]); nt.links.new(ta2.outputs["Color"], ma.inputs["B"])

        tn1 = nt.nodes.new("ShaderNodeTexImage"); tn1.image = nrm_img
        nt.links.new(va1.outputs["Vector"], tn1.inputs["Vector"])
        tn2 = nt.nodes.new("ShaderNodeTexImage"); tn2.image = nrm_img
        nt.links.new(va2.outputs["Vector"], tn2.inputs["Vector"])
        mn = nt.nodes.new("ShaderNodeMix"); mn.data_type = "RGBA"
        nt.links.new(n_break.outputs["Fac"], mn.inputs["Factor"])
        nt.links.new(tn1.outputs["Color"], mn.inputs["A"]); nt.links.new(tn2.outputs["Color"], mn.inputs["B"])

        to = nt.nodes.new("ShaderNodeTexImage"); to.image = orm_img
        nt.links.new(va1.outputs["Vector"], to.inputs["Vector"])
        sepo = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(to.outputs["Color"], sepo.inputs["Color"])
        return ma.outputs["Result"], mn.outputs["Result"], sepo.outputs["Green"]

    # TL: Basalt, TR: Scree, BL: Moss, BR: Snow
    alb_scree, nrm_scree, rgh_scree = sample_quadrant(0.52, 0.52)
    alb_basalt_raw, nrm_basalt_raw, rgh_basalt = sample_quadrant(0.02, 0.52)
    # Dunkel-schiefergrauer / anthrazitfarbener Vulkanbasalt fuer harten Kontrast zum Schnee
    mix_rock_c = nt.nodes.new("ShaderNodeMix"); mix_rock_c.data_type = "RGBA"
    mix_rock_c.inputs["Factor"].default_value = 0.42
    nt.links.new(alb_basalt_raw, mix_rock_c.inputs["A"])
    mix_rock_c.inputs["B"].default_value = (0.052, 0.056, 0.064, 1.0)
    alb_basalt = mix_rock_c.outputs["Result"]

    mix_rock_n = nt.nodes.new("ShaderNodeMix"); mix_rock_n.data_type = "RGBA"
    mix_rock_n.inputs["Factor"].default_value = 0.25
    nt.links.new(nrm_scree, mix_rock_n.inputs["A"]); nt.links.new(nrm_basalt_raw, mix_rock_n.inputs["B"])
    nrm_basalt = mix_rock_n.outputs["Result"]

    alb_moss_raw, nrm_moss, rgh_moss = sample_quadrant(0.02, 0.02)
    # Dezentes, erdiges Olivgruen fuer Pioniermoos
    hsv_moss = nt.nodes.new("ShaderNodeHueSaturation")
    hsv_moss.inputs["Saturation"].default_value = 0.72
    hsv_moss.inputs["Value"].default_value = 0.78
    nt.links.new(alb_moss_raw, hsv_moss.inputs["Color"])
    alb_moss = hsv_moss.outputs["Color"]

    alb_snow, nrm_snow, rgh_snow = sample_quadrant(0.52, 0.02)

    def mix_chain(base, lr, lg, lb, is_color=True):
        dt = "RGBA" if is_color else "FLOAT"
        m1 = nt.nodes.new("ShaderNodeMix"); m1.data_type = dt
        nt.links.new(sep.outputs["Red"], m1.inputs["Factor"])
        nt.links.new(base, m1.inputs["A"]); nt.links.new(lr, m1.inputs["B"])

        m2 = nt.nodes.new("ShaderNodeMix"); m2.data_type = dt
        nt.links.new(sep.outputs["Green"], m2.inputs["Factor"])
        nt.links.new(m1.outputs["Result"], m2.inputs["A"]); nt.links.new(lg, m2.inputs["B"])

        m3 = nt.nodes.new("ShaderNodeMix"); m3.data_type = dt
        nt.links.new(sep.outputs["Blue"], m3.inputs["Factor"])
        nt.links.new(m2.outputs["Result"], m3.inputs["A"]); nt.links.new(lb, m3.inputs["B"])
        return m3.outputs["Result"]

    col_out = mix_chain(alb_scree, alb_basalt, alb_moss, alb_snow, True)
    nrm_out = mix_chain(nrm_scree, nrm_basalt, nrm_moss, nrm_snow, True)
    rgh_out = mix_chain(rgh_scree, rgh_basalt, rgh_moss, rgh_snow, False)

    # Geologische Makro-Schichten gegen Uniformitaet an grossen Felswaenden
    geom_w = nt.nodes.new("ShaderNodeNewGeometry")
    n_strata = nt.nodes.new("ShaderNodeTexNoise")
    n_strata.inputs["Scale"].default_value = 0.045
    n_strata.inputs["Detail"].default_value = 8.0
    n_strata.inputs["Roughness"].default_value = 0.65
    nt.links.new(geom_w.outputs["Position"], n_strata.inputs["Vector"])

    mr_str = nt.nodes.new("ShaderNodeMapRange")
    mr_str.inputs["From Min"].default_value = 0.28
    mr_str.inputs["From Max"].default_value = 0.72
    mr_str.inputs["To Min"].default_value = 0.68
    mr_str.inputs["To Max"].default_value = 1.18
    nt.links.new(n_strata.outputs["Fac"], mr_str.inputs["Value"])

    hsv_s = nt.nodes.new("ShaderNodeHueSaturation")
    nt.links.new(mr_str.outputs["Result"], hsv_s.inputs["Value"])
    nt.links.new(col_out, hsv_s.inputs["Color"])

    nrm_map = nt.nodes.new("ShaderNodeNormalMap")
    nrm_map.inputs["Strength"].default_value = 0.72
    nt.links.new(nrm_out, nrm_map.inputs["Color"])

    nt.links.new(hsv_s.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(rgh_out, bsdf.inputs["Roughness"])
    nt.links.new(nrm_map.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def _build_glacial_water_material(name="Mat_Ararat_Meltwater", col=(0.08, 0.28, 0.34), rough=0.05):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (col[0], col[1], col[2], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["IOR"].default_value = 1.333

    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.18, 0.18, 0.18)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])

    tn = nt.nodes.new("ShaderNodeTexImage")
    tn.image = wbu.load_image_cached("water_blender_normal_a.png", "Non-Color")
    nt.links.new(mp.outputs["Vector"], tn.inputs["Vector"])
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nm.inputs["Strength"].default_value = 0.32
    nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def create_ararat_terrain_and_water(col_terrain, splat_png_path):
    t0 = time.time()
    print("[2/5] Erzeuge 3000x3000 m Ararat-Gebirgsmesh & Schmelzwasser-Becken...", flush=True)

    # Center-fokussiertes Gitter fuer scharfen Kielsattel, Altarterrasse & Bergflanken bis +-1500 m
    u1 = np.linspace(-1.0, 1.0, TERRAIN_GRID_N + 1, dtype=np.float64)
    warp1 = np.sign(u1) * (310.0 * np.abs(u1) + 390.0 * (np.abs(u1) ** 2) + 800.0 * (np.abs(u1) ** 5))
    gx, gy = np.meshgrid(warp1, warp1)
    gz = eval_ararat_z_np(gx, gy)

    stride = TERRAIN_GRID_N + 1
    verts = np.column_stack([gx.ravel(), gy.ravel(), gz.ravel()]).tolist()
    ii, jj = np.meshgrid(np.arange(TERRAIN_GRID_N), np.arange(TERRAIN_GRID_N), indexing="xy")
    v00 = (jj * stride + ii).ravel()
    v10 = v00 + 1
    v11 = v00 + stride + 1
    v01 = v00 + stride
    faces_tri1 = np.column_stack([v00, v10, v11])
    faces_tri2 = np.column_stack([v00, v11, v01])
    faces = np.vstack([faces_tri1, faces_tri2]).tolist()

    mesh_terr = bpy.data.meshes.new("Terrain_Ararat_Mesh")
    mesh_terr.from_pydata(verts, [], faces)

    # Flach schattierte Felsfacetten auf steilen Basaltwaenden, glatt auf flachen Boeden/Kielsattel
    dx_q = np.maximum(1e-4, np.abs(gx[:-1, 1:] - gx[:-1, :-1]))
    dy_q = np.maximum(1e-4, np.abs(gy[1:, :-1] - gy[:-1, :-1]))
    sl_x = np.abs(gz[:-1, 1:] - gz[:-1, :-1]) / dx_q
    sl_y = np.abs(gz[1:, :-1] - gz[:-1, :-1]) / dy_q
    is_smooth_q = (np.hypot(sl_x, sl_y) < 0.62).ravel()
    smooth_arr = np.concatenate([is_smooth_q, is_smooth_q]).tolist()
    mesh_terr.polygons.foreach_set("use_smooth", smooth_arr)

    uv_layer = mesh_terr.uv_layers.new(name="UVMap")
    uv_u = ((gx + HALF_SPAN) / WORLD_SIZE).ravel()
    uv_v = ((gy + HALF_SPAN) / WORLD_SIZE).ravel()
    loop_v = np.empty(len(mesh_terr.loops), dtype=np.int64)
    mesh_terr.loops.foreach_get("vertex_index", loop_v)
    uv_arr = np.column_stack([uv_u[loop_v], uv_v[loop_v]]).astype(np.float32)
    uv_layer.data.foreach_set("uv", uv_arr.ravel())

    mat_terr = _build_ararat_terrain_material(splat_png_path)
    mesh_terr.materials.append(mat_terr)
    obj_terr = bpy.data.objects.new("Terrain_Ararat", mesh_terr)
    col_terrain.objects.link(obj_terr)
    terrain_tris = len(mesh_terr.polygons)

    # B) Schmelzwasser-Tuempel (natuerliches, tiefes, leicht spiegelndes Gletscher-Schieferblau)
    mat_pool = _build_glacial_water_material("Mat_Ararat_Meltwater", (0.032, 0.078, 0.105), 0.045)
    bm_w = bmesh.new()
    uv_w = bm_w.loops.layers.uv.new("UVMap")

    def add_pool_disc(cx, cy, rad):
        # Wasserstand strikt unter dem niedrigsten Beckenrand halten (0 % Ueberlaufen/Schweben!)
        rim_zs = []
        for si in range(28):
            ang = (si / 28.0) * math.tau
            rm = rad * (0.88 + 0.16 * math.sin(ang * 3.0 + cx * 0.1))
            rim_zs.append(eval_ara_z(cx + math.cos(ang) * rm * 1.15, cy + math.sin(ang) * rm * 1.25))
        z_floor = eval_ara_z(cx, cy)
        z_water = min(min(rim_zs) - 0.14, z_floor + 0.85)
        z_water = max(z_water, z_floor + 0.25)
        vc = bm_w.verts.new((cx, cy, z_water))
        ring = []
        for si in range(28):
            ang = (si / 28.0) * math.tau
            rm = rad * (0.88 + 0.16 * math.sin(ang * 3.0 + cx * 0.1))
            ring.append(bm_w.verts.new((cx + math.cos(ang) * rm, cy + math.sin(ang) * rm * 1.12, z_water)))
        for si in range(28):
            f = bm_w.faces.new((vc, ring[si], ring[(si + 1) % 28]))
            f.smooth = True
            for lp in f.loops:
                lp[uv_w].uv = (lp.vert.co.x * 0.12, lp.vert.co.y * 0.12)

    for px, py, pr in POOL_ANCHORS:
        add_pool_disc(px, py, pr)
    add_pool_disc(-120.5, -46.0, 9.8)
    add_pool_disc(130.5, -44.0, 9.2)

    # Organischer Wasserfall-Shader: tiefes Schieferwasser + gestufte weisse Schaum-Gischt + weicher Uferrand
    mat_wf = bpy.data.materials.new("Mat_Ararat_Waterfall_Foam")
    mat_wf.use_nodes = True
    nt_wf = mat_wf.node_tree
    nt_wf.nodes.clear()
    out_wf = nt_wf.nodes.new("ShaderNodeOutputMaterial")
    bsdf_wf = nt_wf.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_wf.inputs["Roughness"].default_value = 0.22
    tc_wf = nt_wf.nodes.new("ShaderNodeTexCoord")

    # UV.x = [0..1] quer ueber den Fall, UV.y = Flusslaenge
    sep_wf = nt_wf.nodes.new("ShaderNodeSeparateXYZ")
    nt_wf.links.new(tc_wf.outputs["UV"], sep_wf.inputs["Vector"])

    mp_wf = nt_wf.nodes.new("ShaderNodeMapping")
    mp_wf.inputs["Scale"].default_value = (1.6, 0.18, 1.0)
    nt_wf.links.new(tc_wf.outputs["UV"], mp_wf.inputs["Vector"])
    t_foam = nt_wf.nodes.new("ShaderNodeTexImage")
    t_foam.image = wbu.load_image_cached("water_blender_foam.png", "Non-Color")
    nt_wf.links.new(mp_wf.outputs["Vector"], t_foam.inputs["Vector"])

    # Zusaetzliche Fliess-Streifen ueber gestrecktes Noise + Kaskaden-Gischt
    n_flow = nt_wf.nodes.new("ShaderNodeTexNoise")
    n_flow.inputs["Scale"].default_value = 6.5
    n_flow.inputs["Detail"].default_value = 6.0
    n_flow.inputs["Roughness"].default_value = 0.65
    nt_wf.links.new(mp_wf.outputs["Vector"], n_flow.inputs["Vector"])

    # Vertex-Color R = Kaskaden-Steilheit (mehr Schaum an Steilstufen!)
    vcol_wf = nt_wf.nodes.new("ShaderNodeVertexColor")
    vcol_wf.layer_name = "Col_Cascade"
    add_foam1 = nt_wf.nodes.new("ShaderNodeMath"); add_foam1.operation = "MULTIPLY"
    nt_wf.links.new(t_foam.outputs["Color"], add_foam1.inputs[0])
    nt_wf.links.new(n_flow.outputs["Fac"], add_foam1.inputs[1])
    add_foam2 = nt_wf.nodes.new("ShaderNodeMath"); add_foam2.operation = "ADD"
    nt_wf.links.new(add_foam1.outputs["Value"], add_foam2.inputs[0])
    nt_wf.links.new(vcol_wf.outputs["Color"], add_foam2.inputs[1])

    ramp_foam = nt_wf.nodes.new("ShaderNodeMapRange")
    ramp_foam.inputs["From Min"].default_value = 0.28
    ramp_foam.inputs["From Max"].default_value = 0.85
    ramp_foam.inputs["To Min"].default_value = 0.0
    ramp_foam.inputs["To Max"].default_value = 1.0
    nt_wf.links.new(add_foam2.outputs["Value"], ramp_foam.inputs["Value"])

    mix_wf = nt_wf.nodes.new("ShaderNodeMix")
    mix_wf.data_type = "RGBA"
    mix_wf.inputs["A"].default_value = (0.045, 0.105, 0.135, 1.0)
    mix_wf.inputs["B"].default_value = (0.90, 0.94, 0.97, 1.0)
    nt_wf.links.new(ramp_foam.outputs["Result"], mix_wf.inputs["Factor"])
    nt_wf.links.new(mix_wf.outputs["Result"], bsdf_wf.inputs["Base Color"])

    # Organischer Alpha-Rand ueber UV.x (0 am Rand -> 1 in der Mitte)
    sub_u = nt_wf.nodes.new("ShaderNodeMath"); sub_u.operation = "SUBTRACT"
    sub_u.inputs[1].default_value = 0.5
    nt_wf.links.new(sep_wf.outputs["X"], sub_u.inputs[0])
    abs_u = nt_wf.nodes.new("ShaderNodeMath"); abs_u.operation = "ABSOLUTE"
    nt_wf.links.new(sub_u.outputs["Value"], abs_u.inputs[0])
    edge_fade = nt_wf.nodes.new("ShaderNodeMapRange")
    edge_fade.inputs["From Min"].default_value = 0.22
    edge_fade.inputs["From Max"].default_value = 0.50
    edge_fade.inputs["To Min"].default_value = 0.94
    edge_fade.inputs["To Max"].default_value = 0.08
    nt_wf.links.new(abs_u.outputs["Value"], edge_fade.inputs["Value"])
    nt_wf.links.new(edge_fade.outputs["Result"], bsdf_wf.inputs["Alpha"])
    nt_wf.links.new(bsdf_wf.outputs["BSDF"], out_wf.inputs["Surface"])

    # Zwei breite, gestufte Schlucht-Wasserfaelle tief in den eingekerbten Basalt-Schluchten
    bm_wf = bmesh.new()
    uv_wf = bm_wf.loops.layers.uv.new("UVMap")
    col_wf = bm_wf.loops.layers.color.new("Col_Cascade")
    segs_x = 6
    for side, y0, y1, wf_w in (("W", 126.0, -44.0, 4.6), ("E", 130.0, -42.0, 4.3)):
        segs_y = 84
        rows = []
        z_prev = None
        for i in range(segs_y + 1):
            t = i / segs_y
            cy = y0 + (y1 - y0) * t
            cx = float(eval_gorge_center_x_np(side, np.array([cy]))[0])
            # Organisch verbreitert an Kaskadenstufen & Tosbecken-Auslauf
            cascade_pulse = 0.5 + 0.5 * math.sin(cy * 0.22 + (0.0 if side == "W" else 0.9))
            hw = wf_w * (0.38 + 0.48 * math.sin(t * math.pi * 0.78 + 0.20) + 0.22 * cascade_pulse + 0.42 * (t ** 2.4))
            z_mid = eval_ara_z(cx, cy)
            steep = 0.35 if z_prev is None else min(0.85, max(0.15, abs(z_prev - z_mid) * 0.22))
            z_prev = z_mid
            row_verts = []
            for xi in range(segs_x + 1):
                u = xi / segs_x
                ux = u * 2.0 - 1.0  # -1..+1
                px = cx + ux * hw
                # In der Mitte sauber ueber der Schluchtsohle, Raender tief im Fels verankert
                z_off = 0.68 * (1.0 - ux * ux) - 0.35 * (ux * ux)
                v = bm_wf.verts.new((px, cy, eval_ara_z(px, cy) + z_off))
                row_verts.append((v, u, cy * 0.08, steep + 0.25 * cascade_pulse))
            rows.append(row_verts)
        for i in range(segs_y):
            for c_i in range(segs_x):
                v00, u00, v_y0, st0 = rows[i][c_i]
                v10, u10, _, _ = rows[i][c_i + 1]
                v11, u11, v_y1, st1 = rows[i + 1][c_i + 1]
                v01, u01, _, _ = rows[i + 1][c_i]
                f = bm_wf.faces.new((v00, v10, v11, v01))
                f.smooth = True
                uvs = [(u00, v_y0), (u10, v_y0), (u11, v_y1), (u01, v_y1)]
                sts = [st0, st0, st1, st1]
                for li, lp in enumerate(f.loops):
                    lp[uv_wf].uv = uvs[li]
                    s_val = min(1.0, sts[li])
                    lp[col_wf] = (s_val, s_val, s_val, 1.0)

    bmesh.ops.triangulate(bm_wf, faces=bm_wf.faces[:])
    m_wf = bpy.data.meshes.new("Water_Ararat_Waterfalls_Mesh")
    bm_wf.to_mesh(m_wf)
    bm_wf.free()
    m_wf.materials.append(mat_wf)
    obj_wf = bpy.data.objects.new("Water_Ararat_Waterfalls", m_wf)
    col_terrain.objects.link(obj_wf)

    bmesh.ops.triangulate(bm_w, faces=bm_w.faces[:])
    m_wat = bpy.data.meshes.new("Water_Ararat_Meltwater_Mesh")
    bm_w.to_mesh(m_wat)
    bm_w.free()
    m_wat.materials.append(mat_pool)
    obj_wat = bpy.data.objects.new("Water_Ararat_Meltwater_And_Falls", m_wat)
    col_terrain.objects.link(obj_wat)

    print(f"    -> Ararat Terrain ({terrain_tris:,} Tris) + Schmelzwasser fertig in {time.time() - t0:.2f}s", flush=True)
    return [obj_terr, obj_wat, obj_wf], terrain_tris


# ==============================================================================
# 3. GIPFEL-KOMPOSITION (ALTAR, STEG, LAGER, FELSEN & SCHUETTERER BERGWALD)
# ==============================================================================

def populate_ararat_world(scene):
    t_start = time.time()
    linker = wbu.AssetLinker()
    layout_records = []

    col_terrain = wbu.get_or_create_collection("01_Terrain_And_Water")
    col_ark = wbu.get_or_create_collection("02_Ark_Placeholder")
    col_summit = wbu.get_or_create_collection("03_Summit_Altar_And_Camp")
    col_rocks = wbu.get_or_create_collection("04_Tectonic_Basalt_Boulders")
    col_trees = wbu.get_or_create_collection("05_Alpine_Pioneer_Trees")
    col_flora = wbu.get_or_create_collection("06_Pioneer_Shrubs_And_Grass")
    col_lighting = wbu.get_or_create_collection("07_Lighting_And_Cameras")

    splat_png, _ = build_ararat_heightmap_and_splatmap()
    terrain_export_objs, terrain_tris = create_ararat_terrain_and_water(col_terrain, splat_png)

    # Arche-Platzhalter exakt auf dem 220-Ellen-Kielsattel (Z = +0.04 m)
    wbu.build_ark_placeholder(col_ark, z_sole=0.04)

    print("[3/5] Platziere Zyklopischen Altar, Ausschiffungssteg, Lager & Basaltbloecke...", flush=True)
    SY_BLEND = "world/shipyard_industry_kit.blend"
    ALTAR_BLEND = "world/ararat_altar_cyclopean.blend"

    # Zyklopischer Steinaltar bei (-18.0, -24.0, Z=4.18) -> beide Meshes Altar_Stone_Mesh + Altar_Charcoal_Ember_Mesh!
    altar_z = eval_ara_z(-18.0, -24.0)
    linker.spawn(col_summit, ALTAR_BLEND, "Altar_Stone_Mesh", "ararat_altar_cyclopean",
                 (-18.0, -24.0, altar_z), (0, 0, 0.28), (1.05, 1.05, 1.05), layout_records=layout_records)
    linker.spawn(col_summit, ALTAR_BLEND, "Altar_Charcoal_Ember_Mesh", "ararat_altar_cyclopean_ember",
                 (-18.0, -24.0, altar_z), (0, 0, 0.28), (1.05, 1.05, 1.05), layout_records=None)

    # Buendiger Ausschiffungssteg vom Seitentor (-5.0, -11.67, 6.6) auf die Backbord-Terrasse (-5.0, -23.0, 4.18)
    for rk in range(2):
        ry = -20.2 + rk * 5.60
        rz = 4.18 + rk * 1.18
        linker.spawn(col_summit, SY_BLEND, "sy_ramp_module_LOD0", "sy_ramp_module",
                     (-5.0, ry, rz), (-0.045, 0, 0), (1.15, 1.0, 0.80), layout_records=layout_records)

    # Basislager-Zelte, Vorratskarren & Holzstapel auf der Terrasse (südlich/östlich des Altars)
    for tx, ty, tyaw in ((0.5, -26.5, 0.45), (-9.8, -26.8, -0.30)):
        linker.spawn(col_summit, SY_BLEND, "sy_tent_worker_LOD0", "sy_tent_worker",
                     (tx, ty, eval_ara_z(tx, ty)), (0, 0, tyaw), (0.95, 0.95, 0.95), layout_records=layout_records)
    linker.spawn(col_summit, SY_BLEND, "sy_log_stack_LOD0", "sy_log_stack",
                 (-13.5, -21.2, eval_ara_z(-13.5, -21.2)), (0, 0, 0.15), (0.90, 0.85, 0.85), layout_records=layout_records)
    linker.spawn(col_summit, SY_BLEND, "world_supply_cart_LOD0", "world_supply_cart",
                 (-4.2, -26.4, eval_ara_z(-4.2, -26.4)), (0, 0, 1.25), (1.0, 1.0, 1.0), layout_records=layout_records)

    # Scharfkantige Basalt-Felszinnen (Crags) prozedural erzeugen & um Felskanzel, Plateau & Steilwandfuss verteilen
    rng = random.Random(9941)
    mat_crag = bpy.data.materials.new("Mat_Ararat_Basalt_Crag")
    mat_crag.use_nodes = True
    nt_c = mat_crag.node_tree
    bsdf_c = nt_c.nodes.get("Principled BSDF")
    bsdf_c.inputs["Base Color"].default_value = (0.065, 0.070, 0.078, 1.0)
    bsdf_c.inputs["Roughness"].default_value = 0.88
    n_c = nt_c.nodes.new("ShaderNodeTexNoise")
    n_c.inputs["Scale"].default_value = 4.2
    n_c.inputs["Detail"].default_value = 8.0
    bump_c = nt_c.nodes.new("ShaderNodeBump")
    bump_c.inputs["Strength"].default_value = 0.45
    nt_c.links.new(n_c.outputs["Fac"], bump_c.inputs["Height"])
    nt_c.links.new(bump_c.outputs["Normal"], bsdf_c.inputs["Normal"])

    crag_meshes = []
    for ci in range(3):
        bm_c = bmesh.new()
        bmesh.ops.create_icosphere(bm_c, subdivisions=3, radius=1.0)
        crag_rng = random.Random(7100 + ci * 97)
        for v in bm_c.verts:
            vx, vy, vz = v.co.x, v.co.y, v.co.z
            # Kantige, aufsteigende Basaltsaeule / Felszinne mit gestuften Bruchfacetten
            ang = math.atan2(vy, vx)
            ridge = 0.68 + 0.36 * abs(math.cos(ang * (2.0 + ci) + vz * 1.6)) + 0.14 * math.sin(ang * 5.0 - vz * 2.2)
            taper = max(0.22, 1.18 - 0.62 * max(0.0, vz))
            v.co.x = vx * ridge * taper * crag_rng.uniform(0.86, 1.14)
            v.co.y = vy * ridge * taper * crag_rng.uniform(0.86, 1.14)
            v.co.z = (vz + 0.65) * crag_rng.uniform(1.30, 1.85)
        for f in bm_c.faces:
            f.smooth = False
        m_c = bpy.data.meshes.new(f"Ararat_Basalt_Crag_{ci + 1:02d}_Mesh")
        bm_c.to_mesh(m_c)
        bm_c.free()
        m_c.materials.append(mat_crag)
        crag_meshes.append(m_c)

    # Kuratierte Basalt-Felszinnen rund um die Altar-Felskanzel & Plateau-Raender
    crag_anchors = [
        (-25.5, -24.5, 1.8), (-23.0, -31.5, 2.2), (-15.5, -33.0, 1.6), (4.5, -29.0, 2.0),
        (-31.0, -18.0, 2.4), (11.5, -22.5, 2.1), (-44.0, -34.0, 2.8), (32.0, -32.0, 2.6),
        (-62.0, -28.0, 3.2), (58.0, -26.0, 3.0), (-82.0, 26.0, 4.2), (85.0, 24.0, 4.0),
        (-102.0, -34.0, 3.5), (112.0, -32.0, 3.4), (-138.0, -54.0, 3.8), (146.0, -52.0, 3.6),
    ]
    for idx_c, (cx_r, cy_r, csc) in enumerate(crag_anchors):
        cz_r = eval_ara_z(cx_r, cy_r)
        obj_c = bpy.data.objects.new(f"Basalt_Crag_Hero_{idx_c + 1:02d}", crag_meshes[idx_c % 3])
        obj_c.location = (cx_r, cy_r, cz_r - 0.55 * csc)
        obj_c.rotation_euler = (rng.uniform(-0.14, 0.14), rng.uniform(-0.14, 0.14), rng.uniform(0.0, math.tau))
        obj_c.scale = (csc * rng.uniform(0.9, 1.4), csc * rng.uniform(0.8, 1.3), csc * rng.uniform(1.0, 1.6))
        col_rocks.objects.link(obj_c)

    # Geroellrand um alle Schmelzwasser-Tuempel & Schlucht-Tosbecken
    for px, py, pr in list(POOL_ANCHORS) + [(-120.5, -46.0, 9.8), (130.5, -44.0, 9.2)]:
        rim_cnt = 10 if pr < 7.0 else 16
        for ri in range(rim_cnt):
            ang = (ri / rim_cnt) * math.tau + rng.uniform(-0.15, 0.15)
            rr = pr * rng.uniform(0.98, 1.24)
            rx_p = px + math.cos(ang) * rr
            ry_p = py + math.sin(ang) * rr * 1.12
            rz_p = eval_ara_z(rx_p, ry_p)
            b_key = f"world_boulder_0{(ri % 3) + 1}"
            bsc = rng.uniform(0.45, 1.15)
            linker.spawn(col_rocks, SY_BLEND, f"{b_key}_LOD0", b_key,
                         (rx_p, ry_p, rz_p - 0.22 * bsc),
                         (rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), rng.uniform(0.0, math.tau)),
                         (bsc, bsc * rng.uniform(0.8, 1.2), bsc * rng.uniform(0.55, 0.9)),
                         layout_records=layout_records)

    # Scharfkantige tektonische Basalt-Felsbloecke & Crags ueber Sattelraender, Grate & Schluchten
    boulder_placed = 0
    for bi in range(440):
        if boulder_placed >= 195:
            break
        if bi < 45:
            # Sattelraender, Tuempelufer & Schluchteingaenge
            ang = rng.uniform(0.0, math.tau)
            bx = rng.uniform(18.0, 145.0) * math.cos(ang)
            by = rng.uniform(18.0, 145.0) * math.sin(ang)
        else:
            bx = rng.uniform(-680.0, 680.0)
            by = rng.uniform(-620.0, 480.0)
        if abs(bx) < 76.0 and abs(by) < 16.5:
            continue
        if math.hypot(bx + 18.0, by + 24.0) < 7.5:
            continue
        if abs(bx + 5.0) < 4.5 and -28.0 <= by <= -10.0:
            continue
        bz = eval_ara_z(bx, by)
        if bz > 65.0:
            continue
        sx_b = (eval_ara_z(bx + 2.0, by) - eval_ara_z(bx - 2.0, by)) * 0.25
        sy_b = (eval_ara_z(bx, by + 2.0) - eval_ara_z(bx, by - 2.0)) * 0.25
        if math.hypot(sx_b, sy_b) > 0.48:
            continue
        b_key = f"world_boulder_0{(bi % 3) + 1}"
        lod = "LOD0" if math.hypot(bx, by) < 250.0 else "LOD1"
        bsc = rng.uniform(1.1, 3.6)
        linker.spawn(col_rocks, SY_BLEND, f"{b_key}_{lod}", b_key,
                     (bx, by, bz - 0.35 * bsc),
                     (rng.uniform(-0.18, 0.18), rng.uniform(-0.18, 0.18), rng.uniform(0.0, math.tau)),
                     (bsc, bsc * rng.uniform(0.8, 1.25), bsc * rng.uniform(0.65, 1.15)),
                     layout_records=layout_records)
        boulder_placed += 1

    # 4) SCHUETTERE GEBIRGSBAUM- & PIONIERGRAS-VERTEILUNG BIS ZUM 3000-m-HORIZONT!
    print("[4/5] Platziere spuerbar reduzierten, schuetteren Gebirgsbaum- & Pioniergras-Bewuchs...", flush=True)

    def pick_ararat_pts(count, r_max, z_min, z_max, max_slope):
        pts = []
        tries = 0
        while len(pts) < count and tries < count * 28:
            tries += 1
            rad = (rng.random() ** 0.72) * r_max
            ang = rng.uniform(0.0, math.tau)
            fx = rad * math.cos(ang)
            fy = rad * math.sin(ang) - 60.0
            if abs(fx) < 76.0 and abs(fy) < 16.5:
                continue
            if math.hypot(fx + 18.0, fy + 24.0) < 7.5:
                continue
            if abs(fx + 5.0) < 4.0 and -28.5 <= fy <= -10.0:
                continue
            fz = eval_ara_z(fx, fy)
            if fz < z_min or fz > z_max:
                continue
            sx = (eval_ara_z(fx + 2.5, fy) - eval_ara_z(fx - 2.5, fy)) * 0.2
            sy = (eval_ara_z(fx, fy + 2.5) - eval_ara_z(fx, fy - 2.5)) * 0.2
            if math.hypot(sx, sy) > max_slope:
                continue
            # Wasserflaechen meiden
            if any(math.hypot(fx - px, fy - py) < pr + 0.8 for px, py, pr in POOL_ANCHORS):
                continue
            pts.append((fx, fy, fz))
        return pts

    # Kuratierte schuettere Leitbaeume am Sattel & Hangflanken (viel Fels & Weite sichtbar!)
    hero_ara_trees = [
        (-36.0, -24.0, "olive", "young", 1, 0.82),
        (16.0, -26.0, "olive", "young", 2, 0.84),
        (34.0, -19.0, "olive", "sapling", 1, 0.90),
        (-48.0, -16.0, "cedar", "young", 1, 0.85),
        (44.0, -36.0, "cypress", "young", 2, 0.86),
        (-28.0, 22.0, "cedar", "sapling", 2, 0.82),
        (28.0, 24.0, "cypress", "sapling", 1, 0.84),
    ]
    for hx, hy, sp, st, vi, sc in hero_ara_trees:
        hz = eval_ara_z(hx, hy)
        linker.spawn(col_trees, f"botany/trees_{sp}.blend", f"{sp}_{st}_{vi:02d}_LOD0",
                     f"trees_{sp}:{sp}_{st}_{vi:02d}", (hx, hy, hz),
                     (0, 0, rng.uniform(0.0, math.tau)), (sc, sc, sc), layout_records=layout_records)

    # Bewusst stark reduzierte Gesamtbaumzahl (~210 Baeume ueber volle 3000x3000 m bis zur Baumgrenze Z <= 38 m!)
    tree_batches = [
        ("olive",     "sapling", 45,  550.0, -45.0, 16.0, 0.65, (0.72, 0.98)),
        ("olive",     "young",   35,  720.0, -48.0, 18.0, 0.68, (0.72, 0.96)),
        ("cedar",     "young",   45, 1250.0, -45.0, 38.0, 0.78, (0.68, 0.98)),
        ("cypress",   "young",   40, 1250.0, -52.0, 30.0, 0.76, (0.68, 0.96)),
        ("terebinth", "sapling", 20,  900.0, -55.0, 14.0, 0.65, (0.68, 0.92)),
        ("fig",       "sapling", 15,  900.0, -55.0, 10.0, 0.65, (0.68, 0.92)),
    ]
    for sp, st, cnt, rmax, zmin, zmax, msl, sc_rng in tree_batches:
        pts = pick_ararat_pts(cnt, rmax, zmin, zmax, msl)
        for fx, fy, fz in pts:
            dist = math.hypot(fx, fy)
            lod = "LOD0" if dist < 280.0 else ("LOD1" if dist < 680.0 else "LOD2")
            vi = rng.randint(1, 3 if st == "sapling" else 4)
            sc = rng.uniform(sc_rng[0], sc_rng[1])
            tint = (rng.uniform(0.90, 1.02), rng.uniform(0.94, 1.02), rng.uniform(0.88, 0.98))
            linker.spawn(col_trees, f"botany/trees_{sp}.blend", f"{sp}_{st}_{vi:02d}_{lod}",
                         f"trees_{sp}:{sp}_{st}_{vi:02d}", (fx, fy, fz),
                         (0, 0, rng.uniform(0.0, math.tau)), (sc, sc, sc), tint=tint, layout_records=layout_records)

    # Sparsame Gebirgsstraeucher (Wacholder, Ginster, Dornbusch)
    for ssp in ("juniper", "broom", "thornbush"):
        spts = pick_ararat_pts(40, 820.0, -52.0, 26.0, 0.75)
        for fx, fy, fz in spts:
            sv = rng.randint(1, 12)
            lod = "LOD0" if math.hypot(fx, fy) < 240.0 else "LOD1"
            sc = rng.uniform(0.52, 0.92)
            linker.spawn(col_flora, "botany/shrubs_oriental.blend", f"{ssp}_mature_{sv:02d}_{lod}",
                         f"shrubs_oriental:{ssp}_mature_{sv:02d}", (fx, fy, fz),
                         (0, 0, rng.uniform(0.0, math.tau)), (sc, sc, sc), layout_records=layout_records)

    # Pioniergras-Horste (geclustert um die Schmelzwassertuempel & schuettere Suedhaenge)
    grass_pts = []
    for px, py, pr in POOL_ANCHORS:
        for _ in range(38):
            ang = rng.uniform(0.0, math.tau)
            rr = pr + rng.uniform(0.6, 11.0)
            gx_p, gy_p = px + math.cos(ang) * rr, py + math.sin(ang) * rr
            grass_pts.append((gx_p, gy_p, eval_ara_z(gx_p, gy_p), "euphrates_reed" if rr < pr + 3.2 else "steppe_grass"))
    for fx, fy, fz in pick_ararat_pts(260, 520.0, -45.0, 18.0, 0.68):
        grass_pts.append((fx, fy, fz, "steppe_grass"))

    for fx, fy, fz, gsp in grass_pts:
        gv = rng.randint(1, 14)
        lod = "LOD0" if math.hypot(fx, fy) < 200.0 else "LOD1"
        sc = rng.uniform(0.68, 1.15)
        linker.spawn(col_flora, "botany/grass_and_reeds.blend", f"{gsp}_mature_{gv:02d}_{lod}",
                     f"grass_and_reeds:{gsp}_mature_{gv:02d}", (fx, fy, fz),
                     (0, 0, rng.uniform(0.0, math.tau)), (sc, sc, sc), layout_records=layout_records)

    # 5) LICHT & GIPFEL-KONTROLLKAMERA (3/4-Panorama: Sattel + Altar + Tuempel + Arche + beide schneebedeckten Gipfel & Himmel!)
    sun_obj = wbu.setup_nishita_sky_and_sun(scene, sun_elev_deg=24.0, sun_azim_deg=142.0, sun_energy=3.4, dust_density=0.85, air_density=0.9)
    col_lighting.objects.link(sun_obj)

    cam_summit = wbu.add_camera(col_lighting, "Cam_Ararat_Summit", (-145.0, -235.0, 56.0), (10.0, 40.0, 88.0), lens=19.0)
    scene.camera = cam_summit

    print(f"[5/5] Speichere ararat_world_master.blend, GLB, Layout ({len(layout_records)} Instanzen) & rendere Summit-Preview...", flush=True)

    blend_path = os.path.join(wbu.WORLDS_BLEND_DIR, "ararat_world_master.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    try:
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_mainfile()
    except Exception:
        pass

    layout_path = os.path.join(wbu.WORLDS_OUT_DIR, "ararat_layout.json")
    with open(layout_path, "w", encoding="utf-8") as f:
        json.dump({
            "scene": "ararat",
            "worldSizeMeters": WORLD_SIZE,
            "arkPlaceholder": {"x": 0.0, "y": 0.0, "zSole": 0.04, "dims": [140.0, 23.333, 14.0]},
            "instanceCount": len(layout_records),
            "instances": layout_records,
        }, f)

    # Terrain GLB Export
    terr_obj = terrain_export_objs[0]
    rich_terr_mat = terr_obj.data.materials[0]
    glb_mat = bpy.data.materials.new("Mat_Ararat_Terrain_Export")
    glb_mat.use_nodes = True
    nt_g = glb_mat.node_tree
    bsdf_g = nt_g.nodes.get("Principled BSDF")
    bsdf_g.inputs["Roughness"].default_value = 0.92
    tex_g = nt_g.nodes.new("ShaderNodeTexImage")
    tex_g.image = bpy.data.images.load(os.path.abspath(splat_png))
    nt_g.links.new(tex_g.outputs["Color"], bsdf_g.inputs["Base Color"])
    terr_obj.data.materials[0] = glb_mat

    glb_path = os.path.join(wbu.WORLDS_OUT_DIR, "ararat_terrain.glb")
    wbu.export_selected_objects_glb(terrain_export_objs, glb_path)

    terr_obj.data.materials[0] = rich_terr_mat
    bpy.data.materials.remove(glb_mat)
    bpy.ops.wm.save_mainfile()

    # Cycles CUDA Render
    backend = wbu.setup_cycles(scene, samples=40, use_oidn=True, res_x=1600, res_y=900)
    print(f"    -> Cycles Backend: {backend}", flush=True)
    tr0 = time.time()
    out_png = os.path.join(wbu.PREVIEWS_DIR, "world_ararat_summit.png")
    scene.render.filepath = out_png
    bpy.ops.render.render(write_still=True)
    print(f"    -> Gerendert: {os.path.basename(out_png)} in {time.time() - tr0:.1f}s", flush=True)

    print(
        f"ARARAT_WORLD_DONE instances={len(layout_records)} terrain_tris={terrain_tris} total_s={time.time() - t_start:.1f}",
        flush=True,
    )


def main():
    wbu.ensure_dirs()
    scene = wbu.clear_scene()
    populate_ararat_world(scene)


if __name__ == "__main__":
    main()
