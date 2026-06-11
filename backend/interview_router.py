import os
from collections.abc import AsyncIterator
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import AsyncOpenAI
from fastapi import HTTPException
from pydantic import BaseModel, Field
# from sessons import *
from backend.sessions import *

load_dotenv()

# 여기에 APIRouter를 만들어요.
# prefix="/interview", tags=["interview"] 로 설정합니다.
router = APIRouter(prefix="/interview",tags=["interview"])
# (3) 출력 검증+import만 — 아래 TODO 주석을 파일에 추가하고 import 위치를 확인한다.
# 응답 모델
class SessionCreateResponse(BaseModel):
    session_id: str
    role: str

# 세션 생성 요청 모델
class SessionCreateRequest(BaseModel):
    role: str = Field(default="general", description="초기 면접관 유형")

class HistoryResponse(BaseModel):
    session_id: str
    messages: list[dict[str, str]]
    role: str
    message_count: int
ALLOWED_ROLES = {"general", "technical", "hr"}

class RoleUpdateRequest(BaseModel):
    role: str = Field(..., description="변경할 면접관 유형 (general · technical · hr)")

class RoleUpdateResponse(BaseModel):
    session_id: str
    role: str
    message: str
# TODO 1: UUID 세션 관리
# from interview_app.backend.sessions import create_session, add_message, get_history
# → day2-self2에서 연결. session_id 를 InterviewStreamRequest 에서 받아 get_history() 로 이전 이력을 꺼낸다.
# 엔드포인트
@router.post("/session/create", response_model=SessionCreateResponse)
async def create_interview_session(body: SessionCreateRequest) -> SessionCreateResponse:
#     힌트:
#     - create_session(body.role) 로 session_id 를 얻는다.
#     - SessionCreateResponse(session_id=session_id, role=body.role) 를 반환한다.
    session_id=create_session(body.role)
    return SessionCreateResponse(session_id=session_id,role=body.role)

@router.get("/session/{session_id}/history", response_model=HistoryResponse)
async def get_interview_history(session_id: str) -> HistoryResponse:
    """
    세션 ID 로 면접 이력을 조회합니다.

    힌트:
    - try: get_history(session_id) 로 이력을 꺼낸다.
    - except KeyError: raise HTTPException(status_code=404, detail="session not found")
    - HistoryResponse(...) 를 반환한다.
    """
    try:
        # 여기에 get_history(session_id) 호출 코드를 채워요.
        messages = get_history(session_id)
        role = get_session_role(session_id)
    except KeyError:
        # 여기에 HTTPException(status_code=404, ...) 을 발생시키는 코드를 채워요.
        raise HTTPException(status_code=404,detail="없는 세션 번호입니다.")

    return HistoryResponse(
        session_id=session_id,
        messages=messages,
        role=role,
        message_count=len(messages),
    )
@router.patch("/session/{session_id}/role", response_model=RoleUpdateResponse)
async def update_interview_role(session_id: str, body: RoleUpdateRequest):
#   1. body.role 이 ALLOWED_ROLES 에 없으면 HTTPException(status_code=400, ...) 발생
#   2. set_session_role(session_id, body.role) 호출 (없는 세션이면 KeyError → 404)
#   3. RoleUpdateResponse(...) 반환
    if body.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400,detail="role의 형식이 잘못되었습니다.")
    allowed_session=set_session_role(session_id,body.role)
    if allowed_session:
        raise KeyError("없는 세션입니다.")
    return RoleUpdateResponse(
        session_id=session_id,
        role=body.role,
        message="수정"
    )
    # TODO 2: 예외 핸들러
# from interview_app.backend.errors import register_exception_handlers
# → backend/main.py 에서 register_exception_handlers(app) 로 등록한다.
# → RateLimitError → 429, APIError → 502 로 변환.

# TODO 3: 토큰 사용량 추적
# from interview_app.backend.usage import record_usage
# → stream 경로에서 usage 기록 시점이 제한될 수 있으므로 일반 /interview 엔드포인트에서 먼저 연결.

# TODO 4: 8주차 역할 프리셋 재사용
# from interview_app.core.roles import ROLE_PROMPTS  (8주차 roles.py 이미 있으면 import만)
# → 본 파일의 ROLE_PROMPTS 와 8주차 코드를 비교해 import 중심으로 재사용. 재작성 금지.
class InterviewStreamRequest(BaseModel):
    """면접 코치 `/interview/stream` 엔드포인트가 받는 요청 모델입니다."""
    question: str = Field(
        ...,
        min_length=1,
        description="면접관이 제시한 질문입니다.",
        examples=["자기소개를 해 주세요."]
        # 여기에 examples=["자기소개를 해 주세요."] 를 추가해요.
    )
    answer: str = Field(
        ...,
        min_length=1,
        description="지원자가 입력한 답변입니다.",
        examples=["안녕하세요, 저는 ..."]
        # 여기에 examples=["안녕하세요, 저는 ..."] 를 추가해요.
    )
    role: str = Field(
        default="general",
        description="면접관 유형입니다. general · technical · hr 중 하나를 사용합니다.",
        examples=["technical"]
        # 여기에 examples=["technical"] 를 추가해요.
    )
    session_id: str | None = Field(
        default=None,
        description="UUID 기반 면접 세션 ID입니다. self2에서 연결합니다.",
    )
    model: str = Field(default="gpt-5.4-nano", description="사용할 OpenAI 모델명입니다.")

