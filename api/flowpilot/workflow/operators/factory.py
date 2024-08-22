from typing import Any, Optional, TypeVar

from flowpilot.common.registry import Registry
from flowpilot.workflow.node import GNode

T = TypeVar("T", bound="GNode")

OPERATOR_REGISTRY = Registry("OPERATOR")
OPERATOR_REGISTRY.__doc__ = """
Registry for operators, which extract feature maps from images

The registered object must be a callable that accepts two arguments:

1. A :class:`name`
2. A :class:`metadata`

Registered object must return instance of :class:`GNode`.
"""


def new_operator(operator_class: str, name: Optional[str] = None, *args, **kwargs) -> T:
    """
    Build a operator from `operator_class`.

    Returns:
        an instance of :class:`GNode`
    """

    operator = OPERATOR_REGISTRY.get(operator_class)(name, *args, **kwargs)
    assert isinstance(operator, T)
    return operator
