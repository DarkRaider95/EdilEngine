"use client";

import { User, Bot } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ChatMessageResponse } from "@/lib/types";

interface ChatMessageProps {
  message: ChatMessageResponse;
  isStreaming?: boolean;
}

export default function ChatMessage({
  message,
  isStreaming = false,
}: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-3 animate-fade-in",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {/* Avatar (only for assistant) */}
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
          <Bot className="w-4 h-4 text-primary-600" />
        </div>
      )}

      {/* Bubble */}
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-3",
          isUser
            ? "bg-primary-600 text-white rounded-br-md"
            : "bg-slate-100 text-slate-900 rounded-bl-md"
        )}
      >
        <div
          className={cn(
            "text-sm leading-relaxed whitespace-pre-wrap break-words",
            isStreaming && "streaming-cursor"
          )}
        >
          {message.content || ""}
          {isStreaming && (
            <span className="inline-block w-2 h-4 bg-slate-500 ml-0.5 animate-pulse rounded-sm" />
          )}
        </div>
        {!isStreaming && message.created_at && (
          <p
            className={cn(
              "text-xs mt-2",
              isUser ? "text-primary-200" : "text-slate-400"
            )}
          >
            {new Date(message.created_at).toLocaleTimeString("it-IT", {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </p>
        )}
      </div>

      {/* Avatar (only for user) */}
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
          <User className="w-4 h-4 text-green-600" />
        </div>
      )}
    </div>
  );
}
