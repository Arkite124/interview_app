"""frontend/pages/chat.py — 💬 기본 면접 코치 채팅"""

import httpx
import streamlit as st

from app import BACKEND_URL, handle_backend_error, init_history, render_history, reset_button

HISTORY_KEY = "chat_messages"
init_history(HISTORY_KEY)

with st.sidebar:
    st.divider()
    reset_button(HISTORY_KEY)
    st.divider()
    st.caption("10주차 관통예제")
    st.caption("LangChain + LangGraph + Chroma")
    st.info("면접 코치로서 자유 질문에 답합니다.")

st.title("💬 기본 면접 코치")
st.caption("10주차 관통예제 — LangChain LCEL + LangGraph + Chroma RAG")

render_history(HISTORY_KEY)

if user_input := st.chat_input("질문을 입력하세요..."):
    st.session_state[HISTORY_KEY].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            response = httpx.post(
                f"{BACKEND_URL}/chat",
                json={"message": user_input},
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            reply = data.get("reply", "응답을 받지 못했습니다.")
            st.markdown(reply)
            st.session_state[HISTORY_KEY].append({
                "role": "assistant",
                "content": reply,
            })

        except Exception as e:
            handle_backend_error(e)
