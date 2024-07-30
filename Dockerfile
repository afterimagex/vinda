FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

# RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list \
#     && apt-get update \
#     && apt-get install -y --no-install-recommends \
#     python3-pip \
#     && apt clean \
#     && rm -rf /var/lib/apt/lists/*

# USER vinda

COPY ./dist /workspace/vinda
# COPY ./requirements.txt /workspace/vinda

WORKDIR /workspace/vinda

RUN pip install --no-cache-dir -U pip && \
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple && \
    pip install vinda-*.whl