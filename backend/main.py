from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import backend.interview_router as interview

load_dotenv()

app=FastAPI(title="Customer Support Chatbot API",version="0.1.0")
allow_origins=["http://localhost:8501","http://localhost:5173","http://192.168.0.132"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(interview.router)

@app.get("/health")
def health_check()->dict[str,str]:
    """서버가 실행중인지 확인"""
    api_key=os.getenv("OPENAI_API_KEY")
    valid_key=False
    if not api_key:
        valid_key=False
    else : valid_key=True
    return{"status":str(valid_key)}