"""
Geometry Nodes adapter for Conjure.

Provides an interface for creating and manipulating Geometry Nodes
modifiers programmatically, enabling AI-driven procedural geometry.
"""

from typing import Any, Dict, List, Optional, Tuple

import bpy
from mathutils import Vector


class GeometryNodesAdapter:
    """Adapter for Blender Geometry Nodes operations."""

    # Common node type mappings
    NODE_TYPES = {
        # Input
        "object_info": "GeometryNodeObjectInfo",
        "collection_info": "GeometryNodeCollectionInfo",
        "value": "ShaderNodeValue",
        "vector": "FunctionNodeInputVector",
        "boolean": "FunctionNodeInputBool",
        "integer": "FunctionNodeInputInt",
        "string": "FunctionNodeInputString",
        "group_input": "NodeGroupInput",
        "group_output": "NodeGroupOutput",
        # Geometry
        "transform": "GeometryNodeTransform",
        "set_position": "GeometryNodeSetPosition",
        "join_geometry": "GeometryNodeJoinGeometry",
        "separate_geometry": "GeometryNodeSeparateGeometry",
        "bounding_box": "GeometryNodeBoundBox",
        "convex_hull": "GeometryNodeConvexHull",
        "merge_by_distance": "GeometryNodeMergeByDistance",
        # Mesh Primitives
        "mesh_circle": "GeometryNodeMeshCircle",
        "mesh_cone": "GeometryNodeMeshCone",
        "mesh_cube": "GeometryNodeMeshCube",
        "mesh_cylinder": "GeometryNodeMeshCylinder",
        "mesh_grid": "GeometryNodeMeshGrid",
        "mesh_ico_sphere": "GeometryNodeMeshIcoSphere",
        "mesh_line": "GeometryNodeMeshLine",
        "mesh_uv_sphere": "GeometryNodeMeshUVSphere",
        # Mesh Operations
        "extrude_mesh": "GeometryNodeExtrudeMesh",
        "flip_faces": "GeometryNodeFlipFaces",
        "mesh_boolean": "GeometryNodeMeshBoolean",
        "mesh_to_curve": "GeometryNodeMeshToCurve",
        "subdivide_mesh": "GeometryNodeSubdivideMesh",
        "subdivision_surface": "GeometryNodeSubdivisionSurface",
        "triangulate": "GeometryNodeTriangulate",
        # Curve Primitives
        "curve_arc": "GeometryNodeCurveArc",
        "curve_circle": "GeometryNodeCurvePrimitiveCircle",
        "curve_line": "GeometryNodeCurvePrimitiveLine",
        "curve_spiral": "GeometryNodeCurveSpiral",
        "bezier_segment": "GeometryNodeCurvePrimitiveBezierSegment",
        "quadrilateral": "GeometryNodeCurvePrimitiveQuadrilateral",
        # Curve Operations
        "curve_to_mesh": "GeometryNodeCurveToMesh",
        "curve_to_points": "GeometryNodeCurveToPoints",
        "fill_curve": "GeometryNodeFillCurve",
        "fillet_curve": "GeometryNodeFilletCurve",
        "resample_curve": "GeometryNodeResampleCurve",
        "reverse_curve": "GeometryNodeReverseCurve",
        "trim_curve": "GeometryNodeTrimCurve",
        # Instances
        "instance_on_points": "GeometryNodeInstanceOnPoints",
        "realize_instances": "GeometryNodeRealizeInstances",
        "rotate_instances": "GeometryNodeRotateInstances",
        "scale_instances": "GeometryNodeScaleInstances",
        "translate_instances": "GeometryNodeTranslateInstances",
        # Math
        "math": "ShaderNodeMath",
        "vector_math": "ShaderNodeVectorMath",
        "mix": "ShaderNodeMix",
        "clamp": "ShaderNodeClamp",
        "map_range": "ShaderNodeMapRange",
        "float_curve": "ShaderNodeFloatCurve",
        "combine_xyz": "ShaderNodeCombineXYZ",
        "separate_xyz": "ShaderNodeSeparateXYZ",
        # Attribute
        "store_named_attribute": "GeometryNodeStoreNamedAttribute",
        "named_attribute": "GeometryNodeInputNamedAttribute",
        "capture_attribute": "GeometryNodeCaptureAttribute",
        "attribute_statistic": "GeometryNodeAttributeStatistic",
        # Utilities
        "random_value": "FunctionNodeRandomValue",
        "compare": "FunctionNodeCompare",
        "switch": "GeometryNodeSwitch",
        "index": "GeometryNodeInputIndex",
        "position": "GeometryNodeInputPosition",
        "normal": "GeometryNodeInputNormal",
        "set_material": "GeometryNodeSetMaterial",
        # Volume
        "mesh_to_volume": "GeometryNodeMeshToVolume",
        "volume_to_mesh": "GeometryNodeVolumeToMesh",
        "volume_cube": "GeometryNodeVolumeCube",
    }

    def __init__(self):
        pass

    def create_node_group(
        self,
        name: str,
        object_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new Geometry Nodes modifier/group.

        Args:
            name: Name for the node group
            object_name: Optional object to add modifier to

        Returns:
            Dict with node_group and modifier info
        """
        # Create new node group
        node_group = bpy.data.node_groups.new(name=name, type="GeometryNodeTree")

        # Add default input/output nodes
        input_node = node_group.nodes.new("NodeGroupInput")
        input_node.location = (-300, 0)

        output_node = node_group.nodes.new("NodeGroupOutput")
        output_node.location = (300, 0)

        # Add geometry socket to input and output
        node_group.interface.new_socket(
            name="Geometry",
            in_out="INPUT",
            socket_type="NodeSocketGeometry",
        )
        node_group.interface.new_socket(
            name="Geometry",
            in_out="OUTPUT",
            socket_type="NodeSocketGeometry",
        )

        # Connect input to output by default
        node_group.links.new(
            input_node.outputs["Geometry"],
            output_node.inputs["Geometry"],
        )

        result = {
            "status": "success",
            "node_group": node_group.name,
            "nodes": ["Group Input", "Group Output"],
        }

        # Add modifier to object if specified
        if object_name:
            obj = bpy.data.objects.get(object_name)
            if obj:
                mod = obj.modifiers.new(name=name, type="NODES")
                mod.node_group = node_group
                result["modifier"] = mod.name
                result["object"] = obj.name

        return result

    def add_node(
        self,
        node_group_name: str,
        node_type: str,
        location: Optional[Tuple[float, float]] = None,
        name: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a node to a geometry node group.

        Args:
            node_group_name: Name of the target node group
            node_type: Type of node (use short name from NODE_TYPES)
            location: Node location (x, y)
            name: Optional custom name for the node
            settings: Node settings to apply

        Returns:
            Dict with node info
        """
        node_group = bpy.data.node_groups.get(node_group_name)
        if not node_group:
            return {"status": "error", "error": f"Node group '{node_group_name}' not found"}

        # Resolve node type
        bl_idname = self.NODE_TYPES.get(node_type.lower(), node_type)

        try:
            node = node_group.nodes.new(type=bl_idname)
        except RuntimeError as e:
            return {"status": "error", "error": f"Cannot create node type '{node_type}': {e}"}

        if name:
            node.name = name
            node.label = name

        if location:
            node.location = location

        # Apply settings
        if settings:
            for key, value in settings.items():
                if hasattr(node, key):
                    setattr(node, key, value)
                elif key in node.inputs:
                    node.inputs[key].default_value = value

        return {
            "status": "success",
            "node": node.name,
            "type": bl_idname,
            "location": list(node.location),
            "inputs": [s.name for s in node.inputs],
            "outputs": [s.name for s in node.outputs],
        }

    def connect_nodes(
        self,
        node_group_name: str,
        from_node: str,
        from_socket: str,
        to_node: str,
        to_socket: str,
    ) -> Dict[str, Any]:
        """
        Connect two nodes in a geometry node group.

        Args:
            node_group_name: Name of the target node group
            from_node: Source node name
            from_socket: Source socket name or index
            to_node: Target node name
            to_socket: Target socket name or index

        Returns:
            Dict with connection info
        """
        node_group = bpy.data.node_groups.get(node_group_name)
        if not node_group:
            return {"status": "error", "error": f"Node group '{node_group_name}' not found"}

        # Get nodes
        source = node_group.nodes.get(from_node)
        target = node_group.nodes.get(to_node)

        if not source:
            return {"status": "error", "error": f"Source node '{from_node}' not found"}
        if not target:
            return {"status": "error", "error": f"Target node '{to_node}' not found"}

        # Get sockets
        try:
            if isinstance(from_socket, int):
                output_socket = source.outputs[from_socket]
            else:
                output_socket = source.outputs[from_socket]
        except (KeyError, IndexError):
            return {"status": "error", "error": f"Output socket '{from_socket}' not found on '{from_node}'"}

        try:
            if isinstance(to_socket, int):
                input_socket = target.inputs[to_socket]
            else:
                input_socket = target.inputs[to_socket]
        except (KeyError, IndexError):
            return {"status": "error", "error": f"Input socket '{to_socket}' not found on '{to_node}'"}

        # Create link
        node_group.links.new(output_socket, input_socket)

        return {
            "status": "success",
            "from": f"{from_node}.{from_socket}",
            "to": f"{to_node}.{to_socket}",
        }

    def set_node_input(
        self,
        node_group_name: str,
        node_name: str,
        input_name: str,
        value: Any,
    ) -> Dict[str, Any]:
        """
        Set a node input value.

        Args:
            node_group_name: Name of the target node group
            node_name: Name of the node
            input_name: Name of the input socket
            value: Value to set

        Returns:
            Dict with result
        """
        node_group = bpy.data.node_groups.get(node_group_name)
        if not node_group:
            return {"status": "error", "error": f"Node group '{node_group_name}' not found"}

        node = node_group.nodes.get(node_name)
        if not node:
            return {"status": "error", "error": f"Node '{node_name}' not found"}

        try:
            node.inputs[input_name].default_value = value
        except (KeyError, TypeError) as e:
            return {"status": "error", "error": f"Cannot set input '{input_name}': {e}"}

        return {
            "status": "success",
            "node": node_name,
            "input": input_name,
            "value": str(value),
        }

    def add_group_input(
        self,
        node_group_name: str,
        name: str,
        socket_type: str,
        default_value: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Add an input to the node group interface.

        Args:
            node_group_name: Name of the target node group
            name: Name of the input
            socket_type: Socket type (float, vector, geometry, etc.)
            default_value: Default value for the input

        Returns:
            Dict with result
        """
        node_group = bpy.data.node_groups.get(node_group_name)
        if not node_group:
            return {"status": "error", "error": f"Node group '{node_group_name}' not found"}

        # Map common names to socket types
        socket_type_map = {
            "float": "NodeSocketFloat",
            "int": "NodeSocketInt",
            "vector": "NodeSocketVector",
            "bool": "NodeSocketBool",
            "geometry": "NodeSocketGeometry",
            "material": "NodeSocketMaterial",
            "object": "NodeSocketObject",
            "collection": "NodeSocketCollection",
            "string": "NodeSocketString",
            "color": "NodeSocketColor",
        }

        bl_socket_type = socket_type_map.get(socket_type.lower(), socket_type)

        socket = node_group.interface.new_socket(
            name=name,
            in_out="INPUT",
            socket_type=bl_socket_type,
        )

        if default_value is not None and hasattr(socket, "default_value"):
            socket.default_value = default_value

        return {
            "status": "success",
            "name": name,
            "socket_type": bl_socket_type,
        }

    def get_node_group_info(self, node_group_name: str) -> Dict[str, Any]:
        """
        Get information about a geometry node group.

        Args:
            node_group_name: Name of the node group

        Returns:
            Dict with node group info
        """
        node_group = bpy.data.node_groups.get(node_group_name)
        if not node_group:
            return {"status": "error", "error": f"Node group '{node_group_name}' not found"}

        nodes = []
        for node in node_group.nodes:
            nodes.append(
                {
                    "name": node.name,
                    "type": node.bl_idname,
                    "location": list(node.location),
                    "inputs": [s.name for s in node.inputs],
                    "outputs": [s.name for s in node.outputs],
                }
            )

        links = []
        for link in node_group.links:
            links.append(
                {
                    "from": f"{link.from_node.name}.{link.from_socket.name}",
                    "to": f"{link.to_node.name}.{link.to_socket.name}",
                }
            )

        # Get interface sockets
        inputs = []
        outputs = []
        for item in node_group.interface.items_tree:
            socket_info = {"name": item.name, "type": item.socket_type}
            if item.in_out == "INPUT":
                inputs.append(socket_info)
            else:
                outputs.append(socket_info)

        return {
            "status": "success",
            "name": node_group.name,
            "node_count": len(nodes),
            "nodes": nodes,
            "links": links,
            "inputs": inputs,
            "outputs": outputs,
        }

    def apply_node_group(
        self,
        object_name: str,
        node_group_name: str,
        modifier_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Apply a geometry node group to an object as a modifier.

        Args:
            object_name: Name of the target object
            node_group_name: Name of the node group to apply
            modifier_name: Optional name for the modifier

        Returns:
            Dict with result
        """
        obj = bpy.data.objects.get(object_name)
        if not obj:
            return {"status": "error", "error": f"Object '{object_name}' not found"}

        node_group = bpy.data.node_groups.get(node_group_name)
        if not node_group:
            return {"status": "error", "error": f"Node group '{node_group_name}' not found"}

        mod = obj.modifiers.new(
            name=modifier_name or node_group_name,
            type="NODES",
        )
        mod.node_group = node_group

        return {
            "status": "success",
            "object": obj.name,
            "modifier": mod.name,
            "node_group": node_group.name,
        }

    def create_procedural_grid(
        self,
        object_name: str,
        size_x: float = 10.0,
        size_y: float = 10.0,
        vertices_x: int = 10,
        vertices_y: int = 10,
        wave_amplitude: float = 0.0,
        wave_frequency: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Create a procedural grid with optional wave deformation.

        This is a convenience method that demonstrates geometry nodes.

        Args:
            object_name: Name for the created object
            size_x, size_y: Grid dimensions
            vertices_x, vertices_y: Vertex counts
            wave_amplitude: Wave height (0 for flat)
            wave_frequency: Wave frequency

        Returns:
            Dict with created object info
        """
        # Create empty mesh object
        mesh = bpy.data.meshes.new(object_name)
        obj = bpy.data.objects.new(object_name, mesh)
        bpy.context.collection.objects.link(obj)

        # Create node group
        result = self.create_node_group(f"{object_name}_Nodes", object_name)
        node_group = bpy.data.node_groups.get(result["node_group"])

        # Get existing input/output nodes
        node_group.nodes.get("Group Input")  # Ensure it exists
        output_node = node_group.nodes.get("Group Output")

        # Remove default connection
        for link in node_group.links:
            node_group.links.remove(link)

        # Add grid node
        grid = node_group.nodes.new("GeometryNodeMeshGrid")
        grid.location = (0, 0)
        grid.inputs["Size X"].default_value = size_x
        grid.inputs["Size Y"].default_value = size_y
        grid.inputs["Vertices X"].default_value = vertices_x
        grid.inputs["Vertices Y"].default_value = vertices_y

        if wave_amplitude > 0:
            # Add position node
            pos = node_group.nodes.new("GeometryNodeInputPosition")
            pos.location = (-200, -200)

            # Add separate XYZ
            sep = node_group.nodes.new("ShaderNodeSeparateXYZ")
            sep.location = (0, -200)

            # Add math for wave
            math1 = node_group.nodes.new("ShaderNodeMath")
            math1.operation = "MULTIPLY"
            math1.location = (200, -200)
            math1.inputs[1].default_value = wave_frequency

            math2 = node_group.nodes.new("ShaderNodeMath")
            math2.operation = "SINE"
            math2.location = (400, -200)

            math3 = node_group.nodes.new("ShaderNodeMath")
            math3.operation = "MULTIPLY"
            math3.location = (600, -200)
            math3.inputs[1].default_value = wave_amplitude

            # Combine for offset
            comb = node_group.nodes.new("ShaderNodeCombineXYZ")
            comb.location = (800, -200)

            # Set position
            set_pos = node_group.nodes.new("GeometryNodeSetPosition")
            set_pos.location = (200, 0)

            # Connect wave calculation
            node_group.links.new(pos.outputs["Position"], sep.inputs["Vector"])
            node_group.links.new(sep.outputs["X"], math1.inputs[0])
            node_group.links.new(math1.outputs["Value"], math2.inputs[0])
            node_group.links.new(math2.outputs["Value"], math3.inputs[0])
            node_group.links.new(math3.outputs["Value"], comb.inputs["Z"])

            # Connect main geometry flow
            node_group.links.new(grid.outputs["Mesh"], set_pos.inputs["Geometry"])
            node_group.links.new(comb.outputs["Vector"], set_pos.inputs["Offset"])
            node_group.links.new(set_pos.outputs["Geometry"], output_node.inputs["Geometry"])
        else:
            # Simple flat grid
            node_group.links.new(grid.outputs["Mesh"], output_node.inputs["Geometry"])

        return {
            "status": "success",
            "object": obj.name,
            "node_group": node_group.name,
            "size": [size_x, size_y],
            "vertices": [vertices_x, vertices_y],
            "has_wave": wave_amplitude > 0,
        }


# Singleton instance
_adapter = None


def get_nodes_adapter() -> GeometryNodesAdapter:
    """Get the geometry nodes adapter singleton."""
    global _adapter
    if _adapter is None:
        _adapter = GeometryNodesAdapter()
    return _adapter
