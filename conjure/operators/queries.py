"""
Query operators for Conjure.

Operators for querying scene and object state.
"""

import bpy
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator


class CONJURE_OT_get_state(Operator):
    """Get scene state via Conjure."""

    bl_idname = "conjure.get_state"
    bl_label = "Get Scene State"
    bl_description = "Get current scene state information"

    def execute(self, context):
        from ..engine import get_server

        server = get_server()
        if not server:
            # Direct query without server
            scene = context.scene
            obj_count = len(scene.objects)
            mesh_count = sum(1 for obj in scene.objects if obj.type == "MESH")
            self.report({"INFO"}, f"Scene: {scene.name}, Objects: {obj_count}, Meshes: {mesh_count}")
            return {"FINISHED"}

        result = server.executor.execute("get_state", {})

        if result.get("status") == "success":
            obj_count = result.get("object_count", 0)
            scene_name = result.get("scene", "Unknown")
            self.report({"INFO"}, f"Scene: {scene_name}, Objects: {obj_count}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}


class CONJURE_OT_list_objects(Operator):
    """List objects via Conjure."""

    bl_idname = "conjure.list_objects"
    bl_label = "List Objects"
    bl_description = "List all objects in the scene"

    object_type: EnumProperty(
        name="Type",
        items=[
            ("ALL", "All", "All object types"),
            ("MESH", "Mesh", "Mesh objects only"),
            ("CURVE", "Curve", "Curve objects only"),
            ("ARMATURE", "Armature", "Armature objects only"),
            ("EMPTY", "Empty", "Empty objects only"),
            ("LIGHT", "Light", "Light objects only"),
            ("CAMERA", "Camera", "Camera objects only"),
        ],
        default="ALL",
        description="Filter by object type",
    )

    def execute(self, context):
        from ..engine import get_server

        type_filter = None if self.object_type == "ALL" else self.object_type

        server = get_server()
        if not server:
            objects = [obj.name for obj in context.scene.objects if type_filter is None or obj.type == type_filter]
            self.report(
                {"INFO"}, f"Objects ({len(objects)}): {', '.join(objects[:10])}{'...' if len(objects) > 10 else ''}"
            )
            return {"FINISHED"}

        result = server.executor.execute(
            "list_objects",
            {"type": type_filter} if type_filter else {},
        )

        if result.get("status") == "success":
            objects = result.get("objects", [])
            names = [obj.get("name", "?") for obj in objects]
            self.report({"INFO"}, f"Objects ({len(names)}): {', '.join(names[:10])}{'...' if len(names) > 10 else ''}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
