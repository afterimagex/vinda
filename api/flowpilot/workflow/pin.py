import copy
import json
from enum import Enum
from typing import Optional, Set
from uuid import uuid4


class Direction(Enum):
    INPUT = 0
    OUTPUT = 1


class Pin:

    id: str
    name: Optional[str]
    direction: Direction
    links: Set[str]
    owning_node: Optional[str]
    _version: int = 1

    def __init__(self, name: Optional[str] = None) -> None:
        super().__setattr__("id", str(uuid4()))
        super().__setattr__("name", name)
        super().__setattr__("direction", Direction.INPUT)
        super().__setattr__("links", set())
        super().__setattr__("owning_node", None)

    # def __repr__(self) -> str:
    #     return self.dumps()

    def link(self, other: "Pin") -> None:
        """Link to another pin"""
        if other.id not in self.links:
            assert self.id not in other.links
            self.links.add(other.id)
            other.links.add(self.id)

    def unlink(self, other: "Pin") -> None:
        """Break link to another pin"""
        if other.id in self.links:
            assert self.id in other.links
            self.links.remove(other.id)
            other.links.remove(self.id)

    def dict(self) -> dict:
        return copy.deepcopy(self.__dict__)

    def load(self, state: dict) -> None:
        for k in state.keys():
            if k == "direction":
                state[k] = Direction(state[k])
            elif k == "links":
                state[k] = set(state[k])
            super().__setattr__(k, state[k])
        return self

    def dumps(self) -> str:
        state = self.dict()
        state["links"] = list(state["links"])
        state["direction"] = self.direction.value
        return json.dumps(state)

    @classmethod
    def loads(self, state: str) -> "Pin":
        cls = self()
        cls.load(json.loads(state))
        return cls


if __name__ == "__main__":

    p1 = Pin(name="1")
    print(p1)
    p2 = Pin(name="2")
    print(p2)

    p1.link(p2)
    print(p1)

    print("***")

    dp = p1.dumps()
    print(dp)

    p3 = Pin.loads(dp)
    print(p3)

    print("***")

    d2 = p1.json()
    print(p1)

    d3 = Pin()
    d4 = d3.load(d2)

    print(d4)
