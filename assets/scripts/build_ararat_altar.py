"""
build_ararat_altar.py — Parametrischer Blender-Generator für den zyklopischen Steinaltar am Ararat
================================================================================================
Biblische & archäologische Vorlage: Gen 8,20 / Ex 20,25 (unbehauene Natursteine, ohne Eisenwerkzeug)
Maßstab: 1 BU = 1.0 m | Z-Up | Origin (0,0,0) mittig auf Bodenunterkante (Z = 0.0)
         inkl. 0.25 m tiefem Fundament-Sockel unter Z = 0.0 gegen Hangkanten-Schweben.

Ausführung:
  1. Generieren + Bake-Vorbereitung + .blend speichern:
     blender --background --python assets/scripts/build_ararat_altar.py
  2. Export & PBR-Bake via Master-Exporter:
     blender --background assets/blend/world/ararat_altar_cyclopean.blend --python assets/export_arche_glb.py -- --category world --bake --keep-pivot
  3. 2-Ansichten-Kontrollrender aus finaler .glb:
     blender --background --python assets/scripts/build_ararat_altar.py -- --preview-only
"""

import os
import sys
import math
import random
import bpy
import bmesh
from mathutils import Vector, Euler, noise


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


def enable_cycles(scene, samples=16, use_denoising=False):
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
    if hasattr(scene, "cycles"):
        used_gpu = False
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
        scene.cycles.use_denoising = bool(use_denoising)
        if use_denoising and hasattr(scene.cycles, "denoiser"):
            try:
                scene.cycles.denoiser = "OPENIMAGEDENOISE"
            except Exception:
                pass


def set_float_attr(mesh, name, values):
    """Speichert ein skalares FLOAT-Point-Attribut für Cycles-Baking (wird NICHT als glTF COLOR_0 exportiert)."""
    attr = mesh.attributes.get(name)
    if attr is None:
        attr = mesh.attributes.new(name=name, type="FLOAT", domain="POINT")
    for idx, val in enumerate(values):
        attr.data[idx].value = float(val)


def make_fractured_stone(
    bm,
    center,
    radii,
    rot_euler,
    rng,
    cuts=1,
    cleavage_count=6,
    noise_amp=0.16,
    flat_top=None,
    flat_bot=None,
    stone_type=0.1,
    meta_records=None,
    smooth_faces=False,
):
    """
    Erzeugt einen individuellen unbehauenen Naturstein (Ex 20,25) aus einem unterteilten
    Würfel mit zufälligen Bruch-Spaltflächen (Cleavage Planes) und 3D-Felsrauschen.
    """
    tmp = bmesh.new()
    bmesh.ops.create_cube(tmp, size=2.0)
    if cuts > 0:
        bmesh.ops.subdivide_edges(tmp, edges=list(tmp.edges), cuts=cuts, use_grid_fill=True)

    rx, ry, rz = radii
    planes = []
    for _ in range(cleavage_count):
        n = Vector((rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0), rng.uniform(-0.80, 0.80)))
        if n.length < 1e-4:
            n = Vector((0.0, 0.0, 1.0))
        n.normalize()
        limit = rng.uniform(0.66, 0.94)
        planes.append((n, limit))

    seed_off = Vector((rng.uniform(-50, 50), rng.uniform(-50, 50), rng.uniform(-50, 50)))
    rot_mat = Euler(rot_euler, "XYZ").to_matrix()

    for v in tmp.verts:
        p = v.co.copy()
        for pn, plim in planes:
            d = p.dot(pn)
            if d > plim:
                p -= pn * ((d - plim) * 0.78)

        nv = noise.turbulence_vector(p * 1.35 + seed_off, 3, False)
        p += nv * noise_amp

        taper = 1.0 - 0.10 * max(-0.8, min(0.8, p.z))
        p.x *= rx * taper
        p.y *= ry * taper
        p.z *= rz

        if flat_top is not None and p.z > flat_top:
            p.z = flat_top + (p.z - flat_top) * 0.16
        if flat_bot is not None and p.z < flat_bot:
            p.z = flat_bot + (p.z - flat_bot) * 0.14

        v.co = (rot_mat @ p) + Vector(center)

    vert_map = {}
    new_verts = []
    for v in tmp.verts:
        nv = bm.verts.new(v.co)
        vert_map[v] = nv
        new_verts.append(nv)
        if meta_records is not None:
            d_fire = math.hypot(v.co.x, v.co.y)
            soot = max(0.0, min(1.0, (1.0 - d_fire / 1.15))) * max(0.0, min(1.0, (v.co.z - 0.70) / 0.35))
            moss = max(0.0, min(1.0, (0.40 - v.co.z) / 0.36))
            meta_records[nv] = (stone_type, soot, moss)

    for f in tmp.faces:
        try:
            nf = bm.faces.new([vert_map[v] for v in f.verts])
            nf.smooth = smooth_faces
        except ValueError:
            pass

    tmp.free()
    return new_verts


def build_deck_slab(bm, rng, meta_records):
    """
    Erzeugt die leicht auskragende, organisch gerundet-eckige Opfer-Deckplatte (Z ~ 0.76..1.02 m)
    mit flacher zentraler Glut-Mulde (Z = 0.96 m mittig, 1.02 m am Rand) und rauen Bruchflanken.
    """
    tmp = bmesh.new()
    bmesh.ops.create_cube(tmp, size=2.0)
    bmesh.ops.subdivide_edges(tmp, edges=list(tmp.edges), cuts=6, use_grid_fill=True)

    rx, ry, hz = 1.14, 0.92, 0.13
    seed_off = Vector((13.7, -7.2, 4.9))
    for v in tmp.verts:
        p = v.co.copy()
        # Ecken sanft abrunden -> zyklopischer Natur-Monolith statt Rechteck-Kasten
        r_sq = math.hypot(p.x, p.y)
        if r_sq > 1e-4:
            blend = 0.28 * max(0.0, min(1.0, (r_sq - 0.85) / 0.57))
            p.x *= (1.0 - blend * 0.42)
            p.y *= (1.0 - blend * 0.42)

        ang = math.atan2(p.y, p.x)
        rad_mod = 1.0 + 0.07 * math.sin(ang * 3.0 + 0.6) + 0.05 * math.cos(ang * 5.0 - 0.4)
        n_edge = noise.noise(Vector((p.x * 1.4, p.y * 1.4, p.z * 1.4)) + seed_off)
        x = p.x * rx * rad_mod + n_edge * 0.055
        y = p.y * ry * rad_mod + n_edge * 0.048
        if p.z < 0.0:
            x *= 0.94
            y *= 0.94

        r_norm = math.hypot(x / 0.74, y / 0.60)
        dish = -0.058 * max(0.0, 1.0 - r_norm * r_norm)
        if p.z > 0.2:
            z = 1.015 + dish + n_edge * 0.014
        elif p.z < -0.2:
            z = 0.75 + n_edge * 0.024
        else:
            z = 0.885 + p.z * hz + n_edge * 0.018
        v.co = Vector((x, y, z))

    vert_map = {}
    for v in tmp.verts:
        nv = bm.verts.new(v.co)
        vert_map[v] = nv
        d_fire = math.hypot(v.co.x, v.co.y)
        soot = (max(0.0, min(1.0, 1.0 - d_fire / 0.88)) ** 0.85) * (1.0 if v.co.z > 0.90 else 0.25)
        meta_records[nv] = (0.90, soot, 0.02)

    for f in tmp.faces:
        try:
            nf = bm.faces.new([vert_map[v] for v in f.verts])
            nf.smooth = True
        except ValueError:
            pass
    tmp.free()


def build_foundation_plinth(bm, rng, meta_records):
    """
    0.25 m tiefer Vulkanbasalt-Fundamentsockel unter Z = 0.0 (Z = -0.25 .. +0.06 m),
    damit an leichten Ararat-Hangkanten niemals eine Ecke schwebt.
    """
    n_seg = 14
    bot_verts = []
    top_verts = []
    for i in range(n_seg):
        ang = (i / n_seg) * math.tau
        jit = 1.0 + 0.06 * math.sin(ang * 3.0 + 0.4) + rng.uniform(-0.03, 0.03)
        vb = bm.verts.new((math.cos(ang) * 1.45 * jit, math.sin(ang) * 1.18 * jit, -0.25))
        vt = bm.verts.new((math.cos(ang) * 1.35 * jit, math.sin(ang) * 1.10 * jit, 0.06))
        bot_verts.append(vb)
        top_verts.append(vt)
        meta_records[vb] = (0.04, 0.0, 1.0)
        meta_records[vt] = (0.06, 0.0, 0.85)

    for i in range(n_seg):
        j = (i + 1) % n_seg
        bm.faces.new([bot_verts[i], bot_verts[j], top_verts[j], top_verts[i]]).smooth = False
    bm.faces.new(top_verts).smooth = False
    bm.faces.new(list(reversed(bot_verts))).smooth = False


