# EdilEngine - Progresso

## Fase 1: Database ✅
- [x] Schema SQL (7 tabelle, indici, trigger, funzioni search)
- [x] docker-compose.yml con supporto embedding locale
- [x] .env.example con configurazione multi-provider

## Fase 2: Scraper ✅
- [x] Struttura Scrapy completa (4 spider scheletro)

## Fase 3: Backend ✅
- [x] FastAPI + config + database.py (fix DeclarativeBase, Numeric)
- [x] Models, Schemas, Routers, Services
- [x] Embedding service locale (sentence-transformers) + OpenAI

## Fase 4: Frontend ✅
- [x] Next.js 14 completo (fix Dockerfile: npm ci senza --only=production, cartella public/)

## Fase 5-7: RAG + Chatbot + Guida ✅

## Data Loader ✅ (NUOVO)
- [x] db/seed.py con dati reali italiani
- [x] 16 leggi (Testo Unico, Superbonus, Ecobonus, Sismabonus, ecc.)
- [x] 8 incentivi (Superbonus 110%, Ecobonus 65%, ecc.)
- [x] 15 vincoli territoriali (Milano, Roma, Firenze, Venezia, ecc.)
- [x] 8 categorie (Urbanistica, Edilizia, Incentivi, Sismica, ecc.)
- [x] Generazione embeddings automatica con modello locale
- [x] Idempotente (può essere eseguito più volte)

## Review e Fix ✅
- [x] Fix DeclarativeBase() → class Base(DeclarativeBase)
- [x] Fix Decimal → Numeric in incentivi model
- [x] Fix Dockerfile frontend (npm ci senza --only=production, cartella public/)
- [x] Fix SSE format, guida response, XSS, ForeignKey, datetime

## Come avviare e popolare il DB

```bash
# 1. Avvia i servizi
./start.sh

# 2. Popola il DB con dati reali
docker compose exec backend python db/seed.py
```