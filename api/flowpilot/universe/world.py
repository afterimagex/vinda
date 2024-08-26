import weakref
from dataclasses import dataclass

from flowpilot.universe import IEventableMixin, UObject, USimInstance
from flowpilot.universe.timer import WorldTimer


@dataclass
class FWorldContext:
    """
    FWorldContext
    """

    sim_instance: weakref.ReferenceType["USimInstance"] = None
    world: weakref.ReferenceType["UWorld"] = None


class UGameMode(UObject):
    """UScene"""

    def __init__(
        self,
    ) -> None:
        super().__init__()
        self._ctx = None

    def get_world(self) -> "UWorld":
        return self._ctx.world


class UWorld(UObject, IEventableMixin):
    """
    UWrold
    UWorld 是游戏世界的类，它包含了游戏中的所有实体（如Actor、Component等）。
    每个 UWorld 实例都代表了一个独立的游戏世界，可以包含多个关卡（Level）。
    UWorld 负责管理游戏世界中的物理、光照、AI等系统，以及处理游戏世界的更新和渲染。
    在Unreal Engine中，游戏世界是动态的，可以包含各种交互元素和逻辑。
    """

    def __init__(
        self,
    ) -> None:
        super().__init__()
        self.tickable = True
        self.timer = WorldTimer()
        self._ctx: FWorldContext = None
        self._coordinator = None
        self._game_mode = UGameMode()

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

    def update_actors_and_components(self, delta_time: float) -> None:
        """update actors and components"""
        pass

    async def tick(self, delta_time: float, tick_type):
        """tick"""
        self.timer.update(delta_time)
        # self._process_input(delta_time)
        # self._update_physics(delta_time)
        # self._update_ai(delta_time)
        # self._update_animation(delta_time)
        # self._update_actors_and_components(delta_time)
        # self._prepare_rendering(delta_time)
        # self._network_sync(delta_time)

    def get_sim_instance(self) -> USimInstance:
        return self._ctx.sim_instance()


# void UWorld::Tick(ELevelTick TickType, float DeltaTime)
# {
#     // 更新世界时间
#     UpdateWorldTime(TickType, DeltaTime);

#     // 处理输入
#     ProcessInput(DeltaTime);

#     // 更新物理
#     UpdatePhysics(DeltaTime);

#     // 更新AI
#     UpdateAI(DeltaTime);

#     // 更新动画
#     UpdateAnimation(DeltaTime);

#     // 更新所有Actor和Component
#     UpdateActorsAndComponents(DeltaTime);

#     // 准备渲染
#     PrepareRendering(DeltaTime);

#     // 网络同步
#     NetworkSync(DeltaTime);
# }
