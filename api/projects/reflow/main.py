import json
import os
import os.path as osp
import sys
import threading
import time
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List

import requests
from flowpilot.universe.core.engine import UEngine
from flowpilot.universe.core.event import WorldEventMixin
from flowpilot.universe.core.object import UObject
from flowpilot.universe.core.world import ULevel, UWorld
from flowpilot.utils.logger import setup_logger
from flowpilot.workflow.nodes import NodeBase
from flowpilot.workflow.nodes.basic import EventNode, FunctionNode, function
from flowpilot.workflow.pins import DictPin, ExecPin, StringPin
from omegaconf import OmegaConf


@dataclass
class Config:
    runtime_class: str = os.getenv("RUNTIME_CLASS", "URuntime")
    tick_interval: float = 0.016


def setup_cfg():
    # load config from file and command-line arguments
    cfg = OmegaConf.merge(
        OmegaConf.create(asdict(Config())), OmegaConf.from_cli(sys.argv[1:])
    )
    return cfg


class NodeGraph(NodeBase):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.begin_play = ExecPin("BeginPlay")


class HttpNode(NodeBase):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.host = StringPin("host")
        self.headers = DictPin("headers")
        self.method = StringPin("method")
        self.data = DictPin("data")

    def execute(self) -> None:
        response = requests.post(
            self.host.value,
            headers=self.headers.value,
            data=json.dumps(self.data.value),
            timeout=10,
        )
        response.raise_for_status()


class PythonNode(NodeBase):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.code = StringPin("code")


class Blackboard(object):
    pass


def main() -> None:
    logger = setup_logger(name="reflow")

    cfg = setup_cfg()
    logger.info(f"Config: {OmegaConf.to_container(cfg)}")

    level = ULevel()

    engine = UEngine(
        cfg,
        UWorld(
            [
                Controller(),
            ]
        ),
    )
    engine.loop_until()


def get_boscer():
    return ""


if __name__ == "__main__":
    cfg = OmegaConf.merge(
        OmegaConf.create(asdict(Config())), OmegaConf.from_cli(sys.argv[1:])
    )
    main()

    fn = FunctionNode("GetBoscer", "get_boscer")
    fn.then.link(FunctionNode("UploadBos", upload_bos))

    blackboard = Blackboard()
    graph = NodeGraph()

    node1 = function(graph.begin_play, target=blackboard, method=blackboard.sf)
    node2 = function(node1.then, target=blackboard, method="submit_task")

    node1 = GetBoscer()
    node2 = UploadBos()
    node3 = SubmitTask()
    node4 = AddWatchTask()

    graph.begin_play.link(node1.exec)
    node1.then.link(node2.exec)
    node2.then.link(node3.exec)
    node3.then.link(node4.exec)

    graph.begin_play.exec()
