from flowpilot.workflow.nodes.base import BaseNode
from flowpilot.workflow.pin import Direction, Pin


class BlueprintGraph(BaseNode):
    pass


class EventGraph(BaseNode):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)


class EventNode(BaseNode):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)


class FunctionNode(BaseNode):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.exec = Pin()
        self.then = Pin(direction=Direction.OUTPUT)

        self.this = Pin()
        self.retv = Pin(direction=Direction.OUTPUT)

        self.func = None

    # async def execute(self) -> None:
    #     pass


class BranchNode(BaseNode):
    pass


if __name__ == "__main__":
    print("Hello World")
