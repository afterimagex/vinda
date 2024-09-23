import copy
import json
from enum import Enum
from typing import TYPE_CHECKING, Iterator, Optional, Set
from uuid import uuid4

if TYPE_CHECKING:
    from .graph import GraphContext
    from .nodes import NodeBase


class PinCategories(Enum):
    """PinCategories"""

    Exec = 0  # 描述: 表示执行流控制的引脚，用于控制节点的执行顺序。示例: Execute, Then
    Boolean = 1  # 描述: 布尔类型引脚，用于传递True或False值。示例: IsActive, bIsVisible
    Integer = 2  # 描述: 整型引脚，用于传递整数值。示例: Health, Score
    Float = 3  # 描述: 浮点型引脚，用于传递浮点数值。示例: Speed, Rotation
    String = 4  # 描述: 字符串类型引脚，用于传递文本数据。示例: PlayerName, Description
    Name = 5  # 描述: 名称类型引脚，用于传递名称（类似于字符串，但在UE中有特殊用途）。示例: BoneName, Tag
    Vector = 6  # 描述: 向量类型引脚，用于传递三维向量值。示例: Location, Direction
    Rotator = 7  # 描述: 旋转器类型引脚，用于传递三维旋转值。示例: Rotation, Orientation
    Transform = 8  # 描述: 变换类型引脚，用于传递位置、旋转和缩放的组合。示例: Transform, TransformMatrix
    Object = 9  # 描述: 对象类型引脚，用于传递对象引用。示例: Actor, Component, 子类别: 具体的对象类型，如Actor, StaticMeshComponent等。
    Class = 10  # 描述: 类别类型引脚，用于传递类引用, 示例: CharacterClass, WeaponClass, 子类别: 具体的类类型。
    Struct = 11  # 描述: 结构体类型引脚，用于传递用户定义的结构体类型。示例: Vector2D, HitResult, 子类别: 具体的结构体类型。
    Enum = 12  # 描述: 枚举类型引脚，用于传递枚举值。示例: MovementMode, WeaponType, 子类别: 具体的枚举类型。


class ContainerTypes(Enum):
    """ContainerTypes"""

    Null = 0  # 描述: 单一值，引脚只传递单一值。示例: int, float
    Array = 1  # 描述: 数组，引脚可以传递多个值。示例: int[], float[]
    Set = 2  # 描述: 集合类型，引脚传递一个集合。示例: Set<int>, Set<float>
    Map = 3  # 描述: 映射类型，引脚传递一个键值对映射。示例: Map<int, int>, Map<float, float>, Map<int, string>


class PinProperties(Enum):
    """PinProperties"""

    bIsReference = 0  # 是否为引用类型。
    bIsConst = 1  # 是否为常量。
    bIsWeakPointer = 2  # 是否为弱引用。
    bIsUObjectWrapper = 3  # 是否为UObject包装器。
    bSerializeAsSinglePrecisionFloat = 4  # 是否作为单精度浮点数序列化。
    bOrphanedPin = 5  # 是否为孤立引脚。
    bNotConnectable = 6  # 是否为不可连接的引脚。
    bDefaultValueIsReadOnly = 7  # 默认值是否只读。


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
