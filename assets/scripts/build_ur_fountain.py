"""
build_ur_fountain.py — Detaillierter Sumerischer Marktplatzbrunnen (ur_fountain_hero.glb)
==========================================================================================
Erzeugt den hero-detaillierten mesopotamischen Marktplatzbrunnen aus gebranntem Ziegel,
feuchtem Kapillarsockel, abgetrepptem Kalksteinrand, 4 Schoepf-Nischen, Zentral-Wasserspeier
mit Zinnbronze-Auslaessen, Terrakotta-Wasserkroegen und belebter Blender-Wasseroberflaeche:

  - Material 0: Mat_Mesopotamia_City_Trim (shared city_trim_atlas_{baseColor,normal,orm}.png)
  - Material 1: Mat_Ur_Fountain_Water     (water_blender_normal_{a,b}.png + water_blender_foam.png)
  - LODs:       ur_fountain_hero_LOD0 + ur_fountain_hero_LOD1 (beide in ur_fountain_hero.glb)
  - Origin:     (0, 0, 0) auf Platz-Niveau mit -0.30 m Fundament-Sockel

Exportiert:
  - assets/blend/world/ur_fountain_hero.blend
  - assets/glb/world/ur_fountain_hero.glb
  - assets/manifest.json (categories.world.items.ur_fountain_hero)

Aufruf:
  blender --background --python-exit-code 1 --python assets/scripts/build_ur_fountain.py
"""

import os
import sys
import math
import time
import json
import datetime
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler


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


# Exakte Unter-Regionen innerhalb city_trim_atlas fuer sauberes Stein-/Ziegel-/Bronze-Mapping
FOUNTAIN_UV = {
    "limestone":   (0.050, 0.008, 0.950, 0.029),  # Sauber behauener Kalkstein-Randblock (Band 0 Curb)
    "limestone_b": (0.050, 0.139, 0.950, 0.158),  # Zweiter Kalkstein-Streifen (Band 0 oberer Curb)
    "wet_stone":   (0.050, 0.215, 0.950, 0.305),  # Dunkles Kalk-/Basalt-Beckenpflaster (Band 1 Mitte)
    "damp_brick":  TRIM_REGIONS["damp_plinth"],   # Feuchter Ziegelsockel inkl. Kapillar-Linie & Bitumen
    "fired_brick": TRIM_REGIONS["fired_brick_upper"],  # Gebrannter sumerischer Terrakotta-Ziegel
    "gypsum":      TRIM_REGIONS["gypsum_temple"], # Helle geschnitzte sumerische Nischen-Verkleidung
    "lapis":       TRIM_REGIONS["lapis_frieze"],  # Lapislazuli-Rosettenband am Zentralspeier
    "bronze":      TRIM_REGIONS["tin_bronze"],    # Zinnbronze-Wasserspeier
    "terracotta":  (0.080, 0.605, 0.850, 0.678),  # Warmer gebrannter Ton fuer Wasserkroege
}


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    return scene


def create_city_trim_material(tex_dir):
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
            raise FileNotFoundError(f"City-Trim-Textur fehlt: {p}")

    img_c = bpy.data.images.load(p_col, check_existing=True); img_c.colorspace_settings.name = "sRGB"
    img_n = bpy.data.images.load(p_nrm, check_existing=True); img_n.colorspace_settings.name = "Non-Color"
    img_o = bpy.data.images.load(p_orm, check_existing=True); img_o.colorspace_settings.name = "Non-Color"

    tc = nt.nodes.new("ShaderNodeTexImage"); tc.image = img_c
    tn = nt.nodes.new("ShaderNodeTexImage"); tn.image = img_n
    to = nt.nodes.new("ShaderNodeTexImage"); to.image = img_o

    nrm_map = nt.nodes.new("ShaderNodeNormalMap")
    nrm_map.inputs["Strength"].default_value = 0.88
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


