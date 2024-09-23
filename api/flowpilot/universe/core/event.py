import re


class AsyncWorldEventMixin:
    pass


class EventMixin:

    def __init__(self):
        self._tickable = True
        self._has_begun_play = False
        self._pending_kill = False

    def _on_children(self, method_name, *args, **kwargs):
        for obj in self.children():
            if isinstance(obj, EventMixin):
                getattr(obj, method_name)(*args, **kwargs)

    def on_begin_play(self):
        self._on_children("on_begin_play")
        if not self._has_begun_play:
            self._has_begun_play = True
            self.begin_play()

    def on_tick(self, delta_time: float):
        self._on_children("on_tick", delta_time)
        if self._tickable:
            self.tick(delta_time)

    def on_end_play(self, end_play_reason: str):
        self._on_children("on_end_play", end_play_reason)
        self._has_begun_play = False
        self.end_play(end_play_reason)

    def on_finally_destroy(self):
        self._on_children("on_finally_destroy")
        if self._pending_kill:
            self.finally_destroy()

    def begin_play(self):
        """begin_play"""

    def end_play(self, end_play_reason):
        """end_play"""

    def tick(self, delta_time: float):
        """tick"""

    def destroy(self):
        """标记待销毁"""
        self._on_children("on_destroy")
        self._pending_kill = True

    def finally_destroy(self):
        """销毁前最后一个回调"""
        if world := self.ctx.world():
            world.final_remove_actor(self)


def parse_blueprint_script(script):
    nodes = {}
    current_node = None

    # 匹配Begin Object行
    node_pattern = re.compile(
        r'Begin Object Class=/Script/BlueprintGraph\.(\w+) Name="(\w+)"'
    )
    pin_pattern = re.compile(
        r'CustomProperties Pin $PinId=([0-9A-F]+),PinName="(\w+)",(.*?)$'
    )

    for line in script.splitlines():
        # 检查是否为新节点开始
        node_match = node_pattern.match(line)
        if node_match:
            node_type, node_name = node_match.groups()
            current_node = {"type": node_type, "name": node_name, "pins": []}
            nodes[node_name] = current_node
        elif current_node:
            # 检查引脚信息
            pin_match = pin_pattern.search(line)
            if pin_match:
                pin_id, pin_name, pin_properties = pin_match.groups()
                pin_dict = {
                    "id": pin_id,
                    "name": pin_name,
                    "properties": pin_properties,
                }
                current_node["pins"].append(pin_dict)

    return nodes
