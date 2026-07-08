import asyncio
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
import os
from typing import Any
import backend.interview_router as interview
import backend.agent_router as agent
import backend.files_router as files
from pydantic import BaseModel

from backend.interview_rag import interview_chain   # 오늘 만든 직무 RAG chain
from backend.interview_graph_wrapper import run_interview_graph  # thread_id 유지 RAG
from backend.chains import (
    build_chat_chain,
    build_structured_chain,
    build_interview_parallel_chain,
    build_interview_parallel_stream_chains,
)
from backend.schemas import ChatRequest, ChatResponse
from backend.sse import sse, stream_text_chain

class InterviewRagRequest(BaseModel):
    question: str

class InterviewStructuredRequest(BaseModel):
    question: str
    answer: str

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

# ─── 모듈 레벨 1회 생성 — chain은 stateless, 모든 요청이 공유 ─────────
_interview_chat_chain = build_chat_chain()
_interview_structured_chain = build_structured_chain()
_interview_parallel_chain = build_interview_parallel_chain()
_interview_questions_chain, _interview_tips_chain = build_interview_parallel_stream_chains()


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


def _word_chunk_answer(answer: str):
    """완성된 답변 문자열을 5단어 단위로 쪼개 SSE 'token' 프레임을 만든다.

    interview_chain/run_interview_graph는 LangGraph 동기 invoke라 실제 토큰
    스트리밍이 어려워, backend/app.py의 /rag/stream과 동일하게 완성된 답변을
    사후에 청크로 쪼개 보낸다 (astream 효과 시뮬레이션).
    """
    words = answer.split()
    buffer = ""
    for i, word in enumerate(words):
        buffer += word + " "
        if (i + 1) % 5 == 0 or i == len(words) - 1:
            yield buffer.strip()
            buffer = ""


@app.get("/interview/rag/stream")
async def interview_rag_stream(question: str = Query(..., description="면접 코칭 질문")):
    """직무 기반 RAG 코칭 — SSE 스트리밍."""

    async def event_generator():
        result = await interview_chain.ainvoke({"question": question})

        for chunk in _word_chunk_answer(result.get("answer", "")):
            yield sse({"type": "token", "delta": chunk})
            await asyncio.sleep(0.05)

        yield sse({"type": "sources", "content": result.get("sources", [])})
        yield sse({"type": "done"})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/interview/rag/thread")
async def interview_rag_thread_endpoint(
    req: InterviewRagRequest,
    thread_id: str = Query(..., description="interview:{이름}:{회차} 형식의 세션 ID"),
):
    """thread_id로 대화 맥락을 유지하는 면접 코칭 — LangGraph checkpointer 기반.

    run_interview_graph()는 동기 함수(StateGraph.invoke) — asyncio.to_thread로
    event loop 블로킹을 방지한다.
    """
    return await asyncio.to_thread(run_interview_graph, req.question, thread_id)


@app.get("/interview/rag/thread/stream")
async def interview_rag_thread_stream(
    question: str = Query(..., description="면접 코칭 질문"),
    thread_id: str = Query(..., description="interview:{이름}:{회차} 형식의 세션 ID"),
):
    """thread_id 유지 RAG 코칭 — SSE 스트리밍."""

    async def event_generator():
        result = await asyncio.to_thread(run_interview_graph, question, thread_id)

        for chunk in _word_chunk_answer(result.get("answer", "")):
            yield sse({"type": "token", "delta": chunk})
            await asyncio.sleep(0.05)

        yield sse({"type": "sources", "content": result.get("sources", [])})
        yield sse({"type": "result", "content": {"thread_id": result.get("thread_id", thread_id)}})
        yield sse({"type": "done"})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/interview/chat", response_model=ChatResponse)
async def interview_chat_endpoint(req: ChatRequest):
    """직무 문서 없이 일반적인 면접 상담."""
    result = await _interview_chat_chain.ainvoke({"question": req.message})
    return {"reply": result}


@app.post("/interview/chat/stream")
async def interview_chat_stream(req: ChatRequest):
    """일반 면접 상담 — chain.astream()으로 실제 토큰 단위 스트리밍."""

    async def event_generator():
        async for frame in stream_text_chain(_interview_chat_chain, {"question": req.message}):
            yield frame
        yield sse({"type": "done"})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/interview/structured")
async def interview_structured_endpoint(req: InterviewStructuredRequest):
    """면접 답변을 점수/강점/개선점/후속 질문으로 평가."""
    result = await _interview_structured_chain.ainvoke({
        "question": req.question,
        "answer": req.answer,
    })
    return result.model_dump()


@app.post("/interview/structured/stream")
async def interview_structured_stream(req: InterviewStructuredRequest):
    """구조화 평가는 토큰 단위로 쪼개기 어려워 status → result → done 순으로 보낸다."""

    async def event_generator():
        yield sse({"type": "status", "label": "답변 평가 중..."})
        result = await _interview_structured_chain.ainvoke({
            "question": req.question,
            "answer": req.answer,
        })
        yield sse({"type": "result", "content": result.model_dump()})
        yield sse({"type": "done"})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/interview/parallel")
async def interview_parallel_endpoint(req: ChatRequest):
    """주제를 기반으로 예상 면접 질문 + 준비 팁을 동시 생성."""
    return await _interview_parallel_chain.ainvoke({"question": req.message})


@app.post("/interview/parallel/stream")
async def interview_parallel_stream(req: ChatRequest):
    """questions는 토큰 단위로 실시간 스트리밍하고, tips는 완료 후 한 번에 보낸다."""

    async def event_generator():
        payload = {"question": req.message}
        async for frame in stream_text_chain(_interview_questions_chain, payload):
            yield frame
        tips = await _interview_tips_chain.ainvoke(payload)
        yield sse({"type": "result", "content": {"tips": tips}})
        yield sse({"type": "done"})

    return StreamingResponse(event_generator(), media_type="text/event-stream")
