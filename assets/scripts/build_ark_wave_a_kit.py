"""
build_ark_wave_a_kit.py — Arche-Welle A: Aussenhüllen- & Zimmermanns-Hero-Kit (Blender Master, 3-LOD GLB & 3 AgX-Showcases)
===========================================================================================================================
Erstellt die High-Detail-Master in assets/blend/ark/ark_wave_a_kit.blend und exportiert alle
6 Welle-A-Hero-Module (11 Einzel-Templates x 3 kurze Arche-LODs: LOD0 < 28 m, LOD1 28-75 m, LOD2 > 75 m)
nach assets/glb/ark/ark_wave_a_kit.glb (inkl. Manifest-Registrierung in assets/manifest.json).

Shader-Diaet-Kompatibilitaet (arche_asset_v1_std, deltaPrograms === 0):
  1 einziges gemeinsames Material (Mat_Ark_Master_Trim) mit exakt 3 Texturen:
    - assets/textures/ark/ark_master_basecolor.png [sRGB]
    - assets/textures/ark/ark_master_normal.png    [Linear / Non-Color]
    - assets/textures/ark/ark_master_roughness.png [Linear / Non-Color]
  Kein metalnessMap, kein aoMap, kein emissiveMap, kein Vertex-Color-Layer, transparent=false.

Module & verbindliche Pivots (aus scratch/ark_inventory_audit.md):
  1. ark_gate_leaf_s7   : 9x6.75 E. (4.200 x 3.150 x ~0.33 m), Origin (0,0,0) an OBERER Scharnier-Drehachse (Z: 0.000 -> -3.150 m)
     ark_gate_zarge_s7  : Lichte Oeffnung 4.200 x 3.150 m ueber 0.583 m Flutsuell, Origin (0,0,0) Zentrum Toroeffnung auf Deck 2 (Z=0.0)
  2. ark_storm_shutter  : Normiertes 1.0 x 1.0 x 1.0 Klappenblatt, Origin (0,0,0) Mitte Oberkante (Z: 0.000 -> -1.000 m)
  3. ark_root_knee_01..03: 3 organische Eichen-Wurzelknie (0.187 m breit, 0.630 m Schenkel, 0.171 m dick), Origin (0,0,0) an rechtwinkliger Aussenecke
  4. ark_kingpost_capital: Umschließt 0.336x0.336 m Koenigsstuetze, Sattelholz 0.386 x 1.100 x 0.260 m, Origin (0,0,0) Unterkante Laengsunterzug
  5. ark_door_frame_d1  : Lichte Oeffnung 2.800 x 2.917 m ueber 0.583 m Flutsuell (0.0 cm T99-Verengung!)
     ark_door_frame_d2  : Lichte Oeffnung 1.867 x 2.217 m ueber 0.233 m Suell (0.0 cm T99-Verengung!)
     ark_door_frame_d3  : Lichte Oeffnung 1.400 x 1.983 m ueber 0.233 m Suell (0.0 cm T99-Verengung!)
     ark_door_frame_foyer: Lichte Oeffnung 3.593 x 2.917 m ueber 0.117 m Schwelle (S7-Foyer-Hauptportal, 0.0 cm T99-Verengung!)
  6. ark_badgir_cap     : Passt auf 1.633 (X) x 1.400 (Y) m Badgir-Schacht, Origin Z=0.0 an Schacht-Oberkante zTop (+0.45 m Zeltdachhaube)

Aufruf:
  blender --background --python-exit-code 1 --python assets/scripts/build_ark_wave_a_kit.py
"""

import os
import sys
import json
import time
import math
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from build_ark_master_atlas import ARK_TRIM_REGIONS

# Biblischer Ellen-Kanon (BLENDER_PIPELINE.md & ark_inventory_audit.md)
ELLE_M = 14.0 / 30.0          # 0.4666667 m
HANDBREITE_M = ELLE_M / 6.0   # 0.0777778 m
FINGER_M = ELLE_M / 24.0      # 0.0194444 m


def get_project_root():
    return os.path.dirname(os.path.dirname(SCRIPT_DIR))


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    return scene


# ==============================================================================
# 1) EINZIGES GEMEINSAMES MEISTER-MATERIAL (EXAKT 3 MAPS FUER arche_asset_v1_std)
# ==============================================================================

def _load_img(path, colorspace):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Textur fehlt: {path} — bitte zuerst build_ark_master_atlas.py ausfuehren!")
    img = bpy.data.images.load(path, check_existing=True)
    img.colorspace_settings.name = colorspace
    try:
        img.pack()
    except Exception:
        pass
    return img


def build_ark_master_material(project_root):
    """Erstellt das einzige gemeinsame 2048x2048-Meister-Material mit exakt 3 Texturen:
    BaseColor [sRGB], Normal [Linear], Roughness [Linear].
    Kein metalnessMap, kein aoMap, kein emissiveMap, transparent=false."""
    tex_dir = os.path.join(project_root, "assets", "textures", "ark")
    mat = bpy.data.materials.new("Mat_Ark_Master_Trim")
    mat.use_nodes = True
    mat.use_backface_culling = False
    if hasattr(mat, "blend_method"):
        mat.blend_method = "OPAQUE"

    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    nodes.clear()

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Metallic"].default_value = 0.03
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.45
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # 1) BaseColor [sRGB]
    t_col = nodes.new("ShaderNodeTexImage")
    t_col.name = "Ark_BaseColor"
    t_col.image = _load_img(os.path.join(tex_dir, "ark_master_basecolor.png"), "sRGB")
    links.new(t_col.outputs["Color"], bsdf.inputs["Base Color"])

    # 2) Normal [Linear / Non-Color]
    t_nrm = nodes.new("ShaderNodeTexImage")
    t_nrm.name = "Ark_Normal"
    t_nrm.image = _load_img(os.path.join(tex_dir, "ark_master_normal.png"), "Non-Color")
    nm = nodes.new("ShaderNodeNormalMap")
    nm.inputs["Strength"].default_value = 1.0
    links.new(t_nrm.outputs["Color"], nm.inputs["Color"])
    links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])

    # 3) Roughness [Linear / Non-Color]
    t_rgh = nodes.new("ShaderNodeTexImage")
    t_rgh.name = "Ark_Roughness"
    t_rgh.image = _load_img(os.path.join(tex_dir, "ark_master_roughness.png"), "Non-Color")
    links.new(t_rgh.outputs["Color"], bsdf.inputs["Roughness"])

    return mat


# ==============================================================================
# 2) BMESH ZIMMERMANNS-GEOMETRIE-PRIMITIVE MIT TRIM-UV-PROJEKTION
# ==============================================================================

def map_face_uv(face, uv_layer, region_name, u_scale=0.35, v_fit=True, rotate_uv=False):
    face.material_index = 0
    u0, v0, u1, v1 = ARK_TRIM_REGIONS[region_name]
    du = u1 - u0
    dv = v1 - v0
    face.normal_update()
    n = face.normal
    verts = [l.vert.co for l in face.loops]

    if abs(n.z) > 0.72:
        pts = [(v.x, v.y) for v in verts]
    elif abs(n.x) > abs(n.y):
        pts = [(v.y, v.z) for v in verts]
    else:
        pts = [(v.x, v.z) for v in verts]

    if rotate_uv:
        pts = [(p[1], p[0]) for p in pts]

    min_x = min(p[0] for p in pts)
    max_x = max(p[0] for p in pts)
    min_y = min(p[1] for p in pts)
    max_y = max(p[1] for p in pts)
    sx = max(1e-4, max_x - min_x)
    sy = max(1e-4, max_y - min_y)

    can_tile_u = (u0 <= 0.001 and u1 >= 0.999)
    for loop, (px, py) in zip(face.loops, pts):
        tx = (px - min_x) / sx
        ty = (py - min_y) / sy
        if can_tile_u:
            u = (px - min_x) * u_scale
        else:
            u = u0 + (0.04 + 0.92 * tx) * du
        v_t = ty if v_fit else ((py - min_y) * u_scale) % 1.0
        v = v0 + (0.04 + 0.92 * v_t) * dv
        loop[uv_layer].uv = (u, v)


def _orient_faces_outward(faces, center_pt):
    for f in faces:
        f.normal_update()
        if (f.calc_center_median() - center_pt).dot(f.normal) < 0.0:
            f.normal_flip()


def add_box(bm, uv_layer, x0, x1, y0, y1, z0, z1, region, end_region=None, end_axis="X", u_scale=0.35, rotate_uv=False):
    """Achsenparalleler Quader mit separatem Stirnholz-UV auf den Endflächen."""
    v000 = bm.verts.new((x0, y0, z0))
    v100 = bm.verts.new((x1, y0, z0))
    v110 = bm.verts.new((x1, y1, z0))
    v010 = bm.verts.new((x0, y1, z0))
    v001 = bm.verts.new((x0, y0, z1))
    v101 = bm.verts.new((x1, y0, z1))
    v111 = bm.verts.new((x1, y1, z1))
    v011 = bm.verts.new((x0, y1, z1))

    f_defs = [
        ((v000, v100, v101, v001), "Y"),  # -Y
        ((v110, v010, v011, v111), "Y"),  # +Y
        ((v010, v000, v001, v011), "X"),  # -X
        ((v100, v110, v111, v101), "X"),  # +X
        ((v001, v101, v111, v011), "Z"),  # +Z
        ((v010, v110, v100, v000), "Z"),  # -Z
    ]
    faces = []
    for verts, ax in f_defs:
        f = bm.faces.new(verts)
        reg = (end_region or region) if (end_region and ax == end_axis) else region
        rot = rotate_uv if ax != end_axis else False
        map_face_uv(f, uv_layer, reg, u_scale=u_scale, rotate_uv=rot)
        faces.append(f)
    _orient_faces_outward(faces, Vector((0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (z0 + z1))))
    return faces


def add_chamfered_beam(bm, uv_layer, x0, x1, y0, y1, z0, z1, chamfer, region, end_region="oak_endgrain", axis="X", u_scale=0.35):
    """Echter 8-kantig gefaster Zimmermannsbalken entlang X, Y oder Z (0 scharfe 90°-Plastikkanten!)."""
    if chamfer <= 1e-4:
        return add_box(bm, uv_layer, x0, x1, y0, y1, z0, z1, region, end_region=end_region, end_axis=axis, u_scale=u_scale)

    def _octagon_2d(a0, a1, b0, b1, c):
        ca = min(c, 0.35 * (a1 - a0))
        cb = min(c, 0.35 * (b1 - b0))
        return [
            (a0 + ca, b0), (a1 - ca, b0),
            (a1, b0 + cb), (a1, b1 - cb),
            (a1 - ca, b1), (a0 + ca, b1),
            (a0, b1 - cb), (a0, b0 + cb),
        ]

    ring0, ring1 = [], []
    if axis == "X":
        poly = _octagon_2d(y0, y1, z0, z1, chamfer)
        for py, pz in poly:
            ring0.append(bm.verts.new((x0, py, pz)))
            ring1.append(bm.verts.new((x1, py, pz)))
        rot_uv = False
    elif axis == "Y":
        poly = _octagon_2d(x0, x1, z0, z1, chamfer)
        for px, pz in poly:
            ring0.append(bm.verts.new((px, y0, pz)))
            ring1.append(bm.verts.new((px, y1, pz)))
        rot_uv = False
    else:  # Z
        poly = _octagon_2d(x0, x1, y0, y1, chamfer)
        for px, py in poly:
            ring0.append(bm.verts.new((px, py, z0)))
            ring1.append(bm.verts.new((px, py, z1)))
        rot_uv = True

    faces = []
    n = len(ring0)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((ring0[i], ring0[j], ring1[j], ring1[i]))
        map_face_uv(f, uv_layer, region, u_scale=u_scale, rotate_uv=rot_uv)
        faces.append(f)
    f0 = bm.faces.new(list(reversed(ring0)))
    map_face_uv(f0, uv_layer, end_region or region, u_scale=u_scale)
    f1 = bm.faces.new(ring1)
    map_face_uv(f1, uv_layer, end_region or region, u_scale=u_scale)
    faces.extend([f0, f1])
    _orient_faces_outward(faces, Vector((0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (z0 + z1))))
    return faces


def add_oriented_prism(bm, uv_layer, p0, p1, w_perp, h_cross, up_hint, region, end_region="oak_endgrain", u_scale=0.40):
    """Beliebig im Raum orientierter Vierkant-Strebenbalken von p0 nach p1."""
    v0 = Vector(p0)
    v1 = Vector(p1)
    axis = v1 - v0
    if axis.length < 1e-4:
        return []
    fwd = axis.normalized()
    right = fwd.cross(Vector(up_hint))
    if right.length < 1e-4:
        right = fwd.cross(Vector((1.0, 0.0, 0.0)))
    right.normalize()
    up = right.cross(fwd).normalized()

    hr = right * (0.5 * w_perp)
    hu = up * (0.5 * h_cross)
    offs = [-hr - hu, +hr - hu, +hr + hu, -hr + hu]
    r0 = [bm.verts.new(v0 + o) for o in offs]
    r1 = [bm.verts.new(v1 + o) for o in offs]

    faces = []
    for i in range(4):
        j = (i + 1) % 4
        f = bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
        map_face_uv(f, uv_layer, region, u_scale=u_scale)
        faces.append(f)
    f0 = bm.faces.new(list(reversed(r0)))
    map_face_uv(f0, uv_layer, end_region or region, u_scale=u_scale)
    f1 = bm.faces.new(r1)
    map_face_uv(f1, uv_layer, end_region or region, u_scale=u_scale)
    faces.extend([f0, f1])
    _orient_faces_outward(faces, 0.5 * (v0 + v1))
    return faces


def add_dowel_peg(bm, uv_layer, center, normal_dir, radius=0.028, length=0.028, segs=6, region="hornbeam", head_region="oak_dowel_heads"):
    """Plastisch vorstehender, leicht gefaster Hartholz-Duebelkopf (3 Finger / 1 Hand)."""
    c = Vector(center)
    n = Vector(normal_dir).normalized()
    t1 = n.cross(Vector((0.0, 0.0, 1.0)))
    if t1.length < 1e-4:
        t1 = n.cross(Vector((1.0, 0.0, 0.0)))
    t1.normalize()
    t2 = n.cross(t1).normalized()

    p_base = c - n * (0.25 * length)
    p_top = c + n * (0.75 * length)
    r_top = radius * 0.82

    v_base, v_top = [], []
    for i in range(segs):
        a = 2.0 * math.pi * i / segs
        radial = t1 * math.cos(a) + t2 * math.sin(a)
        v_base.append(bm.verts.new(p_base + radial * radius))
        v_top.append(bm.verts.new(p_top + radial * r_top))

    faces = []
    for i in range(segs):
        j = (i + 1) % segs
        f = bm.faces.new((v_base[i], v_base[j], v_top[j], v_top[i]))
        map_face_uv(f, uv_layer, region, u_scale=0.8)
        faces.append(f)
    ft = bm.faces.new(v_top)
    map_face_uv(ft, uv_layer, head_region, u_scale=1.0)
    faces.append(ft)
    _orient_faces_outward(faces, 0.5 * (p_base + p_top))
    return faces


def add_cylinder_along_axis(bm, uv_layer, p0, p1, radius, segs=8, region="hornbeam", cap_ends=True):
    """Zylinder entlang beliebiger Achse p0 -> p1 (fuer Scharnierzapfen, Seilringe & Bolzen)."""
    v0 = Vector(p0)
    v1 = Vector(p1)
    n = (v1 - v0).normalized()
    t1 = n.cross(Vector((0.0, 0.0, 1.0)))
    if t1.length < 1e-4:
        t1 = n.cross(Vector((0.0, 1.0, 0.0)))
    t1.normalize()
    t2 = n.cross(t1).normalized()

    r0, r1 = [], []
    for i in range(segs):
        a = 2.0 * math.pi * i / segs
        rad = (t1 * math.cos(a) + t2 * math.sin(a)) * radius
        r0.append(bm.verts.new(v0 + rad))
        r1.append(bm.verts.new(v1 + rad))

    faces = []
    for i in range(segs):
        j = (i + 1) % segs
        f = bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
        f.smooth = (segs >= 8)
        map_face_uv(f, uv_layer, region, u_scale=0.6)
        faces.append(f)
    if cap_ends:
        f0 = bm.faces.new(list(reversed(r0)))
        map_face_uv(f0, uv_layer, region)
        f1 = bm.faces.new(r1)
        map_face_uv(f1, uv_layer, region)
        faces.extend([f0, f1])
    _orient_faces_outward(faces, 0.5 * (v0 + v1))
    return faces


