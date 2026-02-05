"""
Conjure - AI-Powered CAD Control for Blender

A comprehensive Blender add-on that integrates with the Conjure AI CAD platform,
enabling AI-assisted 3D modeling workflows for designers, engineers, and artists.

Features:
- AI-powered modeling operations via Conjure server
- Full Blender operation support (primitives, modifiers, geometry nodes, physics)
- Real-time connection to Conjure cloud for orchestration
- Hybrid simulation support (physics executed locally, FEA/CFD via server)
"""

bl_info = {
    "name": "Conjure - AI CAD Control",
    "author": "Lautrek",
    "version": (0, 1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > Conjure",
    "description": "AI-powered CAD control system for Blender",
    "warning": "",
    "doc_url": "https://docs.conjure.lautrek.com/blender",
    "tracker_url": "https://github.com/lautrek/conjure/issues",
    "category": "3D View",
}

import bpy
from bpy.props import BoolProperty, EnumProperty, IntProperty, StringProperty

# Import submodules
from . import conjure


class ConjurePreferences(bpy.types.AddonPreferences):
    """Conjure add-on preferences."""

    bl_idname = __name__

    server_host: StringProperty(
        name="Server Host",
        default="127.0.0.1",
        description="Conjure server host address",
    )

    server_port: IntProperty(
        name="Server Port",
        default=9877,
        min=1024,
        max=65535,
        description="Conjure server port",
    )

    cloud_url: StringProperty(
        name="Cloud URL",
        default="wss://api.conjure.lautrek.com/ws",
        description="Conjure cloud WebSocket URL",
    )

    api_server_url: StringProperty(
        name="API Server URL",
        default="http://localhost:8000",
        description="Conjure API server URL for materials and simulations",
    )

    api_key: StringProperty(
        name="API Key",
        subtype="PASSWORD",
        description="Your Conjure API key for cloud features",
    )

    auto_connect: BoolProperty(
        name="Auto Connect",
        default=True,
        description="Automatically connect to server on startup",
    )

    workflow_mode: EnumProperty(
        name="Workflow Mode",
        items=[
            ("DESIGN", "Product Design", "Optimized for product designers"),
            ("ENGINEERING", "Engineering/Maker", "Optimized for engineers and makers"),
            ("ANIMATION", "Artist/Animation", "Optimized for artists and animators"),
        ],
        default="DESIGN",
        description="Workflow mode affects available tools and defaults",
    )

    def draw(self, context):
        layout = self.layout

        # Connection settings
        box = layout.box()
        box.label(text="Connection Settings", icon="LINKED")
        col = box.column(align=True)
        col.prop(self, "server_host")
        col.prop(self, "server_port")
        col.prop(self, "auto_connect")

        # Cloud settings
        box = layout.box()
        box.label(text="Cloud Settings", icon="WORLD")
        col = box.column(align=True)
        col.prop(self, "cloud_url")
        col.prop(self, "api_key")

        # Workflow
        box = layout.box()
        box.label(text="Workflow", icon="PREFERENCES")
        box.prop(self, "workflow_mode")


class ConjureSceneProperties(bpy.types.PropertyGroup):
    """Scene-level properties for Conjure state."""

    is_connected: BoolProperty(
        name="Connected",
        default=False,
        description="Whether connected to Conjure server",
    )

    adapter_id: StringProperty(
        name="Adapter ID",
        default="",
        description="Unique adapter ID for this session",
    )

    operations_used: IntProperty(
        name="Operations Used",
        default=0,
        description="Number of operations used this period",
    )

    operations_limit: IntProperty(
        name="Operations Limit",
        default=100,
        description="Maximum operations allowed this period",
    )

    subscription_tier: StringProperty(
        name="Tier",
        default="free",
        description="Current subscription tier",
    )

    server_status: StringProperty(
        name="Server Status",
        default="disconnected",
        description="Current server connection status",
    )

    # Material library properties
    materials_loaded: BoolProperty(
        name="Materials Loaded",
        default=False,
        description="Whether the material library has been loaded from server",
    )

    materials_count: IntProperty(
        name="Materials Count",
        default=0,
        description="Number of materials in the library",
    )

    material_category: EnumProperty(
        name="Category",
        items=[
            ("ALL", "All", "All material categories"),
            ("metal", "Metals", "Metal materials"),
            ("plastic", "Plastics", "Plastic materials"),
            ("composite", "Composites", "Composite materials"),
            ("ceramic", "Ceramics", "Ceramic materials"),
            ("elastomer", "Elastomers", "Rubber and elastomer materials"),
            ("wood", "Wood", "Wood materials"),
        ],
        default="ALL",
        description="Filter materials by category",
    )

    selected_material: StringProperty(
        name="Selected Material",
        default="",
        description="Currently selected engineering material ID",
    )


# Classes to register
classes = [
    ConjurePreferences,
    ConjureSceneProperties,
]


def register():
    """Register the add-on."""
    # Register classes
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register scene properties
    bpy.types.Scene.conjure = bpy.props.PointerProperty(type=ConjureSceneProperties)

    # Register submodules
    conjure.register()

    print("Conjure: Add-on registered successfully")


def unregister():
    """Unregister the add-on."""
    # Unregister submodules
    conjure.unregister()

    # Unregister scene properties
    del bpy.types.Scene.conjure

    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    print("Conjure: Add-on unregistered")


if __name__ == "__main__":
    register()
