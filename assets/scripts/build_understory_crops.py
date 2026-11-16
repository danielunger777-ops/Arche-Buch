"""
build_understory_crops.py — Unterholz-, Feld- & Zierbotanik-Generator (ARCHE Teil 1)
======================================================================================
Erzeugt nach BLENDER_PIPELINE.md (Z-Up, Origin Z=0, Ctrl+A applied, Col_Wind):

1. Zwei gemeinsame 1024x1024 Cycles-CUDA-PBR-Atlanten (0 Schlagschatten, HDR Albedo [0.05..0.75],
   BaseColor+Alpha [sRGB], Normal [Linear], ORM [Linear], Thickness-SSS [Linear]):
   - assets/textures/understory_crops_atlas_*
   - assets/textures/ornamental_garden_atlas_*

2. Vier gebuendelte 4-LOD-.glb-Pakete (exportiert ueber export_arche_glb.py) + .blend-Dateien:
   - shrubs_oriental.glb      (5 Arten x 12 Varianten = 60, je LOD0 120-420 Tris + LOD1-LOD3)
   - grass_and_reeds.glb      (3 Typen x 14 Varianten = 42, je LOD0  20-90  Tris + LOD1-LOD3)
   - crops_mesopotamia.glb    (5 Arten x 12 Varianten = 60, je LOD0  24-110 Tris + LOD1-LOD3)
   - ornamental_gardens.glb   (4 Klassen x 13 Varianten = 52, je LOD0 80-480 Tris + LOD1-LOD3)

3. Registrierung in assets/manifest.json + Kontroll-Rendering assets/previews/understory_showcase.png.

Aufruf:
  blender --background --python assets/scripts/build_understory_crops.py
"""

import os
import sys
import math
import time
import json
import random
import datetime
import bpy
import bmesh
from mathutils import Vector, Matrix


def get_project_root():
    if "__file__" in globals():
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.getcwd()


ROOT_DIR = get_project_root()
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
if ASSETS_DIR not in sys.path:
    sys.path.insert(0, ASSETS_DIR)
import export_arche_glb  # noqa: E402


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
        scene.cycles.use_denoising = False
        scene.cycles.max_bounces = 2
        scene.cycles.diffuse_bounces = 1
        scene.cycles.glossy_bounces = 0
        scene.cycles.transparent_max_bounces = 8

    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    return "CUDA (GPU)" if used_gpu else "CPU"


def clamp_hdr(rgb, lo=0.05, hi=0.75):
    return (
        max(lo, min(hi, float(rgb[0]))),
        max(lo, min(hi, float(rgb[1]))),
        max(lo, min(hi, float(rgb[2]))),
    )


def atlas_uv_box(col, row, pad_x=0.014, pad_y=0.014):
    """4x4-Atlas-UVs (row=0 oben in WebGL/V=0.75..1.0 in Blender)."""
    u0 = col * 0.25 + pad_x
    u1 = (col + 1) * 0.25 - pad_x
    v0 = (3 - row) * 0.25 + pad_y
    v1 = (4 - row) * 0.25 - pad_y
    return (u0, v0, u1, v1)


# ==============================================================================
# 1. CYCLES 1024x1024 ATLAS-BAKER (UNTERHOLZ/FELDER & TEMPEL-ZIERGARTEN)
# ==============================================================================

def _bm_tube(bm, pts, r0, r1, sides=5, col_layer=None, c_tag=(0.0, 0.55, 0.12, 1.0), uv_layer=None, u_range=(0.0, 1.0), v_scale=1.0):
    if len(pts) < 2:
        return
    rings = []
    cum_len = 0.0
    for idx, p in enumerate(pts):
        t = idx / float(len(pts) - 1)
        if idx > 0:
            cum_len += (p - pts[idx - 1]).length
        rad = max(0.0005, r0 * (1.0 - t) + r1 * t)
        if idx == 0:
            tang = (pts[1] - pts[0]).normalized()
        elif idx == len(pts) - 1:
            tang = (pts[-1] - pts[-2]).normalized()
        else:
            tang = (pts[idx + 1] - pts[idx - 1]).normalized()
        if tang.length < 1e-6:
            tang = Vector((0.0, 0.0, 1.0))
        ref = Vector((1.0, 0.0, 0.0)) if abs(tang.x) < 0.8 else Vector((0.0, 1.0, 0.0))
        bx = tang.cross(ref).normalized()
        by = tang.cross(bx).normalized()
        ring = []
        for si in range(sides):
            ang = 2.0 * math.pi * si / sides
            v = bm.verts.new(p + (bx * math.cos(ang) + by * math.sin(ang)) * rad)
            ring.append((v, si / float(sides), cum_len * v_scale))
        rings.append(ring)
    for ri in range(len(rings) - 1):
        ra, rb = rings[ri], rings[ri + 1]
        for si in range(sides):
            sn = (si + 1) % sides
            v0, u0, va = ra[si]
            v1, u1, _ = ra[sn]
            v2, _, vb = rb[sn]
            v3, _, _ = rb[si]
            try:
                f = bm.faces.new((v0, v1, v2, v3))
                f.smooth = True
                for lp, uu, vv in zip(f.loops, (u0, u1, u1, u0), (va, va, vb, vb)):
                    if col_layer is not None:
                        lp[col_layer] = c_tag
                    if uv_layer is not None:
                        uu_m = u_range[0] + (u_range[1] - u_range[0]) * uu
                        lp[uv_layer].uv = (uu_m, vv)
            except ValueError:
                pass


def _bm_blade(bm, base, d_vec, length, width, arch=0.003, lobes=0, col_layer=None, r_mode=1.0, ao_b=0.58, ao_t=0.98, thk_b=0.50, thk_t=0.92, col_b=(0,0,0,1), segs=4):
    d = d_vec.normalized()
    perp = Vector((-d.y, d.x, 0.0))
    if perp.length < 1e-5:
        perp = Vector((1.0, 0.0, 0.0))
    perp.normalize()
    up = d.cross(perp).normalized()
    if up.z < 0.0:
        up = -up
    rows = []
    for si in range(segs + 1):
        t = si / float(segs)
        center = base + d * (length * t) + up * (math.sin(math.pi * t) * arch)
        if lobes > 0:
            w = width * math.sin(math.pi * max(0.06, t ** 0.72)) * (0.68 + 0.34 * abs(math.sin(t * lobes * math.pi)))
        else:
            w = width * (math.sin(math.pi * (0.08 + 0.90 * t)) ** 0.8)
        w = max(0.0006, w)
        if si == 0:
            w *= 0.25
        elif si == segs:
            w *= 0.08
        vl = bm.verts.new(center - perp * (w * 0.5) + up * (0.0005 * (1.0 - t)))
        vm = bm.verts.new(center)
        vr = bm.verts.new(center + perp * (w * 0.5) + up * (0.0005 * (1.0 - t)))
        rows.append((t, vl, vm, vr))
    for si in range(segs):
        t0, l0, m0, r0 = rows[si]
        t1, l1, m1, r1 = rows[si + 1]
        for q in ((l0, m0, m1, l1), (m0, r0, r1, m1)):
            try:
                f = bm.faces.new(q)
                f.smooth = True
                for lp in f.loops:
                    if col_layer is not None:
                        tf = t0 if lp.vert in (l0, m0, r0) else t1
                        ao = ao_b + (ao_t - ao_b) * tf
                        thk = thk_b + (thk_t - thk_b) * tf
                        lp[col_layer] = (r_mode, ao, thk, col_b[3])
            except ValueError:
                pass


def _bm_disk(bm, center, radius, segs=12, col_layer=None, c_edge=(1.0, 0.78, 0.85, 1.0), c_center=(1.0, 0.65, 0.72, 1.0), notch=False):
    vc = bm.verts.new(center)
    ring = []
    n_pts = segs - 1 if notch else segs
    for i in range(n_pts):
        ang = 2.0 * math.pi * (i + (0.45 if notch else 0.0)) / segs
        r = radius * (0.96 + 0.04 * math.sin(ang * 5.0))
        ring.append(bm.verts.new(center + Vector((math.cos(ang) * r, math.sin(ang) * r, 0.001))))
    limit = n_pts - 1 if notch else n_pts
    for i in range(limit):
        va = ring[i]
        vb = ring[(i + 1) % len(ring)]
        try:
            f = bm.faces.new((vc, va, vb))
            f.smooth = True
            if col_layer is not None:
                for lp in f.loops:
                    lp[col_layer] = c_center if lp.vert == vc else c_edge
        except ValueError:
            pass


def _bm_flower_cluster(bm, center, radius, petals=5, col_layer=None, r_petal=0.45, r_core=0.22):
    for pi in range(petals):
        ang = 2.0 * math.pi * pi / petals
        d = Vector((math.cos(ang), math.sin(ang), 0.14)).normalized()
        _bm_blade(bm, center, d, radius, radius * 0.68, arch=radius * 0.15,
                  col_layer=col_layer, r_mode=r_petal, ao_b=0.72, ao_t=1.0, thk_b=0.68, thk_t=0.95, segs=3)
    # Bluetenkern
    _bm_disk(bm, center + Vector((0, 0, 0.003)), radius * 0.28, segs=8, col_layer=col_layer,
             c_edge=(r_core, 0.72, 0.55, 1.0), c_center=(r_core, 0.80, 0.65, 1.0))


def _bm_full_quad(bm, x0, y0, x1, y1, col_layer, tag=(0.0, 0.92, 0.05, 1.0), uv_layer=None):
    v0 = bm.verts.new((x0, y0, 0.0))
    v1 = bm.verts.new((x1, y0, 0.0))
    v2 = bm.verts.new((x1, y1, 0.0))
    v3 = bm.verts.new((x0, y1, 0.0))
    f = bm.faces.new((v0, v1, v2, v3))
    uvs = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
    for lp, uv in zip(f.loops, uvs):
        lp[col_layer] = tag
        if uv_layer is not None:
            lp[uv_layer].uv = uv


