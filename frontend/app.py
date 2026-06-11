import streamlit as st
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

st.set_page_config(
    page_title="AI 면접 코치",
    page_icon="🎤",
    layout="wide",
)

def build_pages():
    """면접 코치 앱의 세 페이지를 등록하고 실행합니다."""

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

    settings_page = st.Page(
        "pages/settings.py",
        title="설정",
        icon="⚙️",
    )

    pg = st.navigation([
        interview_page,
        resume_page,
        settings_page,
    ])

    pg.run()


build_pages()