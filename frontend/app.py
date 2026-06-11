import streamlit as st
import sys
from pathlib import Path
import time

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))
from core.roles import ROLES
st.set_page_config(
    page_title="AI 면접 코치",
    page_icon="🎤",
    layout="wide",
)

st.title("면접 코치")
st.write("면접과 함께 합니다.")

def initialize_messages()->None:
    """면접 대화 기록이 없으면 초기 안내 메시지를 준비합니다."""
    if "messages" not in st.session_state:
        st.session_state.messages=[{"role": "assistant", "content": "안녕하세요. AI 면접관 입니다."}]
    st.write("유지 확인 : ",st.session_state.messages)
initialize_messages()
st.write(list(ROLES.keys()))

def get_interviewer_options() -> dict[str, str]:
    """면접관 유형의 키와 화면 표시 이름을 반환합니다."""
    preset={}
    # "tech"
    # "personality"
    # "executive"
    # "structured"
    for ROLE in ROLES:
        if ROLE == "tech":
            preset.update({"tech": "기술 면접관"})
        if ROLE == "personality":
            preset.update({"personality":"인성 면접관"})
        if ROLE == "executive":
            preset.update({"executive":"임원 면접관"})
        if ROLE == "structured":
            preset.update({"structured":"구조화 면접관"})
    return preset

def get_system_prompt(role_key: str) -> str:
    """선택한 면접관 유형의 시스템 프롬프트를 반환합니다."""
    # 여기에 role_key로 roles.py에서 system_prompt를 찾아 반환하는 코드를 채워요.
    sys_prompt = ROLES[role_key]
    prompt=sys_prompt.system_prompt
    return prompt

def handle_user_input(user_text: str) -> None:
    """사용자 입력을 받아 메시지 목록에 저장합니다."""
    # 여기에 user 메시지 append 코드를 채워요.
    # role="user", content=user_text
    user_message = {"role": "user", "content": user_text}
    st.session_state.messages.append(user_message)
    # 여기에 임시 assistant 응답 append 코드를 채워요.
    # (실제 API 호출 전, 임시 응답 문자열로 대체합니다)
    assistant_reply = "면접 답변을 확인했습니다. (임시 응답)"
    assistant_message = {"role": "assistant", "content": assistant_reply}
    st.session_state.messages.append(assistant_message)
    # 여기에 두 메시지를 st.session_state.messages에 추가하는 코드를 채워요.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
    # 여기에 메시지 내용을 출력하는 코드를 채워요.
        st.write(message["content"]) 
with st.expander("면접코치 설정 확인"):
    st.write(ROLES.keys())
    st.write(len(st.session_state.messages))
with st.sidebar:
    st.divider()
    st.subheader("Day2 입력 준비 상태")
    st.header("면접관 설정")
    interview_record = {
        "role": st.session_state.get("selected_role", "미선택"),
        "message_count": len(st.session_state.get("messages", [])),
        "ready_for_day2": len(st.session_state.get("messages", [])) >= 2,
    }
    st.json(interview_record)

    if "selected_role" not in st.session_state:
        st.session_state.selected_role = "tech"
    selected_value =st.selectbox("면접관 설정", list(get_interviewer_options().keys()))
    st.session_state.selected_role = selected_value
    # 여기에 면접관 유형 선택 위젯을 채워요.
    # 1. st.session_state.selected_role 초기화 (없으면 기본값 "tech")
    # 2. st.selectbox로 면접관 유형 목록을 표시
    # 3. 선택값을 st.session_state.selected_role에 저장

def generate_coach_reply(user_text: str, role_key: str) -> str:
    """선택한 면접관 유형에 맞는 임시 코치 응답을 만듭니다."""
    # 여기에 role_key로 시스템 프롬프트를 가져오는 코드를 채워요.
    system_prompt = f"{user_text},{get_system_prompt(role_key)}"
    # 여기에 시스템 프롬프트와 사용자 입력을 조합한 임시 응답 문자열을 채워요.
    # 예: f"[{면접관 유형 이름}] 다음 관점으로 피드백합니다: {system_prompt 첫 30자}..."
    return f"{ROLES[st.session_state.selected_role]} 다음 관점으로 피드백 합니다. {system_prompt[:30]}"

# 채팅 입력 위젯 — 화면 하단에 고정됩니다.
user_input = st.chat_input("면접 답변을 입력해 주세요.")

def fake_stream_generator(reply_text: str):
    """실제 API 없이 st.write_stream 동작을 확인하는 임시 generator입니다."""
    words = reply_text.split()
    for word in words:
        time.sleep(0.08)
        yield word + " "
    # 새 입력이 들어왔을 때 stream 출력

if user_input:
    # user 메시지 저장
    st.session_state.messages.append({"role": "user", "content": user_input})
    # 임시 코치 응답 생성
    reply_text = generate_coach_reply(
        user_input, st.session_state.selected_role
    )

    # st.write_stream으로 순차 출력
    with st.chat_message("assistant"):
        # 여기에 st.write_stream 호출 코드를 채워요.
        # 반환값을 response_text 변수로 받는 것을 잊지 마세요!
        response_text = st.write_stream(fake_stream_generator(reply_text))
    st.session_state.messages.append({"role": "assistant", "content": response_text})

    # 여기에 response_text를 st.session_state.messages에 append하는 코드를 채워요.
    st.rerun()

def build_pages():
    """면접 코치 앱의 세 페이지를 등록하고 실행합니다."""
    # TODO: st.Page로 frontend/pages/interview.py를 등록해요.
    interview_page = st.Page("pages/interview.py")

    # TODO: st.Page로 frontend/pages/resume.py를 등록해요.
    resume_page = st.Page("pages/resume.py")

    # TODO: st.Page로 frontend/pages/settings.py를 등록해요.
    settings_page = st.Page("pages/settings.py")

    # TODO: st.navigation에 세 페이지를 그룹으로 묶어요.
    pg = st.navigation([interview_page,resume_page,settings_page])

    # TODO: 선택된 페이지를 실행해요.
    pg.run()
    
build_pages()

# TODO: 아래 주석 블록을 app.py 하단에 붙여요.
# day1-self2에서 구현할 항목입니다.

# ============================
# day1-self2 TODO
# ============================
# TODO 1: 면접관 유형 사이드바 위젯 추가 (압박/편안/기술/인성 선택)
# TODO 2: 선택한 면접관 유형을 st.session_state에 저장하기
# TODO 3: st.write_stream 출력 흐름 연결 (임시 generator 사용)
# TODO 4: 면접 기록 (면접관 유형 + 질문 + 답변 + 코치 응답) 구조 설계
# ============================