def _build_atlas_cell_understory(bm, spec, col_layer):
    mode, col, row, *_ = spec
    rng = random.Random(700 + row * 13 + col * 31)
    bx, by = col * 0.25, (3 - row) * 0.25
    cx = bx + 0.125
    px, py = 0.018, 0.018
    sx, sy = 0.25 - 2 * px, 0.25 - 2 * py
    by0 = by + py

    if mode in ("shrub_wood_trim", "vine_wood_earth"):
        _bm_full_quad(bm, col * 0.25, by, (col + 1) * 0.25, by + 0.25, col_layer,
                      tag=(0.0, 0.88, 0.06, 1.0), uv_layer=bm.loops.layers.uv.active)
        return

    if mode == "thornbush":
        # Gekreuzte verholzte Dornen-Aestchen + winzige Grau-Oliv-Blaetter
        main = [Vector((cx + 0.008 * math.sin(i * 1.1), by0 + sy * (i / 5.0), 0.004)) for i in range(6)]
        _bm_tube(bm, main, 0.0032, 0.0010, sides=5, col_layer=col_layer, c_tag=(0.0, 0.62, 0.12, 1.0))
        for k in range(8):
            t = 0.14 + 0.78 * (k / 7.0)
            p = Vector((cx + 0.005 * math.sin(k * 1.3), by0 + sy * t, 0.005))
            sgn = -1.0 if k % 2 == 0 else 1.0
            ang = sgn * rng.uniform(0.55, 1.12)
            d = Vector((math.sin(ang), math.cos(ang), 0.12)).normalized()
            p_end = p + d * (sx * rng.uniform(0.32, 0.45))
            _bm_tube(bm, [p, p_end], 0.0018, 0.0006, sides=4, col_layer=col_layer, c_tag=(0.0, 0.66, 0.12, 1.0))
            for m in range(5):
                lp = p.lerp(p_end, 0.22 + 0.75 * (m / 4.0))
                for ls in (-1.0, 1.0):
                    lang = ang + ls * 0.75
                    ld = Vector((math.sin(lang), math.cos(lang), 0.2)).normalized()
                    _bm_blade(bm, lp, ld, 0.015, 0.007, arch=0.002, col_layer=col_layer, r_mode=1.0, ao_b=0.64, ao_t=0.98)
            # Dornenspitze
            _bm_tube(bm, [p_end, p_end + d * 0.014], 0.0008, 0.0002, sides=3, col_layer=col_layer, c_tag=(0.45, 0.85, 0.35, 1.0))

    elif mode == "tamarisk":
        # Feine blaue/gruene Schuppentriebe + rosa Bluetenrispen
        main = [Vector((cx + 0.005 * math.sin(i * 0.9), by0 + sy * (i / 5.0), 0.004)) for i in range(6)]
        _bm_tube(bm, main, 0.0028, 0.0009, sides=4, col_layer=col_layer, c_tag=(0.0, 0.58, 0.12, 1.0))
        for k in range(12):
            t = 0.12 + 0.80 * (k / 11.0)
            p = Vector((cx, by0 + sy * t, 0.005))
            sgn = -1.0 if k % 2 == 0 else 1.0
            ang = sgn * rng.uniform(0.35, 0.88)
            d = Vector((math.sin(ang), math.cos(ang), 0.12)).normalized()
            _bm_blade(bm, p, d, sx * 0.44, 0.012, arch=0.003, lobes=5, col_layer=col_layer, r_mode=1.0, ao_b=0.68, ao_t=0.98)
            if k >= 5 and k % 2 == 0:
                _bm_flower_cluster(bm, p + d * (sx * 0.28), 0.008, petals=4, col_layer=col_layer, r_petal=0.45, r_core=0.35)

    elif mode in ("oleander", "juniper"):
        # Lanzett-Blaetter + rosa Oleanderblueten ODER dichte Wacholder-Nadeln + Beeren
        is_jun = (mode == "juniper")
        main = [Vector((cx, by0 + sy * (i / 5.0), 0.004)) for i in range(6)]
        _bm_tube(bm, main, 0.0032, 0.0010, sides=4, col_layer=col_layer, c_tag=(0.0, 0.54, 0.12, 1.0))
        n_sprays = 16 if is_jun else 12
        for k in range(n_sprays):
            t = 0.10 + 0.78 * (k / float(n_sprays - 1))
            p = Vector((cx, by0 + sy * t, 0.006))
            for sgn in (-1.0, 1.0):
                ang = sgn * rng.uniform(0.40, 0.95)
                d = Vector((math.sin(ang), math.cos(ang), 0.14)).normalized()
                if is_jun:
                    _bm_blade(bm, p, d, 0.030, 0.014, arch=0.003, lobes=4, col_layer=col_layer, r_mode=1.0, ao_b=0.58, ao_t=0.96)
                else:
                    _bm_blade(bm, p, d, 0.048, 0.014, arch=0.004, lobes=0, col_layer=col_layer, r_mode=1.0, ao_b=0.62, ao_t=0.98)
        if is_jun:
            for bp in ((-0.025, 0.45), (0.028, 0.58), (-0.014, 0.72), (0.018, 0.34)):
                _bm_disk(bm, Vector((cx + bp[0], by0 + sy * bp[1], 0.010)), 0.007, segs=8, col_layer=col_layer,
                         c_edge=(0.45, 0.68, 0.25, 1.0), c_center=(0.45, 0.85, 0.30, 1.0))
        else:
            for bp in ((-0.032, 0.74), (0.028, 0.80), (0.0, 0.86)):
                _bm_flower_cluster(bm, Vector((cx + bp[0], by0 + sy * bp[1], 0.012)), 0.016, petals=5, col_layer=col_layer, r_petal=0.45, r_core=0.35)

    elif mode == "broom_juniper":
        # Ginster-Ruten + gelbe Schmetterlingsblueten
        for k in range(9):
            x_off = (k - 4) * 0.018
            pts = [Vector((cx + x_off * 0.4, by0 + sy * (0.02 + 0.90 * (i / 5.0)), 0.003)) + Vector((x_off * (i / 5.0), 0.0, 0.0)) for i in range(6)]
            _bm_tube(bm, pts, 0.0022, 0.0007, sides=4, col_layer=col_layer, c_tag=(0.88, 0.68, 0.40, 1.0))
            for m in range(3):
                fp = pts[3 + min(2, m)] + Vector((rng.uniform(-0.008, 0.008), 0.004, 0.005))
                _bm_flower_cluster(bm, fp, 0.010, petals=4, col_layer=col_layer, r_petal=0.45, r_core=0.35)

    elif mode in ("steppe_grass", "tall_grass"):
        n_b = 11 if mode == "steppe_grass" else 13
        for k in range(n_b):
            fan = (k / float(n_b - 1) - 0.5) * 1.05
            d = Vector((math.sin(fan), math.cos(fan) * 0.96, 0.08)).normalized()
            hlen = min(sy * 0.84, sy * rng.uniform(0.64, 0.84) / max(0.72, abs(d.y)))
            wid = 0.010 if mode == "steppe_grass" else 0.014
            _bm_blade(bm, Vector((cx + fan * 0.014, by0 + 0.005, 0.002)), d, hlen, wid, arch=0.006,
                      col_layer=col_layer, r_mode=1.0, ao_b=0.52, ao_t=0.99, thk_b=0.58, thk_t=0.95, segs=5)

    elif mode == "euphrates_reed":
        # Schilfhalme + silberbeige Rispen + schmale Halmblaetter
        for k in range(5):
            xo = (k - 2) * 0.024
            pts = [Vector((cx + xo * (0.3 + 0.7 * (i / 5.0)), by0 + sy * 0.90 * (i / 5.0) * rng.uniform(0.86, 0.98), 0.004)) for i in range(6)]
            _bm_tube(bm, pts, 0.0036, 0.0014, sides=4, col_layer=col_layer, c_tag=(0.78, 0.72, 0.52, 1.0))
            # Schilf-Rispe an der Spitze
            tip = pts[-2]
            for pf in range(8):
                ang = (pf / 7.0 - 0.5) * 1.05
                ld = Vector((math.sin(ang), math.cos(ang), 0.08)).normalized()
                _bm_blade(bm, tip, ld, 0.036, 0.011, arch=0.003, col_layer=col_layer, r_mode=0.50, ao_b=0.72, ao_t=1.0, segs=3)
            for sgn in (-1.0, 1.0):
                ld = Vector((sgn * 0.42, 0.88, 0.06)).normalized()
                _bm_blade(bm, pts[2], ld, 0.062, 0.010, arch=0.005, col_layer=col_layer, r_mode=1.0, ao_b=0.62, ao_t=0.96, segs=4)

    elif mode == "papyrus_head":
        # Radialer Papyrus-Strauss (faecherfoermige strahlende Deckblaetter)
        hub = Vector((cx, by0 + sy * 0.14, 0.003))
        _bm_tube(bm, [Vector((cx, by0, 0.003)), hub], 0.0055, 0.0040, sides=5, col_layer=col_layer, c_tag=(0.78, 0.72, 0.52, 1.0))
        for k in range(21):
            ang = (k / 20.0 - 0.5) * 2.10
            d = Vector((math.sin(ang), math.cos(ang), 0.06)).normalized()
            rlen = sy * rng.uniform(0.64, 0.78) * (1.0 - 0.18 * abs(ang))
            _bm_blade(bm, hub, d, rlen, 0.0055, arch=0.006, col_layer=col_layer, r_mode=1.0, ao_b=0.58, ao_t=0.98, segs=4)

    elif mode in ("emmer_wheat", "barley"):
        is_barley = (mode == "barley")
        for k in range(4):
            xo = (k - 1.5) * 0.034
            top_y = by0 + sy * rng.uniform(0.80, 0.90)
            stalk_pts = [Vector((cx + xo * (0.4 + 0.6 * (i / 4.0)), by0 + (top_y - by0) * 0.58 * (i / 4.0), 0.004)) for i in range(5)]
            _bm_tube(bm, stalk_pts, 0.0030, 0.0018, sides=4, col_layer=col_layer, c_tag=(0.78, 0.74, 0.50, 1.0))
            head_b = stalk_pts[-1]
            # Zweireihige Aehrenkoerner + lange Grannen!
            n_gr = 9 if is_barley else 10
            for gi in range(n_gr):
                gp = head_b + Vector((rng.uniform(-0.002, 0.002), gi * 0.0064, 0.006))
                for sgn in (-1.0, 1.0):
                    gd = Vector((sgn * 0.42, 0.86, 0.05)).normalized()
                    _bm_blade(bm, gp, gd, 0.015, 0.008, arch=0.002, col_layer=col_layer, r_mode=0.50, ao_b=0.68, ao_t=0.98, segs=2)
                    # Feine Granne
                    awn_len = 0.032 if is_barley else 0.022
                    _bm_tube(bm, [gp + gd * 0.010, gp + Vector((sgn * 0.008, awn_len, 0.008))], 0.0005, 0.0002, sides=3, col_layer=col_layer, c_tag=(0.50, 0.90, 0.45, 1.0))
            # Laubblatt am Halm
            _bm_blade(bm, stalk_pts[2], Vector(((1 if k % 2 == 0 else -1) * 0.45, 0.85, 0.04)), 0.062, 0.010, arch=0.004,
                      col_layer=col_layer, r_mode=1.0, ao_b=0.62, ao_t=0.95, segs=3)

    elif mode == "lentil_chickpea":
        # Feine paarig gefiederte Leguminosen-Blaettchen + weisse Blueten
        for k in range(3):
            xo = (k - 1) * 0.042
            stem = [Vector((cx + xo * 0.4, by0 + sy * (i / 4.0) * 0.84, 0.004)) + Vector((xo * 0.6 * (i / 4.0), 0.0, 0.0)) for i in range(5)]
            _bm_tube(bm, stem, 0.0020, 0.0008, sides=4, col_layer=col_layer, c_tag=(0.78, 0.68, 0.50, 1.0))
            for pi in range(7):
                lp = stem[1].lerp(stem[-1], pi / 6.5)
                for sgn in (-1.0, 1.0):
                    d = Vector((sgn * 0.82, 0.52, 0.14)).normalized()
                    _bm_blade(bm, lp, d, 0.018, 0.011, arch=0.002, col_layer=col_layer, r_mode=1.0, ao_b=0.65, ao_t=0.98, segs=3)
            _bm_flower_cluster(bm, stem[-1] + Vector((0, 0.005, 0.006)), 0.009, petals=4, col_layer=col_layer, r_petal=0.50, r_core=0.25)

    elif mode == "flax":
        # Luftige Leinstengel + himmelblaue 5-Blaettrige Flachsblueten!
        for k in range(6):
            xo = (k - 2.5) * 0.024
            stem = [Vector((cx + xo * (0.2 + 0.8 * (i / 4.0)), by0 + sy * (i / 4.0) * rng.uniform(0.72, 0.86), 0.004)) for i in range(5)]
            _bm_tube(bm, stem, 0.0018, 0.0008, sides=4, col_layer=col_layer, c_tag=(0.78, 0.68, 0.48, 1.0))
            for m in range(5):
                sp = stem[1].lerp(stem[-2], m / 4.0)
                d = Vector(((1 if (m + k) % 2 == 0 else -1) * 0.55, 0.82, 0.10)).normalized()
                _bm_blade(bm, sp, d, 0.018, 0.006, arch=0.002, col_layer=col_layer, r_mode=1.0, ao_b=0.66, ao_t=0.98, segs=2)
            _bm_flower_cluster(bm, stem[-1] + Vector((0, 0.006, 0.006)), 0.016, petals=5, col_layer=col_layer, r_petal=0.50, r_core=0.25)

    elif mode == "grapevine":
        # Rebtrieb + gelappte Weinblaetter + tiefviolette Traubenbeeren
        cane = [Vector((cx + 0.009 * math.sin(i * 1.1), by0 + sy * 0.80 * (i / 4.0), 0.004)) for i in range(5)]
        _bm_tube(bm, cane, 0.0042, 0.0016, sides=5, col_layer=col_layer, c_tag=(0.0, 0.54, 0.14, 1.0))
        for p, d, lsz in (
            (cane[1], Vector((-0.78, 0.56, 0.12)), 0.050),
            (cane[2], Vector((0.80, 0.52, 0.12)), 0.052),
            (cane[3], Vector((-0.62, 0.72, 0.15)), 0.046),
            (cane[4], Vector((0.28, 0.85, 0.14)), 0.042),
        ):
            _bm_blade(bm, p, d, lsz, lsz * 0.95, arch=0.004, lobes=5, col_layer=col_layer, r_mode=1.0, ao_b=0.60, ao_t=0.98, segs=4)
        # Traubenbeeren-Rispe (dunkelviolett r_mode=0.50)
        gr_base = cane[2] + Vector((-0.024, -0.006, 0.008))
        for row_g in range(4):
            cnt_g = 4 - row_g
            for gi in range(cnt_g):
                gp = gr_base + Vector(((gi - (cnt_g - 1) * 0.5) * 0.010, -row_g * 0.010, 0.002))
                _bm_disk(bm, gp, 0.0062, segs=8, col_layer=col_layer, c_edge=(0.50, 0.52, 0.30, 1.0), c_center=(0.50, 0.88, 0.45, 1.0))


