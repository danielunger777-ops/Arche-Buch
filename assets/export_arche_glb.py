"""
export_arche_glb.py — Blender -> ARCHE 2.0/3.0 (.glb) Master-Exporter (Vollausbau)
===================================================================================

Ausführung im Blender Scripting-Tab ("Run Script") oder per CLI:
    blender --background assets/blend/world/ararat_altar_cyclopean.blend --python assets/export_arche_glb.py -- --category world --lods --preview
    blender --background assets/blend/botany/tree_cedar_01.blend --python assets/export_arche_glb.py -- --category botany --bake --lods --preview
    blender --background assets/blend/families/fam_bovid.blend --python assets/export_arche_glb.py -- --category family --bake --bake-sss

Funktionen gemäß BLENDER_PIPELINE.md:
  1. Category-Budgets & Pflicht-Tagging prüfen (ark: Col_Meta, botany: Col_Wind, family: Col_Rig + ShapeKeys).
  2. Transforms (Rotation/Scale) anwenden & Pivot auf BBox-Unterkante (Z=0) zentrieren (--keep-pivot für Drehachsen/Fundamente).
  3. Optionaler Auto-Bake (--bake): Cycles BaseColor (inkl. Pointiness/Cavity), Normal, gepackte ORM-Textur (R=AO, G=Roughness, B=Metallic) & optional Thickness-Maske für Echtzeit-SSS (--bake-sss).
  4. glTF 2.0 Binary Export (+Y Up, Morph Targets / Shape Keys, Color Attributes, Tangents/Normals, Sheen/Clearcoat/Anisotropy/Iridescence).
  5. Optionale LOD1/LOD2-Decimate-Varianten (--lods) & headless Vorschau-Render nach assets/previews/<name>.png (--preview).
  6. Synchronisiert assets/manifest.json (categories + slots).
"""

import os
import sys
import json
import math
import datetime
import bpy
import addon_utils
from mathutils import Vector

# ==============================================================================
# KATEGORIE-BUDGETS & PFLICHT-TAGS (BLENDER_PIPELINE.md Kap. 2 & 4)
# ==============================================================================
CATEGORY_CONFIG = {
    "ark": {
        "manifest_group": "ark",
        "subdir": "ark",
        "min_tris": 2000,
        "max_tris": 15000,
        "max_mats": 2,
        "max_tex": 1024,
        "lod1_ratio": 0.45,
        "lod2_ratio": 0.18,
        "required_color_attr": "Col_Meta",
        "require_shapekeys": False,
        "sss_default": False,
        "label": "Arche Struktur-Modul",
    },
    "botany": {
        "manifest_group": "botany",
        "subdir": "botany",
        "min_tris": 1500,
        "max_tris": 4000,
        "max_mats": 2,
        "max_tex": 1024,
        "lod1_ratio": 0.28,
        "lod2_ratio": 0.02,
        "lod2_target_tris": 32,
        "required_color_attr": "Col_Wind",
        "require_shapekeys": False,
        "sss_default": True,
        "label": "Botanik / Baum-Variante",
    },
    "world": {
        "manifest_group": "world",
        "subdir": "world",
        "min_tris": 300,
        "max_tris": 2500,
        "max_mats": 1,
        "max_tex": 1024,
        "lod1_ratio": 0.40,
        "lod2_ratio": 0.15,
        "required_color_attr": None,
        "require_shapekeys": False,
        "sss_default": False,
        "label": "Gebäude / Werft-Modul",
    },
    "family": {
        "manifest_group": "families",
        "subdir": "families",
        "min_tris": 1200,
        "max_tris": 3000,
        "max_mats": 1,
        "max_tex": 512,
        "lod1_ratio": 0.45,
        "lod2_ratio": 0.20,
        "required_color_attr": "Col_Rig",
        "require_shapekeys": True,
        "sss_default": True,
        "label": "Tier-Familie (+Shape Keys)",
    },
    "character": {
        "manifest_group": "characters",
        "subdir": "characters",
        "min_tris": 4000,
        "max_tris": 8000,
        "max_mats": 2,
        "max_tex": 1024,
        "lod1_ratio": 0.45,
        "lod2_ratio": 0.18,
        "required_color_attr": None,
        "require_shapekeys": False,
        "sss_default": True,
        "label": "Hero-Charakter",
    },
    "prop": {
        "manifest_group": "ark",
        "subdir": "ark",
        "min_tris": 150,
        "max_tris": 800,
        "max_mats": 1,
        "max_tex": 512,
        "lod1_ratio": 0.45,
        "lod2_ratio": 0.20,
        "required_color_attr": None,
        "require_shapekeys": False,
        "sss_default": False,
        "label": "Kleinst-Requisit",
    },
}

