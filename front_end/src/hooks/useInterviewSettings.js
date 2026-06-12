// src/hooks/useInterviewSettings.js

import { useEffect, useState } from "react";

const DEFAULT_SETTINGS = {
  model: "gpt-5.4-nano",
  temperature: 0.7,
  system_prompt:
    "당신은 전문 면접관입니다. 지원자의 역량을 파악하는 심층 질문을 해주세요.",
  role_preset: "기술 면접",
  mode: "single",
};

const STORAGE_KEY = "interview_settings";

export function useInterviewSettings() {
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEY);

    if (!saved) {
      return DEFAULT_SETTINGS;
    }

    try {
      const parsed = JSON.parse(saved);

      return {
        ...DEFAULT_SETTINGS,
        ...parsed,
      };
    } catch {
      return DEFAULT_SETTINGS;
    }
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
  }, [settings]);

  const updateSettings = (nextSettings) => {
    setSettings((prev) => ({
      ...prev,
      ...nextSettings,
    }));
  };

  const resetSettings = () => {
    setSettings(DEFAULT_SETTINGS);
  };

  return {
    settings,
    updateSettings,
    resetSettings,
  };
}