def _build_atlas_cell_ornamental(bm, spec, col_layer):
    mode, col, row, *_ = spec
    rng = random.Random(1700 + row * 19 + col * 37)
    bx, by = col * 0.25, (3 - row) * 0.25
    cx = bx + 0.125
    px, py = 0.018, 0.018
    sx, sy = 0.25 - 2 * px, 0.25 - 2 * py
    by0 = by + py

    if mode in ("terracotta_pot", "terracotta_soil_rim", "lapis_glaze_band", "travertine_rim"):
        _bm_full_quad(bm, col * 0.25, by, (col + 1) * 0.25, by + 0.25, col_layer,
                      tag=(0.0, 0.90, 0.05, 1.0), uv_layer=bm.loops.layers.uv.active)
        return

    if mode == "terracotta_bark":
        _bm_full_quad(bm, col * 0.25, by, (col + 1) * 0.25, by + 0.25, col_layer,
                      tag=(0.0, 0.86, 0.08, 1.0), uv_layer=bm.loops.layers.uv.active)
        return

    if mode in ("pomegranate_foliage", "pomegranate_fruit", "myrtle"):
        is_myrtle = (mode == "myrtle")
        is_fruit = (mode == "pomegranate_fruit")
        main = [Vector((cx, by0 + sy * (i / 5.0), 0.004)) for i in range(6)]
        _bm_tube(bm, main, 0.0030, 0.0009, sides=4, col_layer=col_layer, c_tag=(0.0, 0.54, 0.12, 1.0))
        for k in range(12):
            t = 0.10 + 0.78 * (k / 11.0)
            p = Vector((cx, by0 + sy * t, 0.005))
            for sgn in (-1.0, 1.0):
                ang = sgn * rng.uniform(0.45, 0.95)
                d = Vector((math.sin(ang), math.cos(ang), 0.14)).normalized()
                llen = 0.026 if is_myrtle else 0.036
                lwid = 0.013 if is_myrtle else 0.015
                _bm_blade(bm, p, d, llen, lwid, arch=0.003, col_layer=col_layer, r_mode=1.0, ao_b=0.62, ao_t=0.98, segs=3)
        if is_fruit:
            for fp in ((-0.028, 0.42), (0.026, 0.66), (-0.006, 0.80)):
                _bm_disk(bm, Vector((cx + fp[0], by0 + sy * fp[1], 0.010)), 0.017, segs=12, col_layer=col_layer,
                         c_edge=(0.45, 0.65, 0.30, 1.0), c_center=(0.45, 0.95, 0.45, 1.0))
        else:
            pet = 6 if is_myrtle else 5
            for bp in ((-0.030, 0.56), (0.028, 0.72), (-0.004, 0.86)):
                _bm_flower_cluster(bm, Vector((cx + bp[0], by0 + sy * bp[1], 0.010)), 0.015 if is_myrtle else 0.016,
                                   petals=pet, col_layer=col_layer, r_petal=0.45, r_core=0.32)

    elif mode == "dwarf_palm_olive":
        # Zier-Zwergpalme & Olivenzweig (silbrig-sattes Gruen)
        main = [Vector((cx, by0 + sy * (i / 5.0), 0.004)) for i in range(6)]
        _bm_tube(bm, main, 0.0032, 0.0010, sides=4, col_layer=col_layer, c_tag=(0.0, 0.56, 0.12, 1.0))
        for k in range(14):
            t = 0.08 + 0.84 * (k / 13.0)
            p = Vector((cx, by0 + sy * t, 0.005))
            for sgn in (-1.0, 1.0):
                d = Vector((sgn * 0.74, 0.62, 0.10)).normalized()
                _bm_blade(bm, p, d, 0.048 * (1.06 - 0.35 * t), 0.012, arch=0.004,
                          col_layer=col_layer, r_mode=1.0, ao_b=0.60, ao_t=0.98, segs=3)

    elif mode in ("ornamental_fern", "cyperus_fan"):
        is_cyp = (mode == "cyperus_fan")
        if is_cyp:
            hub = Vector((cx, by0 + sy * 0.16, 0.004))
            _bm_tube(bm, [Vector((cx, by0, 0.003)), hub], 0.0048, 0.0036, sides=5, col_layer=col_layer, c_tag=(0.82, 0.72, 0.50, 1.0))
            for k in range(19):
                ang = (k / 18.0 - 0.5) * 2.35
                d = Vector((math.sin(ang), math.cos(ang), 0.06)).normalized()
                _bm_blade(bm, hub, d, sy * 0.76 * (1.0 - 0.16 * abs(ang)), 0.0085, arch=0.005,
                          col_layer=col_layer, r_mode=1.0, ao_b=0.62, ao_t=0.98, segs=4)
        else:
            main = [Vector((cx + 0.005 * math.sin(i), by0 + sy * (i / 6.0), 0.004)) for i in range(7)]
            _bm_tube(bm, main, 0.0024, 0.0006, sides=4, col_layer=col_layer, c_tag=(0.80, 0.62, 0.45, 1.0))
            for k in range(14):
                t = 0.08 + 0.84 * (k / 13.0)
                p = Vector((cx, by0 + sy * t, 0.005))
                env = math.sin(math.pi * (0.12 + 0.84 * t))
                for sgn in (-1.0, 1.0):
                    d = Vector((sgn * 0.82, 0.48, 0.10)).normalized()
                    _bm_blade(bm, p, d, 0.048 * env, 0.013 * max(0.45, env), arch=0.003, lobes=3,
                              col_layer=col_layer, r_mode=1.0, ao_b=0.60, ao_t=0.98, segs=3)

    elif mode in ("jasmine_pink_lily", "madonna_lily_white", "lily_rose_iris"):
        # Bluetenstaengel mit Laubblaettern unten & strahlenden Lilien-/Jasminblueten oben
        stem = [Vector((cx + 0.006 * math.sin(i), by0 + sy * (i / 5.0) * 0.88, 0.004)) for i in range(6)]
        _bm_tube(bm, stem, 0.0028, 0.0012, sides=4, col_layer=col_layer, c_tag=(0.82, 0.65, 0.48, 1.0))
        for k in range(6):
            p = stem[0].lerp(stem[3], k / 5.0)
            for sgn in (-1.0, 1.0):
                d = Vector((sgn * 0.65, 0.72, 0.10)).normalized()
                _bm_blade(bm, p, d, 0.044, 0.013, arch=0.004, col_layer=col_layer, r_mode=1.0, ao_b=0.60, ao_t=0.96, segs=3)
        for fp in (stem[3], stem[4], stem[5], stem[4] + Vector((-0.026, 0.012, 0.003)), stem[4] + Vector((0.026, 0.014, 0.003))):
            _bm_flower_cluster(bm, fp + Vector((0, 0, 0.005)), 0.022 if "lily" in mode else 0.016,
                               petals=6 if "lily" in mode else 5, col_layer=col_layer, r_petal=0.45, r_core=0.22)

    elif mode == "lotus_pad":
        _bm_disk(bm, Vector((cx, by0 + sy * 0.50, 0.004)), min(sx, sy) * 0.46, segs=22,
                 col_layer=col_layer, c_edge=(1.0, 0.85, 0.82, 1.0), c_center=(1.0, 0.55, 0.65, 1.0), notch=True)

    elif mode == "lotus_flower":
        hc = Vector((cx, by0 + sy * 0.50, 0.004))
        for ring_i, (n_p, r_p, z_o) in enumerate(((10, 0.068, 0.002), (8, 0.048, 0.006))):
            for pi in range(n_p):
                ang = 2.0 * math.pi * (pi + 0.5 * ring_i) / n_p
                d = Vector((math.cos(ang), math.sin(ang), 0.15)).normalized()
                _bm_blade(bm, hc + Vector((0, 0, z_o)), d, r_p, r_p * 0.55, arch=0.004,
                          col_layer=col_layer, r_mode=0.45, ao_b=0.68, ao_t=1.0, thk_b=0.72, thk_t=0.98, segs=3)
        _bm_disk(bm, hc + Vector((0, 0, 0.012)), 0.016, segs=10, col_layer=col_layer,
                 c_edge=(0.22, 0.85, 0.60, 1.0), c_center=(0.22, 0.95, 0.70, 1.0))


def _make_atlas_material(spec):
    mode, col, row, c_leaf, c_accent, c_wood, rough = spec
    c_leaf = clamp_hdr(c_leaf)
    c_accent = clamp_hdr(c_accent)
    c_wood = clamp_hdr(c_wood)

    mat = bpy.data.materials.new(name=f"Mat_Cell_{mode}_{row}_{col}")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    emit = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])

    texcoord = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 34.0
    noise.inputs["Detail"].default_value = 5.0
    nt.links.new(texcoord.outputs["Object"], noise.inputs["Vector"])

    # Spezialfall: nahtlose Kacheln / Keramik / Holztrim
    if mode in ("shrub_wood_trim", "vine_wood_earth", "terracotta_pot", "terracotta_soil_rim", "lapis_glaze_band", "travertine_rim", "terracotta_bark"):
        wave = nt.nodes.new("ShaderNodeTexWave")
        wave.wave_type = "BANDS"
        wave.bands_direction = "Y" if mode in ("terracotta_pot", "lapis_glaze_band", "terracotta_soil_rim") else "X"
        wave.inputs["Scale"].default_value = 10.0 if mode == "lapis_glaze_band" else 14.0
        wave.inputs["Distortion"].default_value = 2.5 if mode == "lapis_glaze_band" else 6.0
        wave.inputs["Detail"].default_value = 4.0
        nt.links.new(texcoord.outputs["UV"], wave.inputs["Vector"])

        mix_f = nt.nodes.new("ShaderNodeMix")
        mix_f.data_type = "FLOAT"
        mix_f.inputs["Factor"].default_value = 0.45
        nt.links.new(wave.outputs["Fac"], mix_f.inputs["A"])
        nt.links.new(noise.outputs["Fac"], mix_f.inputs["B"])

        mix_c = nt.nodes.new("ShaderNodeMix")
        mix_c.data_type = "RGBA"
        mix_c.inputs["A"].default_value = (*c_wood, 1.0)
        mix_c.inputs["B"].default_value = (*c_accent, 1.0)
        nt.links.new(mix_f.outputs["Result"], mix_c.inputs["Factor"])
        col_out = mix_c.outputs["Result"]

        # Bump-Normal ueber Height
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.35
        bump.inputs["Distance"].default_value = 0.02
        nt.links.new(mix_f.outputs["Result"], bump.inputs["Height"])
        vec_n = nt.nodes.new("ShaderNodeVectorMath")
        vec_n.operation = "MULTIPLY_ADD"
        vec_n.inputs[1].default_value = (0.5, 0.5, 0.5)
        vec_n.inputs[2].default_value = (0.5, 0.5, 0.5)
        nt.links.new(bump.outputs["Normal"], vec_n.inputs[0])

        comb_orm = nt.nodes.new("ShaderNodeCombineColor")
        comb_orm.inputs["Blue"].default_value = 0.0
        mix_ao = nt.nodes.new("ShaderNodeMapRange")
        mix_ao.inputs["To Min"].default_value = 0.65
        mix_ao.inputs["To Max"].default_value = 1.0
        nt.links.new(mix_f.outputs["Result"], mix_ao.inputs["Value"])
        nt.links.new(mix_ao.outputs["Result"], comb_orm.inputs["Red"])
        comb_orm.inputs["Green"].default_value = rough

        comb_thk = nt.nodes.new("ShaderNodeCombineColor")
        comb_thk.inputs["Red"].default_value = 0.04
        comb_thk.inputs["Green"].default_value = 0.04
        comb_thk.inputs["Blue"].default_value = 0.04

        nt.links.new(col_out, emit.inputs["Color"])
        return {
            "mat": mat, "nt": nt, "emit": emit,
            "basecolor_out": col_out, "normal_out": vec_n.outputs["Vector"],
            "orm_out": comb_orm.outputs["Color"], "thick_out": comb_thk.outputs["Color"],
        }

    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "LeafData"
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(attr.outputs["Color"], sep.inputs["Color"])

    # Blattfarbe leicht organisch variieren
    leaf_hi = clamp_hdr((c_leaf[0] * 1.18, c_leaf[1] * 1.16, c_leaf[2] * 1.12))
    leaf_lo = clamp_hdr((c_leaf[0] * 0.80, c_leaf[1] * 0.82, c_leaf[2] * 0.84))
    mix_leaf = nt.nodes.new("ShaderNodeMix")
    mix_leaf.data_type = "RGBA"
    mix_leaf.inputs["A"].default_value = (*leaf_lo, 1.0)
    mix_leaf.inputs["B"].default_value = (*leaf_hi, 1.0)
    nt.links.new(noise.outputs["Fac"], mix_leaf.inputs["Factor"])

    # sep.Red (linear via float_color!): 0.0=Holz, 0.25=Bluetenkern Gold, 0.50=Bluete/Frucht/Aehre, 0.78=Halm, 1.0=Blatt
    stem_c = clamp_hdr((c_leaf[0] * 0.84, c_leaf[1] * 0.92, c_leaf[2] * 0.74))
    core_c = clamp_hdr((0.74, 0.58, 0.12))

    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    elems = ramp.color_ramp.elements
    elems[0].position = 0.00; elems[0].color = (*c_wood, 1.0)
    elems[1].position = 0.89; elems[1].color = (1.0, 1.0, 1.0, 1.0)
    e_core = elems.new(0.15); e_core.color = (*core_c, 1.0)
    e_acc = elems.new(0.36); e_acc.color = (*c_accent, 1.0)
    e_st = elems.new(0.66); e_st.color = (*stem_c, 1.0)
    nt.links.new(sep.outputs["Red"], ramp.inputs["Fac"])

    # Bei Red > 0.89 modulierte Blattfarbe nehmen, sonst scharfe Palette ohne graue Mischung!
    gt = nt.nodes.new("ShaderNodeMath")
    gt.operation = "GREATER_THAN"
    gt.inputs[1].default_value = 0.89
    nt.links.new(sep.outputs["Red"], gt.inputs[0])

    mix_col = nt.nodes.new("ShaderNodeMix")
    mix_col.data_type = "RGBA"
    nt.links.new(gt.outputs["Value"], mix_col.inputs["Factor"])
    nt.links.new(ramp.outputs["Color"], mix_col.inputs["A"])
    nt.links.new(mix_leaf.outputs["Result"], mix_col.inputs["B"])

    geom = nt.nodes.new("ShaderNodeNewGeometry")
    vec_mul = nt.nodes.new("ShaderNodeVectorMath")
    vec_mul.operation = "MULTIPLY_ADD"
    vec_mul.inputs[1].default_value = (0.5, 0.5, 0.5)
    vec_mul.inputs[2].default_value = (0.5, 0.5, 0.5)
    nt.links.new(geom.outputs["Normal"], vec_mul.inputs[0])

    comb_orm = nt.nodes.new("ShaderNodeCombineColor")
    comb_orm.inputs["Blue"].default_value = 0.0
    nt.links.new(sep.outputs["Green"], comb_orm.inputs["Red"])
    comb_orm.inputs["Green"].default_value = rough

    comb_thk = nt.nodes.new("ShaderNodeCombineColor")
    nt.links.new(sep.outputs["Blue"], comb_thk.inputs["Red"])
    nt.links.new(sep.outputs["Blue"], comb_thk.inputs["Green"])
    nt.links.new(sep.outputs["Blue"], comb_thk.inputs["Blue"])

    nt.links.new(mix_col.outputs["Result"], emit.inputs["Color"])
    return {
        "mat": mat, "nt": nt, "emit": emit,
        "basecolor_out": mix_col.outputs["Result"], "normal_out": vec_mul.outputs["Vector"],
        "orm_out": comb_orm.outputs["Color"], "thick_out": comb_thk.outputs["Color"],
    }


