# EdilEngine

Sistema completo per navigare le leggi italiane dell'edilizia: catalogazione di norme, incentivi, vincoli, e chatbot RAG per rispondere a domande specifiche. L'utente inserisce la propria situazione (terreno, tipo immobile, zona) e ottiene una guida passo-passo su permessi, vincoli e incentivi applicabili.

## Architettura

```
┌─────────────────────────────────────────────────────────────┐
│                    Cloud Scheduler                           │
│                 (trigger periodico scraper)                   │
└──────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                Cloud Run Job: Scraper                        │
│   Python + Scrapy → raccoglie leggi/incentivi → scrive DB   │
└──────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│              Cloud SQL: PostgreSQL 16 + pgvector              │
│   Tabelle: leggi, incentivi, categorie, vincoli, embeddings  │
└─────────────┬────────────────────────────────┬───────────────┘
              │                                │
              ▼                                ▼
┌──────────────────────────┐    ┌──────────────────────────────┐
│   Cloud Run: Backend     │    │     Cloud Run: Frontend       │
│   FastAPI, REST, RAG     │◄───│     Next.js 14 (SSR)          │
│   Porta 8080             │    │     Porta 3000                │
└──────────┬───────────────┘    └──────────────────────────────┘
           │
           ▼
┌──────────────────────────┐
│   LLM Provider (API)     │
│   DeepSeek / OpenAI /    │
│   Groq / OpenRouter      │
└──────────────────────────┘
```

## Componenti

### Database (`/db`)

PostgreSQL 16 con estensione pgvector per vector search.

| Tabella | Descrizione |
|---------|-------------|
| `leggi` | Fonti normative con full-text search (tsvector italiano) |
| `categorie` | Categorie gerarchiche per navigazione |
| `leggi_categorie` | Relazione M:N tra leggi e categorie |
| `incentivi` | Incentivi edilizi (Superbonus, Ecobonus, ecc.) |
| `vincoli` | Vincoli territoriali per comune/zona |
| `embedding_chunks` | Chunk di testo con embedding vettoriali per RAG |
| `chat_sessions` | Sessioni chatbot |
| `chat_messages` | Messaggi chat con riferimenti normativi |

Indici: GIN (full-text search italiano), IVFFlat (vector similarity), BTREE (filtri).

### Scraper (`/scraper`)

Python 3.12 + Scrapy. Raccoglie dati da fonti ufficiali:

- **normattiva.it** — leggi nazionali
- **gazzettaufficiale.it** — decreti e decreti-legge
- **gazzettaamministrativa.it** — norme regionali e locali
- **Siti incentivi** — ENEA, GSE, MASE

Pipeline: scraping → pulizia testo → chunking semantico (512 token, overlap 50) → embedding → salvataggio DB.

### Backend (`/backend`)

