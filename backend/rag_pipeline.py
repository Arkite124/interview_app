from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

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
DOC_PATH = "backend/docs/sample.pdf"

loader = PyPDFLoader(DOC_PATH)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,         # 문자 수 기준 — 기본값 4000이라 생략하면 안 됩니다
    chunk_overlap=50,
    add_start_index=True,   # 기본값 False — 빼먹으면 start_index metadata가 사라집니다
)
chunks = splitter.split_documents(docs)
embeddings = get_embeddings()   # index 생성과 검색이 같은 좌표계를 쓰도록 단일 factory 사용

# CUSTOMIZE: PERSIST_DIR — 면접 코치 트랙은 "./chroma_job_docs"로 분리 (혼합 금지)
PERSIST_DIR = "./chroma_job_docs"

db = Chroma.from_documents(
    chunks,                         # list[Document] — 원문 chunk + metadata가 통째로 저장됩니다
    embedding=embeddings,           # from_documents의 인자명은 embedding= 입니다
    persist_directory=PERSIST_DIR,  # 지정하는 순간 자동 영속화 — 별도 저장 호출이 없습니다
)
query = "휴가 신청 절차는 어떻게 되나요?"
results = db.similarity_search(query, k=2)   # k=2: 좌표가 가장 가까운 chunk 후보 2개

for doc in results:
    print(doc.page_content[:120])
    print({
        "source": doc.metadata.get("source"),
        "page": doc.metadata.get("page"),
        "start_index": doc.metadata.get("start_index"),
    })

# QUESTION = "휴가 신청 절차는 어떻게 되나요?"     # 오늘 모든 실험의 고정 질문

# # store에 직접 묻는 호출 — 동작 확인용 1회만
# results = db.similarity_search(QUESTION, k=2)
# print(f"similarity_search 반환 {len(results)}건")
# print(results[0].metadata)