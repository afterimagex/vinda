from flowpilot.universe import UEpisode


class FairyEpisode(UEpisode):
    def __init__(self):
        super().__init__()

    def start(self, *args, **kwargs) -> None:
        print("Fairy is here!")