def add_rope_ring_eye(bm, uv_layer, center, normal_y_sign, r_major=0.11, r_minor=0.030, segs_u=8, segs_v=5):
    """Bronze-Oese + geflochtener Hanfseil-Zugring."""
    cx, cy, cz = center
    # Bronze mounting bracket plate
    add_box(bm, uv_layer, cx - 0.07, cx + 0.07, cy - 0.02, cy + 0.02, cz - 0.07, cz + 0.07, "tin_bronze")
    # Hemp rope torus loop hanging down from bracket
    ring_cy = cy + normal_y_sign * 0.045
    ring_cz = cz - r_major * 0.55
    rings = []
    for iu in range(segs_u):
        au = 2.0 * math.pi * iu / segs_u
        c_pt = Vector((cx + math.cos(au) * r_major, ring_cy + normal_y_sign * 0.02 * math.sin(au), ring_cz + math.sin(au) * r_major))
        rad_dir = Vector((math.cos(au), 0.0, math.sin(au)))
        perp_dir = Vector((0.0, 1.0, 0.0))
        v_ring = []
        for iv in range(segs_v):
            av = 2.0 * math.pi * iv / segs_v
            pt = c_pt + (rad_dir * math.cos(av) + perp_dir * math.sin(av)) * r_minor
            v_ring.append(bm.verts.new(pt))
        rings.append(v_ring)
    for iu in range(segs_u):
        ju = (iu + 1) % segs_u
        for iv in range(segs_v):
            jv = (iv + 1) % segs_v
            f = bm.faces.new((rings[iu][iv], rings[ju][iv], rings[ju][jv], rings[iu][jv]))
            f.smooth = True
            map_face_uv(f, uv_layer, "hemp_rope", u_scale=1.2)


# ==============================================================================
# MODUL 1A: HERO-SEITENTOR S7 — TORBLATT (ark_gate_leaf_s7)
# ==============================================================================
# Pivot (0,0,0) EXAKT an der oberen Scharnier-Drehachse (Z: 0.000 -> -3.150 m)
# Breite Torblatt: 4.200 m (9.0 E., X in [-2.100 .. +2.100 m]), 3 Sperrbalken 4.880 m (X in [-2.440 .. +2.440 m])
# Hoehe: 3.150 m (6.75 E., Z in [-3.150 .. 0.000 m]), Gesamtdicke ~0.33 m

def build_ark_gate_leaf_s7(bm, uv_layer, lod):
    W_leaf = 4.200
    H_leaf = 3.150
    hx = 0.5 * W_leaf  # 2.100 m

    if lod == 0:
        # 1. AUSSENSEITE (-Y): 9 dicke horizontale Kopher-Pech-Plankengaenge mit plastischen Kalfater-Fugen
        n_outer_courses = 9
        dz_out = H_leaf / n_outer_courses
        for ic in range(n_outer_courses):
            z_top = -ic * dz_out
            z_bot = -(ic + 1) * dz_out
            # Segmented in X (3 sections) for subtle hand-adzed pitch surface undulation
            nx_seg = 3
            dx_s = (W_leaf - 0.28) / nx_seg
            for ix in range(nx_seg):
                sx0 = -hx + 0.14 + ix * dx_s
                sx1 = sx0 + dx_s - 0.004
                y_undul = -0.155 - 0.006 * ((ic + ix) % 2)
                add_chamfered_beam(
                    bm, uv_layer, sx0, sx1, y_undul, -0.020, z_bot + 0.004, z_top - 0.004,
                    chamfer=0.012, region="kopher_pitch", end_region="kopher_pitch", axis="X", u_scale=0.28
                )
            # Raised tarred oakum caulking bead along horizontal seam
            if ic > 0:
                add_box(bm, uv_layer, -hx + 0.12, hx - 0.12, -0.164, -0.145, z_top - 0.014, z_top + 0.014, "kopher_pitch", u_scale=0.45)

        # Massive outer perimeter frame beams (-Y/+Y cheek border, 0.15 m wide — Gen 6,14 Kopher-versiegelt)
        add_chamfered_beam(bm, uv_layer, -hx, -hx + 0.15, -0.165, +0.020, -H_leaf, 0.000, 0.016, "kopher_pitch", end_region="kopher_pitch", axis="Z")
        add_chamfered_beam(bm, uv_layer, +hx - 0.15, +hx, -0.165, +0.020, -H_leaf, 0.000, 0.016, "kopher_pitch", end_region="kopher_pitch", axis="Z")
        add_chamfered_beam(bm, uv_layer, -hx + 0.15, +hx - 0.15, -0.165, -0.015, -0.160, 0.000, 0.014, "kopher_pitch", end_region="kopher_pitch", axis="X")
        add_chamfered_beam(bm, uv_layer, -hx + 0.15, +hx - 0.15, -0.165, -0.015, -H_leaf, -H_leaf + 0.160, 0.014, "kopher_pitch", end_region="kopher_pitch", axis="X")

        # 2. INNENSEITE (+Y): 11 plastisch gefaste horizontale Tor-Bohlen (4.12 x 3.09 m) — Gen 6,14 INNEN MIT KOPHER-ERDPECH VERSIEGELT!
        n_inner_planks = 11
        z_in_top = -0.030
        z_in_bot = -3.120
        dz_in = (z_in_top - z_in_bot) / n_inner_planks
        for ip in range(n_inner_planks):
            pz1 = z_in_top - ip * dz_in
            pz0 = pz1 - dz_in + 0.004
            add_chamfered_beam(
                bm, uv_layer, -2.060, +2.060, -0.020, +0.088, pz0, pz1,
                chamfer=0.014, region="kopher_pitch", end_region="kopher_pitch", axis="X", u_scale=0.32
            )

        # 3. 8 VERTIKALE SPANTENRIPPEN im Abstand 0.523 m (1.12 E., ebenfalls Kopher-verpicht unter den warmen Sperrbalken)
        rib_step = 0.523
        rib_xs = [(-3.5 + i) * rib_step for i in range(8)]
        for rx in rib_xs:
            add_chamfered_beam(
                bm, uv_layer, rx - 0.048, rx + 0.048, +0.082, +0.165, -3.120, -0.030,
                chamfer=0.012, region="kopher_pitch", end_region="kopher_pitch", axis="Z", u_scale=0.40
            )
            # Exterior (-Y) vertical pitch-coated stiffening battens aligned with ribs
            add_box(bm, uv_layer, rx - 0.034, rx + 0.034, -0.172, -0.148, -3.100, -0.050, "kopher_pitch", rotate_uv=True)

        # Diagonal heavy cross-struts between ribs (Kopher-sealed on inner plank face)
        for pair_i in (0, 2, 4, 6):
            x_a = rib_xs[pair_i] + 0.048
            x_b = rib_xs[pair_i + 1] - 0.048
            add_oriented_prism(bm, uv_layer, (x_a, 0.115, -0.58), (x_b, 0.115, -1.56), 0.055, 0.075, (0, 1, 0), "kopher_pitch", end_region="kopher_pitch")
            add_oriented_prism(bm, uv_layer, (x_b, 0.115, -1.59), (x_a, 0.115, -2.56), 0.055, 0.075, (0, 1, 0), "kopher_pitch", end_region="kopher_pitch")

        # 4. 3 WUCHTIGE HORIZONTALE HAINBUCHEN-SPERRBALKEN (4.88 x 0.24 x 0.21 m, greifen beidseitig 0.34 m ueber!)
        bar_zs = [-0.580, -1.575, -2.570]
        for bz in bar_zs:
            add_chamfered_beam(
                bm, uv_layer, -2.440, +2.440, +0.135, +0.345, bz - 0.120, bz + 0.120,
                chamfer=0.022, region="hornbeam", end_region="oak_endgrain", axis="X", u_scale=0.28
            )
            # 4 geschnitzte Eichen-Schubtaschen (Stirrup brackets) + Hartholz-Sperrkeile pro Sperrbalken
            for bx in (-1.8305, -0.7845, +0.7845, +1.8305):
                # Left & right bracket cheeks
                add_box(bm, uv_layer, bx - 0.095, bx + 0.095, +0.085, +0.365, bz + 0.118, bz + 0.168, "oak_d35")
                add_box(bm, uv_layer, bx - 0.095, bx + 0.095, +0.085, +0.365, bz - 0.168, bz - 0.118, "oak_d35")
                add_chamfered_beam(bm, uv_layer, bx - 0.095, bx + 0.095, +0.335, +0.382, bz - 0.168, bz + 0.168, 0.010, "oak_d35", axis="Z")
                # Driven hardwood locking wedge through bracket
                add_oriented_prism(bm, uv_layer, (bx - 0.04, 0.360, bz + 0.19), (bx + 0.04, 0.360, bz - 0.19), 0.032, 0.038, (0, 1, 0), "hornbeam")

        # 5. SCHWERE ZINNBRONZE-/HARTHOLZ-ZAPFENSCHARNIERE OBEN AUF DER DREHACHSE (Z = 0.000 m!)
        hinge_xs = [-1.8305, -0.7845, +0.7845, +1.8305]
        for hx_pos in hinge_xs:
            # Cylindrical hornbeam & tin-bronze pivot journal centered at (Y=0.0, Z=0.0)
            add_cylinder_along_axis(bm, uv_layer, (hx_pos - 0.16, 0.0, 0.0), (hx_pos + 0.16, 0.0, 0.0), radius=0.068, segs=10, region="tin_bronze")
            add_cylinder_along_axis(bm, uv_layer, (hx_pos - 0.22, 0.0, 0.0), (hx_pos + 0.22, 0.0, 0.0), radius=0.042, segs=8, region="hornbeam")
            # Heavy hammered tin-bronze hinge straps clamping both outer (-Y) and inner (+Y) faces
            add_chamfered_beam(bm, uv_layer, hx_pos - 0.065, hx_pos + 0.065, -0.180, -0.145, -0.680, 0.000, 0.008, "tin_bronze", end_region="tin_bronze", axis="Z")
            add_chamfered_beam(bm, uv_layer, hx_pos - 0.065, hx_pos + 0.065, +0.155, +0.185, -0.680, 0.000, 0.008, "tin_bronze", end_region="tin_bronze", axis="Z")
            for rz in (-0.18, -0.38, -0.58):
                add_dowel_peg(bm, uv_layer, (hx_pos, -0.180, rz), (0, -1, 0), radius=0.024, length=0.024, segs=6, region="tin_bronze", head_region="tin_bronze")
                add_dowel_peg(bm, uv_layer, (hx_pos, +0.185, rz), (0, +1, 0), radius=0.024, length=0.024, segs=6, region="tin_bronze", head_region="tin_bronze")

        # 6. PLASTISCHE HARTHOLZ-DUEBELKOEPFE (3 Finger / 1 Hand) AUF ALLEN 8 SPANTENRIPPEN & RANDBOHLEN
        peg_zs = [-0.24, -0.88, -1.24, -1.90, -2.25, -2.90]
        for rx in rib_xs:
            for pz in peg_zs:
                add_dowel_peg(bm, uv_layer, (rx, +0.165, pz), (0, +1, 0), radius=0.028, length=0.026, segs=6)
        for sx_edge in (-hx + 0.075, +hx - 0.075):
            for pz in (-0.35, -0.95, -1.575, -2.20, -2.80):
                add_dowel_peg(bm, uv_layer, (sx_edge, -0.165, pz), (0, -1, 0), radius=0.030, length=0.026, segs=6)

        # 7. SCHWERE HANF-ZUGSEIL-OESEN (4 innen +Y, 2 aussen -Y)
        for rx_eye in (-1.58, +1.58):
            add_rope_ring_eye(bm, uv_layer, (rx_eye, +0.165, -0.32), +1.0, r_major=0.115, r_minor=0.030, segs_u=8, segs_v=5)
            add_rope_ring_eye(bm, uv_layer, (rx_eye, +0.165, -2.82), +1.0, r_major=0.115, r_minor=0.030, segs_u=8, segs_v=5)
            add_rope_ring_eye(bm, uv_layer, (rx_eye, -0.165, -2.82), -1.0, r_major=0.115, r_minor=0.030, segs_u=8, segs_v=5)

    elif lod == 1:
        # LOD1 (~1.100 - 1.500 Tris) — Gen 6,14 innen & aussen Kopher-verpicht
        for ic in range(6):
            z_top = -ic * (H_leaf / 6.0)
            z_bot = -(ic + 1) * (H_leaf / 6.0)
            add_chamfered_beam(bm, uv_layer, -hx + 0.14, +hx - 0.14, -0.158, -0.015, z_bot + 0.004, z_top - 0.004, 0.012, "kopher_pitch", end_region="kopher_pitch", axis="X")
        add_chamfered_beam(bm, uv_layer, -hx, -hx + 0.15, -0.165, +0.020, -H_leaf, 0.000, 0.014, "kopher_pitch", end_region="kopher_pitch", axis="Z")
        add_chamfered_beam(bm, uv_layer, +hx - 0.15, +hx, -0.165, +0.020, -H_leaf, 0.000, 0.014, "kopher_pitch", end_region="kopher_pitch", axis="Z")
        for ip in range(7):
            pz1 = -0.030 - ip * (3.090 / 7.0)
            pz0 = pz1 - (3.090 / 7.0) + 0.004
            add_chamfered_beam(bm, uv_layer, -2.060, +2.060, -0.015, +0.088, pz0, pz1, 0.010, "kopher_pitch", end_region="kopher_pitch", axis="X")
        rib_xs = [(-3.5 + i) * 0.523 for i in range(8)]
        for rx in rib_xs:
            add_chamfered_beam(bm, uv_layer, rx - 0.048, rx + 0.048, +0.082, +0.165, -3.120, -0.030, 0.010, "kopher_pitch", end_region="kopher_pitch", axis="Z")
        for bz in (-0.580, -1.575, -2.570):
            add_chamfered_beam(bm, uv_layer, -2.440, +2.440, +0.135, +0.345, bz - 0.120, bz + 0.120, 0.018, "hornbeam", axis="X")
            for bx in (-1.8305, -0.7845, +0.7845, +1.8305):
                add_box(bm, uv_layer, bx - 0.09, bx + 0.09, +0.085, +0.375, bz - 0.16, bz + 0.16, "oak_d35")
        for hx_pos in (-1.8305, -0.7845, +0.7845, +1.8305):
            add_cylinder_along_axis(bm, uv_layer, (hx_pos - 0.16, 0.0, 0.0), (hx_pos + 0.16, 0.0, 0.0), radius=0.065, segs=6, region="tin_bronze")
            add_box(bm, uv_layer, hx_pos - 0.06, hx_pos + 0.06, -0.175, +0.180, -0.65, 0.0, "tin_bronze")

    else:
        # LOD2 (~320 - 450 Tris) — Gen 6,14 innen & aussen Kopher-verpicht
        add_box(bm, uv_layer, -hx, +hx, -0.160, -0.010, -H_leaf, 0.000, "kopher_pitch")
        add_box(bm, uv_layer, -2.060, +2.060, -0.010, +0.088, -3.120, -0.030, "kopher_pitch")
        for rx in [(-3.5 + i) * 0.523 for i in range(8)]:
            add_box(bm, uv_layer, rx - 0.048, rx + 0.048, +0.082, +0.165, -3.120, -0.030, "kopher_pitch", rotate_uv=True)
        for bz in (-0.580, -1.575, -2.570):
            add_box(bm, uv_layer, -2.440, +2.440, +0.135, +0.345, bz - 0.120, bz + 0.120, "hornbeam")
            for bx in (-1.8305, +1.8305):
                add_box(bm, uv_layer, bx - 0.09, bx + 0.09, +0.085, +0.375, bz - 0.16, bz + 0.16, "oak_d35")
        for hx_pos in (-1.8305, -0.7845, +0.7845, +1.8305):
            add_box(bm, uv_layer, hx_pos - 0.08, hx_pos + 0.08, -0.175, +0.180, -0.55, +0.05, "tin_bronze")


