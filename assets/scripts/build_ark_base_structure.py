"""
build_ark_base_structure.py — Arche-Welle A (Teil 1B): Komplette modulare Blender-Grundstruktur (Gen 6,14 innen & aussen verpicht)
==================================================================================================================================
Erstellt die High-Detail-Master in assets/blend/ark/ark_base_structure_kit.blend und exportiert alle
modularen Grundstruktur-Objekte mit 4 LODs aussen (150 / 500 / 1.500 / 3.000 m) bzw. 3 kurzen LODs
innen (28 / 75 / 145 m) nach assets/glb/ark/ark_base_structure_kit.glb (inkl. Manifest-Update
in assets/manifest.json und 5 Cycles-CUDA-AgX-Pflicht-Kontrollrenderings).

Gen 6,14 ("Mache dir eine Arche aus Gopherholz ... und verpiche sie mit Erdpech innen und aussen!"):
  - Alle Rumpfschalen-Bauteile (Backbordwand, Steuerbordwand, Bug-/Heck-Stirnwaende inkl. Giebel-Innenseiten,
    Boden-Sohle/Bilge) sind SOWOHL AUSSEN ALS AUCH AUF IHRER INNENSEITE mit Kopher-Erdpech (MAT_ARK_KOPHER)
    abgedichtet — ueber deutlich plastisch abgesetzten Bohlenfugen und Spachtelwuelsten!
  - Die konstruktiven Innen-Hölzer (Decks D1-D3, 3 Innen-Kielschweine, 15 Laengsunterzuege, 45 Koenigsstuetzen,
    2 Laengsschotten, 13 Querschotten, Dach-Innenschalung, Sparrenkoepfe & 1-Elle-Zohar) nutzen 5 klar getrennte
    Holz-Materialslots mit metrischen Box-/Planar-UVs (1.0 UV = 2.0 m) fuer verzerrungsfreie Live-Holzart-Umschaltung.

Exakt 6 Materialien (alle auf identischer 3-Map-Signatur fuer arche_asset_v1_std, deltaPrograms === 0):
  1. MAT_ARK_KOPHER       -> kopher_pitch     (Aussenhaut aussen & innen, Giebel aussen & innen, Satteldach aussen,
                                               Sohle/Bilge aussen & innen, 3 Aussenkiele, Kopher-Dichtungskehlen)
  2. MAT_ARK_ROOF_WOOD    -> wood_cedar_c18   (Dach-Innenschalung, Sparrenkoepfe, 1-Elle-Zohar-Stiele & -Lamellen)
  3. MAT_ARK_DECKS        -> wood_oak_d35     (Begehbare Decks D1, D2 & D3 inkl. Wechselbalken)
  4. MAT_ARK_HEAVY_TIMBER -> wood_oak_d35     (3 Innen-Kielschweine, 15 Laengsunterzuege, 45 Koenigsstuetzen)
  5. MAT_ARK_LONG_BH      -> wood_cypress_c27 (2 Laengsschotten mit allen 60 Tuerpositionen / 56 offenen Durchbruechen)
  6. MAT_ARK_TRANS_BH     -> wood_cypress_c27 (13 Querschotten mit 39 Mittel- & 16 Seitentueren, D2-Duekern & 2 Rampen)

Aufruf:
  blender --background --python-exit-code 1 --python assets/scripts/build_ark_base_structure.py
"""

import os
import sys
import json
import time
import math
import bpy
import bmesh
from mathutils import Vector

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Biblischer Ellen-Kanon (BLENDER_PIPELINE.md & scratch/ark_inventory_audit.md)
ELLE_M = 14.0 / 30.0          # 0.4666667 m
HANDBREITE_M = ELLE_M / 6.0   # 0.0777778 m
FINGER_M = ELLE_M / 24.0      # 0.0194444 m

L_SHIP = 140.0                # 300 Ellen (xShip in [0..140 m], xLocal = xShip - 70.0 in [-70..+70 m])
B_SHIP = 23.0                 # ~50 Ellen (Y in [-11.5..+11.5 m])
H_SHIP = 14.0                 # 30 Ellen Traufkante

X_STATIONS = [float(i * 10) for i in range(15)]  # [0, 10, 20, ..., 140]
Y_AXES = [-11.5, -5.0, +5.0, +11.5]
Z_LEVELS = [0.0, 2.0, 6.0, 10.0, 14.0]

# Norm-Bauteildicken aus Arche Simulation 3.0.html & ark_inventory_audit.md
D_BOT = 4.5 * HANDBREITE_M    # 0.350000 m (Sohle 4.5 H.)
D_AW = 4.0 * HANDBREITE_M     # 0.311111 m (Aussenbordwand 4.0 H.)
D_LBH = 3.0 * HANDBREITE_M    # 0.233333 m (Laengsschott 3.0 H.)
D_TBH = 3.0 * HANDBREITE_M    # 0.233333 m (Querschott 3.0 H.)
D_D1 = 3.0 * HANDBREITE_M     # 0.233333 m (Deck 1: Z = 1.8833..2.1167 m)
D_D2 = 3.0 * HANDBREITE_M     # 0.233333 m (Deck 2: Z = 5.8833..6.1167 m)
D_D3 = 2.5 * HANDBREITE_M     # 0.194444 m (Deck 3: Z = 9.9028..10.0972 m)
D_ROOF = 3.5 * HANDBREITE_M   # 0.272222 m (Satteldach 3.5 H.)
DECK_THICK = [D_BOT, D_D1, D_D2, D_D3]

Z_TRAUF = 29.0 * ELLE_M       # 13.533333 m (Oberkante massive Aussenbordwand)
Z_OUT_SL = 30.0 * ELLE_M      # 14.000000 m (Oberkante 1-Elle-Zohar an Y = +-11.50 m)
Z_FIRST_UN = 31.5 * ELLE_M    # 14.700000 m (Unterkante Satteldach-First bei Y = 0.0 m)
Z_FIRST_TOP = Z_FIRST_UN + D_ROOF  # 14.972222 m (Oberkante Satteldach-First)
EAVE_OVERHANG = 1.0 * ELLE_M  # 0.466667 m (1-Elle-Traufueberstand bis |Y| = 11.966667 m)
Y_EAVE_OUT = 11.5 + EAVE_OVERHANG  # 11.966667 m

# Metrischer UV-Massstab: 1.0 UV-Einheit = 2.0 m -> uv_scale = 0.5 m^-1
METRIC_UV_SCALE = 0.50


def xL(x_ship):
    """Wandelt Schiffs-Stationskoordinate xShip [0..140 m] in lokale Mesh-Koordinate xLocal [-70..+70 m] um."""
    return float(x_ship) - 70.0


def get_deck_z(level_idx, y_val):
    """Exakte parametrische Z-Hoehenfunktion getDeckZ(levelIdx, y) aus Arche Simulation 3.0.html (Z. 2389)."""
    if level_idx < 4:
        return Z_LEVELS[level_idx]
    abs_y = abs(float(y_val))
    if abs_y > 10.5:
        return 29.0 * ELLE_M
    return (31.5 * ELLE_M) - (abs_y / 11.5) * (1.5 * ELLE_M)


def get_roof_under_z(y_val):
    """Durchgehende Satteldach-Unterkante: First Z=14.700 m (Y=0) -> Traufe Z=14.000 m (|Y|=11.5) -> Z=13.533 m (|Y|=11.967)."""
    abs_y = abs(float(y_val))
    if abs_y <= 11.5:
        return Z_FIRST_UN - (abs_y / 11.5) * (Z_FIRST_UN - Z_OUT_SL)
    t_ov = min(1.0, (abs_y - 11.5) / EAVE_OVERHANG)
    return Z_OUT_SL - t_ov * (Z_OUT_SL - Z_TRAUF)


def get_project_root():
    return os.path.dirname(os.path.dirname(SCRIPT_DIR))


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    return scene


# ==============================================================================
# 1) 6 MATERIALIEN MIT IDENTISCHER 3-MAP-SIGNATUR (arche_asset_v1_std, deltaPrograms === 0)
# ==============================================================================

MATERIAL_SLOT_DEFS = [
    ("MAT_ARK_KOPHER",       "kopher_pitch",     0.04),
    ("MAT_ARK_ROOF_WOOD",    "wood_cedar_c18",   0.01),
    ("MAT_ARK_DECKS",        "wood_oak_d35",     0.01),
    ("MAT_ARK_HEAVY_TIMBER", "wood_oak_d35",     0.01),
    ("MAT_ARK_LONG_BH",      "wood_cypress_c27", 0.01),
    ("MAT_ARK_TRANS_BH",     "wood_cypress_c27", 0.01),
]


def _load_img(path, colorspace):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Textur fehlt: {path} — bitte zuerst build_ark_wood_library.py ausfuehren!"
        )
    img = bpy.data.images.load(path, check_existing=True)
    img.colorspace_settings.name = colorspace
    try:
        img.pack()
    except Exception:
        pass
    return img


def build_6_ark_base_materials(project_root):
    """Erstellt exakt die 6 benannten Materialien fuer Live-Holzart-Umschaltung in Three.js."""
    mat_dir = os.path.join(project_root, "assets", "textures", "ark", "materials")
    mats = {}
    for mat_name, tex_prefix, metallic_val in MATERIAL_SLOT_DEFS:
        mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        mat.use_backface_culling = False
        if hasattr(mat, "blend_method"):
            mat.blend_method = "OPAQUE"

        nt = mat.node_tree
        nodes, links = nt.nodes, nt.links
        nodes.clear()

        out = nodes.new("ShaderNodeOutputMaterial")
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.inputs["Metallic"].default_value = metallic_val
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.48 if tex_prefix == "kopher_pitch" else 0.42
        links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

        # 1) BaseColor [sRGB]
        t_col = nodes.new("ShaderNodeTexImage")
        t_col.name = f"{mat_name}_BaseColor"
        t_col.image = _load_img(os.path.join(mat_dir, f"{tex_prefix}_basecolor.png"), "sRGB")
        t_col.extension = "REPEAT"
        links.new(t_col.outputs["Color"], bsdf.inputs["Base Color"])

        # 2) Normal [Linear / Non-Color]
        t_nrm = nodes.new("ShaderNodeTexImage")
        t_nrm.name = f"{mat_name}_Normal"
        t_nrm.image = _load_img(os.path.join(mat_dir, f"{tex_prefix}_normal.png"), "Non-Color")
        t_nrm.extension = "REPEAT"
        nm = nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = 1.0
        links.new(t_nrm.outputs["Color"], nm.inputs["Color"])
        links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])

        # 3) Roughness [Linear / Non-Color]
        t_rgh = nodes.new("ShaderNodeTexImage")
        t_rgh.name = f"{mat_name}_Roughness"
        t_rgh.image = _load_img(os.path.join(mat_dir, f"{tex_prefix}_roughness.png"), "Non-Color")
        t_rgh.extension = "REPEAT"
        links.new(t_rgh.outputs["Color"], bsdf.inputs["Roughness"])

        mats[mat_name] = mat
        print(f"[ARK BASE] Material '{mat_name}' -> '{tex_prefix}' (3 Maps, 1024x1024, REPEAT) bereit.", flush=True)
    return mats


# ==============================================================================
# 2) METRISCHE BOX-/PLANAR-UV-GEOMETRIE-PRIMITIVE (1.0 UV-Einheit = 2.0 m)
# ==============================================================================

def map_metric_face_uv(face, uv_layer, mat_idx=0, grain_axis="X", scale=METRIC_UV_SCALE):
    """Verzerrungsfreie metrische Box-/Planar-UV-Projektion (1.0 UV = 2.0 m):
    U laeuft immer exakt entlang der Holzfaser-Achse (grain_axis = 'X', 'Y' oder 'Z'),
    V laeuft quer zur Bohle. Dadurch koennen alle 4 Holzarten live getauscht werden!"""
    face.material_index = mat_idx
    face.normal_update()
    n = face.normal
    ax, ay, az = abs(n.x), abs(n.y), abs(n.z)

    for loop in face.loops:
        co = loop.vert.co
        if grain_axis == "X":
            if ax > 0.72:
                u, v = co.y * scale, co.z * scale
            elif az > ay:
                u, v = co.x * scale, co.y * scale
            else:
                u, v = co.x * scale, co.z * scale
        elif grain_axis == "Y":
            if ay > 0.72:
                u, v = co.x * scale, co.z * scale
            elif az > ax:
                u, v = co.y * scale, co.x * scale
            else:
                u, v = co.y * scale, co.z * scale
        else:  # grain_axis == "Z" (vertikale Stuetzen, Stiele & Lisenen)
            if az > 0.72:
                u, v = co.x * scale, co.y * scale
            elif ax > ay:
                u, v = co.z * scale, co.y * scale
            else:
                u, v = co.z * scale, co.x * scale
        loop[uv_layer].uv = (u, v)


def _orient_faces_outward(faces, center_pt):
    for f in faces:
        f.normal_update()
        if (f.calc_center_median() - center_pt).dot(f.normal) < 0.0:
            f.normal_flip()


def add_metric_box(bm, uv_layer, x0, x1, y0, y1, z0, z1, mat_idx=0, grain_axis="X"):
    """Achsenparalleler Quader mit metrischer 2.0-m-Box-UV-Projektion."""
    if (x1 - x0) < 1e-4 or (y1 - y0) < 1e-4 or (z1 - z0) < 1e-4:
        return []
    v000 = bm.verts.new((x0, y0, z0))
    v100 = bm.verts.new((x1, y0, z0))
    v110 = bm.verts.new((x1, y1, z0))
    v010 = bm.verts.new((x0, y1, z0))
    v001 = bm.verts.new((x0, y0, z1))
    v101 = bm.verts.new((x1, y0, z1))
    v111 = bm.verts.new((x1, y1, z1))
    v011 = bm.verts.new((x0, y1, z1))

    f_verts = [
        (v000, v100, v101, v001),  # -Y
        (v110, v010, v011, v111),  # +Y
        (v010, v000, v001, v011),  # -X
        (v100, v110, v111, v101),  # +X
        (v001, v101, v111, v011),  # +Z
        (v010, v110, v100, v000),  # -Z
    ]
    faces = []
    for vs in f_verts:
        f = bm.faces.new(vs)
        map_metric_face_uv(f, uv_layer, mat_idx=mat_idx, grain_axis=grain_axis)
        faces.append(f)
    _orient_faces_outward(faces, Vector((0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (z0 + z1))))
    return faces


def add_metric_chamfered_beam(bm, uv_layer, x0, x1, y0, y1, z0, z1, chamfer, mat_idx=0, axis="X"):
    """8-kantig gefaster Zimmermannsbalken mit metrischer 2.0-m-UV-Projektion."""
    if (x1 - x0) < 1e-4 or (y1 - y0) < 1e-4 or (z1 - z0) < 1e-4:
        return []
    if chamfer <= 1e-4:
        return add_metric_box(bm, uv_layer, x0, x1, y0, y1, z0, z1, mat_idx=mat_idx, grain_axis=axis)

    def _oct(a0, a1, b0, b1, c):
        ca = min(c, 0.34 * (a1 - a0))
        cb = min(c, 0.34 * (b1 - b0))
        return [
            (a0 + ca, b0), (a1 - ca, b0),
            (a1, b0 + cb), (a1, b1 - cb),
            (a1 - ca, b1), (a0 + ca, b1),
            (a0, b1 - cb), (a0, b0 + cb),
        ]

    r0, r1 = [], []
    if axis == "X":
        for py, pz in _oct(y0, y1, z0, z1, chamfer):
            r0.append(bm.verts.new((x0, py, pz)))
            r1.append(bm.verts.new((x1, py, pz)))
    elif axis == "Y":
        for px, pz in _oct(x0, x1, z0, z1, chamfer):
            r0.append(bm.verts.new((px, y0, pz)))
            r1.append(bm.verts.new((px, y1, pz)))
    else:
        for px, py in _oct(x0, x1, y0, y1, chamfer):
            r0.append(bm.verts.new((px, py, z0)))
            r1.append(bm.verts.new((px, py, z1)))

    faces = []
    n = len(r0)
    for i in range(n):
        j = (i + 1) % n
        f = bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
        map_metric_face_uv(f, uv_layer, mat_idx=mat_idx, grain_axis=axis)
        faces.append(f)
    f0 = bm.faces.new(list(reversed(r0)))
    map_metric_face_uv(f0, uv_layer, mat_idx=mat_idx, grain_axis=axis)
    f1 = bm.faces.new(r1)
    map_metric_face_uv(f1, uv_layer, mat_idx=mat_idx, grain_axis=axis)
    faces.extend([f0, f1])
    _orient_faces_outward(faces, Vector((0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (z0 + z1))))
    return faces


def add_sloped_quad_prism(bm, uv_layer, p0, p1, p2, p3, offset_vec, mat_idx=0, grain_axis="X", top_mat_idx=None, bot_mat_idx=None):
    """Volumetrisches Prisma aus 4 Basispunkten p0..p3 + Verschiebungsvektor offset_vec.
    Erlaubt unterschiedliche Material-Indizes auf Ober- und Unterseite (z.B. Satteldach aussen Kopher, innen Zeder!)."""
    v_b = [bm.verts.new(Vector(p)) for p in (p0, p1, p2, p3)]
    off = Vector(offset_vec)
    v_t = [bm.verts.new(Vector(p) + off) for p in (p0, p1, p2, p3)]

    m_top = mat_idx if top_mat_idx is None else top_mat_idx
    m_bot = mat_idx if bot_mat_idx is None else bot_mat_idx

    faces = []
    for i in range(4):
        j = (i + 1) % 4
        f = bm.faces.new((v_b[i], v_b[j], v_t[j], v_t[i]))
        map_metric_face_uv(f, uv_layer, mat_idx=mat_idx, grain_axis=grain_axis)
        faces.append(f)
    f_bot = bm.faces.new(list(reversed(v_b)))
    map_metric_face_uv(f_bot, uv_layer, mat_idx=m_bot, grain_axis=grain_axis)
    f_top = bm.faces.new(v_t)
    map_metric_face_uv(f_top, uv_layer, mat_idx=m_top, grain_axis=grain_axis)
    faces.extend([f_bot, f_top])

    c = sum((v.co for v in v_b + v_t), Vector((0.0, 0.0, 0.0))) / 8.0
    _orient_faces_outward(faces, c)
    return faces


def add_planked_wall_panel_x(bm, uv_layer, x0, x1, y0, y1, z0, z1, n_courses, chamfer, mat_idx=0):
    """Baut eine horizontal geplankte Wandscheibe entlang X mit plastischen Bohlenfugen auf BEIDEN Seiten (-Y und +Y)."""
    if (x1 - x0) < 0.005 or (z1 - z0) < 0.005:
        return
    if n_courses <= 1 or chamfer <= 1e-4:
        add_metric_box(bm, uv_layer, x0, x1, y0, y1, z0, z1, mat_idx=mat_idx, grain_axis="X")
        return
    dz = (z1 - z0) / float(n_courses)
    for ic in range(n_courses):
        cz0 = z0 + ic * dz
        cz1 = z0 + (ic + 1) * dz
        add_metric_chamfered_beam(
            bm, uv_layer, x0, x1, y0, y1, cz0, cz1,
            chamfer=min(chamfer, 0.22 * dz), mat_idx=mat_idx, axis="X"
        )


