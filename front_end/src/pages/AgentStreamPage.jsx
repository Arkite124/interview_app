import { useRef, useState } from "react";
import { streamAgentMessage } from "../api/agentStreamApi";

function AgentStreamPage() {
  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState("");
  const [statuses, setStatuses] = useState([]);
  const [errorMessage, setErrorMessage] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);

  const abortControllerRef = useRef(null);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!message.trim()) {
      setErrorMessage("에이전트에게 보낼 메시지를 입력하세요.");
      return;
    }

    setAnswer("");
    setStatuses([]);
    setErrorMessage("");
    setIsStreaming(true);

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    await streamAgentMessage({
      message,
      signal: abortController.signal,

      onToken: (delta) => {
        setAnswer((prev) => prev + delta);
      },

      onStatus: (label) => {
        setStatuses((prev) => [...prev, label]);
      },

      onDone: () => {
        setIsStreaming(false);
        abortControllerRef.current = null;
      },

      onError: (error) => {
        setErrorMessage(error.message);
        setIsStreaming(false);
        abortControllerRef.current = null;
      },
    });
  };

  const handleStop = () => {
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;
    setIsStreaming(false);
  };

  const handleReset = () => {
    handleStop();
    setMessage("");
    setAnswer("");
    setStatuses([]);
    setErrorMessage("");
  };

  return (
    <section className="mx-auto max-w-5xl">
      <div className="mb-8">
        <p className="text-sm font-semibold text-blue-600">Agent Stream</p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
          면접 에이전트 스트리밍
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
          FastAPI의 <code className="rounded bg-slate-100 px-1">/agents/stream</code>{" "}
          응답을 실시간으로 받아 화면에 출력합니다.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200 md:p-8">
          <form onSubmit={handleSubmit}>
            <label className="mb-2 block text-sm font-semibold text-slate-700">
              사용자 메시지
            </label>

            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              placeholder="예: 백엔드 신입 면접에서 자기소개를 어떻게 말하면 좋을까?"
              rows={6}
              disabled={isStreaming}
              className="w-full resize-y rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm leading-6 text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 disabled:bg-slate-100"
            />

            {errorMessage && (
              <div className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-red-200">
                {errorMessage}
              </div>
            )}

            <div className="mt-5 flex flex-col gap-3 sm:flex-row">
              <button
                type="submit"
                disabled={isStreaming}
                className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                {isStreaming ? "응답 생성 중..." : "에이전트에게 보내기"}
              </button>

              {isStreaming && (
                <button
                  type="button"
                  onClick={handleStop}
                  className="inline-flex items-center justify-center rounded-xl bg-red-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-red-700"
                >
                  중지
                </button>
              )}

              <button
                type="button"
                onClick={handleReset}
                className="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
              >
                초기화
              </button>
            </div>
          </form>

          <div className="mt-8">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-900">실시간 응답</h2>

              {isStreaming && (
                <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                  Streaming
                </span>
              )}
            </div>

            <div className="min-h-64 rounded-2xl bg-slate-950 p-5 text-sm leading-7 text-slate-100 ring-1 ring-slate-800">
              {answer ? (
                <pre className="whitespace-pre-wrap font-sans">{answer}</pre>
              ) : (
                <p className="text-slate-400">
                  아직 응답이 없습니다. 메시지를 보내면 토큰이 실시간으로 표시됩니다.
                </p>
              )}
            </div>
          </div>
        </div>

        <aside className="space-y-6">
          <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
            <h2 className="text-lg font-bold text-slate-900">상태 이벤트</h2>

            {statuses.length > 0 ? (
              <ul className="mt-4 space-y-2">
                {statuses.map((status, index) => (
                  <li
                    key={`${status}-${index}`}
                    className="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-700 ring-1 ring-slate-200"
                  >
                    {status}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-4 text-sm leading-6 text-slate-500">
                run_item, handoff_detected 같은 상태 이벤트가 여기에 표시됩니다.
              </p>
            )}
          </div>

          <div className="rounded-3xl bg-slate-900 p-6 text-white shadow-sm">
            <h2 className="text-lg font-bold">연결 방식</h2>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              POST 요청으로 메시지를 보내고, 응답 body를 ReadableStream으로 읽어서
              SSE의 data 라인을 직접 파싱합니다.
            </p>
          </div>
        </aside>
      </div>
    </section>
  );
}

export default AgentStreamPage;