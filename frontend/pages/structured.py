"""frontend/pages/structured.py — 📊 면접 답변 구조화 평가

입력 형식: `질문 | 답변`
"""

import httpx
import streamlit as st

from app import BACKEND_URL, handle_backend_error, init_history, render_history, reset_button

HISTORY_KEY = "structured_messages"
init_history(HISTORY_KEY)

with st.sidebar:
    st.divider()
    reset_button(HISTORY_KEY)
    st.divider()
    st.caption("10주차 관통예제")
    st.caption("LangChain + LangGraph + Chroma")
    st.info("면접 답변을 점수/강점/개선점으로 구조화 평가합니다.\n\n형식: `질문 | 답변`")

st.title("📊 면접 답변 평가")
st.caption("10주차 관통예제 — LangChain LCEL + LangGraph + Chroma RAG")

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

            response = httpx.post(
                f"{BACKEND_URL}/chat/structured",
                json={"question": question, "answer": answer},
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()

            col1, col2 = st.columns([1, 3])
            with col1:
                score = data.get("score", 0)
                score_emoji = ["", "😟", "🤔", "😐", "😊", "🌟"][score]
                st.metric("점수", f"{score}/5 {score_emoji}")
            with col2:
                st.markdown(f"**💪 강점:** {data.get('strengths', '-')}")
                st.markdown(f"**📝 개선점:** {data.get('improvements', '-')}")
                st.markdown(f"**❓ 후속 질문:** {data.get('next_question', '-')}")

            st.session_state[HISTORY_KEY].append({
                "role": "assistant",
                "content": (
                    f"**점수:** {data.get('score', 0)}/5\n\n"
                    f"**강점:** {data.get('strengths', '-')}\n\n"
                    f"**개선점:** {data.get('improvements', '-')}\n\n"
                    f"**후속 질문:** {data.get('next_question', '-')}"
                ),
                "metadata": data,
            })

        except Exception as e:
            handle_backend_error(e)
