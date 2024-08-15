import asyncio
import concurrent.futures
import functools
import json
import time
from abc import ABCMeta
from collections import defaultdict, deque
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import matplotlib.pyplot as plt
import networkx as nx
import yaml
from flowpilot.core.module import UObject


class Job:
    pass


class Callbacks:
    pass


class Chains:
    pass


class UTaskNode(UObject):
    pass


class Task(UTaskNode, metaclass=ABCMeta):
    def __init__(
        self,
        name: Optional[str] = None,
        deps: Optional[Set[str]] = None,
    ):
        super().__init__(name)

        self.input = None
        self.output = None

        if deps is None:
            self.dependencies = set()
        elif isinstance(deps, str):
            self.dependencies = {deps}
        elif isinstance(deps, list):
            self.dependencies = set(deps)
        else:
            self.dependencies = deps

    async def execute(self, *args, **kwargs):
        print(f"Running {self.name} with input {self.input}")
        await asyncio.sleep(1)
        self.output = f"+{self.name}.{self.input}"
        print(f"Completed {self.name} with output {self.output}")


class Sequential(Task):
    def __init__(
        self,
        name: Optional[str] = None,
        deps: Optional[Set[str]] = None,
        *,
        tasks: List[Task],
    ) -> None:
        super().__init__(name, deps)
        self._tasks = {task.name: task for task in tasks}

    def add_task(self, task: Task) -> None:
        if task.name in self._tasks:
            raise ValueError(f"Task {task.name} already exists.")
        self._tasks[task.name] = task

    async def execute(self, *args, **kwargs):
        for task in self._tasks.values():
            await task.execute(*args, **kwargs)


class Parallel(Task):
    def __init__(
        self,
        name: Optional[str] = None,
        deps: Optional[Set[str]] = None,
        *,
        tasks: List[Task],
    ) -> None:
        super().__init__(name, deps)
        self._tasks = {task.name: task for task in tasks}
        self._sorted_task_names, self._reverse_dependencies = self._topological_sort()

    def _topological_sort(self) -> Tuple[List[str], Dict[str, List[str]]]:
        sorted_tasks = []
        in_degree = {name: len(task.dependencies) for name, task in self._tasks.items()}
        reverse_dependencies = defaultdict(list)

        for name, task in self._tasks.items():
            for dep in task.dependencies:
                reverse_dependencies[dep].append(name)

        no_dependency_tasks = deque(
            [name for name, degree in in_degree.items() if degree == 0]
        )

        while no_dependency_tasks:
            current_task_name = no_dependency_tasks.popleft()
            sorted_tasks.append(current_task_name)

            for dependent_name in reverse_dependencies[current_task_name]:
                in_degree[dependent_name] -= 1
                if in_degree[dependent_name] == 0:
                    no_dependency_tasks.append(dependent_name)

        if len(sorted_tasks) != len(self._tasks):
            raise ValueError("Cyclic dependency detected!")

        return sorted_tasks, reverse_dependencies

    def add_task(self, task: Task) -> None:
        if task.name in self._tasks:
            raise ValueError(f"Task {task.name} already exists.")
        self._tasks[task.name] = task
        self._sorted_task_names, self._reverse_dependencies = self._topological_sort()

    async def execute(self, *args, **kwargs):
        sorted_task_names = self._sorted_task_names.copy()
        reverse_dependencies = self._reverse_dependencies

        # 初始化第一个任务的输入
        # if initial_input is not None:
        # self._tasks[sorted_task_names[0]].input = initial_input

        task_coroutines = {
            name: task.execute(*args, **kwargs) for name, task in self._tasks.items()
        }
        completed_tasks = set()

        while sorted_task_names:
            # 找出当前可以运行的任务（依赖项都已完成）
            runnable_tasks = [
                name
                for name in sorted_task_names
                if all(dep in completed_tasks for dep in self._tasks[name].dependencies)
            ]

            if not runnable_tasks:
                raise ValueError("Cyclic dependency detected!")

            # 并发运行所有可运行的任务
            await asyncio.gather(*[task_coroutines[name] for name in runnable_tasks])

            # 更新已完成的任务列表
            for name in runnable_tasks:
                sorted_task_names.remove(name)
                completed_tasks.add(name)

                # 更新后续任务的输入
                for dependent_name in reverse_dependencies[name]:
                    self._tasks[dependent_name].input = self._tasks[name].output


class ConditionalBranch(UTaskNode):
    def __init__(
        self,
        condition: Callable[[Any], bool],
        true_branch: UTaskNode,
        false_branch: UTaskNode,
    ):
        self._condition = condition
        self._true_branch = true_branch
        self._false_branch = false_branch

    async def execute(self):
        if self._condition(self._ctx):
            await self._true_branch.run()
        else:
            await self._false_branch.run()


class Workflow(UTaskNode):
    def __init__(self, tasks: List[UTaskNode]):
        self._tasks = {task.name: task for task in tasks}

    async def execute(self, initial_input):
        pass


# async def run_workflow(tasks, initial_input=None):
#     sorted_task_names, reverse_dependencies = topological_sort(tasks)

#     # 初始化第一个任务的输入
#     if initial_input is not None:
#         tasks[sorted_task_names[0]].input = initial_input

