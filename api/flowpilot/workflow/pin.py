import uuid
import weakref
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional, Set, Union
from uuid import UUID, uuid4
from weakref import ReferenceType

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    GenerateSchema,
    PrivateAttr,
    field_serializer,
    field_validator,
    model_serializer,
    model_validator,
)
from pydantic_core import CoreSchema

if TYPE_CHECKING:
    from weakref import ReferenceType

    from flowpilot.workflow.node import NodeBase


# @dataclass
# class FPinType:
#     category: str
#     sub_category_object: Optional[weakref.ReferenceType] = None


class Direction(Enum):
    INPUT = 0
    OUTPUT = 1


class PinSchema(BaseModel):
    name: str = ""
    direction: Direction = Direction.INPUT
    links: Set[str] = Field(default_factory=set)
    owning_node: Optional[str] = None
    id: str = Field(default_factory=lambda: str(uuid4()))


class Pin:

    def __init__(self, schema: Union[PinSchema, dict, None] = None) -> None:
        self._schema = (
            PinSchema(**schema) if isinstance(schema, dict) else (schema or PinSchema())
        )

    def link(self, other: "Pin") -> None:
        """Link to another pin"""
        if other.s.id not in self.s.links:
            assert self.s.id not in other.s.links
            # Notify owning nodes about upcoming change
            # self.modify()
            # other.modify()
            self.s.links.add(other.s.id)
            other.s.links.add(self.s.id)

    def unlink(self, other: "Pin") -> None:
        """Break link to another pin"""
        if other.s.id in self.s.links:
            assert self.s.id in other.s.links
            # Notify owning nodes about upcoming change
            # self.modify()
            # other.modify()
            self.s.links.remove(other.s.id)
            other.s.links.remove(self.s.id)

    def dumps(self) -> str:
        return self.s.model_dump_json()

    @classmethod
    def loads(cls, schema: str) -> "Pin":
        return cls(PinSchema.model_validate_json(schema))

    def __getattr__(self, name: str):
        return getattr(self._schema, name)

    def __setattr__(self, name: str, value):
        if name == "_schema":
            super().__setattr__(name, value)
        elif hasattr(self._schema, name):
            setattr(self._schema, name, value)
        else:
            super().__setattr__(name, value)

    def __repr__(self) -> str:
        return str(self.s)


if __name__ == "__main__":
    # pass
    # import json

    d = Pin({"name": "123"})
    print(d)
    r = d.dumps()
    print(r)
    f = Pin.loads(r)
    print(f)
    # # no = No()
    # # k = weakref.ref(no)
    # p1 = Pin(name="123")
    # p2 = Pin()

    # p1.link(p2)

    # r = p1.dumps()
    # print(r)

    # d = Pin.loads(r)
    # print(d)

    # dp = p1.model_dump_json()
    # print(dp)
    # d2 = p2.model_dump_json()
    # print(d2)
    # gp = GPin(name="321", gwater=1)
    # print(gp)

    # # dp.link(gp)

    # # p2 = FPin(name="321")
    # # ss = {p1, p2}
    # dp_data = dp.model_dump_json()
    # gp_data = gp.model_dump_json()

    # print(dp_data)
    # print(gp_data)

    # dk = FPin.model_validate_json(dp_data)
    # gk = FPin.model_validate_json(gp_data)

    # print(dk, type(dk))
    # print(gk, type(gk))

    # xx = json.loads(x)

    # y = FPin(**xx)
    # print(y)
    # print(ss)

    # import json

    # spec = json.dumps(p1.to_dict())
    # print(spec)

    # new_p = FPin.from_dict(json.loads(spec))
    # print(new_p)
