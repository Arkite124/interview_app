from __future__ import annotations

from datetime import datetime
from typing import Any

import uuid
from typing import TypedDict
import pandas as pd
import streamlit as st


class InterviewMessage(TypedDict):
    """면접 대화 메시지 한 건입니다."""
    role: str
    content: str


class InterviewSession(TypedDict):
    """UUID 세션 하나에 연결되는 제목과 메시지 목록입니다."""
    title: str
    messages: list[InterviewMessage]


def get_selected_conversation() -> InterviewSession | None:
    """리포트로 내보낼 현재 면접 세션을 반환한다."""
    conversations = st.session_state.get("conversations", {})
    current_id = st.session_state.get("current_session_id")

    if not current_id or current_id not in conversations:
        return None

    return conversations[current_id]


def ensure_session_state() -> None:
    """면접 세션 저장소와 현재 세션 ID를 초기화한다."""
    if "conversations" not in st.session_state:
        first_id = str(uuid.uuid4())

        st.session_state.conversations = {
            first_id: {
                "title": "면접 세션 1",
                "messages": [],
            }
        }

        st.session_state.current_session_id = first_id

    if "current_session_id" not in st.session_state:
        conversations = st.session_state.conversations
        st.session_state.current_session_id = next(iter(conversations))


def add_new_session() -> None:
    """새 UUID 면접 세션을 추가하고 현재 세션으로 전환한다."""
    ensure_session_state()

    new_id = str(uuid.uuid4())
    session_count = len(st.session_state.conversations) + 1

    st.session_state.conversations[new_id] = {
        "title": f"면접 세션 {session_count}",
        "messages": [],
    }

    st.session_state.current_session_id = new_id


def delete_current_session() -> None:
    """현재 세션을 삭제하고 남은 세션으로 안전하게 이동한다."""
    ensure_session_state()

    conversations = st.session_state.conversations
    current_id = st.session_state.current_session_id

    if current_id not in conversations:
        st.session_state.current_session_id = next(iter(conversations))
        return

    # 마지막 세션이면 삭제하지 않고 메시지만 비움
    if len(conversations) == 1:
        conversations[current_id]["messages"] = []
        conversations[current_id]["title"] = "면접 세션 1"
        return

    del conversations[current_id]

    # 남아 있는 세션 중 첫 번째 세션으로 이동
    st.session_state.current_session_id = next(iter(conversations))

def render_final_dashboard(usage_summary: dict) -> None:
    """최종 제출 전 사용량과 진행 상태를 대시보드로 표시한다."""

    st.subheader("사용량 요약")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "총 요청 수",
            f"{usage_summary.get('request_count', 0)}회",
        )

    with col2:
        st.metric(
            "총 토큰",
            f"{usage_summary.get('total_tokens', 0):,}",
        )

    st.divider()

    st.subheader("토큰 사용 비율")

    prompt_tokens = usage_summary.get("prompt_tokens", 0)
    completion_tokens = usage_summary.get("completion_tokens", 0)

    token_data = pd.DataFrame(
        {
            "tokens": [
                prompt_tokens,
                completion_tokens,
            ]
        },
        index=[
            "입력(prompt)",
            "출력(completion)",
        ],
    )

    st.bar_chart(token_data)

    st.divider()

    st.subheader("일일 한도 소진율")

    ratio = float(usage_summary.get("daily_limit_ratio", 0.0))

    # st.progress는 0.0 ~ 1.0까지만 허용
    ratio = min(max(ratio, 0.0), 1.0)

    st.progress(ratio)
    st.caption(f"현재 일일 한도의 {ratio * 100:.1f}%를 사용했습니다.")

