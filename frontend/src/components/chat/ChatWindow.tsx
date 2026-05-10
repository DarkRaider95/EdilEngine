"use client";

import { useRef, useEffect, useState } from "react";
import { Send } from "lucide-react";
import ChatMessage from "./ChatMessage";
import SourceCitation from "./SourceCitation";
import Spinner from "@/components/ui/Spinner";
import Button from "@/components/ui/Button";
import type { ChatMessageResponse } from "@/lib/types";

interface ChatWindowProps {
  messages: ChatMessageResponse[];
  streaming: boolean;
  streamingContent: string;
  sources: Record<string, unknown> | null;
  onSendMessage: (content: string) => void;
  loading: boolean;
  error: string | null;
}

export default function ChatWindow({
  messages,
  streaming,
  streamingContent,
  sources,
  onSendMessage,
  loading,
  error,
}: ChatWindowProps) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading || streaming) return;
    onSendMessage(trimmed);
    setInput("");
  };

  return (
    <div className="flex flex-col h-[calc(100vh-16rem)] bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !loading && !error && !streaming && (
          <div className="flex items-center justify-center h-full text-center">
            <div className="max-w-sm">
              <h3 className="text-lg font-semibold text-slate-700 mb-2">
                Benvenuto nel Chatbot EdilEngine
              </h3>
              <p className="text-sm text-slate-500">
                Puoi chiedermi qualsiasi cosa sulle leggi italiane
                dell&apos;edilizia. Cercherò di aiutarti con risposte basate
                sulle fonti normative.
              </p>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}

        {/* Streaming message */}
        {streaming && streamingContent && (
          <ChatMessage
            message={{
              id: "streaming",
              role: "assistant",
              content: streamingContent,
              sources: null,
              created_at: new Date().toISOString(),
            }}
            isStreaming
          />
        )}

        {/* Loading spinner (before first token) */}
        {loading && !streamingContent && !streaming && (
          <div className="flex justify-center py-4">
            <Spinner size="sm" label="Pensando..." />
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Sources after message is complete */}
        {sources && !streaming && (
          <SourceCitation sources={sources} />
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <form
        onSubmit={handleSubmit}
        className="border-t border-slate-200 p-4 bg-slate-50"
      >
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Scrivi un messaggio..."
            disabled={loading || streaming}
            className="flex-1 rounded-lg border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-slate-100"
            aria-label="Messaggio chat"
          />
          <Button
            type="submit"
            size="md"
            disabled={loading || streaming || !input.trim()}
            rightIcon={<Send size={16} />}
          >
            Invia
          </Button>
        </div>
      </form>
    </div>
  );
}
