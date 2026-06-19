# interview_app/frontend/pages/resume.py
# 책임 메모:
# - Day 4 self2에서 이력서 업로드와 맞춤 질문 생성을 확장할 자리입니다.
# - 오늘은 입력 영역과 TODO 위치만 표시합니다.
# - 면접 채팅 로직을 이 파일 안에 복사하지 않습니다.
# - LLM 호출 없이 규칙 기반 백엔드 API를 호출해 질문을 생성합니다.

from __future__ import annotations

import httpx
import streamlit as st
from frontend_legacy.api_client import get_backend_url

def read_resume_text(uploaded_file) -> str:
    """업로드된 txt 파일을 utf-8 문자열로 읽습니다."""
    if uploaded_file is None:
        return ""

    if uploaded_file.type != "text/plain":
        return ""

    try:
        return uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError:
        st.error("파일을 utf-8로 읽을 수 없습니다. utf-8로 저장된 .txt 파일을 업로드해 주세요.")
        return ""


def build_resume_question_request(resume_text: str, question_count: int) -> dict:
    """이력서 기반 면접 질문 생성 요청 값을 만듭니다."""
    settings = st.session_state.get("setting", {})

    return {
        "input": resume_text,
        "question_count": question_count,
        "role_preset": settings.get("role_preset", "기술 면접"),
    }


def request_resume_questions(request: dict) -> dict:
    """백엔드에 이력서 기반 질문 생성을 요청합니다."""
    url = f"{get_backend_url()}/files/analyze"

    response = httpx.post(
        url,
        json=request,
        timeout=30.0,
    )

    response.raise_for_status()
    return response.json()


def render_function_call_result(result: dict) -> None:
    """질문 생성 결과와 도구 호출 확인 데이터를 분리해 표시합니다."""
    questions = result.get("questions", [])

    if questions:
        st.subheader("생성된 면접 질문")

        for idx, question in enumerate(questions, start=1):
            st.markdown(f"**{idx}. {question}**")
    else:
        st.warning("생성된 질문이 없습니다.")

    tool_calls = result.get("tool_calls", [])

    with st.expander("Function Calling 확인 데이터"):
        if tool_calls:
            st.json(tool_calls)
        else:
            st.info("도구 호출 데이터가 없습니다.")


def save_resume_question_state(file_name: str, questions: list[str]) -> None:
    """이력서 기반 질문 생성 결과를 세션 상태에 저장합니다."""
    st.session_state.resume_question = {
        "file_name": file_name,
        "questions": questions,
        "question_count": len(questions),
        "progress": 1.0 if questions else 0.0,
        "memo": "Day 4 self2 이력서 기반 질문 생성 완료",
    }


def render_resume_dashboard(result: dict) -> None:
    """이력서 기반 질문 생성 결과를 대시보드로 표시합니다."""
    questions = result.get("questions", [])
    tool_calls = result.get("tool_calls", [])

    st.subheader("질문 생성 대시보드")

    st.metric("생성 질문 수", len(questions))

    chart_data = {
        "개수": {
            "면접 질문": len(questions),
            "도구 호출": len(tool_calls),
        }
    }

    st.bar_chart(chart_data)

    progress_value = 1.0 if questions else 0.0
    st.progress(progress_value, text="Step 4-B 완료" if questions else "질문 생성 전")


# -----------------------------
# 화면 영역
# -----------------------------

st.title("이력서 분석")

settings = st.session_state.get("setting", {})
st.caption(f"현재 질문 역할: {settings.get('role_preset', '기술 면접')}")

uploaded_file = st.file_uploader(
    "자기소개서 파일을 업로드하세요",
    type=["txt"],
    
)

resume_text = read_resume_text(uploaded_file)

if resume_text:
    st.text_area(
        "자기소개서 내용",
        resume_text,
        height=300,
    )

    st.text_area(
        "미리보기",
        resume_text[:500],
        height=150,
    )
else:
    st.info("txt 파일을 업로드하면 내용이 표시됩니다.")
    st.caption("utf-8로 인코딩된 .txt 파일만 가능합니다.")

question_count = st.number_input(
    "생성할 질문 수",
    min_value=3,
    max_value=10,
    value=5,
    step=1,
)

if st.button("이력서 기반 질문 생성"):
    if not resume_text:
        st.warning("먼저 자기소개서 txt 파일을 업로드하세요.")
        st.stop()

    request = build_resume_question_request(
        resume_text=resume_text,
        question_count=question_count,
    )

    try:
        result = request_resume_questions(request)
    except httpx.HTTPStatusError as exc:
        st.error(f"백엔드 응답 오류: {exc.response.status_code}")
        st.code(exc.response.text)
        st.stop()
    except httpx.RequestError as exc:
        st.error(f"백엔드 연결 실패: {exc}")
        st.info("FastAPI 서버가 실행 중인지 확인해 주세요.")
        st.stop()

    questions = result.get("questions", [])

    file_name = uploaded_file.name if uploaded_file else "unknown.txt"

    save_resume_question_state(
        file_name=file_name,
        questions=questions,
    )

    render_function_call_result(result)

    render_resume_dashboard(result)


if "resume_question" in st.session_state:
    with st.expander("세션에 저장된 이력서 질문 상태"):
        st.json(st.session_state.resume_question)