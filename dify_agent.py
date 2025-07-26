import os
from fastapi.responses import StreamingResponse
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 环境变量配置
DIFY_API_URL = os.getenv("DIFY_API_URL", "http://localhost/v1/chat-messages")
DIFY_API_KEY = os.getenv("DIFY_API_KEY", "app-o0GB6iXkTGpLJjodoBYOHb7J")

class ChatRequest(BaseModel):
    query: str
    conversation_id: str = ""
    user: str = ""
    files: list = []

@app.post("/chat")
async def chat_stream(request: Request, chat_request: ChatRequest):
    """
    流式聊天接口，将请求转发到Dify API并以SSE流返回响应
    """
    # 构建Dify请求体
    dify_payload = {
        "inputs": {},
        "query": chat_request.query,
        "response_mode": "streaming",
        "conversation_id": chat_request.conversation_id,
        "user": chat_request.user,
        "files": chat_request.files
    }

    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    # 创建SSE流响应
    async def event_stream():
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # 发送请求到Dify API
                async with client.stream(
                    "POST",
                    DIFY_API_URL,
                    headers=headers,
                    json=dify_payload
                ) as response:
                    # 处理非200响应
                    if response.status_code != 200:
                        error_data = await response.aread()
                        yield f"event: error\ndata: {error_data}\n\n"
                        return

                    # 流式转发Dify响应
                    async for chunk in response.aiter_bytes():
                        # 将原始SSE块转发给客户端
                        yield chunk
                        
            except httpx.RequestError as e:
                # 处理请求错误
                error_event = {
                    "event": "error",
                    "message": f"Connection error: {str(e)}",
                    "code": "connection_error"
                }
                yield f"data: {error_event}\n\n"
            except Exception as e:
                # 处理其他异常
                error_event = {
                    "event": "error",
                    "message": f"Internal server error: {str(e)}",
                    "code": "server_error"
                }
                yield f"data: {error_event}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )

# 健康检查端点
@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    
    # 启动配置 - 延长超时时间
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        timeout_keep_alive=180,  # 保持连接超时时间设为3分钟
        timeout_graceful_shutdown=30
    )