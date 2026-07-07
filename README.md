# AI 면접 코치 웹앱

## 1. 프로젝트 개요
TODO: 이 프로젝트가 무엇을 하는지 2~3문장으로 설명하세요.
8주차 CLI 면접 코치를 Streamlit + FastAPI로 전환한 결과물입니다.
FastAPI에서 LLM을 호출하여 Streamlit으로 frontend를 띄워 결과물을 볼 수 있습니다.
덧붙인 react 구조는 보지 않으셔도 됩니다.
FastAPI+React도 했지만, session 상태 유지가 아닌 임의로 localStorage 방식을 선택했습니다. 
## 2. 프로젝트 구조

이 레포지토리의 본체는 **면접 에이전트(interview app)** 입니다 — FastAPI 백엔드(`backend/main.py`) + Streamlit(`frontend/interview_app.py`) + React(`front_end/`) 3개 프론트가 같은 백엔드를 바라봅니다.

```
interview_app/
├── backend/
│   ├── main.py                # FastAPI 엔트리포인트 — 아래 라우터 3개 + /interview/rag, /health
│   ├── interview_router.py    #   /interview/session/*, /interview/stream (세션 관리 + SSE 피드백)
│   ├── agent_router.py        #   /agents/stream — openai-agents 기반 single/multi 에이전트 SSE
│   ├── files_router.py        #   /files/analyze — 이력서 텍스트 → 규칙 기반 질문 생성
│   ├── interview_rag.py       #   /interview/rag가 사용하는 직무 공고 RAG chain
│   └── sessions.py            #   in-memory 세션 저장소
│
├── frontend/
│   └── interview_app.py       # Streamlit 단일 파일, 5모드 면접 코치 UI
│
├── front_end/                 # React + Vite UI — ⚠️ 완전히 분리된 별도 구성 요소
│   │                           #   Python venv/uv와 무관, Node.js 환경을 따로 설치·실행해야 함
│   └── src/
│       ├── layouts/RootLayout.jsx   # 사이드바 내비게이션
│       ├── pages/                    # HomePage, ResumePage, AgentStreamPage, SettingsPage
│       ├── components/               # ChatInput, ChatMessageList, InterviewSettingsPanel 등
│       ├── api/                      # resumeApi, interviewAPI, agentStreamApi
│       └── config/, hooks/, utils/
│
├── core/                       # 8주차부터 재사용하는 공용 모듈 (roles, agents, tools, config)
└── .env                        # OPENAI_API_KEY, BACKEND_URL 등
```

> 이 레포지토리 뒤쪽에 **사내 문서 QA 챗봇**(`backend/app.py` + `frontend/app.py`/`pages/` + React `front_end/src/pages/qa/*`)을 별도로 이어서 만들었습니다. interview app과는 독립된 확장이라 위 구조도에서는 생략했습니다.

## 3. 페이지별 역할

### Streamlit — `frontend/interview_app.py`
사이드바 라디오로 5개 모드를 전환하는 단일 스크립트:

| 모드 | 호출 엔드포인트 | 역할 |
|---|---|---|
| `rag` 📚 | `POST /interview/rag` | 직무 공고 문서를 근거로 맞춤형 면접 코칭 |
| `rag_thread` 🧵 | `POST /interview/rag/thread` | thread_id로 대화 맥락을 유지하며 코칭 |
| `chat` 💬 | `POST /interview/chat` | 직무 문서 없이 일반 면접 상담 |
| `structured` 📊 | `POST /interview/structured` | `질문 \| 답변` 형식 입력을 점수/강점/개선점/후속 질문으로 평가 |
| `parallel` 🔀 | `POST /interview/parallel` | 면접 질문 생성 + 준비 팁을 동시에 생성 |

⚠️ 현재 `backend/main.py`에는 `/interview/rag`만 구현되어 있어 **`rag` 모드만 정상 동작**하며, 나머지 모드는 대응 엔드포인트가 없어 404가 발생합니다.

### React — `front_end/src/pages/`

