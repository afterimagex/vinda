from flowpilot.workflow.nodes.base import BaseNode
from flowpilot.workflow.pin import Direction, Pin


class ExecPin(Pin):
    pass


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
        self.exec = ExecPin("exec")
        self.then = ExecPin("then", direction=Direction.OUTPUT)

        self.this = Pin("self")
        self.retv = Pin("return_value", direction=Direction.OUTPUT)

        self.func_name = None

    # async def execute(self) -> None:
    #     pass


class BranchNode(BaseNode):
    pass


if __name__ == "__main__":
    print("Hello World")
