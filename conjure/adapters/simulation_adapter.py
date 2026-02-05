"""
Simulation Adapter for Conjure Blender Client.

Handles client-side simulation execution including:
- Physics simulations (rigid body, cloth, fluid, soft body)
- Dynamic property calculations (mass, volume, CoM, inertia)
- Geometry transfer to/from server via UGF format
"""

import json
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import bmesh
import bpy
from mathutils import Matrix, Vector


@dataclass
class DynamicProperties:
    """Dynamic properties calculated from geometry."""

    mass: float
    volume: float
    surface_area: float
    center_of_mass: Tuple[float, float, float]
    moments_of_inertia: Dict[str, float]  # Ixx, Iyy, Izz, Ixy, Ixz, Iyz
    principal_axes: List[List[float]]
    bounding_box: Dict[str, List[float]]


@dataclass
class SimulationResult:
    """Result from a simulation run."""

    status: str
    simulation_type: str
    frames_computed: int
    computation_time_ms: float
    results: Dict[str, Any]
    warnings: List[str]


class SimulationAdapter:
    """Adapter for executing simulations in Blender."""

    def __init__(self):
        """Initialize the simulation adapter."""
        # Default material densities (kg/m^3)
        self.material_densities = {
            "aluminum_6061": 2700,
            "steel_1018": 7870,
            "titanium_ti6al4v": 4430,
            "abs_plastic": 1050,
            "pla": 1240,
            "nylon_6": 1140,
            "copper_c110": 8940,
            "brass_c360": 8500,
            "wood_oak": 750,
            "glass": 2500,
            "concrete": 2400,
            "water": 1000,
            "air": 1.225,
        }

    # =========================================================================
    # Dynamic Properties Calculations
    # =========================================================================

    def calculate_dynamic_properties(
        self,
        object_name: str,
        material_id: Optional[str] = None,
        density: Optional[float] = None,
    ) -> DynamicProperties:
        """
        Calculate dynamic properties (mass, inertia, etc.) for an object.

        Args:
            object_name: Name of the Blender object
            material_id: Optional material ID from Conjure material library
            density: Optional explicit density in kg/m^3 (overrides material)

        Returns:
            DynamicProperties dataclass with all calculated values
        """
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object not found: {object_name}")

        if obj.type != "MESH":
            raise ValueError(f"Object must be a mesh, got: {obj.type}")

        # Get density
        if density is None:
            if material_id and material_id in self.material_densities:
                density = self.material_densities[material_id]
            else:
                density = 1000  # Default to water density

        # Create BMesh for calculations
        bm = bmesh.new()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        bm.from_mesh(obj_eval.data)
        bm.transform(obj.matrix_world)

        # Calculate volume using signed tetrahedron method
        volume = self._calculate_mesh_volume(bm)

        # Calculate surface area
        surface_area = sum(f.calc_area() for f in bm.faces)

        # Calculate center of mass (centroid for uniform density)
        center_of_mass = self._calculate_center_of_mass(bm, volume)

        # Calculate mass
        mass = volume * density

        # Calculate moments of inertia
        moments = self._calculate_moments_of_inertia(bm, center_of_mass, density)

        # Calculate bounding box
        bbox = self._calculate_bounding_box(obj)

        # Calculate principal axes
        principal_axes = self._calculate_principal_axes(moments)

        bm.free()

        return DynamicProperties(
            mass=mass,
            volume=volume,
            surface_area=surface_area,
            center_of_mass=tuple(center_of_mass),
            moments_of_inertia=moments,
            principal_axes=principal_axes,
            bounding_box=bbox,
        )

    def _calculate_mesh_volume(self, bm: bmesh.types.BMesh) -> float:
        """Calculate mesh volume using signed tetrahedron method."""
        volume = 0.0
        Vector((0, 0, 0))

        for face in bm.faces:
            if len(face.verts) < 3:
                continue

            # Triangulate the face for calculation
            v0 = face.verts[0].co
            for i in range(1, len(face.verts) - 1):
                v1 = face.verts[i].co
                v2 = face.verts[i + 1].co

                # Signed volume of tetrahedron with origin
                vol = v0.dot(v1.cross(v2)) / 6.0
                volume += vol

        return abs(volume)

    def _calculate_center_of_mass(self, bm: bmesh.types.BMesh, total_volume: float) -> Vector:
        """Calculate center of mass for uniform density mesh."""
        if total_volume < 1e-10:
            # Fallback to geometric centroid
            return sum((v.co for v in bm.verts), Vector()) / len(bm.verts)

        com = Vector((0, 0, 0))

        for face in bm.faces:
            if len(face.verts) < 3:
                continue

            v0 = face.verts[0].co
            for i in range(1, len(face.verts) - 1):
                v1 = face.verts[i].co
                v2 = face.verts[i + 1].co

                # Tetrahedron volume
                vol = v0.dot(v1.cross(v2)) / 6.0

                # Tetrahedron centroid (average of 4 vertices including origin)
                centroid = (v0 + v1 + v2) / 4.0

                com += centroid * vol

        return com / total_volume if total_volume > 0 else com

    def _calculate_moments_of_inertia(
        self,
        bm: bmesh.types.BMesh,
        center_of_mass: Vector,
        density: float,
    ) -> Dict[str, float]:
        """Calculate moments of inertia tensor about center of mass."""
        Ixx = Iyy = Izz = 0.0
        Ixy = Ixz = Iyz = 0.0

        for face in bm.faces:
            if len(face.verts) < 3:
                continue

            v0 = face.verts[0].co - center_of_mass
            for i in range(1, len(face.verts) - 1):
                v1 = face.verts[i].co - center_of_mass
                v2 = face.verts[i + 1].co - center_of_mass

                # Volume contribution
                vol = abs(v0.dot(v1.cross(v2)) / 6.0)

                # Centroid of tetrahedron
                c = (v0 + v1 + v2) / 4.0

                # Add contribution using parallel axis theorem
                dm = vol * density

                Ixx += dm * (c.y**2 + c.z**2)
                Iyy += dm * (c.x**2 + c.z**2)
                Izz += dm * (c.x**2 + c.y**2)
                Ixy -= dm * c.x * c.y
                Ixz -= dm * c.x * c.z
                Iyz -= dm * c.y * c.z

        return {
            "Ixx": Ixx,
            "Iyy": Iyy,
            "Izz": Izz,
            "Ixy": Ixy,
            "Ixz": Ixz,
            "Iyz": Iyz,
        }

    def _calculate_bounding_box(self, obj: bpy.types.Object) -> Dict[str, List[float]]:
        """Calculate world-space axis-aligned bounding box."""
        # Get world-space bounding box corners
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

        min_corner = Vector(
            (
                min(c.x for c in bbox_corners),
                min(c.y for c in bbox_corners),
                min(c.z for c in bbox_corners),
            )
        )
        max_corner = Vector(
            (
                max(c.x for c in bbox_corners),
                max(c.y for c in bbox_corners),
                max(c.z for c in bbox_corners),
            )
        )

        return {
            "min": list(min_corner),
            "max": list(max_corner),
            "size": list(max_corner - min_corner),
            "center": list((min_corner + max_corner) / 2),
        }

    def _calculate_principal_axes(self, moments: Dict[str, float]) -> List[List[float]]:
        """Calculate principal axes of inertia (eigenvectors of inertia tensor).

        Uses Jacobi eigenvalue algorithm for symmetric 3x3 matrix decomposition.

        Args:
            moments: Dictionary with Ixx, Iyy, Izz, Ixy, Ixz, Iyz components

        Returns:
            List of 3 eigenvectors (principal axes) as [x, y, z] lists,
            sorted by eigenvalue magnitude (largest first)
        """
        # Build symmetric inertia tensor matrix
        I = [
            [moments["Ixx"], moments["Ixy"], moments["Ixz"]],
            [moments["Ixy"], moments["Iyy"], moments["Iyz"]],
            [moments["Ixz"], moments["Iyz"], moments["Izz"]],
        ]

        # Initialize eigenvectors as identity matrix
        V = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]

        # Jacobi iteration for symmetric eigenvalue decomposition
        max_iterations = 50
        tolerance = 1e-10

        for _ in range(max_iterations):
            # Find largest off-diagonal element
            max_val = 0.0
            p, q = 0, 1
            for i in range(3):
                for j in range(i + 1, 3):
                    if abs(I[i][j]) > max_val:
                        max_val = abs(I[i][j])
                        p, q = i, j

            # Check convergence
            if max_val < tolerance:
                break

            # Calculate rotation angle
            if abs(I[p][p] - I[q][q]) < tolerance:
                theta = math.pi / 4.0
            else:
                theta = 0.5 * math.atan2(2.0 * I[p][q], I[p][p] - I[q][q])

            c = math.cos(theta)
            s = math.sin(theta)

            # Apply Jacobi rotation to I
            I_new = [row[:] for row in I]  # Deep copy

            I_new[p][p] = c * c * I[p][p] + s * s * I[q][q] - 2 * s * c * I[p][q]
            I_new[q][q] = s * s * I[p][p] + c * c * I[q][q] + 2 * s * c * I[p][q]
            I_new[p][q] = 0.0
            I_new[q][p] = 0.0

            for i in range(3):
                if i != p and i != q:
                    I_new[p][i] = c * I[p][i] - s * I[q][i]
                    I_new[i][p] = I_new[p][i]
                    I_new[q][i] = s * I[p][i] + c * I[q][i]
                    I_new[i][q] = I_new[q][i]

            I = I_new

            # Apply rotation to eigenvectors
            V_new = [row[:] for row in V]
            for i in range(3):
                V_new[i][p] = c * V[i][p] - s * V[i][q]
                V_new[i][q] = s * V[i][p] + c * V[i][q]
            V = V_new

        # Extract eigenvalues (diagonal) and sort by magnitude
        eigenvalues = [I[i][i] for i in range(3)]
        eigenvectors = [[V[j][i] for j in range(3)] for i in range(3)]

        # Sort by eigenvalue magnitude (largest first = primary axis)
        paired = list(zip(eigenvalues, eigenvectors))
        paired.sort(key=lambda x: abs(x[0]), reverse=True)

        # Return just the eigenvectors (principal axes)
        return [pair[1] for pair in paired]

    # =========================================================================
    # Physics Simulation
    # =========================================================================

    def run_physics_simulation(
        self,
        simulation_type: str,
        objects: List[str],
        frame_start: int = 1,
        frame_end: int = 250,
        substeps: int = 10,
        settings: Optional[Dict[str, Any]] = None,
    ) -> SimulationResult:
        """
        Run a physics simulation in Blender.

        Args:
            simulation_type: One of "rigid_body", "soft_body", "cloth", "fluid"
            objects: List of object names to simulate
            frame_start: Start frame
            frame_end: End frame
            substeps: Simulation substeps per frame
            settings: Additional simulation settings

        Returns:
            SimulationResult with status and results
        """
        import time

        start_time = time.time()
        warnings = []
        settings = settings or {}

        # Validate objects exist
        obj_refs = []
        for name in objects:
            obj = bpy.data.objects.get(name)
            if not obj:
                warnings.append(f"Object not found: {name}")
                continue
            obj_refs.append(obj)

        if not obj_refs:
            return SimulationResult(
                status="error",
                simulation_type=simulation_type,
                frames_computed=0,
                computation_time_ms=0,
                results={"error": "No valid objects found"},
                warnings=warnings,
            )

        scene = bpy.context.scene
        scene.frame_start = frame_start
        scene.frame_end = frame_end

        # Configure simulation based on type
        if simulation_type == "rigid_body":
            self._setup_rigid_body_simulation(obj_refs, substeps, settings)
        elif simulation_type == "soft_body":
            self._setup_soft_body_simulation(obj_refs, substeps, settings)
        elif simulation_type == "cloth":
            self._setup_cloth_simulation(obj_refs, substeps, settings)
        elif simulation_type == "fluid":
            self._setup_fluid_simulation(obj_refs, substeps, settings)
        else:
            return SimulationResult(
                status="error",
                simulation_type=simulation_type,
                frames_computed=0,
                computation_time_ms=0,
                results={"error": f"Unknown simulation type: {simulation_type}"},
                warnings=warnings,
            )

        # Bake the simulation
        try:
            if simulation_type == "rigid_body":
                bpy.ops.ptcache.bake_all(bake=True)
            else:
                # Bake individual object caches
                for obj in obj_refs:
                    for mod in obj.modifiers:
                        if hasattr(mod, "point_cache"):
                            with bpy.context.temp_override(object=obj, point_cache=mod.point_cache):
                                bpy.ops.ptcache.bake(bake=True)

            frames_computed = frame_end - frame_start + 1
            status = "success"

        except Exception as e:
            frames_computed = 0
            status = "error"
            warnings.append(str(e))

        computation_time = (time.time() - start_time) * 1000

        # Collect results
        results = self._collect_simulation_results(obj_refs, frame_end)

        return SimulationResult(
            status=status,
            simulation_type=simulation_type,
            frames_computed=frames_computed,
            computation_time_ms=computation_time,
            results=results,
            warnings=warnings,
        )

    def _setup_rigid_body_simulation(self, objects: List[bpy.types.Object], substeps: int, settings: Dict[str, Any]):
        """Configure rigid body simulation."""
        scene = bpy.context.scene

        # Ensure rigid body world exists
        if scene.rigidbody_world is None:
            bpy.ops.rigidbody.world_add()

        rbw = scene.rigidbody_world
        rbw.substeps_per_frame = substeps
        rbw.solver_iterations = settings.get("solver_iterations", 10)

        # Set gravity
        if "gravity" in settings:
            scene.gravity = Vector(settings["gravity"])

        # Configure objects
        for obj in objects:
            if obj.rigid_body is None:
                bpy.context.view_layer.objects.active = obj
                bpy.ops.rigidbody.object_add()

            rb = obj.rigid_body
            rb.mass = settings.get("mass", rb.mass)
            rb.friction = settings.get("friction", rb.friction)
            rb.restitution = settings.get("restitution", rb.restitution)

    def _setup_soft_body_simulation(self, objects: List[bpy.types.Object], substeps: int, settings: Dict[str, Any]):
        """Configure soft body simulation."""
        for obj in objects:
            # Check for existing soft body modifier
            sb_mod = None
            for mod in obj.modifiers:
                if mod.type == "SOFT_BODY":
                    sb_mod = mod
                    break

            if sb_mod is None:
                sb_mod = obj.modifiers.new(name="Softbody", type="SOFT_BODY")

            sb = sb_mod.settings
            sb.mass = settings.get("mass", 1.0)
            sb.friction = settings.get("friction", 0.5)
            sb.speed = settings.get("speed", 1.0)
            sb.goal_default = settings.get("goal_strength", 0.7)

    def _setup_cloth_simulation(self, objects: List[bpy.types.Object], substeps: int, settings: Dict[str, Any]):
        """Configure cloth simulation."""
        for obj in objects:
            # Check for existing cloth modifier
            cloth_mod = None
            for mod in obj.modifiers:
                if mod.type == "CLOTH":
                    cloth_mod = mod
                    break

            if cloth_mod is None:
                cloth_mod = obj.modifiers.new(name="Cloth", type="CLOTH")

            cloth = cloth_mod.settings
            cloth.quality = substeps
            cloth.mass = settings.get("mass", 0.3)
            cloth.air_damping = settings.get("air_damping", 1.0)
            cloth.tension_stiffness = settings.get("tension", 15.0)
            cloth.compression_stiffness = settings.get("compression", 15.0)
            cloth.bending_stiffness = settings.get("bending", 0.5)

    def _setup_fluid_simulation(self, objects: List[bpy.types.Object], substeps: int, settings: Dict[str, Any]):
        """Configure fluid simulation."""
        # Fluid simulation requires domain + flow objects
        # This is a simplified setup
        for obj in objects:
            fluid_mod = None
            for mod in obj.modifiers:
                if mod.type == "FLUID":
                    fluid_mod = mod
                    break

            if fluid_mod is None:
                fluid_mod = obj.modifiers.new(name="Fluid", type="FLUID")

            fluid_type = settings.get("fluid_type", "DOMAIN")
            fluid_mod.fluid_type = fluid_type

            if fluid_type == "DOMAIN":
                domain = fluid_mod.domain_settings
                domain.resolution_max = settings.get("resolution", 64)
                domain.timesteps_max = substeps

    def _collect_simulation_results(self, objects: List[bpy.types.Object], end_frame: int) -> Dict[str, Any]:
        """Collect simulation results at the end frame."""
        bpy.context.scene.frame_set(end_frame)

        results = {
            "final_frame": end_frame,
            "objects": {},
        }

        for obj in objects:
            obj_result = {
                "name": obj.name,
                "location": list(obj.location),
                "rotation": list(obj.rotation_euler),
                "velocity": [0, 0, 0],  # Would need velocity tracking
            }

            if obj.rigid_body:
                obj_result["is_active"] = obj.rigid_body.type == "ACTIVE"

            results["objects"][obj.name] = obj_result

        return results

    # =========================================================================
    # Geometry Transfer (UGF Format)
    # =========================================================================

    def export_geometry_ugf(self, object_name: str, include_materials: bool = False) -> Dict[str, Any]:
        """
        Export object geometry in Universal Geometry Format (UGF).

        UGF is a simplified geometry interchange format for Conjure.

        Returns:
            Dict with vertices, faces, normals, and optional materials
        """
        obj = bpy.data.objects.get(object_name)
        if not obj:
            raise ValueError(f"Object not found: {object_name}")

        if obj.type != "MESH":
            raise ValueError(f"Object must be a mesh, got: {obj.type}")

        # Get evaluated mesh (with modifiers applied)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        mesh = obj_eval.data

        # Ensure triangulated for simplicity
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces)

        # Collect vertices
        vertices = []
        for v in bm.verts:
            world_co = obj.matrix_world @ v.co
            vertices.append(list(world_co))

        # Collect faces (triangles)
        faces = []
        for f in bm.faces:
            faces.append([v.index for v in f.verts])

        # Collect normals
        normals = []
        for v in bm.verts:
            normals.append(list(v.normal))

        bm.free()

        ugf = {
            "format": "UGF",
            "version": "1.0",
            "object_name": object_name,
            "vertices": vertices,
            "faces": faces,
            "normals": normals,
            "transform": {
                "location": list(obj.location),
                "rotation": list(obj.rotation_euler),
                "scale": list(obj.scale),
            },
        }

        if include_materials and obj.data.materials:
            ugf["materials"] = []
            for mat in obj.data.materials:
                if mat:
                    mat_info = {
                        "name": mat.name,
                    }
                    # Get principled BSDF color if available
                    if mat.use_nodes:
                        for node in mat.node_tree.nodes:
                            if node.type == "BSDF_PRINCIPLED":
                                base_color = node.inputs["Base Color"].default_value
                                mat_info["base_color"] = list(base_color)[:3]
                                mat_info["metallic"] = node.inputs["Metallic"].default_value
                                mat_info["roughness"] = node.inputs["Roughness"].default_value
                                break
                    ugf["materials"].append(mat_info)

        return ugf

    def import_geometry_ugf(self, ugf_data: Dict[str, Any], object_name: Optional[str] = None) -> str:
        """
        Import geometry from Universal Geometry Format (UGF).

        Args:
            ugf_data: UGF formatted geometry data
            object_name: Override name for the created object

        Returns:
            Name of the created object
        """
        if ugf_data.get("format") != "UGF":
            raise ValueError("Invalid UGF format")

        vertices = ugf_data.get("vertices", [])
        faces = ugf_data.get("faces", [])
        name = object_name or ugf_data.get("object_name", "ImportedMesh")

        # Create mesh
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(vertices, [], faces)
        mesh.update()

        # Create object
        obj = bpy.data.objects.new(name, mesh)

        # Apply transform if provided
        if "transform" in ugf_data:
            t = ugf_data["transform"]
            if "location" in t:
                obj.location = Vector(t["location"])
            if "rotation" in t:
                obj.rotation_euler = t["rotation"]
            if "scale" in t:
                obj.scale = Vector(t["scale"])

        # Link to scene
        bpy.context.collection.objects.link(obj)

        return obj.name


# Singleton instance
_simulation_adapter: Optional[SimulationAdapter] = None


def get_simulation_adapter() -> SimulationAdapter:
    """Get the singleton simulation adapter instance."""
    global _simulation_adapter
    if _simulation_adapter is None:
        _simulation_adapter = SimulationAdapter()
    return _simulation_adapter
