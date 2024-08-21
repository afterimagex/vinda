import asyncio
import threading

from flowpilot.workflow.graph import GGraph


class GraphExecutor:
    def __init__(self, graph: GGraph, parallel: bool = True):
        self._graph = graph
        self._parallel = parallel

    async def _parallel_execute(self):

        sorted_node_names = self._graph.sorted_node_names.copy()

        task_coroutines = {
            name: node._execute() for name, node in self._graph.nodes.items()
        }

        completed_tasks = set()

        while sorted_node_names:
            # 找出当前可以运行的任务（依赖项都已完成）
            runnable_tasks = [
                name
                for name in sorted_node_names
                if all(
                    deps_node().name in completed_tasks
                    for deps_node in self._graph.nodes[name].get_dependencies()
                )
            ]

            if not runnable_tasks:
                raise ValueError("Cyclic dependency detected!")

            # 并发运行所有可运行的任务
            await asyncio.gather(*[task_coroutines[name] for name in runnable_tasks])

            # 更新已完成的任务列表
            for name in runnable_tasks:
                sorted_node_names.remove(name)
                completed_tasks.add(name)

    async def _sequential_execute(self):
        for name in self._graph._sorted_node_names:
            await self._graph.nodes[name].execute()

    async def execute(self):
        if self._parallel:
            await self._parallel_execute()
        else:
            await self._sequential_execute()

    def run_thread(self):
        thread = threading.Thread(target=lambda: asyncio.run(self.execute()))
        thread.start()
        thread.join()
