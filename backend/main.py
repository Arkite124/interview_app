from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from typing import Any
import backend.interview_router as interview
import backend.agent_router as agent
import backend.files_router as files
from pydantic import BaseModel

from backend.interview_rag import interview_chain   # 오늘 만든 직무 RAG chain

class InterviewRagRequest(BaseModel):
    question: str
load_dotenv()

app=FastAPI(title="Customer Support Chatbot API",version="0.1.0")
allow_origins=["http://localhost:8501","http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(interview.router)
app.include_router(agent.router)
app.include_router(files.router)
@app.get("/health")
def health_check()->dict[str,Any]:
    """서버가 실행중인지 확인"""
    api_key=os.getenv("OPENAI_API_KEY")
    if not api_key:
        valid_key=False
    else : valid_key=True
    return{"status":valid_key}

@app.post("/interview/rag")
async def interview_rag_endpoint(req: InterviewRagRequest):
    # async endpoint에서는 ainvoke — answer와 sources가 한 응답에 담겨요
    # sources는 이미 dict 목록이라 그대로 JSON 직렬화됩니다 (Document 객체 반환 금지)
    return await interview_chain.ainvoke({"question": req.question})
