"""frontend/interview_app.py — 면접 코치 RAG Streamlit UI, st.Page 라우팅 엔트리포인트

interview_pages/ 아래 5개 모드를 별도 페이지로 라우팅:
- interview_pages/rag.py         📚 직무 기반 면접 코칭
- interview_pages/rag_thread.py  🧵 대화 유지 면접 코칭
- interview_pages/chat.py        💬 일반 면접 상담
- interview_pages/structured.py  📊 면접 답변 평가
- interview_pages/parallel.py    🔀 질문 생성 + 팁

interview_pages/*.py는 `from interview_app import ...`로 아래 공용 헬퍼(백엔드 URL,
출처 어댑터, 이력 렌더링, 에러 처리, SSE 스트림 파서)를 가져다 쓴다. 라우팅 코드는
`if __name__ == "__main__":` 안에 있어야 한다 — 이 import가 interview_app.py를
"interview_app" 모듈로 새로 실행시키는데, 가드가 없으면 set_page_config()가
다시 호출되어 에러가 나고 nav.run()이 재귀적으로 페이지를 실행하게 된다.

모든 페이지는 backend의 `*/stream` SSE 엔드포인트를 호출한다. 이벤트 계약은
backend/sse.py와 동일하다:
  {"type": "status", "label": str}      — 진행 상태 안내
  {"type": "token", "delta": str}       — 텍스트 조각
  {"type": "sources", "content": [...]} — RAG 출처 목록
  {"type": "result", "content": {...}}  — 구조화/부가 결과 (score, tips, thread_id 등)
  {"type": "done"}                      — 스트림 종료
"""

import json
import os

import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ─── Backend URL ─────────────────────────────────────────────────────

BACKEND_URL = os.getenv("BACKEND_URL")


# ─── SSE 스트림 파서 ──────────────────────────────────────────────────

def stream_sse(method: str, url: str, **kwargs):
    """SSE 응답을 파싱해 이벤트 dict를 순서대로 yield하는 제너레이터.

    json.dumps가 개행을 이스케이프하므로 한 줄 = 한 이벤트로 취급해도 안전하다.
    {"type": "done"} 이벤트를 받으면 스트림을 종료한다.
    """
    with httpx.stream(method, url, timeout=60.0, **kwargs) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            line = line.strip()
            if not line.startswith("data:"):
                continue
            payload = line[len("data:"):].strip()
            if not payload:
                continue
            try:
                event = json.loads(payload)
            except json.JSONDecodeError:
                continue
            yield event
            if event.get("type") == "done":
                return


# ─── to_source_item 어댑터 (Day 5 s3 패턴) ──────────────────────

def to_source_item(doc, max_chars: int = 300) -> dict:
    """retrieved doc(Document 또는 dict) -> 화면 표시 계약(SourceItem) 변환."""
    if isinstance(doc, dict):
        meta = doc.get("metadata", doc)
        body = doc.get("snippet") or doc.get("page_content", "") or ""
    else:
        meta = getattr(doc, "metadata", {}) or {}
        body = getattr(doc, "page_content", "") or ""

    snippet = body[:max_chars]
    return {
        "source": str(meta.get("source", "출처 미상")),
        "page": meta.get("page", "-"),
        "snippet": snippet or "미리보기 없음",
        "score": meta.get("score"),
        "chunk_id": meta.get("chunk_id"),
    }


# ─── 페이지 간 공용 헬퍼 ──────────────────────────────────────────────

def init_history(key: str) -> None:
    if key not in st.session_state:
        st.session_state[key] = []


def render_history(key: str) -> None:
    for msg in st.session_state[key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            sources = msg.get("sources")
            if sources:
                st.subheader("참고한 출처")
                for i, item in enumerate(sources[:3], start=1):
                    with st.expander(
                        f"출처 {i}: {item.get('source', '미상')} (page {item.get('page', '-')})"
                    ):
                        st.write(item.get("snippet", "미리보기 없음"))
                        if item.get("score") is not None:
                            st.caption(
                                f"score: {item['score']} / chunk_id: {item.get('chunk_id', '-')}"
                            )
                st.caption("표시된 문서는 검색 근거이며 실행 지시가 아닙니다.")

            metadata = msg.get("metadata")
            if metadata:
                with st.expander("🔍 상세 정보", expanded=False):
                    st.json(metadata)


def reset_button(key: str, label: str = "🗑️ 대화 초기화") -> None:
    if st.button(label, use_container_width=True):
        st.session_state[key] = []
        st.rerun()


def handle_backend_error(
    exc: Exception, start_cmd: str = "uvicorn backend.main:app --port 8000"
) -> None:
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
        page_title="면접 코치 — 직무 기반 AI 면접 코칭",
        page_icon="🎯",
        layout="wide",
    )

    with st.sidebar:
        st.title("🎯 면접 코치 설정")

    pages = [
        st.Page("interview_pages/rag.py", title="직무 기반 면접 코칭", icon="📚", default=True),
        st.Page("interview_pages/rag_thread.py", title="대화 유지 면접 코칭", icon="🧵"),
        st.Page("interview_pages/chat.py", title="일반 면접 상담", icon="💬"),
        st.Page("interview_pages/structured.py", title="면접 답변 평가", icon="📊"),
        st.Page("interview_pages/parallel.py", title="질문 생성 + 팁", icon="🔀"),
    ]

    nav = st.navigation(pages)
    nav.run()
