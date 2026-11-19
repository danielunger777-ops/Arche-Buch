"""
build_shipyard_industry.py — Modulares Bronzezeit-Werft-, Aquädukt-, Boots- & Feld-Kit (4 LODs)
=================================================================================================
Erzeugt 38 echte bronzezeitliche Blender-Modelle OHNE Arche und OHNE Tiere, jedes mit:
  - 4 Detailstufen: LOD0 (0-150 m), LOD1 (150-500 m), LOD2 (500-1500 m), LOD3 (1500-3000 m)
  - -0.35 m Fundament-Sockel an allen stehenden Bauwerken gegen Schweben an Haengen
  - Exakten Dreh-/Scharnier-/Wasserlinien-Origins fuer bewegliche Teile & Magur-Boote
  - 1 Shared-Trim-Material 'Mat_Shipyard_Industry_Trim' (BaseColor, Normal, ORM, Emissive=4.0)

Module (38 Stueck, je 4 LODs = 152 Meshes):
  A) Werft & Bauwerke (20):
     sy_scaffold_bay, sy_cribbing_block, sy_ramp_module, sy_drawbridge_flap,
     sy_crane_aframe, sy_crane_winch_rotor, sy_crane_timber_load,
     sy_pitch_kiln, sy_smithy_forge, sy_charcoal_kiln,
     sy_sawmill_base, sy_sawmill_capstan_rotor, sy_sawmill_driveshaft,
     sy_sawmill_frame, sy_sawmill_pitman, sy_sawpit_shed,
     sy_timber_chute_segment, sy_log_stack, sy_tent_worker, sy_cage_rolling
  B) Aquädukt, Flussbau & Magur-Boote (12):
     sy_aqueduct_source, sy_aqueduct_pier_span, sy_aqueduct_trough,
     river_magur_cargo, river_magur_timber,
     river_waterwheel_base, river_waterwheel_rotor,
     river_shaduf_post, river_shaduf_arm,
     river_sluice_gate, river_weir, river_timber_jetty
  C) Feld-, Lager- & Weg-Requisiten (6):
     field_straw_rick, field_shelter,
     world_boulder_01, world_boulder_02, world_boulder_03, world_supply_cart

Exportiert nach:
  - assets/blend/world/shipyard_industry_kit.blend
  - assets/glb/world/shipyard_industry_kit.glb  (via export_arche_glb.export_glb)
  - assets/manifest.json
  - assets/previews/shipyard_industry_showcase.png

Aufruf:
  blender --background --python-exit-code 1 --python assets/scripts/build_shipyard_industry.py
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
from build_shipyard_trim_atlas import TRIM_REGIONS  # noqa: E402


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


def create_shipyard_trim_material(tex_dir):
    """Erstellt 1 gemeinsames PBR-Material mit BaseColor [sRGB], Normal, ORM und Emissive=4.0."""
    mat = bpy.data.materials.new("Mat_Shipyard_Industry_Trim")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    p_col = os.path.join(tex_dir, "shipyard_trim_atlas_baseColor.png")
    p_nrm = os.path.join(tex_dir, "shipyard_trim_atlas_normal.png")
    p_orm = os.path.join(tex_dir, "shipyard_trim_atlas_orm.png")
    p_emi = os.path.join(tex_dir, "shipyard_trim_atlas_emissive.png")
    for p in (p_col, p_nrm, p_orm, p_emi):
        if not os.path.isfile(p):
            raise FileNotFoundError(f"Trim-Sheet-Textur fehlt: {p} (bitte zuerst build_shipyard_trim_atlas.py ausfuehren!)")

    img_c = bpy.data.images.load(p_col, check_existing=True)
    img_c.colorspace_settings.name = "sRGB"
    img_n = bpy.data.images.load(p_nrm, check_existing=True)
    img_n.colorspace_settings.name = "Non-Color"
    img_o = bpy.data.images.load(p_orm, check_existing=True)
    img_o.colorspace_settings.name = "Non-Color"
    img_e = bpy.data.images.load(p_emi, check_existing=True)
    img_e.colorspace_settings.name = "sRGB"

    tc = nt.nodes.new("ShaderNodeTexImage"); tc.image = img_c
    tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = img_n
    to = nt.nodes.new("ShaderNodeTexImage"); to.image = img_o
    te = nt.nodes.new("ShaderNodeTexImage"); te.image = img_e

    nrm_map = nt.nodes.new("ShaderNodeNormalMap")
    nrm_map.inputs["Strength"].default_value = 0.85

    sep = nt.nodes.new("ShaderNodeSeparateColor")

    nt.links.new(tc.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tn.outputs["Color"], nrm_map.inputs["Color"])
    nt.links.new(nrm_map.outputs["Normal"], bsdf.inputs["Normal"])
    nt.links.new(to.outputs["Color"], sep.inputs["Color"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])

    nt.links.new(te.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 4.0

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

_FULL_U_SEAMLESS = {
    "cut_basalt",
    "wet_spring_stone",
    "rammed_earth_charcoal",
    "cedar_timber",
    "oak_timber",
}


def _pingpong01(t):
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


def _apply_box_uv(faces, uv_layer, region_key, u_scale=0.35, v_fit=True, z_bounds=None, rot_uv=False):
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
            xs = [v.co.x for v in f.verts]
            ys = [v.co.y for v in f.verts]
            min_x, span_x = min(xs), max(1e-4, max(xs) - min(xs))
            min_y, span_y = min(ys), max(1e-4, max(ys) - min(ys))
            for lp in f.loops:
                co = lp.vert.co
                lu = (co.x - min_x) * u_scale if tile_u else (co.x - min_x) / span_x
                lv = (co.y - min_y) / span_y if v_fit else ((co.y - min_y) * u_scale) % 1.0
                if rot_uv:
                    lu, lv = lv, lu
                lp[uv_layer].uv = _map_uv(region_key, lu, lv, tile_u=tile_u)
        else:
            use_x = ay >= ax
            hs = [v.co.x if use_x else v.co.y for v in f.verts]
            min_h, span_h = min(hs), max(1e-4, max(hs) - min(hs))
            for lp in f.loops:
                co = lp.vert.co
                h_coord = co.x if use_x else co.y
                lu = (h_coord - min_h) * u_scale if tile_u else (h_coord - min_h) / span_h
                lv = (co.z - z_lo) / dz if v_fit else ((co.z - z_lo) * u_scale) % 1.0
                if rot_uv:
                    lu, lv = lv, lu
                lp[uv_layer].uv = _map_uv(region_key, lu, lv, tile_u=tile_u)


def add_prism(bm, uv_layer, cx, cy, z0, z1, sx0, sy0, sx1, sy1, region_key,
              u_scale=0.32, v_fit=True, cap_bottom=True, cap_top=True, top_region=None, rot_uv=False):
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
    sides = [bm.faces.new((b[i], b[(i + 1) % 4], t[(i + 1) % 4], t[i])) for i in range(4)]
    _apply_box_uv(sides, uv_layer, region_key, u_scale=u_scale, v_fit=v_fit, z_bounds=(z0, z1), rot_uv=rot_uv)
    tops = []
    if cap_top:
        ft = bm.faces.new((t[0], t[1], t[2], t[3]))
        tops.append(ft)
        _apply_box_uv([ft], uv_layer, top_region or region_key, u_scale=u_scale, v_fit=True, rot_uv=rot_uv)
    if cap_bottom:
        fb = bm.faces.new((b[3], b[2], b[1], b[0]))
        _apply_box_uv([fb], uv_layer, region_key, u_scale=u_scale, v_fit=True, rot_uv=rot_uv)
    return sides + tops


def add_box(bm, uv_layer, cx, cy, z0, z1, sx, sy, region_key, u_scale=0.35, v_fit=True, top_region=None, rot_uv=False):
    return add_prism(bm, uv_layer, cx, cy, z0, z1, sx, sy, sx, sy, region_key,
                     u_scale=u_scale, v_fit=v_fit, top_region=top_region, rot_uv=rot_uv)


def add_beam(bm, uv_layer, p0, p1, width, height, region_key, end_region="timber_endgrain", u_scale=0.45):
    """Erzeugt einen rechteckigen Balken entlang p0->p1 mit Laengs-Masern und Stirnholz-Kappen."""
    v0 = Vector(p0)
    v1 = Vector(p1)
    axis = v1 - v0
    length = axis.length
    if length < 1e-5:
        return []
    z_dir = axis.normalized()
    up_ref = Vector((0.0, 0.0, 1.0)) if abs(z_dir.z) < 0.94 else Vector((1.0, 0.0, 0.0))
    x_dir = up_ref.cross(z_dir).normalized()
    y_dir = z_dir.cross(x_dir).normalized()

    hw, hh = 0.5 * width, 0.5 * height
    corners = [(-hw, -hh), (+hw, -hh), (+hw, +hh), (-hw, +hh)]
    r0 = [bm.verts.new(v0 + x_dir * cx + y_dir * cy) for cx, cy in corners]
    r1 = [bm.verts.new(v1 + x_dir * cx + y_dir * cy) for cx, cy in corners]

    tile_u = region_key in _FULL_U_SEAMLESS
    u_len = length * u_scale if tile_u else min(1.0, max(0.2, length * u_scale))
    faces = []
    for i in range(4):
        j = (i + 1) % 4
        f = bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
        faces.append(f)
        uvs = [
            _map_uv(region_key, 0.0, 0.08, tile_u=tile_u),
            _map_uv(region_key, 0.0, 0.92, tile_u=tile_u),
            _map_uv(region_key, u_len, 0.92, tile_u=tile_u),
            _map_uv(region_key, u_len, 0.08, tile_u=tile_u),
        ]
        for lp, uv in zip(f.loops, uvs):
            lp[uv_layer].uv = uv

    for verts, r_key in ((list(reversed(r0)), end_region), (r1, end_region)):
        fc = bm.faces.new(verts)
        faces.append(fc)
        cap_uvs = [
            _map_uv(r_key, 0.15, 0.15, tile_u=False),
            _map_uv(r_key, 0.85, 0.15, tile_u=False),
            _map_uv(r_key, 0.85, 0.85, tile_u=False),
            _map_uv(r_key, 0.15, 0.85, tile_u=False),
        ]
        for lp, uv in zip(fc.loops, cap_uvs):
            lp[uv_layer].uv = uv
    return faces


def add_cylinder(bm, uv_layer, p0, p1, r0, r1, segs=8, region_key="cedar_timber",
                 cap0=True, cap1=True, cap0_region="timber_endgrain", cap1_region="timber_endgrain", u_scale=0.5):
    v0 = Vector(p0)
    v1 = Vector(p1)
    axis = v1 - v0
    length = axis.length
    if length < 1e-5:
        return []
    z_dir = axis.normalized()
    up_ref = Vector((0.0, 0.0, 1.0)) if abs(z_dir.z) < 0.94 else Vector((1.0, 0.0, 0.0))
    x_dir = up_ref.cross(z_dir).normalized()
    y_dir = z_dir.cross(x_dir).normalized()

    ring0, ring1 = [], []
    for i in range(segs):
        ang = 2.0 * math.pi * i / segs
        d = x_dir * math.cos(ang) + y_dir * math.sin(ang)
        ring0.append(bm.verts.new(v0 + d * r0))
        ring1.append(bm.verts.new(v1 + d * r1))

    faces = []
    tile_u = region_key in _FULL_U_SEAMLESS
    u_len = length * u_scale if tile_u else min(1.0, max(0.25, length * u_scale))
    for i in range(segs):
        j = (i + 1) % segs
        f = bm.faces.new((ring0[i], ring0[j], ring1[j], ring1[i]))
        faces.append(f)
        va, vb = i / segs, (i + 1) / segs
        uvs = [
            _map_uv(region_key, 0.0, va, tile_u=tile_u),
            _map_uv(region_key, 0.0, vb, tile_u=tile_u),
            _map_uv(region_key, u_len, vb, tile_u=tile_u),
            _map_uv(region_key, u_len, va, tile_u=tile_u),
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
        for k, lp in enumerate(fc.loops):
            ang = 2.0 * math.pi * k / segs
            lu = 0.5 + 0.44 * math.cos(ang)
            lv = 0.5 + 0.44 * math.sin(ang)
            lp[uv_layer].uv = _map_uv(r_key, lu, lv, tile_u=False)
    return faces


def add_spoked_wheel(bm, uv_layer, center, axis_vec, radius, thickness, spoke_count,
                     rim_region="oak_timber", tire_region="bloomery_iron", spoke_region="hornbeam_timber",
                     segs=16, add_tire=True):
    """Erzeugt ein Speichenrad (Nabe, Speichen, Radkranz, optional Eisenreif) um center/axis_vec."""
    c = Vector(center)
    ax = Vector(axis_vec).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(ax.z) < 0.92 else Vector((1.0, 0.0, 0.0))
    u_dir = ref.cross(ax).normalized()
    v_dir = ax.cross(u_dir).normalized()

    # Nabe
    hub_w = thickness * 1.45
    add_cylinder(bm, uv_layer, c - ax * (hub_w * 0.5), c + ax * (hub_w * 0.5),
                 radius * 0.22, radius * 0.22, segs=max(6, segs // 2),
                 region_key=rim_region, cap0_region="timber_endgrain", cap1_region="timber_endgrain")

    # Speichen
    for s in range(spoke_count):
        ang = 2.0 * math.pi * s / spoke_count
        rad_dir = u_dir * math.cos(ang) + v_dir * math.sin(ang)
        add_beam(bm, uv_layer, c + rad_dir * (radius * 0.16), c + rad_dir * (radius * 0.88),
                 thickness * 0.48, thickness * 0.48, spoke_region, end_region=spoke_region)

    # Radkranz als Ring-Segmente
    r_in = radius * 0.83
    r_out = radius * 0.96
    hw = thickness * 0.5
    for i in range(segs):
        a0 = 2.0 * math.pi * i / segs
        a1 = 2.0 * math.pi * (i + 1) / segs
        d0 = u_dir * math.cos(a0) + v_dir * math.sin(a0)
        d1 = u_dir * math.cos(a1) + v_dir * math.sin(a1)
        p_mid0 = c + d0 * ((r_in + r_out) * 0.5)
        p_mid1 = c + d1 * ((r_in + r_out) * 0.5)
        add_beam(bm, uv_layer, p_mid0, p_mid1, r_out - r_in, thickness, rim_region, end_region=rim_region)
        if add_tire:
            t0 = c + d0 * (radius * 0.975)
            t1 = c + d1 * (radius * 0.975)
            add_beam(bm, uv_layer, t0, t1, radius * 0.045, thickness * 1.04, tire_region, end_region=tire_region)


def add_pitched_roof(bm, uv_layer, cx, cy, z_eave, z_ridge, sx, sy, region_key="woven_reed_mat",
                     gable_axis="Y", thickness=0.14):
    """Satteldach mit First entlang Y (gable_axis='Y') oder X (gable_axis='X')."""
    hx, hy = 0.5 * sx, 0.5 * sy
    if gable_axis == "Y":
        pts_b = [(-hx, -hy, z_eave), (+hx, -hy, z_eave), (0.0, -hy, z_ridge)]
        pts_f = [(-hx, +hy, z_eave), (+hx, +hy, z_eave), (0.0, +hy, z_ridge)]
        for side_sign, x_eave in ((-1, -hx), (+1, +hx)):
            p0 = Vector((cx + x_eave, cy - hy, z_eave))
            p1 = Vector((cx + x_eave, cy + hy, z_eave))
            p2 = Vector((cx, cy + hy, z_ridge))
            p3 = Vector((cx, cy - hy, z_ridge))
            dz = Vector((0.0, 0.0, thickness))
            vs_b = [bm.verts.new(p) for p in (p0, p1, p2, p3)]
            vs_t = [bm.verts.new(p + dz) for p in (p0, p1, p2, p3)]
            if side_sign < 0:
                fs = [
                    bm.faces.new((vs_t[0], vs_t[1], vs_t[2], vs_t[3])),
                    bm.faces.new((vs_b[3], vs_b[2], vs_b[1], vs_b[0])),
                    bm.faces.new((vs_b[0], vs_b[1], vs_t[1], vs_t[0])),
                ]
            else:
                fs = [
                    bm.faces.new((vs_t[3], vs_t[2], vs_t[1], vs_t[0])),
                    bm.faces.new((vs_b[0], vs_b[1], vs_b[2], vs_b[3])),
                    bm.faces.new((vs_b[1], vs_b[0], vs_t[0], vs_t[1])),
                ]
            _apply_box_uv(fs, uv_layer, region_key, u_scale=0.35, v_fit=True)
        # Firstbalken
        add_beam(bm, uv_layer, (cx, cy - hy - 0.08, z_ridge), (cx, cy + hy + 0.08, z_ridge),
                 0.16, 0.18, "cedar_timber")
    else:
        for side_sign, y_eave in ((-1, -hy), (+1, +hy)):
            p0 = Vector((cx - hx, cy + y_eave, z_eave))
            p1 = Vector((cx + hx, cy + y_eave, z_eave))
            p2 = Vector((cx + hx, cy, z_ridge))
            p3 = Vector((cx - hx, cy, z_ridge))
            dz = Vector((0.0, 0.0, thickness))
            vs_b = [bm.verts.new(p) for p in (p0, p1, p2, p3)]
            vs_t = [bm.verts.new(p + dz) for p in (p0, p1, p2, p3)]
            if side_sign < 0:
                fs = [
                    bm.faces.new((vs_t[0], vs_t[1], vs_t[2], vs_t[3])),
                    bm.faces.new((vs_b[3], vs_b[2], vs_b[1], vs_b[0])),
                    bm.faces.new((vs_b[0], vs_b[1], vs_t[1], vs_t[0])),
                ]
            else:
                fs = [
                    bm.faces.new((vs_t[3], vs_t[2], vs_t[1], vs_t[0])),
                    bm.faces.new((vs_b[0], vs_b[1], vs_b[2], vs_b[3])),
                    bm.faces.new((vs_b[1], vs_b[0], vs_t[0], vs_t[1])),
                ]
            _apply_box_uv(fs, uv_layer, region_key, u_scale=0.35, v_fit=True)
        add_beam(bm, uv_layer, (cx - hx - 0.08, cy, z_ridge), (cx + hx + 0.08, cy, z_ridge),
                 0.16, 0.18, "cedar_timber")


def add_barrel(bm, uv_layer, cx, cy, z0, radius=0.28, height=0.72, segs=8):
    z_mid = z0 + height * 0.5
    add_cylinder(bm, uv_layer, (cx, cy, z0), (cx, cy, z_mid),
                 radius * 0.84, radius, segs=segs, region_key="oak_timber",
                 cap0=True, cap1=False, cap0_region="timber_endgrain")
    add_cylinder(bm, uv_layer, (cx, cy, z_mid), (cx, cy, z0 + height),
                 radius, radius * 0.84, segs=segs, region_key="oak_timber",
                 cap0=False, cap1=True, cap1_region="timber_endgrain")
    if segs >= 8:
        for f_h in (0.22, 0.78):
            zh = z0 + height * f_h
            add_cylinder(bm, uv_layer, (cx, cy, zh - 0.025), (cx, cy, zh + 0.025),
                         radius * 0.99, radius * 0.99, segs=segs, region_key="hemp_rope",
                         cap0=False, cap1=False)


def add_amphora(bm, uv_layer, cx, cy, z0, radius=0.18, height=0.58, segs=7):
    pts = [
        (0.00, 0.35),
        (0.32, 0.72),
        (0.62, 1.00),
        (0.80, 0.42),
        (0.92, 0.34),
        (1.00, 0.48),
    ]
    for k in range(len(pts) - 1):
        f0, r0 = pts[k]
        f1, r1 = pts[k + 1]
        add_cylinder(bm, uv_layer, (cx, cy, z0 + f0 * height), (cx, cy, z0 + f1 * height),
                     max(0.03, r0 * radius), max(0.03, r1 * radius), segs=segs,
                     region_key="rammed_earth_charcoal" if k == 0 else "straw_thatch",
                     cap0=(k == 0), cap1=(k == len(pts) - 2),
                     cap0_region="rammed_earth_charcoal", cap1_region="kopher_bitumen")


def add_grain_sack(bm, uv_layer, cx, cy, z0, sx=0.48, sy=0.34, sz=0.26):
    add_prism(bm, uv_layer, cx, cy, z0, z0 + sz * 0.72, sx, sy, sx * 0.90, sy * 0.88, "tent_linen_striped", v_fit=True)
    add_prism(bm, uv_layer, cx, cy, z0 + sz * 0.72, z0 + sz, sx * 0.90, sy * 0.88, sx * 0.55, sy * 0.52, "tent_linen_striped", v_fit=True)


def add_rope_coil(bm, uv_layer, cx, cy, z0, r_outer=0.36, turns=4, rope_r=0.035, segs=10):
    for t in range(turns):
        zt = z0 + rope_r + t * rope_r * 1.45
        rt = r_outer - t * rope_r * 0.45
        for i in range(segs):
            a0 = 2.0 * math.pi * i / segs
            a1 = 2.0 * math.pi * (i + 1) / segs
            p0 = (cx + rt * math.cos(a0), cy + rt * math.sin(a0), zt)
            p1 = (cx + rt * math.cos(a1), cy + rt * math.sin(a1), zt)
            add_beam(bm, uv_layer, p0, p1, rope_r * 2.0, rope_r * 1.8, "hemp_rope", end_region="hemp_rope")


# ==============================================================================
# A) WERFT- & BAUWERKS-MODULE (20 MODULE)
# ==============================================================================

def build_sy_scaffold_bay(bm, uv_layer, lod):
    """1a. Mehrstoekiges Baugeruest-Feld (6.0 x 2.6 x 8.4 m, -0.35 m Pfostenfundament)."""
    if lod >= 3:
        add_box(bm, uv_layer, 0.0, 0.0, -0.35, 8.2, 5.8, 2.4, "cedar_timber")
        return
    xs = [-2.8, 0.0, 2.8] if lod == 0 else [-2.8, 2.8]
    ys = [-1.15, 1.15]
    tiers = [2.6, 5.2, 7.8]
    post_r = 0.11

    # Vertikale Pfosten (-0.35 m Verankerung)
    for x in xs:
        for y in ys:
            add_cylinder(bm, uv_layer, (x, y, -0.35), (x, y, 8.35), post_r, post_r * 0.88,
                         segs=6 if lod == 0 else 5, region_key="oak_timber")

    # Ebenen-Riegel, Laufbohlen & Gelaender
    for tz in tiers:
        for y in ys:
            add_beam(bm, uv_layer, (-2.95, y, tz), (2.95, y, tz), 0.14, 0.16, "cedar_timber")
        for x in xs:
            add_beam(bm, uv_layer, (x, -1.25, tz), (x, 1.25, tz), 0.14, 0.14, "cedar_timber")
        if lod <= 1:
            # Laufbohlen
            plank_n = 4 if lod == 0 else 2
            for p in range(plank_n):
                py = -0.82 + p * (1.64 / max(1, plank_n - 1))
                add_box(bm, uv_layer, 0.0, py, tz + 0.08, tz + 0.14, 5.8, 0.36, "cedar_timber")
            # Gelaender
            add_beam(bm, uv_layer, (-2.85, -1.15, tz + 0.95), (2.85, -1.15, tz + 0.95), 0.08, 0.08, "cedar_timber")

    if lod <= 1:
        # Diagonalstreben + Seilbunde
        for z_lo, z_hi in ((0.1, 2.6), (2.6, 5.2), (5.2, 7.8)):
            add_beam(bm, uv_layer, (-2.8, -1.15, z_lo), (0.0, -1.15, z_hi), 0.09, 0.09, "oak_timber")
            add_beam(bm, uv_layer, (2.8, -1.15, z_lo), (0.0, -1.15, z_hi), 0.09, 0.09, "oak_timber")
            if lod == 0:
                add_beam(bm, uv_layer, (-2.8, 1.15, z_lo), (0.0, 1.15, z_hi), 0.09, 0.09, "oak_timber")
                add_beam(bm, uv_layer, (2.8, 1.15, z_lo), (0.0, 1.15, z_hi), 0.09, 0.09, "oak_timber")
                for x in (-2.8, 2.8):
                    add_cylinder(bm, uv_layer, (x, -1.15, z_hi - 0.1), (x, -1.15, z_hi + 0.12),
                                 0.14, 0.14, segs=6, region_key="hemp_rope")

    if lod == 0:
        # Sprossenleiter auf rechter Seite
        for lx in (1.75, 2.25):
            add_beam(bm, uv_layer, (lx, -1.35, -0.35), (lx, -0.95, 8.15), 0.06, 0.06, "hornbeam_timber")
        for r in range(14):
            fz = (r + 0.5) / 14.0
            lz = -0.1 + fz * 7.9
            ly = -1.33 + fz * 0.38
            add_beam(bm, uv_layer, (1.75, ly, lz), (2.25, ly, lz), 0.045, 0.045, "hornbeam_timber")


def build_sy_cribbing_block(bm, uv_layer, lod):
    """1b. Massive Eichen-Kielkloetze (2.4 x 1.8 x 1.45 m, -0.35 m Fundament)."""
    if lod >= 3:
        add_box(bm, uv_layer, 0.0, 0.0, -0.35, 1.45, 2.3, 1.7, "oak_timber")
        return
    # Schwere Grundschwelle bis -0.35 m
    add_box(bm, uv_layer, 0.0, 0.0, -0.35, 0.25, 2.4, 1.8, "oak_timber", top_region="mortise_joinery")
    layers = 4 if lod == 0 else (3 if lod == 1 else 2)
    for k in range(layers):
        z0 = 0.25 + k * 0.26
        z1 = z0 + 0.24
        if k % 2 == 0:
            for cy in (-0.52, 0.0, 0.52):
                add_beam(bm, uv_layer, (-1.15, cy, (z0 + z1) * 0.5), (1.15, cy, (z0 + z1) * 0.5), 0.34, 0.24, "oak_timber")
        else:
            for cx in (-0.75, 0.0, 0.75):
                add_beam(bm, uv_layer, (cx, -0.85, (z0 + z1) * 0.5), (cx, 0.85, (z0 + z1) * 0.5), 0.34, 0.24, "oak_timber")
    if lod <= 1:
        # Eichen-Keile oben + Seilbund
        z_top = 0.25 + layers * 0.26
        for wx in (-0.55, 0.55):
            add_prism(bm, uv_layer, wx, 0.0, z_top, z_top + 0.18, 0.52, 1.45, 0.38, 1.35, "hornbeam_timber")
        if lod == 0:
            add_box(bm, uv_layer, 0.0, 0.0, 0.35, 0.43, 2.24, 1.66, "hemp_rope")


def build_sy_ramp_module(bm, uv_layer, lod):
    """2a. Bohlen-Beladerampe mit Radabweisern (6.0 x 3.4 x 2.1 m, -0.35 m Stuetzfundamente)."""
    if lod >= 3:
        # Schraege Rampe als 1 Keilblock
        v = [
            bm.verts.new((-1.7, -3.0, -0.35)), bm.verts.new((1.7, -3.0, -0.35)),
            bm.verts.new((1.7, 3.0, -0.35)), bm.verts.new((-1.7, 3.0, -0.35)),
            bm.verts.new((-1.7, -3.0, 0.15)), bm.verts.new((1.7, -3.0, 0.15)),
            bm.verts.new((1.7, 3.0, 2.15)), bm.verts.new((-1.7, 3.0, 2.15)),
        ]
        fs = [
            bm.faces.new((v[4], v[5], v[6], v[7])),
            bm.faces.new((v[0], v[1], v[5], v[4])),
            bm.faces.new((v[1], v[2], v[6], v[5])),
            bm.faces.new((v[2], v[3], v[7], v[6])),
            bm.faces.new((v[3], v[0], v[4], v[7])),
            bm.faces.new((v[3], v[2], v[1], v[0])),
        ]
        _apply_box_uv(fs, uv_layer, "cedar_timber")
        return

    # Schraegbohlen + Unterzuege (Y=-3.0..+3.0, Z=0.10..2.10)
    for sx in (-1.35, 0.0, 1.35):
        add_beam(bm, uv_layer, (sx, -3.0, -0.02), (sx, 3.0, 1.98), 0.24, 0.26, "oak_timber")

    # Fahrbahnplatte + Radabweiser
    p_bot = [(-1.68, -3.0, 0.08), (1.68, -3.0, 0.08), (1.68, 3.0, 2.08), (-1.68, 3.0, 2.08)]
    p_top = [(-1.68, -3.0, 0.20), (1.68, -3.0, 0.20), (1.68, 3.0, 2.20), (-1.68, 3.0, 2.20)]
    vb = [bm.verts.new(p) for p in p_bot]
    vt = [bm.verts.new(p) for p in p_top]
    ramp_fs = [
        bm.faces.new((vt[0], vt[1], vt[2], vt[3])),
        bm.faces.new((vb[3], vb[2], vb[1], vb[0])),
        bm.faces.new((vb[0], vb[1], vt[1], vt[0])),
        bm.faces.new((vb[1], vb[2], vt[2], vt[1])),
        bm.faces.new((vb[2], vb[3], vt[3], vt[2])),
        bm.faces.new((vb[3], vb[0], vt[0], vt[3])),
    ]
    _apply_box_uv(ramp_fs, uv_layer, "cedar_timber", u_scale=0.4)

    # Radabweiser links & rechts
    for rx in (-1.56, 1.56):
        add_beam(bm, uv_layer, (rx, -2.95, 0.30), (rx, 2.95, 2.30), 0.22, 0.20, "oak_timber")

    # Stuetzboecke bis -0.35 m
    bents = [(-2.6, 0.15), (-0.8, 0.72), (1.0, 1.32), (2.7, 1.90)] if lod <= 1 else [(-2.6, 0.15), (2.7, 1.90)]
    for by, bz in bents:
        for bx in (-1.35, 1.35):
            add_beam(bm, uv_layer, (bx, by, -0.35), (bx, by, bz), 0.24, 0.24, "oak_timber")
        add_beam(bm, uv_layer, (-1.45, by, bz - 0.10), (1.45, by, bz - 0.10), 0.20, 0.20, "oak_timber")
        if lod == 0 and bz > 0.6:
            add_beam(bm, uv_layer, (-1.35, by, -0.10), (1.35, by, bz - 0.15), 0.11, 0.11, "cedar_timber")

    if lod == 0:
        # Quer-Trittleisten auf Rampe
        for i in range(10):
            f = (i + 0.5) / 10.0
            cy = -2.85 + f * 5.7
            cz = 0.22 + f * 1.90
            add_beam(bm, uv_layer, (-1.38, cy, cz), (1.38, cy, cz), 0.08, 0.06, "hornbeam_timber")


def build_sy_drawbridge_flap(bm, uv_layer, lod):
    """2b. Zugbruecken-Klappe (Origin EXAKT auf Scharnierachse (0,0,0) entlang X!)."""
    if lod >= 3:
        add_box(bm, uv_layer, 0.0, 1.8, -0.09, 0.11, 3.2, 3.6, "oak_timber")
        return
    # Scharnierwelle exakt auf (0,0,0) entlang X
    add_cylinder(bm, uv_layer, (-1.65, 0.0, 0.0), (1.65, 0.0, 0.0), 0.075, 0.075,
                 segs=8 if lod == 0 else 6, region_key="bloomery_iron", cap0_region="bloomery_iron", cap1_region="bloomery_iron")
    # Scharnierbaender
    if lod <= 1:
        for hx in (-1.15, 0.0, 1.15):
            add_beam(bm, uv_layer, (hx, -0.05, 0.09), (hx, 1.45, 0.09), 0.14, 0.05, "bloomery_iron", end_region="bloomery_iron")

    # Haupt-Klappe (Y = 0.0..3.6 m)
    add_box(bm, uv_layer, 0.0, 1.80, -0.08, 0.08, 3.16, 3.60, "cedar_timber", top_region="mortise_joinery")
    # Seitenholme & Querriegel
    for sx in (-1.48, 1.48):
        add_beam(bm, uv_layer, (sx, 0.02, 0.12), (sx, 3.55, 0.12), 0.18, 0.14, "oak_timber")
    if lod <= 1:
        for cy in (0.6, 1.4, 2.2, 3.0, 3.52):
            add_beam(bm, uv_layer, (-1.40, cy, -0.11), (1.40, cy, -0.11), 0.14, 0.10, "oak_timber")
    if lod == 0:
        # Bronze-Zugringe & Seilenden an Klappenspitze (Y=3.45)
        for rx in (-1.35, 1.35):
            add_cylinder(bm, uv_layer, (rx, 3.45, 0.16), (rx, 3.45, 0.34), 0.11, 0.11, segs=8, region_key="tin_bronze",
                         cap0_region="tin_bronze", cap1_region="tin_bronze")
            add_beam(bm, uv_layer, (rx, 3.45, 0.32), (rx, 3.10, 1.15), 0.06, 0.06, "hemp_rope", end_region="hemp_rope")


def build_sy_crane_aframe(bm, uv_layer, lod):
    """3a. Schwerer Bockkran-A-Rahmen (4.6 x 4.4 x 8.6 m, -0.35 m Ballast-/Stuetzsohle)."""
    if lod >= 3:
        add_beam(bm, uv_layer, (-2.0, -1.4, -0.35), (0.0, 1.8, 8.4), 0.38, 0.38, "oak_timber")
        add_beam(bm, uv_layer, (2.0, -1.4, -0.35), (0.0, 1.8, 8.4), 0.38, 0.38, "oak_timber")
        add_box(bm, uv_layer, 0.0, -1.5, -0.35, 0.45, 4.2, 1.6, "cut_basalt")
        return

    # Schwellen + Ballast-Schlitten (-0.35 m)
    for sx in (-2.05, 2.05):
        add_box(bm, uv_layer, sx, 0.0, -0.35, 0.20, 0.55, 4.3, "oak_timber")
    add_box(bm, uv_layer, 0.0, -1.65, -0.35, 0.48, 4.5, 1.35, "cut_basalt")

    # Vorwaerts geneigter Haupt-A-Bock
    peak = (0.0, 1.95, 8.45)
    for sx in (-2.05, 2.05):
        add_beam(bm, uv_layer, (sx, 0.85, 0.10), (-0.28 if sx < 0 else 0.28, 1.95, 8.45), 0.30, 0.30, "cedar_timber")
        # Hintere Stuetzstrebe
        add_beam(bm, uv_layer, (sx, -1.75, 0.20), (-0.24 if sx < 0 else 0.24, 1.75, 8.20), 0.24, 0.24, "oak_timber")
        # Senkrechte Winden-Lagerstuetze
        add_beam(bm, uv_layer, (sx * 0.72, -0.65, 0.12), (sx * 0.72, -0.65, 1.45), 0.24, 0.24, "oak_timber")

    # Querjoche + Kronschwelle
    add_beam(bm, uv_layer, (-1.65, 1.15, 2.55), (1.65, 1.15, 2.55), 0.22, 0.22, "oak_timber")
    add_beam(bm, uv_layer, (-1.05, 1.50, 5.45), (1.05, 1.50, 5.45), 0.20, 0.20, "oak_timber")
    add_beam(bm, uv_layer, (-0.55, 1.95, 8.40), (0.55, 1.95, 8.40), 0.26, 0.28, "oak_timber")

    if lod <= 1:
        # Bronze-Seilrolle oben + Abspannseil
        add_cylinder(bm, uv_layer, (-0.18, 1.95, 8.05), (0.18, 1.95, 8.05), 0.34, 0.34,
                     segs=10 if lod == 0 else 6, region_key="tin_bronze",
                     cap0_region="tin_bronze", cap1_region="tin_bronze")
        add_beam(bm, uv_layer, (0.0, -1.90, 0.45), (0.0, 1.85, 8.35), 0.07, 0.07, "hemp_rope", end_region="hemp_rope")
    if lod == 0:
        # Kopher-Ballaststeine auf Schlitten + Hubseil nach unten
        for bx in (-1.3, 0.0, 1.3):
            add_box(bm, uv_layer, bx, -1.65, 0.48, 0.92, 0.95, 0.85, "cut_basalt")
        add_beam(bm, uv_layer, (0.0, -0.65, 1.25), (0.0, 1.95, 8.05), 0.06, 0.06, "hemp_rope", end_region="hemp_rope")


def build_sy_crane_winch_rotor(bm, uv_layer, lod):
    """3b. Drehbare Seilwinde (Origin EXAKT auf Wellenachse (0,0,0) entlang X!)."""
    if lod >= 3:
        add_cylinder(bm, uv_layer, (-1.05, 0.0, 0.0), (1.05, 0.0, 0.0), 0.34, 0.34, segs=6, region_key="hemp_rope")
        return
    segs = 12 if lod == 0 else (8 if lod == 1 else 6)
    # Zentralachse + Lagerzapfen
    add_cylinder(bm, uv_layer, (-1.28, 0.0, 0.0), (1.28, 0.0, 0.0), 0.09, 0.09, segs=segs,
                 region_key="tin_bronze", cap0_region="tin_bronze", cap1_region="tin_bronze")
    # Seiltrommel mit aufgewickeltem Hanftau
    add_cylinder(bm, uv_layer, (-0.82, 0.0, 0.0), (0.82, 0.0, 0.0), 0.25, 0.25, segs=segs,
                 region_key="oak_timber", cap0_region="timber_endgrain", cap1_region="timber_endgrain")
    add_cylinder(bm, uv_layer, (-0.70, 0.0, 0.0), (0.70, 0.0, 0.0), 0.31, 0.31, segs=segs,
                 region_key="hemp_rope", cap0=False, cap1=False)
    # Seitliche Speichenkraenze & Handspeichen
    for fx in (-0.88, 0.88):
        add_cylinder(bm, uv_layer, (fx - 0.06, 0.0, 0.0), (fx + 0.06, 0.0, 0.0), 0.54, 0.54,
                     segs=segs, region_key="oak_timber", cap0_region="timber_endgrain", cap1_region="timber_endgrain")
        if lod <= 1:
            n_spokes = 8 if lod == 0 else 4
            for i in range(n_spokes):
                ang = 2.0 * math.pi * i / n_spokes
                dy, dz = math.cos(ang), math.sin(ang)
                add_beam(bm, uv_layer, (fx, dy * 0.20, dz * 0.20), (fx, dy * 0.92, dz * 0.92),
                         0.08, 0.08, "hornbeam_timber")
    if lod == 0:
        # Sperrklinkenrad aus Zinnbronze
        add_cylinder(bm, uv_layer, (-1.04, 0.0, 0.0), (-0.96, 0.0, 0.0), 0.42, 0.42,
                     segs=12, region_key="tin_bronze", cap0_region="tin_bronze", cap1_region="tin_bronze")


def build_sy_crane_timber_load(bm, uv_layer, lod):
    """3c. Haengender 5-t-Zedernbalken mit Hanfseil-Schlinge (Origin EXAKT im Aufhaenge-Schaekel (0,0,0)!)."""
    if lod >= 3:
        add_beam(bm, uv_layer, (-3.6, 0.0, -1.65), (3.6, 0.0, -1.65), 0.50, 0.50, "cedar_timber")
        return
    # Aufhaengering oben auf (0,0,0)
    add_cylinder(bm, uv_layer, (-0.10, 0.0, 0.0), (0.10, 0.0, 0.0), 0.14, 0.14,
                 segs=8 if lod == 0 else 6, region_key="tin_bronze",
                 cap0_region="tin_bronze", cap1_region="tin_bronze")
    # V-Schlinge aus Hanfseil
    for sx in (-1.65, 1.65):
        add_beam(bm, uv_layer, (0.0, 0.0, -0.05), (sx, 0.0, -1.42), 0.065, 0.065, "hemp_rope", end_region="hemp_rope")
        # Umschlingungsband um Balken
        add_box(bm, uv_layer, sx, 0.0, -1.94, -1.36, 0.18, 0.56, "hemp_rope")
    # Massiver 7.2 m Zedernbalken (5 Tonnen)
    add_beam(bm, uv_layer, (-3.6, 0.0, -1.65), (3.6, 0.0, -1.65), 0.48, 0.48, "cedar_timber")
    if lod == 0:
        # Angehaengter Begleit-Kantholzstamm / Keileisen
        add_beam(bm, uv_layer, (-2.8, 0.28, -1.72), (2.8, 0.28, -1.72), 0.20, 0.22, "oak_timber")


def build_sy_pitch_kiln(bm, uv_layer, lod):
    """4. Gemauerter Kopher-Pechsiedeofen mit Kessel, Glutraum, Kelle & Pechkuebeln (-0.35 m Sockel)."""
    if lod >= 3:
        add_box(bm, uv_layer, 0.0, 0.0, -0.35, 1.45, 2.8, 2.4, "cut_basalt")
        add_cylinder(bm, uv_layer, (0.0, 0.0, 1.25), (0.0, 0.0, 1.82), 0.72, 0.68, segs=6,
                     region_key="tin_bronze", cap1_region="kopher_bitumen")
        return

    # Basalt-Ofensockel & gemauerter Feuerungskranz
    add_box(bm, uv_layer, 0.0, 0.0, -0.35, 0.22, 3.2, 2.8, "cut_basalt")
    add_cylinder(bm, uv_layer, (0.0, 0.0, 0.22), (0.0, 0.0, 1.38), 1.18, 1.05,
                 segs=12 if lod == 0 else 8, region_key="cut_basalt", cap0=False, cap1=True, cap1_region="cut_basalt")
    # Hinterer Rauchabzug / Kamin
    add_prism(bm, uv_layer, 0.0, 1.05, 0.22, 2.45, 0.78, 0.72, 0.54, 0.50, "cut_basalt")

    # Glut im vorderen Feuerungsmaul (-Y)
    add_box(bm, uv_layer, 0.0, -0.96, 0.24, 0.74, 0.78, 0.34, "glowing_embers")
    # Gemauerter Feuerungsbogen-Sturz
    add_box(bm, uv_layer, 0.0, -1.04, 0.74, 0.96, 1.05, 0.28, "cut_basalt")

    # Grosser Zinnbronze-Kessel mit Kopher-Bitumen-Fuellung
    add_cylinder(bm, uv_layer, (0.0, 0.0, 1.25), (0.0, 0.0, 1.82), 0.68, 0.78,
                 segs=12 if lod == 0 else 8, region_key="tin_bronze", cap0=False, cap1=False)
    add_cylinder(bm, uv_layer, (0.0, 0.0, 1.66), (0.0, 0.0, 1.78), 0.73, 0.74,
                 segs=12 if lod == 0 else 8, region_key="kopher_bitumen",
                 cap0=False, cap1=True, cap1_region="kopher_bitumen")

    if lod <= 1:
        # Schoepfkelle auf Kesselrand + 2 Pechkuebel auf Nebenbank
        add_beam(bm, uv_layer, (-0.15, -0.15, 1.80), (-1.15, -0.85, 2.18), 0.06, 0.06, "hornbeam_timber")
        add_cylinder(bm, uv_layer, (-0.15, -0.15, 1.70), (-0.15, -0.15, 1.84), 0.14, 0.18, segs=8, region_key="tin_bronze")
        for bx, by in ((1.15, -0.85), (1.35, -0.25)):
            add_cylinder(bm, uv_layer, (bx, by, 0.22), (bx, by, 0.66), 0.22, 0.26, segs=8,
                         region_key="oak_timber", cap1_region="kopher_bitumen")
    if lod == 0:
        # Brennstoff-Holzscheite neben Ofen
        for lz in (0.30, 0.44):
            add_cylinder(bm, uv_layer, (-1.45, -0.75, lz), (-0.95, -0.25, lz), 0.08, 0.08, segs=6, region_key="cedar_timber")


def build_sy_smithy_forge(bm, uv_layer, lod):
    """5. Ueberdachte Tubal-Kain-Schmiede mit Lehm-Esse, Doppel-Blasebalg, Amboss, Troeg & Werkzeug (-0.35 m)."""
    if lod >= 3:
        for px, py in ((-2.2, -1.7), (2.2, -1.7), (-2.2, 1.7), (2.2, 1.7)):
            add_box(bm, uv_layer, px, py, -0.35, 2.7, 0.22, 0.22, "oak_timber")
        add_pitched_roof(bm, uv_layer, 0.0, 0.0, 2.65, 3.85, 5.1, 4.1, "woven_reed_mat")
        add_box(bm, uv_layer, -1.1, 0.6, -0.35, 1.15, 1.5, 1.3, "cut_basalt")
        return

    # 4 Eckpfosten (-0.35 m) + Pult-/Satteldach
    for px, py in ((-2.25, -1.75), (2.25, -1.75), (-2.25, 1.75), (2.25, 1.75)):
        add_cylinder(bm, uv_layer, (px, py, -0.35), (px, py, 2.75), 0.13, 0.12,
                     segs=6 if lod == 0 else 5, region_key="oak_timber")
    for y in (-1.75, 1.75):
        add_beam(bm, uv_layer, (-2.35, y, 2.72), (2.35, y, 2.72), 0.16, 0.18, "cedar_timber")
    for x in (-2.25, 2.25):
        add_beam(bm, uv_layer, (x, -1.85, 2.72), (x, 1.85, 2.72), 0.16, 0.18, "cedar_timber")
    add_pitched_roof(bm, uv_layer, 0.0, 0.0, 2.74, 3.88, 5.2, 4.2, "woven_reed_mat", gable_axis="X")

    # Lehm-/Basalt-Esse links hinten + Gluehendes Glutbett
    add_box(bm, uv_layer, -1.15, 0.65, -0.35, 0.92, 1.55, 1.35, "cut_basalt")
    add_box(bm, uv_layer, -1.15, 0.65, 0.92, 1.08, 0.95, 0.78, "glowing_embers")
    add_prism(bm, uv_layer, -1.15, 0.98, 1.08, 2.65, 1.15, 0.68, 0.62, 0.45, "rammed_earth_charcoal")

    # Doppel-Blasebalg + Duese rechts der Esse
    add_beam(bm, uv_layer, (-0.35, 0.65, 0.96), (-0.78, 0.65, 0.98), 0.09, 0.09, "tin_bronze", end_region="tin_bronze")
    for by in (0.35, 0.95):
        add_prism(bm, uv_layer, 0.25, by, 0.65, 1.15, 0.95, 0.42, 0.85, 0.34, "tent_linen_striped")
        add_box(bm, uv_layer, 0.25, by, 0.62, 0.68, 1.05, 0.46, "oak_timber")
    if lod <= 1:
        add_box(bm, uv_layer, 0.25, 0.65, -0.35, 0.62, 0.95, 1.05, "oak_timber")

    # Eichenstock + dunkler Rennschmiedeeisen-Amboss in der Mitte
    add_cylinder(bm, uv_layer, (0.45, -0.55, -0.35), (0.45, -0.55, 0.56), 0.34, 0.32,
                 segs=8 if lod == 0 else 6, region_key="oak_timber")
    add_box(bm, uv_layer, 0.45, -0.55, 0.56, 0.72, 0.52, 0.30, "bloomery_iron")
    add_prism(bm, uv_layer, 0.45, -0.55, 0.72, 0.88, 0.62, 0.26, 0.78, 0.28, "bloomery_iron")
    if lod <= 1:
        add_cylinder(bm, uv_layer, (0.82, -0.55, 0.80), (1.18, -0.55, 0.82), 0.09, 0.025, segs=6, region_key="bloomery_iron")

    # Loeschwassertrog (Quellstein) + Werkzeugstaender (Zinnbronze)
    add_box(bm, uv_layer, 1.48, 0.55, -0.35, 0.58, 0.88, 0.64, "wet_spring_stone", top_region="kopher_bitumen")
    if lod <= 1:
        add_beam(bm, uv_layer, (-1.75, -1.25, -0.35), (-1.75, -1.25, 1.35), 0.10, 0.10, "oak_timber")
        add_beam(bm, uv_layer, (-0.75, -1.25, -0.35), (-0.75, -1.25, 1.35), 0.10, 0.10, "oak_timber")
        add_beam(bm, uv_layer, (-1.82, -1.25, 1.25), (-0.68, -1.25, 1.25), 0.10, 0.10, "cedar_timber")
        if lod == 0:
            for tx in (-1.52, -1.25, -0.98):
                add_beam(bm, uv_layer, (tx, -1.22, 0.55), (tx, -1.22, 1.22), 0.05, 0.03, "tin_bronze", end_region="tin_bronze")
                add_box(bm, uv_layer, tx, -1.22, 0.45, 0.58, 0.14, 0.06, "bloomery_iron")


def build_sy_charcoal_kiln(bm, uv_layer, lod):
    """6. Kuppel-Holzkohlemeiler mit geschichteten Holzstoessen, Lueftungszuegen & Erdmantel (-0.35 m)."""
    if lod >= 3:
        add_cylinder(bm, uv_layer, (0.0, 0.0, -0.35), (0.0, 0.0, 2.35), 2.35, 0.55, segs=8, region_key="rammed_earth_charcoal")
        return
    segs = 14 if lod == 0 else (10 if lod == 1 else 7)
    # Erd-Schuerze (-0.35 m) + abgestufte Kuppel
    add_cylinder(bm, uv_layer, (0.0, 0.0, -0.35), (0.0, 0.0, 0.25), 2.42, 2.25, segs=segs, region_key="rammed_earth_charcoal")
    add_cylinder(bm, uv_layer, (0.0, 0.0, 0.25), (0.0, 0.0, 1.45), 2.25, 1.45, segs=segs, region_key="rammed_earth_charcoal", cap0=False, cap1=False)
    add_cylinder(bm, uv_layer, (0.0, 0.0, 1.45), (0.0, 0.0, 2.35), 1.45, 0.48, segs=segs, region_key="rammed_earth_charcoal", cap0=False, cap1=True, cap1_region="glowing_embers")

    # Geschichteter Holzstoss-Ausschnitt auf Vorderseite (-Y)
    add_cylinder(bm, uv_layer, (0.0, -1.28, 0.15), (0.0, -1.28, 1.38), 0.72, 0.52, segs=6, region_key="cedar_timber")
    if lod <= 1:
        # Radiale Holzscheite sichtbar im Anschnitt + Lueftungs-Glutschlitze
        n_logs = 7 if lod == 0 else 4
        for i in range(n_logs):
            ang = math.radians(-125 + i * (70.0 / max(1, n_logs - 1)))
            lx = math.cos(ang) * 1.68
            ly = math.sin(ang) * 1.68
            add_cylinder(bm, uv_layer, (lx * 0.55, ly * 0.55, 0.35 + (i % 2) * 0.22),
                         (lx, ly, 0.28 + (i % 2) * 0.22), 0.11, 0.10, segs=6, region_key="cedar_timber")
        for v in range(6):
            ang = 2.0 * math.pi * v / 6.0
            vx, vy = math.cos(ang) * 2.08, math.sin(ang) * 2.08
            add_box(bm, uv_layer, vx, vy, 0.05, 0.28, 0.24, 0.24, "glowing_embers")


def build_sy_sawmill_base(bm, uv_layer, lod):
    """7a. Galgenportal & Basalt-Ring fuer Goepel-Saegewerk (Origin auf Koenigswellen-Mitte (0,0,0), -0.35 m)."""
    if lod >= 3:
        add_cylinder(bm, uv_layer, (0.0, 0.0, -0.35), (0.0, 0.0, 0.16), 4.4, 4.3, segs=10, region_key="cut_basalt")
        add_beam(bm, uv_layer, (-2.8, 0.0, -0.35), (-2.8, 0.0, 4.2), 0.32, 0.32, "oak_timber")
        add_beam(bm, uv_layer, (2.8, 0.0, -0.35), (2.8, 0.0, 4.2), 0.32, 0.32, "oak_timber")
        add_beam(bm, uv_layer, (-3.0, 0.0, 4.15), (3.0, 0.0, 4.15), 0.34, 0.34, "oak_timber")
        return

    # Basalt-Laufring fuer Ochsen (R=3.3..4.4 m, -0.35 m Fundament)
    segs = 16 if lod == 0 else (12 if lod == 1 else 8)
    for i in range(segs):
        a0 = 2.0 * math.pi * i / segs
        a1 = 2.0 * math.pi * (i + 1) / segs
        am = 0.5 * (a0 + a1)
        r_mid = 3.85
        seg_len = 2.0 * r_mid * math.sin(math.pi / segs) + 0.14
        cx, cy = r_mid * math.cos(am), r_mid * math.sin(am)
        # Sektor als gedrehter Quader
        dx, dy = math.cos(am), math.sin(am)
        tx, ty = -dy, dx
        hw, hl = 0.56, 0.5 * seg_len
        pts = [
            (cx - dx * hw - tx * hl, cy - dy * hw - ty * hl),
            (cx + dx * hw - tx * hl, cy + dy * hw - ty * hl),
            (cx + dx * hw + tx * hl, cy + dy * hw + ty * hl),
            (cx - dx * hw + tx * hl, cy - dy * hw + ty * hl),
        ]
        vb = [bm.verts.new((px, py, -0.35)) for px, py in pts]
        vt = [bm.verts.new((px, py, 0.12)) for px, py in pts]
        fs = [bm.faces.new((vt[0], vt[1], vt[2], vt[3])), bm.faces.new((vb[3], vb[2], vb[1], vb[0]))]
        for k in range(4):
            fs.append(bm.faces.new((vb[k], vb[(k + 1) % 4], vt[(k + 1) % 4], vt[k])))
        _apply_box_uv(fs, uv_layer, "cut_basalt", u_scale=0.25)

    # Zentraler Basalt-Lagerblock der Koenigswelle
    add_cylinder(bm, uv_layer, (0.0, 0.0, -0.35), (0.0, 0.0, 0.24), 0.72, 0.58, segs=8, region_key="cut_basalt")

    # Schweres Eichen-Galgenportal (X = -2.85 / +2.85)
    for sx in (-2.85, 2.85):
        add_box(bm, uv_layer, sx, 0.0, -0.35, 0.35, 0.65, 1.35, "cut_basalt")
        add_beam(bm, uv_layer, (sx, 0.0, -0.10), (sx, 0.0, 4.25), 0.34, 0.34, "oak_timber")
        add_beam(bm, uv_layer, (sx, -0.95, -0.35), (sx, 0.0, 2.85), 0.22, 0.22, "oak_timber")
        add_beam(bm, uv_layer, (sx, 0.95, -0.35), (sx, 0.0, 2.85), 0.22, 0.22, "oak_timber")
    add_beam(bm, uv_layer, (-3.15, 0.0, 4.20), (3.15, 0.0, 4.20), 0.36, 0.38, "oak_timber")
    if lod <= 1:
        add_beam(bm, uv_layer, (-2.85, 0.0, 2.95), (-1.65, 0.0, 4.20), 0.20, 0.20, "cedar_timber")
        add_beam(bm, uv_layer, (2.85, 0.0, 2.95), (1.65, 0.0, 4.20), 0.20, 0.20, "cedar_timber")
        # Erhoehter Lagerbock fuer Vorgelegewelle (Wellenmitte Z = 2.88 m ueber 48er-Kammrad)
        add_box(bm, uv_layer, 0.0, 1.45, -0.35, 2.86, 0.56, 0.56, "cut_basalt")
        add_beam(bm, uv_layer, (-2.85, 0.0, 2.84), (0.0, 1.45, 2.84), 0.18, 0.20, "oak_timber")


def build_sy_sawmill_capstan_rotor(bm, uv_layer, lod):
    """7b. Drehendes 48er-Kammrad + Jochbalken (Origin EXAKT auf Koenigswellen-Mitte (0,0,0)!)."""
    if lod >= 3:
        add_cylinder(bm, uv_layer, (0.0, 0.0, 0.10), (0.0, 0.0, 4.10), 0.22, 0.20, segs=6, region_key="oak_timber")
        add_cylinder(bm, uv_layer, (0.0, 0.0, 2.25), (0.0, 0.0, 2.55), 1.65, 1.65, segs=10, region_key="hornbeam_timber")
        add_beam(bm, uv_layer, (-3.8, 0.0, 1.45), (3.8, 0.0, 1.45), 0.22, 0.22, "cedar_timber")
        return

    # Koenigswelle (Z=0.05..4.15 m)
    add_cylinder(bm, uv_layer, (0.0, 0.0, 0.05), (0.0, 0.0, 4.15), 0.22, 0.20,
                 segs=10 if lod == 0 else 6, region_key="oak_timber",
                 cap0_region="tin_bronze", cap1_region="tin_bronze")

    # 48er-Kammrad auf Z = 2.35 m (Radius = 1.62 m)
    segs_rim = 16 if lod == 0 else 10
    r_wheel = 1.62
    for i in range(segs_rim):
        a0 = 2.0 * math.pi * i / segs_rim
        a1 = 2.0 * math.pi * (i + 1) / segs_rim
        add_beam(bm, uv_layer, (r_wheel * math.cos(a0), r_wheel * math.sin(a0), 2.35),
                 (r_wheel * math.cos(a1), r_wheel * math.sin(a1), 2.35), 0.24, 0.22, "oak_timber")
    # Rad-Speichen
    for s in range(4):
        ang = s * math.pi * 0.5
        add_beam(bm, uv_layer, (-r_wheel * math.cos(ang), -r_wheel * math.sin(ang), 2.35),
                 (r_wheel * math.cos(ang), r_wheel * math.sin(ang), 2.35), 0.16, 0.16, "oak_timber")

    # 48 Hainbuchen-Kaemme (Zaehe) bei LOD0, 24 bei LOD1, 12 bei LOD2
    cog_n = 48 if lod == 0 else (24 if lod == 1 else 12)
    cog_w = 0.08 if lod == 0 else 0.13
    for c in range(cog_n):
        ang = 2.0 * math.pi * c / cog_n
        cx, cy = r_wheel * math.cos(ang), r_wheel * math.sin(ang)
        add_box(bm, uv_layer, cx, cy, 2.45, 2.61, cog_w, cog_w, "hornbeam_timber")

    # Sweeping Jochbalken (Z = 1.45 m, R = 4.05 m) + Zugstrebe + Ochsenjoch-Boegen
    add_beam(bm, uv_layer, (-4.05, 0.0, 1.45), (4.05, 0.0, 1.45), 0.20, 0.22, "cedar_timber")
    add_beam(bm, uv_layer, (-2.6, 0.0, 1.52), (0.0, 0.0, 3.25), 0.14, 0.14, "cedar_timber")
    add_beam(bm, uv_layer, (2.6, 0.0, 1.52), (0.0, 0.0, 3.25), 0.14, 0.14, "cedar_timber")
    if lod <= 1:
        for sx in (-3.65, 3.65):
            add_beam(bm, uv_layer, (sx, -0.55, 1.38), (sx, 0.55, 1.38), 0.12, 0.12, "hornbeam_timber")
            for by in (-0.38, 0.38):
                add_cylinder(bm, uv_layer, (sx, by, 0.95), (sx, by, 1.42), 0.045, 0.045, segs=5, region_key="hornbeam_timber")


def build_sy_sawmill_driveshaft(bm, uv_layer, lod):
    """7c. Vorgelegewelle mit 8er-Stockritzel, Schwungrad & Kurbelzapfen (Origin EXAKT auf Wellenachse (0,0,0)!)."""
    if lod >= 3:
        add_cylinder(bm, uv_layer, (-2.3, 0.0, 0.0), (2.3, 0.0, 0.0), 0.14, 0.14, segs=6, region_key="oak_timber")
        add_cylinder(bm, uv_layer, (1.2, 0.0, 0.0), (1.38, 0.0, 0.0), 0.92, 0.92, segs=8, region_key="oak_timber")
        return
    segs = 10 if lod == 0 else 6
    # Vorgelegewelle entlang X
    add_cylinder(bm, uv_layer, (-2.35, 0.0, 0.0), (2.35, 0.0, 0.0), 0.13, 0.13, segs=segs,
                 region_key="oak_timber", cap0_region="tin_bronze", cap1_region="tin_bronze")

    # 8er-Stockritzel (bei X = -1.35 m, R = 0.34 m)
    for dx in (-1.62, -1.08):
        add_cylinder(bm, uv_layer, (dx - 0.04, 0.0, 0.0), (dx + 0.04, 0.0, 0.0), 0.36, 0.36,
                     segs=segs, region_key="oak_timber", cap0_region="timber_endgrain", cap1_region="timber_endgrain")
    staves = 8 if lod <= 1 else 4
    for i in range(staves):
        ang = 2.0 * math.pi * i / staves
        sy, sz = 0.27 * math.cos(ang), 0.27 * math.sin(ang)
        add_cylinder(bm, uv_layer, (-1.60, sy, sz), (-1.10, sy, sz), 0.042, 0.042, segs=5, region_key="hornbeam_timber")

    # Schweres Speichen-Schwungrad (bei X = +1.15 m, R = 0.94 m)
    add_spoked_wheel(bm, uv_layer, (1.15, 0.0, 0.0), (1.0, 0.0, 0.0), 0.94, 0.18,
                     6 if lod == 0 else 4, rim_region="oak_timber", tire_region="bloomery_iron",
                     spoke_region="cedar_timber", segs=12 if lod == 0 else 8, add_tire=(lod <= 1))

    # Exzenter-Kurbelarm & Kurbelzapfen (X = +2.35 m, R_crank = 0.36 m)
    add_beam(bm, uv_layer, (2.32, 0.0, -0.06), (2.32, 0.0, 0.38), 0.14, 0.16, "bloomery_iron", end_region="bloomery_iron")
    add_cylinder(bm, uv_layer, (2.32, 0.0, 0.34), (2.68, 0.0, 0.34), 0.075, 0.075, segs=8,
                 region_key="tin_bronze", cap0_region="tin_bronze", cap1_region="tin_bronze")


def build_sy_sawmill_frame(bm, uv_layer, lod):
    """7d. Vertikales Saegegatter mit Bronze-Saegeblatt (Origin EXAKT auf unterem Gatterzapfen (0,0,0)!)."""
    if lod >= 3:
        add_box(bm, uv_layer, 0.0, 0.0, 0.0, 2.55, 1.45, 0.16, "oak_timber")
        return
    # Unterer & oberer Querholm + 2 Seitenholme
    add_beam(bm, uv_layer, (-0.75, 0.0, 0.10), (0.75, 0.0, 0.10), 0.16, 0.18, "oak_timber")
    add_beam(bm, uv_layer, (-0.75, 0.0, 2.45), (0.75, 0.0, 2.45), 0.16, 0.18, "oak_timber")
    for sx in (-0.68, 0.68):
        add_beam(bm, uv_layer, (sx, 0.0, 0.04), (sx, 0.0, 2.52), 0.15, 0.16, "oak_timber")
    # Zapfenlager unten auf (0,0,0)
    add_cylinder(bm, uv_layer, (0.0, -0.14, 0.0), (0.0, 0.14, 0.0), 0.065, 0.065, segs=6, region_key="tin_bronze")

    # Zinnbronze-Saegeblatt (Metallic=1.0) in Mitte
    add_box(bm, uv_layer, 0.0, 0.0, 0.18, 2.38, 0.16, 0.035, "tin_bronze")
    if lod == 0:
        # Zaehne an Vorderkante (+Y) + Spannknebel oben
        for t in range(14):
            tz = 0.28 + t * 0.145
            add_prism(bm, uv_layer, 0.0, 0.035, tz, tz + 0.09, 0.028, 0.04, 0.022, 0.005, "tin_bronze")
        add_beam(bm, uv_layer, (-0.28, 0.0, 2.62), (0.28, 0.0, 2.62), 0.09, 0.09, "hornbeam_timber")


def build_sy_sawmill_pitman(bm, uv_layer, lod):
    """7e. Pleuelstange (Origin EXAKT auf Kurbelzapfen (0,0,0), Laenge L=2.4 m entlang +Z!)."""
    if lod >= 3:
        add_beam(bm, uv_layer, (0.0, 0.0, 0.0), (0.0, 0.0, 2.40), 0.14, 0.14, "hornbeam_timber")
        return
    add_beam(bm, uv_layer, (0.0, 0.0, 0.05), (0.0, 0.0, 2.35), 0.13, 0.11, "hornbeam_timber")
    # Lageraugen & Eisenbeschlaege an beiden Enden
    for ez in (0.0, 2.40):
        add_cylinder(bm, uv_layer, (-0.11, 0.0, ez), (0.11, 0.0, ez), 0.12, 0.12,
                     segs=8 if lod == 0 else 6, region_key="bloomery_iron",
                     cap0_region="tin_bronze", cap1_region="tin_bronze")
    if lod <= 1:
        add_box(bm, uv_layer, 0.0, 0.0, 0.08, 0.36, 0.15, 0.13, "bloomery_iron")
        add_box(bm, uv_layer, 0.0, 0.0, 2.04, 2.32, 0.15, 0.13, "bloomery_iron")


def build_sy_sawpit_shed(bm, uv_layer, lod):
    """7f. Ueberdachte Saegegrube mit Stammauflage (6.4 x 3.8 x 3.6 m, -0.35 m Grubenwaende & Pfosten)."""
    if lod >= 3:
        add_box(bm, uv_layer, 0.0, 0.0, -0.35, 0.32, 6.2, 3.6, "cut_basalt")
        add_pitched_roof(bm, uv_layer, 0.0, 0.0, 2.55, 3.65, 6.4, 3.8, "woven_reed_mat", gable_axis="X")
        return

    # Basalt-Einfassung der Saegegrube (-0.35..0.30 m)
    for sy in (-1.35, 1.35):
        add_box(bm, uv_layer, 0.0, sy, -0.35, 0.30, 6.0, 0.52, "cut_basalt")
    for sx in (-2.75, 2.75):
        add_box(bm, uv_layer, sx, 0.0, -0.35, 0.30, 0.52, 2.2, "cut_basalt")

    # 6 Zedernpfosten (-0.35..2.58 m) + Dachstuhl
    for px in (-2.85, 0.0, 2.85):
        for py in (-1.70, 1.70):
            add_cylinder(bm, uv_layer, (px, py, -0.35), (px, py, 2.58), 0.13, 0.12, segs=6, region_key="cedar_timber")
    for py in (-1.70, 1.70):
        add_beam(bm, uv_layer, (-2.95, py, 2.56), (2.95, py, 2.56), 0.16, 0.16, "oak_timber")
    add_pitched_roof(bm, uv_layer, 0.0, 0.0, 2.58, 3.65, 6.4, 3.8, "woven_reed_mat", gable_axis="X")

    # Querschwellen (Stammauflage) + aufgelegter Zedernstamm mit Saegeschlitz
    for bx in (-2.1, -0.7, 0.7, 2.1):
        add_beam(bm, uv_layer, (bx, -1.45, 0.38), (bx, 1.45, 0.38), 0.22, 0.18, "oak_timber")
    if lod <= 1:
        add_cylinder(bm, uv_layer, (-2.55, 0.0, 0.72), (2.55, 0.0, 0.72), 0.32, 0.29,
                     segs=10 if lod == 0 else 6, region_key="cedar_timber")
    if lod == 0:
        # Aufgestapeltes Schnittholz seitlich + Saegekeil
        add_box(bm, uv_layer, 0.0, -1.05, 0.46, 0.68, 4.2, 0.42, "cedar_timber")
        add_box(bm, uv_layer, 0.25, 0.0, 0.96, 1.06, 0.32, 0.06, "hornbeam_timber")


def build_sy_timber_chute_segment(bm, uv_layer, lod):
    """8a. Holzriesen-Rinne (6.0 x 1.5 x 1.25 m, -0.35 m Bockstuetzen)."""
    if lod >= 3:
        add_box(bm, uv_layer, 0.0, 0.0, -0.35, 1.20, 1.45, 6.0, "cedar_timber")
        return
    # 3 Stuetzboecke entlang Y (-2.2, 0.0, +2.2) mit Neigung
    for cy, z_top in ((-2.2, 0.85), (0.0, 1.05), (2.2, 1.25)):
        for sx in (-0.65, 0.65):
            add_beam(bm, uv_layer, (sx, cy, -0.35), (sx * 0.82, cy, z_top), 0.16, 0.16, "oak_timber")
        add_beam(bm, uv_layer, (-0.75, cy, z_top), (0.75, cy, z_top), 0.16, 0.16, "oak_timber")
        if lod <= 1:
            add_beam(bm, uv_layer, (-0.62, cy, -0.05), (0.62, cy, z_top - 0.15), 0.10, 0.10, "oak_timber")

    # Rinnenboden + schraege Seitenwangen
    add_beam(bm, uv_layer, (0.0, -3.0, 0.82), (0.0, 3.0, 1.42), 0.88, 0.12, "cedar_timber")
    for sx_bot, sx_top in ((-0.46, -0.74), (0.46, 0.74)):
        p0 = Vector((sx_bot, -3.0, 0.86))
        p1 = Vector((sx_bot, 3.0, 1.46))
        p2 = Vector((sx_top, 3.0, 1.88))
        p3 = Vector((sx_top, -3.0, 1.28))
        n_off = Vector((-0.07 if sx_bot < 0 else 0.07, 0.0, 0.04))
        va = [bm.verts.new(p) for p in (p0, p1, p2, p3)]
        vb = [bm.verts.new(p + n_off) for p in (p0, p1, p2, p3)]
        fs = [
            bm.faces.new((va[0], va[1], va[2], va[3])),
            bm.faces.new((vb[3], vb[2], vb[1], vb[0])),
            bm.faces.new((va[2], vb[2], vb[3], va[3])),
            bm.faces.new((va[0], vb[0], vb[1], va[1])),
        ]
        _apply_box_uv(fs, uv_layer, "cedar_timber", u_scale=0.3)
    if lod == 0:
        # Geschmierte Gleitleisten innen
        for gx in (-0.25, 0.25):
            add_beam(bm, uv_layer, (gx, -2.95, 0.90), (gx, 2.95, 1.50), 0.10, 0.06, "hornbeam_timber")


def build_sy_log_stack(bm, uv_layer, lod):
    """8b. Verzimmerter Balken-/Plankenstapel + Werkbank mit Bronze-Werkzeug (4.2 x 2.4 x 1.75 m, -0.35 m)."""
    if lod >= 3:
        add_box(bm, uv_layer, 0.0, -0.3, -0.35, 1.45, 4.0, 1.8, "cedar_timber")
        return
    # Eichen-Lagerschwellen bis -0.35 m
    for sx in (-1.55, 0.0, 1.55):
        add_box(bm, uv_layer, sx, -0.25, -0.35, 0.18, 0.28, 1.85, "oak_timber")

    # Gestapelte Zedernstaemme & Kanthoelzer
    rows = [(0.36, 4), (0.70, 3), (1.02, 2)] if lod <= 1 else [(0.38, 3), (0.76, 2)]
    for rz, cnt in rows:
        for i in range(cnt):
            cy = -0.85 + i * 0.42 + (4 - cnt) * 0.18
            add_cylinder(bm, uv_layer, (-2.05, cy, rz), (2.05, cy, rz), 0.18, 0.17,
                         segs=8 if lod == 0 else 6, region_key="cedar_timber")
    # Stapel-Kanthoelzer nebenan
    add_box(bm, uv_layer, 0.0, -0.85, 0.18, 0.62, 3.8, 0.55, "oak_timber")

    if lod <= 1:
        # Zimmermanns-Werkbank vorne (+Y) mit Bronze-Saege & Beil
        add_box(bm, uv_layer, -0.35, 0.92, 0.66, 0.78, 2.15, 0.58, "hornbeam_timber", top_region="mortise_joinery")
        for lx in (-1.28, 0.58):
            for ly in (0.70, 1.14):
                add_beam(bm, uv_layer, (lx, ly, -0.35), (lx, ly, 0.66), 0.11, 0.11, "oak_timber")
        if lod == 0:
            # Bronze-Handsaege + Holzhammer auf Bank
            add_box(bm, uv_layer, -0.55, 0.90, 0.78, 0.81, 0.68, 0.14, "tin_bronze")
            add_beam(bm, uv_layer, (-0.15, 0.90, 0.80), (0.15, 0.90, 0.80), 0.06, 0.06, "hornbeam_timber")
            add_box(bm, uv_layer, 0.35, 0.92, 0.78, 0.88, 0.18, 0.12, "oak_timber")


def build_sy_tent_worker(bm, uv_layer, lod):
    """8c. Gestreiftes Arbeiterzelt mit Abspannseilen (4.4 x 3.6 x 2.75 m, -0.35 m Pfloecke & Pfosten)."""
    if lod >= 3:
        add_prism(bm, uv_layer, 0.0, 0.0, -0.35, 2.65, 3.4, 4.2, 0.25, 3.8, "tent_linen_striped")
        return

    # Zelt-Koerper als gespannte Dach-/Wand-Prismen mit -0.35 m Saumschuerze
    add_prism(bm, uv_layer, 0.0, 0.0, -0.35, 0.95, 3.5, 4.2, 3.2, 4.0, "tent_linen_striped", cap_top=False)
    add_prism(bm, uv_layer, 0.0, 0.0, 0.95, 2.72, 3.2, 4.0, 0.18, 3.6, "tent_linen_striped")

    # Mittelpfosten & Firststange
    for py in (-1.85, 1.85):
        add_cylinder(bm, uv_layer, (0.0, py, -0.35), (0.0, py, 2.84), 0.08, 0.07, segs=6, region_key="cedar_timber")
    add_beam(bm, uv_layer, (0.0, -1.98, 2.75), (0.0, 1.98, 2.75), 0.10, 0.10, "cedar_timber")

    if lod <= 1:
        # Offenes Vordach (-Y) + Stuetzen + Abspannseile mit Holzpfloecken
        add_beam(bm, uv_layer, (-1.15, -2.55, -0.35), (-1.15, -2.55, 1.65), 0.06, 0.06, "cedar_timber")
        add_beam(bm, uv_layer, (1.15, -2.55, -0.35), (1.15, -2.55, 1.65), 0.06, 0.06, "cedar_timber")
        add_prism(bm, uv_layer, 0.0, -2.25, 1.60, 2.30, 2.4, 0.75, 1.8, 0.65, "tent_linen_striped")
        for gx_t, gx_p in ((-1.6, -2.35), (1.6, 2.35)):
            for gy in (-1.2, 0.0, 1.2):
                add_beam(bm, uv_layer, (gx_t, gy, 0.98), (gx_p, gy, 0.02), 0.035, 0.035, "hemp_rope", end_region="hemp_rope")
                add_cylinder(bm, uv_layer, (gx_p, gy, -0.35), (gx_p, gy, 0.14), 0.045, 0.03, segs=5, region_key="oak_timber")
    if lod == 0:
        # Wasseramphore & Schlafmatte am Eingang
        add_amphora(bm, uv_layer, -1.05, -2.05, 0.0, radius=0.18, height=0.56, segs=7)
        add_box(bm, uv_layer, 0.55, -0.8, 0.0, 0.09, 0.85, 1.75, "woven_reed_mat")


def build_sy_cage_rolling(bm, uv_layer, lod):
    """9. Eichen-/Bronze-Raubtier-Transportkaefig auf Holzraedern (Origin mittig auf Radaufstand Z=0.0!)."""
    if lod >= 3:
        add_box(bm, uv_layer, 0.0, 0.0, 0.32, 1.88, 1.45, 2.4, "oak_timber")
        return

    wheel_r = 0.36
    # Fahrgestell-Rahmen + Deichsel
    add_box(bm, uv_layer, 0.0, 0.0, wheel_r - 0.06, wheel_r + 0.14, 1.44, 2.55, "oak_timber")
    add_beam(bm, uv_layer, (0.0, 1.25, wheel_r + 0.04), (0.0, 2.65, wheel_r + 0.12), 0.11, 0.11, "cedar_timber")

    # 4 Speichenraeder exakt auf Z=0.0 aufliegend
    for wy in (-0.85, 0.85):
        add_cylinder(bm, uv_layer, (-0.90, wy, wheel_r), (0.90, wy, wheel_r), 0.065, 0.065, segs=6, region_key="bloomery_iron")
        for wx in (-0.82, 0.82):
            add_spoked_wheel(bm, uv_layer, (wx, wy, wheel_r), (1.0, 0.0, 0.0), wheel_r, 0.12,
                             6 if lod == 0 else 4, segs=10 if lod == 0 else 8, add_tire=(lod <= 1))

    # Kaefig-Oberbau (Eichen-Eckpfosten, Dach, Bronze-Gitterstaebe)
    z_floor = wheel_r + 0.14
    z_roof = z_floor + 1.38
    for px in (-0.64, 0.64):
        for py in (-1.18, 1.18):
            add_beam(bm, uv_layer, (px, py, z_floor), (px, py, z_roof), 0.13, 0.13, "oak_timber")
    add_box(bm, uv_layer, 0.0, 0.0, z_roof, z_roof + 0.14, 1.52, 2.58, "cedar_timber", top_region="oak_timber")

    # Vertikale Zinnbronze-Gitterstaebe
    n_bars_y = 6 if lod == 0 else (4 if lod == 1 else 2)
    for i in range(n_bars_y):
        by = -0.92 + i * (1.84 / max(1, n_bars_y - 1))
        for bx in (-0.64, 0.64):
            add_cylinder(bm, uv_layer, (bx, by, z_floor), (bx, by, z_roof), 0.028, 0.028, segs=5, region_key="tin_bronze")
    n_bars_x = 4 if lod == 0 else 2
    for i in range(n_bars_x):
        bx = -0.40 + i * (0.80 / max(1, n_bars_x - 1))
        for by in (-1.18, 1.18):
            add_cylinder(bm, uv_layer, (bx, by, z_floor), (bx, by, z_roof), 0.028, 0.028, segs=5, region_key="tin_bronze")
    if lod == 0:
        for hz in (z_floor + 0.48, z_floor + 0.96):
            add_box(bm, uv_layer, 0.0, 0.0, hz - 0.025, hz + 0.025, 1.32, 2.40, "bloomery_iron")


# ==============================================================================
# B) AQUAEDUKT, FLUSSBAU & MAGUR-BOOTE (12 MODULE)
# ==============================================================================

def build_sy_aqueduct_source(bm, uv_layer, lod):
    """10a. Quellbecken-Fassung am Hang (4.8 x 4.2 x 2.8 m, -0.35 m Quellstein-Fundament)."""
    if lod >= 3:
        add_box(bm, uv_layer, 0.0, 0.0, -0.35, 2.35, 4.6, 4.0, "wet_spring_stone")
        return
    # Steinschale & Hang-Stuetzmauer (-0.35 m)
    add_box(bm, uv_layer, 0.0, 0.0, -0.35, 0.35, 4.8, 4.2, "wet_spring_stone")
    add_prism(bm, uv_layer, 0.0, -1.55, 0.35, 2.75, 4.8, 0.95, 4.5, 0.72, "wet_spring_stone")
    for sx in (-2.05, 2.05):
        add_prism(bm, uv_layer, sx, 0.25, 0.35, 1.85, 0.70, 3.2, 0.56, 3.0, "wet_spring_stone")
    add_box(bm, uv_layer, 0.0, 1.65, 0.35, 1.35, 3.6, 0.65, "cut_basalt")

    # Auslauf-Holzgerinne nach vorne (+Y)
    add_box(bm, uv_layer, 0.0, 2.35, 1.05, 1.32, 1.10, 1.25, "cedar_timber", top_region="kopher_bitumen")
    if lod <= 1:
        # Bronze-Einlaufgitter + Wasserstand
        add_box(bm, uv_layer, 0.0, 0.15, 0.35, 0.92, 3.4, 2.4, "kopher_bitumen")
        for gx in (-0.32, -0.16, 0.0, 0.16, 0.32):
            add_cylinder(bm, uv_layer, (gx, 1.72, 1.08), (gx, 1.72, 1.48), 0.025, 0.025, segs=5, region_key="tin_bronze")
    if lod == 0:
        # Ueberdachter Quellschacht-Bogen
        add_box(bm, uv_layer, 0.0, -0.95, 1.85, 2.45, 2.4, 0.85, "cut_basalt")


def build_sy_aqueduct_pier_span(bm, uv_layer, lod):
    """10b. Gemauerter Basalt-/Holzbogen mit ueberlappendem Holzgerinne (6.0 x 1.8 x 5.2 m, -0.35 m)."""
    if lod >= 3:
        for px in (-2.3, 2.3):
            add_box(bm, uv_layer, px, 0.0, -0.35, 4.4, 1.4, 1.7, "cut_basalt")
        add_box(bm, uv_layer, 0.0, 0.0, 4.35, 5.15, 6.0, 1.5, "cedar_timber")
        return

    # 2 geboeschte Basalt-/Quellsteinpfeiler (-0.35..3.15 m)
    for px in (-2.35, 2.35):
        add_prism(bm, uv_layer, px, 0.0, -0.35, 1.45, 1.45, 1.95, 1.28, 1.75, "wet_spring_stone")
        add_prism(bm, uv_layer, px, 0.0, 1.45, 3.15, 1.28, 1.75, 1.15, 1.62, "cut_basalt")
        add_box(bm, uv_layer, px, 0.0, 3.15, 3.35, 1.32, 1.78, "cut_basalt")

    # Echter Bogen aus Keilsteinen (Keil-Bogen X = -1.78..+1.78, Z_spring = 2.85, R = 1.78)
    arch_segs = 9 if lod == 0 else (7 if lod == 1 else 5)
    r_in, r_out = 1.62, 2.12
    z_spring = 2.65
    for i in range(arch_segs):
        a0 = math.pi * i / arch_segs
        a1 = math.pi * (i + 1) / arch_segs
        am = 0.5 * (a0 + a1)
        x0, z0 = -math.cos(a0), math.sin(a0)
        x1, z1 = -math.cos(a1), math.sin(a1)
        p_in0 = (x0 * r_in, 0.0, z_spring + z0 * r_in)
        p_in1 = (x1 * r_in, 0.0, z_spring + z1 * r_in)
        p_out0 = (x0 * r_out, 0.0, z_spring + z0 * r_out)
        p_out1 = (x1 * r_out, 0.0, z_spring + z1 * r_out)
        hy = 0.76
        vb = [bm.verts.new((px, -hy, pz)) for px, _, pz in (p_in0, p_in1, p_out1, p_out0)]
        vt = [bm.verts.new((px, +hy, pz)) for px, _, pz in (p_in0, p_in1, p_out1, p_out0)]
        fs = [bm.faces.new((vt[0], vt[1], vt[2], vt[3])), bm.faces.new((vb[3], vb[2], vb[1], vb[0]))]
        for k in range(4):
            fs.append(bm.faces.new((vb[k], vb[(k + 1) % 4], vt[(k + 1) % 4], vt[k])))
        _apply_box_uv(fs, uv_layer, "cut_basalt" if i % 2 == 0 else "wet_spring_stone", u_scale=0.35)

    # Gesimsbalken + ueberlappendes Zedern-Wassergerinne (Z=4.60..5.20 m)
    add_box(bm, uv_layer, 0.0, 0.0, 4.45, 4.65, 6.0, 1.65, "oak_timber")
    add_box(bm, uv_layer, 0.0, 0.0, 4.65, 4.78, 6.24, 1.32, "cedar_timber", top_region="kopher_bitumen")
    for sy in (-0.58, 0.58):
        add_box(bm, uv_layer, 0.0, sy, 4.78, 5.20, 6.24, 0.14, "cedar_timber")
    if lod <= 1:
        # Ueberlappungs-Dichtungsringe & Streben
        for rx in (-2.95, 0.0, 2.95):
            add_box(bm, uv_layer, rx, 0.0, 4.63, 5.24, 0.22, 1.44, "oak_timber")
    if lod == 0:
        # Hoelzernes Lehrgeruest unter Bogen
        add_beam(bm, uv_layer, (-1.65, 0.0, 2.65), (1.65, 0.0, 2.65), 0.14, 0.14, "cedar_timber")
        add_beam(bm, uv_layer, (0.0, 0.0, 2.65), (0.0, 0.0, 4.25), 0.14, 0.14, "cedar_timber")


def build_sy_aqueduct_trough(bm, uv_layer, lod):
    """10c. Ablauf-Trog & Verteilungsbecken (3.8 x 2.2 x 1.65 m, -0.35 m Steinsockel)."""
    if lod >= 3:
        add_box(bm, uv_layer, 0.0, 0.0, -0.35, 1.55, 3.6, 2.1, "wet_spring_stone")
        return
    # Quellstein-Plinthe (-0.35..0.55 m)
    add_box(bm, uv_layer, 0.0, 0.0, -0.35, 0.55, 3.8, 2.2, "wet_spring_stone")
    # Kaskaden-Holztrog auf Steinbock
    add_box(bm, uv_layer, 0.0, 0.0, 0.55, 0.72, 3.4, 1.55, "oak_timber")
    add_box(bm, uv_layer, 0.0, 0.0, 0.72, 0.90, 3.2, 1.35, "kopher_bitumen")
    for sy in (-0.64, 0.64):
        add_box(bm, uv_layer, 0.0, sy, 0.72, 1.45, 3.4, 0.14, "cedar_timber")
    for sx in (-1.63, 1.63):
        add_box(bm, uv_layer, sx, 0.0, 0.72, 1.45, 0.14, 1.42, "cedar_timber")

    if lod <= 1:
        # Bronze-Auslaufruellen vorne (-Y) + Fangtrog unten
        for ax in (-0.85, 0.0, 0.85):
            add_beam(bm, uv_layer, (ax, -0.68, 1.15), (ax, -1.05, 1.05), 0.10, 0.10, "tin_bronze", end_region="tin_bronze")
        add_box(bm, uv_layer, 0.0, -1.02, -0.35, 0.45, 2.6, 0.78, "wet_spring_stone", top_region="kopher_bitumen")


def _build_magur_hull(bm, uv_layer, lod, with_timber=False):
    """Sumerisches Magur-Flussboot (Origin EXAKT auf Wasserlinie Z = 0.0!)."""
    if lod >= 3:
        # 5-Segment Bootssilhouette mit hochgezogenen Steven
        add_prism(bm, uv_layer, 0.0, 0.0, -0.40, 0.65, 2.35, 6.2, 2.50, 7.6, "kopher_bitumen", top_region="woven_reed_mat")
        add_beam(bm, uv_layer, (0.0, -3.5, 0.45), (0.0, -4.65, 2.05), 0.45, 0.45, "woven_reed_mat")
        add_beam(bm, uv_layer, (0.0, 3.5, 0.45), (0.0, 4.65, 2.05), 0.45, 0.45, "woven_reed_mat")
        return

    # Profil-Stationen entlang Y (-4.7 .. +4.7 m), Z=0.0 ist Wasserlinie!
    # (y, half_beam, z_keel, z_gunwale)
    stations = [
        (-4.75, 0.10, 1.75, 2.12),
        (-4.05, 0.42, 0.35, 1.15),
        (-2.85, 0.92, -0.38, 0.68),
        (-1.40, 1.18, -0.42, 0.58),
        ( 0.00, 1.24, -0.42, 0.56),
        ( 1.40, 1.18, -0.42, 0.58),
        ( 2.85, 0.92, -0.38, 0.68),
        ( 4.05, 0.42, 0.35, 1.15),
        ( 4.75, 0.10, 1.75, 2.12),
    ]
    if lod == 2:
        stations = [stations[0], stations[2], stations[4], stations[6], stations[8]]

    rings = []
    for y, hb, zk, zg in stations:
        zm = 0.5 * (zk + zg)
        # 5 Punkte je Querschnitt (BB oben -> BB Kimm -> Kiel -> SB Kimm -> SB oben)
        pts = [
            (-hb, y, zg),
            (-hb * 0.72, y, zk + 0.15),
            (0.0, y, zk),
            (hb * 0.72, y, zk + 0.15),
            (hb, y, zg),
        ]
        rings.append([bm.verts.new(p) for p in pts])

    hull_faces = []
    reed_faces = []
    for s in range(len(rings) - 1):
        r0, r1 = rings[s], rings[s + 1]
        for k in range(4):
            f = bm.faces.new((r0[k], r0[k + 1], r1[k + 1], r1[k]))
            if k in (0, 3):
                reed_faces.append(f)
            else:
                hull_faces.append(f)
        # Deckboden innen
        fd = bm.faces.new((r0[0], r1[0], r1[4], r0[4]))
        hull_faces.append(fd)

    # Bug- und Heck-Kappen
    hull_faces.append(bm.faces.new((rings[0][0], rings[0][4], rings[0][2])))
    hull_faces.append(bm.faces.new((rings[-1][4], rings[-1][0], rings[-1][2])))

    _apply_box_uv(hull_faces, uv_layer, "kopher_bitumen", u_scale=0.35)
    _apply_box_uv(reed_faces, uv_layer, "woven_reed_mat", u_scale=0.35)

    # Schilfrohr-Dollbord-Wulste + Spanten + Ruderbaenke
    if lod <= 1:
        for side in (-1.0, 1.0):
            for s in range(len(stations) - 1):
                y0, hb0, _, zg0 = stations[s]
                y1, hb1, _, zg1 = stations[s + 1]
                add_cylinder(bm, uv_layer, (side * hb0, y0, zg0), (side * hb1, y1, zg1),
                             0.11, 0.11, segs=6, region_key="woven_reed_mat", cap0=False, cap1=False)
        for ry in (-2.1, -0.7, 0.7, 2.1):
            add_beam(bm, uv_layer, (-0.98, ry, 0.34), (0.98, ry, 0.34), 0.24, 0.08, "cedar_timber")
        # Stechruder am Heck (-Y)
        add_beam(bm, uv_layer, (0.45, -3.55, 0.92), (0.85, -5.25, -0.35), 0.09, 0.09, "oak_timber")
        add_box(bm, uv_layer, 0.86, -5.28, -0.52, -0.10, 0.05, 0.85, "cedar_timber")

    if lod == 0:
        # Innere Eichenspanten + Seilbunde an Steven
        for ry in (-2.5, -1.5, -0.5, 0.5, 1.5, 2.5):
            add_beam(bm, uv_layer, (-0.95, ry, 0.05), (0.95, ry, 0.05), 0.09, 0.12, "oak_timber")
        for sy in (-4.45, 4.45):
            add_cylinder(bm, uv_layer, (0.0, sy, 1.45), (0.0, sy * 1.04, 1.75), 0.19, 0.16, segs=8, region_key="hemp_rope")

    # Fracht-Unterschied: Zedernstaemme vs. Amphoren/Saecke
    if with_timber:
        log_z = 0.42 if lod <= 1 else 0.35
        for lx in (-0.42, 0.0, 0.42):
            add_cylinder(bm, uv_layer, (lx, -2.55, log_z), (lx, 2.55, log_z), 0.18, 0.17,
                         segs=7 if lod == 0 else 5, region_key="cedar_timber")
        if lod <= 1:
            for lx in (-0.22, 0.22):
                add_cylinder(bm, uv_layer, (lx, -2.35, log_z + 0.30), (lx, 2.35, log_z + 0.30), 0.17, 0.16,
                             segs=6, region_key="cedar_timber")
            add_box(bm, uv_layer, 0.0, -1.2, log_z - 0.1, log_z + 0.48, 1.15, 0.12, "hemp_rope")
            add_box(bm, uv_layer, 0.0, 1.2, log_z - 0.1, log_z + 0.48, 1.15, 0.12, "hemp_rope")
    else:
        add_grain_sack(bm, uv_layer, -0.35, -1.35, 0.22, sx=0.55, sy=0.72, sz=0.36)
        add_grain_sack(bm, uv_layer, 0.32, -1.25, 0.22, sx=0.52, sy=0.68, sz=0.34)
        add_grain_sack(bm, uv_layer, 0.0, -1.30, 0.56, sx=0.50, sy=0.65, sz=0.32)
        if lod <= 1:
            for ax, ay in ((-0.40, 0.15), (0.35, 0.20), (-0.30, 1.25), (0.35, 1.35)):
                add_amphora(bm, uv_layer, ax, ay, 0.22, radius=0.20, height=0.62, segs=7 if lod == 0 else 5)
        if lod == 0:
            add_rope_coil(bm, uv_layer, 0.0, 2.45, 0.28, r_outer=0.28, turns=3, rope_r=0.032, segs=8)


def build_river_magur_cargo(bm, uv_layer, lod):
    """11a. Sumerisches Magur-Frachtboot mit Amphoren/Saecken (Origin auf Wasserlinie Z=0.0!)."""
    _build_magur_hull(bm, uv_layer, lod, with_timber=False)


def build_river_magur_timber(bm, uv_layer, lod):
    """11b. Sumerisches Magur-Holztransportschiff mit Zedernstaemmen (Origin auf Wasserlinie Z=0.0!)."""
    _build_magur_hull(bm, uv_layer, lod, with_timber=True)


def build_river_waterwheel_base(bm, uv_layer, lod):
    """12a. Lagerboecke fuer Noria-Wasserrad (Achshoehe Z=2.05 m, -0.35 m Flussbett-Fundament)."""
    if lod >= 3:
        for sx in (-1.35, 1.35):
            add_box(bm, uv_layer, sx, 0.0, -0.35, 2.25, 0.72, 1.85, "wet_spring_stone")
        return
    # Boden-Sohle im Gerinne (-0.35..0.08 m)
    add_box(bm, uv_layer, 0.0, 0.0, -0.35, 0.08, 3.4, 2.8, "wet_spring_stone")
    # Twin Lagerboecke aus Quellstein + Eichen-Lagersattel auf Z = 2.05 m
    for sx in (-1.35, 1.35):
        add_prism(bm, uv_layer, sx, 0.0, 0.08, 1.85, 0.85, 2.25, 0.62, 1.45, "wet_spring_stone")
        add_box(bm, uv_layer, sx, 0.0, 1.85, 2.02, 0.68, 0.95, "oak_timber")
        add_box(bm, uv_layer, sx, 0.0, 2.02, 2.14, 0.42, 0.56, "tin_bronze")
    if lod <= 1:
        # Ueberlauf-Holzrinne auf Seite (+X)
        add_box(bm, uv_layer, 1.85, 0.0, 3.40, 3.67, 0.75, 3.8, "cedar_timber", top_region="kopher_bitumen")
        for sy in (1.58, 2.12):
            add_box(bm, uv_layer, sy, 0.0, 3.67, 3.93, 0.10, 3.8, "cedar_timber")
        add_beam(bm, uv_layer, (1.85, -1.2, -0.35), (1.85, -1.2, 3.40), 0.18, 0.18, "oak_timber")
        add_beam(bm, uv_layer, (1.85, 1.2, -0.35), (1.85, 1.2, 3.40), 0.18, 0.18, "oak_timber")


def build_river_waterwheel_rotor(bm, uv_layer, lod):
    """12b. Noria-Wasserrad mit Schaufeln & Schoepfkaesten (Origin EXAKT auf Drehachse (0,0,0) entlang X!)."""
    if lod >= 3:
        add_cylinder(bm, uv_layer, (-0.55, 0.0, 0.0), (0.55, 0.0, 0.0), 2.20, 2.20, segs=10, region_key="oak_timber")
        return
    r_wheel = 2.22
    # Hauptwelle entlang X
    add_cylinder(bm, uv_layer, (-1.55, 0.0, 0.0), (1.55, 0.0, 0.0), 0.16, 0.16,
                 segs=8 if lod == 0 else 6, region_key="oak_timber",
                 cap0_region="tin_bronze", cap1_region="tin_bronze")

    # Twin Speichenkraenze bei X = -0.42 & +0.42
    spokes = 8 if lod == 0 else (6 if lod == 1 else 4)
    segs = 16 if lod == 0 else (12 if lod == 1 else 8)
    for wx in (-0.42, 0.42):
        add_spoked_wheel(bm, uv_layer, (wx, 0.0, 0.0), (1.0, 0.0, 0.0), r_wheel, 0.14,
                         spokes, rim_region="cedar_timber", spoke_region="oak_timber",
                         segs=segs, add_tire=False)

    # Schaufelbretter + Schoepfkaesten am Umfang
    paddles = 16 if lod == 0 else (10 if lod == 1 else 6)
    for i in range(paddles):
        ang = 2.0 * math.pi * i / paddles
        cy, cz = math.cos(ang), math.sin(ang)
        ty, tz = -cz, cy
        p_in = (0.0, cy * (r_wheel - 0.35), cz * (r_wheel - 0.35))
        p_out = (0.0, cy * (r_wheel + 0.12), cz * (r_wheel + 0.12))
        add_beam(bm, uv_layer, (-0.45, p_in[1], p_in[2]), (0.45, p_in[1], p_in[2]), 0.12, 0.06, "cedar_timber")
        add_beam(bm, uv_layer, (-0.48, p_out[1], p_out[2]), (0.48, p_out[1], p_out[2]), 0.18, 0.05, "cedar_timber")
        if lod <= 1:
            # Schoepfkasten seitlich (X = +0.58)
            bx, by, bz = 0.58, cy * (r_wheel - 0.15), cz * (r_wheel - 0.15)
            add_box(bm, uv_layer, bx, by, bz - 0.12, bz + 0.12, 0.24, 0.24, "oak_timber", top_region="kopher_bitumen")


def build_river_shaduf_post(bm, uv_layer, lod):
    """13a. Gabelpfosten-Staender fuer Schaduf (Origin auf Boden (0,0,0), Kippachse bei Z=2.10 m, -0.35 m)."""
    if lod >= 3:
        add_box(bm, uv_layer, 0.0, 0.0, -0.35, 0.32, 1.1, 1.1, "rammed_earth_charcoal")
        add_beam(bm, uv_layer, (0.0, 0.0, -0.35), (0.0, 0.0, 2.25), 0.24, 0.24, "oak_timber")
        return
    # Lehmsockel (-0.35..0.35 m)
    add_cylinder(bm, uv_layer, (0.0, 0.0, -0.35), (0.0, 0.0, 0.36), 0.72, 0.56, segs=8, region_key="rammed_earth_charcoal")
    # Twin Gabelpfosten + Querlagerachse auf Z = 2.10 m
    for sx in (-0.32, 0.32):
        add_cylinder(bm, uv_layer, (sx * 1.15, 0.0, -0.35), (sx, 0.0, 2.28), 0.11, 0.09, segs=7 if lod == 0 else 5, region_key="cedar_timber")
    add_cylinder(bm, uv_layer, (-0.46, 0.0, 2.10), (0.46, 0.0, 2.10), 0.065, 0.065, segs=6, region_key="hornbeam_timber")
    if lod <= 1:
        add_beam(bm, uv_layer, (-0.38, 0.0, 1.55), (0.38, 0.0, 1.55), 0.10, 0.10, "oak_timber")
        add_cylinder(bm, uv_layer, (0.0, 0.0, 1.48), (0.0, 0.0, 1.62), 0.18, 0.18, segs=6, region_key="hemp_rope")


def build_river_shaduf_arm(bm, uv_layer, lod):
    """13b. Schwenkbarer Schaduf-Schoepfbaum mit Gegengewicht & Eimer (Origin EXAKT auf Kippachse (0,0,0)!)."""
    if lod >= 3:
        add_beam(bm, uv_layer, (0.0, -1.6, -0.20), (0.0, 3.6, 0.48), 0.14, 0.14, "cedar_timber")
        add_cylinder(bm, uv_layer, (0.0, -1.5, -0.35), (0.0, -1.5, 0.15), 0.36, 0.34, segs=6, region_key="rammed_earth_charcoal")
        return
    # Langer verjuengter Schoepfbaum (Kippachse exakt bei (0,0,0))
    add_cylinder(bm, uv_layer, (0.0, -1.65, -0.22), (0.0, 3.65, 0.48), 0.11, 0.05,
                 segs=8 if lod == 0 else 6, region_key="cedar_timber")
    # Lehm-/Stein-Gegengewicht hinten (Y = -1.52 m) + Hanfseil-Wicklung
    add_cylinder(bm, uv_layer, (0.0, -1.52, -0.45), (0.0, -1.52, 0.08), 0.36, 0.30,
                 segs=8 if lod == 0 else 6, region_key="rammed_earth_charcoal")
    add_cylinder(bm, uv_layer, (0.0, -1.52, -0.18), (0.0, -1.52, -0.02), 0.37, 0.37, segs=8, region_key="hemp_rope")

    # Zugseil + Leder-/Bitumen-Schoepfeimer vorne (Y = +3.55 m)
    add_beam(bm, uv_layer, (0.0, 3.55, 0.45), (0.0, 3.55, -1.18), 0.04, 0.04, "hemp_rope", end_region="hemp_rope")
    add_cylinder(bm, uv_layer, (0.0, 3.55, -1.62), (0.0, 3.55, -1.15), 0.15, 0.24,
                 segs=8 if lod == 0 else 6, region_key="kopher_bitumen", cap1_region="kopher_bitumen")
    if lod == 0:
        add_cylinder(bm, uv_layer, (-0.18, 0.0, 0.0), (0.18, 0.0, 0.0), 0.12, 0.12, segs=6, region_key="hemp_rope")


def build_river_sluice_gate(bm, uv_layer, lod):
    """14a. Gemauerte Kanal-Schleuse mit Schuetztafel (3.6 x 1.4 x 2.85 m, -0.35 m Sohlschwelle)."""
    if lod >= 3:
        add_box(bm, uv_layer, 0.0, 0.0, -0.35, 0.12, 3.6, 1.4, "wet_spring_stone")
        for sx in (-1.45, 1.45):
            add_box(bm, uv_layer, sx, 0.0, 0.12, 2.75, 0.72, 1.35, "wet_spring_stone")
        add_box(bm, uv_layer, 0.0, 0.0, 0.35, 1.65, 2.2, 0.22, "oak_timber")
        return

    # Sohle (-0.35..0.10 m) & 2 genutete Wangenmauern
    add_box(bm, uv_layer, 0.0, 0.0, -0.35, 0.10, 3.6, 1.45, "wet_spring_stone")
    for sx in (-1.42, 1.42):
        add_prism(bm, uv_layer, sx, 0.0, 0.10, 2.35, 0.78, 1.40, 0.65, 1.25, "wet_spring_stone")
        add_box(bm, uv_layer, sx, 0.0, 2.35, 2.52, 0.72, 1.32, "cut_basalt")

    # Eichen-Jochbalken + Zugwinde oben
    add_beam(bm, uv_layer, (-1.85, 0.0, 2.68), (1.85, 0.0, 2.68), 0.24, 0.26, "oak_timber")
    # Schuetztafel (halb geoeffnet bei Z = 0.42..1.72 m)
    add_box(bm, uv_layer, 0.0, 0.0, 0.42, 1.72, 2.22, 0.16, "cedar_timber", top_region="mortise_joinery")
    if lod <= 1:
        for bz in (0.65, 1.45):
            add_box(bm, uv_layer, 0.0, 0.0, bz - 0.04, bz + 0.04, 2.24, 0.20, "tin_bronze")
        # Zahnstangen-/Hebelstangen zur Winde
        for hx in (-0.65, 0.65):
            add_beam(bm, uv_layer, (hx, 0.0, 1.68), (hx, 0.0, 2.95), 0.10, 0.10, "oak_timber")
        add_cylinder(bm, uv_layer, (-0.95, 0.0, 2.86), (0.95, 0.0, 2.86), 0.11, 0.11, segs=8, region_key="hemp_rope")


def build_river_weir(bm, uv_layer, lod):
    """14b. Holzbohlen-Wehr mit Ramm-Pfaehlen & Basalt-Schuettung (6.0 x 2.3 x 1.25 m, -0.35 m)."""
    if lod >= 3:
        add_prism(bm, uv_layer, 0.0, 0.0, -0.35, 1.15, 6.0, 2.2, 5.9, 1.1, "oak_timber")
        return

    # Basalt-Fundamentbank (-0.35..0.45 m)
    add_prism(bm, uv_layer, 0.0, 0.0, -0.35, 0.48, 6.0, 2.3, 5.8, 1.75, "cut_basalt")
    # Reihe gerammter Eichenpfaehle entlang X
    n_piles = 11 if lod == 0 else (7 if lod == 1 else 5)
    for i in range(n_piles):
        px = -2.75 + i * (5.5 / max(1, n_piles - 1))
        add_cylinder(bm, uv_layer, (px, -0.45, -0.35), (px, -0.45, 1.18), 0.13, 0.12,
                     segs=6 if lod == 0 else 5, region_key="oak_timber")

    # Schraeges Ueberfall-Bohlenwehr (Y = -0.45 -> +1.05, Z = 1.08 -> 0.15)
    for px in (-2.2, 0.0, 2.2):
        add_beam(bm, uv_layer, (px, -0.45, 1.02), (px, 1.02, 0.18), 0.18, 0.18, "oak_timber")
    p_b = [(-2.95, -0.45, 0.96), (2.95, -0.45, 0.96), (2.95, 1.08, 0.14), (-2.95, 1.08, 0.14)]
    p_t = [(x, y, z + 0.12) for x, y, z in p_b]
    vb = [bm.verts.new(p) for p in p_b]
    vt = [bm.verts.new(p) for p in p_t]
    fs = [bm.faces.new((vt[0], vt[1], vt[2], vt[3])), bm.faces.new((vb[3], vb[2], vb[1], vb[0]))]
    for k in range(4):
        fs.append(bm.faces.new((vb[k], vb[(k + 1) % 4], vt[(k + 1) % 4], vt[k])))
    _apply_box_uv(fs, uv_layer, "cedar_timber", u_scale=0.35)
    if lod <= 1:
        # Quer-Staubalken + Bronze-Bindeisen
        add_beam(bm, uv_layer, (-2.98, -0.45, 1.10), (2.98, -0.45, 1.10), 0.18, 0.18, "oak_timber")


def build_river_timber_jetty(bm, uv_layer, lod):
    """14c. Hoelzerner Landungssteg mit Pollern, Tauwerk & Faessern (6.0 x 2.6 m, Deck Z=0.55 m, -0.50 m Pfaehle)."""
    if lod >= 3:
        add_box(bm, uv_layer, 0.0, 0.0, 0.42, 0.62, 2.55, 6.0, "cedar_timber")
        for sx in (-1.05, 1.05):
            for sy in (-2.4, 0.0, 2.4):
                add_cylinder(bm, uv_layer, (sx, sy, -0.50), (sx, sy, 1.15), 0.14, 0.14, segs=5, region_key="oak_timber")
        return

    # 8 gerammte Eichenpfaehle (-0.50 m im Flussboden -> Pollerkoepfe auf +1.18 m)
    for sx in (-1.10, 1.10):
        for sy in (-2.55, -0.85, 0.85, 2.55):
            top_z = 1.18 if abs(sy) > 2.0 or sx < 0 else 0.55
            add_cylinder(bm, uv_layer, (sx, sy, -0.50), (sx, sy, top_z), 0.14, 0.13,
                         segs=7 if lod == 0 else 5, region_key="oak_timber")
            if lod <= 1 and top_z > 1.0:
                add_cylinder(bm, uv_layer, (sx, sy, 0.72), (sx, sy, 0.92), 0.17, 0.17, segs=6, region_key="hemp_rope")

    # Unterzuege & Querbalken
    for sx in (-1.05, 0.0, 1.05):
        add_beam(bm, uv_layer, (sx, -2.95, 0.42), (sx, 2.95, 0.42), 0.16, 0.18, "oak_timber")
    for sy in (-2.55, -0.85, 0.85, 2.55):
        add_beam(bm, uv_layer, (-1.22, sy, 0.34), (1.22, sy, 0.34), 0.16, 0.16, "oak_timber")

    # Planken-Deck (Z = 0.50..0.60 m)
    if lod == 0:
        for i in range(14):
            py = -2.80 + i * 0.43
            add_box(bm, uv_layer, 0.0, py, 0.50, 0.60, 2.56, 0.38, "cedar_timber")
    else:
        add_box(bm, uv_layer, 0.0, 0.0, 0.50, 0.60, 2.56, 5.95, "cedar_timber")

    if lod <= 1:
        # Faesser, Amphore & Tau-Rolle auf dem Steg
        add_barrel(bm, uv_layer, -0.65, 1.75, 0.60, radius=0.25, height=0.68, segs=8 if lod == 0 else 6)
        add_barrel(bm, uv_layer, -0.10, 2.05, 0.60, radius=0.25, height=0.68, segs=8 if lod == 0 else 6)
        add_rope_coil(bm, uv_layer, 0.62, 1.95, 0.60, r_outer=0.32, turns=3, rope_r=0.035, segs=8)
    if lod == 0:
        add_amphora(bm, uv_layer, 0.55, -1.65, 0.60, radius=0.18, height=0.55, segs=7)


# ==============================================================================
# C) FELD-, LAGER- & WEG-REQUISITEN (6 MODULE)
# ==============================================================================

def build_field_straw_rick(bm, uv_layer, lod):
    """15. Aufgeschichteter konischer Stroh-/Heudiemen mit Dreschflegel/Gabel (-0.35 m Schuerze)."""
    if lod >= 3:
        add_cylinder(bm, uv_layer, (0.0, 0.0, -0.35), (0.0, 0.0, 2.55), 1.45, 0.18, segs=7, region_key="straw_thatch")
        return
    segs = 12 if lod == 0 else (8 if lod == 1 else 6)
    # Abgestufter Diemen (-0.35..2.62 m)
    add_cylinder(bm, uv_layer, (0.0, 0.0, -0.35), (0.0, 0.0, 0.95), 1.45, 1.52, segs=segs, region_key="straw_thatch")
    add_cylinder(bm, uv_layer, (0.0, 0.0, 0.95), (0.0, 0.0, 1.85), 1.52, 0.95, segs=segs, region_key="straw_thatch", cap0=False)
    add_cylinder(bm, uv_layer, (0.0, 0.0, 1.85), (0.0, 0.0, 2.62), 0.95, 0.12, segs=segs, region_key="straw_thatch", cap0=False)
    # Zentraler Firstpfahl oben
    add_cylinder(bm, uv_layer, (0.0, 0.0, 2.35), (0.0, 0.0, 2.92), 0.055, 0.04, segs=5, region_key="oak_timber")
    if lod <= 1:
        # Hanfseil-Bund + angelehnte Holzgabel
        add_cylinder(bm, uv_layer, (0.0, 0.0, 0.90), (0.0, 0.0, 1.02), 1.55, 1.55, segs=segs, region_key="hemp_rope")
        add_beam(bm, uv_layer, (1.45, -0.55, -0.05), (0.95, -0.35, 1.75), 0.055, 0.055, "hornbeam_timber")
        if lod == 0:
            for tx in (-0.10, 0.0, 0.10):
                add_beam(bm, uv_layer, (0.95 + tx, -0.35, 1.75), (0.85 + tx, -0.32, 2.08), 0.025, 0.025, "hornbeam_timber")


def build_field_shelter(bm, uv_layer, lod):
    """16. Offener Schilfdach-Feldunterstand mit Wasserkrugen (3.6 x 2.8 x 2.45 m, -0.35 m Pfosten)."""
    if lod >= 3:
        for px, py in ((-1.6, -1.2), (1.6, -1.2), (-1.6, 1.2), (1.6, 1.2)):
            add_beam(bm, uv_layer, (px, py, -0.35), (px, py, 2.05), 0.14, 0.14, "cedar_timber")
        add_box(bm, uv_layer, 0.0, 0.0, 1.98, 2.25, 3.7, 2.9, "woven_reed_mat")
        return
    # 4 naturkrumme Zedernpfosten (-0.35 m) + Pultdach-Gefälle
    posts = [(-1.62, -1.22, 1.92), (1.62, -1.22, 1.92), (-1.62, 1.22, 2.32), (1.62, 1.22, 2.32)]
    for px, py, pz in posts:
        add_cylinder(bm, uv_layer, (px, py, -0.35), (px, py, pz), 0.10, 0.09, segs=6, region_key="cedar_timber")
    # Pfetten & Sparren
    add_beam(bm, uv_layer, (-1.75, -1.22, 1.92), (1.75, -1.22, 1.92), 0.12, 0.12, "oak_timber")
    add_beam(bm, uv_layer, (-1.75, 1.22, 2.32), (1.75, 1.22, 2.32), 0.12, 0.12, "oak_timber")
    for sx in (-1.55, 0.0, 1.55):
        add_beam(bm, uv_layer, (sx, -1.45, 1.90), (sx, 1.45, 2.38), 0.10, 0.10, "cedar_timber")

    # Schraeges Schilfrohr-Dach
    p_b = [(-1.90, -1.52, 1.94), (1.90, -1.52, 1.94), (1.90, 1.52, 2.42), (-1.90, 1.52, 2.42)]
    p_t = [(x, y, z + 0.16) for x, y, z in p_b]
    vb = [bm.verts.new(p) for p in p_b]
    vt = [bm.verts.new(p) for p in p_t]
    fs = [bm.faces.new((vt[0], vt[1], vt[2], vt[3])), bm.faces.new((vb[3], vb[2], vb[1], vb[0]))]
    for k in range(4):
        fs.append(bm.faces.new((vb[k], vb[(k + 1) % 4], vt[(k + 1) % 4], vt[k])))
    _apply_box_uv(fs, uv_layer, "woven_reed_mat", u_scale=0.35)

    if lod <= 1:
        # Niedrige Holzbank + 2 Wasserkruge darunter
        add_box(bm, uv_layer, -0.55, 0.35, 0.38, 0.46, 1.55, 0.45, "cedar_timber")
        for lx in (-1.15, 0.05):
            add_beam(bm, uv_layer, (lx, 0.35, -0.35), (lx, 0.35, 0.38), 0.09, 0.09, "oak_timber")
        add_amphora(bm, uv_layer, 0.85, 0.15, 0.0, radius=0.19, height=0.58, segs=7 if lod == 0 else 5)
        if lod == 0:
            add_amphora(bm, uv_layer, 1.18, -0.15, 0.0, radius=0.16, height=0.48, segs=6)


def _add_faceted_rock(bm, uv_layer, cx, cy, z_bot, rx, ry, rz, seed=1, segs=8, rings=3, region="cut_basalt"):
    """Erzeugt einen verwitterten Steppen-Findling mit -0.35 m Schuerze (kein Schweben!)."""
    ring_verts = []
    for r in range(rings):
        fz = r / max(1, rings - 1)
        z = z_bot + fz * rz
        rad_scale = math.sin(0.18 + fz * 2.55) * (1.05 - 0.35 * fz)
        row = []
        for s in range(segs):
            ang = 2.0 * math.pi * s / segs
            jit = 0.80 + 0.32 * math.sin(ang * 3.0 + seed * 1.7 + r * 2.1) * math.cos(ang * 2.0 - seed)
            vx = cx + math.cos(ang) * rx * rad_scale * jit
            vy = cy + math.sin(ang) * ry * rad_scale * jit
            row.append(bm.verts.new((vx, vy, z)))
        ring_verts.append(row)

    v_top = bm.verts.new((cx + 0.08 * rx, cy - 0.05 * ry, z_bot + rz * 1.06))
    v_bot = bm.verts.new((cx, cy, z_bot))
    faces = []
    for r in range(rings - 1):
        for s in range(segs):
            sn = (s + 1) % segs
            faces.append(bm.faces.new((ring_verts[r][s], ring_verts[r][sn], ring_verts[r + 1][sn], ring_verts[r + 1][s])))
    for s in range(segs):
        sn = (s + 1) % segs
        faces.append(bm.faces.new((ring_verts[-1][s], ring_verts[-1][sn], v_top)))
        faces.append(bm.faces.new((ring_verts[0][sn], ring_verts[0][s], v_bot)))
    _apply_box_uv(faces, uv_layer, region, u_scale=0.35)


def build_world_boulder_01(bm, uv_layer, lod):
    """17a. Verwitterter Steppen-Findling Form 1 (breiter Basaltblock, -0.35 m)."""
    segs = 9 if lod == 0 else (7 if lod == 1 else (5 if lod == 2 else 4))
    rings = 3 if lod <= 1 else 2
    _add_faceted_rock(bm, uv_layer, 0.0, 0.0, -0.35, 1.25, 0.98, 1.65, seed=11, segs=segs, rings=rings, region="cut_basalt")


def build_world_boulder_02(bm, uv_layer, lod):
    """17b. Verwitterter Steppen-Findling Form 2 (schlanker gespaltener Fels, -0.35 m)."""
    segs = 8 if lod == 0 else (6 if lod == 1 else (5 if lod == 2 else 4))
    rings = 3 if lod <= 1 else 2
    _add_faceted_rock(bm, uv_layer, 0.0, 0.0, -0.35, 0.85, 0.72, 2.10, seed=27, segs=segs, rings=rings, region="wet_spring_stone")


def build_world_boulder_03(bm, uv_layer, lod):
    """17c. Verwitterter Steppen-Findling Form 3 (Dreier-Felsgruppe, -0.35 m)."""
    segs = 8 if lod == 0 else (6 if lod == 1 else 4)
    rings = 3 if lod == 0 else 2
    _add_faceted_rock(bm, uv_layer, -0.35, 0.0, -0.35, 1.10, 0.92, 1.42, seed=43, segs=segs, rings=rings, region="cut_basalt")
    if lod <= 2:
        _add_faceted_rock(bm, uv_layer, 0.82, 0.35, -0.35, 0.78, 0.68, 1.05, seed=59, segs=max(4, segs - 1), rings=2, region="wet_spring_stone")
    if lod <= 1:
        _add_faceted_rock(bm, uv_layer, 0.25, -0.78, -0.35, 0.62, 0.56, 0.82, seed=71, segs=5, rings=2, region="cut_basalt")


def build_world_supply_cart(bm, uv_layer, lod):
    """17d. Beladener Vorratskarren mit Kornsaecken/Faessern (Origin auf Radaufstand Z=0.0!)."""
    if lod >= 3:
        add_box(bm, uv_layer, 0.0, 0.0, 0.42, 1.35, 1.55, 2.35, "cedar_timber")
        add_beam(bm, uv_layer, (0.0, 1.15, 0.52), (0.0, 2.55, 0.62), 0.11, 0.11, "oak_timber")
        return

    wheel_r = 0.54
    # Achse + 2 grosse Speichenraeder auf Z=0.0 aufliegend
    add_cylinder(bm, uv_layer, (-0.98, 0.0, wheel_r), (0.98, 0.0, wheel_r), 0.07, 0.07, segs=6, region_key="oak_timber")
    for wx in (-0.88, 0.88):
        add_spoked_wheel(bm, uv_layer, (wx, 0.0, wheel_r), (1.0, 0.0, 0.0), wheel_r, 0.13,
                         8 if lod == 0 else 4, segs=12 if lod == 0 else 8, add_tire=(lod <= 1))

    # Ladeflaeche + Latten-Seitenwaende + Deichsel
    z_bed = wheel_r + 0.08
    add_box(bm, uv_layer, 0.0, 0.0, z_bed, z_bed + 0.10, 1.44, 2.40, "oak_timber")
    for sx in (-0.68, 0.68):
        add_box(bm, uv_layer, sx, 0.0, z_bed + 0.10, z_bed + 0.56, 0.08, 2.38, "cedar_timber")
    add_box(bm, uv_layer, 0.0, -1.16, z_bed + 0.10, z_bed + 0.56, 1.40, 0.08, "cedar_timber")
    add_box(bm, uv_layer, 0.0, 1.16, z_bed + 0.10, z_bed + 0.48, 1.40, 0.08, "cedar_timber")
    # Deichsel & Jochquerstange
    add_beam(bm, uv_layer, (0.0, 0.55, z_bed - 0.04), (0.0, 2.75, z_bed + 0.16), 0.11, 0.11, "oak_timber")
    add_beam(bm, uv_layer, (-0.75, 2.65, z_bed + 0.22), (0.75, 2.65, z_bed + 0.22), 0.09, 0.09, "hornbeam_timber")

    # Fracht: Kornsaecke, Eichenfass & Amphoren
    add_grain_sack(bm, uv_layer, -0.30, -0.45, z_bed + 0.10, sx=0.58, sy=0.72, sz=0.36)
    add_grain_sack(bm, uv_layer, 0.30, -0.42, z_bed + 0.10, sx=0.56, sy=0.70, sz=0.35)
    add_grain_sack(bm, uv_layer, 0.0, -0.40, z_bed + 0.45, sx=0.54, sy=0.68, sz=0.32)
    if lod <= 1:
        add_barrel(bm, uv_layer, -0.28, 0.55, z_bed + 0.10, radius=0.26, height=0.68, segs=8 if lod == 0 else 6)
        add_amphora(bm, uv_layer, 0.32, 0.58, z_bed + 0.10, radius=0.19, height=0.58, segs=7 if lod == 0 else 5)
    if lod == 0:
        add_rope_coil(bm, uv_layer, 0.28, 0.15, z_bed + 0.44, r_outer=0.22, turns=3, rope_r=0.025, segs=8)


# ==============================================================================
# MODUL-KATALOG (38 MODULE x 4 LODS)
# ==============================================================================

MODULE_BUILDERS = [
    # A) Werft- & Bauwerks-Module (20)
    ("sy_scaffold_bay",          build_sy_scaffold_bay,          (0, 1, 2, 3), "Mehrstoeckiges Baugeruest-Feld mit Diagonalstreben, Leitern & Seilbunden (Origin Boden, -0.35m)"),
    ("sy_cribbing_block",        build_sy_cribbing_block,        (0, 1, 2, 3), "Massive Eichen-Kielkloetze mit Keilen (Origin Boden, -0.35m)"),
    ("sy_ramp_module",           build_sy_ramp_module,           (0, 1, 2, 3), "Bohlen-Beladerampe mit Radabweisern & Bockstuetzen (Origin Boden, -0.35m)"),
    ("sy_drawbridge_flap",       build_sy_drawbridge_flap,       (0, 1, 2, 3), "Zugbruecken-Klappe (Origin exakt auf Scharnierachse X @ (0,0,0))"),
    ("sy_crane_aframe",          build_sy_crane_aframe,          (0, 1, 2, 3), "Schwerer Bockkran-A-Rahmen mit Ballastschlitten & Seilrolle (Origin Boden, -0.35m)"),
    ("sy_crane_winch_rotor",     build_sy_crane_winch_rotor,     (0, 1, 2, 3), "Drehbare Kran-Seilwinde mit Handspeichen & Sperrrad (Origin exakt auf Wellenachse X @ (0,0,0))"),
    ("sy_crane_timber_load",     build_sy_crane_timber_load,     (0, 1, 2, 3), "Haengender 5-t-Zedernbalken mit Hanfseil-Schlinge (Origin exakt am Aufhaenge-Schaekel (0,0,0))"),
    ("sy_pitch_kiln",            build_sy_pitch_kiln,            (0, 1, 2, 3), "Gemauerter Kopher-Pechsiedeofen mit Kessel, Glutraum, Kelle & Kuebeln (Origin Boden, -0.35m)"),
    ("sy_smithy_forge",          build_sy_smithy_forge,          (0, 1, 2, 3), "Ueberdachte Tubal-Kain-Schmiede mit Esse, Blasebalg, Amboss, Trog & Werkzeug (Origin Boden, -0.35m)"),
    ("sy_charcoal_kiln",         build_sy_charcoal_kiln,         (0, 1, 2, 3), "Kuppel-Holzkohlemeiler mit Holzstoss, Glut-Lueftungen & Erdmantel (Origin Boden, -0.35m)"),
    ("sy_sawmill_base",          build_sy_sawmill_base,          (0, 1, 2, 3), "Saegewerk Galgenportal & Basalt-Ochsenring (Origin Koenigswellen-Mitte (0,0,0), -0.35m)"),
    ("sy_sawmill_capstan_rotor", build_sy_sawmill_capstan_rotor, (0, 1, 2, 3), "Drehendes 48er-Kammrad + Jochbalken (Origin exakt auf Koenigswellen-Mitte Z @ (0,0,0))"),
    ("sy_sawmill_driveshaft",    build_sy_sawmill_driveshaft,    (0, 1, 2, 3), "Vorgelegewelle mit 8er-Stockritzel, Schwungrad & Kurbelzapfen (Origin exakt auf Wellenachse X @ (0,0,0))"),
    ("sy_sawmill_frame",         build_sy_sawmill_frame,         (0, 1, 2, 3), "Vertikales Saegegatter mit Bronze-Saegeblatt (Origin exakt auf unterem Gatterzapfen (0,0,0))"),
    ("sy_sawmill_pitman",        build_sy_sawmill_pitman,        (0, 1, 2, 3), "Pleuelstange mit Lageraugen (Origin exakt auf Kurbelzapfen (0,0,0))"),
    ("sy_sawpit_shed",           build_sy_sawpit_shed,           (0, 1, 2, 3), "Ueberdachte Saegegrube mit Stammauflage & Zedernstamm (Origin Boden, -0.35m)"),
    ("sy_timber_chute_segment",  build_sy_timber_chute_segment,  (0, 1, 2, 3), "Holzriesen-Rinne auf Bockstuetzen (Origin Boden, -0.35m)"),
    ("sy_log_stack",             build_sy_log_stack,             (0, 1, 2, 3), "Verzimmerter Balken-/Plankenstapel mit Werkbank & Bronze-Werkzeug (Origin Boden, -0.35m)"),
    ("sy_tent_worker",           build_sy_tent_worker,           (0, 1, 2, 3), "Gestreiftes Arbeiterzelt mit Abspannseilen & Vordach (Origin Boden, -0.35m)"),
    ("sy_cage_rolling",          build_sy_cage_rolling,          (0, 1, 2, 3), "Eichen-/Bronze-Raubtier-Transportkaefig auf Holzraedern (Origin Radaufstand Z=0.0)"),
    # B) Aquädukt, Flussbau & Magur-Boote (12)
    ("sy_aqueduct_source",       build_sy_aqueduct_source,       (0, 1, 2, 3), "Quellbecken-Fassung am Hang mit Einlaufgitter (Origin Boden, -0.35m)"),
    ("sy_aqueduct_pier_span",    build_sy_aqueduct_pier_span,    (0, 1, 2, 3), "Gemauerter Basalt-/Quellsteinbogen mit ueberlappendem Holzgerinne (Origin Boden, -0.35m)"),
    ("sy_aqueduct_trough",       build_sy_aqueduct_trough,       (0, 1, 2, 3), "Ablauf-Trog & Verteilungsbecken mit Bronze-Auslaeufen (Origin Boden, -0.35m)"),
    ("river_magur_cargo",        build_river_magur_cargo,        (0, 1, 2, 3), "Sumerisches Magur-Frachtboot mit Amphoren/Kornsaecken & Stechruder (Origin Wasserlinie Z=0.0)"),
    ("river_magur_timber",       build_river_magur_timber,       (0, 1, 2, 3), "Sumerisches Magur-Holzboot mit Zedernstaemmen & Stechruder (Origin Wasserlinie Z=0.0)"),
    ("river_waterwheel_base",    build_river_waterwheel_base,    (0, 1, 2, 3), "Lagerboecke & Gerinne fuer Noria-Wasserrad (Origin Boden, Achse bei Z=2.05m, -0.35m)"),
    ("river_waterwheel_rotor",   build_river_waterwheel_rotor,   (0, 1, 2, 3), "Schaufel- & schoepfkastenbestuecktes Noria-Wasserrad (Origin exakt auf Drehachse X @ (0,0,0))"),
    ("river_shaduf_post",        build_river_shaduf_post,        (0, 1, 2, 3), "Gabelpfosten-Staender fuer Schaduf (Origin Boden, Kippachse Z=2.10m, -0.35m)"),
    ("river_shaduf_arm",         build_river_shaduf_arm,         (0, 1, 2, 3), "Schwenkbarer Schaduf-Schoepfbaum mit Gegengewicht & Eimer (Origin exakt auf Kippachse (0,0,0))"),
    ("river_sluice_gate",        build_river_sluice_gate,        (0, 1, 2, 3), "Gemauerte Kanal-Schleuse mit Schuetztafel & Winde (Origin Boden, -0.35m)"),
    ("river_weir",               build_river_weir,               (0, 1, 2, 3), "Holzbohlen-Wehr mit Ramm-Pfaehlen & Basalt-Schuettung (Origin Boden, -0.35m)"),
    ("river_timber_jetty",       build_river_timber_jetty,       (0, 1, 2, 3), "Hoelzerner Landungssteg mit Pollern, Tauwerk & Faessern (Origin Boden, -0.50m Pfaehle)"),
    # C) Feld-, Lager- & Weg-Requisiten (6)
    ("field_straw_rick",         build_field_straw_rick,         (0, 1, 2, 3), "Konischer Stroh-/Heudiemen mit Holzgabel (Origin Boden, -0.35m)"),
    ("field_shelter",            build_field_shelter,            (0, 1, 2, 3), "Offener Schilfdach-Feldunterstand mit Wasserkrugen (Origin Boden, -0.35m)"),
    ("world_boulder_01",         build_world_boulder_01,         (0, 1, 2, 3), "Verwitterter Steppen-Findling Form 1 (breiter Basaltblock, -0.35m)"),
    ("world_boulder_02",         build_world_boulder_02,         (0, 1, 2, 3), "Verwitterter Steppen-Findling Form 2 (schlanker Spaltfels, -0.35m)"),
    ("world_boulder_03",         build_world_boulder_03,         (0, 1, 2, 3), "Verwitterter Steppen-Findling Form 3 (Dreier-Felsgruppe, -0.35m)"),
    ("world_supply_cart",        build_world_supply_cart,        (0, 1, 2, 3), "Beladener Vorratskarren mit Kornsaecken, Fass & Amphore (Origin Radaufstand Z=0.0)"),
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
    mat = create_shipyard_trim_material(tex_dir)
    all_objs = []
    module_stats = {}

    print(f"[SHIPYARD KIT] Generiere {len(MODULE_BUILDERS)} Werft-/Aquädukt-/Fluss-Module (je 4 LODs)...", flush=True)
    for mod_name, builder_fn, lod_tuple, desc in MODULE_BUILDERS:
        lod_counts = {}
        min_z_all = 0.0
        max_z_all = -999.0
        for lod in lod_tuple:
            bm = bmesh.new()
            uv_layer = bm.loops.layers.uv.new("UVMap")
            builder_fn(bm, uv_layer, lod)
            obj_name = f"{mod_name}_LOD{lod}"
            obj, tri_cnt, min_z, max_z = _finalize_bmesh_to_object(scene, obj_name, bm, mat)
            all_objs.append(obj)
            lod_counts[f"LOD{lod}"] = tri_cnt
            min_z_all = min(min_z_all, min_z)
            max_z_all = max(max_z_all, max_z)

        module_stats[mod_name] = {
            "lods": lod_counts,
            "minZ": round(min_z_all, 3),
            "maxZ": round(max_z_all, 3),
            "description": desc,
        }
        lod_str = " | ".join(f"{k}={v:4d}" for k, v in lod_counts.items())
        print(f"  [MOD] {mod_name:26s} | {lod_str} | minZ={min_z_all:+.2f}m", flush=True)

    blend_path = os.path.join(blend_dir, "shipyard_industry_kit.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[SHIPYARD KIT] .blend gespeichert: {blend_path}", flush=True)

    glb_path = os.path.join(glb_dir, "shipyard_industry_kit.glb")
    export_arche_glb.export_glb(all_objs, glb_path, use_draco=False)
    size_kb = os.path.getsize(glb_path) / 1024.0
    print(f"[SHIPYARD KIT] GLB exportiert in {time.time() - t0:.2f}s ({size_kb:.1f} KB, {len(all_objs)} Meshes).", flush=True)
    return module_stats, size_kb


def update_manifest(module_stats, glb_kb):
    mpath = os.path.join(ASSETS_DIR, "manifest.json")
    with open(mpath, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    items = manifest.setdefault("categories", {}).setdefault("world", {}).setdefault("items", {})
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_lod0 = sum(v["lods"].get("LOD0", 0) for v in module_stats.values())

    items["shipyard_industry_kit"] = {
        "enabled": True,
        "url": "assets/glb/world/shipyard_industry_kit.glb",
        "blend": "assets/blend/world/shipyard_industry_kit.blend",
        "category": "world",
        "description": (
            f"Modulares Bronzezeit-Werft-, Aquädukt-, Fluss- & Magur-Boots-Kit "
            f"({len(module_stats)} Module, 4 LODs, -0.35m Sockel, 1 Shared 2048x1024 Trim-Sheet inkl. Emissive=4.0)"
        ),
        "instanced": True,
        "materials": 1,
        "emissiveStrength": 4.0,
        "modulesCount": len(module_stats),
        "totalLod0Tris": total_lod0,
        "lodBandsMeters": {
            "LOD0": [0, 150],
            "LOD1": [150, 500],
            "LOD2": [500, 1500],
            "LOD3": [1500, 3000],
        },
        "sharedTextures": {
            "baseColor": "assets/textures/shipyard_trim_atlas_baseColor.png",
            "normal": "assets/textures/shipyard_trim_atlas_normal.png",
            "orm": "assets/textures/shipyard_trim_atlas_orm.png",
            "emissive": "assets/textures/shipyard_trim_atlas_emissive.png",
        },
        "modules": module_stats,
        "preview": "assets/previews/shipyard_industry_showcase.png",
        "glbSizeKB": round(glb_kb, 1),
        "exportedAt": now_str,
    }

    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"[MANIFEST] assets/manifest.json fuer 'shipyard_industry_kit' ({len(module_stats)} Module) aktualisiert.", flush=True)


# ==============================================================================
# VISUELLES KONTROLL-RENDERING (shipyard_industry_showcase.png)
# ==============================================================================

def render_showcase():
    t0 = time.time()
    print("[SHOWCASE] Lade shipyard_industry_kit.blend und erstelle Studio-Tableau...", flush=True)
    scene = clear_scene()
    dev = setup_cycles(scene, samples=48, use_oidn=True)

    vts = [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items]
    scene.view_settings.view_transform = "AgX" if "AgX" in vts else "Filmic"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = -0.10

    blend_path = os.path.join(ASSETS_DIR, "blend", "world", "shipyard_industry_kit.blend")
    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
        data_to.objects = list(data_from.objects)
    obj_map = {o.name: o for o in data_to.objects if o is not None}

    # Bodenplatte auf Z=0.0 (warm-sandiger Werftboden)
    bpy.ops.mesh.primitive_plane_add(size=180.0, location=(0.0, 0.0, 0.0))
    ground = bpy.context.active_object
    g_mat = bpy.data.materials.new("ShowcaseWerftGround")
    g_mat.use_nodes = True
    bsdf_g = g_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf_g:
        bsdf_g.inputs["Base Color"].default_value = (0.31, 0.25, 0.17, 1.0)
        bsdf_g.inputs["Roughness"].default_value = 0.90
    ground.data.materials.append(g_mat)

    # Fluss-Wasserstreifen vorne links fuer Magur-Boote, Wasserrad, Wehr & Steg (Z = +0.02 m)
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(-11.5, -20.5, 0.02))
    water = bpy.context.active_object
    water.scale = (34.0, 14.0, 1.0)
    w_mat = bpy.data.materials.new("ShowcaseRiverWater")
    w_mat.use_nodes = True
    bsdf_w = w_mat.node_tree.nodes.get("Principled BSDF")
    if bsdf_w:
        bsdf_w.inputs["Base Color"].default_value = (0.04, 0.16, 0.18, 1.0)
        bsdf_w.inputs["Roughness"].default_value = 0.09
        bsdf_w.inputs["Specular IOR Level"].default_value = 0.65
    water.data.materials.append(w_mat)

    # Gestaffelte Studio-Aufstellung (ohne Ueberdeckung, von vorne flach -> hinten hoch!)
    # (Objektname, Position (X, Y, Z), Rotation (rx, ry, rz))
    placements = [
        # Vordergrund rechts (Y = -22.5m): Exemplarische LOD0 -> LOD1 -> LOD2 -> LOD3 Vergleichsreihe an sy_pitch_kiln
        ("sy_pitch_kiln_LOD0",            ( +7.0, -22.5, 0.0), (0.0, 0.0, math.radians(-12.0))),
        ("sy_pitch_kiln_LOD1",            (+11.6, -22.5, 0.0), (0.0, 0.0, math.radians(-12.0))),
        ("sy_pitch_kiln_LOD2",            (+16.2, -22.5, 0.0), (0.0, 0.0, math.radians(-12.0))),
        ("sy_pitch_kiln_LOD3",            (+20.8, -22.5, 0.0), (0.0, 0.0, math.radians(-12.0))),

        # Vordergrund Flussbereich (Y = -20.5m, auf Wasserlinie Z=0.0): Magur-Boote, Steg, Wehr, Schleuse, Wasserrad, Schaduf
        ("river_magur_cargo_LOD0",        (-20.2, -21.2, 0.0), (0.0, 0.0, math.radians(58.0))),
        ("river_magur_timber_LOD0",       (-16.5, -16.2, 0.0), (0.0, 0.0, math.radians(96.0))),
        ("river_timber_jetty_LOD0",       ( -9.5, -21.2, 0.0), (0.0, 0.0, math.radians(15.0))),
        ("river_weir_LOD0",               ( -3.5, -21.2, 0.0), (0.0, 0.0, math.radians(10.0))),
        ("river_sluice_gate_LOD0",        ( +2.2, -20.8, 0.0), (0.0, 0.0, math.radians(180.0))),
        ("river_waterwheel_base_LOD0",    (-13.8, -23.2, 0.0), (0.0, 0.0, math.radians(22.0))),
        ("river_waterwheel_rotor_LOD0",   (-13.8, -23.2, 2.05),(0.0, 0.0, math.radians(22.0))),
        ("river_shaduf_post_LOD0",        ( +1.8, -15.2, 0.0), (0.0, 0.0, math.radians(25.0))),
        ("river_shaduf_arm_LOD0",         ( +1.8, -15.2, 2.10),(math.radians(-12.0), 0.0, math.radians(25.0))),

        # Reihe 1 (Y = -8.5m): Feld-, Lager- & Weg-Requisiten + Meiler, Schmiede, Kaefig, Kielkloetze (alle Fronten zur Kamera!)
        ("world_boulder_01_LOD0",         (-24.8,  -9.5, 0.0), (0.0, 0.0, 0.3)),
        ("world_boulder_02_LOD0",         (-22.2,  -9.0, 0.0), (0.0, 0.0, -0.4)),
        ("world_boulder_03_LOD0",         (-19.0,  -9.8, 0.0), (0.0, 0.0, 0.8)),
        ("field_straw_rick_LOD0",         (-15.2,  -9.0, 0.0), (0.0, 0.0, 0.2)),
        ("field_shelter_LOD0",            (-10.4,  -9.0, 0.0), (0.0, 0.0, math.radians(12.0))),
        ("world_supply_cart_LOD0",        ( -5.6,  -9.2, 0.0), (0.0, 0.0, math.radians(130.0))),
        ("sy_cage_rolling_LOD0",          ( -1.2,  -9.2, 0.0), (0.0, 0.0, math.radians(125.0))),
        ("sy_cribbing_block_LOD0",        ( +3.0,  -9.2, 0.0), (0.0, 0.0, 0.2)),
        ("sy_log_stack_LOD0",             ( +8.0,  -8.8, 0.0), (0.0, 0.0, math.radians(180.0))),
        ("sy_tent_worker_LOD0",           (+13.8,  -8.8, 0.0), (0.0, 0.0, math.radians(-15.0))),
        ("sy_charcoal_kiln_LOD0",         (+19.6,  -8.8, 0.0), (0.0, 0.0, math.radians(-12.0))),
        ("sy_smithy_forge_LOD0",          (+25.2,  -8.6, 0.0), (0.0, 0.0, math.radians(18.0))),

        # Reihe 2 (Y = +4.8m): Rampe+Klappe, Holzriese, Saegegrube & zusammengebautes Saegewerk-Ensemble
        ("sy_ramp_module_LOD0",           (-24.0,  +4.5, 0.0), (0.0, 0.0, math.radians(-20.0))),
        ("sy_drawbridge_flap_LOD0",       (-22.97, +7.32,2.14),(math.radians(8.0), 0.0, math.radians(-20.0))),
        ("sy_timber_chute_segment_LOD0",  (-17.0,  +4.8, 0.0), (0.0, 0.0, math.radians(25.0))),
        ("sy_sawpit_shed_LOD0",           ( -8.8,  +5.2, 0.0), (0.0, 0.0, math.radians(-10.0))),
        # Komplettes Saegewerk sauber gekoppelt (X=+2.8, Y=+5.2): Kammrad Z=2.35 -> Stockritzel Y=6.82, Z=2.88 -> Kurbel Y=3.12, Z=3.22
        ("sy_sawmill_base_LOD0",          ( +2.8,  +5.2, 0.0), (0.0, 0.0, 0.0)),
        ("sy_sawmill_capstan_rotor_LOD0", ( +2.8,  +5.2, 0.0), (0.0, 0.0, math.radians(15.0))),
        ("sy_sawmill_driveshaft_LOD0",    ( +2.8,  +5.47,2.88),(0.0, 0.0, math.radians(-90.0))),
        ("sy_sawmill_pitman_LOD0",        ( +2.8,  +3.12,3.22),(math.pi, 0.0, 0.0)),
        ("sy_sawmill_frame_LOD0",         ( +2.8,  +3.12,0.82),(0.0, 0.0, 0.0)),
        # Saegewerk-Einzelteile daneben freigestellt sichtbar
        ("sy_sawmill_capstan_rotor_LOD0", (+13.2,  +5.2, 0.0), (0.0, 0.0, math.radians(35.0))),
        ("sy_sawmill_driveshaft_LOD0",    (+20.2,  +5.0, 1.05),(0.0, 0.0, math.radians(20.0))),
        ("sy_sawmill_frame_LOD0",         (+24.2,  +5.0, 0.15),(0.0, 0.0, math.radians(-15.0))),
        ("sy_sawmill_pitman_LOD0",        (+26.0,  +5.0, 0.15),(0.0, 0.0, math.radians(-15.0))),

        # Reihe 3 (Y = +19.5m): Hohe Bauwerke: Aquädukt-Ensemble, Baugeruest & Bockkran+Winde+Zedernlast
        ("sy_aqueduct_source_LOD0",       (-24.8, +19.5, 0.0), (0.0, 0.0, math.radians(-70.0))),
        ("sy_aqueduct_pier_span_LOD0",    (-17.2, +19.5, 0.0), (0.0, 0.0, 0.0)),
        ("sy_aqueduct_pier_span_LOD0",    (-11.2, +19.5, 0.0), (0.0, 0.0, 0.0)),
        ("sy_aqueduct_trough_LOD0",       ( -5.2, +19.5, 0.0), (0.0, 0.0, math.radians(75.0))),
        ("sy_scaffold_bay_LOD0",          ( +3.8, +19.5, 0.0), (0.0, 0.0, math.radians(180.0))),
        ("sy_crane_aframe_LOD0",          (+14.8, +19.5, 0.0), (0.0, 0.0, math.radians(165.0))),
        ("sy_crane_winch_rotor_LOD0",     (+14.63,+20.12,1.25),(0.0, 0.0, math.radians(165.0))),
        ("sy_crane_timber_load_LOD0",     (+14.28,+17.55,7.95),(0.0, 0.0, math.radians(165.0))),
    ]

    for idx, (oname, pos, rot) in enumerate(placements):
        src = obj_map.get(oname)
        if not src:
            print(f"  [WARN] Fehlendes Showcase-Objekt: {oname}", flush=True)
            continue
        inst = src.copy()
        inst.data = src.data
        inst.name = f"Show_{idx:02d}_{oname}"
        inst.location = pos
        inst.rotation_euler = rot
        scene.collection.objects.link(inst)

    # Dezente Feuer-Akzente in Pechofen, Meiler & Schmiede-Esse
    for lx, ly, lz, en in ((+7.0, -23.6, 0.6, 24.0), (+19.6, -9.8, 0.4, 18.0), (+24.4, -8.2, 1.35, 38.0)):
        pt_d = bpy.data.lights.new("WerftFireGlow", type="POINT")
        pt_d.energy = en
        pt_d.color = (1.0, 0.45, 0.12)
        pt_o = bpy.data.objects.new("WerftFireGlow", pt_d)
        pt_o.location = (lx, ly, lz)
        scene.collection.objects.link(pt_o)

    # Warme Nachmittagssonne von schraeg-vorne-links
    sun_d = bpy.data.lights.new("WerftSun", type="SUN")
    sun_d.energy = 3.2
    sun_d.color = (1.0, 0.94, 0.85)
    sun_d.angle = math.radians(1.5)
    sun_o = bpy.data.objects.new("WerftSun", sun_d)
    sun_o.rotation_euler = (math.radians(52.0), math.radians(14.0), math.radians(-30.0))
    scene.collection.objects.link(sun_o)

    # Himmels-Weltlicht
    w = bpy.data.worlds.new("WerftSky")
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
    cam_d.lens = 33.0
    cam_d.clip_end = 500.0
    cam_o = bpy.data.objects.new("ShowcaseCam", cam_d)
    cam_o.location = (0.0, -64.0, 33.0)
    target = Vector((0.0, -2.0, 1.6))
    cam_o.rotation_euler = (target - cam_o.location).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cam_o)
    scene.camera = cam_o

    prev_dir = os.path.join(ASSETS_DIR, "previews")
    os.makedirs(prev_dir, exist_ok=True)
    out_png = os.path.join(prev_dir, "shipyard_industry_showcase.png")
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
    print(f"[SHIPYARD KIT DONE] Gesamtlaufzeit: {time.time() - t_total:.2f}s.", flush=True)


if __name__ == "__main__":
    main()
