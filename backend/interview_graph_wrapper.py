 # self1 (사내 QA 트랙): 스크립트에 풀어진 호출부

from backend.interview_graph import interview_app as app
from backend.interview_rag import ask_job_rag
# self2 (면접 트랙): 단일 진입점 함수 — ① signature
def run_interview_graph(question: str, thread_id: str) -> dict:
    """면접 코치 LangGraph workflow 단일 진입점.
    thread_id 규약: interview:{이름}:{회차} — 예: interview:alice:1
   """
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke(
        {"question": question, "sample_docs": [], "answer": "",
         "quality": {}, "attempts": 0, "route_log": []},  # 초기 state — self1과 동일 골격
        config,  # invoke의 두 번째 인자
    )
    return {
        "answer": result["answer"],
        "sources": result.get("sources", []),  # 방어적 접근 — 비면 빈 list
        "thread_id": thread_id,  # 부가 metadata — 계약 key는 위 두 개
    }
# def run_interview_graph(question: str, thread_id: str) -> dict:
#     out = ask_job_rag(question)            # Day 3 service 함수 재사용
#     return {"answer": out["answer"], "sources": out.get("sources", []), "thread_id": thread_id}
if __name__ == "__main__":
    # thread naming 규약: interview:{이름}:{회차}
    print(run_interview_graph("자기소개 피드백 주세요", "interview:alice:1"))            # alice 1회차
    print(run_interview_graph("방금 답변의 강점을 한 가지 더 보완해 주세요", "interview:alice:1"))  # alice 2회차 — 같은 슬롯
    print(run_interview_graph("자기소개 피드백 주세요", "interview:bob:1"))
    snap_alice =app.get_state({"configurable": {"thread_id": "interview:alice:1"}})
    snap_bob = app.get_state({"configurable": {"thread_id": "interview:bob:1"}})
    print(snap_alice.values["question"])  # 2회차 질문 — alice 슬롯의 최신 저장본
    print(snap_bob.values["question"])