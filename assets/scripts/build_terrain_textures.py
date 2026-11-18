"""
build_terrain_textures.py — Prozeduraler Blender-Cycles-Terrain-Baker (Set A, Plaza & Set B)
===========================================================================================
Erzeugt nahtlos kachelnde PBR-Terrain-Textur-Atlanten (1024x1024, 2x2) + Plaza (512x512)
über 3D-Mikro-Displacement (4x4 m + periodischer Kachel-Schürze) und Cycles CUDA (GTX 1070
mit CPU-Fallback):
  - Set A (Mesopotamien): assets/textures/terrain_meso_atlas_{albedo,normal,orm}.png
  - Plaza (Ur-Schinar):   assets/textures/terrain_plaza_{albedo,normal,orm}.png
  - Set B (Ararat):       assets/textures/terrain_ararat_atlas_{albedo,normal,orm}.png
  - Preview:              assets/previews/terrain_textures_showcase.png

Ausführung:
  blender --background --python assets/scripts/build_terrain_textures.py
"""

import os
import sys
import math
import time
import bpy
import bmesh
import numpy as np
from mathutils import Vector


TILE_SIZE = 512
ATLAS_SIZE = 1024
TILE_WORLD_M = 4.0
GRID_N = 192  # 192x192 (~73k Tris pro 4x4m Kachel + Schürze)


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
        scene.cycles.use_denoising = use_oidn
        if use_oidn:
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
# PERIODISCHE / NAHTLOSE NUMPY-HÖHENFELDER (f(0,v)==f(1,v) & f(u,0)==f(u,1))
# ==============================================================================

def _hash2(ix, iy, seed=0):
    n = (ix * 374761393 + iy * 668265263 + seed * 1442695041) & 0x7FFFFFFF
    n = (n ^ (n >> 13)) * 1274126177
    n = n & 0x7FFFFFFF
    return (n & 0xFFFFFF) / float(0x1000000)


def periodic_value_noise(u, v, period, seed=0):
    """2D periodisches Value-Noise auf [0,1)^2 mit glatter Quintic-Interpolation."""
    px = np.mod(u, 1.0) * period
    py = np.mod(v, 1.0) * period
    x0 = np.floor(px).astype(np.int64) % period
    y0 = np.floor(py).astype(np.int64) % period
    x1 = (x0 + 1) % period
    y1 = (y0 + 1) % period
    fx = px - np.floor(px)
    fy = py - np.floor(py)
    wx = fx * fx * fx * (fx * (fx * 6.0 - 15.0) + 10.0)
    wy = fy * fy * fy * (fy * (fy * 6.0 - 15.0) + 10.0)

    v00 = _hash2(x0, y0, seed)
    v10 = _hash2(x1, y0, seed)
    v01 = _hash2(x0, y1, seed)
    v11 = _hash2(x1, y1, seed)
    return (v00 * (1.0 - wx) + v10 * wx) * (1.0 - wy) + (v01 * (1.0 - wx) + v11 * wx) * wy


def periodic_fbm(u, v, base_period=4, octaves=4, seed=11):
    val = np.zeros_like(u, dtype=np.float64)
    amp = 0.5
    norm = 0.0
    per = base_period
    for o in range(octaves):
        val += amp * periodic_value_noise(u, v, per, seed + o * 97)
        norm += amp
        amp *= 0.5
        per *= 2
    return val / max(1e-8, norm)


def periodic_voronoi(u, v, cells=8, seed=101, jitter=0.82):
    """2D periodisches Worley/Voronoi: liefert (F1, F2 - F1, cell_id)."""
    px = np.mod(u, 1.0) * cells
    py = np.mod(v, 1.0) * cells
    ix = np.floor(px).astype(np.int64)
    iy = np.floor(py).astype(np.int64)
    fx = px - ix
    fy = py - iy

    f1 = np.full_like(px, 1e9, dtype=np.float64)
    f2 = np.full_like(px, 1e9, dtype=np.float64)
    cid = np.zeros_like(px, dtype=np.float64)

    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            cx = (ix + dx) % cells
            cy = (iy + dy) % cells
            ox = 0.5 + (_hash2(cx, cy, seed) - 0.5) * jitter
            oy = 0.5 + (_hash2(cx, cy, seed + 53) - 0.5) * jitter
            ddx = (dx + ox) - fx
            ddy = (dy + oy) - fy
            d = np.sqrt(ddx * ddx + ddy * ddy)
            mask1 = d < f1
            f2 = np.where(mask1, f1, np.minimum(f2, d))
            f1 = np.where(mask1, d, f1)
            cid = np.where(mask1, _hash2(cx, cy, seed + 199), cid)
    return f1, np.maximum(0.0, f2 - f1), cid