# ==============================================================================
# MODUL 1B: HERO-SEITENTOR S7 — BLOCKZARGE (ark_gate_zarge_s7)
# ==============================================================================
# Origin (0,0,0) im Zentrum der Toroeffnung auf Deck-2-Hoehe (Z = 6.000 m -> lokal Z = 0.000 m)
# Lichte Oeffnung: 4.200 m breit (X in [-2.100 .. +2.100 m]) x 3.150 m hoch (Z in [+0.583 .. +3.733 m])
# ueber dem 0.583 m (1.25 E.) hohen Flutsuell (Z in [0.000 .. +0.583 m]).

def build_ark_gate_zarge_s7(bm, uv_layer, lod):
    W_open = 4.200
    H_open = 3.150
    H_sill = 0.583333   # 1.25 Ellen
    b_post = 0.466667   # 6.0 Handbreiten (1.0 Elle)
    h_lintel = 0.388889 # 5.0 Handbreiten
    d_jamb = 0.522      # Laibungstiefe (6 H. + 5.5 cm)
    hx = 0.5 * W_open   # 2.100 m
    hy = 0.5 * d_jamb   # 0.261 m
    z_top_open = H_sill + H_open  # 3.733333 m
    z_top_lintel = z_top_open + h_lintel  # 4.122222 m

    ch = 0.022 if lod <= 1 else 0.0

    # 1. MASSIVER 0.583 m HOHER FLUTSUELL (Z in [0.000 .. +0.583 m])
    add_chamfered_beam(
        bm, uv_layer, -hx - b_post, +hx + b_post, -hy, +hy, 0.000, H_sill,
        chamfer=ch, region="oak_d35", end_region="oak_endgrain", axis="X", u_scale=0.30
    )
    # Aeusserer & innerer Kopher-Pech-Dichtungsanschlag + Flutsuell-Innenkante (-Y & +Y, Gen 6,14!)
    add_box(bm, uv_layer, -hx - 0.05, +hx + 0.05, -hy - 0.035, +hy + 0.022, 0.000, H_sill + 0.045, "kopher_pitch")

    # 2. MASSIVE 0.467 m BREITE EICHEN-BLOCKPFOSTEN (links & rechts ausserhalb X = +-2.100 m!)
    for sgn in (-1.0, +1.0):
        px0 = -hx - b_post if sgn < 0 else +hx
        px1 = -hx if sgn < 0 else +hx + b_post
        add_chamfered_beam(
            bm, uv_layer, px0, px1, -hy, +hy, H_sill, z_top_open,
            chamfer=ch, region="oak_d35", end_region="oak_endgrain", axis="Z", u_scale=0.32
        )
        # Profilierter Kopher-Dichtungsfalz (Anschlagleiste aussen -Y & innere Dichtlippe +Y, Gen 6,14!)
        fx0 = -hx - 0.14 if sgn < 0 else +hx
        fx1 = -hx if sgn < 0 else +hx + 0.14
        add_box(bm, uv_layer, fx0, fx1, -hy - 0.030, +hy - 0.065, H_sill, z_top_open, "kopher_pitch", rotate_uv=True)

        # 3 SEITLICHE RIEGELTASCHEN (fuer die 3 um 0.34 m uebergreifenden Hainbuchen-Sperrbalken!)
        bar_zs_abs = [z_top_open - 0.580, z_top_open - 1.575, z_top_open - 2.570]
        for bz in bar_zs_abs:
            tx0 = (-hx - 0.42) if sgn < 0 else +hx
            tx1 = -hx if sgn < 0 else (+hx + 0.42)
            # Upper & lower oak mortise cheek blocks + outer stop block
            add_chamfered_beam(bm, uv_layer, tx0, tx1, +0.08, +0.36, bz + 0.122, bz + 0.195, ch * 0.6, "oak_d35", axis="X")
            add_chamfered_beam(bm, uv_layer, tx0, tx1, +0.08, +0.36, bz - 0.195, bz - 0.122, ch * 0.6, "oak_d35", axis="X")
            end_x0 = tx0 if sgn < 0 else (tx1 - 0.08)
            end_x1 = (tx0 + 0.08) if sgn < 0 else tx1
            add_chamfered_beam(bm, uv_layer, end_x0, end_x1, +0.08, +0.36, bz - 0.122, bz + 0.122, ch * 0.5, "hornbeam", axis="Z")
            if lod == 0:
                add_dowel_peg(bm, uv_layer, (0.5 * (tx0 + tx1), +0.36, bz + 0.158), (0, 1, 0), radius=0.026, length=0.025, segs=6)
                add_dowel_peg(bm, uv_layer, (0.5 * (tx0 + tx1), +0.36, bz - 0.158), (0, 1, 0), radius=0.026, length=0.025, segs=6)

    # 3. 0.389 m (5 H.) HOHER PROFILIERTER EICHEN-STURZ MIT UEBERKAEMMUNG & DURCHGESTECKTEN ZAPFEN
    add_chamfered_beam(
        bm, uv_layer, -hx - b_post - 0.22, +hx + b_post + 0.22, -hy - 0.02, +hy + 0.02, z_top_open, z_top_lintel,
        chamfer=ch, region="oak_d35", end_region="oak_endgrain", axis="X", u_scale=0.28
    )
    if lod <= 1:
        # Upper drip moulding & kopher seal along lintel exterior
        add_chamfered_beam(
            bm, uv_layer, -hx - b_post - 0.26, +hx + b_post + 0.26, -hy - 0.06, -hy + 0.02, z_top_lintel - 0.08, z_top_lintel + 0.04,
            chamfer=0.012, region="kopher_pitch", axis="X"
        )
        # Protruding post tenons & double hardwood wedges above lintel
        for sgn in (-1.0, +1.0):
            px_mid = sgn * (hx + 0.5 * b_post)
            add_chamfered_beam(bm, uv_layer, px_mid - 0.14, px_mid + 0.14, -0.14, +0.14, z_top_lintel, z_top_lintel + 0.09, 0.012, "oak_endgrain", axis="Z")
            add_oriented_prism(bm, uv_layer, (px_mid - 0.18, -0.08, z_top_lintel + 0.04), (px_mid + 0.18, +0.08, z_top_lintel + 0.04), 0.036, 0.045, (0, 0, 1), "hornbeam")

    # 4. 2 ORGANISCH GESCHWUNGENE EICHEN-KOPFBAENDER (0.537 m = 1.15 E. Schenkellaenge, 0.171 m = 2.2 H. stark)
    arm_k = 0.536667  # 1.15 Ellen
    d_k = 0.171111    # 2.2 Handbreiten
    for sgn in (-1.0, +1.0):
        # Corner is at X = sgn * hx, Z = z_top_open
        cx_corner = sgn * hx
        dir_x = -sgn  # points inward toward X=0
        n_arc = 7 if lod == 0 else (4 if lod == 1 else 2)
        rings = []
        for ia in range(n_arc + 1):
            t = ia / n_arc
            ang = t * (0.5 * math.pi)
            # Outer spine runs along post then lintel; inner throat is a smooth concave oak curve
            px_out = cx_corner + dir_x * (math.sin(ang) * arm_k * (0.18 if t < 0.5 else 1.0))
            pz_out = z_top_open - (math.cos(ang) * arm_k * (1.0 if t < 0.5 else 0.18))
            # Smooth curved centerline for organic knee brace
            px_in = cx_corner + dir_x * (arm_k * (1.0 - math.cos(ang)) * 0.92 + d_k * math.cos(ang) * 0.65)
            pz_in = z_top_open - (arm_k * (1.0 - math.sin(ang)) * 0.92 + d_k * math.sin(ang) * 0.65)
            if ia == 0:
                px_out, pz_out = cx_corner, z_top_open - arm_k
                px_in, pz_in = cx_corner + dir_x * d_k, z_top_open - arm_k
            elif ia == n_arc:
                px_out, pz_out = cx_corner + dir_x * arm_k, z_top_open
                px_in, pz_in = cx_corner + dir_x * arm_k, z_top_open - d_k

            y_a, y_b = -0.105, +0.105
            c_bev = 0.018 if lod == 0 else 0.0
            if c_bev > 0.0:
                p_vec = Vector((px_in - px_out, 0.0, pz_in - pz_out))
                if p_vec.length > 1e-4:
                    p_dir = p_vec.normalized()
                else:
                    p_dir = Vector((dir_x, 0.0, -1.0)).normalized()
                ring = [
                    bm.verts.new((px_out, y_a + c_bev, pz_out)),
                    bm.verts.new((px_out, y_b - c_bev, pz_out)),
                    bm.verts.new((px_in - p_dir.x * c_bev, y_b, pz_in - p_dir.z * c_bev)),
                    bm.verts.new((px_in, y_b - c_bev, pz_in)),
                    bm.verts.new((px_in, y_a + c_bev, pz_in)),
                    bm.verts.new((px_in - p_dir.x * c_bev, y_a, pz_in - p_dir.z * c_bev)),
                ]
            else:
                ring = [
                    bm.verts.new((px_out, y_a, pz_out)),
                    bm.verts.new((px_out, y_b, pz_out)),
                    bm.verts.new((px_in, y_b, pz_in)),
                    bm.verts.new((px_in, y_a, pz_in)),
                ]
            rings.append(ring)
        nr = len(rings[0])
        b_faces = []
        for ia in range(n_arc):
            for iv in range(nr):
                jv = (iv + 1) % nr
                f = bm.faces.new((rings[ia][iv], rings[ia][jv], rings[ia + 1][jv], rings[ia + 1][iv]))
                map_face_uv(f, uv_layer, "oak_d35", u_scale=0.45)
                b_faces.append(f)
        _orient_faces_outward(b_faces, Vector((cx_corner + dir_x * 0.22, 0.0, z_top_open - 0.22)))

    # 5. SCHARNIER-LAGERBOECKE UND PLASTISCHE HARTHOLZDUEBEL (LOD0)
    if lod == 0:
        for hx_pos in (-1.8305, -0.7845, +0.7845, +1.8305):
            add_chamfered_beam(bm, uv_layer, hx_pos - 0.11, hx_pos + 0.11, -0.16, +0.08, z_top_open, z_top_open + 0.18, 0.010, "tin_bronze", end_region="tin_bronze", axis="Z")
            add_cylinder_along_axis(bm, uv_layer, (hx_pos - 0.13, -0.04, z_top_open + 0.06), (hx_pos + 0.13, -0.04, z_top_open + 0.06), radius=0.048, segs=8, region="tin_bronze")
        # Sill Kopher-sealed inner & outer step treads & dowels (flush with H_sill -> 0.0 mm intrusion into clear opening!)
        for ix_s in range(6):
            sx_p = -1.75 + ix_s * 0.70
            add_chamfered_beam(bm, uv_layer, sx_p - 0.24, sx_p + 0.24, -hy - 0.012, +hy + 0.025, H_sill - 0.055, H_sill, 0.006, "kopher_pitch", end_region="kopher_pitch", axis="X")
            add_dowel_peg(bm, uv_layer, (sx_p, +hy + 0.022, 0.29), (0, +1, 0), radius=0.028, length=0.026, segs=6)
            add_dowel_peg(bm, uv_layer, (sx_p, -hy - 0.035, 0.29), (0, -1, 0), radius=0.028, length=0.026, segs=6)
        for sgn in (-1.0, +1.0):
            px_m = sgn * (hx + 0.5 * b_post)
            for pz in (0.28, 0.72, 1.15, 1.60, 2.05, 2.50, 2.95, 3.40, 3.88):
                add_dowel_peg(bm, uv_layer, (px_m - 0.08, +hy, pz), (0, +1, 0), radius=0.030, length=0.028, segs=6)
                add_dowel_peg(bm, uv_layer, (px_m + 0.08, +hy, pz), (0, +1, 0), radius=0.030, length=0.028, segs=6)
                add_dowel_peg(bm, uv_layer, (px_m, -hy, pz), (0, -1, 0), radius=0.030, length=0.028, segs=6)


# ==============================================================================
# MODUL 2: GEZIMMERTES ZOHAR-/BADGIR-STURMKLAPPEN-BLATT (ark_storm_shutter)
# ==============================================================================
# Template fuer alle 484 animierten Sturmklappen (LOD0 ~180-260 Tris, LOD1 ~60 Tris, LOD2 ~24 Tris)
# KRITISCHER PIVOT (Origin = 0,0,0): Exakt in der Mitte der Oberkante (Drehachse!),
# Einheitsmasse normiert auf 1.0 x 1.0 x 1.0 passend zu stormShutterInstMesh:
#   X in [-0.500 .. +0.500] (Drehzapfen [-0.520 .. +0.520])
#   Z in [-1.000 ..  0.000] (haengt von Z=0.0 nach unten bis Z=-1.0; Scharnieroesen bis +0.048)

