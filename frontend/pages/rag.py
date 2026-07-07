"""frontend/pages/rag.py — 📚 RAG 사내 문서 QA

- st.status: 검색 미리보기 (진행 상태 표시)
- st.expander: 출처 카드 (source/page/snippet 3필드)
"""

import httpx
import streamlit as st

from app import BACKEND_URL, handle_backend_error, init_history, render_history, reset_button

HISTORY_KEY = "rag_messages"
init_history(HISTORY_KEY)

with st.sidebar:
    st.divider()
    reset_button(HISTORY_KEY)
    st.divider()
    st.caption("10주차 관통예제")
    st.caption("LangChain + LangGraph + Chroma")
    st.info(
        "사내 규정 문서를 기반으로 질문에 답합니다.\n\n"
        "예시 질문:\n- 휴가 신청 절차는?\n- 출장비 한도는?\n- 재택근무 규정은?"
    )

st.title("🤖 AI 사내 문서 QA 챗봇")
st.caption("10주차 관통예제 — LangChain LCEL + LangGraph + Chroma RAG")

render_history(HISTORY_KEY)

if user_input := st.chat_input("질문을 입력하세요..."):
    st.session_state[HISTORY_KEY].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            with st.status("🔍 사내 문서 검색 중...", expanded=True) as status:
                st.write("질문 분석 및 문서 검색...")

                response = httpx.post(
                    f"{BACKEND_URL}/rag",
                    json={"message": user_input},
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()

                st.write(f"✅ 검색 완료 (근거 {len(data.get('sources', []))}건)")

                if data.get("attempts", 0) > 0:
                    st.write(f"🔄 재검색 {data['attempts']}회 수행")

                status.update(label="검색 완료", state="complete", expanded=False)

            answer = data.get("answer", "응답을 받지 못했습니다.")
            st.markdown(answer)

            sources = data.get("sources", [])
            if sources:
                with st.expander(f"📎 출처 ({len(sources)}건)", expanded=True):
                    for src in sources:
                        st.markdown(
                            f"**{src.get('source', 'unknown')}** "
                            f"(p.{src.get('page', 0)})\n\n"
                            f"> {src.get('snippet', '')}"
                        )
                        st.divider()

            metadata = {
                "quality_passed": data.get("quality_passed", False),
                "attempts": data.get("attempts", 0),
            }

            st.session_state[HISTORY_KEY].append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "metadata": metadata,
            })

        except Exception as e:
            handle_backend_error(e)
