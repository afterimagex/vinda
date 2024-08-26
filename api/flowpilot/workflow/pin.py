import uuid
import weakref
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional, Set
from uuid import UUID, uuid4
from weakref import ReferenceType

from flowpilot.common.module import Module
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

    from flowpilot.workflow.node import GNode


# @dataclass
# class FPinType:
#     category: str
#     sub_category_object: Optional[weakref.ReferenceType] = None


class EDirection(Enum):
    INPUT = 0
    OUTPUT = 1


class FPin(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    owning_node_ref: Optional[ReferenceType] = Field(default=None, alias="owning_node")
    direction: EDirection = EDirection.INPUT
    value: Any = None
    # links: Set["FPin"] = Field(default_factory=set)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        *,
        include_default_values: bool = True,
        ref_template: str = "#/components/schemas/{model}",
        **kwargs: Any
    ) -> Dict[str, Any]:
        return {
            "title": "CustomType",
            "type": "object",
            "properties": {
                "value": {
                    "type": "string",
                    "description": "The value of the custom type.",
                    # 可以添加其他属性和验证规则
                },
            },
            "required": ["value"],  # 如果该字段是必需的
            # 可以添加其他 JSON Schema 关键字
        }

    # def to_dict(self) -> dict:
    #     data = asdict(self)
    #     data["direction"] = self.direction.value
    #     data["links"] = []
    #     data["owning_node"] = None
    #     # data["id"] = str(self.id)
    #     return data

    # @classmethod
    # def from_dict(cls, data: dict) -> "FPin":
    #     # data["id"] = uuid.UUID(data["id"])
    #     data["direction"] = EDirection(data["direction"])
    #     data["links"] = set()
    #     return cls(**data)

    # def modify(self) -> None:
    #     pass

    def link(self, other: "FPin") -> None:
        """link to another pin"""
        if other not in self.links:
            assert self not in other.links
            # Notify owning nodes about upcoming change
            # self.modify()
            # other.modify()
            self.links.add(other)
            other.links.add(self)

    def unlink(self, other: "FPin") -> None:
        """break link to another pin"""
        if other in self.links:
            assert self in other.links
            # Notify owning nodes about upcoming change
            # self.modify()
            # other.modify()
            self.links.remove(other)
            other.links.remove(self)

    def __hash__(self) -> int:
        return hash(self.id)

    # def __eq__(self, other):
    #     if not isinstance(other, FPin):
    #         return False
    #     return self._id == other._id


if __name__ == "__main__":
    # pass
    # import json

    # # no = No()
    # # k = weakref.ref(no)
    dp = FPin().model_dump_json()
    print(dp)
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
