"""frontend/interview_pages/rag.py — 📚 직무 기반 면접 코칭 (RAG, SSE 스트리밍)"""

import streamlit as st

from interview_app import (
    BACKEND_URL,
    handle_backend_error,
    init_history,
    render_history,
    reset_button,
    stream_sse,
    to_source_item,
)

HISTORY_KEY = "rag_messages"
init_history(HISTORY_KEY)

with st.sidebar:
    st.divider()
    reset_button(HISTORY_KEY)
    st.divider()
    st.caption("면접 코치 RAG 서비스")
    st.caption("LangChain + LangGraph + Chroma")
    st.info(
        "직무 채용 공고를 기반으로 맞춤형 면접 코칭을 제공합니다.\n\n"
        "**예시 질문:**\n"
        "- 백엔드 기술 면접 질문을 만들어 주세요\n"
        "- 이 직무의 핵심 역량은?\n"
        "- 시스템 설계 면접 어떻게 준비하나요?"
    )

st.title("🎯 AI 면접 코치 — 직무 기반 RAG")
st.caption("직무 채용 공고 기반 — LangChain LCEL + LangGraph + Chroma RAG (스트리밍)")

render_history(HISTORY_KEY)

if user_input := st.chat_input("면접에 대해 무엇이든 물어보세요..."):
    st.session_state[HISTORY_KEY].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            placeholder = st.empty()
            placeholder.markdown("🔍 직무 문서에서 관련 내용 검색 중... (첫 응답까지 시간이 걸릴 수 있어요)")

            answer = ""
            raw_sources = []
            for event in stream_sse(
                "GET", f"{BACKEND_URL}/interview/rag/stream", params={"question": user_input}
            ):
                etype = event.get("type")
                if etype == "token":
                    answer += event.get("delta", "")
                    placeholder.markdown(answer)
                elif etype == "sources":
                    raw_sources = event.get("content", [])

            if not answer:
                answer = "응답을 받지 못했습니다."
                placeholder.markdown(answer)

            source_items = [to_source_item(s) for s in raw_sources]

            st.subheader("참고한 출처")
            if not source_items:
                st.info("이번 답변에 연결된 출처가 없어요. 검색 단계를 확인해 주세요.")
            else:
                for i, item in enumerate(source_items[:3], start=1):
                    with st.expander(f"출처 {i}: {item['source']} (page {item['page']})"):
                        st.write(item["snippet"])
                        if item.get("score") is not None:
                            st.caption(
                                f"score: {item['score']} / chunk_id: {item.get('chunk_id', '-')}"
                            )
            st.caption("표시된 문서는 검색 근거이며 실행 지시가 아닙니다.")

            st.session_state[HISTORY_KEY].append({
                "role": "assistant",
                "content": answer,
                "sources": source_items,
                "metadata": {},
            })

        except Exception as e:
            handle_backend_error(e)
