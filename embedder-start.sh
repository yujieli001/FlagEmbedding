#!/bin/bash
set -e

# 生产环境启动脚本
# 使用 uvicorn 启动 FastAPI 服务

# 虚拟环境路径
VENV_PATH="${EMBEDDER_VENV_PATH:-/data/FlagEmbedding/.venv}"

# 激活虚拟环境
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
fi

echo "Starting FlagModel Embedder service..."
echo "  MODEL_NAME: ${EMBEDDER_MODEL_NAME}"
echo "  MODEL_PATH: ${EMBEDDER_MODEL_PATH}"
echo "  HOST: ${EMBEDDER_HOST}"
echo "  PORT: ${EMBEDDER_PORT}"
echo "  USE_FP16: ${EMBEDDER_USE_FP16}"

# 使用 uvicorn 启动服务
exec "$VENV_PATH/bin/uvicorn" embedder:app \
    --host "${EMBEDDER_HOST:-0.0.0.0}" \
    --port "${EMBEDDER_PORT:-10010}" \
    --workers "${EMBEDDER_WORKERS:-2}"
