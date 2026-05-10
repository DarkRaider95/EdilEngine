# EdilEngine - Specifiche tecniche

## Panoramica

Sistema completo per navigare le leggi italiane dell'edilizia: catalogazione di norme, incentivi, vincoli, e chatbot RAG per rispondere a domande specifiche. L'utente inserisce la propria situazione (terreno, tipo immobile, zona) e ottiene una guida passo-passo su permessi, vincoli, incentivi applicabili.

## Stack tecnologico

| Componente  | Tecnologia               | Motivazione                                                                 |
|-------------|--------------------------|-----------------------------------------------------------------------------|
| Scraper     | Python 3.12 + Scrapy     | Miglior ecosistema per scraping, PDF parsing, NLP italiano                  |
| Database    | PostgreSQL 16 + pgvector | Read-heavy, full-text search nativo in italiano, vector embeddings per RAG |
| Backend API | Python 3.12 + FastAPI    | Async, tipizzato, stesso linguaggio dello scraper, ottimo per Cloud Run     |
| Frontend    | Next.js 14 (App Router)  | SSR per SEO (fondamentale), React condivisione logica con RN               |
| Mobile App  | React Native + Expo      | Stesso ecosistema React, unica codebase iOS+Android, deploy semplificato   |
| Chatbot     | OpenAI GPT-4o + RAG       | Qualità alta, pgvector per retrieval, streaming risposte                   |
| Hosting     | Google Cloud Run         | Serverless, pay-per-use, zero costi a riposo, deploy containerizzato       |
| CI/CD       | GitHub Actions           | Build docker, push Artifact Registry, deploy Cloud Run                     |

## Architettura Cloud Run

```
┌─────────────────────────────────────────────────────────────────┐
│                         Cloud Scheduler                         │
│                    (trigger ogni 24h/7gg)                       │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Cloud Run Job: Scraper                         │
│   Python + Scrapy → raccoglie leggi/incentivi → scrive su DB    │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     Cloud SQL: PostgreSQL 16 + pgvector               │
│   Tabelle: leggi, incentivi, categorie, vincoli, embedding_chunks    │
└────────────┬────────────────────────────────────────────┬────────────┘
             │                                            │
             ▼                                            ▼
┌──────────────────────────────┐          ┌──────────────────────────────┐
│   Cloud Run: Backend API     │          │     Cloud Run: Frontend       │
│   FastAPI, REST, RAG         │◄─────────│     Next.js 14 (SSR)         │
│   Porta 8080                 │          │     Porta 3000               │
└──────────────────────────────┘          └──────────────────────────────┘
             │
             ▼
┌──────────────────────────────┐
│      OpenAI API (GPT-4o)     │
│      Embeddings + Chat       │
└──────────────────────────────┘
```

## Componenti

### 1. Scraper (`/scraper`)

**Container:** Docker, eseguito come Cloud Run Job periodico.

**Fonti da raccogliere:**
- normattiva.it (leggi nazionali)
- gazzettaufficiale.it (decreti, decreti-legge)
- gazzettaamministrativa.it (norme regionali e locali)
- siti delle regioni per piani regolatori e vincoli
- incentivi: ENEA, GSE, MASE, siti regionali
- prontuario: permessi (CILA, SCIA, Permesso di Costruire), oneri, contributi

**Tecnologia:** Scrapy spiders separate per ogni fonte. Pipeline di:
1. Scraping HTML e PDF
2. Estrazione testo (pdfplumber/PyMuPDF)
3. Pulizia e normalizzazione testo
4. Chunking semantico (per embedding)
5. Salvataggio su PostgreSQL

**Struttura:**
```
scraper/
  scrapy.cfg
  requirements.txt
  Dockerfile
  edilengine/
    settings.py
    pipelines.py
    items.py
    middlewares.py
    spiders/
      normattiva.py
      gazzetta_ufficiale.py
      incentivi.py
      regionali.py
      ...
    processors/
      text_cleaner.py
      chunker.py
      embedder.py
```

### 2. Database PostgreSQL (`/db`)

**Tabelle principali:**

