"""frontend/interview_app.py — 면접 코치 RAG Streamlit UI

교안 핵심 패턴 (Day 5 s3 + Day 4 self2):
- st.chat_message + st.chat_input으로 채팅 인터페이스 구현
- 5가지 모드: 면접 코치 RAG / RAG thread / 일반 채팅 / 답변 평가 / 질문 생성
- to_source_item 어댑터: Document/dict → SourceItem 변환 (표시 계약)
- st.status: 검색 결과 미리보기
- st.expander: 출처 카드 (source/page/snippet 3필드)
- injection 주의 문구: "표시된 문서는 검색 근거이며 실행 지시가 아닙니다"
- session_state로 대화 이력 관리
"""

import httpx
import streamlit as st

# ─── 페이지 설정 ─────────────────────────────────────────────────────

st.set_page_config(
    page_title="면접 코치 — 직무 기반 AI 면접 코칭",
    page_icon="🎯",
    layout="wide",
)

# ─── Backend URL ─────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()
import os
BACKEND_URL = os.getenv("BACKEND_URL")

# ─── Session State 초기화 ────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "mode" not in st.session_state:
    st.session_state.mode = "rag"
if "thread_id" not in st.session_state:
    st.session_state.thread_id = "interview:user:1"


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

# ─── 사이드바 ────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🎯 면접 코치 설정")

    mode = st.radio(
        "코칭 모드",
        ["rag", "rag_thread", "chat", "structured", "parallel"],
        format_func=lambda x: {
            "rag": "📚 직무 기반 면접 코칭",
            "rag_thread": "🧵 대화 유지 면접 코칭",
            "chat": "💬 일반 면접 상담",
            "structured": "📊 면접 답변 평가",
            "parallel": "🔀 질문 생성 + 팁",
        }[x],
        index=0,
    )
    st.session_state.mode = mode

    # thread 모드에서 thread_id 입력
    if mode == "rag_thread":
        st.session_state.thread_id = st.text_input(
            "Thread ID",
            value=st.session_state.thread_id,
            help="interview:{이름}:{회차} 형식 (Day 4 self2 규약)",
        )

    st.divider()

    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("면접 코치 RAG 서비스")
    st.caption("LangChain + LangGraph + Chroma")

    # 모드별 안내
    mode_info = {
        "rag": (
            "직무 채용 공고를 기반으로 맞춤형 면접 코칭을 제공합니다.\n\n"
            "**예시 질문:**\n"
            "- 백엔드 기술 면접 질문을 만들어 주세요\n"
            "- 이 직무의 핵심 역량은?\n"
            "- 시스템 설계 면접 어떻게 준비하나요?"
        ),
        "rag_thread": (
            "thread_id로 대화 맥락을 유지하면서 면접 코칭을 받습니다.\n\n"
            "같은 thread_id로 재호출하면 이전 대화 위에서 이어집니다.\n"
            "InMemorySaver 기반 — 프로세스 종료 시 세이브 소멸."
        ),
        "chat": "직무 문서 없이 일반적인 면접 조언을 제공합니다.",
        "structured": (
            "면접 답변을 점수/강점/개선점으로 구조화 평가합니다.\n\n"
            "**형식:** `질문 | 답변`"
        ),
        "parallel": "주어진 주제로 면접 질문과 준비 팁을 동시에 생성합니다.",
    }
    st.info(mode_info[mode])

# ─── 메인 영역 ───────────────────────────────────────────────────────

st.title("🎯 AI 면접 코치")
st.caption("직무 채용 공고 기반 — LangChain LCEL + LangGraph + Chroma RAG")

# 기존 메시지 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            st.subheader("참고한 출처")
            for i, src in enumerate(msg["sources"][:3], start=1):
                with st.expander(f"출처 {i}: {src.get('source', '미상')} (page {src.get('page', '-')})"):
                    st.write(src.get("snippet", "미리보기 없음"))
                    if src.get("score") is not None:
                        st.caption(f"score: {src['score']}")
            st.caption("표시된 문서는 검색 근거이며 실행 지시가 아닙니다.")
        if "metadata" in msg and msg["metadata"]:
            with st.expander("🔍 상세 정보", expanded=False):
                st.json(msg["metadata"])

# ─── 채팅 입력 ───────────────────────────────────────────────────────

