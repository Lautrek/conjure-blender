"""
Physics operators for Conjure.

These operators manage rigid body, cloth, and fluid simulations in Blender.
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
# Rigid Body Operators
# =============================================================================


class CONJURE_OT_add_rigid_body(Operator):
    """Add rigid body physics to the selected object."""

    bl_idname = "conjure.add_rigid_body"
    bl_label = "Add Rigid Body"
    bl_description = "Add rigid body physics to the active object"
    bl_options = {"REGISTER", "UNDO"}

    body_type: EnumProperty(
        name="Type",
        items=[
            ("ACTIVE", "Active", "Object is affected by physics"),
            ("PASSIVE", "Passive", "Object is static, affects other objects"),
        ],
        default="ACTIVE",
        description="Rigid body type",
    )

    mass: FloatProperty(
        name="Mass",
        default=1.0,
        min=0.001,
        max=10000.0,
        description="Mass of the object in kg",
    )

    friction: FloatProperty(
        name="Friction",
        default=0.5,
        min=0.0,
        max=1.0,
        description="Surface friction coefficient",
    )

    restitution: FloatProperty(
        name="Bounciness",
        default=0.0,
        min=0.0,
        max=1.0,
        description="Bounciness of collisions",
    )

    collision_shape: EnumProperty(
        name="Shape",
        items=[
            ("BOX", "Box", "Use bounding box"),
            ("SPHERE", "Sphere", "Use bounding sphere"),
            ("CAPSULE", "Capsule", "Use capsule shape"),
            ("CYLINDER", "Cylinder", "Use cylinder shape"),
            ("CONE", "Cone", "Use cone shape"),
            ("CONVEX_HULL", "Convex Hull", "Use convex hull of mesh"),
            ("MESH", "Mesh", "Use mesh geometry (slowest)"),
        ],
        default="CONVEX_HULL",
        description="Collision shape to use",
    )

    use_margin: BoolProperty(
        name="Use Margin",
        default=False,
        description="Use collision margin",
    )

    collision_margin: FloatProperty(
        name="Margin",
        default=0.04,
        min=0.0,
        max=1.0,
        description="Collision margin in meters",
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "MESH"

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        server = get_server()

        if not server:
            # Direct Blender operation
            bpy.ops.rigidbody.object_add(type=self.body_type)
            rb = obj.rigid_body
            rb.mass = self.mass
            rb.friction = self.friction
            rb.restitution = self.restitution
            rb.collision_shape = self.collision_shape
            rb.use_margin = self.use_margin
            rb.collision_margin = self.collision_margin
            self.report({"INFO"}, f"Added rigid body to: {obj.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "add_rigid_body",
            {
                "object": obj.name,
                "type": self.body_type,
                "mass": self.mass,
                "friction": self.friction,
                "restitution": self.restitution,
                "collision_shape": self.collision_shape,
                "use_margin": self.use_margin,
                "collision_margin": self.collision_margin,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Added rigid body to: {obj.name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_remove_rigid_body(Operator):
    """Remove rigid body physics from the selected object."""

    bl_idname = "conjure.remove_rigid_body"
    bl_label = "Remove Rigid Body"
    bl_description = "Remove rigid body physics from the active object"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.rigid_body is not None

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        server = get_server()

        if not server:
            bpy.ops.rigidbody.object_remove()
            self.report({"INFO"}, f"Removed rigid body from: {obj.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "remove_rigid_body",
            {"object": obj.name},
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Removed rigid body from: {obj.name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}


class CONJURE_OT_rigid_body_world(Operator):
    """Configure rigid body world settings."""

    bl_idname = "conjure.rigid_body_world"
    bl_label = "Rigid Body World Settings"
    bl_description = "Configure the rigid body world simulation settings"
    bl_options = {"REGISTER", "UNDO"}

    gravity: FloatVectorProperty(
        name="Gravity",
        default=(0.0, 0.0, -9.81),
        subtype="ACCELERATION",
        description="World gravity vector",
    )

    time_scale: FloatProperty(
        name="Time Scale",
        default=1.0,
        min=0.0,
        max=100.0,
        description="Time scale for simulation",
    )

    substeps_per_frame: IntProperty(
        name="Substeps",
        default=10,
        min=1,
        max=1000,
        description="Number of simulation steps per frame",
    )

    solver_iterations: IntProperty(
        name="Solver Iterations",
        default=10,
        min=1,
        max=1000,
        description="Number of constraint solver iterations",
    )

    def execute(self, context):
        from ..engine import get_server

        scene = context.scene
        server = get_server()

        if not server:
            # Ensure rigid body world exists
            if scene.rigidbody_world is None:
                bpy.ops.rigidbody.world_add()

            rbw = scene.rigidbody_world
            rbw.time_scale = self.time_scale
            rbw.substeps_per_frame = self.substeps_per_frame
            rbw.solver_iterations = self.solver_iterations
            # Gravity is set on the scene
            scene.gravity = self.gravity
            self.report({"INFO"}, "Updated rigid body world settings")
            return {"FINISHED"}

        result = server.executor.execute(
            "configure_rigid_body_world",
            {
                "gravity": list(self.gravity),
                "time_scale": self.time_scale,
                "substeps_per_frame": self.substeps_per_frame,
                "solver_iterations": self.solver_iterations,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, "Updated rigid body world settings")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        # Initialize from current values if they exist
        scene = context.scene
        if scene.rigidbody_world:
            self.time_scale = scene.rigidbody_world.time_scale
            self.substeps_per_frame = scene.rigidbody_world.substeps_per_frame
            self.solver_iterations = scene.rigidbody_world.solver_iterations
        self.gravity = scene.gravity
        return context.window_manager.invoke_props_dialog(self)


# =============================================================================
# Cloth Simulation Operators
# =============================================================================


class CONJURE_OT_add_cloth(Operator):
    """Add cloth simulation to the selected object."""

    bl_idname = "conjure.add_cloth"
    bl_label = "Add Cloth"
    bl_description = "Add cloth simulation modifier to the active object"
    bl_options = {"REGISTER", "UNDO"}

    quality: IntProperty(
        name="Quality Steps",
        default=5,
        min=1,
        max=80,
        description="Quality of the simulation",
    )

    mass: FloatProperty(
        name="Vertex Mass",
        default=0.3,
        min=0.0,
        max=10.0,
        description="Mass of each vertex",
    )

    air_damping: FloatProperty(
        name="Air Damping",
        default=1.0,
        min=0.0,
        max=10.0,
        description="Air resistance",
    )

    tension_stiffness: FloatProperty(
        name="Tension",
        default=15.0,
        min=0.0,
        max=10000.0,
        description="Tension stiffness",
    )

    compression_stiffness: FloatProperty(
        name="Compression",
        default=15.0,
        min=0.0,
        max=10000.0,
        description="Compression stiffness",
    )

    bending_stiffness: FloatProperty(
        name="Bending",
        default=0.5,
        min=0.0,
        max=10000.0,
        description="Bending stiffness",
    )

    use_pressure: BoolProperty(
        name="Use Pressure",
        default=False,
        description="Apply internal pressure to cloth",
    )

    pressure: FloatProperty(
        name="Pressure",
        default=0.0,
        min=-10000.0,
        max=10000.0,
        description="Internal pressure",
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "MESH"

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        server = get_server()

        if not server:
            # Add cloth modifier
            cloth_mod = obj.modifiers.new(name="Cloth", type="CLOTH")
            cloth = cloth_mod.settings

            cloth.quality = self.quality
            cloth.mass = self.mass
            cloth.air_damping = self.air_damping
            cloth.tension_stiffness = self.tension_stiffness
            cloth.compression_stiffness = self.compression_stiffness
            cloth.bending_stiffness = self.bending_stiffness
            cloth.use_pressure = self.use_pressure
            cloth.uniform_pressure_force = self.pressure

            self.report({"INFO"}, f"Added cloth to: {obj.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "add_cloth",
            {
                "object": obj.name,
                "quality": self.quality,
                "mass": self.mass,
                "air_damping": self.air_damping,
                "tension_stiffness": self.tension_stiffness,
                "compression_stiffness": self.compression_stiffness,
                "bending_stiffness": self.bending_stiffness,
                "use_pressure": self.use_pressure,
                "pressure": self.pressure,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Added cloth to: {obj.name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_remove_cloth(Operator):
    """Remove cloth simulation from the selected object."""

    bl_idname = "conjure.remove_cloth"
    bl_label = "Remove Cloth"
    bl_description = "Remove cloth simulation modifier from the active object"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        return any(m.type == "CLOTH" for m in obj.modifiers)

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        server = get_server()

        if not server:
            for mod in obj.modifiers:
                if mod.type == "CLOTH":
                    obj.modifiers.remove(mod)
                    break
            self.report({"INFO"}, f"Removed cloth from: {obj.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "remove_cloth",
            {"object": obj.name},
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Removed cloth from: {obj.name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}


class CONJURE_OT_add_collision(Operator):
    """Add collision modifier to object for cloth/soft body interaction."""

    bl_idname = "conjure.add_collision"
    bl_label = "Add Collision"
    bl_description = "Add collision modifier for physics interaction"
    bl_options = {"REGISTER", "UNDO"}

    damping: FloatProperty(
        name="Damping",
        default=0.0,
        min=0.0,
        max=1.0,
        description="Amount of velocity lost on collision",
    )

    thickness_outer: FloatProperty(
        name="Outer Thickness",
        default=0.02,
        min=0.001,
        max=1.0,
        description="Outer collision boundary thickness",
    )

    friction: FloatProperty(
        name="Friction",
        default=0.0,
        min=0.0,
        max=1.0,
        description="Friction of surface",
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "MESH"

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        server = get_server()

        if not server:
            collision_mod = obj.modifiers.new(name="Collision", type="COLLISION")
            coll = collision_mod.settings
            coll.damping = self.damping
            coll.thickness_outer = self.thickness_outer
            coll.cloth_friction = self.friction
            self.report({"INFO"}, f"Added collision to: {obj.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "add_collision",
            {
                "object": obj.name,
                "damping": self.damping,
                "thickness_outer": self.thickness_outer,
                "friction": self.friction,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Added collision to: {obj.name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


# =============================================================================
# Fluid Simulation Operators
# =============================================================================


class CONJURE_OT_add_fluid_domain(Operator):
    """Create a fluid domain for simulation."""

    bl_idname = "conjure.add_fluid_domain"
    bl_label = "Add Fluid Domain"
    bl_description = "Add fluid domain modifier to the active object"
    bl_options = {"REGISTER", "UNDO"}

    domain_type: EnumProperty(
        name="Domain Type",
        items=[
            ("LIQUID", "Liquid", "Simulate liquid fluid"),
            ("GAS", "Gas", "Simulate gas/smoke/fire"),
        ],
        default="LIQUID",
        description="Type of fluid simulation",
    )

    resolution_max: IntProperty(
        name="Resolution",
        default=64,
        min=6,
        max=512,
        description="Maximum resolution divisions",
    )

    use_adaptive_domain: BoolProperty(
        name="Adaptive Domain",
        default=False,
        description="Use adaptive domain for efficiency",
    )

    timesteps_max: IntProperty(
        name="Max Timesteps",
        default=4,
        min=1,
        max=100,
        description="Maximum simulation timesteps per frame",
    )

    use_mesh: BoolProperty(
        name="Use Mesh",
        default=True,
        description="Generate mesh for liquid surface",
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "MESH"

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        server = get_server()

        if not server:
            fluid_mod = obj.modifiers.new(name="Fluid", type="FLUID")
            fluid_mod.fluid_type = "DOMAIN"

            domain = fluid_mod.domain_settings
            domain.domain_type = self.domain_type
            domain.resolution_max = self.resolution_max
            domain.use_adaptive_domain = self.use_adaptive_domain
            domain.timesteps_max = self.timesteps_max
            if self.domain_type == "LIQUID":
                domain.use_mesh = self.use_mesh

            self.report({"INFO"}, f"Added fluid domain to: {obj.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "add_fluid_domain",
            {
                "object": obj.name,
                "domain_type": self.domain_type,
                "resolution_max": self.resolution_max,
                "use_adaptive_domain": self.use_adaptive_domain,
                "timesteps_max": self.timesteps_max,
                "use_mesh": self.use_mesh,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Added fluid domain to: {obj.name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_add_fluid_flow(Operator):
    """Add fluid flow (source/inflow) to an object."""

    bl_idname = "conjure.add_fluid_flow"
    bl_label = "Add Fluid Flow"
    bl_description = "Add fluid flow/inflow modifier to the active object"
    bl_options = {"REGISTER", "UNDO"}

    flow_type: EnumProperty(
        name="Flow Type",
        items=[
            ("LIQUID", "Liquid", "Emit liquid"),
            ("SMOKE", "Smoke", "Emit smoke"),
            ("FIRE", "Fire", "Emit fire"),
            ("BOTH", "Fire + Smoke", "Emit both fire and smoke"),
        ],
        default="LIQUID",
        description="Type of flow emission",
    )

    flow_behavior: EnumProperty(
        name="Behavior",
        items=[
            ("INFLOW", "Inflow", "Continuously add fluid"),
            ("OUTFLOW", "Outflow", "Remove fluid"),
            ("GEOMETRY", "Geometry", "Use as obstacle/initial geometry"),
        ],
        default="INFLOW",
        description="Flow behavior type",
    )

    use_inflow: BoolProperty(
        name="Use Inflow",
        default=True,
        description="Enable fluid emission",
    )

    velocity_factor: FloatProperty(
        name="Initial Velocity",
        default=1.0,
        min=0.0,
        max=10.0,
        description="Initial velocity multiplier",
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "MESH"

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        server = get_server()

        if not server:
            fluid_mod = obj.modifiers.new(name="Fluid", type="FLUID")
            fluid_mod.fluid_type = "FLOW"

            flow = fluid_mod.flow_settings
            flow.flow_type = self.flow_type
            flow.flow_behavior = self.flow_behavior
            flow.use_inflow = self.use_inflow
            flow.velocity_factor = self.velocity_factor

            self.report({"INFO"}, f"Added fluid flow to: {obj.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "add_fluid_flow",
            {
                "object": obj.name,
                "flow_type": self.flow_type,
                "flow_behavior": self.flow_behavior,
                "use_inflow": self.use_inflow,
                "velocity_factor": self.velocity_factor,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Added fluid flow to: {obj.name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_add_fluid_effector(Operator):
    """Add fluid effector (obstacle/guide) to an object."""

    bl_idname = "conjure.add_fluid_effector"
    bl_label = "Add Fluid Effector"
    bl_description = "Add fluid effector/obstacle modifier to the active object"
    bl_options = {"REGISTER", "UNDO"}

    effector_type: EnumProperty(
        name="Effector Type",
        items=[
            ("COLLISION", "Collision", "Object blocks fluid"),
            ("GUIDE", "Guide", "Object guides fluid flow"),
        ],
        default="COLLISION",
        description="Type of effector",
    )

    use_effector: BoolProperty(
        name="Enabled",
        default=True,
        description="Enable this effector",
    )

    subframes: IntProperty(
        name="Subframes",
        default=0,
        min=0,
        max=200,
        description="Number of subframes for fast-moving objects",
    )

    surface_distance: FloatProperty(
        name="Surface Distance",
        default=0.0,
        min=0.0,
        max=10.0,
        description="Distance offset from surface",
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "MESH"

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        server = get_server()

        if not server:
            fluid_mod = obj.modifiers.new(name="Fluid", type="FLUID")
            fluid_mod.fluid_type = "EFFECTOR"

            effector = fluid_mod.effector_settings
            effector.effector_type = self.effector_type
            effector.use_effector = self.use_effector
            effector.subframes = self.subframes
            effector.surface_distance = self.surface_distance

            self.report({"INFO"}, f"Added fluid effector to: {obj.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "add_fluid_effector",
            {
                "object": obj.name,
                "effector_type": self.effector_type,
                "use_effector": self.use_effector,
                "subframes": self.subframes,
                "surface_distance": self.surface_distance,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Added fluid effector to: {obj.name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CONJURE_OT_bake_physics(Operator):
    """Bake physics simulation for selected object or scene."""

    bl_idname = "conjure.bake_physics"
    bl_label = "Bake Physics"
    bl_description = "Bake the physics simulation"
    bl_options = {"REGISTER", "UNDO"}

    physics_type: EnumProperty(
        name="Type",
        items=[
            ("ALL", "All Physics", "Bake all physics types"),
            ("RIGID_BODY", "Rigid Body", "Bake rigid body simulation"),
            ("CLOTH", "Cloth", "Bake cloth simulation"),
            ("FLUID", "Fluid", "Bake fluid simulation"),
        ],
        default="ALL",
        description="Type of physics to bake",
    )

    frame_start: IntProperty(
        name="Start Frame",
        default=1,
        min=0,
        description="Start frame for baking",
    )

    frame_end: IntProperty(
        name="End Frame",
        default=250,
        min=1,
        description="End frame for baking",
    )

    def execute(self, context):
        from ..engine import get_server

        server = get_server()

        if not server:
            # Set frame range
            context.scene.frame_start = self.frame_start
            context.scene.frame_end = self.frame_end

            if self.physics_type == "ALL" or self.physics_type == "RIGID_BODY":
                if context.scene.rigidbody_world:
                    bpy.ops.ptcache.bake_all(bake=True)

            if self.physics_type == "CLOTH":
                for obj in context.selected_objects:
                    for mod in obj.modifiers:
                        if mod.type == "CLOTH":
                            # Point cache bake for cloth
                            with context.temp_override(object=obj, point_cache=mod.point_cache):
                                bpy.ops.ptcache.bake(bake=True)

            self.report({"INFO"}, f"Baked {self.physics_type.lower()} simulation")
            return {"FINISHED"}

        result = server.executor.execute(
            "bake_physics",
            {
                "physics_type": self.physics_type,
                "frame_start": self.frame_start,
                "frame_end": self.frame_end,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Baked {self.physics_type.lower()} simulation")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        self.frame_start = context.scene.frame_start
        self.frame_end = context.scene.frame_end
        return context.window_manager.invoke_props_dialog(self)


# =============================================================================
# Soft Body Operator
# =============================================================================


class CONJURE_OT_add_soft_body(Operator):
    """Add soft body simulation to the selected object."""

    bl_idname = "conjure.add_soft_body"
    bl_label = "Add Soft Body"
    bl_description = "Add soft body simulation modifier to the active object"
    bl_options = {"REGISTER", "UNDO"}

    mass: FloatProperty(
        name="Mass",
        default=1.0,
        min=0.001,
        max=50.0,
        description="Mass of the soft body",
    )

    friction: FloatProperty(
        name="Friction",
        default=0.5,
        min=0.0,
        max=50.0,
        description="General friction coefficient",
    )

    speed: FloatProperty(
        name="Speed",
        default=1.0,
        min=0.01,
        max=100.0,
        description="Simulation speed multiplier",
    )

    goal_strength: FloatProperty(
        name="Goal Strength",
        default=0.7,
        min=0.0,
        max=1.0,
        description="Strength of goal (shape retention)",
    )

    goal_friction: FloatProperty(
        name="Goal Damping",
        default=0.5,
        min=0.0,
        max=50.0,
        description="Goal spring damping",
    )

    use_edges: BoolProperty(
        name="Use Edges",
        default=True,
        description="Use edges as springs",
    )

    pull: FloatProperty(
        name="Pull",
        default=0.9,
        min=0.0,
        max=0.999,
        description="Edge spring stiffness when longer than original",
    )

    push: FloatProperty(
        name="Push",
        default=0.9,
        min=0.0,
        max=0.999,
        description="Edge spring stiffness when shorter than original",
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == "MESH"

    def execute(self, context):
        from ..engine import get_server

        obj = context.active_object
        server = get_server()

        if not server:
            soft_mod = obj.modifiers.new(name="Softbody", type="SOFT_BODY")
            sb = soft_mod.settings

            sb.mass = self.mass
            sb.friction = self.friction
            sb.speed = self.speed
            sb.goal_default = self.goal_strength
            sb.goal_friction = self.goal_friction
            sb.use_edges = self.use_edges
            sb.pull = self.pull
            sb.push = self.push

            self.report({"INFO"}, f"Added soft body to: {obj.name}")
            return {"FINISHED"}

        result = server.executor.execute(
            "add_soft_body",
            {
                "object": obj.name,
                "mass": self.mass,
                "friction": self.friction,
                "speed": self.speed,
                "goal_strength": self.goal_strength,
                "goal_friction": self.goal_friction,
                "use_edges": self.use_edges,
                "pull": self.pull,
                "push": self.push,
            },
        )

        if result.get("status") == "success":
            self.report({"INFO"}, f"Added soft body to: {obj.name}")
            return {"FINISHED"}
        else:
            self.report({"ERROR"}, result.get("error", "Unknown error"))
            return {"CANCELLED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
