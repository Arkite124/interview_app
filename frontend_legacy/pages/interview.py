# interview_app/frontend/pages/interview.py
# 책임 메모:
# - Day 3에서 완성한 면접 질문 입력과 SSE 응답 표시를 이어받습니다.
# - st.session_state.settings에서 모델과 temperature를 읽습니다.
# - 8주차 agents.py, roles.py, tools.py 파일은 수정하지 않습니다.
from __future__ import annotations
import json
from typing import Any
from collections.abc import Iterator
import httpx
import streamlit as st
from dotenv import load_dotenv
from frontend_legacy.pages.settings import ensure_settings
from frontend_legacy.pages.history import ensure_session_state, get_selected_conversation
from frontend_legacy.api_client import get_backend_url
load_dotenv()


def initialize_messages()->None:
    """면접 대화 기록이 없으면 초기 안내 메시지를 준비합니다."""
    if "messages" not in st.session_state:
        st.session_state.messages=[{"role": "assistant", "content": "안녕하세요. AI 면접관 입니다."}]

initialize_messages()

def post_interview_message(message: str) -> dict[str, Any]:
    """면접 코치 백엔드에 일반 응답 요청을 보냅니다."""
    # TODO: httpx.Client를 사용해 get_backend_url() + "/chat"에 POST 요청을 보내요.
    with httpx.Client(base_url=get_backend_url(), timeout=10.0) as client:
        response = client.post("/chat", json={"message": message})
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
        "mode": settings["mode"],
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

            raw_data = line.removeprefix("data:").strip()

            if raw_data == "[DONE]":
                break

            # 1차 JSON 파싱
            try:
                event = json.loads(raw_data)
            except json.JSONDecodeError:
                # JSON이 아니면 그냥 텍스트로 간주
                yield raw_data
                continue

            event_type = event.get("type")

            if event_type == "status":
                continue

            if event_type == "token":
                delta = event.get("delta", "")

                # 핵심: delta 자체가 또 JSON 문자열인 경우 방어
                if isinstance(delta, str) and delta.strip().startswith("{"):
                    try:
                        nested_event = json.loads(delta)
                        if nested_event.get("type") == "token":
                            yield nested_event.get("delta", "")
                        continue
                    except json.JSONDecodeError:
                        pass

                yield delta


# -----------------------------
# 화면 렌더링
# -----------------------------

st.title("면접 연습")
st.caption("LLM 면접 코치가 함께 합니다.")

settings = ensure_settings()

st.caption(f"사용 중인 모델: {settings['model']}")
st.caption(f"답변 정확성/창의성: {settings['temperature']}")

ensure_session_state()

current_session = get_selected_conversation()

if current_session is None:
    st.error("현재 면접 세션을 찾을 수 없습니다.")
    st.stop()

messages = current_session["messages"]

for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("면접 답변을 입력해 주세요.")

if user_input:
    messages.append({
        "role": "user",
        "content": user_input,
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response_text = st.write_stream(
            stream_interview_message(user_input)
        )

    messages.append({
        "role": "assistant",
        "content": response_text,
    })

    st.rerun()
# TODO: st.session_state.settings에서 model, temperature를 읽어 화면에 표시해요.
# TODO: Day 3의 stream_interview_agent 호출 흐름을 이 페이지로 옮겨요.
# TODO: 사용자의 질문 입력과 assistant 응답 표시 영역을 배치해요.

