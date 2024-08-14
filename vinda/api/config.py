import os

from easydict import EasyDict

from pathlib import Path

from loguru import logger

try:
    from dotenv import load_dotenv, find_dotenv
    load_dotenv(find_dotenv("vinda.env"))
except ImportError:
    print("dotenv not installed, skipping...")

cfg = EasyDict()

cfg.base_dir = Path(__file__).parent

cfg.app = EasyDict()
cfg.app.title = 'Vinda API Server'

cfg.celery = EasyDict()
## List of modules to import when the Celery worker starts.
cfg.celery.imports = ('vinda.api.worker.celery_tasks',)
## Broker settings.
cfg.celery.broker_url = os.getenv('CELERY_BROKER_URL', 'redis://:vinda1234@127.0.0.1:6379/0')
## Using the database to store task state and results.
cfg.celery.result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://:vinda1234@127.0.0.1:6379/1')

cfg.db = EasyDict()
cfg.db.db_url = ''

cfg.trainer = EasyDict()
cfg.trainer.output = os.getenv('OUTDIR', '/data/output')

## make dirs
os.makedirs(f"{cfg.trainer.output}/logs", exist_ok=True)
os.makedirs(f"{cfg.trainer.output}/exported", exist_ok=True)
os.makedirs(f"{cfg.trainer.output}/datasets", exist_ok=True)

## Log settings.
logger.level(os.getenv('LOG_LEVEL', 'INFO'))
logger.add(f"{cfg.trainer.output}/logs/{os.getenv('LOG_NAME', 'vinda')}.log", rotation="500 MB")