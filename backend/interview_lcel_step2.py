# interview_lcel_step2.py — 면접 코치 Step 2: Parallel/Branch/Fallback
# Step 1 입력 계약 {job_role, candidate_answer, question}은 그대로 — 변경 금지!
import json

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnableParallel

load_dotenv()  # .env의 OPENAI_API_KEY 로드 — 모델 초기화보다 먼저
model = init_chat_model("openai:gpt-4o-mini")  # provider prefix 고정


# ── [1/5] payload — Step 1 입력 계약 그대로 ──────────────────────────
def build_payload() -> dict:
    """Step 1과 동일한 3-key 입력 dict를 만들어요. key 이름 변경 금지."""
    return {
        "job_role": "백엔드 신입 개발자",
        "question": "대용량 트래픽을 처리하기 위해 어떤 구조를 설계해 본 경험이 있나요?",
        "candidate_answer": (
            "FastAPI와 PostgreSQL을 사용한 프로젝트에서 게시글 목록 조회 성능을 개선하기 위해 "
            "페이지네이션을 적용하고, 필요한 데이터만 조회하도록 쿼리를 수정한 경험이 있습니다."
        ),
    }


# ── [2/5] Parallel — 질문/모범답변/평가기준 동시 생성 ────────────────
question_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "당신은 {job_role} 직무 면접관입니다."),
        ("human", "직전 질문: {question}\n후보자 답변: {candidate_answer}\n"
                  "이 답변을 더 깊게 파고들 다음 면접 질문 1개를 만드세요."),
    ])
    | model | StrOutputParser()
)

model_answer_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "당신은 {job_role} 직무 시니어 멘토입니다."),
        ("human", "질문: {question}\n이 질문에 대한 모범 답변을 5문장 이내로 작성하세요."),
    ])
    | model | StrOutputParser()
)

rubric_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "당신은 {job_role} 직무 채용 평가위원입니다."),
        ("human", "질문: {question}\n이 질문의 답변을 채점할 평가기준 3개를 한 줄씩 작성하세요."),
    ])
    | model | StrOutputParser()
)


def extract_text(payload: dict) -> dict:
    """payload에서 prompt 변수 3개만 꺼내요 — force_fail 같은 meta key는 모델로 보내지 않아요."""
    return {
        "job_role": payload["job_role"],
        "question": payload["question"],
        "candidate_answer": payload["candidate_answer"],
    }


def guard(payload: dict) -> dict:
    """수업용 강제 실패 스위치 — fallback 시연 전용이에요."""
    if payload.get("force_fail"):
        raise ValueError("mock primary failure (수업용 강제 실패)")
    return payload


# 입력 1개가 세 가지(branch)에 복사되고, key별 결과 dict가 돌아와요.
step2_parallel = RunnableParallel(
    question=question_chain,
    model_answer=model_answer_chain,
    rubric=rubric_chain,
)

step2_core = RunnableLambda(guard) | RunnableLambda(extract_text) | step2_parallel


# ── [3/5] Branch — label enum 4종 + default ─────────────────────────
def classify_label(payload: dict) -> dict:
    """질문 키워드로 branch_label을 정해요. label은 4종 enum으로 제한."""
    q = payload["question"]

    if any(keyword in q for keyword in ["구현", "코드", "설계"]):
        label = "technical"
    elif any(keyword in q for keyword in ["경험", "갈등", "실패"]):
        label = "behavioral"
    elif any(keyword in q for keyword in ["가치관", "팀 문화", "협업 방식"]):
        label = "culture_fit"
    else:
        label = "general"

    return {**payload, "branch_label": label}


def make_route(label: str, focus: str) -> RunnableLambda:
    """route 증거를 dict로 남기는 가벼운 분기 대상이에요."""
    def _route(payload: dict) -> dict:
        return {
            "route": label,
            "focus": focus,
            "question": payload["question"],
        }

    return RunnableLambda(_route)


technical_route = make_route("technical", "구현 경험의 구체성과 기술 선택 근거를 봐요")
behavioral_route = make_route("behavioral", "상황-행동-결과가 본인 행동 중심으로 드러나는지 봐요")
culture_fit_route = make_route("culture_fit", "팀 가치와 협업 방식의 일치 여부를 봐요")
general_route = make_route("general", "기본 평가기준으로 채점해요")  # default 경로

# 좁은 조건 먼저! 앞 조건이 True면 뒤는 평가되지 않아요(first-match).
interview_branch = RunnableBranch(
    (lambda x: x["branch_label"] == "technical", technical_route),
    (lambda x: x["branch_label"] == "behavioral", behavioral_route),
    (lambda x: x["branch_label"] == "culture_fit", culture_fit_route),
    general_route,  # default — 튜플이 아니라 마지막 단독 인자예요!
)

branch_chain = RunnableLambda(classify_label) | interview_branch


# ── [4/5] Fallback — 동일 schema + 메타 2필드 ───────────────────────
def mock_step2_fallback(payload: dict) -> dict:
    """정상 결과와 같은 3-key schema에 메타 2필드만 얹어요 — 임시 문자열 금지!"""
    err = payload.get("error")  # exception_key="error"로 주입된 예외 객체

    return {
        "question": "(fallback) 준비된 기본 면접 질문이에요.",
        "model_answer": "(fallback) 준비된 기본 모범 답변이에요.",
        "rubric": "(fallback) 준비된 기본 평가기준이에요.",
        "fallback_used": True,
        "error_type": type(err).__name__ if err else None,
    }


resilient_step2 = step2_core.with_fallbacks(
    [RunnableLambda(mock_step2_fallback)],
    exceptions_to_handle=(ValueError,),  # 처리 대상 예외가 맞아야 fallback이 돌아요
    exception_key="error",               # primary/fallback 모두 dict 입력 필수
)


# ── [5/5] 실행부 — layer별 증거 3종 출력 ────────────────────────────
if __name__ == "__main__":
    payload = build_payload()

    # 증거 1) Parallel dict shape — 출력은 문자열이 아니라 dict예요
    out = resilient_step2.invoke(payload)
    print("[parallel]", out.keys())
    print(json.dumps({k: str(v)[:40] for k, v in out.items()}, ensure_ascii=False, indent=2))

    # 증거 2) Branch route — 4 label + default 사례 1건
    sample_questions = [
        "대용량 트래픽 처리를 구현한 코드 설계 경험을 말해 주세요.",      # technical
        "고객과의 갈등을 해결한 경험을 말해 주세요.",                    # behavioral
        "우리 팀 문화에서 본인의 협업 방식은 어떻게 작동할까요?",         # culture_fit
        "오늘 점심 뭐 드셨어요?",                                       # 매칭 실패 → default
    ]

    for q in sample_questions:
        route_out = branch_chain.invoke({**payload, "question": q})
        print("[branch]", route_out)

    # 증거 3) Fallback 메타 2필드 — 강제 실패로 fallback 경로를 태워요
    fb_out = resilient_step2.invoke({**payload, "force_fail": True})
    print("[fallback]", fb_out.keys())
    print("[fallback]", {
        "fallback_used": fb_out["fallback_used"],
        "error_type": fb_out["error_type"],
    })