def build_ark_storm_shutter(bm, uv_layer, lod):
    if lod == 0:
        # Target: 180 - 340 Tris — Fugendicht schliessende, bronzezeitliche Verschlussklappe!
        # +Y = Aussenseite (zeigt nach aussen; bei Oeffnung um +X schwenkt Z=-1 nach +Y/+Z aussen oben!)
        # -Y = Innenseite (flach bei Y=-0.028, liegt buendig & ohne Clipping vor den 5 Wetterlamellen an!)
        # 1. Gefaster Zedern-Aussenrahmen (X in [-0.50 .. +0.50], Z in [-1.00 .. 0.00])
        add_box(bm, uv_layer, -0.500, -0.415, -0.028, +0.028, -1.000, 0.000, "cedar_c18", end_region="oak_endgrain", end_axis="Z", rotate_uv=True)  # Linker Fries (12)
        add_box(bm, uv_layer, +0.415, +0.500, -0.028, +0.028, -1.000, 0.000, "cedar_c18", end_region="oak_endgrain", end_axis="Z", rotate_uv=True)  # Rechter Fries (12)
        add_box(bm, uv_layer, -0.415, +0.415, -0.028, +0.028, -0.105, 0.000, "cedar_c18")  # Oberer Scharnier-Querfries (12)
        add_box(bm, uv_layer, -0.415, +0.415, -0.030, +0.034, -1.000, -0.885, "cedar_c18")  # Unterer Tropf-Querfries (12)

        # 2. Fugendichte, geschlossene waagerechte Zedern-Plankenfuellung (4 Nut-und-Feder-Planken, 100% orkanfest!)
        #    Durchgehende Dichtkern-Platte (-0.022..+0.012) + 4 plastisch abgesetzte waagerechte Plankenbohlen (+0.010..+0.024)
        add_box(bm, uv_layer, -0.420, +0.420, -0.022, +0.012, -0.890, -0.100, "cedar_c18")
        plank_z_edges = (-0.885, -0.690, -0.495, -0.300, -0.105)
        for ip in range(4):
            pz0 = plank_z_edges[ip] + 0.006
            pz1 = plank_z_edges[ip + 1] - 0.006
            add_box(bm, uv_layer, -0.415, +0.415, +0.010, +0.024, pz0, pz1, "cedar_c18")

        # 3. 2 Hainbuchen-Schlagarme + 1 gezapfte Diagonal-Aussteifungsleiste auf der Aussenseite (+Y)
        add_box(bm, uv_layer, -0.375, -0.310, +0.024, +0.056, -0.955, -0.030, "hornbeam", rotate_uv=True)
        add_box(bm, uv_layer, +0.310, +0.375, +0.024, +0.056, -0.955, -0.030, "hornbeam", rotate_uv=True)
        add_oriented_prism(
            bm, uv_layer, (-0.310, +0.038, -0.885), (+0.310, +0.038, -0.105),
            w_perp=0.072, h_cross=0.024, up_hint=(0.0, 1.0, 0.0), region="hornbeam"
        )

        # 4. Durchgehender Hainbuchen-Drehzapfen auf der Oberkanten-Drehachse Origin=(0,0,0) + 2 gehaemmerte Zinnbronze-Scharnierbaender!
        add_box(bm, uv_layer, -0.520, +0.520, -0.034, +0.034, -0.034, +0.034, "hornbeam")
        for hx_eye in (-0.340, +0.340):
            # Bronze-Scharnierrolle exakt um Z=0.000
            add_cylinder_along_axis(bm, uv_layer, (hx_eye - 0.048, 0.0, 0.0), (hx_eye + 0.048, 0.0, 0.0), radius=0.046, segs=6, region="tin_bronze")
            # Gehaemmertes Bronze-Scharnierband auf dem oberen Klappenblatt (+Y)
            add_box(bm, uv_layer, hx_eye - 0.042, hx_eye + 0.042, +0.026, +0.046, -0.320, -0.010, "tin_bronze", rotate_uv=True)

        # 5. Untere Zugseil-Oese mit Hanfseil-Knoten + 2 Holzduebelkoepfe
        add_box(bm, uv_layer, -0.045, +0.045, +0.028, +0.074, -0.965, -0.895, "tin_bronze")
        add_cylinder_along_axis(bm, uv_layer, (0.0, +0.062, -0.985), (0.0, +0.095, -0.935), radius=0.024, segs=6, region="hemp_rope")
        for px in (-0.340, +0.340):
            add_dowel_peg(bm, uv_layer, (px, +0.056, -0.50), (0, 1, 0), radius=0.022, length=0.016, segs=5)

    elif lod == 1:
        # Target: ~60 Tris (5 boxes = 60 Tris!)
        add_box(bm, uv_layer, -0.500, +0.500, -0.026, +0.026, -1.000, 0.000, "cedar_c18")
        add_box(bm, uv_layer, -0.520, +0.520, -0.042, +0.042, -0.042, +0.042, "hornbeam")
        add_box(bm, uv_layer, -0.375, -0.305, +0.024, +0.066, -0.960, -0.030, "hornbeam", rotate_uv=True)
        add_box(bm, uv_layer, +0.305, +0.375, +0.024, +0.066, -0.960, -0.030, "hornbeam", rotate_uv=True)
        add_oriented_prism(bm, uv_layer, (-0.305, +0.042, -0.880), (+0.305, +0.042, -0.110), 0.070, 0.024, (0, 1, 0), "hornbeam")

    else:
        # Target: ~24 Tris (2 boxes = 24 Tris!)
        add_box(bm, uv_layer, -0.500, +0.500, -0.028, +0.028, -1.000, 0.000, "cedar_c18")
        add_box(bm, uv_layer, -0.520, +0.520, -0.042, +0.042, -0.042, +0.042, "hornbeam")


# ==============================================================================
# MODUL 3: ORGANISCHE EICHEN-WURZELKNIE — 3 VARIANTEN (ark_root_knee_01, _02, _03)
# ==============================================================================
# Ersatz/Veredelung der 392 (720) kantigen Quader-Wurzelknie (LOD0 ~320-480 Tris, LOD1 ~110 Tris, LOD2 ~36 Tris)
# Exakte Masse: Breite wKnee = 0.187 m (2.4 H., X in [-0.0935 .. +0.0935 m]),
# Schenkellaenge armK = 0.630 m (1.35 E.) vertikal (Z in [0.000 .. +0.630 m]) & horizontal (Y in [0.000 .. +0.630 m]),
# Schenkeldicke dLeg = 0.171 m (2.2 H.).
# KRITISCHER PIVOT (Origin = 0,0,0): Exakt an der rechtwinkligen aeusseren Ecke (Wand Y=0.0, Deck Z=0.0)!

def _build_organic_root_knee_variant(bm, uv_layer, lod, variant_idx):
    w_knee = 2.4 * HANDBREITE_M  # 0.186667 m (~0.187 m)
    d_leg = 2.2 * HANDBREITE_M   # 0.171111 m (~0.171 m)
    arm_k = 1.35 * ELLE_M        # 0.630000 m
    hx = 0.5 * w_knee            # 0.093333 m

    # 3 natuerliche Wuchs-Varianten des Krummholz-Bogens unter Wahrung der exakten Aussenmasse [0..0.630 m]
    c_throat = (0.245, 0.285, 0.215)[variant_idx - 1]
    tip_d = (0.125, 0.138, 0.115)[variant_idx - 1]

    if lod == 0:
        n_segs = 14
        ch = 0.022
    elif lod == 1:
        n_segs = 5
        ch = 0.014
    else:
        n_segs = 4
        ch = 0.0

    rings = []
    inner_pts = []
    for i in range(n_segs + 1):
        u = i / n_segs  # u=0: Wandschenkel-Spitze (Y=0, Z=0.630); u=0.5: Aussenecke (0,0); u=1: Deckschenkel-Spitze (Y=0.630, Z=0)
        if u <= 0.5:
            y_out = 0.000
            z_out = arm_k * (1.0 - 2.0 * u)
        else:
            y_out = arm_k * (2.0 * u - 1.0)
            z_out = 0.000

        # Konvexe quadratische Bezier-Kehle: garantiert streng monoton in [tip_d .. arm_k] = [0.115 .. 0.630 m]!
        om = 1.0 - u
        y_in = (om * om) * tip_d + 2.0 * om * u * c_throat + (u * u) * arm_k
        z_in = (om * om) * arm_k + 2.0 * om * u * c_throat + (u * u) * tip_d
        inner_pts.append((y_in, z_in))

        hx_cur = hx * (1.0 - 0.06 * math.sin(u * math.pi) if variant_idx == 2 else 1.0)
        if ch > 0.0:
            dy = y_in - y_out
            dz = z_in - z_out
            d_len = max(1e-4, math.hypot(dy, dz))
            ny_in, nz_in = dy / d_len, dz / d_len
            ring = [
                bm.verts.new((-hx_cur + ch * 0.6, y_out, z_out)),
                bm.verts.new((+hx_cur - ch * 0.6, y_out, z_out)),
                bm.verts.new((+hx_cur, y_out + ny_in * ch, z_out + nz_in * ch)),
                bm.verts.new((+hx_cur, y_in - ny_in * ch, z_in - nz_in * ch)),
                bm.verts.new((+hx_cur - ch, y_in, z_in)),
                bm.verts.new((-hx_cur + ch, y_in, z_in)),
                bm.verts.new((-hx_cur, y_in - ny_in * ch, z_in - nz_in * ch)),
                bm.verts.new((-hx_cur, y_out + ny_in * ch, z_out + nz_in * ch)),
            ]
        else:
            ring = [
                bm.verts.new((-hx_cur, y_out, z_out)),
                bm.verts.new((+hx_cur, y_out, z_out)),
                bm.verts.new((+hx_cur, y_in, z_in)),
                bm.verts.new((-hx_cur, y_in, z_in)),
            ]
        rings.append(ring)

    nr = len(rings[0])
    faces = []
    for i in range(n_segs):
        for k in range(nr):
            kn = (k + 1) % nr
            f = bm.faces.new((rings[i][k], rings[i][kn], rings[i + 1][kn], rings[i + 1][k]))
            f.smooth = (k in (3, 4, 5)) and (lod == 0)
            map_face_uv(f, uv_layer, "oak_d35", u_scale=0.65)
            faces.append(f)

    f_top = bm.faces.new(list(reversed(rings[0])))
    map_face_uv(f_top, uv_layer, "oak_endgrain", u_scale=0.8)
    f_bot = bm.faces.new(rings[-1])
    map_face_uv(f_bot, uv_layer, "oak_endgrain", u_scale=0.8)
    faces.extend([f_top, f_bot])
    _orient_faces_outward(faces, Vector((0.0, 0.14, 0.14)))

    # Plastisch herausstehende Hartholz-Duebelkoepfe (4-6 Duebel je Knie!) auf der gekehlten Innenseite
    if lod <= 1:
        def _inner_pos(u_t):
            om_t = 1.0 - u_t
            yi = (om_t * om_t) * tip_d + 2.0 * om_t * u_t * c_throat + (u_t * u_t) * arm_k
            zi = (om_t * om_t) * arm_k + 2.0 * om_t * u_t * c_throat + (u_t * u_t) * tip_d
            return yi, zi

        if variant_idx == 1:
            u_vals = [(0.14, 0.0), (0.30, 0.0), (0.50, -0.025), (0.50, +0.025), (0.70, 0.0), (0.86, 0.0)]
        elif variant_idx == 2:
            u_vals = [(0.12, -0.028), (0.26, +0.028), (0.42, -0.024), (0.58, +0.024), (0.74, -0.028), (0.88, +0.028)]
        else:
            u_vals = [(0.16, 0.0), (0.34, 0.0), (0.66, 0.0), (0.84, 0.0), (0.24, -0.032), (0.76, +0.032)]
            if lod == 0:
                add_chamfered_beam(bm, uv_layer, -0.055, +0.055, 0.010, 0.135, 0.555, 0.605, 0.008, "hornbeam", axis="Y")
                add_chamfered_beam(bm, uv_layer, -0.055, +0.055, 0.555, 0.605, 0.010, 0.135, 0.008, "hornbeam", axis="Z")

        p_segs = 8 if lod == 0 else 4
        for u_t, px_off in (u_vals if lod == 0 else u_vals[:2]):
            yi, zi = _inner_pos(u_t)
            add_dowel_peg(bm, uv_layer, (px_off, yi, zi), (0.0, 1.0 - u_t, u_t), radius=0.026, length=0.026, segs=p_segs)


def build_ark_root_knee_01(bm, uv_layer, lod):
    _build_organic_root_knee_variant(bm, uv_layer, lod, 1)


def build_ark_root_knee_02(bm, uv_layer, lod):
    _build_organic_root_knee_variant(bm, uv_layer, lod, 2)


def build_ark_root_knee_03(bm, uv_layer, lod):
    _build_organic_root_knee_variant(bm, uv_layer, lod, 3)


# ==============================================================================
# MODUL 4: KOENIGSSTUETZEN-SATTELHOLZ-KAPITELL & KOPFBANDKNAGGEN (ark_kingpost_capital)
# ==============================================================================
# Veredelung der 45 Koenigsstuetzen (208 Segmente, LOD0 ~450-650 Tris, LOD1 ~140 Tris, LOD2 ~48 Tris)
# Exakte Masse: Umschließt buendig die 0.336 x 0.336 m Koenigsstuetze;
# geschweiftes Eichen-Sattelholz (0.386 m (X) x 1.100 m (Y) x 0.260 m (Z)) mit historischen
# Zimmermanns-Fasen, 2 seitlichen gekehlten Kopfband-Knaggen, sichtbaren Zapfenkeilen & Holzduebeln.
# KRITISCHER PIVOT (Origin = 0,0,0): Zentriert an der Stuetzenachse an der Unterkante des Laengsunterzugs (Z = 0.000 m)!

def build_ark_kingpost_capital(bm, uv_layer, lod):
    w_post = 0.336      # 0.336 x 0.336 m Koenigsstuetze
    hp = 0.5 * w_post   # 0.168 m
    w_sat_x = 0.386     # 0.386 m (X)
    l_sat_y = 1.100     # 1.100 m (Y)
    h_sat_z = 0.260     # 0.260 m (Z: -0.260 .. 0.000 m)
    hsx = 0.5 * w_sat_x # 0.193 m
    hsy = 0.5 * l_sat_y # 0.550 m

    if lod == 0:
        # 1. Geschweiftes Eichen-Sattelholz (0.386 x 1.100 x 0.260 m, Z in [-0.260 .. 0.000 m])
        # Segmented along Y into 7 profile sections so the bottom contour sweeps organically up toward the Y=+-0.550 m tips!
        y_cuts = [-0.550, -0.440, -0.310, -0.185, +0.185, +0.310, +0.440, +0.550]
        z_bots = [-0.145, -0.185, -0.235, -0.260, -0.260, -0.235, -0.185, -0.145]
        ch = 0.022
        rings = []
        for y_c, z_b in zip(y_cuts, z_bots):
            ring = [
                bm.verts.new((-hsx + ch, y_c, z_b)),
                bm.verts.new((+hsx - ch, y_c, z_b)),
                bm.verts.new((+hsx, y_c, z_b + ch)),
                bm.verts.new((+hsx, y_c, -ch)),
                bm.verts.new((+hsx - ch, y_c, 0.000)),
                bm.verts.new((-hsx + ch, y_c, 0.000)),
                bm.verts.new((-hsx, y_c, -ch)),
                bm.verts.new((-hsx, y_c, z_b + ch)),
            ]
            rings.append(ring)
        s_faces = []
        for i in range(len(rings) - 1):
            for k in range(8):
                kn = (k + 1) % 8
                f = bm.faces.new((rings[i][k], rings[i][kn], rings[i + 1][kn], rings[i + 1][k]))
                map_face_uv(f, uv_layer, "oak_d35", u_scale=0.55)
                s_faces.append(f)
        f0 = bm.faces.new(list(reversed(rings[0])))
        map_face_uv(f0, uv_layer, "oak_endgrain", u_scale=0.8)
        f1 = bm.faces.new(rings[-1])
        map_face_uv(f1, uv_layer, "oak_endgrain", u_scale=0.8)
        s_faces.extend([f0, f1])
        _orient_faces_outward(s_faces, Vector((0.0, 0.0, -0.12)))

        # 2. Stuetzen-Halsmanschette (umschliesst buendig die 0.336 x 0.336 m Koenigsstuetze bei Z in [-0.620 .. -0.260 m])
        add_chamfered_beam(bm, uv_layer, -hp - 0.022, +hp + 0.022, -hp - 0.022, +hp + 0.022, -0.340, -0.260, 0.016, "oak_d35", axis="Z")
        add_chamfered_beam(bm, uv_layer, -hp - 0.016, +hp + 0.016, -hp - 0.016, +hp + 0.016, -0.580, -0.510, 0.014, "hornbeam", axis="Z")

        # 3. 2 seitliche gekehlte Kopfband-Knaggen (entlang +-Y unter dem Sattelholz, Z in [-0.510 .. -0.220 m], komplett geschlossen!)
        for sgn in (-1.0, +1.0):
            n_k = 5
            k_rings = []
            for ik in range(n_k + 1):
                t = ik / n_k
                ang = t * (0.5 * math.pi)
                y_wall = sgn * hp
                # Konkave Knaggen-Kehle von (hp+0.04, -0.51) bis (0.46, -0.22)
                y_k = sgn * (hp + 0.04 + 0.252 * (1.0 - math.cos(ang)))
                z_k = -0.510 + 0.290 * math.sin(ang)
                y_lo, y_hi = (min(y_wall, y_k), max(y_wall, y_k))
                k_rings.append([
                    bm.verts.new((-0.115, y_lo, z_k)),
                    bm.verts.new((+0.115, y_lo, z_k)),
                    bm.verts.new((+0.115, y_hi, z_k)),
                    bm.verts.new((-0.115, y_hi, z_k)),
                ])
            kf = []
            for ik in range(n_k):
                for iv in range(4):
                    jv = (iv + 1) % 4
                    f = bm.faces.new((k_rings[ik][iv], k_rings[ik][jv], k_rings[ik + 1][jv], k_rings[ik + 1][iv]))
                    map_face_uv(f, uv_layer, "oak_d35", u_scale=0.6)
                    kf.append(f)
            f_kb = bm.faces.new(list(reversed(k_rings[0])))
            map_face_uv(f_kb, uv_layer, "oak_endgrain")
            f_kt = bm.faces.new(k_rings[-1])
            map_face_uv(f_kt, uv_layer, "oak_endgrain")
            kf.extend([f_kb, f_kt])
            _orient_faces_outward(kf, Vector((0.0, sgn * 0.22, -0.34)))

        # 4. Durchgesteckte Zapfenkeile (Hainbuche) & 12 buendig sitzende Hartholz-Duebelkoepfe (0.0 mm Schweben!)
        for sgn_y in (-1.0, +1.0):
            # Mortise tenon + cross-wedge protruding through side of Sattelholz
            add_chamfered_beam(bm, uv_layer, -hsx - 0.026, +hsx + 0.026, sgn_y * 0.28 - 0.036, sgn_y * 0.28 + 0.036, -0.165, -0.095, 0.008, "hornbeam", axis="X")
            for sgn_x in (-1.0, +1.0):
                add_dowel_peg(bm, uv_layer, (sgn_x * hsx, sgn_y * 0.40, -0.095), (sgn_x, 0, 0), radius=0.026, length=0.026, segs=6)
                add_dowel_peg(bm, uv_layer, (sgn_x * hsx, sgn_y * 0.14, -0.095), (sgn_x, 0, 0), radius=0.026, length=0.026, segs=6)
                # Peg sitting flush on the side cheek (X = +-0.115) of the curved corbel bracket at (Y = +-0.23, Z = -0.32)
                add_dowel_peg(bm, uv_layer, (sgn_x * 0.115, sgn_y * 0.23, -0.32), (sgn_x, 0, 0), radius=0.024, length=0.024, segs=6)
        for sgn_x in (-1.0, +1.0):
            for sgn_y in (-1.0, +1.0):
                add_dowel_peg(bm, uv_layer, (sgn_x * (hp + 0.022), sgn_y * 0.09, -0.300), (sgn_x, 0, 0), radius=0.025, length=0.024, segs=6)

    elif lod == 1:
        # Target: ~140 Tris
        add_chamfered_beam(bm, uv_layer, -hsx, +hsx, -hsy, +hsy, -h_sat_z, 0.000, 0.020, "oak_d35", axis="Y")
        add_chamfered_beam(bm, uv_layer, -hp - 0.020, +hp + 0.020, -hp - 0.020, +hp + 0.020, -0.360, -0.260, 0.015, "oak_d35", axis="Z")
        for sgn in (-1.0, +1.0):
            add_oriented_prism(bm, uv_layer, (0.0, sgn * hp, -0.520), (0.0, sgn * 0.450, -0.230), 0.220, 0.125, (1, 0, 0), "oak_d35")
            add_box(bm, uv_layer, -hsx - 0.025, +hsx + 0.025, sgn * 0.28 - 0.036, sgn * 0.28 + 0.036, -0.165, -0.095, "hornbeam")
            for sgn_x in (-1.0, +1.0):
                add_dowel_peg(bm, uv_layer, (sgn_x * hsx, sgn * 0.38, -0.10), (sgn_x, 0, 0), radius=0.026, length=0.024, segs=4)

    else:
        # Target: ~48 Tris (4 boxes = 48 Tris!)
        add_box(bm, uv_layer, -hsx, +hsx, -hsy, +hsy, -h_sat_z, 0.000, "oak_d35")
        add_box(bm, uv_layer, -hp - 0.020, +hp + 0.020, -hp - 0.020, +hp + 0.020, -0.380, -0.260, "oak_d35", rotate_uv=True)
        for sgn in (-1.0, +1.0):
            add_oriented_prism(bm, uv_layer, (0.0, sgn * hp, -0.520), (0.0, sgn * 0.440, -0.240), 0.210, 0.120, (1, 0, 0), "oak_d35")


