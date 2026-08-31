#!/usr/bin/env bash

set -euo pipefail

: "${VLLM_API_KEY:?VLLM_API_KEY must be set}"

MODEL_ID="${INFERENCE_MODEL_ID:-Qwen/Qwen2.5-VL-7B-Instruct}"
MODEL_REVISION="${INFERENCE_MODEL_REVISION:-cc594898137f460bfe9f0759e9844b3ce807cfb5}"
SERVED_MODEL="${INFERENCE_SERVED_MODEL:-qwen2.5-vl-7b}"

docker run \
  --rm \
  --name multimodal-vllm \
  --runtime nvidia \
  --gpus all \
  --env CUDA_VISIBLE_DEVICES=0 \
  --volume "${HOME}/.cache/huggingface:/root/.cache/huggingface" \
  --ipc=host \
  --publish 8001:8000 \
  vllm/vllm-openai:v0.26.0 \
  --model "${MODEL_ID}" \
  --revision "${MODEL_REVISION}" \
  --served-model-name "${SERVED_MODEL}" \
  --api-key "${VLLM_API_KEY}" \
  --max-model-len 4096 \
  --limit-mm-per-prompt '{"image":1,"video":0}' \
  --gpu-memory-utilization 0.90 \
  --generation-config vllm
