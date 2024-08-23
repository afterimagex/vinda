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


class GraphSpec(BaseModel):
    name: str
    nodes: list[dict]
    type: GraphType = GraphType.DAG


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