CLASS_ALIASES = {
    "ark": "ark",
    "botany": "botany",
    "vegetation": "botany",
    "tree": "botany",
    "world": "world",
    "building": "world",
    "env": "world",
    "family": "family",
    "families": "family",
    "animal": "family",
    "character": "character",
    "characters": "character",
    "hero_character": "character",
    "prop": "prop",
}

ENABLE_DRACO_DEFAULT = False
AUTO_ENABLE_IN_MANIFEST = True


def parse_cli_args():
    """Liest optionale Argumente hinter '--' aus sys.argv."""
    opts = {
        "slot": None,
        "category": None,
        "draco": ENABLE_DRACO_DEFAULT,
        "enable": AUTO_ENABLE_IN_MANIFEST,
        "bake": False,
        "bake_size": None,
        "bake_sss": False,
        "lods": False,
        "preview": False,
        "keep_pivot": False,
    }
    if "--" not in sys.argv:
        return opts
    tail = sys.argv[sys.argv.index("--") + 1:]
    i = 0
    while i < len(tail):
        arg = tail[i]
        if arg == "--slot" and i + 1 < len(tail):
            opts["slot"] = tail[i + 1].strip()
            i += 2
        elif arg in ("--category", "--class") and i + 1 < len(tail):
            raw_cat = tail[i + 1].strip().lower()
            opts["category"] = CLASS_ALIASES.get(raw_cat, raw_cat)
            i += 2
        elif arg == "--draco":
            opts["draco"] = True
            i += 1
        elif arg == "--enable":
            opts["enable"] = True
            i += 1
        elif arg == "--no-enable":
            opts["enable"] = False
            i += 1
        elif arg == "--bake":
            opts["bake"] = True
            i += 1
        elif arg == "--bake-size" and i + 1 < len(tail):
            opts["bake_size"] = int(tail[i + 1])
            i += 2
        elif arg == "--bake-sss":
            opts["bake"] = True
            opts["bake_sss"] = True
            i += 1
        elif arg == "--lods":
            opts["lods"] = True
            i += 1
        elif arg == "--preview":
            opts["preview"] = True
            i += 1
        elif arg == "--keep-pivot":
            opts["keep_pivot"] = True
            i += 1
        else:
            i += 1
    return opts


def resolve_assets_dir():
    """Ermittelt das assets/-Verzeichnis zuverlässig (CLI, Text-Editor oder .blend-Pfad)."""
    if "__file__" in globals():
        candidate = os.path.dirname(os.path.abspath(__file__))
        if os.path.basename(candidate).lower() == "assets":
            return candidate
    if bpy.data.filepath:
        cur = os.path.dirname(os.path.abspath(bpy.data.filepath))
        for _ in range(4):
            if os.path.isfile(os.path.join(cur, "manifest.json")) or os.path.isdir(os.path.join(cur, "glb")):
                return cur
            probe_assets = os.path.join(cur, "assets")
            if os.path.isdir(probe_assets):
                return probe_assets
            cur = os.path.dirname(cur)
    cwd_assets = os.path.join(os.getcwd(), "assets")
    if os.path.isdir(cwd_assets):
        return cwd_assets
    raise RuntimeError("Konnte 'assets/' Verzeichnis nicht finden.")


def infer_slot_name(cli_slot):
    """Bestimmt den Slot-/Dateinamen aus CLI-Flag, .blend-Dateiname oder aktivem Objekt."""
    if cli_slot:
        return cli_slot
    if bpy.data.filepath:
        stem = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
        if stem:
            return stem
    if bpy.context.active_object and bpy.context.active_object.name:
        return bpy.context.active_object.name.lower().replace(" ", "_")
    return bpy.context.scene.name.lower().replace(" ", "_")


def infer_category(slot_name, cli_cat):
    """Ordnet einen Export-Slot bzw. .blend-Pfad einer der 6 Budget-Kategorien zu."""
    if cli_cat in CATEGORY_CONFIG:
        return cli_cat
    path_hint = (bpy.data.filepath or "").lower().replace("\\", "/")
    for folder, cat in (
        ("/ark/", "ark"),
        ("/botany/", "botany"),
        ("/world/", "world"),
        ("/families/", "family"),
        ("/characters/", "character"),
    ):
        if folder in path_hint:
            return cat
    s = slot_name.lower()
    if s.startswith("ark_") or "sole" in s or "bulkhead" in s or "zohar" in s or "badgir" in s:
        return "ark"
    if any(k in s for k in ("tree_", "shrub_", "grass_", "olive_", "palm", "cedar", "cypress", "veg")):
        return "botany"
    if s.startswith("fam_") or any(k in s for k in ("ox_", "dove_", "raven", "bovid", "cervid", "animal")):
        return "family"
    if s.startswith("char_") or any(k in s for k in ("noah", "wife", "son_", "daughter_", "worker")):
        return "character"
    if s.startswith(("env_", "city_", "ararat_", "boat_")) or "altar" in s or "bench" in s:
        return "world"
    return "prop"


