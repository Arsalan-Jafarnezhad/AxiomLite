FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/home/laya/.cache/huggingface \
    TRANSFORMERS_CACHE=/home/laya/.cache/huggingface \
    USE_TF=0

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install CUDA-enabled PyTorch.
RUN pip install \
    --index-url https://download.pytorch.org/whl/cu128 \
    torch

# Install Laya HTTP server.
RUN pip install "laya[serve]"

RUN mkdir -p /home/laya/.cache/huggingface

EXPOSE 8000

CMD ["laya-serve"]