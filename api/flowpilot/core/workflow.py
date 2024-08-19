import asyncio
import concurrent.futures
import functools
import json
import time
import uuid
import weakref
from abc import ABCMeta, abstractmethod
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Iterator, List, Optional, Set, Tuple
from weakref import ReferenceType


class Job:
    pass


class Callbacks:
    pass


class Chains:
    pass


class Operator:
    pass


class Executor:
    pass


class GlobalContext:
    pass


class GraphSchema:
    pass


# G: graph相关基类
# F: 数据结构，一般用dataclass
# E: 枚举
# U: 用户自定义


class ENodeStatus(Enum):
    Initial = 1
    Running = 2
    Paused = 3
    Finished = 4
    Failed = 5
    Canceled = 6
    Unknown = 7


@dataclass
class FPinType:
    category: str
    sub_category_object: Optional[ReferenceType]


@dataclass
class FPin:

    class EDirection(Enum):
        INPUT = 1
        OUTPUT = 2

    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    owning_node: ReferenceType["GNode"] = None
    direction: EDirection = 1
    linked_to: weakref.WeakSet["FPin"] = field(default_factory=set)
    value: Any = None
    type: FPinType = None


class GPin:

    schema = FPin()

    def __init__(self, name: Optional[str] = None) -> None:
        self.schema.name = name if name else f"{self.__class__.__name__}_{id(self)}"
        self._links: Set["GPin"] = set()

    def modify(self) -> None:
        pass

    def linkto(self, other: "FPin") -> None:
        if other not in self._links:
            assert self not in other.linked_to
            # notify owning nodes about upcoming change
            self.modify()
            other.modify()
            self._links.add(other)
            other.linked_to.add(self)

    def breakto(self, other: "FPin") -> None:
        if other in self._links:
            assert self in other.linked_to
            # notify owning nodes about upcoming change
            self.modify()
            other.modify()
            self._links.remove(other)
            other.linked_to.remove(self)


