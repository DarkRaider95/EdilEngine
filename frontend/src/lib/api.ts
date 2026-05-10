// ============================================================
// EdilEngine - API Client
// Client HTTP verso il backend FastAPI
// ============================================================

import { buildQueryString, getApiBaseUrl } from "./utils";
import type {
  LeggeDetail,
  LeggeListResponse,
  SearchResult,
  SemanticSearchResult,
  CategoriaTree,
  IncentivoDetail,
  IncentivoListResponse,
  VincoloListResponse,
  ChatSessionResponse,
  ChatHistoryResponse,
  GuideRequest,
  GuideResponse,
  SSEEvent,
} from "./types";

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}${path}`;

  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let detail = `Errore ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // ignore parse error
    }
    throw new ApiError(detail, res.status);
  }

  return res.json();
}

// ============================================================
// Leggi
// ============================================================

export async function getLeggi(params: {
  page?: number;
  page_size?: number;
  tipo?: string;
  autorita?: string;
  data_da?: string;
  data_a?: string;
}): Promise<LeggeListResponse> {
  const qs = buildQueryString(params as Record<string, string | number | null | undefined>);
  return request<LeggeListResponse>(`/api/leggi${qs}`);
}

export async function getLegge(id: string): Promise<LeggeDetail> {
  return request<LeggeDetail>(`/api/leggi/${id}`);
}

export async function searchLeggi(params: {
  q: string;
  page?: number;
  page_size?: number;
  tipo?: string;
  autorita?: string;
  data_da?: string;
  data_a?: string;
}): Promise<SearchResult> {
  const qs = buildQueryString(params as Record<string, string | number | null | undefined>);
  return request<SearchResult>(`/api/leggi/search${qs}`);
}

export async function semanticSearch(params: {
  q: string;
  top_k?: number;
}): Promise<SemanticSearchResult[]> {
  const qs = buildQueryString(params as Record<string, string | number | null | undefined>);
  return request<SemanticSearchResult[]>(`/api/leggi/semantic-search${qs}`);
}

export async function getCategorie(): Promise<CategoriaTree[]> {
  return request<CategoriaTree[]>("/api/leggi/categorie");
}

// ============================================================
// Incentivi
// ============================================================

export async function getIncentivi(params: {
  tipo?: string;
  ente_erogatore?: string;
  scadenza_dopo?: string;
  page?: number;
  page_size?: number;
}): Promise<IncentivoListResponse> {
  const qs = buildQueryString(params as Record<string, string | number | null | undefined>);
  return request<IncentivoListResponse>(`/api/incentivi${qs}`);
}

export async function getIncentivo(id: string): Promise<IncentivoDetail> {
  return request<IncentivoDetail>(`/api/incentivi/${id}`);
}

// ============================================================
// Vincoli
// ============================================================

export async function getVincoli(params: {
  regione?: string;
  provincia?: string;
  comune?: string;
  tipo_zona?: string;
  page?: number;
  page_size?: number;
}): Promise<VincoloListResponse> {
  const qs = buildQueryString(params as Record<string, string | number | null | undefined>);
  return request<VincoloListResponse>(`/api/vincoli${qs}`);
}

// ============================================================
// Chat
// ============================================================

export async function createChatSession(userAgent?: string): Promise<ChatSessionResponse> {
  return request<ChatSessionResponse>("/api/chat/session", {
    method: "POST",
    body: JSON.stringify({ user_agent: userAgent || null }),
  });
}

/**
 * Invia un messaggio alla chat e itera i chunk SSE via fetch + ReadableStream.
 */
export async function* sendChatMessageStream(
  sessionId: string,
  content: string
): AsyncGenerator<SSEEvent, void, unknown> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/api/chat/message`;

  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, content }),
  });

  if (!res.ok) {
    let detail = `Errore ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // ignore
    }
    throw new ApiError(detail, res.status);
  }

  const reader = res.body?.getReader();
  if (!reader) throw new ApiError("Stream non disponibile", 500);

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6).trim();
        if (!data) continue;
        try {
          const event: SSEEvent = JSON.parse(data);
          yield event;
        } catch {
          // Skip unparseable events
        }
      }
    }
  }
}

export async function getChatHistory(sessionId: string): Promise<ChatHistoryResponse> {
  return request<ChatHistoryResponse>(`/api/chat/session/${sessionId}/history`);
}

// ============================================================
// Guida Personalizzata
// ============================================================

export async function generateGuide(data: GuideRequest): Promise<GuideResponse> {
  return request<GuideResponse>("/api/personalized-guide", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export { ApiError };
