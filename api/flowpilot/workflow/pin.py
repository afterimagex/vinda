import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, Set
from weakref import ReferenceType

if TYPE_CHECKING:
    from weakref import ReferenceType

    from flowpilot.workflow.node import GNode


@dataclass
class FPinType:
    category: str
    sub_category_object: Optional[ReferenceType]


class EDirection(Enum):
    INPUT = 1
    OUTPUT = 2


@dataclass
class FPin:
    name: str = ""
    owning_node: Optional[ReferenceType] = None
    direction: EDirection = EDirection.INPUT
    value: Any = None
    type: FPinType = None
    links: Set["FPin"] = field(default_factory=set)
    _id: uuid.UUID = field(default_factory=uuid.uuid4)

    def to_dict(self) -> dict:
        return asdict(self)

    def modify(self) -> None:
        pass

    def link_to(self, other: "FPin") -> None:
        if other not in self.links:
            assert self not in other.links
            # Notify owning nodes about upcoming change
            self.modify()
            other.modify()
            self.links.add(other)
            other.links.add(self)

    def break_link(self, other: "FPin") -> None:
        if other in self.links:
            assert self in other.links
            # Notify owning nodes about upcoming change
            self.modify()
            other.modify()
            self.links.remove(other)
            other.links.remove(self)

    def to_dict(self) -> dict:
        return asdict(self)

    def __hash__(self) -> int:
        return hash(self._id)

    def __eq__(self, other):
        if not isinstance(other, FPin):
            return False
        return self._id == other._id


if __name__ == "__main__":
    p1 = FPin("123")
    p2 = FPin("123")
    ss = {p1, p2}
    print(ss)
