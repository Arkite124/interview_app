# from sessons import *
from backend.sessions import *

sid = create_session("technical")
print(isinstance(sid, str))          # True
print(get_history(sid))              # []
add_message(sid, "user", "안녕하세요.")
print(len(get_history(sid)))         # 1
print(get_session_role(sid))         # technical
set_session_role(sid, "hr")
print(get_session_role(sid))         # hr
clear_session(sid)
print(get_history(sid)) 
# (3) 출력 검증+import만 — 아래 curl 명령을 순서대로 실행한다.

# 1. 세션 생성
# curl -X POST http://localhost:8000/interview/session/create \
#   -H "Content-Type: application/json" \
#   -d '{"role": "technical"}'
# 기대 출력: {"session_id": "4eaa9f44-...", "role": "technical"}

# 2. 이력 조회 (방금 받은 session_id 사용)
# curl http://localhost:8000/interview/session/{session_id}/history
# 기대 출력: {"session_id": "...", "messages": [], "role": "technical", "message_count": 0}

# 3. 면접관 유형 전환
# curl -X PATCH http://localhost:8000/interview/session/{session_id}/role \
#   -H "Content-Type: application/json" \
#   -d '{"role": "hr"}'
# 기대 출력: {"session_id": "...", "role": "hr", "message": "..."}

# 4. SSE 스트리밍
# curl -N -X POST http://localhost:8000/interview/stream \
#   -H "Content-Type: application/json" \
#   -d '{"question":"자기소개를 해 주세요.","answer":"안녕하세요.","role":"hr","session_id":"{session_id}"}'
# 기대 출력: data: ... 형태의 피드백 + data: [DONE]
