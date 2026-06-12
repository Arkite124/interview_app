# interview_app/frontend/pages/resume.py
# 책임 메모:
# - Day 4 self2에서 이력서 업로드와 맞춤 질문 생성을 확장할 자리입니다.
# - 오늘은 입력 영역과 TODO 위치만 표시합니다.
# - 면접 채팅 로직을 이 파일 안에 복사하지 않습니다.
import streamlit as st

def read_resume_text(uploaded_file):
    if uploaded_file is None:
        return ""
    file_text = ""
    if uploaded_file.type == "text/plain":
        file_text = uploaded_file.read().decode("utf-8")
    else:
        file_text = ""
    return file_text

st.title("이력서 분석")
settings = st.session_state.get("setting", {})
st.caption(f"현재 질문 역할: {settings.get('role_preset', '기술 면접')}")
# TODO: self2에서 st.file_uploader 입력을 추가해요.
uploaded_file = st.file_uploader(
    "자기소개서 파일을 업로드하세요",
    type=["txt"]
)

resume_text = read_resume_text(uploaded_file)

if resume_text:
    st.text_area("자기소개서 내용", resume_text, height=300)
else:
    st.info("txt 파일을 업로드하면 내용이 표시됩니다.")

# TODO: self2에서 이력서 기반 질문 생성 요청을 연결해요.
if resume_text:
    # TODO: st.text_area로 읽은 텍스트 일부를 미리 보여 주세요.
    st.text_area(resume_text[30:])
else:
    # TODO: 업로드 전 안내 문구를 표시해요.
    st.error("utf-8로 인코딩 된 .txt 파일만 가능합니다.")
def build_resume_question_request(resume_text: str, question_count: int) -> dict:
    """이력서 기반 면접 질문 생성 요청 값을 만듭니다."""
    settings = st.session_state.get("settings", {})

    return {
        # TODO: resume_text를 요청 입력으로 넣습니다.
        "input": resume_text,

        # TODO: st.session_state.settings에서 모델과 시스템 프롬프트 값을 읽을 위치를 표시합니다.
        "model": settings["model"],
        "temperature": settings["temperature"],
        "system_prompt": settings["system_prompt"],

        # TODO: 질문 개수와 역할 프리셋 값을 함께 담습니다.
        "question_count": question_count,
        "role_preset": settings["role_preset"],
    }

question_count = st.number_input(
    "생성할 질문 수",
    min_value=3,
    max_value=10,
    value=5,
    step=1,
)

def render_function_call_result(result: dict) -> None:
    """질문 생성 결과와 도구 호출 확인 데이터를 분리해 표시합니다."""

    # TODO: 학습자에게 보여줄 면접 질문 목록을 표시합니다.
    questions = result.get("questions", [])

    if questions:
        st.subheader("생성된 면접 질문")

        for idx, question in enumerate(questions, start=1):
            st.markdown(f"**{idx}. {question}**")
    else:
        st.warning("생성된 질문이 없습니다.")

    # TODO: st.expander 안에 st.json으로 Function Calling 확인 데이터를 표시합니다.
    tool_calls = result.get("tool_calls", [])

    with st.expander("Function Calling 확인 데이터"):
        if tool_calls:
            st.json(tool_calls)
        else:
            st.info("도구 호출 데이터가 없습니다.")

    # TODO: 원본 결과 전체를 무조건 펼쳐 보이지 않도록 합니다.
def save_resume_question_state(file_name: str, questions: list[str]) -> None:
    """이력서 기반 질문 생성 결과를 세션 상태에 저장합니다."""
    # TODO: st.session_state에 파일명과 질문 목록을 저장합니다.
    if "resume_question" not in st.session_state:
        st.session_state.resume_question=[]
    # TODO: 대시보드에서 쓸 질문 개수와 진행 상태 값을 저장합니다.
    total_count=len(questions)
    user_count=sum(1 for message in questions if message.get("role")=="user")
    assistant_count=sum(1 for message in questions if message.get("role")=="assistant")

    assistant_lengths=[
        len(str(message.get("content","")))
        for message in questions
        if message.get("role")=="assistant"
    ]
    if assistant_lengths:
        average_response_length=sum(assistant_lengths)/len(assistant_lengths)
    else:
        average_response_length=0.0
    
    if total_count:
        assistant_ratio=assistant_count/total_count
    else:
        assistant_ratio=0.0

    safe_progress=min(max(assistant_ratio,0.0),1.0)
    return {
        "total_count":total_count,
        "user_count":user_count,
        "assistant_count":assistant_count,
        "average_response_length":average_response_length,
        "assistant_ratio":assistant_ratio
    }
    
    # TODO: Day5 리포트 입력으로 넘길 확인 메모를 남깁니다.
    

if st.button("이력서 기반 질문 생성"):
    # TODO: request dict를 만들어요.
    request = build_resume_question_request(resume_text,question_count)

    # TODO: 백엔드 또는 임시 결과를 통해 result dict를 받아요.
    result =  {
    "questions": [
        "프로젝트에서 FastAPI를 사용한 이유를 설명해 주세요.",
        "SSE 응답이 끊겼을 때 어떤 순서로 확인하겠습니까?",
    ],
    "tool_calls": [
        {
            "name": "extract_resume_keywords",
            "arguments": {"section": "projects"},
            "result": {"keywords": ["FastAPI", "SSE", "Streamlit"]},
        }
    ],
}
    questions = result.get("questions", [])

    # TODO: save_resume_question_state(uploaded_file.name, questions)를 호출해요.
    save_resume_question_state(uploaded_file.name,questions)

    # TODO: render_function_call_result(result)를 호출해요.
    render_function_call_result(result)
def render_resume_dashboard() -> None:
    """이력서 기반 질문 생성 결과를 대시보드로 표시합니다."""
    questions = result.get("questions", [])
    tool_calls = result.get("tool_calls", [])

    # TODO: st.metric으로 생성 질문 수를 표시합니다.
    st.metric("생성 질문 수", len(questions))

    # TODO: st.bar_chart로 질문 분포 확인 영역을 만듭니다.
    chart_data = {
        "개수": {
            "면접 질문": len(questions),
            "도구 호출": len(tool_calls),
        }
    }

    st.bar_chart(chart_data)

    # TODO: st.progress로 Step 4-B 완료 상태를 표시합니다.
    st.progress(1.0, text="Step 4-B 완료")