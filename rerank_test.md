# Rerank 服务测试文档

## 服务地址
- **地址**: `http://localhost:10020`
- **健康检查**: `GET /health`

---

## 基础测试

### 1. 健康检查
```bash
curl http://localhost:10020/health
```

### 2. 基础 rerank 测试
```bash
curl -X POST http://localhost:10020/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "query": "人工智能",
    "documents": ["AI 很强", "今天天气不错", "机器学习是人工智能的一个分支"]
  }'
```

---

## 测试用例

### 用例 1: 技术相关度测试
```bash
curl -X POST http://localhost:10020/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "query": "如何使用 Python 进行数据分析",
    "documents": [
      "Python 的 pandas 库是数据分析的强大工具",
      "今天北京天气晴朗",
      "NumPy 提供了多维数组对象和科学计算功能",
      "红烧肉的做法",
      "Matplotlib 可以绘制各种图表"
    ]
  }'
```

### 用例 2: 语义相似度测试
```bash
curl -X POST http://localhost:10020/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning algorithms",
    "documents": [
      "deep learning neural networks",
      "classical statistics methods",
      "decision trees and random forests",
      "cooking recipes"
    ]
  }'
```

### 用例 3: 单文档测试
```bash
curl -X POST http://localhost:10020/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "query": "大语言模型",
    "documents": ["Transformer 架构是 LLM 的基础"]
  }'
```

### 用例 4: 大量文档测试
```bash
curl -X POST http://localhost:10020/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "query": "机器学习",
    "documents": [
      "监督学习需要标注数据",
      "无监督学习发现数据内在结构",
      "强化学习通过奖励机制优化策略",
      "深度学习是机器学习的子领域",
      "传统机器学习包括 SVM、决策树等算法",
      "神经网络模仿人脑神经元连接",
      "梯度下降是优化模型参数的方法",
      "交叉验证评估模型泛化能力"
    ]
  }'
```

### 用例 5: 空文档测试
```bash
curl -X POST http://localhost:10020/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "query": "测试",
    "documents": []
  }'
```

---

## 预期结果说明

| 测试项 | 预期结果 |
|--------|----------|
| 相关文档 | 分数 > 0，越高越相关 |
| 不相关文档 | 分数 < 0 或接近 0 |
| 返回格式 | `{"data": [{"index": i, "score": float}]}` |
| 排序 | 按分数从高到低 |

---

## 常见问题

1. **503 Service Unavailable**: 服务未启动，检查 `ps aux | grep reranker`
2. **连接超时**: 模型正在加载，等待 30-60 秒后重试
3. **分数异常**: 检查输入文本是否为空或过长