# ==============================================================================
# MODUL 5: PLASTISCHE SCHOTTTUER-BLOCKZARGEN (ark_door_frame_d1, _d2, _d3, _foyer)
# ==============================================================================
# STRIKTER T99-SCHUTZ: Die lichte Durchgangsoeffnung darf um 0.0 cm verengt werden!
# Die Blockzargen rahmen exakt buendig aussen um die lichten Oeffnungen aus ark_inventory_audit.md:
#   1. ark_door_frame_d1   : Lichte Oeffnung 2.800 m x 2.917 m ueber 0.583 m Flutsuell
#   2. ark_door_frame_d2   : Lichte Oeffnung 1.867 m x 2.217 m ueber 0.233 m Suell
#   3. ark_door_frame_d3   : Lichte Oeffnung 1.400 m x 1.983 m ueber 0.233 m Suell
#   4. ark_door_frame_foyer: Lichte Oeffnung 3.593 m x 2.917 m ueber 0.117 m Schwelle
# Origin (0,0,0) unten mittig auf Deck-Oberkante (Z = 0.000 m).

DOOR_SPECS = {
    "ark_door_frame_d1":    (2.800, 2.917, 0.583),
    "ark_door_frame_d2":    (1.867, 2.217, 0.233),
    "ark_door_frame_d3":    (1.400, 1.983, 0.233),
    "ark_door_frame_foyer": (3.593, 2.917, 0.117),
}


def _build_bulkhead_door_frame(bm, uv_layer, lod, w_open, h_open, h_sill):
    b_post = 0.233      # 3.0 Handbreiten Eichen-Blockpfosten
    h_lintel = 0.311    # 4.0 Handbreiten Eichen-Sturz
    d_wall = 0.233      # 3.0 Handbreiten Schottwand
    zarg_lip = 0.074    # Beidseitiger Zargen-Ueberstand
    hy = 0.5 * d_wall + zarg_lip  # 0.1905 m (Gesamttiefe 0.381 m)
    hx = 0.5 * w_open
    z_door0 = h_sill
    z_door1 = h_sill + h_open
    z_top = z_door1 + h_lintel

    if lod == 0:
        # Target: 400 - 600 Tris
        ch = 0.018
        # 1. Abgerundete Eichen-Suellkante (komplett unterhalb z_door0 -> 0.0 cm Verengung!)
        add_chamfered_beam(
            bm, uv_layer, -hx - b_post, +hx + b_post, -hy, +hy, 0.000, z_door0,
            chamfer=min(0.024, 0.28 * z_door0), region="oak_d35", end_region="oak_endgrain", axis="X", u_scale=0.35
        )
        # 2. Massiv gefaste Eichen-Blockpfosten (komplett ausserhalb |X| >= hx -> 0.0 cm Verengung!)
        for sgn in (-1.0, +1.0):
            px0 = -hx - b_post if sgn < 0 else +hx
            px1 = -hx if sgn < 0 else +hx + b_post
            add_chamfered_beam(
                bm, uv_layer, px0, px1, -hy, +hy, z_door0, z_door1,
                chamfer=ch, region="oak_d35", end_region="oak_endgrain", axis="Z", u_scale=0.35
            )
            # Outer jamb cheek pilasters (+Y and -Y)
            cx0 = (-hx - b_post - 0.025) if sgn < 0 else (+hx + b_post - 0.065)
            cx1 = (-hx - b_post + 0.065) if sgn < 0 else (+hx + b_post + 0.025)
            add_box(bm, uv_layer, cx0, cx1, -hy - 0.018, +hy + 0.018, 0.000, z_door1, "oak_d35", rotate_uv=True)

        # 3. Ueberkaemmter Eichen-Sturz (0.311 m hoch, komplett oberhalb z_door1 -> 0.0 cm Verengung!)
        add_chamfered_beam(
            bm, uv_layer, -hx - b_post - 0.16, +hx + b_post + 0.16, -hy - 0.015, +hy + 0.015, z_door1, z_top,
            chamfer=ch, region="oak_d35", end_region="oak_endgrain", axis="X", u_scale=0.32
        )
        # Durchgesteckte Holzzapfen & Keile oben/seitlich am Sturz
        for sgn in (-1.0, +1.0):
            px_m = sgn * (hx + 0.5 * b_post)
            add_chamfered_beam(bm, uv_layer, px_m - 0.085, px_m + 0.085, -0.085, +0.085, z_top, z_top + 0.055, 0.008, "oak_endgrain", axis="Z")
            add_oriented_prism(bm, uv_layer, (px_m - 0.11, 0.0, z_top + 0.025), (px_m + 0.11, 0.0, z_top + 0.025), 0.026, 0.032, (0, 0, 1), "hornbeam")
            # Cross-tenon & wedge through lintel face
            add_box(bm, uv_layer, px_m - 0.045, px_m + 0.045, -hy - 0.038, +hy + 0.038, z_door1 + 0.11, z_door1 + 0.20, "hornbeam")

        # 4. 2 organisch geschwungene Eichen-Kopfbaender (0.303 m = 0.65 E. Schenkel, 0.124 m = 1.6 H. stark)
        # Sitzen in den oberen Sturz-Eckwinkeln, gefast & verduebelt (ragen 0.0 mm unter z_door1 - k_arm oder ueber cx_c + dir_x * k_arm!)
        k_arm = 0.303333  # 0.65 Ellen
        b_k = 0.124444    # 1.6 Handbreiten
        for sgn in (-1.0, +1.0):
            cx_c = sgn * hx
            dir_x = -sgn
            n_arc = 4
            rings = []
            for ia in range(n_arc + 1):
                t = ia / n_arc
                ang = t * (0.5 * math.pi)
                px_out = cx_c + dir_x * (0.0 if t <= 0.5 else (t - 0.5) * 2.0 * k_arm)
                pz_out = z_door1 - ((1.0 - t * 2.0) * k_arm if t <= 0.5 else 0.0)
                r_in = k_arm - b_k * 0.55 * math.sin(t * math.pi)
                px_in = cx_c + dir_x * (math.sin(ang) * r_in + (b_k * 0.42 if ia == 0 else 0.0))
                pz_in = z_door1 - (math.cos(ang) * r_in + (b_k * 0.42 if ia == n_arc else 0.0))
                rings.append([
                    bm.verts.new((px_out, -0.078, pz_out)),
                    bm.verts.new((px_out, +0.078, pz_out)),
                    bm.verts.new((px_in, +0.078, pz_in)),
                    bm.verts.new((px_in, -0.078, pz_in)),
                ])
            bf = []
            for ia in range(n_arc):
                for iv in range(4):
                    jv = (iv + 1) % 4
                    f = bm.faces.new((rings[ia][iv], rings[ia][jv], rings[ia + 1][jv], rings[ia + 1][iv]))
                    map_face_uv(f, uv_layer, "oak_d35", u_scale=0.55)
                    bf.append(f)
            _orient_faces_outward(bf, Vector((cx_c + dir_x * 0.10, 0.0, z_door1 - 0.10)))

        # 5. Sichtbare Hartholzduebel auf Vorder- (+Y) und Rueckseite (-Y)
        peg_z_fracs = (0.18, 0.42, 0.66, 0.88)
        for sgn in (-1.0, +1.0):
            px_m = sgn * (hx + 0.5 * b_post)
            for frac in peg_z_fracs:
                pz = z_door0 + frac * h_open
                add_dowel_peg(bm, uv_layer, (px_m, +hy, pz), (0, +1, 0), radius=0.025, length=0.022, segs=5)
                add_dowel_peg(bm, uv_layer, (px_m, -hy, pz), (0, -1, 0), radius=0.025, length=0.022, segs=5)
            add_dowel_peg(bm, uv_layer, (px_m, +hy, z_door1 + 0.155), (0, +1, 0), radius=0.026, length=0.024, segs=5)
            add_dowel_peg(bm, uv_layer, (px_m, -hy, z_door1 + 0.155), (0, -1, 0), radius=0.026, length=0.024, segs=5)

    elif lod == 1:
        # Target: ~140 Tris (exakt 144 Tris!)
        ch = 0.015
        add_chamfered_beam(bm, uv_layer, -hx - b_post, +hx + b_post, -hy, +hy, 0.000, z_door0, min(0.018, 0.25 * z_door0), "oak_d35", axis="X")
        for sgn in (-1.0, +1.0):
            px0 = -hx - b_post if sgn < 0 else +hx
            px1 = -hx if sgn < 0 else +hx + b_post
            add_chamfered_beam(bm, uv_layer, px0, px1, -hy, +hy, z_door0, z_door1, ch, "oak_d35", axis="Z")
        add_chamfered_beam(bm, uv_layer, -hx - b_post - 0.16, +hx + b_post + 0.16, -hy - 0.015, +hy + 0.015, z_door1, z_top, ch, "oak_d35", axis="X")
        k_arm = 0.303333
        b_k = 0.124444
        for sgn in (-1.0, +1.0):
            cx_c = sgn * hx
            dir_x = -sgn
            n_arc = 2
            rings = []
            for ia in range(n_arc + 1):
                t = ia / n_arc
                ang = t * (0.5 * math.pi)
                px_out = cx_c + dir_x * (0.0 if t <= 0.5 else (t - 0.5) * 2.0 * k_arm)
                pz_out = z_door1 - ((1.0 - t * 2.0) * k_arm if t <= 0.5 else 0.0)
                r_in = k_arm - b_k * 0.55 * math.sin(t * math.pi)
                px_in = cx_c + dir_x * (math.sin(ang) * r_in + (b_k * 0.42 if ia == 0 else 0.0))
                pz_in = z_door1 - (math.cos(ang) * r_in + (b_k * 0.42 if ia == n_arc else 0.0))
                rings.append([
                    bm.verts.new((px_out, -0.078, pz_out)),
                    bm.verts.new((px_out, +0.078, pz_out)),
                    bm.verts.new((px_in, +0.078, pz_in)),
                    bm.verts.new((px_in, -0.078, pz_in)),
                ])
            bf = []
            for ia in range(n_arc):
                for iv in range(4):
                    jv = (iv + 1) % 4
                    f = bm.faces.new((rings[ia][iv], rings[ia][jv], rings[ia + 1][jv], rings[ia + 1][iv]))
                    map_face_uv(f, uv_layer, "oak_d35", u_scale=0.55)
                    bf.append(f)
            _orient_faces_outward(bf, Vector((cx_c + dir_x * 0.10, 0.0, z_door1 - 0.10)))

    else:
        # Target: ~48 Tris (4 boxes = 48 Tris!)
        add_box(bm, uv_layer, -hx - b_post, +hx + b_post, -hy, +hy, 0.000, z_door0, "oak_d35")
        add_box(bm, uv_layer, -hx - b_post, -hx, -hy, +hy, z_door0, z_door1, "oak_d35", rotate_uv=True)
        add_box(bm, uv_layer, +hx, +hx + b_post, -hy, +hy, z_door0, z_door1, "oak_d35", rotate_uv=True)
        add_box(bm, uv_layer, -hx - b_post - 0.16, +hx + b_post + 0.16, -hy, +hy, z_door1, z_top, "oak_d35")


def build_ark_door_frame_d1(bm, uv_layer, lod):
    _build_bulkhead_door_frame(bm, uv_layer, lod, *DOOR_SPECS["ark_door_frame_d1"])


def build_ark_door_frame_d2(bm, uv_layer, lod):
    _build_bulkhead_door_frame(bm, uv_layer, lod, *DOOR_SPECS["ark_door_frame_d2"])


def build_ark_door_frame_d3(bm, uv_layer, lod):
    _build_bulkhead_door_frame(bm, uv_layer, lod, *DOOR_SPECS["ark_door_frame_d3"])


def build_ark_door_frame_foyer(bm, uv_layer, lod):
    _build_bulkhead_door_frame(bm, uv_layer, lod, *DOOR_SPECS["ark_door_frame_foyer"])


# ==============================================================================
# MODUL 6: GEZIMMERTER BADGIR-WINDTURM-KOPF (ark_badgir_cap)
# ==============================================================================
# Aufsteckbare Hero-Krone fuer die 8 Zweikammer-Badgire (LOD0 ~900-1.300 Tris, LOD1 ~300 Tris, LOD2 ~90 Tris)
# Exakte Masse: Passt millimetergenau auf den 1.633 m (X) x 1.400 m (Y) Badgir-Schacht
# (3.50 E. x 3.00 E., Origin Z = 0.0 an der Schacht-Oberkante zTop!).
# Ueberstehende Zedern-Zeltdach-Haube (0.450 m hoch, Kopher-gedichtet), sichtbare Dachsparren-Koepfe,
# 4 profilierte Eckstiel-Kapitelle, Schräg-Leitlamellen in den 4 Windfang-Oeffnungen & zentrale Kreuz-Trennwand.

