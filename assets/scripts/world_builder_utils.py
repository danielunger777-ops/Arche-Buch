"""
world_builder_utils.py — Gemeinsame Blender-5.3-Helfer für die Weltszenen-Master (Werft & Ararat)
==================================================================================================
Enthält:
  - Projektpfade & Cycles CUDA (GTX 1070 + OIDN) Setup
  - Verlustfreien 16-Bit-Grayscale- & 8-Bit-RGBA-PNG-Writer (ohne Gamma-/Color-Management-Drift)
  - AssetLinker für sauberes Blender-Library-Linking (`link=True`) aus assets/blend/
  - Arche-Rumpf-Platzhalter (300 x 50 x 30 Ellen = 140.0 x 23.333 x 14.0 m)
  - glTF-2.0-Terrain-Exporter (+Y Up) & Layout-JSON-Writer
"""

import os
import json
import math
import struct
import zlib
import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix, Euler
from mathutils.bvhtree import BVHTree


def get_project_root():
    if "__file__" in globals():
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.getcwd()


ROOT_DIR = get_project_root()
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
BLEND_DIR = os.path.join(ASSETS_DIR, "blend")
WORLDS_BLEND_DIR = os.path.join(BLEND_DIR, "worlds")
WORLDS_OUT_DIR = os.path.join(ASSETS_DIR, "worlds")
TEXTURES_DIR = os.path.join(ASSETS_DIR, "textures")
PREVIEWS_DIR = os.path.join(ASSETS_DIR, "previews")

ELLE_M = 14.0 / 30.0  # 0.4666667 m
ARK_LEN_X = 140.0     # 300 Ellen
ARK_BEAM_Y = 70.0 / 3.0  # 23.333333 m (50 Ellen)
ARK_HEIGHT_Z = 14.0   # 30 Ellen


def ensure_dirs():
    for d in (WORLDS_BLEND_DIR, WORLDS_OUT_DIR, PREVIEWS_DIR):
        os.makedirs(d, exist_ok=True)


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    return scene


def setup_cycles(scene, samples=40, use_oidn=True, res_x=1600, res_y=900):
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
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.025
        scene.cycles.use_denoising = bool(use_oidn)
        if use_oidn and hasattr(scene.cycles, "denoiser"):
            try:
                scene.cycles.denoiser = "OPENIMAGEDENOISE"
            except Exception:
                pass
        scene.cycles.max_bounces = 4
        scene.cycles.diffuse_bounces = 2
        scene.cycles.glossy_bounces = 2
        scene.cycles.transmission_bounces = 2
        scene.cycles.transparent_max_bounces = 8
        scene.cycles.volume_bounces = 0

    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"

    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        scene.view_settings.view_transform = "Filmic"
        scene.view_settings.look = "None"
    scene.view_settings.exposure = -0.35
    return "CUDA (GPU)" if used_gpu else "CPU"


