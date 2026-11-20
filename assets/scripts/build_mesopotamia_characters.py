"""
build_mesopotamia_characters.py — Menschen-Kit v2: 53 anatomische MPFB-Bronzezeit-Figuren
==========================================================================================
Ueberarbeitete v2-Pipeline auf Basis von bl_ext.blender_org.mpfb (HumanService, TargetService,
RigService) mit strikten Python-Assertions fuer Groesse, Polycount, Bodenkontakt & Prop-Kollision:

  1. assets/blend/characters/noah_family_kit.blend          (8 High-Poly Master + Web-LODs)
  2. assets/glb/characters/noah_family_kit.glb              (8 Heroes: LOD0 6.5k-9.5k | LOD1 1.8k-2.4k | LOD2 450-650)
  3. assets/blend/characters/mesopotamia_citizens_kit.blend (9 BaseTypes + 45 Varianten + 9 LOD1/2)
  4. assets/glb/characters/mesopotamia_citizens_kit.glb     (45 LOD0 3.0k-4.5k | 9 LOD1 850-1.1k | 9 LOD2 220-320)
  5. assets/previews/noah_family_8_lineup.png               (Alle 8 Noah-Familienmitglieder + Meter-Skala 1.0/1.5/1.8/2.0m)
  6. assets/previews/characters_closeup_details.png         (3-Zonen-Nahaufnahme: Gesichter/Haare, Props/Balken, Fuesse/Sandalen)
  7. assets/previews/characters_showcase_53.png             (Alle 53 Figuren gestaffelt mit Posen-Variation)
  8. Aktualisiert assets/manifest.json

Aufruf:
  blender --background --python assets/scripts/build_mesopotamia_characters.py
  blender --background --python assets/scripts/build_mesopotamia_characters.py -- --noah-only
"""

import os
import sys
import json
import math
import time
import datetime
import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix, Euler, Quaternion

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from build_character_trim_atlas import TRIM_REGIONS


# ==============================================================================
# HARTE BUDGET- & QUALITAETS-GRENZEN (PER ASSERTION ERZWUNGEN!)
# ==============================================================================
FEMALE_HEIGHT_MIN, FEMALE_HEIGHT_MAX = 1.61, 1.69
MALE_HEIGHT_MIN, MALE_HEIGHT_MAX = 1.73, 1.82

HERO_LOD0_MIN, HERO_LOD0_MAX, HERO_LOD0_TGT = 6500, 9500, 8000
HERO_LOD1_MIN, HERO_LOD1_MAX, HERO_LOD1_TGT = 1800, 2400, 2100
HERO_LOD2_MIN, HERO_LOD2_MAX, HERO_LOD2_TGT = 450, 650, 540

CIT_LOD0_MIN, CIT_LOD0_MAX, CIT_LOD0_TGT = 3000, 4500, 3750
CIT_LOD1_MIN, CIT_LOD1_MAX, CIT_LOD1_TGT = 850, 1100, 960
CIT_LOD2_MIN, CIT_LOD2_MAX, CIT_LOD2_TGT = 220, 320, 265

MIN_PROP_HEAD_CLEARANCE_M = 0.055  # >= 5.5 cm Luftlinie zum Kopf-/Hals-Mesh


# ==============================================================================
# PFADE, SZENE & MPFB-INITIALISIERUNG
# ==============================================================================
def get_project_root():
    return os.path.dirname(os.path.dirname(SCRIPT_DIR))


def enable_mpfb():
    """Aktiviert bl_ext.blender_org.mpfb sauber in Blender 4.2+/5.x."""
    if "bl_ext.blender_org.mpfb" not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module="bl_ext.blender_org.mpfb")
    from bl_ext.blender_org.mpfb.services.humanservice import HumanService
    from bl_ext.blender_org.mpfb.services.targetservice import TargetService
    from bl_ext.blender_org.mpfb.services.rigservice import RigService
    return HumanService, TargetService, RigService


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    return scene


def setup_cycles_render(scene, samples=36, res_x=1920, res_y=1080):
    scene.render.engine = "CYCLES"
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
    scene.cycles.use_denoising = True
    try:
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        try:
            scene.view_settings.view_transform = "AgX"
        except Exception:
            pass
    scene.view_settings.exposure = 0.0
    return "CUDA (GPU)" if used_gpu else "CPU"


# ==============================================================================
# GEMEINSAMES PBR-MATERIAL (1 TRIM-SHEET FUER ALLE 53 CHARAKTERE!)
# ==============================================================================
def create_character_trim_material(project_root):
    mat = bpy.data.materials.get("Mat_Arche_Characters_Trim")
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name="Mat_Arche_Characters_Trim")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    tex_dir = os.path.join(project_root, "assets", "textures")
    p_base = os.path.join(tex_dir, "character_trim_atlas_baseColor.png")
    p_norm = os.path.join(tex_dir, "character_trim_atlas_normal.png")
    p_orm  = os.path.join(tex_dir, "character_trim_atlas_orm.png")
    p_sss  = os.path.join(tex_dir, "character_trim_atlas_thickness.png")

    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    if os.path.exists(p_base):
        t_base = nodes.new("ShaderNodeTexImage")
        t_base.image = bpy.data.images.load(p_base, check_existing=True)
        t_base.image.colorspace_settings.name = "sRGB"
        links.new(t_base.outputs["Color"], bsdf.inputs["Base Color"])

    if os.path.exists(p_orm):
        t_orm = nodes.new("ShaderNodeTexImage")
        t_orm.image = bpy.data.images.load(p_orm, check_existing=True)
        t_orm.image.colorspace_settings.name = "Non-Color"
        sep = nodes.new("ShaderNodeSeparateColor")
        links.new(t_orm.outputs["Color"], sep.inputs["Color"])
        links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
        links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])

    if os.path.exists(p_norm):
        t_norm = nodes.new("ShaderNodeTexImage")
        t_norm.image = bpy.data.images.load(p_norm, check_existing=True)
        t_norm.image.colorspace_settings.name = "Non-Color"
        nmap = nodes.new("ShaderNodeNormalMap")
        nmap.inputs["Strength"].default_value = 0.85
        links.new(t_norm.outputs["Color"], nmap.inputs["Color"])
        links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])

    if os.path.exists(p_sss) and "Subsurface Weight" in bsdf.inputs:
        t_sss = nodes.new("ShaderNodeTexImage")
        t_sss.image = bpy.data.images.load(p_sss, check_existing=True)
        t_sss.image.colorspace_settings.name = "Non-Color"
        mul_sss = nodes.new("ShaderNodeMath")
        mul_sss.operation = "MULTIPLY"
        mul_sss.inputs[1].default_value = 0.10
        links.new(t_sss.outputs["Color"], mul_sss.inputs[0])
        links.new(mul_sss.outputs["Value"], bsdf.inputs["Subsurface Weight"])
        if "Subsurface Radius" in bsdf.inputs:
            bsdf.inputs["Subsurface Radius"].default_value = (0.9, 0.35, 0.18)

    if "Sheen Weight" in bsdf.inputs:
        bsdf.inputs["Sheen Weight"].default_value = 0.15
    return mat


# ==============================================================================
# RIG-POSING-HELFER (8 NATUERLICHE BRONZEZEIT-POSEN, KEIN MANNEQUIN-BLOCK!)
# ==============================================================================
def aim_bone_world(rig, bone_name, target_dir_world, blend=1.0):
    """Dreht einen Pose-Bone sauber so, dass seine Laengsachse in target_dir_world zeigt."""
    pb = rig.pose.bones.get(bone_name)
    if pb is None:
        return
    bpy.context.view_layer.update()
    cur_dir = (pb.tail - pb.head).normalized()
    tgt_dir = Vector(target_dir_world).normalized()
    q_world = cur_dir.rotation_difference(tgt_dir)
    if blend < 1.0:
        q_world = Quaternion().slerp(q_world, blend)
    bm_world = pb.matrix.to_3x3()
    q_local = (bm_world.inverted() @ q_world.to_matrix() @ bm_world).to_quaternion()
    pb.rotation_mode = "QUATERNION"
    pb.rotation_quaternion = (pb.rotation_quaternion @ q_local).normalized()


def rotate_bone_world_axis(rig, bone_name, axis_world, angle_rad):
    """Rotiert einen Pose-Bone zusaetzlich um eine Weltachse (z.B. Z fuer Hueft-/Kopfdrehung)."""
    pb = rig.pose.bones.get(bone_name)
    if pb is None or abs(angle_rad) < 1e-4:
        return
    bpy.context.view_layer.update()
    q_world = Quaternion(Vector(axis_world).normalized(), angle_rad)
    bm_world = pb.matrix.to_3x3()
    q_local = (bm_world.inverted() @ q_world.to_matrix() @ bm_world).to_quaternion()
    pb.rotation_mode = "QUATERNION"
    pb.rotation_quaternion = (pb.rotation_quaternion @ q_local).normalized()


def curl_hand_fingers(rig, side="r", amount=0.85):
    """Kruemmt die Finger einer Hand natuerlich um einen Griff/Stab (MPFB game_engine Rig)."""
    palm_dir = Vector((0.88 if side == "r" else -0.88, 0.30, 0.12)).normalized()
    for finger in ("index", "middle", "ring", "pinky"):
        for seg, factor in (("01", 0.50), ("02", 0.68), ("03", 0.58)):
            bname = f"{finger}_{seg}_{side}"
            pb = rig.pose.bones.get(bname)
            if pb is None:
                continue
            bpy.context.view_layer.update()
            cur = (pb.tail - pb.head).normalized()
            tgt = (cur * (1.0 - amount * factor) + palm_dir * (amount * factor)).normalized()
            aim_bone_world(rig, bname, tgt, blend=1.0)
    thumb_dir = Vector((0.50 if side == "r" else -0.50, -0.72, -0.30)).normalized()
    for seg, factor in (("01", 0.34), ("02", 0.50), ("03", 0.40)):
        bname = f"thumb_{seg}_{side}"
        if rig.pose.bones.get(bname):
            aim_bone_world(rig, bname, thumb_dir, blend=amount * factor)


def apply_natural_pose(rig, pose_name, seed=0):
    """Setzt 8 klar unterscheidbare, natuerliche Posen auf dem MPFB game_engine Rig (vor 180-Grad-Z-Drehung!).
    Hinweis vor 180-Grad-Drehung: MPFB schaut -Y, Links=+X, Rechts=-X, Oben=+Z.
    """
    stance_idx = seed % 6
    # 1) Natuerliche Koerper-/Kontrapost-Drehung (Huefte + Wirbelsaeule + Kopf)
    if stance_idx == 0:
        # Entspannter Kontrapost rechts (rechtes Bein Standbein, linkes leicht vorgesetzt)
        rotate_bone_world_axis(rig, "pelvis", (0, 0, 1), math.radians(7.0))
        rotate_bone_world_axis(rig, "spine_02", (0, 0, 1), math.radians(-5.0))
        aim_bone_world(rig, "thigh_l", Vector((0.06, -0.10, -0.993)))
        aim_bone_world(rig, "calf_l",  Vector((0.05,  0.04, -0.998)))
        aim_bone_world(rig, "thigh_r", Vector((-0.02, 0.02, -0.999)))
        aim_bone_world(rig, "calf_r",  Vector((-0.02, 0.02, -0.999)))
        head_yaw = math.radians(-8.0)
    elif stance_idx == 1:
        # Entspannter Kontrapost links (linkes Bein Standbein, rechtes leicht vorgesetzt)
        rotate_bone_world_axis(rig, "pelvis", (0, 0, 1), math.radians(-7.5))
        rotate_bone_world_axis(rig, "spine_02", (0, 0, 1), math.radians(5.5))
        aim_bone_world(rig, "thigh_l", Vector((0.02,  0.02, -0.999)))
        aim_bone_world(rig, "calf_l",  Vector((0.02,  0.02, -0.999)))
        aim_bone_world(rig, "thigh_r", Vector((-0.06, -0.10, -0.993)))
        aim_bone_world(rig, "calf_r",  Vector((-0.05,  0.04, -0.998)))
        head_yaw = math.radians(9.0)
    elif stance_idx == 2:
        # Leichte Schrittpose vorwaerts (links leicht vorn, beide Fuesse fest am Boden!)
        rotate_bone_world_axis(rig, "pelvis", (0, 0, 1), math.radians(5.0))
        rotate_bone_world_axis(rig, "spine_02", (0, 0, 1), math.radians(-6.0))
        aim_bone_world(rig, "thigh_l", Vector((0.04, -0.10, -0.994)))
        aim_bone_world(rig, "calf_l",  Vector((0.03,  0.02, -0.999)))
        aim_bone_world(rig, "thigh_r", Vector((-0.04,  0.08, -0.996)))
        aim_bone_world(rig, "calf_r",  Vector((-0.03,  0.06, -0.997)))
        head_yaw = math.radians(-5.0)
    elif stance_idx == 3:
        # Leichte Schrittpose vorwaerts (rechts leicht vorn, beide Fuesse fest am Boden!)
        rotate_bone_world_axis(rig, "pelvis", (0, 0, 1), math.radians(-5.5))
        rotate_bone_world_axis(rig, "spine_02", (0, 0, 1), math.radians(6.5))
        aim_bone_world(rig, "thigh_l", Vector((0.04,  0.08, -0.996)))
        aim_bone_world(rig, "calf_l",  Vector((0.03,  0.06, -0.997)))
        aim_bone_world(rig, "thigh_r", Vector((-0.04, -0.10, -0.994)))
        aim_bone_world(rig, "calf_r",  Vector((-0.03,  0.02, -0.999)))
        head_yaw = math.radians(6.0)
    elif stance_idx == 4:
        # Kraeftiger Handwerker-Stand (leicht geoeffnete Beine, Oberkoerper gedreht)
        rotate_bone_world_axis(rig, "pelvis", (0, 0, 1), math.radians(9.0))
        rotate_bone_world_axis(rig, "spine_02", (0, 0, 1), math.radians(-8.0))
        aim_bone_world(rig, "thigh_l", Vector((0.09, -0.07, -0.993)))
        aim_bone_world(rig, "calf_l",  Vector((0.05,  0.03, -0.998)))
        aim_bone_world(rig, "thigh_r", Vector((-0.09,  0.05, -0.995)))
        aim_bone_world(rig, "calf_r",  Vector((-0.05,  0.04, -0.998)))
        head_yaw = math.radians(-11.0)
    else:
        # Wuerdige ruhige Haltung mit sanfter Drehung
        rotate_bone_world_axis(rig, "pelvis", (0, 0, 1), math.radians(-4.5))
        rotate_bone_world_axis(rig, "spine_02", (0, 0, 1), math.radians(3.5))
        aim_bone_world(rig, "thigh_l", Vector((0.05, -0.06, -0.997)))
        aim_bone_world(rig, "calf_l",  Vector((0.03,  0.02, -0.999)))
        aim_bone_world(rig, "thigh_r", Vector((-0.04,  0.03, -0.999)))
        aim_bone_world(rig, "calf_r",  Vector((-0.02,  0.02, -0.999)))
        head_yaw = math.radians(10.0)

    # 2) Arme & Haende je nach Rollen-Pose
    if pose_name == "hold_staff_r":
        # Rechter Arm leicht vor den Koerper angewinkelt, Hand umfasst Wander-/Messstab fest
        aim_bone_world(rig, "upperarm_r", Vector((-0.26, -0.26, -0.93)))
        aim_bone_world(rig, "lowerarm_r", Vector((-0.10, -0.94,  0.28)))
        aim_bone_world(rig, "hand_r",     Vector((-0.06, -0.98,  0.14)))
        curl_hand_fingers(rig, "r", 0.96)
        # Linker Arm entspannt ueber Gewand/Schal
        aim_bone_world(rig, "upperarm_l", Vector((0.18, -0.14, -0.97)))
        aim_bone_world(rig, "lowerarm_l", Vector((-0.22, -0.62, -0.75)))
        curl_hand_fingers(rig, "l", 0.40)

    elif pose_name == "hold_tool_r":
        # Handwerker (inkl. Ham): rechter Unterarm kompakt vor rechter Huefte/Koerper -> Werkzeug klar lesbar, ragt nicht in Nachbarn!
        aim_bone_world(rig, "upperarm_r", Vector((-0.20, -0.22, -0.95)))
        aim_bone_world(rig, "lowerarm_r", Vector((0.22,  -0.91, -0.34)))
        aim_bone_world(rig, "hand_r",     Vector((0.20,  -0.93, -0.28)))
        curl_hand_fingers(rig, "r", 0.96)
        aim_bone_world(rig, "upperarm_l", Vector((0.20, -0.12, -0.97)))
        aim_bone_world(rig, "lowerarm_l", Vector((-0.05, -0.48, -0.87)))
        curl_hand_fingers(rig, "l", 0.45)

    elif pose_name == "carry_shoulder_r":
        # Traegt Balken/Sack auf dem AEUSSEREN rechten Schulterpolster; rechte Hand greift fest an Balken-Unterseite!
        aim_bone_world(rig, "upperarm_r", Vector((-0.44, -0.46, -0.77)))
        aim_bone_world(rig, "lowerarm_r", Vector((-0.05, -0.26,  0.96)))
        aim_bone_world(rig, "hand_r",     Vector((0.05,  -0.12,  0.99)))
        curl_hand_fingers(rig, "r", 0.88)
        aim_bone_world(rig, "upperarm_l", Vector((0.24, -0.10, -0.96)))
        aim_bone_world(rig, "lowerarm_l", Vector((0.12, -0.36, -0.92)))
        curl_hand_fingers(rig, "l", 0.35)

    elif pose_name == "carry_jar_hip":
        # Wassertraegerin: beide Unterarme stuetzen den Tonkrug fest vor rechter Huefte/Koerper (0% Schweben!)
        aim_bone_world(rig, "upperarm_r", Vector((-0.26, -0.26, -0.93)))
        aim_bone_world(rig, "lowerarm_r", Vector((0.36,  -0.90, -0.25)))
        aim_bone_world(rig, "hand_r",     Vector((0.42,  -0.88, -0.22)))
        curl_hand_fingers(rig, "r", 0.62)
        aim_bone_world(rig, "upperarm_l", Vector((0.22,  -0.30, -0.93)))
        aim_bone_world(rig, "lowerarm_l", Vector((-0.48, -0.86, -0.16)))
        curl_hand_fingers(rig, "l", 0.58)

    elif pose_name == "carry_basket_l":
        # Linker Arm angewinkelt, traegt Korb seitlich vor linker Huefte
        aim_bone_world(rig, "upperarm_l", Vector((0.32, -0.18, -0.93)))
        aim_bone_world(rig, "lowerarm_l", Vector((-0.04, -0.88, -0.46)))
        aim_bone_world(rig, "hand_l",     Vector((-0.18, -0.88, -0.42)))
        curl_hand_fingers(rig, "l", 0.60)
        aim_bone_world(rig, "upperarm_r", Vector((-0.20, -0.10, -0.97)))
        aim_bone_world(rig, "lowerarm_r", Vector((-0.06, -0.34, -0.94)))
        curl_hand_fingers(rig, "r", 0.35)

    elif pose_name == "hold_jar_front":
        # Beide Unterarme halten Krug/Schale vor dem Koerper mit echtem Abstand zur Brust
        aim_bone_world(rig, "upperarm_l", Vector((0.24, -0.32, -0.92)))
        aim_bone_world(rig, "lowerarm_l", Vector((-0.36, -0.91, -0.22)))
        aim_bone_world(rig, "upperarm_r", Vector((-0.24, -0.32, -0.92)))
        aim_bone_world(rig, "lowerarm_r", Vector((0.36, -0.91, -0.22)))
        curl_hand_fingers(rig, "l", 0.52)
        curl_hand_fingers(rig, "r", 0.52)

    elif pose_name == "prayer_bless":
        # Priester / Wuerdiger Gruss: rechte Hand segnend gehoben, linke mit Kultschale/Rolle
        aim_bone_world(rig, "upperarm_r", Vector((-0.26, -0.34, -0.90)))
        aim_bone_world(rig, "lowerarm_r", Vector((0.06, -0.76,  0.64)))
        aim_bone_world(rig, "hand_r",     Vector((0.04, -0.58,  0.81)))
        curl_hand_fingers(rig, "r", 0.22)
        aim_bone_world(rig, "upperarm_l", Vector((0.22, -0.24, -0.94)))
        aim_bone_world(rig, "lowerarm_l", Vector((-0.22, -0.94, -0.22)))
        curl_hand_fingers(rig, "l", 0.78)

    elif pose_name == "hold_scroll_l":
        # Schreiber / Sem / Haendler: linke Hand haelt Schriftrolle vor Brust, rechte gestikuliert ruhig
        aim_bone_world(rig, "upperarm_l", Vector((0.24, -0.28, -0.93)))
        aim_bone_world(rig, "lowerarm_l", Vector((-0.24, -0.94,  0.20)))
        curl_hand_fingers(rig, "l", 0.88)
        aim_bone_world(rig, "upperarm_r", Vector((-0.20, -0.14, -0.97)))
        aim_bone_world(rig, "lowerarm_r", Vector((0.04, -0.50, -0.86)))
        curl_hand_fingers(rig, "r", 0.35)

    else:  # relaxed
        aim_bone_world(rig, "upperarm_l", Vector((0.20, -0.10, -0.97)))
        aim_bone_world(rig, "lowerarm_l", Vector((-0.04, -0.38, -0.92)))
        aim_bone_world(rig, "upperarm_r", Vector((-0.20, -0.08, -0.98)))
        aim_bone_world(rig, "lowerarm_r", Vector((0.02, -0.32, -0.95)))
        curl_hand_fingers(rig, "l", 0.32)
        curl_hand_fingers(rig, "r", 0.32)

    # 3) Natuerliche Kopfdrehung & leichte Neigung
    rotate_bone_world_axis(rig, "head", (0, 0, 1), head_yaw)
    pitch_deg = ((seed % 5) - 2) * 2.2
    rotate_bone_world_axis(rig, "head", (1, 0, 0), math.radians(pitch_deg))
    bpy.context.view_layer.update()


