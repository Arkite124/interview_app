from typing import Any, TypedDict,Literal
from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver

from backend.interview_rag import job_retriever, interview_chain


class RagState(TypedDict):
    question: str               # 사용자의 질문 (입력)
    docs: list[Any]             # 검색된 문서 조각들
    answer: str                 # 최종 답변 (출력)
    sources: list[dict]         # Day 3 출처 계약을 state로 통과시키는 채널
    quality: dict[str, Any]     # 평가 결과 — 통과 여부 + 이유
    attempts: int               # 재검색 시도 횟수 (오늘은 0 고정)
    route_log: list[str]        # 분기 기록 (필드만 확보, 동작은 이어지는 교시)
# 예제 2: prepare_retry node — 변경은 전부 여기서, 새 list 반환으로 (rag_graph.py)
MAX_RETRIES = 1  # attempts cap: 재검색은 전체 실행에서 1회만 허용

def should_retry(state: RagState) -> Literal["retry", "generate"]:
    """router: state를 읽기만 하고 label 문자열만 반환한다. state update 금지."""
    quality_ok = state.get("quality", {}).get("passed", False)
    if not quality_ok and state.get("attempts", 0) < MAX_RETRIES:
        return "retry"
    return "generate"

def prepare_retry(state: RagState) -> dict[str, Any]:
    """state 변경은 node의 책임: attempts 증가 + route_log에 4필드 기록 추가."""
    new_log = {
        "attempts": state.get("attempts", 0) + 1,
        "quality_ok": state.get("quality", {}).get("passed", False),
        "decision": "retry",
        "reason": "insufficient sources",
    }
    return {
        "attempts": state.get("attempts", 0) + 1,
        # append 금지 — 기존 list를 펼쳐서 새 list로 반환해야 누적이 보장됩니다.
        "route_log": [*state.get("route_log", []), new_log],
    }

def grade(state: RagState) -> dict[str, Any]:
    """재검색 조건 단순화: 근거 문서가 2건 미만이면 품질 미달로 판정."""
    passed = len(state.get("docs", [])) >= 2
    reason = "sources ok" if passed else "insufficient sources"
    return {"quality": {"passed": passed, "reason": reason}}


def generate(state: RagState) -> dict[str, Any]:
    """답변 생성 + 'generate로 들어온 이유'를 route_log에 남겨 직행/우회를 구분."""
    out = interview_chain.invoke({
        "question": state["question"]
    }) # Day 3 면접 chain — {answer, sources} 반환
    return {"answer": out["answer"], "sources": out["sources"]}

def retrieve(state: RagState) -> dict[str, Any]:
    # 실제 연결 시: docs = retriever.invoke(state["question"])  # rag_pipeline.get_retriever(k=3)
    docs = job_retriever.invoke(state["question"])
    return {"docs": docs}

builder = StateGraph(RagState)
builder.add_node("retrieve", retrieve)
builder.add_node("grade", grade)
builder.add_node("generate", generate)
builder.add_node("prepare_retry", prepare_retry)  # 변경 전담 node 등록

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "grade")
# grade 다음은 고정 노선이 아니라 router에게 묻습니다.
builder.add_conditional_edges(
    "grade",
    should_retry,
    {"retry": "prepare_retry", "generate": "generate"},  # path_map: label -> node
)
builder.add_edge("prepare_retry", "retrieve")  # 재작업 라인: 기존 retriever 재호출 경로
builder.add_edge("generate", END)              # 종료 경로를 graph에 명시

graph = builder.compile()
# InMemorySaver는 개발/테스트용 — 프로세스가 끝나면 저장 내용도 함께 사라져요.
# (실서비스용 Postgres/Redis/SQLite 영속 saver는 오늘 범위 밖 — 이 주석으로만 기록)
checkpointer = InMemorySaver()            # ← 모듈 수준에서 '1회'만 생성 (요청 처리 함수 내부 금지)

interview_app = builder.compile(checkpointer=checkpointer)  # wrapper가 import하는 이름
# 같은 thread 2회 — thread_id는 input이 아니라 config["configurable"]에!

# # 출력 (예시):
# StateSnapshot
# next = ()
# answer    = 병가 규정은 진단서 제출 시 ...
# sources   = (state에 없음)
# route_log = [{'attempts': 1, 'quality_ok': False, 'decision': 'retry', 'reason': 'insufficient sources'}]
# attempts  = 1


