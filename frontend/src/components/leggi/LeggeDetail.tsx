"use client";

import Link from "next/link";
import { ExternalLink, Calendar, FileText, Building2, Tag } from "lucide-react";
import Badge, { leggeTipoToVariant } from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { formatDate } from "@/lib/utils";
import type { LeggeDetail } from "@/lib/types";

interface LeggeDetailViewProps {
  legge: LeggeDetail;
}

export default function LeggeDetailView({ legge }: LeggeDetailViewProps) {
  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          {legge.tipo && (
            <Badge variant={leggeTipoToVariant(legge.tipo)} size="md">
              {legge.tipo}
            </Badge>
          )}
          {legge.categorie.map((cat) => (
            <Badge key={cat.id} variant="info" size="sm">
              {cat.nome}
            </Badge>
          ))}
        </div>

        <h1 className="text-3xl lg:text-4xl font-bold text-slate-900 leading-tight mb-6">
          {legge.titolo}
        </h1>

        {/* Metadata */}
        <Card className="mb-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {legge.numero && (
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">
                  Numero
                </p>
                <p className="text-sm font-medium text-slate-900 flex items-center gap-1.5">
                  <FileText className="w-4 h-4 text-slate-400" />
                  n. {legge.numero}
                </p>
              </div>
            )}
            {legge.data_emanazione && (
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">
                  Emanazione
                </p>
                <p className="text-sm font-medium text-slate-900 flex items-center gap-1.5">
                  <Calendar className="w-4 h-4 text-slate-400" />
                  {formatDate(legge.data_emanazione)}
                </p>
              </div>
            )}
            {legge.data_pubblicazione && (
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">
                  Pubblicazione
                </p>
                <p className="text-sm font-medium text-slate-900 flex items-center gap-1.5">
                  <Calendar className="w-4 h-4 text-slate-400" />
                  {formatDate(legge.data_pubblicazione)}
                </p>
              </div>
            )}
            {legge.data_vigore && (
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">
                  In vigore dal
                </p>
                <p className="text-sm font-medium text-slate-900 flex items-center gap-1.5">
                  <Calendar className="w-4 h-4 text-slate-400" />
                  {formatDate(legge.data_vigore)}
                </p>
              </div>
            )}
            {legge.autorita && (
              <div>
                <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">
                  Autorità
                </p>
                <p className="text-sm font-medium text-slate-900 flex items-center gap-1.5">
                  <Building2 className="w-4 h-4 text-slate-400" />
                  {legge.autorita}
                </p>
              </div>
            )}
          </div>
        </Card>

        {/* Categorie */}
        {legge.categorie.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider mb-3">
              <Tag className="w-4 h-4 inline mr-1" />
              Categorie
            </h3>
            <div className="flex flex-wrap gap-2">
              {legge.categorie.map((cat) => (
                <Badge key={cat.id} variant="info" size="md">
                  {cat.nome}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Fonte */}
        {legge.url_fonte && (
          <div className="mb-8">
            <a
              href={legge.url_fonte}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm text-primary-600 hover:text-primary-800"
            >
              <ExternalLink className="w-4 h-4" />
              Vai alla fonte originale (Gazzetta Ufficiale)
            </a>
          </div>
        )}
      </div>

      {/* Testo completo */}
      {legge.testo_completo ? (
        <Card>
          <div className="prose prose-slate max-w-none">
            {legge.testo_completo.split("\n").map((line, i) => (
              <p key={i} className="mb-2">
                {line || "\u00A0"}
              </p>
            ))}
          </div>
        </Card>
      ) : (
        <Card>
          <p className="text-slate-500 italic">
            Testo completo non disponibile per questa legge.
          </p>
        </Card>
      )}

      {/* Chatbot CTA */}
      <div className="mt-8 p-6 bg-primary-50 rounded-xl border border-primary-200">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-primary-900">
              Hai domande su questa legge?
            </h3>
            <p className="text-sm text-primary-700">
              Chiedi al nostro chatbot AI per chiarimenti e approfondimenti.
            </p>
          </div>
          <Link href={`/chat?q=${encodeURIComponent(legge.titolo || '')}`}>
            <Button variant="primary" size="md">
              Chiedi al chatbot
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