@dataclass
class FNode:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    pins: Set[FPin] = field(default_factory=set)
    owning_graph: ReferenceType["GGraph"] = None
    status: ENodeStatus = ENodeStatus.Initial
    position: Tuple[float, float] = (0.0, 0.0)
    metadata: Dict[str, Any] = field(default_factory=dict)
    description: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class GNode(metaclass=ABCMeta):

    schema = FNode(description="A simple tutorial User Interface for Nodes.")

    def __init__(
        self,
        name: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        self._ctx: dict = None
        self.schema.name = name if name else f"{self.__class__.__name__}_{id(self)}"
        self.schema.metadata.update(metadata if metadata else {})
        self.pins = self._allocate_default_pins()

    def _allocate_default_pins(self):
        """在 Node 实例化时自动调用，负责分配一个 Node 中的默认 Pins。"""
        self.allocate_default_pins()
        return {pin.name: pin for pin in self.schema.pins}

    @abstractmethod
    def allocate_default_pins(self):
        pass

    def _autowire_new_node(self, weak_pin: ReferenceType[FPin]):
        """用于在创建新 Node 后，自动将其与指定的 Pin 连接。如果需要，应在创建新 Node 后调用。"""
        pass

    @property
    def name(self) -> str:
        return self.schema.name

    def build(self, _ctx: dict) -> None:
        self._ctx = _ctx

    # def get_dependencies(self) -> Iterator[FPin]:
    #     return filter(
    #         lambda pin: pin.direction == FPin.EDirection.INPUT, self._pins.values()
    #     )

    @staticmethod
    def create_unique_pin_name():
        pass

    async def _execute(self):
        assert self._ctx is not None, "Context is not built yet."
        await self.execute()

    @abstractmethod
    async def execute(self) -> None:
        pass


@dataclass
class FGraph:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    connections: List = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def try_create_connection(self, pa: FPin, pb: FPin) -> None:
        if self.can_create_connection(pa, pb):
            pa.linkto(pb)

    def can_create_connection(self, pa: FPin, pb: FPin) -> bool:
        return True


class GGraph:

    schema = FGraph(description="A simple tutorial User Interface for Graphs.")

    def __init__(self, nodes: List[GNode]) -> None:
        self._nodes = {node.name: node for node in nodes}
        assert self._inputs_binding_check()
        self._sorted_node_names, self._reverse_dependencies = self._topological_sort()
        self._graph_ctx = {"outputs": {}}
        self._schema = GraphSchema()

    def build(self) -> None:
        for node in self._nodes.values():
            node.build(self._graph_ctx)

    def _inputs_binding_check(self) -> bool:
        # for node in self._nodes.values():
        #     for input_binding in node._model.inputs:
        #         if input_binding.id not in self._nodes:
        #             raise ValueError(
        #                 f"Input '{input_binding.id}' for node '{node.name}' does not exist."
        #             )
        return True

    def serialize(self) -> dict:
        return {node.name: node.serialize() for node in self._nodes.values()}

    def deserialize(self, data: dict) -> None:
        for node_name, node_data in data.items():
            if node_name in self._nodes:
                self._nodes[node_name].deserialize(node_data)

    def _topological_sort(self) -> Tuple[List[str], Dict[str, List[str]]]:
        # todo: 抽取，并满足单一职能原则
        sorted_nodes = []
        in_degree = {
            name: len(
                node.get_pins(lambda _, pin: pin.direction == FPin.EDirection.INPUT)
            )
            for name, node in self._nodes.items()
        }
        reverse_dependencies = defaultdict(list)

        for name, node in self._nodes.items():
            for input in node._model.inputs:
                reverse_dependencies[input].append(name)

        no_dependency_nodes = deque(
            [name for name, degree in in_degree.items() if degree == 0]
        )

        while no_dependency_nodes:
            current_node_name = no_dependency_nodes.popleft()
            sorted_nodes.append(current_node_name)

            for dependent_name in reverse_dependencies[current_node_name]:
                in_degree[dependent_name] -= 1
                if in_degree[dependent_name] == 0:
                    no_dependency_nodes.append(dependent_name)

        if len(sorted_nodes) != len(self._nodes):
            raise ValueError("Cyclic dependency detected!")

        return sorted_nodes, reverse_dependencies

    def add_node(self, node: GNode) -> None:
        if node.name in self._nodes:
            raise ValueError(f"Node {node.name} already exists.")
        self._nodes[node.name] = node
        self._sorted_task_names, self._reverse_dependencies = self._topological_sort()


class StartOperator(GNode):

    def allocate_default_pins(self):
        self.schema.pins.add(
            FPin(
                name="output",
                owning_node=weakref.ref(self),
                direction=FPin.EDirection.OUTPUT,
            )
        )

    async def execute(self) -> None:
        self.pins["output"].value = "Start Operator output"
        print("Start Operator", time.time())


class BashOperator(GNode):

    def allocate_default_pins(self):
        self.schema.pins.add(
            FPin(
                name="command",
                owning_node=weakref.ref(self),
                direction=FPin.EDirection.INPUT,
            )
        )
        self.schema.pins.add(
            FPin(
                name="output",
                owning_node=weakref.ref(self),
                direction=FPin.EDirection.OUTPUT,
            )
        )

    async def execute(self):
        command = self.pins["command"].value
        print(f"BashOperator: {command}")
        self.pins["output"]().value = command


class PythonOperator(GNode):

    def allocate_default_pins(self):
        pass

    def execute(self):
        assert self._ctx is not None, "Context is not built yet."

        args = {}
        for input in self._model.inputs:
            args.append(self._ctx["outputs"][input])

        input_op = self._ctx["inputs"][self._model.inputs]
        arg1, arg2 = self._ctx["outputs"][self.name]
        self._ctx["outputs"][self.name] = f"Hello World from {self.name}"


class GraphExecutor:
    def __init__(self, graph: GGraph, parallel: bool = True):
        self._graph = graph
        self._parallel = parallel

    async def _parallel_execute(self):

        sorted_task_names = self._graph._sorted_task_names.copy()
        reverse_dependencies = self._graph._reverse_dependencies

        task_coroutines = {
            name: node.execute() for name, node in self._graph._nodes.items()
        }

        completed_tasks = set()

        while sorted_task_names:
            # 找出当前可以运行的任务（依赖项都已完成）
            runnable_tasks = [
                name
                for name in sorted_task_names
                if all(
                    dep in completed_tasks
                    for dep in self._graph._nodes[name]._model.inputs
                )
            ]

            if not runnable_tasks:
                raise ValueError("Cyclic dependency detected!")

            # 并发运行所有可运行的任务
            await asyncio.gather(*[task_coroutines[name] for name in runnable_tasks])

            # 更新已完成的任务列表
            for name in runnable_tasks:
                sorted_task_names.remove(name)
                completed_tasks.add(name)

                # todo：通过graph_ctx传递
                # 更新后续任务的输入,
                # for dependent_name in reverse_dependencies[name]:
                #     self._graph._nodes[dependent_name]._metadata = self._tasks[name].output

    async def _sequential_execute(self):
        for name in self._graph._sorted_node_names:
            await self._graph._nodes[name].execute()

    async def execute(self):
        if self._parallel:
            await self._parallel_execute()
        else:
            await self._sequential_execute()


if __name__ == "__main__":

    # with GGraph() as graph:
    #     start_op = StartOperator(name="start")
    #     bash_operator = BashOperator(name="bash")
    #     start_op.pins["output"].linkto(bash_operator.pins["command"])

    start_op = StartOperator(name="start")
    bash_operator = BashOperator(name="bash")
    start_op.pins["output"].linkto(bash_operator.pins["cmd"])

    # inputs = {Input(id="cmd", type="string"), Input(id="args", type="list")}
    # outputs = {Output(id="result", type="string")}
    # bash_operator = BashOperator(inputs=set([

    # ]), outputs)
    # context = {"outputs": {}}
    # bash_operator.build(context)
    # asyncio.run(
    #     bash_operator.execute(BashOperator.Inputs(cmd="echo", args=["Hello, World!"]))
    # )

    # graph = GraphDAG(
    #     [
    #         PythonOperator({}, name="P1.S"),
    #         BashOperator({Binding("P1.S", "PythonOperator")}, name="P1.A"),
    #         PythonOperator({Binding("P1.S", "PythonOperator")}, name="P1.B"),
    #         BashOperator({Binding("P1.S", "PythonOperator")}, name="P1.C"),
    #         PythonOperator(
    #             {Binding("P1.B", "PythonOperator"), Binding("P1.C", "BashOperator")},
    #             name="P1.D",
    #         ),
    #     ]
    # )
    # graph.serialize_to_json("dag.json")
    # graph = GraphDAG.from_json("dag.json")
    # exe = GraphExecutor(graph)
    # exe.execute()

    # with GraphDAG() as graph:
    #     op_01 = BashOperator(name="op_01")
    #     op_02 = PythonOperator(name="op_02")
    #     example = ExampleOperator.bind(
    #         "example",
    #         {NodeBind("op_01", "BashOperator"), NodeBind("op_02", "PythonOperator")},
    #     )
    #     # dag = GraphDAG([op_01, op_02, example])
    #     graph.execute()


# class Parallel(Node):
#     def __init__(
#         self,
#         tasks: List[Node],
#         name: Optional[str] = None,
#         deps: Optional[Set[str]] = None,
#     ) -> None:
#         super().__init__(name, deps)
#         self._tasks = {task.name: task for task in tasks}
#         self._sorted_task_names, self._reverse_dependencies = self._topological_sort()

#     def _topological_sort(self) -> Tuple[List[str], Dict[str, List[str]]]:
#         sorted_tasks = []
#         in_degree = {name: len(task.dependencies) for name, task in self._tasks.items()}
#         reverse_dependencies = defaultdict(list)

#         for name, task in self._tasks.items():
#             for dep in task.dependencies:
#                 reverse_dependencies[dep].append(name)

#         no_dependency_tasks = deque(
#             [name for name, degree in in_degree.items() if degree == 0]
#         )

#         while no_dependency_tasks:
#             current_task_name = no_dependency_tasks.popleft()
#             sorted_tasks.append(current_task_name)

#             for dependent_name in reverse_dependencies[current_task_name]:
#                 in_degree[dependent_name] -= 1
#                 if in_degree[dependent_name] == 0:
#                     no_dependency_tasks.append(dependent_name)

#         if len(sorted_tasks) != len(self._tasks):
#             raise ValueError("Cyclic dependency detected!")

#         return sorted_tasks, reverse_dependencies

#     def add_node(self, task: Node) -> None:
#         if task.name in self._tasks:
#             raise ValueError(f"Task {task.name} already exists.")
#         self._tasks[task.name] = task
#         self._sorted_task_names, self._reverse_dependencies = self._topological_sort()

#     async def execute(self, payloads):
#         sorted_task_names = self._sorted_task_names.copy()
#         reverse_dependencies = self._reverse_dependencies

#         # 初始化第一个任务的输入
#         # if initial_input is not None:
#         # self._tasks[sorted_task_names[0]].input = initial_input

#         task_coroutines = {
#             name: task.execute(payloads) for name, task in self._tasks.items()
#         }
#         completed_tasks = set()

#         while sorted_task_names:
#             # 找出当前可以运行的任务（依赖项都已完成）
#             runnable_tasks = [
#                 name
#                 for name in sorted_task_names
#                 if all(dep in completed_tasks for dep in self._tasks[name].dependencies)
#             ]

#             if not runnable_tasks:
#                 raise ValueError("Cyclic dependency detected!")

#             # 并发运行所有可运行的任务
#             await asyncio.gather(*[task_coroutines[name] for name in runnable_tasks])

#             # 更新已完成的任务列表
#             for name in runnable_tasks:
#                 sorted_task_names.remove(name)
#                 completed_tasks.add(name)

#                 # 更新后续任务的输入
#                 for dependent_name in reverse_dependencies[name]:
#                     self._tasks[dependent_name].input = self._tasks[name].output


# class Sequential(Node):
#     def __init__(
#         self,
#         tasks: List[Node],
#         name: Optional[str] = None,
#         deps: Optional[Set] = None,
#     ) -> None:
#         super().__init__(name, deps)
#         self._tasks = {task.name: task for task in tasks}

#     def add_node(self, task: Node) -> None:
#         if task.name in self._tasks:
#             raise ValueError(f"Task {task.name} already exists.")
#         self._tasks[task.name] = task

#     async def execute(self, payloads):
#         for task in self._tasks.values():
#             await task.execute(payloads)


# class Workflow(Node):
#     def __init__(self, tasks: List[Node]):
#         self._tasks = {task.name: task for task in tasks}

#     async def execute(self):
#         payloads = {}
#         await asyncio.gather(*[task.execute(payloads) for task in self._tasks.values()])
#         print(payloads)


# class ConditionalBranch(Node):
#     def __init__(
#         self,
#         condition: Callable[[Any], bool],
#         true_branch: UTaskNode,
#         false_branch: UTaskNode,
#     ):
#         self._condition = condition
#         self._true_branch = true_branch
#         self._false_branch = false_branch

#     async def execute(self):
#         if self._condition(self._ctx):
#             await self._true_branch.run()
#         else:
#             await self._false_branch.run()


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


# if __name__ == "__main__":

#     tc = Sequential(
#         [
#             Parallel(
#                 [
#                     Parallel(
#                         [
#                             Node("P1.S"),
#                             Node("P1.A", inputs=["P1.S"]),
#                             Node("P1.B", inputs=["P1.S"]),
#                             Node("P1.C", inputs=["P1.S"]),
#                             Node("P1.D", inputs=["P1.B", "P1.C"]),
#                         ],
#                         "P1",
#                     ),
#                     Parallel(
#                         [
#                             Node("P2.S"),
#                             Node("P2.A", inputs=["P2.S"]),
#                             Node("P2.B", inputs=["P2.S"]),
#                             Node("P2.C", inputs=["P2.S"]),
#                             Node("P2.D", inputs=["P2.B", "P2.C"]),
#                         ],
#                         "P2",
#                     ),
#                     Parallel(
#                         [
#                             Node("P3.S"),
#                             Node("P3.A", inputs=["P3.S"]),
#                             Node("P3.B", inputs=["P3.S"]),
#                             Node("P3.C", inputs=["P3.S"]),
#                             Node("P3.D", inputs=["P3.B", "P3.C"]),
#                         ],
#                         "P3",
#                     ),
#                 ]
#             ),
#             Parallel(
#                 [
#                     Node("P4.S"),
#                     Node("P4.A", inputs=["P4.S"]),
#                     Node("P4.B", inputs=["P4.A"]),
#                     Node("P4.C", inputs=["P4.A"]),
#                     Node("P4.D", inputs=["P4.B", "P4.C"]),
#                 ],
#             ),
#         ]
#     )

#     wf = Workflow([tc])

#     asyncio.run(wf.execute())

#     # 序列化工作流到文件
#     # serialize_workflow_to_networkx_format(tasks, "workflow_networkx.json")

#     # 从文件反序列化工作流
#     # loaded_tasks = deserialize_workflow_from_networkx_format("workflow_networkx.json")

#     # 运行事件循环
#     # asyncio.run(run_workflow(tasks, initial_input="Initial Input"))

#     # 绘制工作流图
#     # plot_workflow("workflow_networkx.json")

#     # user-interface -> Workflow -> celery-> redis -> workers

#     with DAG(
#         name="tutorial",
#         default_args=default_args,
#         description="A simple tutorial DAG",
#         schedule_interval=timedelta(days=1),
#         start_date=day_ago(2),
#         tags=["example"],
#     ) as dag:
#         seq = Sequential(
#             BashOperator(name="print_date", bash_command="date"),
#             BashOperator(name="sleep", bash_command="sleep 5"),
#         )
#         # t1 = BashOperator(name="print_date", bash_command="date")
#         # t2 = BashOperator(name='sleep', bash_command='sleep 5')