def eval_tile_height_and_masks(tile_id, u, v):
    """
    Liefert (height_m, mask_a, mask_b, mask_c) für jede Kachel, 100% periodisch in u,v!
    mask_a/b/c steuern Poren, Risse, Kiesel, Stroh, Moos, Furchen-Pfützen etc.
    """
    if tile_id == "meso_plowed":
        # 6 leicht wellige Ackerfurchen pro 4m-Kachel
        warp = (periodic_fbm(u, v, 3, 3, 17) - 0.5) * 0.14
        phase = 2.0 * math.pi * (6.0 * u + warp)
        furrow = 0.5 - 0.5 * np.cos(phase)  # 0 in Rille, 1 auf Kamm
        furrow_sharp = np.power(furrow, 0.78)
        clods = periodic_fbm(u, v, 12, 4, 41)
        micro = periodic_fbm(u, v, 32, 3, 83)
        pebbles = np.clip(1.0 - periodic_voronoi(u, v, 18, 123)[0] * 3.8, 0.0, 1.0)
        straw_n = periodic_value_noise(u * 2.0 + v * 0.5, v * 3.0 - u * 0.5, 28, 211)
        straw = np.clip((straw_n - 0.80) * 5.0, 0.0, 1.0) * np.clip(furrow + 0.3, 0.0, 1.0)
        h = furrow_sharp * 0.095 + (clods - 0.5) * 0.032 + (micro - 0.5) * 0.012 + pebbles * 0.010
        trough_mask = np.clip(1.0 - furrow_sharp * 1.45, 0.0, 1.0)
        return h, trough_mask, pebbles, straw

    if tile_id == "meso_steppe":
        # Rissige, sonnengebackene Alluvial-Steppe + Trockengras-Büschel
        wu = u + (periodic_fbm(u, v, 4, 3, 31) - 0.5) * 0.04
        wv = v + (periodic_fbm(u, v, 4, 3, 73) - 0.5) * 0.04
        f1, edge, cid = periodic_voronoi(wu, wv, 9, 307, jitter=0.88)
        crack = np.clip(1.0 - edge / 0.085, 0.0, 1.0)
        plate_curl = np.clip(edge * 1.8, 0.0, 1.0) * 0.012
        undul = (periodic_fbm(u, v, 3, 3, 19) - 0.5) * 0.035
        grain = (periodic_fbm(u, v, 24, 3, 99) - 0.5) * 0.010
        root_tuft = np.clip((periodic_fbm(u, v, 14, 3, 419) - 0.60) * 2.6, 0.0, 1.0) * (1.0 - crack)
        h = undul + plate_curl + grain - crack * 0.034 + root_tuft * 0.014
        return h, crack, root_tuft, cid

    if tile_id == "meso_shipyard":
        # Hart getrampelter Werftboden mit Schleifspuren, Steinchen & Holzspänen
        ruts = np.sin(2.0 * math.pi * (3.0 * u + (periodic_fbm(u, v, 2, 2, 55) - 0.5) * 0.08)) * 0.5 + 0.5
        compacted = (periodic_fbm(u, v, 6, 4, 131) - 0.5) * 0.022
        pebbles = np.clip(1.0 - periodic_voronoi(u, v, 20, 509)[0] * 4.2, 0.0, 1.0)
        chips_v = periodic_voronoi(u * 1.5, v * 0.75, 22, 613)[0]
        woodchips = np.clip(1.0 - chips_v * 4.8, 0.0, 1.0) * (periodic_value_noise(u, v, 16, 617) > 0.52)
        h = (ruts - 0.5) * 0.024 + compacted + pebbles * 0.012 + woodchips * 0.008
        return h, 1.0 - ruts, pebbles, woodchips

    if tile_id == "meso_riverbank":
        # Euphrat-Uferschlamm & natürlich geformte, unterschiedlich große Flusskiesel
        mud_undul = (periodic_fbm(u, v, 4, 4, 701) - 0.5) * 0.036
        wu = u + (periodic_fbm(u, v, 7, 3, 719) - 0.5) * 0.055
        wv = v + (periodic_fbm(u, v, 7, 3, 727) - 0.5) * 0.055
        f1_a, _, cid_a = periodic_voronoi(wu, wv, 11, 733, jitter=0.90)
        f1_b, _, cid_b = periodic_voronoi(wu + 0.17, wv - 0.13, 21, 743, jitter=0.88)
        dom_a = np.clip(1.0 - (f1_a / 0.34) ** 2, 0.0, 1.0) * (cid_a > 0.48)
        dom_b = np.clip(1.0 - (f1_b / 0.36) ** 2, 0.0, 1.0) * (cid_b > 0.45)
        pebble_mask = np.maximum(dom_a, dom_b * 0.65)
        silt_ripples = np.sin(2.0 * math.pi * (8.0 * v + periodic_fbm(u, v, 4, 2, 751) * 1.2)) * 0.005
        h = mud_undul + silt_ripples + pebble_mask * 0.022
        wet_pool = np.clip(1.0 - (h - np.min(h)) / max(1e-5, np.ptp(h)) * 1.35, 0.0, 1.0)
        return h, pebble_mask, wet_pool, cid_a

    if tile_id == "plaza_stone":
        # Verwittertes Ur-Schinar-Steinplatten-/Lehmziegel-Pflaster (4x4 versetzte Platten)
        rows = 4
        cols = 4
        vy = np.mod(v, 1.0) * rows
        row_idx = np.floor(vy).astype(np.int64) % rows
        ux = np.mod(u + (row_idx % 2) * 0.5 / cols, 1.0) * cols
        col_idx = np.floor(ux).astype(np.int64) % cols
        fu = ux - np.floor(ux)
        fv = vy - np.floor(vy)
        # Verzogene Fugen für Handarbeit-Look
        warp_j = (periodic_fbm(u, v, 8, 3, 809) - 0.5) * 0.035
        du = np.minimum(fu, 1.0 - fu) + warp_j
        dv = np.minimum(fv, 1.0 - fv) + warp_j
        edge_d = np.minimum(du, dv)
        joint = np.clip(1.0 - edge_d / 0.065, 0.0, 1.0)
        bevel = np.clip((edge_d - 0.025) / 0.075, 0.0, 1.0)
        tile_var = (_hash2(col_idx, row_idx, 823) - 0.5) * 0.014
        wear = (periodic_fbm(u, v, 10, 4, 853) - 0.5) * 0.016
        f1, _, _ = periodic_voronoi(u, v, 12, 877)
        pit = np.clip((f1 - 0.35) * 2.0, 0.0, 1.0) * 0.008
        h = bevel * 0.032 + tile_var + wear - joint * 0.026 - pit
        return h, joint, _hash2(col_idx, row_idx, 887), wear + 0.5

    if tile_id == "ararat_basalt":
        # Schroffer Vulkanbasalt mit Schichten & Frostsprengungs-Klüften
        strata_u = u + (periodic_fbm(u, v, 4, 3, 907) - 0.5) * 0.12
        strata = np.sin(2.0 * math.pi * 5.0 * strata_u) * 0.35 + np.sin(2.0 * math.pi * 11.0 * strata_u + 1.2) * 0.20
        f1, edge, cid = periodic_voronoi(u + strata * 0.02, v, 7, 941, jitter=0.90)
        crevice = np.clip(1.0 - edge / 0.09, 0.0, 1.0)
        crag = periodic_fbm(u, v, 6, 5, 977)
        h = strata * 0.032 + (crag - 0.5) * 0.095 - crevice * 0.052 + (cid - 0.5) * 0.022
        return h, crevice, np.clip(strata * 0.5 + 0.5, 0.0, 1.0), crag

    if tile_id == "ararat_scree":
        # Post-Flut-Geröll & nasstrüber Basaltschlamm (kantig-unregelmäßige Basaltbrocken in 2 Größen)
        mud = (periodic_fbm(u, v, 5, 4, 1013) - 0.5) * 0.032
        wu = u + (periodic_fbm(u, v, 8, 3, 1021) - 0.5) * 0.065
        wv = v + (periodic_fbm(u, v, 8, 3, 1031) - 0.5) * 0.065
        f1_a, edge_a, cid_a = periodic_voronoi(wu, wv, 9, 1039, jitter=0.92)
        f1_b, _, cid_b = periodic_voronoi(wu + 0.23, wv + 0.11, 19, 1051, jitter=0.90)
        rock_a = np.clip(1.0 - f1_a * 2.25, 0.0, 1.0) * (cid_a > 0.40) * (0.7 + 0.6 * periodic_fbm(u, v, 14, 2, 1071))
        rock_b = np.clip(1.0 - f1_b * 2.55, 0.0, 1.0) * (cid_b > 0.42) * 0.60
        stone_sharp = np.clip(np.maximum(rock_a, rock_b), 0.0, 1.0)
        gravel = np.clip(1.0 - periodic_voronoi(u, v, 28, 1061)[0] * 3.8, 0.0, 1.0) * 0.30
        h = mud + stone_sharp * 0.052 + gravel * 0.015
        wet_mud = np.clip(1.0 - stone_sharp * 1.35, 0.0, 1.0)
        return h, stone_sharp, wet_mud, cid_a

    if tile_id == "ararat_moss":
        # Alpiner Pionierboden mit Moospolstern & Flechten
        soil = (periodic_fbm(u, v, 6, 4, 1103) - 0.5) * 0.048
        moss_base = periodic_fbm(u, v, 5, 4, 1151)
        moss_mask = np.clip((moss_base - 0.44) * 3.2, 0.0, 1.0)
        moss_bumps = periodic_fbm(u, v, 24, 3, 1187) * moss_mask
        lichen = np.clip((periodic_voronoi(u, v, 14, 1201)[0] < 0.22) * (moss_base > 0.38) * (1.0 - moss_mask), 0.0, 1.0)
        h = soil + moss_mask * 0.028 + moss_bumps * 0.016 + lichen * 0.008
        return h, moss_mask, lichen, soil + 0.5

    if tile_id == "ararat_snow":
        # Firn & Hochgebirgs-Schnee mit Windrippeln (Sastrugi)
        warp = (periodic_fbm(u, v, 3, 3, 1301) - 0.5) * 0.18
        sastrugi = np.power(0.5 + 0.5 * np.sin(2.0 * math.pi * (5.0 * u + 1.0 * v + warp)), 1.6)
        drift = (periodic_fbm(u, v, 4, 4, 1327) - 0.5) * 0.036
        grain = (periodic_fbm(u, v, 36, 2, 1361) - 0.5) * 0.007
        h = sastrugi * 0.044 + drift + grain
        return h, sastrugi, grain + 0.5, drift + 0.5

    raise ValueError(f"Unbekannte tile_id: {tile_id}")


