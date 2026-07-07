// src/components/qa/ChatThread.jsx

export default function ChatThread({ messages, renderExtra }) {
  if (!messages.length) {
    return (
      <div className="rounded-2xl bg-slate-50 px-4 py-5 text-sm text-slate-500 ring-1 ring-slate-200">
        아직 대화가 없습니다. 아래에 질문을 입력해 보세요.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {messages.map((message, index) => {
        const isUser = message.role === "user";

        return (
          <div
            key={`${message.role}-${index}`}
            className={`flex ${isUser ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-3xl px-5 py-4 text-sm leading-6 shadow-sm ${
                isUser
                  ? "rounded-br-md bg-blue-600 text-white"
                  : "rounded-bl-md bg-white text-slate-800 ring-1 ring-slate-200"
              }`}
            >
              <div
                className={`mb-2 text-xs font-bold ${
                  isUser ? "text-blue-100" : "text-slate-400"
                }`}
              >
                {isUser ? "나" : "AI"}
              </div>

              <div className="whitespace-pre-wrap">{message.content}</div>

              {!isUser && renderExtra ? renderExtra(message) : null}
            </div>
          </div>
        );
      })}
    </div>
  );
}
