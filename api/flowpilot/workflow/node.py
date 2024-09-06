"""
Module Summary:
This module provides a simple example to demonstrate how to
add a module-level docstring in the style commonly used in Apache projects.

Details:
The module includes a Direction enum, a Pin class, and a MyNode class.
"""

import copy
import json
from abc import ABC
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterator, Optional, Set, TypeVar
from uuid import uuid4

from flowpilot.workflow.pin import Direction, Pin
from pydantic import BaseModel
from tabulate import tabulate

if TYPE_CHECKING:

    from flowpilot.workflow.graph import GraphContext

T = TypeVar("T", bound="NodeBase")


class NodeStatus(Enum):
    Initial = 1
    Pending = 2
    Running = 3
    Paused = 4
    Finished = 5
    Failed = 6
    Canceled = 7
    Unknown = 8


# class TestField:
#     pass


# class NodeSchema(BaseModel):
#     name: str = ""
#     # pins: Set["PinSchema"] = Field(default_factory=set)
#     owning_graph: Optional[str] = None
#     status: NodeStatus = NodeStatus.Initial
#     position: Tuple[float, float] = (0.0, 0.0)
#     description: str = ""
#     id: str = Field(default_factory=lambda: str(uuid4()))
#     _version: int = 1
# fie: TestField = None


class FNodeState(BaseModel):
    pass


class StateMachine:
    pass


# class pin.Container:
#     pass


# Trick mypy into not applying contravariance rules to inputs by defining
# forward as a value, rather than a function.  See also
# https://github.com/python/mypy/issues/8795
def _forward_unimplemented(self, *inputs: Any) -> None:
    r"""Define the computation performed at every call.

    Should be overridden by all subclasses.

    .. note::
        Although the recipe for forward pass needs to be defined within
        this function, one should call the :class:`Module` instance afterwards
        instead of this since the former takes care of running the
        registered hooks while the latter silently ignores them.
    """
    raise NotImplementedError(
        f'Node [{type(self).__name__}] is missing the required "forward" function'
    )


class NodeBase(ABC):

    id: str
    ctx: Optional["GraphContext"]
    name: Optional[str]
    owning_graph: Optional[str]
    _pins: Dict[str, Pin]
    _version: int = 1

    def __init__(self, name: Optional[str] = None) -> None:
        super().__setattr__("id", str(uuid4()))
        super().__setattr__("ctx", None)
        super().__setattr__(
            "name", f"{self.__class__.__name__}_{id(self)}" if name is None else name
        )
        super().__setattr__("owning_graph", None)
        super().__setattr__("_pins", {})

        # Automatically add this node to the current graph if it exists

    forward: Callable[..., Any] = _forward_unimplemented

    @property
    def pins(self) -> Iterator[Pin]:
        return iter(self._pins.values())

    def __setattr__(self, name: str, value: Pin) -> None:
        def remove_from(*dicts_or_sets):
            for d in dicts_or_sets:
                if name in d:
                    if isinstance(d, dict):
                        del d[name]
                    else:
                        d.discard(name)

        pins = self.__dict__.get("_pins")
        if isinstance(value, Pin):
            if pins is None:
                raise AttributeError(
                    f"cannot assign pin before {self.__class__.__name__}.__init__() call"
                )
            remove_from(self.__dict__)
            value.name = f"{self.name}.{name if value.name is None else value.name}"
            value.owning_node = self.id
            pins[name] = value
        elif pins is not None and name in pins:
            if value is not None:
                raise TypeError(
                    f"cannot assign '{value.__class__.__name__}' as member of pins '{name}' "
                    "(Pin or None expected)"
                )
            pins[name] = value
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name: str) -> Any:
        if "_pins" in self.__dict__:
            pins = self.__dict__["_pins"]
            if name in pins:
                return pins[name]

        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def __delattr__(self, name):
        if name in self._pins:
            del self._pins[name]
        else:
            super().__delattr__(name)

    def extra_repr(self) -> str:
        r"""Set the extra representation of the module.

        To print customized extra information, you should re-implement
        this method in your own modules. Both single-line and multi-line
        strings are acceptable.
        """
        return ""

    def _indent(self, s, num_spaces):
        lines = s.split("\n")
        if len(lines) == 1:
            return s
        first = lines.pop(0)
        indented_lines = [(num_spaces * " ") + line for line in lines]
        return first + "\n" + "\n".join(indented_lines)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"

    def table(self):
        # 提取输入和输出引脚名称以及其他信息
        input_pins_info = [
            (name, "int")
            for name, pin in self._pins.items()
            if pin and pin.direction == Direction.INPUT
        ]
        output_pins_info = [
            (name, "dict")
            for name, pin in self._pins.items()
            if pin and pin.direction == Direction.OUTPUT
        ]

        # 节点名和类型信息
        node_name = self.__class__.__name__  # 假设有一个方法来获取节点名
        node_type = type(self).__name__  # 获取类名作为节点类型

        # 构造节点信息部分
        node_info = f"Node Name: {self.id} Node Type: {node_type}"

        # 确定表格的行数
        max_rows = max(len(input_pins_info), len(output_pins_info))

        # 填充引脚信息，以确保输入和输出引脚信息有相同的行数
        input_pins_info.extend([("", "")] * (max_rows - len(input_pins_info)))
        output_pins_info.extend([("", "")] * (max_rows - len(output_pins_info)))

        # 构造表格数据
        table_data = [
            [in_pin, in_info, out_info, out_pin]
            for (in_pin, in_info), (out_pin, out_info) in zip(
                input_pins_info, output_pins_info
            )
        ]

        # 设置表格标题
        headers = ["Input Pin Names", "", "", "Output Pin Names"]

        # 使用 tabulate 库生成格式化的表格字符串
        formatted_table = tabulate(table_data, headers=headers, tablefmt="grid")

        # 合并节点信息和引脚表格
        full_representation = f"{node_info}\n{formatted_table}"

        return full_representation

    def dump(self) -> dict:
        state = copy.deepcopy(self.__dict__)
        state.pop("ctx")
        for pin_name in state["_pins"].keys():
            state["_pins"][pin_name] = self._pins[pin_name].dump()
        return state

    def load(self, state: dict) -> T:
        state = copy.deepcopy(state)
        for key in state.keys():
            if key == "_pins":
                for pin_name in state[key].keys():
                    self._pins[pin_name].load(state["_pins"][pin_name])
            else:
                super().__setattr__(key, state[key])
        return self

    def dumps(self) -> str:
        return json.dumps(self.dump())

    @classmethod
    def loads(self, state: str) -> T:
        cls = self()
        cls.load(json.loads(state))
        return cls

    def get_dependencies(self) -> Set[T]:
        if getattr(self, "ctx") is None:
            raise RuntimeError("Node must be created with a context.")
        deps_node = set()
        for pin in self._pins.values():
            if pin.direction == Direction.INPUT:
                for pin_id in pin.links:
                    pin = self.ctx.get_pin(pin_id)
                    deps_node.add(self.ctx.get_node(pin.owning_node))
        return deps_node