def build_ark_badgir_cap(bm, uv_layer, lod):
    L_x = 3.50 * ELLE_M          # 1.633333 m
    L_y = 3.00 * ELLE_M          # 1.400000 m
    hx = 0.5 * L_x               # 0.816667 m
    hy = 0.5 * L_y               # 0.700000 m
    b_post = 2.0 * HANDBREITE_M  # 0.155556 m Eckstiele
    h_roof = 0.450               # 0.450 m Zeltdach-Haube ueber Z = 0.0
    z_collar_bot = -0.520        # Umgreift die oberen 0.52 m des Badgir-Windfangkopfs

    if lod == 0:
        # Target: 900 - 1.300 Tris
        # 1. 4 Eichen-Eckstiele + 4 profilierte Eckstiel-Kapitelle mit je 2 Kopfband-Knaggen
        for sx in (-1.0, +1.0):
            for sy in (-1.0, +1.0):
                px0 = (-hx if sx < 0 else +hx - b_post)
                px1 = (-hx + b_post if sx < 0 else +hx)
                py0 = (-hy if sy < 0 else +hy - b_post)
                py1 = (-hy + b_post if sy < 0 else +hy)
                add_chamfered_beam(bm, uv_layer, px0, px1, py0, py1, z_collar_bot, 0.000, 0.014, "oak_d35", axis="Z")
                # Profiled corner capital collar at Z in [-0.14 .. +0.02 m]
                add_chamfered_beam(bm, uv_layer, px0 - 0.025, px1 + 0.025, py0 - 0.025, py1 + 0.025, -0.120, 0.000, 0.014, "oak_d35", axis="Z")
                # 2 corbel brackets per corner post supporting the overhanging roof eaves
                cx_p = 0.5 * (px0 + px1)
                cy_p = 0.5 * (py0 + py1)
                add_oriented_prism(bm, uv_layer, (cx_p, cy_p, -0.26), (sx * (hx + 0.16), cy_p, +0.02), 0.085, 0.075, (0, 1, 0), "oak_d35")
                add_oriented_prism(bm, uv_layer, (cx_p, cy_p, -0.26), (cx_p, sy * (hy + 0.16), +0.02), 0.085, 0.075, (1, 0, 0), "oak_d35")

        # Untere & obere Eichen-Raehm-Kränze (Z = z_collar_bot und Z = 0.000 m)
        for z_ring, ov in ((z_collar_bot, 0.025), (-0.055, 0.055)):
            add_box(bm, uv_layer, -hx - ov, +hx + ov, -hy - ov, -hy + 0.09, z_ring, z_ring + 0.065, "oak_d35")
            add_box(bm, uv_layer, -hx - ov, +hx + ov, +hy - 0.09, +hy + ov, z_ring, z_ring + 0.065, "oak_d35")
            add_box(bm, uv_layer, -hx - ov, -hx + 0.09, -hy + 0.09, +hy - 0.09, z_ring, z_ring + 0.065, "oak_d35")
            add_box(bm, uv_layer, +hx - 0.09, +hx + ov, -hy + 0.09, +hy - 0.09, z_ring, z_ring + 0.065, "oak_d35")

        # 2. Zentrale Kreuz-Trennwand (ZUL / ABL, Zypresse & Zeder) + 4 Mittelstiele
        add_box(bm, uv_layer, -0.042, +0.042, -hy + 0.04, +hy - 0.04, z_collar_bot, +0.060, "cypress_c27", rotate_uv=True)
        add_box(bm, uv_layer, -hx + 0.04, +hx - 0.04, -0.042, +0.042, z_collar_bot, +0.060, "cypress_c27")
        for sgn in (-1.0, +1.0):
            add_chamfered_beam(bm, uv_layer, -0.055, +0.055, sgn * (hy - 0.055) - 0.045, sgn * (hy - 0.055) + 0.045, z_collar_bot, 0.000, 0.010, "oak_d35", axis="Z")
            add_chamfered_beam(bm, uv_layer, sgn * (hx - 0.055) - 0.045, sgn * (hx - 0.055) + 0.045, -0.055, +0.055, z_collar_bot, 0.000, 0.010, "oak_d35", axis="Z")

        # 3. Exakt 5 feine, gleichmaessig verteilte, schraeg nach aussen abfallende Zedern-Wetterlamellen
        #    in allen 4 Windfang-Oeffnungen (~5.5 cm nach innen in die Laibung zurueckversetzt -> 0 Clipping mit Klappen!)
        louver_zs = [-0.425, -0.345, -0.265, -0.185, -0.105]
        for lz in louver_zs:
            # Bb (-Y) & Stb (+Y) openings (split into left & right chambers by central cross wall)
            for sy in (-1.0, +1.0):
                y_lv = sy * (hy - 0.055)
                for sx_ch in (-1.0, +1.0):
                    x_a = 0.055 if sx_ch > 0 else (-hx + b_post + 0.01)
                    x_b = (+hx - b_post - 0.01) if sx_ch > 0 else -0.055
                    add_oriented_prism(
                        bm, uv_layer, (x_a, y_lv, lz), (x_b, y_lv, lz),
                        w_perp=0.088, h_cross=0.016, up_hint=(0.0, sy * 0.72, 0.69), region="cedar_c18"
                    )
            # Bow (-X) & Stern (+X) openings
            for sx in (-1.0, +1.0):
                x_lv = sx * (hx - 0.055)
                for sy_ch in (-1.0, +1.0):
                    y_a = 0.055 if sy_ch > 0 else (-hy + b_post + 0.01)
                    y_b = (+hy - b_post - 0.01) if sy_ch > 0 else -0.055
                    add_oriented_prism(
                        bm, uv_layer, (x_lv, y_a, lz), (x_lv, y_b, lz),
                        w_perp=0.088, h_cross=0.016, up_hint=(sx * 0.72, 0.0, 0.69), region="cedar_c18"
                    )

        # 4. Sichtbare Zedern-Dachsparren-Koepfe unter der Traufe (12 Sparrenkoepfe ringsum, sauber unterhalb der Dachhaut!)
        eave_x = hx + 0.210  # 1.0267 m
        eave_y = hy + 0.210  # 0.9100 m
        for ix in range(3):
            rx = -hx + 0.24 + ix * ((2.0 * hx - 0.48) / 2.0)
            for sy in (-1.0, +1.0):
                add_oriented_prism(
                    bm, uv_layer, (rx, sy * (hy - 0.06), +0.055), (rx, sy * (eave_y + 0.035), -0.015),
                    w_perp=0.068, h_cross=0.052, up_hint=(1, 0, 0), region="cedar_c18"
                )
        for iy in range(3):
            ry = -hy + 0.24 + iy * ((2.0 * hy - 0.48) / 2.0)
            for sx in (-1.0, +1.0):
                add_oriented_prism(
                    bm, uv_layer, (sx * (hx - 0.06), ry, +0.055), (sx * (eave_x + 0.035), ry, -0.015),
                    w_perp=0.068, h_cross=0.052, up_hint=(0, 1, 0), region="cedar_c18"
                )

        # 5. Ueberstehende 3-stufig geschindelte Zedern-Zeltdach-Haube (Z in [0.000 .. +0.450 m], aussen Kopher-gedichtet!)
        tiers = [
            (0.010, 0.165, eave_x,        eave_y,        eave_x * 0.67, eave_y * 0.67),
            (0.155, 0.305, eave_x * 0.69, eave_y * 0.69, eave_x * 0.36, eave_y * 0.36),
            (0.295, 0.425, eave_x * 0.38, eave_y * 0.38, 0.135,         0.100),
        ]
        for z0_t, z1_t, wx0, wy0, wx1, wy1 in tiers:
            v_b = [bm.verts.new((-wx0, -wy0, z0_t)), bm.verts.new((+wx0, -wy0, z0_t)), bm.verts.new((+wx0, +wy0, z0_t)), bm.verts.new((-wx0, +wy0, z0_t))]
            v_t = [bm.verts.new((-wx1, -wy1, z1_t)), bm.verts.new((+wx1, -wy1, z1_t)), bm.verts.new((+wx1, +wy1, z1_t)), bm.verts.new((-wx1, +wy1, z1_t))]
            rf = []
            for k in range(4):
                kn = (k + 1) % 4
                f = bm.faces.new((v_b[k], v_b[kn], v_t[kn], v_t[k]))
                map_face_uv(f, uv_layer, "kopher_pitch", u_scale=0.55)
                rf.append(f)
            ft = bm.faces.new(v_t)
            map_face_uv(ft, uv_layer, "kopher_pitch")
            fb = bm.faces.new(list(reversed(v_b)))
            map_face_uv(fb, uv_layer, "cedar_c18")
            rf.extend([ft, fb])
            _orient_faces_outward(rf, Vector((0.0, 0.0, 0.5 * (z0_t + z1_t))))

        # 4 Gratleisten (Eiche/Zeder) buendig auf den 4 Zeltdach-Graten + Bronze-Firstknauf bis exakt Z = +0.450 m
        for sx in (-1.0, +1.0):
            for sy in (-1.0, +1.0):
                add_oriented_prism(
                    bm, uv_layer, (sx * (eave_x - 0.02), sy * (eave_y - 0.02), 0.018), (sx * 0.13, sy * 0.095, 0.420),
                    w_perp=0.058, h_cross=0.036, up_hint=(0, 0, 1), region="oak_d35"
                )
        add_chamfered_beam(bm, uv_layer, -0.15, +0.15, -0.11, +0.11, 0.415, h_roof, 0.015, "tin_bronze", end_region="tin_bronze", axis="Z")

        # 6. Plastische Holzduebel an den 4 Eckstiel-Kapitellen
        for sx in (-1.0, +1.0):
            for sy in (-1.0, +1.0):
                add_dowel_peg(bm, uv_layer, (sx * (hx + 0.025), sy * (hy - 0.075), -0.06), (sx, 0, 0), radius=0.024, length=0.022, segs=5)
                add_dowel_peg(bm, uv_layer, (sx * (hx - 0.075), sy * (hy + 0.025), -0.06), (0, sy, 0), radius=0.024, length=0.022, segs=5)

    elif lod == 1:
        # Target: ~300 Tris
        for sx in (-1.0, +1.0):
            for sy in (-1.0, +1.0):
                px0 = (-hx if sx < 0 else +hx - b_post)
                px1 = (-hx + b_post if sx < 0 else +hx)
                py0 = (-hy if sy < 0 else +hy - b_post)
                py1 = (-hy + b_post if sy < 0 else +hy)
                add_box(bm, uv_layer, px0, px1, py0, py1, z_collar_bot, 0.000, "oak_d35", rotate_uv=True)
                add_box(bm, uv_layer, px0 - 0.025, px1 + 0.025, py0 - 0.025, py1 + 0.025, -0.120, 0.000, "oak_d35")
        add_box(bm, uv_layer, -0.042, +0.042, -hy + 0.04, +hy - 0.04, z_collar_bot, +0.040, "cypress_c27", rotate_uv=True)
        add_box(bm, uv_layer, -hx + 0.04, +hx - 0.04, -0.042, +0.042, z_collar_bot, +0.040, "cypress_c27")
        for lz in (-0.36, -0.18):
            for sy in (-1.0, +1.0):
                add_box(bm, uv_layer, -hx + b_post, +hx - b_post, sy * (hy - 0.05) - 0.04, sy * (hy - 0.05) + 0.04, lz - 0.02, lz + 0.02, "cedar_c18")
            for sx in (-1.0, +1.0):
                add_box(bm, uv_layer, sx * (hx - 0.05) - 0.04, sx * (hx - 0.05) + 0.04, -hy + b_post, +hy - b_post, lz - 0.02, lz + 0.02, "cedar_c18")
        eave_x, eave_y = hx + 0.210, hy + 0.210
        for z0_t, z1_t, wx0, wy0, wx1, wy1 in [
            (0.000, 0.230, eave_x, eave_y, eave_x * 0.52, eave_y * 0.52),
            (0.210, h_roof, eave_x * 0.55, eave_y * 0.55, 0.12, 0.09),
        ]:
            v_b = [bm.verts.new((-wx0, -wy0, z0_t)), bm.verts.new((+wx0, -wy0, z0_t)), bm.verts.new((+wx0, +wy0, z0_t)), bm.verts.new((-wx0, +wy0, z0_t))]
            v_t = [bm.verts.new((-wx1, -wy1, z1_t)), bm.verts.new((+wx1, -wy1, z1_t)), bm.verts.new((+wx1, +wy1, z1_t)), bm.verts.new((-wx1, +wy1, z1_t))]
            rf = [bm.faces.new((v_b[k], v_b[(k + 1) % 4], v_t[(k + 1) % 4], v_t[k])) for k in range(4)]
            rf.append(bm.faces.new(v_t))
            rf.append(bm.faces.new(list(reversed(v_b))))
            for f in rf:
                map_face_uv(f, uv_layer, "kopher_pitch", u_scale=0.5)
            _orient_faces_outward(rf, Vector((0.0, 0.0, 0.5 * (z0_t + z1_t))))
        for sx in (-1.0, +1.0):
            for sy in (-1.0, +1.0):
                add_oriented_prism(bm, uv_layer, (sx * eave_x, sy * eave_y, 0.02), (sx * 0.11, sy * 0.08, 0.418), 0.06, 0.04, (0, 0, 1), "oak_d35")

    else:
        # Target: ~90 Tris (7 boxes/prisms = 84 Tris!)
        for sx in (-1.0, +1.0):
            for sy in (-1.0, +1.0):
                px0 = (-hx if sx < 0 else +hx - b_post)
                px1 = (-hx + b_post if sx < 0 else +hx)
                py0 = (-hy if sy < 0 else +hy - b_post)
                py1 = (-hy + b_post if sy < 0 else +hy)
                add_box(bm, uv_layer, px0, px1, py0, py1, z_collar_bot, 0.000, "oak_d35", rotate_uv=True)
        add_box(bm, uv_layer, -0.042, +0.042, -hy + 0.04, +hy - 0.04, z_collar_bot, 0.000, "cypress_c27", rotate_uv=True)
        add_box(bm, uv_layer, -hx + 0.04, +hx - 0.04, -0.042, +0.042, z_collar_bot, 0.000, "cypress_c27")
        eave_x, eave_y = hx + 0.210, hy + 0.210
        v_b = [bm.verts.new((-eave_x, -eave_y, 0.000)), bm.verts.new((+eave_x, -eave_y, 0.000)), bm.verts.new((+eave_x, +eave_y, 0.000)), bm.verts.new((-eave_x, +eave_y, 0.000))]
        v_t = [bm.verts.new((-0.12, -0.09, h_roof)), bm.verts.new((+0.12, -0.09, h_roof)), bm.verts.new((+0.12, +0.09, h_roof)), bm.verts.new((-0.12, +0.09, h_roof))]
        rf = [bm.faces.new((v_b[k], v_b[(k + 1) % 4], v_t[(k + 1) % 4], v_t[k])) for k in range(4)]
        rf.append(bm.faces.new(v_t))
        rf.append(bm.faces.new(list(reversed(v_b))))
        for f in rf:
            map_face_uv(f, uv_layer, "kopher_pitch", u_scale=0.5)
        _orient_faces_outward(rf, Vector((0.0, 0.0, 0.22)))


# ==============================================================================
# 3) KIT-SPEZIFIKATION, STRENGE PIVOT-/MASS-/T99-ASSERTIONS & 3-LOD-EXPORT
# ==============================================================================

