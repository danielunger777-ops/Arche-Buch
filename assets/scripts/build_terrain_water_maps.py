"""
build_terrain_water_maps.py — Blender Terrain-, Wege- & Wasser-Textur-Baker + Showcase
========================================================================================
Erzeugt und backt in Blender (Cycles CUDA GTX 1070 mit CPU-Fallback, je 1024x1024,
nahtlos kachelnd, HDR-Albedo strikt [0.06..0.68], BaseColor [sRGB], Normal [Linear], ORM [Linear]):

  1. terrain_city_earth_{baseColor,normal,orm}.png
       Festgestampfter mesopotamischer Stadt-Lehmboden & staubiges Kies-Pflaster (kein Gruen!)
  2. terrain_steppe_loam_{baseColor,normal,orm}.png
       Ruhiger, natuerlicher Steppenboden ohne Kachel-/Rissgitter mit feinen Staub-/Grasfasern
  3. terrain_alluvial_bank_{baseColor,normal,orm}.png
       Feuchter, fruchtbarer Auen- & Uferschlammboden (dunkelbraun-oliv bis sattes Ufergruen)
  4. terrain_organic_road_{baseColor,normal,orm}.png
       Organischer bronzezeitlicher Erd-/Karrenweg (U-kachelnd, RGBA mit weicher Alpha-Randmaske)
  5. water_blender_normal_a.png & water_blender_normal_b.png
       Gegenlaeufig kombinierbare, physikalisch weiche Wasser-Normalmaps aus Blenders FFT-Ocean-Sim
  6. water_blender_foam.png
       Organisches Ufer- & Wirbelschaum-Muster (Ocean-Foam + periodische Gischt-Zellen)
  7. assets/previews/terrain_water_showcase.png
       Studio-Kontrollrendering mit allen 4 Boeden, spiegelndem Wasserstreifen + Schaumkante
       sowie dem gemauerten Stadtbrunnen (ur_fountain_hero).

Aufruf:
  blender --background --python-exit-code 1 --python assets/scripts/build_terrain_water_maps.py
  blender --background --python-exit-code 1 --python assets/scripts/build_terrain_water_maps.py -- --bake-only
  blender --background --python-exit-code 1 --python assets/scripts/build_terrain_water_maps.py -- --showcase-only
"""

import os
import sys
import math
import time
import bpy
import numpy as np
from mathutils import Vector


TEX_SIZE = 1024
RELIEF_RES = 384      # High-Poly-Relief-Gitter pro Kachel (~295k Tris inkl. Schuerze)
WATER_OCEAN_RES = 32  # Ocean-Modifier-Aufloesung (mit 3x3 Wrap -> ~38k Tris)


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
# PERIODISCHE NUMPY NOISE-, VORONOI- & FARBWERKZEUGE
# ==============================================================================

def _hash2(ix, iy, seed=0):
    n = (ix * 374761393 + iy * 668265263 + seed * 1442695041) & 0x7FFFFFFF
    n = (n ^ (n >> 13)) * 1274126177
    n = n & 0x7FFFFFFF
    return (n & 0xFFFFFF) / float(0x1000000)


def periodic_noise(u, v, pu, pv=None, seed=0):
    """2D periodisches Value-Noise mit Quintic-Interpolation (Periode pu x pv)."""
    if pv is None:
        pv = pu
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


def periodic_fbm(u, v, pu, pv=None, octaves=4, seed=11, persistence=0.5):
    if pv is None:
        pv = pu
    acc = np.zeros_like(u, dtype=np.float32)
    amp = 0.5
    norm = 0.0
    for o in range(octaves):
        mul = 1 << o
        acc += amp * periodic_noise(u, v, pu * mul, pv * mul, seed + o * 131)
        norm += amp
        amp *= persistence
    return acc / max(1e-8, norm)


def periodic_voronoi(u, v, pu, pv=None, jitter=0.82, seed=101):
    """2D periodisches Voronoi/Worley: liefert (F1, F2 - F1, cell_id)."""
    if pv is None:
        pv = pu
    px = np.mod(u, 1.0) * pu
    py = np.mod(v, 1.0) * pv
    ix0 = np.floor(px).astype(np.int64)
    iy0 = np.floor(py).astype(np.int64)

    f1 = np.full_like(u, 1e9, dtype=np.float32)
    f2 = np.full_like(u, 1e9, dtype=np.float32)
    cid = np.zeros_like(u, dtype=np.float32)

    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            cx = (ix0 + dx) % pu
            cy = (iy0 + dy) % pv
            ox = 0.5 + (_hash2(cx, cy, seed) - 0.5) * jitter
            oy = 0.5 + (_hash2(cx, cy, seed + 53) - 0.5) * jitter
            ddx = (ix0 + dx + ox) - px
            ddy = (iy0 + dy + oy) - py
            d = np.sqrt(ddx * ddx + ddy * ddy)
            val = _hash2(cx, cy, seed + 199)
            m1 = d < f1
            f2 = np.where(m1, f1, np.minimum(f2, d))
            f1 = np.where(m1, d, f1)
            cid = np.where(m1, val, cid)
    return f1, np.maximum(0.0, f2 - f1), cid


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / np.maximum(1e-6, e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def lerp3(c0, c1, w):
    w3 = w[..., None]
    return c0 * (1.0 - w3) + c1 * w3


def _linear_to_srgb(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1.0 / 2.4) - 0.055)


def save_np_png(arr, filepath, is_srgb=False):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    h, w, c = arr.shape
    has_alpha = (c == 4)
    rgba = np.ones((h, w, 4), dtype=np.float32)
    if is_srgb:
        rgba[:, :, :3] = _linear_to_srgb(arr[:, :, :3])
    else:
        rgba[:, :, :3] = np.clip(arr[:, :, :3], 0.0, 1.0)
    if has_alpha:
        rgba[:, :, 3] = np.clip(arr[:, :, 3], 0.0, 1.0)  # Alpha bleibt strikt linear!

    img = bpy.data.images.new("_SaveTmp", width=w, height=h, alpha=has_alpha, float_buffer=False)
    img.colorspace_settings.name = "sRGB" if is_srgb else "Non-Color"
    img.pixels.foreach_set(rgba.ravel())
    img.filepath_raw = filepath
    img.file_format = "PNG"
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.image_settings.color_mode = "RGBA" if has_alpha else "RGB"
    bpy.context.scene.render.image_settings.color_depth = "8"
    img.save()
    bpy.data.images.remove(img)


def _arr_to_blender_image(name, arr_rgb, colorspace="Non-Color"):
    h, w, _ = arr_rgb.shape
    rgba = np.ones((h, w, 4), dtype=np.float32)
    rgba[:, :, :3] = arr_rgb
    img = bpy.data.images.new(name=name, width=w, height=h, alpha=False, float_buffer=True)
    img.colorspace_settings.name = colorspace
    img.pixels.foreach_set(rgba.ravel())
    return img


# ==============================================================================
# 1. PROZEDURALE GELAENDE- & WEGE-FELDER (1024x1024, HDR-ALBEDO 0.06..0.68)
# ==============================================================================

