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


class GraphSpec:
    pass


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

    @classmethod
    def build_from_graph_spec(self, spec: GraphSpec) -> None:
        pass

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
