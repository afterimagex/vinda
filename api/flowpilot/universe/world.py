import weakref
from dataclasses import dataclass
from typing import List, Optional

from flowpilot.universe.acotr import UObject


@dataclass
class FWorldContext:
    """
    FWorldContext
    """

    siminstance: weakref.ReferenceType["USimInstance"]
    world: weakref.ReferenceType["UWrold"]


class UWrold(UObject):
    """UWrold"""

    def __init__(
        self,
        name: Optional[str] = None,
    ) -> None:
        pass

    def tick(self, delta_time: float):
        """tick"""
        return super().tick()
