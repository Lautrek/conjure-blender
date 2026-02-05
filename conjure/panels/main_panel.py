"""
Main Conjure panel for Blender N-panel.

Provides the primary UI for Conjure functionality in the 3D View sidebar.
"""

import bpy
from bpy.types import Panel


class CONJURE_PT_main(Panel):
    """Main Conjure panel."""

    bl_label = "Conjure"
    bl_idname = "CONJURE_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Conjure"

    def draw(self, context):
        layout = self.layout
        props = context.scene.conjure

        # Connection status indicator
        row = layout.row()
        if props.is_connected:
            row.label(text="Connected", icon="CHECKMARK")
        else:
            row.label(text="Disconnected", icon="ERROR")

        # Quick actions
        layout.separator()
        layout.label(text="Quick Actions:")

        col = layout.column(align=True)
        col.operator("conjure.create_cube", icon="MESH_CUBE", text="Create Cube")
        col.operator("conjure.create_sphere", icon="MESH_UVSPHERE", text="Create Sphere")
        col.operator("conjure.create_cylinder", icon="MESH_CYLINDER", text="Create Cylinder")
        col.operator("conjure.create_cone", icon="MESH_CONE", text="Create Cone")

        layout.separator()

        col = layout.column(align=True)
        col.operator("conjure.get_state", icon="INFO", text="Get State")
        col.operator("conjure.list_objects", icon="OUTLINER", text="List Objects")


class CONJURE_PT_connection(Panel):
    """Connection settings sub-panel."""

    bl_label = "Connection"
    bl_idname = "CONJURE_PT_connection"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Conjure"
    bl_parent_id = "CONJURE_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        props = context.scene.conjure

        # Server status
        box = layout.box()
        col = box.column(align=True)

        row = col.row()
        row.label(text="Status:")
        if props.is_connected:
            row.label(text=props.server_status, icon="LINKED")
        else:
            row.label(text=props.server_status, icon="UNLINKED")

        if props.adapter_id:
            row = col.row()
            row.label(text="Adapter ID:")
            row.label(text=props.adapter_id[:16] + "...")

        # Connection buttons
        layout.separator()
        row = layout.row(align=True)
        row.operator("conjure.connect", icon="PLAY", text="Connect")
        row.operator("conjure.disconnect", icon="PAUSE", text="Disconnect")

        layout.operator("conjure.test_connection", icon="FILE_REFRESH", text="Test Connection")

        # Preferences link
        layout.separator()
        layout.operator(
            "preferences.addon_show",
            text="Open Preferences",
            icon="PREFERENCES",
        ).module = "conjure"


class CONJURE_PT_operations(Panel):
    """Operations sub-panel."""

    bl_label = "Operations"
    bl_idname = "CONJURE_PT_operations"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Conjure"
    bl_parent_id = "CONJURE_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        # Transform operations
        layout.label(text="Transforms:", icon="ORIENTATION_GLOBAL")
        col = layout.column(align=True)
        col.operator("conjure.move_object", icon="EMPTY_ARROWS", text="Move")
        col.operator("conjure.rotate_object", icon="DRIVER_ROTATIONAL_DIFFERENCE", text="Rotate")
        col.operator("conjure.scale_object", icon="FULLSCREEN_ENTER", text="Scale")

        # Modifier operations (placeholder)
        layout.separator()
        layout.label(text="Modifiers:", icon="MODIFIER")
        col = layout.column(align=True)
        col.enabled = False  # Placeholder
        col.operator("mesh.primitive_cube_add", text="Add Modifier...")
        col.operator("mesh.primitive_cube_add", text="Apply Modifier...")

        # Boolean operations (placeholder)
        layout.separator()
        layout.label(text="Booleans:", icon="MOD_BOOLEAN")
        col = layout.column(align=True)
        col.enabled = False  # Placeholder
        col.operator("mesh.primitive_cube_add", text="Union")
        col.operator("mesh.primitive_cube_add", text="Difference")
        col.operator("mesh.primitive_cube_add", text="Intersect")


