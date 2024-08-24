import functools
import uuid
import weakref
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
)
from weakref import ReferenceType

from flowpilot.workflow.pin import EDirection, FPin

if TYPE_CHECKING:
    from weakref import ReferenceType

    from flowpilot.workflow.graph import GGraph


class ENodeStatus(Enum):
    Initial = 1
    Pending = 2
    Running = 3
    Paused = 4
    Finished = 5
    Failed = 6
    Canceled = 7
    Unknown = 8


@dataclass
class FNodeSchema:
    name: str = ""
    pins: Set["FPin"] = field(default_factory=set)
    owning_graph: ReferenceType["GGraph"] = None
    status: ENodeStatus = ENodeStatus.Initial
    position: Tuple[float, float] = (0.0, 0.0)
    metadata: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    _id: uuid.UUID = field(default_factory=uuid.uuid4)

    def to_dict(self) -> dict:
        return asdict(self)


class StateMachine:
    pass


class pin.Container:
    pass


class GNode(metaclass=ABCMeta):

    def __init__(
        self,
        name: str,
    ):
        self._ctx: dict = None
        self._name = name
        self._pins: OrderedDict[str, FPin] = {}
        self._schema = FNodeSchema(
            name=f"{name}.schema",
            description="A simple tutorial User Interface for Nodes.",
        )
        self.__allocate_default_pins()

    def __allocate_default_pins(self) -> None:
        """Allocate default pins when the node is instantiated."""
        self.add_pin(FPin("output", direction=EDirection.OUTPUT))
        self._input_bindings()

    @abstractmethod
    def _input_bindings(self) -> None:
        pass

    # def _autowire_new_node(self, weak_pin: ReferenceType["FPin"]):
    #     """用于在创建新 Node 后，自动将其与指定的 Pin 连接。如果需要，应在创建新 Node 后调用。"""
    #     pass

    @property
    def name(self) -> str:
        return self._name

    def __setattr__(self, __name: str, __value: Any) -> None:
        # super().__setattr__("_schema", OrderedDict())
        super().__setattr__("state", OrderedDict())
        super().__setattr__("_forward_hooks", OrderedDict())
        super().__setattr__("_forward_hooks_with_kwargs", OrderedDict())

        if isinstance(__value, GNode):
            nodes = self.__dict__.get("_nodes")
            if nodes is None:
                nodes = self.__dict__["_nodes"] = OrderedDict()

    @property
    def pins(self) -> Dict[str, FPin]:
        return self._pins

    def build(self, ctx: dict) -> None:
        """依赖检查"""
        self._ctx = ctx

    def setup(self):
        """初始化赋值"""

    def reset(self):
        self._schema.status = ENodeStatus.Pending

    @functools.lru_cache()
    def get_dependencies(self) -> Set[ReferenceType["GNode"]]:
        deps_node = set()
        for pin in self._pins.values():
            if pin.direction == EDirection.INPUT:
                for link in pin.links:
                    deps_node.add(link.owning_node)
        return deps_node

    def add_pin(self, pin: FPin) -> None:
        if pin.name in self._pins:
            raise ValueError("Pin name already exists.")
        pin.owning_node = weakref.ref(self)
        self._schema.pins.add(pin)
        self._pins[pin.name] = pin
        self.get_dependencies.cache_clear()

    async def _execute(self):
        assert self._ctx is not None, "Context is not built yet."

        # if self._schema.status == ENodeStatus.Pending:
        await self.execute()

        if self._schema.status == ENodeStatus.Finished:
            for pin in self.pins.values():
                if pin.direction != EDirection.OUTPUT:
                    continue
                for link_pin in pin.links:
                    if link_pin.direction != EDirection.INPUT:
                        continue
                    link_pin.value = pin.value

    @abstractmethod
    async def execute(self) -> None:
        pass

    def serialize(self):
        return self._schema.to_dict()


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
