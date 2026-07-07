// src/api/qaApi.js — backend/app.py (RAG QA / 채팅 / 구조화 평가 / 병렬 응답) 연동

import axios from "axios";

const BACKEND_URL =
  import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

const qaClient = axios.create({
  baseURL: BACKEND_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 60000,
});

function extractErrorMessage(error) {
  if (axios.isAxiosError(error)) {
    const backendMessage =
      error.response?.data?.detail || error.response?.data || error.message;

    return typeof backendMessage === "string"
      ? backendMessage
      : JSON.stringify(backendMessage);
  }

  return error instanceof Error
    ? error.message
    : "알 수 없는 오류가 발생했습니다.";
}

export async function requestRagAnswer(message) {
  try {
    const response = await qaClient.post("/rag", { message });
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error), { cause: error });
  }
}

export async function requestChatReply(message) {
  try {
    const response = await qaClient.post("/chat", { message });
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error), { cause: error });
  }
}

export async function requestStructuredEval({ question, answer }) {
  try {
    const response = await qaClient.post("/chat/structured", {
      question,
      answer,
    });
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error), { cause: error });
  }
}

export async function requestParallelAnswer(message) {
  try {
    const response = await qaClient.post("/chat/parallel", { message });
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error), { cause: error });
  }
}