class AsyncAction(NodeBase):
    pass


if __name__ == "__main__":

    class MyNode(NodeBase):
        def __init__(self, name: Optional[str] = None) -> None:
            super().__init__(name)
            self.inp1 = Pin()
            self.inp2 = Pin()
            self.inp3 = Pin()
            self.output = Pin(direction=Direction.OUTPUT)

    class MyNode2(MyNode):
        def __init__(self, name: Optional[str] = None) -> None:
            super().__init__(name)
            self.input = Pin()
            self.output = Pin(direction=Direction.OUTPUT)

    node = MyNode(name="MyNode")

    print("==> dump")
    data = node.dump()
    print(data)

    print("==> load")
    data["name"] = "loaded"
    node = node.load(data)
    print(node)

    print("==> dumps")
    data = node.dumps()
    print(data)

    print("==> loads")
    node = MyNode.loads(data)
    print(node)

    print("==> MyNode2")
    node2 = MyNode2(name="MyNode2")
    node2.input.link(node.output)

    # print(node2.get_dependencies())

# class GNode(metaclass=ABCMeta):
#     _version: int = 1

#     def __init__(
#         self,
#         name: str,
#     ):
#         self._ctx: dict = None
#         self._name = name
#         self._pins: OrderedDict[str, FPin] = {}
#         self._schema = FNodeSchema(
#             name=f"{name}.schema",
#             description="A simple tutorial User Interface for Nodes.",
#         )
#         self.__allocate_default_pins()

#     def __allocate_default_pins(self) -> None:
#         """Allocate default pins when the node is instantiated."""
#         self.add_pin(FPin("output", direction=EDirection.OUTPUT))
#         self._input_bindings()

#     @abstractmethod
#     def _input_bindings(self) -> None:
#         pass

#     # def _autowire_new_node(self, weak_pin: ReferenceType["FPin"]):
#     #     """用于在创建新 Node 后，自动将其与指定的 Pin 连接。如果需要，应在创建新 Node 后调用。"""
#     #     pass

#     @property
#     def name(self) -> str:
#         return self._name

#     # def __setattr__(self, __name: str, __value: Any) -> None:
#     #     # super().__setattr__("_schema", OrderedDict())
#     #     super().__setattr__("state", OrderedDict())
#     #     super().__setattr__("_forward_hooks", OrderedDict())
#     #     super().__setattr__("_forward_hooks_with_kwargs", OrderedDict())

