from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple, Union

from .event import EventMixin
from .factory import UCLASS
from .message import ListenerHandle, MessageSubsystem
from .object import UObject

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


@UCLASS(category="Component")
class UComponent(UObject):
    """
    UComponent 是可以附加到 UObject 的组件类。
    UComponent 具备 BeginPlay 和 Tick 功能，但需要设置 PrimaryComponentTick.bCanEverTick = true; 来启用 Tick。
    """

    name: Optional[str]

    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__()
        super().__setattr__(
            "name", f"{self.__class__.__name__}_{id(self)}" if name is None else name
        )
        super().__setattr__("_disallow_child_classes", ("AActor", "UComponent"))


@UCLASS(category="Component")
class UActorComponent(UComponent, EventMixin):
    """
    UActorComponent 是可以附加到 AActor 的组件类。
    UActorComponent 具备 BeginPlay 和 TickComponent 功能，但需要设置 PrimaryComponentTick.bCanEverTick = true; 来启用 Tick。
    """

    def __init__(self, name: Optional[str] = None) -> None:
        UComponent.__init__(self, name)
        EventMixin.__init__(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"


@UCLASS(category="Component")
class UMessageProcessorComponent(UActorComponent):
    _listener_handles: List[ListenerHandle]

    def __init__(self, name: str | None = None):
        super().__init__(name)
        self._tickable = False
        self._listener_handles = []

    def end_play(self, end_play_reason: str):
        while self._listener_handles:
            handle = self._listener_handles.pop()
            MessageSubsystem().unregister_listener_by_handle(handle)

    def add_listener_handle(self, handle: ListenerHandle):
        self._listener_handles.append(handle)
