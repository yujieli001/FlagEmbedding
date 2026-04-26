import os
import math
import torch
from FlagEmbedding import FlagReranker
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Dify Compatible Reranker")

# =========================
# 请求结构（必须和 Dify 对齐）
# =========================
class RerankRequest(BaseModel):
    query: str
    documents: List[str]
    score_threshold: float | None = None  # Dify 可能传入的阈值

# =========================
# 环境变量配置
# =========================
MODEL_NAME = os.environ.get('RERANKER_MODEL_NAME', 'BAAI/bge-reranker-v2-m3')
MODEL_PATH = os.environ.get('RERANKER_MODEL_PATH', f'/model/{MODEL_NAME.split("/")[-1]}')
USE_FP16 = os.environ.get('RERANKER_USE_FP16', 'false').lower() == 'true'
USE_GPU = os.environ.get('RERANKER_USE_GPU', 'false').lower() == 'true'
HOST = os.environ.get('RERANKER_HOST', '0.0.0.0')
PORT = int(os.environ.get('RERANKER_PORT', 10020))

print(f"🚀 Loading reranker model: {MODEL_PATH}")

# =========================
# 初始化模型
# =========================
device = 'cuda' if torch.cuda.is_available() and USE_GPU else 'cpu'

model = FlagReranker(
    MODEL_PATH,
    use_fp16=USE_FP16,
    devices=device
)

print(f"✅ Model loaded on {device}")

# =========================
# 工具函数：sigmoid归一化（关键）
# =========================
def sigmoid(x):
    try:
        return 1 / (1 + math.exp(-x))
    except:
        return 0.0

# =========================
# 核心接口（Dify调用）
# =========================
@app.post("/v1/rerank")
@app.post("/rerank")
async def rerank(request: RerankRequest):
    try:
        query = request.query
        docs = request.documents

        if not query or not docs:
            return {"results": []}

        # 构造 pairs
        pairs = [(query, d) for d in docs]
        scores = model.compute_score(pairs)

        if not isinstance(scores, list):
            scores = [scores]

        # 绑定 index + score + document，并使用 sigmoid 归一化
        results = []
        for i, (score, doc) in enumerate(zip(scores, docs)):
            normalized_score = sigmoid(float(score))
            results.append({
                "index": i,
                "relevance_score": normalized_score,
                "score": normalized_score,
                "document": doc
            })

        # 按分数从高到低排序
        results.sort(key=lambda x: x["score"], reverse=True)

        # 应用分数阈值过滤
        threshold = request.score_threshold or 0.0
        results = [r for r in results if r["score"] >= threshold]

        print("RERANK RESULTS:", results)

        return {"results": results}

    except Exception as e:
        print("❌ Error:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# =========================
# 健康检查
# =========================
@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME}


# =========================
# 模型列表（兼容一些客户端）
# =========================
@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_NAME,
                "object": "model",
                "owned_by": "local"
            }
        ]
    }


# =========================
# 启动服务
# =========================
if __name__ == "__main__":
    import uvicorn
    print(f"🚀 Starting service at http://{HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT, workers=1)