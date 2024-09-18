import asyncio
import threading
import time
import traceback
from typing import TYPE_CHECKING

from .factory import new_uclass
from .world import UWorld

if TYPE_CHECKING:
    from .config import Config
    from .runtime import URuntime

__all__ = ["UEngine"]


class UTimer(threading.Thread):
    def __init__(self, tick_event, interval=0.016):
        super().__init__()
        self._tick_event = tick_event
        self._interval = interval
        self._running = False

    def pause(self):
        pass

    def resume(self):
        pass

    def run(self):
        self._running = True
        next_tick_time = time.perf_counter()
        while self._running:
            current_time = time.perf_counter()
            sleep_time = next_tick_time - current_time
            if sleep_time > 0:
                time.sleep(sleep_time)
            self._tick_event.set()
            next_tick_time += self._interval

    @property
    def delta_time(self) -> float:
        return self._interval

    def stop(self):
        self._running = False
        self.join()


class UEngine:
    """
    UEngine
    UEngine 是Unreal Engine的引擎实例的类。
    它代表了整个游戏引擎的单一实例，负责初始化、运行和清理游戏引擎。
    UEngine 提供了对游戏引擎全局状态的访问，比如配置设置、性能统计等。
    在大多数情况下，开发者不需要直接与 UEngine 交互，因为它是由引擎自动管理的。
    """

    runtime_instance: "URuntime"
    world: UWorld

    def __init__(self, cfg: "Config", world: UWorld) -> None:
        """"""
        self._cfg = cfg
        self._running = False
        self._tick_event = threading.Event()
        self._timer = UTimer(self._tick_event, interval=cfg.tick_interval)
        self._world = world

    def _create_default_object(self) -> None:
        """"""
        self.runtime_instance = new_uclass(self._cfg.runtime_class)

    def _init(self) -> None:
        self.runtime_instance.init()

    def _postinit(self) -> None:
        self.runtime_instance.attach(self._world.ctx)

    def tick(self, delta_time: float) -> None:
        self.runtime_instance.tick(delta_time)
        self._world.tick(delta_time)

    # async def atick(self, delta_time: float) -> None:
    #     """"""
    #     await self.runtime_instance.tick(delta_time)

    #     await asyncio.gather(
    #         *[
    #             world.begin_play()
    #             for world in self._worlds
    #             if not world.has_begun_play()
    #         ]
    #     )

    #     await asyncio.gather(*[world.begin_tick() for world in self._worlds])
    #     await asyncio.gather(*[world.tick() for world in self._worlds])
    #     await asyncio.gather(*[world.after_tick() for world in self._worlds])

    def loop_until(self) -> None:
        """loop"""
        self._create_default_object()
        self._init()
        self._postinit()

        self._running = True
        self._timer.start()

        try:
            while self._running:
                self._tick_event.wait()  # Wait for the timer thread to notify
                self._tick_event.clear()
                self.tick(
                    self._timer.delta_time
                )  # Assume fixed time step (e.g., 60 FPS)

            # await asyncio.gather(*[world.after_play() for world in self._worlds])

        except Exception as e:  # pylint: disable=broad-exception-caught
            traceback.print_exception(e)

        finally:
            self._exit()

    def _exit(self):
        self.runtime_instance.shutdown()

    def stop(self):
        self._running = False
        self._timer.stop()
