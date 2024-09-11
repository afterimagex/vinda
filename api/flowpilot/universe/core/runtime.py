import weakref
from typing import TYPE_CHECKING

from .factory import UCLASS, UClass

if TYPE_CHECKING:
    from .world import FWorldContext

__all__ = ["URuntime"]


@UCLASS(category="Runtime")
class URuntime(UClass):
    """
    physics simulation runtime
    USimInstance
    UGameInstance 是游戏实例的类，它代表了游戏的一个特定实例。
    每个游戏实例都可以有自己的配置、数据等，这些在游戏的多个关卡或会话之间保持不变。
    UGameInstance 允许开发者在游戏的不同部分之间共享数据，而不需要将这些数据存储在全局变量中。
    此外，UGameInstance 还提供了在游戏开始时和结束时执行代码的机会，以及处理游戏会话的保存和加载。
    """

    ctx: "FWorldContext"

    def __init__(self) -> None:
        """"""
        self.ctx: "FWorldContext" = None

    def attach(
        self,
        ctx: "FWorldContext",
    ) -> None:
        """"""
        self.ctx = ctx
        self.ctx.runtime = weakref.ref(self)

    def init(self):
        # self.init_subsystems()
        pass

    def tick(self, delta_time: float):
        pass
        # print(f"{self.__class__.__name__}tick", delta_time)

    def shutdown(self):
        pass
        # self.shutdown_subsystems()

    def start(self, delta_time: float) -> None:
        """"""
        pass

    def get_subsystem(self, subsystem_class: type[UClass]):
        pass


@UCLASS(category="Runtime")
class UDefaultRuntime(URuntime):
    pass