def get_interview_openai_client() -> AsyncOpenAI:
    """환경 변수에서 OPENAI_API_KEY를 읽어 AsyncOpenAI 클라이언트를 만듭니다."""
    # 여기에 os.getenv("OPENAI_API_KEY") 로 키를 읽는 코드를 채워요.
    api_key =os.getenv("OPENAI_API_KEY")

    if not api_key:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail="OPENAI_API_KEY is not configured",
        )
    # 여기에 AsyncOpenAI(api_key=api_key) 를 반환하는 코드를 채워요.
    return AsyncOpenAI(api_key=api_key)
ROLE_PROMPTS: dict[str, str] = {
    "general": "당신은 일반 면접관입니다. 지원자의 답변을 종합적으로 평가하고 개선점을 한국어로 피드백하세요.",
    "technical": "당신은 기술 면접관입니다. 지원자의 기술 역량과 문제 해결 방식을 집중 평가하고 한국어로 피드백하세요.",
    "hr": "당신은 인사 면접관입니다. 지원자의 인성, 협업 능력, 조직 적합성을 평가하고 한국어로 피드백하세요.",
}
async def interview_event_generator(
    request: InterviewStreamRequest,
) -> AsyncIterator[str]:
    """
    면접 코치 피드백을 SSE data 이벤트로 스트리밍합니다.

    작성 흐름:
    1. get_interview_openai_client() 를 호출해 client 를 얻는다.
    2. ROLE_PROMPTS 에서 request.role 에 맞는 system_prompt 를 꺼낸다.
       (없으면 "general" 사용)
    3. client.chat.completions.create(..., stream=True) 로 스트림을 연다.
       messages 는 [system_prompt, user 메시지(질문+답변)] 두 개다.
    4. async for chunk in stream: 으로 순회하며
       delta.content 가 있을 때만 f"data: {delta.content}\n\n" 를 yield 한다.
    5. 순회 완료 후 "data: [DONE]\n\n" 을 yield 한다.
    """
    # 여기에 전체 코드를 채워요.

    client=get_interview_openai_client()

    
    # TODO 세션 이력 연결:
    # if request.session_id:
    #     history = get_history(request.session_id)
    #     # history 를 messages 앞에 붙인다.
    user_content = (
        f"[면접 질문]\n{request.question}\n\n"
        f"[지원자 답변]\n{request.answer}\n\n"
        "위 답변을 면접관 역할에 맞게 평가하고 개선 피드백을 제공해 주세요."
    )    
    # TODO 예외 핸들러 연결:
    # try: ... except RateLimitError: ... except APIError: ...
    # → backend/main.py 에서 register_exception_handlers(app) 로 등록하면
    #   여기서 직접 except 없어도 429/502 로 자동 변환.

    stream=await client.chat.completions.create(
        max_completion_tokens=1000,
        model=request.model,
        stream=True,
        messages=[
            {"role":"system","content":ROLE_PROMPTS[request.role]},
            {"role":"user","content":f"질문 : {request.question} \n 답변: {request.answer}"}
            ],
        stream_options={"include_usage": True}
    )
    async for chunk in stream:
        delta=chunk.choices[0].delta
        token=delta.content or ""
        if not token:
            continue
        yield f"data: {token}\n\n"
    # TODO 토큰 사용량 추적:
    # stream 경로에서는 usage 기록 시점이 chunk 마지막에 올 수 있다.
    # stream=True + stream_options={"include_usage": True} 로 요청하면
    # 마지막 chunk 에서 usage 를 받을 수 있다.
    # from interview_app.backend.usage import record_usage
    # record_usage(request.session_id, last_chunk.usage)
    yield "data: [DONE]\n\n"
    
@router.post("/stream")
async def interview_stream(request: InterviewStreamRequest) -> StreamingResponse:
    """
    면접관 유형에 맞는 피드백을 SSE 형식으로 스트리밍합니다.

    힌트:
    - StreamingResponse(interview_event_generator(request), media_type="text/event-stream", ...) 형태로 반환한다.
    - headers 에 "Cache-Control": "no-cache", "X-Accel-Buffering": "no" 를 추가한다.
    """
    # 여기에 StreamingResponse 반환 코드를 채워요.
    return StreamingResponse(
        interview_event_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