def eval_terrain_buffers(terrain_id, res=TEX_SIZE):
    """
    Erzeugt (albedo_rgba_or_rgb, height_m, roughness, periodic_v) fuer eines der 4 Materialien.
    Alle RGB-Albedowerte werden strikt auf [0.06 .. 0.68] geklemmt.
    """
    u_1d = (np.arange(res, dtype=np.float32) + 0.5) / res
    v_1d = (np.arange(res, dtype=np.float32) + 0.5) / res
    uu, vv = np.meshgrid(u_1d, v_1d, indexing="xy")

    n_wide  = periodic_fbm(uu, vv, 4, 4, octaves=4, seed=17)
    n_med   = periodic_fbm(uu, vv, 12, 12, octaves=4, seed=53)
    n_fine  = periodic_fbm(uu, vv, 40, 40, octaves=3, seed=109)
    n_micro = periodic_fbm(uu, vv, 96, 96, octaves=2, seed=211)

    if terrain_id == "terrain_city_earth":
        # Festgestampfter mesopotamischer Stadt-Lehmboden & staubiges Kies-Pflaster (KEIN Rasengruen!)
        # Organisch verdichtete Lauf-Areale, feine unregelmaessige Kiesel & lehmige Feinkorn-Struktur
        wu = uu + (n_wide - 0.5) * 0.14
        wv = vv + (periodic_fbm(uu, vv, 4, 4, octaves=3, seed=31) - 0.5) * 0.14
        trample = smoothstep(0.32, 0.72, periodic_fbm(wu, wv, 3, 3, octaves=4, seed=43))

        # Verformte, unregelmaessige Flusskiesel & Kalksteinsplitt (keine runden Polka-Dots!)
        warp_p = (n_fine - 0.5) * 0.14 + (n_micro - 0.5) * 0.08
        f1_a, _, cid_a = periodic_voronoi(uu, vv, 26, 26, jitter=0.95, seed=401)
        peb_a = (1.0 - smoothstep(0.08, 0.19, f1_a + warp_p)) * (cid_a > 0.62).astype(np.float32)
        f1_b, _, cid_b = periodic_voronoi(uu + 0.37, vv + 0.19, 54, 54, jitter=0.94, seed=433)
        peb_b = (1.0 - smoothstep(0.10, 0.22, f1_b + warp_p * 0.8)) * (cid_b > 0.48).astype(np.float32)
        pebbles = np.clip(peb_a * 0.85 + peb_b * 0.65, 0.0, 1.0)

        # Sehr feiner Mineral- & Lehmgries fuer knackscharfe Nahaufnahme
        clay_crumb = smoothstep(0.35, 0.78, n_fine * 0.55 + n_micro * 0.45)

        # Warme ocker-sandige Lehmpalette (0% Gruen!)
        clay_dark = np.array([0.215, 0.158, 0.098], dtype=np.float32)
        clay_mid  = np.array([0.315, 0.240, 0.154], dtype=np.float32)
        clay_dust = np.array([0.410, 0.320, 0.210], dtype=np.float32)

        alb = lerp3(clay_dark, clay_mid, clay_crumb * 0.72 + n_med * 0.28)
        alb = lerp3(alb, clay_dust, trample * 0.42 + n_micro * 0.14)

        # Kiesel dezent & staubintegriert (warme Ocker-/Kalk-/Basalttoene, nicht grell weiss)
        peb_tone = lerp3(
            np.array([0.20, 0.16, 0.12], dtype=np.float32),
            np.array([0.42, 0.36, 0.27], dtype=np.float32),
            np.clip(cid_a * 0.6 + cid_b * 0.4, 0.0, 1.0),
        )
        alb = lerp3(alb, peb_tone, pebbles * 0.65)

        hgt = (
            (n_wide - 0.5) * 0.009
            + (n_med - 0.5) * 0.007
            + (clay_crumb - 0.5) * 0.005
            - trample * 0.005
            + peb_a * 0.011
            + peb_b * 0.006
        )
        rgh = 0.89 - 0.10 * trample - 0.14 * pebbles + 0.04 * (n_micro - 0.5)
        return np.clip(alb, 0.06, 0.68), hgt, np.clip(rgh, 0.60, 0.96), True

    if terrain_id == "terrain_steppe_loam":
        # Ruhiger, natuerlicher mesopotamischer Steppenboden — KEIN Kachel-/Rissgitter!
        # Feinkoernige Schluff-/Lehmstruktur mit sanften Bodenwellen & dezenten Trockengras-Schlieren
        wu = uu + (n_wide - 0.5) * 0.12
        wv = vv + (periodic_fbm(uu, vv, 4, 4, octaves=3, seed=71) - 0.5) * 0.12
        loam_soft = periodic_fbm(wu, wv, 8, 8, octaves=5, seed=89, persistence=0.52)
        loam_grain = n_fine * 0.55 + n_micro * 0.45

        # Organisch geschwungene Trockengras-/Staubfasern (ohne gerade Pixelstriche!)
        wisp_field = periodic_fbm(wu + (n_med - 0.5) * 0.15, wv - (n_fine - 0.5) * 0.12, 24, 24, octaves=3, seed=137)
        dry_wisps = smoothstep(0.62, 0.82, wisp_field) * smoothstep(0.42, 0.78, n_micro)

        # Sehr feine Sand- & Steinkoernung
        f1_g, _, cid_g = periodic_voronoi(uu, vv, 44, 44, jitter=0.94, seed=163)
        tiny_grit = (1.0 - smoothstep(0.06, 0.16, f1_g + (n_micro - 0.5) * 0.10)) * (cid_g > 0.65).astype(np.float32)

        loam_lo  = np.array([0.235, 0.180, 0.115], dtype=np.float32)
        loam_mid = np.array([0.295, 0.232, 0.150], dtype=np.float32)
        loam_hi  = np.array([0.355, 0.285, 0.186], dtype=np.float32)
        wisp_c   = np.array([0.345, 0.288, 0.172], dtype=np.float32)

        alb = lerp3(loam_lo, loam_mid, smoothstep(0.28, 0.72, loam_soft * 0.65 + loam_grain * 0.35))
        alb = lerp3(alb, loam_hi, smoothstep(0.55, 0.85, loam_grain) * 0.38)
        alb = lerp3(alb, wisp_c, dry_wisps * 0.45)
        alb = lerp3(alb, np.array([0.37, 0.31, 0.22], dtype=np.float32), tiny_grit * 0.42)

        hgt = (
            (loam_soft - 0.5) * 0.010
            + (loam_grain - 0.5) * 0.006
            + dry_wisps * 0.004
            + tiny_grit * 0.004
        )
        rgh = 0.90 + 0.04 * (loam_grain - 0.5) + 0.03 * dry_wisps
        return np.clip(alb, 0.06, 0.68), hgt, np.clip(rgh, 0.80, 0.96), True

    if terrain_id == "terrain_alluvial_bank":
        # Feuchter, fruchtbarer Auen- & Uferschlammboden (dunkelbraun-oliv bis sattes Ufergruen)
        # Weiche, hochfrequent ausgefranste Uebergaenge ohne Flecken- oder Polka-Dot-Artefakte!
        wu = uu + (n_wide - 0.5) * 0.14
        wv = vv + (periodic_fbm(uu, vv, 4, 4, octaves=3, seed=229) - 0.5) * 0.14
        moisture = periodic_fbm(wu, wv, 5, 5, octaves=4, seed=251)
        veg_field = periodic_fbm(wu + 0.25, wv - 0.15, 6, 6, octaves=5, seed=277)
        # Hochfrequente Modulation verhindert scharfe Tarndruck-Konturen
        veg_patch = smoothstep(0.32, 0.70, veg_field * 0.72 + n_fine * 0.28)
        wet_mud_mask = smoothstep(0.62, 0.25, moisture * 0.75 + n_fine * 0.25) * (1.0 - veg_patch * 0.75)

        # Feine organische Ufergras-Halme & Moosfasern
        grass_tex = periodic_fbm(uu + (n_fine - 0.5) * 0.05, vv + (n_med - 0.5) * 0.05, 32, 32, octaves=3, seed=293)
        moss_tuft = smoothstep(0.38, 0.76, grass_tex * 0.65 + n_micro * 0.35)

        mud_wet   = np.array([0.088, 0.072, 0.048], dtype=np.float32)  # dunkler, feuchter Auen-Schlamm
        mud_olive = np.array([0.158, 0.138, 0.078], dtype=np.float32)  # braun-oliver Schlick
        bank_moss = np.array([0.118, 0.192, 0.068], dtype=np.float32)  # sattes feuchtes Ufermoos
        bank_lush = np.array([0.182, 0.272, 0.086], dtype=np.float32)  # frisches Ried-/Ufergruen

        alb = lerp3(mud_olive, mud_wet, wet_mud_mask * 0.78)
        alb = lerp3(alb, mud_olive * 1.15, (n_micro - 0.5) * 0.22 * (1.0 - veg_patch))
        green_col = lerp3(bank_moss, bank_lush, moss_tuft)
        alb = lerp3(alb, green_col, veg_patch * 0.86)

        hgt = (
            (moisture - 0.5) * 0.014
            + veg_patch * 0.014
            + moss_tuft * veg_patch * 0.009
            - wet_mud_mask * 0.010
            + (n_fine - 0.5) * 0.005
        )
        rgh = 0.78 - 0.36 * wet_mud_mask + 0.11 * veg_patch + 0.04 * (n_micro - 0.5)
        return np.clip(alb, 0.06, 0.68), hgt, np.clip(rgh, 0.36, 0.94), True

    if terrain_id == "terrain_organic_road":
        # Organischer bronzezeitlicher Erd-/Karrenweg (nahtlos entlang U, weiche Alpha-Randmaske entlang V!)
        wander = (periodic_fbm(uu, np.full_like(uu, 0.5), 3, 2, octaves=3, seed=503) - 0.5) * 0.055
        v_rel = vv - 0.5 + wander

        edge_noise = (n_wide - 0.5) * 0.14 + (n_med - 0.5) * 0.08 + (n_fine - 0.5) * 0.04
        dist_edge = np.abs(v_rel) * 2.0 + edge_noise
        alpha_mask = 1.0 - smoothstep(0.50, 0.92, dist_edge)
        v_safe_fade = smoothstep(0.015, 0.085, vv) * (1.0 - smoothstep(0.915, 0.985, vv))
        alpha_mask = np.clip(alpha_mask * v_safe_fade, 0.0, 1.0)

        rut_l = np.exp(-((v_rel + 0.175) / 0.068) ** 2)
        rut_r = np.exp(-((v_rel - 0.175) / 0.068) ** 2)
        ruts = np.maximum(rut_l, rut_r) * (0.78 + 0.22 * n_med)
        crown = np.exp(-(v_rel / 0.11) ** 2) * 0.55

        # Verformte Kieselstreuung (keine runden Polka-Dots!)
        warp_r = (n_fine - 0.5) * 0.13 + (n_micro - 0.5) * 0.07
        f1_r, _, cid_r = periodic_voronoi(uu, vv, 28, 28, jitter=0.95, seed=521)
        peb_zone = np.clip(0.30 + 0.75 * crown + 0.60 * smoothstep(0.24, 0.36, np.abs(v_rel)) - 0.65 * ruts, 0.12, 1.0)
        peb_r = (1.0 - smoothstep(0.08, 0.19, f1_r + warp_r)) * (cid_r > 0.55).astype(np.float32) * peb_zone
        f1_r2, _, cid_r2 = periodic_voronoi(uu + 0.29, vv + 0.41, 56, 56, jitter=0.94, seed=547)
        peb_r2 = (1.0 - smoothstep(0.10, 0.22, f1_r2 + warp_r * 0.8)) * (cid_r2 > 0.45).astype(np.float32) * peb_zone
        pebbles = np.clip(peb_r * 0.85 + peb_r2 * 0.60, 0.0, 1.0)

        road_base = lerp3(
            np.array([0.235, 0.178, 0.112], dtype=np.float32),
            np.array([0.355, 0.278, 0.180], dtype=np.float32),
            n_med * 0.55 + n_fine * 0.30 + n_micro * 0.15,
        )
        rut_col = np.array([0.165, 0.120, 0.074], dtype=np.float32)
        alb = lerp3(road_base, rut_col, ruts * 0.72)
        alb = lerp3(alb, np.array([0.40, 0.32, 0.20], dtype=np.float32), crown * 0.26 * n_fine)
        peb_col = lerp3(
            np.array([0.21, 0.17, 0.13], dtype=np.float32),
            np.array([0.42, 0.36, 0.28], dtype=np.float32),
            cid_r * 0.65 + cid_r2 * 0.35,
        )
        alb = lerp3(alb, peb_col, pebbles * 0.70)
        alb = np.clip(alb, 0.06, 0.68)

        hgt = (
            (n_med - 0.5) * 0.009
            + (n_fine - 0.5) * 0.004
            + crown * 0.012
            - ruts * 0.026
            + peb_r * 0.011
            + peb_r2 * 0.006
        )
        rgh = 0.88 - 0.20 * ruts - 0.12 * pebbles + 0.04 * (1.0 - alpha_mask)
        rgba = np.concatenate([alb, alpha_mask[..., None]], axis=-1)
        return rgba, hgt, np.clip(rgh, 0.56, 0.96), False

    raise ValueError(f"Unbekannte Terrain-ID: {terrain_id}")


