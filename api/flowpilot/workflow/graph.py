import copy
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
    def nodes(self) -> Iterable[NodeBase]:
        return iter(self._nodes.values())

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
    _nodes: List[NodeBase]

    def __init__(
        self,
        name: Optional[str] = None,
        nodes: Optional[Union[NodeBase, Iterable[NodeBase]]] = None,
    ) -> None:
        self.id = str(uuid4())
        self.ctx = GraphContext()
        self.name = name
        self._nodes = []
        self.add_nodes(nodes)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"

    def __enter__(self) -> "Graph":
        self._previous_graph = current_graph
        current_graph = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        current_graph = self._previous_graph

    def _add_node(self, node: NodeBase) -> None:
        self.ctx.add_node(node)
        node.owning_graph = self.id
        self._nodes.append(node)

    def add_nodes(self, nodes: Union[NodeBase, Iterable[NodeBase]]) -> None:
        if nodes is None:
            return

        if isinstance(nodes, NodeBase):
            nodes = [nodes]

        for node in nodes:
            self._add_node(node)

        sorted_node_ids = topological_sort(self._nodes)
        self._nodes.sort(key=lambda node: sorted_node_ids.index(node.id))

    def try_create_connection(self, apin: Pin, bpin: Pin) -> None:
        if self.can_create_connection(apin, bpin):
            apin.link(bpin)

    def can_create_connection(self, apin: Pin, bpin: Pin) -> bool:
        return True

    @property
    def sorted_node_names(self) -> List[str]:
        return [node.name for node in self._nodes]

    def dump(self) -> dict:
        state = copy.deepcopy(self.__dict__)
        state["_nodes"] = [node.dump() for node in state["_nodes"]]
        state.pop("ctx")
        return state

    def load(self, state: dict) -> None:
        state = copy.deepcopy(state)
        for key in state.keys():
            if key == "_nodes":
                self._nodes.clear()
                # todo:factory to load nodes
                nodes = [NodeBase().load(node_state) for node_state in state[key]]
                self.add_nodes(nodes)
            else:
                super().__setattr__(key, state[key])
        return self


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

    n1 = MyNode()
    n2 = MyNode2()
    n1.input.link(n2.output)

    g = Graph("test", [n1, n2])

    print(g)
    print(g.sorted_node_names)

    print("==> dump")
    data = g.dump()
    print(data)

    print("==> load")
    g = g.load(data)
    print(g)

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
