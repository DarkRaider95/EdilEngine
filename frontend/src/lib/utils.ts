import { clsx, type ClassValue } from "clsx";

/**
 * Merge class names with Tailwind CSS conflict resolution.
 * Simula clsx + tailwind-merge senza dipendenze extra.
 */
export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs);
}

/**
 * Format a date string (ISO) to Italian locale format.
 */
export function formatDate(dateStr: string | null): string {
  if (!dateStr) return "N/D";
  try {
    return new Date(dateStr).toLocaleDateString("it-IT", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  } catch {
    return dateStr;
  }
}

/**
 * Truncate text to a maximum length with ellipsis.
 */
export function truncateText(text: string | null, maxLength: number = 200): string {
  if (!text) return "";
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trimEnd() + "…";
}

/**
 * Format an aliquota percentage value.
 */
export function formatAliquota(value: number | null): string {
  if (value === null || value === undefined) return "N/D";
  return `${value}%`;
}

/**
 * Build a query string from an object, skipping null/undefined values.
 */
export function buildQueryString(params: Record<string, string | number | null | undefined>): string {
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined && value !== "") {
      searchParams.append(key, String(value));
    }
  }
  const qs = searchParams.toString();
  return qs ? `?${qs}` : "";
}

/**
 * Get the API base URL from environment, defaulting to localhost.
 */
export function getApiBaseUrl(): string {
  if (typeof window !== "undefined") {
    // Client-side: use relative path (Next.js rewrites proxy to backend)
    return "";
  }
  // Server-side (SSR): use internal Docker hostname or env variable
  return process.env.API_URL_INTERNAL || process.env.NEXT_PUBLIC_API_URL || "http://backend:8080";
}
