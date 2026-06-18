from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import sys
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv()  # .env의 OPENAI_API_KEY를 환경 변수로 로딩 — key 값은 절대 print하지 않습니다

# 이 줄이 단일 출처(single source of truth)입니다.
# 모델 이름은 프로젝트 전체에서 오직 여기 한 곳에만 적습니다.
EMBEDDING_MODEL = "text-embedding-3-small"# embedding factory — 여기서 새로 만들지 않고 import만 합니다
def get_embeddings() -> OpenAIEmbeddings:
    """과정 전체가 공유하는 embedding 객체를 만든다 — 다른 파일은 직접 생성 금지, 이 함수만 import."""
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)  # 인자명은 model= 입니다 (model_name 아님)
# CUSTOMIZE: domain PDF path — 면접 코치 트랙에서는 직무 PDF/채용공고 경로로 교체
# DOC_PATH = "backend/docs/sample.pdf"
DOC_PATH = "./docs/sample.pdf"

loader = PyPDFLoader(DOC_PATH)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,         # 문자 수 기준 — 기본값 4000이라 생략하면 안 됩니다
    chunk_overlap=50,
    add_start_index=True,   # 기본값 False — 빼먹으면 start_index metadata가 사라집니다
)
chunks = splitter.split_documents(docs)
embeddings = get_embeddings()   # index 생성과 검색이 같은 좌표계를 쓰도록 단일 factory 사용

# # CUSTOMIZE: PERSIST_DIR — 면접 코치 트랙은 "./chroma_job_docs"로 분리 (혼합 금지)
PERSIST_DIR = "./chroma_company_docs"

db = Chroma.from_documents(
    chunks,                         # list[Document] — 원문 chunk + metadata가 통째로 저장됩니다
    embedding=embeddings,           # from_documents의 인자명은 embedding= 입니다
    persist_directory=PERSIST_DIR,  # 지정하는 순간 자동 영속화 — 별도 저장 호출이 없습니다
)
# query = "휴가 신청 절차는 어떻게 되나요?"
# results = db.similarity_search(query, k=2)   # k=2: 좌표가 가장 가까운 chunk 후보 2개

# for doc in results:
#     print(doc.page_content[:120])
#     print({
#         "source": doc.metadata.get("source"),
#         "page": doc.metadata.get("page"),
#         "start_index": doc.metadata.get("start_index"),
#     })

# QUESTION = "휴가 신청 절차는 어떻게 되나요?"     # 오늘 모든 실험의 고정 질문

# # store에 직접 묻는 호출 — 동작 확인용 1회만
# results = db.similarity_search(QUESTION, k=2)
# print(f"similarity_search 반환 {len(results)}건")
# print(results[0].metadata)
def get_retriever(k: int = 3):
    """Chroma index를 RAG chain에 끼울 수 있는 retriever로 전환합니다.

    k는 후보 문서 수입니다(정답 개수가 아닙니다).
    """
    return db.as_retriever(search_kwargs={"k": k})

def format_sources(docs) -> list[dict]:
    """Document 목록을 API/UI에 바로 내보낼 수 있는 dict 목록으로 변환합니다.

    필수 metadata(source, start_index)가 빠진 문서가 섞여 있으면
    조용히 넘어가지 않고 즉시 멈춥니다(hard exit).
    """
    sources: list[dict] = []
    for doc in docs:
        meta = doc.metadata
        if meta.get("source") is None or meta.get("start_index") is None:
            # 빈 문자열로 메꾸지 않습니다 — 누락은 파이프라인 앞 단계의 버그입니다
            sys.exit(f"[source contract] 필수 metadata 누락: {meta}")
        sources.append({
            "source": meta["source"],            # 어느 문서에서 왔는지
            "page": meta.get("page"),            # TXT는 page가 없으므로 None 허용
            "start_index": meta["start_index"],  # 원문 내 시작 위치
            "snippet": doc.page_content[:100],   # 근거 미리보기 (원문 전체 노출 금지)
        })
    return sources
