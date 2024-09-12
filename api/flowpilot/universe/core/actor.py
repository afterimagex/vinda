from typing import TYPE_CHECKING, List, Optional

from .component import UActorComponent
from .event import WorldEventMixin
from .factory import UCLASS
from .object import UObject

if TYPE_CHECKING:
    from .component import UActorComponent
    from .world import FWorldContext


__all__ = ["AActor"]


@UCLASS(category="Actor")
class AActor(UObject, WorldEventMixin):
    """
    AActor 是 Unreal Engine 中具备 BeginPlay 和 Tick 等功能的最基础类。
    AActor 提供了丰富的生命周期管理功能，包括 BeginPlay、Tick、EndPlay 等。
    """

    ctx: Optional["FWorldContext"]
    name: Optional[str]
    _components: List["UActorComponent"]

    def __init__(
        self,
        name: Optional[str] = None,
    ):
        UObject.__init__(self)
        WorldEventMixin.__init__(self)
        super().__setattr__("ctx", None)
        super().__setattr__(
            "name", f"{self.__class__.__name__}_{id(self)}" if name is None else name
        )

    def __setattr__(self, name: str, value: UObject) -> None:
        super().__setattr__(name, value)
        if isinstance(value, (AActor, UActorComponent)):
            value.name = f"{self.name}.{value.name}"

    def add_component(self, component: "UActorComponent"):
        self.add_uobject(component.name, component)

    def get_world(self):
        return self.ctx.world()
