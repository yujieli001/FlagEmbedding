# Dify × FlagEmbedding 集成指南

替换 Xinference，实现本地化 Embedding 与 Rerank 服务。

## 方案对比

| 特性 | Xinference | FlagEmbedding |
|------|------------|---------------|
| 架构复杂度 | 完整模型管理平台 | 轻量级 API 服务 |
| 资源占用 | 较高（含管理界面） | 低（仅模型推理） |
| 部署难度 | 中等 | 简单 |
| 适用场景 | 多模型管理、高可用 | 单一模型、快速部署 |
| Dify 集成 | 内置供应商支持 | OpenAI 兼容接口 |

## 快速开始

### 1. 安装依赖

```bash
# 激活虚拟环境
source /data/FlagEmbedding/.venv/bin/activate

# 安装依赖
pip install FlagEmbedding fastapi uvicorn transformers torch tiktoken
```

### 2. 配置环境变量

编辑 `.service` 文件配置模型路径：

```bash
# Embedder 配置
EMBEDDER_MODEL_NAME=BAAI/bge-m3
EMBEDDER_MODEL_PATH=/model/bge-m3

# Reranker 配置
RERANKER_MODEL_NAME=BAAI/bge-reranker-v2-m3
RERANKER_MODEL_PATH=/model/bge-reranker-v2-m3
```

### 3. 启动服务

```bash
# 启动 Embedder 服务
sudo systemctl daemon-reload
sudo systemctl enable flagmodel-embedder
sudo systemctl start flagmodel-embedder

# 启动 Reranker 服务
sudo systemctl enable flagmodel-reranker
sudo systemctl start flagmodel-reranker

# 检查服务状态
sudo systemctl status flagmodel-embedder
sudo systemctl status flagmodel-reranker
```

## Dify 配置步骤

### Embedding 模型配置

1. **进入模型供应商设置**
   - 登录 Dify 后台 → 右上角头像 → 设置 → 模型供应商

2. **选择 OpenAI-API-compatible**
   - 由于 FlagEmbedding 提供 OpenAI 兼容接口，选择此供应商类型

3. **填写配置参数**

| 参数 | 值 |
|------|-----|
| 模型名称 | bge-m3（自定义名称） |
| API Key | 任意填写（本地服务可不验证） |
| 基础 URL | http://宿主机 IP:10010 |
| 模型类型 | Text Embedding |

4. **保存并验证**
   - 点击保存，Dify 会自动验证连接
   - 验证通过后即可在知识库中使用

### Rerank 模型配置

Dify 不直接集成 Rerank 模型，需要通过独立 API 服务接入。

1. **供应商配置**

| 参数 | 值 |
|------|-----|
| 供应商类型 | OpenAI-API-compatible |
| 模型名称 | bge-reranker |
| 基础 URL | http://宿主机 IP:10020 |
| 模型类型 | Rerank |

## API 接口说明

### Embedding 接口

```bash
# 请求
curl http://localhost:10010/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model": "bge-m3", "input": ["Hello world"]}'

# 响应
{
  "model": "bge-m3",
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [0.123, 0.456, ...]
    }
  ]
}
```

### Rerank 接口

```bash
# 请求
curl http://localhost:10020/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是人工智能",
    "documents": ["AI 是计算机科学分支", "地球是圆的"]
  }'

# 响应
{
  "object": "list",
  "data": [
    {"index": 0, "score": 0.95, "document": "AI 是计算机科学分支"},
    {"index": 1, "score": 0.12, "document": "地球是圆的"}
  ],
  "model": "BAAI/bge-reranker-v2-m3"
}
```

## 注意事项

### Docker 网络访问

若 Dify 使用 Docker 部署，需将 `localhost` 替换为：
- 宿主机局域网 IP（如 `http://192.168.1.100:10010`）
- 或使用 `host.docker.internal`

### 模型缓存

首次启动会下载模型文件，建议配置镜像加速：

```bash
export HF_ENDPOINT="https://hf-mirror.com"
```

### GPU 加速

安装 CUDA 版本的 PyTorch 可启用 GPU 加速：

```bash
# 修改 .service 文件
Environment="EMBEDDER_USE_GPU=true"

# 重启服务
sudo systemctl restart flagmodel-embedder
```

## 故障排查

### 服务无法启动

```bash
# 查看日志
journalctl -u flagmodel-embedder -n 50
journalctl -u flagmodel-reranker -n 50
```

### 端口被占用

```bash
# 检查端口
netstat -tlnp | grep -E '10010|10020'
```

### 模型加载失败

检查模型路径是否正确：
```bash
ls -la /model/bge-m3/
ls -la /model/bge-reranker-v2-m3/
```
