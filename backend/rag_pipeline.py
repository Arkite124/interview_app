"""rag_pipeline.py — RAG 데이터 파이프라인 (Day 3 S3-S6)

교안 핵심 패턴:
- get_embeddings(): OpenAIEmbeddings factory — 같은 좌표계 계약
  - index 생성과 검색이 반드시 같은 factory를 사용해야 함
  - OpenAIEmbeddings 직접 호출은 이 파일 안에서만 허용
- build_index(): Load → Split → Embed → Chroma 저장
  - chunk_size=500, chunk_overlap=50, add_start_index=True (기준 설정 3종)
  - persist_directory로 자동 영속화 — db.persist() 호출 없음
- get_retriever(): Chroma 재로드 + as_retriever
  - 재로드 시 embedding_function= (인자명 주의: from_documents는 embedding=)
- format_sources(): metadata에서 source/page/snippet 추출

파일 구조 규칙:
- ./chroma_company_docs: 사내 문서 트랙 전용 (혼합 금지)
"""

import os

from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.models import get_model  # noqa: F401 — load_dotenv 보장용

# ─── 상수 ────────────────────────────────────────────────────────────

EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_DOC_PATH = os.path.join(os.path.dirname(__file__), "sample_docs", "company_policy.txt")
DEFAULT_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "./chroma_company_docs")

# 기준 설정 3종 (교안 고정값)
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
ADD_START_INDEX = True


# ─── Embedding factory ──────────────────────────────────────────────

def get_embeddings():
    """OpenAIEmbeddings 단일 factory.

    교안 규칙:
    - 이 함수 바깥에서 OpenAIEmbeddings를 직접 호출하지 않음
    - index 생성과 검색이 같은 좌표계를 쓰도록 단일 factory 사용
    - 모델 교체 시 이 함수만 수정 → 기존 index 폴더 삭제 후 재구축
    """
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)


# ─── Index 생성 ─────────────────────────────────────────────────────

def build_index(
    doc_path: str = DEFAULT_DOC_PATH,
    persist_dir: str = DEFAULT_PERSIST_DIR,
) -> Chroma:
    """Load → Split → Embed → Chroma 저장.

    Args:
        doc_path: 문서 파일 경로
        persist_dir: Chroma index 저장 폴더

    Returns:
        생성된 Chroma db 인스턴스

    교안 규칙:
    - persist_directory를 재사용하면 추가 누적됨 — 설정 변경 시 폴더 삭제 후 재구축
    - from_documents의 인자명은 embedding= (embedding_function= 아님)
    """
    # 1. Load
    loader = TextLoader(doc_path, encoding="utf-8")
    docs = loader.load()
    print(f"[rag_pipeline] 문서 로드: {len(docs)}건")

    # 2. Split (기준 설정 3종)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=ADD_START_INDEX,
    )
    chunks = splitter.split_documents(docs)
    print(f"[rag_pipeline] chunk 분할: {len(chunks)}건")

    # 3. Embed + Store
    embeddings = get_embeddings()
    db = Chroma.from_documents(
        chunks,
        embedding=embeddings,  # 인자명 주의: from_documents는 embedding=
        persist_directory=persist_dir,
    )
    print(f"[rag_pipeline] index 생성 완료: {persist_dir}")
    return db


# ─── Retriever factory ──────────────────────────────────────────────

def get_retriever(persist_dir: str = DEFAULT_PERSIST_DIR, k: int = 3):
    """Chroma 재로드 + as_retriever.

    교안 규칙:
    - 재로드 시 인자명은 embedding_function= (from_documents의 embedding=과 다름!)
    - 검색 시에도 반드시 같은 get_embeddings() factory 사용
    """
    db = Chroma(
        persist_directory=persist_dir,
        embedding_function=get_embeddings(),  # 인자명 주의: 생성자는 embedding_function=
    )
    return db.as_retriever(search_kwargs={"k": k})


# ─── Source 포맷팅 ──────────────────────────────────────────────────

def format_sources(docs: list[Document]) -> list[dict]:
    """검색된 Document 리스트에서 출처 정보를 추출하여 SourceItem 형식으로 반환.

    교안 계약: source/page/snippet 3필드 보존 (Day 5 S3)
    """
    sources = []
    for doc in docs:
        sources.append({
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page", 0),
            "snippet": doc.page_content[:120],
        })
    return sources

#
# # ─── smoke test ──────────────────────────────────────────────────────
#
# if __name__ == "__main__":
#     import shutil
#
#     # 기존 index 초기화 (재현 가능한 테스트)
#     if os.path.exists(DEFAULT_PERSIST_DIR):
#         shutil.rmtree(DEFAULT_PERSIST_DIR)
#         print(f"[rag_pipeline] 기존 index 삭제: {DEFAULT_PERSIST_DIR}")
#
#     # index 생성
#     db = build_index()
#
#     # k=2 smoke 검색
#     query = "휴가 신청 절차는 어떻게 되나요?"
#     results = db.similarity_search(query, k=2)
#     print(f"\n[smoke] query: {query}")
#     for doc in results:
#         print(doc.page_content[:120])
#         print(format_sources([doc])[0])
#         print()
#
#     # retriever smoke
#     retriever = get_retriever(k=3)
#     retriever_results = retriever.invoke("출장비 한도는?")
#     print(f"[retriever smoke] {len(retriever_results)}건 검색됨")
#     for doc in retriever_results:
#         print(f"  - {doc.page_content[:80]}...")
