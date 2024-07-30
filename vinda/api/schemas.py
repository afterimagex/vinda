from typing import Union, Optional
from pydantic import BaseModel, Field


class SolverConfig(BaseModel):
    opt: str = Field('adam', description="优化器类型，可以是 'adam' 或 'sgd'")
    weight_decay: float = Field(0.0001, description="正则化权重衰减")
    momentum: float = Field(0.9, description="SGD优化器的动量")
    base_lr: float = Field(0.001, description="基础学习率")
    lr_scheduler: str = Field('step', description="学习率调度器类型，可以是'step'、'multistep'、'reduce_on_plateau'")
    lr_decay_rate: float = Field(0.1, description="学习率衰减率")
    lr_step_size: int = Field(5, description="步进学习率调度器的步长", gt=0)
    lr_step_milestones: list = Field([10, 15], description="多步学习率调度器的里程碑")

    def __init__(self, **data):
        super().__init__(**data)
        # 验证动量参数是否仅在使用'sgd'优化器时设置
        if self.opt != 'sgd' and self.momentum != 0.9:
            raise ValueError("Momentum should only be used when optimizer is set to 'sgd'")

        # 验证学习率调度器设置
        if self.lr_scheduler == 'step' and self.lr_step_size <= 0:
            raise ValueError("Step size for step learning rate scheduler must be greater than 0")
        elif self.lr_scheduler == 'multistep' and not self.lr_step_milestones:
            raise ValueError("Milestones must be provided for multistep learning rate scheduler")


class TrainingConfig(BaseModel):
    dataset: str = Field(..., description='数据集名称')
    model_name: str = Field('resnet18', description='模型名称')
    img_size: int = Field(112, description='输入网络的图像尺寸（自动resize）')
    epochs: int = Field(100, description='训练周期数')
    save_interval: int = Field(1, description='保存模型的间隔（按周期计算）')
    batch_size: int = Field(8, description='每批处理的样本数量')
    num_workers: int = Field(12, description='工作进程数')
    gpu_ids: Optional[list] = Field(default=None, description='使用的GPU编号列表')
    n_gpu: Optional[int] = Field(default=None, description='使用的GPU数量')
    seed: int = Field(42, description='随机种子，用于结果的可复现性')
    solver: SolverConfig = Field(default_factory=SolverConfig, description='训练过程中使用的优化器配置')

    # 你需要在初始化时手动检查 gpu_ids 和 n_gpu 的互斥性。
    def __init__(self, **data):
        super().__init__(**data)
        if self.gpu_ids is not None and self.n_gpu is not None:
            raise ValueError("Only one of 'gpu_ids' or 'n_gpu' should be set.")

        if 'solver' not in data:
            self.solver = SolverConfig()