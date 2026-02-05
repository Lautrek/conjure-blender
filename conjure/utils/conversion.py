"""
Conversion utilities for Conjure.

Helper functions for converting between different data formats.
"""

import math
from typing import List, Tuple, Union

import mathutils


def degrees_to_radians(degrees: Union[float, List[float], Tuple[float, ...]]) -> Union[float, List[float]]:
    """Convert degrees to radians."""
    if isinstance(degrees, (list, tuple)):
        return [math.radians(d) for d in degrees]
    return math.radians(degrees)


def radians_to_degrees(radians: Union[float, List[float], Tuple[float, ...]]) -> Union[float, List[float]]:
    """Convert radians to degrees."""
    if isinstance(radians, (list, tuple)):
        return [math.degrees(r) for r in radians]
    return math.degrees(radians)


def vector_to_list(vector: mathutils.Vector) -> List[float]:
    """Convert mathutils.Vector to list."""
    return list(vector)


def list_to_vector(data: List[float]) -> mathutils.Vector:
    """Convert list to mathutils.Vector."""
    return mathutils.Vector(data)


def euler_to_list(euler: mathutils.Euler, as_degrees: bool = False) -> List[float]:
    """Convert mathutils.Euler to list."""
    if as_degrees:
        return [math.degrees(e) for e in euler]
    return list(euler)


def list_to_euler(data: List[float], from_degrees: bool = False, order: str = "XYZ") -> mathutils.Euler:
    """Convert list to mathutils.Euler."""
    if from_degrees:
        data = [math.radians(d) for d in data]
    return mathutils.Euler(data, order)


def matrix_to_list(matrix: mathutils.Matrix) -> List[List[float]]:
    """Convert mathutils.Matrix to nested list."""
    return [list(row) for row in matrix]


def list_to_matrix(data: List[List[float]]) -> mathutils.Matrix:
    """Convert nested list to mathutils.Matrix."""
    return mathutils.Matrix(data)
