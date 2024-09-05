"""
Module Summary:
This module provides a simple example to demonstrate how to
add a module-level docstring in the style commonly used in Apache projects.

Details:
The module includes a Direction enum, a Pin class, and a MyNode class.
"""

from .node import NodeBase
from .pin import Direction, Pin

__all__ = [k for k in globals().keys() if not k.startswith("_")]