```sql
-- Fonti normative (leggi, decreti, circolari)
leggi (
  id UUID PK DEFAULT gen_random_uuid(),
  titolo TEXT NOT NULL,
  tipo VARCHAR(50),        -- legge, decreto, circolare, delibera
  numero VARCHAR(50),
  data_emanazione DATE,
  data_pubblicazione DATE,
  data_vigore DATE,
  autorita VARCHAR(255),   -- Stato, Regione, Comune
  testo_completo TEXT,
  url_fonte VARCHAR(1024),
  testo_tsvector TSVECTOR, -- GIN index per full-text search
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Categorie e tag per navigazione
categorie (
  id UUID PK,
  nome VARCHAR(255) UNIQUE,
  parent_id UUID REFERENCES categorie(id)
);

-- Junction table
leggi_categorie (
  legge_id UUID REFERENCES leggi(id) ON DELETE CASCADE,
  categoria_id UUID REFERENCES categorie(id),
  PRIMARY KEY (legge_id, categoria_id)
);

-- Incentivi
incentivi (
  id UUID PK,
  titolo TEXT NOT NULL,
  descrizione TEXT,
  ente_erogatore VARCHAR(255),
  tipo VARCHAR(100),         -- superbonus, ecobonus, sismabonus, ecc.
  aliquota DECIMAL(5,2),
  scadenza DATE,
  requisiti TEXT,
  url_fonte VARCHAR(1024),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vincoli territoriali (piani regolatori, zone)
vincoli (
  id UUID PK,
  regione VARCHAR(255),
  provincia VARCHAR(255),
  comune VARCHAR(255),
  tipo_zona VARCHAR(100),     -- residenziale, agricola, industriale
  descrizione TEXT,
  norma_riferimento TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Embedding chunks per RAG (pgvector)
embedding_chunks (
  id UUID PK,
  legge_id UUID REFERENCES leggi(id) ON DELETE CASCADE,
  chunk_text TEXT NOT NULL,
  chunk_index INT,
  embedding VECTOR(1536),         -- OpenAI ada-002 dimension
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sessioni chatbot
chat_sessions (
  id UUID PK,
  session_id VARCHAR(255) UNIQUE,
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

chat_messages (
  id UUID PK,
  session_id VARCHAR(255) REFERENCES chat_sessions(session_id),
  role VARCHAR(20),             -- user, assistant
  content TEXT,
  sources JSONB,                -- riferimenti alle leggi usate dal RAG
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indici:**
- `GIN` index su `testo_tsvector` in `leggi` (full-text search italiano)
- `IVFFlat` index su `embedding` in `embedding_chunks` (similarity search)
- `BTREE` su `titolo`, `data_emanazione`, `autorita` in `leggi`
- `BTREE` su `comune`, `regione` in `vincoli`

### 3. Backend API (`/backend`)

**Container:** Docker, Cloud Run service.

**Framework:** FastAPI + Uvicorn.

**Endpoint principali:**

```
GET    /api/health                          Health check
GET    /api/leggi                           Lista leggi con paginazione, filtri
GET    /api/leggi/{id}                      Dettaglio singola legge
GET    /api/leggi/search?q=xxx              Full-text search PostgreSQL
GET    /api/leggi/semantic-search?q=xxx     Semantic search via pgvector
GET    /api/categorie                       Albero categorie
GET    /api/incentivi                       Lista incentivi con filtri
GET    /api/incentivi/{id}                  Dettaglio incentivo
GET    /api/vincoli?comune=xxx              Vincoli per area geografica
POST   /api/chat/session                    Crea nuova sessione chat
POST   /api/chat/message                    Invia messaggio chatbot (streaming SSE)
GET    /api/chat/session/{id}/history       Storico messaggi
POST   /api/personalized-guide              Guida passo-passo personalizzata
```

**Struttura:**
```
backend/
  requirements.txt
  Dockerfile
  app/
    main.py             # FastAPI app
    config.py           # Settings (env vars)
    database.py         # SQLAlchemy async engine + pgvector
    models/
      leggi.py
      incentivi.py
      vincoli.py
      chat.py
    schemas/
      leggi.py          # Pydantic schemas
      incentivi.py
      chat.py
    routers/
      leggi.py
      incentivi.py
      vincoli.py
      chat.py
      guide.py
    services/
      search_service.py        # Full-text search + semantic search
      rag_service.py           # RAG pipeline: retrieve → generate → cite
      guide_generator.py       # Guida personalizzata passo-passo
      embedding_service.py     # Embedding creation via OpenAI
    middleware/
      rate_limit.py
      cors.py
