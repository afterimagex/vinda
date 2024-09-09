from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple, Union

from flowpilot.universe import IEventableMixin, UObject

# class UComponentMeta(type):

#     def __new__(
#         cls, name: str, bases: Tuple[type], attrs: Dict[str, Any]
#     ) -> "UComponent":
#         if not hasattr(cls, "_components"):
#             # This is the first time UComponentMeta.__new__ has been called for this class.
#             # We need to create a new _components dict and register it on all subclasses of UComponent.
#             cls._components = {}
#         else:
#             pass
#             # UComponentMeta.__new__ has already been called for this class.
#         if UObject not in bases:
#             raise TypeError(f"{name} must inherit from UObject")
#         return super().__new__(cls, name, bases, attrs)


class UComponent(UObject):

    def __init__(self, name: Optional[str] = None):
        super().__init__(name)

    def __str__(self):
        return f"UComponent(name={self._name})"


class UActorComponent(UObject, IEventableMixin):
    """
    UActorComponent 是可以附加到 AActor 的组件类。
    UActorComponent 具备 BeginPlay 和 TickComponent 功能，但需要设置 PrimaryComponentTick.bCanEverTick = true; 来启用 Tick。
    """

    bCanEverTick = False

    def tick(self, delta_time: float) -> None:
        if self.bCanEverTick:
            self.tick(delta_time)

    # def tick(self, delta_time):
    #     print(f"Ticking {self} with delta_time {delta_time}")
