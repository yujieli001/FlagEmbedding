#!/bin/bash
set -e

# 生产环境启动脚本
# 使用 uvicorn 启动 FastAPI 服务

# 虚拟环境路径
VENV_PATH="${RERANKER_VENV_PATH:-/data/FlagEmbedding/.venv}"

# 激活虚拟环境
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
fi

echo "Starting FlagModel Reranker service..."
echo "  MODEL_NAME: ${RERANKER_MODEL_NAME}"
echo "  MODEL_PATH: ${RERANKER_MODEL_PATH}"
echo "  HOST: ${RERANKER_HOST}"
echo "  PORT: ${RERANKER_PORT}"
echo "  USE_FP16: ${RERANKER_USE_FP16}"

# 使用 uvicorn 启动服务
exec "$VENV_PATH/bin/uvicorn" reranker:app \
    --host "${RERANKER_HOST:-0.0.0.0}" \
    --port "${RERANKER_PORT:-10020}" \
    --workers "${RERANKER_WORKERS:-2}"
