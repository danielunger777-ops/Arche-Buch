"""
build_mesopotamia_cities.py — Modulares Mesopotamien-Architektur- & Strassen-Kit (4 LODs)
=========================================================================================
Erzeugt 21 bronzezeitliche Stadt-, Dorf-, Marschland-, Monumental- & Strassen-Module nach
BLENDER_PIPELINE.md (Z-Up, +Y Vorne, Metric 1.0, Origin mittig auf Z=0.0, -0.50 m
Fundament-Sockel, 1 Shared-Trim-Material 'Mat_Mesopotamia_City_Trim'):

  - 5 Staedtische Wohnhaeuser:  ur_courtyard_house_01..05   (LOD0..LOD3)
  - 5 Dorf-/Vorstadthaeuser:    ur_mudbrick_small_01..05    (LOD0..LOD3)
  - Marschland-Architektur:     ur_mudhif_hut               (LOD0..LOD3)
  - Monumental & Infrastruktur: ur_ziggurat_temple, ur_city_gate, ur_wall_segment,
                                ur_wall_tower, ur_grain_silo, ur_kiln_dome,
                                ur_canal_bridge             (je LOD0..LOD3)
  - Strassen-Requisiten:        road_curb_lamp_post, road_cart_parked,
                                road_market_awning          (je LOD0..LOD1)

Exportiert nach:
  - assets/blend/world/mesopotamia_city_kit.blend
  - assets/glb/world/mesopotamia_city_kit.glb  (via export_arche_glb.export_glb)
  - assets/manifest.json
  - assets/previews/mesopotamia_city_showcase.png

Aufruf:
  blender --background --python-exit-code 1 --python assets/scripts/build_mesopotamia_cities.py
"""

