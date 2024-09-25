import hashlib
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
from flowpilot.universe.core.object import UObject
from flowpilot.universe.core.world import ULevel, UWorld
from flowpilot.utils.logger import setup_logger
from flowpilot.workflow.graph import EventGraph
from flowpilot.workflow.nodes.base import ExecNode
from flowpilot.workflow.nodes.basic import HttpReqNode
from flowpilot.workflow.pins import DataPin, Direction, ExecPin
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


class Blackboard(object):
    pass


class GouzaoParams(ExecNode):
    def __init__(self, name: str | None = None) -> None:
        super().__init__(name)
        self.params = DataPin(direction=Direction.OUTPUT)
        self._userid = "fc962cb7529542209301190e6e8daef7"
        self._authsk = "f83aa442-f7ac-4b7e-b81d-42707e846cb8"
        self._url = (
            "http://10.94.144.139:8290/api/v2/inner/userless/user/getReflowStsToken"
        )

    def hashmd5(self, timestamp):
        md5_hash = hashlib.md5()
        md5_hash.update(
            f"reflow_sts_{self._userid}_{self._authsk}_{timestamp}".encode("utf-8")
        )
        return md5_hash.hexdigest()

    def _execute(self) -> None:
        timestamp = str(int(time.time()))
        self.params.value = {
            "url": self._url,
            "headers": {"Content-Type": "application/json"},
            "data": json.dumps(
                {
                    "userId": self._userid,
                    "timestamp": timestamp,
                    "authKey": self.hashmd5(timestamp),
                }
            ),
            "timeout": 10,
        }


class Workspace:
    def __init__(self) -> None:
        self.op1 = GouzaoParams()
        self.op2 = HttpReqNode()

        self._setup_links()
        self.graph = self._create_event_graph()

    def _setup_links(self):
        self.op1.then.link(self.op2.exec)
        self.op1.params.link(self.op2.params)
        self.op2.method.value = "POST"

    def _create_event_graph(self) -> EventGraph:
        graph = EventGraph(nodes=[self.op1, self.op2])
        graph.begin_play.link(self.op1.exec)
        return graph

    def run(self):
        self.graph.execute()
        print(self.op2.response.value.json())


# def main() -> None:
#     logger = setup_logger(name="reflow")

#     cfg = setup_cfg()
#     logger.info(f"Config: {OmegaConf.to_container(cfg)}")

#     level = ULevel()

#     engine = UEngine(
#         cfg,
#         UWorld(
#             [
#                 Controller(),
#             ]
#         ),
#     )
#     engine.loop_until()


if __name__ == "__main__":
    cfg = OmegaConf.merge(
        OmegaConf.create(asdict(Config())), OmegaConf.from_cli(sys.argv[1:])
    )
    # main()
    ws = Workspace()
    ws.run()

    # fn = FunctionNode("GetBoscer", "get_boscer")
    # fn.then.link(FunctionNode("UploadBos", upload_bos))

    # blackboard = Blackboard()
    # graph = NodeGraph()

    # node1 = function(graph.begin_play, target=blackboard, method=blackboard.sf)
    # node2 = function(node1.then, target=blackboard, method="submit_task")

    # node1 = GetBoscer()
    # node2 = UploadBos()
    # node3 = SubmitTask()
    # node4 = AddWatchTask()

    # graph.begin_play.link(node1.exec)
    # node1.then.link(node2.exec)
    # node2.then.link(node3.exec)
    # node3.then.link(node4.exec)

    # graph.begin_play.exec()
