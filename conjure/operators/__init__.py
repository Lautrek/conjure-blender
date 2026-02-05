"""
Conjure Blender operators package.

Contains all bpy.types.Operator implementations for Conjure functionality.
"""

import bpy

from .animation import (
    CONJURE_OT_add_bone,
    CONJURE_OT_add_shape_key,
    CONJURE_OT_bind_armature,
    CONJURE_OT_clear_animation,
    CONJURE_OT_create_armature,
    CONJURE_OT_delete_keyframe,
    CONJURE_OT_goto_frame,
    CONJURE_OT_insert_keyframe,
    CONJURE_OT_play_animation,
    CONJURE_OT_pose_bone,
    CONJURE_OT_set_frame_range,
    CONJURE_OT_set_keyframe_interpolation,
    CONJURE_OT_set_shape_key_value,
)
from .connection import (
    CONJURE_OT_connect,
    CONJURE_OT_disconnect,
    CONJURE_OT_test_connection,
)
from .physics import (
    CONJURE_OT_add_cloth,
    CONJURE_OT_add_collision,
    CONJURE_OT_add_fluid_domain,
    CONJURE_OT_add_fluid_effector,
    CONJURE_OT_add_fluid_flow,
    CONJURE_OT_add_rigid_body,
    CONJURE_OT_add_soft_body,
    CONJURE_OT_bake_physics,
    CONJURE_OT_remove_cloth,
    CONJURE_OT_remove_rigid_body,
    CONJURE_OT_rigid_body_world,
)
from .primitives import (
    CONJURE_OT_create_cone,
    CONJURE_OT_create_cube,
    CONJURE_OT_create_cylinder,
    CONJURE_OT_create_sphere,
)
from .queries import (
    CONJURE_OT_get_state,
    CONJURE_OT_list_objects,
)
from .transforms import (
    CONJURE_OT_move_object,
    CONJURE_OT_rotate_object,
    CONJURE_OT_scale_object,
)

# All operator classes to register
classes = [
    # Connection
    CONJURE_OT_connect,
    CONJURE_OT_disconnect,
    CONJURE_OT_test_connection,
    # Primitives
    CONJURE_OT_create_cube,
    CONJURE_OT_create_sphere,
    CONJURE_OT_create_cylinder,
    CONJURE_OT_create_cone,
    # Transforms
    CONJURE_OT_move_object,
    CONJURE_OT_rotate_object,
    CONJURE_OT_scale_object,
    # Queries
    CONJURE_OT_get_state,
    CONJURE_OT_list_objects,
    # Physics
    CONJURE_OT_add_rigid_body,
    CONJURE_OT_remove_rigid_body,
    CONJURE_OT_rigid_body_world,
    CONJURE_OT_add_cloth,
    CONJURE_OT_remove_cloth,
    CONJURE_OT_add_collision,
    CONJURE_OT_add_fluid_domain,
    CONJURE_OT_add_fluid_flow,
    CONJURE_OT_add_fluid_effector,
    CONJURE_OT_bake_physics,
    CONJURE_OT_add_soft_body,
    # Animation
    CONJURE_OT_insert_keyframe,
    CONJURE_OT_delete_keyframe,
    CONJURE_OT_clear_animation,
    CONJURE_OT_set_keyframe_interpolation,
    CONJURE_OT_create_armature,
    CONJURE_OT_add_bone,
    CONJURE_OT_bind_armature,
    CONJURE_OT_pose_bone,
    CONJURE_OT_add_shape_key,
    CONJURE_OT_set_shape_key_value,
    CONJURE_OT_set_frame_range,
    CONJURE_OT_goto_frame,
    CONJURE_OT_play_animation,
]


def register():
    """Register all operators."""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister all operators."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