def build_altar_stone_object(rng):
    """
    Baut das zyklopische Steinmauerwerk (Ex 20,25):
      - Fundament-Sockel (Z = -0.25 .. +0.06 m)
      - Lage 1: 10 massive Basalt-Grundsteine
      - Lage 2: 8 versetzte, dicht schließende Basalt-/Kalkstein-Findlinge
      - Lage 3: 1 auskragende Kalkstein-Opferdeckplatte + 5 Herd-Einfassungssteine
      - Seitliche Trittsteine: 4 gestufte Natursteine (West & Ost)
      = Exakt 28 individuelle Natursteine + Fundament-Sockel!
    """
    bm = bmesh.new()
    meta_records = {}

    build_foundation_plinth(bm, rng, meta_records)

    # Lage 1: 10 zyklopische Vulkanbasalt-Grundblöcke (dicht gefügt, Z = -0.05 .. +0.47 m)
    n1 = 10
    for i in range(n1):
        ang = (i / n1) * math.tau + rng.uniform(-0.05, 0.05)
        rx_pos = 1.06 + rng.uniform(-0.04, 0.04)
        ry_pos = 0.86 + rng.uniform(-0.03, 0.03)
        cx = math.cos(ang) * rx_pos
        cy = math.sin(ang) * ry_pos
        sx = rng.uniform(0.36, 0.45)
        sy = rng.uniform(0.31, 0.39)
        sz = rng.uniform(0.24, 0.28)
        cz = sz * 0.82 - 0.03
        st_type = rng.uniform(0.02, 0.22)
        make_fractured_stone(
            bm,
            center=(cx, cy, cz),
            radii=(sx, sy, sz),
            rot_euler=(rng.uniform(-0.07, 0.07), rng.uniform(-0.07, 0.07), ang + math.pi * 0.5 + rng.uniform(-0.20, 0.20)),
            rng=rng,
            cuts=4,
            cleavage_count=7,
            noise_amp=0.14,
            flat_bot=-0.85,
            stone_type=st_type,
            meta_records=meta_records,
            smooth_faces=True,
        )

    # Lage 2: 8 dicht verzahnte Natursteine im Verband unter der Deckplatte (Z = 0.36 .. 0.84 m)
    n2 = 8
    for i in range(n2):
        ang = ((i + 0.5) / n2) * math.tau + rng.uniform(-0.06, 0.06)
        rx_pos = 0.84 + rng.uniform(-0.03, 0.03)
        ry_pos = 0.68 + rng.uniform(-0.03, 0.03)
        cx = math.cos(ang) * rx_pos
        cy = math.sin(ang) * ry_pos
        sx = rng.uniform(0.38, 0.47)
        sy = rng.uniform(0.31, 0.38)
        sz = rng.uniform(0.22, 0.26)
        cz = 0.58 + rng.uniform(-0.015, 0.015)
        st_type = rng.uniform(0.66, 0.92) if (i % 3 == 0) else rng.uniform(0.05, 0.28)
        make_fractured_stone(
            bm,
            center=(cx, cy, cz),
            radii=(sx, sy, sz),
            rot_euler=(rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05), ang + math.pi * 0.5 + rng.uniform(-0.18, 0.18)),
            rng=rng,
            cuts=4,
            cleavage_count=7,
            noise_amp=0.13,
            flat_top=0.82,
            flat_bot=-0.80,
            stone_type=st_type,
            meta_records=meta_records,
            smooth_faces=True,
        )

    # Lage 3A: Auskragende Opfer-Deckplatte (1 großer Kalksteinblock, Z = 0.75 .. 1.02 m)
    build_deck_slab(bm, rng, meta_records)

    # Lage 3B: 5 unbehauene Herd-Einfassungssteine rund um das Glutbett (Z = 0.97 .. 1.13 m)
    n3 = 5
    for i in range(n3):
        ang = (i / n3) * math.tau + 0.38 + rng.uniform(-0.08, 0.08)
        cx = math.cos(ang) * 0.72
        cy = math.sin(ang) * 0.58
        sx = rng.uniform(0.18, 0.23)
        sy = rng.uniform(0.13, 0.16)
        sz = rng.uniform(0.075, 0.095)
        st_type = rng.uniform(0.55, 0.88) if (i % 2 == 0) else rng.uniform(0.10, 0.28)
        make_fractured_stone(
            bm,
            center=(cx, cy, 1.035),
            radii=(sx, sy, sz),
            rot_euler=(rng.uniform(-0.06, 0.06), rng.uniform(-0.06, 0.06), ang + math.pi * 0.5),
            rng=rng,
            cuts=3,
            cleavage_count=6,
            noise_amp=0.13,
            flat_bot=-0.70,
            stone_type=st_type,
            meta_records=meta_records,
            smooth_faces=True,
        )

    # Seitliche Trittsteine: 2 West + 2 Ost (Z = -0.18 .. +0.52 m, sicher innerhalb |X| <= 2.10 m)
    step_specs = [
        ((-1.68, +0.05, 0.07), (0.37, 0.46, 0.17), 0.10, 0.80),
        ((-1.32, +0.02, 0.33), (0.28, 0.39, 0.16), -0.07, 0.16),
        ((+1.66, -0.04, 0.07), (0.36, 0.45, 0.17), -0.14, 0.78),
        ((+1.31, -0.02, 0.33), (0.28, 0.38, 0.16), 0.09, 0.14),
    ]
    for pos, rad, yaw, st_t in step_specs:
        make_fractured_stone(
            bm,
            center=pos,
            radii=rad,
            rot_euler=(0.0, 0.0, yaw),
            rng=rng,
            cuts=3,
            cleavage_count=6,
            noise_amp=0.12,
            flat_top=0.80,
            flat_bot=-0.85,
            stone_type=st_t,
            meta_records=meta_records,
            smooth_faces=True,
        )

    mesh = bpy.data.meshes.new("Altar_Stone_Mesh")
    bm.to_mesh(mesh)

    bm.verts.ensure_lookup_table()
    s_types = [meta_records.get(v, (0.2, 0.0, 0.0))[0] for v in bm.verts]
    s_soots = [meta_records.get(v, (0.2, 0.0, 0.0))[1] for v in bm.verts]
    s_mosss = [meta_records.get(v, (0.2, 0.0, 0.0))[2] for v in bm.verts]
    set_float_attr(mesh, "meta_stone_type", s_types)
    set_float_attr(mesh, "meta_soot", s_soots)
    set_float_attr(mesh, "meta_moss", s_mosss)

    bm.free()
    mesh.update()

    obj = bpy.data.objects.new("Altar_Stone", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def add_charred_log(bm, p0, p1, r0, r1, rng, ember_records, wood_seed=0.0):
    """
    Erzeugt ein leicht gekrümmtes, naturwüchsiges Zedern-/Eichenscheit mit Rindenriefen
    und abgeschrägten Spaltenden zwischen p0 und p1.
    """
    p0 = Vector(p0)
    p1 = Vector(p1)
    axis = p1 - p0
    z_dir = axis.normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(z_dir.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    x_dir = ref.cross(z_dir).normalized()
    y_dir = z_dir.cross(x_dir).normalized()

    n_rings = 9
    n_sides = 10
    rings = []
    for ri in range(n_rings):
        t = ri / (n_rings - 1)
        center = p0.lerp(p1, t)
        bend = math.sin(t * math.pi) * rng.uniform(-0.018, 0.022)
        center += y_dir * bend
        rad = r0 + (r1 - r0) * t
        ring_verts = []
        for si in range(n_sides):
            ang = (si / n_sides) * math.tau
            flute = 1.0 + 0.16 * math.sin(ang * 3.0 + wood_seed + t * 2.2) + rng.uniform(-0.08, 0.08)
            offset = (x_dir * math.cos(ang) + y_dir * math.sin(ang)) * (rad * flute)
            # Leichte Schrägschnitt-Enden (Spaltholz-Optik)
            ax_skew = math.cos(ang) * 0.022 if (ri == 0 or ri == n_rings - 1) else 0.0
            co = center + offset + z_dir * ax_skew
            v = bm.verts.new(co)
            ring_verts.append(v)

            d_core = math.hypot(co.x, co.y)
            core_w = max(0.0, min(1.0, 1.0 - d_core / 0.38)) ** 1.35
            down_w = 0.25 + 0.75 * max(0.0, -math.sin(ang))
            ember_records[v] = (core_w * down_w, 1.0)
        rings.append(ring_verts)

    for ri in range(n_rings - 1):
        r_a = rings[ri]
        r_b = rings[ri + 1]
        for si in range(n_sides):
            sj = (si + 1) % n_sides
            f = bm.faces.new([r_a[si], r_a[sj], r_b[sj], r_b[si]])
            f.smooth = True

    bm.faces.new(list(reversed(rings[0]))).smooth = False
    bm.faces.new(rings[-1]).smooth = False


def add_coal_chunk(bm, center, radii, yaw, rng, ember_records):
    """Kleiner kantiger 3D-Holzkohlebrocken im Glutbett für plastische Nahaufnahme."""
    tmp = bmesh.new()
    bmesh.ops.create_icosphere(tmp, subdivisions=2, radius=1.0)
    rot_m = Euler((rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), yaw), "XYZ").to_matrix()
    rx, ry, rz = radii
    vmap = {}
    for v in tmp.verts:
        p = v.co.copy()
        j = 1.0 + rng.uniform(-0.22, 0.22)
        p.x *= rx * j
        p.y *= ry * j
        p.z *= rz * (0.75 if p.z > 0 else 1.0)
        w = (rot_m @ p) + Vector(center)
        nv = bm.verts.new(w)
        vmap[v] = nv
        d_c = math.hypot(w.x, w.y)
        # Unterseite/Spalten stark glühend, Oberseite dunkle Kohle
        glow = max(0.0, min(1.0, 1.0 - d_c / 0.50)) * (0.95 if p.z <= 0.0 else 0.35)
        ember_records[nv] = (glow, 0.0)
    for f in tmp.faces:
        bm.faces.new([vmap[v] for v in f.verts]).smooth = False
    tmp.free()


def build_charcoal_and_logs_object(rng):
    """
    Erzeugt das Asche- & Glutbett (Z ~ 0.98..1.09 m), 8 plastische Holzkohle-Brocken
    sowie 7 versetzt-gekreuzte verkohlte Zedern-/Eichenscheite (Z ~ 1.06..1.28 m).
    """
    bm = bmesh.new()
    ember_records = {}

    # 1. Geformtes Asche- & Holzkohle-Glutbett in der Herdmulde
    n_rings = 8
    n_seg = 24
    center_v = bm.verts.new((0.0, 0.0, 1.068))
    ember_records[center_v] = (1.0, 0.0)
    rings = []
    for ri in range(1, n_rings + 1):
        frac = ri / n_rings
        rx = 0.60 * frac
        ry = 0.50 * frac
        ring_v = []
        for si in range(n_seg):
            ang = (si / n_seg) * math.tau
            n_val = noise.noise(Vector((math.cos(ang) * frac * 3.8, math.sin(ang) * frac * 3.8, 2.1)))
            z_base = 1.066 - 0.088 * (frac ** 1.6)
            z = z_base + n_val * 0.025 * (1.0 - 0.45 * frac)
            x = math.cos(ang) * rx * (1.0 + 0.06 * n_val)
            y = math.sin(ang) * ry * (1.0 + 0.06 * n_val)
            v = bm.verts.new((x, y, z))
            ring_v.append(v)
            ember_w = max(0.0, min(1.0, 1.0 - (frac ** 1.35) * 0.95))
            ember_records[v] = (ember_w, 0.0)
        rings.append(ring_v)

    for si in range(n_seg):
        sj = (si + 1) % n_seg
        bm.faces.new([center_v, rings[0][si], rings[0][sj]]).smooth = True
    for ri in range(n_rings - 1):
        for si in range(n_seg):
            sj = (si + 1) % n_seg
            bm.faces.new([rings[ri][si], rings[ri + 1][si], rings[ri + 1][sj], rings[ri][sj]]).smooth = True

    # 2. 8 einzelne plastische Holzkohle-Brocken zwischen den Scheiten
    coal_coords = [
        (-0.22, -0.14, 1.065), (0.24, -0.10, 1.068), (-0.15, 0.21, 1.062),
        (0.18, 0.19, 1.064), (0.02, -0.26, 1.055), (-0.28, 0.04, 1.058),
        (0.05, 0.03, 1.080), (0.29, 0.06, 1.056),
    ]
    for cx, cy, cz in coal_coords:
        add_coal_chunk(
            bm,
            (cx, cy, cz),
            (rng.uniform(0.055, 0.085), rng.uniform(0.045, 0.070), rng.uniform(0.030, 0.048)),
            rng.uniform(0.0, math.tau),
            rng,
            ember_records,
        )

    # 3. 7 natürlich versetzt geschichtete verkohlte Zedern- & Eichenscheite (keine sterile X-Kreuzung)
    log_specs = [
        # Untere Lage (leicht versetzt auf dem Glutbett)
        ((-0.48, -0.22, 1.065), (+0.46, +0.02, 1.105), 0.056, 0.050),
        ((-0.42, +0.18, 1.070), (+0.44, -0.16, 1.095), 0.054, 0.058),
        ((-0.18, -0.44, 1.060), (+0.08, +0.42, 1.115), 0.052, 0.048),
        # Obere gekreuzte Lage (natürliches Pyramiden-Lagerfeuer, versetzte Achsen)
        ((-0.34, -0.30, 1.110), (+0.32, +0.28, 1.245), 0.050, 0.044),
        ((+0.36, -0.24, 1.115), (-0.26, +0.34, 1.255), 0.049, 0.045),
        ((-0.40, +0.06, 1.135), (+0.38, +0.14, 1.195), 0.046, 0.050),
        ((+0.06, +0.38, 1.105), (-0.08, -0.34, 1.260), 0.045, 0.041),
    ]
    for idx, (p0, p1, r0, r1) in enumerate(log_specs):
        add_charred_log(bm, p0, p1, r0, r1, rng, ember_records, wood_seed=idx * 2.3)

    mesh = bpy.data.meshes.new("Altar_Charcoal_Ember_Mesh")
    bm.to_mesh(mesh)

    bm.verts.ensure_lookup_table()
    e_ws = [meta_records_val[0] for meta_records_val in (ember_records.get(v, (0.0, 1.0)) for v in bm.verts)]
    is_ws = [meta_records_val[1] for meta_records_val in (ember_records.get(v, (0.0, 1.0)) for v in bm.verts)]
    set_float_attr(mesh, "meta_ember_w", e_ws)
    set_float_attr(mesh, "meta_is_wood", is_ws)

    bm.free()
    mesh.update()

    obj = bpy.data.objects.new("Altar_Charcoal_Ember", mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def _attr_node(nt, name):
    n = nt.nodes.new("ShaderNodeAttribute")
    n.attribute_name = name
    return n


def create_stone_material():
    """
    Prozedurales Zyklen-Natursteinmaterial für den Back-Durchlauf:
      - Basalt (0.08..0.16) & Kalkstein (0.21..0.38) über FLOAT-Attribut meta_stone_type
      - Spärliche natürliche Verwitterungsrisse (maskiert, kein gleichförmiges Gitter!)
      - Pointiness-Kantenabnutzung & AO-Cavity (keine eingebackenen Sonnenschatten!)
      - Moos-/Erdansatz im unteren Drittel (meta_moss) + Ruß-Cavity (meta_soot)
      - Albedo strikt in [0.07 .. 0.44] linear-sRGB!
      - Roughness strikt in [0.38 .. 0.93]
    """
    mat = bpy.data.materials.new("Mat_Altar_Stone")
    if not mat.use_nodes:
        mat.use_nodes = True
    mat["tempC"] = 120.0
    mat["etaEC5"] = 20.0

    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Metallic"].default_value = 0.0
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tex_coord = nt.nodes.new("ShaderNodeTexCoord")
    geom = nt.nodes.new("ShaderNodeNewGeometry")
    a_type = _attr_node(nt, "meta_stone_type")
    a_soot = _attr_node(nt, "meta_soot")
    a_moss = _attr_node(nt, "meta_moss")

    # Makro-Gesteinsschichtung & Mikro-Körnung
    noise_macro = nt.nodes.new("ShaderNodeTexNoise")
    noise_macro.inputs["Scale"].default_value = 2.8
    noise_macro.inputs["Detail"].default_value = 8.0
    noise_macro.inputs["Roughness"].default_value = 0.65
    nt.links.new(tex_coord.outputs["Object"], noise_macro.inputs["Vector"])

    noise_micro = nt.nodes.new("ShaderNodeTexNoise")
    noise_micro.inputs["Scale"].default_value = 24.0
    noise_micro.inputs["Detail"].default_value = 10.0
    noise_micro.inputs["Roughness"].default_value = 0.72
    nt.links.new(tex_coord.outputs["Object"], noise_micro.inputs["Vector"])

    # Spärliche natürliche Verwitterungsrisse (stark verzerrt + lokal durch Noise maskiert)
    noise_mask = nt.nodes.new("ShaderNodeTexNoise")
    noise_mask.inputs["Scale"].default_value = 1.6
    noise_mask.inputs["Detail"].default_value = 4.0
    nt.links.new(tex_coord.outputs["Object"], noise_mask.inputs["Vector"])

    mix_vec = nt.nodes.new("ShaderNodeMix")
    mix_vec.data_type = "VECTOR"
    mix_vec.inputs["Factor"].default_value = 0.24
    nt.links.new(tex_coord.outputs["Object"], mix_vec.inputs[4])
    nt.links.new(noise_macro.outputs["Color"], mix_vec.inputs[5])

    vor_cracks = nt.nodes.new("ShaderNodeTexVoronoi")
    vor_cracks.feature = "DISTANCE_TO_EDGE"
    vor_cracks.inputs["Scale"].default_value = 3.2
    nt.links.new(mix_vec.outputs[1], vor_cracks.inputs["Vector"])

    crack_ramp = nt.nodes.new("ShaderNodeValToRGB")
    crack_ramp.color_ramp.elements[0].position = 0.00
    crack_ramp.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1.0)
    crack_ramp.color_ramp.elements[1].position = 0.032
    crack_ramp.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0)
    nt.links.new(vor_cracks.outputs["Distance"], crack_ramp.inputs["Fac"])

    vein_mask_ramp = nt.nodes.new("ShaderNodeValToRGB")
    vein_mask_ramp.color_ramp.elements[0].position = 0.45
    vein_mask_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    vein_mask_ramp.color_ramp.elements[1].position = 0.72
    vein_mask_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(noise_mask.outputs["Fac"], vein_mask_ramp.inputs["Fac"])

    crack_final = nt.nodes.new("ShaderNodeMath")
    crack_final.operation = "MULTIPLY"
    nt.links.new(crack_ramp.outputs["Color"], crack_final.inputs[0])
    nt.links.new(vein_mask_ramp.outputs["Color"], crack_final.inputs[1])

    # Basaltfarbe (0.075..0.16 linear-sRGB)
    ramp_basalt = nt.nodes.new("ShaderNodeValToRGB")
    ramp_basalt.color_ramp.elements[0].position = 0.25
    ramp_basalt.color_ramp.elements[0].color = (0.075, 0.080, 0.092, 1.0)
    ramp_basalt.color_ramp.elements[1].position = 0.78
    ramp_basalt.color_ramp.elements[1].color = (0.155, 0.160, 0.175, 1.0)
    nt.links.new(noise_macro.outputs["Fac"], ramp_basalt.inputs["Fac"])

    # Kalksteinfarbe (0.21..0.37 linear-sRGB)
    ramp_lime = nt.nodes.new("ShaderNodeValToRGB")
    ramp_lime.color_ramp.elements[0].position = 0.22
    ramp_lime.color_ramp.elements[0].color = (0.21, 0.185, 0.145, 1.0)
    ramp_lime.color_ramp.elements[1].position = 0.80
    ramp_lime.color_ramp.elements[1].color = (0.37, 0.330, 0.265, 1.0)
    nt.links.new(noise_macro.outputs["Fac"], ramp_lime.inputs["Fac"])

    mix_rock = nt.nodes.new("ShaderNodeMix")
    mix_rock.data_type = "RGBA"
    nt.links.new(a_type.outputs["Fac"], mix_rock.inputs["Factor"])
    nt.links.new(ramp_basalt.outputs["Color"], mix_rock.inputs[6])
    nt.links.new(ramp_lime.outputs["Color"], mix_rock.inputs[7])

    # Mikro-Mineralik
    mix_grain = nt.nodes.new("ShaderNodeMix")
    mix_grain.data_type = "RGBA"
    mix_grain.blend_type = "MULTIPLY"
    mix_grain.inputs["Factor"].default_value = 0.30
    nt.links.new(mix_rock.outputs[2], mix_grain.inputs[6])
    ramp_micro = nt.nodes.new("ShaderNodeValToRGB")
    ramp_micro.color_ramp.elements[0].color = (0.72, 0.70, 0.68, 1.0)
    ramp_micro.color_ramp.elements[1].color = (1.00, 0.99, 0.97, 1.0)
    nt.links.new(noise_micro.outputs["Fac"], ramp_micro.inputs["Fac"])
    nt.links.new(ramp_micro.outputs["Color"], mix_grain.inputs[7])

    # Pointiness-Kantenabnutzung
    point_ramp = nt.nodes.new("ShaderNodeValToRGB")
    point_ramp.color_ramp.elements[0].position = 0.49
    point_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    point_ramp.color_ramp.elements[1].position = 0.56
    point_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(geom.outputs["Pointiness"], point_ramp.inputs["Fac"])

    mix_wear = nt.nodes.new("ShaderNodeMix")
    mix_wear.data_type = "RGBA"
    mix_wear.blend_type = "ADD"
    nt.links.new(point_ramp.outputs["Color"], mix_wear.inputs["Factor"])
    nt.links.new(mix_grain.outputs[2], mix_wear.inputs[6])
    mix_wear.inputs[7].default_value = (0.055, 0.050, 0.042, 1.0)

    # Cavity-AO in Fugen (keine Sonnenschatten!)
    ao_node = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao_node.samples = 16
    ao_node.inputs["Distance"].default_value = 0.35
    ao_ramp = nt.nodes.new("ShaderNodeValToRGB")
    ao_ramp.color_ramp.elements[0].position = 0.15
    ao_ramp.color_ramp.elements[0].color = (0.45, 0.43, 0.41, 1.0)
    ao_ramp.color_ramp.elements[1].position = 0.85
    ao_ramp.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)
    nt.links.new(ao_node.outputs["AO"], ao_ramp.inputs["Fac"])

    mix_ao = nt.nodes.new("ShaderNodeMix")
    mix_ao.data_type = "RGBA"
    mix_ao.blend_type = "MULTIPLY"
    mix_ao.inputs["Factor"].default_value = 0.65
    nt.links.new(mix_wear.outputs[2], mix_ao.inputs[6])
    nt.links.new(ao_ramp.outputs["Color"], mix_ao.inputs[7])

    # Spärliche Verwitterungsrisse abdunkeln
    crk_fac = nt.nodes.new("ShaderNodeMath")
    crk_fac.operation = "MULTIPLY"
    crk_fac.inputs[1].default_value = 0.60
    nt.links.new(crack_final.outputs["Value"], crk_fac.inputs[0])

    mix_crk_col = nt.nodes.new("ShaderNodeMix")
    mix_crk_col.data_type = "RGBA"
    nt.links.new(crk_fac.outputs["Value"], mix_crk_col.inputs["Factor"])
    nt.links.new(mix_ao.outputs[2], mix_crk_col.inputs[6])
    mix_crk_col.inputs[7].default_value = (0.072, 0.070, 0.068, 1.0)

    # Moos- & Erdansatz im unteren Drittel (meta_moss * noise)
    moss_mul = nt.nodes.new("ShaderNodeMath")
    moss_mul.operation = "MULTIPLY"
    nt.links.new(a_moss.outputs["Fac"], moss_mul.inputs[0])
    nt.links.new(noise_macro.outputs["Fac"], moss_mul.inputs[1])

    moss_ramp = nt.nodes.new("ShaderNodeValToRGB")
    moss_ramp.color_ramp.elements[0].position = 0.25
    moss_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    moss_ramp.color_ramp.elements[1].position = 0.68
    moss_ramp.color_ramp.elements[1].color = (0.75, 0.75, 0.75, 1.0)
    nt.links.new(moss_mul.outputs["Value"], moss_ramp.inputs["Fac"])

    mix_moss = nt.nodes.new("ShaderNodeMix")
    mix_moss.data_type = "RGBA"
    nt.links.new(moss_ramp.outputs["Color"], mix_moss.inputs["Factor"])
    nt.links.new(mix_crk_col.outputs[2], mix_moss.inputs[6])
    mix_moss.inputs[7].default_value = (0.078, 0.098, 0.044, 1.0)

    # Ruß-Cavity um die Opfermulde (meta_soot)
    soot_mul = nt.nodes.new("ShaderNodeMath")
    soot_mul.operation = "MULTIPLY"
    soot_mul.inputs[1].default_value = 0.88
    nt.links.new(a_soot.outputs["Fac"], soot_mul.inputs[0])

    mix_soot = nt.nodes.new("ShaderNodeMix")
    mix_soot.data_type = "RGBA"
    nt.links.new(soot_mul.outputs["Value"], mix_soot.inputs["Factor"])
    nt.links.new(mix_moss.outputs[2], mix_soot.inputs[6])
    mix_soot.inputs[7].default_value = (0.070, 0.068, 0.066, 1.0)

    # Strikt auf Linear-sRGB [0.072 .. 0.435] begrenzen (niemals > 0.85!)
    clamp_sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(mix_soot.outputs[2], clamp_sep.inputs["Color"])
    clamp_comb = nt.nodes.new("ShaderNodeCombineColor")
    for ch in range(3):
        c_node = nt.nodes.new("ShaderNodeClamp")
        c_node.inputs["Min"].default_value = 0.072
        c_node.inputs["Max"].default_value = 0.435
        nt.links.new(clamp_sep.outputs[ch], c_node.inputs["Value"])
        nt.links.new(c_node.outputs["Result"], clamp_comb.inputs[ch])
    nt.links.new(clamp_comb.outputs["Color"], bsdf.inputs["Base Color"])

    # Roughness: [0.38 .. 0.93]
    rough_base = nt.nodes.new("ShaderNodeMapRange")
    rough_base.inputs["To Min"].default_value = 0.68
    rough_base.inputs["To Max"].default_value = 0.90
    nt.links.new(noise_micro.outputs["Fac"], rough_base.inputs["Value"])

    rough_wear = nt.nodes.new("ShaderNodeMix")
    rough_wear.data_type = "FLOAT"
    nt.links.new(point_ramp.outputs["Color"], rough_wear.inputs["Factor"])
    nt.links.new(rough_base.outputs["Result"], rough_wear.inputs[2])
    rough_wear.inputs[3].default_value = 0.44

    rough_clamp = nt.nodes.new("ShaderNodeClamp")
    rough_clamp.inputs["Min"].default_value = 0.38
    rough_clamp.inputs["Max"].default_value = 0.94
    nt.links.new(rough_wear.outputs[0], rough_clamp.inputs["Value"])
    nt.links.new(rough_clamp.outputs["Result"], bsdf.inputs["Roughness"])

    # Bump: spärliche Risse + scharfe Mikro-Körnung
    bump_crack = nt.nodes.new("ShaderNodeBump")
    bump_crack.invert = True
    bump_crack.inputs["Strength"].default_value = 0.50
    bump_crack.inputs["Distance"].default_value = 0.015
    nt.links.new(crack_final.outputs["Value"], bump_crack.inputs["Height"])

    bump_grain = nt.nodes.new("ShaderNodeBump")
    bump_grain.inputs["Strength"].default_value = 0.38
    bump_grain.inputs["Distance"].default_value = 0.007
    nt.links.new(noise_micro.outputs["Fac"], bump_grain.inputs["Height"])
    nt.links.new(bump_crack.outputs["Normal"], bump_grain.inputs["Normal"])
    nt.links.new(bump_grain.outputs["Normal"], bsdf.inputs["Normal"])

    return mat