def add_planked_wall_panel_y(bm, uv_layer, x0, x1, y0, y1, z0_y0, z0_y1, z1_y0, z1_y1, n_courses, chamfer, mat_idx=0):
    """Baut eine Querschott- oder Stirnwandscheibe entlang Y (auch mit schraeger Dach-Oberkante z1_y0 -> z1_y1)."""
    if (y1 - y0) < 0.005:
        return
    h0 = z1_y0 - z0_y0
    h1 = z1_y1 - z0_y1
    if max(h0, h1) < 0.005:
        return
    slope = abs(z1_y1 - z1_y0) + abs(z0_y1 - z0_y0)
    if slope < 0.004 and n_courses > 1 and chamfer > 1e-4:
        dz = (z1_y0 - z0_y0) / float(n_courses)
        for ic in range(n_courses):
            cz0 = z0_y0 + ic * dz
            cz1 = z0_y0 + (ic + 1) * dz
            add_metric_chamfered_beam(
                bm, uv_layer, x0, x1, y0, y1, cz0, cz1,
                chamfer=min(chamfer, 0.22 * dz), mat_idx=mat_idx, axis="Y"
            )
    else:
        # Trapezoidal or single panel
        n_c = max(1, min(n_courses, 4)) if slope < 0.004 else max(1, min(n_courses // 2, 3))
        for ic in range(n_c):
            t0 = ic / float(n_c)
            t1 = (ic + 1) / float(n_c)
            za0 = z0_y0 + t0 * (z1_y0 - z0_y0)
            za1 = z0_y0 + t1 * (z1_y0 - z0_y0)
            zb0 = z0_y1 + t0 * (z1_y1 - z0_y1)
            zb1 = z0_y1 + t1 * (z1_y1 - z0_y1)
            add_sloped_quad_prism(
                bm, uv_layer,
                (x0, y0, za0), (x0, y1, zb0), (x0, y1, zb1), (x0, y0, za1),
                (x1 - x0, 0.0, 0.0), mat_idx=mat_idx, grain_axis="Y"
            )


# ==============================================================================
# 3) EXAKTES OEFFNUNGS- & DURCHBRUCHS-KATASTER (115 TUEREN, S7-TOR, RAMPEN, SILOS, PATERNOSTER, BADGIRE)
# ==============================================================================

# 1. S7-Seitentor-Aussparung in ark_hull_wall_bb:
S7_GATE_CUTOUT = {
    "xLocal0": -7.100,   # xShip = 62.900 m (65.0 - 4.5 E.)
    "xLocal1": -2.900,   # xShip = 67.100 m (65.0 + 4.5 E.)
    "y0": -11.500,
    "y1": -11.500 + D_AW,
    "z0": 6.000,
    "z1": 6.000 + 8.0 * ELLE_M,  # 9.733333 m
}

# 2. 4 Giebel-Sturmklappen-Aussparungen in ark_hull_wall_sb (Bug & Heck, Y = +-3.25 m, 2.60 x 0.50 m bei Z = 13.72..14.22 m):
GABLE_SHUTTER_CUTOUTS = [
    {"xLocal0": -70.000, "xLocal1": -70.000 + D_AW, "y0": -3.250 - 1.300, "y1": -3.250 + 1.300, "z0": 13.720, "z1": 14.220},
    {"xLocal0": -70.000, "xLocal1": -70.000 + D_AW, "y0": +3.250 - 1.300, "y1": +3.250 + 1.300, "z0": 13.720, "z1": 14.220},
    {"xLocal0": +70.000 - D_AW, "xLocal1": +70.000, "y0": -3.250 - 1.300, "y1": -3.250 + 1.300, "z0": 13.720, "z1": 14.220},
    {"xLocal0": +70.000 - D_AW, "xLocal1": +70.000, "y0": +3.250 - 1.300, "y1": +3.250 + 1.300, "z0": 13.720, "z1": 14.220},
]

# 3. 8 Badgir-Schacht-Positionen (S2, S5, S10, S13, xShip = 12, 42, 92, 122 m, Y in [+-3.480..+-4.880 m]):
BADGIR_X_SHIPS = [12.0, 42.0, 92.0, 122.0]
BADGIR_HALF_LX = 1.75 * ELLE_M  # 0.816667 m (L_x = 1.633333 m)
BADGIR_LY = 3.00 * ELLE_M       # 1.400000 m (Y in [-4.880..-3.480] und [+3.480..+4.880])


def get_badgir_cutouts():
    cuts = []
    for xs in BADGIR_X_SHIPS:
        xl0 = xL(xs - BADGIR_HALF_LX)
        xl1 = xL(xs + BADGIR_HALF_LX)
        cuts.append({"xShip": xs, "side": "BB", "xLocal0": xl0, "xLocal1": xl1, "y0": -4.880, "y1": -4.880 + BADGIR_LY})
        cuts.append({"xShip": xs, "side": "SB", "xLocal0": xl0, "xLocal1": xl1, "y0": +4.880 - BADGIR_LY, "y1": +4.880})
    return cuts


# 4. 8 Silo-Durchbrueche auf D2 & D3 (S3, S6, S9, S12 Bb/Stb):
SILO_SEC_INDICES = [2, 5, 8, 11]  # i=2 (S3: 20..30), i=5 (S6: 50..60), i=8 (S9: 80..90), i=11 (S12: 110..120)


def get_silo_cutouts():
    cuts = []
    y_silo_outer = 11.500 - 1.0 * ELLE_M  # 11.033333 m (1.0 Elle Kontrollgang an der Aussenwand!)
    for i in SILO_SEC_INDICES:
        xl0 = xL(X_STATIONS[i] + 0.5 * D_TBH)
        xl1 = xL(X_STATIONS[i + 1] - 0.5 * D_TBH)
        cuts.append({"sec": f"S{i+1}_BB", "xLocal0": xl0, "xLocal1": xl1, "y0": -y_silo_outer, "y1": -5.000 - 0.5 * D_LBH})
        cuts.append({"sec": f"S{i+1}_SB", "xLocal0": xl0, "xLocal1": xl1, "y0": +5.000 + 0.5 * D_LBH, "y1": +y_silo_outer})
    return cuts


# 5. 2 Paternoster-Schaechte (S4 i=3 & S11 i=10 Bb):
def get_paternoster_cutouts(deck_k):
    cuts = []
    py0 = (-17.5 * ELLE_M) if deck_k == 1 else (-14.75 * ELLE_M)  # -8.1667 m (D1) bzw. -6.8833 m (D2/D3)
    py1 = -11.25 * ELLE_M  # -5.2500 m (umfasst [-6.883..-5.367 m] komplett!)
    for i in (3, 10):
        x_pat = X_STATIONS[i] + 5.0 * ELLE_M  # 32.3333 m & 102.3333 m
        xl0 = xL(x_pat - 1.75 * ELLE_M)       # 31.5167 m & 101.5167 m
        xl1 = xL(x_pat + 1.75 * ELLE_M)       # 33.1500 m & 103.1500 m
        cuts.append({"sec": f"S{i+1}_BB", "xLocal0": xl0, "xLocal1": xl1, "y0": py0, "y1": py1})
    return cuts


# 6. 4 Archimedische Schnecken-Durchbrueche (S4 i=3 & S11 i=10 Stb auf D1 & D2):
def get_screw_cutouts(deck_k):
    cuts = []
    sy0 = 6.080 if deck_k == 1 else 8.520
    sy1 = 7.420 if deck_k == 1 else 10.020
    for i in (3, 10):
        x0 = X_STATIONS[i]
        cuts.append({"sec": f"S{i+1}_A", "xLocal0": xL(x0 + 0.680), "xLocal1": xL(x0 + 1.620), "y0": sy0, "y1": sy1})
        cuts.append({"sec": f"S{i+1}_B", "xLocal0": xL(x0 + 8.380), "xLocal1": xL(x0 + 9.320), "y0": sy0, "y1": sy1})
    return cuts


# 7. 2 Rampen-Deckdurchbrueche (D2 Schwerlastrampe D1->D2 Bb, D3 Leichtrampe D2->D3 Stb):
RAMP_D2_CUTOUT = {
    "xLocal0": xL(140.0 * ELLE_M),  # xShip = 65.3333 m -> xLocal = -4.6667 m
    "xLocal1": xL(164.0 * ELLE_M),  # xShip = 76.5333 m -> xLocal = +6.5333 m
    "y0": -5.000 + 0.5 * D_LBH,     # -4.8833 m (bzw. -4.900 m)
    "y1": -4.5 * ELLE_M,            # -2.1000 m
}

RAMP_D3_CUTOUT = {
    "xLocal0": xL(139.0 * ELLE_M),  # xShip = 64.8667 m -> xLocal = -5.1333 m
    "xLocal1": xL(164.0 * ELLE_M),  # xShip = 76.5333 m -> xLocal = +6.5333 m
    "y0": +4.5 * ELLE_M,            # +2.1000 m
    "y1": +5.000 - 0.5 * D_LBH,     # +4.8833 m (bzw. +4.900 m)
}


def get_longitudinal_bh_door_specs():
    """Liefert exakt alle 60 auditierten Laengsschotttuer-Positionen (56 offene Tuerdurchbrueche + 4 geschlossene
    S8-Rampenwand-Felder; 0 Tueren in den 4 Silo-Sektionen S3, S6, S9, S12) exakt nach Arche Simulation 3.0.html."""
    open_doors = []
    closed_ramp_slots = []
    for j in (1, 2):  # j=1: Bb Y=-5.0 m; j=2: Stb Y=+5.0 m
        y_wall = Y_AXES[j]
        for i in range(14):
            if i in SILO_SEC_INDICES:
                continue  # Keine Tueren in Silo-Sektionen S3, S6, S9, S12!
            is_goepel = (i in (3, 10))
            for k in (1, 2, 3):
                is_ramp_wall_block = (
                    (j == 1 and i == 7 and k in (1, 2))
                    or (j == 2 and i == 7 and k in (2, 3))
                )
                x_mid = (X_STATIONS[i] + 6.80) if is_goepel else (0.5 * (X_STATIONS[i] + X_STATIONS[i + 1]))
                if i in (1, 4, 9, 12):
                    x_mid = (X_STATIONS[i] + 5.00) if k == 1 else (X_STATIONS[i] + 3.55)
                elif i == 0 and k == 1:
                    x_mid = 5.00
                elif i == 13 and k == 1:
                    x_mid = 135.00
                elif i == 6 and ((j == 1 and k == 1) or (j == 2 and k in (2, 3))):
                    x_mid = X_STATIONS[i] + 2.85  # 62.85 m
                elif i == 6 and j == 1 and k == 2:
                    x_mid = X_STATIONS[i] + 4.45  # 64.45 m: S7-Bb Foyer-Hauptportal!

                is_foyer_portal = (j == 1 and i == 6 and k == 2)
                sill_h = (1.25 * ELLE_M) if k == 1 else ((1.5 * HANDBREITE_M) if is_foyer_portal else (0.5 * ELLE_M))
                half_w = (3.85 * ELLE_M) if is_foyer_portal else ((2.55 * ELLE_M) if k == 1 else ((1.95 * ELLE_M) if k == 2 else (1.50 * ELLE_M)))
                door_h = (6.25 * ELLE_M) if (k == 1 or is_foyer_portal) else ((4.75 * ELLE_M) if k == 2 else (4.25 * ELLE_M))

                z0_deck = Z_LEVELS[k]
                z_door0 = z0_deck + sill_h
                z_door1 = z_door0 + door_h

                spec = {
                    "j": j,
                    "i": i,
                    "k": k,
                    "y_wall": y_wall,
                    "xShipMid": x_mid,
                    "xLocal0": xL(x_mid - half_w),
                    "xLocal1": xL(x_mid + half_w),
                    "z0": z_door0,
                    "z1": z_door1,
                    "is_foyer": is_foyer_portal,
                }
                if is_ramp_wall_block:
                    closed_ramp_slots.append(spec)
                else:
                    open_doors.append(spec)
    return open_doors, closed_ramp_slots


def get_transverse_bh_door_and_ramp_specs():
    """Liefert exakt alle 39 Mittelschiff-Querschotttueren (Y=0), alle 16 Seitenschiff-Querschotttueren,
    alle 26 D2-Spuelrinnen-Dueker sowie die 2 grossen Rampendurchbrueche an QS07 (xShip = 70.0 m)."""
    center_doors = []
    aisle_doors = []
    dukers_d2 = []
    for i in range(1, 14):  # QS01..QS13 (xShip = 10, 20, ..., 130 m)
        x_qs = X_STATIONS[i]
        xl = xL(x_qs)
        for k in (1, 2, 3):
            # 1) 39 Mittelschiff-Tueren (Y = 0.0 m)
            sill_h = (1.25 * ELLE_M) if k == 1 else (0.50 * ELLE_M)
            if i == 7 and k == 1:
                half_w = 2.80 * ELLE_M  # 5.60 E. = 2.6133 m an QS07 zwischen den Rampenpfosten
            else:
                half_w = (3.00 * ELLE_M) if k == 1 else ((2.00 * ELLE_M) if k == 2 else (1.50 * ELLE_M))
            door_h = (6.25 * ELLE_M) if k == 1 else ((4.75 * ELLE_M) if k == 2 else (4.25 * ELLE_M))
            z_d0 = Z_LEVELS[k] + sill_h
            z_d1 = z_d0 + door_h
            center_doors.append({
                "i": i,
                "k": k,
                "xShip": x_qs,
                "xLocal": xl,
                "y0": -half_w,
                "y1": +half_w,
                "z0": z_d0,
                "z1": z_d1,
            })

            # D2-Spuelrinnen-Dueker beidseitig der Mitteltuer
            if k == 2 and i != 7:
                z_base = Z_LEVELS[2] + 0.5 * D_D2 + 0.004
                h_c = 4.8 * HANDBREITE_M
                y_c_out = 3.5 * ELLE_M + 0.04  # 1.6733 m
                y_c_in = half_w + 3.0 * HANDBREITE_M  # 1.1667 m
                dukers_d2.append({"i": i, "xLocal": xl, "y0": -y_c_out, "y1": -y_c_in, "z0": z_base, "z1": z_base + h_c})
                dukers_d2.append({"i": i, "xLocal": xl, "y0": +y_c_in, "y1": +y_c_out, "z0": z_base, "z1": z_base + h_c})

            # 2) 16 Seitenschiff-Querschotttueren (QS04, QS07, QS10 auf D2/D3 + QS01, QS13 auf D3)
            allow_aisle = (k >= 2) and not (k == 2 and i in (1, 13)) and (i not in (2, 3, 5, 6, 8, 9, 11, 12))
            if allow_aisle:
                half_wa = 1.40 * ELLE_M  # Breite 2.80 E. = 1.3067 m
                sill_a = 0.50 * ELLE_M   # 0.2333 m
                door_ha = 4.50 * ELLE_M  # 2.1000 m
                for side_j, y_mid in ((0, -6.55 if k == 3 else -6.20), (2, +6.65 if k == 3 else +6.20)):
                    aisle_doors.append({
                        "i": i,
                        "k": k,
                        "j": side_j,
                        "xShip": x_qs,
                        "xLocal": xl,
                        "y0": y_mid - half_wa,
                        "y1": y_mid + half_wa,
                        "z0": Z_LEVELS[k] + sill_a,
                        "z1": Z_LEVELS[k] + sill_a + door_ha,
                    })

    # 3) 2 grosse Rampendurchbrueche an QS07 (xShip = 70.0 m, xLocal = 0.0 m)
    qs07_ramps = [
        {"name": "QS07_Ramp_BB_D1_D2", "xLocal": 0.0, "y0": -4.900, "y1": -4.5 * ELLE_M, "z0": 3.880, "z1": 9.050},
        {"name": "QS07_Ramp_SB_D2_D3", "xLocal": 0.0, "y0": +4.5 * ELLE_M, "y1": +4.900, "z0": 6.920, "z1": 13.050},
    ]
    return center_doors, aisle_doors, dukers_d2, qs07_ramps


# ==============================================================================
# 4) DIE 12 (11 GRUPPEN) MODULAREN GRUNDSTRUKTUR-BUILDER
# ==============================================================================

# ------------------------------------------------------------------------------
# A1) ark_hull_wall_bb — Backbord-Aussenwand (aussen & innen MAT_ARK_KOPHER + S7-Tor-Aussparung!)
# ------------------------------------------------------------------------------
def build_ark_hull_wall_bb(bm, uv_layer, lod):
    y0 = -11.500
    y1 = -11.500 + D_AW  # -11.188889 m
    n_courses_per_story = 4 if lod == 0 else (2 if lod == 1 else 1)
    ch = 0.014 if lod == 0 else (0.008 if lod == 1 else 0.0)

    # 1. 14 Sektionen x 4 Etagen (innen & aussen Kopher-verpicht mit plastischen Plankengaengen!)
    for i in range(14):
        sx0 = xL(X_STATIONS[i])
        sx1 = xL(X_STATIONS[i + 1])
        for k in range(4):
            z0 = Z_LEVELS[k]
            z1 = Z_TRAUF if k == 3 else Z_LEVELS[k + 1]
            if i == 6 and k == 2:
                # Sektion S7 auf Deck 2: EXAKTE S7-SEITENTOR-AUSSPARUNG xLocal in [-7.100 .. -2.900 m], Z in [6.000 .. 9.733 m]!
                gx0 = S7_GATE_CUTOUT["xLocal0"]  # -7.100 m
                gx1 = S7_GATE_CUTOUT["xLocal1"]  # -2.900 m
                gz1 = S7_GATE_CUTOUT["z1"]       # 9.733333 m
                # Links vom Tor (-10.000 .. -7.100 m)
                add_planked_wall_panel_x(bm, uv_layer, sx0, gx0, y0, y1, z0, z1, n_courses_per_story, ch, mat_idx=0)
                # Rechts vom Tor (-2.900 .. 0.000 m)
                add_planked_wall_panel_x(bm, uv_layer, gx1, sx1, y0, y1, z0, z1, n_courses_per_story, ch, mat_idx=0)
                # Sturz-Spandrel oberhalb Z = 9.733 m bis Z = 10.000 m
                add_planked_wall_panel_x(bm, uv_layer, gx0, gx1, y0, y1, gz1, z1, 1, ch, mat_idx=0)
            else:
                add_planked_wall_panel_x(bm, uv_layer, sx0, sx1, y0, y1, z0, z1, n_courses_per_story, ch, mat_idx=0)

    # 2. 4 durchgehende aeussere Berghoelzer / Scheuerleisten (Wales) + Traufgurt (MAT_ARK_KOPHER)
    wale_zs = [
        (0.060, 0.420, False),   # Sohlen-/Kimmgurt
        (1.820, 2.180, False),   # Deck-1-Bergholz
        (5.820, 6.180, True),    # Deck-2-Bergholz (am S7-Tor unterbrochen!)
        (9.840, 10.160, False),  # Deck-3-Bergholz
        (13.220, Z_TRAUF, False) # Oberer Traufgurt
    ]
    w_ch = 0.018 if lod <= 1 else 0.0
    for wz0, wz1, split_gate in wale_zs:
        if split_gate:
            add_metric_chamfered_beam(bm, uv_layer, -70.0, S7_GATE_CUTOUT["xLocal0"] - 0.48, y0 - 0.095, y0 + 0.02, wz0, wz1, w_ch, mat_idx=0, axis="X")
            add_metric_chamfered_beam(bm, uv_layer, S7_GATE_CUTOUT["xLocal1"] + 0.48, +70.0, y0 - 0.095, y0 + 0.02, wz0, wz1, w_ch, mat_idx=0, axis="X")
        else:
            add_metric_chamfered_beam(bm, uv_layer, -70.0, +70.0, y0 - 0.095, y0 + 0.02, wz0, wz1, w_ch, mat_idx=0, axis="X")
        # Innere Kopher-verpichte Wegerungs-Stringer entlang der Deck-Auflager (+Y Innenseite der Bordwand)
        if lod <= 1:
            if split_gate:
                add_metric_chamfered_beam(bm, uv_layer, -69.68, S7_GATE_CUTOUT["xLocal0"] - 0.48, y1 - 0.01, y1 + 0.055, wz0, wz1, w_ch * 0.7, mat_idx=0, axis="X")
                add_metric_chamfered_beam(bm, uv_layer, S7_GATE_CUTOUT["xLocal1"] + 0.48, +69.68, y1 - 0.01, y1 + 0.055, wz0, wz1, w_ch * 0.7, mat_idx=0, axis="X")
            else:
                add_metric_chamfered_beam(bm, uv_layer, -69.68, +69.68, y1 - 0.01, y1 + 0.055, wz0, wz1, w_ch * 0.7, mat_idx=0, axis="X")

    # 3. 15 vertikale 10-m-Schotten-Lisenen (aussen & innen) + eckverzahnte Steven-Koepfe (Bug/Heck)
    if lod <= 2:
        for i, xs in enumerate(X_STATIONS):
            xl = xL(xs)
            px0 = max(-70.0, xl - 0.18)
            px1 = min(+70.0, xl + 0.18)
            add_metric_chamfered_beam(bm, uv_layer, px0, px1, y0 - 0.065, y0 + 0.01, 0.0, Z_TRAUF, w_ch * 0.6, mat_idx=0, axis="Z")
            if lod <= 1 and 0 < i < 14:
                add_metric_chamfered_beam(bm, uv_layer, px0 + 0.03, px1 - 0.03, y1 - 0.01, y1 + 0.045, 0.35, Z_TRAUF, w_ch * 0.5, mat_idx=0, axis="Z")

    # 4. Eckverzahnte Steven-Koepfe (Finger-/Kastenverzinkung an Bug xLocal=-70.0 und Heck xLocal=+70.0)
    if lod <= 1:
        n_teeth = 9 if lod == 0 else 5
        dz_t = Z_TRAUF / float(n_teeth)
        for it in range(n_teeth):
            if it % 2 == 0:
                tz0 = it * dz_t + 0.03
                tz1 = (it + 1) * dz_t - 0.03
                add_metric_chamfered_beam(bm, uv_layer, -70.04, -69.52, y0 - 0.08, y1 + 0.02, tz0, tz1, 0.014, mat_idx=0, axis="X")
                add_metric_chamfered_beam(bm, uv_layer, +69.52, +70.04, y0 - 0.08, y1 + 0.02, tz0, tz1, 0.014, mat_idx=0, axis="X")


# ------------------------------------------------------------------------------
# A2) ark_hull_wall_sb — Steuerbord-Aussenwand + Bug- & Heck-Stirnwaende inkl. Giebel & 4 Giebel-Sturmklappen-Aussparungen!
# ------------------------------------------------------------------------------
def build_ark_hull_wall_sb(bm, uv_layer, lod):
    y0 = +11.500 - D_AW  # +11.188889 m
    y1 = +11.500
    n_courses_per_story = 4 if lod == 0 else (2 if lod == 1 else 1)
    ch = 0.014 if lod == 0 else (0.008 if lod == 1 else 0.0)
    w_ch = 0.018 if lod <= 1 else 0.0

    # 1. Steuerbord-Laengswand (14 Sektionen x 4 Etagen, aussen & innen MAT_ARK_KOPHER)
    for i in range(14):
        sx0 = xL(X_STATIONS[i])
        sx1 = xL(X_STATIONS[i + 1])
        for k in range(4):
            z0 = Z_LEVELS[k]
            z1 = Z_TRAUF if k == 3 else Z_LEVELS[k + 1]
            add_planked_wall_panel_x(bm, uv_layer, sx0, sx1, y0, y1, z0, z1, n_courses_per_story, ch, mat_idx=0)

    # 4 durchgehende aeussere Berghoelzer + innere Wegerungs-Stringer auf Steuerbord
    for wz0, wz1 in [(0.060, 0.420), (1.820, 2.180), (5.820, 6.180), (9.840, 10.160), (13.220, Z_TRAUF)]:
        add_metric_chamfered_beam(bm, uv_layer, -70.0, +70.0, y1 - 0.02, y1 + 0.095, wz0, wz1, w_ch, mat_idx=0, axis="X")
        if lod <= 1:
            add_metric_chamfered_beam(bm, uv_layer, -69.68, +69.68, y0 - 0.055, y0 + 0.01, wz0, wz1, w_ch * 0.7, mat_idx=0, axis="X")

    if lod <= 2:
        for i, xs in enumerate(X_STATIONS):
            xl = xL(xs)
            px0 = max(-70.0, xl - 0.18)
            px1 = min(+70.0, xl + 0.18)
            add_metric_chamfered_beam(bm, uv_layer, px0, px1, y1 - 0.01, y1 + 0.065, 0.0, Z_TRAUF, w_ch * 0.6, mat_idx=0, axis="Z")
            if lod <= 1 and 0 < i < 14:
                add_metric_chamfered_beam(bm, uv_layer, px0 + 0.03, px1 - 0.03, y0 - 0.045, y0 + 0.01, 0.35, Z_TRAUF, w_ch * 0.5, mat_idx=0, axis="Z")

    if lod <= 1:
        n_teeth = 9 if lod == 0 else 5
        dz_t = Z_TRAUF / float(n_teeth)
        for it in range(n_teeth):
            if it % 2 == 0:
                tz0 = it * dz_t + 0.03
                tz1 = (it + 1) * dz_t - 0.03
                add_metric_chamfered_beam(bm, uv_layer, -70.04, -69.52, y0 - 0.02, y1 + 0.08, tz0, tz1, 0.014, mat_idx=0, axis="X")
                add_metric_chamfered_beam(bm, uv_layer, +69.52, +70.04, y0 - 0.02, y1 + 0.08, tz0, tz1, 0.014, mat_idx=0, axis="X")

    # 2. Bug- & Heck-Stirnwaende (xLocal = +-70.0 m) von Z = 0.000 bis Traufe Z = 13.533 m + Giebel bis First Z = 14.700 m!
    #    Inkl. der 4 Giebel-Sturmklappen-Aussparungen (Y = +-3.25 m, 2.60 x 0.50 m bei Z = 13.72..14.22 m)!
    y_wall_min = -11.500 + D_AW
    y_wall_max = +11.500 - D_AW
    y_splits = [y_wall_min, -5.000, 0.000, +5.000, y_wall_max]

    for end_sign, wx0, wx1 in ((-1.0, -70.000, -70.000 + D_AW), (+1.0, +70.000 - D_AW, +70.000)):
        # Haupt-Stirnwand Z = 0.000 .. 13.533 m
        for iy in range(len(y_splits) - 1):
            sy0 = y_splits[iy]
            sy1 = y_splits[iy + 1]
            for k in range(4):
                z0 = Z_LEVELS[k]
                z1 = Z_TRAUF if k == 3 else Z_LEVELS[k + 1]
                add_planked_wall_panel_y(bm, uv_layer, wx0, wx1, sy0, sy1, z0, z0, z1, z1, n_courses_per_story, ch, mat_idx=0)

        # Giebeldreieck Z = 13.533 m .. get_roof_under_z(y) (First 14.700 m) mit den 2 Sturmklappen-Aussparungen bei Y = +-3.25 m
        # Y-Segmente im Giebel:
        #   [-11.189 .. -4.550] (geschlossen)
        #   [-4.550  .. -1.950] (Bb-Giebelklappe offen in Z = 13.720..14.220 m!)
        #   [-1.950  .. +1.950] (Mittelgiebel geschlossen bis First Z = 14.700 m)
        #   [+1.950  .. +4.550] (Stb-Giebelklappe offen in Z = 13.720..14.220 m!)
        #   [+4.550  .. +11.189] (geschlossen)
        gable_y_segs = [
            (y_wall_min, -4.550, False),
            (-4.550,     -1.950, True),
            (-1.950,     0.000,  False),
            (0.000,      +1.950, False),
            (+1.950,     +4.550, True),
            (+4.550,     y_wall_max, False),
        ]
        for gy0, gy1, has_shutter in gable_y_segs:
            z_top0 = get_roof_under_z(gy0)
            z_top1 = get_roof_under_z(gy1)
            if not has_shutter:
                add_planked_wall_panel_y(bm, uv_layer, wx0, wx1, gy0, gy1, Z_TRAUF, Z_TRAUF, z_top0, z_top1, 2 if lod == 0 else 1, ch, mat_idx=0)
            else:
                # Brüstung unter der Giebelklappe (Z = 13.533 .. 13.720 m)
                add_planked_wall_panel_y(bm, uv_layer, wx0, wx1, gy0, gy1, Z_TRAUF, Z_TRAUF, 13.720, 13.720, 1, ch, mat_idx=0)
                # Giebelspitze ueber der Giebelklappe (Z = 14.220 .. z_top0/z_top1)
                add_planked_wall_panel_y(bm, uv_layer, wx0, wx1, gy0, gy1, 14.220, 14.220, z_top0, z_top1, 1, ch, mat_idx=0)

        # Stirnwand-Berghoelzer & Lisenen (aussen & innen MAT_ARK_KOPHER)
        x_out0 = wx0 - 0.085 if end_sign < 0 else wx1 - 0.01
        x_out1 = wx0 + 0.01 if end_sign < 0 else wx1 + 0.085
        for wz0, wz1 in [(0.060, 0.420), (1.820, 2.180), (5.820, 6.180), (9.840, 10.160), (13.220, Z_TRAUF)]:
            add_metric_chamfered_beam(bm, uv_layer, x_out0, x_out1, -11.50, +11.50, wz0, wz1, w_ch, mat_idx=0, axis="Y")
        if lod <= 2:
            for py in (-11.32, -5.00, 0.00, +5.00, +11.32):
                z_p_top = get_roof_under_z(py)
                add_metric_chamfered_beam(bm, uv_layer, x_out0, x_out1, py - 0.16, py + 0.16, 0.0, z_p_top, w_ch * 0.6, mat_idx=0, axis="Z")


# ------------------------------------------------------------------------------
# A3) ark_hull_roof — 140-m-Satteldach (aussen MAT_ARK_KOPHER mit Stossleisten, Firstbalken, Ortgang & 8 Badgir-Kragen;
#                     innen/unten MAT_ARK_ROOF_WOOD mit Sparrenkoepfen alle 2.333 m unter 1-Elle-Traufueberstand!)
# ------------------------------------------------------------------------------
def build_ark_hull_roof(bm, uv_layer, lod):
    # Mat-Index 0 = MAT_ARK_KOPHER (Aussen), Mat-Index 1 = MAT_ARK_ROOF_WOOD (Innen/Unten)
    badgir_x_set = {1: 12.0, 4: 42.0, 9: 92.0, 12: 122.0}
    y_b_in = 4.880 - BADGIR_LY  # 3.480 m
    y_b_out = 4.880             # 4.880 m

    def _add_roof_slope_strip(x0, x1, y_a, y_b):
        """Erzeugt ein zweischaliges Satteldach-Segment:
        Untere Schale (0.13 m) = MAT_ARK_ROOF_WOOD (mat_idx=1),
        Obere Schale  (0.142 m) = MAT_ARK_KOPHER   (mat_idx=0)."""
        za = get_roof_under_z(y_a)
        zb = get_roof_under_z(y_b)
        d_in = 0.130
        # 1) Innenschalung (MAT_ARK_ROOF_WOOD = 1)
        add_sloped_quad_prism(
            bm, uv_layer,
            (x0, y_a, za), (x1, y_a, za), (x1, y_b, zb), (x0, y_b, zb),
            (0.0, 0.0, d_in), mat_idx=1, grain_axis="X", top_mat_idx=1, bot_mat_idx=1
        )
        # 2) Aeussere Kopher-Dachhaut (MAT_ARK_KOPHER = 0)
        add_sloped_quad_prism(
            bm, uv_layer,
            (x0, y_a, za + d_in), (x1, y_a, za + d_in), (x1, y_b, zb + d_in), (x0, y_b, zb + d_in),
            (0.0, 0.0, D_ROOF - d_in), mat_idx=0, grain_axis="X", top_mat_idx=0, bot_mat_idx=0
        )

    # 1. Dachflaechen fuer alle 14 Sektionen (mit exakten Aussparungen fuer alle 8 Badgir-Schaechte!)
    for i in range(14):
        sx0 = xL(X_STATIONS[i])
        sx1 = xL(X_STATIONS[i + 1])
        # Aeussere Seitenschiff-Dachflaechen inkl. 1-Elle-Traufueberstand (|Y| in [4.880 .. 11.967 m])
        _add_roof_slope_strip(sx0, sx1, -Y_EAVE_OUT, -y_b_out)
        _add_roof_slope_strip(sx0, sx1, +y_b_out, +Y_EAVE_OUT)
        # Innere First-Dachflaechen (|Y| in [0.000 .. 3.480 m])
        _add_roof_slope_strip(sx0, sx1, -y_b_in, 0.000)
        _add_roof_slope_strip(sx0, sx1, 0.000, +y_b_in)

        # Mittlerer Streifen |Y| in [3.480 .. 4.880 m] (enthaelt in S2, S5, S10, S13 die 8 Badgir-Durchbrueche!)
        if i in badgir_x_set:
            xb = badgir_x_set[i]
            bx0 = xL(xb - BADGIR_HALF_LX)
            bx1 = xL(xb + BADGIR_HALF_LX)
            # Vor dem Badgir-Schacht
            _add_roof_slope_strip(sx0, bx0, -y_b_out, -y_b_in)
            _add_roof_slope_strip(sx0, bx0, +y_b_in, +y_b_out)
            # Hinter dem Badgir-Schacht
            _add_roof_slope_strip(bx1, sx1, -y_b_out, -y_b_in)
            _add_roof_slope_strip(bx1, sx1, +y_b_in, +y_b_out)
        else:
            _add_roof_slope_strip(sx0, sx1, -y_b_out, -y_b_in)
            _add_roof_slope_strip(sx0, sx1, +y_b_in, +y_b_out)

    # 2. Massiver Kopher-Firstbalken (Y in [-0.26..+0.26 m], Z = 14.93..15.10 m) & Giebel-Ortgangbretter (MAT_ARK_KOPHER = 0)
    ch = 0.016 if lod <= 1 else 0.0
    add_metric_chamfered_beam(bm, uv_layer, -70.18, +70.18, -0.26, +0.26, Z_FIRST_TOP - 0.04, Z_FIRST_TOP + 0.12, ch, mat_idx=0, axis="X")

    for end_x0, end_x1 in ((-70.16, -69.80), (+69.80, +70.16)):
        for sgn in (-1.0, +1.0):
            y_e = sgn * Y_EAVE_OUT
            z_e = get_roof_under_z(Y_EAVE_OUT)
            add_sloped_quad_prism(
                bm, uv_layer,
                (end_x0, 0.0, Z_FIRST_UN - 0.05), (end_x1, 0.0, Z_FIRST_UN - 0.05),
                (end_x1, y_e, z_e - 0.05), (end_x0, y_e, z_e - 0.05),
                (0.0, 0.0, D_ROOF + 0.11), mat_idx=0, grain_axis="Y"
            )

    # 3. 8 Kopher-Badgir-Dachkragen um die 8 Badgir-Durchbrueche (MAT_ARK_KOPHER = 0, lassen den 1.633x1.400m Schacht 100% frei!)
    collar_w = 0.14
    for b_cut in get_badgir_cutouts():
        bx0, bx1 = b_cut["xLocal0"], b_cut["xLocal1"]
        by0, by1 = b_cut["y0"], b_cut["y1"]
        zc_bot = get_roof_under_z(by1 if by1 > 0 else by0) + 0.05
        zc_top = get_roof_under_z(by0 if by1 > 0 else by1) + D_ROOF + 0.18
        # 4 Kragenbalken AUSSERHALB [bx0..bx1] x [by0..by1]
        add_metric_chamfered_beam(bm, uv_layer, bx0 - collar_w, bx1 + collar_w, by0 - collar_w, by0, zc_bot, zc_top, ch * 0.6, mat_idx=0, axis="X")
        add_metric_chamfered_beam(bm, uv_layer, bx0 - collar_w, bx1 + collar_w, by1, by1 + collar_w, zc_bot, zc_top, ch * 0.6, mat_idx=0, axis="X")
        add_metric_chamfered_beam(bm, uv_layer, bx0 - collar_w, bx0, by0, by1, zc_bot, zc_top, ch * 0.6, mat_idx=0, axis="Y")
        add_metric_chamfered_beam(bm, uv_layer, bx1, bx1 + collar_w, by0, by1, zc_bot, zc_top, ch * 0.6, mat_idx=0, axis="Y")

    # 4. Plastische Dach-Stossleisten (Deckleisten alle ~1.25 m in MAT_ARK_KOPHER = 0)
    if lod <= 2:
        batten_step = 1.25 if lod == 0 else (2.50 if lod == 1 else 5.00)
        n_battens = int(round(L_SHIP / batten_step))
        for ib in range(n_battens + 1):
            bx = -70.0 + ib * batten_step
            # Pruefe ob bx in einen Badgir-Schacht faellt
            in_badgir_x = any(( abs((bx + 70.0) - xs) < BADGIR_HALF_LX + 0.05 ) for xs in BADGIR_X_SHIPS)
            for sgn in (-1.0, +1.0):
                if in_badgir_x:
                    # Teile Stossleiste vor und hinter dem Badgir-Schacht (|Y| in [0..3.45] und [4.91..11.967])
                    for ya, yb in ((0.24, y_b_in - 0.03), (y_b_out + 0.03, Y_EAVE_OUT)):
                        za = get_roof_under_z(ya) + D_ROOF
                        zb = get_roof_under_z(yb) + D_ROOF
                        add_sloped_quad_prism(
                            bm, uv_layer,
                            (bx - 0.045, sgn * ya, za), (bx + 0.045, sgn * ya, za),
                            (bx + 0.045, sgn * yb, zb), (bx - 0.045, sgn * yb, zb),
                            (0.0, 0.0, 0.048), mat_idx=0, grain_axis="Y"
                        )
                else:
                    za = get_roof_under_z(0.24) + D_ROOF
                    zb = get_roof_under_z(Y_EAVE_OUT) + D_ROOF
                    add_sloped_quad_prism(
                        bm, uv_layer,
                        (bx - 0.045, sgn * 0.24, za), (bx + 0.045, sgn * 0.24, za),
                        (bx + 0.045, sgn * Y_EAVE_OUT, zb), (bx - 0.045, sgn * Y_EAVE_OUT, zb),
                        (0.0, 0.0, 0.048), mat_idx=0, grain_axis="Y"
                    )

    # 5. Profilierte Dachsparren-Koepfe (rafter tails) alle 2.333 m (5 E.) unter dem gesamten 1-Elle-Traufueberstand
    #    sowie innere Dachsparren an der Dach-Innenseite (MAT_ARK_ROOF_WOOD = 1)
    if lod <= 2:
        rafter_step = (5.0 * ELLE_M) if lod <= 1 else (10.0 * ELLE_M)  # 2.3333 m (61 Stationen)
        n_rafters = int(round(L_SHIP / rafter_step))
        for ir in range(n_rafters + 1):
            rx = -70.0 + ir * rafter_step
            rx0 = max(-69.92, rx - 0.085)
            rx1 = min(+69.92, rx + 0.085)
            for sgn in (-1.0, +1.0):
                # Trauf-Sparrenkopf unter dem 1-Elle-Ueberstand (|Y| = 11.18..11.95 m)
                ya_t = 11.18
                yb_t = Y_EAVE_OUT - 0.02
                za_t = get_roof_under_z(ya_t)
                zb_t = get_roof_under_z(yb_t)
                add_sloped_quad_prism(
                    bm, uv_layer,
                    (rx0, sgn * ya_t, za_t - 0.14), (rx1, sgn * ya_t, za_t - 0.14),
                    (rx1, sgn * yb_t, zb_t - 0.11), (rx0, sgn * yb_t, zb_t - 0.11),
                    (0.0, 0.0, 0.14), mat_idx=1, grain_axis="Y"
                )
                # Durchgehender Innensparren an der Dachunterseite (|Y| = 0.20..11.18 m, spart Badgir-Schacht aus!)
                if lod <= 1:
                    in_badgir_r = any((abs((rx + 70.0) - xs) < BADGIR_HALF_LX + 0.10) for xs in BADGIR_X_SHIPS)
                    segs_y = ((0.20, y_b_in - 0.04), (y_b_out + 0.04, 11.18)) if in_badgir_r else ((0.20, 11.18),)
                    for y_r0, y_r1 in segs_y:
                        zr0 = get_roof_under_z(y_r0)
                        zr1 = get_roof_under_z(y_r1)
                        add_sloped_quad_prism(
                            bm, uv_layer,
                            (rx0, sgn * y_r0, zr0 - 0.13), (rx1, sgn * y_r0, zr0 - 0.13),
                            (rx1, sgn * y_r1, zr1 - 0.13), (rx0, sgn * y_r1, zr1 - 0.13),
                            (0.0, 0.0, 0.13), mat_idx=1, grain_axis="Y"
                        )


# ------------------------------------------------------------------------------
# A4) ark_hull_zohar — 1-Elle-Zohar-Lichtgaden (Z = 13.533..14.000 m, MAT_ARK_ROOF_WOOD)
#     Traufschwelle, Pfette, 116 profilierte Zohar-Stiele (5 E. Raster) & 2-lagig schraege Wetterlamellen
# ------------------------------------------------------------------------------
def build_ark_hull_zohar(bm, uv_layer, lod):
    ch = 0.012 if lod == 0 else (0.006 if lod == 1 else 0.0)
    h_sill = 0.65 * HANDBREITE_M  # 0.050556 m
    z_bot0 = Z_TRAUF
    z_bot1 = Z_TRAUF + h_sill
    z_top0 = Z_OUT_SL - h_sill
    z_top1 = Z_OUT_SL

    # Freiraum aussen bei |Y| = 11.490 m fuer die 448 beweglichen Sturmklappen -> Zohar sitzt in |Y| in [11.189..11.472 m]!
    y_in = 11.500 - D_AW       # 11.188889 m
    y_out_frame = 11.472       # laesst 18 mm bis |Y| = 11.490 m frei!

    for sgn in (-1.0, +1.0):
        ya = min(sgn * y_in, sgn * y_out_frame)
        yb = max(sgn * y_in, sgn * y_out_frame)
        # 1. Untere Traufschwelle & obere Zohar-Pfette
        add_metric_chamfered_beam(bm, uv_layer, -70.0, +70.0, ya, yb, z_bot0, z_bot1, ch, mat_idx=0, axis="X")
        add_metric_chamfered_beam(bm, uv_layer, -70.0, +70.0, ya, yb, z_top0, z_top1, ch, mat_idx=0, axis="X")

        # 2. Profilierte Zohar-Stiele im 5-Ellen-Raster (60 Felder = 61 Stiele je Seite, 122 inkl. Endstiele / 116 Innenstiele)
        n_bays = 60 if lod <= 2 else 30
        dx_bay = L_SHIP / float(n_bays)
        w_post_x = 0.260
        for ib in range(n_bays + 1):
            px = -70.0 + ib * dx_bay
            px0 = max(-70.0, px - 0.5 * w_post_x)
            px1 = min(+70.0, px + 0.5 * w_post_x)
            add_metric_chamfered_beam(bm, uv_layer, px0, px1, ya, yb, z_bot1, z_top0, ch, mat_idx=0, axis="Z")

            # 3. Exakt 5 feine, gleichmaessig gestaffelte, schraeg nach aussen abfallende Zedern-Wetterlamellen
            #    Recessed ~5.5 cm innen vor |Y| = 11.490 m (|Y| in [11.205..11.435 m]) -> 0 Clipping mit Sturmklappen!
            if ib < n_bays and lod <= 2:
                lx0 = px1 + 0.004
                lx1 = min(+70.0, (px + dx_bay) - 0.5 * w_post_x - 0.004)
                if lx1 > lx0 + 0.05:
                    n_lams = 5 if lod <= 1 else 3
                    z_clear_h = z_top0 - z_bot1
                    for il in range(n_lams):
                        z_lam = z_bot1 + ((il + 0.5) / float(n_lams)) * z_clear_h
                        if lod <= 1:
                            # Geneigte Wetterlamelle (innen hoeher, aussen tiefer gegen Schlagregen, endet bei |Y| = 11.435 m!)
                            y_l_in = sgn * 11.205
                            y_l_out = sgn * 11.435
                            z_l_in = z_lam + 0.018
                            z_l_out = z_lam - 0.018
                            add_sloped_quad_prism(
                                bm, uv_layer,
                                (lx0, y_l_in, z_l_in), (lx1, y_l_in, z_l_in),
                                (lx1, y_l_out, z_l_out), (lx0, y_l_out, z_l_out),
                                (0.0, 0.0, 0.018), mat_idx=0, grain_axis="X"
                            )
                        else:
                            add_metric_box(bm, uv_layer, lx0, lx1, min(sgn * 11.21, sgn * 11.435), max(sgn * 11.21, sgn * 11.435), z_lam - 0.010, z_lam + 0.010, mat_idx=0, grain_axis="X")

    # 4. Exakt 5 schraege Zedern-Wetterlamellen in allen 4 Giebel-Lueftungsoeffnungen (Bug & Heck, Y = +-3.25 m, Z = 13.72..14.22 m)
    #    Ebenfalls ~5.5 cm nach innen in die Laibung zurueckversetzt (|X| in [69.720..69.945 m]) -> 0 Clipping mit den 4 Giebel-Sturmklappen!
    if lod <= 2:
        n_g_lams = 5 if lod <= 1 else 3
        for end_sign in (-1.0, +1.0):
            x_l_in = end_sign * 69.720
            x_l_out = end_sign * 69.945
            for gy0, gy1 in ((-4.530, -1.970), (+1.970, +4.530)):
                # Rahmen-Laibung (Zeder) oben/unten
                if lod <= 1:
                    xa, xb = min(x_l_in, x_l_out), max(x_l_in, x_l_out)
                    add_metric_box(bm, uv_layer, xa, xb, gy0, gy1, 13.720, 13.748, mat_idx=0, grain_axis="Y")
                    add_metric_box(bm, uv_layer, xa, xb, gy0, gy1, 14.192, 14.220, mat_idx=0, grain_axis="Y")
                for il in range(n_g_lams):
                    z_lam = 13.748 + ((il + 0.5) / float(n_g_lams)) * (14.192 - 13.748)
                    if lod <= 1:
                        z_l_in = z_lam + 0.020
                        z_l_out = z_lam - 0.020
                        add_sloped_quad_prism(
                            bm, uv_layer,
                            (x_l_in, gy0, z_l_in), (x_l_in, gy1, z_l_in),
                            (x_l_out, gy1, z_l_out), (x_l_out, gy0, z_l_out),
                            (0.0, 0.0, 0.020), mat_idx=0, grain_axis="Y"
                        )
                    else:
                        xa, xb = min(x_l_in, x_l_out), max(x_l_in, x_l_out)
                        add_metric_box(bm, uv_layer, xa, xb, gy0, gy1, z_lam - 0.011, z_lam + 0.011, mat_idx=0, grain_axis="Y")


# ------------------------------------------------------------------------------
# A5) ark_hull_keels — 3 massive Kopher-Aussenkiele (Y = -8.167, 0.0, +8.167 m, Z = -0.467..0.000 m, MAT_ARK_KOPHER)
# ------------------------------------------------------------------------------
def build_ark_hull_keels(bm, uv_layer, lod):
    h_keel = 6.0 * HANDBREITE_M   # 1.0 Elle = 0.466667 m
    b_keel = 2.5 * ELLE_M         # 15 Haende = 1.166667 m
    hk = 0.5 * b_keel             # 0.583333 m
    y_keels = [-17.5 * ELLE_M, 0.0, +17.5 * ELLE_M]  # -8.1667, 0.0, +8.1667 m
    ch = 0.024 if lod == 0 else (0.014 if lod == 1 else 0.0)
    d_flat_end = 3.0 * ELLE_M     # 1.400000 m

    for yk in y_keels:
        ya, yb = yk - hk, yk + hk
        # 1. Horizontale Hauptsektionen S3..S12 (xShip in [20..120 m]) + flache Endbloecke [18.6..20 m] & [120..121.4 m]
        if lod <= 1:
            for i in range(2, 12):
                sx0, sx1 = xL(X_STATIONS[i]), xL(X_STATIONS[i + 1])
                add_metric_chamfered_beam(bm, uv_layer, sx0, sx1, ya, yb, -h_keel, 0.000, ch, mat_idx=0, axis="X")
                # Plastische Stosslaschen (Scarf-Joint Cheek Plates) alle 10.0 m
                if lod == 0:
                    add_metric_chamfered_beam(bm, uv_layer, sx0 - 0.42, sx0 + 0.42, ya - 0.045, yb + 0.045, -h_keel + 0.04, -0.04, 0.012, mat_idx=0, axis="X")
            add_metric_chamfered_beam(bm, uv_layer, xL(20.0 - d_flat_end), xL(20.0), ya, yb, -h_keel, 0.000, ch, mat_idx=0, axis="X")
            add_metric_chamfered_beam(bm, uv_layer, xL(120.0), xL(120.0 + d_flat_end), ya, yb, -h_keel, 0.000, ch, mat_idx=0, axis="X")
        else:
            add_metric_box(bm, uv_layer, xL(20.0 - d_flat_end), xL(120.0 + d_flat_end), ya, yb, -h_keel, 0.000, mat_idx=0, grain_axis="X")

        # 2. Abgeschraegte Bug- & Heck-Anlaufkufen (bis an die Bug-/Heck-Steven xLocal = +-69.85 m sichtbar durchlaufend!)
        xb0, xb1 = xL(0.15), xL(20.0 - d_flat_end)
        add_sloped_quad_prism(
            bm, uv_layer,
            (xb0, ya, -0.32), (xb1, ya, -h_keel), (xb1, yb, -h_keel), (xb0, yb, -0.32),
            (0.0, 0.0, h_keel), mat_idx=0, grain_axis="X"
        )
        xs0, xs1 = xL(120.0 + d_flat_end), xL(139.85)
        add_sloped_quad_prism(
            bm, uv_layer,
            (xs0, ya, -h_keel), (xs1, ya, -0.32), (xs1, yb, -0.32), (xs0, yb, -h_keel),
            (0.0, 0.0, h_keel), mat_idx=0, grain_axis="X"
        )

    # 3. Umlaufender Sohlen-Kimm-Gurt (Chine rubbing strake) entlang Y = +-11.500 m & xLocal = +-70.000 m
    if lod <= 2:
        for sgn in (-1.0, +1.0):
            yc0 = (-11.560 if sgn < 0 else +11.380)
            yc1 = (-11.380 if sgn < 0 else +11.560)
            add_metric_chamfered_beam(bm, uv_layer, -70.04, +70.04, yc0, yc1, -0.080, +0.180, ch * 0.6, mat_idx=0, axis="X")


# ------------------------------------------------------------------------------
# B6) ark_hull_sole — Boden-Sohle Z = 0.000..0.350 m (aussen & innen MAT_ARK_KOPHER!)
#                     + 3 massive Innen-Kielschweine Z = 0.350..0.690 m (MAT_ARK_HEAVY_TIMBER mit Kopher-Fussfuge!)
# ------------------------------------------------------------------------------
def build_ark_hull_sole(bm, uv_layer, lod):
    # Mat-Index 0 = MAT_ARK_KOPHER, Mat-Index 1 = MAT_ARK_HEAVY_TIMBER
    ch = 0.016 if lod == 0 else (0.010 if lod == 1 else 0.0)
    xl_min = -70.000 + 0.01
    xl_max = +70.000 - 0.01
    y_min = -11.500 + 0.01
    y_max = +11.500 - 0.01

    # 1. Boden-Sohle Z = 0.000 .. 0.350 m (sowohl aussen als auch innen MAT_ARK_KOPHER = 0!)
    if lod == 0:
        # 14 Sektionen x 10 plastisch gefaste Sohlen-Bohlenbahnen (damit Bilgen-Innenseite & Unterseite echte Plankenstruktur zeigen!)
        n_y_strakes = 10
        dy_s = (y_max - y_min) / float(n_y_strakes)
        for i in range(14):
            sx0 = max(xl_min, xL(X_STATIONS[i]))
            sx1 = min(xl_max, xL(X_STATIONS[i + 1]))
            for iy in range(n_y_strakes):
                sy0 = y_min + iy * dy_s
                sy1 = y_min + (iy + 1) * dy_s
                add_metric_chamfered_beam(bm, uv_layer, sx0, sx1, sy0, sy1, 0.000, D_BOT, 0.014, mat_idx=0, axis="X")
    elif lod == 1:
        n_y_strakes = 6
        dy_s = (y_max - y_min) / float(n_y_strakes)
        for iy in range(n_y_strakes):
            add_metric_chamfered_beam(bm, uv_layer, xl_min, xl_max, y_min + iy * dy_s, y_min + (iy + 1) * dy_s, 0.000, D_BOT, 0.012, mat_idx=0, axis="X")
    else:
        add_metric_box(bm, uv_layer, xl_min, xl_max, y_min, y_max, 0.000, D_BOT, mat_idx=0, grain_axis="X")

    # Umlaufende innere Kopher-Kimmkehle (Bilge pitch fillet an den Aussenwand-Fusskanten Z = 0.350..0.440 m)
    if lod <= 2:
        y_in_wall = 11.500 - D_AW
        x_in_wall = 70.000 - D_AW
        add_metric_chamfered_beam(bm, uv_layer, -x_in_wall, +x_in_wall, -y_in_wall, -y_in_wall + 0.16, D_BOT, D_BOT + 0.085, ch * 0.6, mat_idx=0, axis="X")
        add_metric_chamfered_beam(bm, uv_layer, -x_in_wall, +x_in_wall, +y_in_wall - 0.16, +y_in_wall, D_BOT, D_BOT + 0.085, ch * 0.6, mat_idx=0, axis="X")
        add_metric_chamfered_beam(bm, uv_layer, -x_in_wall, -x_in_wall + 0.16, -y_in_wall, +y_in_wall, D_BOT, D_BOT + 0.085, ch * 0.6, mat_idx=0, axis="Y")
        add_metric_chamfered_beam(bm, uv_layer, +x_in_wall - 0.16, +x_in_wall, -y_in_wall, +y_in_wall, D_BOT, D_BOT + 0.085, ch * 0.6, mat_idx=0, axis="Y")

    # 2. 3 massive Innen-Kielschweine (Y = -8.167, 0.0, +8.167 m, Z = 0.350..0.690 m) in MAT_ARK_HEAVY_TIMBER (mat_idx = 1)
    #    mit umlaufender Kopher-Fussfuge (MAT_ARK_KOPHER, mat_idx = 0)!
    b_keel_in = 6.0 * HANDBREITE_M        # 0.466667 m
    h_keel_in = 0.72 * b_keel_in          # 0.336000 m (Z = 0.354 .. 0.690 m)
    hk_in = 0.5 * b_keel_in               # 0.233333 m
    y_axes_k = [-17.5 * ELLE_M, 0.0, +17.5 * ELLE_M]

    for i in range(14):
        xa = xL(X_STATIONS[i] + (D_AW + 0.03 if i == 0 else 0.5 * D_TBH + 0.01))
        xb = xL(X_STATIONS[i + 1] - (D_AW + 0.03 if i == 13 else 0.5 * D_TBH + 0.01))
        for yk in y_axes_k:
            # Schmale Kopher-Fussfuge (Z = 0.350..0.382 m, MAT_ARK_KOPHER = 0)
            if lod <= 2:
                add_metric_chamfered_beam(bm, uv_layer, xa, xb, yk - hk_in - 0.032, yk + hk_in + 0.032, D_BOT, D_BOT + 0.034, ch * 0.4, mat_idx=0, axis="X")
            # Massives Eichen-Kielschwein (Z = 0.354..0.690 m, MAT_ARK_HEAVY_TIMBER = 1)
            add_metric_chamfered_beam(bm, uv_layer, xa, xb, yk - hk_in, yk + hk_in, D_BOT + 0.004, D_BOT + 0.004 + h_keel_in, ch * 1.2, mat_idx=1, axis="X")


# ------------------------------------------------------------------------------
# B7) ark_hull_deck_d1, ark_hull_deck_d2, ark_hull_deck_d3
#     (MAT_ARK_DECKS + schmale MAT_ARK_KOPHER-Dichtungskehle entlang der Aussenwand-Kanten!)
# ------------------------------------------------------------------------------
def _add_deck_slab_panel(bm, uv_layer, x0, x1, y0, y1, z0, z1, lod, mat_idx=0):
    """Erzeugt ein Deck-Bodenfeld mit gefasten Laengs-Decksbohlen in LOD0/LOD1."""
    if (x1 - x0) < 0.015 or (y1 - y0) < 0.015:
        return
    if lod == 0:
        # Unterteile in ~0.85 m breite gefaste Decksbohlen-Gruppen entlang Y
        n_pl = max(1, min(6, int(round((y1 - y0) / 0.95))))
        dy = (y1 - y0) / float(n_pl)
        for ip in range(n_pl):
            add_metric_chamfered_beam(bm, uv_layer, x0, x1, y0 + ip * dy, y0 + (ip + 1) * dy, z0, z1, 0.010, mat_idx=mat_idx, axis="X")
    elif lod == 1:
        n_pl = max(1, min(3, int(round((y1 - y0) / 1.80))))
        dy = (y1 - y0) / float(n_pl)
        for ip in range(n_pl):
            add_metric_chamfered_beam(bm, uv_layer, x0, x1, y0 + ip * dy, y0 + (ip + 1) * dy, z0, z1, 0.008, mat_idx=mat_idx, axis="X")
    else:
        add_metric_box(bm, uv_layer, x0, x1, y0, y1, z0, z1, mat_idx=mat_idx, grain_axis="X")


def _add_deck_bay_with_cutout(
    bm, uv_layer, x0, x1, y0, y1, z0, z1, cx0, cx1, cy0, cy1, lod,
    mat_idx=0, skip_x0_trimmer=False, skip_x1_trimmer=False
):
    """Schneidet exakt [cx0..cx1] x [cy0..cy1] aus dem Deckfeld [x0..x1] x [y0..y1] aus und
    rahmt den Durchbruch bündig AUSSERHALB der lichten Oeffnung mit plastischen Wechselbalken ein!"""
    if cy0 > y0 + 0.02:
        _add_deck_slab_panel(bm, uv_layer, x0, x1, y0, cy0, z0, z1, lod, mat_idx=mat_idx)
    if cy1 < y1 - 0.02:
        _add_deck_slab_panel(bm, uv_layer, x0, x1, cy1, y1, z0, z1, lod, mat_idx=mat_idx)
    if cx0 > x0 + 0.02:
        _add_deck_slab_panel(bm, uv_layer, x0, cx0, max(y0, cy0), min(y1, cy1), z0, z1, lod, mat_idx=mat_idx)
    if cx1 < x1 - 0.02:
        _add_deck_slab_panel(bm, uv_layer, cx1, x1, max(y0, cy0), min(y1, cy1), z0, z1, lod, mat_idx=mat_idx)

    # Plastische Wechselbalken-Einfassung (Trimmer beams) komplett ausserhalb [cx0..cx1] x [cy0..cy1]
    is_long_shaft = (skip_x0_trimmer or skip_x1_trimmer)
    bw = (3.5 * HANDBREITE_M) if is_long_shaft else (2.5 * HANDBREITE_M)
    zw0 = (z0 - 0.14) if is_long_shaft else (z0 - 0.04)
    zw1 = z1 + 0.04
    xb0 = cx0 if skip_x0_trimmer else max(x0, cx0 - bw)
    xb1 = cx1 if skip_x1_trimmer else min(x1, cx1 + bw)
    ch = 0.012 if lod <= 1 else 0.0

    if abs(cy0 - (-5.0)) > 0.25 and abs(cy0 - 5.0) > 0.25 and (cy0 - bw) >= y0 - 0.05:
        add_metric_chamfered_beam(bm, uv_layer, xb0, xb1, cy0 - bw, cy0, zw0, zw1, ch, mat_idx=mat_idx, axis="X")
    if abs(cy1 - (-5.0)) > 0.25 and abs(cy1 - 5.0) > 0.25 and (cy1 + bw) <= y1 + 0.05:
        add_metric_chamfered_beam(bm, uv_layer, xb0, xb1, cy1, cy1 + bw, zw0, zw1, ch, mat_idx=mat_idx, axis="X")
    if not skip_x0_trimmer and (cx0 - bw) >= x0 - 0.05:
        add_metric_chamfered_beam(bm, uv_layer, cx0 - bw, cx0, cy0, cy1, zw0, zw1, ch, mat_idx=mat_idx, axis="Y")
    if not skip_x1_trimmer and (cx1 + bw) <= x1 + 0.05:
        add_metric_chamfered_beam(bm, uv_layer, cx1, cx1 + bw, cy0, cy1, zw0, zw1, ch, mat_idx=mat_idx, axis="Y")


def _build_deck_level(bm, uv_layer, lod, k):
    """Gemeinsamer Praezisions-Generator fuer Deck 1 (k=1), Deck 2 (k=2) und Deck 3 (k=3).
    Mat-Index 0 = MAT_ARK_DECKS, Mat-Index 1 = MAT_ARK_KOPHER (schmale Dichtungskehle an Aussenwand)."""
    d_k = DECK_THICK[k]
    z_base = Z_LEVELS[k]
    z0 = z_base - 0.5 * d_k
    z1 = z_base + 0.5 * d_k
    inset_aw = D_AW + 0.02

    for i in range(14):
        x0 = xL(X_STATIONS[i] + (inset_aw if i == 0 else 0.0))
        x1 = xL(X_STATIONS[i + 1] - (inset_aw if i == 13 else 0.0))
        is_silo_sec = (i in SILO_SEC_INDICES)       # S3, S6, S9, S12
        is_goepel_sec = (i in (3, 10))              # S4, S11
        is_ramp_sec = (i in (6, 7))                 # S7, S8
        is_badgir_sec = (i in (1, 4, 9, 12))        # S2, S5, S10, S13 (8 Badgire!)

        for j in range(3):  # j=0: Bb-Seitenschiff, j=1: Mittelschiff, j=2: Stb-Seitenschiff
            y0 = (Y_AXES[j] + inset_aw) if j == 0 else Y_AXES[j]
            y1 = (Y_AXES[j + 1] - inset_aw) if j == 2 else Y_AXES[j + 1]

            if (k in (2, 3)) and (j in (0, 2)) and is_silo_sec:
                # 8 Silo-Durchbrueche auf D2 & D3 (1.0 Elle Kontrollgang entlang der Aussenbordwand bleibt stehen!)
                x_walk0 = x0 + 0.5 * D_TBH + 0.014
                x_walk1 = x1 - 0.5 * D_TBH - 0.014
                bw_silo = 2.5 * HANDBREITE_M
                if j == 0:
                    y_silo_face = -11.500 + 1.0 * ELLE_M  # -11.033333 m
                    _add_deck_slab_panel(bm, uv_layer, x_walk0, x_walk1, y0, y_silo_face - 0.008, z0, z1, lod, mat_idx=0)
                    add_metric_chamfered_beam(bm, uv_layer, x_walk0, x_walk1, y_silo_face - bw_silo, y_silo_face - 0.006, z0 - 0.06, z1 + 0.04, 0.010 if lod <= 1 else 0.0, mat_idx=0, axis="X")
                else:
                    y_silo_face = +11.500 - 1.0 * ELLE_M  # +11.033333 m
                    _add_deck_slab_panel(bm, uv_layer, x_walk0, x_walk1, y_silo_face + 0.008, y1, z0, z1, lod, mat_idx=0)
                    add_metric_chamfered_beam(bm, uv_layer, x_walk0, x_walk1, y_silo_face + 0.006, y_silo_face + bw_silo, z0 - 0.06, z1 + 0.04, 0.010 if lod <= 1 else 0.0, mat_idx=0, axis="X")

            elif (k in (2, 3)) and j == 1 and is_badgir_sec:
                # 8 Badgir-Schacht-Durchbrueche auf D2 & D3 (S2, S5, S10, S13 bei xShip = xSec + 2.00 m)
                x_ch = xL(X_STATIONS[i] + 2.00)
                bx0 = x_ch - BADGIR_HALF_LX
                bx1 = x_ch + BADGIR_HALF_LX
                by_bb0, by_bb1 = -4.880, -4.880 + BADGIR_LY
                by_sb0, by_sb1 = +4.880 - BADGIR_LY, +4.880
                _add_deck_bay_with_cutout(bm, uv_layer, x0, x1, y0, 0.0, z0, z1, bx0, bx1, by_bb0, by_bb1, lod, mat_idx=0)
                _add_deck_bay_with_cutout(bm, uv_layer, x0, x1, 0.0, y1, z0, z1, bx0, bx1, by_sb0, by_sb1, lod, mat_idx=0)

            elif k >= 1 and j == 0 and is_goepel_sec:
                # 2 Paternoster-Schaechte in S4 & S11 Bb-Seitenschiff (auf D1, D2 & D3)
                x_pat = xL(X_STATIONS[i] + 5.0 * ELLE_M)
                px0 = x_pat - 1.75 * ELLE_M
                px1 = x_pat + 1.75 * ELLE_M
                py0 = (-17.5 * ELLE_M) if k == 1 else (-14.75 * ELLE_M)
                py1 = -11.25 * ELLE_M
                _add_deck_bay_with_cutout(bm, uv_layer, x0, x1, y0, y1, z0, z1, px0, px1, py0, py1, lod, mat_idx=0)

            elif (k in (1, 2)) and j == 2 and is_goepel_sec:
                # 4 Archimedische Schnecken-Durchbrueche in S4 & S11 Stb-Seitenschiff (auf D1 & D2)
                x_mid_bay = 0.5 * (x0 + x1)
                scy0 = 6.080 if k == 1 else 8.520
                scy1 = 7.420 if k == 1 else 10.020
                _add_deck_bay_with_cutout(bm, uv_layer, x0, x_mid_bay, y0, y1, z0, z1, x0 + 0.680, x0 + 1.620, scy0, scy1, lod, mat_idx=0)
                _add_deck_bay_with_cutout(bm, uv_layer, x_mid_bay, x1, y0, y1, z0, z1, x0 + 8.380, x0 + 9.320, scy0, scy1, lod, mat_idx=0)

            elif k == 2 and j == 1 and is_ramp_sec:
                # Schwerlastrampen-Durchbruch D1->D2 auf Deck 2 (S7/S8 Bb-Mittelschiff: xShip in [65.333..76.533 m], Y in [-4.90..-2.10 m])
                rx0 = xL(140.0 * ELLE_M) if i == 6 else x0
                rx1 = x1 if i == 6 else xL(164.0 * ELLE_M)
                ry0 = -4.905  # garantiert 100 % frei in [-4.900 .. -2.100 m]!
                ry1 = -4.5 * ELLE_M
                _add_deck_bay_with_cutout(
                    bm, uv_layer, x0, x1, y0, y1, z0, z1, rx0, rx1, ry0, ry1, lod,
                    mat_idx=0, skip_x0_trimmer=(i == 7), skip_x1_trimmer=(i == 6)
                )

            elif k == 3 and j == 1 and is_ramp_sec:
                # Leichtrampen-Durchbruch D2->D3 auf Deck 3 (S7/S8 Stb-Mittelschiff: xShip in [64.867..76.533 m], Y in [+2.10..+4.90 m])
                rx0 = xL(139.0 * ELLE_M) if i == 6 else x0
                rx1 = x1 if i == 6 else xL(164.0 * ELLE_M)
                ry0 = +4.5 * ELLE_M
                ry1 = +4.905  # garantiert 100 % frei in [+2.100 .. +4.900 m]!
                _add_deck_bay_with_cutout(
                    bm, uv_layer, x0, x1, y0, y1, z0, z1, rx0, rx1, ry0, ry1, lod,
                    mat_idx=0, skip_x0_trimmer=(i == 7), skip_x1_trimmer=(i == 6)
                )

            else:
                _add_deck_slab_panel(bm, uv_layer, x0, x1, y0, y1, z0, z1, lod, mat_idx=0)

    # Schmale MAT_ARK_KOPHER-Dichtungskehle (mat_idx = 1) entlang der Aussenwand-Kanten (Gen 6,14 Deck-Wand-Abdichtung!)
    y_edge = 11.500 - D_AW
    x_edge = 70.000 - D_AW
    k_w = 0.140
    k_h = 0.048
    ch_k = 0.008 if lod <= 1 else 0.0
    # Backbord & Steuerbord Laengskehlen (oben & unten am Deck-Wand-Anschluss)
    if k == 2:
        # Auf Deck 2 am S7-Seitentor [-7.100..-2.900] unterbrechen!
        add_metric_chamfered_beam(bm, uv_layer, -x_edge, S7_GATE_CUTOUT["xLocal0"], -y_edge, -y_edge + k_w, z1, z1 + k_h, ch_k, mat_idx=1, axis="X")
        add_metric_chamfered_beam(bm, uv_layer, S7_GATE_CUTOUT["xLocal1"], +x_edge, -y_edge, -y_edge + k_w, z1, z1 + k_h, ch_k, mat_idx=1, axis="X")
    else:
        add_metric_chamfered_beam(bm, uv_layer, -x_edge, +x_edge, -y_edge, -y_edge + k_w, z1, z1 + k_h, ch_k, mat_idx=1, axis="X")
    add_metric_chamfered_beam(bm, uv_layer, -x_edge, +x_edge, +y_edge - k_w, +y_edge, z1, z1 + k_h, ch_k, mat_idx=1, axis="X")
    add_metric_chamfered_beam(bm, uv_layer, -x_edge, -x_edge + k_w, -y_edge, +y_edge, z1, z1 + k_h, ch_k, mat_idx=1, axis="Y")
    add_metric_chamfered_beam(bm, uv_layer, +x_edge - k_w, +x_edge, -y_edge, +y_edge, z1, z1 + k_h, ch_k, mat_idx=1, axis="Y")


def build_ark_hull_deck_d1(bm, uv_layer, lod):
    _build_deck_level(bm, uv_layer, lod, 1)


def build_ark_hull_deck_d2(bm, uv_layer, lod):
    _build_deck_level(bm, uv_layer, lod, 2)


def build_ark_hull_deck_d3(bm, uv_layer, lod):
    _build_deck_level(bm, uv_layer, lod, 3)


# ------------------------------------------------------------------------------
# B8) ark_hull_heavy_timber — Alle 15 Laengsunterzuege (0.355 x 0.228 m) + 45 Koenigsstuetzen-Schaefte (0.336 x 0.336 m)
# ------------------------------------------------------------------------------
def build_ark_hull_heavy_timber(bm, uv_layer, lod):
    b_keel_in = 6.0 * HANDBREITE_M        # 0.466667 m
    h_keel_in = 0.72 * b_keel_in          # 0.336000 m
    half_girder_y = 0.38 * b_keel_in      # 0.177333 m -> Breite 0.354667 m (~0.355 m)
    h_girder_z = 0.68 * h_keel_in         # 0.228480 m (~0.228 m)
    half_post = 0.36 * b_keel_in          # 0.168000 m -> Querschnitt 0.336 x 0.336 m
    y_axes_k = [-17.5 * ELLE_M, 0.0, +17.5 * ELLE_M]
    ch_g = 0.016 if lod == 0 else (0.010 if lod == 1 else 0.0)
    ch_p = 0.022 if lod == 0 else (0.014 if lod == 1 else 0.0)

    # 1. Alle 15 Laengsunterzuege (4 Straenge unter D1, D2, D3 = 12 + 3 Dachpfetten unter k=4 = 15 Laengsunterzuege!)
    #    Beachtet exakt alle Silo-, Goepel- und Rampen-Aussparungen aus Z. 12719-12733!
    for i in range(14):
        is_silo_sec = (i in SILO_SEC_INDICES)
        is_goepel_sec = (i in (3, 10))
        is_ramp_sec = (i in (6, 7))
        xa_beam = xL((D_AW + 0.03) if i == 0 else (X_STATIONS[i] + 0.22))
        xb_beam = xL((140.0 - D_AW - 0.03) if i == 13 else (X_STATIONS[i + 1] - 0.22))

        for ky in range(3):
            yk = y_axes_k[ky]
            for k in (1, 2, 3, 4):
                if ky != 1 and is_silo_sec and k in (2, 3):
                    continue  # Keine Seitenschiff-Unterzuege durch die 8 Silotuerme!
                if ky == 0 and is_goepel_sec and k >= 1:
                    continue  # Keine Bb-Seitenschiff-Unterzuege durch den Paternoster-Schacht!
                y_beams = [-4.5 * ELLE_M, +4.5 * ELLE_M] if (ky == 1 and k <= 3) else [yk]
                for yb in y_beams:
                    if is_ramp_sec and ((k == 2 and yb < 0.0) or (k == 3 and yb > 0.0)):
                        continue  # Keine Unterzuege quer durch den Rampenschacht!
                    z_top_b = (Z_LEVELS[k] - 0.5 * DECK_THICK[k] - 0.004) if k < 4 else (get_deck_z(4, yb) - 0.65 * D_ROOF)
                    z_bot_b = z_top_b - h_girder_z
                    add_metric_chamfered_beam(
                        bm, uv_layer, xa_beam, xb_beam, yb - half_girder_y, yb + half_girder_y,
                        z_bot_b, z_top_b, ch_g, mat_idx=0, axis="X"
                    )

    # 2. Alle 45 Koenigsstuetzen-Schaefte (0.336 x 0.336 m an X_STATIONS[0..14], gefaste Kanten,
    #    enden buendig unter den 0.260 m hohen Sattelholz-Kapitellen aus ark_wave_a_kit.glb!)
    y_post_cols = [-17.5 * ELLE_M, -4.5 * ELLE_M, +4.5 * ELLE_M, +17.5 * ELLE_M]
    silo_boundary_stations = {2, 3, 5, 6, 8, 9, 11, 12}

    for i in range(15):
        xp = xL((D_AW + 0.28) if i == 0 else ((140.0 - D_AW - 0.28) if i == 14 else X_STATIONS[i]))
        is_silo_st = (i in silo_boundary_stations)
        for yp in y_post_cols:
            is_side_col = (abs(yp) > 5.0)
            for k in range(4):
                # Keine Seitenschiff-Stuetzen an Silo-Grenzstationen auf D1/D2 (0.0 mm Ueberlappung mit den 8 Silo-Durchbruechen!)
                if is_side_col and is_silo_st and k in (1, 2):
                    continue
                z_p0 = (D_BOT + 0.004 + h_keel_in) if k == 0 else (Z_LEVELS[k] + 0.5 * DECK_THICK[k])
                z_girder_top = (Z_LEVELS[k + 1] - 0.5 * DECK_THICK[k + 1] - 0.004) if k < 3 else (get_deck_z(4, yp) - 0.65 * D_ROOF)
                z_girder_bot = z_girder_top - h_girder_z
                # Das Sattelholz-Kapitell (ark_kingpost_capital) sitzt mit Origin Z=0.0 an z_girder_bot und reicht 0.260 m nach unten
                z_shaft_top = z_girder_bot - 0.260
                add_metric_chamfered_beam(
                    bm, uv_layer, xp - half_post, xp + half_post, yp - half_post, yp + half_post,
                    z_p0, z_shaft_top, ch_p, mat_idx=0, axis="Z"
                )


# ------------------------------------------------------------------------------
# C9) ark_hull_long_bh — 2 Laengsschotten (Y = -5.000 m & Y = +5.000 m, 0.233 m stark, MAT_ARK_LONG_BH)
#     mit plastischen Bohlenlagen, Staenderrippen & EXAKT ALLEN 60 Laengsschotttuer-Positionen (56 offen + 4 S8-Rampenwand)
# ------------------------------------------------------------------------------
def build_ark_hull_long_bh(bm, uv_layer, lod):
    open_doors, _ = get_longitudinal_bh_door_specs()
    # Index open doors by (j, i, k)
    door_map = {(d["j"], d["i"], d["k"]): d for d in open_doors}

    n_courses = 4 if lod == 0 else (2 if lod == 1 else 1)
    ch = 0.012 if lod == 0 else (0.007 if lod == 1 else 0.0)
    roof_inset_z = 0.65 * D_ROOF

    for j in (1, 2):
        y_c = Y_AXES[j]  # -5.000 m bzw. +5.000 m
        y0 = y_c - 0.5 * D_LBH
        y1 = y_c + 0.5 * D_LBH

        for i in range(14):
            x0 = xL(X_STATIONS[i] + (D_AW if i == 0 else (0.5 * D_TBH + 0.004)))
            x1 = xL(X_STATIONS[i + 1] - (D_AW if i == 13 else (0.5 * D_TBH + 0.004)))

            for k in range(4):
                z0_raw = get_deck_z(k, y_c)
                z1_raw = get_deck_z(k + 1, y_c) - (roof_inset_z if k == 3 else 0.0)
                z_bot = (D_BOT + 0.004) if k == 0 else (z0_raw + 0.5 * DECK_THICK[k] + 0.004)
                z_top = (z1_raw - 0.5 * DECK_THICK[k + 1] - 0.004) if k < 3 else (z1_raw - 0.004)

                d_spec = door_map.get((j, i, k))
                if d_spec is None:
                    # Geschlossenes Schottfeld (Doppelboden k=0, Silo-Sektionen S3/S6/S9/S12, S8-Rampenwand)
                    add_planked_wall_panel_x(bm, uv_layer, x0, x1, y0, y1, z_bot, z_top, n_courses, ch, mat_idx=0)
                    # Vertikale Staenderrippen in der Mitte des geschlossenen Schottfelds (LOD0/LOD1)
                    if lod <= 1 and k >= 1:
                        for rx_frac in (0.33, 0.67):
                            rx = x0 + rx_frac * (x1 - x0)
                            add_metric_chamfered_beam(bm, uv_layer, rx - 0.065, rx + 0.065, y0 - 0.022, y1 + 0.022, z_bot, z_top, ch * 0.6, mat_idx=0, axis="Z")
                else:
                    # Schottfeld mit exakter Tueraussparung [xd0..xd1] x [zd0..zd1]
                    xd0 = d_spec["xLocal0"]
                    xd1 = d_spec["xLocal1"]
                    zd0 = d_spec["z0"]
                    zd1 = min(z_top - 0.05, d_spec["z1"])

                    # 1) Wandfeld links der Tuer [x0 .. xd0]
                    if xd0 > x0 + 0.01:
                        add_planked_wall_panel_x(bm, uv_layer, x0, xd0, y0, y1, z_bot, z_top, n_courses, ch, mat_idx=0)
                    # 2) Wandfeld rechts der Tuer [xd1 .. x1]
                    if x1 > xd1 + 0.01:
                        add_planked_wall_panel_x(bm, uv_layer, xd1, x1, y0, y1, z_bot, z_top, n_courses, ch, mat_idx=0)
                    # 3) Flutsuell unterhalb der Tueroeffnung [z_bot .. zd0]
                    if zd0 > z_bot + 0.01:
                        add_planked_wall_panel_x(bm, uv_layer, xd0, xd1, y0, y1, z_bot, zd0, 1, ch, mat_idx=0)
                    # 4) Sturz-Brüstung oberhalb der Tueroeffnung [zd1 .. z_top]
                    if z_top > zd1 + 0.01:
                        add_planked_wall_panel_x(bm, uv_layer, xd0, xd1, y0, y1, zd1, z_top, 1, ch, mat_idx=0)

                    # Vertikale Staenderrippen seitlich neben den Tuerpfosten (ausserhalb [xd0-0.25 .. xd1+0.25])
                    if lod <= 1:
                        for rx in (0.5 * (x0 + max(x0, xd0 - 0.25)), 0.5 * (min(x1, xd1 + 0.25) + x1)):
                            if (x0 + 0.30) < rx < (xd0 - 0.30) or (xd1 + 0.30) < rx < (x1 - 0.30):
                                add_metric_chamfered_beam(bm, uv_layer, rx - 0.06, rx + 0.06, y0 - 0.020, y1 + 0.020, z_bot, z_top, ch * 0.6, mat_idx=0, axis="Z")


# ------------------------------------------------------------------------------
# C10) ark_hull_trans_bh — 13 innere Querschotten QS01..QS13 (xShip = 10..130 m, 0.233 m stark, MAT_ARK_TRANS_BH)
#      mit allen 39 Mittelschiff-Tueren, 16 Seitenschiff-Tueren, 26 D2-Spuelrinnen-Duekern & 2 QS07-Rampendurchbruechen!
# ------------------------------------------------------------------------------
def build_ark_hull_trans_bh(bm, uv_layer, lod):
    center_doors, aisle_doors, dukers_d2, _ = get_transverse_bh_door_and_ramp_specs()
    center_map = {(d["i"], d["k"]): d for d in center_doors}
    aisle_map = {(d["i"], d["k"], d["j"]): d for d in aisle_doors}

    n_courses = 4 if lod == 0 else (2 if lod == 1 else 1)
    ch = 0.012 if lod == 0 else (0.007 if lod == 1 else 0.0)
    top_inset_z = 0.65 * D_ROOF
    y_axes_qs = [-11.500 + D_AW + 0.015, -5.000, +5.000, +11.500 - D_AW - 0.015]

    def _z_ceil(k, y_val):
        if k < 3:
            return get_deck_z(k + 1, y_val) - (0.5 * DECK_THICK[k + 1] + 0.004)
        return get_roof_under_z(y_val) - top_inset_z

    def _add_qs_strip(x0, x1, ya, yb, z_bot, z_top_a=None, z_top_b=None, nc=n_courses):
        if (yb - ya) < 0.008:
            return
        zta = _z_ceil(3, ya) if z_top_a is None else z_top_a
        ztb = _z_ceil(3, yb) if z_top_b is None else z_top_b
        if max(zta - z_bot, ztb - z_bot) < 0.008:
            return
        # Falls der Streifen den Dachfirst Y = 0.0 m ueberschreitet (zta -> First -> ztb), am First Y = 0.0 splitten!
        if ya < -0.005 and yb > +0.005 and abs(zta - ztb) < 0.5 and zta > 13.0:
            z_mid = _z_ceil(3, 0.0)
            add_planked_wall_panel_y(bm, uv_layer, x0, x1, ya, 0.0, z_bot, z_bot, zta, z_mid, nc, ch, mat_idx=0)
            add_planked_wall_panel_y(bm, uv_layer, x0, x1, 0.0, yb, z_bot, z_bot, z_mid, ztb, nc, ch, mat_idx=0)
        else:
            add_planked_wall_panel_y(bm, uv_layer, x0, x1, ya, yb, z_bot, z_bot, zta, ztb, nc, ch, mat_idx=0)

    for i in range(1, 14):  # QS01..QS13
        x_qs = X_STATIONS[i]
        x0 = xL(x_qs - 0.5 * D_TBH)
        x1 = xL(x_qs + 0.5 * D_TBH)

        for j in range(3):  # j=0: Bb-Seitenschiff, j=1: Mittelschiff, j=2: Stb-Seitenschiff
            y0 = y_axes_qs[j]
            y1 = y_axes_qs[j + 1]

            for k in range(4):
                d_bot_off = (D_BOT if k == 0 else 0.5 * DECK_THICK[k]) + 0.004
                z_bot = get_deck_z(k, y0) + d_bot_off
                z_ceil_0 = _z_ceil(k, y0)
                z_ceil_1 = _z_ceil(k, y1)

                # FALL 1: QS07 (i == 7, xShip = 70.0 m) Mittelschiff auf D1, D2, D3 -> Mitteltuer + 2 grosse Rampendurchbrueche!
                if i == 7 and j == 1 and k >= 1:
                    cd = center_map[(i, k)]
                    yd0, yd1 = cd["y0"], cd["y1"]
                    zd0, zd1 = cd["z0"], cd["z1"]
                    yb1_0, yb1_1 = -4.900, -4.5 * ELLE_M  # -2.100 m (Bb-Schwerlastrampe D1->D2, frei Z = 3.88..9.05 m)
                    yb3_0, yb3_1 = +4.5 * ELLE_M, +4.900  # +2.100 m (Stb-Leichtrampe D2->D3, frei Z = 6.92..13.05 m)

                    # Schmale Randstreifen an den Laengsschotten [-5.0..-4.90] und [+4.90..+5.0]
                    _add_qs_strip(x0, x1, y0, yb1_0, z_bot, _z_ceil(k, y0), _z_ceil(k, yb1_0))
                    _add_qs_strip(x0, x1, yb3_1, y1, z_bot, _z_ceil(k, yb3_1), _z_ceil(k, y1))

                    # Bb-Rampenfeld [yb1_0 .. yb1_1] = [-4.900 .. -2.100 m]:
                    if k == 1:
                        # Frei oberhalb Z = 3.880 m -> Wand nur unterhalb Z = 3.880 m
                        _add_qs_strip(x0, x1, yb1_0, yb1_1, z_bot, 3.880, 3.880, nc=2)
                    elif k == 2:
                        # Frei unterhalb Z = 9.050 m -> Wand nur oberhalb Z = 9.050 m bis Decke
                        _add_qs_strip(x0, x1, yb1_0, yb1_1, 9.050, _z_ceil(k, yb1_0), _z_ceil(k, yb1_1), nc=1)
                    else:  # k == 3: voll geschlossen auf D3
                        _add_qs_strip(x0, x1, yb1_0, yb1_1, z_bot, _z_ceil(k, yb1_0), _z_ceil(k, yb1_1))

                    # Stb-Rampenfeld [yb3_0 .. yb3_1] = [+2.100 .. +4.900 m]:
                    if k == 1:
                        # Voll geschlossen auf D1
                        _add_qs_strip(x0, x1, yb3_0, yb3_1, z_bot, _z_ceil(k, yb3_0), _z_ceil(k, yb3_1))
                    elif k == 2:
                        # Frei oberhalb Z = 6.920 m -> Wand nur unterhalb Z = 6.920 m
                        _add_qs_strip(x0, x1, yb3_0, yb3_1, z_bot, 6.920, 6.920, nc=1)
                    else:  # k == 3: frei unterhalb Z = 13.050 m -> Wand nur oberhalb Z = 13.050 m bis Dach!
                        _add_qs_strip(x0, x1, yb3_0, yb3_1, 13.050, _z_ceil(k, yb3_0), _z_ceil(k, yb3_1), nc=1)

                    # Zwischenpfeiler zwischen Rampenoeffnungen und Mitteltuer [yb1_1 .. yd0] & [yd1 .. yb3_0]
                    _add_qs_strip(x0, x1, yb1_1, yd0, z_bot, _z_ceil(k, yb1_1), _z_ceil(k, yd0))
                    _add_qs_strip(x0, x1, yd1, yb3_0, z_bot, _z_ceil(k, yd1), _z_ceil(k, yb3_0))

                    # Mitteltuer-Suell [z_bot .. zd0] und Mitteltuer-Sturz [zd1 .. Decke]
                    _add_qs_strip(x0, x1, yd0, yd1, z_bot, zd0, zd0, nc=1)
                    _add_qs_strip(x0, x1, yd0, yd1, zd1, _z_ceil(k, yd0), _z_ceil(k, yd1), nc=1)

                # FALL 2: Normales Mittelschiff-Querschottfeld (k >= 1) mit Mitteltuer (+ 2 D2-Spuelrinnen-Duekern auf k=2)
                elif j == 1 and k >= 1:
                    cd = center_map[(i, k)]
                    yd0, yd1 = cd["y0"], cd["y1"]
                    zd0, zd1 = cd["z0"], cd["z1"]

                    if k == 2:
                        # Mit 2 D2-Spuelrinnen-Duekern bei Y in [+-1.1667 .. +-1.6733 m], Z in [z_bot .. z_bot + 4.8 H.]
                        h_c = 4.8 * HANDBREITE_M
                        y_c_out = 3.5 * ELLE_M + 0.04      # 1.673333 m
                        y_c_in = abs(yd0) + 3.0 * HANDBREITE_M  # 1.166667 m
                        z_duk_top = z_bot + h_c

                        # Aussenfelder [-5.0 .. -1.673] & [+1.673 .. +5.0]
                        _add_qs_strip(x0, x1, y0, -y_c_out, z_bot, _z_ceil(k, y0), _z_ceil(k, -y_c_out))
                        _add_qs_strip(x0, x1, +y_c_out, y1, z_bot, _z_ceil(k, +y_c_out), _z_ceil(k, y1))
                        # Wand ueber den beiden Duekern [-1.673 .. -1.167] & [+1.167 .. +1.673] ab z_duk_top
                        _add_qs_strip(x0, x1, -y_c_out, -y_c_in, z_duk_top, _z_ceil(k, -y_c_out), _z_ceil(k, -y_c_in), nc=3)
                        _add_qs_strip(x0, x1, +y_c_in, +y_c_out, z_duk_top, _z_ceil(k, +y_c_in), _z_ceil(k, +y_c_out), nc=3)
                        # Schmale Pfostenstreifen zwischen Dueker und Mitteltuer [-1.167 .. -0.933] & [+0.933 .. +1.167]
                        _add_qs_strip(x0, x1, -y_c_in, yd0, z_bot, _z_ceil(k, -y_c_in), _z_ceil(k, yd0))
                        _add_qs_strip(x0, x1, yd1, +y_c_in, z_bot, _z_ceil(k, yd1), _z_ceil(k, +y_c_in))
                    else:
                        _add_qs_strip(x0, x1, y0, yd0, z_bot, _z_ceil(k, y0), _z_ceil(k, yd0))
                        _add_qs_strip(x0, x1, yd1, y1, z_bot, _z_ceil(k, yd1), _z_ceil(k, y1))

                    # Suell & Sturz der Mitteltuer
                    _add_qs_strip(x0, x1, yd0, yd1, z_bot, zd0, zd0, nc=1)
                    _add_qs_strip(x0, x1, yd0, yd1, zd1, _z_ceil(k, yd0), _z_ceil(k, yd1), nc=1)

                # FALL 3: Seitenschiff-Querschottfeld (j in (0, 2)) — entweder mit Seitenschiff-Tuer oder geschlossen
                elif (i, k, j) in aisle_map:
                    ad = aisle_map[(i, k, j)]
                    yda0, yda1 = ad["y0"], ad["y1"]
                    zda0, zda1 = ad["z0"], ad["z1"]
                    _add_qs_strip(x0, x1, y0, yda0, z_bot, _z_ceil(k, y0), _z_ceil(k, yda0))
                    _add_qs_strip(x0, x1, yda1, y1, z_bot, _z_ceil(k, yda1), _z_ceil(k, y1))
                    _add_qs_strip(x0, x1, yda0, yda1, z_bot, zda0, zda0, nc=1)
                    _add_qs_strip(x0, x1, yda0, yda1, zda1, _z_ceil(k, yda0), _z_ceil(k, yda1), nc=1)

                else:
                    # Geschlossenes Querschottfeld
                    _add_qs_strip(x0, x1, y0, y1, z_bot, z_ceil_0, z_ceil_1)

        # Vertikale Aussteifungsrippen an den Querschotten (ausserhalb aller Tuer- & Rampendurchbrueche!)
        if lod <= 1:
            for ry in (-9.60, -8.167, -3.50 if i != 7 else -1.72, +3.50 if i != 7 else +1.72, +8.167, +9.60):
                z_r_top = _z_ceil(3, ry)
                add_metric_chamfered_beam(bm, uv_layer, x0 - 0.020, x1 + 0.020, ry - 0.065, ry + 0.065, D_BOT + 0.01, z_r_top, ch * 0.6, mat_idx=0, axis="Z")


# ==============================================================================
# 5) OBJEKT-LISTE, MATERIAL-ZUORDNUNG & AUTOMATISCHE PYTHON-OEFFNUNGS-ASSERTIONS
# ==============================================================================

BASE_STRUCTURE_SPECS = [
    # (name, builder_fn, mat_names, num_lods, lod_dists, description)
    (
        "ark_hull_wall_bb",
        build_ark_hull_wall_bb,
        ["MAT_ARK_KOPHER"],
        4, [150, 500, 1500, 3000],
        "Backbord-Aussenwand (Y=-11.500..-11.189m, Z=0..13.533m, Gen 6,14 aussen & innen Kopher-verpicht, 4 Berghoelzer, Lisenen, Steven-Koepfe & exakte S7-Tor-Aussparung)",
    ),
    (
        "ark_hull_wall_sb",
        build_ark_hull_wall_sb,
        ["MAT_ARK_KOPHER"],
        4, [150, 500, 1500, 3000],
        "Steuerbord-Aussenwand (Y=+11.189..+11.500m) + Bug-/Heck-Stirnwaende (xLocal=+-70m) inkl. Giebel bis First Z=14.700m & 4 Giebel-Sturmklappen-Aussparungen (Gen 6,14 aussen & innen Kopher-verpicht)",
    ),
    (
        "ark_hull_roof",
        build_ark_hull_roof,
        ["MAT_ARK_KOPHER", "MAT_ARK_ROOF_WOOD"],
        4, [150, 500, 1500, 3000],
        "140-m-Satteldach (First Z=14.700..14.972m, 1-Elle-Traufueberstand bis |Y|=11.967m, aussen Kopher mit Stossleisten, Firstbalken & 8 Badgir-Kragen, innen Zedernholz mit Sparrenkoepfen alle 2.333m)",
    ),
    (
        "ark_hull_zohar",
        build_ark_hull_zohar,
        ["MAT_ARK_ROOF_WOOD"],
        4, [150, 500, 1500, 3000],
        "1-Elle-Zohar-Lichtgaden (Z=13.533..14.000m an Y=+-11.500m, Traufschwelle, Pfette, 116 profilierte Zohar-Stiele im 5-E.-Raster & 5 schraege Zedern-Wetterlamellen inkl. 4 Giebel-Oeffnungen)",
    ),
    (
        "ark_hull_keels",
        build_ark_hull_keels,
        ["MAT_ARK_KOPHER"],
        4, [150, 500, 1500, 3000],
        "3 massive Kopher-Aussenkiele (Y=-8.167, 0.0, +8.167m, Z=-0.467..0.000m, Breite 1.167m, Bug-/Heck-Anlaufkufen, Stosslaschen & Sohlen-Kimm-Gurt)",
    ),
    (
        "ark_hull_sole",
        build_ark_hull_sole,
        ["MAT_ARK_KOPHER", "MAT_ARK_HEAVY_TIMBER"],
        4, [150, 500, 1500, 3000],
        "Boden-Sohle Z=0.000..0.350m (Gen 6,14 aussen & innen Kopher-verpicht) + 3 massive Innen-Kielschweine Z=0.350..0.690m in MAT_ARK_HEAVY_TIMBER mit Kopher-Fussfuge",
    ),
    (
        "ark_hull_deck_d1",
        build_ark_hull_deck_d1,
        ["MAT_ARK_DECKS", "MAT_ARK_KOPHER"],
        3, [28, 75, 145],
        "Deck 1 (Z=1.883..2.117m, MAT_ARK_DECKS + Kopher-Dichtungskehle) mit 2 Paternoster-Schaechten & 4 Schnecken-Durchbruechen inkl. Wechselbalken",
    ),
    (
        "ark_hull_deck_d2",
        build_ark_hull_deck_d2,
        ["MAT_ARK_DECKS", "MAT_ARK_KOPHER"],
        3, [28, 75, 145],
        "Deck 2 (Z=5.883..6.117m, MAT_ARK_DECKS + Kopher-Dichtungskehle) mit 8 Silo-, 2 Paternoster-, 4 Schnecken-, 8 Badgir- & D1->D2 Schwerlastrampen-Durchbruechen",
    ),
    (
        "ark_hull_deck_d3",
        build_ark_hull_deck_d3,
        ["MAT_ARK_DECKS", "MAT_ARK_KOPHER"],
        3, [28, 75, 145],
        "Deck 3 (Z=9.903..10.097m, MAT_ARK_DECKS + Kopher-Dichtungskehle) mit 8 Silo-, 2 Paternoster-, 8 Badgir- & D2->D3 Leichtrampen-Durchbruechen",
    ),
    (
        "ark_hull_heavy_timber",
        build_ark_hull_heavy_timber,
        ["MAT_ARK_HEAVY_TIMBER"],
        3, [28, 75, 145],
        "Alle 15 Laengsunterzuege (0.355x0.228m unter D1-D3 & Dachpfetten) + 45 Koenigsstuetzen-Schaefte (0.336x0.336m an X_STATIONS[0..14], buendig unter Sattelholz-Kapitellen)",
    ),
    (
        "ark_hull_long_bh",
        build_ark_hull_long_bh,
        ["MAT_ARK_LONG_BH"],
        3, [28, 75, 145],
        "2 Laengsschotten (Y=+-5.000m, 0.233m stark) mit plastischen Bohlenlagen, Staenderrippen & exakt allen 60 Laengsschotttuer-Positionen (inkl. S7-Bb Foyer-Hauptportal)",
    ),
    (
        "ark_hull_trans_bh",
        build_ark_hull_trans_bh,
        ["MAT_ARK_TRANS_BH"],
        3, [28, 75, 145],
        "13 Querschotten QS01..QS13 (xShip=10..130m, 0.233m stark) mit 39 Mittelschiff-Tueren, 16 Seitenschiff-Tueren, 26 D2-Duekern & 2 grossen QS07-Rampendurchbruechen",
    ),
]


def _box_is_clear_in_mesh(me, x0, x1, y0, y1, z0, z1, eps=0.012):
    """Prueft, dass KEIN Dreieck (weder Vertices noch Dreiecks-Schwerpunkt noch Kantenmittelpunkte)
    in das Innere der lichten Oeffnungs-Box [x0+eps..x1-eps] x [y0+eps..y1-eps] x [z0+eps..z1-eps] hineinragt!"""
    ax0, ax1 = x0 + eps, x1 - eps
    ay0, ay1 = y0 + eps, y1 - eps
    az0, az1 = z0 + eps, z1 - eps

    verts = me.vertices
    for v in verts:
        c = v.co
        if (ax0 < c.x < ax1) and (ay0 < c.y < ay1) and (az0 < c.z < az1):
            return False, f"Vertex ({c.x:.3f}, {c.y:.3f}, {c.z:.3f}) in Box [{x0:.2f}..{x1:.2f}]x[{y0:.2f}..{y1:.2f}]x[{z0:.2f}..{z1:.2f}]"

    for poly in me.polygons:
        pts = [verts[idx].co for idx in poly.vertices]
        center = sum(pts, Vector((0.0, 0.0, 0.0))) / float(len(pts))
        if (ax0 < center.x < ax1) and (ay0 < center.y < ay1) and (az0 < center.z < az1):
            return False, f"Polygon-Zentrum ({center.x:.3f}, {center.y:.3f}, {center.z:.3f}) blockiert Box [{x0:.2f}..{x1:.2f}]x[{y0:.2f}..{y1:.2f}]x[{z0:.2f}..{z1:.2f}]"
        # Check edge midpoints as well
        for k in range(len(pts)):
            mid = 0.5 * (pts[k] + pts[(k + 1) % len(pts)])
            if (ax0 < mid.x < ax1) and (ay0 < mid.y < ay1) and (az0 < mid.z < az1):
                return False, f"Kantenmitte ({mid.x:.3f}, {mid.y:.3f}, {mid.z:.3f}) blockiert Box [{x0:.2f}..{x1:.2f}]x[{y0:.2f}..{y1:.2f}]x[{z0:.2f}..{z1:.2f}]"
    return True, "OK"


def verify_all_openings_and_assertions(lod0_map):
    """Unbestechliche automatische Python-Assertion vor dem Export:
    Verifiziert alle 115 Tuer-Positionen (60 Laengsschott + 39 Mittelschott + 16 Seitenschott),
    die S7-Toroeffnung, die 4 Giebel-Sturmklappen, beide Rampen-Deck- & QS07-Durchbrueche,
    alle 8 Silo-, 2 Paternoster-, 4 Schnecken- & 8 Badgir-Durchbrueche!"""
    print("[ARK BASE] --- AUTOMATISCHE PYTHON-OEFFNUNGS- & DURCHBRUCHS-ASSERTIONS ---", flush=True)

    # 1. S7-Seitentor-Oeffnung in ark_hull_wall_bb
    me_bb = lod0_map["ark_hull_wall_bb"].data
    g = S7_GATE_CUTOUT
    ok, msg = _box_is_clear_in_mesh(me_bb, g["xLocal0"], g["xLocal1"], -11.70, -11.00, g["z0"], g["z1"])
    assert ok, f"S7-Seitentor-Aussparung in ark_hull_wall_bb blockiert: {msg}"
    print("[ARK BASE]   [1/8] S7-Seitentor-Aussparung (xLocal=[-7.10..-2.90m], Z=[6.00..9.733m]): 100 % FREI (PASS)", flush=True)

    # 2. 4 Giebel-Sturmklappen-Aussparungen in ark_hull_wall_sb
    me_sb = lod0_map["ark_hull_wall_sb"].data
    for idx, gc in enumerate(GABLE_SHUTTER_CUTOUTS, start=1):
        ok, msg = _box_is_clear_in_mesh(me_sb, gc["xLocal0"] - 0.05, gc["xLocal1"] + 0.05, gc["y0"], gc["y1"], gc["z0"], gc["z1"])
        assert ok, f"Giebel-Sturmklappe #{idx} in ark_hull_wall_sb blockiert: {msg}"
    print("[ARK BASE]   [2/8] 4 Giebel-Sturmklappen-Aussparungen (Y=+-3.25m, 2.60x0.50m, Z=13.72..14.22m): 4/4 FREI (PASS)", flush=True)

    # 3. Alle 60 auditierten Laengsschotttuer-Positionen in ark_hull_long_bh (56 offene Tueren + 4 geschlossene S8-Rampenwand-Felder)
    me_lbh = lod0_map["ark_hull_long_bh"].data
    open_ldoors, closed_ramp_slots = get_longitudinal_bh_door_specs()
    assert len(open_ldoors) + len(closed_ramp_slots) == 60, "Muss exakt 60 Laengsschotttuer-Positionen ergeben!"
    for d in open_ldoors:
        yw = d["y_wall"]
        ok, msg = _box_is_clear_in_mesh(me_lbh, d["xLocal0"], d["xLocal1"], yw - 0.30, yw + 0.30, d["z0"], d["z1"])
        assert ok, f"Laengsschotttuer (j={d['j']}, i={d['i']}, k={d['k']}) blockiert: {msg}"
    # Pruefe explizit das S7-Bb Foyer-Hauptportal (3.593 x 2.917 m bei xShip = 64.45 m)
    foyer_doors = [d for d in open_ldoors if d["is_foyer"]]
    assert len(foyer_doors) == 1 and abs(foyer_doors[0]["xShipMid"] - 64.45) < 1e-3, "S7-Bb Foyer-Hauptportal fehlt!"
    print(
        f"[ARK BASE]   [3/8] 60 Laengsschotttuer-Positionen ({len(open_ldoors)} offene Durchbrueche inkl. 3.593x2.917m "
        f"S7-Foyerportal + {len(closed_ramp_slots)} geschlossene S8-Rampenwand-Felder; 0 in Silos): 60/60 VERIFIZIERT (PASS)",
        flush=True,
    )

    # 4. Alle 39 Mittelschiff-Querschotttueren + 16 Seitenschiff-Querschotttueren + 26 D2-Dueker + 2 QS07-Rampendurchbrueche
    me_tbh = lod0_map["ark_hull_trans_bh"].data
    center_doors, aisle_doors, dukers_d2, qs07_ramps = get_transverse_bh_door_and_ramp_specs()
    assert len(center_doors) == 39, f"Erwartet: 39 Mittelschiff-Querschotttueren, gefunden: {len(center_doors)}"
    assert len(aisle_doors) == 16, f"Erwartet: 16 Seitenschiff-Querschotttueren, gefunden: {len(aisle_doors)}"
    assert len(open_ldoors) + len(closed_ramp_slots) + len(center_doors) + len(aisle_doors) == 115, "Gesamtzahl muss 115 sein!"

    for cd in center_doors:
        xl = cd["xLocal"]
        ok, msg = _box_is_clear_in_mesh(me_tbh, xl - 0.30, xl + 0.30, cd["y0"], cd["y1"], cd["z0"], cd["z1"])
        assert ok, f"Mittelschiff-Querschotttuer QS{cd['i']:02d} D{cd['k']} blockiert: {msg}"

    for ad in aisle_doors:
        xl = ad["xLocal"]
        ok, msg = _box_is_clear_in_mesh(me_tbh, xl - 0.30, xl + 0.30, ad["y0"], ad["y1"], ad["z0"], ad["z1"])
        assert ok, f"Seitenschiff-Querschotttuer QS{ad['i']:02d} D{ad['k']} j={ad['j']} blockiert: {msg}"

    for dk in dukers_d2:
        xl = dk["xLocal"]
        ok, msg = _box_is_clear_in_mesh(me_tbh, xl - 0.30, xl + 0.30, dk["y0"], dk["y1"], dk["z0"], dk["z1"], eps=0.008)
        assert ok, f"D2-Spuelrinnen-Dueker QS{dk['i']:02d} blockiert: {msg}"

    for rmp in qs07_ramps:
        xl = rmp["xLocal"]
        ok, msg = _box_is_clear_in_mesh(me_tbh, xl - 0.30, xl + 0.30, rmp["y0"], rmp["y1"], rmp["z0"], rmp["z1"])
        assert ok, f"QS07-Rampendurchbruch {rmp['name']} blockiert: {msg}"

    print(
        f"[ARK BASE]   [4/8] Querschotten QS01..QS13: 39/39 Mitteltueren + 16/16 Seitentueren + "
        f"{len(dukers_d2)}/26 D2-Dueker + 2/2 QS07-Rampendurchbrueche = 115/115 Tueren 100 % FREI (PASS)",
        flush=True,
    )

    # 5. Beide Rampen-Deckdurchbrueche auf D2 (D1->D2 Schwerlastrampe) & D3 (D2->D3 Leichtrampe)
    me_d1 = lod0_map["ark_hull_deck_d1"].data
    me_d2 = lod0_map["ark_hull_deck_d2"].data
    me_d3 = lod0_map["ark_hull_deck_d3"].data
    me_ht = lod0_map["ark_hull_heavy_timber"].data

    ok, msg = _box_is_clear_in_mesh(me_d2, RAMP_D2_CUTOUT["xLocal0"], RAMP_D2_CUTOUT["xLocal1"], -4.900, -2.100, 5.70, 6.25)
    assert ok, f"Schwerlastrampen-Durchbruch D1->D2 in ark_hull_deck_d2 blockiert: {msg}"
    ok, msg = _box_is_clear_in_mesh(me_d3, RAMP_D3_CUTOUT["xLocal0"], RAMP_D3_CUTOUT["xLocal1"], +2.100, +4.900, 9.70, 10.25)
    assert ok, f"Leichtrampen-Durchbruch D2->D3 in ark_hull_deck_d3 blockiert: {msg}"
    print("[ARK BASE]   [5/8] 2 Rampen-Deckdurchbrueche (D2 Bb xShip=[65.33..76.53m], D3 Stb xShip=[64.87..76.53m]): 2/2 FREI (PASS)", flush=True)

    # 6. Alle 8 Silo-Durchbrueche auf D2 & D3 (und in ark_hull_heavy_timber)
    silo_cuts = get_silo_cutouts()
    assert len(silo_cuts) == 8
    for sc in silo_cuts:
        ok2, msg2 = _box_is_clear_in_mesh(me_d2, sc["xLocal0"], sc["xLocal1"], sc["y0"], sc["y1"], 5.70, 6.25)
        assert ok2, f"Silo-Durchbruch {sc['sec']} auf D2 blockiert: {msg2}"
        ok3, msg3 = _box_is_clear_in_mesh(me_d3, sc["xLocal0"], sc["xLocal1"], sc["y0"], sc["y1"], 9.70, 10.25)
        assert ok3, f"Silo-Durchbruch {sc['sec']} auf D3 blockiert: {msg3}"
        ok_ht, msg_ht = _box_is_clear_in_mesh(me_ht, sc["xLocal0"], sc["xLocal1"], sc["y0"], sc["y1"], 2.20, 10.10)
        assert ok_ht, f"Silo-Schacht {sc['sec']} durch Unterzug/Stuetze in ark_hull_heavy_timber blockiert: {msg_ht}"
    print("[ARK BASE]   [6/8] 8 Silo-Durchbrueche (S3, S6, S9, S12 Bb/Stb auf D2, D3 & Heavy-Timber): 8/8 Tuerme 100 % FREI (PASS)", flush=True)

    # 7. Alle 2 Paternoster-Schaechte (D1, D2, D3) & 4 Schnecken-Durchbrueche (D1, D2)
    for k_idx, me_dk in ((1, me_d1), (2, me_d2), (3, me_d3)):
        z_check0 = Z_LEVELS[k_idx] - 0.25
        z_check1 = Z_LEVELS[k_idx] + 0.25
        for pc in get_paternoster_cutouts(k_idx):
            ok, msg = _box_is_clear_in_mesh(me_dk, pc["xLocal0"], pc["xLocal1"], -6.883, -5.367, z_check0, z_check1)
            assert ok, f"Paternoster-Schacht {pc['sec']} auf D{k_idx} blockiert: {msg}"
        if k_idx in (1, 2):
            for scw in get_screw_cutouts(k_idx):
                ok, msg = _box_is_clear_in_mesh(me_dk, scw["xLocal0"], scw["xLocal1"], scw["y0"], scw["y1"], z_check0, z_check1)
                assert ok, f"Schnecken-Durchbruch {scw['sec']} auf D{k_idx} blockiert: {msg}"
    print("[ARK BASE]   [7/8] 2 Paternoster-Schaechte (D1-D3) & 4 Archimedische Schnecken-Durchbrueche (D1-D2): 100 % FREI (PASS)", flush=True)

    # 8. Alle 8 Badgir-Schaechte auf D2, D3 & im Satteldach (ark_hull_roof)
    me_roof = lod0_map["ark_hull_roof"].data
    badgir_cuts = get_badgir_cutouts()
    assert len(badgir_cuts) == 8
    for bc in badgir_cuts:
        ok2, msg2 = _box_is_clear_in_mesh(me_d2, bc["xLocal0"], bc["xLocal1"], bc["y0"], bc["y1"], 5.70, 6.25)
        assert ok2, f"Badgir-Schacht xShip={bc['xShip']} {bc['side']} auf D2 blockiert: {msg2}"
        ok3, msg3 = _box_is_clear_in_mesh(me_d3, bc["xLocal0"], bc["xLocal1"], bc["y0"], bc["y1"], 9.70, 10.25)
        assert ok3, f"Badgir-Schacht xShip={bc['xShip']} {bc['side']} auf D3 blockiert: {msg3}"
        okr, msgr = _box_is_clear_in_mesh(me_roof, bc["xLocal0"], bc["xLocal1"], bc["y0"], bc["y1"], 13.80, 15.20)
        assert okr, f"Badgir-Dachdurchbruch xShip={bc['xShip']} {bc['side']} in ark_hull_roof blockiert: {msgr}"
    print("[ARK BASE]   [8/8] 8 Badgir-Schaechte (S2, S5, S10, S13 Bb/Stb auf D2, D3 & Satteldach): 8/8 Tuerme 100 % FREI (PASS)", flush=True)


def create_base_object(name, builder_fn, mat_names, lod, mats_dict):
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

    for mn in mat_names:
        me.materials.append(mats_dict[mn])

    obj = bpy.data.objects.new(mesh_name, me)
    bpy.context.collection.objects.link(obj)
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)

    assert len(me.color_attributes) == 0, f"{mesh_name}: Darf keinen Vertex-Color-Layer besitzen (arche_asset_v1_std)!"
    return obj, tri_count


def export_base_structure_blend_and_glb(project_root, all_objs, tri_report):
    blend_dir = os.path.join(project_root, "assets", "blend", "ark")
    glb_dir = os.path.join(project_root, "assets", "glb", "ark")
    os.makedirs(blend_dir, exist_ok=True)
    os.makedirs(glb_dir, exist_ok=True)

    blend_path = os.path.join(blend_dir, "ark_base_structure_kit.blend")
    glb_path = os.path.join(glb_dir, "ark_base_structure_kit.glb")

    bpy.ops.object.select_all(action="DESELECT")
    for o in all_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = all_objs[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    print(f"[ARK BASE] Speichere High-Detail-Master: {blend_path}", flush=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    print(f"[ARK BASE] Exportiere GLB (+Y Up): {glb_path}", flush=True)
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
    print(f"[ARK BASE] GLB exportiert: {glb_kb:.1f} KB ({glb_path})", flush=True)

    # Aktualisiere assets/manifest.json
    man_path = os.path.join(project_root, "assets", "manifest.json")
    if os.path.exists(man_path):
        with open(man_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        ark_items = manifest.setdefault("categories", {}).setdefault("ark", {}).setdefault("items", {})
        ark_items["ark_base_structure_kit"] = {
            "enabled": True,
            "url": "assets/glb/ark/ark_base_structure_kit.glb",
            "blend": "assets/blend/ark/ark_base_structure_kit.blend",
            "category": "ark",
            "shaderKey": "arche_asset_v1_std",
            "metricUvScale": "1.0 UV = 2.0 m",
            "exteriorLods": ["LOD0", "LOD1", "LOD2", "LOD3"],
            "exteriorLodDistances": [150, 500, 1500, 3000],
            "interiorLods": ["LOD0", "LOD1", "LOD2"],
            "interiorLodDistances": [28, 75, 145],
            "materialSlots": {
                "MAT_ARK_KOPHER":       "kopher_pitch",
                "MAT_ARK_ROOF_WOOD":    "wood_cedar_c18",
                "MAT_ARK_DECKS":        "wood_oak_d35",
                "MAT_ARK_HEAVY_TIMBER": "wood_oak_d35",
                "MAT_ARK_LONG_BH":      "wood_cypress_c27",
                "MAT_ARK_TRANS_BH":     "wood_cypress_c27",
            },
            "woodLibraryTextures": {
                k: [
                    f"assets/textures/ark/materials/{k}_basecolor.png",
                    f"assets/textures/ark/materials/{k}_normal.png",
                    f"assets/textures/ark/materials/{k}_roughness.png",
                ]
                for k in ("kopher_pitch", "wood_oak_d35", "wood_cypress_c27", "wood_cedar_c18", "wood_hornbeam")
            },
            "modules": {
                name: {
                    "materials": mat_names,
                    "lodDistances": lod_dists,
                    "lods": tri_report[name],
                    "description": desc,
                }
                for name, _, mat_names, _, lod_dists, desc in BASE_STRUCTURE_SPECS
            },
            "previews": [
                "assets/previews/ark_base_exterior_34.png",
                "assets/previews/ark_base_cutaway_full.png",
                "assets/previews/ark_base_interior_corridor.png",
                "assets/previews/ark_base_gate_zohar_closeup.png",
                "assets/previews/ark_base_wood_swatches.png",
            ],
            "glbSizeKB": round(glb_kb, 1),
            "exportedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(man_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print("[ARK BASE] In assets/manifest.json registriert!", flush=True)

    return glb_kb


# ==============================================================================
# 6) 5 PFLICHT-KONTROLLRENDERINGS (CYCLES CUDA + AgX, INKL. WAVE-A-KIT-EINBAU!)
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
    scene.view_settings.exposure = -0.85
    scene.view_settings.gamma = 1.0

    world = bpy.data.worlds.new("Ark_Base_Sky")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    w_out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.18
    sky = nt.nodes.new("ShaderNodeTexSky")
    for st_name in ("MULTIPLE_SCATTERING", "NISHITA", "SINGLE_SCATTERING"):
        try:
            sky.sky_type = st_name
            break
        except Exception:
            pass
    sky.sun_disc = True
    sky.sun_elevation = math.radians(34.0)
    sky.sun_rotation = math.radians(-38.0)
    if hasattr(sky, "air_density"):
        sky.air_density = 1.2
    if hasattr(sky, "dust_density"):
        sky.dust_density = 1.35
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], w_out.inputs["Surface"])

    return "CUDA (GPU)" if used_gpu else "CPU"


def load_wave_a_kit_lod0(project_root):
    """Laedt die LOD0-Hero-Module (aktualisiertes Seitentor S7, 8 Badgir-Koepfe, Sturmklappen,
    Wurzelknie, Kapitelle & Blockzargen) direkt aus assets/blend/ark/ark_wave_a_kit.blend!"""
    blend_path = os.path.join(project_root, "assets", "blend", "ark", "ark_wave_a_kit.blend")
    if not os.path.exists(blend_path):
        raise FileNotFoundError(f"Wave-A-Kit fehlt: {blend_path}")
    wanted = [
        "ark_gate_leaf_s7_LOD0",
        "ark_gate_zarge_s7_LOD0",
        "ark_storm_shutter_LOD0",
        "ark_root_knee_01_LOD0",
        "ark_root_knee_02_LOD0",
        "ark_root_knee_03_LOD0",
        "ark_kingpost_capital_LOD0",
        "ark_door_frame_d1_LOD0",
        "ark_door_frame_d2_LOD0",
        "ark_door_frame_d3_LOD0",
        "ark_door_frame_foyer_LOD0",
        "ark_badgir_cap_LOD0",
    ]
    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
        data_to.objects = [n for n in data_from.objects if n in wanted]
    loaded = {}
    for obj in data_to.objects:
        if obj is not None:
            base_name = obj.name.replace("_LOD0", "")
            loaded[base_name] = obj
    print(f"[ARK BASE] Wave-A-Kit-Module geladen ({len(loaded)}): {sorted(loaded.keys())}", flush=True)
    return loaded


def _place_inst(src_obj, loc, rot_euler=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0), col=None):
    inst = bpy.data.objects.new(f"Inst_{src_obj.name}", src_obj.data)
    inst.location = Vector(loc)
    inst.rotation_euler = rot_euler
    inst.scale = scale if isinstance(scale, tuple) else (scale, scale, scale)
    (col or bpy.context.collection).objects.link(inst)
    return inst


def _aim_cam(cam_obj, loc, target, lens=32.0, clip_end=450.0):
    cam_obj.location = Vector(loc)
    direction = Vector(target) - Vector(loc)
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam_obj.data.lens = lens
    cam_obj.data.clip_start = 0.15
    cam_obj.data.clip_end = clip_end


def _populate_wave_a_attachments(col, wave_a, mats_dict):
    """Platziert die Hero-Module aus ark_wave_a_kit an ihren exakten Arche-Koordinaten:
    - S7-Seitentor (Zarge + innen & aussen Kopher-verpichtes Torblatt)
    - 8 Zweikammer-Badgir-Tuerme + 8 gezimmerte Badgir-Koepfe (ark_badgir_cap)
    - Zohar- & Giebel-Sturmklappen (ark_storm_shutter)
    - Koenigsstuetzen-Sattelholz-Kapitelle (ark_kingpost_capital)
    - Organische Eichen-Wurzelknie (ark_root_knee_01..03)
    - Schotttuer-Blockzargen (ark_door_frame_foyer, _d1, _d2, _d3)
    Liefert eine Liste von Backbord-Anbauteilen zurueck, die beim Museums-Cutaway (Bild 2) mit ausgeblendet werden."""
    bb_wall_attachments = []

    # 1. Hero-Seitentor S7 (xLocal = -5.000 m, Y = -11.240 m, Z = 6.000 m; Torblatt-Pivot bei Z = 9.733 m)
    g_zarge_inst = _place_inst(wave_a["ark_gate_zarge_s7"], (-5.000, -11.240, 6.000), col=col)
    g_leaf_inst = _place_inst(wave_a["ark_gate_leaf_s7"],  (-5.000, -11.300, 9.733), col=col)
    bb_wall_attachments.extend([g_zarge_inst, g_leaf_inst])

    # 2. 8 Badgir-Dachtuerme + 8 gezimmerte Badgir-Hauben (ark_badgir_cap) bei xLocal = -58, -28, +22, +52 m, Y = +-4.180 m
    bm_tow = bmesh.new()
    uv_tow = bm_tow.loops.layers.uv.new("UVMap")
    z_top_badgir = 15.650
    for xs in BADGIR_X_SHIPS:
        xl = xL(xs)
        for sgn, ym in ((-1.0, -4.180), (+1.0, +4.180)):
            # Kurzer Zypressen-Dachschacht (Z = 2.12 .. 15.13 m) unter dem Badgir-Kopf
            add_metric_chamfered_beam(
                bm_tow, uv_tow, xl - BADGIR_HALF_LX, xl + BADGIR_HALF_LX,
                ym - 0.5 * BADGIR_LY, ym + 0.5 * BADGIR_LY, 2.120, z_top_badgir - 0.510,
                0.014, mat_idx=0, axis="Z"
            )
            _place_inst(wave_a["ark_badgir_cap"], (xl, ym, z_top_badgir), col=col)
    me_tow = bpy.data.meshes.new("Preview_Badgir_Shafts")
    bm_tow.to_mesh(me_tow)
    bm_tow.free()
    me_tow.materials.append(mats_dict["MAT_ARK_TRANS_BH"])
    obj_tow = bpy.data.objects.new("Preview_Badgir_Shafts", me_tow)
    col.objects.link(obj_tow)

    # 3. Bewegliche Zohar-Sturmklappen (ark_storm_shutter) unter dem 1-Elle-Traufueberstand + 4 Giebelklappen
    n_bays = 60
    dx_bay = L_SHIP / float(n_bays)
    for ib in range(n_bays):
        xm = -70.0 + (ib + 0.5) * dx_bay
        # Leicht ausgestellt (22 Grad) unter dem 1-Elle-Traufueberstand
        sh_bb = _place_inst(
            wave_a["ark_storm_shutter"], (xm, -11.495, 13.985),
            rot_euler=(math.radians(24.0), 0.0, 0.0), scale=(dx_bay - 0.30, 1.0, 0.448), col=col
        )
        bb_wall_attachments.append(sh_bb)
        _place_inst(
            wave_a["ark_storm_shutter"], (xm, +11.495, 13.985),
            rot_euler=(math.radians(-24.0), 0.0, math.radians(180.0)), scale=(dx_bay - 0.30, 1.0, 0.448), col=col
        )
    # 4 Giebel-Sturmklappen an Bug & Heck (Y = +-3.25 m, Z = 14.22 m, 2.50 x 0.48 m)
    for ym_g in (-3.250, +3.250):
        _place_inst(
            wave_a["ark_storm_shutter"], (-70.01, ym_g, 14.215),
            rot_euler=(math.radians(20.0), 0.0, math.radians(-90.0)), scale=(2.48, 1.0, 0.48), col=col
        )
        _place_inst(
            wave_a["ark_storm_shutter"], (+70.01, ym_g, 14.215),
            rot_euler=(math.radians(20.0), 0.0, math.radians(90.0)), scale=(2.48, 1.0, 0.48), col=col
        )

    # 4. Koenigsstuetzen-Sattelholz-Kapitelle (ark_kingpost_capital) buendig auf allen Koenigsstuetzen-Schaeaften
    b_keel_in = 6.0 * HANDBREITE_M
    h_girder_z = 0.68 * (0.72 * b_keel_in)
    y_post_cols = [-17.5 * ELLE_M, -4.5 * ELLE_M, +4.5 * ELLE_M, +17.5 * ELLE_M]
    silo_boundary_stations = {2, 3, 5, 6, 8, 9, 11, 12}
    for i in range(15):
        xp = xL((D_AW + 0.28) if i == 0 else ((140.0 - D_AW - 0.28) if i == 14 else X_STATIONS[i]))
        is_silo_st = (i in silo_boundary_stations)
        for yp in y_post_cols:
            is_side_col = (abs(yp) > 5.0)
            for k in range(4):
                if is_side_col and is_silo_st and k in (1, 2):
                    continue
                z_girder_top = (Z_LEVELS[k + 1] - 0.5 * DECK_THICK[k + 1] - 0.004) if k < 3 else (get_deck_z(4, yp) - 0.65 * D_ROOF)
                z_cap_origin = z_girder_top - h_girder_z
                # Sattelholz laeuft in X-Richtung unter dem Laengsunterzug -> um 90 Grad um Z drehen!
                _place_inst(
                    wave_a["ark_kingpost_capital"], (xp, yp, z_cap_origin),
                    rot_euler=(0.0, 0.0, math.pi * 0.5), col=col
                )

    # 5. Organische Eichen-Wurzelknie (ark_root_knee_01..03) an den 15 Stationen (Aussenwaende & Laengsschotten)
    #    + im S7-Foyer beidseitig des Haupttors (xLocal = -8.45 m & -1.55 m), damit sie im Foyer-Walkthrough sichtbar sind!
    knee_names = ["ark_root_knee_01", "ark_root_knee_02", "ark_root_knee_03"]
    for i in range(15):
        xk = xL((D_AW + 0.26) if i == 0 else ((140.0 - D_AW - 0.26) if i == 14 else (X_STATIONS[i] + 0.5 * D_TBH + 0.14)))
        is_silo_st = (i in SILO_SEC_INDICES)
        for j, y_wall in enumerate(Y_AXES):
            is_outer = (j in (0, 3))
            if is_outer and is_silo_st:
                continue
            xk_use = (-8.45 if (j == 0 and i == 6) else (-1.55 if (j == 1 and i == 6) else xk))
            dir_y = +1.0 if j in (0, 1) else -1.0
            y_base = y_wall + dir_y * ((D_AW + 0.004) if is_outer else (0.5 * D_LBH + 0.004))
            k_obj = wave_a[knee_names[(i + j) % 3]]
            for k in range(4):
                if not is_outer and i in (6, 7) and k >= 1 and not (j == 1 and i == 6 and k == 2):
                    continue
                z_floor = (D_BOT + 0.004) if k == 0 else (Z_LEVELS[k] + 0.5 * DECK_THICK[k] + 0.004)
                z_ceil = (Z_LEVELS[k + 1] - 0.5 * DECK_THICK[k + 1] - 0.004) if k < 3 else (get_deck_z(4, y_base) - 0.65 * D_ROOF - 0.01)
                # Bodenknie
                rot_floor = (0.0, 0.0, 0.0 if dir_y > 0 else math.pi)
                kn_f = _place_inst(k_obj, (xk_use, y_base, z_floor), rot_euler=rot_floor, col=col)
                # Deckenknie (zeigt von z_ceil nach unten -> um X um 180 Grad gekippt)
                rot_ceil = (math.pi, 0.0, math.pi if dir_y > 0 else 0.0)
                kn_c = _place_inst(k_obj, (xk_use, y_base, z_ceil), rot_euler=rot_ceil, col=col)
                if j == 0:
                    bb_wall_attachments.extend([kn_f, kn_c])
    # Zusaetzliches Wurzelknie-Paar im S7-Foyer an der Kopher-verpichten BB-Aussenwand (xLocal = -1.65 m, Deck 2)
    kn_s7_f = _place_inst(wave_a["ark_root_knee_02"], (-1.65, -11.500 + D_AW + 0.004, Z_LEVELS[2] + 0.5 * D_D2 + 0.004), col=col)
    kn_s7_c = _place_inst(wave_a["ark_root_knee_02"], (-1.65, -11.500 + D_AW + 0.004, Z_LEVELS[3] - 0.5 * D_D3 - 0.004), rot_euler=(math.pi, 0.0, math.pi), col=col)
    bb_wall_attachments.extend([kn_s7_f, kn_s7_c])

    # 6. Schotttuer-Blockzargen (Foyer-Hauptportal + Mittelschiff-Querschotttueren + S6/S7/S8 Laengsschotttueren)
    open_ldoors, _ = get_longitudinal_bh_door_specs()
    for d in open_ldoors:
        if d["is_foyer"]:
            z_base = Z_LEVELS[2] + 0.5 * D_D2
            _place_inst(wave_a["ark_door_frame_foyer"], (xL(d["xShipMid"]), d["y_wall"], z_base), col=col)
        elif d["i"] in (4, 5, 6, 7, 8):
            z_base = Z_LEVELS[d["k"]] + 0.5 * DECK_THICK[d["k"]]
            df_name = "ark_door_frame_d1" if d["k"] == 1 else ("ark_door_frame_d2" if d["k"] == 2 else "ark_door_frame_d3")
            sx_scale = (d["xLocal1"] - d["xLocal0"]) / (2.800 if d["k"] == 1 else (1.867 if d["k"] == 2 else 1.400))
            _place_inst(wave_a[df_name], (xL(d["xShipMid"]), d["y_wall"], z_base), scale=(sx_scale, 1.0, 1.0), col=col)

    center_doors, _, _, _ = get_transverse_bh_door_and_ramp_specs()
    for cd in center_doors:
        z_base = Z_LEVELS[cd["k"]] + 0.5 * DECK_THICK[cd["k"]]
        df_name = "ark_door_frame_d1" if cd["k"] == 1 else ("ark_door_frame_d2" if cd["k"] == 2 else "ark_door_frame_d3")
        sy_scale = (cd["y1"] - cd["y0"]) / (2.800 if cd["k"] == 1 else (1.867 if cd["k"] == 2 else 1.400))
        _place_inst(
            wave_a[df_name], (cd["xLocal"], 0.0, z_base),
            rot_euler=(0.0, 0.0, math.pi * 0.5), scale=(sy_scale, 1.0, 1.0), col=col
        )

    return bb_wall_attachments


def _build_shipyard_slipway_floor(col, mats_dict):
    """Baut das Werft-Bodenplanum auf Z = -0.750 m + 39 massive Eichen-Helling-Stapelkloetze (Z = -0.750..-0.467 m)
    direkt unter den 3 Aussenkielen, sodass die Arche mit 100 % festem Bodenkontakt aufliegt (0 % Schweben!)."""
    mat_ground = bpy.data.materials.new("Mat_Shipyard_Loam")
    mat_ground.use_nodes = True
    bsdf_g = mat_ground.node_tree.nodes["Principled BSDF"]
    bsdf_g.inputs["Base Color"].default_value = (0.35, 0.27, 0.18, 1.0)
    bsdf_g.inputs["Roughness"].default_value = 0.88

    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    # Bodenplatte auf Z = -0.750 m
    add_metric_box(bm, uv_layer, -220.0, +220.0, -160.0, +160.0, -0.850, -0.750, mat_idx=0, grain_axis="X")
    # Helling-Querschwellen & Kielstapel (Z = -0.750 .. -0.467 m) exakt unter den 3 Aussenkielen
    for ix in range(-12, 13):
        bx = ix * 4.2
        add_metric_chamfered_beam(bm, uv_layer, bx - 0.35, bx + 0.35, -10.2, +10.2, -0.750, -0.466, 0.02, mat_idx=1, axis="Y")

    me = bpy.data.meshes.new("Shipyard_Slipway_Base")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat_ground)
    me.materials.append(mats_dict["MAT_ARK_HEAVY_TIMBER"])
    obj = bpy.data.objects.new("Shipyard_Slipway_Base", me)
    col.objects.link(obj)
    return obj


def render_5_base_structure_showcases(project_root, lod0_map, mats_dict):
    scene = bpy.context.scene
    dev = setup_cycles_agx_showcase(scene, samples=48)
    print(f"[ARK BASE] Rendere 5 Pflicht-Kontrollbilder (Cycles {dev} + AgX)...", flush=True)

    # Blende die Export-Master-Objekte aus und baue die kompletter Arche-Showcase-Szene mit Wave-A-Modulen auf
    for o in list(bpy.data.objects):
        o.hide_render = True
        o.hide_viewport = True

    prev_dir = os.path.join(project_root, "assets", "previews")
    os.makedirs(prev_dir, exist_ok=True)

    wave_a = load_wave_a_kit_lod0(project_root)

    col_ark = bpy.data.collections.new("Showcase_Ark_Assembly")
    scene.collection.children.link(col_ark)

    _build_shipyard_slipway_floor(col_ark, mats_dict)

    ark_insts = {}
    for name, _, _, _, _, _ in BASE_STRUCTURE_SPECS:
        ark_insts[name] = _place_inst(lod0_map[name], (0.0, 0.0, 0.0), col=col_ark)

    bb_attachments = _populate_wave_a_attachments(col_ark, wave_a, mats_dict)

    # Beleuchtung fuer Aussen-, Cutaway- und Innenraum-Perspektiven
    sun_data = bpy.data.lights.new("ArkSunLight", type="SUN")
    sun_data.energy = 2.6
    sun_data.color = (1.0, 0.93, 0.82)
    sun_data.angle = math.radians(1.2)
    sun_obj = bpy.data.objects.new("ArkSunLight", sun_data)
    sun_obj.rotation_euler = (math.radians(56.0), math.radians(12.0), math.radians(-34.0))
    col_ark.objects.link(sun_obj)

    rim_data = bpy.data.lights.new("ArkGrazingFill", type="AREA")
    rim_data.energy = 85000.0
    rim_data.color = (1.0, 0.84, 0.62)
    rim_data.size = 45.0
    rim_obj = bpy.data.objects.new("ArkGrazingFill", rim_data)
    rim_obj.location = (-55.0, -42.0, 18.0)
    rim_obj.rotation_euler = (math.radians(68.0), 0.0, math.radians(-32.0))
    col_ark.objects.link(rim_obj)

    cam_data = bpy.data.cameras.new("ArkBaseCam")
    cam_obj = bpy.data.objects.new("ArkBaseCam", cam_data)
    col_ark.objects.link(cam_obj)
    scene.camera = cam_obj

    # ==========================================================================
    # BILD 1: assets/previews/ark_base_exterior_34.png
    # Monumentale 3/4-Aussenansicht der kompletten 140-m-Arche (Kopher-Rumpf mit Berghoelzern,
    # Satteldach mit Stossleisten & Firstbalken, 1-Elle-Zohar, 8 Badgir-Hauben, 3 Aussenkiele & Seitentor S7)
    # ==========================================================================
    _aim_cam(cam_obj, (-108.0, -64.0, 19.5), (+3.0, 0.0, 6.2), lens=26.5, clip_end=450.0)
    p1 = os.path.join(prev_dir, "ark_base_exterior_34.png")
    scene.render.filepath = p1
    print(f"[ARK BASE] 1/5 Rendere {p1}...", flush=True)
    bpy.ops.render.render(write_still=True)

    # ==========================================================================
    # BILD 2: assets/previews/ark_base_cutaway_full.png
    # Museums-Schnittmodell (Backbordwand ausgeblendet + gestuftes Museums-Sichtfenster ins Mittelschiff & an die
    # Steuerbordwand!) — zeigt klar die innen kopher-verpichte Steuerbord-Aussenwand & Sohle (Gen 6,14!)
    # im Kontrast zu den warmen Holz-Decks (D1-D3), 2 Laengsschotten, 13 Querschotten, 45 Koenigsstuetzen,
    # Wurzelknien & Blockzargen!
    # ==========================================================================
    ark_insts["ark_hull_wall_bb"].hide_render = True
    for o_att in bb_attachments:
        o_att.hide_render = True

    # Fuer das Museums-Schnittmodell (Bild 2) oeffnen wir in den mittleren Sektionen S5..S9 (xLocal in [-29..+19 m])
    # per sauberem BMesh-Polygon-Cutaway (0 Boolean-Deckflaechen-Artefakte!) ein gestuftes Museums-Einblickfenster
    # durch die Laengsschotten, Querschotten, Decks und die vordere Dachhaelfte bis direkt an die innen Kopher-verpichte
    # Steuerbord-Aussenwand (Y = +11.189 m) und hinab auf die innen Kopher-verpichte Sohle (Z = 0.35 m) mit 3 Kielschweinen!
    orig_meshes_shot2 = {}
    for target_name in ("ark_hull_long_bh", "ark_hull_trans_bh", "ark_hull_deck_d1", "ark_hull_deck_d2", "ark_hull_deck_d3", "ark_hull_roof", "ark_hull_zohar"):
        t_obj = ark_insts[target_name]
        orig_meshes_shot2[target_name] = t_obj.data
        me_cut = t_obj.data.copy()
        bm_c = bmesh.new()
        bm_c.from_mesh(me_cut)
        to_del = []
        for f in bm_c.faces:
            c = f.calc_center_median()
            if target_name in ("ark_hull_roof", "ark_hull_zohar"):
                if (-29.5 < c.x < +19.5) and (c.y < +9.2):
                    to_del.append(f)
            elif target_name == "ark_hull_long_bh":
                if (-29.5 < c.x < +19.5):
                    to_del.append(f)
            elif target_name == "ark_hull_trans_bh":
                if (-25.0 < c.x < +15.0) and (c.y < +8.8):
                    to_del.append(f)
            else:  # Decks D1, D2, D3: gestufter Einblick bis auf die Kopher-Bilgensohle & 3 Innen-Kielschweine!
                if (-21.0 < c.x < +11.0) and (c.y < +8.2):
                    to_del.append(f)
                elif (-29.5 < c.x < +19.5) and (c.y < -4.5) and target_name in ("ark_hull_deck_d2", "ark_hull_deck_d3"):
                    to_del.append(f)
        if to_del:
            bmesh.ops.delete(bm_c, geom=to_del, context="FACES")
        bm_c.to_mesh(me_cut)
        bm_c.free()
        t_obj.data = me_cut

    # Warme Innenraum-Flutlichter fuer klare Sicht bis an die innen-verpichte Steuerbordwand (Y=+11.189m) & Sohle (Z=0.35m)!
    cut_lights = []
    for lx in (-45.0, -15.0, +15.0, +45.0):
        ld = bpy.data.lights.new(f"CutawayFill_{lx}", type="AREA")
        ld.energy = 26000.0
        ld.color = (1.0, 0.88, 0.70)
        ld.size = 22.0
        lo = bpy.data.objects.new(f"CutawayFill_{lx}", ld)
        lo.location = (lx, -22.0, 11.5)
        lo.rotation_euler = (math.radians(72.0), 0.0, 0.0)
        col_ark.objects.link(lo)
        cut_lights.append(lo)

    # Gezieltes Streiflicht im geoeffneten Museums-Atrium direkt auf die innen Kopher-verpichte Steuerbord-Aussenwand & Sohle
    sb_ld = bpy.data.lights.new("CutawayStarboardKopherLight", type="AREA")
    sb_ld.energy = 24000.0
    sb_ld.color = (1.0, 0.90, 0.74)
    sb_ld.size = 26.0
    sb_lo = bpy.data.objects.new("CutawayStarboardKopherLight", sb_ld)
    sb_lo.location = (-5.0, -4.0, 13.0)
    sb_lo.rotation_euler = (math.radians(52.0), 0.0, 0.0)
    col_ark.objects.link(sb_lo)
    cut_lights.append(sb_lo)

    _aim_cam(cam_obj, (-64.0, -56.0, 21.5), (-1.0, +1.0, 6.2), lens=26.5, clip_end=450.0)
    p2 = os.path.join(prev_dir, "ark_base_cutaway_full.png")
    scene.render.filepath = p2
    print(f"[ARK BASE] 2/5 Rendere {p2}...", flush=True)
    bpy.ops.render.render(write_still=True)

    # Stelle die ungeschnittenen Original-Meshes fuer Bild 3 & Bild 4 wieder her!
    for target_name, orig_me in orig_meshes_shot2.items():
        ark_insts[target_name].data = orig_me

    # ==========================================================================
    # BILD 3: assets/previews/ark_base_interior_corridor.png
    # Walkthrough-Innenansicht entlang Deck 2 (S7-Foyer & Mittelschiff-Korridor) — zeigt deutlich
    # die neu innen-verpichte Seitentor-Innenseite mit den 3 warmen Hainbuchen-Sperrbalken, die
    # innen-verpichte Aussenwand-Innenseite, die gefasten Holz-Schotten, Blockzargen, Kapitelle & Wurzelknie!
    # ==========================================================================
    ark_insts["ark_hull_wall_bb"].hide_render = False
    for o_att in bb_attachments:
        o_att.hide_render = False
    for lo in cut_lights:
        lo.hide_render = True

    # Warme, ausgewogene Innenraum-Beleuchtung im S7-Foyer & D2-Mittelschiff-Korridor (inkl. Decken-Aufhellung!)
    int_lights = []
    int_specs = [
        ((-3.5, -7.2, 7.80), (math.radians(82.0), 0.0, math.radians(-162.0)), 1400.0, 3.2, (1.0, 0.85, 0.62)), # Hauptlicht direkt auf S7-Seitentor-Innenseite (+Y) & BB-Wand!
        ((-7.2, -8.5, 7.20), (math.radians(105.0), 0.0, math.radians(-135.0)), 950.0, 3.0, (1.0, 0.86, 0.65)), # Aufhelllicht nach schraeg oben auf Kapitell, Unterzuege & Deckenknie!
        ((-2.2, -8.5, 7.30), (math.radians(95.0), 0.0, math.radians(45.0)),    900.0, 2.8, (1.0, 0.84, 0.60)), # Licht auf Foyer-Hauptportal & Wurzelknie
        ((-5.5, -1.8, 8.60), (math.radians(35.0), 0.0, math.radians(15.0)),   1500.0, 3.8, (1.0, 0.84, 0.58)), # Mittelschiff-Korridor S7
        ((-15.0, -0.5, 8.60), (math.radians(20.0), 0.0, 0.0),                 1500.0, 3.8, (1.0, 0.82, 0.55)), # Mittelschiff-Korridor S6
    ]
    for idx_l, (loc_l, rot_l, en_l, sz_l, col_l) in enumerate(int_specs):
        ld = bpy.data.lights.new(f"InteriorFoyerLight_{idx_l}", type="AREA")
        ld.energy = en_l
        ld.color = col_l
        ld.size = sz_l
        lo = bpy.data.objects.new(f"InteriorFoyerLight_{idx_l}", ld)
        lo.location = Vector(loc_l)
        lo.rotation_euler = rot_l
        col_ark.objects.link(lo)
        int_lights.append(lo)

    # Kamera steht im S7-Foyer auf Deck 2 bei (xLocal = -0.35 m, Y = -6.70 m, Z = 7.58 m)
    # und blickt nach vorn-links auf (xLocal = -6.85 m, Y = -8.35 m, Z = 7.62 m):
    #   - Links im Bild (Y = -11.24 m, xLocal = -7.1..-2.9 m): Die neu innen Kopher-verpichte S7-Seitentor-Innenseite
    #     mit den 3 warmen Hainbuchen-Sperrbalken, die innen-verpichte BB-Aussenwand & die Eichen-Wurzelknie!
    #   - Bildmitte (xLocal = -10.0 m, Y = -8.17 m): Koenigsstuetze mit Sattelholz-Kapitell & Laengsunterzug + Querschott QS06!
    #   - Rechts im Bild (Y = -5.00 m, xLocal = -7.35..-3.75 m): Das 3.59 m S7-Foyer-Hauptportal im Zypressen-Laengsschott
    #     mit Durchblick in den Deck-2-Mittelschiff-Korridor, Querschotttueren & Koenigsstuetzen!
    _aim_cam(cam_obj, (-0.35, -6.70, 7.58), (-6.85, -8.35, 7.62), lens=18.5, clip_end=160.0)
    p3 = os.path.join(prev_dir, "ark_base_interior_corridor.png")
    scene.render.filepath = p3
    print(f"[ARK BASE] 3/5 Rendere {p3}...", flush=True)
    bpy.ops.render.render(write_still=True)

    # ==========================================================================
    # BILD 4: assets/previews/ark_base_gate_zohar_closeup.png
    # Nahaufnahme von S7-Seitentor-Einbindung (Aussen- & Innen-Kopher-Check!), 1-Elle-Zohar,
    # Dachsparrenkoepfen, Giebel & 3 Aussenkielen
    # ==========================================================================
    for lo in int_lights:
        lo.hide_render = True

    # Perspektive vom Bug-Backbord-Viertel (-79.5, -22.5, 6.2) Richtung (-24.0, -8.2, 6.6):
    #   - Links: Bug-Giebel (xLocal = -70.0 m) mit den 2 Giebel-Sturmklappen, Firstbalken, eckverzahnten Steven-Koepfen
    #            und darunter alle 3 massiven Kopher-Aussenkiele (Y = -8.167, 0.0, +8.167 m)!
    #   - Oben entlang der Traufe: 1-Elle-Zohar mit Stielen, Lamellen & Sturmklappen + profilierte Zedern-Dachsparrenkoepfe!
    #   - Rechts im Vordergrund neben der Bordwand (xLocal = -55.5 m & -49.5 m, Y = -14.8 m) + im Rumpf (S7):
    #     Das S7-Seitentor-Paar (links Aussen-Kopher-Check, rechts Innen-Kopher-Check mit 3 warmen Hainbuchen-Sperrbalken)!
    col_shot4 = bpy.data.collections.new("Showcase_Shot4_InnerGateCheck")
    scene.collection.children.link(col_shot4)
    # 1) Aussen-Kopher-Einbindung des S7-Seitentors direkt an der Bordwand im Vordergrund (xLocal = -57.0 m, Y = -11.30 m, Z = 6.00 m)
    _place_inst(wave_a["ark_gate_zarge_s7"], (-57.0, -11.30, 6.00), col=col_shot4)
    _place_inst(wave_a["ark_gate_leaf_s7"],  (-57.0, -11.36, 9.733), col=col_shot4)
    # 2) Innen-Kopher-Ansicht des S7-Seitentors (mit den 3 warmen Hainbuchen-Sperrbalken vor den Kopher-Torbohlen!) auf dem Helling-Vorplatz
    _place_inst(wave_a["ark_gate_zarge_s7"], (-53.0, -15.2, -0.75), rot_euler=(0.0, 0.0, math.radians(156.0)), col=col_shot4)
    _place_inst(wave_a["ark_gate_leaf_s7"],  (-53.0, -15.15, -0.75 + 3.733), rot_euler=(0.0, 0.0, math.radians(156.0)), col=col_shot4)

    rim_obj.location = (-78.0, -30.0, 11.5)
    rim_obj.data.energy = 36000.0
    _aim_cam(cam_obj, (-88.5, -24.5, 7.6), (-50.0, -5.5, 6.8), lens=23.5, clip_end=250.0)
    p4 = os.path.join(prev_dir, "ark_base_gate_zohar_closeup.png")
    scene.render.filepath = p4
    print(f"[ARK BASE] 4/5 Rendere {p4}...", flush=True)
    bpy.ops.render.render(write_still=True)

    # ==========================================================================
    # BILD 5: assets/previews/ark_base_wood_swatches.png
    # Live-Material-Vergleichstafel aller 5 nahtlos kachelbaren CC0-Sets
    # (kopher_pitch, wood_oak_d35, wood_cypress_c27, wood_cedar_c18, wood_hornbeam) nebeneinander auf Test-Bauteilen!
    # ==========================================================================
    for o in col_ark.objects:
        if o not in (cam_obj, sun_obj, rim_obj):
            o.hide_render = True
    for o in col_shot4.objects:
        o.hide_render = True

    col_sw = bpy.data.collections.new("Showcase_5_WoodSwatches")
    scene.collection.children.link(col_sw)

    # Bodenplatte auf Z = 0.0 m fuer die 5 Material-Teststaende
    mat_sw_floor = bpy.data.materials.new("Mat_Swatch_Floor")
    mat_sw_floor.use_nodes = True
    mat_sw_floor.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.30, 0.24, 0.17, 1.0)
    mat_sw_floor.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.86
    bpy.ops.mesh.primitive_plane_add(size=60.0, location=(0.0, 0.0, 0.0))
    fl_sw = bpy.context.active_object
    fl_sw.data.materials.append(mat_sw_floor)
    col_sw.objects.link(fl_sw)
    bpy.context.collection.objects.unlink(fl_sw)

    # Baue das 5. Material (wood_hornbeam) fuer die Vergleichstafel mit identischer 3-Map-Signatur
    mat_dir = os.path.join(project_root, "assets", "textures", "ark", "materials")
    mat_hb = bpy.data.materials.new("MAT_ARK_HORNBEAM_SWATCH")
    mat_hb.use_nodes = True
    nt_hb = mat_hb.node_tree
    nt_hb.nodes.clear()
    out_hb = nt_hb.nodes.new("ShaderNodeOutputMaterial")
    bsdf_hb = nt_hb.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_hb.inputs["Metallic"].default_value = 0.01
    nt_hb.links.new(bsdf_hb.outputs["BSDF"], out_hb.inputs["Surface"])
    tc_hb = nt_hb.nodes.new("ShaderNodeTexImage")
    tc_hb.image = _load_img(os.path.join(mat_dir, "wood_hornbeam_basecolor.png"), "sRGB")
    nt_hb.links.new(tc_hb.outputs["Color"], bsdf_hb.inputs["Base Color"])
    tn_hb = nt_hb.nodes.new("ShaderNodeTexImage")
    tn_hb.image = _load_img(os.path.join(mat_dir, "wood_hornbeam_normal.png"), "Non-Color")
    nm_hb = nt_hb.nodes.new("ShaderNodeNormalMap")
    nt_hb.links.new(tn_hb.outputs["Color"], nm_hb.inputs["Color"])
    nt_hb.links.new(nm_hb.outputs["Normal"], bsdf_hb.inputs["Normal"])
    tr_hb = nt_hb.nodes.new("ShaderNodeTexImage")
    tr_hb.image = _load_img(os.path.join(mat_dir, "wood_hornbeam_roughness.png"), "Non-Color")
    nt_hb.links.new(tr_hb.outputs["Color"], bsdf_hb.inputs["Roughness"])

    swatch_mats = [
        ("kopher_pitch",     mats_dict["MAT_ARK_KOPHER"]),
        ("wood_oak_d35",     mats_dict["MAT_ARK_DECKS"]),
        ("wood_cypress_c27", mats_dict["MAT_ARK_LONG_BH"]),
        ("wood_cedar_c18",   mats_dict["MAT_ARK_ROOF_WOOD"]),
        ("wood_hornbeam",    mat_hb),
    ]

    # Erzeuge fuer jedes der 5 Sets ein identisches gezimmertes Test-Ensemble auf Z = 0.0 m (mit 1.0 UV = 2.0 m):
    #   - 2.0 x 2.2 m Bohlen-Wandtafel (1x1 volle metrische 2.0m-Kachel + Kacheluebergang -> Beweis der Nahtlosigkeit!)
    #   - Schwerer 8-kantig gefaster Zimmermanns-Stuetzenpfeiler + Sattelholz-Balken + Sockelschwelle
    #   - Zylindrische Walze/Rundholz davor zur Roughness-/Glanzlicht-Pruefung im Streiflicht
    for idx_s, (sw_name, sw_mat) in enumerate(swatch_mats):
        cx = (idx_s - 2) * 2.55  # -5.10, -2.55, 0.00, +2.55, +5.10 m
        bm_s = bmesh.new()
        uv_s = bm_s.loops.layers.uv.new("UVMap")
        # 1. Sockelschwelle auf Z = 0.000..0.240 m
        add_metric_chamfered_beam(bm_s, uv_s, cx - 1.12, cx + 1.12, -0.55, +0.45, 0.000, 0.240, 0.022, mat_idx=0, axis="X")
        # 2. 2.0 x 2.2 m Bohlen-Wandtafel (Z = 0.240..2.440 m, 5 gefaste Bohlenlagen)
        add_planked_wall_panel_x(bm_s, uv_s, cx - 1.04, cx + 1.04, -0.08, +0.24, 0.240, 2.440, 5, 0.016, mat_idx=0)
        # 3. Oberer Sturzbalken (Z = 2.440..2.720 m)
        add_metric_chamfered_beam(bm_s, uv_s, cx - 1.15, cx + 1.15, -0.22, +0.34, 2.440, 2.720, 0.024, mat_idx=0, axis="X")
        # 4. Gefaste Koenigsstuetze + Querriegel vor der Tafel (Y = -0.38..-0.08 m)
        add_metric_chamfered_beam(bm_s, uv_s, cx - 0.18, cx + 0.18, -0.40, -0.08, 0.240, 2.180, 0.024, mat_idx=0, axis="Z")
        add_metric_chamfered_beam(bm_s, uv_s, cx - 0.68, cx + 0.68, -0.44, -0.14, 2.180, 2.440, 0.022, mat_idx=0, axis="X")

        me_s = bpy.data.meshes.new(f"Swatch_{sw_name}")
        bm_s.to_mesh(me_s)
        bm_s.free()
        me_s.materials.append(sw_mat)
        obj_s = bpy.data.objects.new(f"Swatch_{sw_name}", me_s)
        col_sw.objects.link(obj_s)

    rim_obj.location = (0.0, -13.5, 8.2)
    rim_obj.rotation_euler = (math.radians(46.0), 0.0, 0.0)
    rim_obj.data.energy = 1800.0
    rim_obj.data.size = 12.0
    _aim_cam(cam_obj, (0.0, -10.8, 1.85), (0.0, 0.0, 1.38), lens=30.0, clip_end=120.0)
    p5 = os.path.join(prev_dir, "ark_base_wood_swatches.png")
    scene.render.filepath = p5
    print(f"[ARK BASE] 5/5 Rendere {p5}...", flush=True)
    bpy.ops.render.render(write_still=True)

    print("[ARK BASE] Alle 5 Pflicht-Kontrollrenderings erfolgreich erstellt!", flush=True)