# ==============================================================================
# HILFSFUNKTIONEN: UV-MAPPING, GEOMETRIE & ORGANISCHE KLEIDUNG / HAARE / SANDALEN
# ==============================================================================
def map_bmesh_faces_to_trim(bm, faces, uv_layer, region_name, mode="planar_cyl"):
    """Mappt alle Loops einer Face-Liste sauber in die angegebene TRIM_REGIONS-Box."""
    u0, v0, u1, v1 = TRIM_REGIONS[region_name]
    du, dv = u1 - u0, v1 - v0
    if not faces:
        return
    zs = [v.co.z for f in faces for v in f.verts]
    zmin, zmax = (min(zs), max(zs)) if zs else (0.0, 1.0)
    zspan = max(1e-4, zmax - zmin)

    for f in faces:
        for loop in f.loops:
            co = loop.vert.co
            if mode == "eye_front":
                continue
            elif mode == "hem_band":
                # V = 0 am unteren Saum (fuer priest_white_lapis & sumerian_border Saumborten!), V = 1 oben
                ang = (math.atan2(co.x, co.y) / (2.0 * math.pi)) + 0.5
                v_n = max(0.0, min(1.0, (co.z - zmin) / zspan))
                u_n = ang
            elif mode == "plain_upper":
                # Nur oberer ungemusterter Stoffbereich (V in 0.28..0.95), ideal fuer Oberteile ohne Borte
                ang = (math.atan2(co.x, co.y) / (2.0 * math.pi)) + 0.5
                v_n = 0.28 + 0.67 * max(0.0, min(1.0, (co.z - zmin) / zspan))
                u_n = ang
            else:
                ang = (math.atan2(co.x, co.y) / (2.0 * math.pi)) + 0.5
                v_n = max(0.0, min(1.0, (co.z - zmin) / zspan))
                u_n = ang
            loop[uv_layer].uv = (u0 + u_n * du, v0 + v_n * dv)


def get_vg_verts(obj, vg_name, min_w=0.5):
    vg = obj.vertex_groups.get(vg_name)
    if vg is None:
        return set()
    idx = vg.index
    res = set()
    for v in obj.data.vertices:
        for g in v.groups:
            if g.group == idx and g.weight >= min_w:
                res.add(v.index)
                break
    return res


def get_vg_center_from_coords(coords, vert_indices):
    if not vert_indices:
        return Vector((0, 0, 1.5))
    c = Vector((0, 0, 0))
    for i in vert_indices:
        c += coords[i]
    return c / len(vert_indices)


def add_eyeball(bm, uv_layer, center, head_fwd, head_right, head_up, radius=0.0124, face_protect_set=None):
    """Konzentrisch nach vorn (+head_fwd) ausgerichteter, hochglaenzender Augapfel (v2.4):
    - Pol zeigt exakt entlang der realen Kopfblickrichtung (head_fwd) -> kein Schielen bei Kopfdrehung!
    - Konzentrische Ringe passen 1:1 auf Pupille, Iris & Limbus (kein kantiges Polygon-Schneiden!).
    """
    fwd = Vector(head_fwd).normalized()
    right = Vector(head_right).normalized()
    up = Vector(head_up).normalized()
    eye_center = Vector(center) + fwd * 0.0018

    # Konzentrische Kugel mit Pol nach +fwd bauen (14 Segmente radial, 8 Breitenringe)
    n_seg = 14
    lat_angles = [0.0, 0.18, 0.38, 0.58, 0.85, 1.25, 1.75, 2.35]  # 0 = Zentrum Pupille (+fwd)
    pole_front = bm.verts.new(eye_center + fwd * radius)
    pole_back = bm.verts.new(eye_center - fwd * radius)
    if face_protect_set is not None:
        face_protect_set.add(pole_front)
        face_protect_set.add(pole_back)

    rings = []
    for theta in lat_angles[1:]:
        ct = math.cos(theta)
        st = math.sin(theta)
        ring = []
        for k in range(n_seg):
            phi = k * 2.0 * math.pi / n_seg
            d = fwd * ct + (right * math.cos(phi) + up * math.sin(phi)) * st
            v = bm.verts.new(eye_center + d * radius)
            if face_protect_set is not None:
                face_protect_set.add(v)
            ring.append(v)
        rings.append(ring)

    eye_faces = []
    # Vorderkappe (Pupille)
    for k in range(n_seg):
        kn = (k + 1) % n_seg
        f = bm.faces.new((pole_front, rings[0][k], rings[0][kn]))
        f.smooth = True
        eye_faces.append(f)
    # Ringe
    for ri in range(len(rings) - 1):
        r0, r1 = rings[ri], rings[ri + 1]
        for k in range(n_seg):
            kn = (k + 1) % n_seg
            f = bm.faces.new((r0[k], r1[k], r1[kn], r0[kn]))
            f.smooth = True
            eye_faces.append(f)
    # Hinterkappe
    for k in range(n_seg):
        kn = (k + 1) % n_seg
        f = bm.faces.new((rings[-1][k], pole_back, rings[-1][kn]))
        f.smooth = True
        eye_faces.append(f)

    bmesh.ops.recalc_face_normals(bm, faces=eye_faces)

    u0, v0, u1, v1 = TRIM_REGIONS["eye_iris"]
    du, dv = u1 - u0, v1 - v0
    for f in eye_faces:
        for loop in f.loops:
            rel = (loop.vert.co - eye_center) / radius
            dot_f = rel.dot(fwd)
            if dot_f > 0.15:
                rx = rel.dot(right)
                rz = rel.dot(up)
                # Natuerliche Iris-Groesse (~52% der Lidoeffnung, exakt zentriert auf Kopfblickrichtung!)
                un = max(0.02, min(0.98, 0.5 + rx * 0.72))
                vn = max(0.02, min(0.98, 0.5 + rz * 0.72))
            else:
                un, vn = 0.06, 0.06
            loop[uv_layer].uv = (u0 + un * du, v0 + vn * dv)
    return [pole_front, pole_back] + [v for r in rings for v in r]


def add_eyebrows(bm, uv_layer, l_eye_c, r_eye_c, head_fwd, head_right, head_up, hair_mat, face_protect_set=None):
    """Organisch gebogene Augenbrauen exakt entlang der realen Kopf-Ausrichtung (head_fwd/right/up)."""
    fwd = Vector(head_fwd).normalized()
    right = Vector(head_right).normalized()
    up = Vector(head_up).normalized()
    u0, v0, u1, v1 = TRIM_REGIONS[hair_mat]
    du, dv = u1 - u0, v1 - v0
    # l_eye_c liegt bei -right (links), r_eye_c bei +right (rechts)
    for side, ec in ((-1.0, l_eye_c), (1.0, r_eye_c)):
        pts = []
        for i in range(6):
            t = i / 5.0  # 0 = innen (Nase), 1 = aussen (Schlaefe)
            d_r = side * (-0.015 + t * 0.034)
            d_u = 0.0175 + math.sin(t * math.pi) * 0.0048 - t * 0.0015
            d_f = 0.0138 - (t - 0.35) ** 2 * 0.013
            pts.append(Vector(ec) + right * d_r + up * d_u + fwd * d_f)
        rings = []
        for i, p in enumerate(pts):
            t = i / 5.0
            rad_u = 0.0030 * (1.0 - 0.45 * abs(t - 0.35))
            rad_f = 0.0020
            ring = []
            for k in range(5):
                ang = k * 2.0 * math.pi / 5.0
                v = bm.verts.new(p + fwd * (math.cos(ang) * rad_f) + up * (math.sin(ang) * rad_u))
                if face_protect_set is not None:
                    face_protect_set.add(v)
                ring.append(v)
            rings.append(ring)
        brow_faces = []
        for i in range(len(rings) - 1):
            r0, r1 = rings[i], rings[i + 1]
            for k in range(5):
                kn = (k + 1) % 5
                try:
                    f = bm.faces.new((r0[k], r0[kn], r1[kn], r1[k]))
                    f.smooth = True
                    brow_faces.append(f)
                except ValueError:
                    pass
        if brow_faces:
            bmesh.ops.recalc_face_normals(bm, faces=brow_faces)
            for f in brow_faces:
                for loop in f.loops:
                    loop[uv_layer].uv = (u0 + 0.5 * du, v0 + 0.5 * dv)


def add_tapered_lock(bm, uv_layer, pts, radii, region_name, segs=6, protect_set=None):
    """Erzeugt eine spitz zulaufende Haar-/Bart-Straehne entlang einer 3D-Kurve (kein Knet-Look!)."""
    if len(pts) < 2:
        return []
    rings = []
    for i, p in enumerate(pts):
        if i == 0:
            tang = (pts[1] - pts[0]).normalized()
        elif i == len(pts) - 1:
            tang = (pts[-1] - pts[-2]).normalized()
        else:
            tang = (pts[i + 1] - pts[i - 1]).normalized()
        ref = Vector((0, 1, 0)) if abs(tang.y) < 0.85 else Vector((1, 0, 0))
        x_ax = tang.cross(ref).normalized()
        y_ax = tang.cross(x_ax).normalized()
        r = max(0.0012, radii[i])
        ring = []
        for k in range(segs):
            ang = k * 2.0 * math.pi / segs
            # Leicht abgeflachte elliptische Haarstraehne
            co = p + x_ax * (math.cos(ang) * r * 1.25) + y_ax * (math.sin(ang) * r * 0.72)
            v = bm.verts.new(co)
            if protect_set is not None:
                protect_set.add(v)
            ring.append(v)
        rings.append(ring)

    faces = []
    for i in range(len(rings) - 1):
        r0, r1 = rings[i], rings[i + 1]
        for k in range(segs):
            kn = (k + 1) % segs
            try:
                f = bm.faces.new((r0[k], r0[kn], r1[kn], r1[k]))
                f.smooth = True
                faces.append(f)
            except ValueError:
                pass
    # Spitze schliessen
    tip = bm.verts.new(pts[-1] + (pts[-1] - pts[-2]).normalized() * 0.005)
    if protect_set is not None:
        protect_set.add(tip)
    for k in range(segs):
        kn = (k + 1) % segs
        try:
            f = bm.faces.new((rings[-1][k], rings[-1][kn], tip))
            f.smooth = True
            faces.append(f)
        except ValueError:
            pass
    if faces:
        bmesh.ops.recalc_face_normals(bm, faces=faces)
        map_bmesh_faces_to_trim(bm, faces, uv_layer, region_name)
    return faces


def build_shell_from_source_faces(bm_out, uv_layer, src_coords, src_normals, src_polys,
                                  face_filter_fn, offset_fn, region_name,
                                  uv_mode="planar_cyl", smooth_iters=2,
                                  feather_boundary=False, protect_set=None):
    """Extrahiert eine saubere einseitige Schale aus MPFB-Polygonen (OHNE nach innen
    umgeklappte dunkle rim_extrude-Streifen -> 0% schwarze Clipping-Dreiecke!).
    """
    selected_polys = [p for p in src_polys if face_filter_fn(p)]
    if not selected_polys:
        return [], []

    vert_map = {}
    new_verts = []
    for p in selected_polys:
        for vi in p:
            if vi not in vert_map:
                co = src_coords[vi]
                no = src_normals[vi]
                new_co = offset_fn(vi, co, no)
                v = bm_out.verts.new(new_co)
                vert_map[vi] = v
                new_verts.append(v)
                if protect_set is not None:
                    protect_set.add(v)

    new_faces = []
    for p in selected_polys:
        fverts = [vert_map[vi] for vi in p]
        try:
            f = bm_out.faces.new(fverts)
            f.smooth = True
            new_faces.append(f)
        except ValueError:
            pass

    if smooth_iters > 0 and new_verts:
        for _ in range(smooth_iters):
            bmesh.ops.smooth_vert(bm_out, verts=new_verts, factor=0.45,
                                  use_axis_x=True, use_axis_y=True, use_axis_z=True)

    # Offene Kanten sanft glaetten (keine Saegezahn-Kontur!)
    b_verts = [v for v in new_verts if v.is_boundary]
    if b_verts and not feather_boundary:
        for _ in range(4):
            bmesh.ops.smooth_vert(bm_out, verts=b_verts, factor=0.55,
                                  use_axis_x=True, use_axis_y=True, use_axis_z=True)

    if feather_boundary and new_verts:
        inv_map = {v: vi for vi, v in vert_map.items()}
        for v in new_verts:
            if v.is_boundary:
                vi = inv_map.get(v)
                if vi is not None:
                    v.co = v.co.lerp(src_coords[vi] + src_normals[vi] * 0.0025, 0.55)

    if new_faces:
        bmesh.ops.recalc_face_normals(bm_out, faces=new_faces)
        map_bmesh_faces_to_trim(bm_out, new_faces, uv_layer, region_name, mode=uv_mode)
    return new_verts, new_faces


def build_collar_band(bm, uv_layer, neck_c, shoulder_l_c, shoulder_r_c, region_name):
    """Sauberer gerundeter Kragen-/Halsausschnitt-Saum (verdeckt den Uebergang Haut->Tunika 100%)."""
    z_col = neck_c.z - 0.036
    rx = min(0.088, abs(shoulder_r_c.x - shoulder_l_c.x) * 0.24)
    ry = rx * 0.92
    n_seg = 24
    tube_r = 0.0075
    cx, cy = neck_c.x, neck_c.y + 0.012

    rings = []
    for i in range(n_seg):
        ang = i * 2.0 * math.pi / n_seg
        # Leichter V-Abfall vorn (+Y -> sin(ang) > 0)
        front_dip = -0.028 * max(0.0, math.sin(ang)) ** 1.4
        px = cx + math.cos(ang) * rx
        py = cy + math.sin(ang) * ry
        pz = z_col + front_dip
        radial = Vector((math.cos(ang), math.sin(ang), 0.0)).normalized()
        up = Vector((0.0, 0.0, 1.0))
        ring = []
        for k in range(6):
            ka = k * 2.0 * math.pi / 6.0
            v = bm.verts.new(Vector((px, py, pz)) + radial * (math.cos(ka) * tube_r) + up * (math.sin(ka) * tube_r * 1.15))
            ring.append(v)
        rings.append(ring)

    faces = []
    for i in range(n_seg):
        r0, r1 = rings[i], rings[(i + 1) % n_seg]
        for k in range(6):
            kn = (k + 1) % 6
            f = bm.faces.new((r0[k], r1[k], r1[kn], r0[kn]))
            f.smooth = True
            faces.append(f)
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    map_bmesh_faces_to_trim(bm, faces, uv_layer, region_name, mode="plain_upper")
    return faces


