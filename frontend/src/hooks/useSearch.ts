"use client";

import { useState, useCallback } from "react";
import {
  searchLeggi,
  semanticSearch,
  ApiError,
} from "@/lib/api";
import type { LeggeBase, SemanticSearchResult } from "@/lib/types";

interface UseSearchReturn {
  results: LeggeBase[] | SemanticSearchResult[];
  total: number;
  page: number;
  pageSize: number;
  loading: boolean;
  error: string | null;
  isSemantic: boolean;
  search: (query: string, page?: number, filters?: Record<string, string>) => Promise<void>;
  semanticSearchFn: (query: string, topK?: number) => Promise<void>;
  setPage: (page: number) => void;
  clearResults: () => void;
}

export function useSearch(): UseSearchReturn {
  const [results, setResults] = useState<LeggeBase[] | SemanticSearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSemantic, setIsSemantic] = useState(false);
  const [lastQuery, setLastQuery] = useState("");
  const [lastFilters, setLastFilters] = useState<Record<string, string>>({});

  const search = useCallback(
    async (query: string, pageNum = 1, filters?: Record<string, string>) => {
      setLoading(true);
      setError(null);
      setIsSemantic(false);
      setLastQuery(query);
      if (filters) setLastFilters(filters);
      setPage(pageNum);

      try {
        const response = await searchLeggi({
          q: query,
          page: pageNum,
          page_size: pageSize,
          ...filters,
        });
        setResults(response.items);
        setTotal(response.total);
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError("Errore di connessione al server");
        }
        setResults([]);
        setTotal(0);
      } finally {
        setLoading(false);
      }
    },
    [pageSize]
  );

  const semanticSearchFn = useCallback(
    async (query: string, topK = 5) => {
      setLoading(true);
      setError(null);
      setIsSemantic(true);
      setLastQuery(query);

      try {
        const response = await semanticSearch({ q: query, top_k: topK });
        setResults(response);
        setTotal(response.length);
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError("Errore di connessione al server");
        }
        setResults([]);
        setTotal(0);
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const clearResults = useCallback(() => {
    setResults([]);
    setTotal(0);
    setPage(1);
    setError(null);
    setLastQuery("");
    setLastFilters({});
    setIsSemantic(false);
  }, []);

  return {
    results,
    total,
    page,
    pageSize,
    loading,
    error,
    isSemantic,
    search,
    semanticSearchFn,
    setPage: (newPage) => search(lastQuery, newPage, lastFilters),
    clearResults,
  };
}
