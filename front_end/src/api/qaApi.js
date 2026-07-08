// src/api/qaApi.js — backend/app.py (RAG QA / 채팅 / 구조화 평가 / 병렬 응답) 연동
//
// 모든 함수는 backend의 `*/stream` SSE 엔드포인트를 호출한다. 이벤트 계약은
// backend/sse.py와 동일하다:
//   {"type": "status", "label": string}      — 진행 상태 안내
//   {"type": "token", "delta": string}       — 텍스트 조각 (누적 시 전체 답변)
//   {"type": "sources", "content": [...]}    — RAG 출처 목록
//   {"type": "result", "content": {...}}     — 구조화/부가 결과 (score, faq 등)
//   {"type": "done"}                         — 스트림 종료

const BACKEND_URL =
  import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

async function streamSse(
  path,
  { method = "POST", body, params } = {},
  { onStatus, onToken, onSources, onResult, onDone, onError, signal } = {}
) {
  try {
    const url = new URL(`${BACKEND_URL}${path}`);

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.set(key, value);
      });
    }

    const response = await fetch(url.toString(), {
      method,
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: body ? JSON.stringify(body) : undefined,
      signal,
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`백엔드 오류 ${response.status}: ${errorText}`);
    }

    if (!response.body) {
      throw new Error("브라우저가 스트리밍 응답을 지원하지 않습니다.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();

      if (done) {
        onDone?.();
        return;
      }

      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const rawLine of lines) {
        const line = rawLine.trim();

        if (!line || !line.startsWith("data:")) continue;

        const data = line.slice(5).trim();
        if (!data) continue;

        let event;
        try {
          event = JSON.parse(data);
        } catch {
          console.warn("SSE JSON 파싱 실패:", data);
          continue;
        }

        if (event.type === "status") onStatus?.(event.label || "");
        if (event.type === "token") onToken?.(event.delta || "");
        if (event.type === "sources") onSources?.(event.content || []);
        if (event.type === "result") onResult?.(event.content || {});

        if (event.type === "done") {
          onDone?.();
          return;
        }
      }
    }
  } catch (error) {
    if (error.name === "AbortError") return;
    onError?.(error);
  }
}

export function streamRagAnswer(message, handlers, signal) {
  return streamSse(
    "/rag/stream",
    { method: "GET", params: { message } },
    { ...handlers, signal }
  );
}

export function streamChatReply(message, handlers, signal) {
  return streamSse(
    "/chat/stream",
    { method: "POST", body: { message } },
    { ...handlers, signal }
  );
}

export function streamStructuredEval({ question, answer }, handlers, signal) {
  return streamSse(
    "/chat/structured/stream",
    { method: "POST", body: { question, answer } },
    { ...handlers, signal }
  );
}

export function streamParallelAnswer(message, handlers, signal) {
  return streamSse(
    "/chat/parallel/stream",
    { method: "POST", body: { message } },
    { ...handlers, signal }
  );
}
