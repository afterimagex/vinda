from redis import Redis

from api.config import get_cfg
from api.core.module import UComponent


class RedisComponent(UComponent):

    def setup(self):
        celery_app = Redis(__name__)

        # celery_app.conf.task_routes = {
        #     "flap.app.worker.main": "main_queue"
        # }

        # celery_app.conf.update(get_cfg().celery)
        print("setup celery")
        # self._celery_app = celery.Celery(
        #     "tasks", broker=self.broker, backend=self.backend
        # )

    def tick(self):
        print("celery tick")
