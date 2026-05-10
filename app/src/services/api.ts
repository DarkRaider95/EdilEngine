// ============================================================
// EdilEngine - API Client (React Native)
// Client HTTP verso il backend FastAPI
// ============================================================

import { Platform } from 'react-native';
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
} from './types';

// ============================================================
// Configurazione
// ============================================================

const DEFAULT_BASE_URL = Platform.select({
  android: 'http://10.0.2.2:8080', // Android emulator -> host machine
  ios: 'http://localhost:8080',
  default: 'http://localhost:8080',
});

let _baseUrl = DEFAULT_BASE_URL;

export function setBaseUrl(url: string): void {
  _baseUrl = url;
}

export function getBaseUrl(): string {
  return _baseUrl;
}

// ============================================================
// Error handling
// ============================================================

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${_baseUrl}${path}`;

  const res = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
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
// Utility
// ============================================================

export function buildQueryString(
  params: Record<string, string | number | null | undefined>
): string {
  const searchParams = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined && value !== '') {
      searchParams.append(key, String(value));
    }
  }
  const qs = searchParams.toString();
  return qs ? `?${qs}` : '';
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
  return request<CategoriaTree[]>('/api/leggi/categorie');
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

export async function createChatSession(): Promise<ChatSessionResponse> {
  return request<ChatSessionResponse>('/api/chat/session', {
    method: 'POST',
    body: JSON.stringify({ user_agent: 'EdilEngine-Mobile' }),
  });
}

/**
 * Invia un messaggio alla chat e riceve eventi SSE tramite EventSource.
 * In React Native usiamo un approccio basato su fetch con streaming manuale
 * poiché EventSource nativo su React Native richiede polyfill.
 */
export async function* sendChatMessageStream(
  sessionId: string,
  content: string
): AsyncGenerator<SSEEvent, void, unknown> {
  const url = `${_baseUrl}/api/chat/message`;

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
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

  // Leggiamo il corpo come testo e splittiamo sugli eventi SSE
  const text = await res.text();
  const lines = text.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
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

export async function getChatHistory(sessionId: string): Promise<ChatHistoryResponse> {
  return request<ChatHistoryResponse>(`/api/chat/session/${sessionId}/history`);
}

// ============================================================
// Guida Personalizzata
// ============================================================

export async function generateGuide(data: GuideRequest): Promise<GuideResponse> {
  return request<GuideResponse>('/api/personalized-guide', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}
