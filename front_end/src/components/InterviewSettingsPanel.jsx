// src/components/InterviewSettingsPanel.jsx

const ROLE_PRESETS = ["기술 면접", "인성 면접", "임원 면접"];
const MODE_OPTIONS = ["single", "multi"];
const MODEL_OPTIONS = ["gpt-4o-mini", "gpt-5.4-nano"];

export default function InterviewSettingsPanel({
  settings,
  updateSettings,
  resetSettings,
}) {
  return (
    <section className="rounded border p-4">
      <h2 className="mb-3 text-lg font-bold">면접 설정</h2>

      <label className="mb-3 block">
        <span className="mb-1 block text-sm font-medium">모델</span>
        <select
          className="w-full rounded border p-2"
          value={settings.model}
          onChange={(event) =>
            updateSettings({ model: event.target.value })
          }
        >
          {MODEL_OPTIONS.map((model) => (
            <option key={model} value={model}>
              {model}
            </option>
          ))}
        </select>
      </label>

      <label className="mb-3 block">
        <span className="mb-1 block text-sm font-medium">
          답변 창의성: {settings.temperature}
        </span>
        <input
          className="w-full"
          type="range"
          min="0"
          max="2"
          step="0.1"
          value={settings.temperature}
          onChange={(event) =>
            updateSettings({
              temperature: Number(event.target.value),
            })
          }
        />
      </label>

      <label className="mb-3 block">
        <span className="mb-1 block text-sm font-medium">역할</span>
        <select
          className="w-full rounded border p-2"
          value={settings.role_preset}
          onChange={(event) =>
            updateSettings({ role_preset: event.target.value })
          }
        >
          {ROLE_PRESETS.map((role) => (
            <option key={role} value={role}>
              {role}
            </option>
          ))}
        </select>
      </label>

      <label className="mb-3 block">
        <span className="mb-1 block text-sm font-medium">모드</span>
        <select
          className="w-full rounded border p-2"
          value={settings.mode}
          onChange={(event) =>
            updateSettings({ mode: event.target.value })
          }
        >
          {MODE_OPTIONS.map((mode) => (
            <option key={mode} value={mode}>
              {mode}
            </option>
          ))}
        </select>
      </label>

      <label className="mb-3 block">
        <span className="mb-1 block text-sm font-medium">
          시스템 프롬프트
        </span>
        <textarea
          className="h-32 w-full rounded border p-2"
          value={settings.system_prompt}
          onChange={(event) =>
            updateSettings({ system_prompt: event.target.value })
          }
        />
      </label>

      <button
        type="button"
        className="rounded border px-3 py-2"
        onClick={resetSettings}
      >
        기본값으로 초기화
      </button>
    </section>
  );
}