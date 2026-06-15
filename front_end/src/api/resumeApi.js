// src/api/resumeApi.js

import axios from "axios";
import { getSettings } from "../utils/settingsStorage";

const BACKEND_URL =
  import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

const resumeClient = axios.create({
  baseURL: BACKEND_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

export async function requestResumeQuestions({
  resumeText,
  questionCount,
}) {
  const settings = getSettings();

  const requestBody = {
    input: resumeText.trim(),
    question_count: Number(questionCount),
    role_preset: settings.role_preset || "기술 면접",
  };

  console.log("files/analyze 요청 body:", requestBody);

  try {
    const response = await resumeClient.post("/files/analyze", requestBody);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error("files/analyze axios 오류:", {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
      });

      const backendMessage =
        error.response?.data?.detail ||
        error.response?.data ||
        error.message;

      throw new Error(
        typeof backendMessage === "string"
          ? backendMessage
          : JSON.stringify(backendMessage)
      );
    }

    throw error;
  }
}