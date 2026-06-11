# interview_app/frontend/pages/settings.py
# 책임 메모:
# - 앱 전체에서 공유할 모델, temperature, system_prompt, role_preset 값을 관리합니다.
# - API 키를 입력받지 않습니다.
# - 저장 버튼을 눌렀을 때만 st.session_state.settings를 갱신합니다.
import streamlit as st
from dotenv import load_dotenv
load_dotenv()
st.title("설정")
st.caption("면접 코치 앱 전체에서 공유할 설정을 관리합니다.")

DEFAULT_SETTINGS = {
    "model": "gpt-5.4-nano",
    "temperature": 0.7,
    "system_prompt": "당신은 전문 면접관입니다. 지원자의 역량을 파악하는 심층 질문을 해주세요.",
    "role_preset": "기술 면접",
}

setting=dict()
def ensure_settings() -> dict:
    """앱 전체에서 공유할 설정 dict를 준비합니다."""
    global setting
    if "setting" not in st.session_state:
        st.session_state.setting=DEFAULT_SETTINGS.copy()
    return st.session_state.setting
    # TODO: "settings" 키가 아직 없는 경우를 먼저 확인해요.
    # TODO: DEFAULT_SETTINGS.copy()로 기본값을 넣어요.
    # TODO: st.session_state.settings를 반환해요.

ROLE_PRESETS = {
    "기술 면접": "기술 역량을 중심으로 질문합니다.",
    "인성 면접": "협업과 태도를 중심으로 질문합니다.",
    "임원 면접": "비전과 조직 기여도를 중심으로 질문합니다.",
}

settings = ensure_settings()

# TODO: st.selectbox로 model을 선택하게 해요.
selected_model = st.selectbox("모델 선택",["gpt-4o-mini","gpt-5.4-nano"])

# TODO: st.slider로 temperature를 선택하게 해요.
selected_temperature = st.slider("답변 창의성", 0.0, 2.0, 0.7, 0.1,help="낮을수록 안정적이고, 높을수록 창의적이지만 예측하기 어려워집니다.")

# TODO: st.selectbox로 role_preset을 선택하게 해요.
selected_role = st.selectbox("역할 선택",list(ROLE_PRESETS.keys()))

# TODO: st.text_area로 system_prompt를 편집하게 해요.
selected_prompt = st.text_area("시스템 프롬프트 편집",height=150)

if st.button("설정 저장"):
    # TODO: 버튼을 눌렀을 때만 st.session_state.settings를 갱신해요.
    st.session_state.setting.update({
        "model": selected_model,
        "temperature": selected_temperature,
        "role_preset": selected_role,
        "system_prompt": selected_prompt,
    })
    st.success("설정을 저장했습니다.")


