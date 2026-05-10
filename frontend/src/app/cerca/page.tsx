"use client";

import { useState, useEffect, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import SearchBar from "@/components/search/SearchBar";
import SearchResults from "@/components/search/SearchResults";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Card from "@/components/ui/Card";
import { useSearch } from "@/hooks/useSearch";
import { ToggleLeft, ToggleRight, SlidersHorizontal } from "lucide-react";

export default function CercaPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const {
    results,
    total,
    page,
    pageSize,
    loading,
    error,
    isSemantic,
    search,
    semanticSearchFn,
    setPage,
    clearResults,
  } = useSearch();

  const [query, setQuery] = useState(searchParams.get("q") || "");
  const [searchMode, setSearchMode] = useState<"text" | "semantic">("text");
  const [showFilters, setShowFilters] = useState(false);

  // Filters
  const [tipo, setTipo] = useState("");
  const [autorita, setAutorita] = useState("");
  const [dataDa, setDataDa] = useState("");
  const [dataA, setDataA] = useState("");

  // Auto-search from URL query param
  useEffect(() => {
    const q = searchParams.get("q");
    if (q) {
      setQuery(q);
      search(q, 1, buildFilters());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const buildFilters = useCallback(() => {
    const filters: Record<string, string> = {};
    if (tipo) filters.tipo = tipo;
    if (autorita) filters.autorita = autorita;
    if (dataDa) filters.data_da = dataDa;
    if (dataA) filters.data_a = dataA;
    return filters;
  }, [tipo, autorita, dataDa, dataA]);

  const handleSearch = (q: string) => {
    setQuery(q);
    if (searchMode === "semantic") {
      semanticSearchFn(q);
    } else {
      search(q, 1, buildFilters());
    }
    // Update URL
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    router.replace(`/cerca?${params.toString()}`, { scroll: false });
  };

  const handleApplyFilters = () => {
    if (query.trim()) {
      search(query, 1, buildFilters());
    }
  };

  const handleResetFilters = () => {
    setTipo("");
    setAutorita("");
    setDataDa("");
    setDataA("");
    if (query.trim()) {
      search(query, 1, {});
    }
  };

  return (
    <div className="container-page py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-slate-900 mb-6">
          Cerca nelle leggi edilizie
        </h1>

        {/* Search Bar + Mode Toggle */}
        <div className="mb-6">
          <SearchBar
            defaultValue={query}
            onSearch={handleSearch}
            size="lg"
          />

          <div className="flex items-center justify-between mt-4">
            {/* Search mode toggle */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  setSearchMode("text");
                  if (query.trim()) search(query, 1, buildFilters());
                }}
                className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  searchMode === "text"
                    ? "bg-primary-100 text-primary-700"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {searchMode === "text" ? (
                  <ToggleLeft className="w-4 h-4" />
                ) : (
                  <ToggleRight className="w-4 h-4" />
                )}
                Ricerca testuale
              </button>
              <button
                onClick={() => {
                  setSearchMode("semantic");
                  if (query.trim()) semanticSearchFn(query);
                }}
                className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  searchMode === "semantic"
                    ? "bg-primary-100 text-primary-700"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {searchMode === "semantic" ? (
                  <ToggleRight className="w-4 h-4" />
                ) : (
                  <ToggleLeft className="w-4 h-4" />
                )}
                Ricerca semantica
              </button>
            </div>

            {/* Filter toggle (solo per ricerca testuale) */}
            {searchMode === "text" && (
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="inline-flex items-center gap-2 px-3 py-2 text-sm text-slate-600 hover:text-slate-900 transition-colors"
              >
                <SlidersHorizontal className="w-4 h-4" />
                Filtri
              </button>
            )}
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && searchMode === "text" && (
          <Card className="mb-6 animate-fade-in">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Input
                label="Tipo legge"
                placeholder="es. Legge, Decreto..."
                value={tipo}
                onChange={(e) => setTipo(e.target.value)}
              />
              <Input
                label="Autorità"
                placeholder="es. Parlamento, Governo..."
                value={autorita}
                onChange={(e) => setAutorita(e.target.value)}
              />
              <Input
                label="Data da"
                type="date"
                value={dataDa}
                onChange={(e) => setDataDa(e.target.value)}
              />
              <Input
                label="Data a"
                type="date"
                value={dataA}
                onChange={(e) => setDataA(e.target.value)}
              />
            </div>
            <div className="flex gap-2 mt-4 justify-end">
              <Button variant="outline" size="sm" onClick={handleResetFilters}>
                Reset
              </Button>
              <Button size="sm" onClick={handleApplyFilters}>
                Applica filtri
              </Button>
            </div>
          </Card>
        )}

        {/* Results */}
        <SearchResults
          results={results}
          total={total}
          page={page}
          pageSize={pageSize}
          loading={loading}
          error={error}
          isSemantic={isSemantic}
          onPageChange={setPage}
          query={query}
        />
      </div>
    </div>
  );
}
