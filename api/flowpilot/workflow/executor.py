import asyncio
import threading

from flowpilot.workflow.graph import DagGraph


class GraphExecutor:
    def __init__(self, graph: DagGraph, parallel: bool = True):
        self._graph = graph
        self._parallel = parallel

    async def _parallel_execute(self):
        task_coroutines = {node.id: node.inner_execute() for node in self._graph.nodes}
        sorted_node_ids = list(task_coroutines.keys())
        completed_tasks = set()

        while sorted_node_ids:
            # 找出当前可以运行的任务（依赖项都已完成）
            runnable_tasks = [
                node_id
                for node_id in sorted_node_ids
                if all(
                    deps_node.id in completed_tasks
                    for deps_node in self._graph.get_node(node_id).get_dependencies()
                )
            ]

            if not runnable_tasks:
                raise ValueError("Cyclic dependency detected!")

            # 并发运行所有可运行的任务
            await asyncio.gather(
                *[task_coroutines[node_id] for node_id in runnable_tasks]
            )

            # 更新已完成的任务列表
            # todo: 节点执行失败，停止流程
            for node_id in runnable_tasks:
                sorted_node_ids.remove(node_id)
                completed_tasks.add(node_id)

    async def _sequential_execute(self):
        for node in self._graph.nodes:
            await node.execute()

    async def execute(self):
        if self._parallel:
            await self._parallel_execute()
        else:
            await self._sequential_execute()

    def run_thread(self):
        thread = threading.Thread(target=lambda: asyncio.run(self.execute()))
        thread.start()
        thread.join()


if __name__ == "__main__":
    import json
    from datetime import datetime
    from typing import Optional

    from flowpilot.workflow.nodes import UNODE, NodeBase
    from flowpilot.workflow.pin import Direction, Pin

    @UNODE()
    class MyNode(NodeBase):
        def __init__(self, name: Optional[str] = None) -> None:
            super().__init__(name)
            self.arg1 = Pin()
            self.arg2 = Pin()
            self.out1 = Pin(direction=Direction.OUTPUT)
            self.out2 = Pin(direction=Direction.OUTPUT)

        async def execute(self) -> None:
            date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            arg1_input_node = self.arg1.get_input_node(self.ctx)
            arg2_input_node = self.arg2.get_input_node(self.ctx)
            print(
                f"Node({self.name}) start at {date}, "
                f"arg1 from {arg1_input_node.name if arg1_input_node else 'null'}, value: {self.arg1.value}, "
                f"arg2 from {arg2_input_node.name if arg2_input_node else 'null'}, value: {self.arg2.value} "
            )
            await asyncio.sleep(1)
            self.out1.value = date
            self.out2.value = date

    n1 = MyNode("n1")
    n2 = MyNode("n2")
    n3 = MyNode("n3")
    n4 = MyNode("n4")
    n5 = MyNode("n5")

    n1.out1.link(n3.arg1)
    n1.out2.link(n4.arg1)

    n2.out1.link(n3.arg2)
    n2.out2.link(n4.arg2)

    n3.out1.link(n5.arg1)
    n3.out2.link(n5.arg2)

    # n4.out1.link(n5.arg1)
    # n4.out2.link(n5.arg2)

    dg = DagGraph(nodes=[n1, n2, n3, n4, n5])
    exe = GraphExecutor(dg)
    exe.run_thread()

    print(json.dumps(dg.dump(), indent=4))
