# Structured LLM API (结构化大模型流式接口)

## 📖 项目简介
基于 FastAPI 和 DeepSeek 大模型 API 构建的高并发异步接口，支持流式返回结构化的 JSON 信息，并包含 Token 成本监控与日志记录。

## 🛠️ 技术栈
- Python 3.13 + FastAPI + Pydantic
- 异步编程 (asyncio)
- 大模型 API (DeepSeek)
- Docker 容器化部署

## 🚀 快速开始
1. 配置 `.env` 文件（参考 `config.py` 里的环境变量）。
2. 安装依赖：`pip install -r requirements.txt`
3. 本地运行：`uvicorn main:app --reload`
4. Docker部署：`docker build -t structured-llm-api .` 及 `docker run -p 8000:8000 structured-llm-api`

## 📡 接口说明
- `POST /api/v1/chat`
- 请求体：`{"user_id": "xxx", "message": "需要解析的文本"}`
- 响应：SSE 流式返回，格式为 `data: {content}\n\n`，结束标志为 `data: [DONE]\n\n`。
