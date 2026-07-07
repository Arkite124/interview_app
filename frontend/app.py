"""frontend/app.py — Streamlit 라우팅 엔트리포인트 + 공용 헬퍼 (Day 5 S3-S4)

st.Page + st.navigation으로 pages/ 아래 각 모드를 별도 페이지로 라우팅:
- pages/rag.py         📚 RAG 사내 문서 QA
- pages/chat.py        💬 기본 면접 코치
- pages/structured.py  📊 면접 답변 평가
- pages/parallel.py    🔀 병렬 + 분기 응답

pages/*.py는 `from app import ...`로 아래 공용 헬퍼(백엔드 URL, 이력
렌더링, 에러 처리)를 가져다 쓴다. 라우팅 코드는 `if __name__ == "__main__":`
안에 있어야 한다 — 이 import가 app.py를 "app" 모듈로 새로 실행시키는데,
가드가 없으면 set_page_config()가 다시 호출되어 에러가 나고 nav.run()이
재귀적으로 페이지를 실행하게 된다.
"""

import httpx
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")


def init_history(key: str) -> None:
    if key not in st.session_state:
        st.session_state[key] = []


def render_history(key: str) -> None:
    for msg in st.session_state[key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(f"📎 출처 ({len(msg['sources'])}건)", expanded=False):
                    for src in msg["sources"]:
                        st.markdown(
                            f"**{src.get('source', 'unknown')}** "
                            f"(p.{src.get('page', 0)})\n\n"
                            f"> {src.get('snippet', '')}"
                        )
                        st.divider()
            if msg.get("metadata"):
                with st.expander("🔍 상세 정보", expanded=False):
                    st.json(msg["metadata"])


def reset_button(key: str, label: str = "🗑️ 대화 초기화") -> None:
    if st.button(label, use_container_width=True):
        st.session_state[key] = []
        st.rerun()


def handle_backend_error(exc: Exception, start_cmd: str = "uvicorn backend.app:app --port 8000") -> None:
    if isinstance(exc, httpx.ConnectError):
        st.error(
            "⚠️ Backend 서버에 연결할 수 없습니다.\n\n"
            f"`{start_cmd}` 으로 서버를 먼저 시작해주세요."
        )
    elif isinstance(exc, httpx.HTTPStatusError):
        st.error(f"⚠️ API 오류: {exc.response.status_code}\n\n{exc.response.text}")
    else:
        st.error(f"⚠️ 오류 발생: {exc}")


if __name__ == "__main__":
    st.set_page_config(
        page_title="10주차 관통예제 — AI 사내 문서 QA",
        page_icon="🤖",
        layout="wide",
    )

    with st.sidebar:
        st.title("⚙️ 설정")

    pages = [
        st.Page("pages/rag.py", title="RAG 사내 문서 QA", icon="📚", default=True),
        st.Page("pages/chat.py", title="기본 면접 코치", icon="💬"),
        st.Page("pages/structured.py", title="면접 답변 평가", icon="📊"),
        st.Page("pages/parallel.py", title="병렬 + 분기 응답", icon="🔀"),
    ]

    nav = st.navigation(pages)
    nav.run()
