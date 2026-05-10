// ============================================================
// EdilEngine - TypeScript Types (React Native)
// Corrispondenti ai Pydantic schemas del backend FastAPI
// ============================================================

// ---- Leggi ----
export interface LeggeBase {
  id?: string;
  titolo: string;
  tipo: string | null;
  numero: string | null;
  data_emanazione: string | null;
  data_pubblicazione: string | null;
  data_vigore: string | null;
  autorita: string | null;
  url_fonte: string | null;
}

export interface LeggeDetail extends LeggeBase {
  id: string;
  testo_completo: string | null;
  categorie: CategoriaBase[];
  created_at: string;
  updated_at: string;
}

export interface LeggeListResponse {
  items: LeggeBase[];
  total: number;
  page: number;
  page_size: number;
}

// ---- Categorie ----
export interface CategoriaBase {
  id: string;
  nome: string;
  parent_id: string | null;
}

export interface CategoriaTree extends CategoriaBase {
  children: CategoriaTree[];
}

// ---- Search ----
export interface SearchResult {
  items: LeggeBase[];
  total: number;
  page: number;
  page_size: number;
}

export interface SemanticSearchResult {
  chunk_id: string;
  legge_id: string;
  chunk_text: string;
  chunk_index: number | null;
  similarity: number;
  legge_titolo: string | null;
  legge_tipo: string | null;
  legge_numero: string | null;
  legge_url_fonte: string | null;
}

// ---- Incentivi ----
export interface IncentivoBase {
  id?: string;
  titolo: string;
  descrizione: string | null;
  ente_erogatore: string | null;
  tipo: string | null;
  aliquota: number | null;
  scadenza: string | null;
  requisiti: string | null;
  url_fonte: string | null;
}

export interface IncentivoDetail extends IncentivoBase {
  id: string;
  created_at: string;
}

export interface IncentivoListResponse {
  items: IncentivoBase[];
  total: number;
  page: number;
  page_size: number;
}

// ---- Vincoli ----
export interface Vincolo {
  id: string;
  regione: string | null;
  provincia: string | null;
  comune: string | null;
  tipo_zona: string | null;
  descrizione: string | null;
  norma_riferimento: string | null;
  created_at: string;
}

export interface VincoloListResponse {
  items: Vincolo[];
  total: number;
  page: number;
  page_size: number;
}

// ---- Chat ----
export interface ChatSessionResponse {
  id: string;
  session_id: string;
  created_at: string;
}

export interface ChatMessageResponse {
  id: string;
  role: 'user' | 'assistant';
  content: string | null;
  sources: Record<string, unknown> | null;
  created_at: string;
}

export interface ChatHistoryResponse {
  session_id: string;
  messages: ChatMessageResponse[];
}

// ---- Guide ----
export interface GuideRequest {
  regione: string;
  provincia: string;
  comune: string;
  tipo_intervento: string;
  materiale_costruzione?: string | null;
  destinazione_uso: string;
  num_unita: number;
  superficie_terreno_mq?: number | null;
  volume_previsto_mc?: number | null;
}

export interface GuideResponse {
  vincoli: Vincolo[];
  permessi: unknown[];
  incentivi: IncentivoBase[];
  checklist: string[];
  markdown: string;
}

// ---- SSE Event types ----
export interface SSERetrievalEvent {
  type: 'retrieval';
  retrieved_count: number;
  chunks: { text: string; similarity: number }[];
}

export interface SSEMessageEvent {
  type: 'message';
  content: string;
}

export interface SSEDoneEvent {
  type: 'done';
  sources: Record<string, unknown>;
}

export interface SSEErrorEvent {
  type: 'error';
  detail: string;
}

export type SSEEvent = SSERetrievalEvent | SSEMessageEvent | SSEDoneEvent | SSEErrorEvent;
