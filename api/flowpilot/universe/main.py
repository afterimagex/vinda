import threading
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from flowpilot.universe.core import (
    AActor,
    Config,
    UEngine,
    UWorld,
    get_argparser_config,
)


class SpringTaskScheduling(AActor):
    _next_execution_time: datetime

    class Policy(Enum):
        Custom = 0
        Daily = 1

    def __init__(
        self,
        name: str = None,
        *,
        policy: Policy = Policy.Custom,
        interval: int = 60,
        start_time_hour: int = 0,
        start_time_minute: int = 0,
        use_threads: bool = True
    ) -> None:
        super().__init__(name)
        self._policy = policy
        self._interval = interval
        self._start_hour = start_time_hour
        self._start_minute = start_time_minute
        self._use_threads = use_threads

    def begin_play(self):
        super().begin_play()
        self.calculate_next_execution_time()

    def calculate_next_execution_time(self) -> datetime:
        now = datetime.now()
        if self._policy == self.Policy.Custom:
            self._next_execution_time = now + timedelta(seconds=self._interval)
        elif self._policy == self.Policy.Daily:
            today_start = now.replace(
                hour=self._start_hour,
                minute=self._start_minute,
                second=0,
                microsecond=0,
            )
            self._next_execution_time = (
                today_start if now < today_start else today_start + timedelta(days=1)
            )

    def tick(self, delta_time: float):
        super().tick(delta_time)
        now = datetime.now()
        if (self._next_execution_time - now).total_seconds() <= 0:
            self.execute_task()
            self.calculate_next_execution_time()

    def execute_task(self):
        if self._use_threads:
            threading.Thread(target=self._http_request, daemon=True).start()
        else:
            self._http_request()

    def _http_request(self):
        print("http request")


if __name__ == "__main__":

    s1 = SpringTaskScheduling(interval=1)
    # print(s1)

    world = UWorld(actors=[s1])
    print(world)

    cfg = get_argparser_config(Config)
    cfg.tick_interval = 0.1
    engine = UEngine(cfg, world)
    engine.loop_until()
