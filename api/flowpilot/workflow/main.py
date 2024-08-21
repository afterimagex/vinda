import asyncio
import time
import weakref

from flowpilot.workflow.executor import GraphExecutor
from flowpilot.workflow.graph import GGraph
from flowpilot.workflow.operators import OPERATOR_REGISTRY, build_operator

if __name__ == "__main__":
    print(OPERATOR_REGISTRY)
    n1 = build_operator("StartOperator", "start")
    n2 = build_operator("BashOperator", "bash")
    n3 = build_operator("PythonOperator", "python1")
    n4 = build_operator("PythonOperator", "python2")
    n5 = build_operator("EndOperator", "end")

    n1.pins["output"].link_to(n2.pins["arg1"])

    n1.pins["output"].link_to(n3.pins["arg1"])
    n2.pins["output"].link_to(n3.pins["arg2"])

    n1.pins["output"].link_to(n4.pins["arg1"])
    n2.pins["output"].link_to(n4.pins["arg2"])

    n3.pins["output"].link_to(n5.pins["merge"])
    n4.pins["output"].link_to(n5.pins["merge"])

    nodes = [n1, n2, n3, n4, n5]

    g = GGraph("task", nodes)
    g.build()

    exe = GraphExecutor(g, parallel=True)
    exe.run_thread()
