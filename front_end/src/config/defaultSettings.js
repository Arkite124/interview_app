export const DEFAULT_SETTINGS = {
  model: "gpt-5.4-nano",
  temperature: 0.7,
  system_prompt:
    "당신은 전문 면접관입니다. 지원자의 역량을 파악하는 심층 질문을 해주세요.",
  role_preset: "기술 면접",
  mode: "single",
};
export const ROLE_PRESETS = {
  "기술 면접": "기술 역량을 중심으로 질문합니다.",
  "인성 면접": "협업과 태도를 중심으로 질문합니다.",
  "임원 면접": "비전과 조직 기여도를 중심으로 질문합니다.",
};

export const MODEL_OPTIONS = ["gpt-4o-mini", "gpt-5.4-nano"];

export const MODE_OPTIONS = {
  single: {
    label: "Single Agent",
    description: "interview_agent 하나로 면접 응답을 생성합니다.",
  },
  multi: {
    label: "Multi Agent",
    description: "triage agent 구조로 여러 에이전트 흐름을 사용합니다.",
  },
};