def _dilate_rgba_4x4(filepath, pad_iters=24):
    import numpy as np
    img = bpy.data.images.load(filepath, check_existing=False)
    w, h = img.size[0], img.size[1]
    arr = np.array(img.pixels[:], dtype=np.float32).reshape((h, w, 4))
    rgb = arr[:, :, :3].copy()
    alpha = arr[:, :, 3].copy()
    valid = alpha > 0.04
    for _ in range(pad_iters):
        if valid.all():
            break
        acc = np.zeros_like(rgb)
        cnt = np.zeros((h, w), dtype=np.float32)
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            sr0, sr1 = max(0, -dy), h - max(0, dy)
            dr0, dr1 = max(0, dy), h - max(0, -dy)
            sc0, sc1 = max(0, -dx), w - max(0, dx)
            dc0, dc1 = max(0, dx), w - max(0, -dx)
            m = valid[sr0:sr1, sc0:sc1]
            acc[dr0:dr1, dc0:dc1][m] += rgb[sr0:sr1, sc0:sc1][m]
            cnt[dr0:dr1, dc0:dc1][m] += 1.0
        fill = (~valid) & (cnt > 0.0)
        if not fill.any():
            break
        rgb[fill] = acc[fill] / cnt[fill, None]
        valid[fill] = True
    if not valid.all():
        cw, ch = w // 4, h // 4
        for r in range(4):
            y0, y1 = r * ch, (r + 1) * ch if r < 3 else h
            for c in range(4):
                x0, x1 = c * cw, (c + 1) * cw if c < 3 else w
                cmask = valid[y0:y1, x0:x1]
                mean_col = rgb[y0:y1, x0:x1][cmask].mean(axis=0) if cmask.any() else np.array([0.30, 0.40, 0.22], dtype=np.float32)
                rgb[y0:y1, x0:x1][~cmask] = mean_col
    arr[:, :, :3] = np.clip(rgb, 0.0, 1.0)
    arr[:, :, 3] = np.clip(alpha, 0.0, 1.0)
    img.pixels.foreach_set(arr.ravel())
    img.save()
    bpy.data.images.remove(img)


UNDERSTORY_CELLS = [
    # (mode, col, row, leaf_rgb, accent_rgb, wood_rgb, roughness)
    ("thornbush",       0, 0, (0.28, 0.34, 0.20), (0.48, 0.42, 0.28), (0.24, 0.19, 0.14), 0.78),
    ("tamarisk",        1, 0, (0.22, 0.38, 0.26), (0.68, 0.44, 0.50), (0.26, 0.19, 0.14), 0.74),
    ("oleander",        2, 0, (0.14, 0.32, 0.15), (0.72, 0.32, 0.42), (0.24, 0.20, 0.14), 0.52),
    ("broom_juniper",   3, 0, (0.30, 0.38, 0.16), (0.74, 0.62, 0.12), (0.26, 0.24, 0.14), 0.72),
    ("shrub_wood_trim", 0, 1, (0.26, 0.20, 0.14), (0.34, 0.27, 0.19), (0.20, 0.15, 0.10), 0.88),
    ("juniper",         1, 1, (0.14, 0.27, 0.16), (0.26, 0.34, 0.46), (0.22, 0.17, 0.12), 0.76),
    ("steppe_grass",    2, 1, (0.42, 0.40, 0.20), (0.58, 0.50, 0.26), (0.34, 0.30, 0.16), 0.80),
    ("tall_grass",      3, 1, (0.24, 0.42, 0.16), (0.52, 0.48, 0.24), (0.24, 0.34, 0.14), 0.74),
    ("euphrates_reed",  0, 2, (0.22, 0.40, 0.18), (0.60, 0.55, 0.42), (0.28, 0.35, 0.16), 0.72),
    ("papyrus_head",    1, 2, (0.20, 0.44, 0.16), (0.48, 0.44, 0.24), (0.24, 0.36, 0.15), 0.70),
    ("emmer_wheat",     2, 2, (0.48, 0.42, 0.18), (0.68, 0.52, 0.18), (0.36, 0.30, 0.14), 0.76),
    ("barley",          3, 2, (0.44, 0.42, 0.20), (0.72, 0.62, 0.26), (0.38, 0.34, 0.18), 0.76),
    ("lentil_chickpea", 0, 3, (0.24, 0.42, 0.18), (0.68, 0.64, 0.66), (0.24, 0.34, 0.16), 0.72),
    ("flax",            1, 3, (0.22, 0.40, 0.22), (0.34, 0.52, 0.74), (0.24, 0.36, 0.18), 0.68),
    ("grapevine",       2, 3, (0.22, 0.44, 0.15), (0.24, 0.10, 0.28), (0.24, 0.17, 0.12), 0.64),
    ("vine_wood_earth", 3, 3, (0.24, 0.17, 0.12), (0.28, 0.21, 0.15), (0.16, 0.11, 0.08), 0.90),
]

ORNAMENTAL_CELLS = [
    ("pomegranate_foliage", 0, 0, (0.16, 0.38, 0.14), (0.74, 0.22, 0.10), (0.24, 0.18, 0.13), 0.54),
    ("pomegranate_fruit",   1, 0, (0.16, 0.38, 0.14), (0.64, 0.12, 0.10), (0.24, 0.18, 0.13), 0.50),
    ("dwarf_palm_olive",    2, 0, (0.24, 0.40, 0.20), (0.36, 0.46, 0.26), (0.26, 0.20, 0.14), 0.62),
    ("ornamental_fern",     3, 0, (0.18, 0.46, 0.16), (0.26, 0.52, 0.18), (0.18, 0.28, 0.12), 0.60),
    ("myrtle",              0, 1, (0.12, 0.30, 0.14), (0.74, 0.72, 0.68), (0.22, 0.17, 0.12), 0.54),
    ("jasmine_pink_lily",   1, 1, (0.18, 0.38, 0.16), (0.72, 0.52, 0.58), (0.20, 0.26, 0.14), 0.56),
    ("madonna_lily_white",  2, 1, (0.20, 0.40, 0.16), (0.74, 0.73, 0.68), (0.20, 0.32, 0.14), 0.54),
    ("lily_rose_iris",      3, 1, (0.18, 0.38, 0.16), (0.56, 0.46, 0.68), (0.20, 0.30, 0.14), 0.56),
    ("lotus_pad",           0, 2, (0.18, 0.40, 0.18), (0.30, 0.48, 0.22), (0.16, 0.30, 0.14), 0.44),
    ("lotus_flower",        1, 2, (0.22, 0.42, 0.18), (0.72, 0.40, 0.50), (0.20, 0.32, 0.15), 0.52),
    ("cyperus_fan",         2, 2, (0.20, 0.44, 0.16), (0.32, 0.48, 0.20), (0.18, 0.32, 0.14), 0.64),
    ("terracotta_bark",     3, 2, (0.26, 0.20, 0.15), (0.34, 0.28, 0.21), (0.22, 0.17, 0.12), 0.86),
    ("terracotta_pot",      0, 3, (0.54, 0.28, 0.17), (0.60, 0.34, 0.21), (0.46, 0.22, 0.13), 0.78),
    ("terracotta_soil_rim", 1, 3, (0.18, 0.13, 0.09), (0.42, 0.22, 0.14), (0.14, 0.10, 0.07), 0.88),
    ("lapis_glaze_band",    2, 3, (0.10, 0.24, 0.52), (0.62, 0.48, 0.20), (0.08, 0.16, 0.42), 0.34),
    ("travertine_rim",      3, 3, (0.60, 0.54, 0.42), (0.66, 0.60, 0.48), (0.50, 0.44, 0.34), 0.72),
]


def bake_1024_atlas(prefix, cells, builder_fn, tex_dir, size=1024):
    t0 = time.time()
    print(f"[ATLAS] Starte Cycles-Bake fuer {prefix}_* ({size}x{size}, 16 Zellen)...", flush=True)
    scene = clear_scene()
    dev = setup_cycles(scene, samples=4)

    mesh = bpy.data.meshes.new(f"{prefix}_Atlas3D")
    bm = bmesh.new()
    col_layer = bm.loops.layers.float_color.new("LeafData") if hasattr(bm.loops.layers, "float_color") else bm.loops.layers.color.new("LeafData")
    bm.loops.layers.uv.new("UVMap")

    mat_infos = []
    for idx, spec in enumerate(cells):
        f_start = len(bm.faces)
        builder_fn(bm, spec, col_layer)
        bm.faces.ensure_lookup_table()
        for fi in range(f_start, len(bm.faces)):
            bm.faces[fi].material_index = idx
        mat_infos.append(_make_atlas_material(spec))

    bm.to_mesh(mesh)
    bm.free()
    for info in mat_infos:
        mesh.materials.append(info["mat"])

    obj = bpy.data.objects.new(f"{prefix}_Atlas3D", mesh)
    scene.collection.objects.link(obj)

    cam_d = bpy.data.cameras.new("AtlasCam")
    cam_d.type = "ORTHO"
    cam_d.ortho_scale = 1.0
    cam_o = bpy.data.objects.new("AtlasCam", cam_d)
    cam_o.location = (0.5, 0.5, 2.0)
    scene.collection.objects.link(cam_o)
    scene.camera = cam_o

    scene.render.resolution_x = size
    scene.render.resolution_y = size
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_depth = "8"

    world = bpy.data.worlds.new("AtlasWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")

    def _pass(key, name, colorspace, rgba, bg_col=None):
        if bg and bg_col is not None:
            bg.inputs["Color"].default_value = bg_col
        for info in mat_infos:
            info["nt"].links.new(info[key], info["emit"].inputs["Color"])
        scene.render.film_transparent = bool(rgba)
        scene.render.image_settings.color_mode = "RGBA" if rgba else "RGB"
        scene.view_settings.view_transform = "Raw" if colorspace == "Non-Color" else "Standard"
        fp = os.path.join(tex_dir, f"{prefix}_{name}.png")
        scene.render.filepath = fp
        bpy.ops.render.render(write_still=True)
        return fp

    p_bc = _pass("basecolor_out", "baseColor", "sRGB", True)
    _dilate_rgba_4x4(p_bc, pad_iters=24)
    p_nm = _pass("normal_out", "normal", "Non-Color", False, (0.5, 0.5, 1.0, 1.0))
    p_or = _pass("orm_out", "orm", "Non-Color", False, (1.0, 0.5, 0.0, 1.0))
    p_th = _pass("thick_out", "thickness", "Non-Color", False, (0.0, 0.0, 0.0, 1.0))

    dt = time.time() - t0
    print(f"[ATLAS] {prefix}_* fertig auf {dev} in {dt:.2f}s.", flush=True)
    return {"baseColor": p_bc, "normal": p_nm, "orm": p_or, "thickness": p_th, "time_s": dt}


# ==============================================================================
# 2. GEMEINSAME GEOMETRIE-BAUSTEINE (Col_Wind: R=Wind, G=Flutter, B=AO)
# ==============================================================================