# ==============================================================================
# BLENDER MESH-AUFBAU (4x4m KACHEL + PERIODISCHE SCHÜRZE FÜR NAHTLOSES AO/NORMAL)
# ==============================================================================

def build_displaced_tile_mesh(name, tile_id, grid_n=GRID_N, tile_m=TILE_WORLD_M, pad_cells=28):
    """
    Erzeugt High-Poly-Plane über [-pad..grid_n+pad]^2 mit exakter periodischer Höhe
    aus eval_tile_height_and_masks, sowie Vertex-Color-Layer 'TerrainMasks' (R,G,B).
    Nur der innere Bereich [0..tile_m]^2 wird auf das Active-Plane gebacken; die äußere
    Schürze garantiert identische Normals & AO über alle Kachelränder!
    """
    total_n = grid_n + 2 * pad_cells
    idx_1d = np.arange(total_n + 1, dtype=np.float64) - pad_cells
    u_1d = idx_1d / float(grid_n)
    uu, vv = np.meshgrid(u_1d, u_1d, indexing="xy")

    h, m_a, m_b, m_c = eval_tile_height_and_masks(tile_id, uu, vv)
    xx = u_1d * tile_m
    xg, yg = np.meshgrid(xx, xx, indexing="xy")

    mesh = bpy.data.meshes.new(name + "_Mesh")
    verts = np.column_stack([xg.ravel(), yg.ravel(), h.ravel()]).tolist()

    stride = total_n + 1
    i0 = np.arange(total_n, dtype=np.int64)
    j0 = np.arange(total_n, dtype=np.int64)
    ii, jj = np.meshgrid(i0, j0, indexing="xy")
    v00 = (jj * stride + ii).ravel()
    v10 = v00 + 1
    v11 = v00 + stride + 1
    v01 = v00 + stride
    faces = np.column_stack([v00, v10, v11, v01]).tolist()

    mesh.from_pydata(verts, [], faces)
    mesh.update()

    # Smooth shading für saubere Normal-Interpolation
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))

    # Vertex Color Attribute 'TerrainMasks' (loop-weise aus Grid-Werten)
    col_attr = mesh.color_attributes.new(name="TerrainMasks", type="FLOAT_COLOR", domain="CORNER")
    ma_flat = np.clip(m_a.ravel(), 0.0, 1.0)
    mb_flat = np.clip(m_b.ravel(), 0.0, 1.0)
    mc_flat = np.clip(m_c.ravel(), 0.0, 1.0)
    loop_v = np.empty(len(mesh.loops), dtype=np.int64)
    mesh.loops.foreach_get("vertex_index", loop_v)
    rgba = np.ones((len(mesh.loops), 4), dtype=np.float32)
    rgba[:, 0] = ma_flat[loop_v]
    rgba[:, 1] = mb_flat[loop_v]
    rgba[:, 2] = mc_flat[loop_v]
    col_attr.data.foreach_set("color", rgba.ravel())

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def build_bake_target_plane(name, tile_m=TILE_WORLD_M):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    v0 = bm.verts.new((0.0, 0.0, 0.0))
    v1 = bm.verts.new((tile_m, 0.0, 0.0))
    v2 = bm.verts.new((tile_m, tile_m, 0.0))
    v3 = bm.verts.new((0.0, tile_m, 0.0))
    f = bm.faces.new((v0, v1, v2, v3))
    uv_lay = bm.loops.layers.uv.new("UVMap")
    uvs = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    for loop, uv in zip(f.loops, uvs):
        loop[uv_lay].uv = uv
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