def create_fountain_water_material(tex_dir):
    """Spiegelndes, belebtes Brunnenwasser mit Blenders Normal A/B & Gischt-Schaum-Map."""
    mat = bpy.data.materials.new("Mat_Ur_Fountain_Water")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.055
    bsdf.inputs["IOR"].default_value = 1.333
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.65
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.30
        bsdf.inputs["Coat Roughness"].default_value = 0.03
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    p_na = os.path.join(tex_dir, "water_blender_normal_a.png")
    p_nb = os.path.join(tex_dir, "water_blender_normal_b.png")
    p_fm = os.path.join(tex_dir, "water_blender_foam.png")
    for p in (p_na, p_nb, p_fm):
        if not os.path.isfile(p):
            raise FileNotFoundError(f"Wasser-Textur fehlt: {p} (zuerst build_terrain_water_maps.py ausfuehren!)")

    img_na = bpy.data.images.load(p_na, check_existing=True); img_na.colorspace_settings.name = "Non-Color"
    img_nb = bpy.data.images.load(p_nb, check_existing=True); img_nb.colorspace_settings.name = "Non-Color"
    img_fm = bpy.data.images.load(p_fm, check_existing=True); img_fm.colorspace_settings.name = "Non-Color"

    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp_a = nt.nodes.new("ShaderNodeMapping"); mp_a.inputs["Scale"].default_value = (1.6, 1.6, 1.0)
    mp_b = nt.nodes.new("ShaderNodeMapping"); mp_b.inputs["Scale"].default_value = (2.3, 2.3, 1.0); mp_b.inputs["Rotation"].default_value = (0.0, 0.0, 0.55)
    mp_f = nt.nodes.new("ShaderNodeMapping"); mp_f.inputs["Scale"].default_value = (2.8, 2.8, 1.0)
    nt.links.new(tc.outputs["UV"], mp_a.inputs["Vector"])
    nt.links.new(tc.outputs["UV"], mp_b.inputs["Vector"])
    nt.links.new(tc.outputs["UV"], mp_f.inputs["Vector"])

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
    nrm.inputs["Strength"].default_value = 0.55
    nt.links.new(mix_n.outputs["Result"], nrm.inputs["Color"])
    nt.links.new(nrm.outputs["Normal"], bsdf.inputs["Normal"])

    # Vertex-Color Col_Foam (R = Gischt-Gewicht um Zentralspeier & Beckenrand)
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "Col_Foam"
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(attr.outputs["Color"], sep.inputs["Color"])

    mul_f = nt.nodes.new("ShaderNodeMath"); mul_f.operation = "MULTIPLY"
    nt.links.new(sep.outputs["Red"], mul_f.inputs[0])
    nt.links.new(t_fm.outputs["Color"], mul_f.inputs[1])

    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["From Min"].default_value = 0.06
    ramp.inputs["From Max"].default_value = 0.52
    ramp.inputs["To Min"].default_value = 0.0
    ramp.inputs["To Max"].default_value = 0.90
    nt.links.new(mul_f.outputs["Value"], ramp.inputs["Value"])

    mix_c = nt.nodes.new("ShaderNodeMix"); mix_c.data_type = "RGBA"
    mix_c.inputs["A"].default_value = (0.048, 0.165, 0.155, 1.0)  # Tiefes kristallklares Tuirkis-Teal
    mix_c.inputs["B"].default_value = (0.64, 0.64, 0.60, 1.0)     # Organischer Schaum
    nt.links.new(ramp.outputs["Result"], mix_c.inputs["Factor"])
    nt.links.new(mix_c.outputs["Result"], bsdf.inputs["Base Color"])

    mix_r = nt.nodes.new("ShaderNodeMapRange")
    mix_r.inputs["From Min"].default_value = 0.0
    mix_r.inputs["From Max"].default_value = 0.9
    mix_r.inputs["To Min"].default_value = 0.055
    mix_r.inputs["To Max"].default_value = 0.58
    nt.links.new(ramp.outputs["Result"], mix_r.inputs["Value"])
    nt.links.new(mix_r.outputs["Result"], bsdf.inputs["Roughness"])

    return mat


# ==============================================================================
# BMESH BAUKASTEN (SAUBERE BOX-UVs, SEKTOREN & TONKRUEGE)
# ==============================================================================

def _uv_box(bm, uv_layer, faces, region_key, scale_u=0.45, scale_v=1.0, mat_index=0):
    u0, v0, u1, v1 = FOUNTAIN_UV[region_key]
    du = u1 - u0
    dv = v1 - v0
    for f in faces:
        f.material_index = mat_index
        f.smooth = False
        n = f.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        zs = [lp.vert.co.z for lp in f.loops]
        zmin, zmax = min(zs), max(zs)
        zspan = max(0.05, zmax - zmin)
        for lp in f.loops:
            p = lp.vert.co
            if az >= ax and az >= ay:
                tu = (p.x * scale_u) % 1.0
                tv = (p.y * scale_u) % 1.0
            elif ax >= ay:
                tu = (p.y * scale_u) % 1.0
                tv = ((p.z - zmin) / zspan) if scale_v <= 0.0 else ((p.z * scale_v) % 1.0)
            else:
                tu = (p.x * scale_u) % 1.0
                tv = ((p.z - zmin) / zspan) if scale_v <= 0.0 else ((p.z * scale_v) % 1.0)
            if scale_v <= 0.0:
                tv = max(0.02, min(0.98, tv))
            else:
                tv = 0.04 + 0.92 * tv
            lp[uv_layer].uv = (u0 + tu * du, v0 + tv * dv)


