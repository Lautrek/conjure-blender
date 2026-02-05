"""
Transform operators for Conjure.

Operators for moving, rotating, and scaling objects.
"""

import bpy
from bpy.props import FloatProperty, FloatVectorProperty, StringProperty
from bpy.types import Operator


class CONJURE_OT_move_object(Operator):
    """Move an object via Conjure."""

    bl_idname = "conjure.move_object"
    bl_label = "Move Object"
    bl_description = "Move an object to a new location"
    bl_options = {"REGISTER", "UNDO"}

    object_name: StringProperty(
        name="Object",
        description="Name of the object to move",
    )

    location: FloatVectorProperty(
        name="Location",
        default=(0.0, 0.0, 0.0),
        subtype="TRANSLATION",
        description="New location for the object",
    )

    def execute(self, context):
        from ..engine import get_server

        obj_name = self.object_name or (context.active_object.name if context.active_object else None)
        if not obj_name:
            self.report({"ERROR"}, "No object selected")
            return {"CANCELLED"}

        server = get_server()
        if not server:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                obj.location = self.location
                self.report({"INFO"}, f"Moved {obj_name}")
                return {"FINISHED"}
            else:
                self.report({"ERROR"}, f"Object '{obj_name}' not found")
                return {"CANCELLED"}

        result = server.executor.execute(
            "move_object",
            {
                "object": obj_name,
                "location": list(self.location),
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Moved {obj_name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        if context.active_object:
            self.object_name = context.active_object.name
            self.location = context.active_object.location.copy()
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_rotate_object(Operator):
    """Rotate an object via Conjure."""

    bl_idname = "conjure.rotate_object"
    bl_label = "Rotate Object"
    bl_description = "Rotate an object"
    bl_options = {"REGISTER", "UNDO"}

    object_name: StringProperty(
        name="Object",
        description="Name of the object to rotate",
    )

    rotation: FloatVectorProperty(
        name="Rotation (degrees)",
        default=(0.0, 0.0, 0.0),
        subtype="EULER",
        description="Rotation in degrees",
    )

    def execute(self, context):
        import math

        from ..engine import get_server

        obj_name = self.object_name or (context.active_object.name if context.active_object else None)
        if not obj_name:
            self.report({"ERROR"}, "No object selected")
            return {"CANCELLED"}

        server = get_server()
        if not server:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                obj.rotation_euler = [math.radians(r) for r in self.rotation]
                self.report({"INFO"}, f"Rotated {obj_name}")
                return {"FINISHED"}
            else:
                self.report({"ERROR"}, f"Object '{obj_name}' not found")
                return {"CANCELLED"}

        result = server.executor.execute(
            "rotate_object",
            {
                "object": obj_name,
                "rotation": list(self.rotation),
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Rotated {obj_name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        import math

        if context.active_object:
            self.object_name = context.active_object.name
            self.rotation = [math.degrees(r) for r in context.active_object.rotation_euler]
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_scale_object(Operator):
    """Scale an object via Conjure."""

    bl_idname = "conjure.scale_object"
    bl_label = "Scale Object"
    bl_description = "Scale an object"
    bl_options = {"REGISTER", "UNDO"}

    object_name: StringProperty(
        name="Object",
        description="Name of the object to scale",
    )

    scale: FloatVectorProperty(
        name="Scale",
        default=(1.0, 1.0, 1.0),
        subtype="XYZ",
        description="Scale factors",
    )

    uniform: FloatProperty(
        name="Uniform Scale",
        default=1.0,
        min=0.001,
        description="Uniform scale factor (overrides XYZ if non-default)",
    )

    def execute(self, context):
        from ..engine import get_server

        obj_name = self.object_name or (context.active_object.name if context.active_object else None)
        if not obj_name:
            self.report({"ERROR"}, "No object selected")
            return {"CANCELLED"}

        server = get_server()
        if not server:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                if self.uniform != 1.0:
                    obj.scale = (self.uniform, self.uniform, self.uniform)
                else:
                    obj.scale = self.scale
                self.report({"INFO"}, f"Scaled {obj_name}")
                return {"FINISHED"}
            else:
                self.report({"ERROR"}, f"Object '{obj_name}' not found")
                return {"CANCELLED"}

        params = {"object": obj_name}
        if self.uniform != 1.0:
            params["uniform"] = self.uniform
        else:
            params["scale"] = list(self.scale)

        result = server.executor.execute("scale_object", params)

        if result.get("status") == "success":
            self.report({"INFO"}, f"Scaled {obj_name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        if context.active_object:
            self.object_name = context.active_object.name
            self.scale = context.active_object.scale.copy()
        return context.window_manager.invoke_props_dialog(self)
