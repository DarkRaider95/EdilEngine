"use client";

import { useState, useEffect, useCallback } from "react";
import { getIncentivi } from "@/lib/api";
import IncentivoCard from "@/components/incentivi/IncentivoCard";
import IncentivoFilter, {
  type IncentivoFilterValues,
} from "@/components/incentivi/IncentivoFilter";
import Spinner from "@/components/ui/Spinner";
import Button from "@/components/ui/Button";
import type { IncentivoBase } from "@/lib/types";

export default function IncentiviPage() {
  const [incentivi, setIncentivi] = useState<IncentivoBase[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<IncentivoFilterValues>({
    tipo: "",
    ente_erogatore: "",
    scadenza_dopo: "",
  });

  const pageSize = 20;

  const loadIncentivi = useCallback(
    async (pageNum: number, currentFilters: IncentivoFilterValues) => {
      setLoading(true);
      setError(null);
      try {
        const params: Record<string, string | number> = {
          page: pageNum,
          page_size: pageSize,
        };
        if (currentFilters.tipo) params.tipo = currentFilters.tipo;
        if (currentFilters.ente_erogatore)
          params.ente_erogatore = currentFilters.ente_erogatore;
        if (currentFilters.scadenza_dopo)
          params.scadenza_dopo = currentFilters.scadenza_dopo;

        const response = await getIncentivi(params);
        setIncentivi(response.items);
        setTotal(response.total);
        setPage(response.page);
      } catch (err) {
        setError("Errore nel caricamento degli incentivi.");
      } finally {
        setLoading(false);
      }
    },
    []
  );

  useEffect(() => {
    loadIncentivi(1, filters);
  }, []);

  const handleFilter = (values: IncentivoFilterValues) => {
    setFilters(values);
    setPage(1);
    loadIncentivi(1, values);
  };

  const handleReset = () => {
    const empty = { tipo: "", ente_erogatore: "", scadenza_dopo: "" };
    setFilters(empty);
    setPage(1);
    loadIncentivi(1, empty);
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="container-page py-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">
        Incentivi Edilizi
      </h1>
      <p className="text-slate-600 mb-8">
        Tutti gli incentivi, bonus e agevolazioni disponibili per l&apos;edilizia.
      </p>

      <IncentivoFilter
        onFilter={handleFilter}
        onReset={handleReset}
        loading={loading}
      />

      {loading && (
        <div className="flex justify-center py-16">
          <Spinner size="lg" label="Caricamento incentivi..." />
        </div>
      )}

      {error && (
        <div className="text-center py-16">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {!loading && !error && incentivi.length === 0 && (
        <div className="text-center py-16">
          <p className="text-slate-600">
            Nessun incentivo trovato con i filtri selezionati.
          </p>
        </div>
      )}

      {!loading && !error && incentivi.length > 0 && (
        <>
          <p className="text-sm text-slate-500 mb-6">
            {total} incentivo{total !== 1 ? "i" : ""} trovato
            {total !== 1 ? "i" : ""}
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {incentivi.map((inc, i) => (
              <IncentivoCard key={inc.titolo + i} incentivo={inc} />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => loadIncentivi(page - 1, filters)}
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
                onClick={() => loadIncentivi(page + 1, filters)}
              >
                Successiva
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
