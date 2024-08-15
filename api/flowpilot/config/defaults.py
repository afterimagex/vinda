import os
from pathlib import Path

from easydict import EasyDict

package_path = Path(__file__).parent.parent
env_path = package_path / ".env"


try:
    from dotenv import find_dotenv, load_dotenv

    if not load_dotenv(find_dotenv(env_path)):
        print("No .env file found")

except ImportError:

    print("dotenv not installed, skipping...")


# -----------------------------------------------------------------------------
# Config definition
# -----------------------------------------------------------------------------

_C = EasyDict()

_C.base_dir = Path(__file__).parent

_C.app = EasyDict()
_C.app.title = "Vinda API Server"

_C.celery = EasyDict()
## List of modules to import when the Celery worker starts.
_C.celery.imports = ("vinda.api.worker.celery_tasks",)
## Broker settings.
_C.celery.broker_url = os.getenv(
    "CELERY_BROKER_URL", "redis://:vinda1234@127.0.0.1:6379/0"
)
## Using the database to store task state and results.
_C.celery.result_backend = os.getenv(
    "CELERY_RESULT_BACKEND", "redis://:vinda1234@127.0.0.1:6379/1"
)

_C.db = EasyDict()
_C.db.db_url = ""

_C.trainer = EasyDict()
_C.trainer.output = os.getenv("OUTDIR", "/data/output")

## make dirs
# os.makedirs(f"{_C.trainer.output}/logs", exist_ok=True)
# os.makedirs(f"{_C.trainer.output}/exported", exist_ok=True)
# os.makedirs(f"{_C.trainer.output}/datasets", exist_ok=True)

## Log settings.
# logger.remove()
# logger.level(os.getenv("LOG_LEVEL", "INFO"))
# logger.add(RichHandler(), format="{message}")
# logger.add(
#     f"{_C.trainer.output}/logs/{os.getenv('LOG_NAME', 'vinda')}.log", rotation="500 MB"
# )


# logger.info(package_path)


if __name__ == "__main__":
    print(_C)
