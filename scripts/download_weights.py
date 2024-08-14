# from urllib.request import urlopen
# from PIL import Image
import timm
# import numpy as np

# export HF_ENDPOINT=https://hf-mirror.com
# import os

from huggingface_hub import snapshot_download

snapshot_download(
    repo_id='timm/mobilenetv4_conv_small.e2400_r224_in1k', 
    local_dir='../hf-cache/mobilenetv4_conv_small.e2400_r224_in1k', 
    local_dir_use_symlinks=False
)

# os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# img = Image.open(urlopen(
#     'https://hf-mirror.com/datasets/huggingface/documentation-images/resolve/main/beignets-task-guide.png'
# ))

# model = timm.create_model('mobilenetv4_conv_medium.e500_r256_in1k', pretrained=True)
# model = timm.create_model('hf_hub:timm/mobilenetv4_conv_small.e2400_r224_in1k', pretrained=True)

# print(model.default_cfg)

# model_list = timm.list_models()
# print(model_list)
# model = model.eval()

# # get model specific transforms (normalization, resize)
# data_config = timm.data.resolve_model_data_config(model)
# transforms = timm.data.create_transform(**data_config, is_training=False)

# output = model(transforms(img).unsqueeze(0))  # unsqueeze single image into batch of 1

# top5_probabilities, top5_class_indices = np.topk(output.softmax(dim=1) * 100, k=5)