#     #     if isinstance(__value, GNode):
#     #         nodes = self.__dict__.get("_nodes")
#     #         if nodes is None:
#     #             nodes = self.__dict__["_nodes"] = OrderedDict()

#     @property
#     def pins(self) -> Dict[str, FPin]:
#         return self._pins

#     def build(self, ctx: dict) -> None:
#         """依赖检查"""
#         self._ctx = ctx

#     def setup(self):
#         """初始化赋值"""

#     def reset(self):
#         self._schema.status = ENodeStatus.Pending

#     @functools.lru_cache()
#     def get_dependencies(self) -> Set[ReferenceType["GNode"]]:
#         deps_node = set()
#         for pin in self._pins.values():
#             if pin.direction == EDirection.INPUT:
#                 for link in pin.links:
#                     deps_node.add(link.owning_node)
#         return deps_node

#     def add_pin(self, pin: FPin) -> None:
#         if pin.name in self._pins:
#             raise ValueError("Pin name already exists.")
#         pin.owning_node = weakref.ref(self)
#         self._schema.pins.add(pin)
#         self._pins[pin.name] = pin
#         self.get_dependencies.cache_clear()

#     async def _execute(self):
#         assert self._ctx is not None, "Context is not built yet."

#         # if self._schema.status == ENodeStatus.Pending:
#         await self.execute()

#         if self._schema.status == ENodeStatus.Finished:
#             for pin in self.pins.values():
#                 if pin.direction != EDirection.OUTPUT:
#                     continue
#                 for link_pin in pin.links:
#                     if link_pin.direction != EDirection.INPUT:
#                         continue
#                     link_pin.value = pin.value

#     @abstractmethod
#     async def execute(self) -> None:
#         pass

#     def serialize(self):
#         return self._schema.to_dict()


# PyTorch隐式注册子模块的过程主要依赖于其内部对`nn.Module`类及其相关属性的操作。具体来说，当你定义一个`nn.Module`的子类，并在其构造函数中通过赋值操作（如`self.some_module = SomeOtherModule()`）添加子模块时，PyTorch会隐式地完成以下几个步骤来注册这些子模块：

# 1. **`__setattr__`方法的重写**：
#    在PyTorch的`nn.Module`类中，`__setattr__`方法被重写以处理对模块属性的赋值操作。当你尝试给模块的一个属性赋值时，如果这个属性值是一个`nn.Module`的实例（即子模块），`__setattr__`方法会检查这个值，并将其添加到模块的`_modules`字典中。这一步是隐式的，因为用户不需要显式调用任何注册方法。

# 2. **`_modules`字典的更新**：
#    `_modules`是一个`OrderedDict`，它存储了模块的所有直接子模块，键是子模块的名称（即属性名），值是子模块本身。当你在构造函数中为新创建的子模块分配一个属性名时，PyTorch会自动将这个子模块及其名称添加到这个字典中。这样，PyTorch就能够跟踪模块的完整层次结构。

# 3. **参数的自动注册**：
#    除了子模块外，`nn.Module`还负责注册其所有参数。当你定义了一个包含参数（如权重和偏置）的层（这些层本身也是`nn.Module`的实例）时，这些参数会自动成为外部`nn.Module`实例的一部分。与子模块类似，这些参数的注册也是隐式的。你可以通过调用`.parameters()`方法来访问模块及其所有子模块的所有参数。

# 4. **递归行为**：
#    由于`nn.Module`的设计支持嵌套模块，因此当子模块本身也包含子模块时，这种隐式注册的过程会递归地应用到整个模型结构中。每当一个子模块被添加到父模块中时，它也会检查并注册自己的子模块（如果有的话），从而形成一个完整的树状结构。

# 5. **使用场景**：
#    这种隐式注册机制使得在PyTorch中构建复杂的神经网络变得非常简单和直观。你只需要定义模块类，并在其构造函数中添加所需的层，PyTorch就会自动为你处理模块的注册和参数管理。这使得你能够专注于实现网络的逻辑，而不是担心如何跟踪和组织这些组件。

# 总结来说，PyTorch通过重写`nn.Module`类的`__setattr__`方法，并利用`_modules`字典来隐式地注册子模块。这种设计简化了模型的构建过程，并使得PyTorch模型具有高度可定制性和灵活性。


# class Schema(BaseModel):
#     name: str
#     description: str = ""
#     pins: List[str] = []


# class SchemaNode(Schema):
#     type: str = "node"
#     pins: Dict[str, Optional["FPin"]] = Field(default_factory=dict)

#     def __init__(self):
#         super().__init__()
