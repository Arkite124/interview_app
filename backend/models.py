"""models.py — ChatModel factory (Day 1 S3)

교안 핵심 패턴:
- init_chat_model("openai:gpt-4o-mini") provider prefix
- load_dotenv()는 모델 초기화보다 반드시 먼저 호출
- 모든 모듈이 이 factory를 import하여 모델 생성 (provider/model 변경 시 이 파일만 수정)
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# .env를 최상위에서 1회 로드 — 모델 초기화보다 반드시 먼저
load_dotenv()

# 프로젝트 전체에서 사용하는 기본 모델 설정
DEFAULT_MODEL = "openai:gpt-4o-mini"


def get_model(model_id: str = DEFAULT_MODEL):
    """ChatModel 단일 factory.

    교안 규칙:
    - provider:model 형식의 문자열을 받아 ChatModel을 반환
    - 이 함수 바깥에서 init_chat_model을 직접 호출하지 않음
    """
    return init_chat_model(model_id)
