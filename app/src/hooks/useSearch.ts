// ============================================================
// EdilEngine - Hook useSearch
// ============================================================

import { useState, useCallback } from 'react';
import {
  searchLeggi,
  semanticSearch,
  ApiError,
} from '../services/api';
import type { LeggeBase, SemanticSearchResult } from '../services/types';
import { addRecentSearch } from '../utils/storage';

export interface UseSearchReturn {
  results: LeggeBase[] | SemanticSearchResult[];
  total: number;
  page: number;
  pageSize: number;
  loading: boolean;
  error: string | null;
  isSemantic: boolean;
  search: (query: string, pageNum?: number, filters?: Record<string, string>) => Promise<void>;
  semanticSearchFn: (query: string, topK?: number) => Promise<void>;
  loadMore: () => Promise<void>;
  clearResults: () => void;
}

export function useSearch(): UseSearchReturn {
  const [results, setResults] = useState<LeggeBase[] | SemanticSearchResult[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(20);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSemantic, setIsSemantic] = useState(false);
  const [lastQuery, setLastQuery] = useState('');
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

        if (pageNum === 1) {
          setResults(response.items);
        } else {
          setResults((prev) => [...(prev as LeggeBase[]), ...response.items]);
        }
        setTotal(response.total);

        // Save to recent searches
        addRecentSearch(query);
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message);
        } else {
          setError('Errore di connessione al server');
        }
        if (pageNum === 1) {
          setResults([]);
          setTotal(0);
        }
      } finally {
        setLoading(false);
      }
    },
    [pageSize]
  );

  const semanticSearchFn = useCallback(async (query: string, topK = 5) => {
    setLoading(true);
    setError(null);
    setIsSemantic(true);
    setLastQuery(query);

    try {
      const response = await semanticSearch({ q: query, top_k: topK });
      setResults(response);
      setTotal(response.length);

      // Save to recent searches
      addRecentSearch(query);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('Errore di connessione al server');
      }
      setResults([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadMore = useCallback(async () => {
    if (loading || isSemantic) return;
    const nextPage = page + 1;
    await search(lastQuery, nextPage, lastFilters);
  }, [loading, isSemantic, page, lastQuery, lastFilters, search]);

  const clearResults = useCallback(() => {
    setResults([]);
    setTotal(0);
    setPage(1);
    setError(null);
    setLastQuery('');
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
    loadMore,
    clearResults,
  };
}