Python 3.12 + FastAPI. API REST con RAG chatbot.

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/leggi` | GET | Lista leggi con paginazione e filtri |
| `/api/leggi/{id}` | GET | Dettaglio legge |
| `/api/leggi/search?q=` | GET | Ricerca full-text (tsvector italiano) |
| `/api/leggi/semantic-search?q=` | GET | Ricerca semantica (pgvector) |
| `/api/leggi/categorie` | GET | Albero categorie |
| `/api/incentivi` | GET | Lista incentivi con filtri |
| `/api/incentivi/{id}` | GET | Dettaglio incentivo |
| `/api/vincoli` | GET | Vincoli per area geografica |
| `/api/chat/session` | POST | Crea sessione chat |
| `/api/chat/message` | POST | Invia messaggio (SSE streaming) |
| `/api/chat/session/{id}/history` | GET | Storico messaggi |
| `/api/personalized-guide` | POST | Guida personalizzata passo-passo |

### Frontend (`/frontend`)

Next.js 14 App Router + TypeScript + Tailwind CSS.

| Pagina | Route | Descrizione |
|--------|-------|-------------|
| Landing | `/` | Homepage con search bar |
| Cerca | `/cerca` | Ricerca full-text e semantica |
| Dettaglio legge | `/leggi/[id]` | Testo completo e categorie |
| Categorie | `/categorie` | Albero navigabile |
| Incentivi | `/incentivi` | Lista con filtri |
| Dettaglio incentivo | `/incentivi/[id]` | Requisiti e scadenze |
| Vincoli | `/vincoli` | Ricerca per area geografica |
| Guida | `/guida-personalizzata` | Form → guida passo-passo |
| Chat | `/chat` | Chatbot RAG con fonti normative |

### Mobile App (`/app`)

React Native + Expo SDK 51. Stesse funzionalità del web ottimizzate per mobile.

### Chatbot RAG

Pipeline: query utente → embedding query → ricerca pgvector (top-K chunks) → prompt con contesto + storico → GPT-4o streaming → risposta con fonti normative.

Il chatbot risponde **solo** basandosi sui documenti normativi recuperati, cita sempre le fonti, e dice onestamente quando non trova la risposta nei documenti.

### Guida Personalizzata

L'utente inserisce regione, provincia, comune, tipo intervento, materiale, destinazione d'uso. Il sistema recupera vincoli urbanistici, identifica permessi necessari (CILA/SCIA/Permesso di Costruire), elenca incentivi applicabili e genera una checklist ordinata tramite LLM.

## Stack tecnologico

| Componente | Tecnologia | Motivazione |
|-----------|-----------|-------------|
| Scraper | Python 3.12 + Scrapy | Ecosistema scraping, PDF parsing, NLP italiano |
| Database | PostgreSQL 16 + pgvector | Read-heavy, full-text search italiano, vector embeddings |
| Backend | Python 3.12 + FastAPI | Async, tipizzato, stesso linguaggio scraper |
| Frontend | Next.js 14 (App Router) | SSR per SEO, React ecosystem |
| Mobile | React Native + Expo | Stesso ecosistema React, codebase unica iOS+Android |
| Chatbot | LLM API + RAG | Qualità alta, pgvector per retrieval, streaming |
| Embeddings | sentence-transformers (locale) | Gratuito, funziona offline, buono per italiano |
| Hosting | Google Cloud Run | Serverless, pay-per-use, deploy containerizzato |

## Come funziona

### Ricerca full-text

Le leggi vengono indicizzate con `to_tsvector('italian', testo)` che applica stemming e stop words italiane. La ricerca usa `plainto_tsquery('italian', query)` con ranking `ts_rank`.

### Ricerca semantica

Il testo delle leggi viene diviso in chunk da ~512 token con overlap di 50. Ogni chunk riceve un embedding vettoriale (384 dimensioni, modello `paraphrase-multilingual-MiniLM-L12-v2`). La ricerca semantica usa pgvector con cosine similarity (`<=>`).

### Chatbot RAG

1. L'utente invia un messaggio
2. Il sistema genera l'embedding della query
3. Cerca i 5 chunk più simili nel database
4. Costruisce un prompt con: system prompt + contesto normativo + storico chat + query
5. Chiama il LLM con streaming SSE
6. La risposta include le fonti normative citate

### Guida personalizzata

1. L'utente compila il form con i dati del progetto
2. Il sistema recupera vincoli urbanistici del comune
3. Identifica il permesso necessario in base al tipo di intervento
4. Elenca gli incentivi applicabili
5. Genera una checklist passo-passo tramite LLM

## Avvio rapido

### Prerequisiti

- [Docker](https://docs.docker.com/get-docker/) e Docker Compose
- Una API key per il LLM (vedi [LLM_SETUP.md](./LLM_SETUP.md) per le opzioni gratuite)

### 1. Configura le variabili d'ambiente

```bash
cp .env.example .env
```

Modifica `.env` con almeno queste righe:

```env
# Scegli un provider LLM (vedi LLM_SETUP.md per le opzioni gratuite)
OPENAI_API_KEY=sk-la-tua-chiave
OPENAI_BASE_URL=https://api.groq.com/openai/v1    # esempio con Groq (gratuito)
OPENAI_CHAT_MODEL=llama-3.1-70b-versatile

