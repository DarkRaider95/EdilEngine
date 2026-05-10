"use client";

import { useEffect, useState } from "react";
import { useParams, notFound } from "next/navigation";
import Link from "next/link";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Spinner from "@/components/ui/Spinner";
import { formatDate, formatAliquota } from "@/lib/utils";
import {
  Calendar,
  Building2,
  Percent,
  ExternalLink,
  FileText,
} from "lucide-react";
import { getIncentivo, getIncentivi } from "@/lib/api";
import type { IncentivoDetail } from "@/lib/types";

export default function IncentivoDetailPage() {
  const params = useParams<{ id: string }>();
  const id = decodeURIComponent(params.id);

  const [incentivo, setIncentivo] = useState<IncentivoDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadIncentivo();
  }, [id]);

  async function loadIncentivo() {
    setLoading(true);
    setError(null);
    try {
      // Prima prova: assumiamo sia un UUID
      const detail = await getIncentivo(id);
      setIncentivo(detail);
    } catch {
      // Seconda prova: cerchiamo per titolo
      try {
        const listResult = await getIncentivi({
          page: 1,
          page_size: 5,
        });
        const match = listResult.items.find(
          (item) =>
            item.titolo === id ||
            encodeURIComponent(item.titolo) === id
        );
        if (match && match.id) {
          const detail = await getIncentivo(match.id);
          setIncentivo(detail);
          return;
        }
        setError("Incentivo non trovato. Prova a cercarlo dalla lista incentivi.");
      } catch {
        setError("Errore nel caricamento dell'incentivo.");
      }
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="container-page py-20 flex justify-center">
        <Spinner size="lg" label="Caricamento incentivo..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container-page py-20">
        <Card>
          <div className="text-center py-8">
            <p className="text-red-600 mb-4">{error}</p>
            <Link href="/incentivi" className="text-primary-600 hover:text-primary-800 text-sm">
              Vai alla lista incentivi
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  if (!incentivo) {
    notFound();
  }

  return (
    <div className="container-page py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            {incentivo.tipo && (
              <Badge variant="success" size="md">
                {incentivo.tipo}
              </Badge>
            )}
            {incentivo.aliquota !== null && incentivo.aliquota !== undefined && (
              <Badge variant="primary" size="md">
                {formatAliquota(incentivo.aliquota)}
              </Badge>
            )}
          </div>

          <h1 className="text-3xl lg:text-4xl font-bold text-slate-900 leading-tight mb-6">
            {incentivo.titolo}
          </h1>

          <Card className="mb-8">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {incentivo.ente_erogatore && (
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">
                    Ente erogatore
                  </p>
                  <p className="text-sm font-medium text-slate-900 flex items-center gap-1.5">
                    <Building2 className="w-4 h-4 text-slate-400" />
                    {incentivo.ente_erogatore}
                  </p>
                </div>
              )}
              {incentivo.scadenza && (
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">
                    Scadenza
                  </p>
                  <p className="text-sm font-medium text-slate-900 flex items-center gap-1.5">
                    <Calendar className="w-4 h-4 text-slate-400" />
                    {formatDate(incentivo.scadenza)}
                  </p>
                </div>
              )}
              {incentivo.aliquota !== null && incentivo.aliquota !== undefined && (
                <div>
                  <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">
                    Aliquota
                  </p>
                  <p className="text-sm font-bold text-green-700 flex items-center gap-1.5">
                    <Percent className="w-4 h-4" />
                    {formatAliquota(incentivo.aliquota)}
                  </p>
                </div>
              )}
            </div>
          </Card>

          {incentivo.url_fonte && (
            <div className="mb-8">
              <a
                href={incentivo.url_fonte}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm text-primary-600 hover:text-primary-800"
              >
                <ExternalLink className="w-4 h-4" />
                Vai alla fonte ufficiale
              </a>
            </div>
          )}
        </div>

        {/* Descrizione */}
        {incentivo.descrizione && (
          <Card className="mb-8">
            <h2 className="text-xl font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-slate-400" />
              Descrizione
            </h2>
            <div className="prose prose-slate max-w-none">
              <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">
                {incentivo.descrizione}
              </p>
            </div>
          </Card>
        )}

        {/* Requisiti */}
        {incentivo.requisiti && (
          <Card className="mb-8">
            <h2 className="text-xl font-semibold text-slate-900 mb-4">
              Requisiti
            </h2>
            <div className="prose prose-slate max-w-none">
              <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">
                {incentivo.requisiti}
              </p>
            </div>
          </Card>
        )}

        {/* Chatbot CTA */}
        <div className="p-6 bg-green-50 rounded-xl border border-green-200">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-green-900">
                Vuoi saperne di più su questo incentivo?
              </h3>
              <p className="text-sm text-green-700">
                Chiedi al chatbot come applicarlo al tuo progetto.
              </p>
            </div>
            <Link
              href={`/chat?q=${encodeURIComponent(incentivo.titolo || "")}`}
            >
              <Button variant="secondary" size="md">
                Chiedi al chatbot
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
