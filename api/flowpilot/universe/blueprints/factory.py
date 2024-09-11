from abc import ABC
from typing import Optional, Type, TypeVar

from flowpilot.common.registry import Registry

__all__ = ["UBlueprint"]

T = TypeVar("T", bound="UBlueprint")

UBLUEPRINT_REGISTRY = Registry("UBLUEPRINT")
UBLUEPRINT_REGISTRY.__doc__ = """
Registry for UBLUEPRINT
"""


class UBlueprint(ABC):
    category: Optional[str] = None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"


# def UBLUEPRINT(category: Optional[str] = None):

#     def deco(uclass: Type[T]) -> Type[T]:
#         assert issubclass(uclass, UBlueprint)
#         UBLUEPRINT_REGISTRY.register(uclass)
#         uclass.category = category
#         return uclass

#     return deco


# def new_uclass(class_name: str, *args, **kwargs) -> T:
#     """
#     Build a uclass from `class_name`.

#     Returns:
#         an instance of :class:`UObject`
#     """
#     uclass = UBLUEPRINT_REGISTRY.get(class_name)
#     return uclass(*args, **kwargs)
