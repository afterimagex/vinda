from typing import Any, Optional, TypeVar

from flowpilot.common.registry import Registry
from flowpilot.workflow.node import GNode

T = TypeVar("T", bound="GNode")

NODE_REGISTRY = Registry("NODE")
NODE_REGISTRY.__doc__ = """
Registry for operators, which extract feature maps from images

The registered object must be a callable that accepts two arguments:

1. A :class:`name`
2. A :class:`metadata`

Registered object must return instance of :class:`GNode`.
"""


def UNODE(category: Optional[str] = None):

    def deco(node_class: T) -> T:
        NODE_REGISTRY.register(node_class)
        return node_class

    return deco


def new_node(node_class: str, name: Optional[str] = None, *args, **kwargs) -> T:
    """
    Build a operator from `node_class`.

    Returns:
        an instance of :class:`GNode`
    """

    node = NODE_REGISTRY.get(node_class)(name, *args, **kwargs)
    assert isinstance(node, GNode)
    return node