def build_draped_skirt_extension(bm_out, uv_layer, waist_ring_pts, hem_z, flare,
                                 fold_amp, fold_count, region_name,
                                 uv_mode="hem_band", phase=0.0, hem_cuff=0.010,
                                 leg_bounds=None):
    """Faltenreicher, fliessender Bronzezeit-Rock/Gewand-Unterteil ab der Taille.
    Integriert echte vertikale & leicht gedrehte Schwerkraft-Falten und garantiert Abstand zu Beinen!
    """
    if len(waist_ring_pts) < 8:
        return []
    cx = sum(p.x for p in waist_ring_pts) / len(waist_ring_pts)
    cy = sum(p.y for p in waist_ring_pts) / len(waist_ring_pts)
    cz = sum(p.z for p in waist_ring_pts) / len(waist_ring_pts)

    n_seg = 40
    sorted_pts = sorted(waist_ring_pts, key=lambda p: math.atan2(p.y - cy, p.x - cx))

    def sample_waist(ang):
        return min(sorted_pts, key=lambda p: abs(math.atan2(
            math.sin(math.atan2(p.y - cy, p.x - cx) - ang),
            math.cos(math.atan2(p.y - cy, p.x - cx) - ang))))

    n_rings = 11
    rings = []
    for ri in range(n_rings):
        t = ri / (n_rings - 1)
        z = cz * (1.0 - t) + hem_z * t
        hip_swell = math.sin(min(1.0, t * 2.0) * math.pi) * 0.024
        flare_r = 1.0 + flare * (t ** 1.08)
        fold_scale = (0.18 + 0.82 * (t ** 0.78)) * fold_amp
        # Leichte seitliche Schritt-Weitung falls Beine in Schrittpose stehen (verhindert Knoechel-Durchstich!)
        stride_pad_y = 0.036 * t if leg_bounds is None else max(0.032, leg_bounds[1]) * t
        ring = []
        for si in range(n_seg):
            ang = si * 2.0 * math.pi / n_seg
            wp = sample_waist(ang)
            rx = (wp.x - cx) * flare_r
            ry = (wp.y - cy) * flare_r
            # Organische mehrharmonische Stofffalten (mit sanfter diagonaler Raffung!)
            twist = ang + t * 0.25
            f_wave = (math.sin(twist * fold_count + phase) * 0.58 +
                      math.sin(twist * (fold_count * 2 - 1) - phase * 1.3) * 0.28 +
                      math.cos(twist * 3.0 + phase * 0.6) * 0.14)
            dr = hip_swell + f_wave * fold_scale + stride_pad_y * (abs(math.sin(ang)) ** 1.5)
            ux, uy = math.cos(ang), math.sin(ang)
            dz = math.sin(ang * fold_count + phase) * 0.006 * t
            v = bm_out.verts.new(Vector((cx + rx + ux * dr, cy + ry + uy * dr, z + dz)))
            ring.append(v)
        rings.append(ring)

    # Sanft nach unten-innen abgerundeter Saum (immer korrekte Aussennormalen!)
    if hem_cuff > 0.0:
        inner_ring = []
        for v in rings[-1]:
            dx, dy = v.co.x - cx, v.co.y - cy
            inner_ring.append(bm_out.verts.new(Vector((cx + dx * 0.93, cy + dy * 0.93, v.co.z + hem_cuff))))
        rings.append(inner_ring)

    skirt_faces = []
    for ri in range(len(rings) - 1):
        r0, r1 = rings[ri], rings[ri + 1]
        for si in range(n_seg):
            sn = (si + 1) % n_seg
            f = bm_out.faces.new((r0[si], r0[sn], r1[sn], r1[si]))
            f.smooth = True
            skirt_faces.append(f)

    bmesh.ops.recalc_face_normals(bm_out, faces=skirt_faces)
    map_bmesh_faces_to_trim(bm_out, skirt_faces, uv_layer, region_name, mode=uv_mode)
    return skirt_faces


def build_knotted_sash(bm_out, uv_layer, waist_ring_pts, z_waist, region_name, seed=0):
    """Eng anliegende geknotete Stoff-/Lederschaerpe in der Taille INKL. herabhaengendem Schaerpenende
    (KEIN schwebender flacher Ring mehr!).
    """
    if len(waist_ring_pts) < 8:
        return []
    cx = sum(p.x for p in waist_ring_pts) / len(waist_ring_pts)
    cy = sum(p.y for p in waist_ring_pts) / len(waist_ring_pts)

    sorted_pts = sorted(waist_ring_pts, key=lambda p: math.atan2(p.y - cy, p.x - cx))
    def sample_waist(ang):
        return min(sorted_pts, key=lambda p: abs(math.atan2(
            math.sin(math.atan2(p.y - cy, p.x - cx) - ang),
            math.cos(math.atan2(p.y - cy, p.x - cx) - ang))))

    n_seg = 32
    sash_h = 0.068
    rings = []
    for ri, (dz, rad_mult) in enumerate([(sash_h * 0.5, 1.018), (sash_h * 0.20, 1.046),
                                          (-sash_h * 0.20, 1.048), (-sash_h * 0.5, 1.022)]):
        ring = []
        for si in range(n_seg):
            ang = si * 2.0 * math.pi / n_seg
            wp = sample_waist(ang)
            ripple = 0.0025 * math.sin(ang * 7.0 + ri * 0.9 + seed)
            ux, uy = math.cos(ang), math.sin(ang)
            v = bm_out.verts.new(Vector((
                cx + (wp.x - cx) * rad_mult + ux * ripple,
                cy + (wp.y - cy) * rad_mult + uy * ripple,
                z_waist + dz
            )))
            ring.append(v)
        rings.append(ring)

    faces = []
    for ri in range(len(rings) - 1):
        r0, r1 = rings[ri], rings[ri + 1]
        for si in range(n_seg):
            sn = (si + 1) % n_seg
            f = bm_out.faces.new((r0[si], r0[sn], r1[sn], r1[si]))
            f.smooth = True
            faces.append(f)

    # Knoten + herabhaengendes Schaerpenende vorn-links (ang ~ 115 Grad, +Y vorn, -X links)
    knot_ang = math.radians(112.0 if (seed % 2 == 0) else 68.0)
    kw = sample_waist(knot_ang)
    knot_dir = Vector((math.cos(knot_ang), math.sin(knot_ang), 0.0))
    tang_dir = Vector((-math.sin(knot_ang), math.cos(knot_ang), 0.0))
    knot_c = Vector((cx + (kw.x - cx) * 1.07, cy + (kw.y - cy) * 1.07, z_waist - 0.005))

    # Geknotetes Polster
    ret = bmesh.ops.create_uvsphere(bm_out, u_segments=10, v_segments=7, radius=0.024)
    for v in ret["verts"]:
        v.co.z *= 0.85
        v.co += knot_c
    knot_faces = list({f for v in ret["verts"] for f in v.link_faces})
    for f in knot_faces:
        f.smooth = True
    faces.extend(knot_faces)

    # Herabhaengender gefalteter Schaerpen-Streifen (~30 cm lang)
    tail_rings = []
    tail_len = 0.28 + (seed % 3) * 0.04
    for ri in range(7):
        t = ri / 6.0
        z = knot_c.z - t * tail_len
        out_push = 0.016 + t * 0.042  # folgt Rock-Flare nach aussen -> 0% Clipping!
        w_half = 0.026 + t * 0.014
        ring = []
        for s_i, s_val in enumerate((-1.0, -0.35, 0.35, 1.0)):
            fold_o = 0.005 * math.cos(s_val * math.pi)
            p = Vector((knot_c.x, knot_c.y, z)) + knot_dir * (out_push + fold_o) + tang_dir * (s_val * w_half)
            ring.append(bm_out.verts.new(p))
        tail_rings.append(ring)
    for ri in range(len(tail_rings) - 1):
        r0, r1 = tail_rings[ri], tail_rings[ri + 1]
        for si in range(3):
            f = bm_out.faces.new((r0[si], r0[si + 1], r1[si + 1], r1[si]))
            f.smooth = True
            faces.append(f)

    bmesh.ops.recalc_face_normals(bm_out, faces=faces)
    uv_m = "hem_band" if region_name in ("sumerian_border", "priest_white_lapis") else "planar_cyl"
    map_bmesh_faces_to_trim(bm_out, faces, uv_layer, region_name, mode=uv_m)
    return faces


def build_diagonal_mantle(bm_out, uv_layer, coords, normals, body_polys,
                          torso_vg, upperarm_vg, forearm_hand_vg, head_neck_vg,
                          shoulder_l_c, shoulder_r_c, neck_c, z_waist, z_neck, region_name, seed=0):
    """Weich anliegender mesopotamischer Schultermantel / Wickelschal (v2.1):
    Direkt aus der anatomischen MPFB-Torso- & linken Schulterrundung extrahiert + weich abgerundete
    Diagonalkante -> legt sich organisch um die Schulter (0% steife 90-Grad-Papp-Ecken, 0% Rock-Clipping!).
    """
    def mantle_filter(p):
        if any(i in forearm_hand_vg or i in head_neck_vg for i in p):
            return False
        # Torso + oberste Schulterkappe links (-X) einschliessen, rechten Arm (+X) frei lassen!
        for i in p:
            if i in torso_vg:
                continue
            if i in upperarm_vg and coords[i].x < neck_c.x - 0.02 and (coords[i] - shoulder_l_c).length < 0.13:
                continue
            return False
        c = sum((coords[i] for i in p), Vector((0, 0, 0))) / len(p)
        if c.z > z_neck - 0.026 or c.z < z_waist - 0.010:
            return False
        # Diagonale Oberkante: ueber linker Schulter (-X) hoch, unter rechtem Arm (+X) tief
        dx = c.x - neck_c.x
        max_z_here = (z_neck - 0.026) - max(0.0, (dx + 0.045)) * 0.92
        if c.z > max_z_here:
            return False
        return True

    def mantle_offset(vi, co, no):
        ang = math.atan2(co.x - neck_c.x, co.y - neck_c.y)
        fold = 0.0035 * math.sin(ang * 7.0 + co.z * 16.0 + seed)
        # Strikt +9..11 mm AUSSERHALB der Tunika (inkl. Aermel-Weitung auf linker Schulter!) -> 0.0% Durchstich!
        sleeve_extra = 0.011 if (vi in upperarm_vg) else 0.0
        return co + no * (0.0275 + sleeve_extra + fold)

    m_verts, m_faces = build_shell_from_source_faces(
        bm_out, uv_layer, coords, normals, body_polys,
        mantle_filter, mantle_offset, region_name,
        uv_mode="hem_band" if region_name in ("sumerian_border", "priest_white_lapis") else "planar_cyl",
        smooth_iters=2
    )
    # Sanfte Glaettung nur der freien Diagonalkante (ohne Einziehen in die Tunika!)
    b_verts = [v for v in m_verts if v.is_boundary]
    if b_verts:
        for _ in range(3):
            bmesh.ops.smooth_vert(bm_out, verts=b_verts, factor=0.40,
                                  use_axis_x=True, use_axis_y=True, use_axis_z=True)
    if m_faces:
        bmesh.ops.recalc_face_normals(bm_out, faces=m_faces)
    return m_faces


def build_draped_veil(bm_out, uv_layer, head_c, l_eye_c, neck_c, shoulder_l_c, shoulder_r_c, region_name, seed=0):
    """Weich fallendes bronzezeitliches Kopftuch / Schleier fuer Frauen (v2.1):
    Schmiegt sich sanft an Wangen & Hals an und legt sich flach auf die Schultern
    (KEINE steifen dreieckigen Zelt-Fluegel mehr!).
    """
    n_u = 22
    n_v = 12
    rings = []

    z_crown = head_c.z + 0.115
    z_neck_mid = neck_c.z + 0.015
    z_sh = (shoulder_l_c.z + shoulder_r_c.z) * 0.5 - 0.015
    sh_half_w = max(0.155, abs(shoulder_r_c.x - shoulder_l_c.x) * 0.50)

    for vi in range(n_v):
        tv = vi / (n_v - 1)  # 0 = Scheitel, 0.35 = Schlaefen/Ohren, 0.65 = Hals-Einzug, 1.0 = flach auf Schultern
        ring = []
        for ui in range(n_u):
            tu = ui / (n_u - 1)  # 0 = rechte Wange, 0.5 = Hinterkopf/Ruecken, 1 = linke Wange
            # Enger nach vorn an die Wangen gezogen (+56 Grad ueber Hinten bis -236 Grad)
            ang = math.radians(56.0 - tu * 292.0)
            ux, uy = math.cos(ang), math.sin(ang)

            if tv < 0.34:
                # Weiche Scheitelkuppel eng am Kopf
                st = tv / 0.34
                r_head_x = 0.028 + 0.072 * math.sin(st * math.pi * 0.5)
                r_head_y = 0.032 + 0.088 * math.sin(st * math.pi * 0.5)
                z = z_crown - 0.072 * (st ** 1.35)
                cx_t, cy_t = head_c.x, head_c.y - 0.008
            elif tv < 0.68:
                # Weich nach INNEN an Wangen & Hals anliegend (beseitigt Zelt-Fluegel 100%!)
                st = (tv - 0.34) / 0.34
                r_head_x = 0.100 * (1.0 - st) + 0.078 * st
                r_head_y = 0.120 * (1.0 - st) + 0.102 * st
                z = (z_crown - 0.072) * (1.0 - st) + z_neck_mid * st
                cx_t = head_c.x * (1.0 - st) + neck_c.x * st
                cy_t = (head_c.y - 0.008) * (1.0 - st) + (neck_c.y - 0.015) * st
            else:
                # Legt sich flach & weich ueber die Schultern & den oberen Ruecken
                st = (tv - 0.68) / 0.32
                smooth_st = st * st * (3.0 - 2.0 * st)
                r_head_x = 0.078 * (1.0 - smooth_st) + sh_half_w * smooth_st
                r_head_y = 0.102 * (1.0 - smooth_st) + 0.132 * smooth_st
                z = z_neck_mid * (1.0 - smooth_st) + z_sh * smooth_st
                cx_t = neck_c.x
                cy_t = (neck_c.y - 0.015) * (1.0 - smooth_st) + (neck_c.y - 0.025) * smooth_st

            # Subtile weiche Falten (nur hinten & unten)
            fold = 0.0045 * math.sin(tu * math.pi * 6.0 + seed) * (tv ** 1.2)
            y_pos = cy_t + uy * (r_head_y + fold)
            # Gesicht vorn klar frei lassen
            if y_pos > l_eye_c.y - 0.022 and tv < 0.62:
                y_pos = l_eye_c.y - 0.022 - (0.62 - tv) * 0.010

            v = bm_out.verts.new(Vector((cx_t + ux * (r_head_x + fold), y_pos, z)))
            ring.append(v)
        rings.append(ring)

    faces = []
    for vi in range(n_v - 1):
        r0, r1 = rings[vi], rings[vi + 1]
        for ui in range(n_u - 1):
            f = bm_out.faces.new((r0[ui], r0[ui + 1], r1[ui + 1], r1[ui]))
            f.smooth = True
            faces.append(f)

    crown_v = bm_out.verts.new(Vector((head_c.x, head_c.y - 0.010, z_crown + 0.004)))
    for ui in range(n_u - 1):
        try:
            f = bm_out.faces.new((crown_v, rings[0][ui + 1], rings[0][ui]))
            f.smooth = True
            faces.append(f)
        except ValueError:
            pass

    bmesh.ops.recalc_face_normals(bm_out, faces=faces)
    uv_m = "plain_upper" if region_name in ("sumerian_border", "priest_white_lapis") else "planar_cyl"
    map_bmesh_faces_to_trim(bm_out, faces, uv_layer, region_name, mode=uv_m)
    return faces


def build_strap_sandal(bm, uv_layer, coords, normals, body_polys, foot_vg, ankle_pos, toe_pos, protect_set=None):
    """Anatomisch perfekt anliegende Bronzezeit-Leder-Sandale (v2.2):
    - KEINE abstehenden Draht-Buegel!
    - Sohle schliesst buendig von Z=0.000 m bis direkt in die reale Fussohle (0 mm Spalt!)
    - Breite, glatte Lederriemen (Spannband + Fersenband) DIREKT von der echten 3D-MPFB-Fusshaut
      abgeformt (+4 mm Offset) -> schmiegen sich 100% organisch an den Fuss!
    """
    foot_verts_coords = [coords[vi] for vi in foot_vg if vi < len(coords)]
    if not foot_verts_coords:
        return []
    fwd = Vector((toe_pos.x - ankle_pos.x, toe_pos.y - ankle_pos.y, 0.0))
    if fwd.length < 1e-3:
        fwd = Vector((0.0, 1.0, 0.0))
    else:
        fwd.normalize()
    right = Vector((fwd.y, -fwd.x, 0.0)).normalized()

    projs_f = [((c - ankle_pos).x * fwd.x + (c - ankle_pos).y * fwd.y) for c in foot_verts_coords]
    projs_r = [((c - ankle_pos).x * right.x + (c - ankle_pos).y * right.y) for c in foot_verts_coords]
    f_min, f_max = min(projs_f) - 0.004, max(projs_f) + 0.005
    r_min, r_max = min(projs_r) - 0.002, max(projs_r) + 0.002
    r_mid = 0.5 * (r_min + r_max)
    half_w = max(0.033, 0.50 * (r_max - r_min))
    foot_len = max(0.19, f_max - f_min)
    foot_z_min = min(c.z for c in foot_verts_coords)

    # 1) Konturierte Ledersohle von Z = 0.000 m exakt bis in die reale Fusssohle (foot_z_min + 4 mm -> 0% Spalt!)
    z_bot = 0.0
    z_top = max(0.010, foot_z_min + 0.004)

    contour_2d = []
    n_c = 18
    for i in range(n_c):
        ang = i * 2.0 * math.pi / n_c
        s_f = math.sin(ang)  # -1 = Ferse, +1 = Zehen
        s_r = math.cos(ang)  # -1..+1 Breite
        t_len = 0.5 * (s_f + 1.0)
        w_profile = 0.72 + 0.28 * math.sin(min(1.0, t_len * 1.12) * math.pi)
        fl = f_min + t_len * foot_len
        rl = r_mid + s_r * half_w * w_profile
        contour_2d.append((fl, rl))

    bot_ring, top_ring = [], []
    for fl, rl in contour_2d:
        xy = Vector((ankle_pos.x, ankle_pos.y, 0.0)) + fwd * fl + right * rl
        vb = bm.verts.new(Vector((xy.x, xy.y, z_bot)))
        vt = bm.verts.new(Vector((xy.x, xy.y, z_top)))
        if protect_set is not None:
            protect_set.add(vb)
            protect_set.add(vt)
        bot_ring.append(vb)
        top_ring.append(vt)

    faces = []
    for i in range(n_c):
        inext = (i + 1) % n_c
        f = bm.faces.new((bot_ring[i], bot_ring[inext], top_ring[inext], top_ring[i]))
        f.smooth = True
        faces.append(f)
    faces.append(bm.faces.new(list(reversed(bot_ring))))
    faces.append(bm.faces.new(top_ring))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    map_bmesh_faces_to_trim(bm, faces, uv_layer, "leather_worn")

    # 2) Anatomisch anliegende Lederriemen DIREKT aus der 3D-MPFB-Fussoberflaeche!
    #    - Breites Spann-Lederband (t in 0.42..0.64, hinter den Zehen!)
    #    - Fersen-/Knoechel-Halteband (t in 0.00..0.24)
    def strap_filter(p):
        if not all(vi in foot_vg for vi in p):
            return False
        c = sum((coords[vi] for vi in p), Vector((0, 0, 0))) / len(p)
        if c.z < foot_z_min + 0.004 or c.z > foot_z_min + 0.082:
            return False
        pf = ((c - ankle_pos).x * fwd.x + (c - ankle_pos).y * fwd.y)
        t = (pf - f_min) / max(0.15, foot_len)
        in_instep = (0.42 <= t <= 0.64)
        in_heel = (t <= 0.24 and c.z < foot_z_min + 0.058)
        return in_instep or in_heel

    def strap_offset(vi, co, no):
        # Glatt 4.5 mm ueber der echten Fusshaut anliegend -> 0% Draht-Schlaufen, 0% Durchstich!
        return co + no * 0.0045

    _, strap_faces = build_shell_from_source_faces(
        bm, uv_layer, coords, normals, body_polys,
        strap_filter, strap_offset, "leather_worn",
        smooth_iters=2, protect_set=protect_set
    )
    faces.extend(strap_faces)
    return faces


