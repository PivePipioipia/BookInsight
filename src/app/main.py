import sys
import os
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import Any


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_PATH = os.path.join(PROJECT_ROOT, 'src')
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

# import Agent
from agent.agent import create_book_agent_executor


# Tạo một biến toàn cục để giữ Agent, dùng một dictđể dễ truyền qua lại
agent_cache = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- [FastAPI] Ứng dụng đang khởi động... ---")
    print("[FastAPI] Đang gọi 'nhà máy' để tạo Agent Executor...")
    # Tải model và khởi tạo Agent
    agent_executor = create_book_agent_executor()
    agent_cache["agent_executor"] = agent_executor
    print("[FastAPI] Agent đã được tải và sẵn sàng!")
    
    yield 
    
   
    print("--- [FastAPI] Ứng dụng đang tắt... ---")
    agent_cache.clear()

app = FastAPI(
    title="BookInsight API",
    description="API cho Trợ lý AI Đa công cụ BookInsight",
    version="1.0.0",
    lifespan=lifespan 
)

class ChatRequest(BaseModel):
    """Mẫu JSON mà client (frontend) sẽ gửi đến"""
    user_id: str = "default_user" # Tạm thời dùng 1 user
    question: str

class ChatResponse(BaseModel):
    """Mẫu JSON mà server sẽ trả về"""
    user_id: str
    answer: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Đây là endpoint chính để nói chuyện với Agent.
    Nó nhận câu hỏi và trả về câu trả lời.
    """
    print(f"[FastAPI] Nhận được câu hỏi từ user '{request.user_id}': {request.question}")
    
    agent_executor = agent_cache.get("agent_executor")
    
    if not agent_executor:
        return {"answer": "Lỗi: Agent chưa được khởi tạo."}

    response = agent_executor.invoke({"input": request.question})
    
    return ChatResponse(
        user_id=request.user_id,
        answer=response['output']
    )

@app.get("/")
async def root():
    return {"message": "Chào mừng đến với BookInsight API! Hãy dùng endpoint /chat."}