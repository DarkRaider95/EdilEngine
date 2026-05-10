"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import { CheckCircle2, MapPin, FileCheck, Gift, ClipboardList } from "lucide-react";
import type { GuideResponse } from "@/lib/types";

interface GuideResultProps {
  guide: GuideResponse;
}

export default function GuideResult({ guide }: GuideResultProps) {
  const [activeTab, setActiveTab] = useState<
    "vincoli" | "permessi" | "incentivi" | "checklist"
  >("checklist");

  const tabs = [
    {
      key: "checklist" as const,
      label: "Checklist",
      icon: ClipboardList,
      count: guide.checklist.length,
    },
    {
      key: "vincoli" as const,
      label: "Vincoli",
      icon: MapPin,
      count: guide.vincoli.length,
    },
    {
      key: "permessi" as const,
      label: "Permessi",
      icon: FileCheck,
      count: guide.permessi.length,
    },
    {
      key: "incentivi" as const,
      label: "Incentivi",
      icon: Gift,
      count: guide.incentivi.length,
    },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Markdown text */}
      {guide.markdown && (
        <Card>
          <div className="prose prose-slate max-w-none">
            <ReactMarkdown>{guide.markdown}</ReactMarkdown>
          </div>
        </Card>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-200 pb-2 overflow-x-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-4 py-2 rounded-t-lg text-sm font-medium transition-colors whitespace-nowrap
                ${
                  activeTab === tab.key
                    ? "bg-primary-50 text-primary-700 border-b-2 border-primary-600"
                    : "text-slate-500 hover:text-slate-700 hover:bg-slate-50"
                }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
              {tab.count > 0 && (
                <Badge variant="default" size="sm">
                  {tab.count}
                </Badge>
              )}
            </button>
          );
        })}
      </div>

      {/* Checklist */}
      {activeTab === "checklist" && (
        <div className="space-y-3">
          {guide.checklist.length === 0 ? (
            <p className="text-slate-500 text-sm italic">
              Nessun elemento nella checklist.
            </p>
          ) : (
            guide.checklist.map((item, i) => (
              <div
                key={i}
                className="flex items-start gap-3 p-4 bg-white rounded-lg border border-slate-200 hover:shadow-sm transition-shadow"
              >
                <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-slate-800">{item}</p>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Vincoli */}
      {activeTab === "vincoli" && (
        <div className="space-y-3">
          {guide.vincoli.length === 0 ? (
            <p className="text-slate-500 text-sm italic">
              Nessun vincolo territoriale rilevato.
            </p>
          ) : (
            guide.vincoli.map((v, i) => (
              <Card key={v.id || i}>
                <div className="flex items-start gap-3">
                  <MapPin className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-slate-900">
                      {v.comune && `${v.comune} (${v.provincia || ""})`}
                    </h4>
                    {v.tipo_zona && (
                      <Badge variant="warning" size="sm" className="mt-1">
                        {v.tipo_zona}
                      </Badge>
                    )}
                    {v.descrizione && (
                      <p className="text-sm text-slate-600 mt-2">
                        {v.descrizione}
                      </p>
                    )}
                    {v.norma_riferimento && (
                      <p className="text-xs text-slate-400 mt-1">
                        Norma: {v.norma_riferimento}
                      </p>
                    )}
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Permessi */}
      {activeTab === "permessi" && (
        <div className="space-y-3">
          {guide.permessi.length === 0 ? (
            <p className="text-slate-500 text-sm italic">
              Nessun permesso identificato.
            </p>
          ) : (
            guide.permessi.map((p, i) => (
              <Card key={i}>
                <div className="flex items-start gap-3">
                  <FileCheck className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm text-slate-700">
                      {typeof p === "string" ? p : JSON.stringify(p)}
                    </p>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Incentivi */}
      {activeTab === "incentivi" && (
        <div className="space-y-3">
          {guide.incentivi.length === 0 ? (
            <p className="text-slate-500 text-sm italic">
              Nessun incentivo applicabile identificato.
            </p>
          ) : (
            guide.incentivi.map((inc, i) => (
              <Card key={i}>
                <div className="flex items-start gap-3">
                  <Gift className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-slate-900">
                      {inc.titolo}
                    </h4>
                    {inc.aliquota !== null && (
                      <Badge variant="success" size="sm" className="mt-1">
                        {inc.aliquota}%
                      </Badge>
                    )}
                    {inc.descrizione && (
                      <p className="text-sm text-slate-600 mt-2">
                        {inc.descrizione}
                      </p>
                    )}
                    {inc.requisiti && (
                      <p className="text-xs text-slate-500 mt-1">
                        Requisiti: {inc.requisiti}
                      </p>
                    )}
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      )}
    </div>
  );
}
