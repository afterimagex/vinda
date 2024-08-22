import asyncio
import functools
import threading
import time
import traceback
import weakref
from abc import ABC
from collections import OrderedDict, defaultdict, deque
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple, Union

from flowpilot.universe import FWorldContext, UObject, UTimer, UWorld


class UEngine:
    """
    UEngine
    UEngine 是Unreal Engine的引擎实例的类。
    它代表了整个游戏引擎的单一实例，负责初始化、运行和清理游戏引擎。
    UEngine 提供了对游戏引擎全局状态的访问，比如配置设置、性能统计等。
    在大多数情况下，开发者不需要直接与 UEngine 交互，因为它是由引擎自动管理的。
    """

    def __init__(self, name: Optional[str] = None, timer_interval=0.016) -> None:
        """"""
        super().__init__(name)
        self._is_running = False
        self._tick_event = threading.Event()
        self._timer = UTimer(self._tick_event, interval=timer_interval)
        self._worlds: List[UWorld] = []

    def _preinit(self) -> None:
        """"""
        pass

    def _init(self) -> None:
        pass

    def _create_default_object(self) -> None:
        """"""
        self._sim_instance = USimInstance()

        context = FWorldContext()
        self._sim_instance.attach(context)

        self._worlds.append(UWorld("DefaultWorld", self._sim_instance))
        self._worlds[0].attach(context)

    def tick(self, delta_time: float) -> None:
        """"""
        self._sim_instance.tick(delta_time)

    def loop(self) -> None:
        """"""
        self._preinit()
        self._init()
        self._create_default_object()
        self._is_running = True
        self._timer.start()
        try:
            while self._is_running:
                self._tick_event.wait()  # Wait for the timer thread to notify
                self._tick_event.clear()
                self.tick(
                    self._timer.delta_time
                )  # Assume fixed time step (e.g., 60 FPS)
        finally:
            self.stop()

    def stop(self):
        self._is_running = False
        self._timer.stop()


class USimInstance(UObject):
    """
    USimInstance
    UGameInstance 是游戏实例的类，它代表了游戏的一个特定实例。
    每个游戏实例都可以有自己的配置、数据等，这些在游戏的多个关卡或会话之间保持不变。
    UGameInstance 允许开发者在游戏的不同部分之间共享数据，而不需要将这些数据存储在全局变量中。
    此外，UGameInstance 还提供了在游戏开始时和结束时执行代码的机会，以及处理游戏会话的保存和加载。
    """

    def __init__(self) -> None:
        """"""
        super().__init__("SimInstance")

    def attach(
        self,
        world_context: FWorldContext,
    ) -> None:
        """"""
        self._ctx = world_context
        self._ctx.sim_instance = weakref.ref(self)

    def tick(self, delta_time: float) -> None:
        """"""
        pass
