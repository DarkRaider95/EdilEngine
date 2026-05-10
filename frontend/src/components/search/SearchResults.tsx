"use client";

import Link from "next/link";
import LeggeCard from "@/components/leggi/LeggeCard";
import Button from "@/components/ui/Button";
import Spinner from "@/components/ui/Spinner";
import type { LeggeBase, SemanticSearchResult } from "@/lib/types";

type SearchItem = LeggeBase | SemanticSearchResult;

interface SearchResultsProps {
  results: SearchItem[];
  total: number;
  page: number;
  pageSize: number;
  loading: boolean;
  error: string | null;
  isSemantic?: boolean;
  onPageChange: (page: number) => void;
  query: string;
}

function isSemanticResult(item: SearchItem): item is SemanticSearchResult {
  return "chunk_id" in item;
}

export default function SearchResults({
  results,
  total,
  page,
  pageSize,
  loading,
  error,
  isSemantic = false,
  onPageChange,
  query,
}: SearchResultsProps) {
  const totalPages = Math.ceil(total / pageSize);

  if (loading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner size="lg" label="Ricerca in corso..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-16">
        <p className="text-red-600 text-lg font-medium mb-2">
          Errore durante la ricerca
        </p>
        <p className="text-slate-600">{error}</p>
      </div>
    );
  }

  if (results.length === 0 && query) {
    return (
      <div className="text-center py-16">
        <p className="text-slate-600 text-lg font-medium mb-2">
          Nessun risultato trovato
        </p>
        <p className="text-slate-500">
          Prova a modificare i termini di ricerca o i filtri.
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* Results count */}
      {total > 0 && (
        <p className="text-sm text-slate-500 mb-4">
          {total} risultato{total !== 1 ? "i" : ""} trovato{total !== 1 ? "i" : ""}
          {query ? ` per "${query}"` : ""}
        </p>
      )}

      {/* Results grid */}
      <div className="space-y-4">
        {isSemantic
          ? results.map((item) => {
              const s = item as SemanticSearchResult;
              return (
                <div
                  key={s.chunk_id}
                  className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div>
                      <Link
                        href={`/leggi/${s.legge_id}`}
                        className="text-lg font-semibold text-primary-700 hover:text-primary-800"
                      >
                        {s.legge_titolo || "Legge senza titolo"}
                      </Link>
                      {s.legge_tipo && (
                        <span className="ml-2 text-xs text-slate-500">
                          {s.legge_tipo}
                          {s.legge_numero ? ` n. ${s.legge_numero}` : ""}
                        </span>
                      )}
                    </div>
                    <span className="text-xs bg-primary-50 text-primary-700 px-2 py-1 rounded-full whitespace-nowrap">
                      {Math.round(s.similarity * 100)}% match
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    {s.chunk_text}
                  </p>
                  <div className="mt-3 flex gap-2">
                    <Link href={`/leggi/${s.legge_id}`}>
                      <Button variant="outline" size="sm">
                        Vedi legge completa
                      </Button>
                    </Link>
                  </div>
                </div>
              );
            })
          : results.map((item, idx) => {
              const legge = item as LeggeBase;
              return <LeggeCard key={legge.id || idx} legge={legge} />;
            })}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-8">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
          >
            Precedente
          </Button>
          <span className="text-sm text-slate-600 px-4">
            Pagina {page} di {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => onPageChange(page + 1)}
          >
            Successiva
          </Button>
        </div>
      )}
    </div>
  );
}