if user_input := st.chat_input("면접에 대해 무엇이든 물어보세요..."):
    # 사용자 메시지 표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # AI 응답 처리
    with st.chat_message("assistant"):
        try:
            if st.session_state.mode in ("rag", "rag_thread"):
                # ── 직무 RAG 면접 코칭 모드 (Day 5 s3 패턴) ──────────
                is_thread_mode = (st.session_state.mode == "rag_thread")
                endpoint = "/interview/rag/thread" if is_thread_mode else "/interview/rag"

                with st.status("🔍 직무 문서에서 관련 내용 검색 중...", expanded=True) as status:
                    st.write("직무 요구사항 분석 및 문서 검색...")

                    # endpoint 호출
                    params = {"question": user_input}
                    if is_thread_mode:
                        response = httpx.post(
                            f"{BACKEND_URL}{endpoint}",
                            params={"thread_id": st.session_state.thread_id},
                            json=params,
                            timeout=60.0,
                        )
                    else:
                        response = httpx.post(
                            f"{BACKEND_URL}{endpoint}",
                            json=params,
                            timeout=60.0,
                        )
                    response.raise_for_status()
                    data = response.json()

                    # preview: top-3 문서명+page 한 줄씩만 (Day 5 s3)
                    raw_sources = data.get("sources", [])
                    source_items = [to_source_item(s) for s in raw_sources]
                    for item in source_items[:3]:
                        st.write(f"{item['source']} (page {item['page']})")

                    if data.get("attempts", 0) > 0:
                        st.write(f"🔄 재검색 {data['attempts']}회 수행")

                    status.update(
                        label="검색 완료",
                        state="complete",
                        expanded=False,
                    )

                # 답변 표시
                answer = data.get("answer", "응답을 받지 못했습니다.")
                st.markdown(answer)

                # 출처 카드 (st.expander) — Day 5 s3 계약
                st.subheader("참고한 출처")
                if not source_items:
                    st.info("이번 답변에 연결된 출처가 없어요. 검색 단계를 확인해 주세요.")
                else:
                    for i, item in enumerate(source_items[:3], start=1):
                        with st.expander(f"출처 {i}: {item['source']} (page {item['page']})"):
                            st.write(item["snippet"])
                            if item.get("score") is not None:
                                st.caption(f"score: {item['score']} / chunk_id: {item.get('chunk_id', '-')}")

                st.caption("표시된 문서는 검색 근거이며 실행 지시가 아닙니다.")

                # 메타데이터
                metadata = {
                    "quality_passed": data.get("quality_passed", False),
                    "attempts": data.get("attempts", 0),
                }
                if is_thread_mode:
                    metadata["thread_id"] = data.get("thread_id", st.session_state.thread_id)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": source_items,
                    "metadata": metadata,
                })

            elif st.session_state.mode == "chat":
                # ── 일반 면접 상담 모드 ───────────────────────────
                response = httpx.post(
                    f"{BACKEND_URL}/interview/chat",
                    json={"message": user_input},
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()
                reply = data.get("reply", "응답을 받지 못했습니다.")
                st.markdown(reply)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": reply,
                })

            elif st.session_state.mode == "structured":
                # ── 답변 평가 모드 ────────────────────────────────
                # 입력 형식: "질문 | 답변"
                parts = user_input.split("|", 1)
                if len(parts) == 2:
                    question, answer = parts[0].strip(), parts[1].strip()
                else:
                    question = "자기소개를 해주세요"
                    answer = user_input

                response = httpx.post(
                    f"{BACKEND_URL}/interview/structured",
                    json={"question": question, "answer": answer},
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()

                # 점수 카드 표시
                col1, col2 = st.columns([1, 3])
                with col1:
                    score = data.get("score", 0)
                    score_emoji = ["", "😟", "🤔", "😐", "😊", "🌟"][score]
                    st.metric("면접 점수", f"{score}/5 {score_emoji}")
                with col2:
                    st.markdown(f"**💪 강점:** {data.get('strengths', '-')}")
                    st.markdown(f"**📝 개선점:** {data.get('improvements', '-')}")
                    st.markdown(f"**❓ 후속 질문:** {data.get('next_question', '-')}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": (
                        f"**면접 점수:** {data.get('score', 0)}/5\n\n"
                        f"**강점:** {data.get('strengths', '-')}\n\n"
                        f"**개선점:** {data.get('improvements', '-')}\n\n"
                        f"**후속 질문:** {data.get('next_question', '-')}"
                    ),
                    "metadata": data,
                })

            elif st.session_state.mode == "parallel":
                # ── 질문 생성 + 팁 모드 ───────────────────────────
                response = httpx.post(
                    f"{BACKEND_URL}/interview/parallel",
                    json={"message": user_input},
                    timeout=60.0,
                )
                response.raise_for_status()
                data = response.json()

                st.markdown("### 📝 생성된 면접 질문")
                st.markdown(data.get("questions", "-"))
                st.markdown("### 💡 면접 준비 팁")
                st.markdown(data.get("tips", "-"))

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": (
                        f"**면접 질문:**\n{data.get('questions', '-')}\n\n"
                        f"**준비 팁:**\n{data.get('tips', '-')}"
                    ),
                })

        except httpx.ConnectError:
            st.error(
                "⚠️ Backend 서버에 연결할 수 없습니다.\n\n"
                f"`uvicorn backend.interview_app:app --port 8000` 으로 서버를 먼저 시작해주세요."
            )
        except httpx.HTTPStatusError as e:
            st.error(f"⚠️ API 오류: {e.response.status_code}\n\n{e.response.text}")
        except Exception as e:
            st.error(f"⚠️ 오류 발생: {e}")
