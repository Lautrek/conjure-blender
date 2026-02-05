"""
Primitive creation operators for Conjure.

These operators create basic mesh primitives via Conjure commands.
"""

import bpy
from bpy.props import FloatProperty, FloatVectorProperty, IntProperty, StringProperty
from bpy.types import Operator


class CONJURE_OT_create_cube(Operator):
    """Create a cube via Conjure."""

    bl_idname = "conjure.create_cube"
    bl_label = "Create Cube"
    bl_description = "Create a cube mesh primitive"
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty(
        name="Name",
        default="Cube",
        description="Name for the new cube",
    )

    size: FloatProperty(
        name="Size",
        default=2.0,
        min=0.001,
        description="Size of the cube",
    )

    location: FloatVectorProperty(
        name="Location",
        default=(0.0, 0.0, 0.0),
        subtype="TRANSLATION",
        description="Location for the new cube",
    )

    def execute(self, context):
        from ..engine import get_server

        server = get_server()
        if not server:
            # Fallback to direct Blender operation
            bpy.ops.mesh.primitive_cube_add(size=self.size, location=self.location)
            bpy.context.active_object.name = self.name
            self.report({"INFO"}, f"Created cube: {self.name}")
            return {"FINISHED"}

        # Execute via server
        result = server.executor.execute(
            "create_cube",
            {
                "name": self.name,
                "size": self.size,
                "location": list(self.location),
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Created cube: {result.get('object')}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_create_sphere(Operator):
    """Create a sphere via Conjure."""

    bl_idname = "conjure.create_sphere"
    bl_label = "Create Sphere"
    bl_description = "Create a UV sphere mesh primitive"
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty(
        name="Name",
        default="Sphere",
        description="Name for the new sphere",
    )

    radius: FloatProperty(
        name="Radius",
        default=1.0,
        min=0.001,
        description="Radius of the sphere",
    )

    segments: IntProperty(
        name="Segments",
        default=32,
        min=3,
        max=256,
        description="Number of segments",
    )

    rings: IntProperty(
        name="Rings",
        default=16,
        min=2,
        max=256,
        description="Number of rings",
    )

    location: FloatVectorProperty(
        name="Location",
        default=(0.0, 0.0, 0.0),
        subtype="TRANSLATION",
        description="Location for the new sphere",
    )

    def execute(self, context):
        from ..engine import get_server

        server = get_server()
        if not server:
            bpy.ops.mesh.primitive_uv_sphere_add(
                radius=self.radius,
                segments=self.segments,
                ring_count=self.rings,
                location=self.location,
            )
            bpy.context.active_object.name = self.name
            self.report({"INFO"}, f"Created sphere: {self.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "create_sphere",
            {
                "name": self.name,
                "radius": self.radius,
                "segments": self.segments,
                "rings": self.rings,
                "location": list(self.location),
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Created sphere: {result.get('object')}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_create_cylinder(Operator):
    """Create a cylinder via Conjure."""

    bl_idname = "conjure.create_cylinder"
    bl_label = "Create Cylinder"
    bl_description = "Create a cylinder mesh primitive"
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty(
        name="Name",
        default="Cylinder",
        description="Name for the new cylinder",
    )

    radius: FloatProperty(
        name="Radius",
        default=1.0,
        min=0.001,
        description="Radius of the cylinder",
    )

    depth: FloatProperty(
        name="Depth",
        default=2.0,
        min=0.001,
        description="Depth (height) of the cylinder",
    )

    vertices: IntProperty(
        name="Vertices",
        default=32,
        min=3,
        max=256,
        description="Number of vertices in cap",
    )

    location: FloatVectorProperty(
        name="Location",
        default=(0.0, 0.0, 0.0),
        subtype="TRANSLATION",
        description="Location for the new cylinder",
    )

    def execute(self, context):
        from ..engine import get_server

        server = get_server()
        if not server:
            bpy.ops.mesh.primitive_cylinder_add(
                radius=self.radius,
                depth=self.depth,
                vertices=self.vertices,
                location=self.location,
            )
            bpy.context.active_object.name = self.name
            self.report({"INFO"}, f"Created cylinder: {self.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "create_cylinder",
            {
                "name": self.name,
                "radius": self.radius,
                "depth": self.depth,
                "vertices": self.vertices,
                "location": list(self.location),
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Created cylinder: {result.get('object')}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_create_cone(Operator):
    """Create a cone via Conjure."""

    bl_idname = "conjure.create_cone"
    bl_label = "Create Cone"
    bl_description = "Create a cone mesh primitive"
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty(
        name="Name",
        default="Cone",
        description="Name for the new cone",
    )

    radius1: FloatProperty(
        name="Base Radius",
        default=1.0,
        min=0.0,
        description="Radius of the base",
    )

    radius2: FloatProperty(
        name="Top Radius",
        default=0.0,
        min=0.0,
        description="Radius of the top (0 for point)",
    )

    depth: FloatProperty(
        name="Depth",
        default=2.0,
        min=0.001,
        description="Depth (height) of the cone",
    )

    vertices: IntProperty(
        name="Vertices",
        default=32,
        min=3,
        max=256,
        description="Number of vertices in cap",
    )

    location: FloatVectorProperty(
        name="Location",
        default=(0.0, 0.0, 0.0),
        subtype="TRANSLATION",
        description="Location for the new cone",
    )

    def execute(self, context):
        from ..engine import get_server

        server = get_server()
        if not server:
            bpy.ops.mesh.primitive_cone_add(
                radius1=self.radius1,
                radius2=self.radius2,
                depth=self.depth,
                vertices=self.vertices,
                location=self.location,
            )
            bpy.context.active_object.name = self.name
            self.report({"INFO"}, f"Created cone: {self.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "create_cone",
            {
                "name": self.name,
                "radius1": self.radius1,
                "radius2": self.radius2,
                "depth": self.depth,
                "vertices": self.vertices,
                "location": list(self.location),
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Created cone: {result.get('object')}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
