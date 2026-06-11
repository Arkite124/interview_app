function getBackendUrl() {
  return (
    localStorage.getItem("backendUrl") ||
    import.meta.env.VITE_BACKEND_URL ||
    "http://localhost:8000"
  );
}

export async function streamAgentMessage({
  message,
  role,
  temperature,
  onToken,
  onStatus,
  onDone,
  onError,
  signal,
}) {
  try {
    const response = await fetch(`${getBackendUrl()}/agents/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({
        message,
        role,
        temperature: Number(temperature),
      }),
      signal,
    });

    if (!response.ok) {
      throw new Error("에이전트 스트리밍 요청에 실패했습니다.");
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
        break;
      }

      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const rawLine of lines) {
        const line = rawLine.trim();

        if (!line) continue;
        if (!line.startsWith("data:")) continue;

        const data = line.slice(5).trim();

        if (data === "[DONE]") {
          onDone?.();
          return;
        }

        try {
          const event = JSON.parse(data);

          if (event.type === "token") {
            onToken?.(event.delta || "");
          }

          if (event.type === "status") {
            onStatus?.(event.label || "");
          }
        } catch {
          console.warn("SSE JSON 파싱 실패:", data);
        }
      }
    }
  } catch (error) {
    if (error.name === "AbortError") {
      return;
    }

    onError?.(error);
  }
}