# ==============================================================================
# PROZEDURALE SHADER (TOROIDAL-NAHTLOS + STRENG HDR [0.04..0.78])
# ==============================================================================

def _clamp_rgb(rgb, lo=0.04, hi=0.78):
    return (
        max(lo, min(hi, float(rgb[0]))),
        max(lo, min(hi, float(rgb[1]))),
        max(lo, min(hi, float(rgb[2]))),
    )


def _mix_rgba(nt, fac, col_a, col_b):
    node = nt.nodes.new("ShaderNodeMix")
    node.data_type = "RGBA"
    rgba_ins = [s for s in node.inputs if s.type == "RGBA"]
    rgba_outs = [s for s in node.outputs if s.type == "RGBA"]
    if isinstance(fac, (int, float)):
        node.inputs[0].default_value = float(fac)
    else:
        nt.links.new(fac, node.inputs[0])
    for sock, col in ((rgba_ins[0], col_a), (rgba_ins[1], col_b)):
        if isinstance(col, tuple):
            sock.default_value = col if len(col) == 4 else (*col, 1.0)
        else:
            nt.links.new(col, sock)
    return rgba_outs[0]


def _mix_float(nt, fac, a, b):
    node = nt.nodes.new("ShaderNodeMix")
    node.data_type = "FLOAT"
    if isinstance(fac, (int, float)):
        node.inputs[0].default_value = float(fac)
    else:
        nt.links.new(fac, node.inputs[0])
    if isinstance(a, (int, float)):
        node.inputs[2].default_value = float(a)
    else:
        nt.links.new(a, node.inputs[2])
    if isinstance(b, (int, float)):
        node.inputs[3].default_value = float(b)
    else:
        nt.links.new(b, node.inputs[3])
    return node.outputs[0]


def _add_torus_coords(nt, tile_m=TILE_WORLD_M):
    """Mappt Welt/Objekt (X,Y) auf einen 3D-Torus für 100% periodisches Blender-Noise."""
    geom = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geom.outputs["Position"], sep.inputs["Vector"])

    # theta = X * (2*pi / tile_m), phi = Y * (2*pi / tile_m)
    k = 2.0 * math.pi / tile_m
    mul_u = nt.nodes.new("ShaderNodeMath")
    mul_u.operation = "MULTIPLY"
    mul_u.inputs[1].default_value = k
    nt.links.new(sep.outputs["X"], mul_u.inputs[0])

    mul_v = nt.nodes.new("ShaderNodeMath")
    mul_v.operation = "MULTIPLY"
    mul_v.inputs[1].default_value = k
    nt.links.new(sep.outputs["Y"], mul_v.inputs[0])

    cos_u = nt.nodes.new("ShaderNodeMath"); cos_u.operation = "COSINE"; nt.links.new(mul_u.outputs[0], cos_u.inputs[0])
    sin_u = nt.nodes.new("ShaderNodeMath"); sin_u.operation = "SINE";   nt.links.new(mul_u.outputs[0], sin_u.inputs[0])
    cos_v = nt.nodes.new("ShaderNodeMath"); cos_v.operation = "COSINE"; nt.links.new(mul_v.outputs[0], cos_v.inputs[0])
    sin_v = nt.nodes.new("ShaderNodeMath"); sin_v.operation = "SINE";   nt.links.new(mul_v.outputs[0], sin_v.inputs[0])

    # R_major = 2.5, r_minor = 1.0 -> rad_xy = 2.5 + cos_v
    rad_xy = nt.nodes.new("ShaderNodeMath"); rad_xy.operation = "ADD"; rad_xy.inputs[1].default_value = 2.5
    nt.links.new(cos_v.outputs[0], rad_xy.inputs[0])

    tx = nt.nodes.new("ShaderNodeMath"); tx.operation = "MULTIPLY"
    nt.links.new(rad_xy.outputs[0], tx.inputs[0]); nt.links.new(cos_u.outputs[0], tx.inputs[1])

    ty = nt.nodes.new("ShaderNodeMath"); ty.operation = "MULTIPLY"
    nt.links.new(rad_xy.outputs[0], ty.inputs[0]); nt.links.new(sin_u.outputs[0], ty.inputs[1])

    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(tx.outputs[0], comb.inputs["X"])
    nt.links.new(ty.outputs[0], comb.inputs["Y"])
    nt.links.new(sin_v.outputs[0], comb.inputs["Z"])
    return comb.outputs["Vector"]


