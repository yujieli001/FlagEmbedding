import os
import torch
from FlagEmbedding import FlagReranker
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="FlagReranker Service")

class RerankRequest(BaseModel):
    query: str
    documents: List[str]
    model: str = "reranker"

class RerankResult(BaseModel):
    index: int
    score: float
    document: str

class RerankResponse(BaseModel):
    object: str = "list"
    data: List[RerankResult]
    model: str

# 从环境变量读取配置
MODEL_NAME = os.environ.get('RERANKER_MODEL_NAME', 'BAAI/bge-reranker-v2-m3')
MODEL_PATH = os.environ.get('RERANKER_MODEL_PATH', f'/model/{MODEL_NAME.split("/")[-1]}')
USE_FP16 = os.environ.get('RERANKER_USE_FP16', 'false').lower() == 'true'
HOST = os.environ.get('RERANKER_HOST', '0.0.0.0')
PORT = int(os.environ.get('RERANKER_PORT', 10020))

print(f"Loading reranker model: {MODEL_PATH}")

# 初始化模型
model = FlagReranker(
    MODEL_PATH,
    use_fp16=USE_FP16,
    devices='cuda' if torch.cuda.is_available() and os.environ.get('RERANKER_USE_GPU', 'false').lower() == 'true' else 'cpu'
)

@app.post("/rerank")
@app.post("/v1/rerank")
async def rerank_route(request: RerankRequest):
    """Rerank 接口 - 兼容 OpenAI/AnythingLLM 格式"""
    try:
        if not request.query or not request.documents:
            raise HTTPException(status_code=400, detail="query or documents missing")

        # 单条处理，避免 Qwen3 模型的 batch size 限制
        scores = []
        for doc in request.documents:
            score = model.compute_score([[request.query, doc]])
            scores.append(score[0] if isinstance(score, list) else score)

        # 按分数从高到低排序
        results = [
            RerankResult(index=i, score=float(score), document=doc)
            for i, (score, doc) in enumerate(zip(scores, request.documents))
        ]
        results.sort(key=lambda x: x.score, reverse=True)

        return RerankResponse(data=results, model=MODEL_NAME)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "model": MODEL_NAME}

@app.get("/v1/models")
async def list_models():
    """模型列表"""
    return {
        "object": "list",
        "data": [{"id": MODEL_NAME, "object": "model", "owned_by": "local"}]
    }

if __name__ == "__main__":
    import uvicorn
    print(f"Starting reranker service on {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT, workers=2)