# Embeddings: GRATUITI con modello locale (non cambiare)
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIMENSION=384
```

### 2. Avvia tutto

```bash
./start.sh
```

Il primo avvio scarica le immagini Docker e il modello di embedding (~500MB). Può richiedere qualche minuto.

### 3. Verifica

| Servizio | URL |
|----------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8080 |
| API Docs | http://localhost:8080/api/docs |
| Health check | http://localhost:8080/api/health |

### 4. Popola il database (opzionale)

Lo scraper raccoglie le leggi dalle fonti ufficiali:

```bash
docker compose --profile scraper up scraper
```

> **Nota**: Gli spider sono scheletri pronti da estendere. Per avere dati di test, puoi inserirli direttamente nel DB.

### 5. Ferma tutto

```bash
./stop.sh
```

I dati del database sono preservati nel volume Docker `pgdata`. Per cancellarli: `docker compose down -v`.

## Sviluppo senza Docker

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database

Puoi usare Docker solo per il DB:

```bash
docker compose up -d db
```

## Configurazione LLM

Il chatbot e la guida personalizzata richiedono un LLM. Il semantic search è **gratuito** con i modelli locali.

Vedi [LLM_SETUP.md](./LLM_SETUP.md) per la configurazione dettagliata di ogni provider.

| Provider | Costo chat | Registrazione |
|----------|-----------|---------------|
| **Groq** | GRATIS (con limiti) | [console.groq.com](https://console.groq.com) |
| **OpenRouter** | GRATIS (modelli free) | [openrouter.ai](https://openrouter.ai) |
| **DeepSeek** | ~€0.14/1M token | [platform.deepseek.com](https://platform.deepseek.com) |
| **OpenAI** | ~$5/1M token | [platform.openai.com](https://platform.openai.com) |

## Struttura del progetto

```
EdilEngine/
├── db/
│   └── init.sql                    # Schema PostgreSQL + pgvector
├── scraper/
│   ├── scrapy.cfg
│   ├── requirements.txt
│   ├── Dockerfile
│   └── edilengine/
│       ├── settings.py
│       ├── pipelines.py            # Pulizia → Chunking → Embedding → DB
│       ├── items.py
│       ├── spiders/                # normattiva, gazzetta, incentivi, regionali
│       └── processors/             # text_cleaner, chunker, embedder
├── backend/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── app/
│       ├── main.py                 # FastAPI app
│       ├── config.py               # Settings (env vars, multi-provider LLM)
│       ├── database.py             # SQLAlchemy async + pgvector
│       ├── models/                 # Legge, Categoria, Incentivo, Vincolo, Chat
│       ├── schemas/                # Pydantic v2 request/response
│       ├── routers/                # leggi, incentivi, vincoli, chat, guide
│       ├── services/
│       │   ├── search_service.py   # Full-text + semantic search
│       │   ├── rag_service.py      # RAG pipeline (retrieve → generate → cite)
│       │   ├── guide_generator.py  # Guida personalizzata
│       │   └── embedding_service.py # Locale (sentence-transformers) o OpenAI
│       └── middleware/             # CORS, rate limiting
├── frontend/
│   ├── package.json
│   ├── Dockerfile
│   └── src/
│       ├── app/                    # 10 pagine Next.js App Router
│       ├── components/             # UI, layout, search, leggi, chat, guide
│       ├── lib/                    # API client, types, utils
│       └── hooks/                  # useSearch, useChat, useGuide
├── app/                            # React Native + Expo
│   └── src/
│       ├── screens/                # 8 schermate
│       ├── components/
│       ├── navigation/             # Bottom tabs + Stack navigator
│       └── services/               # API client
├── docker-compose.yml
├── .env.example
├── start.sh                        # Avvio rapido
├── stop.sh                         # Stop servizi
├── LLM_SETUP.md                    # Configurazione provider LLM
└── SPECIFICHE.md                   # Specifiche tecniche complete
```

## Deploy su Google Cloud

Vedi [SPECIFICHE.md](./SPECIFICHE.md) per i dettagli su Cloud Run, Cloud SQL, Artifact Registry e GitHub Actions.

```bash
# Deploy backend
gcloud run deploy edilengine-api --image ... --region europe-west8

# Deploy frontend
gcloud run deploy edilengine-frontend --image ... --region europe-west8

# Deploy scraper (Cloud Run Job)
gcloud run jobs create edilengine-scraper --image ... --region europe-west8
```

## Licenza

Progetto privato. Tutti i diritti riservati.