def _add_prism_ring(bm, uv_layer, r_in, r_out, z0, z1, segs, region_key, scale_u=0.45, scale_v=0.0, rot_offset=0.0):
    """Erzeugt einen geschlossenen polygonalen Mauer-/Stufenring mit sauberem UV-Mapping."""
    verts_bot_in = []
    verts_bot_out = []
    verts_top_in = []
    verts_top_out = []
    for i in range(segs):
        ang = rot_offset + (i / segs) * 2.0 * math.pi
        ca, sa = math.cos(ang), math.sin(ang)
        verts_bot_in.append(bm.verts.new((ca * r_in, sa * r_in, z0)))
        verts_bot_out.append(bm.verts.new((ca * r_out, sa * r_out, z0)))
        verts_top_in.append(bm.verts.new((ca * r_in, sa * r_in, z1)))
        verts_top_out.append(bm.verts.new((ca * r_out, sa * r_out, z1)))

    new_faces = []
    u0, v0, u1, v1 = FOUNTAIN_UV[region_key]
    du, dv = u1 - u0, v1 - v0
    for i in range(segs):
        j = (i + 1) % segs
        f_out = bm.faces.new((verts_bot_out[i], verts_bot_out[j], verts_top_out[j], verts_top_out[i]))
        f_in  = bm.faces.new((verts_bot_in[j], verts_bot_in[i], verts_top_in[i], verts_top_in[j]))
        f_top = bm.faces.new((verts_top_in[i], verts_top_out[i], verts_top_out[j], verts_top_in[j]))
        f_bot = bm.faces.new((verts_bot_out[i], verts_bot_in[i], verts_bot_in[j], verts_bot_out[j]))
        for f in (f_out, f_in, f_top, f_bot):
            f.material_index = 0
            f.smooth = False
            new_faces.append(f)

        # Sauberes zylindrisches UV entlang des Ring-Umfangs
        ang0 = (i / segs) * 2.0 * math.pi * r_out * scale_u
        ang1 = ((i + 1) / segs) * 2.0 * math.pi * r_out * scale_u
        ua = u0 + (ang0 % 1.0) * du
        ub = u0 + (ang1 % 1.0) * du
        if ub < ua:
            ub += du * 0.25
        va, vb = v0 + 0.04 * dv, v0 + 0.96 * dv
        for lp, uv in zip(f_out.loops, [(ua, va), (ub, va), (ub, vb), (ua, vb)]):
            lp[uv_layer].uv = uv
        for lp, uv in zip(f_in.loops, [(ub, va), (ua, va), (ua, vb), (ub, vb)]):
            lp[uv_layer].uv = uv
        for lp, uv in zip(f_top.loops, [(ua, va), (ua, vb), (ub, vb), (ub, va)]):
            lp[uv_layer].uv = uv
        for lp, uv in zip(f_bot.loops, [(ua, va), (ua, vb), (ub, vb), (ub, va)]):
            lp[uv_layer].uv = uv
    return new_faces


