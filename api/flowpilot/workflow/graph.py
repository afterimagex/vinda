import copy
import json
import weakref
from typing import Dict, Iterable, List, Optional, Union
from uuid import uuid4

from flowpilot.workflow.nodes import NodeBase, new_node
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

    def clear(self):
        self._pins.clear()
        self._nodes.clear()


class DagGraph:

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
        self.name = f"{self.__class__.__name__}_{id(self)}" if name is None else name
        self._nodes = []
        self.add_nodes(nodes)

    @property
    def nodes(self) -> Iterable[NodeBase]:
        return self._nodes

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"

    def __enter__(self) -> "DagGraph":
        pass
        # self._previous_graph = current_graph
        # current_graph = self
        # return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass
        # current_graph = self._previous_graph

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

    def clear(self):
        self.ctx.clear()
        self._nodes.clear()

    def dump(self) -> dict:
        state = copy.deepcopy(self.__dict__)
        state["nodes"] = [node.dump() for node in state["_nodes"]]
        state.pop("_nodes")
        state.pop("ctx")
        return state

    def load(self, state: dict) -> None:
        state = copy.deepcopy(state)
        for key in state.keys():
            if key == "nodes":
                self.clear()
                nodes = [
                    new_node(node_state["class"]).load(node_state)
                    for node_state in state[key]
                ]
                self.add_nodes(nodes)
            else:
                super().__setattr__(key, state[key])
        return self

    def dumps(self) -> str:
        return json.dumps(self.dump())

    @classmethod
    def loads(self, state: str) -> "DagGraph":
        cls = self()
        cls.load(json.loads(state))
        return cls

    def plot(self, filename: str = "dag_graph.png"):
        import matplotlib.pyplot as plt
        import networkx as nx

        G = nx.DiGraph()
        edges = []
        for node in self._nodes:
            G.add_node(node.id, label=node.name)
            for deps_node in node.get_dependencies():
                edges.append((deps_node.id, node.id))
        G.add_edges_from(edges)

        pos = nx.planar_layout(G)
        labels = nx.get_node_attributes(G, "label")

        plt.figure(figsize=(10, 7))
        nx.draw(
            G,
            pos,
            labels=labels,
            with_labels=True,
            node_size=3000,
            node_color="skyblue",
            font_size=16,
            font_color="black",
            font_weight="bold",
            arrows=True,
        )
        plt.title("DAG Graph")
        plt.savefig(filename, format="png")
        plt.show()


if __name__ == "__main__":

    from flowpilot.workflow.nodes import UNODE
    from flowpilot.workflow.pin import Direction

    @UNODE()
    class MyNode(NodeBase):
        def __init__(self, name: Optional[str] = None) -> None:
            super().__init__(name)
            self.arg1 = Pin("arg1")
            self.arg2 = Pin("arg2")
            self.output = Pin(direction=Direction.OUTPUT)

        async def execute(self, *args, **kwargs) -> None:
            pass

    n1 = MyNode("n1")
    n2 = MyNode("n2")
    n3 = MyNode("n3")
    n4 = MyNode("n4")
    n5 = MyNode("n5")

    n1.output.link(n3.arg1)
    n3.output.link(n4.arg1)
    n4.output.link(n2.arg1)
    n3.output.link(n5.arg1)
    n4.output.link(n5.arg2)
    n5.output.link(n2.arg2)

    dg = DagGraph(nodes=[n1, n2, n3, n4, n5])

    print(dg)
    print(dg.sorted_node_names)
    dg.plot()

    print("==> dump")
    data = dg.dump()
    print(json.dumps(data, indent=4))

    print("==> load")
    dg = dg.load(data)
    print(dg)

    print("==> dumps")
    data = dg.dumps()
    print(json.dumps(json.loads(data), indent=4))

    print("==> loads")
    node = DagGraph.loads(data)
    print(node)

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
