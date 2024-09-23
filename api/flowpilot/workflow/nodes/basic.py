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

import asyncio

import aiohttp
from flowpilot.workflow.pin import Direction, Pin

from .base import BaseNode
from .factory import UNODE


@UNODE()
class StartAction(NodeBase):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.output = Pin(direction=Direction.OUTPUT)

    async def execute(self) -> None:
        pass

    #     inp = input("Please enter something: ")
    #     self.pins["output"].value = inp
    # print(f'{self.name}: Input({inp}), Output({self.pins["output"].value})')


@UNODE()
class BranchAction(NodeBase):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.input = Pin()
        self.output1 = Pin(direction=Direction.OUTPUT)
        self.output2 = Pin(direction=Direction.OUTPUT)

    async def execute(self):
        pass


@UNODE()
class EndAction(NodeBase):

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.input = Pin()

    async def execute(self):
        pass

    #     arg1 = self.pins["merge"].value
    #     self.pins["output"].value = "end"
    #     print(f'{self.name}: Input({arg1}), Output({self.pins["output"].value})')


@UNODE()
class PythonAction(NodeBase):

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.arg1 = Pin()
        self.arg2 = Pin()
        self.output = Pin(direction=Direction.OUTPUT)

    async def execute(self):
        pass

    #     arg1 = self.pins["arg1"].value
    #     arg2 = self.pins["arg2"].value
    #     self.pins["output"].value = self.name
    #     await asyncio.sleep(1)
    #     print(f'{self.name}: Input({arg1},{arg2}), Output({self.pins["output"].value})')


@UNODE()
class BashAction(NodeBase):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.args = Pin()
        self.output = Pin(direction=Direction.OUTPUT)

    async def execute(self):
        pass

    #     arg1 = self.pins["arg1"].value
    #     self.pins["output"].value = self.name
    #     await asyncio.sleep(1)
    #     print(f'{self.name}: Input({arg1}), Output({self.pins["output"].value})')


@UNODE()
class HttpOperator(NodeBase):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.args = Pin()
        self.output = Pin(direction=Direction.OUTPUT)

    async def execute(self) -> None:
        pass

    async def _send_request(self) -> None:
        async with aiohttp.ClientSession() as session:
            # tasks = [fetch(session, url) for url in urls]
            tasks = []
            responses = await asyncio.gather(*tasks)

            for response in responses:
                print(response)
