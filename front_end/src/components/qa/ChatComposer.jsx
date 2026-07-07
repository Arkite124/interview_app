// src/components/qa/ChatComposer.jsx — Enter 전송 / Shift+Enter 줄바꿈 입력창

import { useState } from "react";

export default function ChatComposer({
  onSubmit,
  disabled,
  placeholder,
  submitLabel = "전송",
}) {
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
    <form
      onSubmit={handleSubmit}
      className="rounded-3xl bg-white p-3 shadow-sm ring-1 ring-slate-200"
    >
      <div className="flex gap-3">
        <textarea
          value={value}
          onChange={(event) => setValue(event.target.value)}
          disabled={disabled}
          rows={1}
          placeholder={placeholder}
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
          disabled={disabled || !value.trim()}
          className="inline-flex min-w-20 items-center justify-center rounded-2xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {disabled ? "응답 중" : submitLabel}
        </button>
      </div>

      <p className="mt-2 px-2 text-xs text-slate-400">
        Enter로 전송하고, Shift + Enter로 줄바꿈할 수 있습니다.
      </p>
    </form>
  );
}
