// src/pages/qa/RagPage.jsx — 📚 RAG 사내 문서 QA (SSE 스트리밍)

import { useState } from "react";
import ChatThread from "../../components/qa/ChatThread";
import ChatComposer from "../../components/qa/ChatComposer";
import SourceList from "../../components/qa/SourceList";
import { streamRagAnswer } from "../../api/qaApi";

function updateLastAssistant(setMessages, updater) {
  setMessages((prev) => {
    const next = [...prev];
    for (let i = next.length - 1; i >= 0; i -= 1) {
      if (next[i].role === "assistant") {
        next[i] = updater(next[i]);
        break;
      }
    }
    return next;
  });
}

function RagPage() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (question) => {
    setErrorMessage("");
    setMessages((prev) => [
      ...prev,
      { role: "user", content: question },
      { role: "assistant", content: "", sources: [], attempts: 0 },
    ]);
    setIsLoading(true);

    let answer = "";

    await streamRagAnswer(question, {
      onToken: (delta) => {
        answer += delta;
        updateLastAssistant(setMessages, (msg) => ({ ...msg, content: answer }));
      },
      onSources: (sources) => {
        updateLastAssistant(setMessages, (msg) => ({ ...msg, sources }));
      },
      onResult: (result) => {
        updateLastAssistant(setMessages, (msg) => ({
          ...msg,
          attempts: result.attempts || 0,
        }));
      },
      onDone: () => {
        updateLastAssistant(setMessages, (msg) => ({
          ...msg,
          content: msg.content || "응답을 받지 못했습니다.",
        }));
      },
      onError: (error) => {
        setErrorMessage(error.message);
        updateLastAssistant(setMessages, (msg) => ({
          ...msg,
          content: msg.content || "⚠️ 오류가 발생했습니다. 백엔드 서버를 확인해 주세요.",
        }));
      },
    });

    setIsLoading(false);
  };

  const handleReset = () => {
    setMessages([]);
    setErrorMessage("");
  };

  return (
    <div className="flex h-[calc(100vh-260px)] flex-col">
      <div className="mb-4 flex items-center justify-between gap-4">
        <p className="text-sm leading-6 text-slate-500">
          사내 규정 문서를 기반으로 질문에 답합니다. 예: 휴가 신청 절차는?
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
          renderExtra={(message) => (
            <>
              <SourceList sources={message.sources} />
              {message.attempts > 0 && (
                <p className="mt-2 text-xs text-slate-400">
                  🔄 재검색 {message.attempts}회 수행
                </p>
              )}
            </>
          )}
        />

        {isLoading && (
          <p className="mt-3 text-center text-xs text-slate-400">
            🔍 사내 문서 검색 중...
          </p>
        )}
      </div>

      <div className="mt-4">
        <ChatComposer
          onSubmit={handleSubmit}
          disabled={isLoading}
          placeholder="질문을 입력하세요..."
        />
      </div>
    </div>
  );
}

export default RagPage;