def _add_wood_branch(bm, pts, r0, r1, sides, col_l, uv_l, cell_col, cell_row, wind_h_norm, flutter, mat_idx=0):
    if len(pts) < 2:
        return
    u0, v0, u1, v1 = atlas_uv_box(cell_col, cell_row, pad_x=0.015, pad_y=0.015)
    rings = []
    for idx, p in enumerate(pts):
        t = idx / float(len(pts) - 1)
        rad = max(0.004, r0 * (1.0 - t) + r1 * t)
        tang = (pts[min(len(pts) - 1, idx + 1)] - pts[max(0, idx - 1)]).normalized()
        if tang.length < 1e-6:
            tang = Vector((0.0, 0.0, 1.0))
        ref = Vector((1.0, 0.0, 0.0)) if abs(tang.x) < 0.8 else Vector((0.0, 1.0, 0.0))
        bx = tang.cross(ref).normalized()
        by = tang.cross(bx).normalized()
        wind_r = min(1.0, max(0.0, p.z / max(0.25, wind_h_norm)) ** 1.35)
        ao_b = 0.46 + 0.38 * t
        ring = []
        for si in range(sides):
            ang = 2.0 * math.pi * si / sides
            v = bm.verts.new(p + (bx * math.cos(ang) + by * math.sin(ang)) * rad)
            ring.append((v, u0 + (u1 - u0) * (si / float(sides)), v0 + (v1 - v0) * t, wind_r, ao_b))
        rings.append(ring)
    for ri in range(len(rings) - 1):
        ra, rb = rings[ri], rings[ri + 1]
        for si in range(sides):
            sn = (si + 1) % sides
            v0_, uu0, vv0, w0, a0 = ra[si]
            v1_, uu1, _, _, _ = ra[sn]
            v2_, _, vv1, w1, a1 = rb[sn]
            v3_, _, _, _, _ = rb[si]
            try:
                f = bm.faces.new((v0_, v1_, v2_, v3_))
                f.material_index = mat_idx
                f.smooth = True
                for lp, uu, vv, ww, aa in zip(f.loops, (uu0, uu1, uu1, uu0), (vv0, vv0, vv1, vv1), (w0, w0, w1, w1), (a0, a0, a1, a1)):
                    lp[col_l] = (ww, flutter, aa, 1.0)
                    lp[uv_l].uv = (uu, vv)
            except ValueError:
                pass


def _add_card(bm, base, axis, side, card_w, card_h, col_l, uv_l, cell_col, cell_row,
              wind_r0, wind_r1, flutter, ao_base=0.60, ao_tip=0.98, bend=0.08, segs_v=2, mat_idx=1):
    """Gewoelbte PBR-Pflanzenkarte (2 bis 6 Tris, strikt Col_Wind & Zellen-UVs)."""
    u0, v0, u1, v1 = atlas_uv_box(cell_col, cell_row, pad_x=0.015, pad_y=0.015)
    ax = axis.normalized()
    sd = side.normalized()
    nrm = sd.cross(ax).normalized()
    grid = []
    for vi in range(segs_v + 1):
        tv = vi / float(segs_v)
        bend_off = math.sin(math.pi * tv) * bend * card_h
        c_pos = base + ax * (card_h * tv) + nrm * bend_off
        w_val = wind_r0 + (wind_r1 - wind_r0) * tv
        ao_val = ao_base + (ao_tip - ao_base) * tv
        row_v = []
        for ui in (0, 1):
            tu = float(ui)
            vpos = c_pos + sd * ((tu - 0.5) * card_w)
            vert = bm.verts.new(vpos)
            row_v.append((vert, u0 + (u1 - u0) * tu, v0 + (v1 - v0) * tv, w_val, ao_val))
        grid.append(row_v)
    for vi in range(segs_v):
        v_bl, u_l, v_b, wb, ab = grid[vi][0]
        v_br, u_r, _, _, _ = grid[vi][1]
        v_tr, _, v_t, wt, at = grid[vi + 1][1]
        v_tl, _, _, _, _ = grid[vi + 1][0]
        try:
            f = bm.faces.new((v_bl, v_br, v_tr, v_tl))
            f.material_index = mat_idx
            f.smooth = True
            for lp, uu, vv, ww, aa in zip(f.loops, (u_l, u_r, u_r, u_l), (v_b, v_b, v_t, v_t), (wb, wb, wt, wt), (ab, ab, at, at)):
                lp[col_l] = (ww, flutter, aa, 1.0)
                lp[uv_l].uv = (uu, vv)
        except ValueError:
            pass


def _add_crossed_bush_spray(bm, center, axis, size, col_l, uv_l, cc, cr, wind_r, ao, rng, n_cards=2, segs_v=1, mat_idx=1):
    ax = axis.normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(ax.z) < 0.85 else Vector((1.0, 0.0, 0.0))
    s0 = ax.cross(ref).normalized()
    s1 = ax.cross(s0).normalized()
    for ci in range(n_cards):
        ang = ci * (math.pi / float(n_cards)) + rng.uniform(-0.22, 0.22)
        sd = (s0 * math.cos(ang) + s1 * math.sin(ang)).normalized()
        c_ax = (ax + sd.cross(ax) * rng.uniform(-0.18, 0.18)).normalized()
        _add_card(bm, center - c_ax * (size * 0.20), c_ax, sd, size * 0.96, size * 1.06,
                  col_l, uv_l, cc, cr, max(0.15, wind_r * 0.72), min(1.0, wind_r),
                  rng.uniform(0.15, 0.95), ao_base=ao * 0.84, ao_tip=min(1.0, ao * 1.08),
                  bend=0.10, segs_v=segs_v, mat_idx=mat_idx)


def _add_vessel(bm, radius, height, wall_t, base_z, sides, rings_z, col_l, uv_l, cc_body, cr_body, cc_rim, cr_rim, cc_soil, cr_soil, mat_idx=0, has_lapis=False):
    """Gedrehtes Terrakotta-/Lapis-Pflanzgefaess: strikt Col_Wind.R = 0.0 (weht NICHT im Wind!)."""
    ring_verts = []
    u0b, v0b, u1b, v1b = atlas_uv_box(cc_body, cr_body, pad_x=0.02, pad_y=0.02)
    u0r, v0r, u1r, v1r = atlas_uv_box(cc_rim, cr_rim, pad_x=0.02, pad_y=0.02)
    u0s, v0s, u1s, v1s = atlas_uv_box(cc_soil, cr_soil, pad_x=0.02, pad_y=0.02)

    for ri in range(rings_z + 1):
        tz = ri / float(rings_z)
        z = base_z + height * tz
        bulge = 0.68 + 0.36 * math.sin(math.pi * (0.12 + 0.72 * tz)) + (0.08 if tz > 0.88 else 0.0)
        rad = radius * bulge
        ring = []
        for si in range(sides):
            ang = 2.0 * math.pi * si / sides
            ring.append(bm.verts.new((math.cos(ang) * rad, math.sin(ang) * rad, z)))
        ring_verts.append((tz, ring))

    for ri in range(rings_z):
        tz0, ra = ring_verts[ri]
        tz1, rb = ring_verts[ri + 1]
        is_band = has_lapis and (tz0 >= 0.66)
        uu0, vv0_box, uu1, vv1_box = (u0r, v0r, u1r, v1r) if is_band else (u0b, v0b, u1b, v1b)
        for si in range(sides):
            sn = (si + 1) % sides
            try:
                f = bm.faces.new((ra[si], ra[sn], rb[sn], rb[si]))
                f.material_index = mat_idx
                f.smooth = True
                for lp, uf, vf in zip(f.loops, (si / sides, (si + 1) / sides, (si + 1) / sides, si / sides), (tz0, tz0, tz1, tz1)):
                    lp[col_l] = (0.0, 0.25, 0.65 + 0.25 * vf, 1.0)
                    lp[uv_l].uv = (uu0 + (uu1 - uu0) * uf, vv0_box + (vv1_box - vv0_box) * vf)
            except ValueError:
                pass

    # Erdfuellungs-Scheibe kurz unter dem Rand (damit Pflanzen sauber im Topf wurzeln)
    soil_z = base_z + height * 0.90
    soil_r = max(0.05, radius * 0.92 - wall_t * 0.5)
    vc = bm.verts.new((0.0, 0.0, soil_z))
    s_ring = [bm.verts.new((math.cos(2 * math.pi * si / sides) * soil_r, math.sin(2 * math.pi * si / sides) * soil_r, soil_z)) for si in range(sides)]
    for si in range(sides):
        sn = (si + 1) % sides
        try:
            f = bm.faces.new((vc, s_ring[si], s_ring[sn]))
            f.material_index = mat_idx
            for lp in f.loops:
                lp[col_l] = (0.0, 0.25, 0.55, 1.0)
                if lp.vert == vc:
                    lp[uv_l].uv = ((u0s + u1s) * 0.5, (v0s + v1s) * 0.5)
                else:
                    lp[uv_l].uv = (u0s + (u1s - u0s) * (0.5 + 0.4 * (lp.vert.co.x / soil_r)),
                                   v0s + (v1s - v0s) * (0.5 + 0.4 * (lp.vert.co.y / soil_r)))
        except ValueError:
            pass
    return soil_z


# ==============================================================================
# 3. SPEZIES-GENERATOREN FÜR ALLE 4 PAKETE (JE 4 LODs: LOD0..LOD3)
# ==============================================================================

def _build_shrub_bm(bm, species, idx, seed, lod):
    rng = random.Random(seed)
    col_l = bm.loops.layers.color.new("Col_Wind")
    uv_l = bm.loops.layers.uv.new("UVMap")

    # Atlas-Zelle der Art bestimmen
    cell_map = {
        "thornbush": (0, 0, 0.85),
        "tamarisk":  (1, 0, 1.55),
        "oleander":  (2, 0, 1.65),
        "broom":     (3, 0, 1.05),
        "juniper":   (1, 1, 0.95),
    }
    cc, cr, h_base = cell_map[species]
    h = h_base * rng.uniform(0.76, 1.24)
    w = h * (1.28 if species in ("thornbush", "juniper") else 0.95)

    if lod == 3:
        # Kompakte Horizont-Proxy (8-16 Tris)
        for ang in (0.0, 1.57):
            _add_card(bm, Vector((0, 0, 0)), Vector((0, 0, 1)), Vector((math.cos(ang), math.sin(ang), 0)),
                      w * 1.1, h, col_l, uv_l, cc, cr, 0.0, 0.88, 0.4, ao_base=0.55, ao_tip=0.95, bend=0.05, segs_v=1, mat_idx=1)
        return

    n_stems = {0: 5 if species != "juniper" else 5, 1: 4, 2: 2}[lod]
    wood_sides = 5 if lod == 0 else (4 if lod == 1 else 3)
    cards_per_tip = {0: 3, 1: 2, 2: 1}[lod]
    segs_card = 2 if lod == 0 else 1

    # Bei kleinerem LOD2 reines Astkreuz + weite Sprays
    for si in range(n_stems):
        az = 2.0 * math.pi * si / n_stems + rng.uniform(-0.35, 0.35)
        tilt = rng.uniform(0.32, 0.88) if species != "oleander" else rng.uniform(0.18, 0.55)
        dir_v = Vector((math.sin(tilt) * math.cos(az), math.sin(tilt) * math.sin(az), math.cos(tilt))).normalized()
        s_len = h * rng.uniform(0.68, 1.02)
        mid = dir_v * (s_len * 0.48) + Vector((0, 0, -0.05 if species == "tamarisk" else 0.04))
        tip = dir_v * s_len + Vector((math.cos(az) * 0.14 * w, math.sin(az) * 0.14 * w, -0.08 * h if species == "tamarisk" else 0.05))
        _add_wood_branch(bm, [Vector((0, 0, 0)), mid, tip], 0.036, 0.011, wood_sides, col_l, uv_l, 0, 1, h, rng.random(), mat_idx=0)

        # Laub-Bueschel am Hauptast & Nebenzweig
        for f_t, c_sz in ((0.55, h * 0.56), (0.92, h * 0.68)) if lod <= 1 else ((0.78, h * 0.78),):
            p_f = mid.lerp(tip, f_t)
            for ci in range(cards_per_tip):
                c_ang = az + ci * 1.4 + rng.uniform(-0.4, 0.4)
                c_ax = (dir_v * 0.55 + Vector((math.cos(c_ang) * 0.45, math.sin(c_ang) * 0.45, rng.uniform(0.2, 0.6)))).normalized()
                _add_crossed_bush_spray(bm, p_f, c_ax, c_sz * rng.uniform(0.85, 1.15), col_l, uv_l, cc, cr,
                                        min(1.0, max(0.25, p_f.z / h)), 0.62 + 0.30 * f_t, rng, n_cards=2 if lod == 0 else 1, segs_v=segs_card, mat_idx=1)

    if lod == 0:
        # Zentrales Innenlaub fuer volle runde Silhouette
        _add_crossed_bush_spray(bm, Vector((0, 0, h * 0.45)), Vector((0.1, 0.1, 1.0)), h * 0.66, col_l, uv_l, cc, cr, 0.65, 0.72, rng, n_cards=3, segs_v=2, mat_idx=1)