#     for task_name in sorted_task_names:
#         task = tasks[task_name]
#         await task.run()
#         for dependent_name in reverse_dependencies[task_name]:
#             tasks[dependent_name].input = task.output


# def plot_workflow(filename):
#     with open(filename, "r") as file:
#         workflow_dict = json.load(file)

#     G = nx.DiGraph()

#     for node in workflow_dict["nodes"]:
#         G.add_node(
#             node["id"], func=node["func"], input=node["input"], output=node["output"]
#         )

#     for edge in workflow_dict["edges"]:
#         G.add_edge(edge["source"], edge["target"])

#     pos = nx.spring_layout(G)  # 使用spring布局
#     labels = {node: f"{node}\n({data['func']})" for node, data in G.nodes(data=True)}
#     nx.draw(
#         G,
#         pos,
#         labels=labels,
#         with_labels=True,
#         node_size=3000,
#         node_color="lightblue",
#         font_size=10,
#         font_weight="bold",
#     )
#     plt.show()


async def runwf(wf):
    wf = [x.run("1") for x in wf]
    await asyncio.gather(*wf)


if __name__ == "__main__":
    # task_s = Task("S", func_a)
    # task_a = Task("A", func_a, deps=[task_s.name])
    # task_b = Task("B", func_b, deps=[task_a.name])
    # task_c = Task("C", func_c, deps=[task_a.name])
    # task_d = Task("D", func_d, deps=[task_b.name, task_c.name])

    # tasks = {
    #     task_s.name: task_s,
    #     task_a.name: task_a,
    #     task_b.name: task_b,
    #     task_c.name: task_c,
    #     task_d.name: task_d,
    # }

    tc = Sequential(
        tasks=[
            Parallel(
                tasks=[
                    Parallel(
                        "P1",
                        tasks=[
                            Task("P1.S"),
                            Task("P1.A", deps=["P1.S"]),
                            Task("P1.B", deps=["P1.A"]),
                            Task("P1.C", deps=["P1.A"]),
                            Task("P1.D", deps=["P1.B", "P1.C"]),
                        ],
                    ),
                    Parallel(
                        "P2",
                        deps=["P3"],
                        tasks=[
                            Task("P2.S"),
                            Task("P2.A", deps=["P2.S"]),
                            Task("P2.B", deps=["P2.A"]),
                            Task("P2.C", deps=["P2.A"]),
                            Task("P2.D", deps=["P2.B", "P2.C"]),
                        ],
                    ),
                    Parallel(
                        "P3",
                        deps=["P1"],
                        tasks=[
                            Task("P3.S"),
                            Task("P3.A", deps=["P3.S"]),
                            Task("P3.B", deps=["P3.A"]),
                            Task("P3.C", deps=["P3.A"]),
                            Task("P3.D", deps=["P3.B", "P3.C"]),
                        ],
                    ),
                ]
            ),
            Parallel(
                "P4",
                tasks=[
                    Task("P4.S"),
                    Task("P4.A", deps=["P4.S"]),
                    Task("P4.B", deps=["P4.A"]),
                    Task("P4.C", deps=["P4.A"]),
                    Task("P4.D", deps=["P4.B", "P4.C"]),
                ],
            ),
        ]
    )

    # tc = Parallel(
    #     tasks=[
    #         Parallel(
    #             "P1",
    #             tasks=[
    #                 Task("P1.S"),
    #                 Task("P1.A", deps=["P1.S"]),
    #                 Task("P1.B", deps=["P1.A"]),
    #                 Task("P1.C", deps=["P1.A"]),
    #                 Task("P1.D", deps=["P1.B", "P1.C"]),
    #             ],
    #         ),
    #         Parallel(
    #             "P2",
    #             deps=["P3"],
    #             tasks=[
    #                 Task("P2.S"),
    #                 Task("P2.A", deps=["P2.S"]),
    #                 Task("P2.B", deps=["P2.A"]),
    #                 Task("P2.C", deps=["P2.A"]),
    #                 Task("P2.D", deps=["P2.B", "P2.C"]),
    #             ],
    #         ),
    #         Parallel(
    #             "P3",
    #             tasks=[
    #                 Task("P3.S"),
    #                 Task("P3.A", deps=["P3.S"]),
    #                 Task("P3.B", deps=["P3.A"]),
    #                 Task("P3.C", deps=["P3.A"]),
    #                 Task("P3.D", deps=["P3.B", "P3.C"]),
    #             ],
    #         ),
    #     ]
    # )

    # tc = Parallel(
    #     "P1",
    #     tasks=[
    #         Task("S"),
    #         Task("A", deps=["S"]),
    #         Task("B", deps=["A"]),
    #         Task("C", deps=["A"]),
    #         Task("D", deps=["B", "C"]),
    #     ],
    # )

    # print(tc._sorted_task_names)
    # runwf(tc)
    # wf = Workflow()

    # asyncio.gather(*wf)
    asyncio.run(tc.execute(123))

    # 序列化工作流到文件
    # serialize_workflow_to_networkx_format(tasks, "workflow_networkx.json")

    # 从文件反序列化工作流
    # loaded_tasks = deserialize_workflow_from_networkx_format("workflow_networkx.json")

    # 运行事件循环
    # asyncio.run(run_workflow(tasks, initial_input="Initial Input"))

    # 绘制工作流图
    # plot_workflow("workflow_networkx.json")
