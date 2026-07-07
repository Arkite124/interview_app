// src/pages/qa/ChatPage.jsx — 💬 기본 면접 코치 채팅

import { useState } from "react";
import ChatThread from "../../components/qa/ChatThread";
import ChatComposer from "../../components/qa/ChatComposer";
import { requestChatReply } from "../../api/qaApi";

function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (question) => {
    setErrorMessage("");
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setIsLoading(true);

    try {
      const data = await requestChatReply(question);

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply || "응답을 받지 못했습니다." },
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
          면접 코치로서 자유 질문에 답합니다.
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
        <ChatThread messages={messages} />
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

export default ChatPage;