def _build_grass_reed_bm(bm, species, idx, seed, lod):
    rng = random.Random(seed)
    col_l = bm.loops.layers.color.new("Col_Wind")
    uv_l = bm.loops.layers.uv.new("UVMap")

    if species == "steppe_grass":
        h = rng.uniform(0.38, 0.72)
        w = h * 0.85
        cc, cr = 2, 1
        n_c = {0: 6, 1: 4, 2: 2, 3: 1}[lod]
        segs = 2 if lod == 0 else 1
    elif species == "tall_grass":
        h = rng.uniform(0.68, 1.12)
        w = h * 0.65
        cc, cr = 3, 1
        n_c = {0: 7, 1: 4, 2: 2, 3: 1}[lod]
        segs = 2 if lod == 0 else 1
    else:  # euphrates_reed
        h = rng.uniform(1.45, 2.55)
        w = h * 0.34
        cc, cr = 0, 2
        n_c = {0: 8, 1: 4, 2: 2, 3: 1}[lod]
        segs = 2 if lod == 0 else 1

    if lod == 3:
        for ang in (0.0, 1.57):
            _add_card(bm, Vector((0, 0, 0)), Vector((0, 0, 1)), Vector((math.cos(ang), math.sin(ang), 0)),
                      max(w, 0.45), h, col_l, uv_l, cc, cr, 0.0, 0.95, 0.5, ao_base=0.55, ao_tip=0.98, bend=0.06, segs_v=1, mat_idx=0)
        return

    for ci in range(n_c):
        ang = (ci / float(n_c)) * math.pi * 2.0 + rng.uniform(-0.3, 0.3)
        r_off = rng.uniform(0.02, w * 0.42)
        b_pos = Vector((math.cos(ang) * r_off, math.sin(ang) * r_off, 0.0))
        tilt = rng.uniform(0.06, 0.30 if species != "euphrates_reed" else 0.16)
        ax = Vector((math.cos(ang) * tilt, math.sin(ang) * tilt, 1.0)).normalized()
        sd = Vector((-math.sin(ang + 0.5), math.cos(ang + 0.5), 0.0)).normalized()
        ch = h * rng.uniform(0.75, 1.10)
        cw = w * (0.72 if species != "euphrates_reed" else 0.85)
        _add_card(bm, b_pos, ax, sd, cw, ch, col_l, uv_l, cc, cr, 0.0, 1.0, rng.random(),
                  ao_base=0.52, ao_tip=0.99, bend=0.14 if species != "euphrates_reed" else 0.08, segs_v=segs, mat_idx=0)

    # Bei Papyrus-Schilf-Varianten (gerade Indizes) feine Papyrus-Krone aufsetzen!
    if species == "euphrates_reed" and (idx % 2 == 1) and lod <= 1:
        cap_z = h * 0.84
        _add_card(bm, Vector((0, 0, cap_z)), Vector((0.06, 0.04, 1.0)), Vector((1, 0, 0)),
                  0.52, 0.46, col_l, uv_l, 1, 2, 0.78, 1.0, 0.65, ao_base=0.68, ao_tip=1.0, bend=0.06, segs_v=1, mat_idx=0)


def _build_crop_bm(bm, species, idx, seed, lod):
    rng = random.Random(seed)
    col_l = bm.loops.layers.color.new("Col_Wind")
    uv_l = bm.loops.layers.uv.new("UVMap")

    specs = {
        "emmer_wheat":     (2, 2, 0.85, 1.15, 0.46),
        "barley":          (3, 2, 0.68, 0.96, 0.44),
        "lentil_chickpea": (0, 3, 0.34, 0.54, 0.58),
        "flax":            (1, 3, 0.56, 0.84, 0.42),
        "grapevine":       (2, 3, 0.75, 1.25, 0.92),
    }
    cc, cr, h_min, h_max, spread = specs[species]
    h = rng.uniform(h_min, h_max)

    if species == "grapevine" and lod <= 1:
        # Gnarled Rebstock + Ranken (Material 0 Holz / Material 1 Weinlaub)
        trunk_pts = [Vector((0, 0, 0)), Vector((rng.uniform(-0.08, 0.08), 0.0, h * 0.34)), Vector((0.0, rng.uniform(-0.06, 0.06), h * 0.64))]
        _add_wood_branch(bm, trunk_pts, 0.052, 0.022, 5 if lod == 0 else 4, col_l, uv_l, 3, 3, h, 0.25, mat_idx=0)
        n_arms = 4 if lod == 0 else 2
        for ai in range(n_arms):
            az = 2.0 * math.pi * ai / n_arms + rng.uniform(-0.3, 0.3)
            tip = trunk_pts[-1] + Vector((math.cos(az) * spread * 0.55, math.sin(az) * spread * 0.55, rng.uniform(0.06, 0.24)))
            _add_wood_branch(bm, [trunk_pts[-1], tip], 0.020, 0.008, 3, col_l, uv_l, 3, 3, h, 0.4, mat_idx=0)
            _add_crossed_bush_spray(bm, tip, Vector((math.cos(az) * 0.3, math.sin(az) * 0.3, 1.0)), h * 0.55,
                                    col_l, uv_l, cc, cr, 0.88, 0.78, rng, n_cards=2 if lod == 0 else 1, segs_v=2 if lod == 0 else 1, mat_idx=1)
        return

    # Feldpflanzen-Buendel (Emmer, Gerste, Linsen, Flachs) & LOD2/LOD3-Weinrebe -> immer Cutout-Material Slot 1 (CropsFoliage)!
    mat_use = 1
    n_c = {0: 6 if species != "grapevine" else 5, 1: 4, 2: 2, 3: 1}[lod]
    segs = 2 if lod == 0 else 1
    if lod == 3:
        for ang in (0.0, 1.57):
            _add_card(bm, Vector((0, 0, 0)), Vector((0, 0, 1)), Vector((math.cos(ang), math.sin(ang), 0)),
                      max(spread, 0.38), h, col_l, uv_l, cc, cr, 0.0, 0.92, 0.5, ao_base=0.58, ao_tip=0.98, bend=0.04, segs_v=1, mat_idx=mat_use)
        return
    for ci in range(n_c):
        ang = ci * (math.pi / max(1, n_c * 0.5)) + rng.uniform(-0.25, 0.25)
        r_off = rng.uniform(0.02, spread * 0.35)
        b = Vector((math.cos(ang) * r_off, math.sin(ang) * r_off, 0.0))
        ax = Vector((math.cos(ang) * 0.14, math.sin(ang) * 0.14, 1.0)).normalized()
        sd = Vector((-math.sin(ang), math.cos(ang), 0.0)).normalized()
        _add_card(bm, b, ax, sd, spread * rng.uniform(0.75, 1.05), h * rng.uniform(0.82, 1.08),
                  col_l, uv_l, cc, cr, 0.0, 1.0, rng.random(), ao_base=0.56, ao_tip=0.99, bend=0.09, segs_v=segs, mat_idx=mat_use)