```

### 4. Frontend Web (`/frontend`)

**Container:** Docker, Cloud Run service (o Firebase Hosting).

**Framework:** Next.js 14 App Router + TypeScript + Tailwind CSS.

**Pagine:**
```
/                           Landing page con search bar
/cerca                      Risultati ricerca (full-text + semantic)
/leggi/[id]                 Dettaglio legge
/categorie                  Albero navigazione categorie
/categorie/[slug]           Leggi per categoria
/incentivi                  Lista incentivi
/incentivi/[id]             Dettaglio incentivo
/vincoli                    Ricerca vincoli per area geografica
/guida-personalizzata       Form: inserisci situazione → guida passo-passo
/chat                       Interfaccia chatbot RAG
/chi-siamo                  Info sul progetto
```

**Struttura:**
```
frontend/
  package.json
  Dockerfile
  next.config.js
  tailwind.config.js
  tsconfig.json
  src/
    app/
      layout.tsx
      page.tsx                 # Landing
      cerca/page.tsx
      leggi/[id]/page.tsx
      categorie/page.tsx
      incentivi/page.tsx
      incentivi/[id]/page.tsx
      vincoli/page.tsx
      guida-personalizzata/page.tsx
      chat/page.tsx
    components/
      ui/                       # Componenti base (Button, Card, Input...)
      layout/
        Navbar.tsx
        Footer.tsx
      search/
        SearchBar.tsx
        SearchResults.tsx
      leggi/
        LeggeCard.tsx
        LeggeDetail.tsx
      incentivi/
        IncentivoCard.tsx
        IncentivoFilter.tsx
      chat/
        ChatWindow.tsx
        ChatMessage.tsx
        SourceCitation.tsx     # Mostra riferimenti normativi usati dal RAG
      guide/
        GuideForm.tsx          # Form raccolta dati utente
        GuideResult.tsx        # Guida passo-passo generata
    lib/
      api.ts                    # Client HTTP verso backend
      types.ts                  # TypeScript types
      utils.ts
    hooks/
      useSearch.ts
      useChat.ts
      useGuide.ts
```

### 5. Mobile App (`/app`)

**Framework:** React Native + Expo SDK 51+.

**Feature:** identiche al web ma ottimizzate mobile:
- Ricerca leggi e incentivi
- Chatbot RAG
- Guida personalizzata
- Salvataggio ricerche recenti (AsyncStorage)
- Push notifications per nuove leggi/incentivi

**Struttura:**
```
app/
  package.json
  app.json                 # Expo config
  App.tsx                  # Entry point
  src/
    screens/
      HomeScreen.tsx
      SearchScreen.tsx
      LeggeDetailScreen.tsx
      IncentiviScreen.tsx
      ChatScreen.tsx
      GuideScreen.tsx
      ProfileScreen.tsx
    components/             # Componenti condivisi (o da package condiviso)
    navigation/
      RootNavigator.tsx    # React Navigation
    services/
      api.ts               # Stesso client del frontend (condivisibile via shared package)
    hooks/
      useAuth.ts
      useSearch.ts
    utils/
      storage.ts
