"""
Command Executor for Conjure Blender Client.

Routes commands to appropriate handlers following the _cmd_{type} pattern.
All handlers execute Blender operations via bpy API.
"""

import math
from typing import Any, Callable, Dict, List, Optional, Tuple

import bpy
import mathutils


class CommandExecutor:
    """Executes CAD commands in Blender."""

    def __init__(self, materials_client=None):
        # Materials client for engineering materials from server
        self.materials_client = materials_client

        # Build command handler map
        self._handlers: Dict[str, Callable] = {}
        self._register_handlers()

    def _register_handlers(self):
        """Register all command handlers."""
        # Find all methods starting with _cmd_
        for name in dir(self):
            if name.startswith("_cmd_"):
                cmd_type = name[5:]  # Remove _cmd_ prefix
                self._handlers[cmd_type] = getattr(self, name)

    def execute(self, cmd_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command by type.

        Args:
            cmd_type: The command type (e.g., 'create_cube', 'boolean_union')
            params: Parameters for the command

        Returns:
            Dict with 'status' key ('success' or 'error') and operation-specific data.
            On error, includes 'operation', 'params', and 'error' keys for debugging.
        """
        handler = self._handlers.get(cmd_type)
        if not handler:
            return {
                "status": "error",
                "operation": cmd_type,
                "error": f"Unknown command: {cmd_type}",
                "available_commands": list(self._handlers.keys())[:20],
            }

        try:
            result = handler(params)

            # Enrich error responses with operation context
            if result.get("status") == "error":
                result["operation"] = cmd_type
                if "params" not in result:
                    # Include relevant params (filter out large data)
                    safe_params = {
                        k: v
                        for k, v in params.items()
                        if not isinstance(v, (bytes, bytearray))
                        and (not isinstance(v, (list, dict)) or len(str(v)) < 200)
                    }
                    result["params"] = safe_params

            return result

        except Exception as e:
            return {
                "status": "error",
                "operation": cmd_type,
                "error": f"{type(e).__name__}: {str(e)}",
                "params": {
                    k: v
                    for k, v in params.items()
                    if not isinstance(v, (bytes, bytearray)) and (not isinstance(v, (list, dict)) or len(str(v)) < 200)
                },
            }

    # =========================================================================
    # PRIMITIVE OPERATIONS
    # =========================================================================

    def _cmd_create_cube(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a cube mesh primitive."""
        name = params.get("name", "Cube")
        size = params.get("size", 2.0)
        location = params.get("location", [0, 0, 0])

        bpy.ops.mesh.primitive_cube_add(
            size=size,
            location=tuple(location),
        )

        obj = bpy.context.active_object
        obj.name = name

        return {
            "status": "success",
            "object": obj.name,
            "type": "MESH",
            "vertices": len(obj.data.vertices),
            "faces": len(obj.data.polygons),
        }

    def _cmd_create_sphere(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a UV sphere mesh primitive."""
        name = params.get("name", "Sphere")
        radius = params.get("radius", 1.0)
        segments = params.get("segments", 32)
        rings = params.get("rings", 16)
        location = params.get("location", [0, 0, 0])

        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=radius,
            segments=segments,
            ring_count=rings,
            location=tuple(location),
        )

        obj = bpy.context.active_object
        obj.name = name

        return {
            "status": "success",
            "object": obj.name,
            "type": "MESH",
            "vertices": len(obj.data.vertices),
            "faces": len(obj.data.polygons),
        }

    def _cmd_create_cylinder(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a cylinder mesh primitive."""
        name = params.get("name", "Cylinder")
        radius = params.get("radius", 1.0)
        depth = params.get("depth", 2.0)
        vertices = params.get("vertices", 32)
        location = params.get("location", [0, 0, 0])

        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius,
            depth=depth,
            vertices=vertices,
            location=tuple(location),
        )

        obj = bpy.context.active_object
        obj.name = name

        return {
            "status": "success",
            "object": obj.name,
            "type": "MESH",
            "vertices": len(obj.data.vertices),
            "faces": len(obj.data.polygons),
        }

    def _cmd_create_cone(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a cone mesh primitive."""
        name = params.get("name", "Cone")
        radius1 = params.get("radius1", 1.0)
        radius2 = params.get("radius2", 0.0)
        depth = params.get("depth", 2.0)
        vertices = params.get("vertices", 32)
        location = params.get("location", [0, 0, 0])

        bpy.ops.mesh.primitive_cone_add(
            radius1=radius1,
            radius2=radius2,
            depth=depth,
            vertices=vertices,
            location=tuple(location),
        )

        obj = bpy.context.active_object
        obj.name = name

        return {
            "status": "success",
            "object": obj.name,
            "type": "MESH",
            "vertices": len(obj.data.vertices),
            "faces": len(obj.data.polygons),
        }

    def _cmd_create_torus(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a torus mesh primitive."""
        name = params.get("name", "Torus")
        major_radius = params.get("major_radius", 1.0)
        minor_radius = params.get("minor_radius", 0.25)
        major_segments = params.get("major_segments", 48)
        minor_segments = params.get("minor_segments", 12)
        location = params.get("location", [0, 0, 0])

        bpy.ops.mesh.primitive_torus_add(
            major_radius=major_radius,
            minor_radius=minor_radius,
            major_segments=major_segments,
            minor_segments=minor_segments,
            location=tuple(location),
        )

        obj = bpy.context.active_object
        obj.name = name

        return {
            "status": "success",
            "object": obj.name,
            "type": "MESH",
            "vertices": len(obj.data.vertices),
            "faces": len(obj.data.polygons),
        }

    def _cmd_create_plane(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a plane mesh primitive."""
        name = params.get("name", "Plane")
        size = params.get("size", 2.0)
        location = params.get("location", [0, 0, 0])

        bpy.ops.mesh.primitive_plane_add(
            size=size,
            location=tuple(location),
        )

        obj = bpy.context.active_object
        obj.name = name

        return {
            "status": "success",
            "object": obj.name,
            "type": "MESH",
            "vertices": len(obj.data.vertices),
            "faces": len(obj.data.polygons),
        }

    # =========================================================================
    # CURVE OPERATIONS
    # =========================================================================

    def _cmd_create_bezier(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Bezier curve."""
        name = params.get("name", "BezierCurve")
        location = params.get("location", [0, 0, 0])

        bpy.ops.curve.primitive_bezier_curve_add(location=tuple(location))

        obj = bpy.context.active_object
        obj.name = name

        return {
            "status": "success",
            "object": obj.name,
            "type": "CURVE",
            "spline_count": len(obj.data.splines),
        }

    def _cmd_create_nurbs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a NURBS curve."""
        name = params.get("name", "NurbsCurve")
        location = params.get("location", [0, 0, 0])

        bpy.ops.curve.primitive_nurbs_curve_add(location=tuple(location))

        obj = bpy.context.active_object
        obj.name = name

        return {
            "status": "success",
            "object": obj.name,
            "type": "CURVE",
            "spline_count": len(obj.data.splines),
        }

    def _cmd_create_path(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a path curve."""
        name = params.get("name", "Path")
        location = params.get("location", [0, 0, 0])

        bpy.ops.curve.primitive_nurbs_path_add(location=tuple(location))

        obj = bpy.context.active_object
        obj.name = name

        return {
            "status": "success",
            "object": obj.name,
            "type": "CURVE",
            "spline_count": len(obj.data.splines),
        }

    # =========================================================================
    # TRANSFORM OPERATIONS
    # =========================================================================

    def _cmd_move_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Move an object to a new location or by offset."""
        obj_name = params.get("object")
        location = params.get("location")
        offset = params.get("offset")

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        if location:
            obj.location = mathutils.Vector(location)
        elif offset:
            obj.location += mathutils.Vector(offset)

        return {
            "status": "success",
            "object": obj.name,
            "location": list(obj.location),
        }

    def _cmd_rotate_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rotate an object."""
        obj_name = params.get("object")
        rotation = params.get("rotation")  # Euler angles in degrees
        axis = params.get("axis")  # Single axis rotation
        angle = params.get("angle", 0)  # Angle in degrees

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        if rotation:
            # Full Euler rotation
            obj.rotation_euler = mathutils.Euler([math.radians(r) for r in rotation], "XYZ")
        elif axis and angle:
            # Single axis rotation
            axis_map = {"X": 0, "Y": 1, "Z": 2}
            if axis.upper() in axis_map:
                idx = axis_map[axis.upper()]
                obj.rotation_euler[idx] += math.radians(angle)

        return {
            "status": "success",
            "object": obj.name,
            "rotation_euler": [math.degrees(r) for r in obj.rotation_euler],
        }

    def _cmd_scale_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Scale an object."""
        obj_name = params.get("object")
        scale = params.get("scale", [1, 1, 1])
        uniform = params.get("uniform")  # Single value for uniform scale

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        if uniform is not None:
            obj.scale = mathutils.Vector([uniform, uniform, uniform])
        else:
            obj.scale = mathutils.Vector(scale)

        return {
            "status": "success",
            "object": obj.name,
            "scale": list(obj.scale),
        }

    def _cmd_copy_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Copy an object."""
        obj_name = params.get("object")
        new_name = params.get("new_name")
        location = params.get("location")
        linked = params.get("linked", False)

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        # Create copy
        if linked:
            new_obj = obj.copy()
        else:
            new_obj = obj.copy()
            if obj.data:
                new_obj.data = obj.data.copy()

        if new_name:
            new_obj.name = new_name

        if location:
            new_obj.location = mathutils.Vector(location)

        # Link to scene
        bpy.context.collection.objects.link(new_obj)

        return {
            "status": "success",
            "object": new_obj.name,
            "original": obj.name,
            "location": list(new_obj.location),
        }

    def _cmd_delete_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an object."""
        obj_name = params.get("object")

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        # Store name before deletion
        deleted_name = obj.name

        # Delete object and its data
        bpy.data.objects.remove(obj, do_unlink=True)

        return {
            "status": "success",
            "deleted": deleted_name,
        }

    # =========================================================================
    # BOOLEAN OPERATIONS
    # =========================================================================

    def _cmd_boolean_union(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Boolean union of two objects."""
        return self._boolean_op(params, "UNION")

    def _cmd_boolean_difference(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Boolean difference (subtraction) of two objects."""
        return self._boolean_op(params, "DIFFERENCE")

    def _cmd_boolean_intersect(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Boolean intersection of two objects."""
        return self._boolean_op(params, "INTERSECT")

    def _boolean_op(self, params: Dict[str, Any], operation: str) -> Dict[str, Any]:
        """Perform boolean operation."""
        obj_name = params.get("object")
        target_name = params.get("target")
        apply = params.get("apply", True)

        obj = bpy.data.objects.get(obj_name)
        target = bpy.data.objects.get(target_name)

        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}
        if not target:
            return {"status": "error", "error": f"Target '{target_name}' not found"}

        # Add boolean modifier
        mod = obj.modifiers.new(name=f"Boolean_{operation}", type="BOOLEAN")
        mod.operation = operation
        mod.object = target

        if apply:
            # Apply modifier
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier=mod.name)

            # Optionally delete target
            if params.get("delete_target", True):
                bpy.data.objects.remove(target, do_unlink=True)

        return {
            "status": "success",
            "object": obj.name,
            "operation": operation,
            "vertices": len(obj.data.vertices) if obj.type == "MESH" else 0,
            "faces": len(obj.data.polygons) if obj.type == "MESH" else 0,
        }

    # =========================================================================
    # MODIFIER OPERATIONS
    # =========================================================================

    def _cmd_add_modifier(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a modifier to an object."""
        obj_name = params.get("object")
        mod_type = params.get("modifier_type", "").upper()
        mod_name = params.get("name")
        settings = params.get("settings", {})

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        # Add modifier
        mod = obj.modifiers.new(name=mod_name or mod_type, type=mod_type)

        # Apply settings
        for key, value in settings.items():
            if hasattr(mod, key):
                setattr(mod, key, value)

        return {
            "status": "success",
            "object": obj.name,
            "modifier": mod.name,
            "type": mod_type,
        }

    def _cmd_remove_modifier(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove a modifier from an object."""
        obj_name = params.get("object")
        mod_name = params.get("modifier")

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        mod = obj.modifiers.get(mod_name)
        if not mod:
            return {"status": "error", "error": f"Modifier '{mod_name}' not found"}

        obj.modifiers.remove(mod)

        return {
            "status": "success",
            "object": obj.name,
            "removed": mod_name,
        }

    def _cmd_apply_modifier(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a modifier to an object."""
        obj_name = params.get("object")
        mod_name = params.get("modifier")

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        mod = obj.modifiers.get(mod_name)
        if not mod:
            return {"status": "error", "error": f"Modifier '{mod_name}' not found"}

        # Make object active and apply
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod_name)

        return {
            "status": "success",
            "object": obj.name,
            "applied": mod_name,
            "vertices": len(obj.data.vertices) if obj.type == "MESH" else 0,
        }

    def _cmd_add_bevel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add bevel modifier to an object.

        Args:
            object: Object name
            width: Bevel width (default: 0.1)
            segments: Number of segments (default: 1)
            limit_method: NONE, ANGLE, WEIGHT, VGROUP (default: NONE)
            angle_limit: Angle limit in degrees when limit_method=ANGLE (default: 30)

        Returns:
            status, object name, modifier name
        """
        obj_name = params.get("object")
        width = params.get("width", 0.1)
        segments = params.get("segments", 1)
        limit_method = params.get("limit_method", "NONE").upper()
        angle_limit = params.get("angle_limit", 30)

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        mod = obj.modifiers.new(name="Bevel", type="BEVEL")
        mod.width = width
        mod.segments = segments
        mod.limit_method = limit_method
        if limit_method == "ANGLE":
            mod.angle_limit = math.radians(angle_limit)

        return {
            "status": "success",
            "object": obj.name,
            "modifier": mod.name,
            "width": width,
            "segments": segments,
        }

    def _cmd_add_solidify(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add solidify modifier to an object.

        Args:
            object: Object name
            thickness: Shell thickness (default: 0.1)
            offset: Offset direction -1 to 1 (default: -1, inward)
            use_even_offset: Even thickness (default: True)

        Returns:
            status, object name, modifier name
        """
        obj_name = params.get("object")
        thickness = params.get("thickness", 0.1)
        offset = params.get("offset", -1)
        use_even_offset = params.get("use_even_offset", True)

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        mod = obj.modifiers.new(name="Solidify", type="SOLIDIFY")
        mod.thickness = thickness
        mod.offset = offset
        mod.use_even_offset = use_even_offset

        return {
            "status": "success",
            "object": obj.name,
            "modifier": mod.name,
            "thickness": thickness,
            "offset": offset,
        }

    def _cmd_add_mirror(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add mirror modifier to an object.

        Args:
            object: Object name
            axis: Axis to mirror - x, y, z, or list like [True, False, False] (default: x)
            use_clip: Prevent vertices from crossing mirror plane (default: False)
            mirror_object: Optional object to use as mirror center

        Returns:
            status, object name, modifier name
        """
        obj_name = params.get("object")
        axis = params.get("axis", "x")
        use_clip = params.get("use_clip", False)
        mirror_object = params.get("mirror_object")

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        mod = obj.modifiers.new(name="Mirror", type="MIRROR")
        mod.use_clip = use_clip

        # Handle axis parameter
        if isinstance(axis, list):
            mod.use_axis = axis[:3] if len(axis) >= 3 else axis + [False] * (3 - len(axis))
        else:
            axis_str = axis.lower()
            mod.use_axis[0] = "x" in axis_str
            mod.use_axis[1] = "y" in axis_str
            mod.use_axis[2] = "z" in axis_str

        if mirror_object:
            mirror_obj = bpy.data.objects.get(mirror_object)
            if mirror_obj:
                mod.mirror_object = mirror_obj

        return {
            "status": "success",
            "object": obj.name,
            "modifier": mod.name,
            "axis": list(mod.use_axis),
        }

    def _cmd_add_array(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add array modifier to an object.

        Args:
            object: Object name
            count: Number of copies (default: 2)
            offset: Relative offset [x, y, z] (default: [1, 0, 0])
            use_relative_offset: Use relative offset (default: True)
            constant_offset: Constant offset [x, y, z] (default: None)

        Returns:
            status, object name, modifier name
        """
        obj_name = params.get("object")
        count = params.get("count", 2)
        offset = params.get("offset", [1, 0, 0])
        use_relative = params.get("use_relative_offset", True)
        constant_offset = params.get("constant_offset")

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        mod = obj.modifiers.new(name="Array", type="ARRAY")
        mod.count = count
        mod.use_relative_offset = use_relative

        if use_relative and offset:
            mod.relative_offset_displace = offset

        if constant_offset:
            mod.use_constant_offset = True
            mod.constant_offset_displace = constant_offset

        return {
            "status": "success",
            "object": obj.name,
            "modifier": mod.name,
            "count": count,
        }

    def _cmd_add_subdivision(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add subdivision surface modifier to an object.

        Args:
            object: Object name
            levels: Viewport subdivision levels (default: 2)
            render_levels: Render subdivision levels (default: same as levels)
            use_limit_surface: Use limit surface (default: True)

        Returns:
            status, object name, modifier name
        """
        obj_name = params.get("object")
        levels = params.get("levels", 2)
        render_levels = params.get("render_levels", levels)
        use_limit_surface = params.get("use_limit_surface", True)

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        mod = obj.modifiers.new(name="Subdivision", type="SUBSURF")
        mod.levels = levels
        mod.render_levels = render_levels
        mod.use_limit_surface = use_limit_surface

        return {
            "status": "success",
            "object": obj.name,
            "modifier": mod.name,
            "levels": levels,
            "render_levels": render_levels,
        }

    # =========================================================================
    # QUERY OPERATIONS
    # =========================================================================

    def _cmd_get_state(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current scene state."""
        scene = bpy.context.scene
        objects = []

        for obj in scene.objects:
            obj_data = {
                "name": obj.name,
                "type": obj.type,
                "location": list(obj.location),
                "rotation": [math.degrees(r) for r in obj.rotation_euler],
                "scale": list(obj.scale),
                "visible": obj.visible_get(),
            }

            if obj.type == "MESH" and obj.data:
                obj_data["vertices"] = len(obj.data.vertices)
                obj_data["faces"] = len(obj.data.polygons)
                obj_data["edges"] = len(obj.data.edges)

            objects.append(obj_data)

        return {
            "status": "success",
            "scene": scene.name,
            "frame": scene.frame_current,
            "object_count": len(objects),
            "objects": objects,
        }

    def _cmd_list_objects(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all objects with optional filtering."""
        obj_type = params.get("type")  # Optional type filter

        objects = []
        for obj in bpy.context.scene.objects:
            if obj_type and obj.type != obj_type.upper():
                continue

            objects.append(
                {
                    "name": obj.name,
                    "type": obj.type,
                    "location": list(obj.location),
                }
            )

        return {
            "status": "success",
            "count": len(objects),
            "objects": objects,
        }

    def _cmd_get_object_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about an object."""
        obj_name = params.get("object")

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        details = {
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "rotation_euler": [math.degrees(r) for r in obj.rotation_euler],
            "scale": list(obj.scale),
            "dimensions": list(obj.dimensions),
            "visible": obj.visible_get(),
            "selected": obj.select_get(),
            "modifiers": [m.name for m in obj.modifiers],
            "materials": [m.name if m else None for m in obj.data.materials]
            if obj.data and hasattr(obj.data, "materials")
            else [],
        }

        if obj.type == "MESH" and obj.data:
            mesh = obj.data
            details["mesh"] = {
                "vertices": len(mesh.vertices),
                "edges": len(mesh.edges),
                "faces": len(mesh.polygons),
                "has_custom_normals": mesh.has_custom_normals,
            }

            # Bounding box
            bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]
            details["bounding_box"] = {
                "min": [min(v[i] for v in bbox) for i in range(3)],
                "max": [max(v[i] for v in bbox) for i in range(3)],
            }

        return {
            "status": "success",
            "object": details,
        }

    def _cmd_measure_distance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Measure distance between two objects (center to center)."""
        obj1_name = params.get("object1")
        obj2_name = params.get("object2")

        obj1 = bpy.data.objects.get(obj1_name)
        obj2 = bpy.data.objects.get(obj2_name)

        if not obj1:
            return {"status": "error", "error": f"Object '{obj1_name}' not found"}
        if not obj2:
            return {"status": "error", "error": f"Object '{obj2_name}' not found"}

        # Calculate distance between centers
        distance = (obj1.location - obj2.location).length

        return {
            "status": "success",
            "object1": obj1.name,
            "object2": obj2.name,
            "distance": distance,
            "location1": list(obj1.location),
            "location2": list(obj2.location),
        }

    def _cmd_validate_geometry(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mesh geometry for common issues.

        Checks for:
        - Non-manifold edges (edges shared by more or fewer than 2 faces)
        - Loose vertices (vertices not connected to any face)
        - Loose edges (edges not connected to any face)
        - Zero-area faces (degenerate faces)
        - Flipped normals (faces with inconsistent winding)

        Args:
            object: Object name to validate (validates all mesh objects if not specified)

        Returns:
            status, validation results with issue counts and details
        """
        import bmesh

        obj_name = params.get("object")

        # Get objects to validate
        if obj_name:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {"status": "error", "error": f"Object '{obj_name}' not found"}
            if obj.type != "MESH":
                return {"status": "error", "error": f"Object '{obj_name}' is not a mesh"}
            objects_to_check = [obj]
        else:
            objects_to_check = [o for o in bpy.context.scene.objects if o.type == "MESH"]

        if not objects_to_check:
            return {"status": "error", "error": "No mesh objects to validate"}

        results = []

        for obj in objects_to_check:
            # Create bmesh for analysis
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

            issues = {
                "non_manifold_edges": [],
                "loose_vertices": [],
                "loose_edges": [],
                "zero_area_faces": [],
                "flipped_normals": 0,
            }

            # Check for non-manifold edges
            for edge in bm.edges:
                if not edge.is_manifold:
                    issues["non_manifold_edges"].append(edge.index)

            # Check for loose vertices (not connected to any face)
            for vert in bm.verts:
                if not vert.link_faces:
                    issues["loose_vertices"].append(vert.index)

            # Check for loose edges (not connected to any face)
            for edge in bm.edges:
                if not edge.link_faces:
                    issues["loose_edges"].append(edge.index)

            # Check for zero-area faces (degenerate)
            for face in bm.faces:
                if face.calc_area() < 1e-8:
                    issues["zero_area_faces"].append(face.index)

            # Check for flipped normals using face islands
            # Count faces that point opposite to their neighbors
            checked_faces = set()
            flipped_count = 0

            for face in bm.faces:
                if face.index in checked_faces:
                    continue

                # For each linked face, check if normals are consistent
                for edge in face.edges:
                    for linked_face in edge.link_faces:
                        if linked_face == face:
                            continue
                        checked_faces.add(linked_face.index)

                        # Check winding consistency via shared edge
                        # If both faces use the edge in the same direction, one is flipped
                        face_verts = [v.index for v in face.verts]
                        linked_verts = [v.index for v in linked_face.verts]

                        edge_v0, edge_v1 = edge.verts[0].index, edge.verts[1].index

                        # Find edge direction in each face
                        try:
                            f_idx0 = face_verts.index(edge_v0)
                            f_idx1 = face_verts.index(edge_v1)
                            l_idx0 = linked_verts.index(edge_v0)
                            l_idx1 = linked_verts.index(edge_v1)

                            # Check if edge direction is same (indicates flip)
                            f_direction = (f_idx1 - f_idx0) % len(face_verts) == 1
                            l_direction = (l_idx1 - l_idx0) % len(linked_verts) == 1

                            if f_direction == l_direction:
                                flipped_count += 1
                        except ValueError:
                            pass

            issues["flipped_normals"] = flipped_count

            # Compute summary
            issue_count = (
                len(issues["non_manifold_edges"])
                + len(issues["loose_vertices"])
                + len(issues["loose_edges"])
                + len(issues["zero_area_faces"])
                + (1 if issues["flipped_normals"] > 0 else 0)
            )

            is_valid = issue_count == 0

            result = {
                "object": obj.name,
                "valid": is_valid,
                "vertex_count": len(bm.verts),
                "edge_count": len(bm.edges),
                "face_count": len(bm.faces),
                "issues": {
                    "non_manifold_edges": len(issues["non_manifold_edges"]),
                    "loose_vertices": len(issues["loose_vertices"]),
                    "loose_edges": len(issues["loose_edges"]),
                    "zero_area_faces": len(issues["zero_area_faces"]),
                    "flipped_normals": issues["flipped_normals"],
                },
            }

            # Include indices only if there are issues (limit to first 10 for brevity)
            if issues["non_manifold_edges"]:
                result["non_manifold_edge_indices"] = issues["non_manifold_edges"][:10]
            if issues["loose_vertices"]:
                result["loose_vertex_indices"] = issues["loose_vertices"][:10]
            if issues["loose_edges"]:
                result["loose_edge_indices"] = issues["loose_edges"][:10]
            if issues["zero_area_faces"]:
                result["zero_area_face_indices"] = issues["zero_area_faces"][:10]

            results.append(result)
            bm.free()

        # Overall summary
        all_valid = all(r["valid"] for r in results)

        return {
            "status": "success",
            "valid": all_valid,
            "objects_checked": len(results),
            "results": results,
        }

    def _cmd_health_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check Blender connection health."""
        return {
            "status": "success",
            "blender_version": ".".join(str(v) for v in bpy.app.version),
            "scene": bpy.context.scene.name,
            "object_count": len(bpy.context.scene.objects),
        }

    # =========================================================================
    # EXPORT OPERATIONS
    # =========================================================================

    def _cmd_export_stl(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Export object(s) to STL format."""
        filepath = params.get("filepath")
        obj_name = params.get("object")  # Optional, exports selected if not specified
        ascii_format = params.get("ascii", False)

        if not filepath:
            return {"status": "error", "error": "filepath is required"}

        # Select specific object if provided
        if obj_name:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {"status": "error", "error": f"Object '{obj_name}' not found"}
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)

        bpy.ops.wm.stl_export(
            filepath=filepath,
            export_selected_objects=bool(obj_name),
            ascii_format=ascii_format,
        )

        return {
            "status": "success",
            "filepath": filepath,
            "format": "STL",
        }

    def _cmd_export_obj(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Export object(s) to OBJ format."""
        filepath = params.get("filepath")
        obj_name = params.get("object")

        if not filepath:
            return {"status": "error", "error": "filepath is required"}

        if obj_name:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {"status": "error", "error": f"Object '{obj_name}' not found"}
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)

        bpy.ops.wm.obj_export(
            filepath=filepath,
            export_selected_objects=bool(obj_name),
        )

        return {
            "status": "success",
            "filepath": filepath,
            "format": "OBJ",
        }

    def _cmd_export_gltf(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Export object(s) to glTF format."""
        filepath = params.get("filepath")
        obj_name = params.get("object")
        export_format = params.get("format", "GLB")  # GLB or GLTF

        if not filepath:
            return {"status": "error", "error": "filepath is required"}

        if obj_name:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {"status": "error", "error": f"Object '{obj_name}' not found"}
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)

        bpy.ops.export_scene.gltf(
            filepath=filepath,
            use_selection=bool(obj_name),
            export_format=export_format,
        )

        return {
            "status": "success",
            "filepath": filepath,
            "format": export_format,
        }

    def _cmd_export_fbx(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Export object(s) to FBX format."""
        filepath = params.get("filepath")
        obj_name = params.get("object")

        if not filepath:
            return {"status": "error", "error": "filepath is required"}

        if obj_name:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {"status": "error", "error": f"Object '{obj_name}' not found"}
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)

        bpy.ops.export_scene.fbx(
            filepath=filepath,
            use_selection=bool(obj_name),
        )

        return {
            "status": "success",
            "filepath": filepath,
            "format": "FBX",
        }

    # =========================================================================
    # VIEWPORT OPERATIONS
    # =========================================================================

    def _cmd_capture_viewport(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Capture viewport to image file.

        Args:
            filepath: Output path for the image (default: /tmp/viewport.png)
            width: Image width in pixels (default: 1920)
            height: Image height in pixels (default: 1080)

        Returns:
            status, filepath, dimensions
        """
        import os

        filepath = params.get("filepath", "/tmp/viewport.png")
        width = params.get("width", 1920)
        height = params.get("height", 1080)

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

        # Store original render settings
        scene = bpy.context.scene
        orig_res_x = scene.render.resolution_x
        orig_res_y = scene.render.resolution_y
        orig_filepath = scene.render.filepath
        orig_file_format = scene.render.image_settings.file_format

        try:
            # Configure render settings for viewport capture
            scene.render.resolution_x = width
            scene.render.resolution_y = height
            scene.render.filepath = filepath

            # Determine format from extension
            ext = os.path.splitext(filepath)[1].lower()
            if ext == ".jpg" or ext == ".jpeg":
                scene.render.image_settings.file_format = "JPEG"
            else:
                scene.render.image_settings.file_format = "PNG"

            # Find a 3D viewport
            for area in bpy.context.screen.areas:
                if area.type == "VIEW_3D":
                    # Override context for the viewport render
                    with bpy.context.temp_override(area=area):
                        bpy.ops.render.opengl(write_still=True)
                    break
            else:
                return {
                    "status": "error",
                    "error": "No 3D viewport found",
                }

            return {
                "status": "success",
                "filepath": filepath,
                "width": width,
                "height": height,
            }

        finally:
            # Restore original settings
            scene.render.resolution_x = orig_res_x
            scene.render.resolution_y = orig_res_y
            scene.render.filepath = orig_filepath
            scene.render.image_settings.file_format = orig_file_format

    def _cmd_set_view(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set viewport camera angle.

        Args:
            direction: View direction - front, back, left, right, top, bottom, isometric

        Returns:
            status, direction
        """
        direction = params.get("direction", "front")

        # Map direction to Blender view type
        view_map = {
            "front": "FRONT",
            "back": "BACK",
            "left": "LEFT",
            "right": "RIGHT",
            "top": "TOP",
            "bottom": "BOTTOM",
        }

        # Find a 3D viewport
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                with bpy.context.temp_override(area=area):
                    region = None
                    for r in area.regions:
                        if r.type == "WINDOW":
                            region = r
                            break

                    if region is None:
                        return {"status": "error", "error": "No viewport region found"}

                    with bpy.context.temp_override(area=area, region=region):
                        if direction.lower() == "isometric":
                            # Set to isometric-like view (rotate from front)
                            bpy.ops.view3d.view_axis(type="FRONT")
                            # Orbit to get isometric angle
                            rv3d = area.spaces.active.region_3d
                            rv3d.view_perspective = "PERSP"
                            # Set rotation for isometric view (approx 45° azimuth, 35° elevation)
                            from mathutils import Euler

                            rv3d.view_rotation = Euler((math.radians(60), 0, math.radians(45)), "XYZ").to_quaternion()
                        elif direction.lower() in view_map:
                            bpy.ops.view3d.view_axis(type=view_map[direction.lower()])
                        else:
                            return {
                                "status": "error",
                                "error": f"Unknown direction: {direction}. Valid: front, back, left, right, top, bottom, isometric",
                            }

                return {
                    "status": "success",
                    "direction": direction,
                }

        return {"status": "error", "error": "No 3D viewport found"}

    def _cmd_frame_selected(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Frame selected objects in viewport.

        Args:
            object: Optional object name to select and frame (frames current selection if not provided)

        Returns:
            status, framed objects
        """
        obj_name = params.get("object")

        # Select specific object if provided
        if obj_name:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                return {"status": "error", "error": f"Object '{obj_name}' not found"}
            bpy.ops.object.select_all(action="DESELECT")
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

        # Get selected objects for response
        selected = [obj.name for obj in bpy.context.selected_objects]

        if not selected:
            return {"status": "error", "error": "No objects selected to frame"}

        # Find a 3D viewport and frame selected
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                region = None
                for r in area.regions:
                    if r.type == "WINDOW":
                        region = r
                        break

                if region:
                    with bpy.context.temp_override(area=area, region=region):
                        bpy.ops.view3d.view_selected()

                    return {
                        "status": "success",
                        "framed": selected,
                    }

        return {"status": "error", "error": "No 3D viewport found"}

    def _cmd_set_visibility(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set visibility of objects in viewport.

        Args:
            object_name: Single object name to modify
            object_names: List of object names to modify
            visible: Whether objects should be visible (default: True)
            solo: If True, hide all other objects (default: False)

        Returns:
            status, affected objects, visibility state
        """
        object_name = params.get("object_name")
        object_names = params.get("object_names", [])
        visible = params.get("visible", True)
        solo = params.get("solo", False)

        # Build list of target objects
        targets = []
        if object_name:
            targets.append(object_name)
        targets.extend(object_names)

        if not targets:
            return {"status": "error", "error": "No objects specified (use object_name or object_names)"}

        # Validate all objects exist
        target_objs = []
        for name in targets:
            obj = bpy.data.objects.get(name)
            if not obj:
                return {"status": "error", "error": f"Object '{name}' not found"}
            target_objs.append(obj)

        # Solo mode: hide all objects not in target list
        if solo:
            for obj in bpy.data.objects:
                if obj not in target_objs:
                    obj.hide_viewport = True
                    obj.hide_render = True

        # Set visibility for target objects
        for obj in target_objs:
            obj.hide_viewport = not visible
            obj.hide_render = not visible

        return {
            "status": "success",
            "objects": targets,
            "visible": visible,
            "solo": solo,
        }

    # =========================================================================
    # PHYSICS OPERATIONS
    # =========================================================================

    def _cmd_add_rigid_body(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add rigid body physics to an object.

        Args:
            object: Object name (required)
            type: Body type - ACTIVE (affected by physics) or PASSIVE (static collider)
            mass: Object mass in kg (default: 1.0)
            friction: Surface friction 0-1 (default: 0.5)
            restitution: Bounciness 0-1 (default: 0.0)
            shape: Collision shape - CONVEX_HULL, MESH, BOX, SPHERE, etc.

        Returns:
            status, object name, rigid body configuration
        """
        obj_name = params.get("object")
        body_type = params.get("type", "ACTIVE")  # ACTIVE or PASSIVE
        mass = params.get("mass", 1.0)
        friction = params.get("friction", 0.5)
        restitution = params.get("restitution", 0.0)
        collision_shape = params.get("shape", "CONVEX_HULL")

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        # Make active and add rigid body
        bpy.context.view_layer.objects.active = obj
        bpy.ops.rigidbody.object_add(type=body_type)

        # Configure
        rb = obj.rigid_body
        rb.mass = mass
        rb.friction = friction
        rb.restitution = restitution
        rb.collision_shape = collision_shape

        return {
            "status": "success",
            "object": obj.name,
            "rigid_body": {
                "type": body_type,
                "mass": mass,
                "shape": collision_shape,
            },
        }

    def _cmd_add_cloth(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add cloth simulation modifier to an object.

        Args:
            object: Object name (required) - must be a mesh
            mass: Cloth mass in kg (default: 0.3)
            stiffness: Tension and compression stiffness (default: 15.0)

        Returns:
            status, object name, cloth configuration
        """
        obj_name = params.get("object")
        mass = params.get("mass", 0.3)
        stiffness = params.get("stiffness", 15.0)

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        # Add cloth modifier
        mod = obj.modifiers.new(name="Cloth", type="CLOTH")

        # Configure
        cloth = mod.settings
        cloth.mass = mass
        cloth.tension_stiffness = stiffness
        cloth.compression_stiffness = stiffness

        return {
            "status": "success",
            "object": obj.name,
            "cloth": {
                "mass": mass,
                "stiffness": stiffness,
            },
        }

    def _cmd_bake_physics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Bake physics simulation to keyframes.

        Computes physics simulation across frame range and caches results.
        Required before playback or rendering physics.

        Args:
            frame_start: First frame to bake (default: 1)
            frame_end: Last frame to bake (default: 250)

        Returns:
            status, frame range
        """
        frame_start = params.get("frame_start", 1)
        frame_end = params.get("frame_end", 250)

        # Set frame range
        bpy.context.scene.frame_start = frame_start
        bpy.context.scene.frame_end = frame_end

        # Bake rigid body simulation if exists
        if bpy.context.scene.rigidbody_world:
            bpy.ops.ptcache.bake_all(bake=True)

        return {
            "status": "success",
            "frame_start": frame_start,
            "frame_end": frame_end,
        }

    def _cmd_bake_fluid_async(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Start fluid simulation bake in background (non-blocking).

        This starts the bake process without waiting for completion.
        Use get_bake_status to check progress.

        Args:
            domain: Domain object name (optional, uses first found if not specified)
            frame_start: First frame to bake (optional)
            frame_end: Last frame to bake (optional)

        Returns:
            status, message indicating bake started
        """
        domain_name = params.get("domain")
        frame_start = params.get("frame_start")
        frame_end = params.get("frame_end")

        # Find domain object
        domain_obj = None
        if domain_name:
            domain_obj = bpy.data.objects.get(domain_name)
            if not domain_obj:
                return {"status": "error", "error": f"Object '{domain_name}' not found"}
        else:
            # Find first fluid domain
            for obj in bpy.data.objects:
                for mod in obj.modifiers:
                    if mod.type == "FLUID" and mod.fluid_type == "DOMAIN":
                        domain_obj = obj
                        break
                if domain_obj:
                    break

        if not domain_obj:
            return {"status": "error", "error": "No fluid domain found in scene"}

        # Set frame range if provided
        if frame_start is not None:
            bpy.context.scene.frame_start = frame_start
        if frame_end is not None:
            bpy.context.scene.frame_end = frame_end

        # Select domain and make active
        bpy.ops.object.select_all(action="DESELECT")
        domain_obj.select_set(True)
        bpy.context.view_layer.objects.active = domain_obj

        # Start bake in background (non-blocking)
        try:
            bpy.ops.fluid.bake_all("INVOKE_DEFAULT")
            return {
                "status": "started",
                "domain": domain_obj.name,
                "frame_start": bpy.context.scene.frame_start,
                "frame_end": bpy.context.scene.frame_end,
                "message": "Fluid bake started in background. Use get_bake_status to check progress.",
            }
        except Exception as e:
            return {"status": "error", "error": f"Failed to start bake: {e}"}

    def _cmd_get_bake_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get fluid simulation bake status.

        Checks the bake progress for fluid simulations.

        Args:
            domain: Domain object name (optional, uses first found if not specified)

        Returns:
            status, bake progress info
        """
        domain_name = params.get("domain")

        # Find domain object
        domain_obj = None
        domain_settings = None

        if domain_name:
            domain_obj = bpy.data.objects.get(domain_name)
            if not domain_obj:
                return {"status": "error", "error": f"Object '{domain_name}' not found"}
            for mod in domain_obj.modifiers:
                if mod.type == "FLUID" and mod.fluid_type == "DOMAIN":
                    domain_settings = mod.domain_settings
                    break
        else:
            # Find first fluid domain
            for obj in bpy.data.objects:
                for mod in obj.modifiers:
                    if mod.type == "FLUID" and mod.fluid_type == "DOMAIN":
                        domain_obj = obj
                        domain_settings = mod.domain_settings
                        break
                if domain_obj:
                    break

        if not domain_obj or not domain_settings:
            return {"status": "error", "error": "No fluid domain found in scene"}

        # Get cache info
        cache_dir = domain_settings.cache_directory
        is_baked = domain_settings.cache_frame_end > 0

        # Check for cache files to estimate progress
        import os

        cache_files = []
        if os.path.exists(cache_dir):
            cache_files = [f for f in os.listdir(cache_dir) if f.endswith(".bobj.gz") or f.endswith(".uni")]

        # Determine bake state
        frame_start = bpy.context.scene.frame_start
        frame_end = bpy.context.scene.frame_end
        total_frames = frame_end - frame_start + 1

        # Estimate progress from cache files
        baked_frames = len(cache_files)
        progress = min(100, int((baked_frames / max(1, total_frames)) * 100))

        return {
            "status": "success",
            "domain": domain_obj.name,
            "is_baked": is_baked,
            "cache_directory": cache_dir,
            "frame_range": [frame_start, frame_end],
            "total_frames": total_frames,
            "cached_files": baked_frames,
            "progress_estimate": progress,
            "resolution": domain_settings.resolution_max,
        }

    def _cmd_free_fluid_cache(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Free fluid simulation cache to allow re-baking.

        Args:
            domain: Domain object name (optional, uses first found if not specified)

        Returns:
            status, message
        """
        domain_name = params.get("domain")

        # Find domain object
        domain_obj = None
        if domain_name:
            domain_obj = bpy.data.objects.get(domain_name)
            if not domain_obj:
                return {"status": "error", "error": f"Object '{domain_name}' not found"}
        else:
            for obj in bpy.data.objects:
                for mod in obj.modifiers:
                    if mod.type == "FLUID" and mod.fluid_type == "DOMAIN":
                        domain_obj = obj
                        break
                if domain_obj:
                    break

        if not domain_obj:
            return {"status": "error", "error": "No fluid domain found in scene"}

        # Select and free cache
        bpy.ops.object.select_all(action="DESELECT")
        domain_obj.select_set(True)
        bpy.context.view_layer.objects.active = domain_obj

        try:
            bpy.ops.fluid.free_all()
            return {
                "status": "success",
                "domain": domain_obj.name,
                "message": "Fluid cache freed. Ready for re-bake.",
            }
        except Exception as e:
            return {"status": "error", "error": f"Failed to free cache: {e}"}

    # =========================================================================
    # MATERIAL OPERATIONS
    # =========================================================================

    def _cmd_create_material(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new PBR material with Principled BSDF shader.

        Args:
            name: Material name (default: 'Material')
            color: Base color as [R, G, B, A] 0-1 (default: [0.8, 0.8, 0.8, 1.0])
            metallic: Metallic factor 0-1 (default: 0.0)
            roughness: Roughness factor 0-1 (default: 0.5)

        Returns:
            status, material name, color
        """
        name = params.get("name", "Material")
        color = params.get("color", [0.8, 0.8, 0.8, 1.0])  # RGBA
        metallic = params.get("metallic", 0.0)
        roughness = params.get("roughness", 0.5)

        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True

        # Get principled BSDF node
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Metallic"].default_value = metallic
            bsdf.inputs["Roughness"].default_value = roughness

        return {
            "status": "success",
            "material": mat.name,
            "color": color,
        }

    def _cmd_assign_material(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Assign a material to an object."""
        obj_name = params.get("object")
        mat_name = params.get("material")

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        mat = bpy.data.materials.get(mat_name)
        if not mat:
            return {"status": "error", "error": f"Material '{mat_name}' not found"}

        # Assign material
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        return {
            "status": "success",
            "object": obj.name,
            "material": mat.name,
        }

    # =========================================================================
    # ENGINEERING MATERIAL OPERATIONS (Server-synced)
    # =========================================================================

    def _cmd_list_engineering_materials(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available engineering materials from the server library."""
        if not self.materials_client:
            return {"status": "error", "error": "Materials client not available"}

        category = params.get("category")

        try:
            materials = self.materials_client.list_materials(category=category)
            return {
                "status": "success",
                "materials": [
                    {
                        "id": m.id,
                        "name": m.name,
                        "category": m.category,
                        "density_kg_m3": m.density_kg_m3,
                        "youngs_modulus_gpa": (m.youngs_modulus_pa / 1e9) if m.youngs_modulus_pa else None,
                    }
                    for m in materials
                ],
                "count": len(materials),
                "categories": self.materials_client.get_categories(),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _cmd_get_engineering_material(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get details of a specific engineering material."""
        if not self.materials_client:
            return {"status": "error", "error": "Materials client not available"}

        material_id = params.get("material_id")
        if not material_id:
            return {"status": "error", "error": "material_id is required"}

        try:
            material = self.materials_client.get_material(material_id)
            if not material:
                return {"status": "error", "error": f"Material '{material_id}' not found"}

            return {
                "status": "success",
                "material": material.to_dict(),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _cmd_assign_engineering_material(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assign an engineering material to an object.

        This both:
        1. Stores the engineering material assignment for simulation
        2. Creates/updates a visual Blender material with inferred properties
        """
        if not self.materials_client:
            return {"status": "error", "error": "Materials client not available"}

        obj_name = params.get("object")
        material_id = params.get("material_id")
        apply_visual = params.get("apply_visual", True)

        if not obj_name:
            return {"status": "error", "error": "object is required"}
        if not material_id:
            return {"status": "error", "error": "material_id is required"}

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        # Get the engineering material
        material = self.materials_client.get_material(material_id)
        if not material:
            return {"status": "error", "error": f"Engineering material '{material_id}' not found"}

        # Store the engineering material assignment
        self.materials_client.assign_material(obj_name, material_id)

        # Store in object custom properties for persistence
        obj["conjure_material_id"] = material_id
        obj["conjure_material_name"] = material.name
        if material.density_kg_m3:
            obj["conjure_density_kg_m3"] = material.density_kg_m3

        result = {
            "status": "success",
            "object": obj.name,
            "engineering_material": {
                "id": material.id,
                "name": material.name,
                "category": material.category,
                "density_kg_m3": material.density_kg_m3,
            },
        }

        # Optionally apply visual material
        if apply_visual and material.base_color:
            visual_mat_name = f"Conjure_{material.id}"

            # Create or get the visual material
            visual_mat = bpy.data.materials.get(visual_mat_name)
            if not visual_mat:
                visual_mat = bpy.data.materials.new(name=visual_mat_name)
                visual_mat.use_nodes = True

            # Update visual properties
            bsdf = visual_mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                r, g, b = material.base_color
                bsdf.inputs["Base Color"].default_value = (r, g, b, 1.0)
                if material.metallic is not None:
                    bsdf.inputs["Metallic"].default_value = material.metallic
                if material.roughness is not None:
                    bsdf.inputs["Roughness"].default_value = material.roughness

            # Assign to object
            if obj.data and hasattr(obj.data, "materials"):
                if obj.data.materials:
                    obj.data.materials[0] = visual_mat
                else:
                    obj.data.materials.append(visual_mat)

            result["visual_material"] = visual_mat.name

        return result

    def _cmd_get_object_engineering_material(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get the engineering material assigned to an object."""
        obj_name = params.get("object")
        if not obj_name:
            return {"status": "error", "error": "object is required"}

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        # Check custom properties first
        material_id = obj.get("conjure_material_id")
        if not material_id:
            return {
                "status": "success",
                "object": obj.name,
                "engineering_material": None,
                "message": "No engineering material assigned",
            }

        # Get full material details if client available
        material_data = {"id": material_id, "name": obj.get("conjure_material_name", "Unknown")}

        if self.materials_client:
            material = self.materials_client.get_material(material_id)
            if material:
                material_data = material.to_dict()

        return {
            "status": "success",
            "object": obj.name,
            "engineering_material": material_data,
        }

    def _cmd_clear_engineering_material(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clear the engineering material assignment from an object."""
        obj_name = params.get("object")
        if not obj_name:
            return {"status": "error", "error": "object is required"}

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        # Clear custom properties
        for prop in ["conjure_material_id", "conjure_material_name", "conjure_density_kg_m3"]:
            if prop in obj:
                del obj[prop]

        # Clear from materials client
        if self.materials_client:
            self.materials_client.clear_object_material(obj_name)

        return {
            "status": "success",
            "object": obj.name,
            "message": "Engineering material cleared",
        }

    def _cmd_refresh_materials_cache(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Force refresh of the materials cache from the server."""
        if not self.materials_client:
            return {"status": "error", "error": "Materials client not available"}

        try:
            success = self.materials_client.refresh_cache()
            if success:
                materials = self.materials_client.list_materials()
                return {
                    "status": "success",
                    "message": "Materials cache refreshed",
                    "material_count": len(materials),
                    "categories": self.materials_client.get_categories(),
                }
            else:
                return {"status": "error", "error": "Failed to refresh cache"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # =========================================================================
    # ANIMATION OPERATIONS
    # =========================================================================

    def _cmd_insert_keyframe(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a keyframe on an object property."""
        obj_name = params.get("object")
        data_path = params.get("data_path", "location")
        frame = params.get("frame")

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        if frame is not None:
            bpy.context.scene.frame_set(frame)

        obj.keyframe_insert(data_path=data_path)

        return {
            "status": "success",
            "object": obj.name,
            "data_path": data_path,
            "frame": bpy.context.scene.frame_current,
        }

    def _cmd_create_armature(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an armature for rigging."""
        name = params.get("name", "Armature")
        location = params.get("location", [0, 0, 0])

        bpy.ops.object.armature_add(location=tuple(location))

        obj = bpy.context.active_object
        obj.name = name

        return {
            "status": "success",
            "armature": obj.name,
            "bones": len(obj.data.bones),
        }

    # =========================================================================
    # SIMULATION OPERATIONS (Phase 3)
    # =========================================================================

    def _cmd_calculate_dynamic_properties(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate dynamic properties (mass, inertia, CoM) for an object.

        This is used by the server's /api/v1/simulation/dynamic-properties endpoint
        when routing simulation to this Blender client.
        """
        from ..adapters.simulation_adapter import get_simulation_adapter

        obj_name = params.get("object")
        material_id = params.get("material_id")
        density = params.get("density")

        if not obj_name:
            return {"status": "error", "error": "object is required"}

        try:
            adapter = get_simulation_adapter()
            props = adapter.calculate_dynamic_properties(
                object_name=obj_name,
                material_id=material_id,
                density=density,
            )

            return {
                "status": "success",
                "object": obj_name,
                "dynamic_properties": {
                    "mass": props.mass,
                    "volume": props.volume,
                    "surface_area": props.surface_area,
                    "center_of_mass": props.center_of_mass,
                    "moments_of_inertia": props.moments_of_inertia,
                    "principal_axes": props.principal_axes,
                    "bounding_box": props.bounding_box,
                },
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _cmd_run_physics_simulation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a physics simulation (rigid body, cloth, fluid, soft body).

        This is used by the server's /api/v1/simulation/run endpoint
        when routing physics simulations to this Blender client.
        """
        from ..adapters.simulation_adapter import get_simulation_adapter

        simulation_type = params.get("simulation_type")
        objects = params.get("objects", [])
        frame_start = params.get("frame_start", 1)
        frame_end = params.get("frame_end", 250)
        substeps = params.get("substeps", 10)
        settings = params.get("settings", {})

        if not simulation_type:
            return {"status": "error", "error": "simulation_type is required"}
        if not objects:
            return {"status": "error", "error": "objects list is required"}

        try:
            adapter = get_simulation_adapter()
            result = adapter.run_physics_simulation(
                simulation_type=simulation_type,
                objects=objects,
                frame_start=frame_start,
                frame_end=frame_end,
                substeps=substeps,
                settings=settings,
            )

            return {
                "status": result.status,
                "simulation_type": result.simulation_type,
                "frames_computed": result.frames_computed,
                "computation_time_ms": result.computation_time_ms,
                "results": result.results,
                "warnings": result.warnings,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _cmd_export_geometry_ugf(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export object geometry in Universal Geometry Format (UGF).

        Used for transferring geometry between Conjure clients/server.
        """
        from ..adapters.simulation_adapter import get_simulation_adapter

        obj_name = params.get("object")
        include_materials = params.get("include_materials", False)

        if not obj_name:
            return {"status": "error", "error": "object is required"}

        try:
            adapter = get_simulation_adapter()
            ugf_data = adapter.export_geometry_ugf(
                object_name=obj_name,
                include_materials=include_materials,
            )

            return {
                "status": "success",
                "object": obj_name,
                "ugf": ugf_data,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _cmd_import_geometry_ugf(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Import geometry from Universal Geometry Format (UGF).

        Used for receiving geometry from other Conjure clients/server.
        """
        from ..adapters.simulation_adapter import get_simulation_adapter

        ugf_data = params.get("ugf")
        object_name = params.get("name")

        if not ugf_data:
            return {"status": "error", "error": "ugf data is required"}

        try:
            adapter = get_simulation_adapter()
            created_name = adapter.import_geometry_ugf(
                ugf_data=ugf_data,
                object_name=object_name,
            )

            return {
                "status": "success",
                "object": created_name,
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _cmd_add_soft_body(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add soft body simulation to an object."""
        obj_name = params.get("object")
        mass = params.get("mass", 1.0)
        friction = params.get("friction", 0.5)
        speed = params.get("speed", 1.0)
        goal_strength = params.get("goal_strength", 0.7)
        goal_friction = params.get("goal_friction", 0.5)
        use_edges = params.get("use_edges", True)
        pull = params.get("pull", 0.9)
        push = params.get("push", 0.9)

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        # Add soft body modifier
        mod = obj.modifiers.new(name="Softbody", type="SOFT_BODY")
        sb = mod.settings

        sb.mass = mass
        sb.friction = friction
        sb.speed = speed
        sb.goal_default = goal_strength
        sb.goal_friction = goal_friction
        sb.use_edges = use_edges
        sb.pull = pull
        sb.push = push

        return {
            "status": "success",
            "object": obj.name,
            "soft_body": {
                "mass": mass,
                "goal_strength": goal_strength,
            },
        }

    # Resolution presets for fluid simulation
    FLUID_RESOLUTION_PRESETS = {
        "preview": 32,  # Fast preview, low detail
        "medium": 64,  # Balanced (default)
        "high": 128,  # High quality, slower
        "ultra": 256,  # Maximum quality, very slow
    }

    def _cmd_add_fluid_domain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add fluid domain to an object.

        Args:
            object: Object name (required)
            domain_type: LIQUID or GAS (default: LIQUID)
            preset: Resolution preset - preview, medium, high, ultra (default: medium)
            resolution_max: Override resolution (optional, overrides preset)
            use_adaptive_domain: Use adaptive domain (default: False)
            timesteps_max: Maximum timesteps (default: 4)
            use_mesh: Generate mesh for liquid (default: True)
            cache_directory: Custom cache directory (optional)

        Returns:
            status, object name, fluid domain settings
        """
        obj_name = params.get("object")
        domain_type = params.get("domain_type", "LIQUID")
        preset = params.get("preset", "medium")
        resolution = params.get("resolution_max")
        use_adaptive = params.get("use_adaptive_domain", False)
        timesteps = params.get("timesteps_max", 4)
        use_mesh = params.get("use_mesh", True)
        cache_dir = params.get("cache_directory")

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        # Resolve resolution from preset if not explicitly provided
        if resolution is None:
            if preset not in self.FLUID_RESOLUTION_PRESETS:
                return {
                    "status": "error",
                    "error": f"Invalid preset: {preset}. Valid: {list(self.FLUID_RESOLUTION_PRESETS.keys())}",
                }
            resolution = self.FLUID_RESOLUTION_PRESETS[preset]

        # Add fluid modifier
        mod = obj.modifiers.new(name="Fluid", type="FLUID")
        mod.fluid_type = "DOMAIN"

        domain = mod.domain_settings
        domain.domain_type = domain_type
        domain.resolution_max = resolution
        domain.use_adaptive_domain = use_adaptive
        domain.timesteps_max = timesteps

        if domain_type == "LIQUID":
            domain.use_mesh = use_mesh

        # Set cache directory if provided
        if cache_dir:
            domain.cache_directory = cache_dir

        return {
            "status": "success",
            "object": obj.name,
            "fluid_domain": {
                "type": domain_type,
                "resolution": resolution,
                "preset": preset if not params.get("resolution_max") else "custom",
                "cache_directory": domain.cache_directory,
            },
        }

    def _cmd_add_fluid_flow(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add fluid flow (source/inflow) to an object."""
        obj_name = params.get("object")
        flow_type = params.get("flow_type", "LIQUID")
        flow_behavior = params.get("flow_behavior", "INFLOW")
        use_inflow = params.get("use_inflow", True)
        velocity_factor = params.get("velocity_factor", 1.0)

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        mod = obj.modifiers.new(name="Fluid", type="FLUID")
        mod.fluid_type = "FLOW"

        flow = mod.flow_settings
        flow.flow_type = flow_type
        flow.flow_behavior = flow_behavior
        flow.use_inflow = use_inflow
        flow.velocity_factor = velocity_factor

        return {
            "status": "success",
            "object": obj.name,
            "fluid_flow": {
                "type": flow_type,
                "behavior": flow_behavior,
            },
        }

    def _cmd_add_fluid_effector(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add fluid effector (obstacle/guide) to an object."""
        obj_name = params.get("object")
        effector_type = params.get("effector_type", "COLLISION")
        use_effector = params.get("use_effector", True)
        subframes = params.get("subframes", 0)
        surface_distance = params.get("surface_distance", 0.0)

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        mod = obj.modifiers.new(name="Fluid", type="FLUID")
        mod.fluid_type = "EFFECTOR"

        effector = mod.effector_settings
        effector.effector_type = effector_type
        effector.use_effector = use_effector
        effector.subframes = subframes
        effector.surface_distance = surface_distance

        return {
            "status": "success",
            "object": obj.name,
            "fluid_effector": {
                "type": effector_type,
            },
        }

    def _cmd_add_collision(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add collision modifier for cloth/soft body interaction."""
        obj_name = params.get("object")
        damping = params.get("damping", 0.0)
        thickness_outer = params.get("thickness_outer", 0.02)
        friction = params.get("friction", 0.0)

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        mod = obj.modifiers.new(name="Collision", type="COLLISION")
        coll = mod.settings
        coll.damping = damping
        coll.thickness_outer = thickness_outer
        coll.cloth_friction = friction

        return {
            "status": "success",
            "object": obj.name,
            "collision": {
                "damping": damping,
                "thickness": thickness_outer,
            },
        }

    def _cmd_remove_rigid_body(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove rigid body physics from an object."""
        obj_name = params.get("object")

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        if not obj.rigid_body:
            return {"status": "error", "error": f"Object '{obj_name}' has no rigid body"}

        bpy.context.view_layer.objects.active = obj
        bpy.ops.rigidbody.object_remove()

        return {
            "status": "success",
            "object": obj.name,
            "message": "Rigid body removed",
        }

    def _cmd_remove_cloth(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove cloth modifier from an object."""
        obj_name = params.get("object")

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        for mod in obj.modifiers:
            if mod.type == "CLOTH":
                obj.modifiers.remove(mod)
                return {
                    "status": "success",
                    "object": obj.name,
                    "message": "Cloth modifier removed",
                }

        return {"status": "error", "error": f"Object '{obj_name}' has no cloth modifier"}

    def _cmd_configure_rigid_body_world(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Configure rigid body world settings."""
        gravity = params.get("gravity", [0, 0, -9.81])
        time_scale = params.get("time_scale", 1.0)
        substeps = params.get("substeps_per_frame", 10)
        solver_iterations = params.get("solver_iterations", 10)

        scene = bpy.context.scene

        # Ensure rigid body world exists
        if scene.rigidbody_world is None:
            bpy.ops.rigidbody.world_add()

        rbw = scene.rigidbody_world
        rbw.time_scale = time_scale
        rbw.substeps_per_frame = substeps
        rbw.solver_iterations = solver_iterations
        scene.gravity = mathutils.Vector(gravity)

        return {
            "status": "success",
            "rigid_body_world": {
                "gravity": list(scene.gravity),
                "time_scale": time_scale,
                "substeps": substeps,
                "solver_iterations": solver_iterations,
            },
        }

    def _cmd_get_simulation_capabilities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get the simulation capabilities of this Blender client."""
        return {
            "status": "success",
            "capabilities": {
                "physics": {
                    "supported": True,
                    "types": ["rigid_body", "soft_body", "cloth", "fluid"],
                    "gpu_accelerated": True,
                    "realtime_capable": True,
                },
                "dynamic_properties": {
                    "supported": True,
                    "mass_calculation": True,
                    "volume_calculation": True,
                    "center_of_mass": True,
                    "moments_of_inertia": True,
                    "surface_area": True,
                },
                "heat_transfer": {"supported": False},
                "flow_analysis": {"supported": False},
                "structural": {"supported": False},
            },
        }

    # =========================================================================
    # GEOMETRY NODES OPERATIONS
    # =========================================================================

    def _cmd_create_node_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Geometry Nodes modifier/group."""
        from ..adapters.nodes_adapter import get_nodes_adapter

        adapter = get_nodes_adapter()
        return adapter.create_node_group(
            name=params.get("name", "GeometryNodes"),
            object_name=params.get("object_name"),
        )

    def _cmd_add_node(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a node to a geometry node group."""
        from ..adapters.nodes_adapter import get_nodes_adapter

        adapter = get_nodes_adapter()
        return adapter.add_node(
            node_group_name=params["node_group_name"],
            node_type=params["node_type"],
            location=params.get("location"),
            name=params.get("name"),
            settings=params.get("settings"),
        )

    def _cmd_connect_nodes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Connect two nodes in a geometry node group."""
        from ..adapters.nodes_adapter import get_nodes_adapter

        adapter = get_nodes_adapter()
        return adapter.connect_nodes(
            node_group_name=params["node_group_name"],
            from_node=params["from_node"],
            from_socket=params["from_socket"],
            to_node=params["to_node"],
            to_socket=params["to_socket"],
        )

    def _cmd_set_node_input(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set a node input value."""
        from ..adapters.nodes_adapter import get_nodes_adapter

        adapter = get_nodes_adapter()
        return adapter.set_node_input(
            node_group_name=params["node_group_name"],
            node_name=params["node_name"],
            input_name=params["input_name"],
            value=params["value"],
        )

    def _cmd_add_group_input(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add an input to the node group interface."""
        from ..adapters.nodes_adapter import get_nodes_adapter

        adapter = get_nodes_adapter()
        return adapter.add_group_input(
            node_group_name=params["node_group_name"],
            name=params["name"],
            socket_type=params["socket_type"],
            default_value=params.get("default_value"),
        )

    def _cmd_get_node_group_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a geometry node group."""
        from ..adapters.nodes_adapter import get_nodes_adapter

        adapter = get_nodes_adapter()
        return adapter.get_node_group_info(
            node_group_name=params["node_group_name"],
        )

    def _cmd_apply_node_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a geometry node group to an object as a modifier."""
        from ..adapters.nodes_adapter import get_nodes_adapter

        adapter = get_nodes_adapter()
        return adapter.apply_node_group(
            object_name=params["object_name"],
            node_group_name=params["node_group_name"],
            modifier_name=params.get("modifier_name"),
        )

    def _cmd_create_procedural_grid(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a procedural grid with optional wave deformation."""
        from ..adapters.nodes_adapter import get_nodes_adapter

        adapter = get_nodes_adapter()
        return adapter.create_procedural_grid(
            object_name=params.get("object_name", "ProceduralGrid"),
            size_x=params.get("size_x", 10.0),
            size_y=params.get("size_y", 10.0),
            vertices_x=params.get("vertices_x", 10),
            vertices_y=params.get("vertices_y", 10),
            wave_amplitude=params.get("wave_amplitude", 0.0),
            wave_frequency=params.get("wave_frequency", 1.0),
        )

    # =========================================================================
    # FRAME CONTROL OPERATIONS
    # =========================================================================

    def _cmd_set_frame(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set current frame in timeline.

        Args:
            frame: Frame number to set (required)

        Returns:
            status, current frame
        """
        frame = params.get("frame", 1)
        bpy.context.scene.frame_set(frame)
        return {
            "status": "success",
            "frame": bpy.context.scene.frame_current,
        }

    def _cmd_set_frame_range(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set animation frame range.

        Args:
            start: Start frame (required)
            end: End frame (required)

        Returns:
            status, frame range
        """
        start = params.get("start", 1)
        end = params.get("end", 250)

        bpy.context.scene.frame_start = start
        bpy.context.scene.frame_end = end

        return {
            "status": "success",
            "frame_start": start,
            "frame_end": end,
        }

    def _cmd_play_animation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Play animation (toggle playback).

        Args:
            reverse: Play in reverse direction (optional, default: False)

        Returns:
            status, playing state
        """
        reverse = params.get("reverse", False)

        if reverse:
            bpy.ops.screen.animation_play(reverse=True)
        else:
            bpy.ops.screen.animation_play()

        # Check if animation is playing (this may not reflect immediate state change)
        is_playing = (
            bpy.context.screen.is_animation_playing if hasattr(bpy.context.screen, "is_animation_playing") else True
        )

        return {
            "status": "success",
            "playing": is_playing,
            "reverse": reverse,
        }

    # =========================================================================
    # RENDER OPERATIONS
    # =========================================================================

    def _cmd_render_image(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Render current frame to image file.

        Args:
            filepath: Output file path (required)
            engine: Render engine (optional, e.g., CYCLES, BLENDER_EEVEE)
            samples: Sample count for rendering (optional)

        Returns:
            status, filepath
        """
        import os

        filepath = params.get("filepath", "/tmp/render.png")
        engine = params.get("engine")
        samples = params.get("samples")

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

        # Optionally set render engine
        if engine:
            bpy.context.scene.render.engine = engine

        # Optionally set samples
        if samples:
            if bpy.context.scene.render.engine == "CYCLES":
                bpy.context.scene.cycles.samples = samples
            elif bpy.context.scene.render.engine in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
                bpy.context.scene.eevee.taa_render_samples = samples

        # Set output path and render
        bpy.context.scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)

        return {
            "status": "success",
            "filepath": filepath,
            "engine": bpy.context.scene.render.engine,
        }

    def _cmd_set_render_engine(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set render engine.

        Args:
            engine: Render engine name (required)
                    Options: CYCLES, BLENDER_EEVEE, BLENDER_EEVEE_NEXT, BLENDER_WORKBENCH

        Returns:
            status, current engine
        """
        engine = params.get("engine", "CYCLES")

        # Validate engine name
        valid_engines = ["CYCLES", "BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH"]
        if engine.upper() not in valid_engines:
            return {
                "status": "error",
                "error": f"Invalid engine: {engine}. Valid options: {valid_engines}",
            }

        bpy.context.scene.render.engine = engine.upper()

        return {
            "status": "success",
            "engine": bpy.context.scene.render.engine,
        }

    def _cmd_set_render_resolution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set render resolution.

        Args:
            width: Image width in pixels (required)
            height: Image height in pixels (required)
            percentage: Resolution percentage scale (optional, default: 100)

        Returns:
            status, resolution settings
        """
        width = params.get("width", 1920)
        height = params.get("height", 1080)
        percentage = params.get("percentage", 100)

        bpy.context.scene.render.resolution_x = width
        bpy.context.scene.render.resolution_y = height
        bpy.context.scene.render.resolution_percentage = percentage

        return {
            "status": "success",
            "width": width,
            "height": height,
            "percentage": percentage,
        }

    def _cmd_create_studio_lighting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create 3-point studio lighting setup.

        Creates key light, fill light, and rim light for professional lighting.

        Args:
            intensity: Overall light intensity multiplier (optional, default: 1.0)
            key_energy: Key light energy (optional, default: 1000)
            fill_energy: Fill light energy (optional, default: 300)
            rim_energy: Rim light energy (optional, default: 500)

        Returns:
            status, created light names
        """
        intensity = params.get("intensity", 1.0)
        key_energy = params.get("key_energy", 1000) * intensity
        fill_energy = params.get("fill_energy", 300) * intensity
        rim_energy = params.get("rim_energy", 500) * intensity

        created_lights = []

        # Key light - main light, positioned high and to the side
        bpy.ops.object.light_add(type="AREA", location=(5, -5, 8))
        key_light = bpy.context.active_object
        key_light.name = "Studio_Key"
        key_light.data.energy = key_energy
        key_light.data.size = 2
        key_light.rotation_euler = (math.radians(60), 0, math.radians(45))
        created_lights.append(key_light.name)

        # Fill light - softer light on opposite side
        bpy.ops.object.light_add(type="AREA", location=(-4, -3, 4))
        fill_light = bpy.context.active_object
        fill_light.name = "Studio_Fill"
        fill_light.data.energy = fill_energy
        fill_light.data.size = 3
        fill_light.rotation_euler = (math.radians(45), 0, math.radians(-30))
        created_lights.append(fill_light.name)

        # Rim light - backlight for edge definition
        bpy.ops.object.light_add(type="AREA", location=(0, 6, 5))
        rim_light = bpy.context.active_object
        rim_light.name = "Studio_Rim"
        rim_light.data.energy = rim_energy
        rim_light.data.size = 1.5
        rim_light.rotation_euler = (math.radians(120), 0, math.radians(180))
        created_lights.append(rim_light.name)

        return {
            "status": "success",
            "lights": created_lights,
            "key_energy": key_energy,
            "fill_energy": fill_energy,
            "rim_energy": rim_energy,
        }

    # =========================================================================
    # SCRIPT EXECUTION OPERATIONS
    # =========================================================================

    def _cmd_run_script(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute arbitrary Python script in Blender.

        WARNING: This executes arbitrary code. Use with caution.

        Args:
            script: Python script to execute (required)

        Returns:
            status, execution result or error
        """
        script = params.get("script", "")

        if not script:
            return {"status": "error", "error": "No script provided"}

        try:
            # Create execution context with bpy and common modules
            exec_globals = {
                "bpy": bpy,
                "mathutils": mathutils,
                "math": math,
                "__builtins__": __builtins__,
            }
            exec_locals = {}

            exec(script, exec_globals, exec_locals)

            # Return any result variable if set
            result = exec_locals.get("result")

            return {
                "status": "success",
                "result": str(result) if result is not None else None,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"{type(e).__name__}: {str(e)}",
            }

    def _cmd_evaluate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate Python expression and return result.

        Args:
            expression: Python expression to evaluate (required)

        Returns:
            status, evaluation result
        """
        expression = params.get("expression", "")

        if not expression:
            return {"status": "error", "error": "No expression provided"}

        try:
            # Create evaluation context
            eval_globals = {
                "bpy": bpy,
                "mathutils": mathutils,
                "math": math,
            }

            result = eval(expression, eval_globals)

            # Convert result to JSON-serializable format
            if hasattr(result, "__iter__") and not isinstance(result, (str, dict)):
                result = list(result)

            return {
                "status": "success",
                "result": str(result)
                if not isinstance(result, (str, int, float, bool, list, dict, type(None)))
                else result,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"{type(e).__name__}: {str(e)}",
            }

    # =========================================================================
    # SCENE OPERATIONS
    # =========================================================================

    def _cmd_add_light(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a light to the scene.

        Args:
            name: Light name (optional)
            type: Light type - POINT, SUN, SPOT, AREA (optional, default: POINT)
            energy: Light energy/power (optional, default: 1000)
            location: Location [x, y, z] (optional)
            color: RGB color [r, g, b] (optional)

        Returns:
            status, light name and properties
        """
        name = params.get("name", "Light")
        light_type = params.get("type", "POINT").upper()
        energy = params.get("energy", 1000)
        location = params.get("location", [0, 0, 5])
        color = params.get("color")

        # Validate light type
        valid_types = ["POINT", "SUN", "SPOT", "AREA"]
        if light_type not in valid_types:
            return {
                "status": "error",
                "error": f"Invalid light type: {light_type}. Valid options: {valid_types}",
            }

        bpy.ops.object.light_add(type=light_type, location=tuple(location))
        light = bpy.context.active_object
        light.name = name
        light.data.energy = energy

        if color:
            light.data.color = tuple(color[:3])

        return {
            "status": "success",
            "light": light.name,
            "type": light_type,
            "energy": energy,
            "location": list(light.location),
        }

    def _cmd_add_camera(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a camera to the scene.

        Args:
            name: Camera name (optional)
            location: Location [x, y, z] (optional)
            rotation: Rotation [x, y, z] in degrees (optional)
            lens: Focal length in mm (optional, default: 50)

        Returns:
            status, camera name and properties
        """
        name = params.get("name", "Camera")
        location = params.get("location", [0, -10, 5])
        rotation = params.get("rotation", [60, 0, 0])
        lens = params.get("lens", 50)

        bpy.ops.object.camera_add(location=tuple(location))
        camera = bpy.context.active_object
        camera.name = name
        camera.data.lens = lens

        # Apply rotation in degrees
        camera.rotation_euler = [math.radians(r) for r in rotation]

        return {
            "status": "success",
            "camera": camera.name,
            "location": list(camera.location),
            "rotation_degrees": rotation,
            "lens": lens,
        }

    def _cmd_clear_scene(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clear all objects from the scene.

        Args:
            keep_cameras: Keep camera objects (optional, default: False)
            keep_lights: Keep light objects (optional, default: False)

        Returns:
            status, count of deleted objects
        """
        keep_cameras = params.get("keep_cameras", False)
        keep_lights = params.get("keep_lights", False)

        deleted_count = 0
        objects_to_delete = []

        for obj in bpy.data.objects:
            if keep_cameras and obj.type == "CAMERA":
                continue
            if keep_lights and obj.type == "LIGHT":
                continue
            objects_to_delete.append(obj)

        for obj in objects_to_delete:
            bpy.data.objects.remove(obj, do_unlink=True)
            deleted_count += 1

        return {
            "status": "success",
            "deleted_count": deleted_count,
            "remaining_objects": len(bpy.data.objects),
        }

    def _cmd_new_collection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new collection.

        Args:
            name: Collection name (required)
            parent: Parent collection name (optional, links to scene if not specified)

        Returns:
            status, collection name
        """
        name = params.get("name", "Collection")
        parent_name = params.get("parent")

        # Create new collection
        new_collection = bpy.data.collections.new(name)

        # Link to parent or scene
        if parent_name:
            parent = bpy.data.collections.get(parent_name)
            if not parent:
                return {"status": "error", "error": f"Parent collection '{parent_name}' not found"}
            parent.children.link(new_collection)
        else:
            bpy.context.scene.collection.children.link(new_collection)

        return {
            "status": "success",
            "collection": new_collection.name,
            "parent": parent_name or "Scene Collection",
        }

    # =========================================================================
    # IMPORT OPERATIONS
    # =========================================================================

    def _cmd_import_stl(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Import an STL file.

        Args:
            filepath: Path to STL file (required)
            scale: Import scale factor (optional, default: 1.0)

        Returns:
            status, imported object info
        """
        filepath = params.get("filepath")
        scale = params.get("scale", 1.0)

        if not filepath:
            return {"status": "error", "error": "filepath is required"}

        # Remember objects before import
        objects_before = set(bpy.data.objects.keys())

        bpy.ops.wm.stl_import(filepath=filepath)

        # Find newly imported objects
        objects_after = set(bpy.data.objects.keys())
        new_objects = list(objects_after - objects_before)

        # Apply scale if needed
        if scale != 1.0:
            for obj_name in new_objects:
                obj = bpy.data.objects.get(obj_name)
                if obj:
                    obj.scale = (scale, scale, scale)

        return {
            "status": "success",
            "filepath": filepath,
            "imported_objects": new_objects,
            "scale": scale,
        }

    def _cmd_import_obj(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Import an OBJ file.

        Args:
            filepath: Path to OBJ file (required)
            scale: Import scale factor (optional, default: 1.0)

        Returns:
            status, imported object info
        """
        filepath = params.get("filepath")
        scale = params.get("scale", 1.0)

        if not filepath:
            return {"status": "error", "error": "filepath is required"}

        objects_before = set(bpy.data.objects.keys())

        bpy.ops.wm.obj_import(filepath=filepath)

        objects_after = set(bpy.data.objects.keys())
        new_objects = list(objects_after - objects_before)

        if scale != 1.0:
            for obj_name in new_objects:
                obj = bpy.data.objects.get(obj_name)
                if obj:
                    obj.scale = (scale, scale, scale)

        return {
            "status": "success",
            "filepath": filepath,
            "imported_objects": new_objects,
            "scale": scale,
        }

    def _cmd_import_gltf(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Import a glTF/GLB file.

        Args:
            filepath: Path to glTF/GLB file (required)

        Returns:
            status, imported object info
        """
        filepath = params.get("filepath")

        if not filepath:
            return {"status": "error", "error": "filepath is required"}

        objects_before = set(bpy.data.objects.keys())

        bpy.ops.import_scene.gltf(filepath=filepath)

        objects_after = set(bpy.data.objects.keys())
        new_objects = list(objects_after - objects_before)

        return {
            "status": "success",
            "filepath": filepath,
            "imported_objects": new_objects,
        }

    def _cmd_import_fbx(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Import an FBX file.

        Args:
            filepath: Path to FBX file (required)
            scale: Import scale factor (optional, default: 1.0)

        Returns:
            status, imported object info
        """
        filepath = params.get("filepath")
        scale = params.get("scale", 1.0)

        if not filepath:
            return {"status": "error", "error": "filepath is required"}

        objects_before = set(bpy.data.objects.keys())

        bpy.ops.import_scene.fbx(filepath=filepath, global_scale=scale)

        objects_after = set(bpy.data.objects.keys())
        new_objects = list(objects_after - objects_before)

        return {
            "status": "success",
            "filepath": filepath,
            "imported_objects": new_objects,
            "scale": scale,
        }

    # =========================================================================
    # TRANSFORM OPERATIONS
    # =========================================================================

    def _cmd_apply_transforms(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply transforms to an object.

        Args:
            object: Object name (required)
            location: Apply location (optional, default: True)
            rotation: Apply rotation (optional, default: True)
            scale: Apply scale (optional, default: True)

        Returns:
            status, applied transforms
        """
        obj_name = params.get("object")
        apply_location = params.get("location", True)
        apply_rotation = params.get("rotation", True)
        apply_scale = params.get("scale", True)

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        # Select and make active
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.transform_apply(
            location=apply_location,
            rotation=apply_rotation,
            scale=apply_scale,
        )

        return {
            "status": "success",
            "object": obj.name,
            "applied": {
                "location": apply_location,
                "rotation": apply_rotation,
                "scale": apply_scale,
            },
        }

    def _cmd_set_origin(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set object origin.

        Args:
            object: Object name (required)
            type: Origin type - GEOMETRY, CENTER_OF_MASS, CURSOR (optional, default: GEOMETRY)

        Returns:
            status, new origin location
        """
        obj_name = params.get("object")
        origin_type = params.get("type", "GEOMETRY").upper()

        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return {"status": "error", "error": f"Object '{obj_name}' not found"}

        # Map type names to Blender operators
        type_map = {
            "GEOMETRY": "ORIGIN_GEOMETRY_TO_CENTER",
            "CENTER_OF_MASS": "ORIGIN_CENTER_OF_MASS",
            "CURSOR": "ORIGIN_CURSOR",
        }

        if origin_type not in type_map:
            return {
                "status": "error",
                "error": f"Invalid origin type: {origin_type}. Valid options: {list(type_map.keys())}",
            }

        # Select and make active
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        bpy.ops.object.origin_set(type=type_map[origin_type])

        return {
            "status": "success",
            "object": obj.name,
            "origin_type": origin_type,
            "location": list(obj.location),
        }

    def _cmd_parent_object(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Parent one object to another.

        Args:
            child: Child object name (required)
            parent: Parent object name (required)
            keep_transform: Keep world transform (optional, default: True)

        Returns:
            status, parent-child relationship
        """
        child_name = params.get("child")
        parent_name = params.get("parent")
        keep_transform = params.get("keep_transform", True)

        child = bpy.data.objects.get(child_name)
        parent = bpy.data.objects.get(parent_name)

        if not child:
            return {"status": "error", "error": f"Child object '{child_name}' not found"}
        if not parent:
            return {"status": "error", "error": f"Parent object '{parent_name}' not found"}

        # Set parent
        child.parent = parent
        if keep_transform:
            child.matrix_parent_inverse = parent.matrix_world.inverted()

        return {
            "status": "success",
            "child": child.name,
            "parent": parent.name,
            "keep_transform": keep_transform,
        }

    def _cmd_join_objects(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Join multiple objects into one.

        Args:
            objects: List of object names to join (required)
            target: Target object that receives others (optional, uses first object)

        Returns:
            status, resulting object
        """
        object_names = params.get("objects", [])
        target_name = params.get("target")

        if not object_names or len(object_names) < 2:
            return {"status": "error", "error": "At least 2 objects required to join"}

        # Get all objects
        objects = []
        for name in object_names:
            obj = bpy.data.objects.get(name)
            if not obj:
                return {"status": "error", "error": f"Object '{name}' not found"}
            objects.append(obj)

        # Determine target
        target = bpy.data.objects.get(target_name) if target_name else objects[0]
        if not target:
            return {"status": "error", "error": f"Target object '{target_name}' not found"}

        # Select all objects and make target active
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = target

        bpy.ops.object.join()

        return {
            "status": "success",
            "object": target.name,
            "joined_count": len(objects),
            "vertices": len(target.data.vertices) if target.type == "MESH" else 0,
        }
