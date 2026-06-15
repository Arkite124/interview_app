from __future__ import annotations
import httpx
from typing import Any
import streamlit as st

def render_waiting_state(message: str) -> None:
    """면접 코치 응답 대기 상태를 화면에 표시한다."""
    # 여기에 st.spinner 또는 st.status로 실행 중 상태를 표시하는 코드를 채워요.
    # 힌트: with st.spinner("..."):  또는  with st.status("...") as status:
    with st.spinner(message):
        st.caption("응답을 기다리는 중입니다...")


def render_empty_interview_state(message_count: int) -> None:
    """아직 면접이 시작되지 않았을 때 첫 화면 안내를 표시한다."""
    # 여기에 message_count가 0일 때 st.empty()와 .info()로 안내 메시지를 표시하는 코드를 채워요.
    # 힌트: placeholder = st.empty()  →  if message_count == 0: placeholder.info("...")
    placeholder = st.empty()
    if message_count == 0: 
        placeholder.info("원하는 면접 요구사항을 말씀하시면 시작하겠습니다.")

def render_streaming_answer(tokens) -> str:
    """수신 토큰을 하나의 placeholder에 누적 표시한다."""
    # 여기에 placeholder를 한 번만 만들고 토큰을 누적하며 placeholder.markdown()으로 덮어쓰는 코드를 채워요.
    # 힌트: placeholder = st.empty()  →  for token in tokens: answer += token; placeholder.markdown(answer + "▌")
    placeholder = st.empty()
    answer = ""
    for token in tokens: 
        answer += token; 
        placeholder.markdown(answer + "▌")
    return answer

def format_error_message(error: Exception) -> dict[str, str]:
    """프론트엔드에서 보여 줄 오류 메시지와 표시 수준을 만든다."""
    # 여기에 error 종류를 isinstance()로 확인하고 level과 message를 담은 dict를 반환하는 코드를 채워요.
    # 힌트: if isinstance(error, httpx.ConnectError): return {"level": "error", "message": "..."}
    if isinstance(error, httpx.ConnectError): return {"level": "error", "message": "연결 오류가 발생했습니다."}
    if isinstance(error, httpx.TimeoutException): return {"level": "warning", "message": "요청 시간이 초과되었습니다."}
    if isinstance(error, httpx.HTTPStatusError):return {
            "level": "error",
            "message": f"백엔드 응답 오류가 발생했습니다. 상태 코드: {error.response.status_code}",
        }
    return {"level": "error", "message": "알 수 없는 오류가 발생했습니다."}


def show_api_error(error: Exception) -> None:
    """오류 종류에 맞는 Streamlit 메시지를 표시한다."""
    error_info = format_error_message(error)

    if error_info["level"] == "warning":
        st.warning(error_info["message"])
    else:
        st.error(error_info["message"])


def check_backend_health(backend_url: str = "http://localhost:8000") -> bool:
    """FastAPI /health endpoint를 호출해 백엔드 생존 여부를 확인한다."""
    # 여기에 httpx.Client로 {backend_url}/health에 GET 요청을 보내고 {"status": "ok"}를 확인하는 코드를 채워요.
    # 성공이면 True, 실패면 False를 반환합니다.
    # 힌트: try: response = ... response.raise_for_status() return response.json().get("status") == "ok"  except ...: return False
    try: 
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{backend_url}/health")
            response.raise_for_status()
        return response.json().get("status") == "True"
    except Exception:
        return False
def render_feedback_widget(message_id: str, conversation_id: str, index: int) -> None:
    """AI 응답에 대한 thumbs 피드백 입력 위치를 만든다."""
    feedback_value = st.feedback(
        "thumbs",
        key=f"fb_{message_id}_{index}",
    )

    # feedback_value:
    # None = 아직 선택 안 함
    # 0 = thumbs down
    # 1 = thumbs up
    if feedback_value is not None:
        rating = "up" if feedback_value == 1 else "down"

        payload = {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "rating": rating,
        }

        result = safe_post_feedback(payload)

        if result is not None:
            st.caption("피드백이 저장되었습니다.")

def safe_post_feedback(payload: dict[str, Any]) -> dict[str, Any] | None:
    """피드백 저장 요청을 보내고 사용자 친화적인 오류 메시지를 표시한다."""
    try:
        response = httpx.post(
            "http://localhost:8000/feedback",
            json=payload,
            timeout=5.0,
        )
        response.raise_for_status()
        return response.json()

    except httpx.ConnectError:
        st.error("백엔드 서버에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인해 주세요.")
        return None

    except httpx.TimeoutException:
        st.warning("피드백 저장 요청 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.")
        return None

    except httpx.HTTPStatusError as error:
        st.error(f"피드백 저장 중 서버 오류가 발생했습니다. 상태 코드: {error.response.status_code}")
        return None

    except Exception:
        st.error("피드백 저장 중 알 수 없는 오류가 발생했습니다.")
        return None
    
def filter_conversations(
    messages: list[dict[str, str]],
    keyword: str,
    roles: list[str],
) -> list[dict[str, str]]:
    """대화 내역에서 조건에 맞는 메시지를 찾는다."""
    filtered: list[dict[str, str]] = []

    normalized_keyword = keyword.strip().lower()

    for message in messages:
        content = message["content"].strip().lower()
        role = message["role"]

        keyword_matches = (
            not normalized_keyword
            or normalized_keyword in content
        )

        role_matches = (
            not roles
            or role in roles
        )

        if keyword_matches and role_matches:
            filtered.append(message)

    return filtered
# interview_app/frontend/utils.py — 7단계: self2 인계 메모
# (파일 하단에 주석으로 추가)

# === Day 5 self1 완료 상태 ===
# [ ] render_waiting_state / render_empty_interview_state / render_streaming_answer 골격 작성
# [ ] format_error_message / show_api_error / check_backend_health 골격 작성
# [ ] render_feedback_widget / safe_post_feedback 골격 작성
# [ ] filter_conversations 골격 작성
# [ ] 대시보드 입력 위치 메모 완료

# === Day 5 self2 인계 항목 ===
# - 멀티 세션 관리: st.session_state.conversations + UUID 세션 관리 연결
# - 리포트 내보내기: frontend/report.py + st.download_button 완성
# - README 최종 작성: Q9-1 5개 기준 확인표 포함
# - 대시보드 완성: render_final_dashboard()로 대시보드 표시 묶기