def create_charcoal_ember_material():
    """
    Material 2: Verkohlte Zedern-/Eichenscheite, Aschebett & HDR-Glutspalten
    (KHR_materials_emissive_strength = 4.5, Thermo = 600 °C).
    """
    mat = bpy.data.materials.new("Mat_Altar_Charcoal_Ember")
    if not mat.use_nodes:
        mat.use_nodes = True
    mat["tempC"] = 600.0
    mat["etaEC5"] = 62.0

    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Emission Strength"].default_value = 4.5
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tex_coord = nt.nodes.new("ShaderNodeTexCoord")
    a_ember = _attr_node(nt, "meta_ember_w")
    a_wood = _attr_node(nt, "meta_is_wood")

    noise_char = nt.nodes.new("ShaderNodeTexNoise")
    noise_char.inputs["Scale"].default_value = 11.0
    noise_char.inputs["Detail"].default_value = 8.0
    nt.links.new(tex_coord.outputs["Object"], noise_char.inputs["Vector"])

    # Riss-Koordinaten leicht verzerren -> organische, zackige Glutspalten statt Wabenmuster
    mix_evec = nt.nodes.new("ShaderNodeMix")
    mix_evec.data_type = "VECTOR"
    mix_evec.inputs["Factor"].default_value = 0.16
    nt.links.new(tex_coord.outputs["Object"], mix_evec.inputs[4])
    nt.links.new(noise_char.outputs["Color"], mix_evec.inputs[5])

    vor_ember = nt.nodes.new("ShaderNodeTexVoronoi")
    vor_ember.feature = "DISTANCE_TO_EDGE"
    vor_ember.inputs["Scale"].default_value = 14.0
    nt.links.new(mix_evec.outputs[1], vor_ember.inputs["Vector"])

    # Enge, scharfe Glutspalten (~12-18% Fläche) zwischen dunklen Holzkohle-Inseln
    fissure_ramp = nt.nodes.new("ShaderNodeValToRGB")
    fissure_ramp.color_ramp.elements[0].position = 0.00
    fissure_ramp.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1.0)
    fissure_ramp.color_ramp.elements[1].position = 0.075
    fissure_ramp.color_ramp.elements[1].color = (0.0, 0.0, 0.0, 1.0)
    nt.links.new(vor_ember.outputs["Distance"], fissure_ramp.inputs["Fac"])

    ember_pow = nt.nodes.new("ShaderNodeMath")
    ember_pow.operation = "POWER"
    ember_pow.inputs[1].default_value = 1.45
    nt.links.new(a_ember.outputs["Fac"], ember_pow.inputs[0])

    ember_mask = nt.nodes.new("ShaderNodeMath")
    ember_mask.operation = "MULTIPLY"
    nt.links.new(fissure_ramp.outputs["Color"], ember_mask.inputs[0])
    nt.links.new(ember_pow.outputs["Value"], ember_mask.inputs[1])

    mix_emit = nt.nodes.new("ShaderNodeMix")
    mix_emit.data_type = "RGBA"
    nt.links.new(ember_mask.outputs["Value"], mix_emit.inputs["Factor"])
    mix_emit.inputs[6].default_value = (0.0, 0.0, 0.0, 1.0)
    mix_emit.inputs[7].default_value = (1.0, 0.145, 0.009, 1.0)
    nt.links.new(mix_emit.outputs[2], bsdf.inputs["Emission Color"])

    # Holzmaserung (dunkle Zeder/Eiche außen) -> tiefschwarze Holzkohle (innen) vs Aschebett
    char_fac = nt.nodes.new("ShaderNodeMapRange")
    char_fac.inputs["From Min"].default_value = 0.0
    char_fac.inputs["From Max"].default_value = 0.45
    char_fac.inputs["To Min"].default_value = 0.0
    char_fac.inputs["To Max"].default_value = 1.0
    nt.links.new(a_ember.outputs["Fac"], char_fac.inputs["Value"])

    wood_col = nt.nodes.new("ShaderNodeMix")
    wood_col.data_type = "RGBA"
    nt.links.new(char_fac.outputs["Result"], wood_col.inputs["Factor"])
    wood_col.inputs[6].default_value = (0.115, 0.064, 0.036, 1.0)
    wood_col.inputs[7].default_value = (0.062, 0.058, 0.055, 1.0)

    ash_ramp = nt.nodes.new("ShaderNodeValToRGB")
    ash_ramp.color_ramp.elements[0].position = 0.35
    ash_ramp.color_ramp.elements[0].color = (0.062, 0.058, 0.055, 1.0)
    ash_ramp.color_ramp.elements[1].position = 0.85
    ash_ramp.color_ramp.elements[1].color = (0.145, 0.136, 0.128, 1.0)
    nt.links.new(noise_char.outputs["Fac"], ash_ramp.inputs["Fac"])

    mix_wood_ash = nt.nodes.new("ShaderNodeMix")
    mix_wood_ash.data_type = "RGBA"
    nt.links.new(a_wood.outputs["Fac"], mix_wood_ash.inputs["Factor"])
    nt.links.new(ash_ramp.outputs["Color"], mix_wood_ash.inputs[6])
    nt.links.new(wood_col.outputs[2], mix_wood_ash.inputs[7])
    nt.links.new(mix_wood_ash.outputs[2], bsdf.inputs["Base Color"])

    rough_map = nt.nodes.new("ShaderNodeMapRange")
    rough_map.inputs["To Min"].default_value = 0.78
    rough_map.inputs["To Max"].default_value = 0.94
    nt.links.new(noise_char.outputs["Fac"], rough_map.inputs["Value"])
    nt.links.new(rough_map.outputs["Result"], bsdf.inputs["Roughness"])

    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.55
    bump.inputs["Distance"].default_value = 0.010
    nt.links.new(vor_ember.outputs["Distance"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    return mat


def unwrap_shared_uv_atlas(objs):
    """Erstellt ein gemeinsames, überlappungsfreies Smart-UV-Layout für beide Altar-Meshes."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objs:
        if not obj.data.uv_layers:
            obj.data.uv_layers.new(name="UVMap")
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(62.0), island_margin=0.015, area_weight=0.5)
    bpy.ops.uv.pack_islands(margin=0.012)
    bpy.ops.object.mode_set(mode="OBJECT")


def _eval_mesh_tris(objs):
    deps = bpy.context.evaluated_depsgraph_get()
    total = 0
    per_obj = {}
    for o in objs:
        eo = o.evaluated_get(deps)
        tm = eo.to_mesh()
        tm.calc_loop_triangles()
        cnt = len(tm.loop_triangles)
        per_obj[o.name] = cnt
        total += cnt
        eo.to_mesh_clear()
    return total, per_obj


def build_highpoly_sources(stone_obj, ember_obj):
    """
    Erzeugt die High-Poly-Quellmeshes (~100k-140k Tris) per Subdivision Surface +
    Voronoi-/Musgrave-Fels-Displacement für den High-to-Low-Poly-Cycles-Bake.
    """
    # 1. Voronoi- & Musgrave-Texturen für echtes Fels-Mikrorelief
    tex_vor = bpy.data.textures.new("HP_Rock_Voronoi", type="VORONOI")
    tex_vor.noise_scale = 0.36
    tex_vor.distance_metric = "DISTANCE_SQUARED"

    tex_mus = bpy.data.textures.new("HP_Rock_Musgrave", type="MUSGRAVE")
    tex_mus.musgrave_type = "RIDGED_MULTIFRACTAL"
    tex_mus.noise_scale = 0.22
    tex_mus.octaves = 4.0

    tex_coal = bpy.data.textures.new("HP_Coal_Voronoi", type="VORONOI")
    tex_coal.noise_scale = 0.10

    def _dup_with_mods(src, suffix, mods_fn):
        hp = src.copy()
        hp.data = src.data.copy()
        hp.name = f"{src.name}_{suffix}"
        bpy.context.collection.objects.link(hp)
        mods_fn(hp)
        bpy.ops.object.select_all(action="DESELECT")
        hp.select_set(True)
        bpy.context.view_layer.objects.active = hp
        for m in list(hp.modifiers):
            bpy.ops.object.modifier_apply(modifier=m.name)
        return hp

    def _stone_mods(hp):
        sub = hp.modifiers.new("HP_Subsurf", type="SUBSURF")
        sub.subdivision_type = "SIMPLE"
        sub.levels = 2
        sub.render_levels = 2
        d1 = hp.modifiers.new("HP_Displace_Voronoi", type="DISPLACE")
        d1.texture = tex_vor
        d1.texture_coords = "OBJECT"
        d1.strength = 0.018
        d1.mid_level = 0.5
        d2 = hp.modifiers.new("HP_Displace_Musgrave", type="DISPLACE")
        d2.texture = tex_mus
        d2.texture_coords = "OBJECT"
        d2.strength = 0.012
        d2.mid_level = 0.5

    def _ember_mods(hp):
        sub = hp.modifiers.new("HP_Subsurf", type="SUBSURF")
        sub.subdivision_type = "SIMPLE"
        sub.levels = 1
        sub.render_levels = 1
        d1 = hp.modifiers.new("HP_Displace_Coal", type="DISPLACE")
        d1.texture = tex_coal
        d1.texture_coords = "OBJECT"
        d1.strength = 0.008
        d1.mid_level = 0.5

    stone_hp = _dup_with_mods(stone_obj, "HP", _stone_mods)
    ember_hp = _dup_with_mods(ember_obj, "HP", _ember_mods)
    return stone_hp, ember_hp


def _create_img(name, size, colorspace):
    img = bpy.data.images.new(name, width=size, height=size, alpha=False)
    img.colorspace_settings.name = colorspace
    return img


def _rewire_baked_pbr_material(mat, img_base, img_norm, img_orm, img_emit=None, is_ember=False):
    """Verdrahtet die gebackenen PBR-Maps sauber für glTF 2.0 Export (inkl. Emissive Strength 4.5)."""
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Metallic"].default_value = 0.0
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tex_base = nt.nodes.new("ShaderNodeTexImage")
    tex_base.image = img_base
    nt.links.new(tex_base.outputs["Color"], bsdf.inputs["Base Color"])

    tex_norm = nt.nodes.new("ShaderNodeTexImage")
    tex_norm.image = img_norm
    norm_map = nt.nodes.new("ShaderNodeNormalMap")
    norm_map.space = "TANGENT"
    norm_map.inputs["Strength"].default_value = 1.0
    nt.links.new(tex_norm.outputs["Color"], norm_map.inputs["Color"])
    nt.links.new(norm_map.outputs["Normal"], bsdf.inputs["Normal"])

    tex_orm = nt.nodes.new("ShaderNodeTexImage")
    tex_orm.image = img_orm
    sep_orm = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(tex_orm.outputs["Color"], sep_orm.inputs["Color"])
    nt.links.new(sep_orm.outputs["Green"], bsdf.inputs["Roughness"])
    nt.links.new(sep_orm.outputs["Blue"], bsdf.inputs["Metallic"])

    if is_ember and img_emit is not None:
        tex_emit = nt.nodes.new("ShaderNodeTexImage")
        tex_emit.image = img_emit
        nt.links.new(tex_emit.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 4.5
    else:
        bsdf.inputs["Emission Strength"].default_value = 0.0


def bake_high_to_low_pbr(pairs, assets_dir, slot_name, tex_size=1024):
    """
    Backt High-Poly -> Low-Poly (LOD0) PBR-Maps (BaseColor, Normal, ORM, Emissive)
    streng nach den 5 HDR-Regeln (0 Sonnenschatten, Albedo 0.06..0.48, Roughness 0.38..0.94, Emissive=4.5).
    """
    tex_dir = os.path.join(assets_dir, "textures")
    os.makedirs(tex_dir, exist_ok=True)
    scene = bpy.context.scene

    img_base = _create_img(f"{slot_name}_BaseColor", tex_size, "sRGB")
    img_norm = _create_img(f"{slot_name}_Normal", tex_size, "Non-Color")
    img_ao = _create_img(f"{slot_name}_AO_tmp", tex_size, "Non-Color")
    img_rough = _create_img(f"{slot_name}_Rough_tmp", tex_size, "Non-Color")
    img_orm = _create_img(f"{slot_name}_ORM", tex_size, "Non-Color")
    img_emit = _create_img(f"{slot_name}_Emissive", tex_size, "sRGB")

    scene.render.bake.use_selected_to_active = True
    scene.render.bake.cage_extrusion = 0.10
    scene.render.bake.max_ray_distance = 0.20
    scene.render.bake.margin = 8

    for idx, (hp_obj, lp_obj) in enumerate(pairs):
        mat = lp_obj.material_slots[0].material
        nt = mat.node_tree
        bake_node = nt.nodes.new("ShaderNodeTexImage")
        bake_node.name = "__arche_bake_target__"
        nt.nodes.active = bake_node
        bake_node.select = True

        bpy.ops.object.select_all(action="DESELECT")
        hp_obj.select_set(True)
        lp_obj.select_set(True)
        bpy.context.view_layer.objects.active = lp_obj

        scene.render.bake.use_clear = (idx == 0)

        # 1. BaseColor [sRGB] (nur Color, keine Sonnenschatten!)
        enable_cycles(scene, samples=4, use_denoising=False)
        scene.render.bake.use_pass_direct = False
        scene.render.bake.use_pass_indirect = False
        scene.render.bake.use_pass_color = True
        bake_node.image = img_base
        bpy.ops.object.bake(type="DIFFUSE")

        # 2. Normal [Non-Color] (High-Poly -> Low-Poly Tangent Space)
        bake_node.image = img_norm
        bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")

        # 3. Roughness [Non-Color]
        bake_node.image = img_rough
        bpy.ops.object.bake(type="ROUGHNESS")

        # 4. Ambient Occlusion [Non-Color] (16 Samples + OIDN)
        enable_cycles(scene, samples=16, use_denoising=True)
        bake_node.image = img_ao
        bpy.ops.object.bake(type="AO")

        # 5. Emissive [sRGB] (nur auf Glut-Mesh)
        if "Charcoal" in lp_obj.name:
            enable_cycles(scene, samples=4, use_denoising=False)
            out_node = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
            bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
            saved_surf = [lk.from_socket for lk in out_node.inputs["Surface"].links]
            for lk in list(out_node.inputs["Surface"].links):
                nt.links.remove(lk)
            tmp_emit = nt.nodes.new("ShaderNodeEmission")
            emit_in = bsdf.inputs["Emission Color"]
            if emit_in.is_linked:
                nt.links.new(emit_in.links[0].from_socket, tmp_emit.inputs["Color"])
            else:
                tmp_emit.inputs["Color"].default_value = emit_in.default_value
            nt.links.new(tmp_emit.outputs["Emission"], out_node.inputs["Surface"])
            scene.render.bake.use_clear = True
            bake_node.image = img_emit
            bpy.ops.object.bake(type="EMIT")
            for lk in list(out_node.inputs["Surface"].links):
                nt.links.remove(lk)
            for fs in saved_surf:
                nt.links.new(fs, out_node.inputs["Surface"])
            nt.nodes.remove(tmp_emit)

        nt.nodes.remove(bake_node)

    # ORM-Kanal packen: R = AO, G = Roughness, B = Metallic (0.0)
    try:
        import numpy as np
        n_px = tex_size * tex_size * 4
        ao_arr = np.empty(n_px, dtype=np.float32)
        rg_arr = np.empty(n_px, dtype=np.float32)
        img_ao.pixels.foreach_get(ao_arr)
        img_rough.pixels.foreach_get(rg_arr)
        orm_arr = np.ones(n_px, dtype=np.float32)
        orm_arr[0::4] = ao_arr[0::4]
        orm_arr[1::4] = rg_arr[1::4]
        orm_arr[2::4] = 0.0
        img_orm.pixels.foreach_set(orm_arr)
    except Exception:
        ao_px = list(img_ao.pixels)
        rg_px = list(img_rough.pixels)
        orm_px = [1.0] * len(ao_px)
        orm_px[0::4] = ao_px[0::4]
        orm_px[1::4] = rg_px[1::4]
        orm_px[2::4] = [0.0] * (len(ao_px) // 4)
        img_orm.pixels.foreach_set(orm_px)

    paths = {}
    for key, img, fname in (
        ("baseColor", img_base, f"{slot_name}_baseColor.png"),
        ("normal", img_norm, f"{slot_name}_normal.png"),
        ("orm", img_orm, f"{slot_name}_orm.png"),
        ("emissive", img_emit, f"{slot_name}_emissive.png"),
    ):
        fpath = os.path.join(tex_dir, fname)
        img.filepath_raw = fpath
        img.file_format = "PNG"
        img.save()
        paths[key] = f"assets/textures/{fname}"
        print(f"[ALTAR] Bake gespeichert ({tex_size}x{tex_size}): {fpath}")

    for tmp_img in (img_ao, img_rough):
        bpy.data.images.remove(tmp_img)

    # Materialien auf LOD0 mit den gebackenen Maps neu verdrahten
    for _, lp_obj in pairs:
        mat = lp_obj.material_slots[0].material
        is_emb = ("Charcoal" in lp_obj.name)
        _rewire_baked_pbr_material(mat, img_base, img_norm, img_orm, img_emit=img_emit, is_ember=is_emb)

    return paths


def render_dual_preview(glb_path, preview_path):
    """
    Lädt die exportierte .glb in eine saubere Cycles-Szene und rendert 2 Kontrollansichten
    nebeneinander (links: 3/4-Totale, rechts: Nahaufnahme auf Stein & HDR-Glut) nach preview_path.
    """
    scene = clear_scene()
    enable_cycles(scene, samples=32)

    bpy.ops.import_scene.gltf(filepath=glb_path)
    imported_meshes = [o for o in scene.objects if o.type == "MESH"]
    print(f"[PREVIEW] Importierte GLB-Meshes: {[o.name for o in imported_meshes]}")

    bpy.ops.mesh.primitive_plane_add(size=10.0, location=(0.0, 0.0, 0.0))
    ground = bpy.context.active_object
    ground_mat = bpy.data.materials.new("Preview_Ground")
    if not ground_mat.use_nodes:
        ground_mat.use_nodes = True
    g_bsdf = ground_mat.node_tree.nodes.get("Principled BSDF")
    g_bsdf.inputs["Base Color"].default_value = (0.09, 0.09, 0.10, 1.0)
    g_bsdf.inputs["Roughness"].default_value = 0.92
    ground.data.materials.append(ground_mat)

    world = bpy.data.worlds.new("Preview_World")
    scene.world = world
    if not world.use_nodes:
        world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.36, 0.43, 0.52, 1.0)
    bg.inputs["Strength"].default_value = 0.85

    sun_d = bpy.data.lights.new("Preview_Sun", type="SUN")
    sun_d.energy = 3.2
    sun_o = bpy.data.objects.new("Preview_Sun", sun_d)
    bpy.context.collection.objects.link(sun_o)
    sun_o.rotation_euler = (math.radians(52.0), math.radians(10.0), math.radians(-38.0))

    fire_pt = bpy.data.lights.new("Preview_FireFill", type="POINT")
    fire_pt.energy = 30.0
    fire_pt.color = (1.0, 0.36, 0.08)
    fire_pt.shadow_soft_size = 0.25
    fire_o = bpy.data.objects.new("Preview_FireFill", fire_pt)
    bpy.context.collection.objects.link(fire_o)
    fire_o.location = (0.0, 0.0, 1.38)

    cam_d = bpy.data.cameras.new("Preview_Cam")
    cam_d.lens = 42.0
    cam_o = bpy.data.objects.new("Preview_Cam", cam_d)
    bpy.context.collection.objects.link(cam_o)
    scene.camera = cam_o

    os.makedirs(os.path.dirname(preview_path), exist_ok=True)
    tmp_dir = os.path.dirname(preview_path)
    shot_a = os.path.join(tmp_dir, "_tmp_altar_overview.png")
    shot_b = os.path.join(tmp_dir, "_tmp_altar_closeup.png")

    scene.render.resolution_x = 640
    scene.render.resolution_y = 512
    scene.render.image_settings.file_format = "PNG"

    target_a = Vector((0.0, 0.0, 0.58))
    cam_o.location = Vector((3.35, -3.55, 2.35))
    cam_o.rotation_euler = (target_a - cam_o.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = shot_a
    bpy.ops.render.render(write_still=True)

    cam_d.lens = 50.0
    target_b = Vector((0.0, 0.0, 1.04))
    cam_o.location = Vector((1.15, -1.35, 1.62))
    cam_o.rotation_euler = (target_b - cam_o.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = shot_b
    bpy.ops.render.render(write_still=True)

    img_a = bpy.data.images.load(shot_a)
    img_b = bpy.data.images.load(shot_b)
    w, h = 640, 512
    px_a = list(img_a.pixels)
    px_b = list(img_b.pixels)
    comb = bpy.data.images.new("Combined_Preview", width=w * 2, height=h, alpha=True)
    out_px = [0.0] * (w * 2 * h * 4)
    row_stride_src = w * 4
    row_stride_dst = w * 2 * 4
    for y in range(h):
        s_off = y * row_stride_src
        d_off = y * row_stride_dst
        out_px[d_off:d_off + row_stride_src] = px_a[s_off:s_off + row_stride_src]
        out_px[d_off + row_stride_src:d_off + row_stride_dst] = px_b[s_off:s_off + row_stride_src]
    comb.pixels.foreach_set(out_px)
    comb.filepath_raw = preview_path
    comb.file_format = "PNG"
    comb.save()

    for p in (shot_a, shot_b):
        if os.path.isfile(p):
            os.remove(p)
    print(f"[PREVIEW] Doppel-Kontrollbild gespeichert: {preview_path} (1280x512)")


def export_lod0_and_lod1(objs, assets_dir, slot_name, hp_tris, lod0_tris, tex_paths, preview_rel):
    """Exportiert LOD0 und LOD1 über export_arche_glb.py und synchronisiert assets/manifest.json."""
    if assets_dir not in sys.path:
        sys.path.insert(0, assets_dir)
    import export_arche_glb as eag

    glb_dir = os.path.join(assets_dir, "glb", "world")
    os.makedirs(glb_dir, exist_ok=True)
    glb_lod0 = os.path.join(glb_dir, f"{slot_name}.glb")
    glb_lod1 = os.path.join(glb_dir, f"{slot_name}_lod1.glb")

    eag.export_glb(objs, glb_lod0, use_draco=False)

    # LOD1 (1.800 - 2.500 Tris) per Decimate mit erhaltenen UVs erzeugen
    target_lod1_tris = 2150.0
    ratio = max(0.05, min(0.95, target_lod1_tris / max(1, lod0_tris)))
    lod1_clones = []
    try:
        for src in objs:
            dup = src.copy()
            dup.data = src.data.copy()
            bpy.context.collection.objects.link(dup)
            dec = dup.modifiers.new(name="Arche_LOD1", type="DECIMATE")
            dec.decimate_type = "COLLAPSE"
            dec.ratio = ratio
            lod1_clones.append(dup)

        lod1_tris, lod1_per_obj = _eval_mesh_tris(lod1_clones)
        print(f"[ALTAR] LOD1-Tris: {lod1_tris} ({lod1_per_obj}, Ratio={ratio:.3f})")
        eag.export_glb(lod1_clones, glb_lod1, use_draco=False)
    finally:
        for c in lod1_clones:
            md = c.data
            bpy.data.objects.remove(c, do_unlink=True)
            if md and md.users == 0:
                bpy.data.meshes.remove(md)

    rel_lod0 = f"assets/glb/world/{slot_name}.glb"
    lod_paths = {"lod1": glb_lod1}
    stats = {
        "max_tris": 12000,
        "tris": lod0_tris,
        "meshes": len(objs),
        "materials": 2,
        "has_required_tag": True,
        "has_shapekeys": False,
    }
    eag.update_manifest(
        assets_dir,
        slot_name,
        rel_lod0,
        "world",
        stats,
        True,
        tex_paths=tex_paths,
        lod_paths=lod_paths,
        preview_rel=preview_rel,
    )
    # Zusätzliche LOD/HP-Metadaten in manifest.json (categories + slots.altar_hero) eintragen
    import json
    manifest_path = os.path.join(assets_dir, "manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    extra_meta = {
        "highPolyTris": hp_tris,
        "lod0Tris": lod0_tris,
        "lod1Tris": lod1_tris,
        "lodDistance": 25.0,
        "lods": {"lod1": f"assets/glb/world/{slot_name}_lod1.glb"},
        "bakedTextures": tex_paths,
        "preview": preview_rel,
        "emissiveStrength": 4.5,
    }
    item_entry = manifest.setdefault("categories", {}).setdefault("world", {}).setdefault("items", {}).setdefault(slot_name, {})
    item_entry.update(extra_meta)
    item_entry["tris"] = lod0_tris
    item_entry["maxTris"] = 12000

    slot_entry = manifest.setdefault("slots", {}).setdefault("altar_hero", {})
    slot_entry.update(extra_meta)
    slot_entry["enabled"] = True
    slot_entry["url"] = rel_lod0
    slot_entry["tris"] = lod0_tris
    slot_entry["maxTris"] = 12000

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"[ALTAR] manifest.json aktualisiert (HP={hp_tris}, LOD0={lod0_tris}, LOD1={lod1_tris})")
    return glb_lod0, glb_lod1, lod1_tris


def main():
    root = get_project_root()
    assets_dir = os.path.join(root, "assets")
    slot_name = "ararat_altar_cyclopean"
    blend_path = os.path.join(assets_dir, "blend", "world", f"{slot_name}.blend")
    glb_path = os.path.join(assets_dir, "glb", "world", f"{slot_name}.glb")
    preview_path = os.path.join(assets_dir, "previews", f"{slot_name}_preview.png")
    preview_rel = f"assets/previews/{slot_name}_preview.png"

    tail = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if "--preview-only" in tail:
        render_dual_preview(glb_path, preview_path)
        return

    rng = random.Random(20260820)
    clear_scene()

    stone_obj = build_altar_stone_object(rng)
    ember_obj = build_charcoal_and_logs_object(rng)

    mat_stone = create_stone_material()
    mat_ember = create_charcoal_ember_material()
    stone_obj.data.materials.append(mat_stone)
    ember_obj.data.materials.append(mat_ember)

    objs = [stone_obj, ember_obj]

    # High-Poly-Quelle (~80k-150k Tris) aus Quad-Topologie erzeugen
    stone_hp, ember_hp = build_highpoly_sources(stone_obj, ember_obj)
    hp_tris, hp_per = _eval_mesh_tris([stone_hp, ember_hp])
    print(f"[ALTAR] HighPoly-Tris: {hp_tris} ({hp_per})")

    # LOD0 triangulieren und sauber gemeinsam unwrappen
    for o in objs:
        bm_tri = bmesh.new()
        bm_tri.from_mesh(o.data)
        bmesh.ops.triangulate(bm_tri, faces=list(bm_tri.faces))
        bm_tri.to_mesh(o.data)
        bm_tri.free()
        o.data.update()

    unwrap_shared_uv_atlas(objs)
    lod0_tris, lod0_per = _eval_mesh_tris(objs)
    print(f"[ALTAR] LOD0-Tris: {lod0_tris} ({lod0_per}) | Materialien: 2")

    tex_paths = bake_high_to_low_pbr(
        [(stone_hp, stone_obj), (ember_hp, ember_obj)],
        assets_dir,
        slot_name,
        tex_size=1024,
    )

    # Temporäre High-Poly-Meshes nach dem Bake entfernen
    for hp_o in (stone_hp, ember_hp):
        md = hp_o.data
        bpy.data.objects.remove(hp_o, do_unlink=True)
        if md and md.users == 0:
            bpy.data.meshes.remove(md)

    os.makedirs(os.path.dirname(blend_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[ALTAR] Editierbare .blend gespeichert: {blend_path}")

    glb_lod0, glb_lod1, lod1_tris = export_lod0_and_lod1(
        objs, assets_dir, slot_name, hp_tris, lod0_tris, tex_paths, preview_rel
    )

    render_dual_preview(glb_lod0, preview_path)
    print(f"[ALTAR] FERTIG: HighPoly={hp_tris} -> LOD0={lod0_tris} / LOD1={lod1_tris} Tris")


if __name__ == "__main__":
    main()