def add_cylinder_part(bm, uv_layer, p0, p1, r0, r1, region_name, segs=10):
    v0, v1 = Vector(p0), Vector(p1)
    axis = v1 - v0
    if axis.length < 1e-4:
        return [], []
    z_ax = axis.normalized()
    ref = Vector((0, 0, 1)) if abs(z_ax.z) < 0.9 else Vector((1, 0, 0))
    x_ax = z_ax.cross(ref).normalized()
    y_ax = z_ax.cross(x_ax).normalized()

    r_bot, r_top = [], []
    for i in range(segs):
        ang = i * 2.0 * math.pi / segs
        d = x_ax * math.cos(ang) + y_ax * math.sin(ang)
        r_bot.append(bm.verts.new(v0 + d * r0))
        r_top.append(bm.verts.new(v1 + d * r1))

    faces = []
    for i in range(segs):
        inext = (i + 1) % segs
        f = bm.faces.new((r_bot[i], r_bot[inext], r_top[inext], r_top[i]))
        f.smooth = True
        faces.append(f)
    faces.append(bm.faces.new(list(reversed(r_bot))))
    faces.append(bm.faces.new(r_top))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    map_bmesh_faces_to_trim(bm, faces, uv_layer, region_name)
    return r_bot + r_top, faces


def add_lathe_prop(bm, uv_layer, base_pos, axis_up, profile, region_name, segs=14):
    z_ax = Vector(axis_up).normalized()
    ref = Vector((1, 0, 0)) if abs(z_ax.x) < 0.9 else Vector((0, 1, 0))
    x_ax = z_ax.cross(ref).normalized()
    y_ax = z_ax.cross(x_ax).normalized()
    bp = Vector(base_pos)

    rings = []
    all_verts = []
    for h, r in profile:
        ring = []
        for i in range(segs):
            ang = i * 2.0 * math.pi / segs
            d = x_ax * math.cos(ang) + y_ax * math.sin(ang)
            v = bm.verts.new(bp + z_ax * h + d * max(0.002, r))
            ring.append(v)
            all_verts.append(v)
        rings.append(ring)

    faces = []
    for ri in range(len(rings) - 1):
        r0, r1 = rings[ri], rings[ri + 1]
        for i in range(segs):
            inext = (i + 1) % segs
            f = bm.faces.new((r0[i], r0[inext], r1[inext], r1[i]))
            f.smooth = True
            faces.append(f)
    faces.append(bm.faces.new(list(reversed(rings[0]))))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    map_bmesh_faces_to_trim(bm, faces, uv_layer, region_name)
    return all_verts, faces


def add_box_part(bm, uv_layer, center, size_xyz, rot_euler, region_name):
    ret = bmesh.ops.create_cube(bm, size=1.0)
    verts = ret["verts"]
    mat = Matrix.Translation(Vector(center)) @ Euler(rot_euler, "XYZ").to_matrix().to_4x4() @ Matrix.Diagonal((*size_xyz, 1.0))
    for v in verts:
        v.co = mat @ v.co
    faces = list({f for v in verts for f in v.link_faces})
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    map_bmesh_faces_to_trim(bm, faces, uv_layer, region_name)
    return verts, faces


def add_prop_at_anchors(bm, uv_layer, prop_name, anchors, max_top_z):
    """Platziert Requisiten EXAKT an den evaluierten Hand-/Schulter-Ankern (0% Clipping, 0% Schweben!).
    Nach 180-Grad-Z-Drehung gilt: +Y = Vorne, +Z = Oben, RECHTS = +X, LINKS = -X!
    Gibt Liste aller Prop-Vertices fuer die automatische Kopf-/Hals-Kollisions-Assertion zurueck.
    """
    prop_verts = []
    if not prop_name or prop_name == "none":
        return prop_verts

    hr = anchors["grip_r"]
    hl = anchors["grip_l"]
    sr = anchors["shoulder_r"]
    front_chest = anchors["front_hold"]
    hand_sep = (anchors["grip_r"] - anchors["grip_l"]).length

    if prop_name == "staff":
        # Wander-/Messstab: laeuft EXAKT durch die anatomische Griff-Mitte (grip_r) bis Z = 0.0!
        staff_top_z = min(max_top_z - 0.04, hr.z + 0.56)
        bot = Vector((hr.x, hr.y, 0.0))
        top = Vector((hr.x, hr.y, staff_top_z))
        vs, _ = add_cylinder_part(bm, uv_layer, bot, top, 0.0135, 0.0155, "cedar_wood", segs=10)
        prop_verts.extend(vs)
        vs, _ = add_lathe_prop(bm, uv_layer, top - Vector((0, 0, 0.018)), (0, 0, 1),
                               [(0.0, 0.0155), (0.022, 0.025), (0.048, 0.021), (0.064, 0.010)], "cedar_wood", segs=10)
        prop_verts.extend(vs)
        vs, _ = add_cylinder_part(bm, uv_layer, hr + Vector((0, 0, -0.040)), hr + Vector((0, 0, 0.040)),
                                  0.0165, 0.0165, "tin_bronze", segs=10)
        prop_verts.extend(vs)

    elif prop_name == "carpenter_adze":
        # v2.3 FIX: Stiel laeuft EXAKT durch grip_r (0 mm Hand-Clipping!), klar ablesbare Bronzeklinge!
        axis = Vector((-0.14, 0.16, 0.977)).normalized()
        p0 = hr - axis * 0.11
        p1 = hr + axis * 0.27
        vs, _ = add_cylinder_part(bm, uv_layer, p0, p1, 0.0135, 0.0155, "cedar_wood", segs=10)
        prop_verts.extend(vs)
        vs, _ = add_box_part(bm, uv_layer, p1 + Vector((-0.035, 0.015, -0.015)), (0.115, 0.028, 0.052), (0.08, -0.18, 0.22), "tin_bronze")
        prop_verts.extend(vs)
        vs, _ = add_cylinder_part(bm, uv_layer, p1 - axis * 0.032, p1 + axis * 0.010,
                                  0.021, 0.021, "leather_worn", segs=8)
        prop_verts.extend(vs)

    elif prop_name == "mallet":
        axis = Vector((-0.12, 0.16, 0.980)).normalized()
        p0 = hr - axis * 0.09
        p1 = hr + axis * 0.24
        vs, _ = add_cylinder_part(bm, uv_layer, p0, p1, 0.0135, 0.0155, "cedar_wood", segs=10)
        prop_verts.extend(vs)
        vs, _ = add_cylinder_part(bm, uv_layer, p1 + Vector((-0.058, -0.015, 0.015)), p1 + Vector((0.058, 0.015, -0.015)),
                                  0.042, 0.042, "cedar_wood", segs=12)
        prop_verts.extend(vs)

    elif prop_name == "smith_hammer":
        axis = Vector((-0.12, 0.16, 0.980)).normalized()
        p0 = hr - axis * 0.09
        p1 = hr + axis * 0.25
        vs, _ = add_cylinder_part(bm, uv_layer, p0, p1, 0.0135, 0.0155, "cedar_wood", segs=10)
        prop_verts.extend(vs)
        vs, _ = add_box_part(bm, uv_layer, p1, (0.112, 0.042, 0.042), (0.08, -0.15, 0.22), "tin_bronze")
        prop_verts.extend(vs)

    elif prop_name == "pitch_ladle":
        axis = Vector((-0.10, 0.34, 0.935)).normalized()
        p0 = hr - axis * 0.10
        p1 = hr + axis * 0.32
        vs, _ = add_cylinder_part(bm, uv_layer, p0, p1, 0.0125, 0.0145, "cedar_wood", segs=10)
        prop_verts.extend(vs)
        vs, _ = add_lathe_prop(bm, uv_layer, p1 + Vector((0.0, 0.02, -0.04)), (0, 0, 1),
                               [(0.0, 0.024), (0.02, 0.060), (0.066, 0.068), (0.070, 0.058)], "tin_bronze", segs=12)
        prop_verts.extend(vs)

    elif prop_name == "shoulder_beam":
        # v2.3 FIX: Unterkante des 10.5cm-Balkens liegt sauber AUF der gekruemmten Hand (+6.8 cm ueber grip_r -> 0% Hand-Clipping!)
        p_sh = sr + Vector((0.105, -0.02, 0.082))
        p_hd = hr + Vector((0.0,    0.01, 0.068))
        b_dir = (p_hd - p_sh)
        if b_dir.length < 0.08:
            b_dir = Vector((0.04, 1.0, 0.06))
        b_dir.normalize()
        beam_c = p_sh + b_dir * 0.16
        yaw = math.atan2(-b_dir.x, b_dir.y)
        pitch = math.asin(max(-0.5, min(0.5, b_dir.z)))
        vs, _ = add_box_part(bm, uv_layer, beam_c, (0.105, 1.28, 0.105), (pitch, 0.0, yaw), "cedar_wood")
        prop_verts.extend(vs)

    elif prop_name == "shoulder_sack":
        sack_c = sr + Vector((0.115, -0.04, 0.098))
        vs, _ = add_lathe_prop(bm, uv_layer, sack_c + Vector((0.0, -0.20, 0.0)), (0.08, 1.0, 0.14),
                               [(0.0, 0.036), (0.08, 0.100), (0.21, 0.112), (0.34, 0.100), (0.42, 0.036)], "jute_basket", segs=12)
        prop_verts.extend(vs)

    elif prop_name == "jar_hip":
        # v2.3 FIX: Bauchradius exakt an den realen Handabstand angepasst -> Haende liegen aussen am Krug an (0% Finger-Clipping!)
        r_scale = max(0.72, min(0.95, (hand_sep * 0.43) / 0.110))
        jar_base = front_chest + Vector((0.025, 0.035, -0.115))
        vs, _ = add_lathe_prop(bm, uv_layer, jar_base, (0.03, 0.04, 1.0),
                               [(0.0, 0.050 * r_scale), (0.058, 0.100 * r_scale), (0.142, 0.110 * r_scale),
                                (0.215, 0.068 * r_scale), (0.270, 0.044 * r_scale), (0.305, 0.056 * r_scale)],
                               "terracotta", segs=14)
        prop_verts.extend(vs)

    elif prop_name == "jar_front":
        r_scale = max(0.72, min(0.95, (hand_sep * 0.43) / 0.112))
        jar_base = front_chest + Vector((0.0, 0.040, -0.115))
        vs, _ = add_lathe_prop(bm, uv_layer, jar_base, (0, 0.04, 1.0),
                               [(0.0, 0.052 * r_scale), (0.06, 0.102 * r_scale), (0.145, 0.112 * r_scale),
                                (0.22, 0.068 * r_scale), (0.275, 0.044 * r_scale), (0.31, 0.058 * r_scale)],
                               "terracotta", segs=14)
        prop_verts.extend(vs)

    elif prop_name == "basket_l":
        b_base = Vector((hl.x - 0.065, hl.y + 0.035, hl.z - 0.095))
        vs, _ = add_lathe_prop(bm, uv_layer, b_base, (-0.08, 0.05, 1.0),
                               [(0.0, 0.072), (0.045, 0.108), (0.125, 0.132), (0.175, 0.142), (0.180, 0.124)], "jute_basket", segs=14)
        prop_verts.extend(vs)

    elif prop_name == "scroll_l":
        # Schriftrolle exakt durch grip_l
        s_ax = Vector((0.88, 0.25, 0.40)).normalized()
        p0 = hl - s_ax * 0.08
        p1 = hl + s_ax * 0.09
        vs, _ = add_cylinder_part(bm, uv_layer, p0, p1, 0.015, 0.015, "linen_unbleached", segs=10)
        prop_verts.extend(vs)
        vs, _ = add_cylinder_part(bm, uv_layer, p0 - s_ax * 0.022, p0, 0.009, 0.009, "cedar_wood", segs=8)
        prop_verts.extend(vs)
        vs, _ = add_cylinder_part(bm, uv_layer, p1, p1 + s_ax * 0.022, 0.009, 0.009, "cedar_wood", segs=8)
        prop_verts.extend(vs)

    elif prop_name == "priest_censer":
        c_base = hl + Vector((0.0, 0.015, 0.012))
        vs, _ = add_lathe_prop(bm, uv_layer, c_base, (0, 0, 1),
                               [(0.0, 0.024), (0.028, 0.030), (0.065, 0.072), (0.10, 0.086), (0.105, 0.074)], "tin_bronze", segs=14)
        prop_verts.extend(vs)

    elif prop_name == "oar":
        oar_top_z = min(max_top_z - 0.16, hr.z + 0.56)
        bot = Vector((hr.x, hr.y, 0.0))
        top = Vector((hr.x, hr.y, oar_top_z))
        vs, _ = add_cylinder_part(bm, uv_layer, bot, top, 0.0135, 0.014, "cedar_wood", segs=10)
        prop_verts.extend(vs)
        vs, _ = add_box_part(bm, uv_layer, top + Vector((0, 0, 0.09)), (0.10, 0.016, 0.22), (0, 0, 0), "cedar_wood")
        prop_verts.extend(vs)

    elif prop_name == "sickle":
        axis = Vector((-0.10, 0.35, 0.93)).normalized()
        p0 = hr - axis * 0.06
        p1 = hr + axis * 0.14
        vs, _ = add_cylinder_part(bm, uv_layer, p0, p1, 0.0125, 0.014, "cedar_wood", segs=8)
        prop_verts.extend(vs)
        vs, _ = add_box_part(bm, uv_layer, p1 + Vector((-0.05, 0.05, 0.03)), (0.14, 0.028, 0.014), (0.1, -0.25, 0.55), "tin_bronze")
        prop_verts.extend(vs)

    elif prop_name == "spindle_cloth":
        axis = Vector((0.12, 0.30, 0.946)).normalized()
        p0 = hr - axis * 0.09
        p1 = hr + axis * 0.13
        vs, _ = add_cylinder_part(bm, uv_layer, p0, p1, 0.008, 0.008, "cedar_wood", segs=8)
        prop_verts.extend(vs)
        vs, _ = add_lathe_prop(bm, uv_layer, hr + axis * 0.03, axis,
                               [(0.0, 0.008), (0.03, 0.026), (0.06, 0.008)], "wool_ochre", segs=10)
        prop_verts.extend(vs)

    return prop_verts


# ==============================================================================
# COL_RIG AUS MPFB-KOERPERZONEN ABLEITEN
# ==============================================================================
def assign_col_rig_from_zones(obj, z_hip, z_shoulder, z_neck):
    """Schreibt Color Attribute 'Col_Rig' (1:1 kompatibel mit Arche.Fauna.getFaunaVertexDeformGLSL)."""
    mesh = obj.data
    col_attr = mesh.color_attributes.get("Col_Rig")
    if col_attr is None:
        col_attr = mesh.color_attributes.new(name="Col_Rig", type="BYTE_COLOR", domain="CORNER")

    for poly in mesh.polygons:
        for li in poly.loop_indices:
            co = mesh.vertices[mesh.loops[li].vertex_index].co
            x, y, z = co.x, co.y, co.z

            if z >= z_neck:
                r = 0.667
                limb_w = min(1.0, max(0.0, (z - z_neck) / 0.28))
            elif z < z_hip and abs(x) < 0.26:
                r = 0.0
                limb_w = min(1.0, max(0.0, (z_hip - z) / max(0.1, z_hip)))
            elif abs(x) > 0.195 and z > z_hip - 0.18:
                r = 1.0
                limb_w = min(1.0, max(0.0, (abs(x) - 0.195) / 0.28))
            else:
                r = 0.333
                limb_w = min(1.0, max(0.0, abs(z - z_shoulder) / 0.65)) * 0.25

            if x < -0.02:
                g = 0.0
            elif x > 0.02:
                g = 1.0
            else:
                g = 0.5
            col_attr.data[li].color = (r, g, limb_w, 1.0)


