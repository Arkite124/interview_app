# AI 면접 코치 웹앱

## 1. 프로젝트 개요
TODO: 이 프로젝트가 무엇을 하는지 2~3문장으로 설명하세요.
8주차 CLI 면접 코치를 Streamlit + FastAPI로 전환한 결과물입니다.
FastAPI에서 LLM을 호출하여 Streamlit으로 frontend를 띄워 결과물을 볼 수 있습니다.
덧붙인 react 구조는 보지 않으셔도 됩니다.
FastAPI+React도 했지만, session 상태 유지가 아닌 임의로 localStorage 방식을 선택했습니다. 
## 2. 실행 방법
uv venv --python 3.11로 venv 생성
uv sync로 필요 패키지 설치 </br>
.env에 OPENAI_API_KEY,BACKEND_URL을 등록하고 사용해야 한다.</br>
CLI에 현재 디렉토리 기준 실행 방법 명령어 </br>
### backend FastAPI 
- uv run uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
- uv run uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000

### frontend-streamlit 
- uv run streamlit run frontend/app.py --server.port 8501

### frontend_react 
- cd front_end
- npm install (package.json에 있는 필수 패키지 설치)
- npm run dev
- react는 10주차 기능 불가
## 3. 핵심 기능 5개

### 1. 면접 에이전트 스트리밍 채팅

사용자가 면접 답변이나 요청을 입력하면 FastAPI 백엔드의 `/agents/stream` 엔드포인트로 요청을 보냅니다.  
백엔드는 SSE 방식으로 AI 면접관의 응답을 토큰 단위로 전달하고, Streamlit,React 화면에서는 이를 실시간 채팅처럼 출력합니다.

---

### 2. 설정 페이지

면접 에이전트가 사용할 설정을 관리하는 페이지를 구현했습니다.

관리하는 설정 항목은 다음과 같습니다.

- 모델 선택
- temperature 설정
- 역할 프리셋 선택
- 시스템 프롬프트 편집
- 에이전트 모드 선택 `single / multi`

저장된 설정은 이후 면접 에이전트 페이지와 이력서 분석 페이지에서 재사용됩니다.

---

### 3. 이력서 / 자기소개서 txt 파일 업로드

사용자가 `.txt` 파일 형식의 이력서 또는 자기소개서를 업로드할 수 있도록 구현했습니다.  
업로드된 파일은 프론트엔드에서 텍스트로 읽어 미리보기로 표시하고, 분석 요청 시 백엔드로 전달합니다.

---

### 4. 이력서 기반 면접 질문 생성

업로드된 이력서 또는 자기소개서 본문을 기반으로 맞춤형 면접 질문을 생성하는 기능을 구현했습니다.  
프론트엔드는 `/files/analyze` 엔드포인트로 다음 데이터를 전송합니다.

```json
{
  "input": "이력서 또는 자기소개서 본문",
  "question_count": 5,
  "role_preset": "기술 면접"
}
```

## 4. 기술 스택
    python
 
    "dotenv>=0.9.9"
    "fastapi>=0.136.3"
    "openai>=2.41.0"
    "openai-agents>=0.17.4"
    "streamlit>=1.58.0"
    "pydantic==2.13.4"

    React

    "@tailwindcss/vite": "^4.3.0",
    "axios": "^1.17.0",
    "react": "^19.2.6",
    "react-dom": "^19.2.6",
    "react-router-dom": "^7.17.0",
    "tailwindcss": "^4.3.0"
- 해당 패키지 버전은 uv pip freeze > requirements.txt 에서 가져온 것이며,react는 package.json에 있는 값을 복사했다.

## 5. Day 1~5 완성 과정
    day 1 : streamlit 준비 및 채팅 골격 준비
    day 2 : FastAPI 백엔드 pydantic,router 골격 및 StreamingResponse를 이용한 프론트 스트리밍 골격
    day 3 : FastAPI 및 Streamlit API 연결 및 agent 전환 / 라우터 역할 파일 분리
    day 4 : sidebar 이력서 Layout 연결 및 광역 session_state 선언
    day 5 : utils.py에 에러상태 정의 fastAPI 연결상태 확인 Swagger docs를 확인햐여 일치하는 값으로 변환
- react버전은 흐름도는 담았지만, 약간 다른 과정, 약간 다른 결과물 , 오류 처리에 한계