def collect_export_meshes():
    """Sammelt alle sichtbaren Mesh-Objekte der aktiven Szene."""
    meshes = [
        obj for obj in bpy.context.scene.objects
        if obj.type == "MESH" and not obj.hide_viewport and obj.visible_get()
    ]
    if not meshes:
        raise RuntimeError("Keine sichtbaren Mesh-Objekte in der Szene gefunden!")
    return meshes


def ensure_single_user_meshes(meshes):
    """Löst Multi-User-Mesh-Links auf, damit Transform-Apply pro Objekt sicher funktioniert."""
    for obj in meshes:
        if obj.data and obj.data.users > 1:
            obj.data = obj.data.copy()


def apply_rotation_and_scale(meshes):
    """Wendet Rotation & Scale auf alle Mesh-Objekte an (Ctrl+A -> Rotation & Scale)."""
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def center_origin_to_bottom_bbox(meshes, keep_pivot=False):
    """
    Berechnet die Welt-Bounding-Box und setzt den Origin auf X/Y-Mitte, Z=0
    (bzw. behält vorhandene Dreh-/Fundament-Pivots bei keep_pivot=True).
    """
    depsgraph = bpy.context.evaluated_depsgraph_get()
    min_x = min_y = min_z = float("inf")
    max_x = max_y = max_z = float("-inf")

    for obj in meshes:
        eval_obj = obj.evaluated_get(depsgraph)
        temp_mesh = eval_obj.to_mesh()
        try:
            mat_w = eval_obj.matrix_world
            for v in temp_mesh.vertices:
                w_co = mat_w @ v.co
                min_x = min(min_x, w_co.x)
                min_y = min(min_y, w_co.y)
                min_z = min(min_z, w_co.z)
                max_x = max(max_x, w_co.x)
                max_y = max(max_y, w_co.y)
                max_z = max(max_z, w_co.z)
        finally:
            eval_obj.to_mesh_clear()

    if min_x == float("inf"):
        raise RuntimeError("Export-Meshes enthalten keine Vertices.")

    if not keep_pivot:
        cx = 0.5 * (min_x + max_x)
        cy = 0.5 * (min_y + max_y)
        shift = Vector((-cx, -cy, -min_z))
        mesh_set = set(meshes)
        for obj in meshes:
            if obj.parent not in mesh_set:
                obj.location += shift
        bpy.context.view_layer.update()

        bpy.ops.object.select_all(action="DESELECT")
        for obj in meshes:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        min_z, max_z = 0.0, max_z - min_z

    dims = (max_x - min_x, max_y - min_y, max_z - min_z)
    print(f"[ARCHE EXPORT] Pivot {'beibehalten' if keep_pivot else 'Z=0 zentriert'} | Maße: {dims[0]:.2f}x{dims[1]:.2f}x{dims[2]:.2f} m | Z:[{min_z:.2f}, {max_z:.2f}]")
    return dims, min_z


def _has_color_attribute(mesh_data, attr_name):
    if hasattr(mesh_data, "color_attributes") and attr_name in mesh_data.color_attributes:
        return True
    if hasattr(mesh_data, "vertex_colors") and attr_name in mesh_data.vertex_colors:
        return True
    return False


