import asyncio

from flowpilot.workflow.node import GNode
from flowpilot.workflow.operators.factory import OPERATOR_REGISTRY
from flowpilot.workflow.pin import EDirection, FPin


@OPERATOR_REGISTRY.register()
class StartOperator(GNode):

    def _create_default_pins(self):
        pass

    async def execute(self) -> None:
        self.pins["output"].value = self.name
        await asyncio.sleep(1)
        print(f'{self.name}: Input(None), Output({self.pins["output"].value})')


@OPERATOR_REGISTRY.register()
class EndOperator(GNode):
    def _create_default_pins(self):
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


@OPERATOR_REGISTRY.register()
class PythonOperator(GNode):

    def _create_default_pins(self):
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


@OPERATOR_REGISTRY.register()
class BashOperator(GNode):

    def _create_default_pins(self):
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