def _build_terrain_relief_mesh(hgt, nu=RELIEF_RES, nv=RELIEF_RES, apron=0.06, periodic_v=True):
    """Erzeugt 4x4m High-Poly-Relief inkl. periodischer Wrap-Schuerze fuer kantenfreie Cycles-Bakes."""
    h_src, w_src = hgt.shape
    u_vals = np.linspace(-apron, 1.0 + apron, nu + 1, dtype=np.float32)
    v_vals = np.linspace(-apron if periodic_v else 0.0, 1.0 + apron if periodic_v else 1.0, nv + 1, dtype=np.float32)
    uu, vv = np.meshgrid(u_vals, v_vals, indexing="xy")

    px = np.mod(uu, 1.0) * w_src
    py = (np.mod(vv, 1.0) if periodic_v else np.clip(vv, 0.0, 1.0)) * (h_src if periodic_v else (h_src - 1))
    ix = np.floor(px).astype(np.int64) % w_src
    iy = (np.floor(py).astype(np.int64) % h_src) if periodic_v else np.clip(np.round(py).astype(np.int64), 0, h_src - 1)
    zz = hgt[iy, ix]

    xg = uu * 4.0
    yg = vv * 4.0

    mesh = bpy.data.meshes.new("TerrainHiPoly")
    verts = np.column_stack([xg.ravel(), yg.ravel(), zz.ravel()]).tolist()
    stride = nu + 1
    ii, jj = np.meshgrid(np.arange(nu), np.arange(nv), indexing="xy")
    v00 = (jj * stride + ii).ravel()
    faces = np.column_stack([v00, v00 + 1, v00 + stride + 1, v00 + stride]).tolist()
    mesh.from_pydata(verts, [], faces)
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))

    uv_layer = mesh.uv_layers.new(name="UVMap")
    # Keine np.mod-Spruenge auf der UVMap, da REPEAT in Cycles negativ/ueber-1 nahtlos kachelt!
    uv_u = uu.ravel()
    uv_v = (vv if periodic_v else np.clip(vv, 0.0, 1.0)).ravel()
    loop_v = np.empty(len(mesh.loops), dtype=np.int64)
    mesh.loops.foreach_get("vertex_index", loop_v)
    uv_arr = np.column_stack([uv_u[loop_v], uv_v[loop_v]]).astype(np.float32)
    uv_layer.data.foreach_set("uv", uv_arr.ravel())

    obj = bpy.data.objects.new("TerrainHiPoly", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def _build_plane_target(name, size_x=4.0, size_y=4.0, offset_x=0.0, offset_y=0.0):
    mesh = bpy.data.meshes.new(name)
    verts = [
        (offset_x, offset_y, 0.0),
        (offset_x + size_x, offset_y, 0.0),
        (offset_x + size_x, offset_y + size_y, 0.0),
        (offset_x, offset_y + size_y, 0.0),
    ]
    mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
    uv_layer = mesh.uv_layers.new(name="UVMap")
    for loop, uv in zip(mesh.loops, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]):
        uv_layer.data[loop.index].uv = uv
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def bake_terrain_material(terrain_id, tex_dir):
    t0 = time.time()
    print(f"[TERRAIN {terrain_id}] Berechne 1024x1024 Felder...", flush=True)
    alb_data, hgt, rgh, periodic_v = eval_terrain_buffers(terrain_id, TEX_SIZE)

    scene = clear_scene()
    dev = setup_cycles(scene, samples=4, use_oidn=False)
    print(f"[TERRAIN {terrain_id}] Baue Relief ({RELIEF_RES}x{RELIEF_RES}) & backe Normal/AO auf {dev}...", flush=True)

    hi_obj = _build_terrain_relief_mesh(hgt, nu=RELIEF_RES, nv=RELIEF_RES, apron=0.06, periodic_v=periodic_v)
    lo_obj = _build_plane_target(f"Lo_{terrain_id}", 4.0, 4.0)

    # High-Poly Material mit feiner Mikro-Bump-Map aus dem 1024er Hoehenfeld fuer knackige Normal-Details
    hi_mat = bpy.data.materials.new(f"HiMat_{terrain_id}")
    hi_mat.use_nodes = True
    nt_h = hi_mat.node_tree
    nt_h.nodes.clear()
    out_h = nt_h.nodes.new("ShaderNodeOutputMaterial")
    bsdf_h = nt_h.nodes.new("ShaderNodeBsdfPrincipled")
    nt_h.links.new(bsdf_h.outputs["BSDF"], out_h.inputs["Surface"])

    # Normiertes Hoehenfeld [0..1] als Mikro-Bump
    h_min, h_max = float(hgt.min()), float(hgt.max())
    h_norm = (hgt - h_min) / max(1e-5, h_max - h_min)
    img_h = _arr_to_blender_image(f"TmpHgt_{terrain_id}", np.repeat(h_norm[..., None], 3, axis=-1), "Non-Color")
    tex_h = nt_h.nodes.new("ShaderNodeTexImage")
    tex_h.image = img_h
    tex_h.extension = "REPEAT"
    bump = nt_h.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.28
    bump.inputs["Distance"].default_value = 0.015
    nt_h.links.new(tex_h.outputs["Color"], bump.inputs["Height"])
    nt_h.links.new(bump.outputs["Normal"], bsdf_h.inputs["Normal"])
    hi_obj.data.materials.append(hi_mat)

    lo_mat = bpy.data.materials.new(f"LoMat_{terrain_id}")
    lo_mat.use_nodes = True
    lo_obj.data.materials.append(lo_mat)

    img_nrm = bpy.data.images.new(f"BakeNrm_{terrain_id}", width=TEX_SIZE, height=TEX_SIZE, alpha=False, float_buffer=True)
    img_nrm.colorspace_settings.name = "Non-Color"
    img_ao  = bpy.data.images.new(f"BakeAO_{terrain_id}", width=TEX_SIZE, height=TEX_SIZE, alpha=False, float_buffer=True)
    img_ao.colorspace_settings.name = "Non-Color"

    tn = lo_mat.node_tree.nodes.new("ShaderNodeTexImage")
    tn.image = img_nrm
    lo_mat.node_tree.nodes.active = tn

    bpy.ops.object.select_all(action="DESELECT")
    hi_obj.select_set(True)
    lo_obj.select_set(True)
    bpy.context.view_layer.objects.active = lo_obj

    scene.render.bake.use_selected_to_active = True
    scene.render.bake.cage_extrusion = 0.16
    scene.render.bake.max_ray_distance = 0.32
    scene.render.bake.margin = 0

    scene.cycles.samples = 4
    scene.cycles.use_denoising = False
    bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")

    tn.image = img_ao
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    try:
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    bpy.ops.object.bake(type="AO")

    nrm_arr = np.empty(TEX_SIZE * TEX_SIZE * 4, dtype=np.float32)
    img_nrm.pixels.foreach_get(nrm_arr)
    nrm_rgb = np.clip(nrm_arr.reshape((TEX_SIZE, TEX_SIZE, 4))[:, :, :3], 0.0, 1.0)

    ao_arr = np.empty(TEX_SIZE * TEX_SIZE * 4, dtype=np.float32)
    img_ao.pixels.foreach_get(ao_arr)
    ao_r = np.clip(ao_arr.reshape((TEX_SIZE, TEX_SIZE, 4))[:, :, 0], 0.25, 1.0)

    orm_rgb = np.stack([ao_r, rgh, np.zeros_like(ao_r)], axis=-1)

    p_alb = os.path.join(tex_dir, f"{terrain_id}_baseColor.png")
    p_nrm = os.path.join(tex_dir, f"{terrain_id}_normal.png")
    p_orm = os.path.join(tex_dir, f"{terrain_id}_orm.png")

    save_np_png(alb_data, p_alb, is_srgb=True)
    save_np_png(nrm_rgb, p_nrm, is_srgb=False)
    save_np_png(orm_rgb, p_orm, is_srgb=False)

    # Kachelnaht-Kontrolle
    seam_u_alb = float(np.mean(np.abs(alb_data[:, 0, :3] - alb_data[:, -1, :3])))
    seam_u_nrm = float(np.mean(np.abs(nrm_rgb[:, 0, :] - nrm_rgb[:, -1, :])))
    seam_v_alb = float(np.mean(np.abs(alb_data[0, :, :3] - alb_data[-1, :, :3]))) if periodic_v else 0.0
    dt = time.time() - t0
    print(
        f"[TERRAIN {terrain_id}] FERTIG in {dt:.1f}s ({dev}) | Albedo=[{alb_data[..., :3].min():.3f}..{alb_data[..., :3].max():.3f}] | "
        f"AO=[{ao_r.min():.2f}..{ao_r.max():.2f}] | Seam(U_alb={seam_u_alb:.4f}, U_nrm={seam_u_nrm:.4f}, V_alb={seam_v_alb:.4f})",
        flush=True,
    )
    return [p_alb, p_nrm, p_orm]


