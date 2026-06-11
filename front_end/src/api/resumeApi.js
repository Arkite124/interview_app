const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export async function analyzeResume(resumeText) {
  const response = await fetch(`${BACKEND_URL}/resume/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      resume_text: resumeText,
    }),
  });

  if (!response.ok) {
    throw new Error("자소서 첨삭 요청에 실패했습니다.");
  }

  return response.json();
}