| 페이지 | 라우트 | 호출 엔드포인트 | 역할 |
|---|---|---|---|
| `HomePage.jsx` | `/` | – | 서비스 소개 랜딩 페이지 |
| `ResumePage.jsx` | `/resume` | `POST /files/analyze` | 이력서/자소서 txt 업로드 → 규칙 기반 예상 질문 생성 |
| `AgentStreamPage.jsx` | `/agents` | `POST /agents/stream` (SSE) | 설정값(모델/온도/역할/프롬프트/single·multi 모드) 기반 면접 에이전트와 실시간 스트리밍 대화 |
| `SettingsPage.jsx` | `/settings` | – (localStorage) | 모델, temperature, system prompt, 역할 프리셋, single/multi 모드를 저장해 다른 페이지에서 재사용 |

### Backend 라우터 요약

| 파일 | 담당 엔드포인트 |
|---|---|
| `backend/main.py` | FastAPI 엔트리포인트, 아래 라우터 3개 + `/interview/rag`, `/health` |
| `backend/interview_router.py` | `/interview/session/*`(세션 생성·이력·역할 변경), `/interview/stream`(SSE 피드백) |
| `backend/agent_router.py` | `/agents/stream` |
| `backend/files_router.py` | `/files/analyze` |

> 사내 문서 QA 챗봇의 페이지(`frontend/app.py`/`pages/`, React `qa/*`)와 백엔드(`backend/app.py`)는 이 레포지토리 뒤쪽에 별도로 이어서 만든 것이라 위 표에서는 생략했습니다.

## 4. 실행 방법
uv venv --python 3.11로 venv 생성
uv sync로 필요 패키지 설치 </br>
.env에 OPENAI_API_KEY,BACKEND_URL을 등록하고 사용해야 한다.</br>
CLI에 현재 디렉토리 기준 실행 방법 명령어 </br>

### backend FastAPI
- `uv run uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000`

### frontend-streamlit
- `uv run streamlit run frontend/interview_app.py --server.port 8501`

### frontend_react (⚠️ 별도 구성 요소 — 필수)
`front_end`는 Python venv/uv 설치와 **무관한 별개의 Node.js 프로젝트**이므로, 위 backend를 켠 뒤 아래를 **따로** 실행해야 화면이 뜹니다.
- `cd front_end`
- `npm install` (package.json에 있는 필수 패키지 설치)
- `npm run dev`

> 사내 문서 QA 챗봇(`backend/app.py` + `frontend/app.py` + React `qa/*`)을 실행하려면 `backend.app:app`을 별도 포트로 띄우세요 — interview app과 기본 포트(8000)가 겹치므로 동시 실행은 피하세요.

## 5. 핵심 기능 5개

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

## 6. 기술 스택
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

## 7. Day 1~5 완성 과정
    day 1 : streamlit 준비 및 채팅 골격 준비
    day 2 : FastAPI 백엔드 pydantic,router 골격 및 StreamingResponse를 이용한 프론트 스트리밍 골격
    day 3 : FastAPI 및 Streamlit API 연결 및 agent 전환 / 라우터 역할 파일 분리
    day 4 : sidebar 이력서 Layout 연결 및 광역 session_state 선언
    day 5 : utils.py에 에러상태 정의 fastAPI 연결상태 확인 Swagger docs를 확인햐여 일치하는 값으로 변환
- react버전은 흐름도는 담았지만, 약간 다른 과정, 약간 다른 결과물 , 오류 처리에 한계
## Q9-1 수료 기준 확인
TODO: 아래 5개 기준을 직접 확인한 결과를 적으세요.
체크 항목
확인
1. interview_app/frontend/report.py가 생성되었다. &gt; 해당 내용은 history.py에 담음
2. build_interview_report() 함수가 비어 있지 않은 문자열을 반환한다.
✅
3. render_report_download()에서 세션/메시지 없을 때 안내 메시지가 표시된다.
✅
4. ensure_session_state(), add_new_session(), delete_current_session()이 작성되었다.
✅
5. render_final_dashboard()에서 st.progress 값이 1.0 이하로 제한된다.
✅
6. interview_app/README.md에 6개 섹션이 모두 채워졌다.
[ ]
7. Q9-1 5개 기준 확인표에서 4개 이상이 ✅로 표시된다.
[ ]

