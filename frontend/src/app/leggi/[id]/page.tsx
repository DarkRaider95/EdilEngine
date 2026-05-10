"use client";

import { useEffect, useState } from "react";
import { useParams, notFound } from "next/navigation";
import LeggeDetailView from "@/components/leggi/LeggeDetail";
import Spinner from "@/components/ui/Spinner";
import Card from "@/components/ui/Card";
import { getLegge, searchLeggi } from "@/lib/api";
import type { LeggeDetail } from "@/lib/types";

export default function LeggeDetailPage() {
  const params = useParams<{ id: string }>();
  const id = decodeURIComponent(params.id);

  const [legge, setLegge] = useState<LeggeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadLegge();
  }, [id]);

  async function loadLegge() {
    setLoading(true);
    setError(null);
    try {
      // Prima prova: assumiamo sia un UUID
      const detail = await getLegge(id);
      setLegge(detail);
    } catch {
      // Seconda prova: cerchiamo per titolo
      try {
        const searchResult = await searchLeggi({ q: id, page: 1, page_size: 5 });
        if (searchResult.items.length > 0) {
          // Prendiamo il primo risultato e cerchiamo di ottenere il dettaglio col suo ID
          // se l'API restituisce l'ID
          const match = searchResult.items[0];
          if (match.id) {
            const detail = await getLegge(match.id);
            setLegge(detail);
            return;
          }
        }
        setError("Legge non trovata. Prova a cercarla dalla pagina di ricerca.");
      } catch {
        setError("Errore nel caricamento della legge. Verifica che il backend sia attivo.");
      }
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="container-page py-20 flex justify-center">
        <Spinner size="lg" label="Caricamento legge..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container-page py-20">
        <Card>
          <div className="text-center py-8">
            <p className="text-red-600 mb-4">{error}</p>
            <a
              href="/cerca"
              className="text-primary-600 hover:text-primary-800 text-sm"
            >
              Vai alla ricerca
            </a>
          </div>
        </Card>
      </div>
    );
  }

  if (!legge) {
    notFound();
  }

  return (
    <div className="container-page py-8">
      <LeggeDetailView legge={legge} />
    </div>
  );
}