```

### 6. RAG Chatbot

**Pipeline:**
1. **Indexing** (offline, eseguito dallo scraper):
   - Estrai chunks di testo dalle leggi (512 token con overlap 50)
   - Genera embedding con `text-embedding-3-small` (OpenAI)
   - Salva in `embedding_chunks`

2. **Retrieval** (online, su ogni query chat):
   - Genera embedding della query utente
   - Cerca top-K chunks simili via pgvector (cosine similarity)
   - Reranking opzionale con metadata filter (categoria, regione)

3. **Generation** (online, su ogni query chat):
   - Costruisci prompt con: system prompt + chunks recuperati + storico chat + query
   - Chiama GPT-4o con streaming SSE
   - Ritoro la risposta + sources (riferimenti normativi con link)

**Prompt system del chatbot:**
```
Sei un assistente esperto di diritto edilizio italiano.
Rispondi SOLO basandoti sui documenti normativi forniti.
Cita sempre gli articoli e le leggi a cui fai riferimento.
Se la risposta non è nei documenti, dillo onestamente.
Le risposte devono essere in italiano, chiare e per un pubblico non tecnico.
Quando possibile, dai indicazioni pratiche e passo-passo.
```

### 7. Guida Personalizzata

Endpoint `POST /api/personalized-guide` che riceve:
```json
{
  "regione": "Lombardia",
  "provincia": "Milano",
  "comune": "Milano",
  "tipo_intervento": "nuova_costruzione",
  "materiale_costruzione": "legno_prefabbricato",
  "destinazione_uso": "residenziale",
  "num_unita": 4,
  "superficie_terreno_mq": 1000,
  "volume_previsto_mc": 1200
}
```

Il backend:
1. Recupera vincoli urbanistici del comune
2. Identifica permessi necessari (CILA/SCIA/permesso di costruire)
3. Elenca incentivi applicabili (materiali legno, nuova residenza, classe energetica)
4. Genera checklist ordinata tramite LLM
5. Restituisce JSON strutturato + testo markdown

## Docker setup

### `docker-compose.yml` (sviluppo locale)
```yaml
version: '3.8'
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: edilengine
      POSTGRES_USER: edilengine
      POSTGRES_PASSWORD: edilengine_dev
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql

  scraper:
    build: ./scraper
    environment:
      DATABASE_URL: postgresql+asyncpg://edilengine:edilengine_dev@db:5432/edilengine
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - db
    profiles:
      - scraper  # eseguito solo on-demand o via scheduler

  backend:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      DATABASE_URL: postgresql+asyncpg://edilengine:edilengine_dev@db:5432/edilengine
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      CORS_ORIGINS: http://localhost:3000
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8080
    depends_on:
      - backend

volumes:
  pgdata:
```

## Deployment su Google Cloud

### Prerequisiti
```bash
# Una tantum: creazione infrastruttura
gcloud services enable run.googleapis.com sqladmin.googleapis.com cloudscheduler.googleapis.com artifactregistry.googleapis.com

# Artifact Registry per i container
gcloud artifacts repositories create edilengine --repository-format=docker --location=europe-west8

# Cloud SQL PostgreSQL con pgvector
gcloud sql instances create edilengine-db \
  --database-version=POSTGRES_16 \
  --tier=db-f1-micro \       # min 0.3 vCPU, per volumi bassi
  --region=europe-west8 \
  --storage-size=10GB \
  --storage-type=SSD \
  --database-flags=cloudsql.enable_pgvector=on

# User e DB
gcloud sql databases create edilengine --instance=edilengine-db
gcloud sql users create edilengine --instance=edilengine-db --password=<password>
```

### Deploy servizi
```bash
# Backend API
gcloud run deploy edilengine-api \
  --image europe-west8-docker.pkg.dev/$PROJECT_ID/edilengine/backend:latest \
  --platform managed \
  --region europe-west8 \
  --allow-unauthenticated \
  --add-cloudsql-instances edilengine-db \
  --set-env-vars DATABASE_URL=...,OPENAI_API_KEY=...

# Frontend
gcloud run deploy edilengine-frontend \
  --image europe-west8-docker.pkg.dev/$PROJECT_ID/edilengine/frontend:latest \
  --platform managed \
  --region europe-west8 \
  --allow-unauthenticated

# Scraper (Cloud Run Job)
gcloud run jobs create edilengine-scraper \
  --image europe-west8-docker.pkg.dev/$PROJECT_ID/edilengine/scraper:latest \
  --region europe-west8 \
  --add-cloudsql-instances edilengine-db \
  --set-env-vars DATABASE_URL=...,OPENAI_API_KEY=...

# Scheduler: esegue lo scraper ogni settimana
gcloud scheduler jobs create http edilengine-scraper-weekly \
  --schedule "0 3 * * 0" \
  --uri "https://europe-west8-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/$PROJECT_ID/jobs/edilengine-scraper:run" \
  --http-method POST \
  --oauth-service-account-email $SA_EMAIL