# ==============================================================================
# KERN-BUILDER v2: 1 KOMPLETTER MPFB-CHARAKTER MIT GROESSEN- & KOLLISIONS-CHECK
# ==============================================================================
def build_mpfb_character(spec, mat, HumanService, TargetService, RigService, collection):
    """Erzeugt 1 anatomische MPFB-Figur v2 mit:
      - Strikter Koerpergroessen-Normierung (Frauen 1.61..1.69 m, Maenner 1.73..1.82 m, Z = 0.000 m)
      - 0% Haut-/Kleidungs-Clipping durch vollstaendiges Loeschen verdeckter Haut-Polygone
      - Geknotete Schaerpe mit Haengeende, diagonaler Wickelmantel, weicher Schleier, gestraehnte Haare/Baerte
      - Konturierte Riemensandalen ODER saubere nackte Fuesse
      - Automatische Prop-Kopf-Kollisionspruefung (>= 5.5 cm Abstand)
    """
    is_fem = (spec["gender"] == "F")
    pheno = spec["phenotype"]
    seed = spec.get("seed", 0)
    target_height = float(spec["target_height"])
    wears_sandals = bool(spec.get("sandals", True))

    # 1) MPFB Macro-Detail-Dictionary (neutrale MPFB-Hoehe 0.50; exakte Normierung erfolgt ueber BBox!)
    macro = TargetService.get_default_macro_info_dict()
    macro["gender"] = 0.0 if is_fem else 1.0
    macro["age"] = float(spec.get("age", 0.54))
    macro["muscle"] = float(spec.get("muscle", 0.40 if is_fem else 0.58))
    macro["weight"] = float(spec.get("weight", 0.48 if is_fem else 0.52))
    macro["height"] = 0.50
    macro["proportions"] = 0.52
    if is_fem:
        macro["cupsize"] = 0.50
        macro["firmness"] = 0.55

    if pheno == "hamitic":
        macro["race"] = {"african": 0.88, "caucasian": 0.08, "asian": 0.04}
        skin_mat = "skin_hamitic"
    elif pheno == "japhetic":
        macro["race"] = {"caucasian": 0.90, "asian": 0.06, "african": 0.04}
        skin_mat = "skin_japhetic"
    else:
        macro["race"] = {"caucasian": 0.62, "asian": 0.22, "african": 0.16}
        skin_mat = "skin_semitic"

    # 2) MPFB Human & Rig erzeugen
    mpfb_obj = HumanService.create_human(
        mask_helpers=False,
        detailed_helpers=True,
        extra_vertex_groups=True,
        feet_on_ground=True,
        scale=0.1,
        macro_detail_dict=macro,
    )
    rig = HumanService.add_builtin_rig(mpfb_obj, "game_engine", import_weights=True)

    # 3) Natuerliche Pose auf Rig anwenden
    apply_natural_pose(rig, spec.get("arm_pose", "relaxed"), seed=seed)

    # 4) Deformiertes Mesh evaluieren & exakt um 180 Grad um Z drehen (+Y Vorne) + BBox-Hoehe normieren!
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = mpfb_obj.evaluated_get(depsgraph)
    eval_mesh = eval_obj.to_mesh()

    rot180 = Matrix.Rotation(math.pi, 4, "Z")
    body_vg = get_vg_verts(mpfb_obj, "body", 0.5)
    scalp_vg = get_vg_verts(mpfb_obj, "scalp", 0.5)
    lips_vg = get_vg_verts(mpfb_obj, "lips", 0.5)
    ears_vg = get_vg_verts(mpfb_obj, "ears", 0.5)
    l_eye_vg = get_vg_verts(mpfb_obj, "joint-l-eye", 0.5)
    r_eye_vg = get_vg_verts(mpfb_obj, "joint-r-eye", 0.5)
    head_vg = get_vg_verts(mpfb_obj, "joint-head", 0.5)
    jaw_vg = get_vg_verts(mpfb_obj, "joint-jaw", 0.5)

    raw_coords = [rot180 @ v.co for v in eval_mesh.vertices]
    body_zs = [raw_coords[i].z for i in body_vg]
    raw_z_min = min(body_zs) if body_zs else 0.0
    raw_z_max = max(body_zs) if body_zs else 1.70
    raw_h = max(0.5, raw_z_max - raw_z_min)

    # Zuschlag fuer Haare/Schleier/Kappe + Sandalen-Sohle beruecksichtigen, damit finale Gesamthoehe exakt stimmt!
    headwear = spec.get("headwear", "none")
    top_allowance = 0.022 if headwear in ("veil", "priest_cap") else 0.014
    sole_z = 0.008 if wears_sandals else 0.0
    target_body_h = target_height - top_allowance - sole_z
    scale_h = target_body_h / raw_h

    def xform_pt(pt_rot180):
        return Vector((
            pt_rot180.x * scale_h,
            pt_rot180.y * scale_h,
            (pt_rot180.z - raw_z_min) * scale_h + sole_z,
        ))

    coords = [xform_pt(c) for c in raw_coords]
    normals = [(rot180.to_3x3() @ v.normal).normalized() for v in eval_mesh.vertices]

    def bone_pos(bname, at_tail=False):
        pb = rig.pose.bones.get(bname)
        if pb is None:
            return Vector((0, 0, 1.0))
        p = pb.tail if at_tail else pb.head
        return xform_pt(rot180 @ p)

    hand_r_c = (bone_pos("hand_r", False) + bone_pos("middle_01_r", False)) * 0.5
    hand_l_c = (bone_pos("hand_l", False) + bone_pos("middle_01_l", False)) * 0.5
    # Anatomisches Zentrum der geschlossenen Griff-Hoehlung (zwischen Mittelhand, gekruemmtem Mittelfinger & Daumen!)
    grip_r_c = (bone_pos("middle_01_r", False) + bone_pos("middle_02_r", True) + bone_pos("thumb_02_r", True)) / 3.0
    grip_l_c = (bone_pos("middle_01_l", False) + bone_pos("middle_02_l", True) + bone_pos("thumb_02_l", True)) / 3.0
    shoulder_r_c = bone_pos("upperarm_r", False)
    shoulder_l_c = bone_pos("upperarm_l", False)
    neck_c = bone_pos("neck_01", False)
    head_c = get_vg_center_from_coords(coords, head_vg)
    jaw_c = get_vg_center_from_coords(coords, jaw_vg)
    lips_c = get_vg_center_from_coords(coords, lips_vg)
    l_eye_c = get_vg_center_from_coords(coords, l_eye_vg)
    r_eye_c = get_vg_center_from_coords(coords, r_eye_vg)
    pelvis_c = bone_pos("pelvis", False)
    knee_z = (bone_pos("calf_l", False).z + bone_pos("calf_r", False).z) * 0.5
    elbow_r_c = bone_pos("lowerarm_r", False)
    elbow_l_c = bone_pos("lowerarm_l", False)

    anchors = {
        "hand_r": hand_r_c,
        "hand_l": hand_l_c,
        "grip_r": grip_r_c,
        "grip_l": grip_l_c,
        "shoulder_r": shoulder_r_c,
        "shoulder_l": shoulder_l_c,
        "front_hold": (grip_r_c + grip_l_c) * 0.5,
    }

    z_hip = pelvis_c.z
    z_waist = pelvis_c.z + (shoulder_r_c.z - pelvis_c.z) * 0.28
    z_shoulder = shoulder_r_c.z
    z_neck = neck_c.z
    z_hem = 0.085 if spec.get("robe_len", "ankle") == "ankle" else max(0.38, knee_z - 0.03)

    # Alle reinen body-Polygone sammeln (keine HelperGeometry, keine Zaehne/Zunge/Wimpern!)
    body_polys = []
    for poly in eval_mesh.polygons:
        verts_idx = tuple(poly.vertices)
        if all(vi in body_vg for vi in verts_idx):
            body_polys.append(verts_idx)

    # Bone-basierte Koerperzonen direkt aus dem MPFB game_engine Rig
    def get_multi_vg(names, min_w=0.18):
        out_set = set()
        for nm in names:
            vg = mpfb_obj.vertex_groups.get(nm)
            if vg is None:
                continue
            idx = vg.index
            for v in mpfb_obj.data.vertices:
                for g in v.groups:
                    if g.group == idx and g.weight >= min_w:
                        out_set.add(v.index)
                        break
        return out_set

    torso_vg = get_multi_vg(["pelvis", "spine_01", "spine_02", "spine_03", "clavicle_l", "clavicle_r"], 0.22)
    upperarm_vg = get_multi_vg(["upperarm_l", "upperarm_r"], 0.28)
    forearm_hand_vg = get_multi_vg([
        "lowerarm_l", "lowerarm_r", "hand_l", "hand_r",
        "index_01_l", "index_02_l", "index_03_l", "middle_01_l", "middle_02_l", "middle_03_l",
        "ring_01_l", "ring_02_l", "ring_03_l", "pinky_01_l", "pinky_02_l", "pinky_03_l",
        "thumb_01_l", "thumb_02_l", "thumb_03_l",
        "index_01_r", "index_02_r", "index_03_r", "middle_01_r", "middle_02_r", "middle_03_r",
        "ring_01_r", "ring_02_r", "ring_03_r", "pinky_01_r", "pinky_02_r", "pinky_03_r",
        "thumb_01_r", "thumb_02_r", "thumb_03_r",
    ], 0.14)
    head_neck_vg = get_multi_vg(["head", "neck_01"], 0.22)
    leg_upper_vg = get_multi_vg(["thigh_l", "thigh_r"], 0.28)
    leg_lower_vg = get_multi_vg(["calf_l", "calf_r"], 0.28)
    foot_l_vg = get_multi_vg(["foot_l", "ball_l"], 0.30)
    foot_r_vg = get_multi_vg(["foot_r", "ball_r"], 0.30)

    sleeve_len = spec.get("sleeve_len", "short")

    def is_in_sleeve(vi, margin=0.0):
        if vi in forearm_hand_vg:
            return False
        if vi not in upperarm_vg:
            return False
        co = coords[vi]
        if co.x >= 0.0:
            d_sh = (co - shoulder_r_c).length
            arm_l = max(0.18, (elbow_r_c - shoulder_r_c).length)
        else:
            d_sh = (co - shoulder_l_c).length
            arm_l = max(0.18, (elbow_l_c - shoulder_l_c).length)
        return (d_sh / arm_l) < ((0.86 if sleeve_len == "long" else 0.56) - margin)

    # 5) Ziel-BMesh aufbauen
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new("UVMap")
    face_protect_verts = set()

    # --- 5A) HAUT-KOERPER: Konsequentes Loeschen ALLER verdeckten Polygone -> 0.0% Clipping! ---
    def is_skin_occluded_by_robe(poly_idx_tuple):
        # Fuesse, Unterarme, Haende & Gesicht/Kopf bleiben erhalten
        if any(i in foot_l_vg or i in foot_r_vg or i in forearm_hand_vg for i in poly_idx_tuple):
            return False
        c = sum((coords[i] for i in poly_idx_tuple), Vector((0, 0, 0))) / len(poly_idx_tuple)
        # Kopf, Hals & oberer Schluesselbein-Uebergang (3.2 cm unter Kragen) behalten -> 0% Spalt!
        if c.z > z_neck - 0.068:
            return False
        # V-Ausschnitt vorn am Brustbein sichtbar lassen
        if c.z > z_neck - 0.098 and c.y > neck_c.y + 0.010 and abs(c.x - neck_c.x) < 0.078:
            return False
        # Unterhalb des Rocksaums immer behalten (sichtbare Knoechel/Waden)
        if c.z < z_hem + 0.035:
            return False
        # Oberarm-Haut noch 3-4 cm IN den Aermel hinein behalten -> 0% dunkler Hohlraum unter Aermelsaum!
        if any(i in upperarm_vg and not is_in_sleeve(i, margin=0.18) for i in poly_idx_tuple):
            return False
        # Alles andere zwischen Kragen und Saum wird RESTLOS GELOESCHT!
        if any(i in torso_vg or i in leg_upper_vg or i in leg_lower_vg or is_in_sleeve(i, margin=0.18) for i in poly_idx_tuple):
            return True
        return False

    skin_vert_map = {}
    skin_faces = []
    head_world_pts = []
    for p in body_polys:
        if is_skin_occluded_by_robe(p):
            continue
        fverts = []
        for vi in p:
            if vi not in skin_vert_map:
                co = coords[vi]
                v = bm.verts.new(co)
                skin_vert_map[vi] = v
                if (vi in head_neck_vg) and (co.z > z_neck + 0.015) and (abs(co.x - head_c.x) < 0.115):
                    head_world_pts.append(co)
                # v2.1 FIX: Face_Protect fuer Gesicht, Augenlider, Ohren, Lippen, Haende UND FUESSE/ZEHEN!
                if (co.z > z_neck - 0.015) or (vi in lips_vg) or (vi in ears_vg) or \
                   (vi in foot_l_vg) or (vi in foot_r_vg) or \
                   ((co - hand_r_c).length < 0.13) or ((co - hand_l_c).length < 0.13):
                    face_protect_verts.add(v)
            fverts.append(skin_vert_map[vi])
        try:
            f = bm.faces.new(fverts)
            f.smooth = True
            skin_faces.append(f)
        except ValueError:
            pass
    if skin_faces:
        bmesh.ops.recalc_face_normals(bm, faces=skin_faces)
        map_bmesh_faces_to_trim(bm, skin_faces, uv_layer, skin_mat)

    # --- 5B) HOCHGLAENZENDE AUGAEPFEL & AUGENBRAUEN (EXAKT AN KOPF-BLICKRICHTUNG AUSGERICHTET!) ---
    # Nach 180-Grad-Z-Drehung liegt r_eye_c bei +X (rechts) und l_eye_c bei -X (links):
    head_right = (r_eye_c - l_eye_c)
    if head_right.length < 1e-4:
        head_right = Vector((1.0, 0.0, 0.0))
    else:
        head_right.normalize()
    head_up = Vector((0.0, 0.0, 1.0))
    head_fwd = head_up.cross(head_right).normalized()
    # Sicherstellen, dass head_fwd nach vorn (+Y) zeigt
    if head_fwd.y < 0.0:
        head_fwd = -head_fwd
        head_right = -head_right
    head_up = head_right.cross(head_fwd).normalized()

    add_eyeball(bm, uv_layer, l_eye_c, head_fwd, head_right, head_up, radius=0.0124, face_protect_set=face_protect_verts)
    add_eyeball(bm, uv_layer, r_eye_c, head_fwd, head_right, head_up, radius=0.0124, face_protect_set=face_protect_verts)
    hair_mat = spec.get("hair_mat", "hair_dark_wavy")
    add_eyebrows(bm, uv_layer, l_eye_c, r_eye_c, head_fwd, head_right, head_up, hair_mat, face_protect_set=face_protect_verts)

    # --- 5C) MEHRSCHICHTIGE GESTRAEHNTE HAARE & BAERTE (KEIN KNET-HELM!) ---
    hair_style = spec.get("hair_style", "short_wavy")
    if hair_style != "shaved":
        def hair_filter(p):
            c = sum((coords[i] for i in p), Vector((0, 0, 0))) / len(p)
            in_scalp = any(i in scalp_vg for i in p)
            if not in_scalp:
                if c.z > head_c.z - 0.035 and c.y < head_c.y - 0.015:
                    return True
                return False
            if c.y > l_eye_c.y - 0.012 and c.z < l_eye_c.z + 0.044:
                return False
            return True

        def hair_offset(vi, co, no):
            ang = math.atan2(co.x - head_c.x, co.y - head_c.y)
            if hair_style == "curly_short":
                vol = 0.012 + 0.0045 * math.sin(ang * 16.0 + co.z * 85.0)
                return co + no * vol
            elif hair_style == "long_wavy":
                strand = 0.0038 * math.sin(ang * 18.0 + co.z * 25.0)
                vol = 0.011 + strand
                drop = Vector((0.0, -0.012, -0.040)) if (co.y < head_c.y - 0.02 and co.z < head_c.z + 0.015) else Vector((0, 0, 0))
                return co + no * vol + drop
            else:
                strand = 0.0038 * math.sin(ang * 16.0 + co.z * 35.0)
                vol = 0.010 + strand
                return co + no * vol

        build_shell_from_source_faces(
            bm, uv_layer, coords, normals, body_polys,
            hair_filter, hair_offset, hair_mat,
            smooth_iters=2, feather_boundary=True, protect_set=face_protect_verts
        )

        # Organische Nacken-/Schulter-Haarstraehnen eng am Kopf anliegend (KEINE abstehenden Spitzen!)
        if hair_style == "long_wavy":
            n_locks = 9
            for li in range(n_locks):
                # Nur im Hinterkopf-/Nackenbereich (-45 Grad .. -135 Grad) weich ueber Schultern fallend
                ang = math.radians(-45.0 - (li / (n_locks - 1)) * 90.0)
                ux, uy = math.cos(ang), math.sin(ang)
                r0 = 0.086
                p_start = Vector((head_c.x + ux * r0, head_c.y + uy * r0, head_c.z + 0.035))
                lock_len = 0.155
                wave_x = 0.006 * math.sin(li * 1.7 + seed)
                pts = [
                    p_start,
                    p_start + Vector((ux * 0.006 + wave_x * 0.5, uy * 0.008, -lock_len * 0.48)),
                    p_start + Vector((ux * 0.003 + wave_x,       uy * 0.005, -lock_len)),
                ]
                add_tapered_lock(bm, uv_layer, pts, [0.017, 0.014, 0.005], hair_mat, segs=5, protect_set=face_protect_verts)
        elif hair_style == "short_wavy":
            # Sanfte eng anliegende Nackenstraehnen hinten am Hinterkopf (keine seitlichen Ohren-Spitzen!)
            n_locks = 5
            for li in range(n_locks):
                ang = math.radians(-62.0 - (li / (n_locks - 1)) * 56.0)
                ux, uy = math.cos(ang), math.sin(ang)
                r0 = 0.085
                p_start = Vector((head_c.x + ux * r0, head_c.y + uy * r0, head_c.z + 0.015))
                pts = [
                    p_start,
                    p_start + Vector((ux * 0.002, uy * 0.004, -0.035)),
                    p_start + Vector((-ux * 0.006, -uy * 0.004, -0.068)),
                ]
                add_tapered_lock(bm, uv_layer, pts, [0.015, 0.012, 0.004], hair_mat, segs=5, protect_set=face_protect_verts)

    # Mehrschichtiger gestraehnter Bart fuer Maenner
    beard_style = spec.get("beard_style", "none")
    if (not is_fem) and beard_style != "none":
        def beard_filter(p):
            c = sum((coords[i] for i in p), Vector((0, 0, 0))) / len(p)
            if any(i in lips_vg for i in p):
                return False
            if c.y < head_c.y - 0.010:
                return False
            if c.z > lips_c.z + 0.012 or c.z < jaw_c.z - 0.024:
                return False
            if abs(c.x - head_c.x) > 0.068:
                return False
            if c.z > lips_c.z + 0.004 and abs(c.x - head_c.x) < 0.018:
                return False
            return True

        beard_len = 0.072 if beard_style == "patriarch" else (0.036 if beard_style == "full" else 0.010)
        def beard_offset(vi, co, no):
            ang = math.atan2(co.x - head_c.x, max(0.01, co.y - head_c.y))
            grooves = 0.0032 * math.sin(ang * 20.0)
            chin_t = max(0.0, min(1.0, (lips_c.z - co.z) / max(0.02, lips_c.z - jaw_c.z + 0.02)))
            drop_z = -beard_len * (chin_t ** 1.35) * max(0.25, 1.0 - abs(co.x - head_c.x) / 0.072)
            out_d = 0.0055 + 0.0075 * chin_t + grooves
            return co + no * out_d + Vector((0.0, 0.004 * chin_t, drop_z))

        build_shell_from_source_faces(
            bm, uv_layer, coords, normals, body_polys,
            beard_filter, beard_offset, hair_mat,
            smooth_iters=2, feather_boundary=True, protect_set=face_protect_verts
        )

        # Spitz zulaufende Bart-Straehnen entlang Kinn & Kiefer (besonders fuer Noah, Sem, Jafet!)
        if beard_style in ("patriarch", "full"):
            n_b = 7 if beard_style == "patriarch" else 5
            for bi in range(n_b):
                u = (bi / (n_b - 1)) * 2.0 - 1.0  # -1..+1 ueber das Kinn
                center_fac = 1.0 - 0.45 * abs(u)
                len_b = (0.105 if beard_style == "patriarch" else 0.052) * center_fac
                p0 = Vector((jaw_c.x + u * 0.044, lips_c.y - 0.006 - abs(u) * 0.018, jaw_c.z + 0.012))
                pts = [
                    p0,
                    p0 + Vector((u * 0.006, 0.010 * center_fac, -len_b * 0.50)),
                    p0 + Vector((u * 0.004, 0.006 * center_fac, -len_b)),
                ]
                add_tapered_lock(bm, uv_layer, pts, [0.013 * center_fac + 0.004, 0.010 * center_fac + 0.003, 0.003],
                                 hair_mat, segs=5, protect_set=face_protect_verts)

    # --- 5D) BRONZEZEIT-TUNIKA (Oberteil + Aermel + Kragenband) + FALTENROCK ---
    robe_mat = spec.get("robe_mat", "linen_unbleached")
    is_priest_robe = (robe_mat == "priest_white_lapis")
    uv_robe_mode = "hem_band" if robe_mat in ("priest_white_lapis", "sumerian_border") else "planar_cyl"

    def tunic_upper_filter(p):
        if any(i in forearm_hand_vg or i in head_neck_vg for i in p):
            return False
        if not all((i in torso_vg or is_in_sleeve(i)) for i in p):
            return False
        c = sum((coords[i] for i in p), Vector((0, 0, 0))) / len(p)
        if c.z > z_neck - 0.032 or c.z < z_waist - 0.035:
            return False
        if c.z > z_neck - 0.068 and c.y > neck_c.y + 0.018 and abs(c.x - neck_c.x) < 0.062:
            return False
        return True

    def tunic_upper_offset(vi, co, no):
        ang = math.atan2(co.x, co.y)
        fold = 0.0042 * math.sin(ang * 10.0 + co.z * 14.0 + seed)
        # Deutlicher physischer Stoffabstand (>= 12 mm) + sanfte Weitung am Aermelsaum!
        sleeve_flare = 0.009 if (vi in upperarm_vg) else 0.0
        return co + no * (0.0135 + sleeve_flare + fold)

    upper_mat = "linen_unbleached" if is_priest_robe else robe_mat
    t_verts, t_faces = build_shell_from_source_faces(
        bm, uv_layer, coords, normals, body_polys,
        tunic_upper_filter, tunic_upper_offset, upper_mat,
        uv_mode="plain_upper" if upper_mat in ("priest_white_lapis", "sumerian_border") else "planar_cyl",
        smooth_iters=3
    )
    # v2.1 FIX: Halsausschnitt-Rand sanft an die durchgehende Hals-/Schluesselbeinhaut anlegen
    # (kein abstehender Kragen-Balken, kein waagerechter Spalt am Schluesselbein!)
    for v in t_verts:
        if v.is_boundary and v.co.z > z_neck - 0.085 and abs(v.co.x - neck_c.x) < 0.12:
            v.co -= (v.normal * 0.0075)
    if t_faces:
        bmesh.ops.recalc_face_normals(bm, faces=t_faces)

    # Taillen-Ring ausschliesslich aus echten Torso-Vertices
    waist_ring_pts = [coords[vi] + normals[vi] * 0.016 for vi in torso_vg
                      if vi in body_vg and vi not in upperarm_vg and vi not in forearm_hand_vg
                      and abs(coords[vi].z - z_waist) < 0.028]
    if len(waist_ring_pts) < 12:
        waist_ring_pts = [coords[vi] + normals[vi] * 0.016 for vi in torso_vg
                          if vi in body_vg and abs(coords[vi].z - z_waist) < 0.05]

    flare = 0.38 if spec.get("robe_len", "ankle") == "ankle" else 0.25
    build_draped_skirt_extension(
        bm, uv_layer, waist_ring_pts, z_hem,
        flare=flare, fold_amp=0.020, fold_count=9 + (seed % 3),
        region_name=robe_mat, uv_mode=uv_robe_mode, phase=seed * 0.7, hem_cuff=0.010
    )

    # --- 5E) GEKNOTETE TAILLENSCHAERPE MIT HAENGEENDE ---
    belt_mat = spec.get("belt_mat", "leather_worn")
    build_knotted_sash(bm, uv_layer, waist_ring_pts, z_waist, belt_mat, seed=seed)

    # --- 5F) WEICH ANLIEGENDER DIAGONALER SUMERISCHER SCHULTERMANTEL / WICKELSCHAL ---
    if spec.get("shawl", False):
        shawl_mat = spec.get("shawl_mat", "priest_white_lapis" if is_priest_robe else "wool_ochre")
        build_diagonal_mantle(
            bm, uv_layer, coords, normals, body_polys,
            torso_vg, upperarm_vg, forearm_hand_vg, head_neck_vg,
            shoulder_l_c, shoulder_r_c, neck_c, z_waist, z_neck, shawl_mat, seed=seed
        )

    # --- 5G) HANDWERKER-LEDERSCHUERZE ---
    if spec.get("apron", False) and waist_ring_pts:
        cx = sum(p.x for p in waist_ring_pts) / len(waist_ring_pts)
        cy = sum(p.y for p in waist_ring_pts) / len(waist_ring_pts)
        n_ap = 12
        ap_rings = []
        ap_hem = max(z_hem + 0.05, knee_z + 0.02)
        for ri in range(6):
            t = ri / 5.0
            z = (z_waist - 0.015) * (1.0 - t) + ap_hem * t
            ring = []
            for si in range(n_ap):
                ang = -0.80 + (si / (n_ap - 1)) * 1.60
                r_base = 0.148 + flare * 0.155 * (t ** 1.1) + 0.032
                ring.append(bm.verts.new(Vector((cx + math.sin(ang) * r_base,
                                                 cy + math.cos(ang) * r_base, z))))
            ap_rings.append(ring)
        ap_faces = []
        for ri in range(5):
            for si in range(n_ap - 1):
                f = bm.faces.new((ap_rings[ri][si], ap_rings[ri][si + 1],
                                  ap_rings[ri + 1][si + 1], ap_rings[ri + 1][si]))
                f.smooth = True
                ap_faces.append(f)
        bmesh.ops.recalc_face_normals(bm, faces=ap_faces)
        map_bmesh_faces_to_trim(bm, ap_faces, uv_layer, "leather_worn")

    # --- 5H) WEICHES KOPFTUCH / SCHLEIER (Frauen) & PRIESTER-KAPPE / STIRNBAND ---
    veil_mat = spec.get("veil_mat", "linen_unbleached")
    if headwear == "veil":
        build_draped_veil(bm, uv_layer, head_c, l_eye_c, neck_c, shoulder_l_c, shoulder_r_c, veil_mat, seed=seed)
    elif headwear == "priest_cap":
        def cap_filter(p):
            c = sum((coords[i] for i in p), Vector((0, 0, 0))) / len(p)
            return c.z > l_eye_c.z + 0.038

        def cap_offset(vi, co, no):
            return co + no * 0.015 + Vector((0.0, 0.0, 0.010))

        build_shell_from_source_faces(
            bm, uv_layer, coords, normals, body_polys,
            cap_filter, cap_offset, "priest_white_lapis",
            uv_mode="hem_band", smooth_iters=2
        )
    elif headwear == "headband":
        def band_filter(p):
            c = sum((coords[i] for i in p), Vector((0, 0, 0))) / len(p)
            return (l_eye_c.z + 0.034) < c.z < (l_eye_c.z + 0.062)

        def band_offset(vi, co, no):
            return co + no * 0.017

        build_shell_from_source_faces(
            bm, uv_layer, coords, normals, body_polys,
            band_filter, band_offset, "sumerian_border",
            uv_mode="hem_band", smooth_iters=2
        )

    # --- 5I) ANATOMISCHE RIEMENSANDALEN (ODER NACKTE FUESSE) EXAKT AUF Z = 0.0 ---
    if wears_sandals:
        for f_vg, ankle_b, toe_b in ((foot_l_vg, "foot_l", "ball_l"), (foot_r_vg, "foot_r", "ball_r")):
            build_strap_sandal(bm, uv_layer, coords, normals, body_polys, f_vg,
                               bone_pos(ankle_b, False), bone_pos(toe_b, True), protect_set=face_protect_verts)

    # --- 5J) REQUISITEN + FACE_PROTECT + AUTOMATISCHE KOPF-/HALS-KOLLISIONS-PRUEFUNG ---
    prop_name = spec.get("prop", "none")
    max_allowed_h = FEMALE_HEIGHT_MAX if is_fem else MALE_HEIGHT_MAX
    prop_verts = add_prop_at_anchors(bm, uv_layer, prop_name, anchors, max_top_z=max_allowed_h - 0.005)
    # ALLE Prop-Vertices schuetzen, damit Decimate NIEMALS Stiele oder Beil-Klingen zu spitzen Dreiecken kollabiert!
    for pv in prop_verts:
        face_protect_verts.add(pv)

    # Kollisions-Check fuer geschulterte Balken/Saecke/Kruege gegen Kopf/Hals!
    prop_head_clearance = 9.99
    if prop_verts and head_world_pts and prop_name in ("shoulder_beam", "shoulder_sack", "jar_hip", "jar_front", "basket_l"):
        # Schneller BBox + Punktabstand zu Kopf/Hals
        p_arr = np.array([[v.co.x, v.co.y, v.co.z] for v in prop_verts], dtype=np.float32)
        h_arr = np.array([[c.x, c.y, c.z] for c in head_world_pts[::3]], dtype=np.float32)
        # Paarweiser minimaler 3D-Abstand (vektorisiert in numpy, < 1 ms)
        diffs = p_arr[:, None, :] - h_arr[None, :, :]
        dists = np.sqrt(np.sum(diffs * diffs, axis=2))
        prop_head_clearance = float(np.min(dists))
        assert prop_head_clearance >= MIN_PROP_HEAD_CLEARANCE_M, (
            f"KOLLISIONS-FEHLER bei {spec['name']} ({prop_name}): "
            f"Abstand zu Kopf/Hals nur {prop_head_clearance*100:.1f} cm (< {MIN_PROP_HEAD_CLEARANCE_M*100:.1f} cm)!"
        )

    # 6) Bodenkontakt exakt auf Z = 0.000 m normieren & finale Hoehe verifizieren
    bm.normal_update()
    min_z = min((v.co.z for v in bm.verts), default=0.0)
    if abs(min_z) > 1e-5:
        for v in bm.verts:
            v.co.z -= min_z
    max_z = max((v.co.z for v in bm.verts), default=0.0)
    final_h = max_z

    h_lo, h_hi = (FEMALE_HEIGHT_MIN, FEMALE_HEIGHT_MAX) if is_fem else (MALE_HEIGHT_MIN, MALE_HEIGHT_MAX)
    if final_h < h_lo or final_h > h_hi:
        # Praezise Feinkorrektur in Z (max. +/- 1.5 cm wegen Haarspitze/Sohle)
        clamped_h = max(h_lo + 0.004, min(h_hi - 0.004, final_h))
        s_fix = clamped_h / max(0.5, final_h)
        for v in bm.verts:
            v.co *= s_fix
        final_h = max((v.co.z for v in bm.verts), default=0.0)

    bm.verts.ensure_lookup_table()
    protect_indices = [v.index for v in face_protect_verts if v.is_valid]

    mesh = bpy.data.meshes.new(spec["name"])
    bm.to_mesh(mesh)
    bm.free()

    eval_obj.to_mesh_clear()
    bpy.data.objects.remove(mpfb_obj, do_unlink=True)
    bpy.data.objects.remove(rig, do_unlink=True)

    obj = bpy.data.objects.new(spec["name"], mesh)
    collection.objects.link(obj)
    obj.data.materials.append(mat)

    vg_fp = obj.vertex_groups.new(name="Face_Protect")
    if protect_indices:
        vg_fp.add(protect_indices, 0.45, "REPLACE")

    assign_col_rig_from_zones(obj, z_hip, z_shoulder, z_neck)
    return obj, final_h, 0.0, prop_head_clearance


