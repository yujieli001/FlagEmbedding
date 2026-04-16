#!/bin/bash
set -e

# 生产环境启动脚本
# 使用 Gunicorn 作为 WSGI 服务器

# 虚拟环境路径
VENV_PATH="${VENV_PATH:-/data/FlagEmbedding/.venv}"

# 激活虚拟环境
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
fi

# 环境变量配置（可按需修改）
export MODEL_PATH="${MODEL_PATH:-/model/bge-m3}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-10010}"
export USE_FP16="${USE_FP16:-false}"

# 计算 worker 数量（如果未设置）
if [ -z "$WORKERS" ]; then
    WORKERS=$(($(nproc) * 2 + 1))
fi
export WORKERS

echo "Starting FlagModel Embedder service..."
echo "  MODEL_PATH: $MODEL_PATH"
echo "  HOST: $HOST"
echo "  PORT: $PORT"
echo "  USE_FP16: $USE_FP16"
echo "  WORKERS: $WORKERS"

# 使用虚拟环境中的 Gunicorn 启动
exec "$VENV_PATH/bin/gunicorn" run:app \
    --bind "$HOST:$PORT" \
    --workers "$WORKERS" \
    --worker-class sync \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile -
