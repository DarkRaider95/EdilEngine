-- EdilEngine Database Schema
-- PostgreSQL 16 + pgvector for RAG and full-text search
-- Idempotent script (CREATE IF NOT EXISTS / DROP IF EXISTS for testing)

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================
-- DROP EXISTING OBJECTS (for clean re-initialization)
-- ============================================
-- Uncomment these lines only for testing/development
-- DROP TABLE IF EXISTS chat_messages CASCADE;
-- DROP TABLE IF EXISTS chat_sessions CASCADE;
-- DROP TABLE IF EXISTS embedding_chunks CASCADE;
-- DROP TABLE IF EXISTS leggi_categorie CASCADE;
-- DROP TABLE IF EXISTS vincoli CASCADE;
-- DROP TABLE IF EXISTS incentivi CASCADE;
-- DROP TABLE IF EXISTS categorie CASCADE;
-- DROP TABLE IF EXISTS leggi CASCADE;
-- DROP TRIGGER IF EXISTS leggi_tsvvector_update ON leggi;

-- ============================================
-- TABELLA: leggi
-- Fonti normative: leggi, decreti, circolari, delibere
-- ============================================
CREATE TABLE IF NOT EXISTS leggi (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titolo TEXT NOT NULL,
    tipo VARCHAR(50),  -- legge, decreto, circolare, delibera, regolamento
    numero VARCHAR(50),
    data_emanazione DATE,
    data_pubblicazione DATE,
    data_vigore DATE,
    autorita VARCHAR(255),  -- Stato, Regione, Comune, Provincia
    testo_completo TEXT,
    url_fonte VARCHAR(1024),
    testo_tsvector TSVECTOR,  -- GIN index per full-text search italiano
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELLA: categorie
-- Categorie e tag per navigazione gerarchica
-- ============================================
CREATE TABLE IF NOT EXISTS categorie (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome VARCHAR(255) UNIQUE NOT NULL,
    parent_id UUID REFERENCES categorie(id)  -- Per gerarchia categorie
);

-- ============================================
-- TABELLA: leggi_categorie
-- Junction table per relazione many-to-many leggi-categorie
-- ============================================
CREATE TABLE IF NOT EXISTS leggi_categorie (
    legge_id UUID NOT NULL REFERENCES leggi(id) ON DELETE CASCADE,
    categoria_id UUID NOT NULL REFERENCES categorie(id) ON DELETE CASCADE,
    PRIMARY KEY (legge_id, categoria_id)
);

-- ============================================
-- TABELLA: incentivi
-- Incentivi edilizi: superbonus, ecobonus, sismabonus, ecc.
-- ============================================
CREATE TABLE IF NOT EXISTS incentivi (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titolo TEXT NOT NULL,
    descrizione TEXT,
    ente_erogatore VARCHAR(255),  -- ENEA, GSE, MASE, Regione, Comune
    tipo VARCHAR(100),  -- superbonus, ecobonus, sismabonus, bonus-casa, altro
    aliquota DECIMAL(5,2),  -- Percentuale incentivata (es. 110, 65, 50)
    scadenza DATE,  -- Data scadenza incentive
    requisiti TEXT,  -- Requisiti per accedere
    url_fonte VARCHAR(1024),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELLA: vincoli
-- Vincoli territoriali: piani regolatori, zone urbanistiche
-- ============================================
CREATE TABLE IF NOT EXISTS vincoli (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    regione VARCHAR(255),
    provincia VARCHAR(255),
    comune VARCHAR(255),
    tipo_zona VARCHAR(100),  -- residenziale, agricola, industriale, storico, parco
    descrizione TEXT,
    norma_riferimento TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELLA: embedding_chunks
-- Chunk di testo con embedding vettoriale per RAG (pgvector)
-- ============================================
CREATE TABLE IF NOT EXISTS embedding_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legge_id UUID NOT NULL REFERENCES leggi(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INT,  -- Ordine del chunk all'interno della legge
    embedding VECTOR(384),  -- Dimensione vettore: 384 per modelli locali (paraphrase-multilingual-MiniLM-L12-v2), 1536 per OpenAI text-embedding-3-small
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELLA: chat_sessions
-- Sessioni chatbot per tracciamento conversazioni
-- ============================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABELLA: chat_messages
-- Messaggi delle chat con riferimenti alle fonti normative
-- ============================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT,
    sources JSONB,  -- Riferimenti alle leggi usate dal RAG per generare la risposta
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDICI
-- ============================================

-- GIN index su testo_tsvector per full-text search italiano
CREATE INDEX IF NOT EXISTS idx_leggi_testo_tsvector ON leggi USING GIN (testo_tsvector);

-- IVFFlat index su embedding per similarity search (RAG retrieval)
-- IVFFlat è ottimale per dataset medio-grandi, usa 100 lists
CREATE INDEX IF NOT EXISTS idx_embedding_chunks_embedding ON embedding_chunks USING IVFFlat (embedding vector_cosine_ops);

-- BTREE su campi di ricerca frequenti in leggi
CREATE INDEX IF NOT EXISTS idx_leggi_titolo ON leggi USING BTREE (titolo);
CREATE INDEX IF NOT EXISTS idx_leggi_data_emanazione ON leggi USING BTREE (data_emanazione);
CREATE INDEX IF NOT EXISTS idx_leggi_autorita ON leggi USING BTREE (autorita);
CREATE INDEX IF NOT EXISTS idx_leggi_tipo ON leggi USING BTREE (tipo);

-- BTREE per ricerca geografica in vincoli
CREATE INDEX IF NOT EXISTS idx_vincoli_comune ON vincoli USING BTREE (comune);
CREATE INDEX IF NOT EXISTS idx_vincoli_regione ON vincoli USING BTREE (regione);
CREATE INDEX IF NOT EXISTS idx_vincoli_tipo_zona ON vincoli USING BTREE (tipo_zona);

-- BTREE per filtri su incentivi
CREATE INDEX IF NOT EXISTS idx_incentivi_tipo ON incentivi USING BTREE (tipo);
CREATE INDEX IF NOT EXISTS idx_incentivi_scadenza ON incentivi USING BTREE (scadenza);

-- BTREE per chat sessions
CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions USING BTREE (session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages USING BTREE (session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages USING BTREE (created_at);

-- ============================================
-- INDICI PARZIALI UTILI
-- ============================================

-- Leggi attive (con vigore non scaduta)
CREATE INDEX IF NOT EXISTS idx_leggi_vigore ON leggi USING BTREE (data_vigore)
WHERE data_vigore IS NOT NULL;

-- Incentivi attivi (non scaduti)
CREATE INDEX IF NOT EXISTS idx_incentivi_attivi ON incentivi USING BTREE (scadenza)
WHERE scadenza IS NOT NULL AND scadenza > CURRENT_DATE;

-- ============================================
-- TRIGGER: aggiornamento automatico testo_tsvector
-- Usa configurazione italiana per stemming e stop words
-- ============================================

CREATE OR REPLACE FUNCTION update_legge_tsvector()
RETURNS TRIGGER AS $$
BEGIN
    -- Aggiorna testo_tsvector quando testo_completo cambia
    IF TG_OP = 'INSERT' OR OLD.testo_completo IS DISTINCT FROM NEW.testo_completo THEN
        NEW.testo_tsvector := to_tsvector('italian', COALESCE(NEW.testo_completo, ''));
    END IF;
    -- Aggiorna updated_at
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Elimina trigger esistente prima di ricrearlo (idempotenza)
DROP TRIGGER IF EXISTS leggi_tsvector_update ON leggi;

CREATE TRIGGER leggi_tsvector_update
    BEFORE INSERT OR UPDATE OF testo_completo ON leggi
    FOR EACH ROW
    EXECUTE FUNCTION update_legge_tsvector();

-- ============================================
-- FUNZIONE: ricerca full-text con ranking
-- ============================================
CREATE OR REPLACE FUNCTION search_leggi(query TEXT)
RETURNS TABLE(
    id UUID,
    titolo TEXT,
    tipo VARCHAR(50),
    numero VARCHAR(50),
    data_emanazione DATE,
    autorita VARCHAR(255),
    url_fonte VARCHAR(1024),
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        l.id,
        l.titolo,
        l.tipo,
        l.numero,
        l.data_emanazione,
        l.autorita,
        l.url_fonte,
        ts_rank(l.testo_tsvector, plainto_tsquery('italian', query)) AS rank
    FROM leggi l
    WHERE l.testo_tsvector @@ plainto_tsquery('italian', query)
    ORDER BY rank DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================
-- FUNZIONE: ricerca similarity su embedding (RAG)
-- ============================================
CREATE OR REPLACE FUNCTION search_similar_chunks(query_embedding VECTOR(384), top_k INT DEFAULT 5)
RETURNS TABLE(
    chunk_id UUID,
    legge_id UUID,
    chunk_text TEXT,
    chunk_index INT,
    similarity REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ec.id AS chunk_id,
        ec.legge_id,
        ec.chunk_text,
        ec.chunk_index,
        1 - (ec.embedding <=> query_embedding) AS similarity
    FROM embedding_chunks ec
    ORDER BY ec.embedding <=> query_embedding
    LIMIT top_k;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================
-- COMMENTI TABELLE (documentazione schema)
-- ============================================
COMMENT ON TABLE leggi IS 'Fonti normative: leggi, decreti, circolari, delibere del sistema italiano';
COMMENT ON TABLE categorie IS 'Categorie gerarchiche per navigazione leggi (es. Urbanistica, Edilizia, Ambiente)';
COMMENT ON TABLE leggi_categorie IS 'Relazione many-to-many tra leggi e categorie';
COMMENT ON TABLE incentivi IS 'Incentivi edilizi: Superbonus, Ecobonus, Sismabonus e altri';
COMMENT ON TABLE vincoli IS 'Vincoli urbanistici e territoriali per comune/zona';
COMMENT ON TABLE embedding_chunks IS 'Chunk di testo con embedding vettoriale per RAG retrieval';
COMMENT ON TABLE chat_sessions IS 'Sessioni chatbot per tracciamento conversazioni utente';
COMMENT ON TABLE chat_messages IS 'Messaggi chat con ruolo e riferimenti alle fonti normative';

COMMENT ON COLUMN leggi.testo_tsvector IS 'TSVECTOR con configurazione italiana per full-text search';
COMMENT ON COLUMN leggi.autorita IS 'Ente emanatore: Stato, Regione, Comune, Provincia';
COMMENT ON COLUMN incentivi.aliquota IS 'Percentuale incentivata (es. 110.00 per superbonus 110%)';
COMMENT ON COLUMN chat_messages.sources IS 'JSONB con riferimenti alle leggi citate nella risposta RAG';
COMMENT ON COLUMN embedding_chunks.embedding IS 'Vettore 384 dimensioni (modelli locali) o 1536 (OpenAI). Cambiare VECTOR(N) se si usa OpenAI';
