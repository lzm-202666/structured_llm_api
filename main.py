#计算耗时，统计请求花了多少秒
import time
#日志模块，打印运行信息，排查问题
import logging
from fastapi import FastAPI
#FastAPI的流式响应，用来做SSE流式输出，一段一段返回内容
from fastapi.responses import StreamingResponse
from schemas import ChatRequest,StructuredOutput
from openai import AsyncOpenAI
from config import LLM_API_KEY,LLM_BASE_URL

#配置日志+app+LLM客户端初始化
#配置全局规则，如：日志格式，输出时间，日志级别，信息内容
logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")
#获得本模块日志对象
logger = logging.getLogger(__name__)  #下面打印日志logger.info("xxx")
#创建FastAPI实例对象
app = FastAPI()
#LLM客户端初始化
client = AsyncOpenAI(api_key=LLM_API_KEY,base_url=LLM_BASE_URL)

#注册post接口函数-上游：接受请求，打日志，计时
#              -中间：所有业务逻辑，调用LLM，循环，生成器，计算
#              -下游：return 返回响应给前端
@app.post("/api/v1/chat")
async def chat_endpoint(request: ChatRequest):
    logger.info(f"收到请求：User={request.user_id},Message={request.message}")
    start_time = time.time()

    #异步生成器函数（流式生成器）
    async def event_generator():
        prompt = f"请提取以下文本的结构化信息，**输出标准JSON格式**：{request.message}"
        #开启流式＋JSON强势化输出
        stream = await client.chat.completions.create(
            model="deepseek-flash",
            messages=[{"role":"user","content":prompt}],
            stream=True,
            response_format={"type":"json_object"}
        )
        #循环接受大模型流式分片，逐段输出
        full_content = ""
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                #生成器内部：yield 的内容，标准SSE要包 data: xxx\n\n
                yield f"data: {content}\n\n"
        #循环跑完，结束推送信号
        yield "data: [DONE]\n\n"
        #请求结束：统计耗时，模拟token，成本日志
        #统计耗时，现在-开始
        elapsed = time.time()-start_time
        #模拟token一个汉字大约2个token
        prompt_tokens = len(request.message) // 2
        completions_tokens = len(full_content) // 2
        total_cost = (prompt_tokens*0.01 + completions_tokens*0.02) / 1000
        logger.info(f"请求完成 | 耗时：{elapsed:.2f}s | 预估Token：{prompt_tokens + completions_tokens} | 预估成本：{total_cost:.6f}元")

    #返回流式响应给客户端
    return StreamingResponse(event_generator(),media_type="text/event-stream")

