import os

import timm
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image
from pytorch_lightning import LightningDataModule, LightningModule, Trainer
from pytorch_lightning.loggers import TensorBoardLogger
from pytorch_lightning.callbacks import LearningRateMonitor, ModelCheckpoint
# from pytorch_lightning.utilities.seed import seed_everything
from torch.utils.data import DataLoader
from torchmetrics import Accuracy
from torchvision.datasets import ImageFolder

from vinda.api import schemas
from vinda.api.config import cfg
from celery import current_task

from loguru import logger

# torch.multiprocessing.set_start_method('spawn')

def get_optimizer(solver_config : schemas.SolverConfig, parameters) -> torch.optim.Optimizer:
    if solver_config.opt == 'adam':
        optimizer = torch.optim.Adam(parameters, lr=solver_config.base_lr, weight_decay=solver_config.weight_decay)
    elif solver_config.opt == 'sgd':
        optimizer = torch.optim.SGD(
            parameters, lr=solver_config.base_lr, weight_decay=solver_config.weight_decay, momentum=solver_config.momentum
        )
    else:
        raise NotImplementedError()

    return optimizer


def get_lr_scheduler_config(solver_config : schemas.SolverConfig, optimizer: torch.optim.Optimizer) -> dict:
    if solver_config.lr_scheduler == 'step':
        scheduler = torch.optim.lr_scheduler.StepLR(
            optimizer, step_size=solver_config.lr_step_size, gamma=solver_config.lr_decay_rate
        )
        lr_scheduler_config = {
            'scheduler': scheduler,
            'interval': 'epoch',
            'frequency': 1,
        }
    elif solver_config.lr_scheduler == 'multistep':
        scheduler = torch.optim.lr_scheduler.MultiStepLR(
            optimizer, milestones=solver_config.lr_step_milestones, gamma=solver_config.lr_decay_rate
        )
        lr_scheduler_config = {
            'scheduler': scheduler,
            'interval': 'epoch',
            'frequency': 1,
        }
    elif solver_config.lr_scheduler == 'reduce_on_plateau':
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='max', factor=0.1, patience=10, threshold=0.0001
        )
        lr_scheduler_config = {
            'scheduler': scheduler,
            'monitor': 'val_loss',
            'interval': 'epoch',
            'frequency': 1,
        }
    else:
        raise NotImplementedError

    return lr_scheduler_config


class ImageTransform:
    def __init__(self, is_train: bool, img_size: int | tuple = 112):
        if isinstance(img_size, int):
            img_size = (img_size, img_size)

        if is_train:
            self.transform = transforms.Compose(
                [
                    transforms.RandomHorizontalFlip(p=0.5),
                    transforms.RandomRotation(20),
                    transforms.Resize(img_size),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                    ),
                ]
            )
        else:
            self.transform = transforms.Compose(
                [
                    transforms.Resize(img_size),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                    ),
                ]
            )

    def __call__(self, img: Image.Image) -> torch.Tensor:
        return self.transform(img)


class SimpleData(LightningDataModule):
    def __init__(
        self,
        root_dir: str,
        img_size: int = 112,
        batch_size: int = 8,
        num_workers: int = 16,
    ):
        super().__init__()
        self.root_dir = root_dir
        self.img_size = img_size
        self.batch_size = batch_size
        self.num_workers = num_workers

        self.train_dataset = ImageFolder(
            root=os.path.join(root_dir, 'train'),
            transform=ImageTransform(is_train=True, img_size=self.img_size),
        )
        self.val_dataset = ImageFolder(
            root=os.path.join(root_dir, 'val'),
            transform=ImageTransform(is_train=False, img_size=self.img_size),
        )
        self.classes = self.train_dataset.classes
        self.class_to_idx = self.train_dataset.class_to_idx

    def train_dataloader(self) -> DataLoader:
        dataloader = DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            drop_last=True,
            num_workers=self.num_workers,
        )
        return dataloader

    def val_dataloader(self) -> DataLoader:
        dataloader = DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            drop_last=False,
            num_workers=self.num_workers,
        )
        return dataloader


# class DeeplakeData(LightningDataModule):
#     def __init__(
#         self,
#         path: str,
#         img_size: int = 112,
#         batch_size: int = 8,
#         num_workers: int = 16,
#     ):
#         super().__init__()
#         self.img_size = img_size
#         self.batch_size = batch_size
#         self.num_workers = num_workers
#         self.dataset = deeplake.dataset(path, public=True, creds = {
#             "aws_access_key_id": "wxgn3BIy2ghFhQfRDe68", 
#             "aws_secret_access_key": "W3rKG6qe75xqgkUiuMXct7QVis1tPFfT9BxZpFD7",
#             "endpoint_url": "http://172.24.181.62:8588"
#         })
    
#     def train_dataloader(self) -> DataLoader:
#         dataloader = self.dataset.train.dataloader().pytorch(num_workers=self.num_workers)
        
#         # dataloader = self.dataset.train.dataloader()\
#         #     .transform({'images': ImageTransform(is_train=True, img_size=self.img_size), 'labels': None})\
#         #     .batch(self.batch_size)\
#         #     .shuffle()\
#         #     .pytorch(num_workers=self.num_workers, decode_method={'images': 'pil'})
#         return dataloader

#     def val_dataloader(self) -> DataLoader:
#         dataloader = self.dataset.train.dataloader()\
#             .transform({'images': ImageTransform(is_train=False, img_size=self.img_size), 'labels': None})\
#             .batch(self.batch_size)\
#             .pytorch(num_workers=self.num_workers, decode_method={'images': 'pil'})
#         return dataloader


