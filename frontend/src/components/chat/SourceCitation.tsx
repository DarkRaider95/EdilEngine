"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, BookOpen, ExternalLink } from "lucide-react";

interface SourceCitationProps {
  sources: Record<string, unknown>;
}

export default function SourceCitation({ sources }: SourceCitationProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  // Estrai i chunks o array di riferimenti
  const sourceEntries = Object.entries(sources);
  const hasSources = sourceEntries.length > 0;

  if (!hasSources) return null;

  return (
    <div className="border border-primary-200 rounded-lg bg-primary-50/50 overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-3 text-sm font-medium text-primary-700 hover:bg-primary-50 transition-colors"
      >
        <span className="flex items-center gap-2">
          <BookOpen className="w-4 h-4" />
          Fonti normative ({sourceEntries.length})
        </span>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4" />
        ) : (
          <ChevronDown className="w-4 h-4" />
        )}
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 space-y-2 animate-fade-in">
          {sourceEntries.map(([key, value], index) => (
            <div key={index} className="text-xs text-slate-700">
              <span className="font-semibold text-primary-800">{key}:</span>{" "}
              {typeof value === "string" ? (
                value.startsWith("http") ? (
                  <a
                    href={value}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary-600 hover:text-primary-800 inline-flex items-center gap-1"
                  >
                    {value}
                    <ExternalLink className="w-3 h-3" />
                  </a>
                ) : (
                  value
                )
              ) : (
                JSON.stringify(value)
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
