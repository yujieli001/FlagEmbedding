from FlagEmbedding import FlagModel
from flask import Flask, request, jsonify
import numpy as np

model = FlagModel(
    '/model/bge-m3',
    use_fp16=False,
    query_instruction_for_retrieval="",  # BGE-M3不需要指令
    devices='cpu'  # 明确指定CPU
)

app = Flask(__name__)

# 兼容 AnythingLLM 的 OpenAI 格式
@app.route("/v1/embeddings", methods=["POST"])
def embeddings():
    data = request.json
    # 获取输入文本（支持两种格式）
    if "input" in data:
        texts = data["input"]
    elif "texts" in data:  # 兼容你原来的格式
        texts = data["texts"]
    else:
        return jsonify({"error": "No input provided"}), 400
    
    # 确保是列表
    if isinstance(texts, str):
        texts = [texts]
    
    # 编码
    embeddings = model.encode(texts)
    
    # 转换为 OpenAI 格式
    response = {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "index": i,
                "embedding": emb.tolist() if hasattr(emb, 'tolist') else emb
            }
            for i, emb in enumerate(embeddings)
        ],
        "model": "bge-m3",
        "usage": {
            "prompt_tokens": sum(len(t) for t in texts),
            "total_tokens": sum(len(t) for t in texts)
        }
    }
    return jsonify(response)

# 保留你原来的接口（可选）
@app.route("/embed", methods=["POST"])
def embed():
    texts = request.json.get("texts", [])
    vecs = model.encode(texts)
    return jsonify({"embeddings": vecs.tolist()})

# 健康检查端点
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": "bge-m3"})

# 模型信息端点（AnythingLLM 可能需要）
@app.route("/v1/models", methods=["GET"])
def list_models():
    return jsonify({
        "object": "list",
        "data": [{
            "id": "bge-m3",
            "object": "model",
            "created": 1677610602,
            "owned_by": "local"
        }]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10010, threaded=True)