# ==============================================================================
# 2. BLENDER OCEAN-WAVE & FOAM WATER MAPS (1024x1024, SEAMLESS 2D)
# ==============================================================================

def _build_periodic_capillary_height(res=TEX_SIZE, angle_rad=0.35, wind_freq=10, cross_freq=5, seed=701):
    """Erzeugt weiche, physikalische Kapillar-Windrippel ohne Plastikfolie-Knitter."""
    u_1d = (np.arange(res, dtype=np.float32) + 0.5) / res
    v_1d = (np.arange(res, dtype=np.float32) + 0.5) / res
    uu, vv = np.meshgrid(u_1d, v_1d, indexing="xy")

    # Ganzzahlig periodisch rotierte Wellen-Kombination (keine scharfen Spitzen!)
    ca = int(round(math.cos(angle_rad) * wind_freq))
    sa = int(round(math.sin(angle_rad) * wind_freq))
    cb = int(round(math.cos(angle_rad + 0.58) * cross_freq))
    sb = int(round(math.sin(angle_rad + 0.58) * cross_freq))

    n_warp = periodic_fbm(uu, vv, 4, 4, octaves=3, seed=seed) * 0.45
    w1 = np.sin(2.0 * math.pi * (ca * uu + sa * vv) + n_warp * 3.0)
    w2 = np.sin(2.0 * math.pi * (cb * uu + sb * vv) - n_warp * 2.4)
    w3 = np.sin(2.0 * math.pi * ((ca * 2 - sb) * uu + (sa * 2 + cb) * vv) + periodic_fbm(uu, vv, 8, 8, 2, seed + 23) * 2.2)

    # Weiche Gerstner-aehnliche Abrundung
    h = 0.50 * w1 + 0.32 * w2 + 0.18 * w3
    h = (h - h.min()) / max(1e-6, h.max() - h.min())
    return h