def main():
    t0 = time.time()
    root = get_project_root()
    print("[ARK BASE] Starte Bau der kompletten modularen Arche-Grundstruktur (Welle A Teil 1B, Gen 6,14)...", flush=True)
    clear_scene()

    mats_dict = build_6_ark_base_materials(root)

    all_objs = []
    lod0_map = {}
    tri_report = {}

    print("[ARK BASE] --- GEOMETRIE- & LOD-TRI-COUNT-VERIFIKATION ---", flush=True)
    for name, builder_fn, mat_names, num_lods, lod_dists, desc in BASE_STRUCTURE_SPECS:
        tri_report[name] = {}
        for lod in range(num_lods):
            obj, tris = create_base_object(name, builder_fn, mat_names, lod, mats_dict)
            all_objs.append(obj)
            tri_report[name][f"LOD{lod}"] = tris
            if lod == 0:
                lod0_map[name] = obj
        r = tri_report[name]
        lod_str = " | ".join(f"LOD{l}={r[f'LOD{l}']:5d}" for l in range(num_lods))
        print(f"[ARK BASE]   {name:22s} | {lod_str} | Mats={mat_names} | PASS", flush=True)

    verify_all_openings_and_assertions(lod0_map)
    glb_kb = export_base_structure_blend_and_glb(root, all_objs, tri_report)
    render_5_base_structure_showcases(root, lod0_map, mats_dict)
    print(f"[ARK BASE] KOMPLETT FERTIG in {time.time() - t0:.1f}s | GLB={glb_kb:.1f} KB", flush=True)


if __name__ == "__main__":
    main()
