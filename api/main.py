from celery import Celery, Task
from fastapi import BackgroundTasks, Depends, FastAPI, File, UploadFile

from api.components.celery import CeleryComponent
from api.config import get_cfg
from api.core.module import Runner, UContext


def create_app() -> FastAPI:
    app = FastAPI(title=get_cfg().app.title, version="0.1")

    app.state.runner = Runner(childs=[CeleryComponent()]).attach(UContext())

    return app


app = create_app()
