from flowpilot.universe.core.actor import AActor
from flowpilot.universe.core.component import UMessageProcessorComponent
from flowpilot.universe.core.message import MessageSubsystem


class ActorModel(AActor):

    def __init__(self, name: str | None = None):
        super().__init__(name)
        self._mpc = UMessageProcessorComponent()

    def begin_play(self):
        self._mpc.add_listener_handle(
            MessageSubsystem().register_listener(self.name, self.on_receive)
        )

    def on_receive(self, *args, **kwargs):
        print("on_message", *args, **kwargs)

    def tell(self):
        pass

    def ask(self):
        pass


if __name__ == "__main__":
    am = ActorModel()
    am.on_begin_play()
    print(am.__dict__)
    # am.on_end_play(1)
    # print(am.__dict__)

    MessageSubsystem().broadcast_message(am.name, "hello world")