def inspect_category_and_budget(meshes, category, min_z):
    """Prüft Dreiecke, Materialien, Texturgrößen sowie Pflicht-Tags je Kategorie."""
    cfg = CATEGORY_CONFIG[category]
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total_tris = 0
    unique_mats = set()
    oversized_textures = []
    warnings = []

    has_req_col = (cfg["required_color_attr"] is None)
    has_shapekeys = False
    mat_names_lower = set()

    for obj in meshes:
        eval_obj = obj.evaluated_get(depsgraph)
        temp_mesh = eval_obj.to_mesh()
        try:
            temp_mesh.calc_loop_triangles()
            total_tris += len(temp_mesh.loop_triangles)
        finally:
            eval_obj.to_mesh_clear()

        if cfg["required_color_attr"] and _has_color_attribute(obj.data, cfg["required_color_attr"]):
            has_req_col = True
        if obj.data.shape_keys and len(obj.data.shape_keys.key_blocks) > 1:
            has_shapekeys = True

        for slot in obj.material_slots:
            if not slot.material:
                continue
            mat = slot.material
            unique_mats.add(mat.name)
            mat_names_lower.add(mat.name.lower())
            if mat.node_tree:
                for node in mat.node_tree.nodes:
                    if node.type == "TEX_IMAGE" and node.image:
                        w, h = node.image.size[0], node.image.size[1]
                        if max(w, h) > cfg["max_tex"]:
                            oversized_textures.append(f"{node.image.name} ({w}x{h} > {cfg['max_tex']})")

    mat_count = len(unique_mats)
    print(f"[ARCHE EXPORT] Kategorie: {cfg['label']} ({category}) | Meshes: {len(meshes)} | Tris: {total_tris} / {cfg['max_tris']} | Mats: {mat_count} / {cfg['max_mats']}")

    if total_tris > cfg["max_tris"]:
        warnings.append(f"Polygon-Budget überschritten: {total_tris} > {cfg['max_tris']} Tris")
    if mat_count > cfg["max_mats"]:
        warnings.append(f"Material-Budget überschritten: {mat_count} > {cfg['max_mats']} Mats")
    if oversized_textures:
        warnings.append("Textur-Limit überschritten: " + ", ".join(oversized_textures))
    if not has_req_col:
        warnings.append(f"Pflicht-Color-Attribute '{cfg['required_color_attr']}' fehlt (s. BLENDER_PIPELINE.md)")
    if cfg["require_shapekeys"] and not has_shapekeys:
        warnings.append("Tier-Familie ohne Shape Keys (Morph Targets: Key_NeckLegLength, Key_BodyBulk, ...)")
    if category == "botany" and not (any("bark" in m for m in mat_names_lower) and any("foliage" in m for m in mat_names_lower)):
        warnings.append("Botanik-Empfehlung: Material-Slots idealerweise als 'Bark' (0) und 'Foliage' (1) benennen")
    if category == "world" and min_z > -0.20:
        warnings.append(f"Fundament-Hinweis: min_z={min_z:.2f}m (Gebäude/Stege idealerweise bis Z=-0.50m mit --keep-pivot für Hänge)")

    for w in warnings:
        print(f"[WARNUNG] {w}")

    return {
        "tris": total_tris,
        "meshes": len(meshes),
        "materials": mat_count,
        "max_tris": cfg["max_tris"],
        "has_required_tag": has_req_col,
        "has_shapekeys": has_shapekeys,
        "warnings": warnings,
    }


def _ensure_uv_maps(meshes):
    """Legt bei Meshes ohne UV-Map automatisch ein Smart-UV-Layout an."""
    for obj in meshes:
        if obj.data.uv_layers:
            continue
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.02)
        bpy.ops.object.mode_set(mode="OBJECT")


def _find_principled_bsdf(mat):
    if not mat or not mat.node_tree:
        return None
    for n in mat.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED":
            return n
    return None


def _get_socket_default_scalar(node, names, fallback=0.0):
    for nm in names:
        sock = node.inputs.get(nm)
        if sock is not None and not sock.is_linked and hasattr(sock, "default_value"):
            try:
                return float(sock.default_value)
            except Exception:
                pass
    return fallback


def _create_bake_image(name, size, colorspace="sRGB"):
    img = bpy.data.images.get(name)
    if img:
        bpy.data.images.remove(img)
    img = bpy.data.images.new(name=name, width=size, height=size, alpha=False, float_buffer=False)
    img.colorspace_settings.name = colorspace
    return img


def _enable_cycles_engine(scene):
    """Aktiviert bei Bedarf das Cycles-Addon (für Blender 4.x/5.x Headless-Baking)."""
    try:
        engines = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
    except Exception:
        engines = []
    if "CYCLES" not in engines:
        try:
            addon_utils.enable("cycles", default_set=False, persistent=False)
        except Exception:
            pass
    scene.render.engine = "CYCLES"
    if hasattr(scene, "cycles"):
        scene.cycles.device = "CPU"
        scene.cycles.samples = 16


def _ensure_material_nodes(mat):
    if mat.node_tree is None and hasattr(mat, "use_nodes"):
        mat.use_nodes = True


