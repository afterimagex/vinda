from vinda.api.worker.celery_app import celery_app as celery
from vinda.api.trainer import SimpleData, SimpleModel, get_trainer
from vinda.api import schemas


@celery.task
def train_model(trainning_config: dict):
    cfg = schemas.TrainingConfig(**trainning_config)
    data = SimpleData(
        root_dir=cfg.dataset,
        img_size=cfg.img_size,
        batch_size=cfg.batch_size,
        num_workers=cfg.num_workers,
    )
    model = SimpleModel(
        solver_config=cfg.solver,
        model_name=cfg.model_name, pretrained=True, num_classes=len(data.classes)
    )
    trainer = get_trainer(cfg)
    trainer.fit(model, data)
    return {
        'best_model_path': trainer.checkpoint_callback.best_model_path
    }