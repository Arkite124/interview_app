"""frontend/pages/parallel.py — 🔀 병렬 + 분기 응답 (답변 + FAQ)"""

import httpx
import streamlit as st

from app import BACKEND_URL, handle_backend_error, init_history, render_history, reset_button

HISTORY_KEY = "parallel_messages"
init_history(HISTORY_KEY)

with st.sidebar:
    st.divider()
    reset_button(HISTORY_KEY)
    st.divider()
    st.caption("10주차 관통예제")
    st.caption("LangChain + LangGraph + Chroma")
    st.info("병렬 응답(답변 + FAQ)을 동시에 생성합니다.")

st.title("🔀 병렬 + 분기 응답")
st.caption("10주차 관통예제 — LangChain LCEL + LangGraph + Chroma RAG")

render_history(HISTORY_KEY)

if user_input := st.chat_input("질문을 입력하세요..."):
    st.session_state[HISTORY_KEY].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            response = httpx.post(
                f"{BACKEND_URL}/chat/parallel",
                json={"message": user_input},
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()

            st.markdown("### 💬 답변")
            st.markdown(data.get("answer", "-"))
            st.markdown("### ❓ 관련 FAQ")
            st.markdown(data.get("faq", "-"))

            st.session_state[HISTORY_KEY].append({
                "role": "assistant",
                "content": (
                    f"**답변:** {data.get('answer', '-')}\n\n"
                    f"**FAQ:** {data.get('faq', '-')}"
                ),
            })

        except Exception as e:
            handle_backend_error(e)
