from typing import List

# from flowpilot.universe import UObject


class UEpisodeManager:
    """UWrold"""

    def __init__(self) -> None:
        # self._episodes: List[UEpisodeManager] = []
        self._scenario = Scenario()

    def tick(self, delta_time: float):
        """tick"""
        pass


# ECS
class Scenario:
    """描述，属性，无方法"""

    pass