def _add_arc_ring(bm, uv_layer, r_in, r_out, z0, z1, a_start, a_end, segs, region_key, scale_u=0.50):
    """Erzeugt ein wasserdichtes Ring-Sektorstueck ohne Gehrungs-Luecken entlang der Kruemmung."""
    u0, v0, u1, v1 = FOUNTAIN_UV[region_key]
    du, dv = u1 - u0, v1 - v0
    va, vb = v0 + 0.04 * dv, v0 + 0.96 * dv

    bi, bo, ti, to = [], [], [], []
    angs = []
    for i in range(segs + 1):
        a = a_start + (i / segs) * (a_end - a_start)
        angs.append(a)
        ca, sa = math.cos(a), math.sin(a)
        bi.append(bm.verts.new((ca * r_in,  sa * r_in,  z0)))
        bo.append(bm.verts.new((ca * r_out, sa * r_out, z0)))
        ti.append(bm.verts.new((ca * r_in,  sa * r_in,  z1)))
        to.append(bm.verts.new((ca * r_out, sa * r_out, z1)))

    new_faces = []
    for i in range(segs):
        j = i + 1
        f_out = bm.faces.new((bo[i], bo[j], to[j], to[i]))
        f_in  = bm.faces.new((bi[j], bi[i], ti[i], ti[j]))
        f_top = bm.faces.new((ti[i], to[i], to[j], ti[j]))
        f_bot = bm.faces.new((bo[i], bi[i], bi[j], bo[j]))
        ua = u0 + ((angs[i] * r_out * scale_u) % 0.85) * du
        ub = min(u1 - 0.02 * du, ua + ((angs[j] - angs[i]) * r_out * scale_u) * du)
        for f in (f_out, f_in, f_top, f_bot):
            f.material_index = 0
            f.smooth = False
            new_faces.append(f)
        for lp, uv in zip(f_out.loops, [(ua, va), (ub, va), (ub, vb), (ua, vb)]):
            lp[uv_layer].uv = uv
        for lp, uv in zip(f_in.loops, [(ub, va), (ua, va), (ua, vb), (ub, vb)]):
            lp[uv_layer].uv = uv
        for lp, uv in zip(f_top.loops, [(ua, va), (ua, vb), (ub, vb), (ub, va)]):
            lp[uv_layer].uv = uv
        for lp, uv in zip(f_bot.loops, [(ua, va), (ua, vb), (ub, vb), (ub, va)]):
            lp[uv_layer].uv = uv

    # Endkappen schliessen
    f_c0 = bm.faces.new((bi[0], bo[0], to[0], ti[0]))
    f_c1 = bm.faces.new((bo[-1], bi[-1], ti[-1], to[-1]))
    for f in (f_c0, f_c1):
        f.material_index = 0
        f.smooth = False
        for lp, uv in zip(f.loops, [(u0 + 0.05 * du, va), (u0 + 0.35 * du, va), (u0 + 0.35 * du, vb), (u0 + 0.05 * du, vb)]):
            lp[uv_layer].uv = uv
        new_faces.append(f)
    return new_faces


def _add_box_xform(bm, uv_layer, sx, sy, sz, matrix, region_key, scale_u=0.5, scale_v=0.0):
    ret = bmesh.ops.create_cube(bm, size=1.0)
    verts = ret["verts"]
    s_mat = Matrix.Diagonal((sx, sy, sz, 1.0))
    bmesh.ops.transform(bm, matrix=matrix @ s_mat, verts=verts)
    faces = list({f for v in verts for f in v.link_faces})
    _uv_box(bm, uv_layer, faces, region_key, scale_u=scale_u, scale_v=scale_v, mat_index=0)
    return faces


def _add_cylinder_xform(bm, uv_layer, r_bot, r_top, depth, segs, matrix, region_key, scale_u=0.5, scale_v=0.0, smooth=True):
    ret = bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segs,
        radius1=r_bot,
        radius2=r_top,
        depth=depth,
    )
    verts = ret["verts"]
    bmesh.ops.transform(bm, matrix=matrix, verts=verts)
    faces = list({f for v in verts for f in v.link_faces})
    _uv_box(bm, uv_layer, faces, region_key, scale_u=scale_u, scale_v=scale_v, mat_index=0)
    if smooth:
        for f in faces:
            f.smooth = True
    return faces