def bake_water_normal_map(filename, tex_dir, spatial_size, wind_velocity, wave_scale, wave_alignment, wave_direction, choppiness, sim_time, seed, cap_angle):
    t0 = time.time()
    scene = clear_scene()
    dev = setup_cycles(scene, samples=4, use_oidn=False)
    print(f"[WATER {filename}] Erzeuge Blender Ocean-Sim (res={WATER_OCEAN_RES}, 3x3 Wrap) auf {dev}...", flush=True)

    # Ocean-Modifier mit repeat_x=3, repeat_y=3 -> mittlerer Block [L*0.5 .. L*1.5] ist 100% periodisch umgeben!
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, 0.0, 0.0))
    oc_raw = bpy.context.active_object
    mod = oc_raw.modifiers.new("OceanSim", "OCEAN")
    mod.geometry_mode = "GENERATE"
    mod.spatial_size = int(spatial_size)
    mod.resolution = WATER_OCEAN_RES
    mod.wind_velocity = wind_velocity
    mod.wave_scale = wave_scale
    mod.wave_scale_min = 0.06
    mod.wave_alignment = wave_alignment
    mod.wave_direction = wave_direction
    mod.choppiness = choppiness
    mod.damping = 0.70
    mod.depth = 12.0
    mod.time = sim_time
    mod.random_seed = seed
    mod.repeat_x = 3
    mod.repeat_y = 3
    mod.use_normals = True
    mod.use_foam = True
    mod.foam_layer_name = "foam"
    mod.foam_coverage = 0.35

    deps = bpy.context.evaluated_depsgraph_get()
    eval_obj = oc_raw.evaluated_get(deps)
    hi_mesh = bpy.data.meshes.new_from_object(eval_obj)
    hi_mesh.polygons.foreach_set("use_smooth", [True] * len(hi_mesh.polygons))
    hi_obj = bpy.data.objects.new("OceanHi", hi_mesh)
    bpy.context.collection.objects.link(hi_obj)
    bpy.data.objects.remove(oc_raw, do_unlink=True)

    # Mittlere Kachel liegt exakt bei [spatial_size*0.5 .. spatial_size*1.5]^2!
    L = float(spatial_size)
    half_L = L * 0.5
    lo_obj = _build_plane_target("OceanLo", L, L, offset_x=half_L, offset_y=half_L)

    # High-Poly Shader mit weichem periodischem Kapillar-Ripples-Bump
    hi_mat = bpy.data.materials.new("WaterHiMat")
    hi_mat.use_nodes = True
    nt_h = hi_mat.node_tree
    nt_h.nodes.clear()
    out_h = nt_h.nodes.new("ShaderNodeOutputMaterial")
    bsdf_h = nt_h.nodes.new("ShaderNodeBsdfPrincipled")
    nt_h.links.new(bsdf_h.outputs["BSDF"], out_h.inputs["Surface"])

    cap_h = _build_periodic_capillary_height(TEX_SIZE, angle_rad=cap_angle, wind_freq=10, cross_freq=6, seed=seed + 500)
    img_cap = _arr_to_blender_image(f"Cap_{filename}", np.repeat(cap_h[..., None], 3, axis=-1), "Non-Color")

    # Welt-Koordinaten auf [0..1] pro spatial_size mappen -> nahtlos periodisch!
    tex_coord = nt_h.nodes.new("ShaderNodeTexCoord")
    mapping = nt_h.nodes.new("ShaderNodeMapping")
    mapping.inputs["Location"].default_value = (-0.5, -0.5, 0.0)
    mapping.inputs["Scale"].default_value = (1.0 / L, 1.0 / L, 1.0)
    nt_h.links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

    tex_cap = nt_h.nodes.new("ShaderNodeTexImage")
    tex_cap.image = img_cap
    tex_cap.extension = "REPEAT"
    nt_h.links.new(mapping.outputs["Vector"], tex_cap.inputs["Vector"])

    bump = nt_h.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.065  # physikalisch weich (keine Plastikfolie!)
    bump.inputs["Distance"].default_value = 0.012
    nt_h.links.new(tex_cap.outputs["Color"], bump.inputs["Height"])
    nt_h.links.new(bump.outputs["Normal"], bsdf_h.inputs["Normal"])
    hi_obj.data.materials.append(hi_mat)

    lo_mat = bpy.data.materials.new("WaterLoMat")
    lo_mat.use_nodes = True
    lo_obj.data.materials.append(lo_mat)

    img_nrm = bpy.data.images.new(f"Bake_{filename}", width=TEX_SIZE, height=TEX_SIZE, alpha=False, float_buffer=True)
    img_nrm.colorspace_settings.name = "Non-Color"
    tn = lo_mat.node_tree.nodes.new("ShaderNodeTexImage")
    tn.image = img_nrm
    lo_mat.node_tree.nodes.active = tn

    bpy.ops.object.select_all(action="DESELECT")
    hi_obj.select_set(True)
    lo_obj.select_set(True)
    bpy.context.view_layer.objects.active = lo_obj

    scene.render.bake.use_selected_to_active = True
    scene.render.bake.cage_extrusion = 1.6
    scene.render.bake.max_ray_distance = 3.2
    scene.render.bake.margin = 0
    scene.cycles.samples = 4
    scene.cycles.use_denoising = False
    bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")

    nrm_arr = np.empty(TEX_SIZE * TEX_SIZE * 4, dtype=np.float32)
    img_nrm.pixels.foreach_get(nrm_arr)
    nrm_rgb = np.clip(nrm_arr.reshape((TEX_SIZE, TEX_SIZE, 4))[:, :, :3], 0.0, 1.0)

    out_path = os.path.join(tex_dir, filename)
    save_np_png(nrm_rgb, out_path, is_srgb=False)

    seam_u = float(np.mean(np.abs(nrm_rgb[:, 0, :] - nrm_rgb[:, -1, :])))
    seam_v = float(np.mean(np.abs(nrm_rgb[0, :, :] - nrm_rgb[-1, :, :])))
    dt = time.time() - t0
    print(
        f"[WATER {filename}] FERTIG in {dt:.1f}s ({dev}) | NrmRange X=[{nrm_rgb[...,0].min():.3f}..{nrm_rgb[...,0].max():.3f}] "
        f"Y=[{nrm_rgb[...,1].min():.3f}..{nrm_rgb[...,1].max():.3f}] | Seam(U={seam_u:.4f}, V={seam_v:.4f})",
        flush=True,
    )
    return out_path


