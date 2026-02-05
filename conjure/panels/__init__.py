"""
Conjure UI panels package.

Contains all N-panel UI components for the Conjure add-on.
"""

import bpy

from .main_panel import (
    CONJURE_PT_connection,
    CONJURE_PT_main,
    CONJURE_PT_materials,
    CONJURE_PT_metrics,
    CONJURE_PT_operations,
    CONJURE_PT_simulation,
)

# All panel classes to register
classes = [
    CONJURE_PT_main,
    CONJURE_PT_connection,
    CONJURE_PT_operations,
    CONJURE_PT_materials,
    CONJURE_PT_simulation,
    CONJURE_PT_metrics,
]


def register():
    """Register all panels."""
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    """Unregister all panels."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
