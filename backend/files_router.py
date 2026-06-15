# backend/routers/files.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(tags=["files"])


class ResumeQuestionRequest(BaseModel):
    """이력서 기반 면접 질문 생성 요청"""

    input: str = Field(
        min_length=1,
        description="utf-8로 디코딩된 이력서 또는 자기소개서 본문",
    )
    question_count: int = Field(
        default=5,
        ge=3,
        le=10,
        description="생성할 질문 수",
    )
    role_preset: str = Field(
        default="기술 면접",
        description="질문 역할 프리셋",
    )


class ToolCallLog(BaseModel):
    """규칙 기반 도구 호출 확인용 로그"""

    name: str
    arguments: dict
    result: dict


class ResumeQuestionResponse(BaseModel):
    """이력서 기반 질문 생성 응답"""

    questions: list[str]
    tool_calls: list[ToolCallLog]


def extract_resume_keywords(content: str) -> list[str]:
    """이력서 텍스트에서 간단한 키워드를 규칙 기반으로 추출합니다."""

    normalized_content = content.strip()

    if not normalized_content:
        raise ValueError("분석할 이력서 텍스트가 없습니다.")

    words = [
        word.strip(",.!?()[]{}\"'“”‘’")
        for word in normalized_content.split()
    ]

    words = [
        word
        for word in words
        if len(word) >= 2
    ]

    unique_words = list(dict.fromkeys(words))

    preferred_keywords = []

    tech_markers = [
        "Python","FastAPI","Streamlit","React","Spring","SpringBoot","Java", "MySQL","Oracle","JPA","API",
        "SSE","JWT","Git","Docker","AWS","GCP","프로젝트",
        "협업",
        "백엔드",
        "프론트엔드",
        "데이터베이스",
        "배포",
        "인증",
        "로그인",
    ]

    for marker in tech_markers:
        if marker.lower() in normalized_content.lower():
            preferred_keywords.append(marker)

    for word in unique_words:
        if word not in preferred_keywords:
            preferred_keywords.append(word)

    return preferred_keywords[:8]


def build_rule_based_questions(
    keywords: list[str],
    question_count: int,
    role_preset: str,
) -> list[str]:
    """키워드와 역할 프리셋을 바탕으로 규칙 기반 면접 질문을 생성합니다."""

    base_questions = []

    for keyword in keywords:
        base_questions.append(
            f"{keyword}를 사용하거나 경험한 이유를 설명해 주세요."
        )
        base_questions.append(
            f"{keyword}와 관련해 가장 어려웠던 문제와 해결 과정을 말해 주세요."
        )

    common_questions = [
        "이 프로젝트에서 본인이 맡은 역할을 구체적으로 설명해 주세요.",
        "문제가 발생했을 때 원인을 어떤 순서로 추적했는지 설명해 주세요.",
        "협업 과정에서 의견 충돌이 있었다면 어떻게 해결했는지 말해 주세요.",
        "기술 선택을 할 때 어떤 기준으로 판단했는지 설명해 주세요.",
        "이 경험을 통해 다음 프로젝트에서 개선하고 싶은 점은 무엇인가요?",
        "지원 직무와 이 경험이 어떻게 연결되는지 설명해 주세요.",
    ]

    role_questions = []

    if "기술" in role_preset:
        role_questions.extend([
            "사용한 기술의 동작 원리를 본인의 말로 설명해 주세요.",
            "성능이나 안정성을 개선하기 위해 어떤 고민을 했는지 말해 주세요.",
        ])
    elif "인성" in role_preset:
        role_questions.extend([
            "팀 프로젝트에서 본인의 강점이 드러난 순간을 설명해 주세요.",
            "피드백을 받고 개선했던 경험을 말해 주세요.",
        ])
    else:
        role_questions.extend([
            "이 경험이 지원 직무에 어떤 도움이 된다고 생각하나요?",
            "면접관에게 가장 강조하고 싶은 경험은 무엇인가요?",
        ])

    questions = base_questions + role_questions + common_questions

    unique_questions = list(dict.fromkeys(questions))

    return unique_questions[:question_count]


def generate_resume_questions(
    resume_text: str,
    question_count: int,
    role_preset: str,
) -> ResumeQuestionResponse:
    """이력서 기반 질문 생성 전체 흐름"""

    keywords = extract_resume_keywords(resume_text)

    questions = build_rule_based_questions(
        keywords=keywords,
        question_count=question_count,
        role_preset=role_preset,
    )

    tool_calls = [
        ToolCallLog(
            name="extract_resume_keywords",
            arguments={
                "section": "resume_text",
            },
            result={
                "keywords": keywords,
            },
        ),
        ToolCallLog(
            name="build_rule_based_questions",
            arguments={
                "question_count": question_count,
                "role_preset": role_preset,
            },
            result={
                "question_count": len(questions),
            },
        ),
    ]

    return ResumeQuestionResponse(
        questions=questions,
        tool_calls=tool_calls,
    )


@router.post(
    "/files/analyze",
    response_model=ResumeQuestionResponse,
)
async def create_resume_questions(
    payload: ResumeQuestionRequest,
) -> ResumeQuestionResponse:
    """업로드한 이력서 텍스트를 바탕으로 규칙 기반 면접 질문을 생성합니다."""

    try:
        return generate_resume_questions(
            resume_text=payload.input,
            question_count=payload.question_count,
            role_preset=payload.role_preset,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc