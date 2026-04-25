import os
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Union, List

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

app = FastAPI(title="FlagEmbedding Service")

class EmbedRequest(BaseModel):
    model: str = "bge-m3"
    input: Union[str, List[str]]

class EmbedData(BaseModel):
    object: str = "embedding"
    index: int
    embedding: List[float]

class EmbedResponse(BaseModel):
    model: str
    object: str = "list"
    data: List[EmbedData]

class HealthResponse(BaseModel):
    status: str
    model: str

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = 1677610602
    owned_by: str = "local"

# 从环境变量读取配置
MODEL_NAME = os.environ.get('EMBEDDER_MODEL_NAME', 'BAAI/bge-m3')
MODEL_PATH = os.environ.get('EMBEDDER_MODEL_PATH', f'/model/{MODEL_NAME.split("/")[-1]}')
USE_FP16 = os.environ.get('EMBEDDER_USE_FP16', 'false').lower() == 'true'
HOST = os.environ.get('EMBEDDER_HOST', '0.0.0.0')
PORT = int(os.environ.get('EMBEDDER_PORT', 10010))

print(f"Loading model: {MODEL_PATH}")

# 初始化模型
device = 'cuda' if torch.cuda.is_available() and os.environ.get('EMBEDDER_USE_GPU', 'false').lower() == 'true' else 'cpu'
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True, torch_dtype=torch.float16 if USE_FP16 else torch.float32).to(device)
model.eval()

def generate_embeddings(texts: List[str]):
    """生成 embeddings"""
    all_embeddings = []
    with torch.no_grad():
        inputs = tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=512
        ).to(device)
        outputs = model(**inputs)
        # 使用 mean pooling
        embeddings = outputs.last_hidden_state.mean(dim=1)

        for idx, emb in enumerate(embeddings):
            emb_np = emb.cpu().numpy().astype(float)
            # L2 归一化
            emb_np = emb_np / np.linalg.norm(emb_np)
            all_embeddings.append(EmbedData(index=idx, embedding=emb_np.tolist()))
    return all_embeddings

@app.post("/v1/embeddings", response_model=EmbedResponse)
async def embed_route(request: EmbedRequest):
    """OpenAI 兼容的 embeddings 接口"""
    try:
        if isinstance(request.input, str):
            texts_to_embed = [request.input]
        else:
            texts_to_embed = request.input

        embed_data = generate_embeddings(texts_to_embed)
        return EmbedResponse(model=request.model, data=embed_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", response_model=HealthResponse)
async def health():
    """健康检查"""
    return HealthResponse(status="ok", model=MODEL_NAME)

@app.get("/v1/models", response_model=List[ModelInfo])
async def list_models():
    """模型列表"""
    return [ModelInfo(id=MODEL_NAME)]

if __name__ == "__main__":
    import uvicorn
    print(f"Starting service on {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT, workers=2)
