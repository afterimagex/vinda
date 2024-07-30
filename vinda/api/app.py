
import os
import time
import uvicorn
from vinda.api.config import cfg
from fastapi import Depends, FastAPI, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware
from vinda.api import schemas
from vinda.api.worker.celery_app import celery_app
from vinda.api.worker import celery_tasks as tasks
from celery.result import AsyncResult
from typing import Optional, Tuple
from fastapi.responses import JSONResponse


# fix windows platform
if os.name == "nt":
    os.system('tzutil /s "UTC"')
else:
    os.environ['TZ'] = 'UTC'
    time.tzset()


app = FastAPI(title=cfg.app.title, version='0.1')


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/train", status_code=201)
async def train(training_config: schemas.TrainingConfig, background_task: BackgroundTasks):
    task = tasks.train_model.apply_async(args=(training_config.model_dump(),))
    # def background_on_message(task):
        # task.get(on_message=lambda x: print(x), propagate=False)
    # background_task.add_task(background_on_message, task)
    return {"task_state": task.state, "task_id": task.task_id}


@app.get("/state/{task_id}")
async def get_task_state(task_id: str) -> Optional[dict]:
    task = AsyncResult(task_id, backend=celery_app.backend)
    result = {
        "task_id": task_id,
        "task_state": task.state,
        "task_result": task.result,
        'date_done': str(task.date_done)
    }
    return JSONResponse(result)


if __name__ == '__main__':
    uvicorn.run(app='app:app', host="0.0.0.0", port=8081, reload=True)