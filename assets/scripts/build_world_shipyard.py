"""
build_world_shipyard.py — Blender-Master-Welt A: Werft, Ur-Schinar & Quellgebirge (3.000 x 3.000 m)
====================================================================================================
Erzeugt:
  - assets/blend/worlds/shipyard_world_master.blend  (komplette, editierbare Welt mit verlinkten Kits)
  - assets/worlds/shipyard_terrain.glb               (reines abgestuftes Terrain-Mesh + Wasserflaechen)
  - assets/worlds/shipyard_heightmap.png & .json     (512x512 16-Bit Hoehenkarte fuer Physik & Kamera)
  - assets/worlds/shipyard_splatmap.png              (2048x2048 Biom-/Wege-/Stadtboden-Splatmap)
  - assets/worlds/shipyard_layout.json               (alle platzierten Instanzen mit Transform & Tint)
  - assets/previews/world_shipyard_aerial.png
  - assets/previews/world_ur_city_streets.png
  - assets/previews/world_aqueduct_valley.png

Aufruf:
  blender --background --python-exit-code 1 --python assets/scripts/build_world_shipyard.py
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
TERRAIN_GRID_N = 400   # 400x400 = 320.000 Tris (scharfe Kanaele & Werftsohle, glatt bis +-1500 m)
HEIGHTMAP_RES = 512
SPLATMAP_RES = 2048


# ==============================================================================
# EXAKTE TOPOGRAFIE (SYNCHRON ZU Arche Simulation 3.0.html + QUELLSCHLUCHT)
# ==============================================================================

SHIPYARD_PLATEAUS = [
    (-42.0, -23.5, 7.4, 11.8, 0.40),
    ( 42.0, -23.5, 7.4, 11.8, 0.75),
    (-42.0,  23.5, 7.4, 11.8, 0.60),
    ( 42.0,  23.5, 7.4, 11.8, 0.95),
    (-68.0, -58.0, 11.5, 18.0, 2.80),
    ( 36.0, -48.0, 10.5, 16.0, 1.75),
    ( 62.0, -36.0, 5.5,  9.5, 1.35),
    ( 78.0, -46.0, 5.5,  9.5, 2.15),
    ( 48.0, -68.0, 5.5,  9.5, 2.50),
    ( 68.0, -64.0, 5.5,  9.5, 2.95),
    ( 12.0, -42.0, 6.5, 10.5, 0.35),
    (-55.0,  36.0, 5.0,  9.0, 1.60),
    (-32.0,  40.0, 5.0,  9.0, 2.10),
    (-10.0,  36.0, 5.0,  9.0, 1.85),
    ( 22.0,  44.0, 6.5, 11.5, 3.40),
    ( 30.0,  54.0, 4.5,  8.5, 4.40),
    ( 86.0,  54.0, 4.5,  8.5, 4.85),
    ( 68.0,  66.0, 4.5,  8.5, 5.30),
    ( 78.0,  82.0, 4.5,  8.5, 6.20),
    (-125.0, -102.0, 14.0, 26.0, 9.20),
    ( 58.0,  92.8, 2.8,  5.8, 17.20),
    (478.0,  55.0, 14.0, 24.0, 2.25),
    (165.0, -315.0, 16.0, 26.0, 1.35),
    (-205.0, -175.0, 16.0, 26.0, 1.35),
    (545.0, -65.0, 16.0, 26.0, 1.40),
    (385.0, -415.0, 16.0, 26.0, 1.35),
]

BARGE_CANAL_PTS = [
    (245.5, -171.0), (210.0, -169.5), (184.0, -171.0), (154.0, -173.0),
    (135.0, -161.0), (120.0, -135.0), (105.0, -108.0), (87.0, -93.0), (73.0, -88.5),
]
SOUTH_CANAL_PTS = [(154.0, -173.0), (136.0, -182.0), (116.0, -185.0), (94.0, -183.0)]
SE_CANAL_PTS = [(259.5, -212.0), (280.0, -212.0), (340.0, -210.0), (395.0, -220.0), (414.0, -234.0), (430.0, -248.0)]
EAST_CANAL_PTS = [(283.5, 38.0), (304.0, 38.0), (370.0, 41.0), (442.0, 40.0), (470.0, 39.0), (505.0, 38.0), (568.0, 24.0), (615.0, 4.0)]
SW_CANAL_PTS = [(-296.0, -238.0), (-282.0, -256.0), (-264.0, -292.0), (-235.0, -352.0), (-200.0, -428.0), (-156.0, -488.0)]
KISURRA_CANAL_PTS = [(184.0, -171.0), (168.0, -212.0), (152.0, -248.0), (136.0, -280.0), (128.0, -295.0)]
ADAB_CANAL_PTS = [(505.0, 38.0), (514.0, 12.0), (522.0, -12.0), (525.0, -25.0)]

ALLUVIAL_LAKES = [
    {"id": "sw_reeds", "cx": -310.0, "cy": -225.0, "rx": 58.0, "ry": 40.0, "yaw": 0.42, "seed": 1.2, "zW": 0.86},
    {"id": "se_lagoon", "cx": 455.0, "cy": -270.0, "rx": 68.0, "ry": 44.0, "yaw": -0.35, "seed": 2.7, "zW": 0.78},
    {"id": "south_oasis", "cx": -165.0, "cy": -505.0, "rx": 60.0, "ry": 38.0, "yaw": 0.25, "seed": 4.1, "zW": 0.78},
    {"id": "ne_highland", "cx": 530.0, "cy": 365.0, "rx": 54.0, "ry": 36.0, "yaw": -0.28, "seed": 5.4, "zW": 3.10},
    {"id": "kisurra_pond", "cx": 128.0, "cy": -295.0, "rx": 28.0, "ry": 20.0, "yaw": 0.30, "seed": 6.3, "zW": 0.80},
    {"id": "umma_pond", "cx": -172.0, "cy": -195.0, "rx": 26.0, "ry": 18.0, "yaw": -0.45, "seed": 7.1, "zW": 0.82},
    {"id": "adab_pond", "cx": 525.0, "cy": -25.0, "rx": 26.0, "ry": 18.0, "yaw": 0.22, "seed": 8.4, "zW": 0.84},
    {"id": "lagash_pond", "cx": 355.0, "cy": -375.0, "rx": 28.0, "ry": 19.0, "yaw": -0.32, "seed": 9.2, "zW": 0.78},
    {"id": "west_clay_pond", "cx": -145.0, "cy": -32.0, "rx": 18.0, "ry": 13.0, "yaw": 0.15, "seed": 3.6, "zW": 1.05},
    {"id": "shipyard_south_pond", "cx": -42.0, "cy": -125.0, "rx": 20.0, "ry": 14.0, "yaw": -0.24, "seed": 4.8, "zW": 0.90},
]


def _smoothstep(a, b, v):
    t = np.clip((v - a) / np.maximum(1e-6, (b - a)), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def eval_river_center_x_np(y):
    return 286.0 + 42.0 * np.sin(y * 0.0036 - 0.15) + 15.0 * np.sin(y * 0.0115 - 0.85) - 9.0 * np.exp(-((y + 52.0) / 85.0) ** 2)


def eval_river_half_width_np(y):
    harbor = 3.6 * np.exp(-((y + 52.0) / 56.0) ** 2)
    pulse = 1.1 * np.sin(y * 0.0085 + 0.6)
    return np.maximum(7.2, 8.4 + harbor + pulse)


def eval_river_surface_z_np(y):
    uN = np.clip((y - 35.0) / 520.0, 0.0, 1.0)
    smN = uN * uN * (3.0 - 2.0 * uN)
    base_slope = 0.55 + ((y + 1400.0) / 2800.0) * 0.55
    hill_drop = smN * 11.0 + np.maximum(0.0, (y - 550.0) * 0.0065)
    return base_slope + hill_drop


def eval_approach_road_x_np(y):
    u = np.clip((-y - 45.0) / 140.0, 0.0, 1.0)
    sm = u * u * (3.0 - 2.0 * u)
    val = sm * (8.5 * np.sin((y + 45.0) * 0.0115) + 2.8 * np.sin((y + 45.0) * 0.027 - 0.5))
    return np.where(y >= -45.0, 0.0, val)


def eval_dist_to_polyline_np(x, y, pts):
    min_d = np.full_like(x, 1e9, dtype=np.float64)
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy
        if l2 > 1e-6:
            t = np.clip(((x - ax) * dx + (y - ay) * dy) / l2, 0.0, 1.0)
        else:
            t = 0.0
        d = np.hypot(x - (ax + t * dx), y - (ay + t * dy))
        min_d = np.minimum(min_d, d)
    return min_d


def eval_lake_lobe_frac_np(lake, x, y):
    dx = x - lake["cx"]
    dy = y - lake["cy"]
    c = math.cos(lake["yaw"])
    s = math.sin(lake["yaw"])
    lx = dx * c + dy * s
    ly = -dx * s + dy * c
    ang = np.arctan2(ly / lake["ry"], lx / lake["rx"])
    lobe = 1.0 + 0.16 * np.sin(ang * 2.0 + lake["seed"]) + 0.09 * np.cos(ang * 3.0 - lake["seed"] * 1.7)
    return np.hypot(lx / lake["rx"], ly / lake["ry"]) / lobe


def eval_alluvial_lake_field_np(x, y):
    best_frac = np.full_like(x, 9e9, dtype=np.float64)
    best_zw = np.full_like(x, 0.86, dtype=np.float64)
    for lk in ALLUVIAL_LAKES:
        f = eval_lake_lobe_frac_np(lk, x, y)
        mask = f < best_frac
        best_frac = np.where(mask, f, best_frac)
        best_zw = np.where(mask, lk["zW"], best_zw)
    return best_frac, best_zw


def eval_canal_field_np(x, y):
    z_canal_w = eval_river_surface_z_np(np.array([-171.0]))[0] + 0.04
    cands = [
        (eval_dist_to_polyline_np(x, y, BARGE_CANAL_PTS), 2.35, z_canal_w),
        (np.hypot(x - 73.0, y + 88.5), 7.20, z_canal_w),
        (eval_dist_to_polyline_np(x, y, SOUTH_CANAL_PTS), 1.55, z_canal_w),
        (eval_dist_to_polyline_np(x, y, SE_CANAL_PTS), 2.60, 0.79),
        (eval_dist_to_polyline_np(x, y, EAST_CANAL_PTS), 2.40, 0.85),
        (eval_dist_to_polyline_np(x, y, SW_CANAL_PTS), 2.20, 0.82),
        (eval_dist_to_polyline_np(x, y, KISURRA_CANAL_PTS), 2.00, 0.80),
        (eval_dist_to_polyline_np(x, y, ADAB_CANAL_PTS), 2.00, 0.84),
    ]
    best_norm = np.full_like(x, 9e9, dtype=np.float64)
    best_dist = np.full_like(x, 9e9, dtype=np.float64)
    best_hw = np.full_like(x, 2.35, dtype=np.float64)
    best_zw = np.full_like(x, z_canal_w, dtype=np.float64)
    for dist, hw, zw in cands:
        n = dist / hw
        m = n < best_norm
        best_norm = np.where(m, n, best_norm)
        best_dist = np.where(m, dist, best_dist)
        best_hw = np.where(m, hw, best_hw)
        best_zw = np.where(m, zw, best_zw)
    return best_dist, best_hw, best_zw


def eval_shipyard_z_np(x_in, y_in):
    """Vektorisierte Hoehenfunktion fuer 3000x3000 m Werft + Ur-Schinar + Quellgebirge-Schlucht + Fernhuegel."""
    x = np.asarray(x_in, dtype=np.float64)
    y = np.asarray(y_in, dtype=np.float64)

    road_cx = -5.0 + eval_approach_road_x_np(y)
    dist_road_x = np.abs(x - road_cx)

    # Road blend & wave damping
    in_road_band = (y < -18.0) & (y >= -1420.0) & (dist_road_x < 14.5)
    lat_blend = np.where(dist_road_x <= 5.0, 0.0, np.minimum(1.0, (dist_road_x - 5.0) / 9.5))
    wave_damp = np.where(in_road_band & (y < -42.0), 0.12 + 0.88 * (lat_blend ** 2 * (3.0 - 2.0 * lat_blend)), 1.0)

    road_blend = np.ones_like(x)
    m_rb = in_road_band & (y >= -68.0)
    rb_a = np.minimum(1.0, (-y - 42.0) / 26.0)
    rb_b = np.maximum(lat_blend, rb_a)
    rb_c = np.clip((dist_road_x - 8.0) / 6.5, 0.0, 1.0)
    road_blend = np.where(m_rb & (y < -42.0) & (dist_road_x <= 5.0), rb_a, road_blend)
    road_blend = np.where(m_rb & (y < -42.0) & (dist_road_x > 5.0), rb_b, road_blend)
    road_blend = np.where(m_rb & (y >= -42.0), rb_c, road_blend)

    dx_pit = np.maximum(0.0, np.abs(x) - 75.0)
    dy_pit = np.maximum(0.0, np.abs(y) - 18.0)
    d_pit = np.hypot(dx_pit, dy_pit)
    terrain_wave = 0.50 * np.sin(x * 0.022 + 0.3) * np.cos(y * 0.020 - 0.2) + 0.24 * np.sin(x * 0.048 - y * 0.041)
    gentle_wave = terrain_wave * wave_damp

    u_ns = np.clip((y - 20.0) / 70.0, 0.0, 1.0)
    north_shelf = 3.5 * (u_ns * u_ns * (3.0 - 2.0 * u_ns))

    ry_main = np.where(y < 200.0, 74.0, 240.0)
    d_main = np.hypot((x - 62.0) / 168.0, (y - 200.0) / ry_main)
    main_massif = 56.0 * np.exp(-np.power(d_main, 1.95)) * (1.0 + 0.14 * np.sin(x * 0.022 + y * 0.017))
    spring_shoulder = 6.5 * np.exp(-(((x - 58.0) / 24.0) ** 2 + ((y - 104.0) / 16.0) ** 2))

    # Natuerliche Quellschlucht-Flanken links & rechts von x=58 (y=75..145) ohne kuenstliches Kraterloch
    flank_west = 10.5 * np.exp(-(((x - 36.0) / 15.0) ** 2 + ((y - 106.0) / 26.0) ** 2))
    flank_east = 11.0 * np.exp(-(((x - 82.0) / 15.0) ** 2 + ((y - 108.0) / 26.0) ** 2))
    valley_trough = 1.6 * np.exp(-((x - 58.0) / 10.5) ** 2) * _smoothstep(45.0, 72.0, y) * (1.0 - _smoothstep(86.0, 96.0, y))

    ry_nw = np.where(y < 215.0, 78.0, 220.0)
    nw_ridge = 44.0 * np.exp(-np.power(np.hypot((x + 215.0) / 185.0, (y - 215.0) / ry_nw), 1.9))
    saddle = 26.0 * np.exp(-(((x + 75.0) / 88.0) ** 2 + ((y - 200.0) / 56.0) ** 2))
    east_massif = 38.0 * np.exp(-(((x - 690.0) / 165.0) ** 2 + ((y - 360.0) / 155.0) ** 2))
    sw_forest_hill = 32.0 * np.exp(-np.power(np.hypot((x + 620.0) / 155.0, (y + 75.0) / 145.0), 1.95))
    sw_forest_rise = 6.5 * np.exp(-(((x + 125.0) ** 2 + (y + 102.0) ** 2) / (42.0 ** 2)))

    city_tell = (
        2.65 * np.exp(-(((x - 184.0) / 78.0) ** 2 + ((y + 52.0) / 96.0) ** 2))
        + 1.35 * np.exp(-(((x + 235.0) / 60.0) ** 2 + ((y + 345.0) / 60.0) ** 2))
        + 1.15 * np.exp(-(((x - 395.0) / 52.0) ** 2 + ((y + 210.0) / 52.0) ** 2))
        + 1.45 * np.exp(-(((x - 470.0) / 62.0) ** 2 + ((y - 45.0) / 62.0) ** 2))
        + 1.25 * np.exp(-(((x - 385.0) / 55.0) ** 2 + ((y - 295.0) / 55.0) ** 2))
        + 1.25 * np.exp(-(((x + 65.0) / 58.0) ** 2 + ((y + 520.0) / 58.0) ** 2))
    )

    s_y = np.clip((-620.0 - y) / 160.0, 0.0, 1.0)
    s_x = np.clip((np.abs(x) - 90.0) / 160.0, 0.0, 1.0)
    sm_sy = s_y * s_y * (3.0 - 2.0 * s_y)
    sm_sx = s_x * s_x * (3.0 - 2.0 * s_x)
    south_rim = 18.0 * sm_sy * sm_sx * np.exp(-(((np.abs(x) - 520.0) / 220.0) ** 2 + ((y + 840.0) / 190.0) ** 2))

    # Weicher Uebergang zu 3000-m-Fernhuegeln (Zagros-Vorgebirge im Norden & Huegelketten)
    r_far = np.hypot(x, y)
    u_far = np.clip((r_far - 740.0) / 360.0, 0.0, 1.0)
    sm_far = u_far * u_far * (3.0 - 2.0 * u_far)
    north_foothill = np.clip((y - 520.0) / 950.0, 0.0, 1.0) ** 1.3 * 46.0 * (0.55 + 0.45 * np.sin(x * 0.0042 + 0.6) * np.cos(y * 0.0038 - 0.3))
    distant_hills = sm_far * (
        15.0
        + 11.0 * np.sin(x * 0.0052 + 0.7) * np.cos(y * 0.0046 - 0.4)
        + 6.5 * np.cos(x * 0.009 - y * 0.008)
    ) + north_foothill

    z_macro = (
        1.30
        + north_shelf
        + gentle_wave
        + main_massif
        + spring_shoulder
        + flank_west
        + flank_east
        - valley_trough
        + nw_ridge
        + saddle
        + east_massif
        + sw_forest_hill
        + sw_forest_rise
        + city_tell
        + south_rim
        + distant_hills
    )

    u_pit = np.clip(d_pit / 12.0, 0.0, 1.0)
    z_pit_blend = -0.85 + (u_pit * u_pit * (3.0 - 2.0 * u_pit)) * 2.15
    z_base = np.where(d_pit < 12.0, z_pit_blend, z_macro)

    # Euphrat-Flussbett (ueber volle +-1500 m)
    r_x = eval_river_center_x_np(y)
    r_w = eval_river_half_width_np(y)
    abs_dx_r = np.abs(x - r_x)
    z_water = eval_river_surface_z_np(y)
    z_bank_target = z_water + 0.90

    u_bk = np.clip((abs_dx_r - r_w * 1.12) / (r_w * 3.28), 0.0, 1.0)
    sm_bk = u_bk * u_bk * (3.0 - 2.0 * u_bk)
    z_riv_bank = z_bank_target * (1.0 - sm_bk) + z_base * sm_bk

    u_bed = np.maximum(0.0, 1.0 - np.power(np.clip(abs_dx_r / (r_w * 1.12), 0.0, 1.0), 2.1))
    shoal_var = 0.14 * np.sin(x * 0.38 + y * 0.16) * u_bed
    z_riv_bed = z_bank_target * (1.0 - u_bed) + (z_water - 2.25 + shoal_var) * u_bed

    in_riv_zone = (d_pit >= 12.0) & (abs_dx_r < r_w * 4.4)
    z_base = np.where(in_riv_zone & (abs_dx_r >= r_w * 1.12), z_riv_bank, z_base)
    z_base = np.where(in_riv_zone & (abs_dx_r < r_w * 1.12), z_riv_bed, z_base)

    # 4 Alluvial-Seen
    lf_frac, lf_zw = eval_alluvial_lake_field_np(x, y)
    in_lk_zone = (d_pit >= 12.0) & (abs_dx_r >= r_w * 1.10) & (lf_frac < 1.48)
    z_l_bank = lf_zw + 0.85
    u_lb = np.clip((lf_frac - 1.0) / 0.48, 0.0, 1.0)
    sm_lb = u_lb * u_lb * (3.0 - 2.0 * u_lb)
    z_slope_bank = lf_zw + sm_lb * 0.85
    sm_out = np.maximum(0.0, (lf_frac - 1.12) / 0.36)
    z_lk_outer = z_slope_bank * (1.0 - sm_out) + np.maximum(z_l_bank, z_base) * sm_out
    u_lcut = np.maximum(0.0, 1.0 - np.power(np.clip(lf_frac, 0.0, 1.0), 2.1))
    z_lk_inner = lf_zw - 1.65 * u_lcut
    z_base = np.where(in_lk_zone & (lf_frac >= 1.0), z_lk_outer, z_base)
    z_base = np.where(in_lk_zone & (lf_frac < 1.0), z_lk_inner, z_base)

    # 5 Kanaele + Holzhafenbecken
    c_mask = (d_pit >= 12.0) & (
        ((x > 54.0) & (x < 630.0) & (y > -325.0) & (y < 70.0))
        | ((x > -330.0) & (x < -145.0) & (y > -525.0) & (y < -210.0))
    ) & (abs_dx_r >= r_w * 0.42)
    cf_dist, cf_hw, cf_zw = eval_canal_field_np(x, y)
    pad_ext = np.where((x > 250.0) | (x < -50.0), 7.5, np.where(x > 218.0, 6.2, 4.7))
    cut_pad = np.where((x > 250.0) | (x < -50.0), 3.0, np.where(x > 218.0, 2.6, 1.8))
    rim_r = cf_hw + cut_pad + pad_ext
    in_c = c_mask & (cf_dist < rim_r)
    z_cbank = cf_zw + 0.72
    in_lk_c = lf_frac < 1.0

    u_cb = np.clip((cf_dist - (cf_hw + cut_pad)) / np.maximum(0.1, pad_ext), 0.0, 1.0)
    sm_cb = u_cb * u_cb * (3.0 - 2.0 * u_cb)
    z_c_outer = z_cbank * (1.0 - sm_cb) + z_base * sm_cb

    u_sl = np.clip((cf_dist - cf_hw) / np.maximum(0.1, cut_pad), 0.0, 1.0)
    sm_sl = u_sl * u_sl * (3.0 - 2.0 * u_sl)
    z_c_slope = cf_zw + sm_sl * 0.72
    z_c_slope_final = np.where((abs_dx_r < r_w * 1.18) | in_lk_c, np.minimum(z_base, z_c_slope), z_c_slope)

    u_bed_c = np.maximum(0.0, 1.0 - np.power(np.clip(cf_dist / cf_hw, 0.0, 1.0), 2.0))
    z_c_cut = cf_zw - 1.28 * u_bed_c
    z_c_cut_final = np.where((abs_dx_r < r_w * 1.18) | in_lk_c, np.minimum(z_base, z_c_cut), z_c_cut)

    z_base = np.where(in_c & (cf_dist >= cf_hw + cut_pad) & (abs_dx_r >= r_w * 1.18) & (~in_lk_c), z_c_outer, z_base)
    z_base = np.where(in_c & (cf_dist >= cf_hw) & (cf_dist < cf_hw + cut_pad), z_c_slope_final, z_base)
    z_base = np.where(in_c & (cf_dist < cf_hw), z_c_cut_final, z_base)

    # Ebene Werft-Plateaus
    for px, py, r_in, r_out, pz in SHIPYARD_PLATEAUS:
        d = np.hypot(x - px, y - py)
        m_in = d <= r_in
        m_tr = (d > r_in) & (d < r_out)
        t = np.clip((d - r_in) / (r_out - r_in), 0.0, 1.0)
        sm = t * t * (3.0 - 2.0 * t)
        z_base = np.where(m_in, pz, np.where(m_tr, pz * (1.0 - sm) + z_base * sm, z_base))

    # Helling-Sohle & Zufahrtsrampe
    in_dock = (np.abs(x) <= 75.0) & (np.abs(y) <= 18.0)
    in_ramp = (y < -18.0) & (y >= -42.0) & (dist_road_x <= 8.0)
    z_out = -0.85 * (1.0 - road_blend) + z_base * road_blend
    z_out = np.where(in_dock | in_ramp, -0.85, z_out)
    return z_out


def eval_sy_z(x, y):
    return float(eval_shipyard_z_np(np.array([x]), np.array([y]))[0])


# ==============================================================================
# HILFSFUNKTIONEN FUER STRASSEN, STADT, WERKSTATT & BOTANIK-ZONEN
# ==============================================================================

ORGANIC_ROADS = [
    ([(-5.0, -45.0), (2.0, -45.0), (18.0, -46.8), (46.0, -46.8), (76.0, -47.6), (98.0, -47.5), (122.0, -48.0)], 4.4),
    ([(36.0, -46.8), (36.0, -39.5)], 2.5),
    ([(28.0, -46.8), (28.0, -57.5), (52.0, -57.5)], 2.5),
    ([(56.0, -47.0), (56.0, -37.5)], 2.3),
    ([(101.5, -47.5), (101.5, -41.5)], 2.6),
    ([(98.0, -47.5), (98.0, -55.0), (112.5, -54.5), (120.0, -59.2)], 2.8),
    ([(76.0, -47.6), (73.0, -80.5)], 3.0),
    ([(259.0, -48.0), (278.0, -48.0), (375.0, -5.0), (470.0, 52.0), (565.0, 95.0)], 3.8),
    ([(280.0, -68.0), (342.0, -142.0), (395.0, -210.0), (422.0, -242.0)], 3.6),
    ([(315.0, 125.0), (355.0, 215.0), (385.0, 295.0), (465.0, 345.0)], 3.6),
    ([(184.0, 33.0), (184.0, 62.0), (252.0, 118.0), (315.0, 125.0)], 3.6),
    ([(184.0, -135.0), (184.0, -174.0), (176.0, -245.0), (165.0, -315.0)], 3.8),
    ([(165.0, -315.0), (275.0, -365.0), (385.0, -415.0)], 3.4),
    ([(470.0, 52.0), (510.0, 0.0), (545.0, -65.0), (470.0, -140.0), (395.0, -210.0)], 3.4),
    ([(-5.0, -45.0), (-42.0, -36.5), (-66.0, -56.0), (-98.0, -78.0), (-126.0, -102.0), (-215.0, -85.0), (-345.0, -65.0)], 3.4),
    ([(-345.0, -65.0), (-275.0, -120.0), (-205.0, -175.0), (-220.0, -260.0), (-235.0, -345.0)], 3.4),
    ([(-5.0, -45.0), (-5.2, -92.0), (-10.0, -155.0), (-24.0, -260.0), (-48.0, -410.0), (-65.0, -520.0)], 3.8),
    ([(-235.0, -345.0), (-148.0, -430.0), (-65.0, -520.0)], 3.4),
]

VILLAGE_ZONES = [
    (-235.0, -345.0, 46.0),  # 1) Nisaba-Kornstadt
    (395.0, -210.0, 38.0),   # 2) Eridu-Lagune
    (470.0, 45.0, 44.0),     # 3) Girsu-Osthain
    (385.0, 295.0, 40.0),    # 4) Sippar-Furt
    (-65.0, -520.0, 42.0),   # 5) Larsam-Suedweide
    (-345.0, -65.0, 28.0),   # 6) Zedern-Vorwerk
    (165.0, -315.0, 30.0),   # 7) Kisurra-Faehrweiler
    (-205.0, -175.0, 28.0),  # 8) Umma-Westdorf
    (545.0, -65.0, 28.0),    # 9) Adab-Ostweiler
    (385.0, -415.0, 28.0),   # 10) Lagash-Suedost
]

FLAGSTONE_ROADS = [
    ([(121.0, -48.0), (131.0, -48.0), (168.0, -48.0), (204.0, -48.0), (228.0, -48.0), (238.0, -48.0)], 4.6),
    ([(184.0, 34.0), (184.0, 26.0), (184.0, -18.0), (184.0, -48.0), (184.0, -84.0), (184.0, -128.0), (184.0, -137.0)], 4.6),
    ([(156.0, 14.0), (156.0, -18.0), (156.0, -48.0), (156.0, -84.0), (156.0, -114.0)], 3.4),
    ([(136.0, -18.0), (156.0, -18.0), (184.0, -18.0)], 3.0),
    ([(137.0, -84.0), (156.0, -84.0), (184.0, -84.0), (205.0, -84.0), (224.0, -84.0)], 3.0),
    ([(205.0, -46.0), (205.0, -84.0), (205.0, -114.0)], 3.2),
    ([(156.0, 5.0), (184.0, 5.0)], 2.8),
]


def is_in_ur_city_or_suburb(x, y, pad=0.0):
    if (127.0 - pad <= x <= 238.0 + pad) and (-132.0 - pad <= y <= 30.0 + pad):
        return True
    if (160.0 - pad <= x <= 208.0 + pad) and (30.0 - pad <= y <= 54.0 + pad):
        return True
    if (145.0 - pad <= x <= 224.0 + pad) and (-165.0 - pad <= y <= -130.0 + pad):
        return True
    if (268.0 - pad <= x <= 296.0 + pad) and (-74.0 - pad <= y <= -24.0 + pad):
        return True
    return False


def is_in_village_zone(x, y, pad=0.0):
    for vx, vy, vr in VILLAGE_ZONES:
        if math.hypot(x - vx, y - vy) <= (vr + pad):
            return True
    return False


def is_shipyard_work_zone(x, y, pad=0.0):
    if is_in_ur_city_or_suburb(x, y, pad):
        return True
    if is_in_village_zone(x, y, pad):
        return True
    if abs(x) <= 92.0 + pad and abs(y) <= 28.0 + pad:
        return True
    if (-82.0 - pad <= x <= 128.0 + pad) and (-76.0 - pad <= y <= 58.0 + pad):
        return True
    if (48.0 - pad <= x <= 68.0 + pad) and (8.0 - pad <= y <= 104.0 + pad):
        return True
    if (-114.0 - pad <= x <= -58.0 + pad) and (26.0 - pad <= y <= 60.0 + pad):
        return True
    if (60.0 - pad <= x <= 86.0 + pad) and (-102.0 - pad <= y <= -74.0 + pad):
        return True
    if (-138.0 - pad <= x <= -110.0 + pad) and (-114.0 - pad <= y <= -88.0 + pad):
        return True
    # Strassen-Korridor
    for pts, w in ORGANIC_ROADS:
        for i in range(len(pts) - 1):
            ax, ay = pts[i]
            bx, by = pts[i + 1]
            dx, dy = bx - ax, by - ay
            l2 = dx * dx + dy * dy
            t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / max(1e-6, l2)))
            if math.hypot(x - (ax + t * dx), y - (ay + t * dy)) < (w * 0.5 + 1.8 + pad):
                return True
    return False


# ==============================================================================
# 1. HEIGHTMAP (512x512) & SPLATMAP (2048x2048) GENERIEREN
# ==============================================================================

def build_shipyard_heightmap_and_splatmap():
    t0 = time.time()
    print("[1/6] Berechne 512x512 Heightmap & 2048x2048 Splatmap (Werft)...", flush=True)

    # A) 512x512 Heightmap (Zeile 0 = +Y = +1500, Zeile H-1 = -Y = -1500 fuer UV-Konsistenz)
    xs_h = np.linspace(-HALF_SPAN, HALF_SPAN, HEIGHTMAP_RES, dtype=np.float64)
    ys_h = np.linspace(HALF_SPAN, -HALF_SPAN, HEIGHTMAP_RES, dtype=np.float64)
    gx_h, gy_h = np.meshgrid(xs_h, ys_h)
    z_h = eval_shipyard_z_np(gx_h, gy_h)
    z_min = float(np.min(z_h))
    z_max = float(np.max(z_h))
    z_span = max(1e-4, z_max - z_min)
    z_u16 = np.clip(np.round(((z_h - z_min) / z_span) * 65535.0), 0, 65535).astype(np.uint16)

    hm_png = os.path.join(wbu.WORLDS_OUT_DIR, "shipyard_heightmap.png")
    hm_json = os.path.join(wbu.WORLDS_OUT_DIR, "shipyard_heightmap.json")
    wbu.write_png_uint16_gray(hm_png, z_u16)
    with open(hm_json, "w", encoding="utf-8") as f:
        json.dump({
            "scene": "shipyard",
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

    # B) 2048x2048 Splatmap (R=Stadt-Lehm/Wege, G=Ufer-/Bergwald-Gruen, B=Steinpflaster/Fels, Base=Steppenlehm; A=255)
    xs_s = np.linspace(-HALF_SPAN, HALF_SPAN, SPLATMAP_RES, dtype=np.float64)
    ys_s = np.linspace(HALF_SPAN, -HALF_SPAN, SPLATMAP_RES, dtype=np.float64)
    gx, gy = np.meshgrid(xs_s, ys_s)
    gz = eval_shipyard_z_np(gx, gy)

    # Gradient / Hangneigung
    dz_dx = np.gradient(gz, WORLD_SIZE / (SPLATMAP_RES - 1), axis=1)
    dz_dy = np.gradient(gz, WORLD_SIZE / (SPLATMAP_RES - 1), axis=0)
    slope = np.hypot(dz_dx, dz_dy)

    # Prozedurales Makro-Rauschen fuer organische Uebergaenge
    n_org = (
        0.55 * np.sin(gx * 0.043 + gy * 0.031)
        + 0.30 * np.cos(gx * 0.11 - gy * 0.09)
        + 0.15 * np.sin(gx * 0.27 + gy * 0.23)
    )

    # 1. Ur-Schinar Stadt-, Vorstadt- & 10 Dorf-Masken (STRENG: kein wildes Gruen in den Hoefen!)
    in_ur_core = (gx >= 127.0) & (gx <= 234.0) & (gy >= -131.0) & (gy <= 29.0)
    in_sub_n = (gx >= 161.0) & (gx <= 207.0) & (gy >= 30.0) & (gy <= 52.0)
    in_sub_s = (gx >= 145.0) & (gx <= 223.0) & (gy >= -164.0) & (gy <= -131.0)
    in_sub_e = (gx >= 269.0) & (gx <= 294.0) & (gy >= -72.0) & (gy <= -25.0)
    in_villages = np.zeros_like(gx, dtype=bool)
    for vx, vy, vr in VILLAGE_ZONES:
        in_villages |= (np.hypot(gx - vx, gy - vy) <= (vr * 0.72 + n_org * 2.5))
    in_city_any = in_ur_core | in_sub_n | in_sub_s | in_sub_e | in_villages

    # Werft-Arbeitsplatz & Baudorf (kompakter Rand statt grauem Einheitsboden ringsum)
    in_shipyard_yard = (np.abs(gx) <= 82.0) & (np.abs(gy) <= 24.0)
    in_work_yard = (gx >= -76.0) & (gx <= 125.0) & (gy >= -70.0) & (gy <= 46.0)
    in_ropewalk = (gx >= -112.0) & (gx <= -60.0) & (gy >= 28.0) & (gy <= 57.0)
    in_baudorf_plaza = (np.hypot(gx - 101.5, gy + 41.5) <= 6.0)

    # Organische Aussenwege
    road_w = np.zeros_like(gx)
    for pts, w in ORGANIC_ROADS:
        d = eval_dist_to_polyline_np(gx, gy, pts)
        edge = w * 0.5 + 0.8 + n_org * 0.65
        rw = 1.0 - _smoothstep(edge - 0.9, edge + 1.2, d)
        road_w = np.maximum(road_w, rw)

    # Pflaster-Flaechen & Stadtstrassen (B-Kanal)
    plaza_w = np.zeros_like(gx)
    for pts, w in FLAGSTONE_ROADS:
        d = eval_dist_to_polyline_np(gx, gy, pts)
        pw = 1.0 - _smoothstep(w * 0.5 - 0.3, w * 0.5 + 0.6, d)
        plaza_w = np.maximum(plaza_w, pw)
    # Agora (169.8, -48.0, 24.4x16.6), Temenos (210, -10, 40x52), Ostkai (233, -48), Tor-Vorplaetze, Baudorf-Platz
    in_agora = (np.abs(gx - 169.8) <= 12.6) & (np.abs(gy + 48.0) <= 8.6)
    in_temenos = (gx >= 189.0) & (gx <= 228.0) & (gy >= -38.0) & (gy <= 15.0)
    in_quay = (gx >= 229.0) & (gx <= 237.0) & (gy >= -88.0) & (gy <= -16.0)
    in_wood_quay = (gx >= 60.0) & (gx <= 74.0) & (gy >= -94.0) & (gy <= -78.0)
    plaza_w = np.where(in_agora | in_temenos | in_quay | in_wood_quay | in_baudorf_plaza, np.maximum(plaza_w, 0.92), plaza_w)

    # Steile Haenge & Quellschlucht-Fels (auch im B-Kanal)
    rock_w = _smoothstep(0.32, 0.72, slope + n_org * 0.06) * _smoothstep(3.0, 12.0, gz)

    # R-Kanal: festgestampfter Stadt-Lehmboden, Werftboden, Dorfplaetze & Aussenwege
    earth_w = np.zeros_like(gx)
    earth_w = np.where(in_city_any, 0.94 + 0.05 * n_org, earth_w)
    earth_w = np.where(in_shipyard_yard | in_work_yard | in_ropewalk, np.maximum(earth_w, 0.88 + 0.08 * n_org), earth_w)
    earth_w = np.maximum(earth_w, road_w * 0.92)

    # G-Kanal: Auen-Ufergruen, Oasen, Agrar-Parzellen & Huegelwaelder (STRENG 0 in Ur-Schinar, Doerfern & Werftsohle!)
    riv_x = eval_river_center_x_np(gy)
    riv_hw = eval_river_half_width_np(gy)
    d_riv = np.abs(gx - riv_x) - riv_hw
    cf_d, cf_hw, _ = eval_canal_field_np(gx, gy)
    lf_f, _ = eval_alluvial_lake_field_np(gx, gy)

    riparian_g = np.maximum(
        1.0 - _smoothstep(4.0, 44.0 + n_org * 10.0, np.maximum(0.0, d_riv)),
        1.0 - _smoothstep(2.5, 24.0 + n_org * 6.0, np.maximum(0.0, cf_d - cf_hw)),
    )
    riparian_g = np.maximum(riparian_g, 1.0 - _smoothstep(1.02, 1.68 + n_org * 0.14, lf_f))
    # Bewaesserte Saatfelder im Schwemmland mit Saatfurchen-Kontrast
    field_g = np.zeros_like(gx)
    splat_crop_boxes = (
        (88, 126, -210, -184), (138, 174, -210, -184), (88, 132, -264, -228), (194, 240, -210, -184),
        (194, 244, -264, -228), (254, 294, -242, -198), (312, 360, -132, -92), (312, 355, -80, -45),
        (314, 362, -14, 34), (312, 356, 45, 92), (-348, -300, -322, -278), (-282, -240, -308, -268),
        (-224, -176, -310, -266), (-164, -116, -324, -278), (304, 354, -188, -144), (362, 414, -182, -140),
        (306, 354, -260, -212), (492, 540, -234, -186), (436, 494, -84, -30), (502, 560, -22, 28),
        (438, 494, 102, 154), (504, 564, 118, 170), (286, 338, 186, 240), (346, 398, 186, 238),
        (-164, -112, -482, -432), (-102, -48, -480, -430), (196, 244, -338, -292), (72, 116, -328, -284),
        (-256, -210, -220, -182), (-162, -120, -222, -184), (308, 356, -360, -316), (418, 466, -420, -376),
    )
    furrows = 0.62 + 0.28 * np.sin((gx + gy) * 0.42)
    for fi, (fx0, fx1, fy0, fy1) in enumerate(splat_crop_boxes):
        m_f = (gx >= fx0) & (gx <= fx1) & (gy >= fy0) & (gy <= fy1)
        field_g = np.where(m_f, np.maximum(field_g, (0.55 if fi % 2 else 0.78) * furrows), field_g)
    alluvial_meadow = (1.0 - _smoothstep(1.8, 3.6, gz + n_org * 0.7)) * np.clip(0.32 + 0.24 * n_org, 0.05, 0.58)
    hill_g = _smoothstep(2.4, 8.5, gz + n_org * 1.4) * (1.0 - _smoothstep(0.38, 0.78, slope))
    green_w = np.clip(np.maximum(riparian_g * 0.96, np.maximum(hill_g * 0.90, np.maximum(alluvial_meadow, field_g))) + 0.08 * n_org, 0.0, 1.0)

    # Unterdrueckung von Gruen in Stadt, Doerfern, Strassen & Werftplatz
    suppress_g = np.clip(np.maximum(earth_w, plaza_w), 0.0, 1.0)
    green_w = np.where(in_city_any | in_shipyard_yard | in_work_yard, 0.0, green_w * (1.0 - suppress_g * 0.94))

    # B-Kanal ist AUSSCHLIESSLICH fuer Steinpflaster/Plazas/Kais reserviert (KEINE Pflasterkacheln auf Berghaengen!)
    stone_plaza_w = np.clip(plaza_w, 0.0, 1.0)
    # Steile Haenge bekommen verdichtete Gebirgserde / Geroell (R-Kanal) statt Stadtpflaster
    slope_earth_w = _smoothstep(0.32, 0.72, slope + n_org * 0.06) * _smoothstep(4.0, 12.0, gz) * (1.0 - np.where(in_city_any, 1.0, 0.0))
    earth_w = np.maximum(earth_w, slope_earth_w * 0.80)

    # Normalisieren damit R+G+B <= 1.0 (Rest = Steppe-Loam Basis)
    r_f = np.clip(earth_w * (1.0 - stone_plaza_w * 0.92), 0.0, 1.0)
    g_f = np.clip(green_w * (1.0 - stone_plaza_w * 0.95), 0.0, 1.0)
    b_f = np.clip(stone_plaza_w, 0.0, 1.0)
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

    splat_png = os.path.join(wbu.WORLDS_OUT_DIR, "shipyard_splatmap.png")
    wbu.write_png_rgba8(splat_png, splat)
    print(f"    -> Heightmap & Splatmap geschrieben in {time.time() - t0:.2f}s (Z=[{z_min:.2f}, {z_max:.2f}])", flush=True)
    return splat_png, hm_png


# ==============================================================================
# 2. TERRAIN- & WASSER-GEOMETRIE + CYCLES-SPLAT-SHADER
# ==============================================================================

def _build_shipyard_terrain_material(splat_png_path):
    mat = bpy.data.materials.new("Mat_Shipyard_World_Terrain")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # UV0 (0..1 ueber 3000 m) fuer Splatmap + Welt-Kachel-UV fuer PBR-Texturen
    uv_splat = nt.nodes.new("ShaderNodeTexCoord")
    splat_img = bpy.data.images.load(os.path.abspath(splat_png_path))
    splat_img.colorspace_settings.name = "Non-Color"
    n_splat = nt.nodes.new("ShaderNodeTexImage")
    n_splat.image = splat_img
    n_splat.extension = "EXTEND"
    nt.links.new(uv_splat.outputs["UV"], n_splat.inputs["Vector"])

    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(n_splat.outputs["Color"], sep.inputs["Color"])

    # Gekachelte UV (1 Kachel ~ 14 m ueber 3000 m => Scale ~ 214)
    map_tile = nt.nodes.new("ShaderNodeMapping")
    map_tile.inputs["Scale"].default_value = (214.0, 214.0, 1.0)
    nt.links.new(uv_splat.outputs["UV"], map_tile.inputs["Vector"])

    def load_pbr_layer(alb_name, nrm_name, orm_name):
        t_alb = nt.nodes.new("ShaderNodeTexImage")
        t_alb.image = wbu.load_image_cached(alb_name, "sRGB")
        nt.links.new(map_tile.outputs["Vector"], t_alb.inputs["Vector"])

        t_nrm = nt.nodes.new("ShaderNodeTexImage")
        t_nrm.image = wbu.load_image_cached(nrm_name, "Non-Color")
        nt.links.new(map_tile.outputs["Vector"], t_nrm.inputs["Vector"])

        t_orm = nt.nodes.new("ShaderNodeTexImage")
        t_orm.image = wbu.load_image_cached(orm_name, "Non-Color")
        nt.links.new(map_tile.outputs["Vector"], t_orm.inputs["Vector"])

        sep_orm = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(t_orm.outputs["Color"], sep_orm.inputs["Color"])
        return t_alb.outputs["Color"], t_nrm.outputs["Color"], sep_orm.outputs["Green"]

    alb_steppe, nrm_steppe, rgh_steppe = load_pbr_layer(
        "terrain_steppe_loam_baseColor.png", "terrain_steppe_loam_normal.png", "terrain_steppe_loam_orm.png"
    )
    alb_city, nrm_city, rgh_city = load_pbr_layer(
        "terrain_city_earth_baseColor.png", "terrain_city_earth_normal.png", "terrain_city_earth_orm.png"
    )
    alb_green, nrm_green, rgh_green = load_pbr_layer(
        "terrain_alluvial_bank_baseColor.png", "terrain_alluvial_bank_normal.png", "terrain_alluvial_bank_orm.png"
    )
    alb_plaza, nrm_plaza, rgh_plaza = load_pbr_layer(
        "terrain_plaza_albedo.png", "terrain_plaza_normal.png", "terrain_plaza_orm.png"
    )

    def mix_chain(base, l_r, l_g, l_b, is_color=True):
        if is_color:
            m1 = nt.nodes.new("ShaderNodeMix")
            m1.data_type = "RGBA"
            nt.links.new(sep.outputs["Red"], m1.inputs["Factor"])
            nt.links.new(base, m1.inputs["A"])
            nt.links.new(l_r, m1.inputs["B"])

            m2 = nt.nodes.new("ShaderNodeMix")
            m2.data_type = "RGBA"
            nt.links.new(sep.outputs["Green"], m2.inputs["Factor"])
            nt.links.new(m1.outputs["Result"], m2.inputs["A"])
            nt.links.new(l_g, m2.inputs["B"])

            m3 = nt.nodes.new("ShaderNodeMix")
            m3.data_type = "RGBA"
            nt.links.new(sep.outputs["Blue"], m3.inputs["Factor"])
            nt.links.new(m2.outputs["Result"], m3.inputs["A"])
            nt.links.new(l_b, m3.inputs["B"])
            return m3.outputs["Result"]
        else:
            m1 = nt.nodes.new("ShaderNodeMix")
            m1.data_type = "FLOAT"
            nt.links.new(sep.outputs["Red"], m1.inputs["Factor"])
            nt.links.new(base, m1.inputs["A"])
            nt.links.new(l_r, m1.inputs["B"])

            m2 = nt.nodes.new("ShaderNodeMix")
            m2.data_type = "FLOAT"
            nt.links.new(sep.outputs["Green"], m2.inputs["Factor"])
            nt.links.new(m1.outputs["Result"], m2.inputs["A"])
            nt.links.new(l_g, m2.inputs["B"])

            m3 = nt.nodes.new("ShaderNodeMix")
            m3.data_type = "FLOAT"
            nt.links.new(sep.outputs["Blue"], m3.inputs["Factor"])
            nt.links.new(m2.outputs["Result"], m3.inputs["A"])
            nt.links.new(l_b, m3.inputs["B"])
            return m3.outputs["Result"]

    col_out = mix_chain(alb_steppe, alb_city, alb_green, alb_plaza, True)
    nrm_out = mix_chain(nrm_steppe, nrm_city, nrm_green, nrm_plaza, True)
    rgh_out = mix_chain(rgh_steppe, rgh_city, rgh_green, rgh_plaza, False)

    # Steilhang-Fels im Quellgebirge (via Welt-Normal Z & Hoehe, kein Pflaster auf Bergen!)
    geom_n = nt.nodes.new("ShaderNodeNewGeometry")
    sep_n = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geom_n.outputs["Normal"], sep_n.inputs["Vector"])
    sep_p = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geom_n.outputs["Position"], sep_p.inputs["Vector"])

    # Slope-Faktor: je flacher Normal.Z (< 0.90), desto felsiger ab Z > 4.5 m
    rng_slp = nt.nodes.new("ShaderNodeMapRange")
    rng_slp.inputs["From Min"].default_value = 0.90
    rng_slp.inputs["From Max"].default_value = 0.65
    nt.links.new(sep_n.outputs["Z"], rng_slp.inputs["Value"])

    rng_alt = nt.nodes.new("ShaderNodeMapRange")
    rng_alt.inputs["From Min"].default_value = 4.0
    rng_alt.inputs["From Max"].default_value = 12.0
    nt.links.new(sep_p.outputs["Z"], rng_alt.inputs["Value"])

    mul_cliff = nt.nodes.new("ShaderNodeMath")
    mul_cliff.operation = "MULTIPLY"
    nt.links.new(rng_slp.outputs["Result"], mul_cliff.inputs[0])
    nt.links.new(rng_alt.outputs["Result"], mul_cliff.inputs[1])

    # Warm-grauer Gebirgsfels (Ararat-Scree-Quadrant warm getoent)
    vec_qmul = nt.nodes.new("ShaderNodeVectorMath")
    vec_qmul.operation = "MULTIPLY"
    vec_qmul.inputs[1].default_value = (180.0, 180.0, 1.0)
    nt.links.new(uv_splat.outputs["UV"], vec_qmul.inputs[0])
    vec_qmod = nt.nodes.new("ShaderNodeVectorMath")
    vec_qmod.operation = "MODULO"
    vec_qmod.inputs[1].default_value = (1.0, 1.0, 1.0)
    nt.links.new(vec_qmul.outputs["Vector"], vec_qmod.inputs[0])
    vec_qs = nt.nodes.new("ShaderNodeVectorMath")
    vec_qs.operation = "MULTIPLY"
    vec_qs.inputs[1].default_value = (0.46, 0.46, 1.0)
    nt.links.new(vec_qmod.outputs["Vector"], vec_qs.inputs[0])
    vec_qa = nt.nodes.new("ShaderNodeVectorMath")
    vec_qa.operation = "ADD"
    vec_qa.inputs[1].default_value = (0.52, 0.52, 0.0)
    nt.links.new(vec_qs.outputs["Vector"], vec_qa.inputs[0])

    t_rock_a = nt.nodes.new("ShaderNodeTexImage")
    t_rock_a.image = wbu.load_image_cached("terrain_ararat_atlas_albedo.png", "sRGB")
    nt.links.new(vec_qa.outputs["Vector"], t_rock_a.inputs["Vector"])
    t_rock_n = nt.nodes.new("ShaderNodeTexImage")
    t_rock_n.image = wbu.load_image_cached("terrain_ararat_atlas_normal.png", "Non-Color")
    nt.links.new(vec_qa.outputs["Vector"], t_rock_n.inputs["Vector"])

    # Warm toenen (Kalkstein/Sandstein statt blaugrauem Basalt)
    tint_rock = nt.nodes.new("ShaderNodeMix")
    tint_rock.data_type = "RGBA"
    tint_rock.blend_type = "MULTIPLY"
    tint_rock.inputs["Factor"].default_value = 0.85
    tint_rock.inputs["B"].default_value = (0.78, 0.68, 0.56, 1.0)
    nt.links.new(t_rock_a.outputs["Color"], tint_rock.inputs["A"])

    m_cliff_c = nt.nodes.new("ShaderNodeMix")
    m_cliff_c.data_type = "RGBA"
    nt.links.new(mul_cliff.outputs["Value"], m_cliff_c.inputs["Factor"])
    nt.links.new(col_out, m_cliff_c.inputs["A"])
    nt.links.new(tint_rock.outputs["Result"], m_cliff_c.inputs["B"])

    m_cliff_n = nt.nodes.new("ShaderNodeMix")
    m_cliff_n.data_type = "RGBA"
    nt.links.new(mul_cliff.outputs["Value"], m_cliff_n.inputs["Factor"])
    nt.links.new(nrm_out, m_cliff_n.inputs["A"])
    nt.links.new(t_rock_n.outputs["Color"], m_cliff_n.inputs["B"])

    col_out = m_cliff_c.outputs["Result"]
    nrm_out = m_cliff_n.outputs["Result"]

    # Leichte Makro-Variation ueber 3000 m gegen Kachelung
    noise_m = nt.nodes.new("ShaderNodeTexNoise")
    noise_m.inputs["Scale"].default_value = 35.0
    noise_m.inputs["Detail"].default_value = 4.0
    nt.links.new(uv_splat.outputs["UV"], noise_m.inputs["Vector"])

    hsv = nt.nodes.new("ShaderNodeHueSaturation")
    map_val = nt.nodes.new("ShaderNodeMapRange")
    map_val.inputs["From Min"].default_value = 0.25
    map_val.inputs["From Max"].default_value = 0.75
    map_val.inputs["To Min"].default_value = 0.86
    map_val.inputs["To Max"].default_value = 1.12
    nt.links.new(noise_m.outputs["Fac"], map_val.inputs["Value"])
    nt.links.new(map_val.outputs["Result"], hsv.inputs["Value"])
    nt.links.new(col_out, hsv.inputs["Color"])

    nrm_map = nt.nodes.new("ShaderNodeNormalMap")
    nrm_map.inputs["Strength"].default_value = 0.85
    nt.links.new(nrm_out, nrm_map.inputs["Color"])

    nt.links.new(hsv.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(rgh_out, bsdf.inputs["Roughness"])
    nt.links.new(nrm_map.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def _build_water_material(name="Mat_Shipyard_Water", deep_col=(0.045, 0.165, 0.175), rough=0.06):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (deep_col[0], deep_col[1], deep_col[2], 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["IOR"].default_value = 1.333

    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.14, 0.14, 0.14)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])

    t_nrm = nt.nodes.new("ShaderNodeTexImage")
    t_nrm.image = wbu.load_image_cached("water_blender_normal_a.png", "Non-Color")
    nt.links.new(mp.outputs["Vector"], t_nrm.inputs["Vector"])

    nrm = nt.nodes.new("ShaderNodeNormalMap")
    nrm.inputs["Strength"].default_value = 0.35
    nt.links.new(t_nrm.outputs["Color"], nrm.inputs["Color"])
    nt.links.new(nrm.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def create_shipyard_terrain_and_water(col_terrain, splat_png_path):
    t0 = time.time()
    print("[2/6] Erzeuge 3000x3000 m Terrain-Mesh & Wasserflaechen...", flush=True)

    # Smooth center-focused non-linear grid warp [-1, 1] -> [-1500, +1500]
    u1 = np.linspace(-1.0, 1.0, TERRAIN_GRID_N + 1, dtype=np.float64)
    warp1 = np.sign(u1) * (420.0 * np.abs(u1) + 420.0 * (np.abs(u1) ** 2) + 660.0 * (np.abs(u1) ** 5))
    gx, gy = np.meshgrid(warp1, warp1)
    gz = eval_shipyard_z_np(gx, gy)
    # Garantiere dass keine groben Terrain-Vertices einen schmalen Kanal/Teich ueberbruecken
    cf_d_m, cf_hw_m, cf_zw_m = eval_canal_field_np(gx, gy)
    lf_f_m, lf_zw_m = eval_alluvial_lake_field_np(gx, gy)
    riv_x_m = eval_river_center_x_np(gy)
    riv_w_m = eval_river_half_width_np(gy)
    c_mask_m = (
        ((gx > 54.0) & (gx < 630.0) & (gy > -325.0) & (gy < 70.0))
        | ((gx > -330.0) & (gx < -145.0) & (gy > -525.0) & (gy < -210.0))
    ) & (np.abs(gx - riv_x_m) >= riv_w_m * 0.42)
    gz = np.where(c_mask_m & (cf_d_m < cf_hw_m + 3.6), np.minimum(gz, cf_zw_m - 0.95), gz)
    gz = np.where(lf_f_m < 1.04, np.minimum(gz, lf_zw_m - 0.85), gz)

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    rows = TERRAIN_GRID_N + 1
    verts = [[None] * rows for _ in range(rows)]
    for iy in range(rows):
        for ix in range(rows):
            verts[iy][ix] = bm.verts.new((float(gx[iy, ix]), float(gy[iy, ix]), float(gz[iy, ix])))
    bm.verts.ensure_lookup_table()
    for iy in range(TERRAIN_GRID_N):
        for ix in range(TERRAIN_GRID_N):
            v00 = verts[iy][ix]
            v10 = verts[iy][ix + 1]
            v11 = verts[iy + 1][ix + 1]
            v01 = verts[iy + 1][ix]
            f = bm.faces.new((v00, v10, v11, v01))
            f.smooth = True
            for lp in f.loops:
                co = lp.vert.co
                lp[uv_layer].uv = ((co.x + HALF_SPAN) / WORLD_SIZE, (co.y + HALF_SPAN) / WORLD_SIZE)

    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    mesh_terr = bpy.data.meshes.new("Terrain_Shipyard_Mesh")
    bm.to_mesh(mesh_terr)
    bm.free()

    mat_terr = _build_shipyard_terrain_material(splat_png_path)
    mesh_terr.materials.append(mat_terr)
    obj_terr = bpy.data.objects.new("Terrain_Shipyard", mesh_terr)
    col_terrain.objects.link(obj_terr)
    terrain_tris = len(mesh_terr.polygons)

    mat_riv = _build_water_material("Mat_Water_Euphrates", (0.042, 0.145, 0.140), 0.06)
    mat_aqua = _build_water_material("Mat_Water_Aqueduct", (0.065, 0.240, 0.250), 0.04)

    # A) Euphrat-Flussflaeche (y = -1480 .. +1480)
    bm_r = bmesh.new()
    uv_r = bm_r.loops.layers.uv.new("UVMap")
    ny_r = 220
    nx_r = 4
    r_verts = []
    ys_r = np.linspace(-1480.0, 1480.0, ny_r + 1)
    for j, ry in enumerate(ys_r):
        cx = float(eval_river_center_x_np(ry))
        hw = float(eval_river_half_width_np(ry)) * 1.18
        wz = float(eval_river_surface_z_np(ry))
        row_v = []
        for i in range(nx_r + 1):
            frac = i / nx_r
            wx = cx + (frac * 2.0 - 1.0) * hw
            row_v.append(bm_r.verts.new((wx, float(ry), wz)))
        r_verts.append(row_v)
    for j in range(ny_r):
        for i in range(nx_r):
            f = bm_r.faces.new((r_verts[j][i], r_verts[j][i + 1], r_verts[j + 1][i + 1], r_verts[j + 1][i]))
            f.smooth = True
            for lp in f.loops:
                lp[uv_r].uv = (lp.vert.co.x * 0.05, lp.vert.co.y * 0.05)
    bmesh.ops.triangulate(bm_r, faces=bm_r.faces[:])
    m_riv = bpy.data.meshes.new("Water_Euphrates_River_Mesh")
    bm_r.to_mesh(m_riv)
    bm_r.free()
    m_riv.materials.append(mat_riv)
    obj_riv = bpy.data.objects.new("Water_Euphrates_River", m_riv)
    col_terrain.objects.link(obj_riv)

    # B) Kanaele + Holzhafenbecken + 4 Alluvial-Seen
    bm_c = bmesh.new()
    uv_c = bm_c.loops.layers.uv.new("UVMap")
    z_canal_w = float(eval_river_surface_z_np(-171.0)) + 0.04

    def add_canal_water_ribbon(pts, half_w, z0, z1):
        dense = []
        for idx in range(len(pts) - 1):
            ax, ay = pts[idx]
            bx, by = pts[idx + 1]
            seg_l = math.hypot(bx - ax, by - ay)
            steps = max(2, int(math.ceil(seg_l / 4.0)))
            for k in range(0 if idx == 0 else 1, steps + 1):
                f = k / steps
                dense.append((ax + f * (bx - ax), ay + f * (by - ay)))
        rows_c = []
        n_d = len(dense)
        for i, (cx, cy) in enumerate(dense):
            p_prev = dense[max(0, i - 1)]
            p_next = dense[min(n_d - 1, i + 1)]
            tx, ty = p_next[0] - p_prev[0], p_next[1] - p_prev[1]
            tl = max(1e-4, math.hypot(tx, ty))
            tx /= tl
            ty /= tl
            rx, ry = ty, -tx
            wz = z0 + (i / max(1, n_d - 1)) * (z1 - z0)
            vL = bm_c.verts.new((cx - rx * half_w * 1.12, cy - ry * half_w * 1.12, wz))
            vM = bm_c.verts.new((cx, cy, wz))
            vR = bm_c.verts.new((cx + rx * half_w * 1.12, cy + ry * half_w * 1.12, wz))
            rows_c.append((vL, vM, vR))
        for i in range(n_d - 1):
            for c_i in range(2):
                f = bm_c.faces.new((rows_c[i][c_i], rows_c[i][c_i + 1], rows_c[i + 1][c_i + 1], rows_c[i + 1][c_i]))
                f.smooth = True
                for lp in f.loops:
                    lp[uv_c].uv = (lp.vert.co.x * 0.06, lp.vert.co.y * 0.06)

    add_canal_water_ribbon([(242.8, -171.0)] + BARGE_CANAL_PTS[1:-1] + [(80.2, -90.8)], 2.35, float(eval_river_surface_z_np(-171.0)), z_canal_w)
    add_canal_water_ribbon(SOUTH_CANAL_PTS, 1.55, z_canal_w, z_canal_w)
    add_canal_water_ribbon([(262.5, -212.0)] + SE_CANAL_PTS[1:-1] + [(402.7, -225.7)], 2.60, float(eval_river_surface_z_np(-212.0)), 0.78)
    add_canal_water_ribbon([(286.6, 38.0)] + EAST_CANAL_PTS[1:], 2.40, float(eval_river_surface_z_np(38.0)), 0.85)
    add_canal_water_ribbon([(-283.8, -253.7)] + SW_CANAL_PTS[1:-1] + [(-172.9, -464.9)], 2.20, 0.86, 0.78)
    add_canal_water_ribbon(KISURRA_CANAL_PTS, 2.00, z_canal_w, 0.80)
    add_canal_water_ribbon(ADAB_CANAL_PTS, 2.00, 0.85, 0.84)

    # Sauberes ausgebaggertes Kanalbett + sanfte Boeschungsschulter (verhindert gezackte Kanalufer)
    bm_cb = bmesh.new()
    uv_cb = bm_cb.loops.layers.uv.new("UVMap")

    def add_canal_bed_and_bank(pts, half_w, z0, z1):
        dense = []
        for idx in range(len(pts) - 1):
            ax, ay = pts[idx]
            bx, by = pts[idx + 1]
            seg_l = math.hypot(bx - ax, by - ay)
            steps = max(2, int(math.ceil(seg_l / 3.8)))
            for k in range(0 if idx == 0 else 1, steps + 1):
                f = k / steps
                dense.append((ax + f * (bx - ax), ay + f * (by - ay)))
        x_offs = (-half_w - 2.6, -half_w - 0.35, -half_w * 0.55, 0.0, half_w * 0.55, half_w + 0.35, half_w + 2.6)
        z_offs = (-0.35, 0.14, -0.82, -1.24, -0.82, 0.14, -0.35)
        rows_b = []
        n_d = len(dense)
        for i, (cx, cy) in enumerate(dense):
            p_prev = dense[max(0, i - 1)]
            p_next = dense[min(n_d - 1, i + 1)]
            tx, ty = p_next[0] - p_prev[0], p_next[1] - p_prev[1]
            tl = max(1e-4, math.hypot(tx, ty))
            tx /= tl
            ty /= tl
            rx, ry = ty, -tx
            wz = z0 + (i / max(1, n_d - 1)) * (z1 - z0)
            in_lk_or_riv = (
                float(eval_alluvial_lake_field_np(np.array([cx]), np.array([cy]))[0][0]) < 0.96
                or abs(cx - float(eval_river_center_x_np(cy))) < float(eval_river_half_width_np(cy)) * 0.96
            )
            row = []
            for ci, (xo, zo) in enumerate(zip(x_offs, z_offs)):
                wx, wy = cx + rx * xo, cy + ry * xo
                bz = wz + zo
                if in_lk_or_riv or ci in (0, 6) or i in (0, n_d - 1):
                    bz = min(bz, eval_sy_z(wx, wy) - 0.14)
                row.append(bm_cb.verts.new((wx, wy, bz)))
            rows_b.append(row)
        for i in range(n_d - 1):
            for c_i in range(len(x_offs) - 1):
                f = bm_cb.faces.new((rows_b[i][c_i], rows_b[i][c_i + 1], rows_b[i + 1][c_i + 1], rows_b[i + 1][c_i]))
                f.smooth = True
                for lp in f.loops:
                    lp[uv_cb].uv = (lp.vert.co.x * 0.14, lp.vert.co.y * 0.14)

    add_canal_bed_and_bank(BARGE_CANAL_PTS, 2.35, float(eval_river_surface_z_np(-171.0)), z_canal_w)
    add_canal_bed_and_bank(SOUTH_CANAL_PTS, 1.55, z_canal_w, z_canal_w)
    add_canal_bed_and_bank(SE_CANAL_PTS, 2.60, float(eval_river_surface_z_np(-212.0)), 0.78)
    add_canal_bed_and_bank(EAST_CANAL_PTS, 2.40, float(eval_river_surface_z_np(38.0)), 0.85)
    add_canal_bed_and_bank(SW_CANAL_PTS, 2.20, 0.86, 0.78)
    add_canal_bed_and_bank(KISURRA_CANAL_PTS, 2.00, z_canal_w, 0.80)
    add_canal_bed_and_bank(ADAB_CANAL_PTS, 2.00, 0.85, 0.84)

    hb_r_radii = (2.5, 5.5, 7.2, 8.2, 10.2)
    hb_r_zoffs = (-1.18, -0.78, -0.05, 0.16, -0.35)
    hb_rings = []
    for hr, hdz in zip(hb_r_radii, hb_r_zoffs):
        rr = []
        for si in range(36):
            ang = (si / 36.0) * math.pi * 2.0
            wx, wy = 73.0 + math.cos(ang) * hr, -88.5 + math.sin(ang) * hr
            bz = min(eval_sy_z(wx, wy) - 0.12, z_canal_w + hdz) if hr >= 9.5 else (z_canal_w + hdz)
            rr.append(bm_cb.verts.new((wx, wy, bz)))
        hb_rings.append(rr)
    for ri in range(len(hb_rings) - 1):
        for si in range(36):
            s2 = (si + 1) % 36
            f = bm_cb.faces.new((hb_rings[ri][si], hb_rings[ri + 1][si], hb_rings[ri + 1][s2], hb_rings[ri][s2]))
            f.smooth = True
            for lp in f.loops:
                lp[uv_cb].uv = (lp.vert.co.x * 0.14, lp.vert.co.y * 0.14)

    bmesh.ops.triangulate(bm_cb, faces=bm_cb.faces[:])
    m_cb = bpy.data.meshes.new("Canal_Beds_And_Banks_Mesh")
    bm_cb.to_mesh(m_cb)
    bm_cb.free()
    mat_cb = bpy.data.materials.new("Mat_Canal_Alluvial_Bed")
    mat_cb.use_nodes = True
    nt_cb = mat_cb.node_tree
    nt_cb.nodes.clear()
    out_cb = nt_cb.nodes.new("ShaderNodeOutputMaterial")
    bsdf_cb = nt_cb.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_cb.inputs["Roughness"].default_value = 0.88
    tc_cb = nt_cb.nodes.new("ShaderNodeTexCoord")
    t_cb_a = nt_cb.nodes.new("ShaderNodeTexImage")
    t_cb_a.image = wbu.load_image_cached("terrain_city_earth_baseColor.png", "sRGB")
    nt_cb.links.new(tc_cb.outputs["UV"], t_cb_a.inputs["Vector"])
    nt_cb.links.new(t_cb_a.outputs["Color"], bsdf_cb.inputs["Base Color"])
    nt_cb.links.new(bsdf_cb.outputs["BSDF"], out_cb.inputs["Surface"])
    m_cb.materials.append(mat_cb)
    obj_cb = bpy.data.objects.new("Canal_Beds_And_Banks", m_cb)
    col_terrain.objects.link(obj_cb)

    # Holzhafenbecken Wasserflaeche (73, -88.5)
    hb_c = bm_c.verts.new((73.0, -88.5, z_canal_w))
    hb_ring = []
    for si in range(32):
        ang = (si / 32.0) * math.pi * 2.0
        hb_ring.append(bm_c.verts.new((73.0 + math.cos(ang) * 7.6, -88.5 + math.sin(ang) * 7.6, z_canal_w)))
    for si in range(32):
        f = bm_c.faces.new((hb_c, hb_ring[si], hb_ring[(si + 1) % 32]))
        f.smooth = True
        for lp in f.loops:
            lp[uv_c].uv = (lp.vert.co.x * 0.06, lp.vert.co.y * 0.06)

    # 10 Alluvial-Seen & Dorf-Teiche (Wasserflaeche buendig innerhalb Uferlinie 1.005)
    for lk in ALLUVIAL_LAKES:
        vc = bm_c.verts.new((lk["cx"], lk["cy"], lk["zW"]))
        ring = []
        c_y, s_y = math.cos(lk["yaw"]), math.sin(lk["yaw"])
        for si in range(48):
            ang = (si / 48.0) * math.pi * 2.0
            lobe = 1.0 + 0.16 * math.sin(ang * 2.0 + lk["seed"]) + 0.09 * math.cos(ang * 3.0 - lk["seed"] * 1.7)
            lx = math.cos(ang) * lk["rx"] * lobe * 1.005
            ly = math.sin(ang) * lk["ry"] * lobe * 1.005
            wx = lk["cx"] + lx * c_y - ly * s_y
            wy = lk["cy"] + lx * s_y + ly * c_y
            ring.append(bm_c.verts.new((wx, wy, lk["zW"])))
        for si in range(48):
            f = bm_c.faces.new((vc, ring[si], ring[(si + 1) % 48]))
            f.smooth = True
            for lp in f.loops:
                lp[uv_c].uv = (lp.vert.co.x * 0.05, lp.vert.co.y * 0.05)

    bmesh.ops.triangulate(bm_c, faces=bm_c.faces[:])
    m_can = bpy.data.meshes.new("Water_Canals_And_Lakes_Mesh")
    bm_c.to_mesh(m_can)
    bm_c.free()
    m_can.materials.append(mat_riv)
    obj_can = bpy.data.objects.new("Water_Canals_And_Lakes", m_can)
    col_terrain.objects.link(obj_can)

    # C) Aquädukt-Wasserband (Quellbecken -> Rinne -> Bogen-Aquaedukt -> Endtrog)
    bm_aq = bmesh.new()
    uv_aq = bm_aq.loops.layers.uv.new("UVMap")
    src_base_z = 17.20 - 0.16
    src_water_z = src_base_z + 1.24 * 1.15        # 18.466
    src_spout_y = 92.60 - 2.90 * 1.15             # 89.265
    aq_y0, aq_z0 = 89.60, 18.22
    aq_y1, aq_z1 = 15.20, 14.20

    def add_water_quad(x0, x1, y0, y1, z0, z1):
        v0 = bm_aq.verts.new((x0, y0, z0))
        v1 = bm_aq.verts.new((x1, y0, z0))
        v2 = bm_aq.verts.new((x1, y1, z1))
        v3 = bm_aq.verts.new((x0, y1, z1))
        f = bm_aq.faces.new((v0, v1, v2, v3))
        f.smooth = True
        for lp in f.loops:
            lp[uv_aq].uv = (lp.vert.co.x * 0.25, lp.vert.co.y * 0.25)

    # Quellbecken-Wasserflaeche -> Auslauf -> direktes Gefaelle im 12-Bogen-Viadukt -> Zielbecken
    add_water_quad(58.0 - 1.72, 58.0 + 1.72, 92.60 - 1.35, 92.60 + 1.15, src_water_z, src_water_z)
    add_water_quad(58.0 - 0.48, 58.0 + 0.48, src_spout_y, 92.60 - 1.35, src_water_z - 0.02, src_water_z)
    add_water_quad(58.0 - 0.48, 58.0 + 0.48, 89.05, src_spout_y, aq_z0 + 0.22, src_water_z - 0.02)
    add_water_quad(58.0 - 0.48, 58.0 + 0.48, aq_y1 - 0.40, 89.05, aq_z1 + 0.22, aq_z0 + 0.22)
    bmesh.ops.triangulate(bm_aq, faces=bm_aq.faces[:])
    m_aq = bpy.data.meshes.new("Water_Aqueduct_Flow_Mesh")
    bm_aq.to_mesh(m_aq)
    bm_aq.free()
    m_aq.materials.append(mat_aqua)
    obj_aq = bpy.data.objects.new("Water_Aqueduct_Flow", m_aq)
    col_terrain.objects.link(obj_aq)

    print(f"    -> Terrain ({terrain_tris:,} Tris) + 4 Wasser-/Kanal-Meshes fertig in {time.time() - t0:.2f}s", flush=True)
    return [obj_terr, obj_riv, obj_can, obj_cb, obj_aq], terrain_tris


# ==============================================================================
# 3. STADTPFLASTER & NAHTLOSE AQUAEDUKT-RINNE / PFEILERSOCKEL
# ==============================================================================

def create_ur_stone_paving_and_walls(col_city):
    """Erzeugt scharf gekachelte Steinpflaster-Strassen, Agora-Platz & Hofmauern direkt an den Strassenraendern."""
    mat_plaza = bpy.data.materials.new("Mat_Ur_Stone_Paving")
    mat_plaza.use_nodes = True
    nt = mat_plaza.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord")
    t_alb = nt.nodes.new("ShaderNodeTexImage")
    t_alb.image = wbu.load_image_cached("terrain_plaza_albedo.png", "sRGB")
    t_nrm = nt.nodes.new("ShaderNodeTexImage")
    t_nrm.image = wbu.load_image_cached("terrain_plaza_normal.png", "Non-Color")
    t_orm = nt.nodes.new("ShaderNodeTexImage")
    t_orm.image = wbu.load_image_cached("terrain_plaza_orm.png", "Non-Color")
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nrm = nt.nodes.new("ShaderNodeNormalMap")
    nrm.inputs["Strength"].default_value = 0.8
    for t in (t_alb, t_nrm, t_orm):
        nt.links.new(tc.outputs["UV"], t.inputs["Vector"])
    nt.links.new(t_orm.outputs["Color"], sep.inputs["Color"])
    nt.links.new(t_nrm.outputs["Color"], nrm.inputs["Color"])
    nt.links.new(t_alb.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    nt.links.new(nrm.outputs["Normal"], bsdf.inputs["Normal"])

    bm = bmesh.new()
    uv_l = bm.loops.layers.uv.new("UVMap")

    def add_road_strip(pts, width, z_lift=0.045):
        samples = []
        for idx in range(len(pts) - 1):
            ax, ay = pts[idx]
            bx, by = pts[idx + 1]
            L = math.hypot(bx - ax, by - ay)
            steps = max(2, int(math.ceil(L / 1.5)))
            for k in range(0 if idx == 0 else 1, steps + 1):
                f = k / steps
                samples.append((ax + f * (bx - ax), ay + f * (by - ay)))
        hw = width * 0.5
        sk = hw + 0.35
        lat_off = (-sk, -hw, hw, sk)
        dz_off = (-0.12, z_lift, z_lift, -0.12)
        rings = []
        acc = 0.0
        for i, (cx, cy) in enumerate(samples):
            if i > 0:
                acc += math.hypot(cx - samples[i - 1][0], cy - samples[i - 1][1])
            p0 = samples[max(0, i - 1)]
            p1 = samples[min(len(samples) - 1, i + 1)]
            tx, ty = p1[0] - p0[0], p1[1] - p0[1]
            tl = max(1e-4, math.hypot(tx, ty))
            tx /= tl
            ty /= tl
            nx, ny = -ty, tx
            row = []
            for lo, dz in zip(lat_off, dz_off):
                wx, wy = cx + nx * lo, cy + ny * lo
                wz = eval_sy_z(wx, wy) + dz
                row.append((bm.verts.new((wx, wy, wz)), acc * 0.55, (lo + sk) / (2.0 * sk) * 2.2))
            rings.append(row)
        for i in range(len(rings) - 1):
            for c in range(3):
                v00, u00, v_00 = rings[i][c]
                v01, u01, v_01 = rings[i][c + 1]
                v11, u11, v_11 = rings[i + 1][c + 1]
                v10, u10, v_10 = rings[i + 1][c]
                f = bm.faces.new((v00, v01, v11, v10))
                f.smooth = True
                uvs = [(u00, v_00), (u01, v_01), (u11, v_11), (u10, v_10)]
                for lp, uv_c in zip(f.loops, uvs):
                    lp[uv_l].uv = uv_c

    def add_plaza_pad(cx, cy, w, d, nx=10, ny=8, z_lift=0.05):
        grid = []
        for iy in range(ny + 1):
            row = []
            for ix in range(nx + 1):
                wx = cx - w * 0.5 + (ix / nx) * w
                wy = cy - d * 0.5 + (iy / ny) * d
                wz = eval_sy_z(wx, wy) + z_lift
                row.append((bm.verts.new((wx, wy, wz)), (wx - (cx - w * 0.5)) * 0.55, (wy - (cy - d * 0.5)) * 0.55))
            grid.append(row)
        for iy in range(ny):
            for ix in range(nx):
                v00, u00, v_00 = grid[iy][ix]
                v10, u10, v_10 = grid[iy][ix + 1]
                v11, u11, v_11 = grid[iy + 1][ix + 1]
                v01, u01, v_01 = grid[iy + 1][ix]
                f = bm.faces.new((v00, v10, v11, v01))
                f.smooth = True
                for lp, uv_c in zip(f.loops, [(u00, v_00), (u10, v_10), (u11, v_11), (u01, v_01)]):
                    lp[uv_l].uv = uv_c

    for pts, w in FLAGSTONE_ROADS:
        add_road_strip(pts, w, 0.055)
    add_plaza_pad(169.8, -48.0, 24.4, 16.6, 12, 8, 0.06)
    add_plaza_pad(125.0, -48.0, 11.5, 14.5, 5, 6, 0.05)
    add_plaza_pad(184.0, 32.5, 18.0, 7.5, 8, 4, 0.05)
    add_plaza_pad(184.0, -134.5, 18.0, 7.5, 8, 4, 0.05)
    add_plaza_pad(233.5, -48.0, 9.5, 22.0, 5, 10, 0.05)
    add_plaza_pad(210.0, -24.0, 26.0, 24.0, 10, 10, 0.05)

    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    m_pave = bpy.data.meshes.new("Ur_Flagstone_Streets_Mesh")
    bm.to_mesh(m_pave)
    bm.free()
    m_pave.materials.append(mat_plaza)
    obj_pave = bpy.data.objects.new("Ur_Flagstone_Streets_And_Agora", m_pave)
    col_city.objects.link(obj_pave)


def create_aqueduct_masonry_connectors(col_aqua, linker):
    """Baut geerdete Basalt-Quellstuetze, buendige Pfeilerfundamente unter allen 13 Auflagern & das Verteiler-Postament."""
    # Nutze exakt das verlinkte Material 'Mat_Shipyard_Industry_Trim' vom Aquaedukt-Kit!
    src_mesh = linker.link_mesh("world/shipyard_industry_kit.blend", "sy_aqueduct_pier_span_LOD0")
    trim_mat = src_mesh.materials[0]

    aq_y0, aq_z0 = 89.60, 18.22
    aq_y1, aq_z1 = 15.20, 14.20

    # Exakte Trim-Regionen aus build_shipyard_trim_atlas.py (verhindert Streifen-/Band-Bleed!):
    UV_REGIONS = {
        "cedar": (0.02, 0.98, 0.388, 0.488),
        "bitumen": (0.738, 0.846, 0.888, 0.988),
        "basalt": (0.02, 0.98, 0.012, 0.112),
    }

    bm = bmesh.new()
    uv_l = bm.loops.layers.uv.new("UVMap")

    def add_box_uv(cx, cy, cz, sx, sy, sz, reg_key, rx=0.0):
        res = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=res["verts"])
        if abs(rx) > 1e-6:
            bmesh.ops.rotate(bm, verts=res["verts"], matrix=Matrix.Rotation(rx, 3, "X"))
        bmesh.ops.translate(bm, vec=(cx, cy, cz), verts=res["verts"])
        u0, u1, v0, v1 = UV_REGIONS[reg_key]
        faces = set()
        for v in res["verts"]:
            for f in v.link_faces:
                faces.add(f)
        for f in faces:
            n = f.normal
            for lp in f.loops:
                p = lp.vert.co
                if abs(n.z) > 0.7:
                    raw_u, raw_v = p.x * 0.28, p.y * 0.28
                elif abs(n.x) > abs(n.y):
                    raw_u, raw_v = p.y * 0.28, p.z * 0.45
                else:
                    raw_u, raw_v = p.x * 0.28, p.z * 0.45
                fu = raw_u % 1.0
                tv = raw_v % 2.0
                fv = tv if tv <= 1.0 else (2.0 - tv)
                lp[uv_l].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))

    # 1) Gestuftes Basalt-Quellwiderlager direkt unter dem Quellauslauf (y = 89.80..91.20)
    gr_abut = eval_sy_z(58.0, 90.0)
    abut_top_z = 17.28
    if abut_top_z > gr_abut - 0.4:
        h_abut = max(1.2, abut_top_z - gr_abut + 1.0)
        add_box_uv(58.0, 90.15, gr_abut - 0.85 + h_abut * 0.5, 4.40, 1.80, h_abut, "basalt")

    # 2) Passgenaue, gestufte Basalt-Pfeilersockel unter allen 13 Auflagerachsen des 12-Bogen-Viadukts
    #    Einzelpfeiler: 1.95 x 1.45 m -> Sockel 2.08 x 1.68 m; Zwillingspfeiler am Stoss: 1.95 x 2.95 m -> Sockel 2.08 x 3.16 m
    num_spans = 12
    span_step = (aq_y0 - aq_y1) / num_spans  # 6.20 m
    for pi in range(num_spans + 1):
        py_joint = aq_y0 - pi * span_step
        if pi == 0:
            py = py_joint - 0.75
            sh_sx, sh_sy = 2.08, 1.68
            cp_sx, cp_sy = 2.24, 1.84
        elif pi == num_spans:
            py = py_joint + 0.75
            sh_sx, sh_sy = 2.08, 1.68
            cp_sx, cp_sy = 2.24, 1.84
        else:
            py = py_joint
            sh_sx, sh_sy = 2.08, 3.16
            cp_sx, cp_sy = 2.24, 3.30

        bf = (aq_y0 - py) / (aq_y0 - aq_y1)
        pier_top_z = (aq_z0 + bf * (aq_z1 - aq_z0)) - 4.78 - 0.14
        gr_z = min(eval_sy_z(58.0, py), eval_sy_z(57.0, py), eval_sy_z(59.0, py))
        if pier_top_z > gr_z - 0.25:
            cap_h = 0.26
            shaft_top_z = pier_top_z - cap_h
            shaft_h = max(0.8, shaft_top_z - (gr_z - 0.85))
            add_box_uv(58.0, py, (gr_z - 0.85) + shaft_h * 0.5, sh_sx, sh_sy, shaft_h, "basalt")
            add_box_uv(58.0, py, pier_top_z - cap_h * 0.5, cp_sx, cp_sy, cap_h, "basalt")

    # 3) Massives Basalt-Zisternenpostament + Zwillings-Ablassrohre am Verteilerbecken (58.0, 14.40)
    gr_term = min(eval_sy_z(58.0, 14.40), eval_sy_z(56.2, 13.40), eval_sy_z(59.8, 13.40))
    term_top_z = aq_z1 - 0.74
    term_h = max(2.0, term_top_z - (gr_term - 0.85))
    add_box_uv(58.0, 14.40, (gr_term - 0.85) + term_h * 0.5, 3.90, 2.30, term_h, "basalt")
    add_box_uv(58.0, 14.40, term_top_z - 0.14, 4.10, 2.50, 0.28, "basalt")
    for dx_p in (-0.52, 0.52):
        gr_end = eval_sy_z(58.0 + dx_p, 13.18)
        h_pipe = max(2.0, aq_z1 - 0.25 - gr_end + 0.3)
        add_box_uv(58.0 + dx_p, 13.18, gr_end - 0.2 + h_pipe * 0.5, 0.32, 0.28, h_pipe, "cedar")

    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    m_conn = bpy.data.meshes.new("Aqueduct_Chute_And_Pier_Plinths_Mesh")
    bm.to_mesh(m_conn)
    bm.free()
    m_conn.materials.append(trim_mat)
    obj_conn = bpy.data.objects.new("Aqueduct_Chute_And_Pier_Plinths", m_conn)
    col_aqua.objects.link(obj_conn)


def build_authentic_shipyard_landmarks(col_shipyard, col_suburbs, linker, z_canal_w):
    """Erzeugt Trockendock-Spundwand, Grundschwellen/Kimmpallen, Holzhafen-Kai, Wachturm, Seilerbahn & Baudorf-Details."""
    src_mesh = linker.link_mesh("world/shipyard_industry_kit.blend", "sy_aqueduct_pier_span_LOD0")
    trim_mat = src_mesh.materials[0]
    pave_mat = bpy.data.materials.get("Mat_Ur_Stone_Paving") or trim_mat

    UV_REGIONS = {
        "basalt": (0.02, 0.98, 0.012, 0.112),
        "cedar": (0.02, 0.98, 0.388, 0.488),
        "oak": (0.02, 0.98, 0.512, 0.612),
        "thatch": (0.40, 0.70, 0.762, 0.862),
        "rope": (0.015, 0.28, 0.888, 0.988),
        "bronze": (0.32, 0.50, 0.888, 0.988),
        "earth": (0.02, 0.98, 0.262, 0.362),
    }

    bm = bmesh.new()
    uv_l = bm.loops.layers.uv.new("UVMap")

    def add_box(cx, cy, cz, sx, sy, sz, reg="oak", rx=0.0, ry=0.0, rz=0.0):
        res = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=res["verts"])
        if abs(rx) > 1e-6 or abs(ry) > 1e-6 or abs(rz) > 1e-6:
            mat_r = (Matrix.Rotation(rz, 3, "Z") @ Matrix.Rotation(ry, 3, "Y") @ Matrix.Rotation(rx, 3, "X"))
            bmesh.ops.rotate(bm, verts=res["verts"], matrix=mat_r)
        bmesh.ops.translate(bm, vec=(cx, cy, cz), verts=res["verts"])
        u0, u1, v0, v1 = UV_REGIONS[reg]
        faces = {f for v in res["verts"] for f in v.link_faces}
        for f in faces:
            n = f.normal
            for lp in f.loops:
                p = lp.vert.co
                if abs(n.z) > 0.7:
                    ru, rv = p.x * 0.32, p.y * 0.32
                elif abs(n.x) > abs(n.y):
                    ru, rv = p.y * 0.32, p.z * 0.45
                else:
                    ru, rv = p.x * 0.32, p.z * 0.45
                fu = ru % 1.0
                tv = rv % 2.0
                fv = tv if tv <= 1.0 else (2.0 - tv)
                lp[uv_l].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))

    def add_beam(p0, p1, r0, r1, reg="cedar", segs=6):
        dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
        L = math.sqrt(dx * dx + dy * dy + dz * dz)
        if L < 1e-4:
            return
        res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r0, radius2=r1, depth=L)
        dir_v = Vector((dx, dy, dz)).normalized()
        rot_q = Vector((0, 0, 1)).rotation_difference(dir_v)
        bmesh.ops.rotate(bm, verts=res["verts"], matrix=rot_q.to_matrix())
        mid = (0.5 * (p0[0] + p1[0]), 0.5 * (p0[1] + p1[1]), 0.5 * (p0[2] + p1[2]))
        bmesh.ops.translate(bm, vec=mid, verts=res["verts"])
        u0, u1, v0, v1 = UV_REGIONS[reg]
        faces = {f for v in res["verts"] for f in v.link_faces}
        for f in faces:
            for lp in f.loops:
                p = lp.vert.co
                fu = ((p.x + p.y) * 0.35) % 1.0
                tv = (p.z * 0.45) % 2.0
                fv = tv if tv <= 1.0 else (2.0 - tv)
                lp[uv_l].uv = (u0 + fu * (u1 - u0), v0 + fv * (v1 - v0))

    # 1) Trockendock-Holz-Spundwand + Sued-Fluegelwaende + 15 Grundschwellen + 22 Kimmpallen
    add_box(0.0, 18.02, 0.20, 152.0, 0.24, 2.20, "oak")
    add_box(-44.075, -18.02, 0.20, 61.85, 0.24, 2.20, "oak")
    add_box(39.075, -18.02, 0.20, 71.85, 0.24, 2.20, "oak")
    for px in range(-74, 75, 4):
        add_beam((px, 17.88, -1.05), (px, 17.88, 1.44), 0.14, 0.16, "cedar", 6)
        if px < -13.2 or px > 3.2:
            add_beam((px, -17.88, -1.05), (px, -17.88, 1.44), 0.14, 0.16, "cedar", 6)
    for wx in (-13.15, 3.15):
        add_beam((wx, -18.02, -1.05), (wx, -18.02, 1.50), 0.15, 0.17, "cedar", 6)
        for wy in (-20.0, -24.0, -28.0, -32.0, -36.0):
            gz_out = eval_sy_z(wx + (-0.9 if wx < 0 else 0.9), wy)
            w_top = max(1.26, gz_out + 0.35)
            add_box(wx, wy, (-1.05 + w_top) * 0.5, 0.24, 4.05, w_top + 1.05, "oak")
            x_in = wx + (0.15 if wx < 0 else -0.15)
            add_beam((x_in, wy - 2.0, -1.15), (x_in, wy - 2.0, w_top + 0.18), 0.13, 0.14, "cedar", 6)
    for xs in range(-70, 71, 10):
        if abs(xs) <= 51:
            add_box(xs, 0.0, -0.70, 1.40, 20.0, 0.30, "oak")
        if -50 <= xs <= 50:
            add_beam((xs, -14.2, -0.75), (xs, -11.55, 1.65), 0.16, 0.14, "oak", 6)
            add_beam((xs, 14.2, -0.75), (xs, 11.55, 1.65), 0.16, 0.14, "oak", 6)
    for ap_x in (-10.6, 0.6):
        ap_z = eval_sy_z(ap_x, -43.0)
        add_box(ap_x, -43.0, ap_z + 0.40, 0.70, 0.70, 0.85, "basalt")
        add_beam((ap_x, -43.0, ap_z + 0.82), (ap_x, -43.0, ap_z + 1.15), 0.22, 0.34, "bronze", 8)

    # 2) Werft-Holzhafenbecken (73, -88.5): Hafenkran, Basaltpoller & 10-Stamm-Zedernfloss
    hq_nw = eval_sy_z(65.0, -83.5)
    for px, py in ((64.2, -82.0), (69.5, -81.0), (63.8, -89.5), (64.2, -93.5)):
        pz = eval_sy_z(px, py)
        add_beam((px, py, pz - 0.15), (px, py, pz + 0.68), 0.22, 0.18, "basalt", 8)
    cr_z = eval_sy_z(64.2, -87.5)
    add_box(64.2, -87.5, cr_z + 0.20, 1.85, 1.85, 0.60, "basalt")
    add_beam((64.2, -87.5, cr_z + 0.3), (64.2, -87.5, cr_z + 6.5), 0.25, 0.20, "oak", 8)
    add_beam((64.2, -87.5, cr_z + 2.2), (70.2, -88.0, cr_z + 5.2), 0.18, 0.14, "oak", 8)
    add_beam((64.2, -87.5, cr_z + 6.2), (70.2, -88.0, cr_z + 5.2), 0.10, 0.08, "oak", 6)
    add_beam((70.2, -88.0, cr_z + 5.2), (70.2, -88.0, z_canal_w + 1.55), 0.03, 0.03, "rope", 5)
    add_beam((68.8, -90.6, z_canal_w + 1.48), (71.6, -85.4, z_canal_w + 1.56), 0.34, 0.32, "cedar", 8)
    for li in range(8):
        lx_f = 71.2 + (li - 3.5) * 0.38
        add_beam((lx_f, -92.2, z_canal_w + 0.06), (lx_f, -85.8, z_canal_w + 0.06), 0.16, 0.15, "cedar", 6)
    add_beam((69.6, -90.5, z_canal_w + 0.22), (72.8, -90.5, z_canal_w + 0.22), 0.10, 0.10, "oak", 6)
    add_beam((69.6, -87.2, z_canal_w + 0.22), (72.8, -87.2, z_canal_w + 0.22), 0.10, 0.10, "oak", 6)
    add_box(67.2, -80.4, hq_nw + 0.55, 4.2, 1.4, 0.14, "oak", rz=0.12)
    add_beam((65.4, -80.2, hq_nw + 0.80), (69.0, -79.8, hq_nw + 0.80), 0.24, 0.24, "cedar", 8)
    add_beam((65.5, -80.8, hq_nw + 0.80), (69.1, -80.4, hq_nw + 0.80), 0.24, 0.24, "cedar", 8)

    # 3) Baudorf Schinar: 9.5-m-Wachturm (90,-26), Dorfbrunnen (101.5,-41.5), 3 Tannurs (114.2,-53.8), Stellmacherei (84.5,-31.5)
    tw_x, tw_y = 90.0, -26.0
    tw_z = eval_sy_z(tw_x, tw_y)
    for px_o, py_o in ((-1.35, -1.35), (1.35, -1.35), (-1.35, 1.35), (1.35, 1.35)):
        add_beam((tw_x + px_o, tw_y + py_o, tw_z - 0.35), (tw_x + px_o * 0.78, tw_y + py_o * 0.78, tw_z + 6.45), 0.15, 0.12, "oak", 6)
        add_beam((tw_x + px_o * 0.78, tw_y + py_o * 0.78, tw_z + 6.45), (tw_x + px_o * 0.78, tw_y + py_o * 0.78, tw_z + 8.95), 0.10, 0.09, "oak", 6)
    for lz in (2.2, 4.4):
        add_box(tw_x, tw_y, tw_z + lz, 2.55 - lz * 0.08, 2.55 - lz * 0.08, 0.16, "oak")
    add_box(tw_x, tw_y, tw_z + 6.45, 2.75, 2.75, 0.18, "cedar")
    add_box(tw_x, tw_y, tw_z + 9.22, 3.10, 3.10, 0.38, "thatch")
    add_box(tw_x, tw_y, tw_z + 9.52, 1.85, 1.85, 0.26, "thatch")
    add_beam((tw_x + 0.85, tw_y + 0.75, tw_z + 6.54), (tw_x + 0.85, tw_y + 0.75, tw_z + 7.28), 0.22, 0.34, "bronze", 8)

    wl_x, wl_y = 101.5, -41.5
    wl_z = eval_sy_z(wl_x, wl_y)
    add_beam((wl_x, wl_y, wl_z - 0.25), (wl_x, wl_y, wl_z + 0.56), 1.15, 1.12, "basalt", 12)
    add_beam((wl_x - 0.95, wl_y, wl_z + 0.56), (wl_x - 0.95, wl_y, wl_z + 2.35), 0.08, 0.07, "oak", 6)
    add_beam((wl_x + 0.95, wl_y, wl_z + 0.56), (wl_x + 0.95, wl_y, wl_z + 2.35), 0.08, 0.07, "oak", 6)
    add_box(wl_x, wl_y, wl_z + 2.45, 2.35, 1.15, 0.12, "oak")
    add_box(wl_x, wl_y, wl_z + 2.62, 2.50, 1.35, 0.24, "thatch")

    for ox, oy in ((114.2, -53.8), (116.0, -54.7), (114.8, -52.1)):
        oz = eval_sy_z(ox, oy)
        add_box(ox, oy, oz + 0.18, 1.45, 1.45, 0.56, "basalt")
        add_beam((ox, oy, oz + 0.42), (ox, oy, oz + 1.45), 0.42, 0.62, "earth", 10)
    for tx, ty in ((105.5, -54.0), (106.2, -40.2)):
        tz = eval_sy_z(tx, ty)
        add_box(tx, ty, tz + 0.78, 3.40, 1.05, 0.10, "cedar")
        add_box(tx, ty - 0.82, tz + 0.42, 3.20, 0.32, 0.12, "oak")
        add_box(tx, ty + 0.82, tz + 0.42, 3.20, 0.32, 0.12, "oak")
    ww_x, ww_y = 84.5, -31.5
    ww_z = eval_sy_z(ww_x, ww_y)
    add_box(ww_x, ww_y, ww_z + 0.45, 1.55, 0.55, 0.90, "oak")
    add_beam((ww_x, ww_y, ww_z + 0.86), (ww_x, ww_y, ww_z + 1.18), 0.76, 0.76, "oak", 10)

    # 4) 45-m-Seilerbahn (-106.5..-63.5, y=52.5) & 6 NW-Holzfaellerhuetten + Gefaellter 20-m-Zedernstamm
    rw_y, rw_x0, rw_x1 = 52.5, -106.5, -63.5
    rw_z0, rw_z1 = eval_sy_z(rw_x0, rw_y), eval_sy_z(rw_x1, rw_y)
    for ry_o in (-1.15, 1.15):
        add_beam((rw_x0, rw_y + ry_o, rw_z0 - 0.25), (rw_x0, rw_y + ry_o, rw_z0 + 2.55), 0.11, 0.10, "oak", 6)
        add_beam((rw_x0 + 1.8, rw_y + ry_o, rw_z0 - 0.25), (rw_x0 + 1.8, rw_y + ry_o, rw_z0 + 2.55), 0.11, 0.10, "oak", 6)
    add_box(rw_x0 + 0.9, rw_y, rw_z0 + 2.60, 2.35, 2.75, 0.12, "oak")
    add_box(rw_x0 + 0.9, rw_y, rw_z0 + 2.80, 2.65, 3.05, 0.28, "thatch")
    for st in range(8):
        sx = rw_x0 + 4.5 + st * 4.8
        sz = eval_sy_z(sx, rw_y)
        add_beam((sx, rw_y - 0.92, sz - 0.20), (sx, rw_y - 0.92, sz + 1.32), 0.06, 0.05, "oak", 5)
        add_beam((sx, rw_y + 0.92, sz - 0.20), (sx, rw_y + 0.92, sz + 1.32), 0.06, 0.05, "oak", 5)
        add_box(sx, rw_y, sz + 1.22, 0.10, 1.98, 0.10, "oak")
    add_box(rw_x1, rw_y, rw_z1 + 0.22, 2.20, 1.45, 0.22, "oak")
    add_box(rw_x1 - 0.35, rw_y - 0.20, rw_z1 + 0.54, 0.85, 0.72, 0.46, "basalt")
    for rx_r, ry_r in ((-109.2, 49.0), (-62.0, 49.0)):
        rz_r = eval_sy_z(rx_r, ry_r)
        add_box(rx_r - 0.65, ry_r, rz_r + 0.48, 0.14, 1.0, 0.96, "oak")
        add_box(rx_r + 0.65, ry_r, rz_r + 0.48, 0.14, 1.0, 0.96, "oak")
        add_beam((rx_r, ry_r - 0.48, rz_r + 0.62), (rx_r, ry_r + 0.48, rz_r + 0.62), 0.54, 0.54, "rope", 12)
    add_beam((rw_x0 + 0.45, rw_y, rw_z0 + 1.25), (rw_x1, rw_y, rw_z1 + 0.95), 0.07, 0.07, "rope", 6)

    nw_cabins = [
        (-102.0, 41.5, 4.4, 3.4, 0.12), (-92.5, 43.0, 4.2, 3.2, -0.18), (-81.5, 41.0, 4.6, 3.5, 0.08),
        (-99.0, 32.5, 4.5, 3.4, -0.25), (-87.5, 31.5, 4.2, 3.2, 0.22), (-75.5, 33.0, 4.4, 3.4, -0.12),
    ]
    for hx, hy, hw, hd, hyaw in nw_cabins:
        hz = eval_sy_z(hx, hy)
        add_box(hx, hy, hz - 0.12, hw + 0.28, hd + 0.28, 0.72, "basalt", rz=hyaw)
        add_box(hx, hy, hz + 1.18, hw, hd, 2.15, "cedar", rz=hyaw)
        add_box(hx, hy, hz + 2.38, hw + 0.65, hd + 0.65, 0.34, "thatch", rz=hyaw)
        add_box(hx, hy, hz + 2.66, hw * 0.68, hd * 0.68, 0.28, "thatch", rz=hyaw)

    fz0 = eval_sy_z(-138.0, -96.0) + 0.65
    fz1 = eval_sy_z(-122.0, -84.0) + 0.52
    add_beam((-138.0, -96.0, fz0), (-122.0, -84.0, fz1), 0.68, 0.52, "cedar", 10)
    st_z = eval_sy_z(-139.2, -96.8)
    add_beam((-139.2, -96.8, st_z - 0.1), (-139.2, -96.8, st_z + 1.35), 0.85, 0.72, "cedar", 10)

    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    m_lm = bpy.data.meshes.new("Shipyard_Authentic_Landmarks_Mesh")
    bm.to_mesh(m_lm)
    bm.free()
    m_lm.materials.append(trim_mat)
    obj_lm = bpy.data.objects.new("Shipyard_Authentic_Landmarks", m_lm)
    col_shipyard.objects.link(obj_lm)

    # Travertin-Kais & Dorfbrunnen-Pflaster (Holzhafen + Baudorf)
    bm_q = bmesh.new()
    uv_q = bm_q.loops.layers.uv.new("UVMap")

    def add_stone_pad(cx, cy, cz, sx, sy, sz, yaw=0.0):
        res = bmesh.ops.create_cube(bm_q, size=1.0)
        bmesh.ops.scale(bm_q, vec=(sx, sy, sz), verts=res["verts"])
        if abs(yaw) > 1e-6:
            bmesh.ops.rotate(bm_q, verts=res["verts"], matrix=Matrix.Rotation(yaw, 3, "Z"))
        bmesh.ops.translate(bm_q, vec=(cx, cy, cz), verts=res["verts"])
        faces = {f for v in res["verts"] for f in v.link_faces}
        for f in faces:
            for lp in f.loops:
                p = lp.vert.co
                lp[uv_q].uv = (p.x * 0.5, p.y * 0.5)

    add_stone_pad(66.5, -80.2, hq_nw + 0.12, 13.0, 3.2, 0.72, 0.12)
    add_stone_pad(62.6, -87.5, hq_nw + 0.12, 3.4, 12.5, 0.72, 0.08)
    add_stone_pad(101.5, -41.5, wl_z - 0.08, 8.8, 7.2, 0.24, 0.0)
    for ap_x in (-10.6, 0.6):
        ap_z = eval_sy_z(ap_x, -45.5)
        add_stone_pad(ap_x, -45.5, ap_z + 0.02, 2.2, 7.5, 0.18, -0.10 if ap_x < -5 else 0.10)

    bmesh.ops.triangulate(bm_q, faces=bm_q.faces[:])
    m_q = bpy.data.meshes.new("Shipyard_Quays_And_Plazas_Mesh")
    bm_q.to_mesh(m_q)
    bm_q.free()
    m_q.materials.append(pave_mat)
    obj_q = bpy.data.objects.new("Shipyard_Quays_And_Plazas", m_q)
    col_suburbs.objects.link(obj_q)


# ==============================================================================
# 4. WELT-BAUGRUPPEN PLATZIEREN (ALLE KITS VERLINKT)
# ==============================================================================

def populate_shipyard_world(scene):
    t_start = time.time()
    linker = wbu.AssetLinker()
    layout_records = []

    col_terrain = wbu.get_or_create_collection("01_Terrain_And_Water")
    col_ark = wbu.get_or_create_collection("02_Ark_Placeholder")
    col_shipyard = wbu.get_or_create_collection("03_Shipyard_Industry")
    col_aqueduct = wbu.get_or_create_collection("04_Aqueduct_Valley")
    col_city = wbu.get_or_create_collection("05_Ur_Schinar_City")
    col_suburbs = wbu.get_or_create_collection("06_Suburbs_And_Villages")
    col_river_infra = wbu.get_or_create_collection("07_Rivers_Canals_Boats")
    col_trees = wbu.get_or_create_collection("08_Botany_Trees")
    col_understory = wbu.get_or_create_collection("09_Botany_Crops_Shrubs_Grass")
    col_lighting = wbu.get_or_create_collection("10_Lighting_And_Cameras")

    # 1) Heightmap & Splatmap + Terrain & Wasser
    splat_png, _ = build_shipyard_heightmap_and_splatmap()
    terrain_export_objs, terrain_tris = create_shipyard_terrain_and_water(col_terrain, splat_png)

    # 2) Arche-Platzhalter (140 x 23.333 x 14 m auf Z = 0.0)
    wbu.build_ark_placeholder(col_ark, z_sole=0.0)

    # 3) Werftplatz & Industrie (shipyard_industry_kit.blend)
    print("[3/6] Platziere verlinkte Werft-, Aquädukt- & Fluss-Module...", flush=True)
    SY_BLEND = "world/shipyard_industry_kit.blend"

    # 45 Kreuzstapel unter der Arche
    for xs in range(-70, 71, 10):
        for yk in (-8.167, 0.0, 8.167):
            linker.spawn(col_shipyard, SY_BLEND, "sy_cribbing_block_LOD0", "sy_cribbing_block",
                         (xs, yk, -0.58), (0, 0, 0), (0.72, 0.72, 0.39), layout_records=layout_records)

    # 60-Ellen-Rampe + Zugbrueckenklappe
    for rk in range(5):
        linker.spawn(col_shipyard, SY_BLEND, "sy_ramp_module_LOD0", "sy_ramp_module",
                     (-5.0, -41.5 + (rk + 0.5) * 5.60, -0.70 - 0.146 + rk * 1.46),
                     (0, 0, 0), (1.25, 0.9333, 0.73), layout_records=layout_records)
    linker.spawn(col_shipyard, SY_BLEND, "sy_drawbridge_flap_LOD0", "sy_drawbridge_flap",
                 (-5.0, -13.5, 6.60), (0, 0, 0), (1.25, 1.0, 1.0), layout_records=layout_records)

    # 12 Geruestjoche Backbord & Steuerbord
    for gx in (-54.0, -32.0, -12.0, 12.0, 32.0, 54.0):
        for side, sy_pos, yaw in ((-1, -13.2, 0.0), (1, 13.2, math.pi)):
            linker.spawn(col_shipyard, SY_BLEND, "sy_scaffold_bay_LOD0", "sy_scaffold_bay",
                         (gx, sy_pos, -0.85), (0, 0, yaw), (1.35, 1.15, 1.38), layout_records=layout_records)

    # 4 Schwere A-Bock-Krane + Spillwinden + Lasten
    for cx, cy, sgn in ((-42.0, -23.5, -1), (42.0, -23.5, -1), (-42.0, 23.5, 1), (42.0, 23.5, 1)):
        z_cr = eval_sy_z(cx, cy)
        c_yaw = 0.0 if sgn < 0 else math.pi
        c_y = cy - sgn * 1.4
        linker.spawn(col_shipyard, SY_BLEND, "sy_crane_aframe_LOD0", "sy_crane_aframe",
                     (cx, c_y, z_cr), (0, 0, c_yaw), (1.95, 1.95, 1.95), layout_records=layout_records)
        linker.spawn(col_shipyard, SY_BLEND, "sy_crane_winch_rotor_LOD0", "sy_crane_winch_rotor",
                     (cx, cy, z_cr + 1.25), (0, 0, c_yaw), (1.25, 1.25, 1.25), layout_records=layout_records)
        linker.spawn(col_shipyard, SY_BLEND, "sy_crane_timber_load_LOD0", "sy_crane_timber_load",
                     (cx, cy - sgn * 3.8, z_cr + 10.2), (0, 0, c_yaw), (1.4, 1.4, 1.4), layout_records=layout_records)

    # 3 Kopher-Pechsiedeoefen
    for pi, (px, py) in enumerate(((-55.0, 36.0), (-32.0, 40.0), (-10.0, 36.0))):
        linker.spawn(col_shipyard, SY_BLEND, "sy_pitch_kiln_LOD0", "sy_pitch_kiln",
                     (px, py, eval_sy_z(px, py)), (0, 0, (pi - 1) * 0.25), (1.35, 1.35, 1.35), layout_records=layout_records)

    # Tubal-Kain-Schmiede & 4 Holzkohlemeiler
    linker.spawn(col_shipyard, SY_BLEND, "sy_smithy_forge_LOD0", "sy_smithy_forge",
                 (22.0, 44.0, eval_sy_z(22.0, 44.0)), (0, 0, -0.3), (1.25, 1.25, 1.25), layout_records=layout_records)
    for ki, (kx, ky) in enumerate(((30.0, 54.0), (86.0, 54.0), (78.0, 58.0), (92.0, 64.0))):
        linker.spawn(col_shipyard, SY_BLEND, "sy_charcoal_kiln_LOD0", "sy_charcoal_kiln",
                     (kx, ky, eval_sy_z(kx, ky)), (0, 0, ki * 0.7), (1.20, 1.20, 1.20), layout_records=layout_records)

    # Goepel-Saegewerk (-68, -58) & 2 Saegegruben (36, -48)
    z_saw = eval_sy_z(-68.0, -58.0)
    linker.spawn(col_shipyard, SY_BLEND, "sy_sawmill_base_LOD0", "sy_sawmill_base", (-68.0, -58.0, z_saw), layout_records=layout_records)
    linker.spawn(col_shipyard, SY_BLEND, "sy_sawmill_capstan_rotor_LOD0", "sy_sawmill_capstan_rotor", (-68.0, -58.0, z_saw), layout_records=layout_records)
    linker.spawn(col_shipyard, SY_BLEND, "sy_sawmill_driveshaft_LOD0", "sy_sawmill_driveshaft", (-64.5, -58.0, z_saw + 2.6), layout_records=layout_records)
    linker.spawn(col_shipyard, SY_BLEND, "sy_sawmill_frame_LOD0", "sy_sawmill_frame", (-61.8, -58.0, z_saw + 0.5), layout_records=layout_records)
    linker.spawn(col_shipyard, SY_BLEND, "sy_sawmill_pitman_LOD0", "sy_sawmill_pitman", (-61.8, -58.0, z_saw + 1.2), layout_records=layout_records)
    for spx, spy in ((33.5, -48.0), (39.5, -48.0)):
        linker.spawn(col_shipyard, SY_BLEND, "sy_sawpit_shed_LOD0", "sy_sawpit_shed",
                     (spx, spy, eval_sy_z(spx, spy)), (0, 0, 0.1), layout_records=layout_records)

    # 4 Meisterzelte & 3 Raubtier-Rollkaefige
    for tx, ty, tyaw in ((62.0, -35.5, 0.10), (78.0, -46.0, -0.12), (48.0, -67.5, 0.22), (68.0, -64.5, -0.14)):
        linker.spawn(col_shipyard, SY_BLEND, "sy_tent_worker_LOD0", "sy_tent_worker",
                     (tx, ty, eval_sy_z(tx, ty)), (0, 0, tyaw), (1.05, 1.05, 1.05), layout_records=layout_records)
    for cx_c in (8.5, 12.0, 15.5):
        linker.spawn(col_shipyard, SY_BLEND, "sy_cage_rolling_LOD0", "sy_cage_rolling",
                     (cx_c, -42.0, eval_sy_z(cx_c, -42.0)), (0, 0, 0.05), layout_records=layout_records)

    # Holzriese (-119.5,-98.8 -> -95.5,-78.8) & 11 Holzstapel
    chute_yaw = math.atan2(20.0, 24.0) - math.pi * 0.5
    for si in range(5):
        f = (si + 0.5) / 5.0
        cx_ch = -119.5 + f * 24.0
        cy_ch = -98.8 + f * 20.0
        linker.spawn(col_shipyard, SY_BLEND, "sy_timber_chute_segment_LOD0", "sy_timber_chute_segment",
                     (cx_ch, cy_ch, eval_sy_z(cx_ch, cy_ch)), (0, 0, chute_yaw), layout_records=layout_records)
    log_stacks = [
        (-62.0, -16.1, 0.03), (64.5, -16.1, -0.04), (-62.0, 16.1, -0.02), (64.5, 16.1, 0.04),
        (-53.5, -51.5, 0.14), (-53.0, -64.5, -0.18), (26.0, -57.5, 0.05), (26.0, -63.5, -0.09),
        (-55.0, -41.5, 0.12), (-46.0, -56.5, -0.09), (43.5, -57.5, 0.08),
    ]
    for lx, ly, lyaw in log_stacks:
        linker.spawn(col_shipyard, SY_BLEND, "sy_log_stack_LOD0", "sy_log_stack",
                     (lx, ly, eval_sy_z(lx, ly)), (0, 0, lyaw), (1.15, 1.05, 1.1), layout_records=layout_records)

    # 4) Quellbecken + nahtloser 12-Bogen-Viadukt (~3 Grad Gleichmaessiggefaelle, x = 58.0)
    src_gz = eval_sy_z(58.0, 92.60)
    linker.spawn(col_aqueduct, SY_BLEND, "sy_aqueduct_source_LOD0", "sy_aqueduct_source",
                 (58.0, 92.60, src_gz - 0.16), (0, 0, math.pi), (1.04, 1.15, 1.15), layout_records=layout_records)
    # Natuerliche Findlinge rund um die Quellfassung in der Schlucht
    boulder_spots = [
        (53.4, 94.6, 1.20, 0.4), (52.6, 92.2, 0.92, 1.8), (62.6, 94.4, 1.15, 2.5), (63.0, 92.0, 0.95, 0.9),
        (55.4, 97.2, 1.30, 3.1), (60.6, 97.2, 1.28, 1.2), (58.0, 98.4, 1.50, 0.2), (56.0, 100.0, 1.20, 2.1),
        (60.0, 99.8, 1.15, 4.0), (50.6, 89.2, 1.25, 1.4), (64.4, 89.0, 1.25, 2.7),
    ]
    for bi, (bx, by, bsc, byaw) in enumerate(boulder_spots):
        r_b = 0.55 * bsc
        bz = min(eval_sy_z(bx, by), eval_sy_z(bx - r_b, by), eval_sy_z(bx + r_b, by), eval_sy_z(bx, by - r_b))
        b_key = f"world_boulder_0{(bi % 3) + 1}"
        linker.spawn(col_aqueduct, SY_BLEND, f"{b_key}_LOD0", b_key,
                     (bx, by, bz - 0.34 * bsc), (0, 0, byaw), (bsc * 1.15, bsc * 1.15, bsc * 0.76), layout_records=layout_records)

    aq_y0, aq_z0 = 89.60, 18.22
    aq_y1, aq_z1 = 15.20, 14.20
    aq_slope = math.atan2(aq_z0 - aq_z1, aq_y0 - aq_y1)
    span_step = (aq_y0 - aq_y1) / 12.0
    # Exakte Rotationsmatrix: R_x(+aq_slope) * R_z(+pi/2) -> lokale +X Achse zeigt nach +Y und steigt um aq_slope an!
    eul_aq = (Matrix.Rotation(aq_slope, 3, "X") @ Matrix.Rotation(math.pi * 0.5, 3, "Z")).to_euler("XYZ")
    for sp in range(12):
        ay = aq_y0 - (sp + 0.5) * span_step
        bf = (aq_y0 - ay) / (aq_y0 - aq_y1)
        trough_floor_z = aq_z0 + bf * (aq_z1 - aq_z0)
        linker.spawn(col_aqueduct, SY_BLEND, "sy_aqueduct_pier_span_LOD0", "sy_aqueduct_pier_span",
                     (58.0, ay, trough_floor_z - 4.78), (eul_aq.x, eul_aq.y, eul_aq.z), (1.0, 1.0, 1.0),
                     layout_records=layout_records)
    linker.spawn(col_aqueduct, SY_BLEND, "sy_aqueduct_trough_LOD0", "sy_aqueduct_trough",
                 (58.0, 14.40, aq_z1 - 0.85), (0, 0, math.pi), (1.0, 1.0, 1.0), layout_records=layout_records)
    create_aqueduct_masonry_connectors(col_aqueduct, linker)

    # 5) UR-SCHINAR METROPOLE (Haeuser dicht an den Strassenraendern + Marktplatzbrunnen!)
    print("[4/6] Platziere Ur-Schinar (Haeuser buendig bis an die Strassenraender, Marktbrunnen, Ziggurat)...", flush=True)
    CITY_BLEND = "world/mesopotamia_city_kit.blend"
    FOUNTAIN_BLEND = "world/ur_fountain_hero.blend"

    create_ur_stone_paving_and_walls(col_city)

    # Hero-Marktplatzbrunnen auf der gepflasterten Agora (170.0, -48.0)
    agora_z = eval_sy_z(170.0, -48.0)
    linker.spawn(col_city, FOUNTAIN_BLEND, "ur_fountain_hero_LOD0", "ur_fountain_hero",
                 (170.0, -48.0, agora_z + 0.05), (0, 0, 0), (1.0, 1.0, 1.0), layout_records=layout_records)

    def spawn_insula(cx, cy, tot_w, tot_d, cols, rows, yaw, seed_off, small_only=False, target_col=col_city):
        alley = 0.25
        u_w = (tot_w - (cols - 1) * alley) / cols
        u_d = (tot_d - (rows - 1) * alley) / rows
        c_y, s_y = math.cos(yaw), math.sin(yaw)
        for r in range(rows):
            for c in range(cols):
                idx = seed_off + r * cols + c
                lx = -tot_w * 0.5 + u_w * 0.5 + c * (u_w + alley)
                ly = -tot_d * 0.5 + u_d * 0.5 + r * (u_d + alley)
                wx = cx + lx * c_y - ly * s_y
                wy = cy + lx * s_y + ly * c_y
                hyaw = yaw
                if rows > 1 and r == rows - 1:
                    hyaw = yaw + math.pi
                elif cols > 1 and rows == 1 and c == 0 and (idx % 3 == 0):
                    hyaw = yaw - math.pi * 0.5
                kit_mod = f"ur_mudbrick_small_0{(idx % 5) + 1}" if small_only else f"ur_courtyard_house_0{(idx % 5) + 1}"
                base_w, base_d = (6.6, 5.8) if small_only else (11.2, 11.4)
                sx = (u_w * 0.96) / base_w
                sy = (u_d * 0.96) / base_d
                sz = max(0.82, min(1.06, 0.5 * (sx + sy)))
                wz = eval_sy_z(wx, wy)
                # Fundamentecken pruefen damit keine Ecke am Tell-Hang schwebt
                for ox in (-u_w * 0.45, u_w * 0.45):
                    for oy in (-u_d * 0.45, u_d * 0.45):
                        wz = min(wz, eval_sy_z(wx + ox, wy + oy) + 0.24 * sz)
                linker.spawn(target_col, CITY_BLEND, f"{kit_mod}_LOD0", kit_mod,
                             (wx, wy, wz), (0, 0, hyaw + math.pi), (sx, sy, sz), layout_records=layout_records)

    # Dicht bis an die Strassen-/Pflasterkanten (Koenigsstrasse y=-45.7..-50.3, Prozessionsstrasse x=181.7..186.3, Agora y=-39.7..-56.3)
    ur_insulae = [
        # Nordwest & Nord der Koenigsstrasse / Agora (Suedfassade buendig an y = -45.5 bzw. -39.5 ohne Strassenueberstand!)
        (143.6, -32.2, 19.2, 24.4, 2, 2, 0.0, 41),
        (169.8, -29.6, 22.8, 19.2, 2, 2, 0.0, 49),
        (143.6, -7.2,  19.2, 18.4, 2, 2, 0.0, 10),
        (169.8, -7.2,  22.8, 18.4, 2, 2, 0.0, 25),
        (150.2, 13.0,  15.0, 11.8, 2, 1, -0.20, 18),
        (170.0, 14.5,  22.4, 14.4, 2, 2, 0.0, 33),
        # Sued der Koenigsstrasse / Agora (Nordfassade buendig an y = -50.6 bzw. -56.6!)
        (143.6, -66.8, 19.2, 30.8, 2, 3, 0.0, 57),
        (169.8, -69.5, 22.8, 25.0, 2, 3, 0.0, 65),
        (194.9, -66.8, 16.0, 30.8, 2, 3, 0.0, 97),
        (216.2, -66.8, 17.6, 30.8, 2, 3, 0.0, 105),
        # Suedviertel (y = -85.8 .. -124)
        (147.8, -99.8, 17.6, 20.2, 2, 2, 0.10, 73),
        (169.8, -96.2, 22.8, 20.2, 2, 2, 0.0, 81),
        (169.8, -115.6, 22.8, 16.2, 2, 2, -0.02, 89),
        (194.9, -96.2, 16.0, 20.2, 2, 2, 0.0, 113),
        (215.2, -96.8, 16.4, 19.0, 2, 2, -0.04, 121),
        (199.6, -114.8, 16.8, 13.8, 2, 1, 0.06, 129),
    ]
    for ix, iy, iw, idp, ic, ir, iyaw, iseed in ur_insulae:
        spawn_insula(ix, iy, iw, idp, ic, ir, iyaw, iseed, small_only=False)

    # Laden- & Hofhaus-Zeilen direkt entlang der Koenigsstrasse Ost (Nordseite y=-41.0 -> Suedfassade an -45.4)
    for hx, mod_i in ((193.2, 140), (204.5, 141), (217.5, 142)):
        kit_m = f"ur_courtyard_house_0{(mod_i % 5) + 1}"
        linker.spawn(col_city, CITY_BLEND, f"{kit_m}_LOD0", kit_m,
                     (hx, -40.2, eval_sy_z(hx, -40.2)), (0, 0, math.pi), (0.98, 0.74, 0.90), layout_records=layout_records)

    # 4 Monumentale Stadttore
    for gx, gy, gyaw in ((131.0, -48.0, math.pi), (228.0, -48.0, 0.0), (184.0, -128.0, -math.pi * 0.5), (184.0, 26.0, math.pi * 0.5)):
        linker.spawn(col_city, CITY_BLEND, "ur_city_gate_LOD0", "ur_city_gate",
                     (gx, gy, eval_sy_z(gx, gy) - 0.04), (0, 0, gyaw - math.pi * 0.5), (1.12, 1.04, 1.0), layout_records=layout_records)

    # Stadtmauer-Ring + Ecktuerme
    wall_chains = [
        [(131.0, -42.6), (131.0, -24.0), (134.0, -4.0), (142.0, 14.0), (156.0, 23.0), (178.6, 26.0)],
        [(189.4, 26.0), (210.0, 25.0), (230.0, 20.0), (242.0, 8.0), (238.0, -14.0), (231.0, -30.0), (228.0, -42.6)],
        [(228.0, -53.4), (227.0, -72.0), (226.0, -92.0), (223.0, -110.0), (210.0, -123.0), (189.4, -128.0)],
        [(178.6, -128.0), (158.0, -124.0), (143.0, -112.0), (135.0, -94.0), (132.0, -74.0), (131.0, -53.4)],
    ]
    for chain in wall_chains:
        for i in range(len(chain) - 1):
            x0, y0 = chain[i]
            x1, y1 = chain[i + 1]
            L = math.hypot(x1 - x0, y1 - y0)
            yaw = math.atan2(y1 - y0, x1 - x0)
            n_seg = max(1, round(L / 7.8))
            seg_l = L / n_seg
            for si in range(n_seg):
                f = (si + 0.5) / n_seg
                wx = x0 + f * (x1 - x0)
                wy = y0 + f * (y1 - y0)
                linker.spawn(col_city, CITY_BLEND, "ur_wall_segment_LOD0", "ur_wall_segment",
                             (wx, wy, eval_sy_z(wx, wy)), (0, 0, yaw), (seg_l / 7.82, 0.72, 0.80), layout_records=layout_records)

    for bx, by in ((134, -4), (142, 14), (230, 20), (242, 8), (226, -92), (210, -123), (143, -112), (135, -94)):
        linker.spawn(col_city, CITY_BLEND, "ur_wall_tower_LOD0", "ur_wall_tower",
                     (bx, by, eval_sy_z(bx, by)), (0, 0, 0), (0.82, 0.82, 0.85), layout_records=layout_records)

    # Grosse Zikkurat von Ur (210, -10) + Kornspeicher
    linker.spawn(col_city, CITY_BLEND, "ur_ziggurat_temple_LOD0", "ur_ziggurat_temple",
                 (210.0, -10.0, eval_sy_z(210.0, -10.0)), (0, 0, math.pi), (1.0, 1.0, 1.0), layout_records=layout_records)
    for sx_s, sy_s in ((194.5, -23.5), (194.5, 2.5), (194.5, -10.5)):
        linker.spawn(col_city, CITY_BLEND, "ur_grain_silo_LOD0", "ur_grain_silo",
                     (sx_s, sy_s, eval_sy_z(sx_s, sy_s)), (0, 0, 0), (1.15, 1.15, 1.15), layout_records=layout_records)

    # Marktstaende um die Agora (direkt an den Agora-Kanten rund um den Brunnen!)
    agora_stalls = [
        (163.5, -42.2, 0.03), (169.0, -42.4, -0.04), (174.5, -42.2, 0.05), (179.6, -42.5, -0.03),
        (163.5, -53.8, math.pi - 0.03), (169.0, -53.6, math.pi + 0.04), (174.5, -53.8, math.pi - 0.05), (179.6, -53.5, math.pi + 0.03),
        (125.0, -43.0, math.pi), (125.0, -53.0, 0.0), (232.0, -41.5, -math.pi * 0.5),
    ]
    for mx, my, myaw in agora_stalls:
        linker.spawn(col_city, CITY_BLEND, "road_market_awning_LOD0", "road_market_awning",
                     (mx, my, eval_sy_z(mx, my) + 0.05), (0, 0, myaw + math.pi), layout_records=layout_records)

    # Strassen-Fackelpfosten & geparkte Karren entlang Koenigs- & Prozessionsstrasse
    lamp_spots = [
        (136.0, -45.3, -math.pi * 0.5), (146.0, -45.3, -math.pi * 0.5), (156.0, -45.3, -math.pi * 0.5),
        (162.0, -50.7, math.pi * 0.5), (178.0, -50.7, math.pi * 0.5), (192.0, -45.3, -math.pi * 0.5),
        (202.0, -50.7, math.pi * 0.5), (218.0, -45.3, -math.pi * 0.5), (181.3, -28.0, 0.0),
        (186.7, -14.0, math.pi), (181.3, -70.0, 0.0), (186.7, -96.0, math.pi),
    ]
    for lx, ly, lyaw in lamp_spots:
        linker.spawn(col_city, CITY_BLEND, "road_curb_lamp_post_LOD0", "road_curb_lamp_post",
                     (lx, ly, eval_sy_z(lx, ly) + 0.04), (0, 0, lyaw), layout_records=layout_records)
    for cx_c, cy_c, cyaw in ((141.5, -44.2, 1.52), (161.5, -52.5, -1.62), (220.0, -44.0, 1.58), (187.5, -142.0, 0.12)):
        linker.spawn(col_city, CITY_BLEND, "road_cart_parked_LOD0", "road_cart_parked",
                     (cx_c, cy_c, eval_sy_z(cx_c, cy_c) + 0.04), (0, 0, cyaw), layout_records=layout_records)

    # Vorstaedte & Handwerkerdorf (Haeuser dicht am Strassenrand!)
    spawn_insula(173.0, 39.5, 16.4, 11.4, 2, 1, 0.0, 150, small_only=True, target_col=col_suburbs)
    spawn_insula(195.0, 39.5, 16.4, 11.4, 2, 1, 0.0, 154, small_only=True, target_col=col_suburbs)
    spawn_insula(173.0, -145.5, 16.8, 14.8, 2, 2, 0.0, 160, small_only=True, target_col=col_suburbs)
    spawn_insula(195.0, -145.5, 16.8, 14.8, 2, 2, 0.0, 166, small_only=True, target_col=col_suburbs)
    linker.spawn(col_suburbs, CITY_BLEND, "ur_courtyard_house_01_LOD0", "ur_courtyard_house_01",
                 (281.5, -36.5, eval_sy_z(281.5, -36.5)), (0, 0, math.pi), (1.25, 1.15, 1.05), layout_records=layout_records)
    spawn_insula(280.0, -61.0, 14.2, 12.6, 2, 2, 0.04, 180, small_only=True, target_col=col_suburbs)
    # 3 Toepfer-Brennöfen in Suedvorstadt
    for ki, (kx, ky) in enumerate(((151.0, -148.0), (157.5, -153.5), (148.5, -157.0))):
        linker.spawn(col_suburbs, CITY_BLEND, "ur_kiln_dome_LOD0", "ur_kiln_dome",
                     (kx, ky, eval_sy_z(kx, ky)), (0, 0, ki * 0.5), layout_records=layout_records)
    # Handwerkerdorf Baudorf Schinar (10 Haeuser rund um Dorfplatz, Brunnen, Backoefen & Wachturm)
    def spawn_grounded(col, blend_path, mod_name, x, y, yaw, sc=(1.0, 1.0, 1.0), hx=2.8, hy=2.5, sink=0.14):
        c, s = math.cos(yaw), math.sin(yaw)
        z_g = min(
            eval_sy_z(x, y),
            eval_sy_z(x + hx * c - hy * s, y + hx * s + hy * c),
            eval_sy_z(x - hx * c - hy * s, y - hx * s + hy * c),
            eval_sy_z(x + hx * c + hy * s, y + hx * s - hy * c),
            eval_sy_z(x - hx * c + hy * s, y - hx * s - hy * c),
        ) - sink
        linker.spawn(col, blend_path, f"{mod_name}_LOD0", mod_name,
                     (x, y, z_g), (0, 0, yaw), sc, layout_records=layout_records)

    baudorf_houses = [
        (95.0, -34.0, 0.10), (107.0, -31.5, -0.14), (120.5, -35.5, 0.32),
        (91.5, -53.8, 0.06 + math.pi), (122.0, -54.2, -0.10 + math.pi),
        (94.0, -64.0, -0.20 + math.pi), (107.5, -67.5, 0.12 + math.pi),
        (121.0, -64.0, -0.28 + math.pi), (114.5, -40.5, 0.55), (101.0, -60.5, -0.42 + math.pi),
    ]
    for vi, (hx, hy, hyaw) in enumerate(baudorf_houses):
        km = f"ur_mudbrick_small_0{(vi % 5) + 1}"
        spawn_grounded(col_suburbs, CITY_BLEND, km, hx, hy, hyaw, (0.98, 0.92, 0.94), hx=2.6, hy=2.2)

    # 10 Umland-Doerfer & Ortschaften rund um Ur-Schinar, Kanaele, Seen & Teiche
    # 1) Nisaba-Kornstadt (-235, -345)
    spawn_insula(-257.0, -335.0, 17.5, 14.0, 2, 2, 0.08, 101, target_col=col_suburbs)
    spawn_insula(-214.0, -336.0, 17.0, 14.0, 2, 2, -0.06, 109, target_col=col_suburbs)
    spawn_insula(-257.0, -366.0, 17.0, 13.5, 2, 1, 0.10, 117, target_col=col_suburbs)
    spawn_insula(-213.0, -366.0, 18.0, 13.5, 2, 1, -0.08, 125, target_col=col_suburbs)
    for sx_n, sy_n, sc_n in ((-235.0, -319.0, 1.35), (-228.0, -321.0, 1.18), (-242.0, -321.0, 1.18)):
        spawn_grounded(col_suburbs, CITY_BLEND, "ur_grain_silo", sx_n, sy_n, 0.0, (sc_n, sc_n, sc_n), hx=1.5, hy=1.5)
    for kx, ky in ((-266.0, -348.0), (-204.0, -356.0)):
        spawn_grounded(col_suburbs, CITY_BLEND, "ur_kiln_dome", kx, ky, 0.4, hx=1.6, hy=1.6)

    # 2) Eridu-Lagune (395, -210)
    for mx, my, myaw in ((386.0, -205.0, 0.25), (404.0, -204.0, -0.18), (415.0, -212.0, -0.65), (380.0, -228.0, 0.42), (418.0, -216.0, -0.30)):
        spawn_grounded(col_suburbs, CITY_BLEND, "ur_mudhif_hut", mx, my, myaw, hx=2.1, hy=3.2)
    spawn_insula(375.0, -194.0, 15.5, 12.5, 2, 1, 0.12, 135, small_only=True, target_col=col_suburbs)
    spawn_insula(398.0, -192.0, 16.5, 12.5, 2, 1, -0.08, 141, small_only=True, target_col=col_suburbs)
    spawn_insula(378.0, -246.0, 17.5, 13.0, 2, 1, 0.05, 147, small_only=True, target_col=col_suburbs)

    # 3) Girsu-Osthain (470, 45 -> Tor & Sanktuar noerdlich des Ostkanals y=39!)
    spawn_grounded(col_suburbs, CITY_BLEND, "ur_city_gate", 442.0, 52.0, 0.0, (0.88, 0.86, 0.85), hx=5.0, hy=3.0)
    spawn_grounded(col_suburbs, CITY_BLEND, "ur_ziggurat_temple", 478.0, 55.0, math.pi * 0.5, (0.60, 0.60, 0.54), hx=6.5, hy=6.5)
    spawn_insula(456.0, 68.0, 17.5, 13.5, 2, 2, 0.04, 155, target_col=col_suburbs)
    spawn_insula(484.0, 68.0, 16.5, 13.5, 2, 2, -0.05, 163, target_col=col_suburbs)
    spawn_insula(456.0, 22.0, 17.5, 13.5, 2, 2, -0.04, 171, target_col=col_suburbs)
    spawn_insula(484.0, 22.0, 16.5, 13.5, 2, 2, 0.06, 179, target_col=col_suburbs)
    for kx, ky in ((446.0, 14.0), (492.0, 14.0)):
        spawn_grounded(col_suburbs, CITY_BLEND, "ur_kiln_dome", kx, ky, 0.8, hx=1.6, hy=1.6)

    # 4) Sippar-Furt (385, 295)
    spawn_insula(374.0, 307.0, 16.5, 13.5, 2, 1, 0.09, 188, small_only=True, target_col=col_suburbs)
    spawn_insula(397.0, 304.0, 16.5, 13.5, 2, 1, -0.10, 194, small_only=True, target_col=col_suburbs)
    spawn_insula(384.0, 277.0, 17.5, 13.5, 2, 1, 0.04, 200, small_only=True, target_col=col_suburbs)
    spawn_grounded(col_suburbs, SY_BLEND, "sy_crane_aframe", 406.0, 292.0, 0.3, (1.25, 1.25, 1.25), hx=2.0, hy=2.0)
    for kx, ky in ((398.0, 272.0), (366.0, 278.0)):
        spawn_grounded(col_suburbs, CITY_BLEND, "ur_kiln_dome", kx, ky, 1.2, hx=1.6, hy=1.6)

    # 5) Larsam-Suedweide (-65, -520)
    spawn_grounded(col_suburbs, CITY_BLEND, "ur_courtyard_house_03", -65.0, -520.0, math.pi, (1.65, 1.55, 0.95), hx=7.0, hy=6.0)
    spawn_insula(-84.0, -504.0, 15.5, 12.5, 2, 1, 0.12, 208, small_only=True, target_col=col_suburbs)
    spawn_insula(-46.0, -505.0, 15.5, 12.5, 2, 1, -0.09, 214, small_only=True, target_col=col_suburbs)
    spawn_insula(-64.0, -539.0, 17.5, 12.5, 2, 1, 0.03, 220, small_only=True, target_col=col_suburbs)
    spawn_grounded(col_suburbs, CITY_BLEND, "ur_kiln_dome", -44.0, -518.0, 0.5, hx=1.6, hy=1.6)

    # 6) Zedern-Vorwerk (-345, -65)
    for zi, (zx, zy, zyaw) in enumerate(((-356, -56, 0.18), (-344, -54, -0.14), (-332, -57, 0.08), (-355, -75, -0.22), (-343, -76, 0.16), (-332, -73, -0.09))):
        km = f"ur_mudbrick_small_0{(zi % 5) + 1}"
        spawn_grounded(col_suburbs, CITY_BLEND, km, zx, zy, zyaw, (0.90, 0.85, 0.85), hx=2.4, hy=2.0)
    for lx in (-336.0, -352.0):
        spawn_grounded(col_suburbs, SY_BLEND, "sy_log_stack", lx, -64.5, 0.12, (1.1, 1.1, 1.1), hx=2.0, hy=1.2)

    # 7) Kisurra-Faehrweiler (165, -315 am Kisurra-Teich & Kanal)
    spawn_grounded(col_suburbs, CITY_BLEND, "ur_courtyard_house_02", 166.0, -306.0, 0.15, (0.95, 0.95, 0.92), hx=4.5, hy=4.2)
    for ki, (kx, ky, kyaw) in enumerate(((154.0, -314.0, 0.30), (176.0, -318.0, -0.20), (160.0, -327.0, 2.9), (172.0, -330.0, 3.2), (184.0, -310.0, -1.4))):
        spawn_grounded(col_suburbs, CITY_BLEND, f"ur_mudbrick_small_0{(ki % 5) + 1}", kx, ky, kyaw, (0.94, 0.90, 0.92))
    spawn_grounded(col_suburbs, CITY_BLEND, "ur_grain_silo", 155.0, -300.0, 0.0, (1.15, 1.15, 1.15), hx=1.5, hy=1.5)
    spawn_grounded(col_suburbs, CITY_BLEND, "ur_kiln_dome", 180.0, -324.0, 0.6, hx=1.6, hy=1.6)

    # 8) Umma-Westdorf (-205, -175 am Umma-Oasenteich)
    spawn_grounded(col_suburbs, CITY_BLEND, "ur_courtyard_house_04", -212.0, -170.0, -0.25, (0.96, 0.94, 0.90), hx=4.5, hy=4.2)
    for ui, (ux, uy, uyaw) in enumerate(((-198.0, -166.0, -0.4), (-218.0, -184.0, 2.8), (-202.0, -186.0, 3.1), (-190.0, -178.0, 1.7), (-224.0, -174.0, 1.2))):
        spawn_grounded(col_suburbs, CITY_BLEND, f"ur_mudbrick_small_0{(ui % 5) + 1}", ux, uy, uyaw, (0.94, 0.90, 0.92))
    spawn_grounded(col_suburbs, CITY_BLEND, "ur_kiln_dome", -196.0, -190.0, 0.2, hx=1.6, hy=1.6)

    # 9) Adab-Ostweiler (545, -65 am Adab-Teich)
    for ai, (ax, ay, ayaw) in enumerate(((538.0, -56.0, 0.1), (552.0, -58.0, -0.2), (540.0, -74.0, 3.0), (554.0, -72.0, 3.3), (562.0, -64.0, -1.5))):
        spawn_grounded(col_suburbs, CITY_BLEND, f"ur_mudbrick_small_0{(ai % 5) + 1}", ax, ay, ayaw, (0.95, 0.92, 0.90))
    spawn_grounded(col_suburbs, CITY_BLEND, "ur_mudhif_hut", 528.0, -48.0, 0.5, hx=2.1, hy=3.2)
    spawn_grounded(col_suburbs, CITY_BLEND, "ur_grain_silo", 558.0, -52.0, 0.0, (1.12, 1.12, 1.12), hx=1.5, hy=1.5)
    spawn_grounded(col_suburbs, CITY_BLEND, "ur_kiln_dome", 536.0, -80.0, 1.1, hx=1.6, hy=1.6)

    # 10) Lagash-Suedost (385, -415 am Lagash-Schilfteich)
    spawn_grounded(col_suburbs, CITY_BLEND, "ur_courtyard_house_05", 388.0, -408.0, 0.22, (0.98, 0.94, 0.92), hx=4.5, hy=4.2)
    for li, (lx, ly, lyaw) in enumerate(((376.0, -414.0, 0.4), (398.0, -418.0, -0.3), (382.0, -426.0, 3.0), (394.0, -428.0, 3.2))):
        spawn_grounded(col_suburbs, CITY_BLEND, f"ur_mudbrick_small_0{(li % 5) + 1}", lx, ly, lyaw, (0.94, 0.90, 0.92))
    spawn_grounded(col_suburbs, CITY_BLEND, "ur_mudhif_hut", 374.0, -396.0, -0.6, hx=2.1, hy=3.2)
    spawn_grounded(col_suburbs, CITY_BLEND, "ur_kiln_dome", 404.0, -424.0, 0.9, hx=1.6, hy=1.6)

    # 6) Bruecken, Schleusen, Wehre, Schadufs, Wasserraeder, Magur-Boote & Felder-Infrastruktur
    z_canal_w = float(eval_river_surface_z_np(-171.0)) + 0.04
    build_authentic_shipyard_landmarks(col_shipyard, col_suburbs, linker, z_canal_w)
    linker.spawn(col_river_infra, CITY_BLEND, "ur_canal_bridge_LOD0", "ur_canal_bridge",
                 (184.0, -171.0, z_canal_w + 0.15), (0, 0, math.pi * 0.5), (0.92, 1.25, 1.0), layout_records=layout_records)
    linker.spawn(col_river_infra, CITY_BLEND, "ur_canal_bridge_LOD0", "ur_canal_bridge",
                 (-235.0, -352.0, 0.95), (0, 0, 0.35), (0.90, 1.20, 1.0), layout_records=layout_records)
    linker.spawn(col_river_infra, CITY_BLEND, "ur_canal_bridge_LOD0", "ur_canal_bridge",
                 (395.0, -220.0, 0.92), (0, 0, -0.35), (0.92, 1.25, 1.0), layout_records=layout_records)
    linker.spawn(col_river_infra, CITY_BLEND, "ur_canal_bridge_LOD0", "ur_canal_bridge",
                 (470.0, 39.0, 0.98), (0, 0, 1.54), (0.92, 1.25, 1.0), layout_records=layout_records)
    linker.spawn(col_river_infra, CITY_BLEND, "ur_wooden_bridge_LOD0", "ur_wooden_bridge",
                 (126.0, -183.5, z_canal_w + 0.06), (0, 0, 1.72), layout_records=layout_records)
    linker.spawn(col_river_infra, CITY_BLEND, "ur_wooden_bridge_LOD0", "ur_wooden_bridge",
                 (337.0, 39.5, 0.90), (0, 0, 1.63), layout_records=layout_records)
    linker.spawn(col_river_infra, CITY_BLEND, "ur_wooden_bridge_LOD0", "ur_wooden_bridge",
                 (158.0, -234.0, 0.88), (0, 0, 0.45), layout_records=layout_records)

    # Euphrat-Bruecke bei y=-48 (3-Felder-Holz-/Steinbruecke aus mod. Jetties & Bridge)
    br_x = float(eval_river_center_x_np(-48.0))
    br_wz = float(eval_river_surface_z_np(-48.0))
    for bx_off in (-7.5, 0.0, 7.5):
        linker.spawn(col_river_infra, CITY_BLEND, "ur_canal_bridge_LOD0", "ur_canal_bridge",
                     (br_x + bx_off, -48.0, br_wz + 0.30), (0, 0, 0.0), (0.95, 1.15, 1.05), layout_records=layout_records)

    # 3 Schleusen, 3 Wehre, 3 Landungsstege
    for sx, sy, sz in ((237.5, -171.0, z_canal_w), (266.0, -212.0, float(eval_river_surface_z_np(-212.0))), (290.5, 38.0, float(eval_river_surface_z_np(38.0)))):
        linker.spawn(col_river_infra, SY_BLEND, "river_sluice_gate_LOD0", "river_sluice_gate",
                     (sx, sy, sz - 0.18), (0, 0, math.pi * 0.5), (1.8, 1.2, 1.15), layout_records=layout_records)
    for wx, wy, wyaw, wz in ((154.0, -173.0, 0.12, 0.78), (370.0, 42.0, 1.48, 0.85), (-250.0, -320.0, 0.48, 0.82)):
        linker.spawn(col_river_infra, SY_BLEND, "river_weir_LOD0", "river_weir",
                     (wx, wy, wz - 0.12), (0, 0, wyaw), (1.05, 1.0, 1.25), layout_records=layout_records)
    for jy in (-25.0, -64.0, -79.0):
        jx = float(eval_river_center_x_np(jy)) - float(eval_river_half_width_np(jy)) + 1.8
        jz = float(eval_river_surface_z_np(jy))
        linker.spawn(col_river_infra, SY_BLEND, "river_timber_jetty_LOD0", "river_timber_jetty",
                     (jx, jy, jz + 0.15), (0, 0, math.pi * 0.5), (1.1, 1.1, 1.0), layout_records=layout_records)
    # Seen- & Teich-Stege + Boote auf allen 10 Gewaessern
    lake_jetties = [
        (-282.0, -248.0, 0.72, 0.86), (416.0, -264.0, -0.15, 0.78), (-125.0, -498.0, 2.96, 0.78),
        (502.0, 355.0, 0.34, 3.10), (144.0, -298.0, 2.90, 0.80), (-186.0, -186.0, -0.58, 0.82),
        (526.0, -42.0, 1.65, 0.84), (368.0, -390.0, 2.30, 0.78),
    ]
    for ljx, ljy, ljyaw, ljz in lake_jetties:
        linker.spawn(col_river_infra, SY_BLEND, "river_timber_jetty_LOD0", "river_timber_jetty",
                     (ljx, ljy, ljz + 0.14), (0, 0, ljyaw), (1.05, 1.05, 1.0), layout_records=layout_records)

    # 6 Schadufs & 2 Noria-Wasserraeder
    for sx, sy, syaw in ((192.0, -162.0, -math.pi * 0.5), (246.0, -98.0, 0.0), (-224.0, -380.0, math.pi), (365.0, -210.0, -math.pi * 0.5), (435.0, 50.0, math.pi * 0.5), (348.0, 288.0, math.pi)):
        sz = eval_sy_z(sx, sy)
        linker.spawn(col_river_infra, SY_BLEND, "river_shaduf_post_LOD0", "river_shaduf_post",
                     (sx, sy, sz), (0, 0, syaw - math.pi * 0.5), (1.1, 1.1, 1.1), layout_records=layout_records)
        linker.spawn(col_river_infra, SY_BLEND, "river_shaduf_arm_LOD0", "river_shaduf_arm",
                     (sx, sy, sz + 2.31), (0, 0.15, syaw - math.pi * 0.5), (1.0, 1.0, 1.0), layout_records=layout_records)
    ur_wx = float(eval_river_center_x_np(-18.0)) - float(eval_river_half_width_np(-18.0)) + 1.1
    for nx, ny, nz, nyaw, nsc in ((ur_wx, -18.0, float(eval_river_surface_z_np(-18.0)) + 1.35, 0.0, 0.74), (442.0, 48.0, 2.15, math.pi * 0.5, 0.65)):
        linker.spawn(col_river_infra, SY_BLEND, "river_waterwheel_base_LOD0", "river_waterwheel_base",
                     (nx, ny, nz - 2.05 * nsc), (0, 0, nyaw), (nsc, nsc, nsc), layout_records=layout_records)
        linker.spawn(col_river_infra, SY_BLEND, "river_waterwheel_rotor_LOD0", "river_waterwheel_rotor",
                     (nx, ny, nz), (0, 0, nyaw), (nsc, nsc, nsc), layout_records=layout_records)

    # 14 Magur-Boote auf Euphrat & Barkenkanal
    for bi, by in enumerate((-26.0, -64.5, -105.0, -145.0, -210.0, -290.0, 18.0, 75.0, 150.0, 240.0)):
        bx = float(eval_river_center_x_np(by)) + (0.0 if bi % 2 == 0 else -3.5)
        bz = float(eval_river_surface_z_np(by)) + 0.02
        b_key = "river_magur_timber" if bi % 2 == 0 else "river_magur_cargo"
        linker.spawn(col_river_infra, SY_BLEND, f"{b_key}_LOD0", b_key,
                     (bx, by, bz), (0, 0, 0.08 * math.sin(bi)), layout_records=layout_records)
    for ci, (bx, by, byaw) in enumerate((
        (196.0, -170.2, 1.57), (144.0, -168.0, 0.95), (109.0, -116.0, 0.52), (74.5, -86.5, 0.35),
        (-302.0, -230.0, 0.42), (442.0, -268.0, -0.25), (-158.0, -502.0, 0.65),
        (126.0, -294.0, 0.85), (-170.0, -196.0, -0.45), (524.0, -24.0, 1.15), (355.0, -374.0, 0.25),
    )):
        b_key = "river_magur_timber" if ci % 2 == 0 else "river_magur_cargo"
        bz_c = float(eval_alluvial_lake_field_np(np.array([bx]), np.array([by]))[1][0]) if ci >= 4 else z_canal_w
        linker.spawn(col_river_infra, SY_BLEND, f"{b_key}_LOD0", b_key,
                     (bx, by, bz_c + 0.02), (0, 0, byaw), layout_records=layout_records)

    # Marschland-Mudhifs, Strohschober & Feldunterstaende
    for mx, my, myaw in ((-255.0, -212.0, 0.4), (-272.0, -242.0, -0.3), (382.0, -252.0, 0.8), (-132.0, -468.0, -0.5)):
        linker.spawn(col_suburbs, CITY_BLEND, "ur_mudhif_hut_LOD0", "ur_mudhif_hut",
                     (mx, my, eval_sy_z(mx, my)), (0, 0, myaw), layout_records=layout_records)
    straw_pts = [
        (140, -245), (108, -220), (204, -220), (244, -238), (332, -140), (398, -138), (326, -86), (406, -40),
        (336, -18), (412, 38), (-305, -278), (-255, -268), (-202, -272), (-142, -280), (-334, -338), (-146, -346),
        (326, -144), (388, -142), (462, -32), (534, -28), (308, 190), (368, 188), (-138, -434), (-74, -430),
    ]
    for fi, (fx, fy) in enumerate(straw_pts):
        fz = eval_sy_z(fx, fy)
        lod = "LOD0" if math.hypot(fx, fy) < 340.0 else "LOD1"
        linker.spawn(col_river_infra, SY_BLEND, f"field_straw_rick_{lod}", "field_straw_rick",
                     (fx, fy, fz), (0, 0, fi * 1.1), layout_records=layout_records)
    for sx, sy, syaw in ((124, -216, 0.25), (238, -220, -0.35), (322, -110, 0.82), (388, 12, -0.45), (-318, -304, 0.55), (-192, -300, -0.40), (342, -168, -0.60), (488, -56, 0.72), (318, 280, 0.45), (-68, -456, -0.25)):
        linker.spawn(col_river_infra, SY_BLEND, "field_shelter_LOD0", "field_shelter",
                     (sx, sy, eval_sy_z(sx, sy)), (0, 0, syaw), layout_records=layout_records)

    # 7) BOTANIK (Dichte Berg- & Uferwaelder, Felder, Schilf & Zierbotanik — NULL wildes Gruen in Ur-Schinar!)
    print("[5/6] Platziere verlinkte Botanik (Baeume, Straeucher, Getreide, Schilf, Temenos-Zierpflanzen)...", flush=True)
    rng = random.Random(42107)

    TREE_SPECIES = ["cedar", "cypress", "oak", "hornbeam", "palm", "acacia", "olive", "fig", "poplar", "terebinth"]
    STAGES = ("young", "mature", "ancient")

    def spawn_tree(sp, stage, var_i, x, y, sc, yaw, tint=None):
        r_tr = 1.25 * sc
        z = min(
            eval_sy_z(x, y),
            eval_sy_z(x - r_tr, y),
            eval_sy_z(x + r_tr, y),
            eval_sy_z(x, y - r_tr),
            eval_sy_z(x, y + r_tr),
        ) - 0.16
        dist = math.hypot(x, y)
        lod = "LOD0" if dist < 320.0 else ("LOD1" if dist < 720.0 else "LOD2")
        mesh_n = f"{sp}_{stage}_{var_i:02d}_{lod}"
        linker.spawn(col_trees, f"botany/trees_{sp}.blend", mesh_n, f"trees_{sp}:{sp}_{stage}_{var_i:02d}",
                     (x, y, z), (0, 0, yaw), (sc, sc, sc), tint=tint, layout_records=layout_records)

    # Kuratierte Hero-Baeume rund um Werft, Quelle & Hafen (grosser Abstand zur Arche & Ur-Strassen)
    hero_trees = [
        (-98.0, -86.0, "acacia", "mature", 1, 1.05),
        (-118.0, -34.0, "terebinth", "mature", 2, 1.08),
        (54.0, -92.0, "palm", "ancient", 1, 1.10),
        (78.0, -94.0, "palm", "mature", 2, 1.06),
        (98.0, -76.0, "fig", "mature", 1, 1.08),
        (112.0, -96.0, "poplar", "mature", 2, 1.12),
        (-128.0, 78.0, "cedar", "mature", 1, 1.14),
        (-82.0, 112.0, "olive", "mature", 2, 1.08),
        (88.0, 106.0, "olive", "mature", 1, 1.06),
        (116.0, 112.0, "cypress", "mature", 2, 1.10),
        (-48.0, -108.0, "acacia", "mature", 1, 1.05),
        (-136.0, -72.0, "oak", "ancient", 1, 1.12),
        (108.0, 34.0, "cypress", "mature", 1, 1.08),
    ]
    for hx, hy, hsp, hst, hvar, hsc in hero_trees:
        spawn_tree(hsp, hst, hvar, hx, hy, hsc, rng.uniform(0.0, math.tau))

    # Dichte Bergwaelder am Quellgebirge & Randhuegeln + Galeriewaelder am Euphrat, Kanaelen & Seen
    forest_groves = [
        (-185, -78, 72, "cedar"), (-168, 20, 65, "oak"), (-138, 128, 82, "cedar"), (-62, 148, 85, "cedar"),
        (14, 142, 78, "oak"), (98, 134, 78, "cypress"), (-10, 225, 118, "cedar"), (145, 185, 92, "olive"),
        (-215, 205, 118, "cedar"), (-145, -142, 65, "acacia"), (68, -138, 50, "palm"), (124, -126, 48, "poplar"),
        (-420, -40, 155, "cedar"), (-530, -145, 175, "cedar"), (-485, 165, 165, "cypress"),
        (585, 325, 165, "oak"), (425, 470, 160, "oak"), (-225, 545, 185, "cedar"), (185, 625, 185, "cypress"),
        (690, 115, 170, "cedar"), (295, -345, 125, "palm"), (545, -215, 135, "palm"), (-415, -285, 135, "palm"),
        (-385, -565, 175, "acacia"), (-85, -695, 165, "oak"), (245, -645, 175, "hornbeam"), (665, -640, 185, "cypress"),
        (-620, -75, 175, "cedar"), (690, 360, 175, "oak"), (-950, 920, 230, "cedar"), (950, 920, 230, "oak"),
        (0, 1180, 240, "cedar"), (-640, 1150, 220, "cypress"), (640, 1150, 220, "cedar"),
        (-1180, 320, 220, "oak"), (-1120, -480, 220, "acacia"), (-920, -1080, 225, "oak"), (920, -1080, 225, "cypress"),
    ]
    trees_placed = 0
    target_trees = 1850
    tries = 0
    while trees_placed < target_trees and tries < target_trees * 20:
        tries += 1
        roll = rng.random()
        if roll < 0.28:
            # Ufer-Galeriewald (Euphrat, Kanaele, Seen)
            if rng.random() < 0.65:
                ty = rng.uniform(-1250.0, 1250.0)
                bsgn = -1.0 if rng.random() < 0.5 else 1.0
                tx = float(eval_river_center_x_np(ty)) + bsgn * (float(eval_river_half_width_np(ty)) + rng.uniform(3.2, 22.0))
            else:
                lk = rng.choice(ALLUVIAL_LAKES)
                ang = rng.uniform(0.0, math.tau)
                lobe = 1.0 + 0.16 * math.sin(ang * 2.0 + lk["seed"]) + 0.09 * math.cos(ang * 3.0 - lk["seed"] * 1.7)
                rf = rng.uniform(1.10, 1.38)
                lx = math.cos(ang) * lk["rx"] * lobe * rf
                ly = math.sin(ang) * lk["ry"] * lobe * rf
                c_y, s_y = math.cos(lk["yaw"]), math.sin(lk["yaw"])
                tx = lk["cx"] + lx * c_y - ly * s_y
                ty = lk["cy"] + lx * s_y + ly * c_y
            sp = rng.choices(["palm", "poplar", "acacia", "fig"], weights=[42, 28, 18, 12])[0]
        else:
            gr = rng.choice(forest_groves)
            ang = rng.uniform(0.0, math.tau)
            rn = (rng.random() ** 0.72) * gr[2]
            tx = max(-1430.0, min(1430.0, gr[0] + rn * math.cos(ang)))
            ty = max(-1430.0, min(1430.0, gr[1] + rn * math.sin(ang)))
            sp = gr[3] if rng.random() < 0.68 else rng.choice(["cedar", "cypress", "oak", "olive", "terebinth", "hornbeam"])

        if is_shipyard_work_zone(tx, ty, pad=3.0):
            continue
        if abs(tx - float(eval_river_center_x_np(ty))) < float(eval_river_half_width_np(ty)) + 2.4:
            continue
        if float(eval_canal_field_np(np.array([tx]), np.array([ty]))[0][0]) < 4.5:
            continue
        # Mindestens >= 2.5 m Abstand zur Wasserlinie aller Alluvial-Seen/Teiche
        if float(eval_alluvial_lake_field_np(np.array([tx]), np.array([ty]))[0][0]) < 1.25:
            continue
        # Aquädukt-Sichtachse (x=58, y=10..102) von Bäumen freihalten (nur seitlich!)
        if abs(tx - 58.0) < 7.5 and 8.0 <= ty <= 104.0:
            continue
        # Brueckenkopf & Hafen von Ur freihalten
        if math.hypot(tx - 279.0, ty + 48.0) < 26.0:
            continue

        tz = eval_sy_z(tx, ty)
        upland = 1.0 + min(0.40, max(0.0, (tz - 5.0) * 0.012))
        sc = rng.uniform(0.84, 1.24) * upland
        stage = rng.choice(STAGES)
        var_i = rng.randint(1, 4)
        tint = (rng.uniform(0.92, 1.04), rng.uniform(0.95, 1.05), rng.uniform(0.88, 1.00))
        spawn_tree(sp, stage, var_i, tx, ty, sc, rng.uniform(0.0, math.tau), tint=tint)
        trees_placed += 1

    # Straeucher & Uferschilf (nur ausserhalb von Ur-Schinar, Doerfern, Werft & Strassen!)
    SHRUB_SPECIES = ["tamarisk", "oleander", "juniper", "broom", "thornbush"]
    shrubs_placed = 0
    for _ in range(2400):
        if shrubs_placed >= 540:
            break
        if rng.random() < 0.48:
            ty = rng.uniform(-650.0, 650.0)
            bsgn = -1.0 if rng.random() < 0.5 else 1.0
            tx = float(eval_river_center_x_np(ty)) + bsgn * (float(eval_river_half_width_np(ty)) + rng.uniform(2.5, 14.0))
        else:
            rad = rng.uniform(95.0, 560.0)
            ang = rng.uniform(0.0, math.tau)
            tx, ty = rad * math.cos(ang), rad * math.sin(ang)
        if is_shipyard_work_zone(tx, ty, pad=2.2):
            continue
        if abs(tx - float(eval_river_center_x_np(ty))) < float(eval_river_half_width_np(ty)) + 1.8:
            continue
        if float(eval_alluvial_lake_field_np(np.array([tx]), np.array([ty]))[0][0]) < 1.04:
            continue
        ssp = rng.choice(SHRUB_SPECIES)
        svar = rng.randint(1, 12)
        slod = "LOD0" if math.hypot(tx, ty) < 280.0 else "LOD1"
        ssc = rng.uniform(0.75, 1.25)
        linker.spawn(col_understory, "botany/shrubs_oriental.blend", f"{ssp}_mature_{svar:02d}_{slod}",
                     f"shrubs_oriental:{ssp}_mature_{svar:02d}", (tx, ty, eval_sy_z(tx, ty)),
                     (0, 0, rng.uniform(0.0, math.tau)), (ssc, ssc, ssc), layout_records=layout_records)
        shrubs_placed += 1

    # Uferschilf an Euphrat, 10 Seen/Teichen & Kanaelen
    reeds_placed = 0
    for _ in range(2000):
        if reeds_placed >= 480:
            break
        if rng.random() < 0.45:
            ty = rng.uniform(-550.0, 550.0)
            bsgn = -1.0 if rng.random() < 0.5 else 1.0
            tx = float(eval_river_center_x_np(ty)) + bsgn * (float(eval_river_half_width_np(ty)) + rng.uniform(0.6, 3.0))
            gsp = "euphrates_reed"
        else:
            lk = rng.choice(ALLUVIAL_LAKES)
            ang = rng.uniform(0.0, math.tau)
            lobe = 1.0 + 0.16 * math.sin(ang * 2.0 + lk["seed"]) + 0.09 * math.cos(ang * 3.0 - lk["seed"] * 1.7)
            rf = rng.uniform(0.95, 1.12)
            lx = math.cos(ang) * lk["rx"] * lobe * rf
            ly = math.sin(ang) * lk["ry"] * lobe * rf
            c_y, s_y = math.cos(lk["yaw"]), math.sin(lk["yaw"])
            tx = lk["cx"] + lx * c_y - ly * s_y
            ty = lk["cy"] + lx * s_y + ly * c_y
            gsp = "euphrates_reed"
        if is_shipyard_work_zone(tx, ty, pad=1.5):
            continue
        gvar = rng.randint(1, 14)
        glod = "LOD0" if math.hypot(tx, ty) < 280.0 else "LOD1"
        gsc = rng.uniform(0.85, 1.30)
        linker.spawn(col_understory, "botany/grass_and_reeds.blend", f"{gsp}_mature_{gvar:02d}_{glod}",
                     f"grass_and_reeds:{gsp}_mature_{gvar:02d}", (tx, ty, eval_sy_z(tx, ty)),
                     (0, 0, rng.uniform(0.0, math.tau)), (gsc, gsc, gsc), layout_records=layout_records)
        reeds_placed += 1

    # Steppengras-Bueschel ausserhalb Ur-Schinar & Doerfer
    grass_placed = 0
    for _ in range(2800):
        if grass_placed >= 780:
            break
        rad = rng.uniform(86.0, 520.0)
        ang = rng.uniform(0.0, math.tau)
        tx, ty = rad * math.cos(ang), rad * math.sin(ang)
        if is_shipyard_work_zone(tx, ty, pad=2.0):
            continue
        if abs(tx - float(eval_river_center_x_np(ty))) < float(eval_river_half_width_np(ty)) + 1.5:
            continue
        if float(eval_alluvial_lake_field_np(np.array([tx]), np.array([ty]))[0][0]) < 1.04:
            continue
        gsp = "steppe_grass" if rng.random() < 0.7 else "tall_grass"
        gvar = rng.randint(1, 14)
        glod = "LOD0" if rad < 260.0 else "LOD1"
        gsc = rng.uniform(0.85, 1.35)
        linker.spawn(col_understory, "botany/grass_and_reeds.blend", f"{gsp}_mature_{gvar:02d}_{glod}",
                     f"grass_and_reeds:{gsp}_mature_{gvar:02d}", (tx, ty, eval_sy_z(tx, ty)),
                     (0, 0, rng.uniform(0.0, math.tau)), (gsc, gsc, gsc), layout_records=layout_records)
        grass_placed += 1

    # Getreide- & Flachsfelder rund um Ur & alle 10 Umland-Doerfer
    crop_parcels = [
        (88, 126, -210, -184, "barley"), (138, 174, -210, -184, "emmer_wheat"),
        (88, 132, -264, -228, "barley"), (194, 240, -210, -184, "barley"),
        (194, 244, -264, -228, "emmer_wheat"), (254, 294, -242, -198, "flax"),
        (312, 360, -132, -92, "barley"), (312, 355, -80, -45, "lentil_chickpea"),
        (314, 362, -14, 34, "barley"), (312, 356, 45, 92, "flax"),
        (-348, -300, -322, -278, "barley"), (-282, -240, -308, -268, "emmer_wheat"),
        (-224, -176, -310, -266, "barley"), (-164, -116, -324, -278, "flax"),
        (304, 354, -188, -144, "barley"), (362, 414, -182, -140, "emmer_wheat"),
        (306, 354, -260, -212, "flax"), (492, 540, -234, -186, "barley"),
        (436, 494, -84, -30, "emmer_wheat"), (502, 560, -22, 28, "barley"),
        (438, 494, 102, 154, "barley"), (504, 564, 118, 170, "lentil_chickpea"),
        (286, 338, 186, 240, "barley"), (346, 398, 186, 238, "emmer_wheat"),
        (-164, -112, -482, -432, "barley"), (-102, -48, -480, -430, "emmer_wheat"),
        (196, 244, -338, -292, "barley"), (72, 116, -328, -284, "emmer_wheat"),
        (-256, -210, -220, -182, "barley"), (-162, -120, -222, -184, "lentil_chickpea"),
        (308, 356, -360, -316, "barley"), (418, 466, -420, -376, "emmer_wheat"),
    ]
    for x0, x1, y0, y1, csp in crop_parcels:
        for cx_f in range(int(x0) + 3, int(x1), 7):
            for cy_f in range(int(y0) + 3, int(y1), 7):
                jx = cx_f + rng.uniform(-1.1, 1.1)
                jy = cy_f + rng.uniform(-1.1, 1.1)
                if is_shipyard_work_zone(jx, jy, pad=1.5):
                    continue
                cz = eval_sy_z(jx, jy)
                if cz < 0.78 or cz > 4.6:
                    continue
                cvar = rng.randint(1, 12)
                clod = "LOD0" if math.hypot(jx, jy) < 300.0 else "LOD1"
                csc = rng.uniform(1.15, 1.45)
                linker.spawn(col_understory, "botany/crops_mesopotamia.blend", f"{csp}_mature_{cvar:02d}_{clod}",
                             f"crops_mesopotamia:{csp}_mature_{cvar:02d}", (jx, jy, cz),
                             (0, 0, rng.uniform(0.0, math.tau)), (csc, csc, csc), layout_records=layout_records)

    # Kuratierte Temenos- & Brunnen-Zierbotanik (nur in Toepfen/Becken, KEIN wildes Strassen-Unkraut!)
    orn_spots = [
        ("terracotta_planter", 1, 164.0, -44.0, 0.90), ("terracotta_planter", 3, 176.0, -44.0, 0.90),
        ("terracotta_planter", 5, 164.0, -52.0, 0.90), ("terracotta_planter", 7, 176.0, -52.0, 0.90),
        ("pomegranate_ornamental", 8, 201.8, -39.4, 1.05), ("pomegranate_ornamental", 9, 215.2, -39.4, 1.05),
        ("myrtle_lily", 2, 201.8, -40.8, 0.95), ("myrtle_lily", 5, 215.2, -40.8, 0.95),
        ("lotus_cyperus", 1, 71.0, -83.2, 0.95), ("lotus_cyperus", 3, 76.5, -83.8, 0.95),
    ]
    for osp, ovar, ox, oy, osc in orn_spots:
        oz = z_canal_w if osp == "lotus_cyperus" else eval_sy_z(ox, oy) + 0.05
        linker.spawn(col_understory, "botany/ornamental_gardens.blend", f"{osp}_mature_{ovar:02d}_LOD0",
                     f"ornamental_gardens:{osp}_mature_{ovar:02d}", (ox, oy, oz),
                     (0, 0, rng.uniform(0.0, math.tau)), (osc, osc, osc), layout_records=layout_records)

    # 8) LICHT & 3 KONTROLLKAMERAS
    sun_obj = wbu.setup_nishita_sky_and_sun(scene, sun_elev_deg=31.0, sun_azim_deg=136.0, sun_energy=3.2, dust_density=1.15)
    col_lighting.objects.link(sun_obj)

    cam_aerial = wbu.add_camera(col_lighting, "Cam_Shipyard_Aerial", (-158.0, -228.0, 126.0), (74.0, -32.0, 6.0), lens=24.0)
    cam_city = wbu.add_camera(col_lighting, "Cam_Ur_City_Streets", (138.0, -48.0, 3.8), (182.0, -48.0, 2.2), lens=26.0)
    cam_aqua = wbu.add_camera(col_lighting, "Cam_Aqueduct_Valley", (22.0, 40.0, 22.5), (58.0, 68.0, 14.2), lens=28.0)
    scene.camera = cam_aerial

    # 9) SPEICHERN, GLB-TERRAIN EXPORTIEREN, LAYOUT-JSON SCHREIBEN & 3 PANORAMEN RENDERN
    print(f"[6/6] Speichere shipyard_world_master.blend, GLB, Layout ({len(layout_records)} Instanzen) & rendere 3 Previews...", flush=True)

    blend_path = os.path.join(wbu.WORLDS_BLEND_DIR, "shipyard_world_master.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    try:
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_mainfile()
    except Exception:
        pass

    # Layout JSON
    layout_path = os.path.join(wbu.WORLDS_OUT_DIR, "shipyard_layout.json")
    with open(layout_path, "w", encoding="utf-8") as f:
        json.dump({
            "scene": "shipyard",
            "worldSizeMeters": WORLD_SIZE,
            "arkPlaceholder": {"x": 0.0, "y": 0.0, "zSole": 0.0, "dims": [140.0, 23.333, 14.0]},
            "instanceCount": len(layout_records),
            "instances": layout_records,
        }, f)

    # Terrain GLB Export (mit sauberem Export-Material fuer kompaktes glTF, danach Master-Material wiederherstellen)
    terr_obj = terrain_export_objs[0]
    rich_terr_mat = terr_obj.data.materials[0]
    glb_mat = bpy.data.materials.new("Mat_Shipyard_Terrain_Export")
    glb_mat.use_nodes = True
    nt_g = glb_mat.node_tree
    bsdf_g = nt_g.nodes.get("Principled BSDF")
    bsdf_g.inputs["Roughness"].default_value = 0.90
    tex_g = nt_g.nodes.new("ShaderNodeTexImage")
    tex_g.image = bpy.data.images.load(os.path.abspath(splat_png))
    nt_g.links.new(tex_g.outputs["Color"], bsdf_g.inputs["Base Color"])
    terr_obj.data.materials[0] = glb_mat

    glb_path = os.path.join(wbu.WORLDS_OUT_DIR, "shipyard_terrain.glb")
    wbu.export_selected_objects_glb(terrain_export_objs, glb_path)

    terr_obj.data.materials[0] = rich_terr_mat
    bpy.data.materials.remove(glb_mat)
    bpy.ops.wm.save_mainfile()

    # Cycles CUDA Renders
    backend = wbu.setup_cycles(scene, samples=36, use_oidn=True, res_x=1600, res_y=900)
    print(f"    -> Cycles Backend: {backend}", flush=True)
    renders = [
        (cam_aerial, os.path.join(wbu.PREVIEWS_DIR, "world_shipyard_aerial.png")),
        (cam_city, os.path.join(wbu.PREVIEWS_DIR, "world_ur_city_streets.png")),
        (cam_aqua, os.path.join(wbu.PREVIEWS_DIR, "world_aqueduct_valley.png")),
    ]
    for cam_obj, out_png in renders:
        tr0 = time.time()
        scene.camera = cam_obj
        scene.render.filepath = out_png
        bpy.ops.render.render(write_still=True)
        print(f"    -> Gerendert: {os.path.basename(out_png)} in {time.time() - tr0:.1f}s", flush=True)

    print(
        f"SHIPYARD_WORLD_DONE instances={len(layout_records)} terrain_tris={terrain_tris} total_s={time.time() - t_start:.1f}",
        flush=True,
    )


def main():
    wbu.ensure_dirs()
    scene = wbu.clear_scene()
    populate_shipyard_world(scene)


if __name__ == "__main__":
    main()