TILE_PALETTES = {
    # (base_lo, base_hi, detail_a, detail_b, rough_lo, rough_hi) — alles Linear HDR [0.04..0.78]!
    "meso_plowed":    ((0.14, 0.09, 0.055), (0.28, 0.19, 0.115), (0.075, 0.050, 0.032), (0.48, 0.37, 0.17), 0.30, 0.88),
    "meso_steppe":    ((0.26, 0.20, 0.12),  (0.42, 0.33, 0.21),  (0.11, 0.08, 0.05),    (0.36, 0.31, 0.15), 0.76, 0.94),
    "meso_shipyard":  ((0.24, 0.18, 0.12),  (0.36, 0.28, 0.19),  (0.16, 0.13, 0.10),    (0.46, 0.30, 0.14), 0.68, 0.90),
    "meso_riverbank": ((0.065, 0.055, 0.042),(0.14, 0.115, 0.085),(0.18, 0.16, 0.13),   (0.048, 0.042, 0.034), 0.20, 0.56),
    "plaza_stone":    ((0.28, 0.24, 0.18),  (0.46, 0.40, 0.31),  (0.22, 0.18, 0.13),    (0.38, 0.33, 0.24), 0.62, 0.88),
    "ararat_basalt":  ((0.06, 0.062, 0.07), (0.16, 0.165, 0.18), (0.042, 0.044, 0.05),  (0.22, 0.21, 0.20), 0.64, 0.92),
    "ararat_scree":   ((0.075, 0.068, 0.062),(0.16, 0.15, 0.14), (0.12, 0.125, 0.135),  (0.055, 0.05, 0.045), 0.34, 0.86),
    "ararat_moss":    ((0.09, 0.075, 0.055),(0.18, 0.15, 0.11),  (0.10, 0.22, 0.065),   (0.24, 0.29, 0.16), 0.66, 0.92),
    "ararat_snow":    ((0.52, 0.57, 0.64),  (0.74, 0.76, 0.78),  (0.46, 0.52, 0.60),    (0.76, 0.77, 0.78), 0.38, 0.72),
}


def make_terrain_bake_material(tile_id):
    pal = TILE_PALETTES[tile_id]
    c_lo = _clamp_rgb(pal[0])
    c_hi = _clamp_rgb(pal[1])
    c_a = _clamp_rgb(pal[2])
    c_b = _clamp_rgb(pal[3])
    r_lo, r_hi = pal[4], pal[5]

    mat = bpy.data.materials.new(name=f"Mat_Terrain_{tile_id}")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Metallic"].default_value = 0.0
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Periodisches 3D-Noise über Torus-Koordinaten
    t_vec = _add_torus_coords(nt)
    n1 = nt.nodes.new("ShaderNodeTexNoise")
    n1.inputs["Scale"].default_value = 6.5
    n1.inputs["Detail"].default_value = 7.0
    n1.inputs["Roughness"].default_value = 0.62
    nt.links.new(t_vec, n1.inputs["Vector"])

    n2 = nt.nodes.new("ShaderNodeTexNoise")
    n2.inputs["Scale"].default_value = 22.0
    n2.inputs["Detail"].default_value = 5.0
    n2.inputs["Roughness"].default_value = 0.68
    nt.links.new(t_vec, n2.inputs["Vector"])

    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "TerrainMasks"
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(attr.outputs["Color"], sep.inputs["Color"])

    # Basis-Albedo aus Noise + Masken R (trough/crack/pebble/joint/moss) & B (straw/woodchip)
    col_base = _mix_rgba(nt, n1.outputs["Fac"], c_lo, c_hi)
    col_grain = _mix_rgba(nt, n2.outputs["Fac"], c_lo, c_hi)
    col_mix = _mix_rgba(nt, 0.38, col_base, col_grain)
    col_m1 = _mix_rgba(nt, sep.outputs["Red"], col_mix, c_a)
    col_final = _mix_rgba(nt, sep.outputs["Blue"] if tile_id in ("meso_plowed", "meso_shipyard", "ararat_moss") else sep.outputs["Green"], col_m1, c_b)
    if tile_id in ("meso_riverbank", "ararat_scree", "plaza_stone"):
        # Subtile Stein-/Schlammvariation über Green/Blue
        col_final = _mix_rgba(nt, sep.outputs["Green"], col_m1, c_b)

    nt.links.new(col_final, bsdf.inputs["Base Color"])

    # Roughness-Graph
    rough_noise = _mix_float(nt, n2.outputs["Fac"], max(0.20, r_hi - 0.14), r_hi)
    if tile_id in ("meso_plowed", "meso_riverbank", "ararat_scree", "meso_steppe"):
        fac_wet = sep.outputs["Red"] if tile_id == "meso_plowed" else sep.outputs["Green"]
        rough_out = _mix_float(nt, fac_wet, rough_noise, r_lo)
    else:
        rough_out = _mix_float(nt, n1.outputs["Fac"], r_lo, r_hi)
    nt.links.new(rough_out, bsdf.inputs["Roughness"])

    # Emission-Helper für schnellen schattenfreien Color/Roughness-Bake
    emit = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(col_final, emit.inputs["Color"])

    return {"mat": mat, "nt": nt, "out": out, "bsdf": bsdf, "emit": emit, "col_out": col_final, "rough_out": rough_out}


