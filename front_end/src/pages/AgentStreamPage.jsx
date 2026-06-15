// src/pages/AgentStreamPage.jsx

import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { getSettings } from "../utils/settingsStorage";

const BACKEND_URL =
  import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

const INITIAL_MESSAGES = [
  {
    role: "agent",
    content:
      "안녕하세요. AI 면접관입니다. 면접 연습을 시작하려면 답변이나 요청을 입력해 주세요.",
  },
];

async function streamAgentMessage({ message, settings, onToken, onStatus }) {
  const payload = {
    message,
    model: settings.model,
    temperature: settings.temperature,
    system_prompt: settings.system_prompt,
    role_preset: settings.role_preset,
    mode: settings.mode || "single",
  };

  const response = await fetch(`${BACKEND_URL}/agents/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`백엔드 오류 ${response.status}: ${errorText}`);
  }

  if (!response.body) {
    throw new Error("스트리밍 응답 body가 없습니다.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();

    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      const trimmed = line.trim();

      if (!trimmed || !trimmed.startsWith("data:")) {
        continue;
      }

      const rawData = trimmed.replace(/^data:\s*/, "");

      if (rawData === "[DONE]") {
        return;
      }

      let event;

      try {
        event = JSON.parse(rawData);
      } catch {
        onToken(rawData);
        continue;
      }

      if (event.type === "status") {
        onStatus(event.label);
        continue;
      }

      if (event.type === "token") {
        const delta = event.delta ?? "";

        if (
          typeof delta === "string" &&
          delta.trim().startsWith("{")
        ) {
          try {
            const nestedEvent = JSON.parse(delta);

            if (nestedEvent.type === "token") {
              onToken(nestedEvent.delta ?? "");
              continue;
            }
          } catch {
            // 중첩 JSON 파싱 실패 시 일반 문자열로 처리
          }
        }

        onToken(delta);
      }
    }
  }
}

function AgentStreamPage() {
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [inputValue, setInputValue] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [statusLabel, setStatusLabel] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const bottomRef = useRef(null);

  const settings = getSettings();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  const updateLastAgentMessage = (nextContent) => {
    setMessages((prevMessages) => {
      const copiedMessages = [...prevMessages];

      for (let i = copiedMessages.length - 1; i >= 0; i -= 1) {
        if (copiedMessages[i].role === "agent") {
          copiedMessages[i] = {
            ...copiedMessages[i],
            content: nextContent,
          };
          break;
        }
      }

      return copiedMessages;
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const userMessage = inputValue.trim();

    if (!userMessage || isStreaming) {
      return;
    }

    setInputValue("");
    setErrorMessage("");
    setStatusLabel("");
    setIsStreaming(true);

    setMessages((prevMessages) => [
      ...prevMessages,
      {
        role: "user",
        content: userMessage,
      },
      {
        role: "agent",
        content: "",
      },
    ]);

    let fullAnswer = "";

    try {
      await streamAgentMessage({
        message: userMessage,
        settings,
        onStatus: (label) => {
          setStatusLabel(label);
        },
        onToken: (token) => {
          fullAnswer += token;
          updateLastAgentMessage(fullAnswer);
        },
      });
    } catch (error) {
      console.error(error);

      const message =
        error instanceof Error
          ? error.message
          : "알 수 없는 오류가 발생했습니다.";

      setErrorMessage(message);

      updateLastAgentMessage(
        "응답을 생성하는 중 오류가 발생했습니다. FastAPI 서버와 /agents/stream 엔드포인트를 확인해 주세요."
      );
    } finally {
      setIsStreaming(false);
      setStatusLabel("");
    }
  };

  const handleClearMessages = () => {
    if (isStreaming) {
      return;
    }

    setMessages(INITIAL_MESSAGES);
    setErrorMessage("");
    setStatusLabel("");
  };

  return (
    <section className="mx-auto flex h-[calc(100vh-120px)] max-w-5xl flex-col">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-blue-600">Agent Stream</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
            면접 에이전트
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
            설정 페이지에서 저장한 값으로 AI 면접관과 메시지를 주고받습니다.
          </p>
        </div>

        <div className="flex gap-2">
          <Link
            to="/settings"
            className="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
          >
            설정 변경
          </Link>

          <button
            type="button"
            onClick={handleClearMessages}
            disabled={isStreaming}
            className="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            대화 초기화
          </button>
        </div>
      </div>

      <div className="mb-4 rounded-3xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
        <div className="grid gap-3 text-sm sm:grid-cols-4">
          <div>
            <p className="text-xs font-medium text-slate-400">Model</p>
            <p className="mt-1 font-semibold text-slate-800">
              {settings.model}
            </p>
          </div>

          <div>
            <p className="text-xs font-medium text-slate-400">Mode</p>
            <p className="mt-1 font-semibold text-slate-800">
              {settings.mode || "single"}
            </p>
          </div>

          <div>
            <p className="text-xs font-medium text-slate-400">Temperature</p>
            <p className="mt-1 font-semibold text-slate-800">
              {settings.temperature}
            </p>
          </div>

          <div>
            <p className="text-xs font-medium text-slate-400">Role</p>
            <p className="mt-1 font-semibold text-slate-800">
              {settings.role_preset}
            </p>
          </div>
        </div>
      </div>

      {errorMessage && (
        <div className="mb-4 rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-red-200">
          {errorMessage}
        </div>
      )}

      <div className="flex-1 overflow-y-auto rounded-3xl bg-slate-50 p-4 shadow-inner ring-1 ring-slate-200">
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
                    {isUser ? "나" : "AI 면접관"}
                  </div>

                  <div className="whitespace-pre-wrap">
                    {message.content}
                    {isStreaming &&
                      index === messages.length - 1 &&
                      message.role === "agent" && (
                        <span className="ml-1 animate-pulse">▌</span>
                      )}
                  </div>
                </div>
              </div>
            );
          })}

          {statusLabel && (
            <div className="text-center text-xs text-slate-400">
              상태: {statusLabel}
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      <form
        onSubmit={handleSubmit}
        className="mt-4 rounded-3xl bg-white p-3 shadow-sm ring-1 ring-slate-200"
      >
        <div className="flex gap-3">
          <textarea
            value={inputValue}
            onChange={(event) => setInputValue(event.target.value)}
            disabled={isStreaming}
            rows={1}
            placeholder="면접 답변이나 요청을 입력하세요."
            className="max-h-32 min-h-[48px] flex-1 resize-none rounded-2xl border border-slate-300 px-4 py-3 text-sm leading-6 text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 disabled:bg-slate-100"
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                event.currentTarget.form?.requestSubmit();
              }
            }}
          />

          <button
            type="submit"
            disabled={isStreaming || !inputValue.trim()}
            className="inline-flex min-w-20 items-center justify-center rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {isStreaming ? "응답 중" : "전송"}
          </button>
        </div>

        <p className="mt-2 px-2 text-xs text-slate-400">
          Enter로 전송하고, Shift + Enter로 줄바꿈할 수 있습니다.
        </p>
      </form>
    </section>
  );
}

export default AgentStreamPage;