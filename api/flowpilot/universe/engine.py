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

from flowpilot.universe import (
    FWorldContext,
    ITickableObject,
    UObject,
    USimInstance,
    UTimer,
    UWorld,
    new_uclass,
)


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
        self._context: FWorldContext = None
        self._sim_instance: USimInstance = None

    def _preinit(self) -> None:
        """"""
        pass

    def _init(self) -> None:
        if self._sim_instance is None:
            self._sim_instance = new_uclass("USimInstance", "DefaultSimInstance")
            self._sim_instance.init()
        self._load_world()
        for world in self._worlds:
            world.init()

    def _create_default_object(self) -> None:
        """"""
        self._context = FWorldContext()

    def _load_world(self) -> None:
        """"""
        self._worlds.append(new_uclass("UWorld", "DefaultWorld"))

    def _postinit(self) -> None:
        self._sim_instance.attach(self._context)
        for world in self._worlds:
            world.attach(self._context)
            world.setup()

    async def tick(self, delta_time: float) -> None:
        """"""
        await self._sim_instance.tick(delta_time)

        await asyncio.gather(
            *[
                world.has_begun_play()
                for world in self._worlds
                if not world.has_begun_play()
            ]
        )

        await asyncio.gather(*[world.on_begin_tick() for world in self._worlds])
        await asyncio.gather(*[world.tick() for world in self._worlds])
        await asyncio.gather(*[world.on_end_tick() for world in self._worlds])

    async def loop(self) -> None:
        """loop"""
        self._preinit()
        self._init()
        self._create_default_object()
        self._postinit()

        self._is_running = True
        self._timer.start()

        try:
            while self._is_running:
                self._tick_event.wait()  # Wait for the timer thread to notify
                self._tick_event.clear()
                await self.tick(
                    self._timer.delta_time
                )  # Assume fixed time step (e.g., 60 FPS)

            await asyncio.gather(*[world.on_after_play() for world in self._worlds])

        except Exception as e:  # pylint: disable=broad-exception-caught
            traceback.print_exception(e)

        finally:
            self._exit()

    def _exit(self):
        self._sim_instance.shutdown()

    def stop(self):
        self._is_running = False
        self._timer.stop()

    def run_thread(self):
        thread = threading.Thread(target=lambda: asyncio.run(self.loop()))
        thread.start()
        thread.join()
