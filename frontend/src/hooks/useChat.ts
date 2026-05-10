"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import {
  createChatSession,
  getChatHistory,
  sendChatMessageStream,
  ApiError,
} from "@/lib/api";
import type {
  ChatSessionResponse,
  ChatMessageResponse,
  SSEMessageEvent,
  SSEDoneEvent,
  SSEErrorEvent,
  SSERetrievalEvent,
} from "@/lib/types";

interface UseChatReturn {
  session: ChatSessionResponse | null;
  messages: ChatMessageResponse[];
  streaming: boolean;
  streamingContent: string;
  sources: Record<string, unknown> | null;
  loading: boolean;
  error: string | null;
  initSession: () => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  loadHistory: () => Promise<void>;
}

export function useChat(): UseChatReturn {
  const [session, setSession] = useState<ChatSessionResponse | null>(null);
  const [messages, setMessages] = useState<ChatMessageResponse[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [sources, setSources] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Initialize session on mount
  useEffect(() => {
    const savedSessionId = sessionStorage.getItem("edilengine_chat_session");
    if (savedSessionId) {
      setSession({
        id: "",
        session_id: savedSessionId,
        created_at: "",
      });
    }
  }, []);

  const initSession = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await createChatSession(
        typeof navigator !== "undefined" ? navigator.userAgent : undefined
      );
      setSession(response);
      sessionStorage.setItem("edilengine_chat_session", response.session_id);
      // Clear messages when starting a new session
      setMessages([]);
      setStreamingContent("");
      setSources(null);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Errore nella creazione della sessione");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const loadHistory = useCallback(async () => {
    if (!session?.session_id) return;
    try {
      const history = await getChatHistory(session.session_id);
      setMessages(history.messages);
    } catch (err) {
      // Silenzioso: la history potrebbe non esistere
    }
  }, [session?.session_id]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!session?.session_id) {
        // Auto-init session if not present
        setError("Sessione non inizializzata. Ricarica la pagina.");
        return;
      }

      setLoading(true);
      setError(null);
      setStreaming(true);
      setStreamingContent("");
      setSources(null);

      // Add user message to local state
      const userMsg: ChatMessageResponse = {
        id: `user-${Date.now()}`,
        role: "user",
        content,
        sources: null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);

      try {
        const stream = sendChatMessageStream(session.session_id, content);

        let fullContent = "";
        for await (const event of stream) {
          switch (event.type) {
            case "retrieval": {
              const retrieval = event as SSERetrievalEvent;
              console.debug(
                `Retrieved ${retrieval.retrieved_count} chunks`
              );
              break;
            }
            case "message": {
              const msg = event as SSEMessageEvent;
              fullContent += msg.content;
              setStreamingContent(fullContent);
              break;
            }
            case "done": {
              const done = event as SSEDoneEvent;
              setSources(done.sources || null);

              // Add assistant message to local state
              const assistantMsg: ChatMessageResponse = {
                id: `assistant-${Date.now()}`,
                role: "assistant",
                content: fullContent,
                sources: done.sources || null,
                created_at: new Date().toISOString(),
              };
              setMessages((prev) => [...prev, assistantMsg]);
              break;
            }
            case "error": {
              const err = event as SSEErrorEvent;
              setError(err.detail || "Errore durante la generazione");
              break;
            }
          }
        }
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError("Errore di connessione. Verifica che il backend sia attivo.");
        }
      } finally {
        setLoading(false);
        setStreaming(false);
        setStreamingContent("");
      }
    },
    [session?.session_id]
  );

  return {
    session,
    messages,
    streaming,
    streamingContent,
    sources,
    loading,
    error,
    initSession,
    sendMessage,
    loadHistory,
  };
}
