import functools
from typing import Any, Optional, TypeVar

from flowpilot.common.registry import Registry
from flowpilot.universe.object import UObject

T = TypeVar("T", bound="UObject")

UCLASS_REGISTRY = Registry("UCLASS")
UCLASS_REGISTRY.__doc__ = """
Registry for UCLASS
"""


def UCLASS(category: Optional[str] = None):

    @functools.wraps()
    def deco(uclass: T) -> T:
        assert isinstance(uclass, T)
        UCLASS_REGISTRY.register(uclass)
        uclass.category = category
        return uclass

    return deco


def new_uclass(class_name: str, name: Optional[str] = None, *args, **kwargs) -> T:
    """
    Build a uclass from `class_name`.

    Returns:
        an instance of :class:`UObject`
    """

    uclass = UCLASS_REGISTRY.get(class_name)(name, *args, **kwargs)
    assert isinstance(uclass, T)
    return uclass
