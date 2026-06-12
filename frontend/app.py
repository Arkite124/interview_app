import sys
from pathlib import Path

import streamlit as st

from api_client import BACKEND_URL

# 현재 파일 기준으로 frontend 루트 경로 잡기
ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

from pages.utils import check_backend_health,show_api_error
from pages.history import ensure_session_state
import os

st.set_page_config(
    page_title="AI 면접 코치",
    page_icon="🎤",
    layout="wide",
)


def render_sidebar_status() -> None:
    """앱 공통 사이드바 상태 표시"""
    with st.sidebar:
        st.subheader("앱 상태")

        if check_backend_health(BACKEND_URL):
            st.success("FastAPI 연결 정상")
        else:
            st.write(f"오류 발생")
            st.caption("uvicorn 실행 여부와 8000번 포트를 확인하세요.")

        st.divider()

        conversations = st.session_state.get("conversations", {})
        current_id = st.session_state.get("current_session_id")

        st.caption(f"저장된 면접 세션 수: {len(conversations)}개")

        if current_id:
            st.caption(f"현재 세션 ID: {current_id[:8]}...")


def build_pages() -> None:
    """면접 코치 앱의 페이지를 등록하고 실행합니다."""

    interview_page = st.Page(
        "pages/interview.py",
        title="면접 연습",
        icon="🎤",
    )

    resume_page = st.Page(
        "pages/resume.py",
        title="이력서 질문 생성",
        icon="📄",
    )

    history_page = st.Page(
        "pages/history.py",
        title="대화 기록 / 리포트",
        icon="📝",
    )

    settings_page = st.Page(
        "pages/settings.py",
        title="설정",
        icon="⚙️",
    )
    pg = st.navigation(
        [
            interview_page,
            resume_page,
            history_page,
            settings_page,
        ]
    )

    pg.run()


def main() -> None:
    """앱 시작점"""
    ensure_session_state()
    render_sidebar_status()
    build_pages()


main()