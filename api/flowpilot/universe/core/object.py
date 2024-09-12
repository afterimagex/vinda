import copy
import weakref
from typing import Any, Callable, Dict, Iterator, Optional, Set, Tuple, Type, TypeVar
from uuid import uuid4

from .factory import UCLASS_REGISTRY, UClass, new_uclass

__all__ = [
    "UObject",
]


T = TypeVar("T", bound="UObject")


class UObject(UClass):
    """
    module 类是 Unreal 引擎中所有对象的基类，但它并不具备 Tick 和 BeginPlay 的功能。
    module 主要是一个用于对象管理和垃圾回收的基础类。
    module 是Unreal Engine中所有可序列化对象的基类。
    几乎所有在Unreal Engine中使用的类（如Actor、Component、Material等）都继承自 module。
    module 提供了对象反射、序列化、垃圾回收等核心功能。
    这意味着你可以通过Unreal的编辑器来编辑这些对象的属性，并且它们的状态可以被保存到磁盘上，
    以便在程序重启时恢复。
    """

    id: str
    _objs: Dict[str, Optional["UObject"]]
    _parent_ref: Optional[weakref.ReferenceType]
    _call_super_init: bool = False
    _disallow_child_classes: Tuple[Type]

    def __init__(self, *args, **kwargs) -> None:

        if self._call_super_init is False and bool(kwargs):
            raise TypeError(
                f"{type(self).__name__}.__init__() got an unexpected keyword argument '{next(iter(kwargs))}'"
                ""
            )

        if self._call_super_init is False and bool(args):
            raise TypeError(
                f"{type(self).__name__}.__init__() takes 1 positional argument but {len(args) + 1} were"
                " given"
            )

        super().__setattr__("id", str(uuid4()))
        super().__setattr__("_objs", {})
        super().__setattr__("_parent_ref", None)
        super().__setattr__("_disallow_child_classes", tuple())

        if self._call_super_init:
            super().__init__(*args, **kwargs)

    def add_uobject(self, name: str, uobject: Optional["UObject"]) -> None:
        r"""Add a child uobject to the current uobject.

        The uobject can be accessed as an attribute using the given name.

        Args:
            name (str): name of the child uobject. The child uobject can be
                accessed from this uobject using the given name
            child (uobject): child uobject to be added to the uobject.
        """
        if not isinstance(uobject, UObject):
            raise TypeError(f"{uobject.__class__.__name__} is not a uobject subclass")
        elif not isinstance(name, str):
            raise TypeError(f"uobject name should be a string. Got {name}")
        elif hasattr(self, name) and name not in self._objs:
            raise KeyError(f"attribute '{name}' already exists")
        elif "." in name:
            raise KeyError(f'uobject name can\'t contain ".", got: {name}')
        elif name == "":
            raise KeyError('uobject name can\'t be empty string ""')
        self._objs[name] = uobject
        uobject._parent_ref = weakref.ref(self)

    def __setattr__(self, name: str, value: "UObject") -> None:
        if self._disallow_child_classes:
            if issubclass(
                type(value),
                tuple(
                    UCLASS_REGISTRY.get(uclass_name)
                    for uclass_name in self._disallow_child_classes
                ),
            ):
                raise TypeError(
                    f"forbidden to assign an instance of type "
                    f"'{type(value).__name__}' as a child of '{self.__class__.__name__}'"
                )

        def remove_from(*dicts_or_sets):
            for d in dicts_or_sets:
                if name in d:
                    if isinstance(d, dict):
                        del d[name]
                    else:
                        d.discard(name)

        objs = self.__dict__.get("_objs")
        if isinstance(value, UObject):
            if objs is None:
                raise AttributeError(
                    "cannot assign uobject before module.__init__() call"
                )
            remove_from(self.__dict__)
            value._parent_ref = weakref.ref(self)
            objs[name] = value
        elif objs is not None and name in objs:
            if value is not None:
                raise TypeError(
                    f"cannot assign '{value.__class__.__name__}' as child uobject '{name}' "
                    "(uobject or None expected)"
                )
            objs[name] = value
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name: str) -> Any:
        if "_objs" in self.__dict__:
            objs = self.__dict__["_objs"]
            if name in objs:
                return objs[name]
        raise AttributeError(
            f"'{type(self).__name__}' uobject has no attribute '{name}'"
        )

    def __delattr__(self, name):
        if name in self._objs:
            del self._objs[name]
        else:
            super().__delattr__(name)

    def objects(self) -> Iterator["UObject"]:
        r"""Return an iterator over all objects in the network.

        Yields:
            UObject: a object in the network

        Note:
            Duplicate modules are returned only once. In the following
            example, ``l`` will be returned only once.

        Example::

            >>> l = nn.Linear(2, 2)
            >>> net = nn.Sequential(l, l)
            >>> for idx, m in enumerate(net.modules()):
            ...     print(idx, '->', m)

            0 -> Sequential(
              (0): Linear(in_features=2, out_features=2, bias=True)
              (1): Linear(in_features=2, out_features=2, bias=True)
            )
            1 -> Linear(in_features=2, out_features=2, bias=True)

        """
        for _, obj in self.named_objects():
            yield obj

    def named_objects(
        self,
        memo: Optional[Set["UObject"]] = None,
        prefix: str = "",
        remove_duplicate: bool = True,
    ):
        r"""Return an iterator over all modules in the network, yielding both the name of the module as well as the module itself.

        Args:
            memo: a memo to store the set of modules already added to the result
            prefix: a prefix that will be added to the name of the module
            remove_duplicate: whether to remove the duplicated module instances in the result
                or not

        Yields:
            (str, Module): Tuple of name and module

        Note:
            Duplicate modules are returned only once. In the following
            example, ``l`` will be returned only once.

        Example::

            >>> l = nn.Linear(2, 2)
            >>> net = nn.Sequential(l, l)
            >>> for idx, m in enumerate(net.named_modules()):
            ...     print(idx, '->', m)

            0 -> ('', Sequential(
              (0): Linear(in_features=2, out_features=2, bias=True)
              (1): Linear(in_features=2, out_features=2, bias=True)
            ))
            1 -> ('0', Linear(in_features=2, out_features=2, bias=True))

        """
        if memo is None:
            memo = set()
        if self not in memo:
            if remove_duplicate:
                memo.add(self)
            yield prefix, self
            for name, obj in self._objs.items():
                if obj is None:
                    continue
                subject_prefix = prefix + ("." if prefix else "") + name
                yield from obj.named_objects(memo, subject_prefix, remove_duplicate)

    def apply(self: T, fn: Callable[["UObject"], None]) -> T:
        r"""Apply ``fn`` recursively to every submodule (as returned by ``.children()``) as well as self.

        Typical use includes initializing the parameters of a model
        (see also :ref:`nn-init-doc`).

        Args:
            fn (:class:`UObject` -> None): function to be applied to each submodule

        Returns:
            Module: self

        """
        for obj in self.children():
            obj.apply(fn)
        fn(self)
        return self

    def children(self) -> Iterator["UObject"]:
        r"""Return an iterator over immediate children modules.

        Yields:
            UObject: a child uobject
        """
        for _, obj in self.named_children():
            yield obj

    def named_children(self) -> Iterator[Tuple[str, "UObject"]]:
        r"""Return an iterator over immediate children modules, yielding both the name of the module as well as the module itself.

        Yields:
            (str, Module): Tuple containing a name and child module

        Example::

            >>> # xdoctest: +SKIP("undefined vars")
            >>> for name, module in model.named_children():
            >>>     if name in ['conv4', 'conv5']:
            >>>         print(module)

        """
        memo = set()
        for name, obj in self._objs.items():
            if obj is not None and obj not in memo:
                memo.add(obj)
                yield name, obj

    def parent(self) -> Optional["UObject"]:
        r"""Returns the immediate parent of this module."""
        return self._parent_ref()

    def dump(self) -> dict:
        state = copy.deepcopy(self.__dict__)
        state["uclass"] = self.__class__.__name__
        state["objects"] = {k: v.dump() for k, v in state["_objs"].items()}
        state.pop("_objs")
        return state

    def load(self, state: dict) -> T:
        state = copy.deepcopy(state)
        assert self.__class__.__name__ == state["uclass"]
        for key in state.keys():
            if key == "objects":
                self.clear()
                for name, obj_state in state[key].items():
                    if name in self._objs:
                        self._objs[name].load(obj_state)
                    else:
                        obj = new_uclass(obj_state["uclass"]).load(obj_state)
                        self.add_object(name, obj)
            else:
                super().__setattr__(key, state[key])
        return self


