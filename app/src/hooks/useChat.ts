// ============================================================
// EdilEngine - Hook useChat
// ============================================================

import { useState, useCallback, useEffect } from 'react';
import {
  createChatSession,
  getChatHistory,
  sendChatMessageStream,
  ApiError,
} from '../services/api';
import type {
  ChatSessionResponse,
  ChatMessageResponse,
  SSEMessageEvent,
  SSEDoneEvent,
  SSEErrorEvent,
  SSERetrievalEvent,
} from '../services/types';
import { getChatSessionId, setChatSessionId } from '../utils/storage';

export interface UseChatReturn {
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
  const [streamingContent, setStreamingContent] = useState('');
  const [sources, setSources] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Restore session from storage on mount
  useEffect(() => {
    const restoreSession = async () => {
      const savedSessionId = await getChatSessionId();
      if (savedSessionId) {
        setSession({
          id: '',
          session_id: savedSessionId,
          created_at: '',
        });
      }
    };
    restoreSession();
  }, []);

  const initSession = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await createChatSession();
      setSession(response);
      await setChatSessionId(response.session_id);
      setMessages([]);
      setStreamingContent('');
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
    } catch {
      // Silenzioso: la history potrebbe non esistere
    }
  }, [session?.session_id]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!session?.session_id) {
        setError('Sessione non inizializzata. Avvia una nuova chat.');
        return;
      }

      setLoading(true);
      setError(null);
      setStreaming(true);
      setStreamingContent('');
      setSources(null);

      const userMsg: ChatMessageResponse = {
        id: `user-${Date.now()}`,
        role: 'user',
        content,
        sources: null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);

      try {
        const stream = sendChatMessageStream(session.session_id, content);

        let fullContent = '';
        for await (const event of stream) {
          switch (event.type) {
            case 'retrieval': {
              const retrieval = event as SSERetrievalEvent;
              console.debug(`Retrieved ${retrieval.retrieved_count} chunks`);
              break;
            }
            case 'message': {
              const msg = event as SSEMessageEvent;
              fullContent += msg.content;
              setStreamingContent(fullContent);
              break;
            }
            case 'done': {
              const done = event as SSEDoneEvent;
              setSources(done.sources || null);

              const assistantMsg: ChatMessageResponse = {
                id: `assistant-${Date.now()}`,
                role: 'assistant',
                content: fullContent,
                sources: done.sources || null,
                created_at: new Date().toISOString(),
              };
              setMessages((prev) => [...prev, assistantMsg]);
              break;
            }
            case 'error': {
              const err = event as SSEErrorEvent;
              setError(err.detail || 'Errore durante la generazione');
              break;
            }
          }
        }
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError('Errore di connessione. Verifica che il backend sia attivo.');
        }
      } finally {
        setLoading(false);
        setStreaming(false);
        setStreamingContent('');
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