class CONJURE_PT_metrics(Panel):
    """Usage metrics sub-panel."""

    bl_label = "Metrics"
    bl_idname = "CONJURE_PT_metrics"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Conjure"
    bl_parent_id = "CONJURE_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        props = context.scene.conjure

        # Usage stats
        box = layout.box()
        col = box.column(align=True)

        row = col.row()
        row.label(text="Tier:")
        row.label(text=props.subscription_tier.capitalize())

        row = col.row()
        row.label(text="Operations:")
        row.label(text=f"{props.operations_used} / {props.operations_limit}")

        # Progress bar
        if props.operations_limit > 0:
            progress = props.operations_used / props.operations_limit
            layout.progress(
                factor=min(progress, 1.0),
                type="BAR",
                text=f"{int(progress * 100)}% used",
            )

        # Simulation capabilities
        layout.separator()
        layout.label(text="Simulation Capabilities:", icon="PHYSICS")
        col = layout.column(align=True)

        row = col.row()
        row.label(text="Physics:")
        row.label(text="Supported", icon="CHECKMARK")

        row = col.row()
        row.label(text="Heat Transfer:")
        row.label(text="Server Only", icon="DOT")

        row = col.row()
        row.label(text="Structural:")
        row.label(text="Server Only", icon="DOT")


class CONJURE_PT_materials(Panel):
    """Engineering materials sub-panel."""

    bl_label = "Engineering Materials"
    bl_idname = "CONJURE_PT_materials"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Conjure"
    bl_parent_id = "CONJURE_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        props = context.scene.conjure

        # Material library status
        box = layout.box()
        col = box.column(align=True)

        row = col.row()
        row.label(text="Material Library", icon="MATERIAL")
        if props.materials_loaded:
            row.label(text=f"{props.materials_count} materials")
        else:
            row.label(text="Not loaded", icon="ERROR")

        # Refresh button
        layout.operator("conjure.refresh_materials", icon="FILE_REFRESH", text="Refresh Library")

        # Category filter
        layout.separator()
        layout.prop(props, "material_category", text="Category")

        # Material list (enum property would be dynamically populated)
        layout.prop(props, "selected_material", text="Material")

        # Selected object's material
        layout.separator()
        layout.label(text="Selected Object:", icon="OBJECT_DATA")

        obj = context.active_object
        if obj:
            box = layout.box()
            col = box.column(align=True)

            row = col.row()
            row.label(text=obj.name)

            # Check for assigned engineering material
            mat_id = obj.get("conjure_material_id")
            mat_name = obj.get("conjure_material_name")

            if mat_id:
                row = col.row()
                row.label(text="Material:")
                row.label(text=mat_name or mat_id)

                density = obj.get("conjure_density_kg_m3")
                if density:
                    row = col.row()
                    row.label(text="Density:")
                    row.label(text=f"{density:.0f} kg/m³")

                # Clear button
                layout.operator("conjure.clear_material", icon="X", text="Clear Material")
            else:
                col.label(text="No engineering material", icon="INFO")

            # Assign button
            layout.operator("conjure.assign_material", icon="IMPORT", text="Assign Selected Material")
        else:
            layout.label(text="No object selected", icon="INFO")

        # Material details (when material selected)
        layout.separator()
        layout.label(text="Material Properties:", icon="PROPERTIES")
        box = layout.box()
        col = box.column(align=True)

        # These would be populated from the selected material
        col.label(text="Select a material to view properties")


class CONJURE_PT_simulation(Panel):
    """Simulation sub-panel."""

    bl_label = "Simulation"
    bl_idname = "CONJURE_PT_simulation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Conjure"
    bl_parent_id = "CONJURE_PT_main"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        # Quick estimate section
        layout.label(text="Quick Estimates:", icon="PHYSICS")
        col = layout.column(align=True)
        col.operator("conjure.estimate_mass", icon="ORIENTATION_GLOBAL", text="Mass Properties")
        col.operator("conjure.estimate_beam", icon="MESH_PLANE", text="Beam Analysis")
        col.operator("conjure.estimate_thermal", icon="LIGHT_SUN", text="Thermal Analysis")

        # Standard simulation
        layout.separator()
        layout.label(text="Simulations:", icon="FORCE_FORCE")
        col = layout.column(align=True)
        col.operator("conjure.run_stress", icon="CON_SHRINKWRAP", text="Stress Analysis")
        col.operator("conjure.run_thermal", icon="LIGHT_SUN", text="Heat Transfer")
        col.operator("conjure.run_dynamic", icon="CURVE_PATH", text="Dynamic Analysis")

        # Note about server
        layout.separator()
        box = layout.box()
        box.scale_y = 0.8
        col = box.column(align=True)
        col.label(text="Simulations are processed by the", icon="INFO")
        col.label(text="Conjure server using the assigned")
        col.label(text="engineering materials.")
