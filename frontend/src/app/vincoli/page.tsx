"use client";

import { useState } from "react";
import { getVincoli } from "@/lib/api";
import Input from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Spinner from "@/components/ui/Spinner";
import { Search, MapPin, RotateCcw } from "lucide-react";
import type { Vincolo } from "@/lib/types";

export default function VincoliPage() {
  const [vincoli, setVincoli] = useState<Vincolo[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);

  const [regione, setRegione] = useState("");
  const [provincia, setProvincia] = useState("");
  const [comune, setComune] = useState("");
  const [tipoZona, setTipoZona] = useState("");

  const pageSize = 20;

  async function search(pageNum = 1) {
    setLoading(true);
    setError(null);
    setSearched(true);
    try {
      const params: Record<string, string | number> = {
        page: pageNum,
        page_size: pageSize,
      };
      if (regione.trim()) params.regione = regione.trim();
      if (provincia.trim()) params.provincia = provincia.trim();
      if (comune.trim()) params.comune = comune.trim();
      if (tipoZona.trim()) params.tipo_zona = tipoZona.trim();

      const response = await getVincoli(params);
      setVincoli(response.items);
      setTotal(response.total);
      setPage(response.page);
    } catch (err) {
      setError("Errore nel caricamento dei vincoli.");
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setRegione("");
    setProvincia("");
    setComune("");
    setTipoZona("");
  }

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="container-page py-8">
      <h1 className="text-3xl font-bold text-slate-900 mb-2">
        Vincoli Territoriali
      </h1>
      <p className="text-slate-600 mb-8">
        Cerca i vincoli urbanistici, paesaggistici e territoriali per area
        geografica.
      </p>

      {/* Search form */}
      <Card className="mb-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Input
            label="Regione"
            placeholder="es. Lombardia"
            value={regione}
            onChange={(e) => setRegione(e.target.value)}
          />
          <Input
            label="Provincia"
            placeholder="es. Milano"
            value={provincia}
            onChange={(e) => setProvincia(e.target.value)}
          />
          <Input
            label="Comune"
            placeholder="es. Milano"
            value={comune}
            onChange={(e) => setComune(e.target.value)}
          />
          <Input
            label="Tipo zona"
            placeholder="es. Centro storico"
            value={tipoZona}
            onChange={(e) => setTipoZona(e.target.value)}
          />
        </div>
        <div className="flex gap-2 mt-4 justify-end">
          <Button variant="outline" size="sm" onClick={handleReset}>
            <RotateCcw className="w-4 h-4 mr-1" />
            Reset
          </Button>
          <Button
            size="sm"
            onClick={() => search(1)}
            loading={loading}
            leftIcon={<Search size={16} />}
          >
            Cerca Vincoli
          </Button>
        </div>
      </Card>

      {/* Results */}
      {loading && (
        <div className="flex justify-center py-16">
          <Spinner size="lg" label="Ricerca vincoli..." />
        </div>
      )}

      {error && (
        <div className="text-center py-16">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {!loading && !error && searched && vincoli.length === 0 && (
        <div className="text-center py-16">
          <p className="text-slate-600">
            Nessun vincolo trovato per i criteri di ricerca specificati.
          </p>
        </div>
      )}

      {!loading && !error && vincoli.length > 0 && (
        <>
          <p className="text-sm text-slate-500 mb-6">
            {total} vincolo{total !== 1 ? "i" : ""} trovato
            {total !== 1 ? "i" : ""}
          </p>

          <div className="space-y-4">
            {vincoli.map((v) => (
              <Card key={v.id}>
                <div className="flex items-start gap-4">
                  <div className="p-2 rounded-lg bg-amber-50 flex-shrink-0">
                    <MapPin className="w-5 h-5 text-amber-600" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      {v.comune && (
                        <h3 className="text-lg font-semibold text-slate-900">
                          {v.comune}
                        </h3>
                      )}
                      {v.provincia && (
                        <span className="text-sm text-slate-500">
                          ({v.provincia})
                        </span>
                      )}
                      {v.regione && (
                        <span className="text-sm text-slate-500">
                          - {v.regione}
                        </span>
                      )}
                    </div>
                    {v.tipo_zona && (
                      <Badge variant="warning" size="sm" className="mb-2">
                        {v.tipo_zona}
                      </Badge>
                    )}
                    {v.descrizione && (
                      <p className="text-sm text-slate-700 mt-2 leading-relaxed">
                        {v.descrizione}
                      </p>
                    )}
                    {v.norma_riferimento && (
                      <p className="text-xs text-slate-500 mt-3">
                        Norma di riferimento: {v.norma_riferimento}
                      </p>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => search(page - 1)}
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
                onClick={() => search(page + 1)}
              >
                Successiva
              </Button>
            </div>
          )}
        </>
      )}

      {/* Initial state */}
      {!searched && !loading && !error && (
        <div className="text-center py-16">
          <MapPin className="w-12 h-12 text-slate-300 mx-auto mb-4" />
          <p className="text-slate-500">
            Inserisci i criteri di ricerca e clicca &quot;Cerca Vincoli&quot; per
            visualizzare i vincoli territoriali.
          </p>
        </div>
      )}
    </div>
  );
}