def bake_pbr_textures(meshes, assets_dir, slot_name, tex_size, bake_sss=False):
    """
    Backt BaseColor [sRGB] (inkl. Pointiness/Cavity-Nodes, ohne Sonnen-Schlagschatten),
    Normal [Non-Color], gepackte ORM-Textur (R=AO, G=Roughness, B=Metallic, Non-Color)
    und optional Thickness-SSS-Maske [Non-Color] nach assets/textures/.
    """
    tex_dir = os.path.join(assets_dir, "textures")
    os.makedirs(tex_dir, exist_ok=True)
    _ensure_uv_maps(meshes)

    scene = bpy.context.scene
    prev_engine = scene.render.engine
    prev_samples = getattr(getattr(scene, "cycles", None), "samples", 16)
    prev_bake = {
        "use_pass_direct": scene.render.bake.use_pass_direct,
        "use_pass_indirect": scene.render.bake.use_pass_indirect,
        "use_pass_color": scene.render.bake.use_pass_color,
        "margin": scene.render.bake.margin,
    }

    try:
        _enable_cycles_engine(scene)
        scene.render.bake.margin = 4

        bpy.ops.object.select_all(action="DESELECT")
        for obj in meshes:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]

        mats = []
        has_sss_mat = False
        has_linked_metal = False
        for obj in meshes:
            for slot in obj.material_slots:
                if slot.material and slot.material not in mats:
                    mats.append(slot.material)
                    bsdf = _find_principled_bsdf(slot.material)
                    if bsdf:
                        if _get_socket_default_scalar(bsdf, ("Subsurface Weight", "Subsurface"), 0.0) > 0.01:
                            has_sss_mat = True
                        m_sock = bsdf.inputs.get("Metallic")
                        if m_sock and m_sock.is_linked:
                            has_linked_metal = True

        do_sss = bool(bake_sss or has_sss_mat)
        img_base = _create_bake_image(f"{slot_name}_BaseColor", tex_size, "sRGB")
        img_norm = _create_bake_image(f"{slot_name}_Normal", tex_size, "Non-Color")
        img_ao = _create_bake_image(f"{slot_name}_AO_tmp", tex_size, "Non-Color")
        img_rough = _create_bake_image(f"{slot_name}_Rough_tmp", tex_size, "Non-Color")
        img_metal = _create_bake_image(f"{slot_name}_Metal_tmp", tex_size, "Non-Color") if has_linked_metal else None
        img_orm = _create_bake_image(f"{slot_name}_ORM", tex_size, "Non-Color")
        img_thick = _create_bake_image(f"{slot_name}_Thickness", tex_size, "Non-Color") if do_sss else None

        # Ziel-Image-Nodes in jedem Material anlegen und selektieren
        target_nodes = []
        for mat in mats:
            _ensure_material_nodes(mat)
            nt = mat.node_tree
            tex_node = nt.nodes.new("ShaderNodeTexImage")
            tex_node.name = "__arche_bake_target__"
            nt.nodes.active = tex_node
            tex_node.select = True
            target_nodes.append((mat, tex_node))

        # 1. BaseColor [sRGB] (rein Color-Pass, ohne eingebackene Sonnen-/Schlagschatten!)
        for _, tn in target_nodes:
            tn.image = img_base
        scene.render.bake.use_pass_direct = False
        scene.render.bake.use_pass_indirect = False
        scene.render.bake.use_pass_color = True
        bpy.ops.object.bake(type="DIFFUSE")

        # 2. Normal [Non-Color] (Tangent Space)
        for _, tn in target_nodes:
            tn.image = img_norm
        bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")

        # 3. Ambient Occlusion -> R-Kanal von ORM
        for _, tn in target_nodes:
            tn.image = img_ao
        bpy.ops.object.bake(type="AO")

        # 4. Roughness -> G-Kanal von ORM
        for _, tn in target_nodes:
            tn.image = img_rough
        bpy.ops.object.bake(type="ROUGHNESS")

        # 5. Optional verknüpfter Metallic-Kanal -> B-Kanal von ORM via EMIT
        if img_metal is not None:
            saved_metal_links = []
            temp_emit_nodes = []
            for mat, tn in target_nodes:
                nt = mat.node_tree
                bsdf = _find_principled_bsdf(mat)
                out_node = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
                if bsdf and out_node:
                    for lk in list(out_node.inputs["Surface"].links):
                        saved_metal_links.append((nt, lk.from_socket, out_node.inputs["Surface"]))
                        nt.links.remove(lk)
                    emit = nt.nodes.new("ShaderNodeEmission")
                    temp_emit_nodes.append((nt, emit))
                    m_sock = bsdf.inputs.get("Metallic")
                    if m_sock and m_sock.is_linked:
                        nt.links.new(m_sock.links[0].from_socket, emit.inputs["Color"])
                    else:
                        val = _get_socket_default_scalar(bsdf, ("Metallic",), 0.0)
                        emit.inputs["Color"].default_value = (val, val, val, 1.0)
                    nt.links.new(emit.outputs["Emission"], out_node.inputs["Surface"])
                    tn.image = img_metal
            bpy.ops.object.bake(type="EMIT")
            for nt, from_sock, to_sock in saved_metal_links:
                nt.links.new(from_sock, to_sock)
            for nt, em in temp_emit_nodes:
                nt.nodes.remove(em)

        # 6. Optional Thickness-Maske für Echtzeit-SSS (AO Inside=True über EMIT-Pass)
        if img_thick is not None:
            saved_links = []
            temp_nodes = []
            for mat, tn in target_nodes:
                nt = mat.node_tree
                out_node = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
                if out_node:
                    for lk in list(out_node.inputs["Surface"].links):
                        saved_links.append((nt, lk.from_socket, out_node.inputs["Surface"]))
                        nt.links.remove(lk)
                    ao_in = nt.nodes.new("ShaderNodeAmbientOcclusion")
                    ao_in.inside = True
                    ao_in.only_local = True
                    emit = nt.nodes.new("ShaderNodeEmission")
                    temp_nodes.extend([(nt, ao_in), (nt, emit)])
                    nt.links.new(ao_in.outputs["AO"], emit.inputs["Color"])
                    nt.links.new(emit.outputs["Emission"], out_node.inputs["Surface"])
                    tn.image = img_thick
            bpy.ops.object.bake(type="EMIT")
            for nt, from_sock, to_sock in saved_links:
                nt.links.new(from_sock, to_sock)
            for nt, tmp_n in temp_nodes:
                nt.nodes.remove(tmp_n)

        # ORM packen (R=AO, G=Roughness, B=Metallic, A=1.0, Non-Color)
        ao_px = list(img_ao.pixels)
        rg_px = list(img_rough.pixels)
        mt_px = list(img_metal.pixels) if img_metal is not None else None
        scalar_metal = 0.0
        if mt_px is None:
            for mat in mats:
                bsdf = _find_principled_bsdf(mat)
                if bsdf:
                    scalar_metal = max(scalar_metal, _get_socket_default_scalar(bsdf, ("Metallic",), 0.0))

        orm_px = [1.0] * (tex_size * tex_size * 4)
        for idx in range(0, len(orm_px), 4):
            orm_px[idx] = ao_px[idx]          # R: AO
            orm_px[idx + 1] = rg_px[idx + 1]  # G: Roughness
            orm_px[idx + 2] = mt_px[idx] if mt_px is not None else scalar_metal  # B: Metallic
            orm_px[idx + 3] = 1.0
        img_orm.pixels.foreach_set(orm_px)

        paths = {}
        for key, img in (("baseColor", img_base), ("normal", img_norm), ("orm", img_orm), ("thickness", img_thick)):
            if img is None:
                continue
            out_png = os.path.join(tex_dir, f"{slot_name}_{key}.png")
            img.filepath_raw = out_png
            img.file_format = "PNG"
            img.save()
            paths[key] = f"assets/textures/{slot_name}_{key}.png"

        # Sauberen glTF-2.0-Material-Graph verdrahten (Sheen/Coat/Anisotropy/ThinFilm/Emission bleiben auf Principled BSDF erhalten!)
        for mat, tn in target_nodes:
            nt = mat.node_tree
            nt.nodes.remove(tn)
            bsdf = _find_principled_bsdf(mat)
            if not bsdf:
                continue
            tex_bc = nt.nodes.new("ShaderNodeTexImage")
            tex_bc.image = img_base
            tex_nm = nt.nodes.new("ShaderNodeTexImage")
            tex_nm.image = img_norm
            norm_map = nt.nodes.new("ShaderNodeNormalMap")
            tex_orm = nt.nodes.new("ShaderNodeTexImage")
            tex_orm.image = img_orm
            sep_node = nt.nodes.new("ShaderNodeSeparateColor" if hasattr(bpy.types, "ShaderNodeSeparateColor") else "ShaderNodeSeparateRGB")

            nt.links.new(tex_bc.outputs["Color"], bsdf.inputs["Base Color"])
            nt.links.new(tex_nm.outputs["Color"], norm_map.inputs["Color"])
            nt.links.new(norm_map.outputs["Normal"], bsdf.inputs["Normal"])
            nt.links.new(tex_orm.outputs["Color"], sep_node.inputs[0])
            sep_outs = list(sep_node.outputs)
            nt.links.new(sep_outs[1], bsdf.inputs["Roughness"])
            nt.links.new(sep_outs[2], bsdf.inputs["Metallic"])

            gltf_grp = bpy.data.node_groups.get("glTF Material Output")
            if gltf_grp is None:
                gltf_grp = bpy.data.node_groups.new("glTF Material Output", "ShaderNodeTree")
                if hasattr(gltf_grp, "interface"):
                    gltf_grp.interface.new_socket(name="Occlusion", in_out="INPUT", socket_type="NodeSocketFloat")
                else:
                    gltf_grp.inputs.new("NodeSocketFloat", "Occlusion")
            g_node = nt.nodes.new("ShaderNodeGroup")
            g_node.node_tree = gltf_grp
            nt.links.new(sep_outs[0], g_node.inputs["Occlusion"])

        bpy.data.images.remove(img_ao)
        bpy.data.images.remove(img_rough)
        if img_metal is not None:
            bpy.data.images.remove(img_metal)
        print(f"[ARCHE EXPORT] Auto-Bake abgeschlossen ({tex_size}px, sRGB+Non-Color ORM): {list(paths.keys())}")
        return paths
    finally:
        scene.render.engine = prev_engine
        if hasattr(scene, "cycles"):
            scene.cycles.samples = prev_samples
        scene.render.bake.use_pass_direct = prev_bake["use_pass_direct"]
        scene.render.bake.use_pass_indirect = prev_bake["use_pass_indirect"]
        scene.render.bake.use_pass_color = prev_bake["use_pass_color"]
        scene.render.bake.margin = prev_bake["margin"]


