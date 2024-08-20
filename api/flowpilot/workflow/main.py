import asyncio
import time
import weakref

from flowpilot.workflow.graph import GGraph, GraphExecutor
from flowpilot.workflow.node import GNode
from flowpilot.workflow.pin import EDirection, FPin
from flowpilot.workflow.utils import get_reverse_dependencies, topological_sort


class StartOperator(GNode):

    def _create_default_pins(self):
        pass

    async def execute(self) -> None:
        self.pins["output"].value = self.name
        await asyncio.sleep(1)
        print(f'{self.name}: Input(None), Output({self.pins["output"].value})')


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


if __name__ == "__main__":
    n1 = StartOperator("start")
    n2 = BashOperator("bash")
    n3 = PythonOperator("python1")
    n4 = PythonOperator("python2")
    n5 = EndOperator("end")

    n1.pins["output"].link_to(n2.pins["arg1"])

    n1.pins["output"].link_to(n3.pins["arg1"])
    n2.pins["output"].link_to(n3.pins["arg2"])

    n1.pins["output"].link_to(n4.pins["arg1"])
    n2.pins["output"].link_to(n4.pins["arg2"])

    n3.pins["output"].link_to(n5.pins["merge"])
    n4.pins["output"].link_to(n5.pins["merge"])

    nodes = [n1, n2, n3, n4, n5]

    # print(list(t2.get_dependencies()))
    g = GGraph("task", nodes)
    g.build()

    exe = GraphExecutor(g, parallel=True)
    exe.run_thread()
