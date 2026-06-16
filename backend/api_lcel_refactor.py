from fastapi import FastAPI
from pydantic import BaseModel
from pydantic import Field
from openai import AsyncOpenAI
from dotenv import load_dotenv
from core.chain import build_chat_chain
from agents import set_trace_processors
from langsmith.integrations.openai_agents_sdk import OpenAIAgentsTracingProcessor
load_dotenv()
from fastapi.responses import StreamingResponse
import json

app=FastAPI()
# client=AsyncOpenAI()
chain=build_chat_chain()
class ChatRequest(BaseModel):
    message:str

@app.post("/chat")
async def chat(req:ChatRequest):
    # response=await client.chat.completions.create(
    #     model=get_model(),
    #     messages=[{
    #         "role":"user",
    #         "content":req.message
    #     }]
    # )
    # result=response.choices[0].message.content
    result=await chain.ainvoke({"question":req.message})
    set_trace_processors([OpenAIAgentsTracingProcessor()])
    return {"reply":result}

@app.post("/chat/stream")
async def stream_chat(req: ChatRequest):

    async def sse_gen():
        # [위치 1] chain.astream() 호출
        # chain이 토큰 조각을 비동기로 하나씩 내놓는 곳
        async for chunk in chain.astream({"question": req.message}):

            # chunk가 문자열이면 그대로 사용
            # chunk가 AIMessageChunk라면 chunk.content를 써야 할 수 있음
            token = chunk.content if hasattr(chunk, "content") else str(chunk)

            # [위치 2] async generator가 조각을 SSE frame으로 포장
            yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"

        # 스트림 종료 신호
        yield "data: [DONE]\n\n"

    # [위치 3] StreamingResponse 반환
    # FastAPI가 sse_gen()을 스트리밍 응답으로 흘려보내게 함
    return StreamingResponse(
        sse_gen(),
        media_type="text/event-stream"
    )