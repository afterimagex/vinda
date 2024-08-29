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
    _version: int = 1


class Pin:
    _schema: PinSchema

    def __init__(self, schema: Union[PinSchema, dict, None] = None) -> None:
        super().__setattr__(
            "_schema",
            (
                PinSchema(**schema)
                if isinstance(schema, dict)
                else (schema or PinSchema())
            ),
        )

    def __repr__(self) -> str:
        return str(self._schema)

    def __setattr__(self, name: str, value: "Pin") -> None:
        schema = self.__dict__.get("_schema")
        if schema is None:
            raise AttributeError(
                f"cannot assign pin before {self.__class__.__name__}.__init__() call"
            )
        if name in schema.__dict__:
            setattr(schema, name, value)
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name: str) -> Any:
        if "_schema" in self.__dict__:
            schema = self.__dict__["_schema"]
            if name in schema.__dict__:
                return getattr(schema, name)
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def __delattr__(self, name):
        if "_schema" in self.__dict__:
            schema = self.__dict__["_schema"]
            if name in schema.__dict__:
                raise AttributeError(
                    f"'{type(self).__name__}' object can not del attribute '{name}'"
                )
        else:
            super().__delattr__(name)

    def link(self, other: "Pin") -> None:
        """Link to another pin"""
        if other.id not in self.links:
            assert self.id not in other.links
            # Notify owning nodes about upcoming change
            # self.modify()
            # other.modify()
            self.links.add(other.id)
            other.links.add(self.id)

    def unlink(self, other: "Pin") -> None:
        """Break link to another pin"""
        if other.id in self.links:
            assert self.id in other.links
            # Notify owning nodes about upcoming change
            # self.modify()
            # other.modify()
            self.links.remove(other.id)
            other.links.remove(self.id)

    def dumps(self) -> str:
        return self._schema.model_dump_json()

    @classmethod
    def loads(cls, schema: str) -> "Pin":
        return cls(PinSchema.model_validate_json(schema))


class MyPin(Pin):
    def __init__(self, schema: PinSchema | Dict | None = None) -> None:
        super().__init__(schema)
        self.name = "09"


if __name__ == "__main__":

    p = Pin({"name": "1235"})
    print(p.name)
    p2 = Pin({"name": "1234"})
    print(p2.name)

    p.link(p2)
    p.name = "00"

    print(p)

    # d = Pin({"name": "123"})
    # print(d)
    # r = d.dumps()
    # print(r)
    # f = Pin.loads(r)
    # print(f)
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