def _add_clay_jug(bm, uv_layer, pos, rot_euler, scale=1.0, segs=14, with_handle=True):
    """Gedrechselter mesopotamischer Terrakotta-Wasserkrug mit Standring, Bauch, Hals & Henkel."""
    # Profil (radius, z) in Metern
    profile = [
        (0.065, 0.000),
        (0.075, 0.020),
        (0.145, 0.110),
        (0.165, 0.210),
        (0.130, 0.300),
        (0.062, 0.355),
        (0.056, 0.415),
        (0.082, 0.450),
        (0.072, 0.458),
    ]
    xform = Matrix.Translation(pos) @ rot_euler.to_matrix().to_4x4() @ Matrix.Scale(scale, 4)

    rings = []
    for r, z in profile:
        ring = []
        for i in range(segs):
            ang = (i / segs) * 2.0 * math.pi
            co = xform @ Vector((math.cos(ang) * r, math.sin(ang) * r, z))
            ring.append(bm.verts.new(co))
        rings.append(ring)

    u0, v0, u1, v1 = FOUNTAIN_UV["terracotta"]
    du, dv = u1 - u0, v1 - v0
    jug_faces = []
    for r_idx in range(len(rings) - 1):
        ra, rb = rings[r_idx], rings[r_idx + 1]
        va = v0 + (r_idx / (len(rings) - 1)) * dv
        vb = v0 + ((r_idx + 1) / (len(rings) - 1)) * dv
        for i in range(segs):
            j = (i + 1) % segs
            f = bm.faces.new((ra[i], ra[j], rb[j], rb[i]))
            f.material_index = 0
            f.smooth = True
            ua = u0 + (i / segs) * du
            ub = u0 + ((i + 1) / segs) * du
            for lp, uv in zip(f.loops, [(ua, va), (ub, va), (ub, vb), (ua, vb)]):
                lp[uv_layer].uv = uv
            jug_faces.append(f)

    # Boden & Oeffnungs-Deckel (leicht vertieft)
    f_bot = bm.faces.new(rings[0][::-1])
    f_top = bm.faces.new(rings[-1])
    for f in (f_bot, f_top):
        f.material_index = 0
        for lp in f.loops:
            lp[uv_layer].uv = (u0 + 0.5 * du, v0 + 0.15 * dv)

    if with_handle:
        # Geschwungener Henkel zwischen Schulter (z=0.25) und Halsrand (z=0.42)
        h_pts = [
            Vector((0.140, 0.0, 0.255)),
            Vector((0.205, 0.0, 0.305)),
            Vector((0.195, 0.0, 0.375)),
            Vector((0.068, 0.0, 0.415)),
        ]
        for k in range(len(h_pts) - 1):
            p0 = xform @ h_pts[k]
            p1 = xform @ h_pts[k + 1]
            mid = 0.5 * (p0 + p1)
            vec = p1 - p0
            length = max(0.01, vec.length)
            quat = vec.normalized().to_track_quat("Z", "Y")
            hm = Matrix.Translation(mid) @ quat.to_matrix().to_4x4()
            _add_cylinder_xform(bm, uv_layer, 0.017 * scale, 0.017 * scale, length * 1.15, 6, hm, "terracotta", smooth=True)


