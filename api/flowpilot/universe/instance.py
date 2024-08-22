import weakref
from typing import Optional

from flowpilot.universe import UCLASS, FWorldContext, ITickableObject, UWorld


@UCLASS(category="SimInstance")
class USimInstance(ITickableObject):
    """
    USimInstance
    UGameInstance 是游戏实例的类，它代表了游戏的一个特定实例。
    每个游戏实例都可以有自己的配置、数据等，这些在游戏的多个关卡或会话之间保持不变。
    UGameInstance 允许开发者在游戏的不同部分之间共享数据，而不需要将这些数据存储在全局变量中。
    此外，UGameInstance 还提供了在游戏开始时和结束时执行代码的机会，以及处理游戏会话的保存和加载。
    """

    def __init__(self, name: Optional[str] = None) -> None:
        """"""
        super().__init__(name)
        self._ctx: FWorldContext = None

    def attach(
        self,
        world_context: FWorldContext,
    ) -> None:
        """"""
        self._ctx = world_context
        self._ctx.sim_instance = weakref.ref(self)

    def init(self):
        # self.init_subsystems()
        pass

    def get_world(self) -> UWorld:
        return self._ctx.world()

    def shutdown(self):
        pass
        # self.shutdown_subsystems()

    async def start(self, delta_time: float) -> None:
        """"""
        pass
