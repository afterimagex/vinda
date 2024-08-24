import asyncio
import json
import time
import weakref
from enum import Enum

from flowpilot.workflow.executor import GraphExecutor
from flowpilot.workflow.graph import GGraph
from flowpilot.workflow.nodes import NODE_REGISTRY, new_node
from pydantic import BaseModel


class GraphType(Enum):
    DAG = "dag"
    LOOP = "loop"


class MyGraph(object):
    def __init__(self) -> None:
        self._name = ""

    def get_name(self):
        return self._name


class GraphSpec(BaseModel):
    name: str
    nodes: list[dict]
    type: GraphType = GraphType.DAG
    obj: MyGraph = MyGraph()


class Pin:

    @staticmethod
    def int():
        pass


class NodeBase:
    def __init__(self) -> None:
        super().__init__()
        self.input = pin.Container(
            pin.Int(),
            pin.Str(),
            pin.Float(),
            pin.List(),
            pin.Dict(),
        ).mark("input")
        self.output = pin.Container(
            pin.Int(),
            pin.Str(),
            pin.Float(),
            pin.List(),
            pin.Dict(),
        ).mark("output")

    def execute(self):
        val1 = self.input1.v()
        val2 = self.input2.v()


class MyGraph:
    def __init__(self) -> None:
        self.node1 = NodeBase()
        self.node2 = NodeBase()
        self.node3 = NodeBase()

    def connection(self):
        self.node1.output >> self.node2.input3
        self.node2.output >> self.node3.input2


if __name__ == "__main__":
    print(NODE_REGISTRY)

    n1 = new_node("StartOperator", "start")
    n2 = new_node("BashOperator", "bash")
    n3 = new_node("PythonOperator", "python1")
    n4 = new_node("PythonOperator", "python2")
    n5 = new_node("EndOperator", "end")

    n1.pins["output"].link_to(n2.pins["arg1"])

    n1.pins["output"].link_to(n3.pins["arg1"])
    n2.pins["output"].link_to(n3.pins["arg2"])

    n1.pins["output"].link_to(n4.pins["arg1"])
    n2.pins["output"].link_to(n4.pins["arg2"])

    n4.pins["output"].link_to(n5.pins["merge"])

    nodes = [n1, n2, n3, n4, n5]

    g = GGraph("task", nodes)
    g.build()

    s = g.serialize()
    # print(s)
    # print(json.dumps(s, indent=4))
    # exe = GraphExecutor(g, parallel=True)
    # exe.run_thread()

    gs = GraphSpec(name="test", nodes=[{"1": "1"}])

    print(gs.model_dump())
