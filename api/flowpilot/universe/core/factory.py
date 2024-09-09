from abc import ABC
from typing import Optional, Type, TypeVar

from flowpilot.common.registry import Registry

__all__ = ["UClass", "UCLASS", "new_uclass"]

T = TypeVar("T", bound="UClass")

UCLASS_REGISTRY = Registry("UCLASS")
UCLASS_REGISTRY.__doc__ = """
Registry for UCLASS
"""


class UClass(ABC):
    category: Optional[str] = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"


def UCLASS(category: Optional[str] = None):

    def deco(uclass: Type[T]) -> Type[T]:
        assert issubclass(uclass, UClass)
        UCLASS_REGISTRY.register(uclass)
        uclass.category = category
        return uclass

    return deco


def new_uclass(class_name: str, *args, **kwargs) -> T:
    """
    Build a uclass from `class_name`.

    Returns:
        an instance of :class:`UObject`
    """
    uclass = UCLASS_REGISTRY.get(class_name)
    return uclass(*args, **kwargs)