def bake_water_foam_map(tex_dir):
    """
    Backt organische Ufer- & Wirbelschaum-Map (1024x1024):
    Kombiniert Blenders Ocean-Foam-Attribut mit mehrskaligen periodischen Gischt-/Blasen-Zellen.
    """
    t0 = time.time()
    scene = clear_scene()
    dev = setup_cycles(scene, samples=4, use_oidn=False)
    print(f"[WATER water_blender_foam.png] Bake Ocean-Foam + Gischt-Zellen auf {dev}...", flush=True)

    L = 16
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, 0.0, 0.0))
    oc_raw = bpy.context.active_object
    mod = oc_raw.modifiers.new("OceanFoam", "OCEAN")
    mod.geometry_mode = "GENERATE"
    mod.spatial_size = L
    mod.resolution = WATER_OCEAN_RES
    mod.wind_velocity = 5.5
    mod.wave_scale = 0.28
    mod.wave_alignment = 0.25
    mod.wave_direction = 0.45
    mod.choppiness = 1.25
    mod.damping = 0.60
    mod.time = 2.1
    mod.random_seed = 313
    mod.repeat_x = 3
    mod.repeat_y = 3
    mod.use_foam = True
    mod.foam_layer_name = "foam"
    mod.foam_coverage = 0.42

    deps = bpy.context.evaluated_depsgraph_get()
    eval_obj = oc_raw.evaluated_get(deps)
    hi_mesh = bpy.data.meshes.new_from_object(eval_obj)
    hi_obj = bpy.data.objects.new("FoamHi", hi_mesh)
    bpy.context.collection.objects.link(hi_obj)
    bpy.data.objects.remove(oc_raw, do_unlink=True)

    half_L = L * 0.5
    lo_obj = _build_plane_target("FoamLo", float(L), float(L), offset_x=half_L, offset_y=half_L)

    hi_mat = bpy.data.materials.new("FoamHiMat")
    hi_mat.use_nodes = True
    nt_h = hi_mat.node_tree
    nt_h.nodes.clear()
    out_h = nt_h.nodes.new("ShaderNodeOutputMaterial")
    emit_h = nt_h.nodes.new("ShaderNodeEmission")
    attr_f = nt_h.nodes.new("ShaderNodeAttribute")
    attr_f.attribute_name = "foam"
    nt_h.links.new(attr_f.outputs["Color"], emit_h.inputs["Color"])
    nt_h.links.new(emit_h.outputs["Emission"], out_h.inputs["Surface"])
    hi_obj.data.materials.append(hi_mat)

    lo_mat = bpy.data.materials.new("FoamLoMat")
    lo_mat.use_nodes = True
    lo_obj.data.materials.append(lo_mat)

    img_ocean_foam = bpy.data.images.new("BakeOceanFoam", width=TEX_SIZE, height=TEX_SIZE, alpha=False, float_buffer=True)
    img_ocean_foam.colorspace_settings.name = "Non-Color"
    tn = lo_mat.node_tree.nodes.new("ShaderNodeTexImage")
    tn.image = img_ocean_foam
    lo_mat.node_tree.nodes.active = tn

    bpy.ops.object.select_all(action="DESELECT")
    hi_obj.select_set(True)
    lo_obj.select_set(True)
    bpy.context.view_layer.objects.active = lo_obj

    scene.render.bake.use_selected_to_active = True
    scene.render.bake.cage_extrusion = 2.0
    scene.render.bake.max_ray_distance = 4.0
    scene.render.bake.margin = 0
    bpy.ops.object.bake(type="EMIT")

    of_arr = np.empty(TEX_SIZE * TEX_SIZE * 4, dtype=np.float32)
    img_ocean_foam.pixels.foreach_get(of_arr)
    ocean_foam = np.clip(of_arr.reshape((TEX_SIZE, TEX_SIZE, 4))[:, :, 0], 0.0, 1.0)
    # Ocean-Foam normieren auf [0..1]
    of_norm = np.clip((ocean_foam - 0.14) / 0.58, 0.0, 1.0)

    # Periodische Gischt-Blasen & Wirbel-Filamente (Voronoi-Spitzennetz, kein hartes Gitter)
    u_1d = (np.arange(TEX_SIZE, dtype=np.float32) + 0.5) / TEX_SIZE
    v_1d = (np.arange(TEX_SIZE, dtype=np.float32) + 0.5) / TEX_SIZE
    uu, vv = np.meshgrid(u_1d, v_1d, indexing="xy")

    # Wirbel-Domain-Warp fuer organische Stroemungsstraehnen
    wu = uu + (periodic_fbm(uu, vv, 5, 5, octaves=3, seed=809) - 0.5) * 0.10
    wv = vv + (periodic_fbm(uu, vv, 5, 5, octaves=3, seed=823) - 0.5) * 0.10

    _, edge_lg, _ = periodic_voronoi(wu, wv, 16, 16, jitter=0.94, seed=839)
    _, edge_md, _ = periodic_voronoi(wu + 0.31, wv + 0.17, 34, 34, jitter=0.92, seed=857)
    _, edge_sm, _ = periodic_voronoi(uu, vv, 68, 68, jitter=0.90, seed=881)

    # Duenne feine Blasenwaende (hoch an F2-F1 ~ 0 -> offene Wasserloecher in der Zellmitte!)
    web_lg = 1.0 - smoothstep(0.015, 0.095, edge_lg)
    web_md = 1.0 - smoothstep(0.020, 0.120, edge_md)
    web_sm = 1.0 - smoothstep(0.025, 0.155, edge_sm)

    swirl_mask = smoothstep(0.30, 0.72, periodic_fbm(wu, wv, 6, 6, octaves=4, seed=907))
    foam_lace = np.clip(web_lg * 0.62 + web_md * 0.58 + web_sm * 0.42, 0.0, 1.0)
    foam_val = np.clip(
        foam_lace * (0.36 + 0.64 * np.maximum(of_norm, swirl_mask * 0.75)) + of_norm * 0.28 * web_md,
        0.0,
        1.0,
    )
    foam_val = np.power(foam_val, 0.92)
    foam_rgb = np.stack([foam_val, foam_val, foam_val], axis=-1)

    out_path = os.path.join(tex_dir, "water_blender_foam.png")
    save_np_png(foam_rgb, out_path, is_srgb=False)

    seam_of_u = float(np.mean(np.abs(of_norm[:, 0] - of_norm[:, -1])))
    seam_of_v = float(np.mean(np.abs(of_norm[0, :] - of_norm[-1, :])))
    seam_u = float(np.mean(np.abs(foam_rgb[:, 0, :] - foam_rgb[:, -1, :])))
    seam_v = float(np.mean(np.abs(foam_rgb[0, :, :] - foam_rgb[-1, :, :])))
    dt = time.time() - t0
    print(
        f"[WATER water_blender_foam.png] FERTIG in {dt:.1f}s ({dev}) | Foam=[{foam_val.min():.3f}..{foam_val.max():.3f}] | "
        f"OceanSeam=({seam_of_u:.4f},{seam_of_v:.4f}) TotalSeam(U={seam_u:.4f}, V={seam_v:.4f})",
        flush=True,
    )
    return out_path


# ==============================================================================
# 3. KONTROLL-RENDERING (assets/previews/terrain_water_showcase.png)
# ==============================================================================

