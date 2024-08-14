from typing import List

from celery import Celery

from api.config import get_cfg
from api.core.module import UComponent, UModule


class CeleryComponent(UComponent):
    def __init__(self, name: str = None):
        super().__init__(name)

    def setup(self):
        celery_app = Celery(__name__)

        # celery_app.conf.task_routes = {
        #     "flap.app.worker.main": "main_queue"
        # }

        celery_app.conf.update(get_cfg().celery)
        print("setup celery")
        # self._celery_app = celery.Celery(
        #     "tasks", broker=self.broker, backend=self.backend
        # )

    def tick(self):
        print("celery tick")
