import copy
import json
from enum import Enum
from typing import TYPE_CHECKING, Iterator, Optional, Set
from uuid import uuid4

if TYPE_CHECKING:
    from .graph import GraphContext
    from .nodes import NodeBase


class Direction(Enum):
    INPUT = 0
    OUTPUT = 1


class Pin:

    id: str
    name: Optional[str]
    direction: Direction
    links: Set[str]
    value: Optional[str]
    owning_node: Optional[str]
    _version: int = 1

    def __init__(
        self,
        name: Optional[str] = None,
        direction: Direction = Direction.INPUT,
    ) -> None:
        super().__setattr__("id", str(uuid4()))
        super().__setattr__("name", name)
        super().__setattr__("direction", direction)
        super().__setattr__("links", set())
        super().__setattr__("value", None)
        super().__setattr__("owning_node", None)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"

    def modify(self) -> None:
        if self.direction == Direction.INPUT:
            assert len(self.links) <= 1, "maximum one link for input pins"

    def link(self, other: "Pin") -> None:
        """Link to another pin"""
        if other.id not in self.links:
            assert self.id not in other.links
            assert self.direction != other.direction
            self.links.add(other.id)
            self.modify()
            other.links.add(self.id)
            other.modify()

    def unlink(self, other: "Pin") -> None:
        """Break link to another pin"""
        if other.id in self.links:
            assert self.id in other.links
            self.links.remove(other.id)
            self.modify()
            other.links.remove(self.id)
            other.modify()

    def get_linked_nodes(self, ctx: "GraphContext") -> Iterator["NodeBase"]:
        for other in self.links:
            if node := ctx.get_pin_node(other):
                yield node

    def get_input_node(self, ctx: "GraphContext") -> Optional["NodeBase"]:
        assert self.direction == Direction.INPUT
        for node in self.get_linked_nodes(ctx):
            return node
        return None

    def dump(self):
        state = copy.deepcopy(self.__dict__)
        state.pop("owning_node")
        state["links"] = list(state["links"])
        state["direction"] = self.direction.value
        return state

    def load(self, state: dict) -> "Pin":
        for key in state.keys():
            if key == "links":
                state[key] = set(state[key])
            elif key == "direction":
                state[key] = Direction(state[key])
            super().__setattr__(key, state[key])
        return self

    def dumps(self) -> str:
        return json.dumps(self.dump())

    @classmethod
    def loads(self, state: str) -> "Pin":
        cls = self()
        cls.load(json.loads(state))
        return cls


if __name__ == "__main__":

    pin = Pin(name="test", direction=Direction.INPUT)

    print("==> dump")
    data = pin.dump()
    print(type(data), data)

    print("==> load")
    data["name"] = "loaded"
    pin = pin.load(data)
    print(type(pin), pin)

    print("==> dumps")
    data = pin.dumps()
    print(type(data), data)

    print("==> loads")
    pin = Pin.loads(data)
    print(type(pin), pin)
