import asyncio
import functools
import traceback
import weakref
from abc import ABC
from collections import OrderedDict, defaultdict, deque
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple, Union

from flowpilot.universe import FTickableObject, FWorldContext, UActorComponent, UObject


class AActor(FTickableObject):
    """
    AActor 是 Unreal Engine 中具备 BeginPlay 和 Tick 等功能的最基础类。
    AActor 提供了丰富的生命周期管理功能，包括 BeginPlay、Tick、EndPlay 等。
    """

    def __init__(
        self,
        name: Optional[str] = None,
        world_context: Optional["FWorldContext"] = None,
    ):
        super().__init__(name)
        self._ctx = world_context
        self._components: List["UActorComponent"] = []

    @property
    def name(self) -> str:
        return self._name

    def attach(self, world_context: FWorldContext) -> "UObject":
        self._ctx = world_context
        return self

    def tick(self, delta_time: float):
        for comp in self._components:
            comp.tick(delta_time)

    def setup(self):
        pass

    def on_begin_play(self):
        pass

    def on_after_play(self):
        pass

    def on_begin_tick(self):
        pass

    def on_after_tick(self):
        pass

    def on_destroy(self):
        pass

    def finally_destroy(self):
        pass
