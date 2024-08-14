from celery import Celery

from vinda.api.config import cfg


celery_app = Celery(__name__)

# celery_app.conf.task_routes = {
#     "flap.app.worker.main": "main_queue"
# }

celery_app.conf.update(cfg.celery)

# 设置并发模型和数量
# celery_app.conf.worker_concurrency = 4  # 根据你的 CPU 核心数调整
# celery_app.conf.worker_pool = 'prefork'  # 或者使用 'eventlet'