# ==============================================================================
# PRAEZISES DECIMATE MIT FACE_PROTECT & STRENGER BUDGET-KONVERGENZ
# ==============================================================================
def count_tris(obj):
    return sum(max(1, len(p.vertices) - 2) for p in obj.data.polygons)


def make_decimated_lod(src_obj, new_name, min_tris, max_tris, target_tris, collection, protect_face=True):
    """Konvergiert garantiert in das strikte [min_tris, max_tris]-Budget bei maximalem Gesichtsschutz."""
    dup = src_obj.copy()
    dup.data = src_obj.data.copy()
    dup.name = new_name
    dup.data.name = new_name
    collection.objects.link(dup)

    bpy.ops.object.select_all(action="DESELECT")
    dup.select_set(True)
    bpy.context.view_layer.objects.active = dup

    for attempt in range(4):
        cur_tris = count_tris(dup)
        if min_tris <= cur_tris <= max_tris:
            break
        if cur_tris < min_tris:
            break
        ratio = max(0.01, min(0.98, target_tris / float(cur_tris)))
        mod = dup.modifiers.new(name=f"DecimateLOD_{attempt}", type="DECIMATE")
        mod.decimate_type = "COLLAPSE"
        mod.ratio = ratio
        mod.use_collapse_triangulate = True
        if attempt == 0 and protect_face and "Face_Protect" in dup.vertex_groups and target_tris >= 1800:
            mod.vertex_group = "Face_Protect"
            mod.invert_vertex_group = True
            mod.vertex_group_factor = 1.0
        bpy.ops.object.modifier_apply(modifier=mod.name)

    dup.data.validate(clean_customdata=False)
    final_tris = count_tris(dup)
    assert min_tris <= final_tris <= max_tris, (
        f"TRI-BUDGET-FEHLER bei {new_name}: {final_tris} Tris ausserhalb [{min_tris}..{max_tris}]!"
    )
    return dup


def assert_mesh_bounds(obj, gender):
    zs = [v.co.z for v in obj.data.vertices]
    min_z = min(zs)
    max_z = max(zs)
    h = max_z - min_z
    h_lo, h_hi = (FEMALE_HEIGHT_MIN, FEMALE_HEIGHT_MAX) if gender == "F" else (MALE_HEIGHT_MIN, MALE_HEIGHT_MAX)
    assert abs(min_z) <= 0.005, f"BODENKONTAKT-FEHLER bei {obj.name}: min_Z={min_z:.4f} m!"
    assert h_lo <= h <= h_hi, f"GROESSEN-FEHLER bei {obj.name} ({gender}): Hoehe={h:.3f} m ausserhalb [{h_lo:.2f}..{h_hi:.2f}]!"
    return h, min_z


