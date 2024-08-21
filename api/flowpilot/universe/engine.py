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

from flowpilot.universe import FWorldContext, UObject, UTimer


class UEngine(UObject):
    """UEngine"""

    def __init__(self, name: Optional[str] = None, timer_interval=0.016) -> None:
        """"""
        super().__init__(name)
        self._is_running = False
        self._tick_event = threading.Event()
        self._timer = UTimer(self._tick_event, interval=timer_interval)
        self._siminstance: USimInstance = None

    def _preinit(self) -> None:
        """"""
        pass

    def _create_default_object(self) -> None:
        """"""
        self._siminstance = USimInstance()

    def tick(self, delta_time: float) -> None:
        """"""
        pass

    def loop(self) -> None:
        """"""
        self._preinit()
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


class USimInstance:
    """USimInstance"""

    def __init__(self) -> None:
        """"""
        self._world: "UWrold" = UWrold()
        self._context: "FWorldContext" = FWorldContext(
            weakref.ref(self), weakref.ref(self._world)
        )


class UEpisode(UObject):
    pass
