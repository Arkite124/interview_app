"""backend/sse.py — SSE(Server-Sent Events) 공용 헬퍼

backend/app.py, backend/main.py의 모든 /stream 엔드포인트가 공유하는 이벤트 계약:
  data: {"type": "status", "label": str}      — 진행 상태 안내
  data: {"type": "token", "delta": str}       — 텍스트 조각 (누적 시 전체 답변)
  data: {"type": "sources", "content": [...]} — RAG 출처 목록
  data: {"type": "result", "content": {...}}  — 구조화/부가 결과 (faq, score, tips 등)
  data: {"type": "done"}                      — 스트림 종료
"""

import json


def sse(event: dict) -> str:
    """dict를 SSE 'data: {...}\\n\\n' 프레임 문자열로 변환."""
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


async def stream_text_chain(chain, payload: dict):
    """LCEL chain의 astream() 결과를 'token' SSE 이벤트로 변환하는 공용 제너레이터.

    StrOutputParser가 붙은 chain은 astream()이 문자열 조각을 그대로 내놓지만,
    모델을 직접 스트리밍하는 경우 AIMessageChunk가 나올 수 있어 .content로 방어한다.
    """
    async for chunk in chain.astream(payload):
        token = chunk if isinstance(chunk, str) else getattr(chunk, "content", str(chunk))
        if token:
            yield sse({"type": "token", "delta": token})
