import { useState } from "react";
import {
  MODEL_OPTIONS,
  ROLE_PRESETS,
  MODE_OPTIONS,
} from "../config/defaultSettings";
import {
  getSettings,
  saveSettings,
  resetSettings,
} from "../utils/settingsStorage";

function SettingsPage() {
  const savedSettings = getSettings();
  const [selectedMode, setSelectedMode] = useState(
    savedSettings.mode || "single"
  );
  const [selectedModel, setSelectedModel] = useState(savedSettings.model);
  const [selectedTemperature, setSelectedTemperature] = useState(
    savedSettings.temperature
  );
  const [selectedRolePreset, setSelectedRolePreset] = useState(
    savedSettings.role_preset
  );
  const [selectedSystemPrompt, setSelectedSystemPrompt] = useState(
    savedSettings.system_prompt
  );

  const [savedMessage, setSavedMessage] = useState("");

  const handleSave = () => {
    const nextSettings = {
      model: selectedModel,
      temperature: Number(selectedTemperature),
      role_preset: selectedRolePreset,
      system_prompt: selectedSystemPrompt,
      mode: selectedMode,
    };

    saveSettings(nextSettings);

    setSavedMessage("설정을 저장했습니다.");

    setTimeout(() => {
      setSavedMessage("");
    }, 2000);
  };

  const handleReset = () => {
    const defaultSettings = resetSettings();

    setSelectedModel(defaultSettings.model);
    setSelectedTemperature(defaultSettings.temperature);
    setSelectedRolePreset(defaultSettings.role_preset);
    setSelectedSystemPrompt(defaultSettings.system_prompt);
    setSelectedMode(defaultSettings.mode);
    setSavedMessage("기본 설정으로 초기화했습니다.");

    setTimeout(() => {
      setSavedMessage("");
    }, 2000);
  };

  return (
    <section className="mx-auto max-w-4xl">
      <div className="mb-8">
        <p className="text-sm font-semibold text-blue-600">Settings</p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
          설정
        </h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-500">
          면접 코치 앱 전체에서 공유할 모델, temperature, system prompt,
          role preset 값을 관리합니다.
        </p>
      </div>
      <div>
  <label className="mb-2 block text-sm font-semibold text-slate-700">
    에이전트 모드
  </label>

    <div className="grid gap-3 sm:grid-cols-2">
      {Object.entries(MODE_OPTIONS).map(([modeValue, modeInfo]) => (
        <label
          key={modeValue}
          className={`cursor-pointer rounded-2xl border p-4 transition ${
            selectedMode === modeValue
              ? "border-blue-500 bg-blue-50 ring-4 ring-blue-100"
              : "border-slate-300 bg-white hover:bg-slate-50"
          }`}
        >
          <input
            type="radio"
            name="agentMode"
            value={modeValue}
            checked={selectedMode === modeValue}
            onChange={(event) => setSelectedMode(event.target.value)}
            className="sr-only"
          />

          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-slate-900">
                {modeInfo.label}
              </p>
              <p className="mt-1 text-xs leading-5 text-slate-500">
                {modeInfo.description}
              </p>
            </div>

            <span
              className={`flex h-5 w-5 items-center justify-center rounded-full border ${
                selectedMode === modeValue
                  ? "border-blue-600 bg-blue-600"
                  : "border-slate-300 bg-white"
              }`}
            >
              {selectedMode === modeValue && (
                <span className="h-2 w-2 rounded-full bg-white" />
              )}
            </span>
          </div>
        </label>
      ))}
    </div>

    <p className="mt-2 text-xs leading-5 text-slate-500">
      single은 interview_agent, multi는 triagent로 요청합니다.
    </p>
  </div>
      <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200 md:p-8">
        <div className="space-y-6">
          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700">
              모델 선택
            </label>

            <select
              value={selectedModel}
              onChange={(event) => setSelectedModel(event.target.value)}
              className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-800 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            >
              {MODEL_OPTIONS.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>

            <p className="mt-2 text-xs leading-5 text-slate-500">
              면접 에이전트가 사용할 모델을 선택합니다.
            </p>
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between">
              <label className="block text-sm font-semibold text-slate-700">
                답변 창의성
              </label>

              <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">
                {selectedTemperature}
              </span>
            </div>

            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={selectedTemperature}
              onChange={(event) =>
                setSelectedTemperature(Number(event.target.value))
              }
              className="w-full accent-blue-600"
            />

            <div className="mt-2 flex justify-between text-xs text-slate-500">
              <span>안정적</span>
              <span>창의적</span>
            </div>

            <p className="mt-2 text-xs leading-5 text-slate-500">
              낮을수록 안정적이고, 높을수록 창의적이지만 예측하기 어려워질 수
              있습니다.
            </p>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700">
              역할 선택
            </label>

            <select
              value={selectedRolePreset}
              onChange={(event) => setSelectedRolePreset(event.target.value)}
              className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-800 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            >
              {Object.keys(ROLE_PRESETS).map((roleName) => (
                <option key={roleName} value={roleName}>
                  {roleName}
                </option>
              ))}
            </select>

            <p className="mt-2 text-xs leading-5 text-slate-500">
              {ROLE_PRESETS[selectedRolePreset]}
            </p>
          </div>

          <div>
            <label className="mb-2 block text-sm font-semibold text-slate-700">
              시스템 프롬프트 편집
            </label>

            <textarea
              value={selectedSystemPrompt}
              onChange={(event) => setSelectedSystemPrompt(event.target.value)}
              rows={7}
              className="w-full resize-y rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm leading-6 text-slate-800 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-100"
            />

            <p className="mt-2 text-xs leading-5 text-slate-500">
              면접 에이전트의 기본 행동 방식을 정하는 프롬프트입니다.
            </p>
          </div>

          {savedMessage && (
            <div className="rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700 ring-1 ring-emerald-200">
              {savedMessage}
            </div>
          )}

          <div className="flex flex-col gap-3 pt-2 sm:flex-row">
            <button
              type="button"
              onClick={handleSave}
              className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
            >
              설정 저장
            </button>

            <button
              type="button"
              onClick={handleReset}
              className="inline-flex items-center justify-center rounded-xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              기본값으로 초기화
            </button>
          </div>
        </div>
      </div>

      <div className="mt-6 rounded-3xl bg-slate-900 p-6 text-white shadow-sm">
        <h2 className="text-lg font-bold">현재 입력 중인 설정</h2>

        <dl className="mt-4 space-y-3 text-sm">
          <div className="flex justify-between gap-4 border-b border-slate-700 pb-3">
            <dt className="text-slate-400">Model</dt>
            <dd className="text-right font-medium">{selectedModel}</dd>
          </div>
          <div className="flex justify-between gap-4 border-b border-slate-700 pb-3">
            <dt className="text-slate-400">Mode</dt>
            <dd className="text-right font-medium">{selectedMode}</dd>
          </div>
          <div className="flex justify-between gap-4 border-b border-slate-700 pb-3">
            <dt className="text-slate-400">Temperature</dt>
            <dd className="text-right font-medium">{selectedTemperature}</dd>
          </div>

          <div className="flex justify-between gap-4 border-b border-slate-700 pb-3">
            <dt className="text-slate-400">Role Preset</dt>
            <dd className="text-right font-medium">{selectedRolePreset}</dd>
          </div>

          <div className="gap-4">
            <dt className="mb-2 text-slate-400">System Prompt</dt>
            <dd className="rounded-2xl bg-slate-800 p-4 text-sm leading-6 text-slate-200">
              {selectedSystemPrompt}
            </dd>
          </div>
        </dl>
      </div>
    </section>
  );
}

export default SettingsPage;