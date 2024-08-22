import weakref
from abc import ABC
from collections import OrderedDict
from typing import Iterator, List, Optional, Set, Tuple, TypeVar

T = TypeVar("T", bound="UObject")


class UObject(ABC):
    """
    UObject 类是 Unreal 引擎中所有对象的基类，但它并不具备 Tick 和 BeginPlay 的功能。
    UObject 主要是一个用于对象管理和垃圾回收的基础类。
    UObject 是Unreal Engine中所有可序列化对象的基类。
    几乎所有在Unreal Engine中使用的类（如Actor、Component、Material等）都继承自 UObject。
    UObject 提供了对象反射、序列化、垃圾回收等核心功能。
    这意味着你可以通过Unreal的编辑器来编辑这些对象的属性，并且它们的状态可以被保存到磁盘上，
    以便在程序重启时恢复。
    """

    def __init__(self, name: Optional[str] = None) -> None:
        self._name = name if name else f"{self.__class__.__name__}_{id(self)}"
        self._children: OrderedDict[str, weakref.ReferenceType[T]] = OrderedDict()

    @property
    def name(self) -> str:
        return self._name

    def is_tickable(self) -> bool:
        return False

    def add_child(self, child: T) -> None:
        """添加一个子对象到当前对象。

        Args:
            child (T): 要添加的 UObject 子类实例。

        Raises:
            TypeError: 如果 child 不是 UObject 子类。
            KeyError: 如果 child 的名称已存在或为空/包含非法字符。
        """
        if not isinstance(child, UObject):
            raise TypeError(f"{child.__class__.__name__} is not a UObject subclass")
        if child.name in self._children:
            raise KeyError(f"Child with name '{child.name}' already exists")
        if not child.name:
            raise KeyError('Child name cannot be empty string ""')
        if "." in child.name:
            raise KeyError('Child name cannot contain "."')
        # 添加 weakref 以避免循环引用问题
        self._children[child.name] = weakref.ref(child)

    def remove_child(self, child_name: str):
        """从当前对象中移除一个子对象"""
        if child_name in self._children:
            self._children.pop(child_name)

    def add_children(self, children: List[T]) -> None:
        """添加多个子对象到当前对象。

        Args:
            childs (List[UObject]): 要添加的子对象列表。
        """
        for child in children:
            self.add_child(child)

    def named_children(self) -> Iterator[Tuple[str, T]]:
        for name, child_ref in self._children.items():
            child = child_ref()
            if child is not None:
                yield name, child

    def traverse(self):
        """遍历并打印对象树"""
        pass

    def find_child(self, path: str) -> Optional[T]:
        """
        通过路径获取子对象。

        参数:
            path (str): 子对象的路径，使用点(.)分隔每个层级。

        返回:
            Optional[T]: 找到的子对象，或 None 如果未找到。
        """
        parts = path.split(".")
        current = self
        for part in parts:
            if part not in current._children:
                return None  # 路径中的某个环节不存在
            current = current._children[part]()  # 使用 weakref 获取实际对象
            if current is None:
                # 如果 weakref 返回 None，说明对象已经被垃圾回收
                return None
        return current


class FTickableObject(UObject):

    def tick(self, delta_time: float) -> None:
        pass

    def is_tickable(self) -> bool:
        return True


class Test(UObject):
    pass


if __name__ == "__main__":

    o1 = Test("o1")
    o2 = Test("o2")
    o3 = Test("o2")
    o4 = Test("o4")

    o1.add_child(o2)
    o2.add_child(o3)
    o3.add_child(o4)

    for name, child in o1.named_children():
        print(name, child)

    print(o1.find_child("o2.o2").name)
