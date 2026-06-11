"""coach_agents.py - Agent정의, @function_tool 등록, Guardrails, Handoff 구성"""

import os
from agents import Agent
from agents import GuardrailFunctionOutput
from agents import RunContextWrapper
from agents import TResponseInputItem
from agents import function_tool
from agents import input_guardrail

from pydantic import BaseModel
from pydantic import Field

from config import MODEL_NAME
from config import ini_env
from roles import get_role
from tools import make_interview_question as _make_question
from tools import score_answer as _score_answer
from tools import make_feedback as _make_feedback

# ======
# 1. INPUT GUARDRAIL - 프롬프트 인젝션 차단
# ======

class InputCheck(BaseModel):
  blocked: bool = Field(description="위험 입력이면 True")
  reason: str = Field(description="판단 사유")
  matched_terms: list[str] = Field(default_factory=list)

DANGER_TERMS = [
  "ignore previous instructions",
  "reveal system prompt",
  "show hidden instructions",
  "developer message",
  "이전 지시 무시",
  "시스템 프롬프트 보여줘",
  "키 보여줘",
  "지시 무시"
]

def inspect_user_text(user_text: str) -> InputCheck:
  """위험 키워드를 검사"""
  lowered = user_text.lower()
  matched = [term for term in DANGER_TERMS if term in lowered]
  # for term in DANGER_TERMS:
  #   if term in lowered:
  #     matched.append(term)
      
  return InputCheck(
    blocked=bool(matched),
    reason="프롬프트 인젝션 의심" if matched else "통과",
    matched_terms=matched
  )

def _normalize_input(raw_input: str | list[TResponseInputItem]) -> str:
  if isinstance(raw_input, str):
    return raw_input
  return " ".join(str(item) for item in raw_input)

@input_guardrail
async def injection_guardrail(
  ctx: RunContextWrapper[None],
  agent: Agent,
  input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
  check = inspect_user_text(_normalize_input(input))
  return GuardrailFunctionOutput(
    output_info=check,
    tripwire_triggered=check.blocked
  )

# =====
# 2. @function_tool 등록
# =====
@function_tool
def make_interview_question(role: str, difficulty: str) -> str:
    """지원 직무와 난이도를 받아 면접 질문 한 개를 만듭니다.
    Args:
      role: 지원 직무 이름입니다. 예: 백엔드 신입, 데이터 분석 신입
      difficulty: 질문 난이도입니다. 예: 기초, 심화
    """
    print(f"[tool-log] make_interview_question called: role={role}, difficulty={difficulty}")
    if difficulty == "기초":
        return f"{role} 직무에서 최근에 해결한 문제를 한가지 설명하세요."
    if difficulty == "심화":
        return f"{role} 직무에서 장애 상황을 반견했을때 원인 분석 순서를 설명하세요."
    return f"{role} 직무 지원자로서 본인의 강점을 사례와 함께 말하십시오."

interview_agent = Agent(
  name="interview-question-agent",
  model="gpt-5.4-nano",
  instructions=(
    "당신은 한국어 면접 코치입니다. 사용자가 면접 질문 생성을 요청하면"
    "반드시 make_interview_question 도구를 사용한 뒤 결과를 짧게 설명하세요."
  ),
  tools=[make_interview_question]
)

@function_tool
def tool_make_question(role_key: str, difficulty: str = "기초") -> str:
  """
  면접관 유형과 난이도를 받아 면접 질문 1개를 생성합니다.
  Args:
      role_key (str): 면접관 유형. tech, personality, executive, structured
      difficulty (str, optional): 질문 난이도. 기초 또는 심화
  """
  result = _make_question(role_key, difficulty)
  print(f" [tool-log] tool_make_question(role={role_key}, difficulty={difficulty})")
  return result

@function_tool
def tool_score_answer(answer: str) -> str:
  """지원자의 면접 답변을 채점합니다.
  Args:
    answer: 지원자의 면접 답변 텍스트
  """
  result = _score_answer(answer)
  print(f" [tool-log] tool_score_answer(len={len(answer)})")
  return result

@function_tool
def tool_make_feedback(answer: str) -> str:
    """지원자의 답변에 대해 다음 답변에서 개선할 행동을 제안합니다.
  Args:
    answer: 지원자의 면접 답변 텍스트
  """
    result = _make_feedback(answer)
    print(f" [tool-log] tool_make_feedback(len={len(answer)})")
    return result

# ======
# 3. Specialist Agent 정의
# ======

question_agent = Agent(
  name="질문출제 Specialist",
  model=MODEL_NAME,
  handoff_description="면접 질문 생성, 직무별 추천, 난이도별 질문 요청을 처리합니다.",
  instructions=(
    "당신은 한국어 면접 질문 출제 전문가입니다 "
    "사용자가 면접 질문을 요청하면 반드시 tool_make_question 도구를 사용하세요. "
    "질문 1개와 질문 의도를 짧게 설명합니다."
    "지원자 답변을 평가하거나 피드백하지 마세요."
  ),
  tools=[tool_make_question]
)

evaluation_agent = Agent(
    name="평가 Specialist",
    model=MODEL_NAME,
    handoff_description="면접 답변 평가, 답변 점검, 채점 요청을 처리합니다.",
    instructions=(
        "당신은 한국어 면접 답변 평가 전문가입니다 "
        "사용자가 답변 평가를 요청하면 반드시 tool_score_answer 도구를 사용하세요. "
        "강점 1개와 보완점 1개를 짧게 제시합니다."
        "새 면접 질문을 만들지 마세요."
    ),
    tools=[tool_score_answer],
)

feedback_agent = Agent(
    name="피드백 Specialist",
    model=MODEL_NAME,
    handoff_description="다변 개선 행동, 말히가 전략, 다음 다변 준비 요청을 처리합니다.",
    instructions=(
        "당신은 한국어 면접 답변 개선 전문가입니다 "
        "사용자가 피드백 요청하면 반드시 tool_make_feedback 도구를 사용하세요. "
        "다음 답변에서 바로 고칠 행동을 구체적으로 제안하세요."
        "점수 산정은 평가 Specialist에게 맡기세요."
    ),
    tools=[tool_score_answer],
)

# ======
# 4. TRIAGE AGENT (접수 담당)
# ======

triage_agent = Agent(
    name="면접 코치 Triage",
    model=MODEL_NAME,
    instructions=(
        "당신은 AI 면접 코치의 접수 담당입니다. "
        "사용자 요청을 읽고 가장 적합한 전문가에게 넘기세요. "
        "- 면접 질문 생성/추천 -> 질문출제 Specialist "
        "- 답변 평가/채점 -> 평가 Specialist"
        "- 다변 개선/피드백 -> 피드백 Specialist"
        "직접 긴 답변을 작성하지 말고 반드시 handoff하세요. "
        "한국어로 응답하세요."
    ),
    handoffs=[question_agent, evaluation_agent, feedback_agent],
    input_guardrails=[injection_guardrail]
)
