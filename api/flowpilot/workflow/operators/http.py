import asyncio

from flowpilot.workflow.node import GNode
from flowpilot.workflow.operators.factory import OPERATOR_REGISTRY
from flowpilot.workflow.pin import EDirection, FPin, FPinType


@OPERATOR_REGISTRY.register()
class HttpOperator(GNode):

    def _input_bindings(self) -> None:
        self.add_pin(
            FPin(name="arg1", direction=EDirection.INPUT, type=FPinType("dict"))
        )