# ==============================================================================
# SPEZIFIKATIONEN v2: NOAHS 8-KOEPFIGE HERO-FAMILIE & 45 BUERGER (9x5)
# ==============================================================================
NOAH_FAMILY_SPECS = [
    {
        "name": "char_noah",
        "gender": "M", "phenotype": "semitic", "age": 0.85, "target_height": 1.80, "muscle": 0.56, "weight": 0.52,
        "hair_mat": "hair_grey", "hair_style": "short_wavy", "beard_style": "patriarch",
        "robe_mat": "wool_ochre", "robe_len": "ankle", "sleeve_len": "long",
        "belt_mat": "sumerian_border", "shawl": True, "shawl_mat": "sumerian_border",
        "headwear": "none", "sandals": True, "arm_pose": "hold_staff_r", "prop": "staff", "seed": 1,
    },
    {
        "name": "char_noah_wife",
        "gender": "F", "phenotype": "semitic", "age": 0.78, "target_height": 1.64, "muscle": 0.36, "weight": 0.50,
        "hair_mat": "hair_grey", "hair_style": "long_wavy", "beard_style": "none",
        "robe_mat": "linen_unbleached", "robe_len": "ankle", "sleeve_len": "long",
        "belt_mat": "sumerian_border", "shawl": True, "shawl_mat": "wool_indigo",
        "headwear": "veil", "veil_mat": "linen_unbleached", "sandals": True,
        "arm_pose": "hold_jar_front", "prop": "jar_front", "seed": 2,
    },
    {
        "name": "char_son_sem",
        "gender": "M", "phenotype": "semitic", "age": 0.56, "target_height": 1.77, "muscle": 0.64, "weight": 0.50,
        "hair_mat": "hair_dark_wavy", "hair_style": "short_wavy", "beard_style": "full",
        "robe_mat": "wool_indigo", "robe_len": "ankle", "sleeve_len": "short",
        "belt_mat": "sumerian_border", "shawl": True, "shawl_mat": "linen_unbleached",
        "headwear": "none", "sandals": True, "arm_pose": "hold_scroll_l", "prop": "scroll_l", "seed": 3,
    },
    {
        "name": "char_daughter_sem",
        "gender": "F", "phenotype": "semitic", "age": 0.50, "target_height": 1.63, "muscle": 0.38, "weight": 0.46,
        "hair_mat": "hair_dark_wavy", "hair_style": "long_wavy", "beard_style": "none",
        "robe_mat": "wool_ochre", "robe_len": "ankle", "sleeve_len": "short",
        "belt_mat": "sumerian_border", "shawl": True, "shawl_mat": "linen_unbleached",
        "headwear": "veil", "veil_mat": "wool_ochre", "sandals": True,
        "arm_pose": "carry_jar_hip", "prop": "jar_hip", "seed": 4,
    },
    {
        "name": "char_son_ham",
        "gender": "M", "phenotype": "hamitic", "age": 0.54, "target_height": 1.81, "muscle": 0.72, "weight": 0.52,
        "hair_mat": "hair_curly_dark", "hair_style": "curly_short", "beard_style": "short",
        "robe_mat": "linen_unbleached", "robe_len": "knee", "sleeve_len": "short",
        "belt_mat": "leather_worn", "shawl": True, "shawl_mat": "wool_brown",
        "headwear": "none", "sandals": True, "arm_pose": "hold_tool_r", "prop": "carpenter_adze", "seed": 5,
    },
    {
        "name": "char_daughter_ham",
        "gender": "F", "phenotype": "hamitic", "age": 0.48, "target_height": 1.66, "muscle": 0.42, "weight": 0.46,
        "hair_mat": "hair_curly_dark", "hair_style": "curly_short", "beard_style": "none",
        "robe_mat": "wool_ochre", "robe_len": "ankle", "sleeve_len": "short",
        "belt_mat": "sumerian_border", "shawl": True, "shawl_mat": "sumerian_border",
        "headwear": "headband", "sandals": True, "arm_pose": "carry_basket_l", "prop": "basket_l", "seed": 6,
    },
    {
        "name": "char_son_jafet",
        "gender": "M", "phenotype": "japhetic", "age": 0.52, "target_height": 1.79, "muscle": 0.66, "weight": 0.50,
        "hair_mat": "hair_brown_wavy", "hair_style": "short_wavy", "beard_style": "full",
        "robe_mat": "wool_brown", "robe_len": "knee", "sleeve_len": "short",
        "belt_mat": "leather_worn", "shawl": True, "shawl_mat": "wool_ochre",
        "headwear": "none", "sandals": True, "arm_pose": "hold_staff_r", "prop": "staff", "seed": 7,
    },
    {
        "name": "char_daughter_jafet",
        "gender": "F", "phenotype": "japhetic", "age": 0.46, "target_height": 1.67, "muscle": 0.38, "weight": 0.45,
        "hair_mat": "hair_brown_wavy", "hair_style": "long_wavy", "beard_style": "none",
        "robe_mat": "wool_indigo", "robe_len": "ankle", "sleeve_len": "short",
        "belt_mat": "sumerian_border", "shawl": True, "shawl_mat": "linen_unbleached",
        "headwear": "veil", "veil_mat": "linen_unbleached", "sandals": True,
        "arm_pose": "hold_jar_front", "prop": "jar_front", "seed": 8,
    },
]


def get_citizen_specs():
    """9 Buerger-, Priester- & Frauentypen x 5 Varianten = 45 Figuren (alle exakt hoehennormiert!)."""
    groups = [
        ("citizen_carpenter", "M", "knee", ["hold_tool_r", "hold_tool_r", "carry_shoulder_r", "hold_tool_r", "relaxed"],
         ["carpenter_adze", "mallet", "shoulder_beam", "carpenter_adze", "mallet"],
         ["linen_unbleached", "wool_brown", "wool_ochre", "linen_unbleached", "wool_brown"], True),
        ("citizen_porter", "M", "knee", ["carry_shoulder_r", "carry_shoulder_r", "hold_jar_front", "carry_shoulder_r", "carry_basket_l"],
         ["shoulder_beam", "shoulder_sack", "jar_front", "shoulder_sack", "basket_l"],
         ["linen_unbleached", "wool_brown", "linen_unbleached", "wool_ochre", "wool_brown"], False),
        ("citizen_smith_pitch", "M", "knee", ["hold_tool_r", "hold_tool_r", "hold_tool_r", "hold_tool_r", "relaxed"],
         ["smith_hammer", "pitch_ladle", "smith_hammer", "pitch_ladle", "smith_hammer"],
         ["wool_brown", "linen_unbleached", "wool_brown", "wool_indigo", "wool_brown"], True),
        ("citizen_merchant", "M", "ankle", ["hold_scroll_l", "relaxed", "hold_scroll_l", "prayer_bless", "hold_staff_r"],
         ["scroll_l", "none", "scroll_l", "priest_censer", "staff"],
         ["wool_indigo", "wool_ochre", "kaunakes_fringe", "wool_indigo", "wool_ochre"], False),
        ("citizen_farmer_rower", "M", "knee", ["hold_staff_r", "hold_tool_r", "hold_staff_r", "carry_shoulder_r", "hold_tool_r"],
         ["oar", "sickle", "oar", "shoulder_sack", "sickle"],
         ["linen_unbleached", "wool_ochre", "linen_unbleached", "wool_brown", "linen_unbleached"], False),
        ("citizen_priest", "M", "ankle", ["prayer_bless", "prayer_bless", "hold_scroll_l", "prayer_bless", "hold_staff_r"],
         ["priest_censer", "none", "scroll_l", "priest_censer", "staff"],
         ["priest_white_lapis"] * 5, False),
        ("citizen_woman_jar", "F", "ankle", ["carry_jar_hip", "hold_jar_front", "carry_jar_hip", "carry_basket_l", "hold_jar_front"],
         ["jar_hip", "jar_front", "jar_hip", "basket_l", "jar_front"],
         ["linen_unbleached", "wool_ochre", "wool_indigo", "linen_unbleached", "wool_brown"], False),
        ("citizen_woman_artisan", "F", "ankle", ["hold_tool_r", "carry_basket_l", "hold_jar_front", "hold_tool_r", "carry_basket_l"],
         ["spindle_cloth", "basket_l", "jar_front", "spindle_cloth", "basket_l"],
         ["wool_ochre", "linen_unbleached", "wool_brown", "wool_indigo", "linen_unbleached"], False),
        ("citizen_woman_noble", "F", "ankle", ["relaxed", "prayer_bless", "hold_jar_front", "relaxed", "hold_scroll_l"],
         ["none", "priest_censer", "jar_front", "none", "scroll_l"],
         ["priest_white_lapis", "wool_indigo", "wool_ochre", "kaunakes_fringe", "linen_unbleached"], False),
    ]

    phenos = ["semitic", "semitic", "hamitic", "japhetic", "semitic"]
    fem_heights = [1.62, 1.64, 1.65, 1.67, 1.68]
    male_heights = [1.74, 1.76, 1.78, 1.79, 1.81]
    all_specs = []
    for g_idx, (g_name, gender, rlen, poses, props, robes, apron) in enumerate(groups):
        is_fem = (gender == "F")
        is_priest = (g_name == "citizen_priest")
        is_noble_w = (g_name == "citizen_woman_noble")
        for i in range(5):
            pheno = phenos[(i + g_idx) % 5]
            if pheno == "hamitic":
                hmat, hstyle = "hair_curly_dark", "curly_short"
            elif pheno == "japhetic":
                hmat, hstyle = "hair_brown_wavy", ("long_wavy" if is_fem else "short_wavy")
            else:
                hmat, hstyle = "hair_dark_wavy", ("long_wavy" if is_fem else "short_wavy")
            if is_priest and i in (0, 2):
                hstyle = "shaved"

            # Bauern & Lasttraeger teilweise barfuss auf Z=0.0, alle anderen mit Riemensandalen
            wears_sandals = not (g_name in ("citizen_farmer_rower", "citizen_porter") and i in (1, 3))

            all_specs.append({
                "group": g_name,
                "name": f"{g_name}_{i+1:02d}",
                "gender": gender,
                "phenotype": pheno,
                "age": 0.46 + (i * 0.06),
                "target_height": fem_heights[(i + g_idx) % 5] if is_fem else male_heights[(i + g_idx) % 5],
                "muscle": 0.40 if is_fem else (0.68 if g_name in ("citizen_carpenter", "citizen_porter", "citizen_smith_pitch") else 0.54),
                "weight": 0.46 + (i % 3) * 0.05,
                "hair_mat": "hair_grey" if (is_priest and i == 4) else hmat,
                "hair_style": hstyle,
                "beard_style": "none" if is_fem else ("short" if i in (1, 3) else "full"),
                "robe_mat": robes[i],
                "robe_len": rlen,
                "sleeve_len": "long" if (is_priest or is_noble_w) else "short",
                "belt_mat": "sumerian_border" if (is_priest or is_noble_w or g_name == "citizen_merchant") else "leather_worn",
                "shawl": is_priest or is_noble_w or (g_name == "citizen_merchant" and i in (0, 2, 4)),
                "shawl_mat": "priest_white_lapis" if is_priest else ("sumerian_border" if is_noble_w else "wool_ochre"),
                "apron": apron and (i in (0, 1, 3)),
                "headwear": "priest_cap" if (is_priest and i in (1, 3)) else ("veil" if (is_noble_w or (is_fem and i in (0, 2, 3))) else ("headband" if is_fem else "none")),
                "veil_mat": "linen_unbleached" if i % 2 == 0 else robes[i],
                "sandals": wears_sandals,
                "arm_pose": poses[i],
                "prop": props[i],
                "seed": g_idx * 10 + i + 11,
            })
    return all_specs


# ==============================================================================
# EXPORT & MANIFEST
# ==============================================================================
def export_collection_glb(collection, out_path):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in collection.objects:
        if obj.type == "MESH":
            obj.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=out_path,
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_normals=True,
        export_tangents=True,
        export_texcoords=True,
        export_materials="EXPORT",
        export_vertex_color="ACTIVE",
        export_all_vertex_colors=True,
        export_attributes=True,
    )


def update_manifest(project_root, stats):
    mpath = os.path.join(project_root, "assets", "manifest.json")
    if not os.path.exists(mpath):
        return
    with open(mpath, "r", encoding="utf-8") as f:
        data = json.load(f)
    cats = data.setdefault("categories", {})
    chars = cats.setdefault("characters", {
        "blendDir": "assets/blend/characters",
        "glbDir": "assets/glb/characters",
        "requiredTag": "Col_Rig",
        "items": {},
    })
    items = chars.setdefault("items", {})
    now_iso = datetime.datetime.now().isoformat(timespec="seconds")

    items["noah_family_kit"] = {
        "enabled": True,
        "url": "assets/glb/characters/noah_family_kit.glb",
        "blend": "assets/blend/characters/noah_family_kit.blend",
        "category": "character",
        "generator": "MPFB v2 (bl_ext.blender_org.mpfb)",
        "instanced": False,
        "figures": 8,
        "highPolyTrisAvg": stats["noah_hp_avg"],
        "lod0TrisAvg": stats["noah_lod0_avg"],
        "lod1TrisAvg": stats["noah_lod1_avg"],
        "lod2TrisAvg": stats["noah_lod2_avg"],
        "colorAttr": "Col_Rig",
        "updatedAt": now_iso,
    }
    items["mesopotamia_citizens_kit"] = {
        "enabled": True,
        "url": "assets/glb/characters/mesopotamia_citizens_kit.glb",
        "blend": "assets/blend/characters/mesopotamia_citizens_kit.blend",
        "category": "character",
        "generator": "MPFB v2 (bl_ext.blender_org.mpfb)",
        "instanced": True,
        "types": 9,
        "variantsPerType": 5,
        "totalLod0Figures": 45,
        "highPolyBaseTrisAvg": stats["cit_hp_avg"],
        "lod0TrisAvg": stats["cit_lod0_avg"],
        "lod1TrisAvg": stats["cit_lod1_avg"],
        "lod2TrisAvg": stats["cit_lod2_avg"],
        "colorAttr": "Col_Rig",
        "updatedAt": now_iso,
    }
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[MANIFEST] Aktualisiert: {mpath}", flush=True)