def _build_ornamental_bm(bm, species, idx, seed, lod):
    rng = random.Random(seed)
    col_l = bm.loops.layers.color.new("Col_Wind")
    uv_l = bm.loops.layers.uv.new("UVMap")

    if species == "pomegranate_ornamental":
        in_pot = (idx >= 7)  # 0..6 frei gepflanzt, 7..12 im mesopotamischen Terrakotta-Kuebel!
        h_total = rng.uniform(1.25, 2.15)
        base_z = 0.0
        if in_pot:
            pot_h = 0.44 * rng.uniform(0.88, 1.15)
            pot_r = 0.28 * rng.uniform(0.90, 1.12)
            p_sides = {0: 12, 1: 8, 2: 6, 3: 5}[lod]
            p_rings = 4 if lod == 0 else (3 if lod == 1 else 2)
            base_z = _add_vessel(bm, pot_r, pot_h, 0.03, 0.0, p_sides, p_rings, col_l, uv_l,
                                 0, 3, 2, 3, 1, 3, mat_idx=0, has_lapis=(idx % 2 == 0))
        if lod == 3:
            for ang in (0.0, 1.57):
                _add_card(bm, Vector((0, 0, base_z)), Vector((0, 0, 1)), Vector((math.cos(ang), math.sin(ang), 0)),
                          h_total * 0.72, h_total - base_z, col_l, uv_l, 1, 0, 0.0, 0.85, 0.4, segs_v=1, mat_idx=1)
            return
        # Mehrstaemmiger Granatapfel-Staemmchenaufbau (Material 0 = Holz/Kuebel, Material 1 = Laub+Blueten+Fruechte)
        n_trunks = 2 if (lod == 0 and idx % 2 == 0) else 1
        wood_s = 6 if lod == 0 else (4 if lod == 1 else 3)
        n_sprays = {0: 6, 1: 3, 2: 2}[lod]
        segs_c = 2 if lod == 0 else 1
        for ti in range(n_trunks):
            lean = Vector((rng.uniform(-0.08, 0.08), rng.uniform(-0.08, 0.08), 0.0))
            pts = [
                Vector((0, 0, base_z - 0.02)),
                lean * 0.5 + Vector((0, 0, base_z + (h_total - base_z) * 0.34)),
                lean + Vector((0, 0, base_z + (h_total - base_z) * 0.58)),
            ]
            _add_wood_branch(bm, pts, 0.055, 0.020, wood_s, col_l, uv_l, 3, 2, h_total, 0.25, mat_idx=0)
            for si in range(n_sprays):
                az = 2.0 * math.pi * si / n_sprays + rng.uniform(-0.3, 0.3)
                d_b = Vector((math.cos(az) * 0.58, math.sin(az) * 0.58, 0.82)).normalized()
                tip = pts[-1] + d_b * (h_total * 0.26)
                _add_wood_branch(bm, [pts[-1], tip], 0.020, 0.008, 3, col_l, uv_l, 3, 2, h_total, 0.45, mat_idx=0)
                cc_use = 1 if (si + idx) % 2 == 0 else 0  # Abwechselnd Blueten- & Fruchtzellen!
                _add_crossed_bush_spray(bm, tip, d_b, h_total * 0.36, col_l, uv_l, cc_use, 0, 0.82, 0.80, rng,
                                        n_cards=2 if lod == 0 else 1, segs_v=segs_c, mat_idx=1)

    elif species == "myrtle_lily":
        # Tempel-Myrte + Madonnen-Lilien & Jasmin-Bluetenhorste (80-240 Tris bei LOD0)
        h = rng.uniform(0.68, 1.18)
        n_c = {0: 14, 1: 6, 2: 3, 3: 1}[lod]
        segs = 2 if lod == 0 else 1
        if lod == 3:
            for ang in (0.0, 1.57):
                _add_card(bm, Vector((0, 0, 0)), Vector((0, 0, 1)), Vector((math.cos(ang), math.sin(ang), 0)),
                          h * 0.9, h, col_l, uv_l, 2, 1, 0.0, 0.88, 0.5, segs_v=1, mat_idx=1)
            return
        # Myrten-Polster unten + hohe Lilien/Jasmin-Stiele mittig
        for ci in range(n_c):
            az = 2.0 * math.pi * ci / n_c + rng.uniform(-0.2, 0.2)
            is_lily = (ci % 2 == 0)
            cc_cell = (2, 1) if (is_lily and idx % 3 != 2) else ((3, 1) if is_lily else (0, 1))
            if is_lily:
                b = Vector((math.cos(az) * 0.14, math.sin(az) * 0.14, 0.0))
                ax = Vector((math.cos(az) * 0.12, math.sin(az) * 0.12, 1.0)).normalized()
                sd = Vector((-math.sin(az), math.cos(az), 0.0)).normalized()
                _add_card(bm, b, ax, sd, h * 0.42, h * rng.uniform(0.84, 1.04), col_l, uv_l, cc_cell[0], cc_cell[1],
                          0.0, 1.0, rng.random(), ao_base=0.62, ao_tip=1.0, bend=0.08, segs_v=segs, mat_idx=1)
            else:
                p = Vector((math.cos(az) * 0.24, math.sin(az) * 0.24, 0.05))
                _add_crossed_bush_spray(bm, p, Vector((math.cos(az) * 0.4, math.sin(az) * 0.4, 0.85)),
                                        h * 0.52, col_l, uv_l, 0, 1, 0.55, 0.72, rng, n_cards=2 if lod == 0 else 1, segs_v=segs, mat_idx=1)

    elif species == "terracotta_planter":
        # Mesopotamischer Tonkuebel / Tempelschale (Mat 0, Wind=0.0) + Zwergpalme / Oliven-Baeumchen / Zierfarn (Mat 1)
        is_bowl = (idx >= 9)
        pot_h = (0.30 if is_bowl else 0.54) * rng.uniform(0.88, 1.15)
        pot_r = (0.42 if is_bowl else 0.30) * rng.uniform(0.90, 1.12)
        p_sides = {0: 14, 1: 8, 2: 6, 3: 5}[lod]
        p_rings = 4 if lod == 0 else (3 if lod == 1 else 2)
        soil_z = _add_vessel(bm, pot_r, pot_h, 0.035, 0.0, p_sides, p_rings, col_l, uv_l,
                             0, 3, 2 if idx % 2 == 0 else 3, 3, 1, 3, mat_idx=0, has_lapis=True)
        # Pflanzeninhalt nach Untertyp: 0..4 Zwergpalme, 5..8 Oliven-Krone, 9..12 Zierfarn/Lilie
        if idx <= 4:
            cc_p, cr_p = 2, 0
            crown_h = rng.uniform(0.75, 1.15)
        elif idx <= 8:
            cc_p, cr_p = 2, 0
            crown_h = rng.uniform(0.85, 1.25)
        else:
            cc_p, cr_p = 3, 0
            crown_h = rng.uniform(0.55, 0.85)
        if lod == 3:
            _add_card(bm, Vector((0, 0, soil_z)), Vector((0, 0, 1)), Vector((1, 0, 0)),
                      pot_r * 2.2, crown_h, col_l, uv_l, cc_p, cr_p, 0.1, 0.85, 0.4, segs_v=1, mat_idx=1)
            return
        n_fronds = {0: 7, 1: 4, 2: 2}[lod]
        segs = 2 if lod == 0 else 1
        if idx >= 5 and idx <= 8:
            # Kleines verholztes Olivenstaemmchen im Kuebel
            _add_wood_branch(bm, [Vector((0, 0, soil_z - 0.02)), Vector((0.02, 0, soil_z + crown_h * 0.48))],
                             0.042, 0.022, 5 if lod == 0 else 4, col_l, uv_l, 3, 2, pot_h + crown_h, 0.25, mat_idx=0)
            hub = Vector((0.02, 0, soil_z + crown_h * 0.48))
        else:
            hub = Vector((0.0, 0.0, soil_z))
        for fi in range(n_fronds):
            az = 2.0 * math.pi * fi / n_fronds + rng.uniform(-0.2, 0.2)
            tilt = 0.72 if idx <= 4 or idx >= 9 else 0.55
            ax = Vector((math.cos(az) * tilt, math.sin(az) * tilt, 0.78)).normalized()
            sd = Vector((-math.sin(az), math.cos(az), 0.1)).normalized()
            _add_card(bm, hub, ax, sd, pot_r * 1.45, crown_h * rng.uniform(0.78, 1.02),
                      col_l, uv_l, cc_p, cr_p, 0.05, 0.96, rng.random(), ao_base=0.60, ao_tip=0.98, bend=0.18, segs_v=segs, mat_idx=1)

    elif species == "lotus_cyperus":
        # 0..6 schwimmende Tempel-Lotus-Cluster (Blaetter flach + Blueten), 7..12 Garten-Zypergras (+ optional Travertin-Beckenring)
        is_lotus = (idx <= 6)
        segs = 2 if lod == 0 else 1
        if is_lotus:
            n_pads = {0: 11, 1: 5, 2: 2, 3: 1}[lod]
            for pi in range(n_pads):
                az = 2.0 * math.pi * pi / max(1, n_pads) + rng.uniform(-0.25, 0.25)
                dist_p = 0.08 if pi == 0 else rng.uniform(0.24, 0.60)
                pad_c = Vector((math.cos(az) * dist_p, math.sin(az) * dist_p, 0.015 + pi * 0.004))
                r_p = rng.uniform(0.18, 0.30)
                _add_card(bm, pad_c - Vector((0, r_p, 0)), Vector((0, 1, 0.03)).normalized(), Vector((1, 0, 0)),
                          r_p * 2.0, r_p * 2.0, col_l, uv_l, 0, 2, 0.05, 0.12, rng.random(), ao_base=0.72, ao_tip=0.92, bend=0.02, segs_v=2 if lod == 0 else 1, mat_idx=1)
            n_fl = {0: 8, 1: 3, 2: 2, 3: 1}[lod]
            for fi in range(n_fl):
                az = fi * 0.92 + rng.uniform(-0.25, 0.25)
                dist_f = rng.uniform(0.10, 0.42)
                fb = Vector((math.cos(az) * dist_f, math.sin(az) * dist_f, 0.02))
                fh = rng.uniform(0.18, 0.34)
                _add_crossed_bush_spray(bm, fb + Vector((0, 0, fh * 0.55)), Vector((0, 0, 1)), 0.26, col_l, uv_l, 1, 2, 0.45, 0.92, rng,
                                        n_cards=3 if lod == 0 else 1, segs_v=1, mat_idx=1)
        else:
            # Zypergras-Faecher im flachen Travertin-Becken (idx % 2 == 0) oder frei
            base_z = 0.0
            if idx % 2 == 0:
                base_z = _add_vessel(bm, 0.36, 0.22, 0.03, 0.0, {0: 12, 1: 8, 2: 6, 3: 4}[lod], 2,
                                     col_l, uv_l, 3, 3, 2, 3, 1, 3, mat_idx=0, has_lapis=True)
            ch = rng.uniform(0.62, 1.05)
            n_c = {0: 12, 1: 5, 2: 3, 3: 1}[lod]
            for ci in range(n_c):
                az = 2.0 * math.pi * ci / n_c + rng.uniform(-0.25, 0.25)
                b = Vector((math.cos(az) * 0.08, math.sin(az) * 0.08, base_z))
                ax = Vector((math.cos(az) * 0.18, math.sin(az) * 0.18, 1.0)).normalized()
                sd = Vector((-math.sin(az), math.cos(az), 0.0)).normalized()
                _add_card(bm, b, ax, sd, 0.48, ch * rng.uniform(0.82, 1.06), col_l, uv_l, 2, 2,
                          0.05, 0.96, rng.random(), ao_base=0.62, ao_tip=0.98, bend=0.10, segs_v=segs, mat_idx=1)
                if lod == 0:
                    sd2 = (sd.cross(ax)).normalized()
                    _add_card(bm, b, ax, sd2, 0.44, ch * rng.uniform(0.78, 1.00), col_l, uv_l, 2, 2,
                              0.05, 0.96, rng.random(), ao_base=0.62, ao_tip=0.98, bend=0.08, segs_v=2, mat_idx=1)


# ==============================================================================
# 4. MATERIALIEN & PAKET-EXPORT ÜBER export_arche_glb.py
# ==============================================================================

def _create_package_materials(tex_dir, prefix, has_opaque_slot, opaque_name, fol_name):
    bc_img = bpy.data.images.load(os.path.join(tex_dir, f"{prefix}_baseColor.png"), check_existing=True)
    bc_img.colorspace_settings.name = "sRGB"
    nm_img = bpy.data.images.load(os.path.join(tex_dir, f"{prefix}_normal.png"), check_existing=True)
    nm_img.colorspace_settings.name = "Non-Color"
    orm_img = bpy.data.images.load(os.path.join(tex_dir, f"{prefix}_orm.png"), check_existing=True)
    orm_img.colorspace_settings.name = "Non-Color"

    def _build_pbr_mat(mat_name, is_cutout):
        m = bpy.data.materials.new(name=mat_name)
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

        t_bc = nt.nodes.new("ShaderNodeTexImage"); t_bc.image = bc_img
        t_nm = nt.nodes.new("ShaderNodeTexImage"); t_nm.image = nm_img
        nmap = nt.nodes.new("ShaderNodeNormalMap")
        t_or = nt.nodes.new("ShaderNodeTexImage"); t_or.image = orm_img
        sep = nt.nodes.new("ShaderNodeSeparateColor" if hasattr(bpy.types, "ShaderNodeSeparateColor") else "ShaderNodeSeparateRGB")

        nt.links.new(t_bc.outputs["Color"], bsdf.inputs["Base Color"])
        nt.links.new(t_nm.outputs["Color"], nmap.inputs["Color"])
        nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
        nt.links.new(t_or.outputs["Color"], sep.inputs[0])
        nt.links.new(sep.outputs[1], bsdf.inputs["Roughness"])
        bsdf.inputs["Metallic"].default_value = 0.0

        if is_cutout:
            nt.links.new(t_bc.outputs["Alpha"], bsdf.inputs["Alpha"])
            if hasattr(m, "alpha_threshold"):
                m.alpha_threshold = 0.38
            if hasattr(m, "blend_method"):
                m.blend_method = "CLIP"
            if hasattr(m, "use_backface_culling"):
                m.use_backface_culling = False
        else:
            if hasattr(m, "blend_method"):
                m.blend_method = "OPAQUE"
        return m

    mats = []
    if has_opaque_slot:
        mats.append(_build_pbr_mat(opaque_name, False))
    mats.append(_build_pbr_mat(fol_name, True))
    return mats


def _link_object(scene, name, bm, mats):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for m in mats:
        mesh.materials.append(m)
    if "Col_Wind" in mesh.color_attributes:
        mesh.color_attributes.active_color = mesh.color_attributes["Col_Wind"]
        mesh.color_attributes.render_color_index = mesh.color_attributes.find("Col_Wind")
    obj = bpy.data.objects.new(name, mesh)
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)
    scene.collection.objects.link(obj)
    tri_cnt = sum(max(1, len(p.vertices) - 2) for p in mesh.polygons)
    return obj, tri_cnt


PACKAGE_SPECS = [
    {
        "slot": "shrubs_oriental",
        "atlas": "understory_crops_atlas",
        "has_opaque": True,
        "opaque_mat": "UnderstoryWood",
        "fol_mat": "UnderstoryFoliage",
        "builder": _build_shrub_bm,
        "species": [("thornbush", 12), ("tamarisk", 12), ("oleander", 12), ("broom", 12), ("juniper", 12)],
        "sss": [[0.32, 0.56, 0.18], 0.46],
        "desc": "5 vorderorientalische Wildstraucharten x 12 Varianten x 4 LODs",
    },
    {
        "slot": "grass_and_reeds",
        "atlas": "understory_crops_atlas",
        "has_opaque": False,
        "opaque_mat": None,
        "fol_mat": "UnderstoryGrassFoliage",
        "builder": _build_grass_reed_bm,
        "species": [("steppe_grass", 14), ("tall_grass", 14), ("euphrates_reed", 14)],
        "sss": [[0.42, 0.62, 0.16], 0.58],
        "desc": "Steppen-Bueschelgras, Hochgras & Euphrat-Schilf/Papyrus (3 x 14 = 42 Var x 4 LODs)",
    },
    {
        "slot": "crops_mesopotamia",
        "atlas": "understory_crops_atlas",
        "has_opaque": True,
        "opaque_mat": "CropsVineWood",
        "fol_mat": "CropsFoliage",
        "builder": _build_crop_bm,
        "species": [("emmer_wheat", 12), ("barley", 12), ("lentil_chickpea", 12), ("flax", 12), ("grapevine", 12)],
        "sss": [[0.48, 0.60, 0.18], 0.52],
        "desc": "5 mesopotamische Kulturpflanzen x 12 Varianten x 4 LODs",
    },
    {
        "slot": "ornamental_gardens",
        "atlas": "ornamental_garden_atlas",
        "has_opaque": True,
        "opaque_mat": "OrnamentalTerracottaWood",
        "fol_mat": "OrnamentalFoliage",
        "builder": _build_ornamental_bm,
        "species": [("pomegranate_ornamental", 13), ("myrtle_lily", 13), ("terracotta_planter", 13), ("lotus_cyperus", 13)],
        "sss": [[0.38, 0.60, 0.22], 0.50],
        "desc": "Granatapfel-Zierbaeume, Tempel-Myrte/Lilien, Terrakotta-Kuebel & Lotus/Zypergras (4 x 13 = 52 Var x 4 LODs)",
    },
]


