"""
build_temenos_hero_kit.py — Hero-Tempelbezirk Ur-Schinar (Blender Master, 4-LOD GLB, Manifest & 4 AgX-Showcases)
=================================================================================================================
Erzeugt das komplette Hero-Asset-Kit fuer den Temenos von Ur-Schinar:
  - assets/blend/city/temenos_hero_kit.blend
  - assets/glb/city/temenos_hero_kit.glb  (alle Hero-Assets x 4 LODs: LOD0..LOD3, +Y Up, Origin Z=0, -0.30m Schuerze)
  - Registrierung in assets/manifest.json
  - 4 verbindliche Cycles CUDA + AgX Kontrollrenderings in assets/previews/:
      1) temenos_hero_overview.png
      2) temenos_ziggurat_closeup.png
      3) temenos_abzu_pond_closeup.png
      4) temenos_garden_props_lineup.png

Aufruf:
  blender --background --python assets/scripts/build_temenos_hero_kit.py
"""

import os
import sys
import json
import time
import math
import random
import bpy
import bmesh
import addon_utils
from mathutils import Vector, Matrix, Euler

# Import UV maps from atlas script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from build_temenos_hero_atlas import TEMENOS_TRIM_REGIONS, BOTANY_CELLS


def get_project_root():
    return os.path.dirname(os.path.dirname(SCRIPT_DIR))


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    return scene


def enable_addons():
    for mod in ("cycles", "bl_ext.blender_org.sapling_tree_gen", "bl_ext.blender_org.ivygen"):
        try:
            addon_utils.enable(mod, default_set=False, persistent=False)
        except Exception as e:
            print(f"[TEMENOS KIT] Hinweis Addon {mod}: {e}", flush=True)


# ==============================================================================
# 1) MATERIAL-FACTORY (3 SHARED MATERIALS: TRIM, BOTANY, ABZU WATER)
# ==============================================================================

def _load_img(path, colorspace):
    img = bpy.data.images.load(path, check_existing=True)
    img.colorspace_settings.name = colorspace
    try:
        img.pack()
    except Exception:
        pass
    return img


