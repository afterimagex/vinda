import os
import time
import zipfile
from traceback import format_exception
from typing import Optional, Tuple

import timm
import uvicorn
from celery.result import AsyncResult
from fastapi import BackgroundTasks, Depends, FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from loguru import logger
from PIL import Image
from starlette.middleware.cors import CORSMiddleware

from vinda.api import schemas
from vinda.api.config import cfg
from vinda.api.onnxinfer import OnnxGlobalInfer, OrtClsInfer
from vinda.api.pattern import response_handle
from vinda.api.worker import celery_tasks as tasks
from vinda.api.worker.celery_app import celery_app

# fix windows platform
if os.name == "nt":
    os.system('tzutil /s "UTC"')
else:
    os.environ["TZ"] = "UTC"
    time.tzset()


app = FastAPI(title=cfg.app.title, version="0.1")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/train_cls_model", status_code=201)
async def train_cls_model(
    training_config: schemas.TrainingConfig, background_task: BackgroundTasks
) -> Optional[dict]:
    ret = {"code": 0, "message": "OK"}

    try:
        task = tasks.train_cls_model.apply_async(args=(training_config.model_dump(),))
        ret["data"] = {"task_state": task.state, "task_id": task.task_id}
    except Exception as e:
        error = {"code": -1, "message": str(e), "traceback": format_exception(e)}
        logger.error(error)
        ret.update(error)

    finally:
        return ret


@app.post("/upload_datasets")
@response_handle
async def upload_datasets(file: UploadFile = File(...)) -> Optional[dict]:
    zip_file = os.path.join(cfg.trainer.output, "datasets", file.filename)
    with open(zip_file, "wb") as f:
        while contents := await file.read(1024 * 1024):
            f.write(contents)
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(os.path.join(cfg.trainer.output, "datasets"))


@app.get("/list_datasets")
@response_handle
async def list_datasets() -> Optional[dict]:
    path = os.path.join(cfg.trainer.output, "datasets")
    datasets = [
        os.path.join(cfg.trainer.output, "datasets", x) for x in os.listdir(path)
    ]
    return {"datasets": [x for x in datasets if os.path.isdir(x)]}


@app.get("/list_models")
@response_handle
async def list_models() -> Optional[dict]:
    return {
        "models_supported": os.listdir("/root/.cache/huggingface/hub/"),
        "models_available": timm.list_models(),
    }


@app.get("/list_trained_models")
@response_handle
async def list_trained_models() -> Optional[dict]:
    lml = os.path.join(cfg.trainer.output, "lightning_logs")
    weights = {}
    for ver in os.listdir(lml):
        weights[ver] = {
            "param": os.path.join(lml, ver, "hparams.yaml"),
            "checkpoints": [],
        }
        ckpts_dir = os.path.join(lml, ver, "checkpoints")
        if os.path.isdir(ckpts_dir):
            for ckpt in os.listdir(ckpts_dir):
                weights[ver]["checkpoints"].append(os.path.join(ckpts_dir, ckpt))
    return weights


@app.post("/export_model")
async def export_model(
    export_config: schemas.ExportConfig, background_task: BackgroundTasks
) -> Optional[dict]:
    ret = {"code": 0, "message": "OK"}

    try:
        assert os.path.exists(export_config.path_param)
        assert os.path.isfile(export_config.path_param)

        assert os.path.exists(export_config.path_model)
        assert os.path.isfile(export_config.path_model)

        basename = os.path.basename(export_config.path_model)
        basename = os.path.splitext(basename)[0] + f".{export_config.format}"
        save_path = os.path.join(
            cfg.trainer.output, "exported", f"{export_config.tag}{basename}"
        )

        background_task.add_task(tasks.export_cls_model, export_config, save_path)

        ret["data"] = {"exported_path": save_path}

    except Exception as e:
        error = {"code": -1, "message": str(e), "traceback": format_exception(e)}
        logger.error(error)
        ret.update(error)

    finally:
        return ret


@app.post("/infer_cls_engine")
async def infer_cls_model(
    infer_config: schemas.InferenceConfig, background_task: BackgroundTasks
) -> Optional[dict]:
    ret = {"code": 0, "message": "OK"}
    try:
        assert os.path.exists(infer_config.path_image)
        assert os.path.isfile(infer_config.path_image)

        def background(cfg: schemas.InferenceConfig):
            try:
                if OnnxGlobalInfer().cls_engine is None:
                    OnnxGlobalInfer().cls_engine = OrtClsInfer(cfg.path_model)
                    logger.info(f"first load cls engine: {cfg.path_model}.")

                image = Image.open(cfg.path_image)
                preds = OnnxGlobalInfer().cls_engine(image, cfg.img_size)
                for k, v in OnnxGlobalInfer().cls_engine.computation_metrics().items():
                    logger.debug(f"{k}: {v}")
                logger.info(f"preds: {preds}")

            except Exception as e:
                logger.error(e)
                for x in format_exception(e):
                    logger.error(x.strip())

        background_task.add_task(background, infer_config)

    except Exception as e:
        error = {"code": -1, "message": str(e), "traceback": format_exception(e)}
        logger.error(error)
        ret.update(error)
    finally:
        return ret


@app.get("/free_cls_engine")
async def free_cls_engine() -> Optional[dict]:
    ret = {"code": 0, "message": "OK"}
    try:
        if OnnxGlobalInfer().cls_engine is None:
            warn = {"code": 404, "message": "cls engine not exists."}
            logger.warning(warn)
            ret.update(warn)
        OnnxGlobalInfer().cls_engine = None
    except Exception as e:
        error = {"code": -1, "message": str(e), "traceback": format_exception(e)}
        logger.error(error)
        ret.update(error)
    finally:
        return ret


@app.get("/task_state/{task_id}")
async def get_task_state(task_id: str) -> Optional[dict]:
    ret = {"code": 0, "message": "OK"}

    try:
        task = AsyncResult(task_id, backend=celery_app.backend)
        ret["data"] = {
            "task_id": task_id,
            "task_state": task.state,
            "task_result": task.result,
            "date_done": str(task.date_done),
        }

    except Exception as e:
        error = {"code": -1, "message": str(e), "traceback": format_exception(e)}
        logger.error(error)
        ret.update(error)

    finally:
        return ret


if __name__ == "__main__":
    uvicorn.run(app="app:app", host="0.0.0.0", port=8081, reload=True)