def build_interview_report(
    conversation: dict[str, Any],
    usage_summary: dict[str, Any],
    feedback_summary: dict[str, int] | None = None,
) -> str:
    """선택된 면접 세션을 마크다운 리포트 문자열로 만든다."""

    title = conversation.get("title", "면접 세션")
    messages = conversation.get("messages", [])

    lines: list[str] = []

    # 제목 / 생성 시각
    lines.append(f"# 면접 리포트 - {title}")
    lines.append("")
    lines.append(f"- 생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 총 메시지 수: {len(messages)}개")
    lines.append("")

    # 메시지 목록
    lines.append("## 1. 메시지 목록")
    lines.append("")
    lines.append("| 번호 | 역할 | 내용 |")
    lines.append("|---:|---|---|")

    for i, msg in enumerate(messages, start=1):
        role = msg.get("role", "")
        content = msg.get("content", "")

        # 마크다운 표 깨짐 방지
        safe_content = (
            content
            .replace("\n", " ")
            .replace("|", "\\|")
            .strip()
        )

        if len(safe_content) > 80:
            safe_content = safe_content[:80] + "..."

        lines.append(f"| {i} | {role} | {safe_content} |")

    lines.append("")

    # 피드백 요약
    lines.append("## 2. 피드백 요약")
    lines.append("")

    if feedback_summary:
        up_count = feedback_summary.get("up", 0)
        down_count = feedback_summary.get("down", 0)

        lines.append(f"- 좋아요: {up_count}개")
        lines.append(f"- 싫어요: {down_count}개")
    else:
        lines.append("- 수집된 피드백이 없습니다.")

    lines.append("")

    # 사용량 요약
    lines.append("## 3. 사용량 요약")
    lines.append("")
    lines.append(f"- 총 요청 수: {usage_summary.get('request_count', 0)}회")
    lines.append(f"- 총 토큰: {usage_summary.get('total_tokens', 0):,}")
    lines.append(f"- 입력 토큰: {usage_summary.get('prompt_tokens', 0):,}")
    lines.append(f"- 출력 토큰: {usage_summary.get('completion_tokens', 0):,}")

    daily_limit_ratio = float(usage_summary.get("daily_limit_ratio", 0.0))
    lines.append(f"- 일일 한도 소진율: {daily_limit_ratio * 100:.1f}%")
    lines.append("")

    # 9주차 완성 기능
    lines.append("## 4. 9주차 완성 기능")
    lines.append("")
    lines.append("- Streamlit 기반 면접 코치 화면 구성")
    lines.append("- FastAPI 백엔드 연동")
    lines.append("- SSE 스트리밍 응답 출력")
    lines.append("- 면접 세션 저장 및 전환")
    lines.append("- AI 응답 thumbs 피드백 저장")
    lines.append("- 사용량 대시보드 표시")
    lines.append("- 마크다운 리포트 다운로드")
    lines.append("")

    # 보안 안내
    lines.append("## 5. 제외된 민감 정보")
    lines.append("")
    lines.append("- API 키는 포함하지 않았습니다.")
    lines.append("- `.env` 값은 포함하지 않았습니다.")
    lines.append("- 시스템 프롬프트 원문은 포함하지 않았습니다.")

    return "\n".join(lines)

def render_report_download(
    session_id: str,
    conversation: dict[str, Any] | None,
    usage_summary: dict[str, Any],
) -> None:
    """리포트 생성 조건을 확인하고 다운로드 버튼을 표시한다."""

    if not conversation:
        st.info("리포트를 만들 세션을 먼저 선택하세요.")
        return

    messages = conversation.get("messages", [])

    if not messages:
        st.warning("선택한 세션에 메시지가 없습니다.")
        return

    report_md = build_interview_report(
        conversation=conversation,
        usage_summary=usage_summary,
    )

    st.download_button(
        label="리포트 다운로드",
        data=report_md,
        file_name=f"interview_{session_id}.md",
        mime="text/markdown",
    )
ensure_session_state()

st.title("대화 기록 / 리포트")

conversations = st.session_state.conversations
current_id = st.session_state.current_session_id

session_options = list(conversations.keys())

selected_id = st.selectbox(
    "면접 세션 선택",
    session_options,
    index=session_options.index(current_id),
    format_func=lambda session_id: conversations[session_id]["title"],
)

st.session_state.current_session_id = selected_id

col1, col2 = st.columns(2)

with col1:
    if st.button("새 세션 추가"):
        add_new_session()
        st.rerun()

with col2:
    if st.button("현재 세션 삭제"):
        delete_current_session()
        st.rerun()

conversation = get_selected_conversation()

if conversation:
    st.subheader(conversation["title"])

    messages = conversation.get("messages", [])

    if messages:
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    else:
        st.info("아직 저장된 메시지가 없습니다.")

    usage_summary = st.session_state.get(
        "usage_summary",
        {
            "request_count": len(messages),
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "daily_limit_ratio": 0.0,
        },
    )

    render_final_dashboard(usage_summary)

    render_report_download(
        session_id=selected_id,
        conversation=conversation,
        usage_summary=usage_summary,
    )