```

## Piano di sviluppo (ordine)

1. **Database**: schema SQL, Docker compose, inizializzazione
2. **Data loader**: script Python per caricare dati reali da fonti aperte (norme, incentivi, vincoli)
3. **Scraper**: spider normattiva + incentivi, pipeline salvataggio DB (per aggiornamenti futuri)
4. **Backend**: FastAPI base, endpoint CRUD leggi, full-text search
5. **Frontend**: Next.js base, landing page, cerca leggi, dettaglio
6. **RAG indexing**: pipeline embedding + pgvector, endpoint semantic search
7. **Chatbot**: endpoint streaming chat SSE, interfaccia frontend
8. **Guida personalizzata**: form frontend + logica backend + prompt LLM
9. **Incentivi + vincoli**: completamento scraper + endpoint
10. **Mobile app**: React Native Expo, schermate principali
11. **CI/CD**: GitHub Actions, deploy automatico su Cloud Run

## Data Loader

Il sistema deve includere uno script di caricamento dati (`/db/seed.py`) che popola il database con dati reali italiani sull'edilizia, **senza scraping**, utilizzando dati aperti e conoscenza normativa curata.

### Requisiti del data loader

- **Fonti**: dati normativi italiani reali (Testo Unico, Superbonus, Ecobonus, vincoli urbanistici, ecc.)
- **Nessun scraping**: i dati sono inseriti direttamente da conoscenza curata, non estratti da siti web
- **Esecuzione**: `python db/seed.py` o `docker compose exec backend python db/seed.py`
- **Idempotenza**: lo script può essere eseguito più volte senza duplicare i dati (upsert su url_fonte)
- **Dati minimi**: almeno 15-20 leggi, 5-8 incentivi, 10+ vincoli territoriali, 5+ categorie
- **Embedding**: genera embedding per tutti i testi usando il provider configurato (locale o OpenAI)
- **Full-text search**: il trigger PostgreSQL aggiorna automaticamente testo_tsvector

### Dati da caricare

**Leggi** (almeno 15-20):
- Testo Unico dell'Edilizia (D.P.R. 380/2001)
- Superbonus (D.L. 34/2020, convertito con L. 77/2020)
- Ecobonus (L. 276/2013, D.M. 26/2015)
- Sismabonus (D.L. 63/2013)
- Bonus Facciate (L. 205/2017)
- Bonus Verde (L. 205/2017)
- Conto Termico (D.M. 16/2016)
- Norme sismiche (L. 64/1974, O.P.C.M. 3274/2003)
- D.Lgs. 192/2005 (energia)
- D.Lgs. 28/2011 (energie rinnovabili)
- L. 10/1991 (energia)
- D.M. 37/2008 (impianti)
- L. 689/1981 (sanzioni)
- D.P.R. 207/2010 (appalti)
- L. 241/1990 (procedimento amministrativo)

**Incentivi** (5-8):
- Superbonus 110%
- Ecobonus 65%
- Sismabonus
- Bonus Facciate
- Bonus Verde
- Conto Termico 2.0
- Bonus Casa
- Detrazione per barriere architettoniche

**Vincoli** (10+):
- Zone residenziali, agricole, industriali per principali città
- Zone sismiche (cat. 2, 3, 4)
- Zone paesaggistiche
- Vincoli idrogeologici
- Zone storiche e centro storico

**Categorie** (5+):
- Urbanistica
- Edilizia
- Incentivi fiscali
- Sismica
- Ambiente ed energia

## Schema specifiche riassuntivo

| Nome progetto   | EdilEngine                                                        |
|-----------------|-------------------------------------------------------------------|
| Scopo           | Navigare leggi edilizia italiana, incentivi, vincoli, con chatbot RAG |
| Scraper         | Python/Scrapy, estrae testi da fonti ufficiali, PDF parsing       |
| Database        | PostgreSQL 16 + pgvector, ~10 tabelle, full-text search nativo    |
| Backend         | FastAPI, REST + streaming SSE, RAG su pgvector, OpenAI GPT-4o     |
| Frontend        | Next.js 14 App Router, SSR, Tailwind CSS                          |
| Mobile          | React Native + Expo, feature allineate al web                     |
| Chatbot         | RAG con embeddings in pgvector, GPT-4o, citation delle fonti     |
| Hosting         | Google Cloud Run (serverless), Cloud SQL, Cloud Scheduler         |
| Orchestrazione  | Docker Compose (dev), Cloud Build + GitHub Actions (prod)         |
| Linguaggio      | Italiano (interfaccia e contenuti)                                |

---

*Questo file è la specifica tecnica completa per il progetto EdilEngine.*
*Da consegnare all'agente nella prossima sessione per l'implementazione.*