import os
import sys
import math
import time
import json
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
SCRIPTS_DIR = os.path.join(ASSETS_DIR, "scripts")
for p in (ASSETS_DIR, SCRIPTS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

import export_arche_glb  # noqa: E402
from build_city_trim_atlas import TRIM_REGIONS  # noqa: E402


# ==============================================================================
# SZENE & SHARED MATERIAL (1 DRAW CALL PRO MODUL / INSTANCED MESH)
# ==============================================================================

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    return scene


def setup_cycles(scene, samples=48, use_oidn=True):
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
        scene.cycles.max_bounces = 4
        scene.cycles.diffuse_bounces = 2
        scene.cycles.glossy_bounces = 2
        scene.cycles.transmission_bounces = 0
    return "CUDA (GPU)" if used_gpu else "CPU"


def create_city_trim_material(tex_dir):
    """Erstellt 1 gemeinsames PBR-Material mit BaseColor [sRGB], Normal [Linear], ORM [Linear]."""
    mat = bpy.data.materials.new("Mat_Mesopotamia_City_Trim")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    p_col = os.path.join(tex_dir, "city_trim_atlas_baseColor.png")
    p_nrm = os.path.join(tex_dir, "city_trim_atlas_normal.png")
    p_orm = os.path.join(tex_dir, "city_trim_atlas_orm.png")
    for p in (p_col, p_nrm, p_orm):
        if not os.path.isfile(p):
            raise FileNotFoundError(f"Trim-Sheet-Textur fehlt: {p} (bitte zuerst build_city_trim_atlas.py ausfuehren!)")

    img_c = bpy.data.images.load(p_col, check_existing=True)
    img_c.colorspace_settings.name = "sRGB"
    img_n = bpy.data.images.load(p_nrm, check_existing=True)
    img_n.colorspace_settings.name = "Non-Color"
    img_o = bpy.data.images.load(p_orm, check_existing=True)
    img_o.colorspace_settings.name = "Non-Color"

    tc = nt.nodes.new("ShaderNodeTexImage"); tc.image = img_c
    tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = img_n
    to = nt.nodes.new("ShaderNodeTexImage"); to.image = img_o

    nrm_map = nt.nodes.new("ShaderNodeNormalMap")
    nrm_map.inputs["Strength"].default_value = 0.85

    sep = nt.nodes.new("ShaderNodeSeparateColor")

    nt.links.new(tc.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tn.outputs["Color"], nrm_map.inputs["Color"])
    nt.links.new(nrm_map.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(to.outputs["Color"], sep.inputs["Color"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])

    gltf_grp = bpy.data.node_groups.get("glTF Material Output")
    if gltf_grp is None:
        gltf_grp = bpy.data.node_groups.new("glTF Material Output", "ShaderNodeTree")
        if hasattr(gltf_grp, "interface"):
            gltf_grp.interface.new_socket(name="Occlusion", in_out="INPUT", socket_type="NodeSocketFloat")
        else:
            gltf_grp.inputs.new("NodeSocketFloat", "Occlusion")
    g_node = nt.nodes.new("ShaderNodeGroup")
    g_node.node_tree = gltf_grp
    nt.links.new(sep.outputs["Red"], g_node.inputs["Occlusion"])

    return mat


# ==============================================================================
# BMESH GEOMETRIE- & TRIM-UV-BAUSTEINE
# ==============================================================================

_FULL_U_SEAMLESS = {"alley_mud_road", "royal_stone_road", "mudbrick_plaster", "fired_brick_plinth", "fired_brick_upper", "damp_plinth"}


def _pingpong01(t):
    """Spiegelt t nahtlos in [0..1] fuer Sub-Panels ohne Mipmap-Bleed."""
    m = t % 2.0
    return m if m <= 1.0 else 2.0 - m


def _map_uv(region_key, u_local, v_local, tile_u=False):
    u0, v0, u1, v1 = TRIM_REGIONS[region_key]
    v_clamped = max(0.0, min(1.0, v_local))
    if region_key in _FULL_U_SEAMLESS and tile_u:
        u_mapped = u_local
    else:
        u_pp = _pingpong01(abs(u_local)) if tile_u else max(0.0, min(1.0, u_local))
        u_mapped = u0 + u_pp * (u1 - u0)
    v_mapped = v0 + v_clamped * (v1 - v0)
    return (u_mapped, v_mapped)


def _apply_box_uv_to_faces(faces, uv_layer, region_key, u_scale=0.35, v_fit=True, z_bounds=None, rot_uv=False):
    """Projiziert saubere Box-UVs auf jede uebergebene Flaeche."""
    tile_u = region_key in _FULL_U_SEAMLESS
    for f in faces:
        f.normal_update()
        n = f.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        zs = [v.co.z for v in f.verts]
        z_lo = z_bounds[0] if z_bounds else min(zs)
        z_hi = z_bounds[1] if z_bounds else max(zs)
        dz = max(1e-4, z_hi - z_lo)

        if az >= ax and az >= ay:
            # Dach / Boden
            xs = [v.co.x for v in f.verts]
            ys = [v.co.y for v in f.verts]
            min_x, span_x = min(xs), max(1e-4, max(xs) - min(xs))
            min_y, span_y = min(ys), max(1e-4, max(ys) - min(ys))
            for loop in f.loops:
                co = loop.vert.co
                lu = (co.x - min_x) * u_scale if tile_u else (co.x - min_x) / span_x
                lv = (co.y - min_y) / span_y if v_fit else ((co.y - min_y) * u_scale) % 1.0
                if rot_uv:
                    lu, lv = lv, lu
                loop[uv_layer].uv = _map_uv(region_key, lu, lv, tile_u=tile_u)
        else:
            # Vertikale oder geböschte Wand
            use_x = ay >= ax
            hs = [v.co.x if use_x else v.co.y for v in f.verts]
            min_h, span_h = min(hs), max(1e-4, max(hs) - min(hs))
            for loop in f.loops:
                co = loop.vert.co
                h_coord = co.x if use_x else co.y
                lu = (h_coord - min_h) * u_scale if tile_u else (h_coord - min_h) / span_h
                lv = (co.z - z_lo) / dz if v_fit else ((co.z - z_lo) * u_scale) % 1.0
                if rot_uv:
                    lu, lv = lv, lu
                loop[uv_layer].uv = _map_uv(region_key, lu, lv, tile_u=tile_u)


def add_battered_prism(
    bm, uv_layer, cx, cy, z0, z1, sx0, sy0, sx1, sy1,
    region_key, u_scale=0.11, v_fit=True, cap_bottom=True, cap_top=True,
    top_region=None, rot_uv=False,
):
    """Erzeugt einen geböschten Quader (sx0/sy0 unten -> sx1/sy1 oben) mit sauberen Trim-UVs."""
    hx0, hy0 = 0.5 * sx0, 0.5 * sy0
    hx1, hy1 = 0.5 * sx1, 0.5 * sy1
    b = [
        bm.verts.new((cx - hx0, cy - hy0, z0)),
        bm.verts.new((cx + hx0, cy - hy0, z0)),
        bm.verts.new((cx + hx0, cy + hy0, z0)),
        bm.verts.new((cx - hx0, cy + hy0, z0)),
    ]
    t = [
        bm.verts.new((cx - hx1, cy - hy1, z1)),
        bm.verts.new((cx + hx1, cy - hy1, z1)),
        bm.verts.new((cx + hx1, cy + hy1, z1)),
        bm.verts.new((cx - hx1, cy + hy1, z1)),
    ]
    side_faces = []
    for i in range(4):
        j = (i + 1) % 4
        side_faces.append(bm.faces.new((b[i], b[j], t[j], t[i])))
    _apply_box_uv_to_faces(side_faces, uv_layer, region_key, u_scale=u_scale, v_fit=v_fit, z_bounds=(z0, z1), rot_uv=rot_uv)

    top_faces = []
    if cap_top:
        ft = bm.faces.new((t[0], t[1], t[2], t[3]))
        top_faces.append(ft)
        _apply_box_uv_to_faces([ft], uv_layer, top_region or region_key, u_scale=u_scale, v_fit=True, rot_uv=rot_uv)
    if cap_bottom:
        fb = bm.faces.new((b[3], b[2], b[1], b[0]))
        _apply_box_uv_to_faces([fb], uv_layer, region_key, u_scale=u_scale, v_fit=True, rot_uv=rot_uv)
    return side_faces, top_faces


def add_wall_with_plinth(
    bm, uv_layer, cx, cy, z_plinth_top, z_top, sx, sy,
    batter=0.08, plinth_z=-0.50,
    plinth_region="fired_brick_plinth", wall_region="mudbrick_plaster",
    top_region=None, u_scale=0.11,
):
    """Zweistufige geböschte Wand: Sockel (Z=-0.50..z_plinth_top) + Oberbau (z_plinth_top..z_top)."""
    tot_h = max(0.2, z_top - plinth_z)
    f_mid = (z_plinth_top - plinth_z) / tot_h
    sx_bot = sx + batter * 2.0
    sy_bot = sy + batter * 2.0
    sx_mid = sx_bot * (1.0 - f_mid) + sx * f_mid
    sy_mid = sy_bot * (1.0 - f_mid) + sy * f_mid

    add_battered_prism(
        bm, uv_layer, cx, cy, plinth_z, z_plinth_top,
        sx_bot, sy_bot, sx_mid, sy_mid,
        plinth_region, u_scale=u_scale, v_fit=True, cap_bottom=True, cap_top=False,
    )
    add_battered_prism(
        bm, uv_layer, cx, cy, z_plinth_top, z_top,
        sx_mid, sy_mid, sx, sy,
        wall_region, u_scale=u_scale, v_fit=True, cap_bottom=False, cap_top=True,
        top_region=top_region or wall_region,
    )


def add_cylinder(
    bm, uv_layer, p0, p1, r0, r1, segs=8, region_key="cedar_timber",
    cap0=True, cap1=True, cap0_region=None, cap1_region=None, u_scale=1.0,
):
    """Erzeugt einen Kegelstumpf/Zylinder entlang p0->p1 mit sauberen Trim-UVs."""
    axis = Vector(p1) - Vector(p0)
    length = axis.length
    if length < 1e-5:
        return []
    z_dir = axis.normalized()
    up_ref = Vector((0.0, 0.0, 1.0)) if abs(z_dir.z) < 0.92 else Vector((1.0, 0.0, 0.0))
    x_dir = up_ref.cross(z_dir).normalized()
    y_dir = z_dir.cross(x_dir).normalized()

    ring0, ring1 = [], []
    for i in range(segs):
        ang = 2.0 * math.pi * i / segs
        ca, sa = math.cos(ang), math.sin(ang)
        d = x_dir * ca + y_dir * sa
        ring0.append(bm.verts.new(Vector(p0) + d * r0))
        ring1.append(bm.verts.new(Vector(p1) + d * r1))

    faces = []
    tile_u = region_key in _FULL_U_SEAMLESS
    for i in range(segs):
        j = (i + 1) % segs
        f = bm.faces.new((ring0[i], ring0[j], ring1[j], ring1[i]))
        faces.append(f)
        u_a = (i / segs) * u_scale
        u_b = ((i + 1) / segs) * u_scale
        uvs = [
            _map_uv(region_key, 0.0, u_a if not tile_u else 0.1, tile_u=tile_u) if False else _map_uv(region_key, u_a, 0.15, tile_u=tile_u),
            _map_uv(region_key, u_b, 0.15, tile_u=tile_u),
            _map_uv(region_key, u_b, 0.85, tile_u=tile_u),
            _map_uv(region_key, u_a, 0.85, tile_u=tile_u),
        ]
        # Laengsausrichtung entlang U (z. B. Holzmaserung entlang Balkenachse)
        v_a = i / segs
        v_b = (i + 1) / segs
        uvs = [
            _map_uv(region_key, 0.0, v_a, tile_u=tile_u),
            _map_uv(region_key, 0.0, v_b, tile_u=tile_u),
            _map_uv(region_key, min(1.0, length * 0.5 * u_scale), v_b, tile_u=tile_u),
            _map_uv(region_key, min(1.0, length * 0.5 * u_scale), v_a, tile_u=tile_u),
        ]
        for lp, uv in zip(f.loops, uvs):
            lp[uv_layer].uv = uv

    for do_cap, ring, rev, r_key in (
        (cap0, ring0, True, cap0_region or region_key),
        (cap1, ring1, False, cap1_region or region_key),
    ):
        if not do_cap:
            continue
        verts = list(reversed(ring)) if rev else ring
        fc = bm.faces.new(verts)
        faces.append(fc)
        for idx, lp in enumerate(fc.loops):
            k = (segs - 1 - idx) if rev else idx
            ang = 2.0 * math.pi * k / segs
            lp[uv_layer].uv = _map_uv(r_key, 0.5 + 0.45 * math.cos(ang), 0.5 + 0.45 * math.sin(ang), tile_u=False)
    return faces


def add_recessed_door(bm, uv_layer, cx, cy, z0, w, h, facing="+Y", depth=0.22, frame_t=0.18, door_region="carved_door", frame_region="fired_brick_upper"):
    """Plastische Tuerlaibung mit Sturz, seitlichen Pfosten, Schwelle und vertieftem Tuerblatt."""
    # Richtungsvektor nach aussen
    dir_map = {
        "+Y": (Vector((0, 1, 0)), Vector((1, 0, 0))),
        "-Y": (Vector((0, -1, 0)), Vector((-1, 0, 0))),
        "+X": (Vector((1, 0, 0)), Vector((0, -1, 0))),
        "-X": (Vector((-1, 0, 0)), Vector((0, 1, 0))),
    }
    fwd, right = dir_map[facing]
    center_base = Vector((cx, cy, z0))

    def _box(local_r, local_f, z_lo, z_hi, sr, sf, reg):
        p = center_base + right * local_r + fwd * local_f
        sx = abs(right.x) * sr + abs(fwd.x) * sf
        sy = abs(right.y) * sr + abs(fwd.y) * sf
        add_battered_prism(bm, uv_layer, p.x, p.y, z_lo, z_hi, sx, sy, sx * 0.96, sy * 0.96, reg, u_scale=0.6)

    # Schwelle
    _box(0.0, depth * 0.35, -0.10, z0 + 0.08, w + frame_t * 2.0, depth * 1.1, "royal_stone_road")
    # Linker & rechter Laibungspfosten
    _box(-(w * 0.5 + frame_t * 0.5), depth * 0.45, z0 + 0.08, z0 + h, frame_t, depth, frame_region)
    _box(+(w * 0.5 + frame_t * 0.5), depth * 0.45, z0 + 0.08, z0 + h, frame_t, depth, frame_region)
    # Zedern-Tuersturz oben
    _box(0.0, depth * 0.50, z0 + h, z0 + h + frame_t * 1.1, w + frame_t * 2.4, depth * 1.15, "cedar_timber")
    # Tuerblatt innen (sauber vor der Wand, innerhalb der Laibung)
    _box(0.0, 0.05, z0 + 0.08, z0 + h, w, 0.08, door_region)


def add_window_niche(bm, uv_layer, cx, cy, z0, w, h, facing="+Y", reg_frame="cedar_timber"):
    """Kleiner plastischer Licht-/Lueftungsschlitz mit vorspringendem Holzsturz & dunkler Oeffnung."""
    dir_map = {"+Y": (0, 1), "-Y": (0, -1), "+X": (1, 0), "-X": (-1, 0)}
    fx, fy = dir_map[facing]
    sx = w if fy != 0 else 0.10
    sy = w if fx != 0 else 0.10
    # Rahmen-Tiefe vorspringend (0.08 m) gegen Z-Fighting
    px, py = cx + fx * 0.04, cy + fy * 0.04
    add_battered_prism(bm, uv_layer, px, py, z0, z0 + h, sx, sy, sx, sy, "carved_door", u_scale=0.9)
    # Zedernsturz darueber
    lx, ly = cx + fx * 0.06, cy + fy * 0.06
    lsx = (w + 0.20) if fy != 0 else 0.14
    lsy = (w + 0.20) if fx != 0 else 0.14
    add_battered_prism(bm, uv_layer, lx, ly, z0 + h, z0 + h + 0.10, lsx, lsy, lsx, lsy, reg_frame, u_scale=0.6)


def add_parapet_with_merlons(bm, uv_layer, cx, cy, z_base, sx, sy, wall_t=0.34, h_parapet=0.52, merlon_step=1.1, region="mudbrick_plaster", add_merlons=True, merlon_h=0.28):
    """Umlaufende Dachbruestung mit optionalen Zinnen (ohne Eck-Ueberlappung)."""
    # Nord/Sued-Bruestung volle Breite
    for sgn in (-1.0, 1.0):
        add_battered_prism(
            bm, uv_layer, cx, cy + sgn * (sy * 0.5 - wall_t * 0.5), z_base, z_base + h_parapet,
            sx, wall_t, sx - 0.04, wall_t * 0.90, region, u_scale=0.12,
        )
    # West/Ost-Bruestung dazwischen
    inner_y = max(0.2, sy - 2.0 * wall_t)
    for sgn in (-1.0, 1.0):
        add_battered_prism(
            bm, uv_layer, cx + sgn * (sx * 0.5 - wall_t * 0.5), cy, z_base, z_base + h_parapet,
            wall_t, inner_y, wall_t * 0.90, inner_y, region, u_scale=0.12,
        )
    if add_merlons:
        nx = max(2, int(round(sx / merlon_step)))
        for i in range(nx):
            mx = cx - sx * 0.5 + wall_t * 0.7 + (i + 0.5) * ((sx - wall_t * 1.4) / nx)
            for sgn in (-1.0, 1.0):
                add_battered_prism(
                    bm, uv_layer, mx, cy + sgn * (sy * 0.5 - wall_t * 0.5),
                    z_base + h_parapet, z_base + h_parapet + merlon_h,
                    0.42, wall_t * 0.85, 0.34, wall_t * 0.72, region, u_scale=0.14,
                )
        ny = max(2, int(round(inner_y / merlon_step)))
        for j in range(ny):
            my = cy - inner_y * 0.5 + (j + 0.5) * (inner_y / ny)
            for sgn in (-1.0, 1.0):
                add_battered_prism(
                    bm, uv_layer, cx + sgn * (sx * 0.5 - wall_t * 0.5), my,
                    z_base + h_parapet, z_base + h_parapet + merlon_h,
                    wall_t * 0.85, 0.42, wall_t * 0.72, 0.34, region, u_scale=0.14,
                )


def add_vigas_along_side(bm, uv_layer, cx, cy, z_beam, span, axis="X", out_dir=1.0, count=5, protrude=0.26, radius=0.09, segs=6):
    """Ueberstehende Zedern-Dachbalkenkoepfe (Vigas) mit Jahresring-Stirn."""
    for i in range(count):
        t = (i + 0.5) / count - 0.5
        offset = t * (span - 0.6)
        if axis == "X":
            p0 = (cx + offset, cy - out_dir * 0.10, z_beam)
            p1 = (cx + offset, cy + out_dir * protrude, z_beam)
        else:
            p0 = (cx - out_dir * 0.10, cy + offset, z_beam)
            p1 = (cx + out_dir * protrude, cy + offset, z_beam)
        add_cylinder(
            bm, uv_layer, p0, p1, radius, radius * 0.94, segs=segs,
            region_key="cedar_timber", cap0=False, cap1=True, cap1_region="vigas_log_end",
        )


def add_exterior_stairs(bm, uv_layer, x0, y0, z0, x1, y1, z1, width=0.95, steps=9, lod=0, region="fired_brick_upper"):
    """Gemauerte Aussentreppe von (x0,y0,z0) nach (x1,y1,z1) inkl. -0.50 m Sockel."""
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    if lod >= 2:
        # Kompakte Treppenrampe in LOD2/LOD3
        mx, my = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
        sx = abs(dx) + width if abs(dx) > abs(dy) else width
        sy = abs(dy) + width if abs(dy) >= abs(dx) else width
        add_battered_prism(bm, uv_layer, mx, my, -0.50, 0.5 * (z0 + z1), sx, sy, sx * 0.9, sy * 0.9, region, u_scale=0.35)
        return

    n_st = steps if lod == 0 else max(4, steps // 2)
    step_len_x = dx / n_st
    step_len_y = dy / n_st
    is_x = abs(dx) >= abs(dy)
    for i in range(n_st):
        cx = x0 + (i + 0.5) * step_len_x
        cy = y0 + (i + 0.5) * step_len_y
        zt = z0 + (i + 1) * (dz / n_st)
        sx = abs(step_len_x) + 0.04 if is_x else width
        sy = width if is_x else abs(step_len_y) + 0.04
        add_battered_prism(
            bm, uv_layer, cx, cy, -0.50, zt,
            sx + 0.08, sy + 0.08, sx, sy,
            "fired_brick_plinth" if i == 0 else region, u_scale=0.4,
        )


def add_reed_pergola(bm, uv_layer, cx, cy, z_floor, z_roof, sx, sy, lod=0, region_cover="reed_pergola", poles_corners=True):
    """Schilf-Pergola / Vordach aus Zedernpfosten, Querbalken & duenner zweiseitiger Schilfmatte."""
    if lod >= 2:
        add_battered_prism(bm, uv_layer, cx, cy, z_roof - 0.05, z_roof + 0.04, sx, sy, sx, sy, region_cover, u_scale=0.5)
        return
    segs = 6 if lod == 0 else 4
    if poles_corners:
        for sx_s in (-1.0, 1.0):
            for sy_s in (-1.0, 1.0):
                px = cx + sx_s * (sx * 0.5 - 0.14)
                py = cy + sy_s * (sy * 0.5 - 0.14)
                add_cylinder(bm, uv_layer, (px, py, z_floor - 0.05), (px, py, z_roof), 0.075, 0.065, segs=segs, region_key="cedar_timber", cap0=False)
    # Tragbalken
    for sy_s in (-1.0, 1.0):
        py = cy + sy_s * (sy * 0.5 - 0.14)
        add_cylinder(bm, uv_layer, (cx - sx * 0.5, py, z_roof - 0.04), (cx + sx * 0.5, py, z_roof - 0.04), 0.07, 0.07, segs=segs, region_key="cedar_timber")
    # Schilfdach-Platte (3 cm stark -> beidseitig sichtbar ohne doubleSided)
    add_battered_prism(bm, uv_layer, cx, cy, z_roof, z_roof + 0.05, sx + 0.12, sy + 0.12, sx + 0.10, sy + 0.10, region_cover, u_scale=0.5)


def add_sloped_awning(bm, uv_layer, cx, cy, z_back, z_front, width, depth, facing="+Y", lod=0, region="woven_awning"):
    """Gespannter Markisen-Schattenbaldachin mit Zedernstuetzen & geneigtem Webtuch."""
    dir_y = 1.0 if facing == "+Y" else -1.0
    y_back = cy
    y_front = cy + dir_y * depth
    if lod <= 1:
        segs = 6 if lod == 0 else 4
        for sx_s in (-1.0, 1.0):
            px = cx + sx_s * (width * 0.5 - 0.12)
            add_cylinder(bm, uv_layer, (px, y_front - dir_y * 0.12, 0.0), (px, y_front - dir_y * 0.12, z_front), 0.065, 0.058, segs=segs, region_key="cedar_timber", cap0=False)
        add_cylinder(bm, uv_layer, (cx - width * 0.5, y_front - dir_y * 0.12, z_front), (cx + width * 0.5, y_front - dir_y * 0.12, z_front), 0.055, 0.055, segs=segs, region_key="cedar_timber")

    # Geneigte dicke Tuchbahn (3 cm Dicke mit leichter Woelbung)
    t = 0.035
    nx = 4 if lod == 0 else 1
    hx = width * 0.5
    for ix in range(nx):
        x0 = cx - hx + (ix / nx) * width
        x1 = cx - hx + ((ix + 1) / nx) * width
        sag0 = -0.04 * math.sin(math.pi * (ix / nx))
        sag1 = -0.04 * math.sin(math.pi * ((ix + 1) / nx))
        ym = 0.5 * (y_back + y_front)
        zm = 0.5 * (z_back + z_front) - 0.05
        # 2 Streifen pro Segment fuer leichten Durchhang in der Mitte
        pts_b = [(x0, y_back, z_back), (x1, y_back, z_back), (x1, ym, zm + sag1), (x0, ym, zm + sag0)]
        pts_f = [(x0, ym, zm + sag0), (x1, ym, zm + sag1), (x1, y_front, z_front), (x0, y_front, z_front)]
        for quad in (pts_b, pts_f):
            top_v = [bm.verts.new((p[0], p[1], p[2])) for p in quad]
            bot_v = [bm.verts.new((p[0], p[1], p[2] - t)) for p in quad]
            f_top = bm.faces.new(top_v)
            f_bot = bm.faces.new(list(reversed(bot_v)))
            faces = [f_top, f_bot]
            for k in range(4):
                kn = (k + 1) % 4
                faces.append(bm.faces.new((bot_v[k], bot_v[kn], top_v[kn], top_v[k])))
            _apply_box_uv_to_faces(faces, uv_layer, region, u_scale=0.5, v_fit=True)


def add_lathe_vessel(bm, uv_layer, cx, cy, z0, profile_rz, segs=8, region="fired_brick_upper"):
    """Erzeugt rotationssymmetrische Amphoren, Backoefen (Tannur), Kuppeln oder Brunnen."""
    rings = []
    for r, z in profile_rz:
        if r <= 1e-4:
            rings.append([bm.verts.new((cx, cy, z0 + z))])
        else:
            ring = []
            for i in range(segs):
                ang = 2.0 * math.pi * i / segs
                ring.append(bm.verts.new((cx + r * math.cos(ang), cy + r * math.sin(ang), z0 + z)))
            rings.append(ring)

    faces = []
    n_rings = len(rings)
    for ri in range(n_rings - 1):
        r_a, r_b = rings[ri], rings[ri + 1]
        v0 = ri / max(1, n_rings - 1)
        v1 = (ri + 1) / max(1, n_rings - 1)
        if len(r_a) == 1 and len(r_b) > 1:
            for i in range(segs):
                j = (i + 1) % segs
                f = bm.faces.new((r_a[0], r_b[i], r_b[j]))
                faces.append(f)
                for lp, uv in zip(f.loops, [_map_uv(region, 0.5, v0), _map_uv(region, i / segs, v1), _map_uv(region, (i + 1) / segs, v1)]):
                    lp[uv_layer].uv = uv
        elif len(r_a) > 1 and len(r_b) == 1:
            for i in range(segs):
                j = (i + 1) % segs
                f = bm.faces.new((r_a[i], r_b[0], r_a[j]))
                faces.append(f)
                for lp, uv in zip(f.loops, [_map_uv(region, i / segs, v0), _map_uv(region, 0.5, v1), _map_uv(region, (i + 1) / segs, v0)]):
                    lp[uv_layer].uv = uv
        elif len(r_a) > 1 and len(r_b) > 1:
            for i in range(segs):
                j = (i + 1) % segs
                f = bm.faces.new((r_a[i], r_a[j], r_b[j], r_b[i]))
                faces.append(f)
                for lp, uv in zip(f.loops, [
                    _map_uv(region, i / segs, v0),
                    _map_uv(region, (i + 1) / segs, v0),
                    _map_uv(region, (i + 1) / segs, v1),
                    _map_uv(region, i / segs, v1),
                ]):
                    lp[uv_layer].uv = uv
    return faces


def add_amphora(bm, uv_layer, cx, cy, z0, scale=1.0, segs=8):
    prof = [
        (0.11 * scale, 0.00),
        (0.22 * scale, 0.24 * scale),
        (0.24 * scale, 0.42 * scale),
        (0.10 * scale, 0.62 * scale),
        (0.13 * scale, 0.72 * scale),
        (0.08 * scale, 0.70 * scale),
    ]
    add_lathe_vessel(bm, uv_layer, cx, cy, z0, prof, segs=segs, region="fired_brick_upper")


def add_tannur_oven(bm, uv_layer, cx, cy, z0, scale=1.0, segs=10):
    prof = [
        (0.46 * scale, 0.00),
        (0.42 * scale, 0.35 * scale),
        (0.32 * scale, 0.75 * scale),
        (0.24 * scale, 0.92 * scale),
        (0.18 * scale, 0.90 * scale),
        (0.16 * scale, 0.45 * scale),
    ]
    add_lathe_vessel(bm, uv_layer, cx, cy, z0, prof, segs=segs, region="mudbrick_plaster")
    # Dunkle Aschen-/Feuer-Oeffnung unten
    add_battered_prism(bm, uv_layer, cx, cy + 0.36 * scale, z0, z0 + 0.24 * scale, 0.24 * scale, 0.16 * scale, 0.18 * scale, 0.12 * scale, "damp_plinth", u_scale=0.8)


def add_wooden_ladder(bm, uv_layer, cx, cy_bot, z_bot, cy_top, z_top, width=0.52, rungs=7, lod=0):
    if lod >= 2:
        return
    segs = 6 if lod == 0 else 4
    hw = width * 0.5
    for sx_s in (-1.0, 1.0):
        add_cylinder(bm, uv_layer, (cx + sx_s * hw, cy_bot, z_bot), (cx + sx_s * hw, cy_top, z_top), 0.04, 0.038, segs=segs, region_key="cedar_timber")
    n_r = rungs if lod == 0 else max(3, rungs // 2)
    for i in range(n_r):
        t = (i + 0.6) / (n_r + 0.2)
        ry = cy_bot * (1.0 - t) + cy_top * t
        rz = z_bot * (1.0 - t) + z_top * t
        add_cylinder(bm, uv_layer, (cx - hw, ry, rz), (cx + hw, ry, rz), 0.028, 0.028, segs=segs, region_key="cedar_timber")


def add_courtyard_well(bm, uv_layer, cx, cy, z0, lod=0):
    segs = 10 if lod == 0 else 6
    prof = [
        (0.68, 0.00), (0.65, 0.58), (0.58, 0.60), (0.48, 0.58), (0.46, 0.10),
    ]
    add_lathe_vessel(bm, uv_layer, cx, cy, z0, prof, segs=segs, region="fired_brick_plinth")
    if lod == 0:
        for sgn in (-1.0, 1.0):
            add_cylinder(bm, uv_layer, (cx + sgn * 0.58, cy, z0 + 0.55), (cx + sgn * 0.58, cy, z0 + 1.55), 0.055, 0.05, segs=6, region_key="cedar_timber")
        add_cylinder(bm, uv_layer, (cx - 0.64, cy, z0 + 1.50), (cx + 0.64, cy, z0 + 1.50), 0.06, 0.06, segs=6, region_key="cedar_timber")


def add_courtyard_shell(bm, uv_layer, sx, sy, z_top, wall_t=0.90, plinth_z=-0.50, z_plinth_top=0.38, wall_region="mudbrick_plaster"):
    """Baut 4 umlaufende Aussenfluegel um einen offenen Innenhof (Atrium)."""
    # Vorne (+Y) & Hinten (-Y) volle Breite
    wing_y = wall_t
    add_wall_with_plinth(bm, uv_layer, 0.0, +(sy * 0.5 - wing_y * 0.5), z_plinth_top, z_top, sx, wing_y, batter=0.07, plinth_z=plinth_z, wall_region=wall_region)
    add_wall_with_plinth(bm, uv_layer, 0.0, -(sy * 0.5 - wing_y * 0.5), z_plinth_top, z_top, sx, wing_y, batter=0.07, plinth_z=plinth_z, wall_region=wall_region)
    # Links (-X) & Rechts (+X) zwischen Vorne/Hinten
    inner_y = max(0.5, sy - 2.0 * wing_y)
    add_wall_with_plinth(bm, uv_layer, -(sx * 0.5 - wing_y * 0.5), 0.0, z_plinth_top, z_top, wing_y, inner_y, batter=0.07, plinth_z=plinth_z, wall_region=wall_region)
    add_wall_with_plinth(bm, uv_layer, +(sx * 0.5 - wing_y * 0.5), 0.0, z_plinth_top, z_top, wing_y, inner_y, batter=0.07, plinth_z=plinth_z, wall_region=wall_region)
    # Hofboden (gepflastert mit Royal/Alley Stone auf Z=0.04)
    add_battered_prism(bm, uv_layer, 0.0, 0.0, -0.50, 0.05, sx - 1.2, sy - 1.2, sx - 1.2, sy - 1.2, "alley_mud_road", u_scale=0.35)


# ==============================================================================
# 1. FUENF STAEDTISCHE WOHNHAEUSER (ur_courtyard_house_01 .. _05)
# ==============================================================================

def build_ur_courtyard_house_01(bm, uv_layer, lod):
    """01: Klassisches zweistoeckiges Atriumhaus mit Holzgalerie, Bruestung & Aussentreppe."""
    sx, sy, h = 9.4, 8.8, 5.8
    if lod == 3:
        add_battered_prism(bm, uv_layer, 0.0, 0.0, -0.50, h + 0.45, sx + 0.15, sy + 0.15, sx - 0.18, sy - 0.18, "mudbrick_plaster", u_scale=0.3)
        return
    if lod == 2:
        add_wall_with_plinth(bm, uv_layer, 0.0, 0.0, 0.38, h, sx, sy, batter=0.09)
        add_parapet_with_merlons(bm, uv_layer, 0.0, 0.0, h, sx - 0.16, sy - 0.16, wall_t=0.36, h_parapet=0.52, add_merlons=False)
        add_exterior_stairs(bm, uv_layer, -sx * 0.5 - 0.48, -1.8, 0.0, -sx * 0.5 - 0.48, +1.8, 3.0, width=0.95, lod=2)
        return

    # Zweistoeckige Atrium-Schale (Fluegelstaerke 1.45 m -> echter Innenhof)
    add_courtyard_shell(bm, uv_layer, sx, sy, h, wall_t=1.55)
    add_parapet_with_merlons(bm, uv_layer, 0.0, 0.0, h, sx - 0.14, sy - 0.14, wall_t=0.36, h_parapet=0.55, add_merlons=(lod == 0), merlon_h=0.26)
    # Eingangsportal +Y
    add_recessed_door(bm, uv_layer, 0.0, sy * 0.5, 0.0, 1.35, 2.25, facing="+Y")
    # Ueberdachte Holzgalerie im Innenhof (OG bei Z=2.95)
    add_reed_pergola(bm, uv_layer, 0.0, -1.5, 0.05, 3.10, sx - 3.3, 1.45, lod=lod, region_cover="cedar_timber")
    # Gemauerte Aussentreppe an Westwand (-X) bis zum Obergeschoss-Absatz
    add_exterior_stairs(bm, uv_layer, -sx * 0.5 - 0.52, -2.1, 0.0, -sx * 0.5 - 0.52, +2.0, 3.05, width=0.95, steps=9, lod=lod)

    if lod == 0:
        add_vigas_along_side(bm, uv_layer, 0.0, +sy * 0.5 - 0.04, h - 0.22, sx - 0.6, axis="X", out_dir=1.0, count=7)
        add_vigas_along_side(bm, uv_layer, 0.0, -sy * 0.5 + 0.04, h - 0.22, sx - 0.6, axis="X", out_dir=-1.0, count=7)
        for wx in (-2.6, +2.6):
            add_window_niche(bm, uv_layer, wx, sy * 0.5 - 0.04, 3.85, 0.55, 0.72, facing="+Y")
        add_amphora(bm, uv_layer, 1.35, sy * 0.5 + 0.42, 0.0, scale=0.85, segs=8)
        add_amphora(bm, uv_layer, 1.85, sy * 0.5 + 0.38, 0.0, scale=0.72, segs=8)


def build_ur_courtyard_house_02(bm, uv_layer, lod):
    """02: L-foermiges Eck-Wohnhaus mit auskragender Dachterrasse, Schilf-Pergola & Vigas."""
    if lod == 3:
        add_battered_prism(bm, uv_layer, -1.2, 0.0, -0.50, 6.4, 7.2, 9.4, 6.9, 9.1, "mudbrick_plaster", u_scale=0.3)
        add_battered_prism(bm, uv_layer, +2.8, -2.0, -0.50, 3.8, 4.4, 5.4, 4.2, 5.2, "mudbrick_plaster", u_scale=0.3)
        return
    if lod == 2:
        add_wall_with_plinth(bm, uv_layer, -1.5, 0.0, 0.38, 6.1, 6.6, 9.2, batter=0.08)
        add_wall_with_plinth(bm, uv_layer, +2.9, -1.8, 0.38, 3.5, 4.4, 5.4, batter=0.07)
        add_parapet_with_merlons(bm, uv_layer, -1.5, 0.0, 6.1, 6.4, 9.0, wall_t=0.32, h_parapet=0.45, add_merlons=False)
        return

    # Hauptfluegel zweistoeckig (-X) + niedrigerer Seitenfluegel (+X, -Y)
    add_wall_with_plinth(bm, uv_layer, -1.5, 0.0, 0.38, 6.1, 6.6, 9.2, batter=0.08)
    add_wall_with_plinth(bm, uv_layer, +2.9, -1.8, 0.38, 3.4, 4.6, 5.4, batter=0.07)
    # Auskragender Zedernbalken-Erker / Dachterrasse ueber dem Eckhof (+X, +Y)
    add_battered_prism(bm, uv_layer, +2.2, +2.1, 3.30, 3.62, 3.8, 3.6, 3.9, 3.7, "cedar_timber", u_scale=0.45)
    add_parapet_with_merlons(bm, uv_layer, -1.5, 0.0, 6.1, 6.44, 9.04, wall_t=0.34, h_parapet=0.50, add_merlons=(lod == 0), merlon_h=0.25)
    add_parapet_with_merlons(bm, uv_layer, +2.9, -1.8, 3.4, 4.46, 5.26, wall_t=0.30, h_parapet=0.45, add_merlons=False)
    # Schilf-Pergola auf der Dachterrasse
    add_reed_pergola(bm, uv_layer, +2.8, -1.6, 3.4, 5.45, 3.6, 4.0, lod=lod, region_cover="reed_pergola")
    # Eck-Stuetzpfosten unter dem Erker
    for px in (+0.6, +3.7):
        add_cylinder(bm, uv_layer, (px, +3.6, 0.0), (px, +3.6, 3.35), 0.11, 0.09, segs=(8 if lod == 0 else 4), region_key="cedar_timber")
    # Tuer im Eckhof (+Y)
    add_recessed_door(bm, uv_layer, +2.4, +0.90, 0.0, 1.25, 2.15, facing="+Y")

    if lod == 0:
        add_vigas_along_side(bm, uv_layer, -1.5, +4.55, 5.88, 6.0, axis="X", out_dir=1.0, count=6, protrude=0.30)
        add_vigas_along_side(bm, uv_layer, -4.75, 0.0, 5.88, 8.2, axis="Y", out_dir=-1.0, count=7, protrude=0.30)
        add_vigas_along_side(bm, uv_layer, +2.9, +0.86, 3.18, 3.8, axis="X", out_dir=1.0, count=4, protrude=0.25)
        for wz in (1.9, 4.3):
            add_window_niche(bm, uv_layer, -1.5, +4.56, wz, 0.58, 0.68, facing="+Y")
        add_wooden_ladder(bm, uv_layer, +1.1, -0.5, 3.4, +0.9, 6.2, width=0.52, rungs=7, lod=0)


def build_ur_courtyard_house_03(bm, uv_layer, lod):
    """03: Wohlhabendes Kaufmanns-Wohnhaus mit gekalktem Portal, Innenhof-Brunnen & Dachzinnen."""
    sx, sy, h = 10.6, 9.6, 6.2
    if lod == 3:
        add_battered_prism(bm, uv_layer, 0.0, 0.0, -0.50, h + 0.72, sx + 0.16, sy + 0.16, sx - 0.20, sy - 0.20, "gypsum_temple", u_scale=0.3)
        return
    if lod == 2:
        add_wall_with_plinth(bm, uv_layer, 0.0, 0.0, 0.38, h, sx, sy, batter=0.08, wall_region="gypsum_temple")
        add_battered_prism(bm, uv_layer, 0.0, sy * 0.5 + 0.35, -0.50, 4.2, 3.4, 0.9, 3.2, 0.85, "gypsum_temple", u_scale=0.4)
        add_parapet_with_merlons(bm, uv_layer, 0.0, 0.0, h, sx - 0.16, sy - 0.16, wall_t=0.38, h_parapet=0.55, region="gypsum_temple", add_merlons=False)
        return

    add_courtyard_shell(bm, uv_layer, sx, sy, h, wall_t=1.75, wall_region="gypsum_temple")
    # Gekalktes Eingangsportal (+Y) mit Vorsprung & Nischenpilastern (Portal hoehe 4.65 m > Fries 4.30 m -> kein Z-Fighting!)
    add_wall_with_plinth(bm, uv_layer, 0.0, sy * 0.5 + 0.35, 0.38, 4.65, 3.5, 0.95, batter=0.06, wall_region="gypsum_temple", u_scale=0.14)
    add_recessed_door(bm, uv_layer, 0.0, sy * 0.5 + 0.82, 0.0, 1.50, 2.45, facing="+Y", frame_region="lapis_frieze")
    # Innenhof-Brunnen (mittig im Hof sichtbar & funktional)
    add_courtyard_well(bm, uv_layer, 0.0, 0.0, 0.05, lod=lod)
    # Bruestung & Dachzinnen
    add_parapet_with_merlons(bm, uv_layer, 0.0, 0.0, h, sx - 0.14, sy - 0.14, wall_t=0.38, h_parapet=0.52, merlon_step=1.05, region="gypsum_temple", add_merlons=True, merlon_h=0.34)
    # Dekoratives Lapislazuli-Friesband ueber dem Portal (leicht vorspringend 3.60 x 1.06)
    add_battered_prism(bm, uv_layer, 0.0, sy * 0.5 + 0.35, 3.85, 4.28, 3.60, 1.06, 3.60, 1.06, "lapis_frieze", u_scale=0.45)

    if lod == 0:
        add_vigas_along_side(bm, uv_layer, 0.0, +sy * 0.5 - 0.04, h - 0.22, sx - 0.8, axis="X", out_dir=1.0, count=8)
        add_vigas_along_side(bm, uv_layer, 0.0, -sy * 0.5 + 0.04, h - 0.22, sx - 0.8, axis="X", out_dir=-1.0, count=8)
        for wx in (-3.2, +3.2):
            add_window_niche(bm, uv_layer, wx, sy * 0.5 - 0.04, 1.8, 0.62, 0.78, facing="+Y")
            add_window_niche(bm, uv_layer, wx, sy * 0.5 - 0.04, 4.2, 0.62, 0.78, facing="+Y")


def build_ur_courtyard_house_04(bm, uv_layer, lod):
    """04: Handwerker-/Laden-Wohnhaus mit Ocker-Markise, Werkbank & Amphoren-Auslage."""
    sx, sy, h = 9.0, 8.4, 5.5
    if lod == 3:
        add_battered_prism(bm, uv_layer, 0.0, 0.0, -0.50, h + 0.45, sx + 0.16, sy + 0.16, sx - 0.16, sy - 0.16, "mudbrick_plaster", u_scale=0.3)
        return
    if lod == 2:
        add_wall_with_plinth(bm, uv_layer, 0.0, 0.0, 0.38, h, sx, sy, batter=0.08)
        add_sloped_awning(bm, uv_layer, 0.0, sy * 0.5, 3.15, 2.45, 6.2, 2.2, facing="+Y", lod=2)
        add_parapet_with_merlons(bm, uv_layer, 0.0, 0.0, h, sx - 0.16, sy - 0.16, wall_t=0.34, h_parapet=0.48, add_merlons=False)
        return

    add_courtyard_shell(bm, uv_layer, sx, sy, h, wall_t=1.45)
    add_parapet_with_merlons(bm, uv_layer, 0.0, 0.0, h, sx - 0.14, sy - 0.14, wall_t=0.34, h_parapet=0.48, add_merlons=(lod == 0), merlon_h=0.22)
    add_recessed_door(bm, uv_layer, -1.6, sy * 0.5, 0.0, 1.35, 2.25, facing="+Y")
    # Strassen-Vordach (Ocker-/Terrakotta-Markise) vor der Ladenfront (+Y)
    add_sloped_awning(bm, uv_layer, +0.4, sy * 0.5, 3.18, 2.42, 6.4, 2.25, facing="+Y", lod=lod)

    # Hoelzerne Werkbank unter der Markise
    add_battered_prism(bm, uv_layer, +1.6, sy * 0.5 + 0.85, 0.72, 0.84, 2.4, 0.82, 2.4, 0.82, "cedar_timber", u_scale=0.5)
    for lx in (+0.55, +2.65):
        for ly in (sy * 0.5 + 0.55, sy * 0.5 + 1.15):
            add_battered_prism(bm, uv_layer, lx, ly, 0.0, 0.72, 0.12, 0.12, 0.12, 0.12, "cedar_timber", u_scale=0.8)

    if lod == 0:
        add_vigas_along_side(bm, uv_layer, 0.0, +sy * 0.5 - 0.04, h - 0.22, sx - 0.6, axis="X", out_dir=1.0, count=6)
        add_vigas_along_side(bm, uv_layer, 0.0, -sy * 0.5 + 0.04, h - 0.22, sx - 0.6, axis="X", out_dir=-1.0, count=6)
        # Amphoren-Auslage auf dem Boden & Werkbank
        for ax, ay, az, sc in (
            (+3.2, sy * 0.5 + 0.6, 0.0, 0.92),
            (+3.6, sy * 0.5 + 1.1, 0.0, 0.78),
            (+2.9, sy * 0.5 + 1.3, 0.0, 0.84),
            (+1.1, sy * 0.5 + 0.85, 0.84, 0.55),
            (+1.9, sy * 0.5 + 0.85, 0.84, 0.62),
        ):
            add_amphora(bm, uv_layer, ax, ay, az, scale=sc, segs=8)


def build_ur_courtyard_house_05(bm, uv_layer, lod):
    """05: Verschachteltes Doppel-Terrassen-Wohnhaus mit Dach-Windfang-Pavillon, Tannur & Leiter."""
    if lod == 3:
        add_battered_prism(bm, uv_layer, -0.8, 0.0, -0.50, 6.2, 8.6, 8.8, 8.3, 8.5, "mudbrick_plaster", u_scale=0.3)
        add_battered_prism(bm, uv_layer, -1.2, -1.2, 6.0, 8.2, 3.8, 3.6, 3.6, 3.4, "reed_pergola", u_scale=0.4)
        return
    if lod == 2:
        add_wall_with_plinth(bm, uv_layer, -1.4, 0.0, 0.38, 6.0, 6.4, 8.6, batter=0.08)
        add_wall_with_plinth(bm, uv_layer, +3.1, 0.2, 0.38, 3.5, 4.0, 7.2, batter=0.07)
        add_reed_pergola(bm, uv_layer, -1.4, -0.8, 6.0, 8.1, 3.8, 3.8, lod=2)
        return

    # Unterer Seitenfluegel (+X, Z=3.5) + hoeherer Hauptfluegel (-X, Z=6.0)
    add_wall_with_plinth(bm, uv_layer, -1.4, 0.0, 0.38, 6.0, 6.4, 8.6, batter=0.08)
    add_wall_with_plinth(bm, uv_layer, +3.1, 0.2, 0.38, 3.45, 4.0, 7.2, batter=0.07)
    add_parapet_with_merlons(bm, uv_layer, -1.4, 0.0, 6.0, 6.24, 8.44, wall_t=0.32, h_parapet=0.48, add_merlons=(lod == 0), merlon_h=0.24)
    add_parapet_with_merlons(bm, uv_layer, +3.1, 0.2, 3.45, 3.86, 7.06, wall_t=0.30, h_parapet=0.44, add_merlons=False)
    # Dach-Windfang-Pavillon (luftiger Schilf-/Zedern-Aufbau auf oberer Terrasse)
    add_reed_pergola(bm, uv_layer, -1.4, -0.6, 6.0, 8.15, 3.8, 3.8, lod=lod, region_cover="reed_pergola")
    # Windfang-Rueckwand auf dem Dach
    add_battered_prism(bm, uv_layer, -1.4, -2.35, 6.0, 8.10, 3.6, 0.28, 3.5, 0.26, "mudbrick_plaster", u_scale=0.4)
    # Tuer im Erdgeschoss (+Y)
    add_recessed_door(bm, uv_layer, +2.9, +3.80, 0.0, 1.25, 2.15, facing="+Y")
    # Tannur-Lehmbackofen auf unterer Terrasse (+X, Z=3.45)
    add_tannur_oven(bm, uv_layer, +3.1, -1.4, 3.45, scale=1.0, segs=(10 if lod == 0 else 6))
    # Aussenleiter von unterer Terrasse zur oberen Terrasse & von Boden zur unteren Terrasse
    add_wooden_ladder(bm, uv_layer, +1.55, +2.6, 3.45, +0.95, 6.25, width=0.52, rungs=7, lod=lod)
    add_wooden_ladder(bm, uv_layer, +4.95, -2.1, 0.0, +4.45, 3.65, width=0.52, rungs=8, lod=lod)

    if lod == 0:
        add_vigas_along_side(bm, uv_layer, -1.4, +4.25, 5.78, 5.8, axis="X", out_dir=1.0, count=5)
        add_vigas_along_side(bm, uv_layer, +3.1, +3.75, 3.25, 3.4, axis="X", out_dir=1.0, count=3)
        add_amphora(bm, uv_layer, +2.2, -2.2, 3.45, scale=0.80, segs=8)


# ==============================================================================
# 2. FUENF DORF- & VORSTADT-LEHMZIEGELHAEUSER (ur_mudbrick_small_01 .. _05)
# ==============================================================================

def build_ur_mudbrick_small_01(bm, uv_layer, lod):
    """Small 01: Kompaktes Einraumhaus mit Aussentreppe & Schilf-Vorbau."""
    sx, sy, h = 5.4, 4.8, 3.4
    if lod == 3:
        add_battered_prism(bm, uv_layer, 0.0, 0.0, -0.50, h + 0.4, sx + 0.14, sy + 0.14, sx - 0.16, sy - 0.16, "mudbrick_plaster", u_scale=0.35)
        return
    if lod == 2:
        add_wall_with_plinth(bm, uv_layer, 0.0, 0.0, 0.36, h, sx, sy, batter=0.07)
        add_reed_pergola(bm, uv_layer, 0.0, sy * 0.5 + 0.9, 0.0, 2.55, 3.4, 1.8, lod=2)
        return

    add_wall_with_plinth(bm, uv_layer, 0.0, 0.0, 0.36, h, sx, sy, batter=0.07)
    add_parapet_with_merlons(bm, uv_layer, 0.0, 0.0, h, sx - 0.14, sy - 0.14, wall_t=0.28, h_parapet=0.40, add_merlons=False)
    add_recessed_door(bm, uv_layer, -0.4, sy * 0.5, 0.0, 1.05, 1.95, facing="+Y")
    add_reed_pergola(bm, uv_layer, +0.2, sy * 0.5 + 0.95, 0.0, 2.55, 3.6, 1.85, lod=lod)
    add_exterior_stairs(bm, uv_layer, -sx * 0.5 - 0.45, -1.6, 0.0, -sx * 0.5 - 0.45, +1.5, h + 0.05, width=0.82, steps=8, lod=lod)
    if lod == 0:
        add_vigas_along_side(bm, uv_layer, 0.0, +sy * 0.5 - 0.04, h - 0.20, sx - 0.6, axis="X", out_dir=1.0, count=5)
        add_vigas_along_side(bm, uv_layer, 0.0, -sy * 0.5 + 0.04, h - 0.20, sx - 0.6, axis="X", out_dir=-1.0, count=5)
        add_amphora(bm, uv_layer, +1.5, sy * 0.5 + 0.55, 0.0, scale=0.82, segs=8)


def build_ur_mudbrick_small_02(bm, uv_layer, lod):
    """Small 02: Zweiteiliges Flachdachhaus mit angebautem Lehm-Backofen & kleiner Hofmauer."""
    if lod == 3:
        add_battered_prism(bm, uv_layer, 0.0, 0.0, -0.50, 3.7, 6.8, 5.2, 6.5, 4.9, "mudbrick_plaster", u_scale=0.35)
        return
    if lod == 2:
        add_wall_with_plinth(bm, uv_layer, -1.2, -0.4, 0.36, 3.7, 4.4, 4.6, batter=0.07)
        add_wall_with_plinth(bm, uv_layer, +2.0, -0.6, 0.36, 2.9, 2.6, 3.8, batter=0.06)
        return

    add_wall_with_plinth(bm, uv_layer, -1.2, -0.5, 0.36, 3.7, 4.4, 4.5, batter=0.07)
    add_wall_with_plinth(bm, uv_layer, +2.1, -0.7, 0.36, 2.9, 2.8, 3.8, batter=0.06)
    add_parapet_with_merlons(bm, uv_layer, -1.2, -0.5, 3.7, 4.26, 4.36, wall_t=0.28, h_parapet=0.38, add_merlons=False)
    add_recessed_door(bm, uv_layer, -1.2, +1.75, 0.0, 1.05, 1.95, facing="+Y")
    # Kleine Hofmauer vorne rechts (+X, +Y)
    add_wall_with_plinth(bm, uv_layer, +3.3, +1.8, 0.36, 1.25, 0.42, 2.2, batter=0.04)
    add_wall_with_plinth(bm, uv_layer, +1.8, +2.75, 0.36, 1.25, 3.4, 0.42, batter=0.04)
    # Lehm-Backofen (Tannur) im Hofwinkel
    add_tannur_oven(bm, uv_layer, +2.0, +1.85, 0.0, scale=0.95, segs=(10 if lod == 0 else 6))
    if lod == 0:
        add_vigas_along_side(bm, uv_layer, -1.2, +1.71, 3.50, 3.8, axis="X", out_dir=1.0, count=4)
        add_vigas_along_side(bm, uv_layer, +2.1, +1.16, 2.72, 2.2, axis="X", out_dir=1.0, count=3)
        add_amphora(bm, uv_layer, -0.1, +2.15, 0.0, scale=0.78, segs=8)


def build_ur_mudbrick_small_03(bm, uv_layer, lod):
    """Small 03: Kleines Lager-/Handwerkerhaus mit Holz-Vordach & Amphoren."""
    sx, sy, h = 5.8, 4.9, 3.55
    if lod == 3:
        add_battered_prism(bm, uv_layer, 0.0, 0.0, -0.50, h + 0.4, sx + 0.14, sy + 0.14, sx - 0.16, sy - 0.16, "mudbrick_plaster", u_scale=0.35)
        return
    if lod == 2:
        add_wall_with_plinth(bm, uv_layer, 0.0, 0.0, 0.36, h, sx, sy, batter=0.07)
        add_sloped_awning(bm, uv_layer, 0.0, sy * 0.5, 2.55, 2.05, 4.6, 1.9, facing="+Y", lod=2, region="cedar_timber")
        return

    add_wall_with_plinth(bm, uv_layer, 0.0, 0.0, 0.36, h, sx, sy, batter=0.07)
    add_parapet_with_merlons(bm, uv_layer, 0.0, 0.0, h, sx - 0.14, sy - 0.14, wall_t=0.28, h_parapet=0.40, add_merlons=False)
    add_recessed_door(bm, uv_layer, -1.1, sy * 0.5, 0.0, 1.15, 2.00, facing="+Y")
    # Holz-Vordach (Zeder)
    add_sloped_awning(bm, uv_layer, 0.0, sy * 0.5, 2.60, 2.05, 4.8, 1.95, facing="+Y", lod=lod, region="cedar_timber")
    if lod == 0:
        add_vigas_along_side(bm, uv_layer, 0.0, +sy * 0.5 - 0.04, h - 0.20, sx - 0.6, axis="X", out_dir=1.0, count=5)
        for ax, ay, sc in ((+0.8, sy * 0.5 + 0.65, 0.90), (+1.45, sy * 0.5 + 0.58, 0.76), (+2.0, sy * 0.5 + 0.85, 0.84), (+1.2, sy * 0.5 + 1.25, 0.68)):
            add_amphora(bm, uv_layer, ax, ay, 0.0, scale=sc, segs=8)


def build_ur_mudbrick_small_04(bm, uv_layer, lod):
    """Small 04: Leicht versetztes Doppelraum-Haus mit Dach-Schilfpergola & Holzleiter."""
    if lod == 3:
        add_battered_prism(bm, uv_layer, 0.0, 0.0, -0.50, 3.85, 6.8, 5.4, 6.5, 5.1, "mudbrick_plaster", u_scale=0.35)
        return
    if lod == 2:
        add_wall_with_plinth(bm, uv_layer, -1.4, -0.35, 0.36, 3.8, 3.8, 4.5, batter=0.07)
        add_wall_with_plinth(bm, uv_layer, +1.5, +0.45, 0.36, 3.3, 3.4, 4.2, batter=0.07)
        return

    add_wall_with_plinth(bm, uv_layer, -1.4, -0.35, 0.36, 3.8, 3.8, 4.5, batter=0.07)
    add_wall_with_plinth(bm, uv_layer, +1.5, +0.45, 0.36, 3.3, 3.4, 4.2, batter=0.07)
    add_parapet_with_merlons(bm, uv_layer, -1.4, -0.35, 3.8, 3.66, 4.36, wall_t=0.26, h_parapet=0.38, add_merlons=False)
    add_parapet_with_merlons(bm, uv_layer, +1.5, +0.45, 3.3, 3.26, 4.06, wall_t=0.26, h_parapet=0.36, add_merlons=False)
    add_recessed_door(bm, uv_layer, +1.5, +2.55, 0.0, 1.05, 1.95, facing="+Y")
    add_reed_pergola(bm, uv_layer, +1.5, +0.4, 3.3, 5.05, 2.9, 3.2, lod=lod)
    add_wooden_ladder(bm, uv_layer, -0.2, +2.45, 0.0, -0.2, 4.05, width=0.50, rungs=8, lod=lod)
    if lod == 0:
        add_vigas_along_side(bm, uv_layer, -1.4, +1.86, 3.60, 3.2, axis="X", out_dir=1.0, count=4)
        add_vigas_along_side(bm, uv_layer, +1.5, +2.51, 3.12, 2.8, axis="X", out_dir=1.0, count=3)


def build_ur_mudbrick_small_05(bm, uv_layer, lod):
    """Small 05: Laendliches Gehoeft mit umfriedetem Kleinvieh-Maeuerchen & Schatten-Vordach."""
    if lod == 3:
        add_battered_prism(bm, uv_layer, -1.0, 0.0, -0.50, 3.55, 5.2, 5.6, 4.9, 5.3, "mudbrick_plaster", u_scale=0.35)
        return
    if lod == 2:
        add_wall_with_plinth(bm, uv_layer, -1.2, 0.0, 0.36, 3.5, 4.8, 5.4, batter=0.07)
        add_wall_with_plinth(bm, uv_layer, +2.4, 0.0, 0.36, 1.15, 2.8, 4.6, batter=0.04)
        return

    add_wall_with_plinth(bm, uv_layer, -1.2, 0.0, 0.36, 3.5, 4.8, 5.4, batter=0.07)
    add_parapet_with_merlons(bm, uv_layer, -1.2, 0.0, 3.5, 4.66, 5.26, wall_t=0.28, h_parapet=0.38, add_merlons=False)
    add_recessed_door(bm, uv_layer, -1.2, +2.70, 0.0, 1.05, 1.95, facing="+Y")
    # Umfriedetes Kleinvieh-Maeuerchen rechts (+X)
    add_wall_with_plinth(bm, uv_layer, +2.45, -2.15, 0.36, 1.15, 3.1, 0.38, batter=0.04)
    add_wall_with_plinth(bm, uv_layer, +2.45, +2.15, 0.36, 1.15, 3.1, 0.38, batter=0.04)
    add_wall_with_plinth(bm, uv_layer, +3.85, 0.0, 0.36, 1.15, 0.38, 4.6, batter=0.04)
    # Schatten-Vordach ueber dem Gehege
    add_reed_pergola(bm, uv_layer, +2.4, -0.8, 0.0, 2.35, 2.6, 2.5, lod=lod)
    if lod == 0:
        add_vigas_along_side(bm, uv_layer, -1.2, +2.66, 3.30, 4.2, axis="X", out_dir=1.0, count=5)
        add_battered_prism(bm, uv_layer, +2.4, +0.9, 0.0, 0.42, 1.3, 0.55, 1.25, 0.50, "cedar_timber", u_scale=0.6)


# ==============================================================================
# 3. MARSCHLAND-ARCHITEKTUR (ur_mudhif_hut)
# ==============================================================================

def build_ur_mudhif_hut(bm, uv_layer, lod):
    """Authentische sumerische Schilf-Bogenhuette (Mudhif) aus gebuendelten Schilfboegen."""
    length = 7.6
    half_w = 2.15
    h_ridge = 3.65

    # -0.50 m gestampfter Schilf-/Lehm-Inselsockel
    add_battered_prism(bm, uv_layer, 0.0, 0.0, -0.50, 0.16, half_w * 2.0 + 0.50, length + 0.50, half_w * 2.0 + 0.20, length + 0.20, "damp_plinth", u_scale=0.35)

    if lod == 3:
        # Ultraleichter Tunnel-Proxy
        add_battered_prism(bm, uv_layer, 0.0, 0.0, 0.16, h_ridge, half_w * 1.9, length, half_w * 0.65, length, "reed_pergola", u_scale=0.35)
        return

    n_len = 8 if lod <= 1 else 3
    n_arc = 10 if lod == 0 else (7 if lod == 1 else 5)

    # Gewaelmtes Tonnen-Dach aus gebuendeltem Schilf (Parabelbogen)
    rings = []
    for iy in range(n_len + 1):
        vy = -length * 0.5 + (iy / n_len) * length
        ring = []
        for ia in range(n_arc + 1):
            t = ia / n_arc
            ang = t * math.pi  # 0 (+X) .. pi (-X)
            vx = half_w * math.cos(ang)
            vz = 0.14 + (h_ridge - 0.14) * math.sin(ang) ** 0.85
            ring.append(bm.verts.new((vx, vy, vz)))
        rings.append(ring)

    roof_faces = []
    for iy in range(n_len):
        for ia in range(n_arc):
            f = bm.faces.new((rings[iy][ia], rings[iy + 1][ia], rings[iy + 1][ia + 1], rings[iy][ia + 1]))
            roof_faces.append(f)
            u0, u1 = ia / n_arc, (ia + 1) / n_arc
            v0, v1 = iy / n_len, (iy + 1) / n_len
            for lp, uv in zip(f.loops, [
                _map_uv("reed_pergola", v0, u0),
                _map_uv("reed_pergola", v1, u0),
                _map_uv("reed_pergola", v1, u1),
                _map_uv("reed_pergola", v0, u1),
            ]):
                lp[uv_layer].uv = uv

    # Stirnwaende vorne & hinten + Tor-Nische (+Y)
    for end_idx, y_sgn in ((0, -1.0), (n_len, 1.0)):
        r = rings[end_idx]
        mid_bot = bm.verts.new((0.0, y_sgn * length * 0.5, 0.14))
        end_faces = []
        for ia in range(n_arc):
            if y_sgn > 0:
                end_faces.append(bm.faces.new((mid_bot, r[ia], r[ia + 1])))
            else:
                end_faces.append(bm.faces.new((mid_bot, r[ia + 1], r[ia])))
        _apply_box_uv_to_faces(end_faces, uv_layer, "reed_pergola", u_scale=0.5, v_fit=True)

    # Dunkle Tuer-Nische vorne (+Y)
    add_battered_prism(bm, uv_layer, 0.0, length * 0.5 + 0.04, 0.16, 1.95, 1.25, 0.10, 0.95, 0.10, "carved_door", u_scale=0.9)

    # Plastische gebuendelte Schilfrippen-Boegen aussen (LOD0 / LOD1)
    if lod <= 1:
        n_ribs = 7 if lod == 0 else 4
        rib_segs = 6 if lod == 0 else 4
        for ir in range(n_ribs):
            ry = -length * 0.46 + (ir / max(1, n_ribs - 1)) * (length * 0.92)
            pts = []
            for ia in range(7):
                ang = (ia / 6.0) * math.pi
                pts.append((
                    (half_w + 0.07) * math.cos(ang),
                    ry,
                    0.12 + (h_ridge - 0.06) * math.sin(ang) ** 0.85,
                ))
            for k in range(len(pts) - 1):
                add_cylinder(bm, uv_layer, pts[k], pts[k + 1], 0.11, 0.10, segs=rib_segs, region_key="reed_pergola", cap0=(k == 0), cap1=(k == len(pts) - 2))


# ==============================================================================
# 4. MONUMENTAL- & INFRASTRUKTURBAUTEN
# ==============================================================================

def build_ur_ziggurat_temple(bm, uv_layer, lod):
    """Gestufte Ziggurat (Ur) mit 3 symmetrischen Freitreppen, Nischenpilastern, Weiss-Blau-Schrein & Opferfeuer."""
    if lod == 3:
        add_battered_prism(bm, uv_layer, 0.0, 0.0, -0.50, 4.6, 22.0, 18.0, 20.6, 16.6, "fired_brick_plinth", u_scale=0.22)
        add_battered_prism(bm, uv_layer, 0.0, -0.8, 4.6, 8.4, 15.2, 12.2, 14.2, 11.2, "mudbrick_plaster", u_scale=0.25)
        add_battered_prism(bm, uv_layer, 0.0, -1.2, 8.4, 11.4, 9.6, 7.6, 9.0, 7.0, "gypsum_temple", u_scale=0.35)
        add_battered_prism(bm, uv_layer, 0.0, -1.2, 11.4, 14.0, 5.4, 4.6, 5.2, 4.4, "lapis_frieze", u_scale=0.45)
        return

    # Stufe 1 (Basis): 22 x 18 m, Z=-0.50 .. +4.8 m (inkl. Sockelfeuchte & Nischenpilastern)
    add_wall_with_plinth(bm, uv_layer, 0.0, 0.0, 0.55, 4.8, 22.0, 18.0, batter=0.42, wall_region="fired_brick_upper", u_scale=0.09)
    add_parapet_with_merlons(bm, uv_layer, 0.0, 0.0, 4.8, 21.6, 17.6, wall_t=0.45, h_parapet=0.52, region="fired_brick_upper", add_merlons=(lod == 0), merlon_h=0.28)

    # Stufe 2: 15.0 x 11.8 m, Z=4.8 .. 8.6 m
    add_battered_prism(bm, uv_layer, 0.0, -0.9, 4.8, 8.6, 15.0, 11.8, 14.1, 11.0, "mudbrick_plaster", u_scale=0.10)
    add_parapet_with_merlons(bm, uv_layer, 0.0, -0.9, 8.6, 14.0, 10.9, wall_t=0.38, h_parapet=0.45, region="mudbrick_plaster", add_merlons=False)

    # Stufe 3: 9.6 x 7.4 m, Z=8.6 .. 11.3 m
    add_battered_prism(bm, uv_layer, 0.0, -1.4, 8.6, 11.3, 9.6, 7.4, 9.0, 6.9, "fired_brick_upper", u_scale=0.12)

    # Weiss-blauer Gipsschrein mit Lapislazuli-Fries auf der Spitze (Z=11.3 .. 14.2 m)
    add_battered_prism(bm, uv_layer, 0.0, -1.5, 11.3, 13.7, 5.4, 4.4, 5.2, 4.2, "gypsum_temple", u_scale=0.45)
    add_battered_prism(bm, uv_layer, 0.0, -1.5, 13.55, 14.25, 5.45, 4.45, 5.45, 4.45, "lapis_frieze", u_scale=0.55)
    add_recessed_door(bm, uv_layer, 0.0, -1.5 + 2.15, 11.3, 1.35, 2.05, facing="+Y", frame_region="lapis_frieze")

    # 3 Symmetrische Monumental-Freitreppen an der +Y-Frontseite (Mittelachse + 2 Seitentreppen!)
    add_exterior_stairs(bm, uv_layer, 0.0, 12.8, 0.0, 0.0, 8.7, 4.85, width=2.4, steps=14, lod=lod, region="fired_brick_upper")
    add_exterior_stairs(bm, uv_layer, -7.8, 9.4, 0.0, -1.6, 9.4, 4.85, width=1.9, steps=13, lod=lod, region="fired_brick_upper")
    add_exterior_stairs(bm, uv_layer, +7.8, 9.4, 0.0, +1.6, 9.4, 4.85, width=1.9, steps=13, lod=lod, region="fired_brick_upper")
    # Treppenturm / Torhaus am Zusammenlauf (Z=0..6.4) + Treppe zur 2. & 3. Ebene
    add_battered_prism(bm, uv_layer, 0.0, 8.4, -0.50, 6.2, 3.6, 2.8, 3.3, 2.6, "fired_brick_upper", u_scale=0.14)
    add_exterior_stairs(bm, uv_layer, 0.0, 7.2, 4.8, 0.0, 4.5, 8.65, width=2.0, steps=10, lod=lod, region="fired_brick_upper")
    add_exterior_stairs(bm, uv_layer, 0.0, 3.8, 8.6, 0.0, 1.4, 11.35, width=1.7, steps=8, lod=lod, region="fired_brick_upper")

    # Tiefe sumerische Nischenpilaster rund um Stufe 1 & 2 (LOD0 / LOD1)
    if lod <= 1:
        n_pil = 6 if lod == 0 else 4
        for ip in range(n_pil):
            px = -9.6 + (ip + 0.5) * (19.2 / n_pil)
            if abs(px) > 2.2:
                add_battered_prism(bm, uv_layer, px, -9.05, 0.4, 4.75, 0.85, 0.42, 0.68, 0.30, "fired_brick_upper", u_scale=0.18)
                add_battered_prism(bm, uv_layer, px, +9.05, 0.4, 4.75, 0.85, 0.42, 0.68, 0.30, "fired_brick_upper", u_scale=0.18)
        for jp in range(n_pil - 1):
            py = -7.2 + (jp + 0.5) * (14.4 / (n_pil - 1))
            for sgn in (-1.0, 1.0):
                add_battered_prism(bm, uv_layer, sgn * 11.0, py, 0.4, 4.75, 0.42, 0.85, 0.30, 0.68, "fired_brick_upper", u_scale=0.18)

    # Zwei Opferfeuer-Becken aus Zinnbronze vor dem Gipfelschrein (LOD0 / LOD1)
    if lod <= 1:
        b_segs = 10 if lod == 0 else 6
        for sgn in (-1.0, 1.0):
            bx, by = sgn * 1.9, +1.05
            add_battered_prism(bm, uv_layer, bx, by, 11.3, 12.15, 0.72, 0.72, 0.62, 0.62, "royal_stone_road", u_scale=0.5)
            prof_bowl = [(0.22, 0.0), (0.48, 0.32), (0.52, 0.42), (0.38, 0.40), (0.18, 0.16)]
            add_lathe_vessel(bm, uv_layer, bx, by, 12.15, prof_bowl, segs=b_segs, region="tin_bronze")


def build_ur_city_gate(bm, uv_layer, lod):
    """Doppelturm-Stadttor mit Stufenzinnen, tiefem Torbogen, Bronze-Zederntoren & Lapislazuli-Band."""
    if lod == 3:
        add_battered_prism(bm, uv_layer, -4.4, 0.0, -0.50, 9.8, 5.2, 7.2, 4.6, 6.6, "fired_brick_plinth", u_scale=0.24)
        add_battered_prism(bm, uv_layer, +4.4, 0.0, -0.50, 9.8, 5.2, 7.2, 4.6, 6.6, "fired_brick_plinth", u_scale=0.24)
        add_battered_prism(bm, uv_layer, 0.0, 0.0, 4.8, 8.6, 5.0, 5.8, 4.8, 5.6, "lapis_frieze", u_scale=0.35)
        return

    # Linker & rechter Torturm (in 2 Ziegel-Lagen unterteilt fuer realistische Ziegelhoehe)
    for sgn in (-1.0, 1.0):
        tx = sgn * 4.5
        add_wall_with_plinth(bm, uv_layer, tx, 0.0, 0.60, 5.0, 5.0, 7.2, batter=0.14, wall_region="fired_brick_upper", u_scale=0.12)
        add_battered_prism(bm, uv_layer, tx, 0.0, 5.0, 9.4, 4.76, 6.96, 4.48, 6.68, "fired_brick_upper", u_scale=0.12)
        # Lapislazuli-Band oben unter Zinnen
        add_battered_prism(bm, uv_layer, tx, 0.0, 8.45, 9.05, 4.62, 6.82, 4.62, 6.82, "lapis_frieze", u_scale=0.45)
        # Stufenzinnen (in LOD2 deaktiviert -> <200 Tris)
        add_parapet_with_merlons(bm, uv_layer, tx, 0.0, 9.4, 4.46, 6.66, wall_t=0.42, h_parapet=0.55, merlon_step=1.15, region="fired_brick_upper", add_merlons=(lod <= 1), merlon_h=(0.45 if lod == 0 else 0.30))

    # Mittelbruecke ueber der Tordurchfahrt (Z=4.9 .. 8.5 m)
    add_battered_prism(bm, uv_layer, 0.0, 0.0, 4.85, 8.45, 4.4, 6.2, 4.2, 6.0, "fired_brick_upper", u_scale=0.12)
    add_battered_prism(bm, uv_layer, 0.0, 0.0, 7.55, 8.20, 4.45, 6.35, 4.45, 6.35, "lapis_frieze", u_scale=0.5)
    add_parapet_with_merlons(bm, uv_layer, 0.0, 0.0, 8.45, 4.2, 6.0, wall_t=0.38, h_parapet=0.50, region="fired_brick_upper", add_merlons=(lod == 0), merlon_h=0.38)

    # Gepflasterte Tordurchfahrt (Koenigsstrasse durch das Tor)
    add_battered_prism(bm, uv_layer, 0.0, 0.0, -0.50, 0.05, 4.4, 7.6, 4.4, 7.6, "royal_stone_road", u_scale=0.25, rot_uv=True)

    # Gestufter Torbogen-Keilstein & Bronzebeschlagene Zedern-Torfluegel
    if lod <= 1:
        for sgn in (-1.0, 1.0):
            # Leicht schraeg geoeffnete monumentale Zedern-Torfluegel mit Zinnbronze-Baendern
            ang = sgn * 0.22
            cx = sgn * 1.12
            cy = 1.6
            add_battered_prism(bm, uv_layer, cx, cy, 0.05, 4.70, 1.85, 0.22, 1.85, 0.22, "carved_door", u_scale=0.6)
            for bz in (0.95, 2.35, 3.85):
                add_battered_prism(bm, uv_layer, cx, cy + 0.02, bz, bz + 0.24, 1.88, 0.27, 1.88, 0.27, "tin_bronze", u_scale=0.9)
            if lod == 0:
                add_window_niche(bm, uv_layer, sgn * 4.5, +3.45, 5.4, 0.36, 1.15, facing="+Y")
                add_window_niche(bm, uv_layer, sgn * 4.5, -3.45, 5.4, 0.36, 1.15, facing="-Y")


def build_ur_wall_segment(bm, uv_layer, lod):
    """Geboeschte Lehmziegel-Stadtmauer (8.0 m breit entlang X) mit Wehrgang & Zinnen."""
    sx, sy, h = 8.0, 3.0, 6.4
    if lod == 3:
        add_battered_prism(bm, uv_layer, 0.0, 0.0, -0.50, h + 0.6, sx, sy + 0.2, sx, sy - 0.35, "mudbrick_plaster", u_scale=0.22)
        return
    if lod == 2:
        add_wall_with_plinth(bm, uv_layer, 0.0, 0.0, 0.55, h, sx, sy, batter=0.22)
        for sgn in (-1.0, 1.0):
            add_battered_prism(bm, uv_layer, 0.0, sgn * 1.15, h, h + 0.65, sx, 0.42, sx, 0.34, "mudbrick_plaster", u_scale=0.25)
        return

    add_wall_with_plinth(bm, uv_layer, 0.0, 0.0, 0.55, h, sx, sy, batter=0.24)
    # Wehrgang-Bruestungen +Y / -Y mit Zinnen
    for sgn in (-1.0, 1.0):
        py = sgn * (sy * 0.5 - 0.28)
        add_battered_prism(bm, uv_layer, 0.0, py, h, h + 0.65, sx, 0.44, sx, 0.36, "mudbrick_plaster", u_scale=0.28)
        n_mer = 7 if lod == 0 else 4
        for i in range(n_mer):
            mx = -sx * 0.5 + (i + 0.5) * (sx / n_mer)
            add_battered_prism(bm, uv_layer, mx, py, h + 0.65, h + 1.02, 0.55, 0.36, 0.44, 0.28, "fired_brick_upper", u_scale=0.5)
    if lod == 0:
        add_vigas_along_side(bm, uv_layer, 0.0, +sy * 0.5 - 0.14, h - 0.32, sx - 0.4, axis="X", out_dir=1.0, count=7, protrude=0.28)


def build_ur_wall_tower(bm, uv_layer, lod):
    """Vorspringender geboeschter Wehrturm mit Zinnenkranz & Schiessscharten."""
    sx, sy, h = 5.0, 5.0, 8.2
    if lod == 3:
        add_battered_prism(bm, uv_layer, 0.0, 0.0, -0.50, h + 0.6, sx + 0.2, sy + 0.2, sx - 0.3, sy - 0.3, "mudbrick_plaster", u_scale=0.25)
        return
    if lod == 2:
        add_wall_with_plinth(bm, uv_layer, 0.0, 0.0, 0.55, h, sx, sy, batter=0.24)
        add_parapet_with_merlons(bm, uv_layer, 0.0, 0.0, h, sx - 0.2, sy - 0.2, wall_t=0.42, h_parapet=0.65, add_merlons=False)
        return

    add_wall_with_plinth(bm, uv_layer, 0.0, 0.0, 0.55, h, sx, sy, batter=0.24)
    add_battered_prism(bm, uv_layer, 0.0, 0.0, h - 0.55, h, sx - 0.06, sy - 0.06, sx - 0.04, sy - 0.04, "fired_brick_upper", u_scale=0.35)
    add_parapet_with_merlons(bm, uv_layer, 0.0, 0.0, h, sx - 0.15, sy - 0.15, wall_t=0.42, h_parapet=0.65, merlon_step=1.15, region="fired_brick_upper", add_merlons=True, merlon_h=(0.42 if lod == 0 else 0.28))
    if lod == 0:
        add_vigas_along_side(bm, uv_layer, 0.0, +sy * 0.5 - 0.15, h - 0.65, sx - 0.6, axis="X", out_dir=1.0, count=5)
        for wx in (-1.2, +1.2):
            add_window_niche(bm, uv_layer, wx, +sy * 0.5 - 0.16, 5.2, 0.28, 0.95, facing="+Y")


def build_ur_grain_silo(bm, uv_layer, lod):
    """Bienenkorb-Kornspeicher aus Lehmziegel mit Sockel & Dachluke."""
    if lod == 3:
        prof = [(1.75, -0.50), (1.68, 0.40), (1.42, 2.40), (0.65, 4.10), (0.0, 4.45)]
        add_lathe_vessel(bm, uv_layer, 0.0, 0.0, 0.0, prof, segs=6, region="mudbrick_plaster")
        return
    segs = 14 if lod == 0 else (10 if lod == 1 else 7)
    prof_base = [(1.78, -0.50), (1.72, 0.42)]
    prof_body = [(1.72, 0.42), (1.62, 1.55), (1.38, 2.75), (0.96, 3.68), (0.48, 4.25), (0.48, 4.45), (0.0, 4.48)]
    add_lathe_vessel(bm, uv_layer, 0.0, 0.0, 0.0, prof_base, segs=segs, region="fired_brick_plinth")
    add_lathe_vessel(bm, uv_layer, 0.0, 0.0, 0.0, prof_body, segs=segs, region="mudbrick_plaster")
    if lod <= 1:
        add_battered_prism(bm, uv_layer, 0.0, 0.0, 4.42, 4.58, 1.05, 1.05, 1.02, 1.02, "cedar_timber", u_scale=0.8)
        add_wooden_ladder(bm, uv_layer, 0.0, +1.82, 0.0, 0.0, 4.15, width=0.48, rungs=9, lod=lod)
        add_battered_prism(bm, uv_layer, 0.0, +1.65, 0.0, 1.15, 0.85, 0.45, 0.78, 0.38, "carved_door", u_scale=0.8)


def build_ur_kiln_dome(bm, uv_layer, lod):
    """Kuppelfoermiger Toepfer-/Backofen mit Feuerungsbogen, Schornstein & Amphoren."""
    if lod == 3:
        prof = [(1.80, -0.50), (1.72, 0.45), (1.35, 2.10), (0.42, 3.25), (0.0, 3.30)]
        add_lathe_vessel(bm, uv_layer, 0.0, 0.0, 0.0, prof, segs=6, region="fired_brick_plinth")
        return
    segs = 14 if lod == 0 else (10 if lod == 1 else 7)
    prof = [(1.82, -0.50), (1.76, 0.50), (1.58, 1.35), (1.16, 2.25), (0.62, 2.90), (0.44, 3.32), (0.28, 3.30), (0.28, 2.65)]
    add_lathe_vessel(bm, uv_layer, 0.0, 0.0, 0.0, prof, segs=segs, region="fired_brick_plinth")
    # Vorgesetzter Feuerungsbogen (+Y)
    add_battered_prism(bm, uv_layer, 0.0, +1.68, -0.50, 1.25, 1.35, 0.85, 1.22, 0.75, "fired_brick_upper", u_scale=0.45)
    add_battered_prism(bm, uv_layer, 0.0, +2.08, 0.0, 0.88, 0.75, 0.14, 0.62, 0.12, "damp_plinth", u_scale=0.8)
    if lod == 0:
        for ax, ay, sc in ((-1.45, +1.45, 0.90), (-1.75, +0.95, 0.75), (+1.55, +1.35, 0.82)):
            add_amphora(bm, uv_layer, ax, ay, 0.0, scale=sc, segs=8)


def build_ur_canal_bridge(bm, uv_layer, lod):
    """Gemauerte Bogenbruecke ueber Kanal (Spanne entlang X=9.6 m, Breite Y=3.6 m, Brueckenscheitel Z=1.85 m)."""
    span_x = 9.6
    w_y = 3.6
    if lod == 3:
        add_battered_prism(bm, uv_layer, 0.0, 0.0, -0.65, 2.15, span_x, w_y, span_x - 0.6, w_y - 0.2, "fired_brick_plinth", u_scale=0.25)
        return

    n_seg = 12 if lod == 0 else (8 if lod == 1 else 4)
    hw = w_y * 0.5
    hs = span_x * 0.5

    def _deck_z(x):
        t = abs(x) / hs
        return 1.65 * (1.0 - t * t * 0.88)

    def _arch_z(x):
        if abs(x) >= 3.1:
            return -0.65
        t = x / 3.1
        return max(-0.65, 1.22 * math.sqrt(max(0.0, 1.0 - t * t)) - 0.05)

    # Boegen / Brueckenkoerper als Streifen entlang X
    xs = [-hs + (i / n_seg) * span_x for i in range(n_seg + 1)]
    deck_faces, side_faces = [], []
    top_L = [bm.verts.new((x, -hw, _deck_z(x))) for x in xs]
    top_R = [bm.verts.new((x, +hw, _deck_z(x))) for x in xs]
    bot_L = [bm.verts.new((x, -hw, _arch_z(x))) for x in xs]
    bot_R = [bm.verts.new((x, +hw, _arch_z(x))) for x in xs]

    for i in range(n_seg):
        deck_faces.append(bm.faces.new((top_L[i], top_L[i + 1], top_R[i + 1], top_R[i])))
        side_faces.append(bm.faces.new((bot_L[i], bot_L[i + 1], top_L[i + 1], top_L[i])))
        side_faces.append(bm.faces.new((top_R[i], top_R[i + 1], bot_R[i + 1], bot_R[i])))
        side_faces.append(bm.faces.new((bot_R[i], bot_R[i + 1], bot_L[i + 1], bot_L[i])))  # Bogenleibung unten

    # Endkappen
    side_faces.append(bm.faces.new((bot_L[0], top_L[0], top_R[0], bot_R[0])))
    side_faces.append(bm.faces.new((bot_R[-1], top_R[-1], top_L[-1], bot_L[-1])))

    _apply_box_uv_to_faces(deck_faces, uv_layer, "royal_stone_road", u_scale=0.25, v_fit=True, rot_uv=False)
    _apply_box_uv_to_faces(side_faces, uv_layer, "fired_brick_plinth", u_scale=0.28, v_fit=True, z_bounds=(-0.65, 1.85))

    # Seitenbruestungen (LOD0 / LOD1)
    if lod <= 1:
        for sgn in (-1.0, 1.0):
            py = sgn * (hw - 0.16)
            p_top_L = [bm.verts.new((x, py - 0.14, _deck_z(x) + 0.62)) for x in xs]
            p_top_R = [bm.verts.new((x, py + 0.14, _deck_z(x) + 0.62)) for x in xs]
            p_bot_L = [bm.verts.new((x, py - 0.16, _deck_z(x))) for x in xs]
            p_bot_R = [bm.verts.new((x, py + 0.16, _deck_z(x))) for x in xs]
            p_faces = []
            for i in range(n_seg):
                p_faces.append(bm.faces.new((p_top_L[i], p_top_L[i + 1], p_top_R[i + 1], p_top_R[i])))
                p_faces.append(bm.faces.new((p_bot_L[i], p_bot_L[i + 1], p_top_L[i + 1], p_top_L[i])))
                p_faces.append(bm.faces.new((p_top_R[i], p_top_R[i + 1], p_bot_R[i + 1], p_bot_R[i])))
            p_faces.append(bm.faces.new((p_bot_L[0], p_top_L[0], p_top_R[0], p_bot_R[0])))
            p_faces.append(bm.faces.new((p_bot_R[-1], p_top_R[-1], p_top_L[-1], p_bot_L[-1])))
            _apply_box_uv_to_faces(p_faces, uv_layer, "fired_brick_upper", u_scale=0.35, v_fit=True)


def build_ur_wooden_bridge(bm, uv_layer, lod):
    """Hoelzerne Zedern-Balkenbruecke fuer Nebenstrassen & schmale Kanaele (Spanne X=7.6m, B=2.6m)."""
    span_x = 7.6
    w_y = 2.6
    hs = span_x * 0.5
    hw = w_y * 0.5

    def _deck_z(x):
        t = min(1.0, abs(x) / hs)
        return 0.02 + 0.92 * (1.0 - t * t)

    if lod == 3:
        add_battered_prism(bm, uv_layer, 0.0, 0.0, -0.65, 0.98, span_x, w_y, span_x - 0.5, w_y - 0.15, "cedar_timber", u_scale=0.35)
        return

    # Ufer-Widerlager links & rechts aus gebranntem Ziegel bis Z=-0.65 m
    for sgn in (-1.0, 1.0):
        add_battered_prism(bm, uv_layer, sgn * 3.45, 0.0, -0.65, 0.20, 0.95, w_y + 0.25, 0.80, w_y + 0.10, "fired_brick_plinth", u_scale=0.18)

    if lod == 2:
        n_seg = 4
        xs = [-hs + (i / n_seg) * span_x for i in range(n_seg + 1)]
        for i in range(n_seg):
            xm = 0.5 * (xs[i] + xs[i + 1])
            zm = _deck_z(xm)
            seg_len = xs[i + 1] - xs[i] + 0.06
            add_battered_prism(bm, uv_layer, xm, 0.0, zm - 0.18, zm, seg_len, w_y, seg_len, w_y, "cedar_timber", u_scale=0.45)
        for px in (-1.5, +1.5):
            add_battered_prism(bm, uv_layer, px, 0.0, -0.65, _deck_z(px) - 0.16, 0.35, w_y - 0.2, 0.30, w_y - 0.2, "cedar_timber", u_scale=0.5)
        return

    segs = 6 if lod == 0 else 4
    # 2 Joch-Reihen gerammter Zedernholz-Pfaehle im Kanalbett (Z=-0.65 bis Brueckendeck) + Querholm
    for px in (-1.55, +1.55):
        z_cap = _deck_z(px) - 0.14
        for py in (-hw + 0.24, 0.0, +hw - 0.24):
            add_cylinder(bm, uv_layer, (px, py, -0.65), (px, py, z_cap), 0.11, 0.095, segs=segs, region_key="cedar_timber", cap0=False)
        # Querholm / Jochbalken
        add_cylinder(bm, uv_layer, (px, -hw - 0.08, z_cap - 0.04), (px, +hw + 0.08, z_cap - 0.04), 0.11, 0.11, segs=segs, region_key="cedar_timber", cap0_region="vigas_log_end", cap1_region="vigas_log_end")
        if lod == 0:
            # Schraege Kopfbänder (Aussteifung)
            for sgn_y in (-1.0, 1.0):
                add_cylinder(bm, uv_layer, (px, sgn_y * (hw - 0.25), z_cap - 0.48), (px, sgn_y * 0.25, z_cap - 0.06), 0.055, 0.055, segs=5, region_key="cedar_timber")

    # 3 durchlaufende Laengsträger (Zedern-Streckbalken entlang gekruemmtem Deck)
    n_seg = 10 if lod == 0 else 6
    xs = [-hs + (i / n_seg) * span_x for i in range(n_seg + 1)]
    for sy in (-hw + 0.26, 0.0, +hw - 0.26):
        for i in range(n_seg):
            p0 = (xs[i], sy, _deck_z(xs[i]) - 0.10)
            p1 = (xs[i + 1], sy, _deck_z(xs[i + 1]) - 0.10)
            add_cylinder(bm, uv_layer, p0, p1, 0.095, 0.095, segs=segs, region_key="cedar_timber", cap0=(i == 0), cap1=(i == n_seg - 1), cap0_region="vigas_log_end", cap1_region="vigas_log_end")

    # Bohlenbelag (LOD0: einzelne Querbohlen; LOD1: durchgehende gekruemmte Bohlenflaeche)
    if lod == 0:
        n_planks = 22
        dx_p = span_x / n_planks
        for ip in range(n_planks):
            px = -hs + (ip + 0.5) * dx_p
            pz = _deck_z(px)
            add_battered_prism(bm, uv_layer, px, 0.0, pz - 0.05, pz + 0.03, dx_p * 0.90, w_y, dx_p * 0.88, w_y, "cedar_timber", u_scale=0.55)
    else:
        deck_faces = []
        top_L = [bm.verts.new((x, -hw, _deck_z(x) + 0.02)) for x in xs]
        top_R = [bm.verts.new((x, +hw, _deck_z(x) + 0.02)) for x in xs]
        bot_L = [bm.verts.new((x, -hw, _deck_z(x) - 0.06)) for x in xs]
        bot_R = [bm.verts.new((x, +hw, _deck_z(x) - 0.06)) for x in xs]
        for i in range(n_seg):
            deck_faces.append(bm.faces.new((top_L[i], top_L[i + 1], top_R[i + 1], top_R[i])))
            deck_faces.append(bm.faces.new((bot_L[i], bot_L[i + 1], top_L[i + 1], top_L[i])))
            deck_faces.append(bm.faces.new((top_R[i], top_R[i + 1], bot_R[i + 1], bot_R[i])))
            deck_faces.append(bm.faces.new((bot_R[i], bot_R[i + 1], bot_L[i + 1], bot_L[i])))
        _apply_box_uv_to_faces(deck_faces, uv_layer, "cedar_timber", u_scale=0.45, v_fit=True)

    # Hoelzernes Seitengelaender (Pfosten + Handlauf + Fussbalken-Schwelle)
    post_xs = [-3.35, -1.65, 0.0, +1.65, +3.35] if lod == 0 else [-3.2, 0.0, +3.2]
    rail_h = 0.78
    for sgn_y in (-1.0, 1.0):
        ry = sgn_y * (hw - 0.11)
        for px in post_xs:
            pz = _deck_z(px)
            add_battered_prism(bm, uv_layer, px, ry, pz - 0.06, pz + rail_h, 0.13, 0.13, 0.12, 0.12, "cedar_timber", u_scale=0.7)
        # Durchgehender Handlauf & Mittelriegel
        for i in range(len(post_xs) - 1):
            x_a, x_b = post_xs[i], post_xs[i + 1]
            za, zb = _deck_z(x_a), _deck_z(x_b)
            add_cylinder(bm, uv_layer, (x_a, ry, za + rail_h - 0.05), (x_b, ry, zb + rail_h - 0.05), 0.055, 0.055, segs=segs, region_key="cedar_timber", cap0=(i == 0), cap1=(i == len(post_xs) - 2), cap0_region="vigas_log_end", cap1_region="vigas_log_end")
            if lod == 0:
                add_cylinder(bm, uv_layer, (x_a, ry, za + 0.38), (x_b, ry, zb + 0.38), 0.04, 0.04, segs=5, region_key="cedar_timber")


# ==============================================================================
# 5. STRASSEN-REQUISITEN (LOD0 + LOD1, INSTANZIERBAR)
# ==============================================================================

def build_road_curb_lamp_post(bm, uv_layer, lod):
    """Strassen-Fackel-/Kohlepfannen-Staender & Grenzstele (-0.35 m Sockel)."""
    segs = 8 if lod == 0 else 5
    # Kalkstein-Grenzstele (abgerundete Stele neben dem Lampenpfosten)
    add_battered_prism(bm, uv_layer, -0.34, 0.0, -0.35, 0.85, 0.36, 0.26, 0.30, 0.22, "royal_stone_road", u_scale=0.6)
    add_battered_prism(bm, uv_layer, -0.34, 0.0, 0.85, 1.05, 0.30, 0.22, 0.18, 0.14, "gypsum_temple", u_scale=0.8)
    # Zedernpfosten + Bronze-Ausleger + Kohlepfanne
    add_battered_prism(bm, uv_layer, +0.22, 0.0, -0.35, 0.32, 0.34, 0.34, 0.28, 0.28, "royal_stone_road", u_scale=0.7)
    add_cylinder(bm, uv_layer, (+0.22, 0.0, 0.25), (+0.22, 0.0, 2.65), 0.075, 0.058, segs=segs, region_key="cedar_timber")
    add_cylinder(bm, uv_layer, (+0.20, 0.0, 2.52), (+0.62, 0.0, 2.62), 0.035, 0.030, segs=segs, region_key="tin_bronze")
    # Haengendes Kohlepfannen-Becken
    prof_cup = [(0.0, 0.0), (0.14, 0.06), (0.20, 0.18), (0.16, 0.18), (0.0, 0.08)]
    add_lathe_vessel(bm, uv_layer, +0.60, 0.0, 2.34, prof_cup, segs=segs, region="tin_bronze")


def build_road_cart_parked(bm, uv_layer, lod):
    """Abgestellter bronzezeitlicher Zweirad-Ochsenkarren mit Saecken (Raeder auf Z=0.0)."""
    segs = 12 if lod == 0 else 8
    r_wheel = 0.54
    # Zwei massive Holzscheibenraeder mit Bronzenabe auf Z=0.0
    for sgn in (-1.0, 1.0):
        wx = sgn * 0.78
        add_cylinder(bm, uv_layer, (wx - 0.06, 0.0, r_wheel), (wx + 0.06, 0.0, r_wheel), r_wheel, r_wheel, segs=segs, region_key="cedar_timber", cap0_region="vigas_log_end", cap1_region="vigas_log_end")
        add_cylinder(bm, uv_layer, (wx - 0.09, 0.0, r_wheel), (wx + 0.09, 0.0, r_wheel), 0.14, 0.14, segs=6, region_key="tin_bronze")
    # Achse + Ladeflaeche + Seitenrungen
    add_cylinder(bm, uv_layer, (-0.90, 0.0, r_wheel), (+0.90, 0.0, r_wheel), 0.06, 0.06, segs=6, region_key="cedar_timber")
    add_battered_prism(bm, uv_layer, 0.0, -0.05, r_wheel + 0.04, r_wheel + 0.14, 1.28, 1.85, 1.28, 1.85, "cedar_timber", u_scale=0.5)
    for sgn in (-1.0, 1.0):
        add_battered_prism(bm, uv_layer, sgn * 0.60, -0.05, r_wheel + 0.14, r_wheel + 0.56, 0.07, 1.80, 0.07, 1.80, "cedar_timber", u_scale=0.6)
    # Deichsel nach vorne (+Y) mit Stuetzfuss auf Z=0.0
    add_cylinder(bm, uv_layer, (0.0, +0.40, r_wheel + 0.05), (0.0, +2.05, 0.42), 0.055, 0.045, segs=6, region_key="cedar_timber")
    add_cylinder(bm, uv_layer, (0.0, +1.45, 0.0), (0.0, +1.45, 0.50), 0.035, 0.035, segs=5, region_key="cedar_timber")
    # Gestapelte Leinen-Kornsaecke
    sacks = [(0.0, -0.35, r_wheel + 0.14, 0.52, 0.85, 0.34), (-0.28, +0.35, r_wheel + 0.14, 0.48, 0.72, 0.32), (+0.26, +0.28, r_wheel + 0.14, 0.48, 0.74, 0.32)]
    if lod == 0:
        sacks.append((0.0, +0.05, r_wheel + 0.46, 0.55, 0.72, 0.30))
    for sx, sy, sz, w, l, h in sacks:
        add_battered_prism(bm, uv_layer, sx, sy, sz, sz + h, w, l, w * 0.82, l * 0.84, "woven_awning", u_scale=0.6)


def build_road_market_awning(bm, uv_layer, lod):
    """Marktstand-Pavillon mit gewebter Markise, Auslagetisch, Koerben & Amphoren."""
    sx, sy = 3.2, 2.2
    segs = 8 if lod == 0 else 5
    # 4 Zedernpfosten (-0.30 m Fundament)
    for px in (-sx * 0.46, +sx * 0.46):
        for py in (-sy * 0.45, +sy * 0.45):
            zh = 2.45 if py < 0 else 2.15
            add_cylinder(bm, uv_layer, (px, py, -0.30), (px, py, zh), 0.065, 0.055, segs=segs, region_key="cedar_timber", cap0=False)
    # Geneigte gewebte Markise
    add_sloped_awning(bm, uv_layer, 0.0, -sy * 0.5, 2.50, 2.12, sx + 0.3, sy + 0.35, facing="+Y", lod=lod, region="woven_awning")
    # Auslagetisch
    add_battered_prism(bm, uv_layer, 0.0, +0.25, 0.72, 0.84, 2.45, 0.85, 2.45, 0.85, "cedar_timber", u_scale=0.5)
    for tx in (-1.05, +1.05):
        for ty in (-0.10, +0.60):
            add_battered_prism(bm, uv_layer, tx, ty, 0.0, 0.72, 0.10, 0.10, 0.10, 0.10, "cedar_timber", u_scale=0.8)
    if lod == 0:
        # Koerbe (Schilf) & Amphoren
        for bx, by, bz in ((-0.75, +0.25, 0.84), (+0.05, +0.25, 0.84), (-1.15, +0.75, 0.0)):
            prof_b = [(0.22, 0.0), (0.30, 0.32), (0.26, 0.32), (0.18, 0.06)]
            add_lathe_vessel(bm, uv_layer, bx, by, bz, prof_b, segs=8, region="reed_pergola")
        for ax, ay, az, sc in ((+0.78, +0.25, 0.84, 0.62), (+1.18, +0.75, 0.0, 0.88), (+0.72, +0.85, 0.0, 0.74)):
            add_amphora(bm, uv_layer, ax, ay, az, scale=sc, segs=8)


# ==============================================================================
# MODUL-KATALOG & EXPORT-PIPELINE
# ==============================================================================

MODULE_BUILDERS = [
    # 5 Staedtische Wohnhaeuser (4 LODs)
    ("ur_courtyard_house_01", build_ur_courtyard_house_01, (0, 1, 2, 3), "Zweistoeckiges Atriumhaus mit Holzgalerie & Aussentreppe"),
    ("ur_courtyard_house_02", build_ur_courtyard_house_02, (0, 1, 2, 3), "L-foermiges Eck-Wohnhaus mit Dachterrasse, Pergola & Vigas"),
    ("ur_courtyard_house_03", build_ur_courtyard_house_03, (0, 1, 2, 3), "Kaufmanns-Wohnhaus mit gekalktem Portal, Brunnen & Dachzinnen"),
    ("ur_courtyard_house_04", build_ur_courtyard_house_04, (0, 1, 2, 3), "Handwerker-/Laden-Wohnhaus mit Ocker-Markise, Werkbank & Amphoren"),
    ("ur_courtyard_house_05", build_ur_courtyard_house_05, (0, 1, 2, 3), "Doppel-Terrassen-Wohnhaus mit Windfang-Pavillon, Tannur & Leiter"),
    # 5 Dorf-/Vorstadthaeuser (4 LODs)
    ("ur_mudbrick_small_01",  build_ur_mudbrick_small_01,  (0, 1, 2, 3), "Kompaktes Einraumhaus mit Aussentreppe & Schilf-Vorbau"),
    ("ur_mudbrick_small_02",  build_ur_mudbrick_small_02,  (0, 1, 2, 3), "Zweiteiliges Flachdachhaus mit Backofen & Hofmauer"),
    ("ur_mudbrick_small_03",  build_ur_mudbrick_small_03,  (0, 1, 2, 3), "Kleines Lager-/Handwerkerhaus mit Holz-Vordach & Amphoren"),
    ("ur_mudbrick_small_04",  build_ur_mudbrick_small_04,  (0, 1, 2, 3), "Versetztes Doppelraum-Haus mit Dach-Pergola & Holzleiter"),
    ("ur_mudbrick_small_05",  build_ur_mudbrick_small_05,  (0, 1, 2, 3), "Laendliches Gehoeft mit Kleinvieh-Maeuerchen & Schatten-Vordach"),
    # Marschland (4 LODs)
    ("ur_mudhif_hut",         build_ur_mudhif_hut,         (0, 1, 2, 3), "Sumerische Schilf-Bogenhuette (Mudhif) fuer Kanaldoerfer"),
    # Monumental & Infrastruktur (4 LODs)
    ("ur_ziggurat_temple",    build_ur_ziggurat_temple,    (0, 1, 2, 3), "Gestufte Ziggurat mit 3 Freitreppen, Nischenpilastern & Lapislazuli-Schrein"),
    ("ur_city_gate",          build_ur_city_gate,          (0, 1, 2, 3), "Doppelturm-Stadttor mit Stufenzinnen, Bronzetoren & Lapislazuli-Fries"),
    ("ur_wall_segment",       build_ur_wall_segment,       (0, 1, 2, 3), "Geboeschte Lehmziegel-Stadtmauer mit Wehrgang & Zinnen"),
    ("ur_wall_tower",         build_ur_wall_tower,         (0, 1, 2, 3), "Vorspringender Wehrturm mit Zinnen & Schiessscharten"),
    ("ur_grain_silo",         build_ur_grain_silo,         (0, 1, 2, 3), "Bienenkorb-Kornspeicher aus Lehmziegeln"),
    ("ur_kiln_dome",          build_ur_kiln_dome,          (0, 1, 2, 3), "Kuppelfoermiger Toepfer-/Backofen mit Feuerungsbogen"),
    ("ur_canal_bridge",       build_ur_canal_bridge,       (0, 1, 2, 3), "Gemauerte Bogenbruecke mit Seitenbruestung"),
    ("ur_wooden_bridge",      build_ur_wooden_bridge,      (0, 1, 2, 3), "Hoelzerne Zedern-Balkenbruecke fuer Nebenstrassen & schmale Kanaele"),
    # Strassen-Requisiten (LOD0 + LOD1)
    ("road_curb_lamp_post",   build_road_curb_lamp_post,   (0, 1),       "Strassen-Fackel-/Kohlepfannen-Staender & Grenzstele"),
    ("road_cart_parked",      build_road_cart_parked,      (0, 1),       "Abgestellter Zweirad-Ochsenkarren mit Kornsaecken"),
    ("road_market_awning",    build_road_market_awning,    (0, 1),       "Marktstand-Pavillon mit Web-Markise, Koerben & Toepfen"),
]


def _finalize_bmesh_to_object(scene, name, bm, mat):
    ngons = [f for f in bm.faces if len(f.verts) > 4]
    if ngons:
        bmesh.ops.triangulate(bm, faces=ngons)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat)
    mesh.polygons.foreach_set("use_smooth", [False] * len(mesh.polygons))

    obj = bpy.data.objects.new(name, mesh)
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)
    scene.collection.objects.link(obj)

    tri_cnt = sum(max(1, len(p.vertices) - 2) for p in mesh.polygons)
    min_z = min((v.co.z for v in mesh.vertices), default=0.0)
    max_z = max((v.co.z for v in mesh.vertices), default=0.0)
    return obj, tri_cnt, min_z, max_z


def build_and_export_kit():
    t0 = time.time()
    tex_dir = os.path.join(ASSETS_DIR, "textures")
    blend_dir = os.path.join(ASSETS_DIR, "blend", "world")
    glb_dir = os.path.join(ASSETS_DIR, "glb", "world")
    os.makedirs(blend_dir, exist_ok=True)
    os.makedirs(glb_dir, exist_ok=True)

    scene = clear_scene()
    mat = create_city_trim_material(tex_dir)
    all_objs = []
    module_stats = {}

    print(f"[CITY KIT] Generiere {len(MODULE_BUILDERS)} Mesopotamien-Module (4 LODs / 2 LODs)...", flush=True)
    for mod_name, builder_fn, lod_tuple, desc in MODULE_BUILDERS:
        lod_counts = {}
        min_z_all = 0.0
        for lod in lod_tuple:
            bm = bmesh.new()
            uv_layer = bm.loops.layers.uv.new("UVMap")
            builder_fn(bm, uv_layer, lod)
            obj_name = f"{mod_name}_LOD{lod}"
            obj, tri_cnt, min_z, _ = _finalize_bmesh_to_object(scene, obj_name, bm, mat)
            all_objs.append(obj)
            lod_counts[f"LOD{lod}"] = tri_cnt
            min_z_all = min(min_z_all, min_z)

        module_stats[mod_name] = {
            "lods": lod_counts,
            "minZ": round(min_z_all, 3),
            "description": desc,
        }
        lod_str = " | ".join(f"{k}={v:4d}" for k, v in lod_counts.items())
        print(f"  [MOD] {mod_name:24s} | {lod_str} | minZ={min_z_all:+.2f}m", flush=True)

    # Editierbare .blend speichern
    blend_path = os.path.join(blend_dir, "mesopotamia_city_kit.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[CITY KIT] .blend gespeichert: {blend_path}", flush=True)

    # Gebuendelten GLB-Export ueber export_arche_glb.py ausfuehren
    glb_path = os.path.join(glb_dir, "mesopotamia_city_kit.glb")
    export_arche_glb.export_glb(all_objs, glb_path, use_draco=False)
    size_kb = os.path.getsize(glb_path) / 1024.0
    print(f"[CITY KIT] GLB exportiert in {time.time() - t0:.2f}s ({size_kb:.1f} KB, {len(all_objs)} Meshes).", flush=True)
    return module_stats, size_kb


def update_manifest(module_stats, glb_kb):
    mpath = os.path.join(ASSETS_DIR, "manifest.json")
    with open(mpath, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    items = manifest.setdefault("categories", {}).setdefault("world", {}).setdefault("items", {})
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_lod0 = sum(v["lods"].get("LOD0", 0) for v in module_stats.values())

    items["mesopotamia_city_kit"] = {
        "enabled": True,
        "url": "assets/glb/world/mesopotamia_city_kit.glb",
        "blend": "assets/blend/world/mesopotamia_city_kit.blend",
        "category": "world",
        "description": f"Modulares Mesopotamien-Architektur- & Strassen-Kit ({len(module_stats)} Module, 4 LODs, -0.50m Sockel, 1 Shared 2048x1024 Trim-Sheet)",
        "instanced": True,
        "materials": 1,
        "modulesCount": len(module_stats),
        "totalLod0Tris": total_lod0,
        "lodBandsMeters": {
            "LOD0": [0, 150],
            "LOD1": [150, 500],
            "LOD2": [500, 1500],
            "LOD3": [1500, 3000],
        },
        "sharedTextures": {
            "baseColor": "assets/textures/city_trim_atlas_baseColor.png",
            "normal": "assets/textures/city_trim_atlas_normal.png",
            "orm": "assets/textures/city_trim_atlas_orm.png",
        },
        "modules": module_stats,
        "preview": "assets/previews/mesopotamia_city_showcase.png",
        "glbSizeKB": round(glb_kb, 1),
        "exportedAt": now_str,
    }

    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"[MANIFEST] assets/manifest.json fuer 'mesopotamia_city_kit' ({len(module_stats)} Module) aktualisiert.", flush=True)


# ==============================================================================
# 6. VISUELLES KONTROLL-RENDERING (mesopotamia_city_showcase.png)
# ==============================================================================

def _add_road_probe_slab(scene, name, cx, cy, sx, sy, region_key, mat, u_tiles=2.5):
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    v0 = bm.verts.new((-sx * 0.5, -sy * 0.5, 0.02))
    v1 = bm.verts.new((+sx * 0.5, -sy * 0.5, 0.02))
    v2 = bm.verts.new((+sx * 0.5, +sy * 0.5, 0.02))
    v3 = bm.verts.new((-sx * 0.5, +sy * 0.5, 0.02))
    f = bm.faces.new((v0, v1, v2, v3))
    u0, v_lo, u1, v_hi = TRIM_REGIONS[region_key]
    uvs = [(0.0, v_lo), (u_tiles, v_lo), (u_tiles, v_hi), (0.0, v_hi)]
    for lp, uv in zip(f.loops, uvs):
        lp[uv_layer].uv = uv
    obj, _, _, _ = _finalize_bmesh_to_object(scene, name, bm, mat)
    obj.location = (cx, cy, 0.0)
    return obj


def render_showcase():
    t0 = time.time()
    print("[SHOWCASE] Lade mesopotamia_city_kit.blend und erstelle Studio-Tableau...", flush=True)
    scene = clear_scene()
    dev = setup_cycles(scene, samples=48, use_oidn=True)

    vts = [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items]
    scene.view_settings.view_transform = "AgX" if "AgX" in vts else "Filmic"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = -0.15

    blend_path = os.path.join(ASSETS_DIR, "blend", "world", "mesopotamia_city_kit.blend")
    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
        data_to.objects = list(data_from.objects)
    obj_map = {o.name: o for o in data_to.objects if o is not None}

    # Bodenplatte auf Z=0.0 (warmes mesopotamisches Schwemmland-Ocker)
    bpy.ops.mesh.primitive_plane_add(size=180.0, location=(0.0, 0.0, 0.0))
    ground = bpy.context.active_object
    g_mat = bpy.data.materials.new("ShowcaseSandGround")
    g_mat.use_nodes = True
    bsdf_g = g_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf_g:
        bsdf_g.inputs["Base Color"].default_value = (0.36, 0.28, 0.18, 1.0)
        bsdf_g.inputs["Roughness"].default_value = 0.92
    ground.data.materials.append(g_mat)

    shared_mat = next((o.data.materials[0] for o in obj_map.values() if o.data.materials), None)

    # Strassenpflaster-Proben im Vordergrund (links: Koenigsstrasse + Wohngasse)
    if shared_mat:
        _add_road_probe_slab(scene, "Probe_Royal_Road", -21.0, -28.0, 15.0, 4.4, "royal_stone_road", shared_mat, u_tiles=2.5)
        _add_road_probe_slab(scene, "Probe_Alley_Road", -21.0, -22.8, 15.0, 3.6, "alley_mud_road", shared_mat, u_tiles=2.5)

    # Aufstellung: Hoehenstaffelung von vorne (0..4m) nach hinten (14m), rot_z=pi dreht +Y Fronten zur Kamera (-Y)!
    placements = [
        # Vordergrund links: Strassen-Requisiten auf/neben den Strassenproben
        ("road_curb_lamp_post_LOD0",   (-27.2, -25.2, 0.02), math.pi),
        ("road_cart_parked_LOD0",      (-21.0, -28.0, 0.02), math.radians(105.0)),
        ("road_market_awning_LOD0",    (-15.5, -22.8, 0.02), math.radians(172.0)),

        # Vordergrund rechts: LOD0 -> LOD1 -> LOD2 -> LOD3 Vergleichsreihe an ur_courtyard_house_01
        ("ur_courtyard_house_01_LOD0", ( -3.5, -26.5, 0.0), math.pi),
        ("ur_courtyard_house_01_LOD1", ( +7.5, -26.5, 0.0), math.pi),
        ("ur_courtyard_house_01_LOD2", (+18.0, -26.5, 0.0), math.pi),
        ("ur_courtyard_house_01_LOD3", (+28.5, -26.5, 0.0), math.pi),

        # Reihe 1 (Y = -8.5 m): Alle 5 Dorf-/Vorstadthaeuser + Mudhif + Silo + Ofen + Stein- & Holzbruecke (3.4..4.5 m hoch)
        ("ur_mudbrick_small_01_LOD0",  (-32.5,  -8.5, 0.0), math.pi),
        ("ur_mudbrick_small_02_LOD0",  (-24.8,  -8.5, 0.0), math.pi),
        ("ur_mudbrick_small_03_LOD0",  (-17.0,  -8.5, 0.0), math.pi),
        ("ur_mudbrick_small_04_LOD0",  ( -9.2,  -8.5, 0.0), math.pi),
        ("ur_mudbrick_small_05_LOD0",  ( -1.0,  -8.5, 0.0), math.pi),
        ("ur_mudhif_hut_LOD0",         ( +7.5,  -8.5, 0.0), math.radians(162.0)),
        ("ur_grain_silo_LOD0",         (+14.2,  -8.5, 0.0), math.pi),
        ("ur_kiln_dome_LOD0",          (+19.8,  -8.5, 0.0), math.pi),
        ("ur_canal_bridge_LOD0",       (+26.8,  -8.5, 0.0), math.radians(90.0)),
        ("ur_wooden_bridge_LOD0",      (+32.8,  -8.5, 0.0), math.radians(90.0)),

        # Reihe 2 (Y = +7.5 m): Alle 5 staedtischen Wohnhaus-Varianten (LOD0, 5.8..8.2 m hoch)
        ("ur_courtyard_house_01_LOD0", (-27.0,  +7.5, 0.0), math.pi),
        ("ur_courtyard_house_02_LOD0", (-13.5,  +7.5, 0.0), math.pi),
        ("ur_courtyard_house_03_LOD0", (  0.0,  +7.5, 0.0), math.pi),
        ("ur_courtyard_house_04_LOD0", (+13.5,  +7.5, 0.0), math.pi),
        ("ur_courtyard_house_05_LOD0", (+27.0,  +7.5, 0.0), math.pi),

        # Reihe 3 (Y = +26.5 m): Monumental- & Befestigungsbauten (6.8..14.2 m hoch)
        ("ur_wall_segment_LOD0",       (-28.0, +26.5, 0.0), math.pi),
        ("ur_wall_tower_LOD0",         (-21.2, +26.0, 0.0), math.pi),
        ("ur_city_gate_LOD0",          (-10.5, +26.5, 0.0), math.pi),
        ("ur_wall_segment_LOD0",       ( +0.5, +26.5, 0.0), math.pi),
        ("ur_ziggurat_temple_LOD0",    (+20.5, +27.0, 0.0), math.pi),
    ]

    for idx, (oname, pos, rot_z) in enumerate(placements):
        src = obj_map.get(oname)
        if not src:
            continue
        inst = src.copy()
        inst.data = src.data
        inst.name = f"Show_{idx:02d}_{oname}"
        inst.location = pos
        inst.rotation_euler = (0.0, 0.0, rot_z)
        scene.collection.objects.link(inst)

    # Warme mesopotamische Nachmittagssonne (schraeg von vorne-links-oben fuer klare Frontbeleuchtung & Relief)
    sun_d = bpy.data.lights.new("MesoSun", type="SUN")
    sun_d.energy = 3.1
    sun_d.color = (1.0, 0.94, 0.84)
    sun_d.angle = math.radians(1.6)
    sun_o = bpy.data.objects.new("MesoSun", sun_d)
    sun_o.rotation_euler = (math.radians(50.0), math.radians(14.0), math.radians(-32.0))
    scene.collection.objects.link(sun_o)

    # Dezente Feuer-Akzente in Ziggurat-Opferbecken & Strassenlampe (gedreht um Z=pi)
    for lx, ly, lz, en in ((+18.6, +25.95, 12.75, 48.0), (+22.4, +25.95, 12.75, 48.0), (-27.8, -25.2, 2.68, 14.0)):
        pt_d = bpy.data.lights.new("FireGlow", type="POINT")
        pt_d.energy = en
        pt_d.color = (1.0, 0.45, 0.12)
        pt_o = bpy.data.objects.new("FireGlow", pt_d)
        pt_o.location = (lx, ly, lz)
        scene.collection.objects.link(pt_o)

    # Himmels-Weltlicht
    w = bpy.data.worlds.new("ShowcaseSky")
    scene.world = w
    w.use_nodes = True
    nt_w = w.node_tree
    bg = nt_w.nodes.get("Background")
    sky = nt_w.nodes.new("ShaderNodeTexSky")
    sky_enums = [i.identifier for i in sky.bl_rna.properties["sky_type"].enum_items]
    sky.sky_type = "PREETHAM" if "PREETHAM" in sky_enums else sky_enums[0]
    nt_w.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.48

    # Kamera von -Y ueberblickend (-X=links, +X=rechts, alle 4 Reihen unbeschnitten & unueberdeckt!)
    cam_d = bpy.data.cameras.new("ShowcaseCam")
    cam_d.lens = 33.0
    cam_d.clip_end = 500.0
    cam_o = bpy.data.objects.new("ShowcaseCam", cam_d)
    cam_o.location = (+1.0, -84.0, 50.0)
    target = Vector((+1.0, +0.5, 1.5))
    cam_o.rotation_euler = (target - cam_o.location).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cam_o)
    scene.camera = cam_o

    prev_dir = os.path.join(ASSETS_DIR, "previews")
    os.makedirs(prev_dir, exist_ok=True)
    out_png = os.path.join(prev_dir, "mesopotamia_city_showcase.png")
    scene.render.resolution_x = 2400
    scene.render.resolution_y = 1500
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = out_png
    bpy.ops.render.render(write_still=True)
    print(f"[SHOWCASE] {out_png} gerendert auf {dev} in {time.time() - t0:.2f}s.", flush=True)
    return out_png


def main():
    t_total = time.time()
    module_stats, glb_kb = build_and_export_kit()
    update_manifest(module_stats, glb_kb)
    render_showcase()
    print(f"[CITY KIT DONE] Gesamtlaufzeit: {time.time() - t_total:.2f}s.", flush=True)


if __name__ == "__main__":
    main()