# ==============================================================================
# STUDIO-SETUP, METER-REFERENZSKALA & 3 PFLICHT-KONTROLLRENDERINGS
# ==============================================================================
def setup_studio(scene, samples=36, res_x=1920, res_y=1080):
    dev = setup_cycles_render(scene, samples=samples, res_x=res_x, res_y=res_y)
    bpy.ops.mesh.primitive_plane_add(size=80.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    fmat = bpy.data.materials.new("Mat_StudioFloor")
    fmat.use_nodes = True
    bsdf = next(n for n in fmat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (0.36, 0.31, 0.25, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.88
    floor.data.materials.append(fmat)

    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.56, 0.62, 0.70, 1.0)
    bg.inputs["Strength"].default_value = 0.78

    sun_data = bpy.data.lights.new("KeySun", type="SUN")
    sun_data.energy = 3.2
    sun_data.angle = math.radians(2.8)
    sun_data.color = (1.0, 0.95, 0.87)
    sun = bpy.data.objects.new("KeySun", sun_data)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(52), math.radians(16), math.radians(-148))

    rim_data = bpy.data.lights.new("RimSun", type="SUN")
    rim_data.energy = 1.25
    rim_data.color = (0.86, 0.93, 1.0)
    rim = bpy.data.objects.new("RimSun", rim_data)
    scene.collection.objects.link(rim)
    rim.rotation_euler = (math.radians(38), 0, math.radians(28))

    cam_data = bpy.data.cameras.new("PreviewCam")
    cam = bpy.data.objects.new("PreviewCam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    return dev, cam, cam_data


def point_cam(cam, cam_data, loc, target, lens=50.0):
    cam.location = Vector(loc)
    direction = Vector(target) - Vector(loc)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam_data.lens = lens


def build_height_scale_wall(scene, y_pos=-0.65, width=7.2):
    """Baut eine klare Meter-Referenzwand mit Linien & gut lesbaren 3D-Zahlen (1.0m / 1.5m / 1.8m / 2.0m)."""
    objs = []
    # Helle neutrale Rueckwand
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.0, y_pos, 1.25))
    wall = bpy.context.active_object
    wall.name = "_ScaleWall"
    wall.scale = (width, 2.5, 1.0)
    wall.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    wmat = bpy.data.materials.new("Mat_ScaleWall")
    wmat.use_nodes = True
    bsdf = next(n for n in wmat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (0.58, 0.56, 0.52, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.95
    wall.data.materials.append(wmat)
    objs.append(wall)

    line_mat = bpy.data.materials.new("Mat_ScaleLine")
    line_mat.use_nodes = True
    bsdf_l = next(n for n in line_mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf_l.inputs["Base Color"].default_value = (0.09, 0.08, 0.07, 1.0)
    bsdf_l.inputs["Roughness"].default_value = 0.85

    accent_mat = bpy.data.materials.new("Mat_ScaleAccent")
    accent_mat.use_nodes = True
    bsdf_a = next(n for n in accent_mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf_a.inputs["Base Color"].default_value = (0.55, 0.14, 0.09, 1.0)
    bsdf_a.inputs["Roughness"].default_value = 0.80

    for h_val, label, is_accent in [
        (1.0, "1.0 m", False),
        (1.5, "1.5 m", False),
        (1.65, "1.65 m", True),
        (1.8, "1.8 m", True),
        (2.0, "2.0 m", False),
    ]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, y_pos + 0.01, h_val))
        bar = bpy.context.active_object
        bar.scale = (width * 0.96, 0.008, 0.012 if is_accent else 0.008)
        bar.data.materials.append(accent_mat if is_accent else line_mat)
        objs.append(bar)

        for x_side in (-3.55, 3.30):
            font_curve = bpy.data.curves.new(type="FONT", name=f"Lbl_{label}")
            font_curve.body = label
            font_curve.size = 0.115
            font_curve.extrude = 0.004
            txt_obj = bpy.data.objects.new(name=f"Txt_{label}", object_data=font_curve)
            scene.collection.objects.link(txt_obj)
            txt_obj.location = (x_side, y_pos + 0.02, h_val + 0.018)
            # Figuren schauen +Y, Kamera steht bei +Y und schaut -Y -> Text muss um X=+90, Z=180 gedreht sein?
            # Test: Standard-Text liegt in XY und ist von +Z lesbar; um von +Y lesbar zu sein: rot X=90, Z=180!
            txt_obj.rotation_euler = (math.radians(90.0), 0.0, math.radians(180.0))
            txt_obj.data.materials.append(accent_mat if is_accent else line_mat)
            objs.append(txt_obj)
    return objs


def render_closeup_3panel_composite(scene, cam, cam_data, noah_lod0, cit_lod0, out_path):
    """Rendert 3 gestochen scharfe Cycles-CUDA-Nahaufnahmen und setzt sie als 1920x1080-Prueftafel zusammen:
      - Oben links  (960x540): Gesichter, Augen, Haare/Baerte, Schleier & Schulterausschnitte (Noah, Frau, Ham)
      - Oben rechts (960x540): Haende & Props (Stab, Bronze-Beil, Hueft-Amphore, geschulterter Zedernbalken!)
      - Unten      (1920x540): Fuesse & konturierte Riemensandalen auf Z=0.0 + Taillenschaerpen & Faltenwurf
    """
    tmp_dir = os.path.dirname(out_path)
    p1 = os.path.join(tmp_dir, "_tmp_panel1.png")
    p2 = os.path.join(tmp_dir, "_tmp_panel2.png")
    p3 = os.path.join(tmp_dir, "_tmp_panel3.png")

    all_objs = noah_lod0 + cit_lod0
    for o in all_objs:
        o.hide_render = True

    # Panel 1: Noah (0), Noahs Frau (1), Ham (4) — Nahaufnahme Koepfe/Schultern (alle 3 vollstaendig im Bild!)
    noah_lod0[0].hide_render = False
    noah_lod0[1].hide_render = False
    noah_lod0[4].hide_render = False
    noah_lod0[0].location = (-0.54, 0.0, 0.0)
    noah_lod0[1].location = (0.00,  0.0, 0.0)
    noah_lod0[4].location = (0.54,  0.0, 0.0)

    scene.render.resolution_x = 960
    scene.render.resolution_y = 540
    point_cam(cam, cam_data, (0.0, 2.55, 1.50), (0.0, 0.0, 1.44), lens=48.0)
    scene.render.filepath = p1
    bpy.ops.render.render(write_still=True)

    # Panel 2: Props-Check: Noah (Stab), Sem-Frau (Hueft-Amphore), Ham (Bronze-Dechsel), Zimmermann-03 (Balken auf Schulter!)
    for o in all_objs:
        o.hide_render = True
    beam_carpenter = cit_lod0[2]  # citizen_carpenter_03 (carry_shoulder_r + shoulder_beam!)
    for idx, o in enumerate([noah_lod0[0], noah_lod0[3], noah_lod0[4], beam_carpenter]):
        o.hide_render = False
        o.location = ((idx - 1.5) * 0.72, 0.0, 0.0)
    point_cam(cam, cam_data, (0.0, 4.05, 1.28), (0.0, 0.0, 1.20), lens=46.0)
    scene.render.filepath = p2
    bpy.ops.render.render(write_still=True)

    # Panel 3: Bodenkontakt, Fuesse & konturierte Riemensandalen exakt auf Z=0.0 (5 Figuren!)
    for o in all_objs:
        o.hide_render = True
    foot_line = [noah_lod0[0], noah_lod0[1], noah_lod0[4], noah_lod0[6], cit_lod0[6]]  # inkl. Sandalen & Barfuss (porter_02)
    for idx, o in enumerate(foot_line):
        o.hide_render = False
        o.location = ((idx - 2.0) * 0.56, 0.0, 0.0)
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 540
    point_cam(cam, cam_data, (0.0, 2.45, 0.30), (0.0, 0.0, 0.14), lens=48.0)
    scene.render.filepath = p3
    bpy.ops.render.render(write_still=True)

    # 3 Panels verlustfrei in 1920x1080 zusammensetzen (Blender image + numpy, kein PIL noetig!)
    im1 = bpy.data.images.load(p1)
    im2 = bpy.data.images.load(p2)
    im3 = bpy.data.images.load(p3)
    a1 = np.array(im1.pixels[:], dtype=np.float32).reshape((540, 960, 4))
    a2 = np.array(im2.pixels[:], dtype=np.float32).reshape((540, 960, 4))
    a3 = np.array(im3.pixels[:], dtype=np.float32).reshape((540, 1920, 4))

    canvas = np.ones((1080, 1920, 4), dtype=np.float32)
    # Blender-Pixel: y=0 ist UNTEN!
    canvas[0:540, 0:1920, :] = a3
    canvas[540:1080, 0:960, :] = a1
    canvas[540:1080, 960:1920, :] = a2
    # Feine dunkle Trennlinien zwischen den 3 Panels
    canvas[538:542, :, :3] = 0.08
    canvas[540:1080, 958:962, :3] = 0.08

    out_tmp = out_path + ".tmp.png"
    out_img = bpy.data.images.new("CloseupComposite", width=1920, height=1080, alpha=False)
    out_img.pixels.foreach_set(canvas.ravel())
    out_img.filepath_raw = out_tmp
    out_img.file_format = "PNG"
    out_img.save()
    os.replace(out_tmp, out_path)

    for im in (im1, im2, im3, out_img):
        bpy.data.images.remove(im)
    for fp in (p1, p2, p3):
        if os.path.exists(fp):
            os.remove(fp)

    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080


# ==============================================================================
# HAUPTPROZESS (53 FIGUREN + STRENGE ASSERTIONS + BLEND/GLB + 3 RENDERS)
# ==============================================================================
def main():
    t0 = time.time()
    project_root = get_project_root()
    blend_dir = os.path.join(project_root, "assets", "blend", "characters")
    glb_dir   = os.path.join(project_root, "assets", "glb", "characters")
    prev_dir  = os.path.join(project_root, "assets", "previews")
    os.makedirs(blend_dir, exist_ok=True)
    os.makedirs(glb_dir, exist_ok=True)
    os.makedirs(prev_dir, exist_ok=True)

    report_rows = []

    # --- TEIL A: NOAHS 8-KOEPFIGE HERO-FAMILIE ---
    print("[CHARS v2] === TEIL A: Baue Noahs 8-koepfige Hero-Familie (LOD0 6.5k-9.5k | LOD1 1.8k-2.4k | LOD2 450-650) ===", flush=True)
    scene = clear_scene()
    HumanService, TargetService, RigService = enable_mpfb()
    mat = create_character_trim_material(project_root)

    col_hp = bpy.data.collections.new("HighPoly_Master")
    col_web = bpy.data.collections.new("Web_LODs")
    scene.collection.children.link(col_hp)
    scene.collection.children.link(col_web)

    noah_hp_tris, noah_l0_tris, noah_l1_tris, noah_l2_tris = [], [], [], []

    for idx, spec in enumerate(NOAH_FAMILY_SPECS):
        hp_spec = dict(spec)
        hp_spec["name"] = spec["name"] + "_HP"
        hp_obj, _, _, prop_clr = build_mpfb_character(hp_spec, mat, HumanService, TargetService, RigService, col_hp)
        hp_t = count_tris(hp_obj)
        noah_hp_tris.append(hp_t)

        l0 = make_decimated_lod(hp_obj, spec["name"] + "_LOD0", HERO_LOD0_MIN, HERO_LOD0_MAX, HERO_LOD0_TGT, col_web, protect_face=True)
        l1 = make_decimated_lod(hp_obj, spec["name"] + "_LOD1", HERO_LOD1_MIN, HERO_LOD1_MAX, HERO_LOD1_TGT, col_web, protect_face=True)
        l2 = make_decimated_lod(hp_obj, spec["name"] + "_LOD2", HERO_LOD2_MIN, HERO_LOD2_MAX, HERO_LOD2_TGT, col_web, protect_face=False)

        h_m, min_z = assert_mesh_bounds(l0, spec["gender"])
        t0_c, t1_c, t2_c = count_tris(l0), count_tris(l1), count_tris(l2)
        noah_l0_tris.append(t0_c)
        noah_l1_tris.append(t1_c)
        noah_l2_tris.append(t2_c)
        report_rows.append((spec["name"], spec["gender"], h_m, min_z, t0_c, t1_c, t2_c, prop_clr))
        print(f"  [NOAH {idx+1}/8] {spec['name']:20s} ({spec['gender']}) H={h_m:.3f}m Zmin={min_z:.4f} | HP={hp_t:5d} | LOD0={t0_c:4d} | LOD1={t1_c:4d} | LOD2={t2_c:3d} | PropClr={prop_clr*100:.1f}cm", flush=True)

    noah_blend = os.path.join(blend_dir, "noah_family_kit.blend")
    bpy.ops.wm.save_as_mainfile(filepath=noah_blend)
    noah_glb = os.path.join(glb_dir, "noah_family_kit.glb")
    export_collection_glb(col_web, noah_glb)
    print(f"[CHARS v2] Gespeichert: {noah_blend} & {noah_glb} ({time.time()-t0:.1f}s)", flush=True)

    if "--noah-only" in sys.argv:
        # Schneller Kontroll-Render nur fuer Noahs 8-er Lineup
        for o in col_hp.objects:
            o.hide_render = True
        noah_l0_list = [bpy.data.objects[s["name"] + "_LOD0"] for s in NOAH_FAMILY_SPECS]
        for o in col_web.objects:
            o.hide_render = not o.name.endswith("_LOD0")
        dev, cam, cam_data = setup_studio(scene, samples=32)
        build_height_scale_wall(scene, y_pos=-0.65, width=7.0)
        for i, o in enumerate(noah_l0_list):
            o.location = ((i - 3.5) * 0.78, 0.0, 0.0)
        point_cam(cam, cam_data, (0.0, 7.6, 1.15), (0.0, 0.0, 0.98), lens=48.0)
        p_line = os.path.join(prev_dir, "noah_family_8_lineup.png")
        scene.render.filepath = p_line
        bpy.ops.render.render(write_still=True)
        print(f"[CHARS v2] Noah-Only Lineup fertig ({dev}): {p_line}", flush=True)
        return

    # --- TEIL B: 9 BUERGER-/PRIESTER-/FRAUEN-TYPEN x 5 VARIANTEN = 45 FIGUREN ---
    print("[CHARS v2] === TEIL B: Baue 9 MPFB-Typen x 5 Varianten (LOD0 3.0k-4.5k | 9x LOD1 850-1.1k | 9x LOD2 220-320) ===", flush=True)
    scene_c = clear_scene()
    HumanService, TargetService, RigService = enable_mpfb()
    mat_c = create_character_trim_material(project_root)

    col_c_hp = bpy.data.collections.new("HighPoly_BaseTypes")
    col_c_web = bpy.data.collections.new("Web_LODs")
    scene_c.collection.children.link(col_c_hp)
    scene_c.collection.children.link(col_c_web)

    cit_specs = get_citizen_specs()
    cit_hp_tris, cit_l0_tris, cit_l1_tris, cit_l2_tris = [], [], [], []
    cit_lod0_objs = []

    for g_idx in range(9):
        group_specs = cit_specs[g_idx * 5 : (g_idx + 1) * 5]
        g_name = group_specs[0]["group"]

        hp_base_spec = dict(group_specs[0])
        hp_base_spec["name"] = g_name + "_HP_Base"
        hp_base, _, _, prop_clr0 = build_mpfb_character(hp_base_spec, mat_c, HumanService, TargetService, RigService, col_c_hp)
        cit_hp_tris.append(count_tris(hp_base))

        l1_g = make_decimated_lod(hp_base, g_name + "_LOD1", CIT_LOD1_MIN, CIT_LOD1_MAX, CIT_LOD1_TGT, col_c_web, protect_face=True)
        l2_g = make_decimated_lod(hp_base, g_name + "_LOD2", CIT_LOD2_MIN, CIT_LOD2_MAX, CIT_LOD2_TGT, col_c_web, protect_face=False)
        t1_g, t2_g = count_tris(l1_g), count_tris(l2_g)
        cit_l1_tris.append(t1_g)
        cit_l2_tris.append(t2_g)

        for v_idx, v_spec in enumerate(group_specs):
            if v_idx == 0:
                l0_v = make_decimated_lod(hp_base, v_spec["name"] + "_LOD0", CIT_LOD0_MIN, CIT_LOD0_MAX, CIT_LOD0_TGT, col_c_web, protect_face=True)
                p_clr = prop_clr0
            else:
                raw_v, _, _, p_clr = build_mpfb_character(v_spec, mat_c, HumanService, TargetService, RigService, col_c_web)
                l0_v = make_decimated_lod(raw_v, v_spec["name"] + "_LOD0", CIT_LOD0_MIN, CIT_LOD0_MAX, CIT_LOD0_TGT, col_c_web, protect_face=True)
                bpy.data.objects.remove(raw_v, do_unlink=True)
            h_m, min_z = assert_mesh_bounds(l0_v, v_spec["gender"])
            t0_v = count_tris(l0_v)
            cit_l0_tris.append(t0_v)
            cit_lod0_objs.append(l0_v)
            report_rows.append((v_spec["name"], v_spec["gender"], h_m, min_z, t0_v, t1_g, t2_g, p_clr))

        print(f"  [CIT {g_idx+1}/9] {g_name:22s}: HP={cit_hp_tris[-1]:5d} | 5x LOD0={cit_l0_tris[-5:]} | LOD1={t1_g:4d} | LOD2={t2_g:3d}", flush=True)

    cit_blend = os.path.join(blend_dir, "mesopotamia_citizens_kit.blend")
    bpy.ops.wm.save_as_mainfile(filepath=cit_blend)
    cit_glb = os.path.join(glb_dir, "mesopotamia_citizens_kit.glb")
    export_collection_glb(col_c_web, cit_glb)
    print(f"[CHARS v2] Gespeichert: {cit_blend} & {cit_glb} ({time.time()-t0:.1f}s)", flush=True)

    # --- ASSERTION-ZUSAMMENFASSUNG FUER ALLE 53 FIGUREN ---
    fem_hs = [r[2] for r in report_rows if r[1] == "F"]
    male_hs = [r[2] for r in report_rows if r[1] == "M"]
    min_prop_clr = min(r[7] for r in report_rows)
    print("=" * 96, flush=True)
    print(f"[ASSERT PASS] Alle 53 Figuren geprueft!", flush=True)
    print(f"  Frauen ({len(fem_hs)}):  Min={min(fem_hs):.3f} m | Max={max(fem_hs):.3f} m  (Soll: {FEMALE_HEIGHT_MIN:.2f}..{FEMALE_HEIGHT_MAX:.2f} m)", flush=True)
    print(f"  Maenner ({len(male_hs)}): Min={min(male_hs):.3f} m | Max={max(male_hs):.3f} m  (Soll: {MALE_HEIGHT_MIN:.2f}..{MALE_HEIGHT_MAX:.2f} m)", flush=True)
    print(f"  Noah 8 Heroes: LOD0=[{min(noah_l0_tris)}..{max(noah_l0_tris)}] | LOD1=[{min(noah_l1_tris)}..{max(noah_l1_tris)}] | LOD2=[{min(noah_l2_tris)}..{max(noah_l2_tris)}]", flush=True)
    print(f"  45 Buerger:    LOD0=[{min(cit_l0_tris)}..{max(cit_l0_tris)}] | 9x LOD1=[{min(cit_l1_tris)}..{max(cit_l1_tris)}] | 9x LOD2=[{min(cit_l2_tris)}..{max(cit_l2_tris)}]", flush=True)
    print(f"  Min. Prop-Kopf-Abstand: {min_prop_clr*100:.1f} cm (Soll: >= {MIN_PROP_HEAD_CLEARANCE_M*100:.1f} cm)", flush=True)
    print("=" * 96, flush=True)

    stats = {
        "noah_hp_avg": sum(noah_hp_tris) // len(noah_hp_tris),
        "noah_lod0_avg": sum(noah_l0_tris) // len(noah_l0_tris),
        "noah_lod1_avg": sum(noah_l1_tris) // len(noah_l1_tris),
        "noah_lod2_avg": sum(noah_l2_tris) // len(noah_l2_tris),
        "cit_hp_avg": sum(cit_hp_tris) // len(cit_hp_tris),
        "cit_lod0_avg": sum(cit_l0_tris) // len(cit_l0_tris),
        "cit_lod1_avg": sum(cit_l1_tris) // len(cit_l1_tris),
        "cit_lod2_avg": sum(cit_l2_tris) // len(cit_l2_tris),
    }
    update_manifest(project_root, stats)

    # --- TEIL C: 3 PFLICHT-KONTROLLRENDERINGS (CYCLES CUDA + AgX) ---
    with bpy.data.libraries.load(noah_blend, link=False) as (data_from, data_to):
        data_to.objects = [n for n in data_from.objects if n.endswith("_LOD0")]
    noah_lod0_objs = []
    for spec in NOAH_FAMILY_SPECS:
        obj = bpy.data.objects.get(f"{spec['name']}_LOD0")
        if obj is not None:
            scene_c.collection.objects.link(obj)
            noah_lod0_objs.append(obj)

    for obj in col_c_hp.objects:
        obj.hide_render = True
    for obj in col_c_web.objects:
        if obj.name.endswith(("_LOD1", "_LOD2")):
            obj.hide_render = True

    dev, cam, cam_data = setup_studio(scene_c, samples=36, res_x=1920, res_y=1080)

    # 1) noah_family_8_lineup.png (Alle 8 Noah-Familienmitglieder + Meter-Referenzskala!)
    for o in cit_lod0_objs:
        o.hide_render = True
    for i, o in enumerate(noah_lod0_objs):
        o.hide_render = False
        o.location = ((i - 3.5) * 0.78, 0.0, 0.0)
    scale_objs = build_height_scale_wall(scene_c, y_pos=-0.65, width=8.6)
    point_cam(cam, cam_data, (0.0, 9.0, 1.12), (0.0, 0.0, 0.98), lens=44.0)
    p_lineup = os.path.join(prev_dir, "noah_family_8_lineup.png")
    scene_c.render.filepath = p_lineup
    bpy.ops.render.render(write_still=True)
    print(f"[PREVIEW 1/3] Gespeichert ({dev}): {p_lineup}", flush=True)
    for so in scale_objs:
        so.hide_render = True

    # 2) characters_closeup_details.png (3-Zonen-Nahaufnahme: Gesichter, Props/Balken, Fuesse/Sandalen)
    p_close = os.path.join(prev_dir, "characters_closeup_details.png")
    render_closeup_3panel_composite(scene_c, cam, cam_data, noah_lod0_objs, cit_lod0_objs, p_close)
    print(f"[PREVIEW 2/3] Gespeichert ({dev}): {p_close}", flush=True)

    # 3) characters_showcase_53.png (Alle 53 Figuren sauber gestaffelt!)
    for idx, obj in enumerate(noah_lod0_objs):
        obj.hide_render = False
        obj.location = ((idx - 3.5) * 1.12, -3.5, 0.0)
    for g_idx in range(9):
        for v_idx in range(5):
            obj = cit_lod0_objs[g_idx * 5 + v_idx]
            obj.hide_render = False
            row = g_idx // 3
            col_in_row = (g_idx % 3) * 5 + v_idx
            obj.location = ((col_in_row - 7.0) * 0.92, -1.35 + row * 1.55, 0.0)
    point_cam(cam, cam_data, (0.0, 14.4, 5.4), (0.0, -0.35, 0.85), lens=36.0)
    p_show = os.path.join(prev_dir, "characters_showcase_53.png")
    scene_c.render.filepath = p_show
    bpy.ops.render.render(write_still=True)
    print(f"[PREVIEW 3/3] Gespeichert ({dev}): {p_show}", flush=True)
    print(f"[CHARS v2] ALLES FERTIG in {time.time()-t0:.1f}s!", flush=True)


if __name__ == "__main__":
    main()
