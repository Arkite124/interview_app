// src/components/ChatMessageList.jsx

export default function ChatMessageList({ messages }) {
  if (!messages.length) {
    return (
      <div className="rounded border bg-gray-50 p-4 text-gray-600">
        원하는 면접 요구사항을 말씀하시면 시작하겠습니다.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {messages.map((message, index) => (
        <div
          key={`${message.role}-${index}`}
          className={
            message.role === "user"
              ? "ml-auto max-w-[80%] rounded bg-blue-100 p-3"
              : "mr-auto max-w-[80%] rounded bg-gray-100 p-3"
          }
        >
          <div className="mb-1 text-xs font-bold text-gray-500">
            {message.role === "user" ? "나" : "AI 면접관"}
          </div>
          <div className="whitespace-pre-wrap">{message.content}</div>
        </div>
      ))}
    </div>
  );
}