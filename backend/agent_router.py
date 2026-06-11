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
import json
from openai.types.responses import ResponseTextDeltaEvent
from agents import Runner, RunItemStreamEvent, ModelSettings
from fastapi.responses import StreamingResponse
from core.agents import *
# /agents 경로로 시작하는 라우터를 한 파일에 모읍니다.
router = APIRouter(prefix="/agents", tags=["agents"])


class InterviewAgentRequest(BaseModel):
    """면접 에이전트 스트림 요청 값을 담습니다."""
    message: str
    mode: str = "single"
    model: str | None = None
    temperature: float | None = None
    system_prompt: str | None = None
    role_preset: str | None = None


@router.post("/stream")
async def stream_interview_agent_endpoint(request: InterviewAgentRequest):
    return StreamingResponse(
        run_interview_agent_stream(
            message=request.message,
            mode=request.mode,
            model=request.model,
            temperature=request.temperature,
            system_prompt=request.system_prompt,
            role_preset=request.role_preset,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

async def run_interview_agent_stream(
    message: str,
    mode: str,
    model: str | None = None,
    temperature: float | None = None,
    system_prompt: str | None = None,
    role_preset: str | None = None,
):
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

    # 프론트에서 받은 설정값을 런타임 agent에 반영
    clone_kwargs = {}

    if model:
        clone_kwargs["model"] = model

    if system_prompt:
        clone_kwargs["instructions"] = system_prompt

    if temperature is not None:
        clone_kwargs["model_settings"] = ModelSettings(
            temperature=temperature
        )

    if clone_kwargs:
        agent = agent.clone(**clone_kwargs)

    # role_preset은 당장 agent 선택에 쓰거나, 입력에 붙여서 전달할 수 있음
    input_text = message

    if role_preset:
        input_text = f"[면접 유형: {role_preset}]\n\n{message}"

    stream_result = Runner.run_streamed(
        starting_agent=agent,
        input=input_text,
    )

    async for sse in iter_agent_events(stream_result.stream_events()):
        yield sse

async def iter_agent_events(agent_stream):
    """에이전트 스트림 이벤트를 SSE 형식으로 정리합니다."""

    async for event in agent_stream:
        # 1) 모델 토큰 delta 이벤트 처리
        if getattr(event, "type", None) == "raw_response_event":
            data = getattr(event, "data", None)

            if isinstance(data, ResponseTextDeltaEvent):
                payload = {
                    "type": "token",
                    "delta": data.delta,
                }

                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                continue

        # 2) run item 이벤트 처리
        if isinstance(event, RunItemStreamEvent):
            payload = {
                "type": "status",
                "label": "run_item",
            }

            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

            item = getattr(event, "item", None)
            item_name = getattr(item, "name", "")

            if "handoff" in str(item_name).lower():
                handoff_payload = {
                    "type": "status",
                    "label": "handoff_detected",
                }

                yield f"data: {json.dumps(handoff_payload, ensure_ascii=False)}\n\n"

            continue

    yield "data: [DONE]\n\n"