def build_fountain_mesh(lod=0):
    """
    Erstellt den sumerischen Marktplatzbrunnen als bmesh (Material 0 = City Trim, Material 1 = Water).
    Origin = (0, 0, 0), Fundament-Sockel bis Z = -0.30 m.
    """
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    foam_layer = bm.loops.layers.color.new("Col_Foam")

    segs = 20 if lod == 0 else 12
    n_sides = 16 if lod == 0 else 12

    # 1. Fundament-Sockel (Z = -0.30 .. +0.06 m) + abgetreppte Kalkstein-Plinthe (Z = +0.06 .. +0.18 m)
    _add_prism_ring(bm, uv_layer, 1.45, 2.38, -0.30, 0.06, n_sides, "wet_stone", scale_u=0.38)
    _add_prism_ring(bm, uv_layer, 1.50, 2.18,  0.06, 0.18, n_sides, "limestone", scale_u=0.45)

    # 2. Becken-Boden (nasses dunkles Pflaster auf Z = +0.18 m)
    _add_cylinder_xform(bm, uv_layer, 1.62, 1.62, 0.24, n_sides, Matrix.Translation((0.0, 0.0, 0.06)), "wet_stone", scale_u=0.45, smooth=False)

    # 3. Feuchter unterer Ziegelsockel mit Kapillar-Linie & Bitumen-Basis (Z = +0.18 .. +0.40 m)
    _add_prism_ring(bm, uv_layer, 1.54, 1.98, 0.18, 0.40, n_sides, "damp_brick", scale_u=0.45)

    # 4. Haupt-Ziegelmauer mit 4 eingetieften Schoepf-Nischen (bei 0, 90, 180, 270 Grad)
    # Nahtlose Bogensegmente (_add_arc_ring) -> 0 dreieckige Gehrungsluecken am Rand!
    niche_angles = [0.0, 0.5 * math.pi, math.pi, 1.5 * math.pi]
    span_n = math.radians(34.0)
    for q in range(4):
        a_niche = niche_angles[q]
        # A) Schoepf-Nische (niedrigerer Schöpf-Rand Z=0.40..0.60 + Kalkstein-Schwelle Z=0.60..0.66)
        n_sub = 4 if lod == 0 else 2
        na0 = a_niche - span_n * 0.5
        na1 = a_niche + span_n * 0.5
        _add_arc_ring(bm, uv_layer, 1.58, 1.92, 0.40, 0.60, na0, na1, n_sub, "fired_brick", scale_u=0.55)
        _add_arc_ring(bm, uv_layer, 1.53, 1.97, 0.60, 0.665, na0, na1, n_sub, "limestone_b", scale_u=0.55)

        # B) Hohe Ziegelmauer zwischen zwei Nischen (Z=0.40..0.75) + Zierband + Kalkstein-Abdeckkrone (Z=0.77..0.86)
        a_start = a_niche + span_n * 0.5
        a_end   = (a_niche + 0.5 * math.pi) - span_n * 0.5
        n_seg_w = 5 if lod == 0 else 2
        _add_arc_ring(bm, uv_layer, 1.57, 1.96, 0.40, 0.74, a_start, a_end, n_seg_w, "fired_brick", scale_u=0.55)
        _add_arc_ring(bm, uv_layer, 1.54, 1.99, 0.74, 0.775, a_start, a_end, n_seg_w, "gypsum", scale_u=0.45)
        _add_arc_ring(bm, uv_layer, 1.51, 2.02, 0.775, 0.865, a_start, a_end, n_seg_w, "limestone", scale_u=0.50)

        # C) 2 Flankierende abgetreppte Ziegel-Pilaster pro Schoepf-Nische (8 Pfeiler insgesamt!)
        for side in (-1.0, +1.0):
            ap = a_niche + side * (span_n * 0.5 + math.radians(3.5))
            r_pil = 1.84
            m_p1 = Matrix.Translation((math.cos(ap) * r_pil, math.sin(ap) * r_pil, 0.53)) @ Matrix.Rotation(ap, 4, "Z")
            _add_box_xform(bm, uv_layer, 0.48, 0.36, 0.68, m_p1, "fired_brick", scale_u=0.55)
            m_pcap = Matrix.Translation((math.cos(ap) * r_pil, math.sin(ap) * r_pil, 0.90)) @ Matrix.Rotation(ap, 4, "Z")
            _add_box_xform(bm, uv_layer, 0.56, 0.42, 0.10, m_pcap, "limestone", scale_u=0.50)
            if lod == 0:
                m_fin = Matrix.Translation((math.cos(ap) * r_pil, math.sin(ap) * r_pil, 0.985)) @ Matrix.Rotation(ap, 4, "Z")
                _add_box_xform(bm, uv_layer, 0.36, 0.28, 0.07, m_fin, "gypsum", scale_u=0.50)

    # 5. Zentraler sumerischer Wasserspeier-Pfeiler (Z = 0.18 .. 1.16 m)
    _add_box_xform(bm, uv_layer, 0.82, 0.82, 0.24, Matrix.Translation((0.0, 0.0, 0.30)), "wet_stone", scale_u=0.5)
    _add_box_xform(bm, uv_layer, 0.66, 0.66, 0.48, Matrix.Translation((0.0, 0.0, 0.66)), "fired_brick", scale_u=0.6)
    _add_box_xform(bm, uv_layer, 0.72, 0.72, 0.14, Matrix.Translation((0.0, 0.0, 0.95)), "lapis", scale_u=0.45)
    _add_box_xform(bm, uv_layer, 0.80, 0.80, 0.09, Matrix.Translation((0.0, 0.0, 1.065)), "limestone", scale_u=0.5)
    if lod == 0:
        _add_box_xform(bm, uv_layer, 0.48, 0.48, 0.08, Matrix.Translation((0.0, 0.0, 1.145)), "gypsum", scale_u=0.5)

    # 4 Zinnbronze-Wasserspeier in Richtung der 4 Schoepf-Nischen (Z = 0.82 m)
    for ang in niche_angles:
        ca, sa = math.cos(ang), math.sin(ang)
        m_sp = Matrix.Translation((ca * 0.42, sa * 0.42, 0.82)) @ Matrix.Rotation(ang, 4, "Z") @ Matrix.Rotation(math.radians(98.0), 4, "Y")
        _add_cylinder_xform(bm, uv_layer, 0.042, 0.030, 0.28, 8 if lod == 0 else 6, m_sp, "bronze", smooth=True)
        if lod == 0:
            # Bronze-Rosettenblende am Austritt
            m_ro = Matrix.Translation((ca * 0.33, sa * 0.33, 0.82)) @ Matrix.Rotation(ang, 4, "Z") @ Matrix.Rotation(math.radians(90.0), 4, "Y")
            _add_cylinder_xform(bm, uv_layer, 0.078, 0.078, 0.035, 8, m_ro, "bronze", smooth=False)
            # Fallender Wasserstrahl-Bogen vom Speier ins Becken (Material 1)
            jet_pts = [(0.55, 0.80, 0.018), (0.64, 0.76, 0.022), (0.71, 0.69, 0.028), (0.76, 0.61, 0.040)]
            jet_rings = []
            for r_off, z_j, r_tube in jet_pts:
                ring_v = []
                for k in range(6):
                    ka = (k / 6) * 2.0 * math.pi
                    lx = r_off + math.cos(ka) * r_tube * 0.6
                    ly = math.sin(ka) * r_tube
                    lz = z_j + math.cos(ka) * r_tube * 0.4
                    wx = ca * lx - sa * ly
                    wy = sa * lx + ca * ly
                    ring_v.append(bm.verts.new((wx, wy, lz)))
                jet_rings.append(ring_v)
            for jri in range(len(jet_rings) - 1):
                ra, rb = jet_rings[jri], jet_rings[jri + 1]
                for k in range(6):
                    kj = (k + 1) % 6
                    fj = bm.faces.new((ra[k], ra[kj], rb[kj], rb[k]))
                    fj.material_index = 1
                    fj.smooth = True
                    for lp in fj.loops:
                        lp[uv_layer].uv = (0.5, 0.5)
                        lp[foam_layer] = (0.85, 0.85, 0.85, 1.0)

    # 6. Terrakotta-Wasserkroege auf dem Rand & den Sockelstufen
    if lod == 0:
        jug_specs = [
            # Auf den Schoepf-Nischen-Schwellen & Brüstungsrand
            (( 1.76,  0.14, 0.665), (0.0, 0.0, 0.4),  0.88, True),
            ((-0.18,  1.77, 0.665), (0.04, -0.05, 1.9), 0.92, True),
            (( 1.24, -1.26, 0.865), (0.0, 0.0, -0.8), 0.82, True),
            # Auf der abgetreppten unteren Kalksteinstufe (Z = 0.18 m)
            ((-1.98, -0.62, 0.18), (0.0, 0.0, 2.4),  1.05, True),
            ((-1.82, -0.96, 0.18), (0.10, 0.06, 0.7), 0.94, True),
            (( 0.82,  1.88, 0.18), (0.0, 0.0, -1.2), 1.00, True),
        ]
    else:
        jug_specs = [
            (( 1.76,  0.14, 0.665), (0.0, 0.0, 0.4),  0.88, False),
            ((-1.98, -0.62, 0.18), (0.0, 0.0, 2.4),  1.05, False),
            (( 0.82,  1.88, 0.18), (0.0, 0.0, -1.2), 1.00, False),
        ]
    for pos, rot, sc, handle in jug_specs:
        _add_clay_jug(bm, uv_layer, Vector(pos), Euler(rot, "XYZ"), scale=sc, segs=14 if lod == 0 else 8, with_handle=handle)

    # Korrigierte Rotation pro Krug (leichte Neigung bei einzelnen Krügen)
    # Hinweis: _add_clay_jug erwartet Euler; setzen wir direkt sauber in neuem Aufruf?
    # Oben war rot_euler via Matrix.Rotation(rot[2]) - fuer leichte Neigung einfach Euler(rot):
    # (already clean upright + subtle tilt can be baked directly via Euler)

    # 7. Belebte Blender-Wasseroberflaeche im Becken (Material 1, Z = +0.635 m)
    r_inner_pillar = 0.30
    r_basin = 1.56
    n_rad = 28 if lod == 0 else 16
    n_ring = 8 if lod == 0 else 2
    w_rings = []
    for ri in range(n_ring + 1):
        t = ri / n_ring
        r = r_inner_pillar + t * (r_basin - r_inner_pillar)
        ring_v = []
        for ai in range(n_rad):
            ang = (ai / n_rad) * 2.0 * math.pi
            # Sanfte konzentrische Wellenrippel vom Zentralspeier nach aussen
            ripple = math.sin(t * 4.5 * math.pi) * 0.0045 * (1.0 - 0.55 * t) if lod == 0 else 0.0
            v = bm.verts.new((math.cos(ang) * r, math.sin(ang) * r, 0.635 + ripple))
            ring_v.append(v)
        w_rings.append(ring_v)

    for ri in range(n_ring):
        ra, rb = w_rings[ri], w_rings[ri + 1]
        ta = ri / n_ring
        tb = (ri + 1) / n_ring
        # Schaumgewicht hoch am zentralen Einlaufstrahl (t < 0.25) und sanft am Beckenrand (t > 0.82)
        fa = max(max(0.0, 1.0 - ta / 0.28), max(0.0, (ta - 0.80) / 0.20) * 0.72)
        fb = max(max(0.0, 1.0 - tb / 0.28), max(0.0, (tb - 0.80) / 0.20) * 0.72)
        for ai in range(n_rad):
            aj = (ai + 1) % n_rad
            f = bm.faces.new((ra[ai], ra[aj], rb[aj], rb[ai]))
            f.material_index = 1
            f.smooth = True
            for lp, val in zip(f.loops, [fa, fa, fb, fb]):
                p = lp.vert.co
                lp[uv_layer].uv = (p.x * 0.35 + 0.5, p.y * 0.35 + 0.5)
                lp[foam_layer] = (val, val, val, 1.0)

    # Alle uebrigen Loops auf Col_Foam = 0
    for f in bm.faces:
        if f.material_index == 0:
            for lp in f.loops:
                lp[foam_layer] = (0.0, 0.0, 0.0, 1.0)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    return bm


