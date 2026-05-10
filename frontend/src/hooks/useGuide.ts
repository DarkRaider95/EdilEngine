"use client";

import { useState, useCallback } from "react";
import { generateGuide, ApiError } from "@/lib/api";
import type { GuideRequest, GuideResponse } from "@/lib/types";

interface UseGuideReturn {
  result: GuideResponse | null;
  loading: boolean;
  error: string | null;
  submitGuide: (data: GuideRequest) => Promise<void>;
  clearResult: () => void;
}

export function useGuide(): UseGuideReturn {
  const [result, setResult] = useState<GuideResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submitGuide = useCallback(async (data: GuideRequest) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await generateGuide(data);
      setResult(response);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Errore nella generazione della guida. Riprova più tardi.");
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const clearResult = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return {
    result,
    loading,
    error,
    submitGuide,
    clearResult,
  };
}