def export_glb(meshes, glb_path, use_draco=False):
    """Exportiert Auswahl als .glb (+Y Up, Morph Targets, Color Attributes, KHR PBR & Emissive Strength)."""
    os.makedirs(os.path.dirname(glb_path), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]

    rna_props = set(bpy.ops.export_scene.gltf.get_rna_type().properties.keys())
    desired_kwargs = {
        "filepath": glb_path,
        "export_format": "GLB",
        "use_selection": True,
        "export_yup": True,
        "export_apply": True,
        "export_normals": True,
        "export_tangents": True,
        "export_texcoords": True,
        "export_colors": True,
        "export_vertex_color": "ACTIVE",
        "export_attributes": True,
        "export_all_vertex_colors": True,
        "export_morph": True,
        "export_morph_normal": True,
        "export_morph_tangent": True,
        "export_materials": "EXPORT",
        "export_extras": True,
        "export_image_format": "AUTO",
        "export_jpeg_quality": 85,
        "export_draco_mesh_compression_enable": bool(use_draco),
        "export_draco_mesh_compression_level": 6,
    }
    safe_kwargs = {k: v for k, v in desired_kwargs.items() if k in rna_props}
    bpy.ops.export_scene.gltf(**safe_kwargs)
    size_kb = os.path.getsize(glb_path) / 1024.0
    print(f"[ARCHE EXPORT] GLB geschrieben: {glb_path} ({size_kb:.1f} KB)")