def build_shared_materials(project_root):
    tex_dir = os.path.join(project_root, "assets", "textures")

    # 1. Hero Temenos Trim Material (glTF 2.0 ORM + Normal + Emissive)
    mat_trim = bpy.data.materials.new("Mat_Temenos_Hero_Trim")
    mat_trim.use_nodes = True
    nt = mat_trim.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    t_col = nodes.new("ShaderNodeTexImage")
    t_col.image = _load_img(os.path.join(tex_dir, "temenos_hero_trim_baseColor.png"), "sRGB")
    links.new(t_col.outputs["Color"], bsdf.inputs["Base Color"])

    t_nrm = nodes.new("ShaderNodeTexImage")
    t_nrm.image = _load_img(os.path.join(tex_dir, "temenos_hero_trim_normal.png"), "Non-Color")
    nm = nodes.new("ShaderNodeNormalMap")
    nm.inputs["Strength"].default_value = 1.0
    links.new(t_nrm.outputs["Color"], nm.inputs["Color"])
    links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])

    t_orm = nodes.new("ShaderNodeTexImage")
    t_orm.image = _load_img(os.path.join(tex_dir, "temenos_hero_trim_orm.png"), "Non-Color")
    sep = nodes.new("ShaderNodeSeparateColor")
    links.new(t_orm.outputs["Color"], sep.inputs["Color"])
    links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])

    # glTF AO socket (KHR / standard glTF Material Output node group)
    ng = bpy.data.node_groups.get("glTF Material Output")
    if ng is None:
        ng = bpy.data.node_groups.new("glTF Material Output", "ShaderNodeTree")
        ng.interface.new_socket(name="Occlusion", in_out="INPUT", socket_type="NodeSocketFloat")
    gltf_out = nodes.new("ShaderNodeGroup")
    gltf_out.node_tree = ng
    links.new(sep.outputs["Red"], gltf_out.inputs["Occlusion"])

    t_emi = nodes.new("ShaderNodeTexImage")
    t_emi.image = _load_img(os.path.join(tex_dir, "temenos_hero_trim_emissive.png"), "sRGB")
    if "Emission Color" in bsdf.inputs:
        links.new(t_emi.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 3.6

    # 2. Temple Botany Material (Alpha Clip Cutout + Normal + ORM)
    mat_bot = bpy.data.materials.new("Mat_Temenos_Botany")
    mat_bot.use_nodes = True
    mat_bot.use_backface_culling = False
    if hasattr(mat_bot, "blend_method"):
        mat_bot.blend_method = "CLIP"
    if hasattr(mat_bot, "alpha_threshold"):
        mat_bot.alpha_threshold = 0.36
    nt = mat_bot.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tb_col = nodes.new("ShaderNodeTexImage")
    tb_col.image = _load_img(os.path.join(tex_dir, "temenos_botany_atlas_baseColor.png"), "sRGB")
    links.new(tb_col.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(tb_col.outputs["Alpha"], bsdf.inputs["Alpha"])

    tb_nrm = nodes.new("ShaderNodeTexImage")
    tb_nrm.image = _load_img(os.path.join(tex_dir, "temenos_botany_atlas_normal.png"), "Non-Color")
    nm_b = nodes.new("ShaderNodeNormalMap")
    nm_b.inputs["Strength"].default_value = 0.75
    links.new(tb_nrm.outputs["Color"], nm_b.inputs["Color"])
    links.new(nm_b.outputs["Normal"], bsdf.inputs["Normal"])

    tb_orm = nodes.new("ShaderNodeTexImage")
    tb_orm.image = _load_img(os.path.join(tex_dir, "temenos_botany_atlas_orm.png"), "Non-Color")
    sep_b = nodes.new("ShaderNodeSeparateColor")
    links.new(tb_orm.outputs["Color"], sep_b.inputs["Color"])
    links.new(sep_b.outputs["Green"], bsdf.inputs["Roughness"])
    bsdf.inputs["Metallic"].default_value = 0.0
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.22
        bsdf.inputs["Subsurface Scale"].default_value = 0.02

    # 3. Abzu Water Surface Material (translucent turquoise-emerald reflective water)
    mat_water = bpy.data.materials.new("Mat_Abzu_Water")
    mat_water.use_nodes = True
    if hasattr(mat_water, "blend_method"):
        mat_water.blend_method = "BLEND"
    nt = mat_water.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.045, 0.22, 0.24, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.055
    bsdf.inputs["Metallic"].default_value = 0.02
    bsdf.inputs["IOR"].default_value = 1.333
    bsdf.inputs["Alpha"].default_value = 0.68
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.65
        bsdf.inputs["Coat Roughness"].default_value = 0.03
    tc = nodes.new("ShaderNodeTexCoord")
    noi = nodes.new("ShaderNodeTexNoise")
    noi.inputs["Scale"].default_value = 9.0
    noi.inputs["Detail"].default_value = 4.0
    noi.inputs["Roughness"].default_value = 0.45
    links.new(tc.outputs["Object"], noi.inputs["Vector"])
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.07
    bump.inputs["Distance"].default_value = 0.015
    links.new(noi.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    return mat_trim, mat_bot, mat_water


# ==============================================================================
# 2) BMESH ARCHITEKTUR- & BOTANIK-PRIMITIVE (MIT EXAKTEM TRIM-UV-MAPPING)
# ==============================================================================

def _map_face_uv(face, uv_layer, region_name, u_scale=0.25, v_fit=True, mat_idx=0):
    face.material_index = mat_idx
    u0, v0, u1, v1 = TEMENOS_TRIM_REGIONS[region_name]
    du = u1 - u0
    dv = v1 - v0
    n = face.normal
    verts = [l.vert.co for l in face.loops]
    # Project onto dominant tangent plane
    if abs(n.z) > 0.72:
        pts = [(v.x, v.y) for v in verts]
    elif abs(n.x) > abs(n.y):
        pts = [(v.y, v.z) for v in verts]
    else:
        pts = [(v.x, v.z) for v in verts]

    min_x = min(p[0] for p in pts)
    max_x = max(p[0] for p in pts)
    min_y = min(p[1] for p in pts)
    max_y = max(p[1] for p in pts)
    sx = max(1e-4, max_x - min_x)
    sy = max(1e-4, max_y - min_y)

    # Full-width bands (u0==0 and u1==1) can tile freely in U; sub-tiles stay clamped inside [u0..u1]
    can_tile_u = (u0 <= 0.001 and u1 >= 0.999)
    for loop, (px, py) in zip(face.loops, pts):
        tx = (px - min_x) / sx
        ty = (py - min_y) / sy
        if can_tile_u:
            u = (px - min_x) * u_scale
        else:
            u = u0 + tx * du
        v = v0 + (ty if v_fit else min(1.0, (py - min_y) * u_scale)) * dv
        loop[uv_layer].uv = (u, v)


def add_prism(bm, uv_layer, cx, cy, z0, z1, wx0, wy0, wx1, wy1, region, u_scale=0.22, top_region=None, mat_idx=0):
    """Battered 3D prism with clean UV projection on every face."""
    hx0, hy0 = wx0 * 0.5, wy0 * 0.5
    hx1, hy1 = wx1 * 0.5, wy1 * 0.5
    v0 = bm.verts.new((cx - hx0, cy - hy0, z0))
    v1 = bm.verts.new((cx + hx0, cy - hy0, z0))
    v2 = bm.verts.new((cx + hx0, cy + hy0, z0))
    v3 = bm.verts.new((cx - hx0, cy + hy0, z0))
    v4 = bm.verts.new((cx - hx1, cy - hy1, z1))
    v5 = bm.verts.new((cx + hx1, cy - hy1, z1))
    v6 = bm.verts.new((cx + hx1, cy + hy1, z1))
    v7 = bm.verts.new((cx - hx1, cy + hy1, z1))

    side_defs = [
        (v0, v1, v5, v4),
        (v1, v2, v6, v5),
        (v2, v3, v7, v6),
        (v3, v0, v4, v7),
    ]
    faces = []
    for verts in side_defs:
        f = bm.faces.new(verts)
        f.normal_update()
        _map_face_uv(f, uv_layer, region, u_scale=u_scale, mat_idx=mat_idx)
        faces.append(f)

    f_top = bm.faces.new((v4, v5, v6, v7))
    f_top.normal_update()
    _map_face_uv(f_top, uv_layer, top_region or region, u_scale=u_scale, mat_idx=mat_idx)
    faces.append(f_top)

    f_bot = bm.faces.new((v3, v2, v1, v0))
    f_bot.normal_update()
    _map_face_uv(f_bot, uv_layer, region, u_scale=u_scale, mat_idx=mat_idx)
    faces.append(f_bot)
    c_mid = Vector((cx, cy, 0.5 * (z0 + z1)))
    for f in faces:
        f.normal_update()
        if (f.calc_center_median() - c_mid).dot(f.normal) < 0.0:
            f.normal_flip()
    return faces


def add_box(bm, uv_layer, cx, cy, z0, z1, wx, wy, region, u_scale=0.22, top_region=None, mat_idx=0):
    return add_prism(bm, uv_layer, cx, cy, z0, z1, wx, wy, wx, wy, region, u_scale=u_scale, top_region=top_region, mat_idx=mat_idx)


def add_cylinder(bm, uv_layer, cx, cy, z0, z1, r0, r1, segs, region, u_scale=0.35, mat_idx=0, cap_top=True):
    bot = []
    top = []
    for i in range(segs):
        a = 2.0 * math.pi * i / segs
        ca, sa = math.cos(a), math.sin(a)
        bot.append(bm.verts.new((cx + ca * r0, cy + sa * r0, z0)))
        top.append(bm.verts.new((cx + ca * r1, cy + sa * r1, z1)))
    u0, v0, u1, v1 = TEMENOS_TRIM_REGIONS[region]
    du, dv = u1 - u0, v1 - v0
    for i in range(segs):
        j = (i + 1) % segs
        f = bm.faces.new((bot[i], bot[j], top[j], top[i]))
        f.material_index = mat_idx
        f.smooth = (segs >= 8)
        ua = u0 + (i / segs) * du
        ub = u0 + ((i + 1) / segs) * du
        for loop, uv in zip(f.loops, [(ua, v0), (ub, v0), (ub, v1), (ua, v1)]):
            loop[uv_layer].uv = uv
    if cap_top and r1 > 1e-4:
        ft = bm.faces.new(top)
        ft.normal_update()
        _map_face_uv(ft, uv_layer, region, u_scale=u_scale, mat_idx=mat_idx)


def add_lathe(bm, uv_layer, cx, cy, z_base, profile, segs, region, mat_idx=0):
    """Rotationskoerper (Amphoren, Terrakotta-Kuebel, Bronze-Feuerschalen)."""
    rings = []
    for r, dz in profile:
        ring = []
        for i in range(segs):
            a = 2.0 * math.pi * i / segs
            ring.append(bm.verts.new((cx + math.cos(a) * r, cy + math.sin(a) * r, z_base + dz)))
        rings.append(ring)
    u0, v0, u1, v1 = TEMENOS_TRIM_REGIONS[region]
    du, dv = u1 - u0, v1 - v0
    n_r = len(rings)
    for ri in range(n_r - 1):
        va = v0 + (ri / max(1, n_r - 1)) * dv
        vb = v0 + ((ri + 1) / max(1, n_r - 1)) * dv
        for i in range(segs):
            j = (i + 1) % segs
            f = bm.faces.new((rings[ri][i], rings[ri][j], rings[ri+1][j], rings[ri+1][i]))
            f.material_index = mat_idx
            f.smooth = (segs >= 8)
            ua = u0 + (i / segs) * du
            ub = u0 + ((i + 1) / segs) * du
            for loop, uv in zip(f.loops, [(ua, va), (ub, va), (ub, vb), (ua, vb)]):
                loop[uv_layer].uv = uv
    # Cap top if open
    if profile[-1][0] > 0.01:
        ft = bm.faces.new(rings[-1])
        ft.normal_update()
        _map_face_uv(ft, uv_layer, region, mat_idx=mat_idx)


def add_parapet_with_merlons(bm, uv_layer, cx, cy, z_deck, wx, wy, wall_t, h_wall, region,
                             merlons=True, merlon_h=0.28, cap_region="travertine", skip_front_gap=0.0):
    """Umlaufende Zinnenbruestung mit optionaler Front-Oeffnung (+Y) fuer Treppen."""
    hx, hy = wx * 0.5, wy * 0.5
    # Back (-Y)
    add_box(bm, uv_layer, cx, cy - hy + wall_t * 0.5, z_deck, z_deck + h_wall, wx, wall_t, region, top_region=cap_region)
    # Left (-X) & Right (+X)
    add_box(bm, uv_layer, cx - hx + wall_t * 0.5, cy, z_deck, z_deck + h_wall, wall_t, wy - wall_t * 2, region, top_region=cap_region)
    add_box(bm, uv_layer, cx + hx - wall_t * 0.5, cy, z_deck, z_deck + h_wall, wall_t, wy - wall_t * 2, region, top_region=cap_region)
    # Front (+Y) with optional stair gap
    if skip_front_gap > 0.1:
        seg_w = max(0.4, (wx - skip_front_gap) * 0.5)
        add_box(bm, uv_layer, cx - hx + seg_w * 0.5, cy + hy - wall_t * 0.5, z_deck, z_deck + h_wall, seg_w, wall_t, region, top_region=cap_region)
        add_box(bm, uv_layer, cx + hx - seg_w * 0.5, cy + hy - wall_t * 0.5, z_deck, z_deck + h_wall, seg_w, wall_t, region, top_region=cap_region)
    else:
        add_box(bm, uv_layer, cx, cy + hy - wall_t * 0.5, z_deck, z_deck + h_wall, wx, wall_t, region, top_region=cap_region)

    if merlons:
        step = 1.05
        m_w = 0.52
        # Along -Y and +Y
        nx = max(2, int(wx / step))
        for i in range(nx):
            mx = cx - hx + 0.45 + i * ((wx - 0.9) / max(1, nx - 1))
            add_box(bm, uv_layer, mx, cy - hy + wall_t * 0.5, z_deck + h_wall, z_deck + h_wall + merlon_h, m_w, wall_t * 0.92, region, top_region=cap_region)
            if abs(mx - cx) > skip_front_gap * 0.5 + 0.35:
                add_box(bm, uv_layer, mx, cy + hy - wall_t * 0.5, z_deck + h_wall, z_deck + h_wall + merlon_h, m_w, wall_t * 0.92, region, top_region=cap_region)
        # Along -X and +X
        ny = max(2, int(wy / step))
        for j in range(1, ny - 1):
            my = cy - hy + 0.45 + j * ((wy - 0.9) / max(1, ny - 1))
            add_box(bm, uv_layer, cx - hx + wall_t * 0.5, my, z_deck + h_wall, z_deck + h_wall + merlon_h, wall_t * 0.92, m_w, region, top_region=cap_region)
            add_box(bm, uv_layer, cx + hx - wall_t * 0.5, my, z_deck + h_wall, z_deck + h_wall + merlon_h, wall_t * 0.92, m_w, region, top_region=cap_region)


def add_pilaster_and_niche_facade(bm, uv_layer, cx, cy, z0, z1, wx0, wy0, wx1, wy1,
                                  n_x, n_y, region, lod, skip_front_x=0.0, add_drains=True):
    """Rhythmische sumerische Strebepfeiler, gestufte Blendnischen & vertikale Regenwasser-Rinnen."""
    if lod >= 2:
        return
    pil_d = 0.44 if lod == 0 else 0.36
    pil_w = 0.88 if lod == 0 else 0.95
    # Front (+Y) and Back (-Y)
    for i in range(n_x):
        t = (i + 0.5) / n_x
        px = cx + (t - 0.5) * (wx0 - 1.4)
        for sgn in (-1.0, 1.0):
            if sgn > 0 and abs(px - cx) < skip_front_x:
                continue
            py0 = cy + sgn * (wy0 * 0.5 + pil_d * 0.32)
            py1 = cy + sgn * (wy1 * 0.5 + pil_d * 0.22)
            py_mid = 0.5 * (py0 + py1)
            add_prism(bm, uv_layer, px, py_mid, z0, z1, pil_w, pil_d, pil_w * 0.86, pil_d * 0.72, region, u_scale=0.26)
            # Stepped inner niche rib (LOD0)
            if lod == 0:
                add_prism(bm, uv_layer, px, py_mid + sgn * 0.12, z0 + 0.25, z1 - 0.25, pil_w * 0.46, pil_d * 0.55, pil_w * 0.38, pil_d * 0.45, region, u_scale=0.28)
    # Left (-X) and Right (+X)
    for j in range(n_y):
        t = (j + 0.5) / n_y
        py = cy + (t - 0.5) * (wy0 - 1.4)
        for sgn in (-1.0, 1.0):
            px0 = cx + sgn * (wx0 * 0.5 + pil_d * 0.32)
            px1 = cx + sgn * (wx1 * 0.5 + pil_d * 0.22)
            px_mid = 0.5 * (px0 + px1)
            add_prism(bm, uv_layer, px_mid, py, z0, z1, pil_d, pil_w, pil_d * 0.72, pil_w * 0.86, region, u_scale=0.26)
            if lod == 0:
                add_prism(bm, uv_layer, px_mid + sgn * 0.12, py, z0 + 0.25, z1 - 0.25, pil_d * 0.55, pil_w * 0.46, pil_d * 0.45, pil_w * 0.38, region, u_scale=0.28)
    # Vertical rainwater drain channels (3D projecting double-ribs with recessed trough!) on LOD0
    if add_drains and lod == 0:
        for dx in (-wx0 * 0.28, wx0 * 0.28):
            for sgn in (-1.0, 1.0):
                if sgn > 0 and abs(dx) < skip_front_x:
                    continue
                py_m = cy + sgn * (0.25 * (wy0 + wy1) + 0.18)
                for off in (-0.16, +0.16):
                    add_prism(bm, uv_layer, cx + dx + off, py_m, z0, z1, 0.10, 0.26, 0.10, 0.22, "travertine", u_scale=0.35)


def add_staircase_with_balustrades(bm, uv_layer, p0, p1, width, steps, lod, wall_region="brick_terracotta",
                                   step_region="travertine", balustrade_h=0.92, foundation_z=-0.35):
    """Monumentale Treppe mit Einzelstufen UND massiven seitlichen Treppenwangen (0 Schweben!)."""
    v0 = Vector(p0)
    v1 = Vector(p1)
    d = v1 - v0
    horiz = Vector((d.x, d.y, 0.0))
    length = horiz.length
    if length < 0.1:
        return
    fwd = horiz.normalized()
    right = Vector((-fwd.y, fwd.x, 0.0))
    n_steps = steps if lod == 0 else (max(5, steps // 2) if lod == 1 else 2)
    step_len = length / n_steps
    dz = (v1.z - v0.z) / n_steps
    w_inner = width - 0.72

    def _add_oriented_box(center_xy, z_bot, z_top, len_fwd, len_right, reg, top_reg=None):
        hf = fwd * (len_fwd * 0.5)
        hr = right * (len_right * 0.5)
        c = Vector((center_xy.x, center_xy.y, 0.0))
        pts = [c - hf - hr, c + hf - hr, c + hf + hr, c - hf + hr]
        vb = [bm.verts.new((p.x, p.y, z_bot)) for p in pts]
        vt = [bm.verts.new((p.x, p.y, z_top)) for p in pts]
        for i in range(4):
            j = (i + 1) % 4
            f = bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
            f.normal_update()
            _map_face_uv(f, uv_layer, reg, u_scale=0.25)
        ft = bm.faces.new(vt)
        ft.normal_update()
        _map_face_uv(ft, uv_layer, top_reg or reg, u_scale=0.25)

    # Solid masonry core & steps
    for s in range(n_steps):
        t = (s + 0.5) / n_steps
        c_xy = Vector((v0.x, v0.y, 0.0)) + fwd * (t * length)
        z_top = v0.z + (s + 1) * dz
        z_bot = min(foundation_z, v0.z - 0.15) if s == 0 else max(foundation_z, z_top - max(dz * 2.2, 0.85))
        _add_oriented_box(c_xy, foundation_z if v0.z < 0.5 else v0.z - 0.25, z_top, step_len * 1.04, w_inner, wall_region, top_reg=step_region)

    # Massive flanking stepped/sloped balustrades (Treppenwangen!)
    bal_t = 0.42
    n_bal = n_steps if lod == 0 else max(4, n_steps // 2)
    b_len = length / n_bal
    for side in (-1.0, 1.0):
        lat = right * (side * (w_inner * 0.5 + bal_t * 0.5))
        for b in range(n_bal):
            t = (b + 0.5) / n_bal
            c_xy = Vector((v0.x, v0.y, 0.0)) + fwd * (t * length) + lat
            z_top = v0.z + (b + 1) * ((v1.z - v0.z) / n_bal) + balustrade_h
            z_bot = foundation_z if v0.z < 0.5 else v0.z - 0.25
            _add_oriented_box(c_xy, z_bot, z_top, b_len * 1.05, bal_t, wall_region, top_reg="travertine")
        # End-post pillar at stair foot
        c_foot = Vector((v0.x, v0.y, 0.0)) - fwd * 0.22 + lat
        _add_oriented_box(c_foot, foundation_z if v0.z < 0.5 else v0.z - 0.25, v0.z + balustrade_h + 0.28, 0.62, 0.62, wall_region, top_reg="lapis_brick")


def add_botany_card(bm, uv_layer, origin, width, height, yaw, pitch, cell_name, bend=0.14, segs_v=2, mat_idx=1):
    """Gewoelbte mehrsegmentige Blatt-/Blueten-Karte (Material-Slot 1 = Tempel-Botanik-Atlas)."""
    col, row = BOTANY_CELLS[cell_name]
    u0 = col / 3.0 + 0.008
    u1 = (col + 1) / 3.0 - 0.008
    v0 = row / 3.0 + 0.008
    v1 = (row + 1) / 3.0 - 0.008

    rot = Euler((pitch, 0.0, yaw), "XYZ").to_matrix()
    base = Vector(origin)
    cols_u = 2
    grid = []
    for iv in range(segs_v + 1):
        tv = iv / segs_v
        row_v = []
        for iu in range(cols_u + 1):
            tu = iu / cols_u
            lx = (tu - 0.5) * width
            ly = math.sin(tv * math.pi) * bend * height + (abs(tu - 0.5) * 0.14 * width)
            lz = tv * height
            p = base + rot @ Vector((lx, ly, lz))
            row_v.append((bm.verts.new(p), u0 + tu * (u1 - u0), v0 + tv * (v1 - v0)))
        grid.append(row_v)

    for iv in range(segs_v):
        for iu in range(cols_u):
            a, ua, va = grid[iv][iu]
            b, ub, vb = grid[iv][iu + 1]
            c, uc, vc = grid[iv + 1][iu + 1]
            d, ud, vd = grid[iv + 1][iu]
            f = bm.faces.new((a, b, c, d))
            f.material_index = mat_idx
            f.smooth = True
            for loop, uv in zip(f.loops, [(ua, va), (ub, vb), (uc, vc), (ud, vd)]):
                loop[uv_layer].uv = uv


def add_bush_cluster(bm, uv_layer, cx, cy, z_soil, radius, height, cell_name, n_cards, seed=0):
    rng = random.Random(seed)
    for i in range(n_cards):
        ang = (i / max(1, n_cards)) * 2.0 * math.pi + rng.uniform(-0.35, 0.35)
        r = rng.uniform(0.0, radius * 0.62)
        ox = cx + math.cos(ang) * r
        oy = cy + math.sin(ang) * r
        w = radius * rng.uniform(0.75, 1.20)
        h = height * rng.uniform(0.72, 1.15)
        pitch = rng.uniform(0.18, 0.58)
        add_botany_card(bm, uv_layer, (ox, oy, z_soil - 0.03), w, h, ang, pitch, cell_name, bend=0.18, segs_v=2)


def add_ivygen_vines_onto_bmesh(bm, uv_layer, target_box_center, target_box_size, start_pts,
                                max_ivy_len=2.2, leaf_scale=0.22, leaf_cell="ivy", lod=0):
    """Nutzt das echte Blender-Addon IvyGen (bl_ext.blender_org.ivygen) auf einem temporaeren Ziel-Mesh
    und ueberfuehrt Ranken (cedar_wood/ivy) + Blaetter direkt in unser Ziel-BMesh (0% Schweben!)."""
    if lod >= 2:
        return
    # Create temporary invisible target collider box at exact parapet/pergola location
    t_mesh = bpy.data.meshes.new("_IvyTargetTmp")
    t_bm = bmesh.new()
    bmesh.ops.create_cube(t_bm, size=1.0)
    bmesh.ops.scale(t_bm, vec=target_box_size, verts=t_bm.verts)
    bmesh.ops.translate(t_bm, vec=target_box_center, verts=t_bm.verts)
    t_bm.to_mesh(t_mesh)
    t_bm.free()
    t_obj = bpy.data.objects.new("_IvyTargetTmp", t_mesh)
    bpy.context.collection.objects.link(t_obj)

    created_objs = []
    for sp in start_pts:
        bpy.ops.object.select_all(action="DESELECT")
        t_obj.select_set(True)
        bpy.context.view_layer.objects.active = t_obj
        bpy.context.scene.cursor.location = Vector(sp)
        before = set(bpy.data.objects.keys())
        try:
            # Configure IvyGen scene properties if present
            if hasattr(bpy.context.window_manager, "ivy_gen_props"):
                ip = bpy.context.window_manager.ivy_gen_props
                ip.maxIvyLength = max_ivy_len
                ip.ivySize = 0.025
                ip.maxFloatLength = 0.25
                ip.gravityWeight = 1.35
                ip.adhesionWeight = 0.35
                ip.branchingProbability = 0.12
                ip.leafProbability = 0.55 if lod == 0 else 0.30
                ip.leafSize = leaf_scale
            bpy.ops.curve.ivy_gen(updateIvy=False, defaultIvy=False)
        except Exception as e:
            print(f"[TEMENOS KIT] IvyGen fallback ({e})", flush=True)
        new_names = [n for n in bpy.data.objects.keys() if n not in before]
        for n in new_names:
            created_objs.append(bpy.data.objects[n])

    # Transfer generated ivy curves & leaves into target bm with clean UVs
    depsgraph = bpy.context.evaluated_depsgraph_get()
    u0_c, v0_c, u1_c, v1_c = TEMENOS_TRIM_REGIONS["cedar_wood"]
    col, row = BOTANY_CELLS[leaf_cell]
    lu0, lu1 = col / 3.0 + 0.02, (col + 1) / 3.0 - 0.02
    lv0, lv1 = row / 3.0 + 0.02, (row + 1) / 3.0 - 0.02

    for obj in created_objs:
        if obj.type not in ("MESH", "CURVE", "SURFACE"):
            continue
        ev = obj.evaluated_get(depsgraph)
        me = ev.to_mesh()
        if me is None or len(me.polygons) == 0:
            if me:
                ev.to_mesh_clear()
            continue
        is_leaf = ("leaf" in obj.name.lower() or "leaves" in obj.name.lower() or obj.type == "MESH")
        mw = obj.matrix_world
        vmap = [bm.verts.new(mw @ v.co) for v in me.vertices]
        for poly in me.polygons:
            p_verts = [vmap[vi] for vi in poly.vertices]
            if len(p_verts) < 3:
                continue
            try:
                f = bm.faces.new(p_verts)
            except ValueError:
                continue
            f.material_index = 1 if is_leaf else 0
            f.smooth = True
            if is_leaf:
                uvs = [(lu0, lv0), (lu1, lv0), (lu1, lv1), (lu0, lv1)]
                for li, loop in enumerate(f.loops):
                    loop[uv_layer].uv = uvs[li % 4]
            else:
                for loop in f.loops:
                    loop[uv_layer].uv = (0.5 * (u0_c + u1_c), 0.5 * (v0_c + v1_c))
        ev.to_mesh_clear()

        # Cleanup temp objects & reset 3D cursor to world origin!
    bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
    for obj in created_objs + [t_obj]:
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data and data.users == 0:
            if isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)
            elif isinstance(data, bpy.types.Curve):
                bpy.data.curves.remove(data)


# ==============================================================================
# 3) HERO-ASSET A: HERO_ZIGGURAT_UR (22x18 m Basis, 3 begehbare Stufen, 4-Wege-Torhaus)
# ==============================================================================

def add_ziggurat_staircase(bm, uv_layer, p0, p1, width, steps, lod, wall_region="brick_terracotta",
                           step_region="travertine", balustrade_h=0.95, foundation_z=-0.35,
                           bal_left=True, bal_right=True, add_foot_posts=True, bal_t=0.38):
    """Massive, sauber gemauerte Ziggurat-Treppe OHNE Orgelpfeifen:
    - Durchgehender gemauerter Treppenkoerper (0 vertikale Streifen!)
    - Gleichmaessige Stufen mit Travertin-Auftritt (Steigung ~0.24-0.26m, Auftritt ~0.35-0.42m)
    - Glatte, schraeg abgedeckte seitliche Treppen-Wangen/Bruestungen (~0.95m hoch)
    """
    v0 = Vector(p0)
    v1 = Vector(p1)
    d = v1 - v0
    horiz = Vector((d.x, d.y, 0.0))
    length = horiz.length
    if length < 0.1:
        return
    fwd = horiz.normalized()
    right = Vector((-fwd.y, fwd.x, 0.0))
    z_bot = foundation_z if v0.z < 0.5 else v0.z - 0.18

    bal_l_w = bal_t if bal_left else 0.0
    bal_r_w = bal_t if bal_right else 0.0
    w_inner = max(0.8, width - bal_l_w - bal_r_w)
    # Shift inner stair center if asymmetric balustrades
    inner_shift = 0.5 * (bal_l_w - bal_r_w)

    def _add_sloped_wall(c0_xy, c1_xy, z_b0, z_b1, z_t0, z_t1, wall_w, reg, top_reg="travertine"):
        hr = right * (wall_w * 0.5)
        p00 = Vector((c0_xy.x, c0_xy.y, 0.0)) - hr
        p01 = Vector((c0_xy.x, c0_xy.y, 0.0)) + hr
        p11 = Vector((c1_xy.x, c1_xy.y, 0.0)) + hr
        p10 = Vector((c1_xy.x, c1_xy.y, 0.0)) - hr
        vb = [
            bm.verts.new((p00.x, p00.y, z_b0)),
            bm.verts.new((p01.x, p01.y, z_b0)),
            bm.verts.new((p11.x, p11.y, z_b1)),
            bm.verts.new((p10.x, p10.y, z_b1)),
        ]
        vt = [
            bm.verts.new((p00.x, p00.y, z_t0)),
            bm.verts.new((p01.x, p01.y, z_t0)),
            bm.verts.new((p11.x, p11.y, z_t1)),
            bm.verts.new((p10.x, p10.y, z_t1)),
        ]
        faces = []
        for i in range(4):
            j = (i + 1) % 4
            f = bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
            f.normal_update()
            _map_face_uv(f, uv_layer, reg, u_scale=0.18)
            faces.append(f)
        ft = bm.faces.new(vt)
        ft.normal_update()
        _map_face_uv(ft, uv_layer, top_reg, u_scale=0.22)
        faces.append(ft)
        fb = bm.faces.new((vb[3], vb[2], vb[1], vb[0]))
        fb.normal_update()
        _map_face_uv(fb, uv_layer, reg, u_scale=0.18)
        faces.append(fb)
        c_mid = sum((v.co for v in vb + vt), Vector((0.0, 0.0, 0.0))) / 8.0
        for f in faces:
            f.normal_update()
            if (f.calc_center_median() - c_mid).dot(f.normal) < 0.0:
                f.normal_flip()

    def _add_oriented_box(center_xy, zb, zt, len_fwd, len_right, reg, top_reg=None):
        hf = fwd * (len_fwd * 0.5)
        hr = right * (len_right * 0.5)
        c = Vector((center_xy.x, center_xy.y, 0.0))
        pts = [c - hf - hr, c + hf - hr, c + hf + hr, c - hf + hr]
        vb = [bm.verts.new((p.x, p.y, zb)) for p in pts]
        vt = [bm.verts.new((p.x, p.y, zt)) for p in pts]
        faces = []
        for i in range(4):
            j = (i + 1) % 4
            f = bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
            f.normal_update()
            _map_face_uv(f, uv_layer, reg, u_scale=0.24)
            faces.append(f)
        ft = bm.faces.new(vt)
        ft.normal_update()
        _map_face_uv(ft, uv_layer, top_reg or reg, u_scale=0.24)
        faces.append(ft)
        fb = bm.faces.new((vb[3], vb[2], vb[1], vb[0]))
        fb.normal_update()
        _map_face_uv(fb, uv_layer, reg, u_scale=0.24)
        faces.append(fb)
        c_mid = Vector((c.x, c.y, 0.5 * (zb + zt)))
        for f in faces:
            f.normal_update()
            if (f.calc_center_median() - c_mid).dot(f.normal) < 0.0:
                f.normal_flip()

    p0_in = Vector((v0.x, v0.y, 0.0)) + right * inner_shift
    p1_in = Vector((v1.x, v1.y, 0.0)) + right * inner_shift

    # 1) Solid continuous masonry stair underbody (tucked cleanly below step line -> 0 coplanar intersection!)
    n_steps = steps if lod <= 1 else max(4, steps // 3)
    step_len = length / n_steps
    dz = (v1.z - v0.z) / n_steps
    _add_sloped_wall(p0_in + fwd * (step_len * 0.35), p1_in - fwd * 0.04,
                     z_bot, z_bot, v0.z + dz * 0.35, v1.z - dz * 0.85,
                     w_inner - 0.01, wall_region, top_reg=wall_region)

    # 2) Crisp uniform individual steps on top of the solid ramp
    for s in range(n_steps):
        t0 = s / n_steps
        t_mid = (s + 0.5) / n_steps
        c_xy = p0_in + fwd * (t_mid * length)
        # Top step sits 2mm below landing slab to prevent any coplanar seam at portal threshold
        z_top = v0.z + (s + 1) * dz - (0.002 if s == n_steps - 1 else 0.0)
        z_step_bot = z_bot if s <= 1 else max(z_bot, v0.z + (s - 0.6) * dz)
        _add_oriented_box(c_xy, z_step_bot, z_top, step_len * 0.995, w_inner, wall_region, top_reg=step_region)
        # Subtle travertine tread lip on LOD0
        if lod == 0:
            c_lip = p0_in + fwd * (t0 * length + step_len * 0.48)
            _add_oriented_box(c_lip, z_top - 0.055, z_top + 0.003, step_len * 0.998, w_inner + 0.016, step_region, top_reg=step_region)

    # 3) Smooth sloped flanking balustrades (Treppen-Wangen) with thin sloped travertine coping cap!
    for do_bal, side in ((bal_left, -1.0), (bal_right, +1.0)):
        if not do_bal:
            continue
        lat = right * (inner_shift + side * (w_inner * 0.5 + bal_t * 0.5))
        b0 = Vector((v0.x, v0.y, 0.0)) + lat
        b1 = Vector((v1.x, v1.y, 0.0)) + lat
        z_t0 = v0.z + balustrade_h
        z_t1 = v1.z + balustrade_h
        # Main continuous brick cheek wall (NO organ pipes, pure terracotta/sand brick!)
        _add_sloped_wall(b0, b1, z_bot, z_bot, z_t0 - 0.09, z_t1 - 0.09, bal_t, wall_region, top_reg="travertine")
        # Thin crisp sloped travertine coping cap (0.11m thick along the slope!)
        cap_w = bal_t + (0.06 if lod == 0 else 0.02)
        _add_sloped_wall(b0 - fwd * 0.03, b1 + fwd * 0.03, z_t0 - 0.09, z_t1 - 0.09, z_t0 + 0.02, z_t1 + 0.02, cap_w, "travertine", top_reg="travertine")
        # Subtle pilaster buttress ribs along tall exterior balustrades on LOD0 (lower stairs only)
        if lod == 0 and v0.z < 0.5:
            for frac in (0.33, 0.66):
                rib_xy = b0.lerp(b1, frac) + right * (side * (bal_t * 0.5 + 0.06))
                z_rib_top = v0.z + frac * (v1.z - v0.z) + balustrade_h - 0.14
                _add_oriented_box(rib_xy, z_bot, z_rib_top, 0.34, 0.14, wall_region, top_reg="travertine")
        # Clean newel end-post at stair foot
        if add_foot_posts:
            c_foot = b0 - fwd * 0.24
            post_w = bal_t + 0.16
            _add_oriented_box(c_foot, z_bot, z_t0 + 0.16, post_w, post_w, wall_region, top_reg="travertine")
            if lod <= 1:
                _add_oriented_box(c_foot, z_t0 + 0.16, z_t0 + 0.25, post_w + 0.06, post_w + 0.06, "travertine", top_reg="lapis_brick")


def add_frieze_with_front_opening(bm, uv_layer, cx, cy, z0, z1, wx, wy, thickness, region,
                                  u_scale=0.38, gap_x0=None, gap_x1=None):
    """Umlaufendes Lapislazuli-Rosetten-Fries, das an Treppen-Austritten (+Y) sauber unterbrochen ist."""
    hx, hy = wx * 0.5, wy * 0.5
    # Back (-Y)
    add_box(bm, uv_layer, cx, cy - hy + thickness * 0.5, z0, z1, wx, thickness, region, u_scale=u_scale, top_region="travertine")
    # Left (-X) & Right (+X)
    add_box(bm, uv_layer, cx - hx + thickness * 0.5, cy, z0, z1, thickness, wy - thickness * 2.0, region, u_scale=u_scale, top_region="travertine")
    add_box(bm, uv_layer, cx + hx - thickness * 0.5, cy, z0, z1, thickness, wy - thickness * 2.0, region, u_scale=u_scale, top_region="travertine")
    # Front (+Y) with clean gap [gap_x0 .. gap_x1]
    if gap_x0 is not None and gap_x1 is not None and gap_x1 > gap_x0:
        lx0, lx1 = cx - hx, max(cx - hx, gap_x0)
        rx0, rx1 = min(cx + hx, gap_x1), cx + hx
        if lx1 - lx0 > 0.15:
            add_box(bm, uv_layer, 0.5 * (lx0 + lx1), cy + hy - thickness * 0.5, z0, z1, lx1 - lx0, thickness, region, u_scale=u_scale, top_region="travertine")
        if rx1 - rx0 > 0.15:
            add_box(bm, uv_layer, 0.5 * (rx0 + rx1), cy + hy - thickness * 0.5, z0, z1, rx1 - rx0, thickness, region, u_scale=u_scale, top_region="travertine")
    else:
        add_box(bm, uv_layer, cx, cy + hy - thickness * 0.5, z0, z1, wx, thickness, region, u_scale=u_scale, top_region="travertine")


def add_ziggurat_parapet(bm, uv_layer, cx, cy, z_deck, wx, wy, wall_t, h_wall, region,
                         merlons=True, merlon_h=0.26, cap_region="travertine",
                         gap_x0=None, gap_x1=None, add_gap_piers=True):
    """Umlaufende Zinnenbruestung mit exaktem Front-Durchbruch [gap_x0..gap_x1] + flankierenden Tor-Pfeilern (0 Coplanar!)."""
    hx, hy = wx * 0.5, wy * 0.5
    # Back (-Y)
    add_box(bm, uv_layer, cx, cy - hy + wall_t * 0.5, z_deck, z_deck + h_wall, wx, wall_t, region, top_region=cap_region)
    # Left (-X) & Right (+X)
    add_box(bm, uv_layer, cx - hx + wall_t * 0.5, cy, z_deck, z_deck + h_wall, wall_t, wy - wall_t * 2.0, region, top_region=cap_region)
    add_box(bm, uv_layer, cx + hx - wall_t * 0.5, cy, z_deck, z_deck + h_wall, wall_t, wy - wall_t * 2.0, region, top_region=cap_region)

    # Front (+Y) with exact opening
    has_gap = (gap_x0 is not None and gap_x1 is not None and gap_x1 > gap_x0)
    if has_gap:
        lx0, lx1 = cx - hx, max(cx - hx, gap_x0)
        rx0, rx1 = min(cx + hx, gap_x1), cx + hx
        if lx1 - lx0 > 0.2:
            add_box(bm, uv_layer, 0.5 * (lx0 + lx1), cy + hy - wall_t * 0.5, z_deck, z_deck + h_wall, lx1 - lx0, wall_t, region, top_region=cap_region)
        if rx1 - rx0 > 0.2:
            add_box(bm, uv_layer, 0.5 * (rx0 + rx1), cy + hy - wall_t * 0.5, z_deck, z_deck + h_wall, rx1 - rx0, wall_t, region, top_region=cap_region)
        if add_gap_piers:
            pw = wall_t + 0.14
            for px in (gap_x0 - pw * 0.42, gap_x1 + pw * 0.42):
                add_box(bm, uv_layer, px, cy + hy - wall_t * 0.5, z_deck, z_deck + h_wall + merlon_h + 0.16, pw, pw, region, top_region=cap_region)
                add_box(bm, uv_layer, px, cy + hy - wall_t * 0.5, z_deck + h_wall + merlon_h + 0.16, z_deck + h_wall + merlon_h + 0.24, pw + 0.06, pw + 0.06, "travertine", top_region="lapis_brick")
    else:
        add_box(bm, uv_layer, cx, cy + hy - wall_t * 0.5, z_deck, z_deck + h_wall, wx, wall_t, region, top_region=cap_region)

    if merlons:
        step = 1.05
        m_w = 0.50
        m_t = wall_t * 0.88
        z_m0 = z_deck + h_wall + 0.003
        z_m1 = z_m0 + merlon_h
        nx = max(2, int(wx / step))
        for i in range(nx):
            mx = cx - hx + 0.45 + i * ((wx - 0.90) / max(1, nx - 1))
            add_box(bm, uv_layer, mx, cy - hy + wall_t * 0.5, z_m0, z_m1, m_w, m_t, region, top_region=cap_region)
            if not has_gap or (mx < gap_x0 - 0.65 or mx > gap_x1 + 0.65):
                add_box(bm, uv_layer, mx, cy + hy - wall_t * 0.5, z_m0, z_m1, m_w, m_t, region, top_region=cap_region)
        ny = max(2, int(wy / step))
        for j in range(1, ny - 1):
            my = cy - hy + 0.45 + j * ((wy - 0.90) / max(1, ny - 1))
            add_box(bm, uv_layer, cx - hx + wall_t * 0.5, my, z_m0, z_m1, m_t, m_w, region, top_region=cap_region)
            add_box(bm, uv_layer, cx + hx - wall_t * 0.5, my, z_m0, z_m1, m_t, m_w, region, top_region=cap_region)


def _add_tube_segment(bm, uv_layer, p0, p1, r0, r1, segs, region="cedar_wood", mat_idx=0):
    d = p1 - p0
    if d.length < 1e-4:
        return
    z_ax = d.normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(z_ax.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    x_ax = z_ax.cross(ref).normalized()
    y_ax = z_ax.cross(x_ax).normalized()
    ring0, ring1 = [], []
    for i in range(segs):
        a = 2.0 * math.pi * i / segs
        ca, sa = math.cos(a), math.sin(a)
        dir_r = x_ax * ca + y_ax * sa
        ring0.append(bm.verts.new(p0 + dir_r * r0))
        ring1.append(bm.verts.new(p1 + dir_r * r1))
    u0, v0, u1, v1 = TEMENOS_TRIM_REGIONS[region]
    uc, vc = 0.5 * (u0 + u1), 0.5 * (v0 + v1)
    for i in range(segs):
        j = (i + 1) % segs
        f = bm.faces.new((ring0[i], ring0[j], ring1[j], ring1[i]))
        f.material_index = mat_idx
        f.smooth = True
        for loop in f.loops:
            loop[uv_layer].uv = (uc, vc)


def _add_small_leaf_blade(bm, uv_layer, origin, direction, normal_hint, size_w, size_l, cell_name="ivy", mat_idx=1):
    """Einzelnes feines, leicht gewoelbtes Blatt (0.08..0.15m) statt plumper Knet-Zungen."""
    col, row = BOTANY_CELLS[cell_name]
    u0, u1 = col / 3.0 + 0.04, (col + 1) / 3.0 - 0.04
    v0, v1 = row / 3.0 + 0.04, (row + 1) / 3.0 - 0.04
    fwd = direction.normalized()
    side = fwd.cross(normal_hint)
    if side.length < 1e-4:
        side = fwd.cross(Vector((0.0, 0.0, 1.0)))
    side.normalize()
    up = side.cross(fwd).normalized()
    p0 = origin
    p1 = origin + fwd * (size_l * 0.45) - side * (size_w * 0.5) + up * (size_l * 0.08)
    p2 = origin + fwd * size_l - up * (size_l * 0.06)
    p3 = origin + fwd * (size_l * 0.45) + side * (size_w * 0.5) + up * (size_l * 0.08)
    verts = [bm.verts.new(p) for p in (p0, p1, p2, p3)]
    f = bm.faces.new(verts)
    f.material_index = mat_idx
    f.smooth = True
    for loop, uv in zip(f.loops, [(0.5 * (u0 + u1), v0), (u0, 0.5 * (v0 + v1)), (0.5 * (u0 + u1), v1), (u1, 0.5 * (v0 + v1))]):
        loop[uv_layer].uv = uv


def add_fine_trailing_vine(bm, uv_layer, start_pt, out_normal, length=1.55, seed=0, lod=0):
    """Feine, kleinteilig verzweigte Blattranken (duenne Holz-Triebe + viele echte kleine Blaetter)."""
    if lod >= 2:
        return
    rng = random.Random(seed)
    n_out = Vector(out_normal).normalized()
    tangent = Vector((-n_out.y, n_out.x, 0.0)).normalized()
    n_stems = 4 if lod == 0 else 1
    segs = 5 if lod == 0 else 3

    for si in range(n_stems):
        cur = Vector(start_pt) + tangent * rng.uniform(-0.36, 0.36) + n_out * 0.04
        stem_len = length * rng.uniform(0.65, 1.12)
        n_steps = 8 if lod == 0 else 4
        step_dz = stem_len / n_steps
        rad = 0.016
        for k in range(n_steps):
            # First step arches slightly out over parapet edge, then drapes close to wall
            out_step = (0.08 if k == 0 else rng.uniform(-0.012, 0.018))
            nxt = cur + Vector((0.0, 0.0, -step_dz)) + tangent * rng.uniform(-0.09, 0.09) + n_out * out_step
            r_next = max(0.005, rad * 0.84)
            _add_tube_segment(bm, uv_layer, cur, nxt, rad, r_next, segs, region="cedar_wood", mat_idx=0)
            # Small branched side-twigs + clusters of tiny leaves
            n_leaves = 5 if lod == 0 else 2
            for li in range(n_leaves):
                frac = (li + 0.5) / n_leaves
                lp = cur.lerp(nxt, frac)
                s_dir = (tangent * rng.uniform(-1.0, 1.0) + n_out * rng.uniform(0.35, 0.95) + Vector((0.0, 0.0, rng.uniform(-0.85, -0.15)))).normalized()
                lw = rng.uniform(0.09, 0.14)
                ll = rng.uniform(0.11, 0.17)
                _add_small_leaf_blade(bm, uv_layer, lp, s_dir, n_out, lw, ll, cell_name="ivy", mat_idx=1)
            # Occasional delicate side shoot on LOD0
            if lod == 0 and k in (2, 4):
                side_sgn = 1.0 if (si + k) % 2 == 0 else -1.0
                branch_end = nxt + tangent * (side_sgn * rng.uniform(0.18, 0.30)) + Vector((0.0, 0.0, -0.22)) + n_out * 0.03
                _add_tube_segment(bm, uv_layer, nxt, branch_end, r_next, 0.005, 3, region="cedar_wood", mat_idx=0)
                for bf in (0.35, 0.70, 1.0):
                    bp = nxt.lerp(branch_end, bf)
                    b_dir = (tangent * side_sgn * 0.6 + n_out * 0.7 + Vector((0.0, 0.0, -0.5))).normalized()
                    _add_small_leaf_blade(bm, uv_layer, bp, b_dir, n_out, 0.10, 0.13, cell_name="ivy", mat_idx=1)
            cur = nxt
            rad = r_next


def add_fine_terrace_shrub(bm, uv_layer, cx, cy, z_soil, radius, height, cell_name, seed=0, lod=0):
    """Ueppiger, fein beblaetterter Terrassen-Strauch mit holzigen Zweigen + gestaffelten Laubfaechern."""
    rng = random.Random(seed)
    n_branches = 6 if lod == 0 else 3
    for i in range(n_branches):
        ang = (i / max(1, n_branches)) * 2.0 * math.pi + rng.uniform(-0.35, 0.35)
        r_top = radius * rng.uniform(0.38, 0.78)
        h_top = height * rng.uniform(0.55, 0.95)
        p0 = Vector((cx + math.cos(ang) * 0.08, cy + math.sin(ang) * 0.08, z_soil - 0.02))
        p1 = Vector((cx + math.cos(ang) * r_top, cy + math.sin(ang) * r_top, z_soil + h_top * 0.78))
        if lod == 0:
            _add_tube_segment(bm, uv_layer, p0, p1, 0.022, 0.009, 4, region="cedar_wood", mat_idx=0)
        # Layered foliage sprays along branch
        add_botany_card(bm, uv_layer, (p0.x, p0.y, z_soil - 0.02), radius * rng.uniform(0.68, 0.98),
                        h_top * rng.uniform(0.85, 1.12), ang, rng.uniform(0.22, 0.52), cell_name, bend=0.18, segs_v=2)
        if lod == 0:
            add_botany_card(bm, uv_layer, (p1.x, p1.y, p1.z - 0.12), radius * 0.56,
                            h_top * 0.58, ang + rng.uniform(-0.5, 0.5), rng.uniform(0.35, 0.68), cell_name, bend=0.16, segs_v=2)


def build_hero_ziggurat_ur(bm, uv_layer, lod):
    # ==========================================================================
    # EXAKTER ARCHITEKTUR-KANON (Nach hinten um +6.50 m verlaengert, 100% symmetrische Axial-Treppen!)
    #   Vorderkante 100% fixiert: Mitteltreppe Antritt Y = +13.80 m, Torhaus Y = +7.825 m, Stufe-1-Front Y = +6.55 m
    #   Stufe 1: Z = 0.00 -> 3.50 m  (Kern X = -11.0..+11.0, Y = -15.50..+6.55 m -> 22.0 x 22.05 m)
    #   4-Wege-Torhaus: Zentrum (0, +7.825), 4 freie Portale >= 2.45m breit x 2.95m hoch!
    #   Seitentreppen 1L & 1R: X = +-8.50 -> +-2.20 m @ Y = +7.825 m (100% symmetrisch, 0 Eck-Klotz!)
    #   Podest Stufe 1 hinter Torhaus: Y = +2.90 .. +6.10 m (3.20 m tief >= 3.0 m!)
    #   Axial-Treppe 2 (X = 0): Y = +2.90 -> -0.40 m, Z = 3.50 -> 6.25 m (11 Stufen, kerzengerade!)
    #   Stufe 2: Z = 3.50 -> 6.25 m  (X = -7.80..+7.80, Y = -14.20..-0.10 m, Top Y = -13.90..-0.40 m)
    #   Podest Stufe 2 vor Treppe 3: Y = -0.40 .. -3.00 m (2.60 m tief >= 2.5 m!)
    #   Axial-Treppe 3 (X = 0): Y = -3.00 -> -6.00 m, Z = 6.25 -> 8.75 m (10 Stufen, kerzengerade!)
    #   Stufe 3: Z = 6.25 -> 8.75 m  (X = -5.20..+5.20, Y = -12.85..-5.75 m, Top Y = -12.60..-6.00 m)
    #   Gipfel-Vorplatz vor Schrein: Y = -6.00 .. -8.75 m (2.75 m tief >= 2.5 m!)
    #   E-Nanna-Schrein: Z = 8.75 -> 13.20 m (Y = -11.35..-8.75 m, Stufenportal 2.75m hoch x 1.72m breit!)
    # ==========================================================================

    Z1 = 3.50
    Z2 = 6.25
    Z3 = 8.75

    # --- LOD3 DISTANT SILHOUETTE ---
    if lod == 3:
        add_prism(bm, uv_layer, 0.0, -4.475, -0.35, Z1, 22.0, 22.05, 21.0, 21.45, "brick_terracotta", top_region="travertine")
        add_prism(bm, uv_layer, 0.0, -7.15, Z1, Z2, 15.6, 14.1, 15.0, 13.5, "brick_sand", top_region="travertine")
        add_prism(bm, uv_layer, 0.0, -9.30, Z2, Z3, 10.4, 7.1, 10.0, 6.6, "brick_terracotta", top_region="travertine")
        add_prism(bm, uv_layer, 0.0, -10.05, Z3, 13.15, 5.5, 2.6, 5.36, 2.5, "travertine", top_region="lapis_rosette_frieze")
        add_prism(bm, uv_layer, 0.0, 10.4, -0.35, Z1, 3.2, 4.8, 2.8, 2.4, "brick_terracotta")
        add_prism(bm, uv_layer, 0.0, 7.82, Z1, Z1 + 3.55, 4.4, 3.45, 4.4, 3.45, "brick_terracotta", top_region="lapis_rosette_frieze")
        return

    # ==========================================================================
    # 1) STUFE 1 (Z = -0.35 .. +3.50 m, nach hinten verlaengert auf Y = -15.50 .. +6.55 m!)
    #    100% freie, symmetrische Front ohne abgeschnittene Eck-Kloetze am Seitentreppen-Antritt!
    # ==========================================================================
    c1_y = -4.475
    w1_x0, w1_y0 = 22.00, 22.05  # Y: -15.50 .. +6.55
    w1_x1, w1_y1 = 21.00, 21.45  # Y: -15.20 .. +6.25
    # Continuous travertine foundation plinth (-0.35 .. +0.35 m) fitted cleanly around Tier 1 core
    add_prism(bm, uv_layer, 0.0, c1_y, -0.35, 0.35, w1_x0 + 0.50, w1_y0 + 0.50, w1_x0 + 0.20, w1_y0 + 0.20, "travertine", u_scale=0.16)
    # Main Tier 1 core
    add_prism(bm, uv_layer, 0.0, c1_y, 0.35, Z1, w1_x0, w1_y0, w1_x1, w1_y1, "brick_terracotta", u_scale=0.14, top_region="travertine")

    # Rhythmic pilasters & drainage channels on Tier 1 exterior walls (skipping lateral stair zone on +Y)
    add_pilaster_and_niche_facade(bm, uv_layer, 0.0, c1_y, 0.35, Z1 - 0.05, w1_x0, w1_y0, w1_x1, w1_y1,
                                  n_x=(9 if lod == 0 else 6), n_y=(8 if lod == 0 else 5),
                                  region="brick_terracotta", lod=lod, skip_front_x=8.8, add_drains=True)
    # Tier 1 Lapis Rosette Frieze (cleanly open across Gatehouse Back Portal X = -2.30 .. +2.30!)
    add_frieze_with_front_opening(bm, uv_layer, 0.0, c1_y, Z1 - 0.32, Z1 - 0.02, w1_x1 + 0.14, w1_y1 + 0.14, 0.14,
                                  "lapis_rosette_frieze", u_scale=0.35, gap_x0=-2.30, gap_x1=+2.30)
    # Tier 1 Parapet + Merlons (cleanly open across Gatehouse Back Portal X = -2.25 .. +2.25!)
    add_ziggurat_parapet(bm, uv_layer, 0.0, c1_y, Z1, w1_x1, w1_y1, 0.44, 0.56, "brick_terracotta",
                         merlons=(lod <= 1), merlon_h=0.26, gap_x0=-2.25, gap_x1=+2.25, add_gap_piers=False)

    # ==========================================================================
    # 2) SYMMETRISCHE DREIFACH-TREPPE + ECHTES 4-WEGE-TORHAUS (STUFE 1)
    # ==========================================================================
    # Gatehouse center: (0.0, +7.825), Z_floor = 3.50 m
    # 4 Corner Piers:
    #   X: [-2.20 .. -1.35] and [+1.35 .. +2.20] -> Front/Back clear width = 2.70 m (>= 2.4 m!)
    #   Y: Back [+6.10 .. +6.60], Front [+9.05 .. +9.55] -> Left/Right clear width = 2.45 m (>= 2.4 m!)
    #   Clear Passage Height (all 4 portals): Z = 3.50 .. 6.45 m = 2.95 m (>= 2.8 m!)
    gh_cy = 7.825
    gh_clear_h = 2.95
    gh_lintel_z0 = Z1 + gh_clear_h      # 6.45 m
    gh_lintel_z1 = gh_lintel_z0 + 0.65  # 7.10 m

    # Solid masonry landing platform beneath Gatehouse (Y = +6.252 .. +9.55 m, Z = -0.35 .. +3.50 m -> 0 coplanar overlap with Tier 1!)
    add_prism(bm, uv_layer, 0.0, 7.90, -0.35, Z1, 4.56, 3.00, 4.44, 3.296, "brick_terracotta", u_scale=0.18, top_region="travertine")

    # 4 Corner Piers (NO closed side walls — all 4 directions wide open!)
    for sx in (-1.0, 1.0):
        for sy, py_c in ((-1.0, 6.35), (+1.0, 9.30)):
            px_c = sx * 1.775
            add_box(bm, uv_layer, px_c, py_c, Z1, gh_lintel_z0, 0.85, 0.50, "brick_terracotta", u_scale=0.22, top_region="travertine")
            # Stepped architectural pier pilaster reveal on exterior face (LOD0/1)
            if lod <= 1:
                add_box(bm, uv_layer, px_c, py_c + sy * 0.28, Z1, gh_lintel_z0, 0.46, 0.10, "brick_sand", u_scale=0.26)
                add_box(bm, uv_layer, px_c + sx * 0.45, py_c, Z1, gh_lintel_z0, 0.10, 0.34, "brick_sand", u_scale=0.26)
                # Travertine plinth base & capital collar on each pier
                add_box(bm, uv_layer, px_c, py_c, Z1, Z1 + 0.24, 0.92, 0.56, "travertine")
                add_box(bm, uv_layer, px_c, py_c, gh_lintel_z0 - 0.16, gh_lintel_z0, 0.92, 0.56, "travertine")

    # Exposed cedarwood ceiling rafters inside the 4-way gatehouse (LOD0 — visible when looking up!)
    if lod == 0:
        for rx in (-1.05, -0.52, 0.0, +0.52, +1.05):
            add_box(bm, uv_layer, rx, gh_cy, gh_lintel_z0 - 0.14, gh_lintel_z0, 0.14, 3.20, "cedar_wood", u_scale=0.35)
        for ry in (6.95, 7.825, 8.70):
            add_box(bm, uv_layer, 0.0, ry, gh_lintel_z0 - 0.08, gh_lintel_z0, 4.10, 0.16, "cedar_wood", u_scale=0.35)

    # Continuous Gatehouse Entablature / Roof Block (cleanly starts at gh_lintel_z0 -> 0 coplanar overlap, 0 black gaps!)
    add_box(bm, uv_layer, 0.0, gh_cy, gh_lintel_z0, gh_lintel_z1, 4.50, 3.56, "brick_terracotta", u_scale=0.22, top_region="travertine")
    # Wraparound Lapis Rosette Frieze on Gatehouse Crown (proud by 0.05m -> 0 Z-fighting!)
    add_frieze_with_front_opening(bm, uv_layer, 0.0, gh_cy, gh_lintel_z0 + 0.26, gh_lintel_z1 - 0.04, 4.62, 3.68, 0.10,
                                  "lapis_rosette_frieze", u_scale=0.48)
    # Gatehouse Roof Parapet + Merlons (cleanly sits at gh_lintel_z1 -> solid travertine roof deck!)
    add_ziggurat_parapet(bm, uv_layer, 0.0, gh_cy, gh_lintel_z1, 4.46, 3.52, 0.30, 0.32, "brick_terracotta",
                         merlons=(lod <= 1), merlon_h=0.20, cap_region="travertine")

    # Central Main Staircase (Stair 1C): Y = +13.80 -> +9.552 m (4.25m run, 14 steps: Rise 0.250m, Tread 0.304m!)
    # Foot at Y=+13.80m aligns millimeter-precisely onto the processional paving slab; top meets Gatehouse front portal threshold!
    add_ziggurat_staircase(bm, uv_layer, (0.0, 13.80, 0.0), (0.0, 9.552, Z1),
                           width=3.26, steps=14, lod=lod, wall_region="brick_terracotta",
                           step_region="travertine", balustrade_h=0.95, foundation_z=-0.35)

    # Left & Right Lateral Staircases (Stair 1L & 1R): X = +-8.50 -> +-2.222 m @ Y = +7.825 m!
    # 6.28m run, 15 steps: Rise 0.233m, Tread 0.418m — 100% mirror-symmetric, open foot on courtyard floor,
    # both inner and outer sloped balustrades cleanly framing the ascent into the 2.45m-wide side portals!
    add_ziggurat_staircase(bm, uv_layer, (-8.50, gh_cy, 0.0), (-2.222, gh_cy, Z1),
                           width=2.64, steps=15, lod=lod, wall_region="brick_terracotta",
                           step_region="travertine", balustrade_h=0.92, foundation_z=-0.35,
                           bal_left=True, bal_right=True, add_foot_posts=True, bal_t=0.34)
    add_ziggurat_staircase(bm, uv_layer, (+8.50, gh_cy, 0.0), (+2.222, gh_cy, Z1),
                           width=2.64, steps=15, lod=lod, wall_region="brick_terracotta",
                           step_region="travertine", balustrade_h=0.92, foundation_z=-0.35,
                           bal_left=True, bal_right=True, add_foot_posts=True, bal_t=0.34)

    # ==========================================================================
    # 3) STUFE 2 (Z = 3.50 .. 6.25 m) + FREIES PODEST (3.20 m) + AXIAL-TREPPE 2 (X = 0)
    # ==========================================================================
    # Tier 1 Front Podest behind Gatehouse: Y = +2.90 .. +6.10 m = 3.20 m deep (>= 3.0 m!)
    # Tier 2 Core: X = -7.80..+7.80 (top +-7.50), Y = -14.20..-0.10 (top -13.90..-0.40)
    c2_y = -7.15
    w2_x0, w2_y0 = 15.60, 14.10
    w2_x1, w2_y1 = 15.00, 13.50
    add_prism(bm, uv_layer, 0.0, c2_y, Z1, Z2, w2_x0, w2_y0, w2_x1, w2_y1, "brick_sand", u_scale=0.16, top_region="travertine")

    # Pilasters & drainage channels on ALL 4 Tier 2 exterior walls (skipping only centered Axial Stair 2 X = -1.65..+1.65 on +Y!)
    add_pilaster_and_niche_facade(bm, uv_layer, 0.0, c2_y, Z1, Z2 - 0.05, w2_x0, w2_y0, w2_x1, w2_y1,
                                  n_x=(7 if lod == 0 else 5), n_y=(6 if lod == 0 else 4),
                                  region="brick_sand", lod=lod, skip_front_x=1.70, add_drains=True)

    # Tier 2 Lapis Rosette Frieze — CLEANLY OPEN across centered Axial Stair 2 exit (X = -1.28 .. +1.28)!
    add_frieze_with_front_opening(bm, uv_layer, 0.0, c2_y, Z2 - 0.30, Z2 - 0.02, w2_x1 + 0.14, w2_y1 + 0.14, 0.14,
                                  "lapis_rosette_frieze", u_scale=0.40, gap_x0=-1.32, gap_x1=+1.32)
    # Tier 2 Parapet + Merlons — CLEANLY OPEN across centered Axial Stair 2 exit (X = -1.28 .. +1.28) with 2 flanking gate-piers!
    add_ziggurat_parapet(bm, uv_layer, 0.0, c2_y, Z2, w2_x1, w2_y1, 0.38, 0.50, "brick_sand",
                         merlons=(lod <= 1), merlon_h=0.22, gap_x0=-1.28, gap_x1=+1.28, add_gap_piers=True)

    # Axial Stair 2 (Tier 1 -> Tier 2): Centered on main axis X = 0.0, climbing straight from Y = +2.90 to Y = -0.398 m!
    # 3.30m run, 11 steps (Rise 0.250m, Tread 0.300m), symmetric sloped balustrades on both left & right!
    add_ziggurat_staircase(bm, uv_layer, (0.0, +2.90, Z1), (0.0, -0.398, Z2),
                           width=2.56, steps=11, lod=lod, wall_region="brick_sand",
                           step_region="travertine", balustrade_h=0.76, foundation_z=Z1 - 0.18,
                           bal_left=True, bal_right=True, add_foot_posts=True, bal_t=0.36)

    # ==========================================================================
    # 4) STUFE 3 (Z = 6.25 .. 8.75 m) + PODEST STUFE 2 (2.60 m) + AXIAL-TREPPE 3 (X = 0)
    # ==========================================================================
    # Tier 2 Center Podest before Stair 3: Y = -0.40 .. -3.00 m = 2.60 m deep (>= 2.5 m!)
    # Tier 3 Core: X = -5.20..+5.20 (top +-5.00), Y = -12.85..-5.75 (top -12.60..-6.00)
    c3_y = -9.30
    w3_x0, w3_y0 = 10.40, 7.10
    w3_x1, w3_y1 = 10.00, 6.60
    add_prism(bm, uv_layer, 0.0, c3_y, Z2, Z3, w3_x0, w3_y0, w3_x1, w3_y1, "brick_terracotta", u_scale=0.18, top_region="travertine")

    # Pilasters on Tier 3 (skipping only centered Axial Stair 3 X = -1.55..+1.55 on +Y!)
    add_pilaster_and_niche_facade(bm, uv_layer, 0.0, c3_y, Z2, Z3 - 0.05, w3_x0, w3_y0, w3_x1, w3_y1,
                                  n_x=(5 if lod == 0 else 3), n_y=(4 if lod == 0 else 2),
                                  region="brick_terracotta", lod=lod, skip_front_x=1.55, add_drains=False)

    # Tier 3 Lapis Rosette Frieze — CLEANLY OPEN across centered Axial Stair 3 exit (X = -1.18 .. +1.18)!
    add_frieze_with_front_opening(bm, uv_layer, 0.0, c3_y, Z3 - 0.28, Z3 - 0.02, w3_x1 + 0.12, w3_y1 + 0.12, 0.12,
                                  "lapis_rosette_frieze", u_scale=0.45, gap_x0=-1.22, gap_x1=+1.22)
    # Tier 3 Parapet + Merlons — CLEANLY OPEN across centered Axial Stair 3 exit (X = -1.18 .. +1.18) with 2 flanking gate-piers!
    add_ziggurat_parapet(bm, uv_layer, 0.0, c3_y, Z3, w3_x1, w3_y1, 0.32, 0.44, "brick_terracotta",
                         merlons=(lod <= 1), merlon_h=0.20, gap_x0=-1.18, gap_x1=+1.18, add_gap_piers=True)

    # Axial Stair 3 (Tier 2 -> Tier 3): Centered on main axis X = 0.0, climbing straight from Y = -3.00 to Y = -5.998 m!
    # 3.00m run, 10 steps (Rise 0.250m, Tread 0.300m), symmetric sloped balustrades on both left & right!
    add_ziggurat_staircase(bm, uv_layer, (0.0, -3.00, Z2), (0.0, -5.998, Z3),
                           width=2.36, steps=10, lod=lod, wall_region="brick_terracotta",
                           step_region="travertine", balustrade_h=0.70, foundation_z=Z2 - 0.18,
                           bal_left=True, bal_right=True, add_foot_posts=True, bal_t=0.34)

    # ==========================================================================
    # 5) GIPFEL-PLATTFORM (2.75 m VORPLATZ) & E-NANNA-SCHREIN MIT TIEFEM STUFENPORTAL
    # ==========================================================================
    # Summit Platform: X = -5.00..+5.00, Y = -12.60..-6.00, Z = 8.75 m
    # Shrine footprint: X = -2.75..+2.75 (5.50m wide), Y = -11.35..-8.75 (2.60m deep)
    # Free Summit Forecourt (Vorplatz): Y = -6.00 .. -8.75 m = 2.75 m deep (>= 2.5 m!)
    # Circumferential walkway around Shrine: Sides 2.25 m, Rear 1.25 m!
    sh_cy = -10.05
    sh_y_front = -8.75
    sh_z0 = Z3 + 0.26     # 9.01 m (elevated temple podium)
    sh_z1 = Z3 + 3.70     # 12.45 m (main shrine walls -> tall enough for >= 2.75m portal!)

    # Elevated Travertine Temple Podium (Z = 8.75 .. 9.01 m) + 2 low entrance steps on +Y
    add_prism(bm, uv_layer, 0.0, sh_cy, Z3, sh_z0, 5.85, 2.90, 5.70, 2.76, "travertine", u_scale=0.25)
    # 2 gentle travertine entrance steps leading up to the portal threshold (projecting 0.36m -> 2.39m to step, 2.75m to facade!)
    add_box(bm, uv_layer, 0.0, sh_y_front + 0.18, Z3, Z3 + 0.13, 2.50, 0.36, "travertine", u_scale=0.30)
    add_box(bm, uv_layer, 0.0, sh_y_front + 0.09, Z3 + 0.13, sh_z0, 2.25, 0.18, "travertine", u_scale=0.30)

    # Main Shrine Body (built around a REAL 0.38m-deep recessed portal cavity on +Y!)
    # Rear solid core (Y = -11.35 .. -9.13 -> leaves Y = -9.13 .. -8.75 open for the deep recessed portal!)
    add_prism(bm, uv_layer, 0.0, -10.24, sh_z0, sh_z1, 5.50, 2.22, 5.36, 2.15, "brick_sand", u_scale=0.22, top_region="travertine")
    # Flanking Front Walls (Left X = -2.75..-1.25, Right X = +1.25..+2.75, Y = -9.13..-8.75)
    for sgn in (-1.0, 1.0):
        add_box(bm, uv_layer, sgn * 2.00, sh_y_front - 0.19, sh_z0, sh_z1, 1.50, 0.38, "brick_sand", u_scale=0.22, top_region="travertine")
    # Lintel Wall above Portal (Z = sh_z0 + 2.75 = 11.76 .. 12.45 m, X = -1.25..+1.25, Y = -9.13..-8.75)
    portal_h = 2.75   # >= 2.60 m clear height!
    portal_w = 1.72   # >= 1.60 m clear width!
    add_box(bm, uv_layer, 0.0, sh_y_front - 0.19, sh_z0 + portal_h, sh_z1, 2.50, 0.38, "brick_sand", u_scale=0.22, top_region="travertine")

    # Stepped Sumerian Rabbeted Niche Portal Frames (3 deep sculptural steps framing the 1.72m x 2.75m doorway!)
    # Outer Frame (Travertine): clear opening 2.24m x 2.95m
    for sgn in (-1.0, 1.0):
        add_box(bm, uv_layer, sgn * 1.24, sh_y_front - 0.02, sh_z0, sh_z0 + portal_h + 0.24, 0.24, 0.16, "travertine", u_scale=0.35)
    add_box(bm, uv_layer, 0.0, sh_y_front - 0.02, sh_z0 + portal_h + 0.12, sh_z0 + portal_h + 0.34, 2.72, 0.18, "travertine", u_scale=0.35)
    # Middle Frame (Glazed Lapis Brick): clear opening 1.98m x 2.85m
    for sgn in (-1.0, 1.0):
        add_box(bm, uv_layer, sgn * 1.09, sh_y_front - 0.14, sh_z0, sh_z0 + portal_h + 0.14, 0.20, 0.14, "lapis_brick", u_scale=0.45)
    add_box(bm, uv_layer, 0.0, sh_y_front - 0.14, sh_z0 + portal_h + 0.04, sh_z0 + portal_h + 0.20, 2.38, 0.16, "lapis_brick", u_scale=0.45)
    # Inner Frame (Travertine Jambs + Cedar Lintel): clear opening 1.72m x 2.75m!
    for sgn in (-1.0, 1.0):
        add_box(bm, uv_layer, sgn * 0.94, sh_y_front - 0.26, sh_z0, sh_z0 + portal_h, 0.16, 0.14, "travertine", u_scale=0.40)
    add_box(bm, uv_layer, 0.0, sh_y_front - 0.26, sh_z0 + portal_h - 0.04, sh_z0 + portal_h + 0.08, 2.04, 0.16, "cedar_wood", u_scale=0.40)

    # Dark Bronze-Studded Cedarwood Double Doors (recessed deep at Y = sh_y_front - 0.33 m!)
    for sgn in (-1.0, 1.0):
        # Twin door leaves with crisp center seam
        add_box(bm, uv_layer, sgn * 0.425, sh_y_front - 0.33, sh_z0, sh_z0 + portal_h - 0.04, 0.83, 0.08, "cedar_wood", u_scale=0.40)
        if lod <= 1:
            # Vertical timber stiles & bronze door-pull rings
            add_box(bm, uv_layer, sgn * 0.14, sh_y_front - 0.275, sh_z0 + 1.25, sh_z0 + 1.43, 0.12, 0.05, "tin_bronze")
            add_box(bm, uv_layer, sgn * 0.76, sh_y_front - 0.285, sh_z0 + 0.04, sh_z0 + portal_h - 0.08, 0.08, 0.03, "tin_bronze")
    # Horizontal hammered bronze reinforcement bands + boss studs across the cedar doors
    if lod <= 1:
        for dz_rel in (0.38, 1.05, 1.75, 2.38):
            add_box(bm, uv_layer, 0.0, sh_y_front - 0.285, sh_z0 + dz_rel, sh_z0 + dz_rel + 0.075, 1.66, 0.035, "tin_bronze")
            if lod == 0:
                for bx_stud in (-0.65, -0.35, +0.35, +0.65):
                    add_box(bm, uv_layer, bx_stud, sh_y_front - 0.26, sh_z0 + dz_rel + 0.015, sh_z0 + dz_rel + 0.06, 0.045, 0.025, "tin_bronze")

    # Pilasters on Shrine Side & Rear Walls
    add_pilaster_and_niche_facade(bm, uv_layer, 0.0, sh_cy, sh_z0, sh_z1 - 0.05, 5.50, 2.60, 5.36, 2.50,
                                  n_x=4, n_y=2, region="travertine", lod=lod, skip_front_x=1.65, add_drains=False)

    # Wraparound Lapis Lazuli + Golden Rosette Frieze + Crown Parapet on Shrine
    add_frieze_with_front_opening(bm, uv_layer, 0.0, sh_cy, sh_z1 - 0.25, sh_z1 + 0.35, 5.56, 2.72, 0.12,
                                  "lapis_rosette_frieze", u_scale=0.55)
    add_box(bm, uv_layer, 0.0, sh_cy, sh_z1, sh_z1 + 0.35, 5.44, 2.60, "lapis_brick", u_scale=0.35, top_region="travertine")
    add_ziggurat_parapet(bm, uv_layer, 0.0, sh_cy, sh_z1 + 0.35, 5.40, 2.56, 0.28, 0.26, "lapis_brick",
                         merlons=(lod <= 1), merlon_h=0.18, cap_region="lapis_brick")

    # Flanking Temple Standards + 2 Summit Bronze Fire Braziers with Prominent Glowing Embers!
    if lod <= 1:
        for sgn in (-1.0, 1.0):
            # Temple Standard pole + bronze crescent finial flanking Shrine facade
            add_cylinder(bm, uv_layer, sgn * 1.65, sh_y_front + 0.18, Z3, sh_z1 + 1.40, 0.055, 0.04, 8 if lod == 0 else 5, "cedar_wood")
            add_box(bm, uv_layer, sgn * 1.65, sh_y_front + 0.18, sh_z1 + 1.32, sh_z1 + 1.66, 0.44, 0.09, "tin_bronze")
            # Summit Bronze Brazier flanking the 2.75m forecourt (X = +-2.45, Y = -7.40 -> completely clear of axial approach!)
            bx, by = sgn * 2.45, -7.40
            add_prism(bm, uv_layer, bx, by, Z3, Z3 + 0.72, 0.84, 0.84, 0.68, 0.68, "travertine", top_region="travertine")
            prof = [(0.22, 0.0), (0.30, 0.10), (0.18, 0.24), (0.48, 0.42), (0.56, 0.50), (0.46, 0.50), (0.38, 0.38)]
            add_lathe(bm, uv_layer, bx, by, Z3 + 0.72, prof, segs=(14 if lod == 0 else 6), region="tin_bronze")
            # Prominent warm glowing charcoal mound clearly visible above the bowl rim!
            add_prism(bm, uv_layer, bx, by, Z3 + 1.12, Z3 + 1.36, 0.66, 0.66, 0.38, 0.38, "glowing_embers")
            if lod == 0:
                add_prism(bm, uv_layer, bx + 0.08, by - 0.06, Z3 + 1.24, Z3 + 1.42, 0.34, 0.32, 0.18, 0.18, "glowing_embers")

    # ==========================================================================
    # 6) TERRASSEN-BEGRUENUNG (100% SYMMETRISCH, KEINE KNET-ZUNGEN, BUENDIGE TROEGE!)
    #    Alle Pflanztroege strikt am aeusseren Rand/Ecken — NIE im Laufweg!
    # ==========================================================================
    if lod <= 1:
        # Tier 1 masonry planter troughs (100% mirror-symmetric on East, West & Front-wings!)
        t1_troughs = [
            (-9.45, -11.5, 0.95, 3.2), (+9.45, -11.5, 0.95, 3.2),
            (-9.45,  -4.8, 0.95, 3.2), (+9.45,  -4.8, 0.95, 3.2),
            (-9.45,  +1.9, 0.95, 3.2), (+9.45,  +1.9, 0.95, 3.2),
            (-5.80,  +5.35, 2.8, 0.90), (+5.80, +5.35, 2.8, 0.90),
        ]
        for idx, (tx, ty, tw, td) in enumerate(t1_troughs):
            add_box(bm, uv_layer, tx, ty, Z1 - 0.02, Z1 + 0.52, tw, td, "travertine", top_region="travertine")
            add_box(bm, uv_layer, tx, ty, Z1 + 0.42, Z1 + 0.54, tw - 0.22, td - 0.22, "garden_soil")
            shrub_cell = ("oleander" if (idx // 2) % 3 == 0 else ("pomegranate" if (idx // 2) % 3 == 1 else "fig"))
            if tw > td:
                for ox in (-0.70, +0.70):
                    add_fine_terrace_shrub(bm, uv_layer, tx + ox, ty, Z1 + 0.52, 0.58, 1.05, shrub_cell, seed=110 + idx * 7 + int(ox * 10), lod=lod)
            else:
                for oy in (-0.80, +0.80):
                    add_fine_terrace_shrub(bm, uv_layer, tx, ty + oy, Z1 + 0.52, 0.58, 1.05, shrub_cell, seed=110 + idx * 7 + int(oy * 10), lod=lod)

        # Tier 2 masonry planters & terracotta urns (100% mirror-symmetric at outer corners & flanks — 0% in path!)
        t2_pots = [
            (-6.45, -12.80), (+6.45, -12.80),
            (-6.45,  -7.15), (+6.45,  -7.15),
            (-6.45,  -1.45), (+6.45,  -1.45),
            (-3.60,  -1.45), (+3.60,  -1.45),
        ]
        for idx, (px, py) in enumerate(t2_pots):
            add_box(bm, uv_layer, px, py, Z2 - 0.02, Z2 + 0.28, 0.90, 0.90, "travertine")
            prof_urn = [(0.24, 0.0), (0.39, 0.28), (0.42, 0.50), (0.34, 0.62), (0.40, 0.68)]
            add_lathe(bm, uv_layer, px, py, Z2 + 0.26, prof_urn, segs=(12 if lod == 0 else 6), region="terracotta_pot")
            add_cylinder(bm, uv_layer, px, py, Z2 + 0.86, Z2 + 0.92, 0.34, 0.34, 8, "garden_soil")
            add_fine_terrace_shrub(bm, uv_layer, px, py, Z2 + 0.90, 0.52, 0.88,
                                   "pomegranate" if (idx // 2) % 2 == 0 else "oleander", seed=220 + idx, lod=lod)

        # Fine multi-branched trailing vines cascading delicately from planter edges (100% symmetric, ZERO flat dough tongues!)
        vine_anchors = [
            # Tier 1 East & West walls
            ((-10.52, -11.5, Z1 + 0.42), (-1.0, 0.0, 0.0), 1.65),
            ((+10.52, -11.5, Z1 + 0.42), (+1.0, 0.0, 0.0), 1.65),
            ((-10.52,  -4.8, Z1 + 0.42), (-1.0, 0.0, 0.0), 1.45),
            ((+10.52,  -4.8, Z1 + 0.42), (+1.0, 0.0, 0.0), 1.45),
            ((-10.52,  +1.9, Z1 + 0.42), (-1.0, 0.0, 0.0), 1.55),
            ((+10.52,  +1.9, Z1 + 0.42), (+1.0, 0.0, 0.0), 1.55),
            # Tier 1 Front wings
            ((-5.80, +6.28, Z1 + 0.42), (0.0, +1.0, 0.0), 1.35),
            ((+5.80, +6.28, Z1 + 0.42), (0.0, +1.0, 0.0), 1.35),
            # Tier 2 East, West & Front wings
            ((-7.52, -11.5, Z2 + 0.36), (-1.0, 0.0, 0.0), 1.40),
            ((+7.52, -11.5, Z2 + 0.36), (+1.0, 0.0, 0.0), 1.40),
            ((-7.52,  -3.2, Z2 + 0.36), (-1.0, 0.0, 0.0), 1.35),
            ((+7.52,  -3.2, Z2 + 0.36), (+1.0, 0.0, 0.0), 1.35),
            ((-4.80, -0.38, Z2 + 0.36), (0.0, +1.0, 0.0), 1.28),
            ((+4.80, -0.38, Z2 + 0.36), (0.0, +1.0, 0.0), 1.28),
            # Tier 3 subtle corner vines
            ((-5.02, -9.8, Z3 + 0.32), (-1.0, 0.0, 0.0), 1.10),
            ((+5.02, -9.8, Z3 + 0.32), (+1.0, 0.0, 0.0), 1.10),
        ]
        for vi, (v_pt, v_nrm, v_len) in enumerate(vine_anchors):
            add_fine_trailing_vine(bm, uv_layer, v_pt, v_nrm, length=v_len, seed=500 + vi * 13, lod=lod)

    # ==========================================================================
    # 7) AAA HERO DETAIL PASS ON LOD0 (Dentil Cornices, Crisp Moldings — 0 Coplanar!)
    # ==========================================================================
    if lod == 0:
        # Dentil corbel courses under all 3 tier parapets & summit shrine (cleanly skipping stair openings!)
        for (dcx, dcy, dz, dwx, dwy, reg, gx0, gx1) in [
            (0.0,  c1_y, Z1 - 0.42, w1_x1 + 0.18, w1_y1 + 0.18, "travertine", -2.35, +2.35),
            (0.0,  c2_y, Z2 - 0.40, w2_x1 + 0.18, w2_y1 + 0.18, "travertine", -1.35, +1.35),
            (0.0,  c3_y, Z3 - 0.38, w3_x1 + 0.16, w3_y1 + 0.16, "travertine", -1.25, +1.25),
            (0.0, sh_cy, sh_z1 - 0.34, 5.62, 2.76, "tin_bronze", None, None),
        ]:
            nx_d = max(6, int(dwx / 0.62))
            ny_d = max(4, int(dwy / 0.62))
            for i in range(nx_d):
                dx = dcx - dwx * 0.48 + i * (dwx * 0.96 / max(1, nx_d - 1))
                # Back (-Y)
                add_box(bm, uv_layer, dx, dcy - dwy * 0.5, dz, dz + 0.13, 0.22, 0.16, reg)
                # Front (+Y) skipping stair gap!
                if gx0 is None or (dx < gx0 or dx > gx1):
                    add_box(bm, uv_layer, dx, dcy + dwy * 0.5, dz, dz + 0.13, 0.22, 0.16, reg)
            for j in range(ny_d):
                dy = dcy - dwy * 0.48 + j * (dwy * 0.96 / max(1, ny_d - 1))
                for sgn in (-1.0, 1.0):
                    add_box(bm, uv_layer, dcx + sgn * (dwx * 0.5), dy, dz, dz + 0.13, 0.16, 0.22, reg)
        # Gatehouse dentil cornice under lapis frieze
        for i in range(8):
            dx = -2.10 + i * (4.20 / 7.0)
            for sgn in (-1.0, 1.0):
                add_box(bm, uv_layer, dx, gh_cy + sgn * 1.82, gh_lintel_z0 + 0.12, gh_lintel_z0 + 0.24, 0.20, 0.14, "travertine")
        for j in range(6):
            dy = gh_cy - 1.60 + j * (3.20 / 5.0)
            for sgn in (-1.0, 1.0):
                add_box(bm, uv_layer, sgn * 2.28, dy, gh_lintel_z0 + 0.12, gh_lintel_z0 + 0.24, 0.14, 0.20, "travertine")



# ==============================================================================
# 4) HERO-ASSET B: HERO_ABZU_POND (Echter versenkter 3D-Teich, 0% Z-Fighting!)
# ==============================================================================

def build_hero_abzu_pond(bm, uv_layer, lod):
    """3D-Beckenarchitektur: Rand +0.28 m, 3D-Stufen hinab bis -0.50 m, -0.35 m Schuerze,
    Wasserspeier, 4 Eckpoller, 2 seitliche Papyrus-Pflanzkaesten, 3D-Seerosen & Lotos bei Z=+0.155 m!"""
    if lod == 3:
        add_box(bm, uv_layer, 0.0, 0.0, -0.35, 0.28, 4.8, 4.8, "travertine", top_region="lapis_brick")
        return

    # 1. Outer Masonry Casing + Deep Foundation Skirt (Z = -0.55 .. +0.28 m)
    # 4 outer rim walls forming a true hollow sunken basin (inner opening 3.60 x 3.60 m)
    rim_w = 4.80
    inner_w = 3.60
    wall_t = (rim_w - inner_w) * 0.5  # 0.60 m thick profiled stone rim
    for sgn in (-1.0, 1.0):
        # North/South rim walls (non-overlapping corner heights -> 0 coplanar Z-fighting!)
        add_box(bm, uv_layer, 0.0, sgn * (inner_w * 0.5 + wall_t * 0.5), -0.55, 0.23, rim_w, wall_t, "travertine")
        add_box(bm, uv_layer, 0.0, sgn * (inner_w * 0.5 + wall_t * 0.5), 0.23, 0.275, rim_w + 0.08, wall_t + 0.04, "travertine", top_region="travertine")
        add_box(bm, uv_layer, 0.0, sgn * (rim_w * 0.5 + 0.02), 0.06, 0.21, rim_w + 0.04, 0.08, "lapis_rosette_frieze", u_scale=0.55)
        # East/West rim walls (fit cleanly between N/S walls -> 0 corner overlap!)
        add_box(bm, uv_layer, sgn * (inner_w * 0.5 + wall_t * 0.5), 0.0, -0.55, 0.23, wall_t, inner_w, "travertine")
        add_box(bm, uv_layer, sgn * (inner_w * 0.5 + wall_t * 0.5), 0.0, 0.23, 0.275, wall_t + 0.04, inner_w - 0.02, "travertine", top_region="travertine")
        add_box(bm, uv_layer, sgn * (rim_w * 0.5 + 0.02), 0.0, 0.06, 0.21, 0.08, inner_w + 0.04, "lapis_rosette_frieze", u_scale=0.55)

    # 2. Stepped 3D Interior Basin Ledges descending to Z = -0.50 m!
    # Step 1 ledge (Z = -0.26 .. -0.02 m, inner opening 3.04 m)
    for sgn in (-1.0, 1.0):
        add_box(bm, uv_layer, 0.0, sgn * 1.66, -0.55, -0.02, 3.60, 0.28, "river_mosaic", top_region="travertine")
        add_box(bm, uv_layer, sgn * 1.66, 0.0, -0.55, -0.02, 0.28, 3.04, "river_mosaic", top_region="travertine")
    # Step 2 ledge (Z = -0.50 .. -0.26 m, inner opening 2.48 m)
    for sgn in (-1.0, 1.0):
        add_box(bm, uv_layer, 0.0, sgn * 1.38, -0.55, -0.26, 3.04, 0.28, "river_mosaic", top_region="river_mosaic")
        add_box(bm, uv_layer, sgn * 1.38, 0.0, -0.55, -0.26, 0.28, 2.48, "river_mosaic", top_region="river_mosaic")
    # Deep Dark River-Mosaic Basin Floor at exact Z = -0.50 m!
    add_box(bm, uv_layer, 0.0, 0.0, -0.60, -0.50, 3.68, 3.68, "river_mosaic", top_region="river_mosaic")

    # 3. 4 Profiled Stone Corner Bollards (Stein-Poller) with Bronze Caps
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            bx, by = sx * 2.16, sy * 2.16
            add_prism(bm, uv_layer, bx, by, 0.26, 0.72, 0.44, 0.44, 0.38, 0.38, "travertine")
            add_box(bm, uv_layer, bx, by, 0.72, 0.80, 0.42, 0.42, "lapis_brick")
            if lod <= 1:
                add_lathe(bm, uv_layer, bx, by, 0.80, [(0.16, 0.0), (0.18, 0.08), (0.09, 0.16), (0.02, 0.20)], segs=(10 if lod == 0 else 6), region="tin_bronze")

    # 4. Bronze Lion-Head / Bowl Waterspout on Stepped Pedestal at -Y end
    add_prism(bm, uv_layer, 0.0, -2.18, 0.26, 1.18, 0.96, 0.76, 0.82, 0.64, "travertine")
    add_box(bm, uv_layer, 0.0, -2.18, 0.92, 1.10, 0.88, 0.70, "lapis_rosette_frieze")
    # Sculpted Bronze Lion-Head Mask + Projecting Water Spout Channel + Catch Basin Bowl
    add_box(bm, uv_layer, 0.0, -1.78, 0.72, 1.04, 0.42, 0.24, "tin_bronze")
    add_box(bm, uv_layer, 0.0, -1.52, 0.76, 0.86, 0.16, 0.44, "tin_bronze")
    if lod <= 1:
        add_lathe(bm, uv_layer, 0.0, -1.48, 0.28, [(0.18, 0.0), (0.42, 0.24), (0.46, 0.30), (0.38, 0.30)], segs=(12 if lod == 0 else 6), region="tin_bronze")

    # 5. Two Integrated Masonry Side Planter Boxes (X = +-2.72 m) with Lush Papyrus & Reeds!
    for sgn in (-1.0, 1.0):
        px = sgn * 2.74
        add_box(bm, uv_layer, px, 0.0, -0.35, 0.34, 0.72, 2.80, "travertine", top_region="travertine")
        add_box(bm, uv_layer, px, 0.0, 0.24, 0.36, 0.52, 2.58, "garden_soil")
        if lod <= 1:
            n_stalks = 10 if lod == 0 else 5
            rng = random.Random(300 + int(sgn * 10))
            for k in range(n_stalks):
                ry = -1.05 + (k + 0.5) * (2.10 / n_stalks) + rng.uniform(-0.08, 0.08)
                rx = px + rng.uniform(-0.14, 0.14)
                yaw = rng.uniform(0.0, math.pi * 2.0)
                h = rng.uniform(1.05, 1.55)
                add_botany_card(bm, uv_layer, (rx, ry, 0.33), 0.58, h, yaw, rng.uniform(-0.12, 0.16), "papyrus", bend=0.10, segs_v=2)

    # 6. Floating 3D Water Lily Pads & Pink/White Sacred Lotus Blossoms at exact Z = +0.155 m (+1.5 cm above water!)
    if lod <= 1:
        lily_spots = [
            (-0.85, +0.65, 0.44, "lotus_pink"),
            (+0.78, -0.52, 0.40, "lotus_white"),
            (-0.42, -0.78, 0.36, None),
            (+0.95, +0.72, 0.38, "lotus_pink"),
            (+0.18, +0.48, 0.34, "lotus_white"),
            (-0.98, -0.22, 0.35, None),
            (+0.35, -0.95, 0.36, None),
        ]
        for idx, (lx, ly, rad, lotus_cell) in enumerate(lily_spots):
            # Horizontal lily pad at Z = +0.155 m (pitch = pi/2 lies flat in XY)
            add_botany_card(bm, uv_layer, (lx, ly, 0.155), rad * 2.0, rad * 2.0, idx * 1.1, math.pi * 0.495, "lilypad", bend=0.02, segs_v=1)
            # Small companion pad
            if lod == 0:
                add_botany_card(bm, uv_layer, (lx + 0.28, ly - 0.18, 0.156), rad * 1.35, rad * 1.35, idx * 2.1 + 0.7, math.pi * 0.495, "lilypad", bend=0.02, segs_v=1)
            # 3D Sacred Lotus blossom rising slightly above the pad (2 crossed upturned petal cards + horizontal crown!)
            if lotus_cell:
                add_botany_card(bm, uv_layer, (lx, ly, 0.168), 0.42, 0.42, idx * 0.9, math.pi * 0.44, lotus_cell, bend=0.08, segs_v=1)
                add_botany_card(bm, uv_layer, (lx, ly, 0.176), 0.34, 0.30, idx * 0.9 + 0.6, 0.42, lotus_cell, bend=0.14, segs_v=1)
                add_botany_card(bm, uv_layer, (lx, ly, 0.176), 0.34, 0.30, idx * 0.9 + 2.1, 0.42, lotus_cell, bend=0.14, segs_v=1)

    # AAA LOD0 detail pass on Abzu pond: individual bevelled travertine coping stones & lion mane ribs (0 black faces!)
    if lod == 0:
        for sgn in (-1.0, 1.0):
            for bi in range(8):
                pos = -1.95 + bi * (3.90 / 7.0)
                add_prism(bm, uv_layer, pos, sgn * 2.10, 0.27, 0.32, 0.50, 0.66, 0.46, 0.62, "travertine")
                add_prism(bm, uv_layer, sgn * 2.10, pos, 0.27, 0.32, 0.66, 0.50, 0.62, 0.46, "travertine")
        # Sculpted bronze lion mane rays around waterspout + subtle water-jet arc into catch basin
        for k in range(10):
            a = -math.pi * 0.1 + k * (math.pi * 1.2 / 9.0)
            mx = math.cos(a) * 0.22
            mz = 0.88 + math.sin(a) * 0.18
            add_box(bm, uv_layer, mx, -1.72, mz - 0.04, mz + 0.04, 0.10, 0.14, "tin_bronze")
        # Inner bevelled stone trim around stepped water basin (non-overlapping with corner bollards)
        for sgn in (-1.0, 1.0):
            add_prism(bm, uv_layer, 0.0, sgn * 1.82, 0.22, 0.268, 3.60, 0.08, 3.56, 0.06, "lapis_brick")
            add_prism(bm, uv_layer, sgn * 1.82, 0.0, 0.22, 0.268, 0.08, 3.52, 0.06, 3.48, "lapis_brick")


def build_abzu_water_surface(bm, uv_layer, lod):
    """Separate Wasseroberflaechen-Komponente auf exakt Z = +0.14 m (64 cm ueber Beckenboden, 14 cm ueber Hof!)."""
    segs = 10 if lod == 0 else (4 if lod == 1 else 1)
    size = 3.64
    half = size * 0.5
    grid = []
    for iy in range(segs + 1):
        row = []
        for ix in range(segs + 1):
            x = -half + size * (ix / segs)
            y = -half + size * (iy / segs)
            # Subtle 3 mm gentle ripple for specular highlights
            z = 0.14 + (0.003 * math.sin(x * 3.4) * math.cos(y * 3.1) if lod == 0 else 0.0)
            row.append((bm.verts.new((x, y, z)), ix / segs, iy / segs))
        grid.append(row)
    for iy in range(segs):
        for ix in range(segs):
            a, ua, va = grid[iy][ix]
            b, ub, vb = grid[iy][ix + 1]
            c, uc, vc = grid[iy + 1][ix + 1]
            d, ud, vd = grid[iy + 1][ix]
            f = bm.faces.new((a, b, c, d))
            f.material_index = 0  # Mat_Abzu_Water on dedicated object
            f.smooth = True
            for loop, uv in zip(f.loops, [(ua, va), (ub, vb), (uc, vc), (ud, vd)]):
                loop[uv_layer].uv = uv


# ==============================================================================
# 5) HERO-ASSET C: HERO_TEMPLE_ANNEX_01 & 02 (6.8 x 11.0 m, 1:1 Grundriss!)
# ==============================================================================

def _build_temple_annex_common(bm, uv_layer, lod, variant=1):
    """Sumerisches Tempel-Nebengebaeude (6.8 x 11.0 m, Portikus nach +X zum Hof, -0.35 m Schuerze)."""
    wx, wy = 6.2, 10.8  # Main body; +X portico adds 1.2 m on courtyard side -> total ~7.4 x 11.0 m
    h_wall = 3.85 if variant == 1 else 3.65

    if lod == 3:
        add_prism(bm, uv_layer, 0.0, 0.0, -0.35, h_wall, wx + 0.6, wy + 0.4, wx + 0.3, wy + 0.2, "brick_terracotta", top_region="reed_mat")
        return

    # 1. Travertine Foundation Plinth (-0.35 .. +0.35 m)
    add_prism(bm, uv_layer, 0.0, 0.0, -0.35, 0.35, wx + 0.8, wy + 0.6, wx + 0.6, wy + 0.4, "travertine", top_region="travertine")

    # 2. Main Pilastered Mudbrick Hall (battered)
    body_reg = "brick_terracotta" if variant == 1 else "brick_sand"
    add_prism(bm, uv_layer, -0.35, 0.0, 0.35, h_wall, wx, wy, wx - 0.35, wy - 0.35, body_reg, u_scale=0.16, top_region="travertine")
    add_pilaster_and_niche_facade(bm, uv_layer, -0.35, 0.0, 0.35, h_wall - 0.1, wx, wy, wx - 0.35, wy - 0.35,
                                  n_x=(4 if lod == 0 else 3), n_y=(6 if lod == 0 else 4),
                                  region=body_reg, lod=lod, add_drains=False)
    # Lapis Rosette upper frieze band (0.02m below roof deck -> 0 coplanar Z-fighting!)
    add_box(bm, uv_layer, -0.35, 0.0, h_wall - 0.38, h_wall - 0.02, wx - 0.22, wy - 0.22, "lapis_rosette_frieze", u_scale=0.45)

    # 3. Walkable Flat Roof + Crenelated Parapet
    add_parapet_with_merlons(bm, uv_layer, -0.35, 0.0, h_wall, wx - 0.35, wy - 0.35, 0.34, 0.50, body_reg,
                             merlons=(lod <= 1), merlon_h=0.22)

    # 4. Stepped Rabbeted Portal + Front Steps on +X (facing Ziggurat courtyard!)
    port_x = -0.35 + wx * 0.5 - 0.15
    door_y = 0.0 if variant == 1 else -1.6
    for si, (dw, dd, dh, reg) in enumerate([
        (0.32, 2.50, 2.65, "travertine"),
        (0.22, 2.05, 2.45, "lapis_brick"),
        (0.14, 1.65, 2.28, "cedar_wood"),
    ]):
        add_box(bm, uv_layer, port_x + si * 0.04, door_y, 0.35, 0.35 + dh, dw, dd, reg)
    # Bronze door bands
    if lod <= 1:
        for dz in (0.95, 1.65, 2.25):
            add_box(bm, uv_layer, port_x + 0.16, door_y, dz, dz + 0.07, 0.05, 1.56, "tin_bronze")
    # 3 Travertine entrance steps
    for st in range(3):
        add_box(bm, uv_layer, port_x + 0.55 + st * 0.32, door_y, -0.35, 0.36 - st * 0.11, 0.36, 2.6 + st * 0.25, "travertine")

    # 5. Projecting Cedar-Columned Portico (Vorhalle on +X for real light-shadow depth!)
    p_x0 = port_x + 0.10
    p_x1 = port_x + 1.55
    p_y_span = 6.8 if variant == 1 else 8.8
    # Portico floor slab
    add_box(bm, uv_layer, 0.5 * (p_x0 + p_x1), 0.0, -0.35, 0.32, (p_x1 - p_x0) + 0.2, p_y_span, "travertine")
    # Cedar columns on stone plinth bases
    n_cols = 4 if variant == 1 else 5
    for ci in range(n_cols):
        cy = -p_y_span * 0.44 + ci * (p_y_span * 0.88 / max(1, n_cols - 1))
        # Stone plinth base
        add_prism(bm, uv_layer, p_x1 - 0.12, cy, 0.32, 0.62, 0.42, 0.42, 0.34, 0.34, "travertine")
        # Cedar column shaft
        add_cylinder(bm, uv_layer, p_x1 - 0.12, cy, 0.62, h_wall - 0.48, 0.13, 0.11, 10 if lod == 0 else 6, "cedar_wood")
        # Capital bolster
        add_box(bm, uv_layer, p_x1 - 0.12, cy, h_wall - 0.48, h_wall - 0.30, 0.36, 0.48, "cedar_wood")
    # Portico architrave beam + overhanging cedar vigas + reed shade canopy
    add_box(bm, uv_layer, p_x1 - 0.12, 0.0, h_wall - 0.30, h_wall - 0.06, 0.28, p_y_span + 0.2, "cedar_wood")
    add_box(bm, uv_layer, 0.5 * (p_x0 + p_x1) + 0.08, 0.0, h_wall - 0.08, h_wall + 0.06, (p_x1 - p_x0) + 0.35, p_y_span + 0.15, "reed_mat")

    # 6. Roof Shading Pergola (Cedar + Woven Reed Mat) + Amphorae + Roof Waterspouts!
    if lod <= 1:
        pg_y = -1.6 if variant == 1 else +1.8
        pg_x = -0.55
        pg_w, pg_d = 3.4, 4.4
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                add_cylinder(bm, uv_layer, pg_x + sx * (pg_w * 0.46), pg_y + sy * (pg_d * 0.46),
                             h_wall, h_wall + 1.65, 0.09, 0.08, 8 if lod == 0 else 5, "cedar_wood")
        # Cross beams & woven reed shade mat
        for by_i in range(5):
            by = pg_y - pg_d * 0.46 + by_i * (pg_d * 0.92 / 4.0)
            add_box(bm, uv_layer, pg_x, by, h_wall + 1.58, h_wall + 1.68, pg_w + 0.35, 0.10, "cedar_wood")
        add_box(bm, uv_layer, pg_x, pg_y, h_wall + 1.68, h_wall + 1.76, pg_w + 0.25, pg_d + 0.20, "reed_mat")

        # Variant 1: Upper Treasury Clerestory Lantern; Variant 2: Roof Archive Bench + More Amphorae
        if variant == 1:
            add_prism(bm, uv_layer, -0.55, +2.6, h_wall, h_wall + 1.15, 2.8, 2.6, 2.6, 2.4, "brick_sand", top_region="travertine")
            add_box(bm, uv_layer, -0.55, +2.6, h_wall + 0.95, h_wall + 1.18, 2.75, 2.55, "lapis_brick")

        # Lathe-turned Terracotta Amphorae on roof
        prof_amp = [(0.06, 0.0), (0.20, 0.22), (0.22, 0.44), (0.10, 0.60), (0.13, 0.72), (0.10, 0.76)]
        for ax, ay in [(-1.8, -3.4), (-1.2, -3.6), (+0.8, +3.6), (+1.2, +3.1)]:
            add_lathe(bm, uv_layer, ax, ay, h_wall, prof_amp, segs=(10 if lod == 0 else 6), region="terracotta_pot")

        # Projecting Travertine Roof Waterspouts
        for wy_sp in (-3.2, 0.0, +3.2):
            add_box(bm, uv_layer, -0.35 - wx * 0.5 - 0.15, wy_sp, h_wall + 0.04, h_wall + 0.18, 0.65, 0.20, "travertine")

    # AAA LOD0 detail pass on Temple Annexes: cedar vigas rafter tails, recessed latticed windows & dentil molding
    if lod == 0:
        # Projecting cedar vigas beams along +X and -X eaves
        for vi in range(11):
            vy = -4.6 + vi * (9.2 / 10.0)
            add_cylinder(bm, uv_layer, port_x + 1.58, vy, h_wall - 0.14, h_wall - 0.04, 0.06, 0.06, 6, "cedar_wood")
            add_box(bm, uv_layer, -0.35 - wx * 0.5 - 0.12, vy, h_wall - 0.22, h_wall - 0.10, 0.32, 0.12, "cedar_wood")
        # Recessed latticed cedar upper windows on +-Y and -X facades
        for wy_w in (-2.8, +2.8):
            add_box(bm, uv_layer, -0.35 - wx * 0.5 - 0.02, wy_w, 2.25, 3.05, 0.16, 1.15, "travertine")
            add_box(bm, uv_layer, -0.35 - wx * 0.5 - 0.06, wy_w, 2.35, 2.95, 0.10, 0.92, "cedar_wood")
            for bar in (-0.28, 0.0, +0.28):
                add_box(bm, uv_layer, -0.35 - wx * 0.5 - 0.11, wy_w + bar, 2.35, 2.95, 0.05, 0.06, "travertine")
        # Dentil corbel course under roof parapet (clean manifold geometry, 0 black faces!)
        for di in range(12):
            dy = -4.9 + di * (9.8 / 11.0)
            for sgn in (-1.0, 1.0):
                add_box(bm, uv_layer, -0.35 + sgn * (wx * 0.5 - 0.08), dy, h_wall - 0.46, h_wall - 0.34, 0.16, 0.22, "travertine")


def build_hero_temple_annex_01(bm, uv_layer, lod):
    _build_temple_annex_common(bm, uv_layer, lod, variant=1)


def build_hero_temple_annex_02(bm, uv_layer, lod):
    _build_temple_annex_common(bm, uv_layer, lod, variant=2)


# ==============================================================================
# 6) HERO-ASSET D: HERO_TEMENOS_GATE & HERO_TEMENOS_WALL_SEG (-0.35 m Schuerze!)
# ==============================================================================

def build_hero_temenos_gate(bm, uv_layer, lod):
    """Temenos-Prunktor (10.8 m breit, 4.6 m Durchgang, 5.6 m Turmhoehe, -0.35 m Schuerze)."""
    if lod == 3:
        for sgn in (-1.0, 1.0):
            add_prism(bm, uv_layer, sgn * 3.6, 0.0, -0.35, 5.5, 3.2, 3.4, 2.9, 3.1, "brick_terracotta")
        add_box(bm, uv_layer, 0.0, 0.0, 3.6, 5.0, 4.8, 2.8, "lapis_rosette_frieze")
        return

    # Twin Pilastered Gate Towers
    for sgn in (-1.0, 1.0):
        tx = sgn * 3.70
        add_prism(bm, uv_layer, tx, 0.0, -0.35, 0.40, 3.55, 3.75, 3.40, 3.60, "travertine")
        add_prism(bm, uv_layer, tx, 0.0, 0.40, 5.10, 3.30, 3.50, 3.05, 3.25, "brick_terracotta", top_region="travertine")
        add_pilaster_and_niche_facade(bm, uv_layer, tx, 0.0, 0.40, 5.00, 3.30, 3.50, 3.05, 3.25, 2, 2, "brick_terracotta", lod, add_drains=False)
        add_box(bm, uv_layer, tx, 0.0, 4.66, 5.08, 3.22, 3.42, "lapis_rosette_frieze", u_scale=0.50)
        add_parapet_with_merlons(bm, uv_layer, tx, 0.0, 5.10, 3.05, 3.25, 0.34, 0.36, "brick_terracotta", merlons=(lod <= 1), merlon_h=0.26)
        # Flanking Torch Brackets on +Y and -Y tower fronts
        if lod <= 1:
            for fy in (-1.82, +1.82):
                add_box(bm, uv_layer, tx - sgn * 0.95, fy, 2.10, 2.26, 0.14, 0.32, "tin_bronze")
                add_lathe(bm, uv_layer, tx - sgn * 0.95, fy + (0.14 if fy > 0 else -0.14), 2.22,
                          [(0.06, 0.0), (0.16, 0.18), (0.18, 0.24)], segs=8, region="tin_bronze")
                add_box(bm, uv_layer, tx - sgn * 0.95, fy + (0.14 if fy > 0 else -0.14), 2.42, 2.52, 0.18, 0.18, "glowing_embers")

    # Central Portal Bridge, Massive Cedar Lintel & Glazed Lapis-Rosette Frieze (open 4.2 m x 3.6 m passage!)
    add_box(bm, uv_layer, 0.0, 0.0, 3.55, 3.85, 4.6, 2.9, "cedar_wood")
    add_box(bm, uv_layer, 0.0, 0.0, 3.85, 4.85, 4.6, 2.8, "brick_sand", top_region="travertine")
    add_box(bm, uv_layer, 0.0, 0.0, 4.25, 4.75, 4.72, 2.94, "lapis_rosette_frieze", u_scale=0.55)
    add_parapet_with_merlons(bm, uv_layer, 0.0, 0.0, 4.85, 4.5, 2.7, 0.30, 0.28, "brick_sand", merlons=(lod <= 1), merlon_h=0.22)

    # Open Bronze-Studded Cedar Gate Leaves swung inward (+Y)
    for sgn in (-1.0, 1.0):
        gx = sgn * 2.02
        add_box(bm, uv_layer, gx, 0.95, 0.02, 3.50, 0.16, 1.85, "cedar_wood")
        if lod <= 1:
            for dz in (0.65, 1.65, 2.65):
                add_box(bm, uv_layer, gx, 0.95, dz, dz + 0.10, 0.20, 1.82, "tin_bronze")


def build_hero_temenos_wall_seg(bm, uv_layer, lod):
    """Temenos-Innenmauer-Modul (6.0 m lang, 2.85 m hoch, Nischen, Zinnen, Fackelhalter, -0.35 m Schuerze)."""
    if lod == 3:
        add_box(bm, uv_layer, 0.0, 0.0, -0.35, 2.75, 6.0, 0.95, "brick_terracotta")
        return
    add_prism(bm, uv_layer, 0.0, 0.0, -0.35, 0.30, 6.0, 1.12, 6.0, 1.04, "travertine")
    add_prism(bm, uv_layer, 0.0, 0.0, 0.30, 2.55, 6.0, 0.96, 6.0, 0.84, "brick_terracotta", top_region="travertine")
    # Rhythmic pilasters & blind niches on both faces
    if lod <= 1:
        for px in (-2.25, -0.75, +0.75, +2.25):
            add_prism(bm, uv_layer, px, 0.0, 0.30, 2.52, 0.56, 1.14, 0.50, 1.02, "brick_terracotta", top_region="travertine")
        # Subtle lapis top trim
        add_box(bm, uv_layer, 0.0, 0.0, 2.34, 2.54, 6.0, 0.90, "lapis_brick")
    # Stepped merlons along top
    if lod <= 1:
        for mx in (-2.5, -1.5, -0.5, +0.5, +1.5, +2.5):
            add_box(bm, uv_layer, mx, 0.0, 2.55, 2.88, 0.52, 0.62, "brick_terracotta", top_region="travertine")
    # Wall torch sconce on +Y inner courtyard side
    if lod == 0:
        add_box(bm, uv_layer, 0.0, 0.54, 1.78, 1.90, 0.14, 0.28, "tin_bronze")
        add_lathe(bm, uv_layer, 0.0, 0.66, 1.88, [(0.05, 0.0), (0.14, 0.16), (0.16, 0.22)], segs=8, region="tin_bronze")
        add_box(bm, uv_layer, 0.0, 0.66, 2.06, 2.14, 0.16, 0.16, "glowing_embers")


# ==============================================================================
# 7) HERO-ASSET E: HERO_TEMPLE_GARDEN_KIT (8 PROPS + SAPLING TREE GEN + IVYGEN)
# ==============================================================================

def build_temple_planter_long(bm, uv_layer, lod):
    """Gemauertes Kalkstein-/Ziegel-Hochbeet (3.2 x 1.1 x 0.45 m, -0.30 m Schuerze) + ueppige Mischbepflanzung."""
    add_box(bm, uv_layer, 0.0, 0.0, -0.30, 0.42, 3.20, 1.10, "brick_terracotta", top_region="travertine")
    add_box(bm, uv_layer, 0.0, 0.0, 0.36, 0.46, 3.30, 1.20, "travertine", top_region="travertine")
    add_box(bm, uv_layer, 0.0, 0.0, 0.38, 0.47, 2.92, 0.84, "garden_soil")
    if lod <= 2:
        n_o = 12 if lod == 0 else (6 if lod == 1 else 3)
        add_bush_cluster(bm, uv_layer, -0.95, 0.0, 0.46, 0.58, 1.15, "oleander", n_o, seed=401)
        add_bush_cluster(bm, uv_layer,  0.00, 0.0, 0.46, 0.62, 1.30, "pomegranate", n_o, seed=402)
        add_bush_cluster(bm, uv_layer, +0.95, 0.0, 0.46, 0.56, 1.05, "fig", n_o, seed=403)
    if lod <= 1:
        for ix in (-1.1, -0.35, +0.45, +1.15):
            for sgn in (-1.0, 1.0):
                add_botany_card(bm, uv_layer, (ix, sgn * 0.56, 0.46), 0.54, 0.68, 0.0 if sgn > 0 else math.pi, math.pi * 0.86, "ivy", bend=0.14, segs_v=2)


def build_temple_planter_corner(bm, uv_layer, lod):
    """Quadratisches Eck-Hochbeet (1.6 x 1.6 x 0.45 m, -0.30 m Schuerze) + Oleander, Kraeuter & Efeu."""
    add_box(bm, uv_layer, 0.0, 0.0, -0.30, 0.42, 1.60, 1.60, "brick_terracotta", top_region="travertine")
    add_box(bm, uv_layer, 0.0, 0.0, 0.36, 0.46, 1.70, 1.70, "travertine", top_region="travertine")
    add_box(bm, uv_layer, 0.0, 0.0, 0.38, 0.47, 1.32, 1.32, "garden_soil")
    if lod <= 2:
        n_o = 12 if lod == 0 else (6 if lod == 1 else 3)
        add_bush_cluster(bm, uv_layer, 0.0, 0.0, 0.46, 0.68, 1.25, "oleander", n_o, seed=411)
        add_bush_cluster(bm, uv_layer, 0.0, 0.0, 0.46, 0.55, 0.85, "fig", max(3, n_o // 2), seed=412)
    if lod <= 1:
        for ang in (0.0, math.pi * 0.5, math.pi, math.pi * 1.5):
            add_botany_card(bm, uv_layer, (math.cos(ang) * 0.80, math.sin(ang) * 0.80, 0.46), 0.55, 0.66, ang - math.pi * 0.5, math.pi * 0.86, "ivy", bend=0.14, segs_v=2)


def _build_sapling_tree_to_bmesh(bm, uv_layer, species, lod):
    """Nutzt das echte Blender-Addon Sapling Tree Gen (bpy.ops.curve.tree_add) fuer Stamm/Aeste
    und setzt gewölbte mehrsegmentige Blatt-/Frucht-Karten an die Astspitzen (4 LODs!)."""
    if lod == 3:
        # Ultra-clean LOD3 billboard/proxy tree
        h = 3.8 if species == "pomegranate" else 7.4
        r = 1.6 if species == "pomegranate" else 1.25
        cell = "pomegranate" if species == "pomegranate" else "cypress"
        add_cylinder(bm, uv_layer, 0.0, 0.0, -0.20, h * 0.55, 0.14, 0.05, 4, "cedar_wood")
        for a in (0.0, math.pi / 3.0, 2.0 * math.pi / 3.0):
            add_botany_card(bm, uv_layer, (0.0, 0.0, h * 0.22), r * 2.2, h * 0.82, a, 0.0, cell, bend=0.04, segs_v=1)
        return

    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.scene.cursor.location = Vector((0.0, 0.0, 0.0))
    before = set(bpy.data.objects.keys())
    try:
        if species == "pomegranate":
            bpy.ops.curve.tree_add(
                do_update=True,
                bevel=True,
                bevelRes=(2 if lod == 0 else (1 if lod == 1 else 0)),
                resU=(3 if lod == 0 else 2),
                showLeaves=False,
                seed=71,
                scale=3.2,
                scaleV=0.25,
                levels=(3 if lod == 0 else 2),
                ratio=0.042,
                baseSize=0.28,
                branches=(0, 14 if lod == 0 else 9, 10 if lod == 0 else 6, 4),
                length=(1.0, 0.55, 0.45, 0.35),
                downAngle=(90.0, 52.0, 44.0, 40.0),
                shape="7",  # Spherical ornamental canopy
            )
        else:  # cypress
            bpy.ops.curve.tree_add(
                do_update=True,
                bevel=True,
                bevelRes=(2 if lod == 0 else (1 if lod == 1 else 0)),
                resU=(3 if lod == 0 else 2),
                showLeaves=False,
                seed=93,
                scale=6.4,
                scaleV=0.15,
                levels=(2 if lod <= 1 else 1),
                ratio=0.028,
                baseSize=0.12,
                branches=(0, 26 if lod == 0 else 16, 6, 0),
                length=(1.0, 0.22, 0.20, 0.15),
                downAngle=(90.0, 32.0, 30.0, 25.0),
                shape="0",  # Conical tall flame cypress!
            )
    except Exception as e:
        print(f"[TEMENOS KIT] Sapling fallback ({species}): {e}", flush=True)

    new_objs = [bpy.data.objects[n] for n in bpy.data.objects.keys() if n not in before]
    depsgraph = bpy.context.evaluated_depsgraph_get()
    u0_b, v0_b, u1_b, v1_b = TEMENOS_TRIM_REGIONS["cedar_wood"]

    branch_tips = []
    for obj in new_objs:
        if obj.type not in ("MESH", "CURVE", "SURFACE"):
            continue
        ev = obj.evaluated_get(depsgraph)
        me = ev.to_mesh()
        if me is not None and len(me.polygons) > 0:
            mw = obj.matrix_world
            vmap = []
            for v in me.vertices:
                wco = mw @ v.co
                vmap.append(bm.verts.new(wco))
                if wco.z > (1.15 if species == "pomegranate" else 1.10):
                    branch_tips.append(wco.copy())
            for poly in me.polygons:
                p_verts = [vmap[vi] for vi in poly.vertices]
                if len(p_verts) < 3:
                    continue
                try:
                    f = bm.faces.new(p_verts)
                except ValueError:
                    continue
                f.material_index = 0
                f.smooth = True
                for li, loop in enumerate(f.loops):
                    u_v = u0_b + (0.2 if li in (0, 3) else 0.8) * (u1_b - u0_b)
                    v_v = v0_b + (0.15 if li in (0, 1) else 0.85) * (v1_b - v0_b)
                    loop[uv_layer].uv = (u_v, v_v)
            ev.to_mesh_clear()
        data = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if data and data.users == 0:
            if isinstance(data, bpy.types.Curve):
                bpy.data.curves.remove(data)
            elif isinstance(data, bpy.types.Mesh):
                bpy.data.meshes.remove(data)

    # Add root flare below Z=0 (-0.25 m) so tree never floats on terrain!
    add_cylinder(bm, uv_layer, 0.0, 0.0, -0.25, 0.35, 0.22 if species == "cypress" else 0.16, 0.12, 8, "cedar_wood")

    # Populate curved botanical leaf/fruit sprays around Sapling branch tips!
    rng = random.Random(701 if species == "pomegranate" else 901)
    if species == "pomegranate":
        n_sprays = 48 if lod == 0 else (24 if lod == 1 else 10)
        for i in range(n_sprays):
            if branch_tips:
                pt = branch_tips[rng.randrange(len(branch_tips))]
            else:
                a = rng.uniform(0, 2 * math.pi)
                r = rng.uniform(0.3, 1.3)
                pt = Vector((math.cos(a) * r, math.sin(a) * r, rng.uniform(1.5, 3.4)))
            yaw = math.atan2(pt.y, pt.x) + rng.uniform(-0.8, 0.8)
            pitch = rng.uniform(0.15, 0.72)
            w = rng.uniform(0.75, 1.15)
            h = rng.uniform(0.75, 1.15)
            add_botany_card(bm, uv_layer, pt - Vector((0, 0, 0.22)), w, h, yaw, pitch, "pomegranate", bend=0.16, segs_v=2 if lod == 0 else 1)
    else:  # cypress — dense layered flame silhouette
        n_tiers = 16 if lod == 0 else (10 if lod == 1 else 5)
        for ti in range(n_tiers):
            t = ti / max(1, n_tiers - 1)
            z = 0.95 + t * 5.95
            # Classic Mediterranean cypress flame profile
            rad = math.sin(t * math.pi) ** 0.65 * 0.92 * (1.0 - 0.35 * t) + 0.18
            n_ring = (6 if lod == 0 else 4) if t < 0.85 else 3
            for k in range(n_ring):
                a = k * (2.0 * math.pi / n_ring) + ti * 0.55
                px, py = math.cos(a) * rad * 0.65, math.sin(a) * rad * 0.65
                w = rad * rng.uniform(1.05, 1.45)
                h = rng.uniform(0.95, 1.45) * (1.15 - 0.35 * t)
                add_botany_card(bm, uv_layer, (px, py, z), w, h, a + math.pi * 0.5, rng.uniform(-0.18, 0.12), "cypress", bend=0.12, segs_v=2 if lod == 0 else 1)


def build_temple_tree_pomegranate(bm, uv_layer, lod):
    _build_sapling_tree_to_bmesh(bm, uv_layer, "pomegranate", lod)


def build_temple_tree_cypress(bm, uv_layer, lod):
    _build_sapling_tree_to_bmesh(bm, uv_layer, "cypress", lod)


def build_temple_pergola_vine(bm, uv_layer, lod):
    """Zedernholz- & Schilf-Pergola (3.6 x 2.8 x 2.9 m, -0.30 m Schuerze) mit echten IvyGen-Ranken!"""
    w, d, h = 3.6, 2.8, 2.85
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            px, py = sx * (w * 0.45), sy * (d * 0.45)
            add_prism(bm, uv_layer, px, py, -0.30, 0.40, 0.44, 0.44, 0.34, 0.34, "travertine")
            add_cylinder(bm, uv_layer, px, py, 0.40, h, 0.11, 0.095, 8 if lod == 0 else 5, "cedar_wood")
    # Longitudinal & transverse roof beams
    for sy in (-1.0, 1.0):
        add_box(bm, uv_layer, 0.0, sy * (d * 0.45), h - 0.14, h + 0.04, w + 0.45, 0.16, "cedar_wood")
    n_rafters = 7 if lod <= 1 else 3
    for i in range(n_rafters):
        rx = -w * 0.48 + i * (w * 0.96 / max(1, n_rafters - 1))
        add_box(bm, uv_layer, rx, 0.0, h + 0.02, h + 0.12, 0.10, d + 0.42, "cedar_wood")
    # Woven reed shade canopy
    add_box(bm, uv_layer, 0.0, 0.0, h + 0.11, h + 0.18, w + 0.20, d + 0.20, "reed_mat")

    # Real IvyGen climbing vines on posts & rafters!
    if lod <= 1:
        add_ivygen_vines_onto_bmesh(
            bm, uv_layer,
            target_box_center=(-w * 0.45, -d * 0.45, 1.5), target_box_size=(0.35, 0.35, 2.8),
            start_pts=[(-w * 0.45, -d * 0.45, 0.45)], max_ivy_len=2.6, leaf_scale=0.20, lod=lod
        )
        add_ivygen_vines_onto_bmesh(
            bm, uv_layer,
            target_box_center=(+w * 0.45, +d * 0.45, 1.5), target_box_size=(0.35, 0.35, 2.8),
            start_pts=[(+w * 0.45, +d * 0.45, 0.45)], max_ivy_len=2.6, leaf_scale=0.20, lod=lod
        )
        # Hanging roof vine curtains
        for vx in (-1.2, 0.0, +1.2):
            for sgn in (-1.0, 1.0):
                add_botany_card(bm, uv_layer, (vx, sgn * (d * 0.52), h + 0.12), 0.72, 1.05, 0.0 if sgn > 0 else math.pi, math.pi * 0.94, "ivy", bend=0.14, segs_v=2)


def build_temple_altar_incense(bm, uv_layer, lod):
    """Monumentaler Vorplatz-Opferaltar aus Kalkstein mit Horn-Ecken & Bronze-Raeucherschale + Glut!"""
    add_prism(bm, uv_layer, 0.0, 0.0, -0.30, 0.24, 1.95, 1.95, 1.85, 1.85, "travertine")
    add_prism(bm, uv_layer, 0.0, 0.0, 0.24, 0.48, 1.55, 1.55, 1.48, 1.48, "travertine")
    add_prism(bm, uv_layer, 0.0, 0.0, 0.48, 1.18, 1.18, 1.18, 1.10, 1.10, "travertine")
    add_box(bm, uv_layer, 0.0, 0.0, 0.88, 1.06, 1.18, 1.18, "lapis_rosette_frieze", u_scale=0.80)
    add_prism(bm, uv_layer, 0.0, 0.0, 1.18, 1.32, 1.28, 1.28, 1.24, 1.24, "travertine")
    # 4 Classical Bronze-Age Altar Horns at corners!
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            add_prism(bm, uv_layer, sx * 0.52, sy * 0.52, 1.32, 1.58, 0.22, 0.22, 0.06, 0.06, "travertine")
    # Large Hammered-Bronze Incense Bowl + Glowing Charcoal Bed
    prof = [(0.24, 0.0), (0.34, 0.08), (0.20, 0.18), (0.46, 0.34), (0.50, 0.40), (0.40, 0.40), (0.32, 0.26)]
    add_lathe(bm, uv_layer, 0.0, 0.0, 1.30, prof, segs=(14 if lod == 0 else (8 if lod == 1 else 5)), region="tin_bronze")
    add_prism(bm, uv_layer, 0.0, 0.0, 1.58, 1.74, 0.56, 0.56, 0.36, 0.36, "glowing_embers")


def build_temple_stele_01(bm, uv_layer, lod):
    """Sumerische Kalkstein-Stele mit Relief-Normalmap & gestuftem Sockel (-0.30 m Schuerze)."""
    add_prism(bm, uv_layer, 0.0, 0.0, -0.30, 0.28, 1.28, 0.78, 1.16, 0.68, "travertine")
    add_prism(bm, uv_layer, 0.0, 0.0, 0.28, 0.48, 1.06, 0.58, 1.00, 0.52, "lapis_brick")
    add_prism(bm, uv_layer, 0.0, 0.0, 0.48, 2.02, 0.90, 0.38, 0.82, 0.34, "stele_relief", top_region="travertine")
    # Rounded Sumerian stele crown (segmented arch)
    n_arc = 6 if lod <= 1 else 3
    for i in range(n_arc):
        t0, t1 = i / n_arc, (i + 1) / n_arc
        z0 = 2.02 + math.sin(t0 * math.pi * 0.5) * 0.36
        z1 = 2.02 + math.sin(t1 * math.pi * 0.5) * 0.36
        w0 = 0.82 * math.cos(t0 * math.pi * 0.5)
        w1 = max(0.08, 0.82 * math.cos(t1 * math.pi * 0.5))
        add_prism(bm, uv_layer, 0.0, 0.0, z0, z1, w0, 0.34, w1, 0.32, "travertine")


def build_temple_brazier_01(bm, uv_layer, lod):
    """Freistehender Bronze-Feuerstaender fuer den Prozessionsweg (-0.30 m Schuerze)."""
    add_prism(bm, uv_layer, 0.0, 0.0, -0.30, 0.26, 0.76, 0.76, 0.64, 0.64, "travertine")
    # 3 bronze tripod legs + central column
    segs = 10 if lod == 0 else (6 if lod == 1 else 4)
    add_cylinder(bm, uv_layer, 0.0, 0.0, 0.26, 1.14, 0.09, 0.07, segs, "tin_bronze")
    if lod <= 1:
        for k in range(3):
            a = k * (2.0 * math.pi / 3.0)
            lx, ly = math.cos(a) * 0.20, math.sin(a) * 0.20
            add_prism(bm, uv_layer, lx, ly, 0.26, 1.12, 0.07, 0.07, 0.05, 0.05, "tin_bronze")
    prof = [(0.16, 0.0), (0.38, 0.26), (0.42, 0.34), (0.34, 0.34), (0.24, 0.18)]
    add_lathe(bm, uv_layer, 0.0, 0.0, 1.12, prof, segs=segs, region="tin_bronze")
    add_prism(bm, uv_layer, 0.0, 0.0, 1.38, 1.52, 0.44, 0.44, 0.26, 0.26, "glowing_embers")


def build_temple_paving_slab(bm, uv_layer, lod):
    """Leicht erhabenes, abgeschrägtes Prozessions-Pflaster-Modul (4.0 x 4.0 m, +0.04 m, -0.12 m Schuerze)."""
    # Main bevelled travertine slab (0 Z-fighting!)
    add_prism(bm, uv_layer, 0.0, 0.0, -0.12, 0.04, 4.06, 4.06, 3.96, 3.96, "travertine", u_scale=0.32, top_region="travertine")
    # Flanking low bevelled curbstones along +-X edges
    for sgn in (-1.0, 1.0):
        add_prism(bm, uv_layer, sgn * 1.92, 0.0, -0.12, 0.09, 0.24, 4.04, 0.18, 3.98, "travertine", u_scale=0.35)
    # Subtle central lapis inlay strips on LOD0/1
    if lod <= 1:
        add_box(bm, uv_layer, 0.0, 0.0, 0.036, 0.046, 0.22, 3.96, "lapis_brick")


# ==============================================================================
# 8) KIT-ASSEMBLY, 4-LOD-EXPORT & MANIFEST-REGISTRIERUNG
# ==============================================================================

KIT_SPECS = [
    ("hero_ziggurat_ur",        build_hero_ziggurat_ur,        "Monumentale 3-Stufen-Ziggurat mit Dreifachtreppe, Torhaus, E-Nanna-Schrein & IvyGen-Terrassengaerten"),
    ("hero_abzu_pond",          build_hero_abzu_pond,          "Versenkter 3D-Abzu-Tempelteich (-0.50m Mosaikboden, Stufen, Wasserspeier, Papyrus, 3D-Lotos)"),
    ("abzu_water_surface",      build_abzu_water_surface,      "Separate reflektierende Wasseroberflaeche fuer hero_abzu_pond bei Z=+0.14m (0% Z-Fighting)"),
    ("hero_temple_annex_01",    build_hero_temple_annex_01,    "Tempel-Nebengebaeude 01 (Schatzhaus mit Pilastern, Zedern-Portikus, Dachpergola & Amphoren)"),
    ("hero_temple_annex_02",    build_hero_temple_annex_02,    "Tempel-Nebengebaeude 02 (Priester-/Archivhaus mit Kolonnade, Nischen & Dachpergola)"),
    ("hero_temenos_gate",       build_hero_temenos_gate,       "Temenos-Prunktor mit Doppeltuermen, Lapislazuli-Fries & offenen Bronze-Zederntoren"),
    ("hero_temenos_wall_seg",   build_hero_temenos_wall_seg,   "Temenos-Innenmauer-Modul (6m) mit Nischen, Zinnen, Fackelhalter & -0.35m Schuerze"),
    ("temple_planter_long",     build_temple_planter_long,     "Gemauertes Hochbeet (3.2m) mit Oleander, Granatapfel, Feige & Efeu"),
    ("temple_planter_corner",   build_temple_planter_corner,   "Gemauertes Eck-Hochbeet (1.6m) mit Oleander, Kraeutern & Efeu"),
    ("temple_tree_pomegranate", build_temple_tree_pomegranate, "Heiliger-Hain Granatapfelbaum (Sapling Tree Gen, 4 LODs)"),
    ("temple_tree_cypress",     build_temple_tree_cypress,     "Heiliger-Hain Tempel-Zypresse (Sapling Tree Gen, 4 LODs)"),
    ("temple_pergola_vine",     build_temple_pergola_vine,     "Zedern- & Schilf-Pergola mit echten IvyGen-Wein-/Efeuranken"),
    ("temple_altar_incense",    build_temple_altar_incense,    "Monumentaler Kalkstein-Hornaltar mit Bronze-Raeucherschale & gluehender Kohle"),
    ("temple_stele_01",         build_temple_stele_01,         "Sumerische Kalkstein-Stele mit Relief-Normalmap & Stufensockel"),
    ("temple_brazier_01",       build_temple_brazier_01,       "Freistehender Bronze-Feuerstaender mit gluehender Holzkohle"),
    ("temple_paving_slab",      build_temple_paving_slab,      "Abgeschraegtes Travertin-Prozessionspflaster (+0.04m, -0.12m Schuerze)"),
]


def create_asset_mesh(name, builder_fn, lod, mat_trim, mat_bot, mat_water):
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    builder_fn(bm, uv_layer, lod)
    if name != "hero_ziggurat_ur":
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    else:
        for f in bm.faces:
            f.normal_update()
    tri_count = sum(max(1, len(f.verts) - 2) for f in bm.faces)

    mesh_name = f"{name}_LOD{lod}"
    me = bpy.data.meshes.new(mesh_name)
    bm.to_mesh(me)
    bm.free()

    if name == "abzu_water_surface":
        me.materials.append(mat_water)
    else:
        me.materials.append(mat_trim)
        me.materials.append(mat_bot)

    obj = bpy.data.objects.new(mesh_name, me)
    bpy.context.collection.objects.link(obj)
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)
    return obj, tri_count


def export_kit_glb_and_blend(project_root, all_objs, tri_report):
    blend_dir = os.path.join(project_root, "assets", "blend", "city")
    glb_dir = os.path.join(project_root, "assets", "glb", "city")
    os.makedirs(blend_dir, exist_ok=True)
    os.makedirs(glb_dir, exist_ok=True)

    blend_path = os.path.join(blend_dir, "temenos_hero_kit.blend")
    glb_path = os.path.join(glb_dir, "temenos_hero_kit.glb")

    # Apply transforms cleanly on all kit objects
    bpy.ops.object.select_all(action="DESELECT")
    for o in all_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = all_objs[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    print(f"[TEMENOS KIT] Speichere Master-Blend: {blend_path}", flush=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    print(f"[TEMENOS KIT] Exportiere 4-LOD GLB (+Y Up): {glb_path}", flush=True)
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_materials="EXPORT",
        export_texcoords=True,
        export_normals=True,
        export_image_format="JPEG",
        export_jpeg_quality=88,
    )
    glb_kb = os.path.getsize(glb_path) / 1024.0
    print(f"[TEMENOS KIT] GLB exportiert: {glb_kb:.1f} KB ({glb_path})", flush=True)

    # Register in assets/manifest.json
    man_path = os.path.join(project_root, "assets", "manifest.json")
    if os.path.exists(man_path):
        with open(man_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        world_items = manifest.setdefault("categories", {}).setdefault("world", {}).setdefault("items", {})
        world_items["temenos_hero_kit"] = {
            "enabled": True,
            "url": "assets/glb/city/temenos_hero_kit.glb",
            "blend": "assets/blend/city/temenos_hero_kit.blend",
            "category": "world",
            "lods": ["LOD0", "LOD1", "LOD2", "LOD3"],
            "lodDistances": [150, 500, 1500, 3000],
            "sharedTextures": {
                "trim": [
                    "assets/textures/temenos_hero_trim_baseColor.png",
                    "assets/textures/temenos_hero_trim_normal.png",
                    "assets/textures/temenos_hero_trim_orm.png",
                    "assets/textures/temenos_hero_trim_emissive.png",
                ],
                "botany": [
                    "assets/textures/temenos_botany_atlas_baseColor.png",
                    "assets/textures/temenos_botany_atlas_normal.png",
                    "assets/textures/temenos_botany_atlas_orm.png",
                    "assets/textures/temenos_botany_atlas_thickness.png",
                ],
            },
            "modules": {
                name: {
                    "lods": tri_report[name],
                    "description": desc,
                }
                for name, _, desc in KIT_SPECS
            },
            "previews": [
                "assets/previews/temenos_hero_overview.png",
                "assets/previews/temenos_ziggurat_closeup.png",
                "assets/previews/temenos_abzu_pond_closeup.png",
                "assets/previews/temenos_garden_props_lineup.png",
                "assets/previews/ziggurat_axial_front.png",
                "assets/previews/ziggurat_axial_top.png",
                "assets/previews/ziggurat_walkability_front.png",
                "assets/previews/ziggurat_walkability_top.png",
                "assets/previews/ziggurat_shrine_gatehouse_closeup.png",
            ],
            "glbSizeKB": round(glb_kb, 1),
            "exportedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(man_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"[TEMENOS KIT] In assets/manifest.json registriert!", flush=True)
    return glb_kb


# ==============================================================================
# 9) 4 VERBINDLICHE CYCLES CUDA + AGX SHOWCASE-RENDERINGS
# ==============================================================================

def setup_showcase_cycles_agx(scene, samples=40):
    scene.render.engine = "CYCLES"
    used_gpu = False
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "CUDA"
        prefs.refresh_devices()
        if any(d.type == "CUDA" for d in prefs.devices):
            for d in prefs.devices:
                d.use = (d.type == "CUDA")
            scene.cycles.device = "GPU"
            used_gpu = True
    except Exception:
        pass
    if not used_gpu:
        scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    try:
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    scene.cycles.max_bounces = 6
    scene.cycles.diffuse_bounces = 3
    scene.cycles.glossy_bounces = 2
    scene.cycles.transmission_bounces = 4
    scene.cycles.transparent_max_bounces = 10

    scene.render.resolution_x = 1440
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"

    # Blender 4/5 AgX Color Management — balanced exposure for Blender 5.3 MULTIPLE_SCATTERING sky!
    scene.view_settings.view_transform = "AgX"
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        scene.view_settings.look = "None"
    scene.view_settings.exposure = -1.15
    scene.view_settings.gamma = 1.0

    # Golden Mesopotamian sky (physically balanced strength 0.16 -> rich warm shadows, zero white blowout!)
    world = bpy.data.worlds.new("Temenos_Sky")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    w_out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.16
    sky = nt.nodes.new("ShaderNodeTexSky")
    for st_name in ("MULTIPLE_SCATTERING", "NISHITA", "SINGLE_SCATTERING"):
        try:
            sky.sky_type = st_name
            break
        except Exception:
            pass
    sky.sun_disc = True
    sky.sun_elevation = math.radians(32.0)
    sky.sun_rotation = math.radians(142.0)
    if hasattr(sky, "air_density"):
        sky.air_density = 1.35
    if hasattr(sky, "dust_density"):
        sky.dust_density = 1.85
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], w_out.inputs["Surface"])

    return "CUDA (GPU)" if used_gpu else "CPU"


def _place_instance(src_obj, loc, rot_z=0.0, scale=1.0, col=None):
    inst = bpy.data.objects.new(f"Diorama_{src_obj.name}", src_obj.data)
    inst.location = loc
    inst.rotation_euler = (0.0, 0.0, rot_z)
    inst.scale = (scale, scale, scale)
    (col or bpy.context.collection).objects.link(inst)
    return inst


def _aim_camera(cam_obj, loc, target, lens=35.0):
    cam_obj.location = Vector(loc)
    direction = Vector(target) - Vector(loc)
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam_obj.data.lens = lens
    cam_obj.data.clip_start = 0.2
    cam_obj.data.clip_end = 500.0


def render_4_showcases(project_root, lod0_map):
    scene = bpy.context.scene
    dev = setup_showcase_cycles_agx(scene, samples=44)
    print(f"[TEMENOS SHOWCASE] Rendere 4 AgX-Showcases auf {dev}...", flush=True)

    # Hide raw origin-stacked kit assets from render
    for o in list(bpy.data.objects):
        o.hide_render = True
        o.hide_viewport = True

    diorama_col = bpy.data.collections.new("Temenos_Diorama")
    scene.collection.children.link(diorama_col)

    # Warm sandy-travertine courtyard ground plane at Z = 0.0 (with cutouts under the two Abzu ponds so you see the deep -0.50m basin!)
    g_mesh = bpy.data.meshes.new("Temenos_Ground")
    g_bm = bmesh.new()
    uv_g = g_bm.loops.layers.uv.new("UVMap")
    # Build courtyard ground grid with exact holes at (-8.5, -20.5) and (+9.5, -20.5) for the two 3.6x3.6m Abzu basins!
    # Local Temenos coords relative to Ziggurat center (0, 0):
    #   Ziggurat @ (0, 0), rotZ = pi -> front stairs face -Y!
    #   Abzu ponds @ (-8.5, -20.5) and (+9.5, -20.5) (exact Ur-Schinar offsets from zigX=210, zigY=-10!)
    #   Annex 01 @ (-15.5, -13.5), Annex 02 @ (-15.5, +12.5)
    #   Temenos Gate @ (-1.5, -28.0)
    pond_centers = [(-8.5, -20.5), (+9.5, -20.5)]
    xs = [-42.0, -10.3, -6.7, +7.7, +11.3, +42.0]
    ys = [-44.0, -22.3, -18.7, +36.0]
    for iy in range(len(ys) - 1):
        for ix in range(len(xs) - 1):
            cx = 0.5 * (xs[ix] + xs[ix + 1])
            cy = 0.5 * (ys[iy] + ys[iy + 1])
            if any(abs(cx - px) < 1.9 and abs(cy - py) < 1.9 for px, py in pond_centers):
                continue  # Leave clean cutout for the sunken 3D Abzu basin!
            v0 = g_bm.verts.new((xs[ix], ys[iy], 0.0))
            v1 = g_bm.verts.new((xs[ix + 1], ys[iy], 0.0))
            v2 = g_bm.verts.new((xs[ix + 1], ys[iy + 1], 0.0))
            v3 = g_bm.verts.new((xs[ix], ys[iy + 1], 0.0))
            f = g_bm.faces.new((v0, v1, v2, v3))
            for loop in f.loops:
                loop[uv_g].uv = (loop.vert.co.x * 0.12, loop.vert.co.y * 0.12)
    g_bm.to_mesh(g_mesh)
    g_bm.free()

    # Warm sandy courtyard material
    mat_g = bpy.data.materials.new("Mat_Courtyard_Sand")
    mat_g.use_nodes = True
    nt = mat_g.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    noi = nt.nodes.new("ShaderNodeTexNoise")
    noi.inputs["Scale"].default_value = 0.45
    noi.inputs["Detail"].default_value = 6.0
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].position = 0.25
    cr.color_ramp.elements[0].color = (0.42, 0.33, 0.21, 1.0)
    cr.color_ramp.elements[1].position = 0.78
    cr.color_ramp.elements[1].color = (0.56, 0.45, 0.30, 1.0)
    nt.links.new(noi.outputs["Fac"], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.88
    g_mesh.materials.append(mat_g)
    g_obj = bpy.data.objects.new("Temenos_Ground", g_mesh)
    diorama_col.objects.link(g_obj)

    # --- POPULATE FULL TEMENOS DIORAMA (1:1 Ur-Schinar Layout!) ---
    # 1. Hero Ziggurat at (0, 0), rotZ = pi (stairs facing -Y South toward Gate!)
    _place_instance(lod0_map["hero_ziggurat_ur"], (0.0, 0.0, 0.0), rot_z=math.pi, col=diorama_col)

    # 2. Both Abzu Temple Ponds + Separate Water Surface at (-8.5, -20.5) and (+9.5, -20.5)
    for px, py in pond_centers:
        _place_instance(lod0_map["hero_abzu_pond"], (px, py, 0.0), rot_z=0.0, col=diorama_col)
        _place_instance(lod0_map["abzu_water_surface"], (px, py, 0.0), rot_z=0.0, col=diorama_col)

    # 3. Both New Temple Annexes at (-15.5, -13.5) and (-15.5, +12.5)
    _place_instance(lod0_map["hero_temple_annex_01"], (-15.5, -13.5, 0.0), rot_z=0.0, col=diorama_col)
    _place_instance(lod0_map["hero_temple_annex_02"], (-15.5, +12.5, 0.0), rot_z=0.0, col=diorama_col)

    # 4. Grand Temenos Gate at (0.0, -28.0) + Flanking Inner Wall Segments
    _place_instance(lod0_map["hero_temenos_gate"], (0.0, -28.0, 0.0), rot_z=0.0, col=diorama_col)
    for wx in (-17.8, -11.8, -7.8, +7.8, +13.8, +19.0):
        _place_instance(lod0_map["hero_temenos_wall_seg"], (wx, -28.0, 0.0), rot_z=0.0, col=diorama_col)
    for wy in (-24.5, -18.5, -12.5, -6.5, -0.5, +5.5, +11.5, +17.5):
        _place_instance(lod0_map["hero_temenos_wall_seg"], (+20.5, wy, 0.0), rot_z=math.pi * 0.5, col=diorama_col)
    for wy in (-24.5, +19.5):
        _place_instance(lod0_map["hero_temenos_wall_seg"], (-21.0, wy, 0.0), rot_z=math.pi * 0.5, col=diorama_col)

    # 5. Processional Paving Slabs from Gate (-28) to Ziggurat Stairs (-13)
    for py in (-26.0, -22.0, -18.0, -14.2):
        _place_instance(lod0_map["temple_paving_slab"], (0.0, py, 0.0), rot_z=0.0, col=diorama_col)

    # 6. Monumental Forecourt Horned Incense Altar, Steles & Bronze Braziers along Processional Way
    _place_instance(lod0_map["temple_altar_incense"], (0.0, -17.8, 0.0), rot_z=0.0, col=diorama_col)
    for sx in (-3.2, +3.2):
        _place_instance(lod0_map["temple_brazier_01"], (sx, -14.4, 0.0), col=diorama_col)
        _place_instance(lod0_map["temple_brazier_01"], (sx, -23.5, 0.0), col=diorama_col)
        _place_instance(lod0_map["temple_stele_01"], (sx * 1.15, -19.2, 0.0), rot_z=(0.35 if sx < 0 else -0.35), col=diorama_col)

    # 7. Lush Gardens: Raised Planters, Vine Pergolas, Sapling Pomegranate & Cypress Trees!
    for tx, ty, rz in [
        (-8.5, -24.8, 0.0), (+9.5, -24.8, 0.0),
        (+15.5, -18.0, math.pi * 0.5), (+15.5, -11.0, math.pi * 0.5),
    ]:
        _place_instance(lod0_map["temple_planter_long"], (tx, ty, 0.0), rot_z=rz, col=diorama_col)
    for tx, ty in [(-15.5, -25.0), (+16.5, -25.0), (-11.0, -14.5), (+12.5, -14.5)]:
        _place_instance(lod0_map["temple_planter_corner"], (tx, ty, 0.0), col=diorama_col)
    # Vine Pergolas framing the east & west sacred garden
    _place_instance(lod0_map["temple_pergola_vine"], (+15.8, -14.5, 0.0), rot_z=math.pi * 0.5, col=diorama_col)
    _place_instance(lod0_map["temple_pergola_vine"], (+15.8, -4.5, 0.0), rot_z=math.pi * 0.5, col=diorama_col)
    # Sapling Pomegranate Trees
    for tx, ty, sc in [(-12.2, -24.5, 1.0), (+13.8, -24.2, 1.05), (-10.8, -5.5, 0.95), (+14.2, +2.0, 1.02)]:
        _place_instance(lod0_map["temple_tree_pomegranate"], (tx, ty, 0.0), rot_z=tx, scale=sc, col=diorama_col)
    # Tall Sacred Temple Cypresses framing the precinct
    for tx, ty, sc in [(-18.5, -25.2, 1.0), (+18.2, -25.2, 1.05), (+17.5, +11.5, 1.10), (-18.5, +2.0, 0.95), (+17.5, -8.0, 0.98)]:
        _place_instance(lod0_map["temple_tree_cypress"], (tx, ty, 0.0), rot_z=ty, scale=sc, col=diorama_col)

    # Create Camera
    cam_data = bpy.data.cameras.new("ShowcaseCam")
    cam_obj = bpy.data.objects.new("ShowcaseCam", cam_data)
    diorama_col.objects.link(cam_obj)
    scene.camera = cam_obj

    prev_dir = os.path.join(project_root, "assets", "previews")
    os.makedirs(prev_dir, exist_ok=True)

    # --- RENDER 1: OVERVIEW ---
    _aim_camera(cam_obj, (+26.0, -44.0, 26.0), (-1.0, -10.5, 3.8), lens=32.0)
    p1 = os.path.join(prev_dir, "temenos_hero_overview.png")
    scene.render.filepath = p1
    print(f"[TEMENOS SHOWCASE] 1/4 Rendere {p1}...", flush=True)
    bpy.ops.render.render(write_still=True)

    # --- RENDER 2: ZIGGURAT CLOSEUP (full summit shrine + standards + braziers + triple stairs + hanging gardens!) ---
    _aim_camera(cam_obj, (+17.5, -28.5, 11.8), (0.0, -2.0, 6.8), lens=34.0)
    p2 = os.path.join(prev_dir, "temenos_ziggurat_closeup.png")
    scene.render.filepath = p2
    print(f"[TEMENOS SHOWCASE] 2/4 Rendere {p2}...", flush=True)
    bpy.ops.render.render(write_still=True)

    # --- RENDER 3: ABZU POND CLOSEUP ---
    _aim_camera(cam_obj, (-4.2, -16.8, 3.2), (-8.5, -20.5, 0.2), lens=38.0)
    p3 = os.path.join(prev_dir, "temenos_abzu_pond_closeup.png")
    scene.render.filepath = p3
    print(f"[TEMENOS SHOWCASE] 3/4 Rendere {p3}...", flush=True)
    bpy.ops.render.render(write_still=True)

    # --- RENDER 4: GARDEN & ANNEX PROPS LINEUP ---
    # Hide diorama temporarily and build clean studio lineup!
    for o in diorama_col.objects:
        if o != cam_obj:
            o.hide_render = True
    lineup_col = bpy.data.collections.new("Temenos_Lineup")
    scene.collection.children.link(lineup_col)

    # Flat warm studio floor
    bpy.ops.mesh.primitive_plane_add(size=80.0, location=(0.0, 0.0, 0.0))
    fl = bpy.context.active_object
    fl.data.materials.append(mat_g)
    lineup_col.objects.link(fl)
    bpy.context.collection.objects.unlink(fl)

    # Back row: Annex 01, Annex 02, Temenos Gate, Vine Pergola
    _place_instance(lod0_map["hero_temple_annex_01"], (-12.5, +6.0, 0.0), rot_z=-math.pi * 0.5, col=lineup_col)
    _place_instance(lod0_map["hero_temple_annex_02"], ( +0.5, +6.0, 0.0), rot_z=-math.pi * 0.5, col=lineup_col)
    _place_instance(lod0_map["temple_pergola_vine"],  (+11.0, +4.5, 0.0), rot_z=0.0, col=lineup_col)
    # Front row: Cypress, Pomegranate, Long Planter, Corner Planter, Altar, Stele, Brazier, Paving Slab
    _place_instance(lod0_map["temple_tree_cypress"],     (-11.5, -3.5, 0.0), col=lineup_col)
    _place_instance(lod0_map["temple_tree_pomegranate"], ( -7.8, -3.5, 0.0), col=lineup_col)
    _place_instance(lod0_map["temple_planter_long"],     ( -3.5, -3.5, 0.0), col=lineup_col)
    _place_instance(lod0_map["temple_planter_corner"],   ( +0.5, -3.5, 0.0), col=lineup_col)
    _place_instance(lod0_map["temple_altar_incense"],    ( +3.6, -3.5, 0.0), col=lineup_col)
    _place_instance(lod0_map["temple_stele_01"],         ( +6.2, -3.5, 0.0), col=lineup_col)
    _place_instance(lod0_map["temple_brazier_01"],       ( +8.2, -3.5, 0.0), col=lineup_col)
    _place_instance(lod0_map["temple_paving_slab"],      ( +3.6, -7.2, 0.0), col=lineup_col)

    _aim_camera(cam_obj, (-1.8, -25.5, 9.0), (-1.2, +0.5, 2.5), lens=30.0)
    p4 = os.path.join(prev_dir, "temenos_garden_props_lineup.png")
    scene.render.filepath = p4
    print(f"[TEMENOS SHOWCASE] 4/4 Rendere {p4}...", flush=True)
    bpy.ops.render.render(write_still=True)
    print("[TEMENOS SHOWCASE] Alle 4 Showcase-Renderings abgeschlossen!", flush=True)


def _create_human_scale_figure(name, loc, rot_z, mat_body, mat_head, col):
    """Schlichte 1.78m-Massstabsfigur (NUR fuer Kontrollrenderings, NIEMALS im GLB-Export!)."""
    bm = bmesh.new()
    # Base plinth/boots (0.00 .. 0.08m), legs (0.08 .. 0.88m), tunic torso (0.88 .. 1.46m),
    # shoulders/arms (1.02 .. 1.42m), neck (1.46 .. 1.54m), head (1.54 .. 1.78m -> exakt 1.78m!)
    def _cyl(cx, cy, z0, z1, r0, r1, segs=12, mat_i=0):
        bot = [bm.verts.new((cx + math.cos(2*math.pi*i/segs)*r0, cy + math.sin(2*math.pi*i/segs)*r0, z0)) for i in range(segs)]
        top = [bm.verts.new((cx + math.cos(2*math.pi*i/segs)*r1, cy + math.sin(2*math.pi*i/segs)*r1, z1)) for i in range(segs)]
        for i in range(segs):
            j = (i + 1) % segs
            f = bm.faces.new((bot[i], bot[j], top[j], top[i]))
            f.material_index = mat_i
            f.smooth = True
        ft = bm.faces.new(top)
        ft.material_index = mat_i
        fb = bm.faces.new(list(reversed(bot)))
        fb.material_index = mat_i

    # Legs / robe lower half
    _cyl(-0.09, 0.0, 0.00, 0.88, 0.075, 0.085, 10, 0)
    _cyl(+0.09, 0.0, 0.00, 0.88, 0.075, 0.085, 10, 0)
    # Sumerian robe / torso
    _cyl(0.0, 0.0, 0.42, 1.44, 0.21, 0.19, 14, 0)
    # Shoulders & hanging arms
    _cyl(-0.23, 0.0, 0.84, 1.40, 0.055, 0.065, 8, 0)
    _cyl(+0.23, 0.0, 0.84, 1.40, 0.055, 0.065, 8, 0)
    # Neck & head (top exact at Z = 1.78 m!)
    _cyl(0.0, 0.0, 1.44, 1.54, 0.06, 0.055, 10, 1)
    bmesh.ops.create_uvsphere(bm, u_segments=14, v_segments=10, radius=0.12,
                              matrix=Matrix.Translation((0.0, 0.0, 1.66)))
    for f in bm.faces:
        if all(v.co.z >= 1.53 for v in f.verts):
            f.material_index = 1
            f.smooth = True

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat_body)
    me.materials.append(mat_head)
    obj = bpy.data.objects.new(name, me)
    obj.location = Vector(loc)
    obj.rotation_euler = (0.0, 0.0, rot_z)
    col.objects.link(obj)
    return obj


def render_ziggurat_walkability_previews(project_root, lod0_map):
    """Rendert die verbindlichen Ziggurat-Axial-Kontrollrenderings (Cycles CUDA + AgX):
    ziggurat_axial_front.png & ziggurat_axial_top.png."""
    scene = bpy.context.scene
    dev = setup_showcase_cycles_agx(scene, samples=44)
    print(f"[ZIGGURAT PREVIEW] Rendere Axial-Kontrollbilder auf {dev}...", flush=True)

    # Hide all raw exported kit objects
    for o in list(bpy.data.objects):
        o.hide_render = True
        o.hide_viewport = True

    prev_col = bpy.data.collections.new("Ziggurat_Walkability_Preview")
    scene.collection.children.link(prev_col)

    # Clean sandy courtyard floor at Z = 0.0
    bpy.ops.mesh.primitive_plane_add(size=120.0, location=(0.0, 0.0, 0.0))
    fl = bpy.context.active_object
    fl.name = "Walkability_Ground"
    mat_g = bpy.data.materials.new("Mat_Walk_Sand")
    mat_g.use_nodes = True
    nt = mat_g.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (0.48, 0.39, 0.26, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.90
    fl.data.materials.append(mat_g)
    prev_col.objects.link(fl)
    bpy.context.collection.objects.unlink(fl)

    # Place hero_ziggurat_ur LOD0 at origin (0,0,0), rotZ = 0 (+Y faces front!)
    _place_instance(lod0_map["hero_ziggurat_ur"], (0.0, 0.0, 0.0), rot_z=0.0, col=prev_col)
    # Place 2 processional paving slabs right in front of the central staircase foot (Y = +13.80)
    _place_instance(lod0_map["temple_paving_slab"], (0.0, 15.80, 0.0), rot_z=0.0, col=prev_col)
    _place_instance(lod0_map["temple_paving_slab"], (0.0, 19.80, 0.0), rot_z=0.0, col=prev_col)

    # Sun angled from front-right (+X, +Y) so front stairs, gatehouse portals, axial stairs & shrine portal are crisply modeled!
    if scene.world and scene.world.use_nodes:
        for n in scene.world.node_tree.nodes:
            if n.type == "TEX_SKY":
                n.sun_elevation = math.radians(34.0)
                n.sun_rotation = math.radians(-38.0)

    cam_data = bpy.data.cameras.new("WalkCam")
    cam_obj = bpy.data.objects.new("WalkCam", cam_data)
    prev_col.objects.link(cam_obj)
    scene.camera = cam_obj

    prev_dir = os.path.join(project_root, "assets", "previews")
    os.makedirs(prev_dir, exist_ok=True)

    # --- RENDER 1: OBLIQUE FRONT VIEW (Full Extended Ziggurat + Symmetric Lateral Stairs + Axial Stairs 1/2/3 + Summit Shrine) ---
    _aim_camera(cam_obj, (+19.5, +28.5, 13.5), (0.0, -1.2, 5.8), lens=32.0)
    p1 = os.path.join(prev_dir, "ziggurat_axial_front.png")
    scene.render.filepath = p1
    print(f"[ZIGGURAT PREVIEW] 1/2 Rendere {p1}...", flush=True)
    bpy.ops.render.render(write_still=True)

    # --- RENDER 2: STEEP TOP-DOWN AXIAL VIEW (All 3 Axial Stairs on X=0 + Symmetric Side Stairs + Podeste + Summit Forecourt) ---
    _aim_camera(cam_obj, (+3.2, +22.0, 32.5), (0.0, -1.8, 4.8), lens=30.0)
    p2 = os.path.join(prev_dir, "ziggurat_axial_top.png")
    scene.render.filepath = p2
    print(f"[ZIGGURAT PREVIEW] 2/2 Rendere {p2}...", flush=True)
    bpy.ops.render.render(write_still=True)

    print("[ZIGGURAT PREVIEW] Beide Axial-Kontrollbilder (ziggurat_axial_front.png & ziggurat_axial_top.png) fertig!", flush=True)


def main():
    t0 = time.time()
    root = get_project_root()
    print("[TEMENOS KIT] Starte Bau des Hero-Tempelbezirk-Kits (Ur-Schinar, Ziggurat-Rework)...", flush=True)
    clear_scene()
    enable_addons()

    mat_trim, mat_bot, mat_water = build_shared_materials(root)

    all_objs = []
    lod0_map = {}
    tri_report = {}

    for name, builder_fn, desc in KIT_SPECS:
        tri_report[name] = {}
        for lod in (0, 1, 2, 3):
            obj, tris = create_asset_mesh(name, builder_fn, lod, mat_trim, mat_bot, mat_water)
            all_objs.append(obj)
            tri_report[name][f"LOD{lod}"] = tris
            if lod == 0:
                lod0_map[name] = obj
        r = tri_report[name]
        print(f"[TEMENOS KIT] {name:26s} | LOD0={r['LOD0']:6d} | LOD1={r['LOD1']:5d} | LOD2={r['LOD2']:4d} | LOD3={r['LOD3']:3d}", flush=True)

    glb_kb = export_kit_glb_and_blend(root, all_objs, tri_report)
    render_ziggurat_walkability_previews(root, lod0_map)
    print(f"[TEMENOS KIT] FERTIG in {time.time() - t0:.1f}s | GLB={glb_kb:.1f} KB", flush=True)


if __name__ == "__main__":
    main()
