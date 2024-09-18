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


if __name__ == "__main__":
    cfg = OmegaConf.merge(
        OmegaConf.create(asdict(Config())), OmegaConf.from_cli(sys.argv[1:])
    )
    main()
