import os
from traceback import format_exception

import torch
import yaml
from loguru import logger

from vinda.api import schemas
from vinda.api.config import cfg
from vinda.api.trainer import ImageTransform, SimpleData, SimpleModel, get_trainer
from vinda.api.worker.celery_app import celery_app as celery


@celery.task
def train_cls_model(trainning_config: dict):
    try:
        cfg = schemas.TrainingConfig(**trainning_config)
        data = SimpleData(
            root_dir=cfg.dataset,
            img_size=cfg.img_size,
            batch_size=cfg.batch_size,
            num_workers=cfg.num_workers,
        )
        pretrain_model = cfg.pretrain_model and os.path.exists(cfg.pretrain_model)
        model = SimpleModel(
            solver_config=cfg.solver,
            model_name=cfg.name_model,
            pretrained=not pretrain_model,
            num_classes=len(data.classes),
        )
        if pretrain_model:
            ckpts = torch.load(cfg.pretrain_model)
            model.load_state_dict(ckpts["state_dict"])
        trainer = get_trainer(cfg)
        trainer.fit(model, data)
        message = {"best_model_path": trainer.checkpoint_callback.best_model_path}
        logger.debug(message)
        return message

    except Exception as e:
        logger.error(e)
        for x in format_exception(e):
            logger.error(x.strip())
        return {"message": str(e), "traceback": format_exception(e)}


def export_cls_model(export_config: schemas.ExportConfig, save_path):
    with open(export_config.path_param, "r") as fp:
        hparams = yaml.unsafe_load(fp)

    model = SimpleModel(
        solver_config=hparams["solver_config"],
        model_name=hparams["model_name"],
        pretrained=False,
        num_classes=hparams["num_classes"],
    )

    ckpts = torch.load(export_config.path_model, map_location="cpu")
    model.load_state_dict(ckpts["state_dict"])
    model.cpu()
    model.eval()

    with torch.no_grad():
        dummy_input = torch.randn(1, 3, 224, 224, requires_grad=True).cpu()
        # Export the model
        torch.onnx.export(
            model,  # model being run
            dummy_input,  # model input (or a tuple for multiple inputs)
            save_path,  # where to save the model
            export_params=True,  # store the trained parameter weights inside the model file
            opset_version=13,  # the ONNX version to export the model to
            do_constant_folding=True,  # whether to execute constant folding for optimization
            input_names=["input"],  # the model's input names
            output_names=["output"],  # the model's output names
            dynamic_axes={
                "input": {0: "N", 2: "H", 3: "W"},  # variable length axes
                "output": {0: "N", 2: "H", 3: "W"},
            },
        )


def inference_cls_model(inference_config: schemas.InferenceConfig):
    pass
