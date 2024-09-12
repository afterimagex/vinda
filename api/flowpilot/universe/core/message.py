import weakref
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from flowpilot.common.easytag import EasyTag
from flowpilot.common.utils import SingletonMeta


class MatchType(Enum):
    EXACT = 1  # 精确匹配
    PARTIAL = 2  # 部分匹配（即标签可以是另一个标签的前缀）


class ListenerHandle:
    id: int

    def __init__(self, subsystem: "MessageSubsystem", channel: EasyTag, id: int):
        self.id = id
        self.channel = channel
        self.subsystem_ref = weakref.ref(subsystem)

    def is_valid(self):
        return self.id != 0

    def unregister(self):
        if subsystem := self.subsystem_ref():
            subsystem.unregister_listener_by_handle(self)
            self.subsystem_ref = None
            self.id = 0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"


@dataclass
class MessageListenerData:
    handle_id: int
    match_type: MatchType
    received_callback: Callable


class MessageSubsystem(metaclass=SingletonMeta):

    _listener_map: Dict[EasyTag, List[MessageListenerData]]

    def __init__(self) -> None:
        self._listener_map = OrderedDict()

    @classmethod
    def get(cls, ctx):
        pass

    def has_instance(self, ctx) -> bool:
        return True

    def deinitialize(self):
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
        entry = MessageListenerData(
            len(self._listener_map[channel]) + 1, match_type, callback
        )
        self._listener_map[channel].append(entry)
        return ListenerHandle(self, channel, entry.handle_id)

    def unregister_listener_by_handle(self, handle: ListenerHandle):
        assert handle.is_valid()
        assert handle.subsystem_ref() is self
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


class SocketMessageSubsystem(metaclass=SingletonMeta):
    _listener_map: Dict[EasyTag, List[MessageListenerData]]
