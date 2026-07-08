"""frontend/interview_pages/structured.py — 📊 면접 답변 평가 (SSE — status + result)

입력 형식: `질문 | 답변`
"""

import streamlit as st

from interview_app import BACKEND_URL, handle_backend_error, init_history, render_history, reset_button, stream_sse

HISTORY_KEY = "interview_structured_messages"
init_history(HISTORY_KEY)

with st.sidebar:
    st.divider()
    reset_button(HISTORY_KEY)
    st.divider()
    st.caption("면접 코치 RAG 서비스")
    st.caption("LangChain + LangGraph + Chroma")
    st.info("면접 답변을 점수/강점/개선점으로 구조화 평가합니다.\n\n**형식:** `질문 | 답변`")

st.title("📊 면접 답변 평가")
st.caption("직무 채용 공고 기반 — LangChain LCEL + LangGraph + Chroma RAG (스트리밍)")

render_history(HISTORY_KEY)

if user_input := st.chat_input("질문 | 답변 형식으로 입력하세요..."):
    st.session_state[HISTORY_KEY].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            parts = user_input.split("|", 1)
            if len(parts) == 2:
                question, answer = parts[0].strip(), parts[1].strip()
            else:
                question = "자기소개를 해주세요"
                answer = user_input

            status_placeholder = st.empty()
            result = {}
            for event in stream_sse(
                "POST",
                f"{BACKEND_URL}/interview/structured/stream",
                json={"question": question, "answer": answer},
            ):
                etype = event.get("type")
                if etype == "status":
                    status_placeholder.markdown(f"⏳ {event.get('label', '')}")
                elif etype == "result":
                    result = event.get("content", {})
            status_placeholder.empty()

            col1, col2 = st.columns([1, 3])
            with col1:
                score = result.get("score", 0)
                score_emoji = ["", "😟", "🤔", "😐", "😊", "🌟"][score]
                st.metric("면접 점수", f"{score}/5 {score_emoji}")
            with col2:
                st.markdown(f"**💪 강점:** {result.get('strengths', '-')}")
                st.markdown(f"**📝 개선점:** {result.get('improvements', '-')}")
                st.markdown(f"**❓ 후속 질문:** {result.get('next_question', '-')}")

            st.session_state[HISTORY_KEY].append({
                "role": "assistant",
                "content": (
                    f"**면접 점수:** {result.get('score', 0)}/5\n\n"
                    f"**강점:** {result.get('strengths', '-')}\n\n"
                    f"**개선점:** {result.get('improvements', '-')}\n\n"
                    f"**후속 질문:** {result.get('next_question', '-')}"
                ),
                "metadata": result,
            })

        except Exception as e:
            handle_backend_error(e)