# class ChildMethodInvokerMixin(ABC):
#     """LifecycleMixin"""

#     async def _call_children(self: UObject, method_name: str, *args, **kwargs):
#         """Helper to gather async calls to children methods"""
#         tasks = [
#             getattr(child, method_name, self._noop)(*args, **kwargs)
#             for _, child in self.named_children()
#         ]
#         tasks.append(getattr(self, method_name, self._noop)(*args, **kwargs))
#         await asyncio.gather(*tasks)

#     async def _noop(self):
#         """Default no-op async method"""
#         pass

#     async def setup(self):
#         """on_setup"""
#         await self._call_children("setup")

#     async def begin_play(self):
#         """on_begin_play"""
#         await self._call_children("begin_play")

#     async def after_play(self):
#         """on_after_play"""
#         await self._call_children("after_play")

#     async def begin_tick(self):
#         await self._call_children("begin_tick")

#     async def tick(self, delta_time: float, event_type=None):
#         await self._call_children("tick", delta_time)

#     async def after_tick(self):
#         await self._call_children("after_tick")

#     async def destroy(self):
#         """标记待销毁"""
#         await self._call_children("destroy")

#     async def finally_destroy(self):
#         """销毁前最后一个回调"""
#         await self._call_children("finally_destroy")


# class World:
#     def __init__(self) -> None:
#         self._actors = {}

#     async def begin_play(self):
#         print("world begin_play")

#     def spawn_actor(self, actor: AActor):
#         self.add_module("actor", actor)

#     def tick(self):
#         for m in self.modules():
#             pass


# class GameEngine:
#     def __init__(self) -> None:
#         self._world = World()

#         actor = AActor()
#         self._world.spawn_actor(actor)

#         self._is_running = False

#     def run(self):
#         self._is_running = True
#         while self._is_running:
#             self._world.tick()


if __name__ == "__main__":

    obj = UObject()

    print(obj)

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
