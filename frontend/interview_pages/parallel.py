"""frontend/interview_pages/parallel.py — 🔀 질문 생성 + 팁 (SSE — questions 토큰 + tips 결과)"""

import streamlit as st

from interview_app import BACKEND_URL, handle_backend_error, init_history, render_history, reset_button, stream_sse

HISTORY_KEY = "interview_parallel_messages"
init_history(HISTORY_KEY)

with st.sidebar:
    st.divider()
    reset_button(HISTORY_KEY)
    st.divider()
    st.caption("면접 코치 RAG 서비스")
    st.caption("LangChain + LangGraph + Chroma")
    st.info("주어진 주제로 면접 질문과 준비 팁을 동시에 생성합니다.")

st.title("🔀 질문 생성 + 팁")
st.caption("직무 채용 공고 기반 — LangChain LCEL + LangGraph + Chroma RAG (스트리밍)")

render_history(HISTORY_KEY)

if user_input := st.chat_input("주제를 입력하세요..."):
    st.session_state[HISTORY_KEY].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            st.markdown("### 📝 생성된 면접 질문")
            questions_placeholder = st.empty()
            questions = ""
            tips = "-"
            for event in stream_sse(
                "POST", f"{BACKEND_URL}/interview/parallel/stream", json={"message": user_input}
            ):
                etype = event.get("type")
                if etype == "token":
                    questions += event.get("delta", "")
                    questions_placeholder.markdown(questions)
                elif etype == "result":
                    tips = event.get("content", {}).get("tips", "-")

            if not questions:
                questions = "-"
                questions_placeholder.markdown(questions)

            st.markdown("### 💡 면접 준비 팁")
            st.markdown(tips)

            st.session_state[HISTORY_KEY].append({
                "role": "assistant",
                "content": (
                    f"**면접 질문:**\n{questions}\n\n"
                    f"**준비 팁:**\n{tips}"
                ),
            })

        except Exception as e:
            handle_backend_error(e)