def _make_pbr_terrain_mat(name, tex_dir, prefix, has_alpha=False, repeat=1.6):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (repeat, 1.0 if has_alpha else repeat, 1.0)
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"])

    img_c = bpy.data.images.load(os.path.join(tex_dir, f"{prefix}_baseColor.png"), check_existing=True)
    img_c.colorspace_settings.name = "sRGB"
    img_n = bpy.data.images.load(os.path.join(tex_dir, f"{prefix}_normal.png"), check_existing=True)
    img_n.colorspace_settings.name = "Non-Color"
    img_o = bpy.data.images.load(os.path.join(tex_dir, f"{prefix}_orm.png"), check_existing=True)
    img_o.colorspace_settings.name = "Non-Color"

    t_c = nt.nodes.new("ShaderNodeTexImage"); t_c.image = img_c
    t_n = nt.nodes.new("ShaderNodeTexImage"); t_n.image = img_n
    t_o = nt.nodes.new("ShaderNodeTexImage"); t_o.image = img_o
    # REPEAT fuer nahtlose U-Kachelung auch beim organischen Weg (Alpha=0 an V=0/1 schuetzt die Kanten!)
    for tn in (t_c, t_n, t_o):
        tn.extension = "REPEAT"
        nt.links.new(mp.outputs["Vector"], tn.inputs["Vector"])

    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(t_o.outputs["Color"], sep.inputs["Color"])

    nrm = nt.nodes.new("ShaderNodeNormalMap")
    nrm.inputs["Strength"].default_value = 0.90
    nt.links.new(t_n.outputs["Color"], nrm.inputs["Color"])

    nt.links.new(t_c.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    nt.links.new(nrm.outputs["Normal"], bsdf.inputs["Normal"])
    if has_alpha:
        nt.links.new(t_c.outputs["Alpha"], bsdf.inputs["Alpha"])
    return mat


def _make_showcase_water_mat(tex_dir):
    """Spiegelndes Bronzezeit-Kanalwasser mit Normal A + Normal B und Ufer-Schaumkante."""
    mat = bpy.data.materials.new("Mat_Showcase_Water")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.032
    bsdf.inputs["IOR"].default_value = 1.333
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.72
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.45
        bsdf.inputs["Coat Roughness"].default_value = 0.02
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = nt.nodes.new("ShaderNodeTexCoord")

    # Gegenlaeufige UVs fuer Normal A und Normal B
    mp_a = nt.nodes.new("ShaderNodeMapping")
    mp_a.inputs["Scale"].default_value = (2.2, 1.4, 1.0)
    mp_a.inputs["Rotation"].default_value = (0.0, 0.0, 0.12)
    nt.links.new(tc.outputs["UV"], mp_a.inputs["Vector"])

    mp_b = nt.nodes.new("ShaderNodeMapping")
    mp_b.inputs["Scale"].default_value = (3.1, 2.0, 1.0)
    mp_b.inputs["Rotation"].default_value = (0.0, 0.0, -0.45)
    nt.links.new(tc.outputs["UV"], mp_b.inputs["Vector"])

    mp_f = nt.nodes.new("ShaderNodeMapping")
    mp_f.inputs["Scale"].default_value = (4.5, 2.6, 1.0)
    nt.links.new(tc.outputs["UV"], mp_f.inputs["Vector"])

    img_na = bpy.data.images.load(os.path.join(tex_dir, "water_blender_normal_a.png"), check_existing=True)
    img_na.colorspace_settings.name = "Non-Color"
    img_nb = bpy.data.images.load(os.path.join(tex_dir, "water_blender_normal_b.png"), check_existing=True)
    img_nb.colorspace_settings.name = "Non-Color"
    img_fm = bpy.data.images.load(os.path.join(tex_dir, "water_blender_foam.png"), check_existing=True)
    img_fm.colorspace_settings.name = "Non-Color"

    t_na = nt.nodes.new("ShaderNodeTexImage"); t_na.image = img_na
    t_nb = nt.nodes.new("ShaderNodeTexImage"); t_nb.image = img_nb
    t_fm = nt.nodes.new("ShaderNodeTexImage"); t_fm.image = img_fm
    nt.links.new(mp_a.outputs["Vector"], t_na.inputs["Vector"])
    nt.links.new(mp_b.outputs["Vector"], t_nb.inputs["Vector"])
    nt.links.new(mp_f.outputs["Vector"], t_fm.inputs["Vector"])

    mix_n = nt.nodes.new("ShaderNodeMix")
    mix_n.data_type = "RGBA"
    mix_n.inputs["Factor"].default_value = 0.5
    nt.links.new(t_na.outputs["Color"], mix_n.inputs["A"])
    nt.links.new(t_nb.outputs["Color"], mix_n.inputs["B"])

    nrm = nt.nodes.new("ShaderNodeNormalMap")
    nrm.inputs["Strength"].default_value = 0.95
    nt.links.new(mix_n.outputs["Result"], nrm.inputs["Color"])
    nt.links.new(nrm.outputs["Normal"], bsdf.inputs["Normal"])

    # Ufer-Schaumkante entlang V-Rand (Vertex-Color R = Ufernaehe 0..1)
    attr_shore = nt.nodes.new("ShaderNodeAttribute")
    attr_shore.attribute_name = "ShoreMask"
    sep_s = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(attr_shore.outputs["Color"], sep_s.inputs["Color"])

    mul_f = nt.nodes.new("ShaderNodeMath")
    mul_f.operation = "MULTIPLY"
    nt.links.new(sep_s.outputs["Red"], mul_f.inputs[0])
    nt.links.new(t_fm.outputs["Color"], mul_f.inputs[1])

    ramp_f = nt.nodes.new("ShaderNodeMapRange")
    ramp_f.inputs["From Min"].default_value = 0.08
    ramp_f.inputs["From Max"].default_value = 0.58
    ramp_f.inputs["To Min"].default_value = 0.0
    ramp_f.inputs["To Max"].default_value = 0.92
    nt.links.new(mul_f.outputs["Value"], ramp_f.inputs["Value"])

    mix_col = nt.nodes.new("ShaderNodeMix")
    mix_col.data_type = "RGBA"
    mix_col.inputs["A"].default_value = (0.045, 0.145, 0.135, 1.0)  # Tiefes Euphrat-Tuirkis/Oliv
    mix_col.inputs["B"].default_value = (0.64, 0.63, 0.59, 1.0)     # Organischer Gischt (unter 0.68 Albedo!)
    nt.links.new(ramp_f.outputs["Result"], mix_col.inputs["Factor"])
    nt.links.new(mix_col.outputs["Result"], bsdf.inputs["Base Color"])

    # Schaum macht Wasser lokal matter
    mix_rgh = nt.nodes.new("ShaderNodeMapRange")
    mix_rgh.inputs["From Min"].default_value = 0.0
    mix_rgh.inputs["From Max"].default_value = 0.9
    mix_rgh.inputs["To Min"].default_value = 0.055
    mix_rgh.inputs["To Max"].default_value = 0.62
    nt.links.new(ramp_f.outputs["Result"], mix_rgh.inputs["Value"])
    nt.links.new(mix_rgh.outputs["Result"], bsdf.inputs["Roughness"])

    return mat


def render_showcase(root):
    t0 = time.time()
    tex_dir = os.path.join(root, "assets", "textures")
    prev_path = os.path.join(root, "assets", "previews", "terrain_water_showcase.png")
    fountain_blend = os.path.join(root, "assets", "blend", "world", "ur_fountain_hero.blend")

    print("[SHOWCASE] Erstelle Studio-Kontrollszene fuer 4 Boeden + Wasser + Stadtbrunnen...", flush=True)
    scene = clear_scene()
    dev = setup_cycles(scene, samples=48, use_oidn=True)

    vts = [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items]
    scene.view_settings.view_transform = "AgX" if "AgX" in vts else "Filmic"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = -0.10

    # Himmelslicht fuer natuerliche Wasser-Reflexionen (Sonne leicht von vorne-oben fuer Wellen-Glanzlichter!)
    world = bpy.data.worlds.new("ShowcaseWorld")
    scene.world = world
    world.use_nodes = True
    nt_w = world.node_tree
    bg = nt_w.nodes.get("Background")
    sky = nt_w.nodes.new("ShaderNodeTexSky")
    sky_enums = [i.identifier for i in sky.bl_rna.properties["sky_type"].enum_items]
    sky.sky_type = "PREETHAM" if "PREETHAM" in sky_enums else sky_enums[0]
    sky.sun_elevation = math.radians(22.0)
    sky.sun_rotation = math.radians(22.0)
    nt_w.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.65

    # Warme mesopotamische Nachmittagssonne (schraeg von +Y/-X Richtung Kamera -> Reflexe auf Wasser & Relief!)
    sun_d = bpy.data.lights.new("MesoSun", type="SUN")
    sun_d.energy = 3.2
    sun_d.color = (1.0, 0.93, 0.83)
    sun_d.angle = math.radians(1.6)
    sun_o = bpy.data.objects.new("MesoSun", sun_d)
    sun_o.rotation_euler = (math.radians(-62.0), math.radians(18.0), math.radians(28.0))
    scene.collection.objects.link(sun_o)

    # Dezentes Fuelllicht von Kameraseite fuer klare Front-Lesbarkeit des Brunnens
    fill_d = bpy.data.lights.new("FrontSkyFill", type="AREA")
    fill_d.energy = 420.0
    fill_d.size = 12.0
    fill_d.color = (0.86, 0.91, 1.0)
    fill_o = bpy.data.objects.new("FrontSkyFill", fill_d)
    fill_o.location = (-3.0, -14.0, 8.5)
    fill_o.rotation_euler = (Vector((0.0, 0.0, 0.0)) - fill_o.location).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(fill_o)

    # 1) 4 Boden-Material-Felder (nebeneinander + Steppe als Untergrund fuer den organischen Weg)
    mat_city   = _make_pbr_terrain_mat("Mat_CityEarth", tex_dir, "terrain_city_earth", has_alpha=False, repeat=1.8)
    mat_steppe = _make_pbr_terrain_mat("Mat_SteppeLoam", tex_dir, "terrain_steppe_loam", has_alpha=False, repeat=2.0)
    mat_bank   = _make_pbr_terrain_mat("Mat_AlluvialBank", tex_dir, "terrain_alluvial_bank", has_alpha=False, repeat=1.8)
    mat_road   = _make_pbr_terrain_mat("Mat_OrganicRoad", tex_dir, "terrain_organic_road", has_alpha=True, repeat=2.2)

    def _add_ground_patch(name, cx, cy, sx, sy, mat, z=0.0):
        mesh = bpy.data.meshes.new(name)
        verts = [
            (cx - sx * 0.5, cy - sy * 0.5, z),
            (cx + sx * 0.5, cy - sy * 0.5, z),
            (cx + sx * 0.5, cy + sy * 0.5, z),
            (cx - sx * 0.5, cy + sy * 0.5, z),
        ]
        mesh.from_pydata(verts, [], [(0, 1, 2, 3)])
        uv_layer = mesh.uv_layers.new(name="UVMap")
        for lp, uv in zip(mesh.loops, [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]):
            uv_layer.data[lp.index].uv = uv
        mesh.materials.append(mat)
        obj = bpy.data.objects.new(name, mesh)
        scene.collection.objects.link(obj)
        return obj

    # Unterbau-Platte fuer saubere Studio-Kante
    _add_ground_patch("Patch_CityEarth",   -4.2, +0.2, 6.4, 7.6, mat_city, z=0.00)
    _add_ground_patch("Patch_SteppeLoam",  +3.0, +0.2, 8.0, 7.6, mat_steppe, z=0.00)
    # Organischer Karrenweg liegt sanft ueber dem Steppenboden (demonstration der weichen Alpha-Randmaske!)
    _add_ground_patch("Patch_OrganicRoad", +3.0, -1.3, 8.0, 2.8, mat_road, z=0.012)

    # Uferboeschung + spiegelnder Wasserstreifen vorne im Bild
    # Alluvial-Bank streckt sich unter das Wasserbecken mit sanfter Neigung zum Wasser
    nx, ny = 48, 24
    ux = np.linspace(-7.4, +7.0, nx + 1)
    vy = np.linspace(-6.8, -3.6, ny + 1)
    gx, gy = np.meshgrid(ux, vy, indexing="xy")
    # Hinterer Teil (y=-3.6) auf Z=0.0, faellt zum Wasserkanal (y=-5.3..-6.8) auf Z=-0.42 m ab
    t_slope = np.clip((-3.8 - gy) / 1.8, 0.0, 1.0)
    gz = -0.44 * (t_slope * t_slope * (3.0 - 2.0 * t_slope))
    bank_mesh = bpy.data.meshes.new("Patch_AlluvialBank")
    verts = np.column_stack([gx.ravel(), gy.ravel(), gz.ravel()]).tolist()
    stride = nx + 1
    ii, jj = np.meshgrid(np.arange(nx), np.arange(ny), indexing="xy")
    v00 = (jj * stride + ii).ravel()
    faces = np.column_stack([v00, v00 + 1, v00 + stride + 1, v00 + stride]).tolist()
    bank_mesh.from_pydata(verts, [], faces)
    bank_mesh.polygons.foreach_set("use_smooth", [True] * len(bank_mesh.polygons))
    uv_b = bank_mesh.uv_layers.new(name="UVMap")
    loop_v = np.empty(len(bank_mesh.loops), dtype=np.int64)
    bank_mesh.loops.foreach_get("vertex_index", loop_v)
    uv_u = ((gx.ravel() + 7.4) / 6.0).astype(np.float32)
    uv_v = ((gy.ravel() + 6.8) / 3.2).astype(np.float32)
    uv_b.data.foreach_set("uv", np.column_stack([uv_u[loop_v], uv_v[loop_v]]).ravel())
    bank_mesh.materials.append(mat_bank)
    bank_obj = bpy.data.objects.new("Patch_AlluvialBank", bank_mesh)
    scene.collection.objects.link(bank_obj)

    # Spiegelnder Wasserstreifen bei Z = -0.14 m (schneidet Uferboeschung -> klare Schaumkante!)
    mat_water = _make_showcase_water_mat(tex_dir)
    wnx, wny = 64, 24
    wux = np.linspace(-7.4, +7.0, wnx + 1)
    wvy = np.linspace(-6.8, -4.15, wny + 1)
    wgx, wgy = np.meshgrid(wux, wvy, indexing="xy")
    wgz = np.full_like(wgx, -0.14)
    w_mesh = bpy.data.meshes.new("WaterStrip")
    w_verts = np.column_stack([wgx.ravel(), wgy.ravel(), wgz.ravel()]).tolist()
    w_stride = wnx + 1
    wi, wj = np.meshgrid(np.arange(wnx), np.arange(wny), indexing="xy")
    wv00 = (wj * w_stride + wi).ravel()
    w_faces = np.column_stack([wv00, wv00 + 1, wv00 + w_stride + 1, wv00 + w_stride]).tolist()
    w_mesh.from_pydata(w_verts, [], w_faces)
    w_mesh.polygons.foreach_set("use_smooth", [True] * len(w_mesh.polygons))
    uv_w = w_mesh.uv_layers.new(name="UVMap")
    w_loop_v = np.empty(len(w_mesh.loops), dtype=np.int64)
    w_mesh.loops.foreach_get("vertex_index", w_loop_v)
    w_u = ((wgx.ravel() + 7.4) / 7.2).astype(np.float32)
    w_v = ((wgy.ravel() + 6.8) / 2.65).astype(np.float32)
    uv_w.data.foreach_set("uv", np.column_stack([w_u[w_loop_v], w_v[w_loop_v]]).ravel())

    # ShoreMask Vertex Color: hoch am Uferkontakt (y ~ -4.4..-4.15) und entlang eines kleinen Brueckenpfahls
    shore_attr = w_mesh.color_attributes.new(name="ShoreMask", type="FLOAT_COLOR", domain="CORNER")
    shore_v = np.clip((wgy.ravel() + 4.95) / 0.72, 0.0, 1.0)
    # Zusaetzlicher kleiner Wirbelring um einen Holzpfahl im Wasser bei (-4.2, -5.6)
    dist_pile = np.sqrt((wgx.ravel() - (-4.2)) ** 2 + (wgy.ravel() - (-5.6)) ** 2)
    pile_wake = np.exp(-((dist_pile - 0.32) / 0.35) ** 2) * 0.95
    shore_val = np.clip(np.maximum(shore_v, pile_wake), 0.0, 1.0)
    shore_rgba = np.column_stack([shore_val[w_loop_v], shore_val[w_loop_v], shore_val[w_loop_v], np.ones_like(w_loop_v, dtype=np.float32)]).ravel()
    shore_attr.data.foreach_set("color", shore_rgba)
    w_mesh.materials.append(mat_water)
    w_obj = bpy.data.objects.new("WaterStrip", w_mesh)
    scene.collection.objects.link(w_obj)

    # Kleiner Holzpfahl im Wasser fuer Schaumwirbel-Test
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.16, depth=1.1, location=(-4.2, -5.6, -0.05))
    pile_obj = bpy.context.active_object
    p_mat = bpy.data.materials.new("PileWood")
    p_mat.use_nodes = True
    p_bsdf = p_mat.node_tree.nodes.get("Principled BSDF")
    if p_bsdf:
        p_bsdf.inputs["Base Color"].default_value = (0.16, 0.10, 0.06, 1.0)
        p_bsdf.inputs["Roughness"].default_value = 0.82
    pile_obj.data.materials.append(p_mat)

    # 2) Neuen gemauerten Stadtbrunnen (ur_fountain_hero_LOD0) prominent auf dem Stadtboden platzieren!
    if os.path.isfile(fountain_blend):
        with bpy.data.libraries.load(fountain_blend, link=False) as (data_from, data_to):
            data_to.objects = [n for n in data_from.objects if "LOD0" in n]
        for o in data_to.objects:
            if o is not None:
                o.location = (-4.0, +0.4, 0.0)
                o.rotation_euler = (0.0, 0.0, math.radians(-28.0))
                scene.collection.objects.link(o)
                print(f"[SHOWCASE] Brunnen geladen: {o.name}", flush=True)
    else:
        print(f"[SHOWCASE WARN] {fountain_blend} noch nicht vorhanden!", flush=True)

    # Kamera so positionieren, dass Stadtboden + Brunnen (links), Steppenboden + Weg (rechts) und Wasserstreifen + Ufer (vorne) klar sichtbar sind
    cam_d = bpy.data.cameras.new("ShowcaseCam")
    cam_d.lens = 34.0
    cam_d.clip_end = 200.0
    cam_o = bpy.data.objects.new("ShowcaseCam", cam_d)
    cam_o.location = (-0.2, -13.2, 7.6)
    target = Vector((-0.2, -1.6, 0.3))
    cam_o.rotation_euler = (target - cam_o.location).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cam_o)
    scene.camera = cam_o

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.filepath = prev_path
    os.makedirs(os.path.dirname(prev_path), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print(f"[SHOWCASE] Gespeichert: {prev_path} ({dev}) in {time.time() - t0:.1f}s", flush=True)
    return prev_path


def main():
    t_total = time.time()
    root = get_project_root()
    tex_dir = os.path.join(root, "assets", "textures")
    os.makedirs(tex_dir, exist_ok=True)

    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    bake_only = "--bake-only" in args
    showcase_only = "--showcase-only" in args

    if not showcase_only:
        print("=== ARCHE TERRAIN- & WASSER-TEXTUREN BAKER START ===", flush=True)
        for tid in (
            "terrain_city_earth",
            "terrain_steppe_loam",
            "terrain_alluvial_bank",
            "terrain_organic_road",
        ):
            bake_terrain_material(tid, tex_dir)

        bake_water_normal_map(
            "water_blender_normal_a.png",
            tex_dir,
            spatial_size=16,
            wind_velocity=4.4,
            wave_scale=0.20,
            wave_alignment=0.35,
            wave_direction=0.38,
            choppiness=0.55,
            sim_time=1.4,
            seed=101,
            cap_angle=0.38,
        )
        bake_water_normal_map(
            "water_blender_normal_b.png",
            tex_dir,
            spatial_size=12,
            wind_velocity=3.0,
            wave_scale=0.13,
            wave_alignment=0.25,
            wave_direction=-1.95,
            choppiness=0.35,
            sim_time=3.7,
            seed=207,
            cap_angle=-1.15,
        )
        bake_water_foam_map(tex_dir)

    if not bake_only:
        render_showcase(root)

    print(f"=== TERRAIN_WATER_MAPS_DONE in {time.time() - t_total:.1f}s ===", flush=True)


if __name__ == "__main__":
    main()
