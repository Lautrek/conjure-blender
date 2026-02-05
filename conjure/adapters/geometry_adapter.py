"""
Geometry adapter for Conjure.

Handles geometry-specific operations and conversions.
"""

import math
from typing import Any, Dict, List, Optional, Tuple

import bpy
import mathutils


class GeometryAdapter:
    """Adapter for geometry operations."""

    @staticmethod
    def get_bounding_box(obj_name: str) -> Optional[Dict[str, List[float]]]:
        """Get world-space bounding box for an object."""
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            return None

        # Get world-space bounding box corners
        bbox = [obj.matrix_world @ mathutils.Vector(corner) for corner in obj.bound_box]

        return {
            "min": [min(v[i] for v in bbox) for i in range(3)],
            "max": [max(v[i] for v in bbox) for i in range(3)],
            "center": [(min(v[i] for v in bbox) + max(v[i] for v in bbox)) / 2 for i in range(3)],
            "dimensions": [max(v[i] for v in bbox) - min(v[i] for v in bbox) for i in range(3)],
        }

    @staticmethod
    def get_mesh_stats(obj_name: str) -> Optional[Dict[str, Any]]:
        """Get mesh statistics for an object."""
        obj = bpy.data.objects.get(obj_name)
        if not obj or obj.type != "MESH":
            return None

        mesh = obj.data

        # Calculate surface area (approximate)
        surface_area = 0.0
        for poly in mesh.polygons:
            surface_area += poly.area

        # Calculate volume (for closed meshes)
        # This is approximate and assumes watertight mesh
        volume = 0.0
        for poly in mesh.polygons:
            # Use signed volume of tetrahedron formed with origin
            v0 = mesh.vertices[poly.vertices[0]].co
            for i in range(1, len(poly.vertices) - 1):
                v1 = mesh.vertices[poly.vertices[i]].co
                v2 = mesh.vertices[poly.vertices[i + 1]].co
                volume += v0.dot(v1.cross(v2)) / 6.0

        return {
            "vertices": len(mesh.vertices),
            "edges": len(mesh.edges),
            "faces": len(mesh.polygons),
            "triangles": sum(len(p.vertices) - 2 for p in mesh.polygons),
            "surface_area": abs(surface_area),
            "volume": abs(volume),
            "has_custom_normals": mesh.has_custom_normals,
            "is_manifold": GeometryAdapter._is_manifold(mesh),
        }

    @staticmethod
    def _is_manifold(mesh) -> bool:
        """Check if mesh is manifold (simplified check)."""
        # Count edge usage
        edge_counts = {}
        for poly in mesh.polygons:
            verts = list(poly.vertices)
            for i in range(len(verts)):
                edge = tuple(sorted([verts[i], verts[(i + 1) % len(verts)]]))
                edge_counts[edge] = edge_counts.get(edge, 0) + 1

        # Each edge should be used exactly twice for manifold mesh
        return all(count == 2 for count in edge_counts.values())

    @staticmethod
    def calculate_center_of_mass(obj_name: str, density: float = 1.0) -> Optional[Dict[str, Any]]:
        """Calculate center of mass for an object."""
        obj = bpy.data.objects.get(obj_name)
        if not obj or obj.type != "MESH":
            return None

        mesh = obj.data
        matrix = obj.matrix_world

        # Calculate centroid (simplified - actual CoM requires volume integration)
        centroid = mathutils.Vector((0, 0, 0))
        total_weight = 0.0

        for poly in mesh.polygons:
            # Use polygon center weighted by area
            center = mathutils.Vector((0, 0, 0))
            for vid in poly.vertices:
                center += mesh.vertices[vid].co
            center /= len(poly.vertices)

            weight = poly.area
            centroid += center * weight
            total_weight += weight

        if total_weight > 0:
            centroid /= total_weight

        # Transform to world space
        world_centroid = matrix @ centroid

        # Get volume for mass calculation
        stats = GeometryAdapter.get_mesh_stats(obj_name)
        volume = stats["volume"] if stats else 0.0
        mass = volume * density

        return {
            "center_of_mass": list(world_centroid),
            "mass": mass,
            "volume": volume,
            "density": density,
        }

    @staticmethod
    def measure_distance(obj1_name: str, obj2_name: str, mode: str = "centers") -> Optional[Dict[str, Any]]:
        """Measure distance between two objects."""
        obj1 = bpy.data.objects.get(obj1_name)
        obj2 = bpy.data.objects.get(obj2_name)

        if not obj1 or not obj2:
            return None

        if mode == "centers":
            # Distance between object origins
            distance = (obj1.location - obj2.location).length
            point1 = list(obj1.location)
            point2 = list(obj2.location)

        elif mode == "bounds":
            # Closest distance between bounding boxes
            bbox1 = GeometryAdapter.get_bounding_box(obj1_name)
            bbox2 = GeometryAdapter.get_bounding_box(obj2_name)

            if not bbox1 or not bbox2:
                return None

            # Calculate closest points on bounding boxes
            point1 = [max(bbox1["min"][i], min(bbox2["center"][i], bbox1["max"][i])) for i in range(3)]
            point2 = [max(bbox2["min"][i], min(bbox1["center"][i], bbox2["max"][i])) for i in range(3)]
            distance = (mathutils.Vector(point1) - mathutils.Vector(point2)).length

        else:
            return {"error": f"Unknown mode: {mode}"}

        return {
            "distance": distance,
            "object1": obj1_name,
            "object2": obj2_name,
            "point1": point1,
            "point2": point2,
            "mode": mode,
        }
