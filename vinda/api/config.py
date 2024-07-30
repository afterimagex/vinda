import os

from easydict import EasyDict

from pathlib import Path

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
cfg.celery.broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://:vinda1234@127.0.0.1:6379/0')
## Using the database to store task state and results.
cfg.celery.result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://:vinda1234@127.0.0.1:6379/1')

cfg.trainer = EasyDict()
cfg.trainer.outdir = os.environ.get('OUTDIR', 'result')