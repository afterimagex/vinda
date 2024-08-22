from typing import List, Optional

from flowpilot.universe import FWorldContext, IEventableMixin, UActorComponent, UObject


class AActor(UObject, IEventableMixin):
    """
    AActor 是 Unreal Engine 中具备 BeginPlay 和 Tick 等功能的最基础类。
    AActor 提供了丰富的生命周期管理功能，包括 BeginPlay、Tick、EndPlay 等。
    """

    is_tickable = True

    def __init__(
        self,
        name: Optional[str] = None,
        world_context: Optional["FWorldContext"] = None,
    ):
        super().__init__(name)
        self._ctx = world_context
        self._components: List["UActorComponent"] = []

    @property
    def name(self) -> str:
        return self._name

    def attach(self, world_context: FWorldContext) -> "UObject":
        self._ctx = world_context
        return self

    async def tick(self, delta_time: float):
        for comp in self._components:
            comp.tick(delta_time)
