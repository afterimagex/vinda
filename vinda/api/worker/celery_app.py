from celery import Celery

from vinda.api.config import cfg


celery_app = Celery(__name__)

# celery_app.conf.task_routes = {
#     "flap.app.worker.main": "main_queue"
# }

celery_app.conf.update(cfg.celery)