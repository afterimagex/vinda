import asyncio
import threading
import uuid
from dataclasses import asdict, dataclass, field
from typing import Dict, Iterable, List, Set

from flowpilot.workflow.node import FNodeSchema, GNode
from flowpilot.workflow.pin import FPin
from flowpilot.workflow.utils import topological_sort


@dataclass
class GraphSchema:
    name: str = ""
    nodes: Set["FNodeSchema"] = field(default_factory=set)
    # connections: List = field(default_factory=list)
    description: str = ""
    _id: uuid.UUID = field(default_factory=uuid.uuid4)

    def to_dict(self) -> dict:
        return asdict(self)


class GGraph:

    def __init__(self, name, nodes: Iterable["GNode"]) -> None:
        self._name = name
        self._nodes = {node.name: node for node in nodes}
        self._sorted_node_names = topological_sort(nodes)
        self._schema = GraphSchema(
            name,
            nodes=[node._schema for node in nodes],
            description="A simple tutorial User Interface for Graphs.",
        )
        self._ctx = dict()

    def build(self) -> None:
        for node in self._nodes.values():
            node.build(self._ctx)
        self._validate_input_bindings()

    def try_create_connection(self, apin: "FPin", bpin: "FPin") -> None:
        if self.can_create_connection(apin, bpin):
            apin.link_to(bpin)

    def can_create_connection(self, apin: "FPin", bpin: "FPin") -> bool:
        return True

    def _validate_input_bindings(self) -> bool:
        # for node in self._nodes.values():
        #     for input_binding in node._model.inputs:
        #         if input_binding.id not in self._nodes:
        #             raise ValueError(
        #                 f"Input '{input_binding.id}' for node '{node.name}' does not exist."
        #             )
        pass

    def serialize(self) -> dict:
        pass

    def deserialize(self, data: dict) -> None:
        pass

    def add_node(self, node: "GNode") -> None:
        if node.name in self._nodes:
            raise ValueError(f"Node {node.name} already exists.")
        self._nodes[node.name] = node
        self._schema.nodes.add(node._schema)
        self._sorted_node_names = topological_sort(self._nodes.values())

    @property
    def nodes(self) -> Dict[str, "GNode"]:
        return self._nodes

    @property
    def sorted_node_names(self) -> List[str]:
        return self._sorted_node_names


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
