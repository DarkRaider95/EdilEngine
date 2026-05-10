"use client";

import { useEffect } from "react";
import { useSearchParams } from "next/navigation";
import ChatWindow from "@/components/chat/ChatWindow";
import Button from "@/components/ui/Button";
import { useChat } from "@/hooks/useChat";
import { MessageCircle, Plus } from "lucide-react";

export default function ChatPage() {
  const searchParams = useSearchParams();
  const {
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
  } = useChat();

  // Initialize session on mount
  useEffect(() => {
    if (!session?.session_id) {
      initSession();
    } else {
      loadHistory();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // If there's a pre-filled query from another page, send it
  useEffect(() => {
    const q = searchParams.get("q");
    if (q && session?.session_id && messages.length === 0 && !loading) {
      sendMessage(q);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.session_id, messages.length]);

  const handleNewSession = () => {
    initSession();
  };

  return (
    <div className="container-wide py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2.5">
            <MessageCircle className="w-6 h-6 text-primary-600" />
            Chatbot Normativo
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Assistente AI con accesso alle fonti normative per risposte
            affidabili.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleNewSession}
          leftIcon={<Plus size={16} />}
        >
          Nuova chat
        </Button>
      </div>

      {/* Session info */}
      {session?.session_id && (
        <p className="text-xs text-slate-400 mb-4">
          Sessione: {session.session_id.slice(0, 8)}...
        </p>
      )}

      {/* Chat Window */}
      <ChatWindow
        messages={messages}
        streaming={streaming}
        streamingContent={streamingContent}
        sources={sources}
        onSendMessage={sendMessage}
        loading={loading}
        error={error}
      />
    </div>
  );
}
