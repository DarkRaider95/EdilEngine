#!/bin/bash
# ============================================
# EdilEngine - Avvio locale per sviluppo
# ============================================
set -e

echo "🏗️  EdilEngine - Avvio locale"
echo "================================"

# Verifica che .env esista
if [ ! -f .env ]; then
    echo "⚠️  File .env non trovato. Lo creo da .env.example..."
    cp .env.example .env
    echo ""
    echo "✏️  IMPORTANTE: Modifica .env con le tue configurazioni."
    echo ""
    echo "   === CONFIGURAZIONE GRATUITA (consigliata per testare) ==="
    echo "   EMBEDDING_PROVIDER=local          # Embeddings GRATUITI con modelli locali"
    echo "   EMBEDDING_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2"
    echo "   EMBEDDING_DIMENSION=384"
    echo "   OPENAI_API_KEY=sk-tua-chiave      # Per il chatbot (DeepSeek, OpenAI, ecc.)"
    echo "   OPENAI_BASE_URL=https://api.deepseek.com  # Per DeepSeek"
    echo "   OPENAI_CHAT_MODEL=deepseek-chat"
    echo ""
    echo "   Il semantic search funziona GRATIS con modelli locali!"
    echo "   Il chatbot richiede una chiave API per il LLM."
    echo ""
    echo "   Poi ri-esegui questo script."
    exit 1
fi

# Mostra configurazione
EMBEDDING_PROVIDER=$(grep "^EMBEDDING_PROVIDER=" .env 2>/dev/null | cut -d'=' -f2 || echo "local")
EMBEDDING_MODEL=$(grep "^EMBEDDING_MODEL_NAME=" .env 2>/dev/null | cut -d'=' -f2 || echo "paraphrase-multilingual-MiniLM-L12-v2")
BASE_URL=$(grep "^OPENAI_BASE_URL=" .env 2>/dev/null | cut -d'=' -f2 || echo "https://api.openai.com/v1")
CHAT_MODEL=$(grep "^OPENAI_CHAT_MODEL=" .env 2>/dev/null | cut -d'=' -f2 || echo "gpt-4o")

echo ""
echo "📋 Configurazione corrente:"
echo "   Embedding provider: ${EMBEDDING_PROVIDER}"
if [ "$EMBEDDING_PROVIDER" = "local" ]; then
    echo "   Embedding model:    ${EMBEDDING_MODEL} (GRATUITO 🆓)"
else
    echo "   Embedding model:    OpenAI (a pagamento 💰)"
fi
echo "   Chat provider:      ${BASE_URL}"
echo "   Chat model:         ${CHAT_MODEL}"

# Verifica che OPENAI_API_KEY sia impostata per il chatbot
if grep -q "sk-your-openai-api-key-here" .env 2>/dev/null; then
    echo ""
    echo "⚠️  OPENAI_API_KEY non configurata."
    echo "   Il chatbot e la guida personalizzata NON funzioneranno."
    echo "   Le API di lettura (leggi, incentivi, vincoli) funzionano."
    echo "   Il semantic search funziona con EMBEDDING_PROVIDER=local."
    echo ""
    read -p "Vuoi continuare comunque? (s/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "1️⃣  Avvio il database PostgreSQL..."
docker compose up -d db

echo "⏳  Attendo che il database sia pronto..."
until docker compose exec db pg_isready -U edilengine -d edilengine > /dev/null 2>&1; do
    sleep 1
done
echo "✅ Database pronto!"

echo ""
echo "2️⃣  Build e avvio del backend (primo build può richiedere minuti per torch)..."
docker compose up -d backend

echo "⏳  Attendo che il backend sia pronto (il primo avvio scarica il modello di embedding, può richiedere 2-3 minuti)..."
for i in {1..120}; do
    if curl -s http://localhost:8080/api/health > /dev/null 2>&1; then
        echo "✅ Backend pronto!"
        break
    fi
    if [ $i -eq 120 ]; then
        echo "❌ Backend non risponde dopo 120 secondi."
        echo "   Il primo avvio scarica il modello di embedding (~500MB) e torch."
        echo "   Controlla i log: docker compose logs -f backend"
        echo ""
        echo "   Errori comuni:"
        echo "   - Import error: dipendenza mancante → docker compose logs backend"
        echo "   - Modello che si scarica: aspetta ancora qualche minuto"
        echo "   - DB non raggiungibile: verifica che il container db sia healthy"
        exit 1
    fi
    sleep 1
done

echo ""
echo "3️⃣  Build e avvio del frontend..."
docker compose up -d frontend

echo "⏳  Attendo che il frontend sia pronto..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend pronto!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Frontend non risponde dopo 30 secondi."
        echo "   Controlla i logs: docker compose logs frontend"
        exit 1
    fi
    sleep 1
done

echo ""
echo "🎉 EdilEngine è in esecuzione!"
echo ""
echo "   🌐 Frontend:  http://localhost:3000"
echo "   🔧 Backend:   http://localhost:8080"
echo "   📖 API Docs:   http://localhost:8080/api/docs"
echo "   🗄️  Database:  localhost:5432"
echo ""
if [ "$EMBEDDING_PROVIDER" = "local" ]; then
    echo "   🆓 Semantic search: GRATUITO (modello locale)"
fi
echo ""
echo "Per avviare lo scraper (popola il DB con le leggi):"
echo "   docker compose --profile scraper up scraper"
echo ""
echo "Per fermare tutto:"
echo "   ./stop.sh  (o docker compose down)"
echo ""
echo "Per vedere i log:"
echo "   docker compose logs -f"