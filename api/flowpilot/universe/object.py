import asyncio
from abc import ABC
from typing import Optional

from flowpilot.common.module import Module


class UObject(Module):
    """
    module 类是 Unreal 引擎中所有对象的基类，但它并不具备 Tick 和 BeginPlay 的功能。
    module 主要是一个用于对象管理和垃圾回收的基础类。
    module 是Unreal Engine中所有可序列化对象的基类。
    几乎所有在Unreal Engine中使用的类（如Actor、Component、Material等）都继承自 module。
    module 提供了对象反射、序列化、垃圾回收等核心功能。
    这意味着你可以通过Unreal的编辑器来编辑这些对象的属性，并且它们的状态可以被保存到磁盘上，
    以便在程序重启时恢复。
    """

    category: Optional[str] = None

    def _destroy(self):
        """标记待销毁"""
        pass


class ChildMethodInvokerMixin(ABC):
    """LifecycleMixin"""

    async def _call_children(self: UObject, method_name: str, *args, **kwargs):
        """Helper to gather async calls to children methods"""
        tasks = [
            getattr(child, method_name, self._noop)(*args, **kwargs)
            for _, child in self.named_children()
        ]
        tasks.append(getattr(self, method_name, self._noop)(*args, **kwargs))
        await asyncio.gather(*tasks)

    async def _noop(self):
        """Default no-op async method"""
        pass

    async def setup(self):
        """on_setup"""
        await self._call_children("setup")

    async def begin_play(self):
        """on_begin_play"""
        await self._call_children("begin_play")

    async def after_play(self):
        """on_after_play"""
        await self._call_children("after_play")

    async def begin_tick(self):
        await self._call_children("begin_tick")

    async def tick(self, delta_time: float, event_type=None):
        await self._call_children("tick", delta_time)

    async def after_tick(self):
        await self._call_children("after_tick")

    async def destroy(self):
        """标记待销毁"""
        await self._call_children("destroy")

    async def finally_destroy(self):
        """销毁前最后一个回调"""
        await self._call_children("finally_destroy")


class World(UObject, ChildMethodInvokerMixin):
    async def setup(self):
        super().setup()
        print("World setup")


if __name__ == "__main__":

    pass
    # o1 = Test2()
    # print(o1)
    # print(o1)
    # o2 = Test()
    # o1.add_module("o2", o2)
    # print(o1)
    # o2 = Test("o2")
    # o3 = Test("o2")
    # o4 = Test("o4")

    # o1.add_module(o2)
    # o2.add_module(o3)
    # o3.add_module(o4)

    # for name, child in o1.named_children():
    #     print(name, child)

    # print(o1.find_child("o2.o2").name)