def _png_chunk(tag, data):
    return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def write_png_uint16_gray(filepath, arr_u16):
    """Schreibt 2D uint16-Array (H, W) verlustfrei als 16-Bit-Grayscale-PNG."""
    h, w = arr_u16.shape
    be = np.ascontiguousarray(arr_u16, dtype=">u2")
    raw = np.empty((h, w * 2 + 1), dtype=np.uint8)
    raw[:, 0] = 0
    raw[:, 1:] = be.view(np.uint8).reshape(h, w * 2)
    ihdr = struct.pack("!IIBBBBB", w, h, 16, 0, 0, 0, 0)
    idat = zlib.compress(raw.tobytes(), level=6)
    with open(filepath, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(_png_chunk(b"IHDR", ihdr))
        f.write(_png_chunk(b"IDAT", idat))
        f.write(_png_chunk(b"IEND", b""))


def write_png_rgba8(filepath, arr_u8):
    """Schreibt 3D uint8-Array (H, W, 4) verlustfrei als 8-Bit-RGBA-PNG."""
    h, w, c = arr_u8.shape
    assert c == 4
    arr = np.ascontiguousarray(arr_u8, dtype=np.uint8)
    raw = np.empty((h, w * 4 + 1), dtype=np.uint8)
    raw[:, 0] = 0
    raw[:, 1:] = arr.reshape(h, w * 4)
    ihdr = struct.pack("!IIBBBBB", w, h, 8, 6, 0, 0, 0)
    idat = zlib.compress(raw.tobytes(), level=6)
    with open(filepath, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(_png_chunk(b"IHDR", ihdr))
        f.write(_png_chunk(b"IDAT", idat))
        f.write(_png_chunk(b"IEND", b""))


def get_or_create_collection(name, parent=None):
    if name in bpy.data.collections:
        col = bpy.data.collections[name]
    else:
        col = bpy.data.collections.new(name)
        if parent is None:
            bpy.context.scene.collection.children.link(col)
        else:
            parent.children.link(col)
    return col


def load_image_cached(rel_path, colorspace="sRGB"):
    abs_path = os.path.abspath(os.path.join(ASSETS_DIR, "textures", rel_path))
    for img in bpy.data.images:
        if os.path.abspath(bpy.path.abspath(img.filepath)) == abs_path:
            img.colorspace_settings.name = colorspace
            return img
    img = bpy.data.images.load(abs_path)
    img.colorspace_settings.name = colorspace
    return img


class AssetLinker:
    """Verlinkt Mesh-Datenbloecke aus bestehenden .blend-Kits mit Caching."""

    def __init__(self):
        self.mesh_cache = {}
        self.available_cache = {}
        self.inst_counter = 0

    def _inspect_blend(self, rel_blend_path):
        abs_path = os.path.abspath(os.path.join(BLEND_DIR, rel_blend_path))
        if abs_path not in self.available_cache:
            with bpy.data.libraries.load(abs_path, link=True) as (data_from, _):
                self.available_cache[abs_path] = set(data_from.meshes)
        return abs_path, self.available_cache[abs_path]

    def preload_meshes(self, rel_blend_path, mesh_names):
        abs_path, avail = self._inspect_blend(rel_blend_path)
        to_load = [m for m in mesh_names if m in avail and (abs_path, m) not in self.mesh_cache]
        if not to_load:
            return
        with bpy.data.libraries.load(abs_path, link=True) as (data_from, data_to):
            data_to.meshes = to_load
        for m in data_to.meshes:
            if m is not None:
                self.mesh_cache[(abs_path, m.name)] = m

    def link_mesh(self, rel_blend_path, mesh_name):
        abs_path, avail = self._inspect_blend(rel_blend_path)
        key = (abs_path, mesh_name)
        if key in self.mesh_cache:
            return self.mesh_cache[key]
        if mesh_name not in avail:
            return None
        with bpy.data.libraries.load(abs_path, link=True) as (data_from, data_to):
            data_to.meshes = [mesh_name]
        if data_to.meshes and data_to.meshes[0] is not None:
            self.mesh_cache[key] = data_to.meshes[0]
            return data_to.meshes[0]
        return None

    def spawn(
        self,
        collection,
        rel_blend_path,
        mesh_name,
        asset_key,
        location,
        rotation=(0.0, 0.0, 0.0),
        scale=(1.0, 1.0, 1.0),
        tint=None,
        layout_records=None,
        name_prefix=None,
    ):
        mesh = self.link_mesh(rel_blend_path, mesh_name)
        if mesh is None:
            raise KeyError(f"Mesh '{mesh_name}' not found in '{rel_blend_path}'")
        self.inst_counter += 1
        obj_name = f"{name_prefix or asset_key}_{self.inst_counter:05d}"
        obj = bpy.data.objects.new(obj_name, mesh)
        obj.location = (float(location[0]), float(location[1]), float(location[2]))
        obj.rotation_mode = "XYZ"
        obj.rotation_euler = (float(rotation[0]), float(rotation[1]), float(rotation[2]))
        obj.scale = (float(scale[0]), float(scale[1]), float(scale[2]))
        obj["arche_asset_key"] = asset_key
        if tint is not None:
            obj.color = (float(tint[0]), float(tint[1]), float(tint[2]), 1.0)
        collection.objects.link(obj)
        if layout_records is not None:
            tint_out = [round(float(tint[0]), 3), round(float(tint[1]), 3), round(float(tint[2]), 3)] if tint is not None else [1.0, 1.0, 1.0]
            layout_records.append({
                "assetKey": asset_key,
                "x": round(float(location[0]), 3),
                "y": round(float(location[1]), 3),
                "z": round(float(location[2]), 3),
                "rx": round(float(rotation[0]), 4),
                "ry": round(float(rotation[1]), 4),
                "rz": round(float(rotation[2]), 4),
                "sx": round(float(scale[0]), 3),
                "sy": round(float(scale[1]), 3),
                "sz": round(float(scale[2]), 3),
                "tint": tint_out,
            })
        return obj


def build_ark_placeholder(collection, z_sole=0.0):
    """Erstellt einen massgenauen 140 x 23.333 x 14 m Arche-Rumpf-Platzhalter inkl. 3 Außenkielen & Zohar."""
    objs = []
    # Material 1: Kopher-Pech-Aussenhaut (dunkles Bitumen-Braunschwarz)
    mat_kopher = bpy.data.materials.new("Mat_Ark_Placeholder_Kopher")
    mat_kopher.use_nodes = True
    bsdf_k = mat_kopher.node_tree.nodes.get("Principled BSDF")
    bsdf_k.inputs["Base Color"].default_value = (0.048, 0.036, 0.028, 1.0)
    bsdf_k.inputs["Roughness"].default_value = 0.62

    # Material 2: Zeder-Dach & Zohar-Trim
    mat_cedar = bpy.data.materials.new("Mat_Ark_Placeholder_Cedar")
    mat_cedar.use_nodes = True
    bsdf_c = mat_cedar.node_tree.nodes.get("Principled BSDF")
    bsdf_c.inputs["Base Color"].default_value = (0.24, 0.14, 0.075, 1.0)
    bsdf_c.inputs["Roughness"].default_value = 0.78

    bm = bmesh.new()
    hx = ARK_LEN_X * 0.5   # 70.0
    hy = ARK_BEAM_Y * 0.5  # 11.6667
    hz = ARK_HEIGHT_Z      # 14.0

    # Haupt-Kastenrumpf (0 .. 13.0 m)
    res_body = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(ARK_LEN_X, ARK_BEAM_Y, 13.0), verts=res_body["verts"])
    bmesh.ops.translate(bm, vec=(0.0, 0.0, z_sole + 6.5), verts=res_body["verts"])
    for f in bm.faces:
        f.material_index = 0

    # 3 Außenkiele (Z = -0.467 .. 0.0 m bei Y = -8.167, 0.0, +8.167)
    for yk in (-8.167, 0.0, 8.167):
        rk = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(138.0, 0.55, 0.467), verts=rk["verts"])
        bmesh.ops.translate(bm, vec=(0.0, yk, z_sole - 0.2335), verts=rk["verts"])
        for v in rk["verts"]:
            for f in v.link_faces:
                f.material_index = 0

    # Leicht gewölbtes Dach + Zohar-Oberlichtaufsatz (Z = 13.0 .. 14.0 m)
    r_roof = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(ARK_LEN_X + 0.6, ARK_BEAM_Y + 0.6, 0.55), verts=r_roof["verts"])
    bmesh.ops.translate(bm, vec=(0.0, 0.0, z_sole + 13.275), verts=r_roof["verts"])
    for v in r_roof["verts"]:
        for f in v.link_faces:
            f.material_index = 1

    r_zohar = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(128.0, 2.8, 0.55), verts=r_zohar["verts"])
    bmesh.ops.translate(bm, vec=(0.0, 0.0, z_sole + 13.725), verts=r_zohar["verts"])
    for v in r_zohar["verts"]:
        for f in v.link_faces:
            f.material_index = 1

    # Seitentor-Rahmen Markierung Backbord bei X = -5.0, Y = -11.67, Z = 6.6..10.3
    r_gate = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(4.4, 0.45, 3.8), verts=r_gate["verts"])
    bmesh.ops.translate(bm, vec=(-5.0, -hy - 0.12, z_sole + 8.3), verts=r_gate["verts"])
    for v in r_gate["verts"]:
        for f in v.link_faces:
            f.material_index = 1

    mesh = bpy.data.meshes.new("Ark_Placeholder_140x23x14_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(mat_kopher)
    mesh.materials.append(mat_cedar)

    obj = bpy.data.objects.new("Ark_Placeholder_300x50x30_Cubits", mesh)
    obj["arche_placeholder"] = True
    obj["dimensions_m"] = "140.0 x 23.333 x 14.0"
    collection.objects.link(obj)
    objs.append(obj)
    return objs


class MeshTerrainSampler:
    """Exakter BVH-Raycast-Sampler auf dem real erzeugten Terrain-Mesh (0 % Schweben an Steilhaengen)."""

    def __init__(self, terrain_obj):
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        self.bvh = BVHTree.FromObject(terrain_obj, depsgraph)

    def sample_z(self, x, y, fallback_z=0.0):
        loc, _, _, _ = self.bvh.ray_cast(Vector((float(x), float(y), 2000.0)), Vector((0.0, 0.0, -1.0)), 4000.0)
        if loc is not None:
            return float(loc.z)
        return float(fallback_z)

    def sample_footprint(self, x, y, radius, fallback_fn, n_ring=8):
        zc = self.sample_z(x, y, fallback_fn(x, y))
        z_min = zc
        z_max = zc
        if radius > 1e-4 and n_ring > 0:
            for k in range(n_ring):
                ang = (k / float(n_ring)) * math.tau
                px = x + math.cos(ang) * radius
                py = y + math.sin(ang) * radius
                pz = self.sample_z(px, py, fallback_fn(px, py))
                if pz < z_min:
                    z_min = pz
                if pz > z_max:
                    z_max = pz
        slope_est = (z_max - z_min) / max(0.5, 2.0 * float(radius))
        return zc, z_min, z_max, slope_est

    def ground_tree_z(self, x, y, root_radius, fallback_fn, extra_sink=0.22):
        _, z_min, _, slope_est = self.sample_footprint(x, y, root_radius, fallback_fn, n_ring=8)
        return z_min - float(extra_sink) - 0.35 * slope_est * float(root_radius)


def setup_nishita_sky_and_sun(
    scene,
    sun_elev_deg=30.0,
    sun_azim_deg=135.0,
    sun_energy=3.2,
    dust_density=1.1,
    air_density=1.1,
    bg_strength=0.18,
    sun_color=(1.0, 0.93, 0.82),
):
    world = bpy.data.worlds.new("Arche_World_Sky")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()

    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    # MULTIPLE_SCATTERING sky outputs high physical radiance; keep strength balanced for crisp contrast
    bg.inputs["Strength"].default_value = float(bg_strength)

    sky = nt.nodes.new("ShaderNodeTexSky")
    avail_types = [e.identifier for e in sky.bl_rna.properties["sky_type"].enum_items]
    for cand in ("MULTIPLE_SCATTERING", "NISHITA", "SINGLE_SCATTERING", "HOSEK_WILKIE"):
        if cand in avail_types:
            sky.sky_type = cand
            break
    if hasattr(sky, "sun_disc"):
        sky.sun_disc = False
    sky.sun_elevation = math.radians(sun_elev_deg)
    sky.sun_rotation = math.radians(sun_azim_deg)
    if hasattr(sky, "altitude"):
        sky.altitude = 450.0
    if hasattr(sky, "air_density"):
        sky.air_density = air_density
    if hasattr(sky, "dust_density"):
        sky.dust_density = dust_density
    if hasattr(sky, "ozone_density"):
        sky.ozone_density = 1.0

    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    # Gerichtete Sonne passend zu Nishita-Richtung
    elev = math.radians(sun_elev_deg)
    azim = math.radians(sun_azim_deg)
    sun_dir = Vector((math.sin(azim) * math.cos(elev), math.cos(azim) * math.cos(elev), math.sin(elev))).normalized()

    light_data = bpy.data.lights.new("Sun_Arche_Main", type="SUN")
    light_data.energy = sun_energy
    light_data.angle = math.radians(1.1)
    light_data.color = (float(sun_color[0]), float(sun_color[1]), float(sun_color[2]))
    light_obj = bpy.data.objects.new("Sun_Arche_Main", light_data)
    light_obj.location = (0.0, 0.0, 200.0)
    light_obj.rotation_euler = sun_dir.to_track_quat("Z", "Y").to_euler()
    return light_obj


def add_camera(collection, name, location, target, lens=32.0, clip_end=15000.0):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_data.clip_start = 0.25
    cam_data.clip_end = clip_end
    cam_obj = bpy.data.objects.new(name, cam_data)
    cam_obj.location = Vector(location)
    direction = (Vector(target) - Vector(location)).normalized()
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    collection.objects.link(cam_obj)
    return cam_obj


def export_selected_objects_glb(objects, glb_path):
    """Exportiert nur ausgewaehlte Meshes als glTF 2.0 Binary (.glb) mit +Y Up."""
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.gltf(
        filepath=glb_path,
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
        export_image_format="AUTO",
    )
    bpy.ops.object.select_all(action="DESELECT")
