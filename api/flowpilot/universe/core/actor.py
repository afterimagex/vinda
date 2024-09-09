from typing import TYPE_CHECKING, List, Optional

from .object import UObject

if TYPE_CHECKING:
    from .world import FWorldContext

__all__ = ["AActor"]


class AActor(UObject):
    """
    AActor 是 Unreal Engine 中具备 BeginPlay 和 Tick 等功能的最基础类。
    AActor 提供了丰富的生命周期管理功能，包括 BeginPlay、Tick、EndPlay 等。
    """

    ctx: Optional["FWorldContext"]
    name: Optional[str]
    tickable: bool
    has_begun_play: bool
    _mark_destroy: bool
    _components: List[str]

    def __init__(
        self,
        name: Optional[str] = None,
    ):
        super().__init__()
        super().__setattr__("ctx", None)
        super().__setattr__(
            "name", f"{self.__class__.__name__}_{id(self)}" if name is None else name
        )
        super().__setattr__("tickable", True)
        super().__setattr__("has_begun_play", False)
        super().__setattr__("_mark_destroy", False)
        super().__setattr__("_components", [])

    def begin_play(self):
        self.has_begun_play = True

    def end_play(self):
        pass

    def tick(self, delta_time: float):
        pass

    async def atick(self):
        pass

    async def abegin_play(self):
        pass

    async def aend_play(self):
        pass

    # async def tick(self, delta_time: float):
    #     for comp in self._components:
    #         comp.tick(delta_time)

    # async def begin_play(self):
    #     """on_begin_play"""

    #     tasks = [
    #         child.begin_play() for child in self.children() if not child.has_begun_play
    #     ]
    #     # if not self.has_begun_play:
    #     # tasks.append(self.begin_play_impl())
    #     if self.has_begun_play:
    #         return

    #     self.has_begun_play = True
    #     await asyncio.gather(*tasks)

    # async def begin_play(self):
    #     """on_begin_play"""
    #     await self._call_children("begin_play")

    # async def after_play(self):
    # """on_after_play"""
    #     await self._call_children("after_play")

    # async def begin_tick(self):
    #     await self._call_children("begin_tick")

    # async def tick(self, delta_time: float, event_type=None):
    #     await self._call_children("tick", delta_time)

    # async def after_tick(self):
    #     await self._call_children("after_tick")

    def destroy(self):
        """标记待销毁"""
        self._mark_destroy = True

    def finally_destroy(self):
        """销毁前最后一个回调"""
        if world := self.ctx.world():
            world.final_remove_actor(self)
