import asyncio
import json
import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from flowpilot.common.easytag import EasyTag
from flowpilot.universe.core import (
    AActor,
    Config,
    UEngine,
    UWorld,
    get_argparser_config,
)
from flowpilot.universe.core.message_router import MessageSubsystem
from flowpilot.workflow.executor import GraphExecutor
from flowpilot.workflow.graph import DagGraph
from flowpilot.workflow.nodes import UNODE, NodeBase
from flowpilot.workflow.pin import Direction, Pin


@UNODE()
class MyNode(NodeBase):
    def __init__(self, name: Optional[str] = None) -> None:
        super().__init__(name)
        self.arg1 = Pin()
        self.arg2 = Pin()
        self.out1 = Pin(direction=Direction.OUTPUT)
        self.out2 = Pin(direction=Direction.OUTPUT)

    async def execute(self) -> None:
        date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        arg1_input_node = self.arg1.get_input_node(self.ctx)
        arg2_input_node = self.arg2.get_input_node(self.ctx)
        print(
            f"Node({self.name}) start at {date}, "
            f"arg1 from {arg1_input_node.name if arg1_input_node else 'null'}, value: {self.arg1.value}, "
            f"arg2 from {arg2_input_node.name if arg2_input_node else 'null'}, value: {self.arg2.value} "
        )
        await asyncio.sleep(1)
        self.out1.value = date
        self.out2.value = date


class ExpAction(AActor):
    def __init__(
        self,
        name: str = None,
    ) -> None:
        super().__init__(name)
        self._ready = 0
        self._reg = MessageSubsystem().register_listener(
            EasyTag("ExpAction"), self.action
        )

    def action(self):
        MessageSubsystem().broadcast_message(EasyTag("ExpAction"), self._ready)


class DeployPiplineManager(AActor):

    def __init__(
        self,
        name: str = None,
    ) -> None:
        super().__init__(name)
        with open("graph.json", "r") as f:
            self._graph = DagGraph.loads(f.read())
        self._exe = GraphExecutor(self._graph)

    def begin_play(self):
        super().begin_play()
        self._exe.run_thread()
        self._reg = MessageSubsystem().register_listener()

    def tick(self, delta_time: float):
        super().tick(delta_time)
        for node in self._graph.nodes:
            print(node.name, node.status)

    def execute_task(self):
        if self._use_threads:
            threading.Thread(target=self._http_request, daemon=True).start()
        else:
            self._http_request()

    def _http_request(self):
        print("http request")


if __name__ == "__main__":
    pipline = DeployPiplineManager()

    world = UWorld(actors=[pipline])
    print(world)

    cfg = get_argparser_config(Config)
    cfg.tick_interval = 0.1
    engine = UEngine(cfg, world)
    engine.loop_until()
