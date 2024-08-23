import asyncio

from flowpilot.workflow.node import GNode
from flowpilot.workflow.nodes.factory import UNODE
from flowpilot.workflow.pin import EDirection, FPin, FPinType


@UNODE()
class HttpOperator(GNode):

    def _input_bindings(self) -> None:
        self.add_pin(
            FPin(name="arg1", direction=EDirection.INPUT, type=FPinType("dict"))
        )

    async def execute(self) -> None:
        pass
