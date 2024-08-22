import weakref
from dataclasses import dataclass
from typing import List, Optional

from flowpilot.universe import IEventableMixin, UEpisode, UObject, USimInstance


@dataclass
class FWorldContext:
    """
    FWorldContext
    """

    sim_instance: weakref.ReferenceType["USimInstance"] = None
    world: weakref.ReferenceType["UWorld"] = None


class UWorld(UObject, IEventableMixin):
    """
    UWrold
    UWorld 是游戏世界的类，它包含了游戏中的所有实体（如Actor、Component等）。
    每个 UWorld 实例都代表了一个独立的游戏世界，可以包含多个关卡（Level）。
    UWorld 负责管理游戏世界中的物理、光照、AI等系统，以及处理游戏世界的更新和渲染。
    在Unreal Engine中，游戏世界是动态的，可以包含各种交互元素和逻辑。
    """

    is_tickable = True

    def __init__(
        self,
        name: Optional[str] = None,
    ) -> None:
        super().__init__(name)
        self._ctx: FWorldContext = None
        self._coordinator = None
        self._episode: UEpisode = None

    def init(self) -> None:
        pass

    def attach(
        self,
        world_context: FWorldContext,
    ) -> None:
        """"""
        self._ctx = world_context
        self._ctx.world = weakref.ref(self)

    def setup(self):
        pass

    async def tick(self, delta_time: float):
        """tick"""

    def get_sim_instance(self) -> USimInstance:
        return self._ctx.sim_instance()
