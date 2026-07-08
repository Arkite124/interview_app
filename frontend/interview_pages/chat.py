"""frontend/interview_pages/chat.py — 💬 일반 면접 상담 (SSE 스트리밍)"""

import streamlit as st

from interview_app import BACKEND_URL, handle_backend_error, init_history, render_history, reset_button, stream_sse

HISTORY_KEY = "interview_chat_messages"
init_history(HISTORY_KEY)

with st.sidebar:
    st.divider()
    reset_button(HISTORY_KEY)
    st.divider()
    st.caption("면접 코치 RAG 서비스")
    st.caption("LangChain + LangGraph + Chroma")
    st.info("직무 문서 없이 일반적인 면접 조언을 제공합니다.")

st.title("💬 일반 면접 상담")
st.caption("직무 채용 공고 기반 — LangChain LCEL + LangGraph + Chroma RAG (스트리밍)")

render_history(HISTORY_KEY)

if user_input := st.chat_input("면접에 대해 무엇이든 물어보세요..."):
    st.session_state[HISTORY_KEY].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            placeholder = st.empty()
            reply = ""
            for event in stream_sse(
                "POST", f"{BACKEND_URL}/interview/chat/stream", json={"message": user_input}
            ):
                if event.get("type") == "token":
                    reply += event.get("delta", "")
                    placeholder.markdown(reply)

            if not reply:
                reply = "응답을 받지 못했습니다."
                placeholder.markdown(reply)

            st.session_state[HISTORY_KEY].append({
                "role": "assistant",
                "content": reply,
            })

        except Exception as e:
            handle_backend_error(e)