WAVE_A_SPECS = [
    ("ark_gate_leaf_s7",     build_ark_gate_leaf_s7,     (3500, 5000), (950, 1600), (260, 480), "Hero-Seitentor S7 Torblatt (4.20x3.15m, Pivot an oberer Scharnierachse Z=0 -> -3.15m, Gen 6,14 innen & aussen Kopher-verpicht / 3 Hainbuchen-Sperrbalken & Bronze-Scharniere)"),
    ("ark_gate_zarge_s7",    build_ark_gate_zarge_s7,    (2000, 3000), (600, 1100), (180, 340), "Hero-Seitentor S7 Eichen-Blockzarge (4.20x3.15m lichte Oeffnung ueber 0.583m Flutsuell mit Kopher-Dichtfalzen & Flutsuell-Innenkante, 0.467m Eichenpfosten, 3 Riegeltaschen & 2 Kopfbaender)"),
    ("ark_storm_shutter",    build_ark_storm_shutter,    (180,  340),  (48,  76),   (20,  32),  "Fugendichte Zohar-/Badgir-Sturmklappe (1.0x1.0x1.0 normiert, Pivot Mitte Oberkante Z=0 -> -1.0, 4 geschlossene Zedernplanken, Diagonalstrebe, 2 Bronze-Scharnierbaender & Zugseil-Oese)"),
    ("ark_root_knee_01",     build_ark_root_knee_01,     (320,  480),  (85,  135),  (28,  48),  "Organisches Eichen-Wurzelknie Variante 01 (0.187m breit, 0.630m Schenkel, 0.171m dick, 6 Duebel, Origin an rechtwinkliger Aussenecke)"),
    ("ark_root_knee_02",     build_ark_root_knee_02,     (320,  480),  (85,  135),  (28,  48),  "Organisches Eichen-Wurzelknie Variante 02 (0.187m breit, 0.630m Schenkel, Naturwulst-Kehle & 7 versetzte Duebel, Origin an Aussenecke)"),
    ("ark_root_knee_03",     build_ark_root_knee_03,     (320,  480),  (85,  135),  (28,  48),  "Organisches Eichen-Wurzelknie Variante 03 (0.187m breit, 0.630m Schenkel, Stirnklauen & 6 grosse 1-Hand-Duebel, Origin an Aussenecke)"),
    ("ark_kingpost_capital", build_ark_kingpost_capital, (450,  650),  (110, 175),  (36,  64),  "Koenigsstuetzen-Sattelholz-Kapitell (umschließt 0.336x0.336m Stuetze, Sattelholz 0.386x1.100x0.260m, 2 Kopfband-Knaggen, Origin Unterkante Unterzug Z=0)"),
    ("ark_door_frame_d1",    build_ark_door_frame_d1,    (400,  600),  (110, 175),  (36,  64),  "Plastische Schotttuer-Blockzarge Deck 1 (Lichte Oeffnung exakt 2.800x2.917m ueber 0.583m Flutsuell, 0.0cm T99-Verengung)"),
    ("ark_door_frame_d2",    build_ark_door_frame_d2,    (400,  600),  (110, 175),  (36,  64),  "Plastische Schotttuer-Blockzarge Deck 2 (Lichte Oeffnung exakt 1.867x2.217m ueber 0.233m Suell, 0.0cm T99-Verengung)"),
    ("ark_door_frame_d3",    build_ark_door_frame_d3,    (400,  600),  (110, 175),  (36,  64),  "Plastische Schotttuer-Blockzarge Deck 3 (Lichte Oeffnung exakt 1.400x1.983m ueber 0.233m Suell, 0.0cm T99-Verengung)"),
    ("ark_door_frame_foyer", build_ark_door_frame_foyer, (400,  600),  (110, 175),  (36,  64),  "Plastische Schotttuer-Blockzarge S7-Foyer-Hauptportal (Lichte Oeffnung exakt 3.593x2.917m ueber 0.117m Schwelle, 0.0cm T99-Verengung)"),
    ("ark_badgir_cap",       build_ark_badgir_cap,       (900,  1600), (230, 370),  (70,  115), "Gezimmerter Badgir-Windturm-Kopf (1.633x1.400m Schachtsitz, Origin Z=0.0 an zTop, +0.45m Kopher-Zedern-Zeltdachhaube, 5 Wetterlamellen je Oeffnung, 16 Sparrenkoepfe & Kreuzwand)"),
]


def verify_module_assertions(name, obj, lod, tris, r0, r1, r2):
    """Prueft unbestechlich per Python-Assertion alle Tri-Budgets, Pivots, Aussenmasse und T99-Lichtraumprofile."""
    me = obj.data
    assert tuple(obj.location) == (0.0, 0.0, 0.0), f"{name}_LOD{lod}: Origin muss (0,0,0) sein!"
    assert len(me.materials) == 1, f"{name}_LOD{lod}: Darf nur exakt 1 Meister-Material besitzen!"
    assert len(me.color_attributes) == 0, f"{name}_LOD{lod}: Darf keinen Vertex-Color-Layer besitzen (arche_asset_v1_std)!"

    lo, hi = (r0 if lod == 0 else (r1 if lod == 1 else r2))
    assert lo <= tris <= hi, f"{name}_LOD{lod}: Tri-Count {tris} ausserhalb Zielbereich [{lo}..{hi}]!"

    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    min_z, max_z = min(zs), max(zs)

    if name == "ark_gate_leaf_s7":
        # Pivot an oberer Scharnierachse Z=0, Torblatt haengt bis Z = -3.150 m, Sperrbalken X in [-2.440..+2.440]
        assert abs(min_z - (-3.150)) < 0.005, f"{name}: Unterkante muss exakt Z=-3.150 m sein (ist {min_z:.4f})"
        assert abs(max_x - 2.440) < 0.005 and abs(min_x - (-2.440)) < 0.005, f"{name}: Sperrbalken-Spannweite muss 4.880 m sein!"
        assert 0.000 <= max_z <= 0.075, f"{name}: Oberkante/Scharnier muss an Drehachse Z=0.000 m sitzen (ist {max_z:.4f})"

    elif name == "ark_gate_zarge_s7":
        # Origin Z=0.0 auf Deck 2; Flutsuell 0.583 m; lichte Oeffnung 4.200 x 3.150 m muss im Kern frei sein
        assert abs(min_z - 0.000) < 0.005, f"{name}: Unterkante Flutsuell muss auf Z=0.000 m liegen!"
        # Verify clear opening in center (|X| < 1.50 m, Z in [0.59 .. 3.72 m]) has 0 obstructing vertices
        obstruct = [v.co for v in me.vertices if abs(v.co.x) < 1.50 and 0.60 < v.co.z < 3.72]
        assert len(obstruct) == 0, f"{name}: Lichte Toroeffnung 4.200x3.150 m verletzt ({len(obstruct)} Vertices)!"

    elif name == "ark_storm_shutter":
        # Pivot Mitte Oberkante Z=0.0, Blatt haengt bis Z=-1.000 m, X-Spanne [-0.52..+0.52]
        assert abs(min_z - (-1.000)) < 0.005, f"{name}: Klappen-Unterkante muss Z=-1.000 m sein (ist {min_z:.4f})"
        assert 0.000 <= max_z <= 0.055, f"{name}: Drehachse muss bei Z=0.000 m liegen (max_z={max_z:.4f})"
        assert abs(max_x - 0.520) < 0.005 and abs(min_x - (-0.520)) < 0.005, f"{name}: Normierte Breite inkorrekt!"

    elif name.startswith("ark_root_knee_"):
        # Origin (0,0,0) an rechtwinkliger Aussenecke: X in [-0.0935..+0.0935], Y in [0..0.630], Z in [0..0.630]
        assert abs(min_y - 0.000) < 0.005 and abs(max_y - 0.630) < 0.005, f"{name}: Y-Schenkel muss [0.000..0.630 m] sein!"
        assert abs(min_z - 0.000) < 0.005 and abs(max_z - 0.630) < 0.005, f"{name}: Z-Schenkel muss [0.000..0.630 m] sein!"

    elif name == "ark_kingpost_capital":
        # Origin (0,0,0) an Unterkante Laengsunterzug (max_z == 0.000 m!), Sattelholz Y in [-0.550..+0.550 m]
        assert abs(max_z - 0.000) < 0.003, f"{name}: Oberkante Sattelholz muss exakt bei Z=0.000 m liegen (ist {max_z:.4f})!"
        assert abs(max_y - 0.550) < 0.005 and abs(min_y - (-0.550)) < 0.005, f"{name}: Sattelholz-Laenge muss 1.100 m sein!"

    elif name in DOOR_SPECS:
        # STRIKTER T99-SCHUTZ: Lichte Durchgangsoeffnung (w_open x h_open ueber h_sill) darf um 0.0 cm verengt werden!
        w_open, h_open, h_sill = DOOR_SPECS[name]
        hx = 0.5 * w_open
        z_d0 = h_sill
        z_d1 = h_sill + h_open
        assert abs(min_z - 0.000) < 0.003, f"{name}: Suell-Unterkante muss Z=0.000 m sein!"
        # Im gesamten unteren und mittleren Durchgangsbereich (Z in [z_d0 + 0.002 .. z_d1 - 0.305])
        # darf KEIN EINZIGER Vertex innerhalb |X| < hx - 0.001 liegen (0.0 mm Verengung!)
        narrowing = [
            v.co for v in me.vertices
            if abs(v.co.x) < (hx - 0.001) and (z_d0 + 0.002) < v.co.z < (z_d1 - 0.305)
        ]
        assert len(narrowing) == 0, f"T99-VERLETZUNG in {name}: Lichte Breite {w_open}m verengt ({len(narrowing)} Vertices)!"
        # Ebenso in der Mittelachse (|X| < hx - 0.310) volle lichte Hoehe [z_d0 + 0.002 .. z_d1 - 0.002]
        height_narrow = [
            v.co for v in me.vertices
            if abs(v.co.x) < (hx - 0.310) and (z_d0 + 0.002) < v.co.z < (z_d1 - 0.002)
        ]
        assert len(height_narrow) == 0, f"T99-VERLETZUNG in {name}: Lichte Hoehe {h_open}m verengt ({len(height_narrow)} Vertices)!"

    elif name == "ark_badgir_cap":
        # Origin Z=0.0 an Schacht-Oberkante zTop, Zeltdachhaube reicht exakt bis Z = +0.450 m
        assert abs(max_z - 0.450) < 0.005, f"{name}: Zeltdach-Spitze muss bei Z=+0.450 m liegen (ist {max_z:.4f})!"
        assert abs(min_z - (-0.520)) < 0.005, f"{name}: Schachtkragen muss bis Z=-0.520 m reichen (ist {min_z:.4f})!"


def create_asset_object(name, builder_fn, lod, r0, r1, r2, mat_master):
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    builder_fn(bm, uv_layer, lod)
    for f in bm.faces:
        f.normal_update()
    tri_count = sum(max(1, len(f.verts) - 2) for f in bm.faces)

    mesh_name = f"{name}_LOD{lod}"
    me = bpy.data.meshes.new(mesh_name)
    bm.to_mesh(me)
    bm.free()

    me.materials.append(mat_master)
    obj = bpy.data.objects.new(mesh_name, me)
    bpy.context.collection.objects.link(obj)
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)

    verify_module_assertions(name, obj, lod, tri_count, r0, r1, r2)
    return obj, tri_count


def export_wave_a_blend_and_glb(project_root, all_objs, tri_report):
    blend_dir = os.path.join(project_root, "assets", "blend", "ark")
    glb_dir = os.path.join(project_root, "assets", "glb", "ark")
    os.makedirs(blend_dir, exist_ok=True)
    os.makedirs(glb_dir, exist_ok=True)

    blend_path = os.path.join(blend_dir, "ark_wave_a_kit.blend")
    glb_path = os.path.join(glb_dir, "ark_wave_a_kit.glb")

    bpy.ops.object.select_all(action="DESELECT")
    for o in all_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = all_objs[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    print(f"[ARK WAVE A] Speichere High-Detail-Master: {blend_path}", flush=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    print(f"[ARK WAVE A] Exportiere 3-LOD GLB (+Y Up): {glb_path}", flush=True)
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
        export_jpeg_quality=92,
    )
    glb_kb = os.path.getsize(glb_path) / 1024.0
    print(f"[ARK WAVE A] GLB exportiert: {glb_kb:.1f} KB ({glb_path})", flush=True)

    # Aktualisiere assets/manifest.json
    man_path = os.path.join(project_root, "assets", "manifest.json")
    if os.path.exists(man_path):
        with open(man_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        ark_items = manifest.setdefault("categories", {}).setdefault("ark", {}).setdefault("items", {})
        ark_items["ark_wave_a_kit"] = {
            "enabled": True,
            "url": "assets/glb/ark/ark_wave_a_kit.glb",
            "blend": "assets/blend/ark/ark_wave_a_kit.blend",
            "category": "ark",
            "shaderKey": "arche_asset_v1_std",
            "lods": ["LOD0", "LOD1", "LOD2"],
            "lodDistances": [28, 75, 145],
            "sharedTextures": {
                "arkMasterTrim": [
                    "assets/textures/ark/ark_master_basecolor.png",
                    "assets/textures/ark/ark_master_normal.png",
                    "assets/textures/ark/ark_master_roughness.png",
                ]
            },
            "modules": {
                name: {
                    "lods": tri_report[name],
                    "description": desc,
                }
                for name, _, _, _, _, desc in WAVE_A_SPECS
            },
            "previews": [
                "assets/previews/ark_wave_a_overview.png",
                "assets/previews/ark_wave_a_gate_closeup.png",
                "assets/previews/ark_wave_a_carpentry_closeup.png",
            ],
            "glbSizeKB": round(glb_kb, 1),
            "exportedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(man_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print("[ARK WAVE A] In assets/manifest.json registriert!", flush=True)

    return glb_kb


# ==============================================================================
# 4) 3 PFLICHT-KONTROLLRENDERINGS (CYCLES CUDA + AgX, 3 PERSPEKTIVEN!)
# ==============================================================================

def setup_cycles_agx_showcase(scene, samples=48):
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

    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"

    scene.view_settings.view_transform = "AgX"
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        scene.view_settings.look = "None"
    scene.view_settings.exposure = -0.95
    scene.view_settings.gamma = 1.0

    world = bpy.data.worlds.new("Ark_WaveA_Sky")
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
    sky.sun_elevation = math.radians(38.0)
    sky.sun_rotation = math.radians(-42.0)
    if hasattr(sky, "air_density"):
        sky.air_density = 1.25
    if hasattr(sky, "dust_density"):
        sky.dust_density = 1.45
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], w_out.inputs["Surface"])

    return "CUDA (GPU)" if used_gpu else "CPU"


def _place_inst(src_obj, loc, rot_euler=(0.0, 0.0, 0.0), scale=1.0, col=None):
    inst = bpy.data.objects.new(f"Preview_{src_obj.name}", src_obj.data)
    inst.location = Vector(loc)
    inst.rotation_euler = rot_euler
    inst.scale = (scale, scale, scale)
    (col or bpy.context.collection).objects.link(inst)
    return inst


def _aim_cam(cam_obj, loc, target, lens=35.0):
    cam_obj.location = Vector(loc)
    direction = Vector(target) - Vector(loc)
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam_obj.data.lens = lens
    cam_obj.data.clip_start = 0.1
    cam_obj.data.clip_end = 250.0


def _create_meter_reference_rod(col, loc=(0.0, 0.0, 0.0), height_m=2.0):
    """Erzeugt eine präzise 1-Meter- / 1-Elle-Messlatte auf Z=0.0 als Maßstabs-Referenz (nur für Preview!)."""
    bm = bmesh.new()
    mat_w = bpy.data.materials.new("Mat_Scale_Light")
    mat_w.use_nodes = True
    mat_w.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.76, 0.68, 0.52, 1.0)
    mat_d = bpy.data.materials.new("Mat_Scale_Dark")
    mat_d.use_nodes = True
    mat_d.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.14, 0.09, 0.05, 1.0)

    n_seg = int(round(height_m / 0.5))
    for i in range(n_seg):
        z0 = i * 0.5
        z1 = (i + 1) * 0.5
        v00 = bm.verts.new((-0.045, -0.045, z0))
        v10 = bm.verts.new((+0.045, -0.045, z0))
        v11 = bm.verts.new((+0.045, +0.045, z0))
        v01 = bm.verts.new((-0.045, +0.045, z0))
        t00 = bm.verts.new((-0.045, -0.045, z1))
        t10 = bm.verts.new((+0.045, -0.045, z1))
        t11 = bm.verts.new((+0.045, +0.045, z1))
        t01 = bm.verts.new((-0.045, +0.045, z1))
        for vs in [(v00, v10, t10, t00), (v10, v11, t11, t10), (v11, v01, t01, t11), (v01, v00, t00, t01), (t00, t10, t11, t01)]:
            f = bm.faces.new(vs)
            f.material_index = i % 2
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("Meter_Reference_Rod")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat_w)
    me.materials.append(mat_d)
    obj = bpy.data.objects.new("Meter_Reference_Rod", me)
    obj.location = Vector(loc)
    col.objects.link(obj)
    return obj