class SimpleModel(LightningModule):
    def __init__(
        self,
        solver_config: schemas.SolverConfig,
        model_name: str = 'resnet18',
        pretrained: bool = False,
        num_classes: int | None = None,
    ):
        super().__init__()
        self.solver_config = solver_config
        self.save_hyperparameters()
        self.model = timm.create_model(
            model_name=model_name, pretrained=pretrained, num_classes=num_classes
        )
        self.train_loss = nn.CrossEntropyLoss()
        self.train_acc = Accuracy(task='multiclass', num_classes=num_classes)
        self.val_loss = nn.CrossEntropyLoss()
        self.val_acc = Accuracy(task='multiclass', num_classes=num_classes)

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, target = batch

        out = self(x)
        _, pred = out.max(1)

        loss = self.train_loss(out, target)
        acc = self.train_acc(pred, target)
        self.log_dict({'train_loss': loss, 'train_acc': acc}, prog_bar=True)

        meta_info = {
            'stage': 'training',
            'current_epoch': self.current_epoch,
            'max_epochs': self.trainer.max_epochs,
            'current_batch': batch_idx,
            'num_batches': self.trainer.num_training_batches,
            'loss': loss.item(),
            'acc': acc.item(),
        }
        
        current_task.update_state(
            state='PROGRESS',
            meta=meta_info
        )
        
        # logger.debug(meta_info)

        return loss

    def validation_step(self, batch, batch_idx):
        x, target = batch

        out = self(x)
        _, pred = out.max(1)

        loss = self.val_loss(out, target)
        acc = self.val_acc(pred, target)
        self.log_dict({'val_loss': loss, 'val_acc': acc})

        meta_info = {
            'stage': 'validation',
            'current_epoch': self.current_epoch,
            'max_epochs': self.trainer.max_epochs,
            'current_batch': batch_idx,
            'num_batches': sum(self.trainer.num_val_batches),
            'loss': loss.item(),
            'acc': acc.item(),
        }
        
        current_task.update_state(
            state='PROGRESS',
            meta=meta_info
        )

        # logger.debug(meta_info)

        if batch_idx == 1:
            tb_logger = None
            for tlogger in self.trainer.loggers:
                if isinstance(tlogger, TensorBoardLogger):
                    tb_logger = tlogger.experiment
                    break
            if tb_logger is None:
                raise ValueError('TensorBoard Logger not found')
            
            for img_idx, (image, y_true, y_pred) in enumerate(zip(*(x, target, pred))):
                tb_logger.add_image(f"Image/{batch_idx}_{img_idx}_标注:{y_true}_预测:{y_pred}", image, 0)
            

    def configure_optimizers(self):
        optimizer = get_optimizer(self.solver_config, self.parameters())
        lr_scheduler_config = get_lr_scheduler_config(self.solver_config, optimizer)
        return {"optimizer": optimizer, "lr_scheduler": lr_scheduler_config}


def get_basic_callbacks(checkpoint_interval: int = 1) -> list:
    lr_callback = LearningRateMonitor(logging_interval='epoch')
    ckpt_callback = ModelCheckpoint(
        filename='model-{epoch:03d}-{val_acc:.3f}',
        monitor='val_acc',
        auto_insert_metric_name=False,
        save_top_k=3,
        mode='max',
        every_n_epochs=checkpoint_interval,
    )
    return [ckpt_callback, lr_callback]


def get_gpu_settings(
    gpu_ids: list[int], n_gpu: int
) -> tuple[str, int | list[int] | None, str | None]:
    """Get gpu settings for pytorch-lightning trainer:
    https://pytorch-lightning.readthedocs.io/en/stable/common/trainer.html#trainer-flags

    Args:
        gpu_ids (list[int])
        n_gpu (int)

    Returns:
        tuple[str, int, str]: accelerator, devices, strategy
    """
    if not torch.cuda.is_available():
        return "cpu", None, None

    if gpu_ids is not None:
        devices = gpu_ids
        strategy = "ddp" if len(gpu_ids) > 1 else None
    elif n_gpu is not None:
        # int
        devices = n_gpu
        strategy = "ddp" if n_gpu > 1 else 'auto'
    else:
        devices = 1
        strategy = 'auto'

    return "gpu", devices, strategy


def get_trainer(trainning_config : schemas.TrainingConfig) -> Trainer:
    callbacks = get_basic_callbacks(checkpoint_interval=trainning_config.save_interval)
    accelerator, devices, strategy = get_gpu_settings(trainning_config.gpu_ids, trainning_config.n_gpu)
    trainer = Trainer(
        max_epochs=trainning_config.epochs,
        callbacks=callbacks,
        default_root_dir=cfg.trainer.output,
        accelerator=accelerator,
        devices=devices,
        strategy=strategy,
        logger=True,
        deterministic=True,
    )
    return trainer


# if __name__ == '__main__':
    # args = get_args()
    # seed_everything(args.seed, workers=True)
    # data = SimpleData(
    #     root_dir=args.dataset,
    #     img_size=args.img_size,
    #     batch_size=args.batch_size,
    #     num_workers=args.num_workers,
    # )
    # model = SimpleModel(
    #     model_name=args.model_name, pretrained=True, num_classes=len(data.classes)
    # )
    # trainer = get_trainer(args)
    # print('Args:')
    # pprint(args.__dict__)
    # print('Training classes:')
    # pprint(data.class_to_idx)
    # trainer.fit(model, data)