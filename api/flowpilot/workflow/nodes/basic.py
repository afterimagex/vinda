# ------------------------------------------------------------------------
# Copyright (c) 2017-present, Pvening. All Rights Reserved.
#
# Licensed under the BSD 2-Clause License,
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://opensource.org/licenses/BSD-2-Clause
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------

# todo: 改成插件形式类似llama-index-

# import asyncio

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional

from flowpilot.workflow.nodes.base import NodeBase
from flowpilot.workflow.nodes.factory import UNODE

# import aiohttp
from flowpilot.workflow.pins import Direction, Pin

# @UNODE()
# class StartAction(NodeBase):
#     def __init__(self, name: str | None = None) -> None:
#         super().__init__(name)
#         self.output = ExecPin(direction=Direction.OUTPUT)

#     async def execute(self) -> None:
#         pass

#     #     inp = input("Please enter something: ")
#     #     self.pins["output"].value = inp
#     # print(f'{self.name}: Input({inp}), Output({self.pins["output"].value})')


# @UNODE()
# class BranchAction(NodeBase):
#     def __init__(self, name: str | None = None) -> None:
#         super().__init__(name)
#         self.input = PinBase()
#         self.output1 = PinBase(direction=Direction.OUTPUT)
#         self.output2 = PinBase(direction=Direction.OUTPUT)

#     async def execute(self):
#         pass


# @UNODE()
# class EndAction(NodeBase):

#     def __init__(self, name: str | None = None) -> None:
#         super().__init__(name)
#         self.input = PinBase()

#     async def execute(self):
#         pass

#     #     arg1 = self.pins["merge"].value
#     #     self.pins["output"].value = "end"
#     #     print(f'{self.name}: Input({arg1}), Output({self.pins["output"].value})')


# @UNODE()
class PyCodeNode(NodeBase):

    def __init__(
        self,
        name: str | None = None,
        *,
        source: str,
        output_fields: Optional[List[str]] = None
    ) -> None:
        super().__init__(name)
        self.exec = Pin()
        self.then = Pin(direction=Direction.OUTPUT)
        self.vars = Pin()
        self.retv = Pin(direction=Direction.OUTPUT)
        self.source = source
        self.output_fields = output_fields

    def exec_code(self):
        namespace = {}
        exec(self.source, deepcopy(self.vars.value), namespace)
        if self.output_fields is None:
            return namespace
        for key in list(namespace.keys()):
            if key not in self.output_fields:
                del namespace[key]
        return namespace

    def _execute(self):
        self.retv.value = self.exec_code()


class EventNode(NodeBase):
    def __init__(
        self,
        name: str | None = None,
        *,
        source: str,
        output_fields: Optional[List[str]] = None
    ) -> None:
        super().__init__(name)
        self.exec = Pin()
        self.then = Pin(direction=Direction.OUTPUT)
        self.vars = Pin()
        self.retv = Pin(direction=Direction.OUTPUT)
        self.source = source
        self.output_fields = output_fields


# @UNODE()
# class BashAction(NodeBase):
#     def __init__(self, name: str | None = None) -> None:
#         super().__init__(name)
#         self.args = Pin()
#         self.output = Pin(direction=Direction.OUTPUT)

#     async def execute(self):
#         pass

#     #     arg1 = self.pins["arg1"].value
#     #     self.pins["output"].value = self.name
#     #     await asyncio.sleep(1)
#     #     print(f'{self.name}: Input({arg1}), Output({self.pins["output"].value})')


# @UNODE()
# class HttpOperator(NodeBase):
#     def __init__(self, name: str | None = None) -> None:
#         super().__init__(name)
#         self.args = Pin()
#         self.output = Pin(direction=Direction.OUTPUT)

#     async def execute(self) -> None:
#         pass

#     async def _send_request(self) -> None:
#         async with aiohttp.ClientSession() as session:
#             # tasks = [fetch(session, url) for url in urls]
#             tasks = []
#             responses = await asyncio.gather(*tasks)

#             for response in responses:
#                 print(response)


# class EventNode(NodeBase):
#     def __init__(self, name: str | None = None) -> None:
#         super().__init__(name)
#         self.exec = new_pin("ExecPin")
#         self.then = new_pin("ExecPin", direction=Direction.OUTPUT)

#         MessageSubsystem().register_listener("Actor.ReceiveBeginPlay", self.execute)

#     def execute(self):
#         pass


# class FunctionNode(NodeBase):
#     def __init__(self, name: str | None = None, *, method: str) -> None:
#         super().__init__(name)
#         self.exec = new_pin("ExecPin")
#         self.then = new_pin("ExecPin", direction=Direction.OUTPUT)

#         self.target = new_pin("ObjectPin", "self")
#         self.output = new_pin("NamePin", "return_value", direction=Direction.OUTPUT)

#         self._method = method

#     def execute(self) -> None:
#         self.output.value = getattr(self.target.value, self._method)()


# def function(name: str | None = None, *, target: Any, method: str) -> Any:
#     fn = FunctionNode(name, method=method)
#     fn.target.value = target
#     return fn


# class ForEachLoopNode(NodeBase):
#     def __init__(self, name: str | None = None) -> None:
#         super().__init__(name)
#         self.exec = new_pin("ExecPin", "Exec")
#         self.then = new_pin("ListPin", "Array")
#         self.then = new_pin("ExecPin", "LoopBody", direction=Direction.OUTPUT)
#         self.then = new_pin("NamePin", "Element", direction=Direction.OUTPUT)
#         self.then = new_pin("IntegerPin", "Index", direction=Direction.OUTPUT)
#         self.then = new_pin("ExecPin", "Completed", direction=Direction.OUTPUT)

#         self.iterable = new_pin("IterablePin")
#         self.item = new_pin("ItemPin", direction=Direction.OUTPUT)


if __name__ == "__main__":
    n1 = PyCodeNode(
        "n1",
        source="""
def hashmd5():
    import hashlib
    md5_hash = hashlib.md5()
    md5_hash.update(f"reflow_sts_{userid}_{authsk}_{timestamp}".encode("utf-8"))
    return md5_hash.hexdigest()
md5 = hashmd5()
""",
        output_fields=["md5"],
    )

    n1.vars.value = {"userid": "123456", "authsk": "123456", "timestamp": "123456"}

    n2 = PyCodeNode(
        "n2",
        source="""
print(md5)
""",
    )

    n1.then.link(n2.exec)
    n1.retv.link(n2.vars)

    import json

    n1.execute()
    print(json.dumps(n1.dump(), indent=4))

    n2.vars.value = n1.retv.value

    n2.execute()

    print(n2)