def build_all_packages(root):
    tex_dir = os.path.join(root, "assets", "textures")
    glb_dir = os.path.join(root, "assets", "glb", "botany")
    blend_dir = os.path.join(root, "assets", "blend", "botany")
    os.makedirs(glb_dir, exist_ok=True)
    os.makedirs(blend_dir, exist_ok=True)

    summary = {}
    showcase_picks = []  # [(blend_path, obj_name, label)]

    for p_idx, pkg in enumerate(PACKAGE_SPECS):
        t0 = time.time()
        slot = pkg["slot"]
        scene = clear_scene()
        mats = _create_package_materials(tex_dir, pkg["atlas"], pkg["has_opaque"], pkg["opaque_mat"], pkg["fol_mat"])
        objs = []
        lod_tris = {0: [], 1: [], 2: [], 3: []}
        total_vars = 0

        for sp_idx, (sp_name, var_cnt) in enumerate(pkg["species"]):
            for vi in range(var_cnt):
                total_vars += 1
                seed = (p_idx + 1) * 50000 + (sp_idx + 1) * 1000 + vi * 79
                base_n = f"{sp_name}_mature_{vi + 1:02d}"
                for lod_i in (0, 1, 2, 3):
                    bm = bmesh.new()
                    pkg["builder"](bm, sp_name, vi, seed, lod_i)
                    obj, tc = _link_object(scene, f"{base_n}_LOD{lod_i}", bm, mats)
                    objs.append(obj)
                    lod_tris[lod_i].append(tc)
                if vi == 0:
                    showcase_picks.append((os.path.join(blend_dir, f"{slot}.blend"), f"{base_n}_LOD0", sp_name))
                if sp_name in ("pomegranate_ornamental", "terracotta_planter", "lotus_cyperus") and vi in (8, 10):
                    showcase_picks.append((os.path.join(blend_dir, f"{slot}.blend"), f"{base_n}_LOD0", f"{sp_name}_{vi + 1:02d}"))

        blend_path = os.path.join(blend_dir, f"{slot}.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)

        # Leichte Platzhalter-Nodes fuers kompakte .glb (Shared Atlas wird im WebGL-Loader einmalig gebunden!)
        for m in mats:
            if m.node_tree:
                nt = m.node_tree
                nt.nodes.clear()
                o_n = nt.nodes.new("ShaderNodeOutputMaterial")
                b_n = nt.nodes.new("ShaderNodeBsdfPrincipled")
                is_fol = (m.name == pkg["fol_mat"])
                b_n.inputs["Base Color"].default_value = (0.24, 0.38, 0.16, 1.0) if is_fol else (0.42, 0.25, 0.16, 1.0)
                b_n.inputs["Roughness"].default_value = 0.72
                nt.links.new(b_n.outputs["BSDF"], o_n.inputs["Surface"])

        glb_path = os.path.join(glb_dir, f"{slot}.glb")
        export_arche_glb.export_glb(objs, glb_path, use_draco=False)
        size_kb = os.path.getsize(glb_path) / 1024.0
        dt = time.time() - t0
        summary[slot] = {
            "variants": total_vars,
            "species": [s for s, _ in pkg["species"]],
            "atlas": pkg["atlas"],
            "sss": pkg["sss"],
            "desc": pkg["desc"],
            "lod0": (min(lod_tris[0]), max(lod_tris[0])),
            "lod1": (min(lod_tris[1]), max(lod_tris[1])),
            "lod2": (min(lod_tris[2]), max(lod_tris[2])),
            "lod3": (min(lod_tris[3]), max(lod_tris[3])),
            "glb_kb": round(size_kb, 1),
            "time_s": round(dt, 2),
        }
        print(
            f"[PACK] {slot:20s}: {total_vars:2d} Var | "
            f"L0 {lod_tris[0] and min(lod_tris[0])}-{max(lod_tris[0])} | "
            f"L1 {min(lod_tris[1])}-{max(lod_tris[1])} | "
            f"L2 {min(lod_tris[2])}-{max(lod_tris[2])} | "
            f"L3 {min(lod_tris[3])}-{max(lod_tris[3])} Tris | {size_kb:.1f} KB ({dt:.2f}s)",
            flush=True,
        )
    return summary, showcase_picks


def update_manifest(root, summary):
    mpath = os.path.join(root, "assets", "manifest.json")
    with open(mpath, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    items = manifest.setdefault("categories", {}).setdefault("botany", {}).setdefault("items", {})
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for slot, info in summary.items():
        ax = info["atlas"]
        items[slot] = {
            "enabled": True,
            "url": f"assets/glb/botany/{slot}.glb",
            "blend": f"assets/blend/botany/{slot}.blend",
            "category": "botany",
            "description": info["desc"],
            "speciesList": info["species"],
            "instanced": True,
            "wind": True,
            "variantsCount": info["variants"],
            "lods": ["LOD0", "LOD1", "LOD2", "LOD3"],
            "lod0TrisRange": list(info["lod0"]),
            "lod1TrisRange": list(info["lod1"]),
            "lod2TrisRange": list(info["lod2"]),
            "lod3TrisRange": list(info["lod3"]),
            "hasRequiredTag": True,
            "sssColor": info["sss"][0],
            "sssStrength": info["sss"][1],
            "sharedTextures": {
                "baseColor": f"assets/textures/{ax}_baseColor.png",
                "normal": f"assets/textures/{ax}_normal.png",
                "orm": f"assets/textures/{ax}_orm.png",
                "thickness": f"assets/textures/{ax}_thickness.png",
            },
            "preview": "assets/previews/understory_showcase.png",
            "glbSizeKB": info["glb_kb"],
            "exportedAt": now_str,
        }
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"[MANIFEST] assets/manifest.json fuer {list(summary.keys())} aktualisiert.", flush=True)


def render_showcase(root, showcase_picks):
    t0 = time.time()
    print("[SHOWCASE] Rendere assets/previews/understory_showcase.png...", flush=True)
    scene = clear_scene()
    dev = setup_cycles(scene, samples=32)
    if hasattr(scene, "cycles"):
        scene.cycles.transparent_max_bounces = 36
    vts = [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items]
    scene.view_settings.view_transform = "AgX" if "AgX" in vts else "Filmic"
    if hasattr(scene.cycles, "use_denoising"):
        scene.cycles.use_denoising = True

    # Warmer Kalksand-Boden (36x36 m, sattes Mesopotamien-Ocker fuer hohen Kontrast zu weissen Lilien & blauem Flachs)
    bpy.ops.mesh.primitive_plane_add(size=36.0, location=(0.0, 0.0, 0.0))
    ground = bpy.context.active_object
    g_mat = bpy.data.materials.new("ShowcaseSand")
    g_mat.use_nodes = True
    g_bsdf = g_mat.node_tree.nodes.get("Principled BSDF")
    if g_bsdf:
        g_bsdf.inputs["Base Color"].default_value = (0.34, 0.27, 0.17, 1.0)
        g_bsdf.inputs["Roughness"].default_value = 0.90
    ground.data.materials.append(g_mat)

    bpy.ops.mesh.primitive_plane_add(size=4.6, location=(3.6, -4.6, 0.004))
    pool = bpy.context.active_object
    p_mat = bpy.data.materials.new("ShowcasePoolWater")
    p_mat.use_nodes = True
    p_bsdf = p_mat.node_tree.nodes.get("Principled BSDF")
    if p_bsdf:
        p_bsdf.inputs["Base Color"].default_value = (0.06, 0.24, 0.34, 1.0)
        p_bsdf.inputs["Roughness"].default_value = 0.08
    pool.data.materials.append(p_mat)

    # Gruppiere Objekte nach .blend und lade genau 1 repraesentatives LOD0-Asset pro Art
    by_blend = {}
    for bp, oname, label in showcase_picks:
        by_blend.setdefault(bp, []).append((oname, label))

    loaded_objs = []
    for bp, entries in by_blend.items():
        want_names = {on for on, _ in entries}
        with bpy.data.libraries.load(bp, link=False) as (data_from, data_to):
            data_to.objects = [n for n in data_from.objects if n in want_names]
        for obj in data_to.objects:
            if obj:
                scene.collection.objects.link(obj)
                loaded_objs.append(obj)

    obj_map = {o.name: o for o in loaded_objs}
    # 4 ordentliche Reihen (von hinten nach vorne):
    # Reihe 3 (hinten Y=+4.2): 5 Straeucher (thornbush, tamarisk, oleander, broom, juniper)
    # Reihe 2 (Y=+1.4): Graser/Schilf/Papyrus + Kulturpflanzen (emmer, barley, lentil, flax, grapevine)
    # Reihe 1 (vorne Y=-2.2): Zierbotanik & Terrakotta (pomegranate frei, pomegranate pot, myrtle_lily, planter_01, planter_09)
    # Reihe 0 (Pool Y=-4.6): Lotus & Zypergras
    placements = [
        # Hinten: Straeucher
        ("thornbush_mature_01_LOD0",     (-4.8, 3.8, 0.0)),
        ("tamarisk_mature_01_LOD0",      (-2.4, 3.8, 0.0)),
        ("oleander_mature_01_LOD0",      ( 0.0, 3.8, 0.0)),
        ("broom_mature_01_LOD0",         ( 2.4, 3.8, 0.0)),
        ("juniper_mature_01_LOD0",       ( 4.8, 3.8, 0.0)),
        # Mitte hinten: Graser & Schilf
        ("steppe_grass_mature_01_LOD0",  (-5.4, 1.4, 0.0)),
        ("tall_grass_mature_01_LOD0",    (-3.6, 1.4, 0.0)),
        ("euphrates_reed_mature_01_LOD0",(-1.8, 1.4, 0.0)),
        # Mitte vorne: Kulturpflanzen
        ("emmer_wheat_mature_01_LOD0",   ( 0.2, 1.4, 0.0)),
        ("barley_mature_01_LOD0",        ( 1.7, 1.4, 0.0)),
        ("lentil_chickpea_mature_01_LOD0",(3.1, 1.4, 0.0)),
        ("flax_mature_01_LOD0",          ( 4.4, 1.4, 0.0)),
        ("grapevine_mature_01_LOD0",     ( 5.8, 1.4, 0.0)),
        # Vorne: Tempel- & Zierpflanzen + Terrakotta
        ("pomegranate_ornamental_mature_01_LOD0", (-5.0, -2.0, 0.0)),
        ("pomegranate_ornamental_mature_09_LOD0", (-2.6, -2.0, 0.0)),
        ("myrtle_lily_mature_01_LOD0",            (-0.4, -2.0, 0.0)),
        ("terracotta_planter_mature_01_LOD0",     ( 1.8, -2.0, 0.0)),
        ("terracotta_planter_mature_09_LOD0",     ( 3.6, -2.0, 0.0)),
        ("terracotta_planter_mature_11_LOD0",     ( 5.2, -2.0, 0.0)),
        # Becken vorne rechts: Lotus & Zypergras
        ("lotus_cyperus_mature_01_LOD0",          ( 2.7, -4.4, 0.005)),
        ("lotus_cyperus_mature_11_LOD0",          ( 4.5, -4.4, 0.005)),
    ]
    for oname, pos in placements:
        ob = obj_map.get(oname)
        if ob:
            ob.location = pos

    # Warme mesopotamische Sonne + blauer Himmel (sauber belichtet ohne Ausbrennen)
    sun_d = bpy.data.lights.new("Sun", type="SUN")
    sun_d.energy = 2.4
    sun_d.angle = math.radians(1.5)
    sun_o = bpy.data.objects.new("Sun", sun_d)
    sun_o.rotation_euler = (math.radians(52.0), math.radians(12.0), math.radians(-38.0))
    scene.collection.objects.link(sun_o)

    w = bpy.data.worlds.new("SkyWorld")
    scene.world = w
    w.use_nodes = True
    nt_w = w.node_tree
    bg = nt_w.nodes.get("Background")
    sky = nt_w.nodes.new("ShaderNodeTexSky")
    sky_enums = [i.identifier for i in sky.bl_rna.properties["sky_type"].enum_items]
    sky.sky_type = "PREETHAM" if "PREETHAM" in sky_enums else sky_enums[0]
    nt_w.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.45

    cam_d = bpy.data.cameras.new("ShowcaseCam")
    cam_d.lens = 34.0
    cam_o = bpy.data.objects.new("ShowcaseCam", cam_d)
    cam_o.location = (0.3, -14.2, 5.2)
    cam_o.rotation_euler = (Vector((0.3, 0.2, 0.55)) - cam_o.location).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cam_o)
    scene.camera = cam_o

    prev_dir = os.path.join(root, "assets", "previews")
    os.makedirs(prev_dir, exist_ok=True)
    out_png = os.path.join(prev_dir, "understory_showcase.png")
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1200
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = out_png
    bpy.ops.render.render(write_still=True)
    print(f"[SHOWCASE] {out_png} gerendert auf {dev} in {time.time() - t0:.2f}s.", flush=True)
    return out_png


def main():
    t_total = time.time()
    tex_dir = os.path.join(ROOT_DIR, "assets", "textures")
    os.makedirs(tex_dir, exist_ok=True)

    # Schritt 1: Gemeinsame 1024x1024 Atlanten backen
    u_info = bake_1024_atlas("understory_crops_atlas", UNDERSTORY_CELLS, _build_atlas_cell_understory, tex_dir, size=1024)
    o_info = bake_1024_atlas("ornamental_garden_atlas", ORNAMENTAL_CELLS, _build_atlas_cell_ornamental, tex_dir, size=1024)
    print(f"[ATLAS] Beide 1024x1024-Setups abgeschlossen (Understory {u_info['time_s']:.2f}s, Ornamental {o_info['time_s']:.2f}s).", flush=True)

    # Schritt 2: 4 .glb-Pakete + .blend + manifest.json
    summary, showcase_picks = build_all_packages(ROOT_DIR)
    update_manifest(ROOT_DIR, summary)

    # Schritt 3: Showcase-Render
    render_showcase(ROOT_DIR, showcase_picks)
    print(f"[DONE] Gesamtlaufzeit Unterholz/Feld/Zierbotanik: {time.time() - t_total:.2f}s.", flush=True)


if __name__ == "__main__":
    main()