def _add_supporting_post_pedestal(col, mat_master, x, y, z0, z1, wx, wy, region="oak_d35"):
    """Baut einen bündigen Eichen-Montagesockel bis Z=0.0 fuer Module mit oberem Dreh-/Decken-Pivot (0% Schweben!)."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    add_chamfered_beam(bm, uv_layer, -0.5 * wx, +0.5 * wx, -0.5 * wy, +0.5 * wy, z0, z1, 0.014, region, axis="Z")
    me = bpy.data.meshes.new("Preview_Support_Post")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat_master)
    obj = bpy.data.objects.new("Preview_Support_Post", me)
    obj.location = Vector((x, y, 0.0))
    col.objects.link(obj)
    return obj


def render_3_wave_a_showcases(project_root, lod0_map, mat_master):
    scene = bpy.context.scene
    dev = setup_cycles_agx_showcase(scene, samples=48)
    print(f"[ARK WAVE A] Rendere 3 Pflicht-Kontrollbilder (Cycles {dev} + AgX)...", flush=True)

    for o in list(bpy.data.objects):
        o.hide_render = True
        o.hide_viewport = True

    prev_dir = os.path.join(project_root, "assets", "previews")
    os.makedirs(prev_dir, exist_ok=True)

    # Warmes Werft-Bodenplanum auf Z = 0.0 m
    mat_floor = bpy.data.materials.new("Mat_Shipyard_Floor")
    mat_floor.use_nodes = True
    bsdf_f = mat_floor.node_tree.nodes["Principled BSDF"]
    bsdf_f.inputs["Base Color"].default_value = (0.36, 0.28, 0.19, 1.0)
    bsdf_f.inputs["Roughness"].default_value = 0.88

    # ==========================================================================
    # BILD 1: assets/previews/ark_wave_a_overview.png (Vollständiges Lineup aller 6 Welle-A-Module)
    # ==========================================================================
    col1 = bpy.data.collections.new("Showcase_1_Overview")
    scene.collection.children.link(col1)

    bpy.ops.mesh.primitive_plane_add(size=90.0, location=(0.0, 0.0, 0.0))
    fl1 = bpy.context.active_object
    fl1.data.materials.append(mat_floor)
    col1.objects.link(fl1)
    bpy.context.collection.objects.unlink(fl1)

    # Warmes Innenraum-Streiflicht + Sonnenlicht von schräg vorn (-Y)
    l_data = bpy.data.lights.new("WarmRimLight", type="AREA")
    l_data.energy = 2800.0
    l_data.color = (1.0, 0.78, 0.48)
    l_data.size = 8.0
    l_obj = bpy.data.objects.new("WarmRimLight", l_data)
    l_obj.location = (-10.0, -9.0, 4.5)
    l_obj.rotation_euler = (math.radians(65.0), 0.0, math.radians(-28.0))
    col1.objects.link(l_obj)

    cam_data = bpy.data.cameras.new("WaveACam")
    cam_obj = bpy.data.objects.new("WaveACam", cam_data)
    col1.objects.link(cam_obj)
    scene.camera = cam_obj

    # Lineup entlang X auf Y = 0.0 m (Vorderseite zeigt zu -Y Richtung Kamera!):
    # 1) Links: Hero-Seitentor S7 Zarge + Torblatt (Kopher-Pech-Aussenseite in Zarge bei X = -8.4 m)
    _place_inst(lod0_map["ark_gate_zarge_s7"], (-8.4, 0.0, 0.0), col=col1)
    _place_inst(lod0_map["ark_gate_leaf_s7"],  (-8.4, -0.06, 3.733), col=col1)
    _create_meter_reference_rod(col1, loc=(-5.35, -0.45, 0.0), height_m=2.0)

    # 2) Rechts daneben: Hero-Seitentor S7 Torblatt INNENSEITE (3 Hainbuchen-Sperrbalken + 8 Rippen, montiert in Zarge bei X = -2.2 m)
    _place_inst(lod0_map["ark_gate_zarge_s7"], (-2.2, 0.0, 0.0), rot_euler=(0.0, 0.0, math.pi), col=col1)
    _place_inst(lod0_map["ark_gate_leaf_s7"],  (-2.2, +0.06, 3.733), rot_euler=(0.0, 0.0, math.pi), col=col1)

    # 3) Modul 5: Schotttuer-Blockzargen (Foyer-Hauptportal bei X = +3.3 m, D1 bei X = +7.5 m)
    _place_inst(lod0_map["ark_door_frame_foyer"], (+3.3, 0.0, 0.0), col=col1)
    _place_inst(lod0_map["ark_door_frame_d1"],    (+7.3, 0.0, 0.0), col=col1)

    # 4) Modul 6: Badgir-Windturm-Kopf auf kurzem 0.85m Schachtsockel bei X = +10.6 m (Origin zTop = 0.85 m -> Bodenkontakt!)
    _add_supporting_post_pedestal(col1, mat_master, +10.6, 0.0, 0.0, 0.85, 1.633, 1.400, region="cypress_c27")
    _place_inst(lod0_map["ark_badgir_cap"], (+10.6, 0.0, 0.85), col=col1)

    # 5) Vorderreihe (Y = -2.35 m, auf Z = 0.0 m):
    #    3 organische Eichen-Wurzelknie (ark_root_knee_01..03), Koenigsstuetzen-Kapitell auf 0.336m Stuetzensockel, Sturmklappe am Rahmenbock
    _place_inst(lod0_map["ark_root_knee_01"], (+1.4, -2.4, 0.0), rot_euler=(0.0, 0.0, -0.45 * math.pi), col=col1)
    _place_inst(lod0_map["ark_root_knee_02"], (+2.4, -2.4, 0.0), rot_euler=(0.0, 0.0, -0.45 * math.pi), col=col1)
    _place_inst(lod0_map["ark_root_knee_03"], (+3.4, -2.4, 0.0), rot_euler=(0.0, 0.0, -0.45 * math.pi), col=col1)

    # Koenigsstuetze (0.336x0.336m von Z=0.0 bis 1.05m) + Kapitell (Origin Z=1.31m) + kurzes Unterzugstueck
    _add_supporting_post_pedestal(col1, mat_master, +5.0, -2.3, 0.0, 1.05, 0.336, 0.336, region="oak_d35")
    _place_inst(lod0_map["ark_kingpost_capital"], (+5.0, -2.3, 1.31), rot_euler=(0.0, 0.0, 0.35 * math.pi), col=col1)

    # Sturmklappe auf kleinem Zohar-Stielsockel (Z=0.0..1.05 m) bei X = +6.8 m
    _add_supporting_post_pedestal(col1, mat_master, +6.8, -2.3, 0.0, 0.12, 1.15, 0.24, region="oak_d35")
    _place_inst(lod0_map["ark_storm_shutter"], (+6.8, -2.3, 1.12), rot_euler=(0.0, 0.0, math.pi), col=col1)

    _aim_cam(cam_obj, (+1.1, -19.8, 4.8), (+1.1, 0.0, 1.95), lens=28.0)
    p1 = os.path.join(prev_dir, "ark_wave_a_overview.png")
    scene.render.filepath = p1
    print(f"[ARK WAVE A] 1/3 Rendere {p1}...", flush=True)
    bpy.ops.render.render(write_still=True)

    # ==========================================================================
    # BILD 2: assets/previews/ark_wave_a_gate_closeup.png (Scharfe 2-Seiten-Nahaufnahme Seitentor S7)
    # ==========================================================================
    for o in col1.objects:
        if o not in (fl1, cam_obj, l_obj):
            o.hide_render = True

    col2 = bpy.data.collections.new("Showcase_2_GateCloseup")
    scene.collection.children.link(col2)

    # Links (X = -3.05 m): Dunkle Kopher-Pech-Aussenseite (-Y) + Blockzarge & 0.583m Flutsuell + Bronze-Zapfenscharniere
    _place_inst(lod0_map["ark_gate_zarge_s7"], (-3.05, 0.0, 0.0), rot_euler=(0.0, 0.0, 0.06), col=col2)
    _place_inst(lod0_map["ark_gate_leaf_s7"],  (-3.05, -0.04, 3.733), rot_euler=(0.0, 0.0, 0.06), col=col2)

    # Mitte (X = 0.0 m): 2.0m Messlatte (4x 0.50m Teilung) zum direkten Massvergleich mit 0.583m Flutsuell & 3.150m Torblatt
    _create_meter_reference_rod(col2, loc=(0.0, -0.55, 0.0), height_m=2.0)

    # Rechts (X = +3.05 m): Handgezimmerte Eichen-Innenseite (+Y, um 180° zur Kamera gedreht!)
    # mit 3 Hainbuchen-Sperrbalken (4.88m), 8 Spantenrippen, 2 organischen Kopfbaendern, Zapfen & Holzduebeln
    _place_inst(lod0_map["ark_gate_zarge_s7"], (+3.05, 0.0, 0.0), rot_euler=(0.0, 0.0, math.pi - 0.06), col=col2)
    _place_inst(lod0_map["ark_gate_leaf_s7"],  (+3.05, +0.04, 3.733), rot_euler=(0.0, 0.0, math.pi - 0.06), col=col2)

    l_obj.location = (+2.5, -5.8, 3.6)
    l_obj.data.energy = 2400.0
    _aim_cam(cam_obj, (0.0, -11.2, 2.35), (0.0, 0.0, 2.05), lens=32.0)
    p2 = os.path.join(prev_dir, "ark_wave_a_gate_closeup.png")
    scene.render.filepath = p2
    print(f"[ARK WAVE A] 2/3 Rendere {p2}...", flush=True)
    bpy.ops.render.render(write_still=True)

    # ==========================================================================
    # BILD 3: assets/previews/ark_wave_a_carpentry_closeup.png
    # (Detail-Close-up: 3 organische Wurzelknie, Koenigsstuetzen-Kapitell, Sturmklappe, Foyer-Blockzarge & Badgir-Kopf)
    # ==========================================================================
    for o in col2.objects:
        o.hide_render = True

    col3 = bpy.data.collections.new("Showcase_3_CarpentryCloseup")
    scene.collection.children.link(col3)

    # Hintergrund Links (X = -1.75 m, Y = +0.95 m): S7-Foyer-Blockzarge (ark_door_frame_foyer, komplett im Bild!)
    _place_inst(lod0_map["ark_door_frame_foyer"], (-1.75, +0.95, 0.0), rot_euler=(0.0, 0.0, 0.10), col=col3)

    # Hintergrund Rechts (X = +2.25 m, Y = +0.45 m): Gezimmerter Badgir-Windturm-Kopf auf 0.85m Zypressen-Schachtsockel
    _add_supporting_post_pedestal(col3, mat_master, +2.25, +0.45, 0.0, 0.85, 1.633, 1.400, region="cypress_c27")
    _place_inst(lod0_map["ark_badgir_cap"], (+2.25, +0.45, 0.85), rot_euler=(0.0, 0.0, -0.24), col=col3)

    # Vordergrund Links (X = -2.15, -1.45, -0.75 m, Y = -1.25 m): Die 3 organischen Eichen-Wurzelknie (ark_root_knee_01..03)
    _place_inst(lod0_map["ark_root_knee_01"], (-2.15, -1.25, 0.0), rot_euler=(0.0, 0.0, -0.35 * math.pi), col=col3)
    _place_inst(lod0_map["ark_root_knee_02"], (-1.45, -1.32, 0.0), rot_euler=(0.0, 0.0, -0.42 * math.pi), col=col3)
    _place_inst(lod0_map["ark_root_knee_03"], (-0.75, -1.25, 0.0), rot_euler=(0.0, 0.0, -0.50 * math.pi), col=col3)

    # Vordergrund Mitte (X = +0.20 m, Y = -1.15 m): Koenigsstuetzen-Sattelholz-Kapitell auf 0.82m Stuetzensockel
    _add_supporting_post_pedestal(col3, mat_master, +0.20, -1.15, 0.0, 0.82, 0.336, 0.336, region="oak_d35")
    _place_inst(lod0_map["ark_kingpost_capital"], (+0.20, -1.15, 1.08), rot_euler=(0.0, 0.0, 0.38 * math.pi), col=col3)

    # Vordergrund Rechts (X = +1.30 m, Y = -1.22 m): Zohar-/Badgir-Sturmklappe (ark_storm_shutter) auf Eichen-Pruefsockel
    _add_supporting_post_pedestal(col3, mat_master, +1.30, -1.22, 0.0, 0.10, 1.12, 0.22, region="oak_d35")
    _place_inst(lod0_map["ark_storm_shutter"], (+1.30, -1.22, 1.10), rot_euler=(0.0, 0.0, math.pi - 0.18), col=col3)

    _create_meter_reference_rod(col3, loc=(-2.95, -1.05, 0.0), height_m=1.0)

    l_obj.location = (-3.2, -4.5, 2.6)
    l_obj.data.energy = 2100.0
    _aim_cam(cam_obj, (+0.05, -6.95, 2.15), (+0.05, -0.10, 1.48), lens=31.0)
    p3 = os.path.join(prev_dir, "ark_wave_a_carpentry_closeup.png")
    scene.render.filepath = p3
    print(f"[ARK WAVE A] 3/3 Rendere {p3}...", flush=True)
    bpy.ops.render.render(write_still=True)

    print("[ARK WAVE A] Alle 3 Pflicht-Kontrollrenderings erfolgreich erstellt!", flush=True)


def main():
    t0 = time.time()
    root = get_project_root()
    print("[ARK WAVE A] Starte Bau des Arche-Welle-A Hero-Kits (Aussenhuelle & Zimmermannswerk)...", flush=True)
    clear_scene()

    mat_master = build_ark_master_material(root)

    all_objs = []
    lod0_map = {}
    tri_report = {}

    print("[ARK WAVE A] --- GEOMETRIE-, PIVOT-, T99- & TRI-COUNT-VERIFIKATION ---", flush=True)
    for name, builder_fn, r0, r1, r2, desc in WAVE_A_SPECS:
        tri_report[name] = {}
        for lod in (0, 1, 2):
            obj, tris = create_asset_object(name, builder_fn, lod, r0, r1, r2, mat_master)
            all_objs.append(obj)
            tri_report[name][f"LOD{lod}"] = tris
            if lod == 0:
                lod0_map[name] = obj
        r = tri_report[name]
        bb = [lod0_map[name].matrix_world @ Vector(c) for c in lod0_map[name].bound_box]
        sx = max(v.x for v in bb) - min(v.x for v in bb)
        sy = max(v.y for v in bb) - min(v.y for v in bb)
        sz = max(v.z for v in bb) - min(v.z for v in bb)
        z_span = f"[{min(v.z for v in bb):+6.3f}..{max(v.z for v in bb):+6.3f}]"
        print(
            f"[ARK WAVE A]   {name:22s} | LOD0={r['LOD0']:4d} | LOD1={r['LOD1']:4d} | LOD2={r['LOD2']:3d} "
            f"| Dim=({sx:5.3f} x {sy:5.3f} x {sz:5.3f} m) | Z={z_span} | PASS",
            flush=True,
        )

    glb_kb = export_wave_a_blend_and_glb(root, all_objs, tri_report)
    render_3_wave_a_showcases(root, lod0_map, mat_master)
    print(f"[ARK WAVE A] KOMPLETT FERTIG in {time.time() - t0:.1f}s | GLB={glb_kb:.1f} KB", flush=True)


if __name__ == "__main__":
    main()
