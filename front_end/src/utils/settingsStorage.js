import { DEFAULT_SETTINGS } from "../config/defaultSettings";

const SETTINGS_KEY = "settings";

export function getSettings() {
  const savedSettings = localStorage.getItem(SETTINGS_KEY);

  if (!savedSettings) {
    return { ...DEFAULT_SETTINGS };
  }

  try {
    return {
      ...DEFAULT_SETTINGS,
      ...JSON.parse(savedSettings),
    };
  } catch {
    return { ...DEFAULT_SETTINGS };
  }
}

export function saveSettings(settings) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

export function resetSettings() {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(DEFAULT_SETTINGS));
  return { ...DEFAULT_SETTINGS };
}