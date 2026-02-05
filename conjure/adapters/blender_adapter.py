"""
Main Blender adapter for Conjure.

Provides the interface between Conjure commands and Blender operations.
"""

from typing import Any, Dict, List, Optional

import bpy


class BlenderAdapter:
    """Main adapter for Blender operations."""

    def __init__(self):
        self.geometry = None  # Lazy import to avoid circular deps

    @property
    def blender_version(self) -> str:
        """Get Blender version string."""
        return ".".join(str(v) for v in bpy.app.version)

    @property
    def scene(self):
        """Get active scene."""
        return bpy.context.scene

    @property
    def active_object(self):
        """Get active object."""
        return bpy.context.active_object

    def get_object(self, name: str):
        """Get object by name."""
        return bpy.data.objects.get(name)

    def get_mesh(self, name: str):
        """Get mesh by name."""
        return bpy.data.meshes.get(name)

    def get_material(self, name: str):
        """Get material by name."""
        return bpy.data.materials.get(name)

    def list_objects(self, obj_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all objects, optionally filtered by type."""
        objects = []
        for obj in bpy.context.scene.objects:
            if obj_type and obj.type != obj_type.upper():
                continue
            objects.append(
                {
                    "name": obj.name,
                    "type": obj.type,
                    "location": list(obj.location),
                    "visible": obj.visible_get(),
                }
            )
        return objects

    def select_object(self, name: str, add: bool = False) -> bool:
        """Select an object by name."""
        obj = self.get_object(name)
        if not obj:
            return False

        if not add:
            bpy.ops.object.select_all(action="DESELECT")

        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        return True

    def delete_object(self, name: str) -> bool:
        """Delete an object by name."""
        obj = self.get_object(name)
        if not obj:
            return False

        bpy.data.objects.remove(obj, do_unlink=True)
        return True

    def duplicate_object(self, name: str, new_name: Optional[str] = None, linked: bool = False):
        """Duplicate an object."""
        obj = self.get_object(name)
        if not obj:
            return None

        if linked:
            new_obj = obj.copy()
        else:
            new_obj = obj.copy()
            if obj.data:
                new_obj.data = obj.data.copy()

        if new_name:
            new_obj.name = new_name

        bpy.context.collection.objects.link(new_obj)
        return new_obj

    def export_mesh_data(self, obj_name: str) -> Optional[Dict[str, Any]]:
        """Export mesh data in UGF-compatible format."""
        obj = self.get_object(obj_name)
        if not obj or obj.type != "MESH":
            return None

        mesh = obj.data

        # Get vertex data
        vertices = []
        for v in mesh.vertices:
            vertices.extend(list(v.co))

        # Get face/index data
        indices = []
        for poly in mesh.polygons:
            # Triangulate quads and n-gons
            verts = list(poly.vertices)
            if len(verts) == 3:
                indices.extend(verts)
            elif len(verts) == 4:
                # Split quad into two triangles
                indices.extend([verts[0], verts[1], verts[2]])
                indices.extend([verts[0], verts[2], verts[3]])
            else:
                # Fan triangulation for n-gons
                for i in range(1, len(verts) - 1):
                    indices.extend([verts[0], verts[i], verts[i + 1]])

        return {
            "name": obj.name,
            "type": "mesh",
            "vertices": {
                "count": len(mesh.vertices),
                "stride": 3,
                "data": vertices,
            },
            "indices": {
                "count": len(indices),
                "data": indices,
            },
            "transform": {
                "location": list(obj.location),
                "rotation": list(obj.rotation_euler),
                "scale": list(obj.scale),
            },
        }
