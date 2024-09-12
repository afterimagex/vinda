from flowpilot.universe.world import UScene, UWorld


class RedQueenWorld(UWorld):
    def __init__(self) -> None:
        super().__init__()


class Main(UScene):
    def __init__(self):
        super().__init__()
        # 初始化场景
        self._actor1 = UActor()
        self._actor2 = UActor()

    async def tick(self):

        pass