# ==============================================================================
# BAKE-PIPELINE PRO KACHEL -> 512x512 NUMPY BUFFERS
# ==============================================================================

def _create_bake_image(name, size, colorspace="Non-Color"):
    img = bpy.data.images.new(name, width=size, height=size, alpha=False, float_buffer=True)
    img.colorspace_settings.name = colorspace
    return img


def _img_to_np(img):
    w, h = img.size
    arr = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(arr)
    return arr.reshape((h, w, 4))[:, :, :3].copy()


def _attach_bake_node(nt, img):
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    nt.nodes.active = tex
    return tex


def bake_single_tile(tile_id, size=TILE_SIZE):
    t0 = time.time()
    scene = clear_scene()
    dev = setup_cycles(scene, samples=4, use_oidn=False)
    print(f"  [BAKE {tile_id}] Baue High-Poly-Relief ({GRID_N}x{GRID_N} + Schürze) auf {dev}...", flush=True)

    hi_obj = build_displaced_tile_mesh(f"Hi_{tile_id}", tile_id)
    lo_obj = build_bake_target_plane(f"Lo_{tile_id}")

    mat_info = make_terrain_bake_material(tile_id)
    hi_obj.data.materials.append(mat_info["mat"])

    lo_mat = bpy.data.materials.new(f"LoMat_{tile_id}")
    lo_mat.use_nodes = True
    lo_obj.data.materials.append(lo_mat)

    # Non-Color Float-Buffer für Albedo, damit Linear-Werte nicht doppelt sRGB-kodiert werden!
    img_alb = _create_bake_image(f"BakeAlb_{tile_id}", size, "Non-Color")
    img_nrm = _create_bake_image(f"BakeNrm_{tile_id}", size, "Non-Color")
    img_rgh = _create_bake_image(f"BakeRgh_{tile_id}", size, "Non-Color")
    img_ao  = _create_bake_image(f"BakeAO_{tile_id}", size, "Non-Color")

    tex_node = _attach_bake_node(lo_mat.node_tree, img_alb)

    bpy.ops.object.select_all(action="DESELECT")
    hi_obj.select_set(True)
    lo_obj.select_set(True)
    bpy.context.view_layer.objects.active = lo_obj

    scene.render.bake.use_selected_to_active = True
    scene.render.bake.cage_extrusion = 0.35
    scene.render.bake.max_ray_distance = 0.65
    scene.render.bake.margin = 0

    # 1. BaseColor (Emission ohne Schatten, 4 Samples)
    mat_info["nt"].links.new(mat_info["col_out"], mat_info["emit"].inputs["Color"])
    mat_info["nt"].links.new(mat_info["emit"].outputs["Emission"], mat_info["out"].inputs["Surface"])
    tex_node.image = img_alb
    scene.cycles.samples = 4
    scene.cycles.use_denoising = False
    bpy.ops.object.bake(type="EMIT")

    # 2. Roughness (Emission aus Roughness-Ausgang, 4 Samples)
    comb_r = mat_info["nt"].nodes.new("ShaderNodeCombineColor")
    mat_info["nt"].links.new(mat_info["rough_out"], comb_r.inputs["Red"])
    mat_info["nt"].links.new(mat_info["rough_out"], comb_r.inputs["Green"])
    mat_info["nt"].links.new(mat_info["rough_out"], comb_r.inputs["Blue"])
    mat_info["nt"].links.new(comb_r.outputs["Color"], mat_info["emit"].inputs["Color"])
    tex_node.image = img_rgh
    bpy.ops.object.bake(type="EMIT")

    # 3. Normal (Tangent-Space, 4 Samples)
    mat_info["nt"].links.new(mat_info["bsdf"].outputs["BSDF"], mat_info["out"].inputs["Surface"])
    tex_node.image = img_nrm
    bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")

    # 4. AO (16 Samples + OIDN)
    tex_node.image = img_ao
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    try:
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    bpy.ops.object.bake(type="AO")

    alb = np.clip(_img_to_np(img_alb), 0.04, 0.78)
    nrm = np.clip(_img_to_np(img_nrm), 0.0, 1.0)
    rgh = np.clip(_img_to_np(img_rgh)[:, :, 0], 0.0, 1.0)
    ao  = np.clip(_img_to_np(img_ao)[:, :, 0], 0.0, 1.0)
    orm = np.stack([ao, rgh, np.zeros_like(ao)], axis=-1)

    dt = time.time() - t0
    seam_alb = float(np.mean(np.abs(alb[0, :, :] - alb[-1, :, :])) + np.mean(np.abs(alb[:, 0, :] - alb[:, -1, :]))) * 0.5
    seam_nrm = float(np.mean(np.abs(nrm[0, :, :] - nrm[-1, :, :])) + np.mean(np.abs(nrm[:, 0, :] - nrm[:, -1, :]))) * 0.5
    print(f"  [DONE {tile_id}] {dt:.1f}s | Albedo=[{alb.min():.3f}..{alb.max():.3f}] | Seam(Alb={seam_alb:.4f}, Nrm={seam_nrm:.4f})", flush=True)
    return alb, nrm, orm


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


