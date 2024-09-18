import asyncio
import atexit
import weakref
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Union
from uuid import uuid4

from .actor import AActor
from .event import EventMixin
from .factory import UCLASS, UClass
from .object import UObject

# from flowpilot.universe.timer import WorldTimer

if TYPE_CHECKING:
    from .runtime import URuntime

__all__ = [
    "FWorldContext",
    "UWorld",
]


class FWorldContext:
    """
    WorldContext WorldContextObject
    """

    runtime: weakref.ReferenceType["URuntime"]
    world: weakref.ReferenceType["UWorld"]

    def __init__(self, world: "UWorld") -> None:
        self.world = weakref.ref(world)
        self._actors: Dict[str, weakref.ReferenceType[AActor]] = {}
        self._named_actors: Dict[str, weakref.ReferenceType[AActor]] = {}

    def add_actor(self, actor: AActor) -> None:
        if actor.id in self._actors:
            raise ValueError("actor id already exists")
        self._actors[actor.id] = weakref.ref(actor)
        self._named_actors[actor.name] = weakref.ref(actor)
        actor.ctx = self

    def remove_actor(self, actor: AActor) -> None:
        if actor.id not in self._actors:
            return
        del self._actors[actor.id]
        del self._named_actors[actor.name]

    def clear(self):
        self._actors.clear()

    def get_actor_by_name(self, name: str):
        return self._named_actors.get(name)


# class UGameMode(UObject):
#     """UScene"""

#     def __init__(
#         self,
#     ) -> None:
#         super().__init__()
#         self._ctx = None

#     def get_world(self) -> "UWorld":
#         return self._ctx.world


@dataclass
class WorldSettings:

    level_name: str


@UCLASS(category="ULevel")
class ULevel(UObject, EventMixin):
    """ActorContainer"""

    _ctx: FWorldContext
    _actors: List[AActor]
    world_settings: Dict[str, Any]

    def __init__(
        self,
        actors: Optional[Union[AActor, Iterable[AActor]]] = None,
    ) -> None:
        self._actors: List[AActor] = []
        atexit.register(self.destroy)

    def add_actor(self, actor: AActor) -> None:
        self._ctx.add_actor(actor)
        self._actors.append(actor)

    def add_actors(self, actors: Union[AActor, Iterable[AActor]]) -> None:
        if not actors:
            return
        if isinstance(actors, AActor):
            actors = [actors]
        for actor in actors:
            self.add_actor(actor)

    def remove_actor(self, actor: AActor) -> None:
        self._ctx.remove_actor(actor)
        self._actors.remove(actor)

    def destroy(self):
        for actor in self._actors:
            actor.destroy()


@UCLASS(category="World")
class UWorld(ULevel):
    """
    UWrold
    UWorld 是游戏世界的类，它包含了游戏中的所有实体（如Actor、Component等）。
    每个 UWorld 实例都代表了一个独立的游戏世界，可以包含多个关卡（Level）。
    UWorld 负责管理游戏世界中的物理、光照、AI等系统，以及处理游戏世界的更新和渲染。
    在Unreal Engine中，游戏世界是动态的，可以包含各种交互元素和逻辑。
    """

    def __init__(
        self,
        actors: Optional[Union[AActor, Iterable[AActor]]] = None,
    ) -> None:
        self.ctx = FWorldContext(self)

        if actors is not None:
            self.add_actors(actors)

    def tick(self, delta_time: float):
        for actor in self._actors:
            actor.on_begin_play()
        for actor in self._actors:
            actor.on_tick(delta_time)
        for actor in self._actors:
            actor.on_end_play("1")
        for actor in self._actors:
            actor.on_finally_destroy()

    # async def atick(self):
    #     await asyncio.gather(
    #         *[actor.abegin_play() for actor in self._actors if not actor.has_begun_play]
    #     )
    #     await asyncio.gather(
    #         *[actor.atick() for actor in self._actors if actor.tickable]
    #     )
    #     await asyncio.gather(
    #         *[
    #             actor.aend_play()
    #             for actor in self._actors
    #             if actor.tickable
    #             if actor.mark_destroy
    #         ]
    #     )

    # has_begun_play: bool

    # def __init__(
    #     self,
    # ) -> None:
    #     super().__init__()
    #     self.timer = WorldTimer()
    #     self._ctx: FWorldContext = None
    #     self._coordinator = None
    #     self._game_mode = UGameMode()

    #     self._objects = {}

    # def init(self) -> None:
    #     pass

    # def attach(
    #     self,
    #     world_context: FWorldContext,
    # ) -> None:
    #     """"""
    #     self._ctx = world_context
    #     self._ctx.world = weakref.ref(self)

    # def _module_call(self, method_name, *args, **kwargs):
    #     tasks = [
    #         getattr(child, method_name, self._noop)(*args, **kwargs)
    #         for _, child in self.modules()
    #     ]
    #     await asyncio.gather(*tasks)

    # def setup(self):
    #     pass

    # def update_actors_and_components(self, delta_time: float) -> None:
    #     """update actors and components"""
    #     pass

    # async def tick(self, delta_time: float, tick_type):
    #     """tick"""
    #     self.timer.update(delta_time)
    #     # self._process_input(delta_time)
    #     # self._update_physics(delta_time)
    #     # self._update_ai(delta_time)
    #     # self._update_animation(delta_time)
    #     # self._update_actors_and_components(delta_time)
    #     # self._prepare_rendering(delta_time)
    #     # self._network_sync(delta_time)

    # def get_sim_instance(self) -> USimInstance:
    #     return self._ctx.sim_instance()


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
