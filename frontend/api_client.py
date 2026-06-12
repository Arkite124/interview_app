# interview_app/frontend/api_client.py
from __future__ import annotations
import json
import os
from typing import Any
import httpx
from dotenv import load_dotenv
from collections.abc import Iterator
from frontend.pages.settings import ensure_settings
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

def get_backend_url() -> str:
    """면접 코치 FastAPI 백엔드 주소를 환경변수 또는 기본값으로 가져옵니다."""
    # 여기에 os.getenv()로 BACKEND_URL을 읽고, 없으면 http://localhost:8000을 반환하는 코드를 채워요.
    return BACKEND_URL

def post_interview_message(message: str) -> dict[str, Any]:
    """면접 코치 백엔드에 일반 응답 요청을 보냅니다."""
    # TODO: httpx.Client를 사용해 get_backend_url() + "/chat"에 POST 요청을 보내요.
    with httpx.Client(base_url=get_backend_url(),timeout=10.0) as client:
        response=client.post("/chat",json={"message":message})
    # TODO: response.raise_for_status()로 실패 응답을 확인해요.
        response.raise_for_status()
    # TODO: response.json()을 반환해요.
        return response.json()
    
def stream_interview_message(message: str) -> Iterator[str]:
    """면접 코치 백엔드의 SSE 응답을 순서대로 전달합니다."""

    settings = ensure_settings()

    payload = {
        "message": message,
        "model": settings["model"],
        "temperature": settings["temperature"],
        "system_prompt": settings["system_prompt"],
        "role_preset": settings["role_preset"],
    }

    url = f"{get_backend_url()}/agents/stream"

    with httpx.stream(
        "POST",
        url,
        json=payload,
        timeout=30.0,
    ) as response:
        response.raise_for_status()

        for line in response.iter_lines():
            if not line:
                continue

            if not line.startswith("data:"):
                continue

            raw_data = line[5:].strip()

            if raw_data == "[DONE]":
                break

            try:
                event = json.loads(raw_data)
            except json.JSONDecodeError:
                continue

            if event.get("type") == "token":
                yield event.get("delta", "")

            elif event.get("type") == "status":
                # run_item 같은 상태 이벤트는 화면에 출력하지 않음
                continue

def render_streaming_answer(placeholder: Any, message: str) -> str:
    """스트리밍 토큰을 누적해 면접 코치 답변을 화면에 표시합니다.

    Args:
        placeholder: st.empty()로 만든 Streamlit placeholder 객체
        message: 면접 질문 문자열

    Returns:
        누적된 전체 답변 문자열
    """
    full_text = ""
    for token in stream_interview_message(message):
        full_text+=token
        placeholder.markdown(full_text)
        # TODO: placeholder.markdown()으로 현재까지의 full_text를 화면에 다시 그려요.
    return full_text

    
    
    
    
    
        



