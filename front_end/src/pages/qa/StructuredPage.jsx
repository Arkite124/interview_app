// src/pages/qa/StructuredPage.jsx — 📊 면접 답변 구조화 평가 (입력 형식: 질문 | 답변)

import { useState } from "react";
import ChatThread from "../../components/qa/ChatThread";
import ChatComposer from "../../components/qa/ChatComposer";
import { requestStructuredEval } from "../../api/qaApi";

const SCORE_EMOJI = ["", "😟", "🤔", "😐", "😊", "🌟"];

function ScoreCard({ score, strengths, improvements, nextQuestion }) {
  return (
    <div className="mt-3 grid gap-3 rounded-xl bg-slate-50 p-3 text-xs ring-1 ring-slate-200 sm:grid-cols-[auto_1fr]">
      <div className="flex items-center justify-center rounded-lg bg-blue-50 px-4 py-2 text-sm font-bold text-blue-700">
        {score}/5 {SCORE_EMOJI[score] || ""}
      </div>

      <div className="space-y-1 text-slate-600">
        <p>
          <span className="font-semibold text-slate-700">💪 강점:</span>{" "}
          {strengths}
        </p>
        <p>
          <span className="font-semibold text-slate-700">📝 개선점:</span>{" "}
          {improvements}
        </p>
        <p>
          <span className="font-semibold text-slate-700">❓ 후속 질문:</span>{" "}
          {nextQuestion}
        </p>
      </div>
    </div>
  );
}

function parseQuestionAnswer(rawInput) {
  const separatorIndex = rawInput.indexOf("|");

  if (separatorIndex === -1) {
    return { question: "자기소개를 해주세요", answer: rawInput.trim() };
  }

  return {
    question: rawInput.slice(0, separatorIndex).trim(),
    answer: rawInput.slice(separatorIndex + 1).trim(),
  };
}

function StructuredPage() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (rawInput) => {
    setErrorMessage("");
    setMessages((prev) => [...prev, { role: "user", content: rawInput }]);
    setIsLoading(true);

    const { question, answer } = parseQuestionAnswer(rawInput);

    try {
      const data = await requestStructuredEval({ question, answer });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `"${question}"에 대한 평가 결과입니다.`,
          score: data.score ?? 0,
          strengths: data.strengths ?? "-",
          improvements: data.improvements ?? "-",
          nextQuestion: data.next_question ?? "-",
        },
      ]);
    } catch (error) {
      setErrorMessage(error.message);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "⚠️ 오류가 발생했습니다. 백엔드 서버를 확인해 주세요.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setMessages([]);
    setErrorMessage("");
  };

  return (
    <div className="flex h-[calc(100vh-260px)] flex-col">
      <div className="mb-4 flex items-center justify-between gap-4">
        <p className="text-sm leading-6 text-slate-500">
          면접 답변을 점수/강점/개선점으로 구조화 평가합니다. 형식:{" "}
          <code className="rounded bg-slate-100 px-1.5 py-0.5">
            질문 | 답변
          </code>
        </p>

        <button
          type="button"
          onClick={handleReset}
          disabled={isLoading}
          className="inline-flex shrink-0 items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
        >
          🗑️ 대화 초기화
        </button>
      </div>

      {errorMessage && (
        <div className="mb-4 rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-red-200">
          {errorMessage}
        </div>
      )}

      <div className="flex-1 overflow-y-auto rounded-3xl bg-slate-50 p-4 shadow-inner ring-1 ring-slate-200">
        <ChatThread
          messages={messages}
          renderExtra={(message) =>
            message.score !== undefined ? (
              <ScoreCard
                score={message.score}
                strengths={message.strengths}
                improvements={message.improvements}
                nextQuestion={message.nextQuestion}
              />
            ) : null
          }
        />
      </div>

      <div className="mt-4">
        <ChatComposer
          onSubmit={handleSubmit}
          disabled={isLoading}
          placeholder="질문 | 답변 형식으로 입력하세요..."
        />
      </div>
    </div>
  );
}

export default StructuredPage;
