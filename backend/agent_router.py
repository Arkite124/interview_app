"""
Day 3 self2 책임 메모
---------------------
- 이 파일이 담당하는 것:
  → (여기에 적어요: 8주차 에이전트를 감싸고 SSE로 내보내는 백엔드 라우터)

- 이 파일이 담당하지 않는 것:
  → (여기에 적어요: 화면 표시, 사용자 입력 처리, AI 키 관리)

- Day 3 self1의 api_client.py와의 관계:
  → (여기에 적어요: 프론트 api_client.py가 이 파일의 엔드포인트를 호출한다)

- 8주차 파일 재사용 원칙:
  → roles.py, tools.py, agents.py는 재작성하지 않고 import만 한다.
"""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel
from agents import Runner
import json
import json
from openai.types.responses import ResponseTextDeltaEvent
from agents import RunItemStreamEvent
from fastapi.responses import StreamingResponse
from core.agents import *
# /agents 경로로 시작하는 라우터를 한 파일에 모읍니다.
router = APIRouter(prefix="/agents", tags=["agents"])


class InterviewAgentRequest(BaseModel):
    """면접 에이전트 스트림 요청 값을 담습니다."""
    # TODO: 면접 질문 텍스트 필드를 추가하세요 (str 타입, 필수).
    message:str
    # TODO: 일반(single) 또는 멀티에이전트(multi) 모드 값을 추가하세요
    #       (str 타입, 기본값 "single").
    mode:str="single"


@router.post("/stream")
async def stream_interview_agent_endpoint(request: InterviewAgentRequest):
    return StreamingResponse(
        run_interview_agent_stream(
            message=request.message,
            mode=request.mode,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
async def run_interview_agent_stream(message: str, mode: str):
    if mode == "single":
        agent = interview_agent
    elif mode == "multi":
        agent = triage_agent
    else:
        payload = {
            "type": "error",
            "message": f"지원하지 않는 mode입니다: {mode}",
        }
        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
        return

    stream_result = Runner.run_streamed(
        starting_agent=agent,
        input=message,
    )

    async for sse in iter_agent_events(stream_result.stream_events()):
        yield sse

async def iter_agent_events(agent_stream):
    """에이전트 스트림 이벤트를 SSE 형식으로 정리합니다."""
    async for event in agent_stream:
        # 1. 토큰 스트리밍 이벤트
        if isinstance(event, ResponseTextDeltaEvent):
            payload = {
                "type": "token",
                "delta": event.delta,
            }
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        # 2. 실행 상태 이벤트
        elif isinstance(event, RunItemStreamEvent):
            payload = {
                "type": "status",
                "label": "run_item",
            }
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

            # 3. Handoff 감지
            event_name = getattr(event, "name", "")
            if "handoff" in event_name.lower():
                payload = {
                    "type": "status",
                    "label": "handoff_detected",
                }
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        # 4. 혹시 다른 event에도 name이 있을 수 있으므로 별도 체크
        else:
            event_name = getattr(event, "name", "")
            if "handoff" in event_name.lower():
                payload = {
                    "type": "status",
                    "label": "handoff_detected",
                }
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    # 스트림 종료 신호
    yield "data: [DONE]\n\n"