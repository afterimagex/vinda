from typing import List

from flowpilot.universe import UObject


class UEpisode(UObject):
    """UWrold"""

    def __init__(self) -> None:
        self._episodes: List[UEpisode] = []

    def tick(self, delta_time: float):
        """tick"""
        return super().tick()
