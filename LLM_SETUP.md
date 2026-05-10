# EdilEngine - Configurazione LLM

## Opzioni per il chatbot (scegli UNA)

### Opzione 1: DeepSeek (più economico, consigliato per testare)
```env
OPENAI_API_KEY=sk-la-tua-chiave-deepseek
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_CHAT_MODEL=deepseek-chat
```
Registrazione: https://platform.deepseek.com → ~€0.14/1M token input

### Opzione 2: OpenRouter (più flessibile, modelli gratuiti)
```env
OPENAI_API_KEY=sk-or-la-tua-chiave-openrouter
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_CHAT_MODEL=meta-llama/llama-3.1-8b-instruct:free
```
Registrazione: https://openrouter.ai → modelli gratuiti disponibili!

### Opzione 3: Groq (gratuito con limiti, velocissimo)
```env
OPENAI_API_KEY=gsk_la-tua-chiave-groq
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_CHAT_MODEL=llama-3.1-70b-versatile
```
Registrazione: https://console.groq.com → GRATIS con rate limits

### Opzione 4: OpenAI (più costoso, massima qualità)
```env
OPENAI_API_KEY=sk-la-tua-chiave-openai
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_CHAT_MODEL=gpt-4o-mini
```
Registrazione: https://platform.openai.com → gpt-4o-mini è il più economico

## Embeddings (SEMPRE GRATUITI con modelli locali)

```env
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL_NAME=paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIMENSION=384
```

Il modello si scarica automaticamente al primo avvio (~471MB).
Non serve nessuna API key per il semantic search!

## Configurazione minima nel .env

Copia .env.example in .env e cambia SOLO queste righe:

```env
OPENAI_API_KEY=sk-la-tua-chiave    # del provider scelto sopra
OPENAI_BASE_URL=https://...         # del provider scelto sopra  
OPENAI_CHAT_MODEL=...               # del provider scelto sopra
EMBEDDING_PROVIDER=local            # lascia così, è gratuito
```

Tutto il resto funziona con i default.