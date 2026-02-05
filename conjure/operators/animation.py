"""
Animation operators for Conjure.

These operators manage keyframes, armatures, and animation-related functionality.
"""

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import Operator

# =============================================================================
# Keyframe Operators
# =============================================================================


class CONJURE_OT_insert_keyframe(Operator):
    """Insert keyframe for the selected object."""

    bl_idname = "conjure.insert_keyframe"
    bl_label = "Insert Keyframe"
    bl_description = "Insert keyframe at the current frame"
    bl_options = {"REGISTER", "UNDO"}

    data_path: EnumProperty(
        name="Property",
        items=[
            ("location", "Location", "Keyframe location"),
            ("rotation_euler", "Rotation", "Keyframe rotation"),
            ("scale", "Scale", "Keyframe scale"),
            ("LOCROT", "Location + Rotation", "Keyframe both location and rotation"),
            ("LOCROTSCALE", "All Transforms", "Keyframe location, rotation, and scale"),
        ],
        default="LOCROTSCALE",
        description="Property to keyframe",
    )

    frame: IntProperty(
        name="Frame",
        default=1,
        min=0,
        description="Frame number to insert keyframe",
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        frame = self.frame
        server = get_server()

        if not server:
            context.scene.frame_set(frame)

            if self.data_path == "LOCROT":
                obj.keyframe_insert(data_path="location", frame=frame)
                obj.keyframe_insert(data_path="rotation_euler", frame=frame)
            elif self.data_path == "LOCROTSCALE":
                obj.keyframe_insert(data_path="location", frame=frame)
                obj.keyframe_insert(data_path="rotation_euler", frame=frame)
                obj.keyframe_insert(data_path="scale", frame=frame)
            else:
                obj.keyframe_insert(data_path=self.data_path, frame=frame)

            self.report({"INFO"}, f"Inserted keyframe at frame {frame}")
            return {"FINISHED"}

        result = server.executor.execute(
            "insert_keyframe",
            {
                "object": obj.name,
                "data_path": self.data_path,
                "frame": frame,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Inserted keyframe at frame {frame}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        self.frame = context.scene.frame_current
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_delete_keyframe(Operator):
    """Delete keyframe for the selected object at current frame."""

    bl_idname = "conjure.delete_keyframe"
    bl_label = "Delete Keyframe"
    bl_description = "Delete keyframe at the current frame"
    bl_options = {"REGISTER", "UNDO"}

    data_path: EnumProperty(
        name="Property",
        items=[
            ("location", "Location", "Delete location keyframe"),
            ("rotation_euler", "Rotation", "Delete rotation keyframe"),
            ("scale", "Scale", "Delete scale keyframe"),
            ("ALL", "All Properties", "Delete all keyframes at this frame"),
        ],
        default="ALL",
        description="Property to delete keyframe from",
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        frame = context.scene.frame_current
        server = get_server()

        if not server:
            if self.data_path == "ALL":
                obj.keyframe_delete(data_path="location", frame=frame)
                obj.keyframe_delete(data_path="rotation_euler", frame=frame)
                obj.keyframe_delete(data_path="scale", frame=frame)
            else:
                obj.keyframe_delete(data_path=self.data_path, frame=frame)

            self.report({"INFO"}, f"Deleted keyframe at frame {frame}")
            return {"FINISHED"}

        result = server.executor.execute(
            "delete_keyframe",
            {
                "object": obj.name,
                "data_path": self.data_path,
                "frame": frame,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Deleted keyframe at frame {frame}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}


class CONJURE_OT_clear_animation(Operator):
    """Clear all animation data from the selected object."""

    bl_idname = "conjure.clear_animation"
    bl_label = "Clear Animation"
    bl_description = "Remove all keyframes and animation data from object"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        server = get_server()

        if not server:
            obj.animation_data_clear()
            self.report({"INFO"}, f"Cleared animation from: {obj.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "clear_animation",
            {"object": obj.name},
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Cleared animation from: {obj.name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}


class CONJURE_OT_set_keyframe_interpolation(Operator):
    """Set interpolation mode for keyframes."""

    bl_idname = "conjure.set_keyframe_interpolation"
    bl_label = "Set Interpolation"
    bl_description = "Set the interpolation mode for object keyframes"
    bl_options = {"REGISTER", "UNDO"}

    interpolation: EnumProperty(
        name="Interpolation",
        items=[
            ("CONSTANT", "Constant", "No interpolation"),
            ("LINEAR", "Linear", "Linear interpolation"),
            ("BEZIER", "Bezier", "Smooth bezier curve"),
            ("SINE", "Sinusoidal", "Sine wave easing"),
            ("QUAD", "Quadratic", "Quadratic easing"),
            ("CUBIC", "Cubic", "Cubic easing"),
            ("QUART", "Quartic", "Quartic easing"),
            ("QUINT", "Quintic", "Quintic easing"),
            ("EXPO", "Exponential", "Exponential easing"),
            ("CIRC", "Circular", "Circular easing"),
            ("BACK", "Back", "Overshoot easing"),
            ("BOUNCE", "Bounce", "Bouncing easing"),
            ("ELASTIC", "Elastic", "Elastic easing"),
        ],
        default="BEZIER",
        description="Keyframe interpolation mode",
    )

    easing: EnumProperty(
        name="Easing",
        items=[
            ("AUTO", "Automatic", "Automatic easing"),
            ("EASE_IN", "Ease In", "Ease in"),
            ("EASE_OUT", "Ease Out", "Ease out"),
            ("EASE_IN_OUT", "Ease In-Out", "Ease in and out"),
        ],
        default="AUTO",
        description="Easing type for interpolation",
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.animation_data and obj.animation_data.action

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        server = get_server()

        if not server:
            action = obj.animation_data.action
            for fcurve in action.fcurves:
                for kfp in fcurve.keyframe_points:
                    kfp.interpolation = self.interpolation
                    kfp.easing = self.easing
            self.report({"INFO"}, f"Set interpolation to {self.interpolation}")
            return {"FINISHED"}

        result = server.executor.execute(
            "set_keyframe_interpolation",
            {
                "object": obj.name,
                "interpolation": self.interpolation,
                "easing": self.easing,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Set interpolation to {self.interpolation}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# =============================================================================
# Armature Operators
# =============================================================================


class CONJURE_OT_create_armature(Operator):
    """Create a new armature object."""

    bl_idname = "conjure.create_armature"
    bl_label = "Create Armature"
    bl_description = "Create a new armature (skeleton) object"
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty(
        name="Name",
        default="Armature",
        description="Name for the new armature",
    )

    location: FloatVectorProperty(
        name="Location",
        default=(0.0, 0.0, 0.0),
        subtype="TRANSLATION",
        description="Location for the armature",
    )

    display_type: EnumProperty(
        name="Display As",
        items=[
            ("OCTAHEDRAL", "Octahedral", "Standard octahedral display"),
            ("STICK", "Stick", "Simple stick display"),
            ("BBONE", "B-Bone", "Bendy bone display"),
            ("ENVELOPE", "Envelope", "Envelope display"),
            ("WIRE", "Wire", "Wire display"),
        ],
        default="OCTAHEDRAL",
        description="Bone display type",
    )

    def execute(self, context):
        from ..engine import get_server

        server = get_server()

        if not server:
            # Create armature data
            armature_data = bpy.data.armatures.new(self.name)
            armature_data.display_type = self.display_type

            # Create armature object
            armature_obj = bpy.data.objects.new(self.name, armature_data)
            armature_obj.location = self.location

            # Link to scene
            context.collection.objects.link(armature_obj)
            context.view_layer.objects.active = armature_obj
            armature_obj.select_set(True)

            self.report({"INFO"}, f"Created armature: {self.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "create_armature",
            {
                "name": self.name,
                "location": list(self.location),
                "display_type": self.display_type,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Created armature: {result.get('object')}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_add_bone(Operator):
    """Add a bone to the active armature."""

    bl_idname = "conjure.add_bone"
    bl_label = "Add Bone"
    bl_description = "Add a new bone to the active armature"
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty(
        name="Name",
        default="Bone",
        description="Name for the new bone",
    )

    head: FloatVectorProperty(
        name="Head",
        default=(0.0, 0.0, 0.0),
        subtype="TRANSLATION",
        description="Head (base) position of the bone",
    )

    tail: FloatVectorProperty(
        name="Tail",
        default=(0.0, 0.0, 1.0),
        subtype="TRANSLATION",
        description="Tail (tip) position of the bone",
    )

    parent_bone: StringProperty(
        name="Parent Bone",
        default="",
        description="Name of parent bone (optional)",
    )

    connected: BoolProperty(
        name="Connected",
        default=False,
        description="Connect to parent bone",
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "ARMATURE"

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        server = get_server()

        if not server:
            # Must be in edit mode to add bones
            bpy.ops.object.mode_set(mode="EDIT")

            armature = obj.data
            bone = armature.edit_bones.new(self.name)
            bone.head = self.head
            bone.tail = self.tail

            if self.parent_bone and self.parent_bone in armature.edit_bones:
                bone.parent = armature.edit_bones[self.parent_bone]
                bone.use_connect = self.connected

            bpy.ops.object.mode_set(mode="OBJECT")
            self.report({"INFO"}, f"Added bone: {self.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "add_bone",
            {
                "armature": obj.name,
                "name": self.name,
                "head": list(self.head),
                "tail": list(self.tail),
                "parent_bone": self.parent_bone,
                "connected": self.connected,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Added bone: {self.name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_bind_armature(Operator):
    """Bind mesh to armature with automatic weights."""

    bl_idname = "conjure.bind_armature"
    bl_label = "Bind to Armature"
    bl_description = "Bind selected mesh objects to the active armature"
    bl_options = {"REGISTER", "UNDO"}

    bind_type: EnumProperty(
        name="Bind Type",
        items=[
            ("ARMATURE_AUTO", "Automatic Weights", "Automatic weight assignment"),
            ("ARMATURE_NAME", "By Name", "Match vertex groups to bones by name"),
            ("ARMATURE_ENVELOPE", "Envelope Weights", "Use bone envelopes"),
        ],
        default="ARMATURE_AUTO",
        description="Method for binding mesh to armature",
    )

    @classmethod
    def poll(cls, context):
        # Need armature and at least one mesh selected
        if context.active_object is None or context.active_object.type != "ARMATURE":
            return False
        return any(obj.type == "MESH" for obj in context.selected_objects if obj != context.active_object)

    def execute(self, context):
        from ..engine import get_server

        armature = context.active_object
        meshes = [obj for obj in context.selected_objects if obj.type == "MESH"]
        server = get_server()

        if not server:
            for mesh in meshes:
                # Add armature modifier
                mod = mesh.modifiers.new(name="Armature", type="ARMATURE")
                mod.object = armature

                # Set parent with automatic weights
                mesh.parent = armature
                bpy.ops.object.parent_set(type=self.bind_type)

            self.report({"INFO"}, f"Bound {len(meshes)} mesh(es) to {armature.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "bind_armature",
            {
                "armature": armature.name,
                "meshes": [m.name for m in meshes],
                "bind_type": self.bind_type,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Bound meshes to {armature.name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_pose_bone(Operator):
    """Set pose for a bone in the active armature."""

    bl_idname = "conjure.pose_bone"
    bl_label = "Pose Bone"
    bl_description = "Set the pose transform for a bone"
    bl_options = {"REGISTER", "UNDO"}

    bone_name: StringProperty(
        name="Bone",
        default="",
        description="Name of the bone to pose",
    )

    location: FloatVectorProperty(
        name="Location",
        default=(0.0, 0.0, 0.0),
        subtype="TRANSLATION",
        description="Bone location offset",
    )

    rotation: FloatVectorProperty(
        name="Rotation",
        default=(0.0, 0.0, 0.0),
        subtype="EULER",
        description="Bone rotation (Euler)",
    )

    scale: FloatVectorProperty(
        name="Scale",
        default=(1.0, 1.0, 1.0),
        subtype="XYZ",
        description="Bone scale",
    )

    insert_keyframe: BoolProperty(
        name="Insert Keyframe",
        default=False,
        description="Insert keyframe at current frame",
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "ARMATURE"

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        server = get_server()

        if not server:
            bpy.ops.object.mode_set(mode="POSE")

            if self.bone_name not in obj.pose.bones:
                self.report({"ERROR"}, f"Bone not found: {self.bone_name}")
                return {"CANCELLED"}

            pose_bone = obj.pose.bones[self.bone_name]
            pose_bone.location = self.location
            pose_bone.rotation_euler = self.rotation
            pose_bone.scale = self.scale

            if self.insert_keyframe:
                frame = context.scene.frame_current
                pose_bone.keyframe_insert(data_path="location", frame=frame)
                pose_bone.keyframe_insert(data_path="rotation_euler", frame=frame)
                pose_bone.keyframe_insert(data_path="scale", frame=frame)

            self.report({"INFO"}, f"Posed bone: {self.bone_name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "pose_bone",
            {
                "armature": obj.name,
                "bone_name": self.bone_name,
                "location": list(self.location),
                "rotation": list(self.rotation),
                "scale": list(self.scale),
                "insert_keyframe": self.insert_keyframe,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Posed bone: {self.bone_name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# =============================================================================
# Shape Key Operators
# =============================================================================


class CONJURE_OT_add_shape_key(Operator):
    """Add a shape key to the active object."""

    bl_idname = "conjure.add_shape_key"
    bl_label = "Add Shape Key"
    bl_description = "Add a new shape key to the active mesh object"
    bl_options = {"REGISTER", "UNDO"}

    name: StringProperty(
        name="Name",
        default="Key",
        description="Name for the new shape key",
    )

    from_mix: BoolProperty(
        name="From Mix",
        default=False,
        description="Create from current mix of shape keys",
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "MESH"

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        server = get_server()

        if not server:
            # Add basis key if none exists
            if obj.data.shape_keys is None:
                obj.shape_key_add(name="Basis", from_mix=False)

            # Add new shape key
            shape_key = obj.shape_key_add(name=self.name, from_mix=self.from_mix)
            self.report({"INFO"}, f"Added shape key: {shape_key.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "add_shape_key",
            {
                "object": obj.name,
                "name": self.name,
                "from_mix": self.from_mix,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Added shape key: {self.name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_set_shape_key_value(Operator):
    """Set the value of a shape key."""

    bl_idname = "conjure.set_shape_key_value"
    bl_label = "Set Shape Key Value"
    bl_description = "Set the influence value of a shape key"
    bl_options = {"REGISTER", "UNDO"}

    shape_key_name: StringProperty(
        name="Shape Key",
        default="",
        description="Name of the shape key",
    )

    value: FloatProperty(
        name="Value",
        default=1.0,
        min=0.0,
        max=1.0,
        description="Shape key influence value",
    )

    insert_keyframe: BoolProperty(
        name="Insert Keyframe",
        default=False,
        description="Insert keyframe at current frame",
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == "MESH" and obj.data.shape_keys is not None

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        server = get_server()

        if not server:
            if self.shape_key_name not in obj.data.shape_keys.key_blocks:
                self.report({"ERROR"}, f"Shape key not found: {self.shape_key_name}")
                return {"CANCELLED"}

            shape_key = obj.data.shape_keys.key_blocks[self.shape_key_name]
            shape_key.value = self.value

            if self.insert_keyframe:
                shape_key.keyframe_insert(data_path="value", frame=context.scene.frame_current)

            self.report({"INFO"}, f"Set {self.shape_key_name} = {self.value}")
            return {"FINISHED"}

        result = server.executor.execute(
            "set_shape_key_value",
            {
                "object": obj.name,
                "shape_key_name": self.shape_key_name,
                "value": self.value,
                "insert_keyframe": self.insert_keyframe,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Set {self.shape_key_name} = {self.value}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# =============================================================================
# Timeline Operators
# =============================================================================


class CONJURE_OT_set_frame_range(Operator):
    """Set the animation frame range."""

    bl_idname = "conjure.set_frame_range"
    bl_label = "Set Frame Range"
    bl_description = "Set the start and end frame for animation"
    bl_options = {"REGISTER", "UNDO"}

    frame_start: IntProperty(
        name="Start Frame",
        default=1,
        min=0,
        description="Animation start frame",
    )

    frame_end: IntProperty(
        name="End Frame",
        default=250,
        min=1,
        description="Animation end frame",
    )

    fps: FloatProperty(
        name="Frame Rate",
        default=24.0,
        min=1.0,
        max=120.0,
        description="Frames per second",
    )

    def execute(self, context):
        from ..engine import get_server

        server = get_server()

        if not server:
            context.scene.frame_start = self.frame_start
            context.scene.frame_end = self.frame_end
            context.scene.render.fps = int(self.fps)
            self.report({"INFO"}, f"Set frame range: {self.frame_start} - {self.frame_end} @ {self.fps}fps")
            return {"FINISHED"}

        result = server.executor.execute(
            "set_frame_range",
            {
                "frame_start": self.frame_start,
                "frame_end": self.frame_end,
                "fps": self.fps,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Set frame range: {self.frame_start} - {self.frame_end}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end
        self.fps = float(context.scene.render.fps)
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_goto_frame(Operator):
    """Jump to a specific frame."""

    bl_idname = "conjure.goto_frame"
    bl_label = "Go To Frame"
    bl_description = "Jump to a specific frame in the timeline"
    bl_options = {"REGISTER", "UNDO"}

    frame: IntProperty(
        name="Frame",
        default=1,
        min=0,
        description="Frame to jump to",
    )

    def execute(self, context):
        from ..engine import get_server

        server = get_server()

        if not server:
            context.scene.frame_set(self.frame)
            self.report({"INFO"}, f"Jumped to frame {self.frame}")
            return {"FINISHED"}

        result = server.executor.execute(
            "goto_frame",
            {"frame": self.frame},
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Jumped to frame {self.frame}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        self.frame = context.scene.frame_current
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_play_animation(Operator):
    """Play/pause the animation."""

    bl_idname = "conjure.play_animation"
    bl_label = "Play Animation"
    bl_description = "Toggle animation playback"
    bl_options = {"REGISTER"}

    def execute(self, context):
        bpy.ops.screen.animation_play()
        return {"FINISHED"}
