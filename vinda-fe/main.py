import requests
import streamlit as st
from tempfile import NamedTemporaryFile
from loguru import logger
import traceback
from pydantic import BaseModel, Field
from typing import Union, Optional, Dict, List
import json

from streamlit_autorefresh import st_autorefresh

import streamlit.components.v1 as components


api_url = 'http://127.0.0.1:8081'
tb_url = 'http://139.9.129.3:8062'


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
    name_model: str = Field('hf_hub:timm/mobilenetv4_conv_small.e2400_r224_in1k', description='模型名称')
    pretrain_model: str = Field('', description='预训练模型')
    img_size: int = Field(224, description='输入网络的图像尺寸（自动resize）')
    epochs: int = Field(100, description='训练周期数')
    save_interval: int = Field(1, description='保存模型的间隔（按周期计算）')
    batch_size: int = Field(8, description='每批处理的样本数量')
    num_workers: int = Field(0, description='工作进程数')
    # gpu_ids: Optional[list] = Field(default=None, description='使用的GPU编号列表')
    n_gpu: Optional[int] = Field(default=None, description='使用的GPU数量')
    seed: int = Field(42, description='随机种子，用于结果的可复现性')
    solver: SolverConfig = Field(default_factory=SolverConfig, description='训练过程中使用的优化器配置')

    # # 你需要在初始化时手动检查 gpu_ids 和 n_gpu 的互斥性。
    # def __init__(self, **data):
    #     super().__init__(**data)
    #     if self.gpu_ids is not None and self.n_gpu is not None:
    #         raise ValueError("Only one of 'gpu_ids' or 'n_gpu' should be set.")

    #     if 'solver' not in data:
    #         self.solver = SolverConfig()


@st.cache_data
def list_trained_models():
    ret = []
    try:
        response = requests.get(api_url + '//list_trained_models')
        data : dict = response.json()['data']
        for v in data.values():
            for ckpt in v['checkpoints']:
                ret.append(ckpt)

    except Exception as e:
        logger.error(traceback.format_exc())

    finally:
        return ret
    

@st.cache_data(show_spinner=True)
def list_models():
    ret = {
        "models_supported": [],
        "models_available": []
    }
    try:
        response = requests.get(api_url + '/list_models')
        data = response.json()['data']
        ret['models_supported'] = data['models_supported']
        ret['models_available'] = data['models_available']
    except Exception as e:
        logger.error(traceback.format_exc())

    finally:
        return ret


def list_datasets():
    ret = []
    try:
        response = requests.get(api_url + '/list_datasets')
        data = response.json()['data']
        ret = data['datasets']
    except Exception as e:
        logger.error(traceback.format_exc())

    finally:
        return ret


# @st.cache_resource(show_spinner=True)
# def load_data(datasets, dataname: str):
#     with NamedTemporaryFile(dir='./datasets/', suffix='.zip') as f:
#         f.write(datasets.getbuffer())
#         with st.spinner(text="Uploads datasets. This should take few minutes."):
#             pass


st.set_page_config(page_title="Trainner", layout='wide')


with st.sidebar:

    train_config = TrainingConfig(dataset='')
    train_config.n_gpu = 1

    st.write("## Task")
    task = st.selectbox(
        "Which problem do you want to solve?", [
            'Train Model', 'Export Model', 'Infer Model'
        ]
    )

    st.write("## Model")
    models = list_models()

    if st.checkbox("Use pre-training model?", value=True):
        model = st.selectbox(
            "Which model?", models['models_supported']
        )
        st.markdown(
            f'<sup>Pre-training on ImageNet, <a href="">More Details</a></sup>', 
            unsafe_allow_html=True
        )
    else:
        if st.checkbox("Use trained model?"):
            model = st.selectbox(
                "Which model?", list_trained_models()
            )
        else:
            model = st.selectbox(
                "Which model?", models['models_available']
            )

    st.write("## Data")

    if 'dataset' not in st.session_state:
        st.session_state['dataset'] = list_datasets()

    if st.checkbox("Upload datasets?"):
        st.write(
            """
        每个文件夹表示一个类别, zip压缩后的格式, 目录结构:
        ```
        +-- train/                   // 训练集
        |   +-- dogs/
        |       +-- lassie.jpg
        |       +-- komisar-rex.png
        |   +-- cats/
        |       +-- garfield.png
        |       +-- smelly-cat.png
        +-- val/                     // 测试集
        |   +-- dogs/
        |       +-- lassie1.jpg
        |       +-- komisar-rex1.png
        |   +-- cats/
        |       +-- garfield1.png
        |       +-- smelly-cat1.png
        ```
            """
        )
        uploaded_file = st.file_uploader("选择一个文件", type=["zip"])
        if uploaded_file is not None:
            response = requests.post(
                api_url + '/upload_datasets', 
                files={'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
            )
            st.session_state['dataset'] = list_datasets()
    
    train_config.dataset = st.selectbox(
        "Which datasets?", st.session_state['dataset']
    )

    st.write("## Training")

    if 'training' not in st.session_state:
        st.session_state['training'] = False
    
    if 'training_best_model' not in st.session_state:
        st.session_state['training_best_model'] = ''

    if st.button('RUN') and not st.session_state['training']:

        # st.write(f'## {train_config.model_dump()}')
        td = json.dumps(train_config.model_dump(), indent=4)
        response = requests.post(
            api_url + '/train_cls_model',
            data=td
        )
        st.write('### train config')
        st.code(td)
        st.write('### train response')
        response_json = response.json()
        st.code(json.dumps(response_json, indent=4))
        st.session_state['training'] = True
        st.session_state['training_task_id'] = response_json['data']['task_id']


count = st_autorefresh()

st.info(f"### best_model_path: {st.session_state['training_best_model']}")

if st.session_state['training'] and 'training_task_id' in st.session_state:
    response = requests.get(
        api_url + f"/task_state/{st.session_state['training_task_id']}",
    )
    ret = response.json()

    if ret['code'] == 0 and ret['data']['task_result'] != None:
        results = ret['data']['task_result']

        if 'stage' in results:
            with st.container():
                max_epochs = results['max_epochs']
                num_batches = results['num_batches']
                current_epoch = results['current_epoch']
                current_batch = results['current_batch']
                loss = results['loss']
                acc = results['acc']
                stage = results['stage']
                ik1 = max_epochs * num_batches
                ik2 = current_epoch * num_batches + current_batch
                val = ik2 / ik1
                st.progress(value=val, text=f'stage={stage}, epoch=[{current_epoch}/{max_epochs}], iter=[{ik2}/{ik1}], loss={loss}, acc={acc}')
    
        elif 'best_model_path' in results:
            st.session_state['training_best_model'] = results['best_model_path']
            st.session_state['training'] = False


style = """
<style>
  html, body {
    margin: 0;
    padding: 0;
    height: 100%;
  }
  .iframe-container {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    width: 100%;
    height: 100%;
    overflow: auto;
  }
  .iframe-container iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: none;
    box-sizing: border-box;
  }
</style>
"""

components.html(style + f'''
<div class="iframe-container">
<iframe src="{tb_url}" width="100%" height="100%" scrolling="yes" frameborder="0" allowfullscreen></iframe>
</div>
''', height=1080)
