# rag_chain.py — 사내 문서 QA: answer + sources 동시 반환
# 전제: rag_pipeline.py(get_retriever, format_sources)와 ./chroma_company_docs index
import sys

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.rag_chain import build_rag_chain
from backend.rag_pipeline import get_embeddings,format_sources
from langchain_chroma import Chroma
load_dotenv()

# ── 전이 계약: 다음 셀프(self2)는 아래 CUSTOMIZE 3곳의 '값만' 바꿔 도메인을 전이해요 ──
# CUSTOMIZE: domain PDF path — 사내 QA 트랙 값 (rag_pipeline.py가 색인한 문서와 동일)
# DOC_PATHS = "backend/docs/company_doc.pdf"
DOC_PATHS = "./docs/company_doc.pdf"
# CUSTOMIZE: PERSIST_DIR — 트랙별 index 분리 (rag_pipeline.py가 재로드하는 폴더와 동일)
PERSIST_DIR = "./chroma_job_docs"
# CUSTOMIZE: system prompt — 도메인 정책의 단일 교체 지점 ({context}는 함수가 붙여요)
SYSTEM_PROMPT = "다음 근거 문서만 사용해 답하세요. 모르면 모른다고 답하세요."
pdf_docs=PyPDFLoader(DOC_PATHS).load()
spliter=RecursiveCharacterTextSplitter(
    chunk_size=500, # 한 청크의 목표 크기 - 문자 수 기준
    chunk_overlap=50, # 인접 청크와 겹치는 문자 수
    add_start_index=True,
)
job_chunks=spliter.split_documents(pdf_docs)

model = init_chat_model("openai:gpt-5.4-nano")

question = "지원 필수 요건은 무엇인가요?"  # 사내 QA 고정 질문

def format_docs(docs) -> str:
    """LLM prompt에 넣을 context '문자열'만 만들어요 (sources와 역할 분리)."""
    return "\n\n".join(doc.page_content for doc in docs)
job_db = Chroma.from_documents(            # 신규 구축은 embedding= 인자
    job_chunks,
    embedding=get_embeddings(),
    persist_directory=PERSIST_DIR,         # 지정만 하면 자동 영속화 — persist() 호출 없음
)
job_retriever = job_db.as_retriever(search_kwargs={"k": 3})
interview_chain = build_rag_chain(job_retriever, SYSTEM_PROMPT)   # 공통 함수 재사용 — 오늘의 핵심 줄

def ask_job_rag(question: str) -> dict:
    """직무 RAG 진입점 — 반환 모양은 self1의 ask_rag와 동일한 {answer, sources} 계약."""
    return interview_chain.invoke({"question": question})

if __name__ == "__main__":
    result = ask_job_rag("이 직무에서 가장 중요한 역량을 기준으로 면접 질문 1개를 만들어 주세요.")
    print(result["answer"][:200])
    print(result["sources"][0])


# # 저장소 로드
# job_db = Chroma(
#     persist_directory="./chroma_job_docs",
#     embedding_function=get_embeddings(),   # 검색 쪽도 반드시 같은 factory
# )
