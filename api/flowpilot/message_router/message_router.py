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

import weakref
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Dict, List

from .tags import EasyTag

__all__ = ["MatchType", "ListenerHandle", "MessageRouter"]


class MatchType(Enum):
    EXACT = 1  # 精确匹配
    PARTIAL = 2  # 部分匹配（即标签可以是另一个标签的前缀）


class ListenerHandle:
    id: int

    def __init__(self, router: "MessageRouter", channel: EasyTag, id: int):
        self.id = id
        self.channel = channel
        self.router_ref = weakref.ref(router)

    def is_valid(self):
        return self.id != 0

    def unregister(self):
        if subsystem := self.router_ref():
            subsystem.unregister_listener_handle(self)
            self.router_ref = None
            self.id = 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"


@dataclass
class ListenerData:
    handle_id: int
    match_type: MatchType
    received_callback: Callable


class MessageRouter:

    _listener_map: Dict[EasyTag, List[ListenerData]]

    def __init__(self) -> None:
        self._listener_map = OrderedDict()

    def clear(self):
        self._listener_map.clear()

    def broadcast_message(self, channel: str | EasyTag, *args, **kwargs):
        if isinstance(channel, str):
            channel = EasyTag(tag_name=channel)
        is_initial_tag = True
        while channel and channel.is_valid():
            if plist := self._listener_map.get(channel):
                for entry in plist:
                    if is_initial_tag or (entry.match_type == MatchType.PARTIAL):
                        # todo: type checking
                        entry.received_callback(*args, **kwargs)
            channel = channel.request_direct_parent()
            is_initial_tag = False

    def register_listener(
        self,
        channel: str | EasyTag,
        callback: Callable,
        match_type: MatchType = MatchType.EXACT,
    ) -> ListenerHandle:
        if isinstance(channel, str):
            channel = EasyTag(tag_name=channel)
        if channel not in self._listener_map:
            self._listener_map[channel] = []
        entry = ListenerData(len(self._listener_map[channel]) + 1, match_type, callback)
        self._listener_map[channel].append(entry)
        return ListenerHandle(self, channel, entry.handle_id)

    def unregister_listener_handle(self, handle: ListenerHandle):
        assert handle.is_valid()
        assert handle.router_ref() is self
        self.unregister_listener(handle.channel, handle.id)

    def unregister_listener(self, channel: str | EasyTag, handle_id: int):
        if isinstance(channel, str):
            channel = EasyTag(tag_name=channel)
        if plist := self._listener_map.get(channel):
            for entry in plist:
                if entry.handle_id == handle_id:
                    plist.remove(entry)
            if len(plist) == 0:
                del self._listener_map[channel]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"


# class SocketMessageSubsystem(metaclass=SingletonMeta):
#     _listener_map: Dict[EasyTag, List[MessageListenerData]]
