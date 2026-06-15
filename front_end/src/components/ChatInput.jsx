// src/components/ChatInput.jsx

import { useState } from "react";

export default function ChatInput({ disabled, onSubmit }) {
  const [value, setValue] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();

    const trimmed = value.trim();

    if (!trimmed || disabled) {
      return;
    }

    onSubmit(trimmed);
    setValue("");
  };

  return (
    <form className="mt-4 flex gap-2" onSubmit={handleSubmit}>
      <input
        className="flex-1 rounded border p-3"
        value={value}
        disabled={disabled}
        placeholder="면접 답변을 입력해 주세요."
        onChange={(event) => setValue(event.target.value)}
      />

      <button
        type="submit"
        disabled={disabled}
        className="rounded bg-black px-4 py-2 text-white disabled:bg-gray-400"
      >
        전송
      </button>
    </form>
  );
}