def generate_lods(meshes, base_glb_path, category, use_draco=False):
    """Erzeugt LOD1 und LOD2 über Decimate-Kopien (ohne die Originale zu verändern)."""
    cfg = CATEGORY_CONFIG[category]
    base_no_ext = os.path.splitext(base_glb_path)[0]
    lod_specs = [("lod1", cfg["lod1_ratio"]), ("lod2", cfg["lod2_ratio"])]
    lod_paths = {}

    for lod_tag, ratio in lod_specs:
        clones = []
        try:
            for src in meshes:
                dup = src.copy()
                dup.data = src.data.copy()
                bpy.context.collection.objects.link(dup)
                dec = dup.modifiers.new(name=f"Arche_{lod_tag}", type="DECIMATE")
                eff_ratio = ratio
                if lod_tag == "lod2" and "lod2_target_tris" in cfg:
                    cur_tris = max(1, len(dup.data.polygons) * 2)
                    eff_ratio = max(0.005, min(ratio, cfg["lod2_target_tris"] / float(cur_tris)))
                dec.ratio = max(0.005, min(1.0, eff_ratio))
                clones.append(dup)

            out_path = f"{base_no_ext}_{lod_tag}.glb"
            export_glb(clones, out_path, use_draco=use_draco)
            lod_paths[lod_tag] = out_path
        finally:
            for c in clones:
                mesh_data = c.data
                bpy.data.objects.remove(c, do_unlink=True)
                if mesh_data and mesh_data.users == 0:
                    bpy.data.meshes.remove(mesh_data)

    return lod_paths


