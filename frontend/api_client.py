# interview_app/frontend/api_client.py
from __future__ import annotations

import os
from typing import Any
import httpx
from dotenv import load_dotenv
from collections.abc import Iterator

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
    payload = {"message": message}
    url = f"{get_backend_url()}/chat/stream"
    # TODO: httpx.stream("POST", url, json=payload, timeout=30.0)으로 스트림을 엽니다.
    with httpx.stream(
        "POST",
        url,
        json=payload,
        timeout=30.0
    ) as response:
        # TODO: response.raise_for_status()를 with 블록 안에서 호출합니다.
        response.raise_for_status()
        # TODO: response.iter_lines()로 줄을 순회합니다.
        for line in response.iter_lines():
            # TODO: 빈 줄과 data: 접두사가 없는 줄을 건너뜁니다.
            if not line:
                continue
            if not line.startswith("data:"):
                continue
            # TODO: token = line[5:].strip() 으로 실제 값만 추출합니다.
            token=line[5:].strip()
            # TODO: token이 "[DONE]"이면 반복을 멈춥니다.
            if token=="[DONE]":
                break
            # TODO: 그 외에는 yield token으로 넘깁니다.
            yield token

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

    
    
    
    
    
        



