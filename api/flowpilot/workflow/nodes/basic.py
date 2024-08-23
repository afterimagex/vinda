import asyncio

from flowpilot.workflow.node import GNode
from flowpilot.workflow.nodes.factory import UNODE
from flowpilot.workflow.pin import EDirection, FPin, FPinType


@UNODE()
class StartOperator(GNode):

    def _input_bindings(self):
        pass

    async def execute(self) -> None:
        inp = input("Please enter something: ")
        self.pins["output"].value = inp
        print(f'{self.name}: Input({inp}), Output({self.pins["output"].value})')


@UNODE()
class EndOperator(GNode):
    def _input_bindings(self):
        self.add_pin(
            FPin(
                name="merge",
                direction=EDirection.INPUT,
            )
        )

    async def execute(self):
        arg1 = self.pins["merge"].value
        self.pins["output"].value = "end"
        print(f'{self.name}: Input({arg1}), Output({self.pins["output"].value})')


@UNODE()
class PythonOperator(GNode):

    def _input_bindings(self):
        self.add_pin(
            FPin(
                name="arg1",
                direction=EDirection.INPUT,
            )
        )
        self.add_pin(
            FPin(
                name="arg2",
                direction=EDirection.INPUT,
            )
        )

    async def execute(self):
        arg1 = self.pins["arg1"].value
        arg2 = self.pins["arg2"].value
        self.pins["output"].value = self.name
        await asyncio.sleep(1)
        print(f'{self.name}: Input({arg1},{arg2}), Output({self.pins["output"].value})')


@UNODE()
class BashOperator(GNode):

    def _input_bindings(self):
        self.add_pin(
            FPin(
                name="arg1",
                direction=EDirection.INPUT,
            )
        )

    async def execute(self):
        arg1 = self.pins["arg1"].value
        self.pins["output"].value = self.name
        await asyncio.sleep(1)
        print(f'{self.name}: Input({arg1}), Output({self.pins["output"].value})')
