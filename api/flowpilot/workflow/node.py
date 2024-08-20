import functools
import uuid
import weakref
from abc import ABCMeta, abstractmethod
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
    Running = 2
    Paused = 3
    Finished = 4
    Failed = 5
    Canceled = 6
    Unknown = 7


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


class GNode(metaclass=ABCMeta):

    def __init__(
        self,
        name: str,
        metadata: Optional[dict] = None,
    ):
        self._ctx: dict = None
        self._name = name
        self._pins: Dict[str, FPin] = {}
        self._schema = FNodeSchema(
            name=f"{name}.schema",
            description="A simple tutorial User Interface for Nodes.",
            metadata=metadata if metadata else {},
        )
        self.__allocate_default_pins()

    def __allocate_default_pins(self) -> None:
        """Allocate default pins when the node is instantiated."""
        self.add_pin(FPin("output", direction=EDirection.OUTPUT))
        self._create_default_pins()

    @abstractmethod
    def _create_default_pins(self) -> None:
        pass

    # def _autowire_new_node(self, weak_pin: ReferenceType["FPin"]):
    #     """用于在创建新 Node 后，自动将其与指定的 Pin 连接。如果需要，应在创建新 Node 后调用。"""
    #     pass

    @property
    def name(self) -> str:
        return self._name

    @property
    def pins(self) -> Dict[str, FPin]:
        return self._pins

    def build(self, _ctx: dict) -> None:
        self._ctx = _ctx

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
        await self.execute()
        for pin in self.pins.values():
            if pin.direction == EDirection.OUTPUT:
                for link_pin in pin.links:
                    if link_pin.direction == EDirection.INPUT:
                        link_pin.value = pin.value

    @abstractmethod
    async def execute(self) -> None:
        pass
