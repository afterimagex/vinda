import traceback
import weakref
from abc import ABC
from collections import OrderedDict
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

from easydict import EasyDict


# is uworld
class UContext:
    def __init__(self):
        self._caches = EasyDict()
        self._components: Dict[str, weakref.ReferenceType[UComponent]] = EasyDict()

    #####################
    #      COMPONENT    #
    #####################

    def add_component(self, cmp: "UComponent"):
        if cmp in self._components:
            raise KeyError("component '{}' already exists".format(cmp))
        self._components[cmp.name] = weakref.ref(cmp)

    def get_component(self, name: str):
        cmp_ref = self._components.get(name)
        if cmp_ref is None:
            return None
        return cmp_ref()

    #####################
    #      EXTRAS       #
    #####################

    def get(self, key):
        return self._caches.get(key)

    def set(self, key, value):
        self._caches[key] = value

    #####################
    #      Function     #
    #####################

    def tick(self):
        pass

    def destroy(self):
        self._caches.clear()
        self._components.clear()


class UObject(ABC):

    def __init__(self, name: Optional[str] = None, ctx: Optional[UContext] = None):
        self._ctx = ctx
        self._name = name if name else self.__class__.__name__

    @property
    def name(self) -> str:
        return self._name

    def attach(self, context: UContext) -> "UObject":
        self._ctx = context
        return self

    def setup(self):
        pass

    def on_begin_play(self):
        pass

    def on_after_play(self):
        pass

    def on_begin_tick(self):
        pass

    def tick(self):
        pass

    def on_after_tick(self):
        pass

    def on_destroy(self):
        pass

    def finally_destroy(self):
        pass


class UModule(UObject):

    def __init__(self, name: str = None, childs: Optional[List["UModule"]] = None):
        super(UModule, self).__init__(name)
        self._childs: OrderedDict[str, UModule] = OrderedDict()  # save module instance
        self._modules: OrderedDict[str, weakref.ReferenceType[UModule]] = (
            OrderedDict()
        )  # save module reference
        self.add_modules(childs)

    def add_module(self, name: str, module: "UModule") -> None:
        r"""Adds a child module to the current module.

        The module can be accessed as an attribute using the given name.

        Args:
            name (string): name of the child module. The child module can be
                accessed from this module using the given name
            module (Module): child module to be added to the module.
        """
        if not isinstance(module, UModule):
            raise TypeError(f"{module.__class__.__name__} is not a UModule subclass")
        elif not isinstance(name, str):
            raise TypeError(f"module name should be a string. Got {type(name)}")
        elif name in self._modules:
            raise KeyError(f"attribute '{name}' already exists")
        elif "." in name:
            raise KeyError('module name can\'t contain "."')
        elif name == "":
            raise KeyError('module name can\'t be empty string ""')
        if weakref.getweakrefcount(module) == 0:
            self._childs[name] = module
        self._modules[name] = weakref.ref(module)

    def add_modules(self, modules: List["UModule"]) -> None:
        if not isinstance(modules, list) or len(modules) == 0:
            return
        for module in modules:
            self.add_module(module.name, module)

    def children(self) -> Iterator["UModule"]:
        r"""Returns an iterator over immediate children modules.

        Yields:
            Module: a child module
        """
        for _, module in self.named_children():
            yield module

    def named_children(self) -> Iterator[Tuple[str, "UModule"]]:
        memo = set()
        for name, module_ref in self._modules.items():
            if module_ref is not None and module_ref not in memo:
                memo.add(module_ref)
                module = module_ref()
                yield name, module

    def attach(self, ctx: UContext):
        for module in self.children():
            module.attach(ctx)
        self.attach(ctx)
        return self

    def _setup(self):
        for module in self.children():
            module._setup()
        self.setup()

    def _on_begin_play(self):
        for module in self.children():
            module._on_begin_play()
        self.on_begin_play()

    def _on_after_play(self):
        for module in self.children():
            module._on_after_play()
        self.on_after_play()

    def _on_begin_tick(self):
        for module in self.children():
            module._on_begin_tick()
        self.on_begin_tick()

    def _on_after_tick(self):
        for module in self.children():
            module._on_after_tick()
        self.on_after_tick()

    def _tick(self):
        for module in self.children():
            module._tick()
        self.tick()

    def _on_destroy(self):
        for module in self.children():
            module._on_destroy()
        self.on_destroy()

    def _finally_destroy(self):
        for module in self.children():
            module._finally_destroy()
        self.finally_destroy()
        self._modules.clear()
        self._childs.clear()


class UComponent(UModule):

    def _setup(self):
        super()._setup()
        self._ctx.add_component(self)


class RedisComponent(UComponent):
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379) -> None:
        super().__init__()
        self.redis_host = redis_host
        self.redis_port = redis_port

    def setup(self):
        print("setup redis")
        # self.redis = redis.Redis(host=self.redis_host, port=self.redis_port)

    def tick(self):
        print("redis tick")


class Runner(UModule):
    def __init__(
        self, name: str = "runner", childs: List[UModule] | None = None
    ) -> None:
        super().__init__(name, childs)
        self._running = True

    def run(self):
        try:
            self._setup()
            self._on_begin_play()
            while self._running:
                self._on_begin_tick()
                self._tick()
                self._on_after_tick()
            self._on_after_play()
        except Exception as e:
            traceback.print_exc()
        finally:
            self._on_destroy()
            self._finally_destroy()

    def finally_destroy(self):
        super().finally_destroy()
        self._ctx.destroy()


# if __name__ == "__main__":
#     app = App(
#         childs=[
#             RedisComponent(),
#             CeleryComponent(),
#         ]
#     )
#     print(1)
#     app.run()
