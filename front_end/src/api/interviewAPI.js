// src/api/interviewApi.js

const BACKEND_URL =
  import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export async function streamInterviewMessage({
  message,
  settings,
  onToken,
  onStatus,
}) {
  const payload = {
    message,
    model: settings.model,
    temperature: settings.temperature,
    system_prompt: settings.system_prompt,
    role_preset: settings.role_preset,
    mode: settings.mode,
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
        onToken?.(rawData);
        continue;
      }

      if (event.type === "status") {
        onStatus?.(event.label);
        continue;
      }

      if (event.type === "token") {
        const delta = event.delta ?? "";

        // Streamlit 코드에 있던 중첩 JSON 방어 로직 반영
        if (
          typeof delta === "string" &&
          delta.trim().startsWith("{")
        ) {
          try {
            const nestedEvent = JSON.parse(delta);

            if (nestedEvent.type === "token") {
              onToken?.(nestedEvent.delta ?? "");
              continue;
            }
          } catch {
            // 그냥 일반 문자열로 처리
          }
        }

        onToken?.(delta);
      }
    }
  }
}