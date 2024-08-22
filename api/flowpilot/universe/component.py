from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple, Union

from flowpilot.universe import FTickableObject, UObject


class UComponent(UObject):

    def __init__(self, name: Optional[str] = None):
        super().__init__(name)

    def __str__(self):
        return f"UComponent(name={self._name})"


class UActorComponent(FTickableObject):
    """
    UActorComponent 是可以附加到 AActor 的组件类。
    UActorComponent 具备 BeginPlay 和 TickComponent 功能，但需要设置 PrimaryComponentTick.bCanEverTick = true; 来启用 Tick。
    """

    bCanEverTick = False

    def _tick(self, delta_time: float) -> None:
        if self.bCanEverTick:
            self.tick(delta_time)

    def tick(self, delta_time):
        print(f"Ticking {self} with delta_time {delta_time}")