def render_preview_png(meshes, preview_path):
    """Rendert headless eine 512x512-Kontrollansicht nach assets/previews/<name>.png."""
    os.makedirs(os.path.dirname(preview_path), exist_ok=True)
    scene = bpy.context.scene
    min_v = Vector((float("inf"), float("inf"), float("inf")))
    max_v = Vector((float("-inf"), float("-inf"), float("-inf")))
    for obj in meshes:
        for corner in obj.bound_box:
            wc = obj.matrix_world @ Vector(corner)
            min_v.x = min(min_v.x, wc.x); min_v.y = min(min_v.y, wc.y); min_v.z = min(min_v.z, wc.z)
            max_v.x = max(max_v.x, wc.x); max_v.y = max(max_v.y, wc.y); max_v.z = max(max_v.z, wc.z)

    center = 0.5 * (min_v + max_v)
    radius = max(0.5, (max_v - min_v).length * 0.5)
    dist = radius * 2.4

    cam_data = bpy.data.cameras.new("__arche_preview_cam__")
    cam_obj = bpy.data.objects.new("__arche_preview_cam__", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = center + Vector((dist * 0.72, -dist * 0.72, dist * 0.45))
    cam_obj.rotation_euler = (center - cam_obj.location).to_track_quat("-Z", "Y").to_euler()

    sun_data = bpy.data.lights.new("__arche_preview_sun__", type="SUN")
    sun_data.energy = 3.2
    sun_obj = bpy.data.objects.new("__arche_preview_sun__", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(50.0), 0.0, math.radians(-35.0))

    prev_cam = scene.camera
    prev_res = (scene.render.resolution_x, scene.render.resolution_y, scene.render.filepath)
    try:
        scene.camera = cam_obj
        scene.render.resolution_x = 512
        scene.render.resolution_y = 512
        scene.render.image_settings.file_format = "PNG"
        scene.render.filepath = preview_path
        bpy.ops.render.render(write_still=True)
        print(f"[ARCHE EXPORT] Preview gespeichert: {preview_path}")
    finally:
        scene.camera = prev_cam
        scene.render.resolution_x, scene.render.resolution_y, scene.render.filepath = prev_res
        bpy.data.objects.remove(cam_obj, do_unlink=True)
        bpy.data.cameras.remove(cam_data)
        bpy.data.objects.remove(sun_obj, do_unlink=True)
        bpy.data.lights.remove(sun_data)


def update_manifest(assets_dir, slot_name, rel_glb_url, category, stats, enable_slot, tex_paths=None, lod_paths=None, preview_rel=None):
    """Aktualisiert assets/manifest.json in categories.<group>.items sowie slots.<slot_name>."""
    manifest_path = os.path.join(assets_dir, "manifest.json")
    if os.path.isfile(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    else:
        manifest = {"version": "2.0.0", "categories": {}, "slots": {}}

    cfg = CATEGORY_CONFIG[category]
    meta = {
        "enabled": bool(enable_slot),
        "url": rel_glb_url.replace("\\", "/"),
        "category": category,
        "maxTris": stats["max_tris"],
        "tris": stats["tris"],
        "meshes": stats["meshes"],
        "materials": stats["materials"],
        "hasRequiredTag": stats["has_required_tag"],
        "hasShapeKeys": stats["has_shapekeys"],
        "exportedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if tex_paths:
        meta["bakedTextures"] = tex_paths
    if lod_paths:
        meta["lods"] = {k: os.path.relpath(v, os.path.dirname(assets_dir)).replace("\\", "/") for k, v in lod_paths.items()}
    if preview_rel:
        meta["preview"] = preview_rel.replace("\\", "/")

    cats = manifest.setdefault("categories", {})
    grp = cats.setdefault(cfg["manifest_group"], {"items": {}})
    items = grp.setdefault("items", {})
    cat_entry = items.get(slot_name, {})
    cat_entry.update(meta)
    items[slot_name] = cat_entry

    slots = manifest.setdefault("slots", {})
    if slot_name in slots:
        slot_entry = slots[slot_name]
        slot_entry.update(meta)
        slots[slot_name] = slot_entry

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"[ARCHE EXPORT] manifest.json aktualisiert: '{slot_name}' (Kategorie={category}, enabled={meta['enabled']})")


def main():
    cli = parse_cli_args()
    assets_dir = resolve_assets_dir()
    slot_name = infer_slot_name(cli["slot"])
    category = infer_category(slot_name, cli["category"])
    cfg = CATEGORY_CONFIG[category]

    meshes = collect_export_meshes()
    ensure_single_user_meshes(meshes)
    apply_rotation_and_scale(meshes)
    _, min_z = center_origin_to_bottom_bbox(meshes, keep_pivot=cli["keep_pivot"])
    stats = inspect_category_and_budget(meshes, category, min_z)

    tex_paths = None
    if cli["bake"]:
        bake_sz = cli["bake_size"] or cfg["max_tex"]
        tex_paths = bake_pbr_textures(meshes, assets_dir, slot_name, bake_sz, bake_sss=cli["bake_sss"])

    subdir = cfg["subdir"]
    rel_glb_url = f"assets/glb/{subdir}/{slot_name}.glb"
    glb_path = os.path.join(assets_dir, "glb", subdir, f"{slot_name}.glb")
    export_glb(meshes, glb_path, use_draco=cli["draco"])

    lod_paths = generate_lods(meshes, glb_path, category, use_draco=cli["draco"]) if cli["lods"] else None

    preview_rel = None
    if cli["preview"]:
        preview_rel = f"assets/previews/{slot_name}.png"
        render_preview_png(meshes, os.path.join(assets_dir, "previews", f"{slot_name}.png"))

    update_manifest(assets_dir, slot_name, rel_glb_url, category, stats, cli["enable"], tex_paths, lod_paths, preview_rel)
    print("[ARCHE EXPORT] Fertig!")


if __name__ == "__main__":
    main()
