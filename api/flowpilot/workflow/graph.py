import weakref
from typing import Dict, Iterable, List, Optional, Set, Union
from uuid import uuid4

from flowpilot.workflow.node import NodeBase
from flowpilot.workflow.pin import Pin
from flowpilot.workflow.utils import topological_sort


class GraphContext:
    def __init__(self) -> None:
        self._pins: Dict[str, weakref.ReferenceType[Pin]] = {}
        self._nodes: Dict[str, weakref.ReferenceType[NodeBase]] = {}

    @property
    def nodes(self) -> Dict[str, weakref.ReferenceType[NodeBase]]:
        return self._nodes

    def get_pin(self, pin_id: str) -> Optional[Pin]:
        """Get pin by id."""
        pin_ref = self._pins.get(pin_id)
        if pin_ref is None:
            print(f"Pin '{pin_id}' does not exist.")
            return None
        pin = pin_ref()
        if pin is None:
            print(f"Pin '{pin_id}' already released.")
            self._pins.pop(pin_id)
        return pin

    def get_node(self, node_id: str) -> Optional[NodeBase]:
        """Get node by id."""
        node_ref = self._nodes.get(node_id)
        if node_ref is None:
            print(f"Node '{node_id}' does not exist.")
            return None
        node = node_ref()
        if node is None:
            print(f"Node '{node_id}' already released.")
            self._nodes.pop(node_id)
        return node

    def add_node(self, node: NodeBase) -> None:
        if node.id in self._nodes:
            raise ValueError(f"Node '{node.id}' already exists.")
        self._nodes[node.id] = weakref.ref(node)
        node.ctx = self
        for pin in node.pins:
            self.add_pin(pin)

    def add_pin(self, pin: Pin) -> None:
        if pin.id in self._pins:
            raise ValueError(f"Pin '{pin.id}' already exists.")
        self._pins[pin.id] = weakref.ref(pin)


class Graph:

    id: str
    ctx: GraphContext
    name: Optional[str]
    _sorted_node_names: List[str]
    _current_graph: Optional["Graph"] = None

    def __init__(
        self,
        name: Optional[str] = None,
        nodes: Optional[Union[NodeBase, Iterable[NodeBase]]] = None,
    ) -> None:
        self.id = str(uuid4())
        self.ctx = GraphContext()
        self.name = name
        self._sorted_node_ids: List[str] = []
        self.add_nodes(nodes)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"

    def __enter__(self) -> "Graph":
        self._previous_graph = Graph._current_graph
        Graph._current_graph = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        Graph._current_graph = self._previous_graph

    @classmethod
    def get_current_graph(cls) -> Optional["Graph"]:
        return cls._current_graph

    def add_nodes(self, nodes: Union[NodeBase, Iterable[NodeBase]]) -> None:
        if nodes is None:
            return

        if isinstance(nodes, NodeBase):
            nodes = [nodes]

        for node in nodes:
            node.owning_graph = self.id
            self.ctx.add_node(node)

        self._sorted_node_ids = topological_sort(
            [n for node in self.ctx.nodes.values() if (n := node())]
        )

    def try_create_connection(self, apin: Pin, bpin: Pin) -> None:
        if self.can_create_connection(apin, bpin):
            apin.link(bpin)

    def can_create_connection(self, apin: Pin, bpin: Pin) -> bool:
        return True

    @property
    def sorted_node_names(self) -> List[str]:
        return [self.ctx.get_node(node_id).name for node_id in self._sorted_node_ids]


if __name__ == "__main__":
    from flowpilot.workflow.pin import Direction

    class MyNode(NodeBase):
        def __init__(self, name: Optional[str] = None) -> None:
            super().__init__(name)
            self.input = Pin()
            self.output = Pin(direction=Direction.OUTPUT)

    class MyNode2(MyNode):
        def __init__(self, name: Optional[str] = None) -> None:
            super().__init__(name)
            self.input = Pin()
            self.output = Pin(direction=Direction.OUTPUT)

    with Graph("test") as g:
        n1 = MyNode()
        n2 = MyNode2()
        n1.input.link(n2.output)

        print(g)
        print(g.sorted_node_names)

    # def _validate_input_bindings(self) -> bool:
    #     # for node in self._nodes.values():
    #     #     for input_binding in node._model.inputs:
    #     #         if input_binding.id not in self._nodes:
    #     #             raise ValueError(
    #     #                 f"Input '{input_binding.id}' for node '{node.name}' does not exist."
    #     #             )
    #     pass

    # def serialize(self) -> dict:
    #     return {node.name: node.serialize() for node in self._nodes.values()}

    # def deserialize(self, data: dict) -> None:
    #     pass