def compose_2x2_atlas(tiles_data):
    """Setzt 4 (512x512) Kacheln zu (1024x1024) 2x2 Atlas zusammen: [TL, TR, BL, BR] (Blender Y-up!)."""
    s = TILE_SIZE
    A = ATLAS_SIZE
    alb = np.zeros((A, A, 3), dtype=np.float32)
    nrm = np.zeros((A, A, 3), dtype=np.float32)
    orm = np.zeros((A, A, 3), dtype=np.float32)
    # In Blender Image-Pixels ist row 0 = unten (V=0), row s = oben (V=0.5..1)
    offsets = [(0, s), (s, s), (0, 0), (s, 0)]  # TL, TR, BL, BR
    for (a, n, o), (ox, oy) in zip(tiles_data, offsets):
        alb[oy:oy + s, ox:ox + s] = a
        nrm[oy:oy + s, ox:ox + s] = n
        orm[oy:oy + s, ox:ox + s] = o
    return alb, nrm, orm


# ==============================================================================
# VISUELLES KONTROLL-RENDERING (SUN-RAKING 3D-SHOWCASE)
# ==============================================================================

def render_showcase(tex_dir, preview_path, all_tiles):
    print("[SHOWCASE] Rendere 3D-Relief-Übersichtskarte unter schrägem Sonnenlicht...", flush=True)
    scene = clear_scene()
    dev = setup_cycles(scene, samples=32, use_oidn=True)
    scene.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
    scene.view_settings.look = "None"

    # Dunkler Studio-Hintergrund & schräges Sonnenlicht (20° Elevation)
    world = bpy.data.worlds.new("ShowcaseWorld")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.045, 0.048, 0.055, 1.0)
        bg.inputs["Strength"].default_value = 0.85

    sun_data = bpy.data.lights.new("RakingSun", type="SUN")
    sun_data.energy = 4.2
    sun_data.angle = math.radians(2.2)
    sun_obj = bpy.data.objects.new("RakingSun", sun_data)
    sun_obj.rotation_euler = (math.radians(68.0), math.radians(15.0), math.radians(-35.0))
    bpy.context.collection.objects.link(sun_obj)

    layout = [
        # (tile_id, gx, gy, mat_atlas_prefix, uv_box)
        ("meso_plowed",    -5.5,  2.8, "terrain_meso_atlas",   (0.0, 0.5, 0.5, 1.0)),
        ("meso_steppe",    -1.0,  2.8, "terrain_meso_atlas",   (0.5, 0.5, 1.0, 1.0)),
        ("meso_shipyard",  -5.5, -1.7, "terrain_meso_atlas",   (0.0, 0.0, 0.5, 0.5)),
        ("meso_riverbank", -1.0, -1.7, "terrain_meso_atlas",   (0.5, 0.0, 1.0, 0.5)),
        ("plaza_stone",     3.6,  0.55,"terrain_plaza",        (0.0, 0.0, 1.0, 1.0)),
        ("ararat_basalt",   8.2,  2.8, "terrain_ararat_atlas", (0.0, 0.5, 0.5, 1.0)),
        ("ararat_scree",   12.7,  2.8, "terrain_ararat_atlas", (0.5, 0.5, 1.0, 1.0)),
        ("ararat_moss",     8.2, -1.7, "terrain_ararat_atlas", (0.0, 0.0, 0.5, 0.5)),
        ("ararat_snow",    12.7, -1.7, "terrain_ararat_atlas", (0.5, 0.0, 1.0, 0.5)),
    ]

    # Lade gebackene Texturen
    loaded_imgs = {}
    for pref in ("terrain_meso_atlas", "terrain_plaza", "terrain_ararat_atlas"):
        alb_i = bpy.data.images.load(os.path.join(tex_dir, f"{pref}_albedo.png"))
        alb_i.colorspace_settings.name = "sRGB"
        nrm_i = bpy.data.images.load(os.path.join(tex_dir, f"{pref}_normal.png"))
        nrm_i.colorspace_settings.name = "Non-Color"
        orm_i = bpy.data.images.load(os.path.join(tex_dir, f"{pref}_orm.png"))
        orm_i.colorspace_settings.name = "Non-Color"
        loaded_imgs[pref] = (alb_i, nrm_i, orm_i)

    for tile_id, gx, gy, pref, (u0, v0, u1, v1) in layout:
        # 128x128 Relief-Kachel mit echten Normal/ORM/Albedo-Texturen
        n = 112
        idx_1d = np.linspace(0.0, 1.0, n + 1)
        uu, vv = np.meshgrid(idx_1d, idx_1d, indexing="xy")
        h, _, _, _ = eval_tile_height_and_masks(tile_id, uu, vv)
        xg = gx - 1.8 + uu * 3.6
        yg = gy - 1.8 + vv * 3.6
        mesh = bpy.data.meshes.new(f"Prev_{tile_id}")
        verts = np.column_stack([xg.ravel(), yg.ravel(), h.ravel()]).tolist()
        stride = n + 1
        ii, jj = np.meshgrid(np.arange(n), np.arange(n), indexing="xy")
        v00 = (jj * stride + ii).ravel()
        faces = np.column_stack([v00, v00 + 1, v00 + stride + 1, v00 + stride]).tolist()
        mesh.from_pydata(verts, [], faces)
        mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))

        uv_layer = mesh.uv_layers.new(name="UVMap")
        uv_u = (u0 + uu * (u1 - u0)).ravel()
        uv_v = (v0 + vv * (v1 - v0)).ravel()
        loop_v = np.empty(len(mesh.loops), dtype=np.int64)
        mesh.loops.foreach_get("vertex_index", loop_v)
        uv_arr = np.column_stack([uv_u[loop_v], uv_v[loop_v]]).astype(np.float32)
        uv_layer.data.foreach_set("uv", uv_arr.ravel())

        mat = bpy.data.materials.new(f"PrevMat_{tile_id}")
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

        alb_i, nrm_i, orm_i = loaded_imgs[pref]
        t_alb = nt.nodes.new("ShaderNodeTexImage"); t_alb.image = alb_i
        t_orm = nt.nodes.new("ShaderNodeTexImage"); t_orm.image = orm_i
        t_nrm = nt.nodes.new("ShaderNodeTexImage"); t_nrm.image = nrm_i

        sep_orm = nt.nodes.new("ShaderNodeSeparateColor")
        nt.links.new(t_orm.outputs["Color"], sep_orm.inputs["Color"])
        nt.links.new(t_alb.outputs["Color"], bsdf.inputs["Base Color"])
        nt.links.new(sep_orm.outputs["Green"], bsdf.inputs["Roughness"])

        nrm_map = nt.nodes.new("ShaderNodeNormalMap")
        nrm_map.inputs["Strength"].default_value = 0.85
        nt.links.new(t_nrm.outputs["Color"], nrm_map.inputs["Color"])
        nt.links.new(nrm_map.outputs["Normal"], bsdf.inputs["Normal"])

        mesh.materials.append(mat)
        obj = bpy.data.objects.new(f"Prev_{tile_id}", mesh)
        bpy.context.collection.objects.link(obj)

    cam_data = bpy.data.cameras.new("ShowcaseCam")
    cam_data.lens = 35.0
    cam_obj = bpy.data.objects.new("ShowcaseCam", cam_data)
    cam_obj.location = (3.6, -15.8, 19.5)
    direction = Vector((3.6, 0.55, 0.0)) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = preview_path
    os.makedirs(os.path.dirname(preview_path), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print(f"[SHOWCASE] Gespeichert: {preview_path} ({dev})", flush=True)


def main():
    t_start = time.time()
    root = get_project_root()
    tex_dir = os.path.join(root, "assets", "textures")
    preview_path = os.path.join(root, "assets", "previews", "terrain_textures_showcase.png")

    print("=== ARCHE TERRAIN-TEXTUREN BAKER START ===", flush=True)

    # Set A: Mesopotamien (2x2 = 1024x1024)
    meso_ids = ["meso_plowed", "meso_steppe", "meso_shipyard", "meso_riverbank"]
    meso_tiles = [bake_single_tile(tid, TILE_SIZE) for tid in meso_ids]
    meso_alb, meso_nrm, meso_orm = compose_2x2_atlas(meso_tiles)
    save_np_png(meso_alb, os.path.join(tex_dir, "terrain_meso_atlas_albedo.png"), is_srgb=True)
    save_np_png(meso_nrm, os.path.join(tex_dir, "terrain_meso_atlas_normal.png"), is_srgb=False)
    save_np_png(meso_orm, os.path.join(tex_dir, "terrain_meso_atlas_orm.png"), is_srgb=False)
    print(f"[SET A] terrain_meso_atlas_* (1024x1024) exportiert | HDR-Albedo=[{meso_alb.min():.3f}..{meso_alb.max():.3f}]", flush=True)

    # Plaza: Ur-Schinar Pflaster (512x512)
    p_alb, p_nrm, p_orm = bake_single_tile("plaza_stone", TILE_SIZE)
    save_np_png(p_alb, os.path.join(tex_dir, "terrain_plaza_albedo.png"), is_srgb=True)
    save_np_png(p_nrm, os.path.join(tex_dir, "terrain_plaza_normal.png"), is_srgb=False)
    save_np_png(p_orm, os.path.join(tex_dir, "terrain_plaza_orm.png"), is_srgb=False)
    print(f"[PLAZA] terrain_plaza_* (512x512) exportiert | HDR-Albedo=[{p_alb.min():.3f}..{p_alb.max():.3f}]", flush=True)

    # Set B: Ararat-Hochgebirge (2x2 = 1024x1024)
    ara_ids = ["ararat_basalt", "ararat_scree", "ararat_moss", "ararat_snow"]
    ara_tiles = [bake_single_tile(tid, TILE_SIZE) for tid in ara_ids]
    ara_alb, ara_nrm, ara_orm = compose_2x2_atlas(ara_tiles)
    save_np_png(ara_alb, os.path.join(tex_dir, "terrain_ararat_atlas_albedo.png"), is_srgb=True)
    save_np_png(ara_nrm, os.path.join(tex_dir, "terrain_ararat_atlas_normal.png"), is_srgb=False)
    save_np_png(ara_orm, os.path.join(tex_dir, "terrain_ararat_atlas_orm.png"), is_srgb=False)
    print(f"[SET B] terrain_ararat_atlas_* (1024x1024) exportiert | HDR-Albedo=[{ara_alb.min():.3f}..{ara_alb.max():.3f}]", flush=True)

    # Visuelles Kontroll-Rendering
    render_showcase(tex_dir, preview_path, meso_ids + ["plaza_stone"] + ara_ids)

    total_s = time.time() - t_start
    print(f"=== TERRAIN_BAKE_DONE in {total_s:.1f}s ===", flush=True)


if __name__ == "__main__":
    main()
