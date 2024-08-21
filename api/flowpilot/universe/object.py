from abc import ABC
from typing import Optional


class UObject(ABC):
    """
    UObject 类是 Unreal 引擎中所有对象的基类，但它并不具备 Tick 和 BeginPlay 的功能。
    UObject 主要是一个用于对象管理和垃圾回收的基础类。
    """

    def __init__(self, name: Optional[str] = None) -> None:
        self._name = name if name else f"{self.__class__.__name__}_{id(self)}"
