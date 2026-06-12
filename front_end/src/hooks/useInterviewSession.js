// src/hooks/useInterviewSession.js

import { useEffect, useMemo, useState } from "react";

const STORAGE_KEY = "interview_conversations";

function createFirstState() {
  const firstId = crypto.randomUUID();

  return {
    currentSessionId: firstId,
    conversations: {
      [firstId]: {
        title: "면접 세션 1",
        messages: [],
      },
    },
  };
}

export function useInterviewSession() {
  const [state, setState] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEY);

    if (!saved) {
      return createFirstState();
    }

    try {
      const parsed = JSON.parse(saved);

      if (!parsed.currentSessionId || !parsed.conversations) {
        return createFirstState();
      }

      return parsed;
    } catch {
      return createFirstState();
    }
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state]);

  const currentSession = useMemo(() => {
    return state.conversations[state.currentSessionId] ?? null;
  }, [state]);

  const addMessage = (message) => {
    setState((prev) => {
      const current = prev.conversations[prev.currentSessionId];

      return {
        ...prev,
        conversations: {
          ...prev.conversations,
          [prev.currentSessionId]: {
            ...current,
            messages: [...current.messages, message],
          },
        },
      };
    });
  };

  const updateLastAssistantMessage = (content) => {
    setState((prev) => {
      const current = prev.conversations[prev.currentSessionId];
      const messages = [...current.messages];

      for (let i = messages.length - 1; i >= 0; i -= 1) {
        if (messages[i].role === "assistant") {
          messages[i] = {
            ...messages[i],
            content,
          };
          break;
        }
      }

      return {
        ...prev,
        conversations: {
          ...prev.conversations,
          [prev.currentSessionId]: {
            ...current,
            messages,
          },
        },
      };
    });
  };

  const addNewSession = () => {
    setState((prev) => {
      const newId = crypto.randomUUID();
      const sessionCount = Object.keys(prev.conversations).length + 1;

      return {
        currentSessionId: newId,
        conversations: {
          ...prev.conversations,
          [newId]: {
            title: `면접 세션 ${sessionCount}`,
            messages: [],
          },
        },
      };
    });
  };

  const deleteCurrentSession = () => {
    setState((prev) => {
      const entries = Object.entries(prev.conversations);

      if (entries.length === 1) {
        const onlyId = prev.currentSessionId;

        return {
          currentSessionId: onlyId,
          conversations: {
            [onlyId]: {
              title: "면접 세션 1",
              messages: [],
            },
          },
        };
      }

      const nextConversations = { ...prev.conversations };
      delete nextConversations[prev.currentSessionId];

      const nextSessionId = Object.keys(nextConversations)[0];

      return {
        currentSessionId: nextSessionId,
        conversations: nextConversations,
      };
    });
  };

  const selectSession = (sessionId) => {
    setState((prev) => ({
      ...prev,
      currentSessionId: sessionId,
    }));
  };

  return {
    conversations: state.conversations,
    currentSessionId: state.currentSessionId,
    currentSession,
    addMessage,
    updateLastAssistantMessage,
    addNewSession,
    deleteCurrentSession,
    selectSession,
  };
}