def main():
    t0 = time.time()
    tex_dir = os.path.join(ASSETS_DIR, "textures")
    blend_dir = os.path.join(ASSETS_DIR, "blend", "world")
    glb_dir = os.path.join(ASSETS_DIR, "glb", "world")
    os.makedirs(blend_dir, exist_ok=True)
    os.makedirs(glb_dir, exist_ok=True)

    scene = clear_scene()
    mat_trim = create_city_trim_material(tex_dir)
    mat_water = create_fountain_water_material(tex_dir)

    objs = []
    lod_stats = {}
    min_z_all = 0.0
    max_z_all = 0.0

    for lod in (0, 1):
        print(f"[FOUNTAIN] Baue ur_fountain_hero_LOD{lod}...", flush=True)
        bm = build_fountain_mesh(lod=lod)
        name = f"ur_fountain_hero_LOD{lod}"
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()

        mesh.materials.append(mat_trim)
        mesh.materials.append(mat_water)

        obj = bpy.data.objects.new(name, mesh)
        obj.location = (0.0, 0.0, 0.0)
        obj.rotation_euler = (0.0, 0.0, 0.0)
        obj.scale = (1.0, 1.0, 1.0)
        scene.collection.objects.link(obj)
        objs.append(obj)

        tris = sum(max(1, len(p.vertices) - 2) for p in mesh.polygons)
        min_z = min((v.co.z for v in mesh.vertices), default=0.0)
        max_z = max((v.co.z for v in mesh.vertices), default=0.0)
        min_z_all = min(min_z_all, min_z)
        max_z_all = max(max_z_all, max_z)
        lod_stats[f"LOD{lod}"] = tris
        print(f"  -> {name}: {tris} Tris | Z=[{min_z:+.3f} .. {max_z:+.3f}] m", flush=True)

    blend_path = os.path.join(blend_dir, "ur_fountain_hero.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[FOUNTAIN] .blend gespeichert: {blend_path}", flush=True)

    glb_path = os.path.join(glb_dir, "ur_fountain_hero.glb")
    export_arche_glb.export_glb(objs, glb_path, use_draco=False)
    glb_kb = os.path.getsize(glb_path) / 1024.0
    print(f"[FOUNTAIN] .glb exportiert: {glb_path} ({glb_kb:.1f} KB)", flush=True)

    # manifest.json aktualisieren
    mpath = os.path.join(ASSETS_DIR, "manifest.json")
    with open(mpath, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    items = manifest.setdefault("categories", {}).setdefault("world", {}).setdefault("items", {})
    items["ur_fountain_hero"] = {
        "enabled": True,
        "url": "assets/glb/world/ur_fountain_hero.glb",
        "blend": "assets/blend/world/ur_fountain_hero.blend",
        "category": "world",
        "description": "Sumerischer Marktplatzbrunnen aus gebranntem Ziegel, Kalkstein, 4 Schoepf-Nischen, Kruegen, feuchtem Sockel (-0.30m) & Blender-Wasseroberflaeche (LOD0 + LOD1)",
        "instanced": False,
        "materials": 2,
        "lods": lod_stats,
        "minZ": round(min_z_all, 3),
        "maxZ": round(max_z_all, 3),
        "lodBandsMeters": {"LOD0": [0, 80], "LOD1": [80, 600]},
        "sharedTextures": {
            "cityTrimBaseColor": "assets/textures/city_trim_atlas_baseColor.png",
            "cityTrimNormal": "assets/textures/city_trim_atlas_normal.png",
            "cityTrimOrm": "assets/textures/city_trim_atlas_orm.png",
            "waterNormalA": "assets/textures/water_blender_normal_a.png",
            "waterNormalB": "assets/textures/water_blender_normal_b.png",
            "waterFoam": "assets/textures/water_blender_foam.png",
        },
        "preview": "assets/previews/terrain_water_showcase.png",
        "glbSizeKB": round(glb_kb, 1),
        "exportedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"[MANIFEST] ur_fountain_hero aktualisiert in {time.time() - t0:.1f}s.", flush=True)


if __name__ == "__main__":
    main()
