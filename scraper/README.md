# EdilEngine Scraper

Scrapy-based scraper for Italian building regulations and incentives.

## Structure

```
scraper/
├── scrapy.cfg                 # Scrapy configuration
├── requirements.txt           # Python dependencies
├── Dockerfile                # Docker image definition
├── .env.example              # Environment variables template
└── edilengine/
    ├── __init__.py
    ├── settings.py           # Scrapy settings
    ├── items.py              # Scrapy item definitions
    ├── pipelines.py          # Data processing pipelines
    ├── middlewares.py        # Request/response middlewares
    ├── spiders/
    │   ├── __init__.py
    │   ├── normattiva.py     # Normattiva.it spider
    │   ├── gazzetta_ufficiale.py  # Gazzetta Ufficiale spider
    │   ├── incentivi.py      # Incentives spider (ENEA, GSE, MASE)
    │   └── regionali.py      # Regional regulations spider
    └── processors/
        ├── __init__.py
        ├── text_cleaner.py   # Text cleaning utilities
        ├── chunker.py        # Text chunking utilities
        └── embedder.py       # OpenAI embedding generator
```

## Installation

### Local Installation

```bash
cd scraper
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Docker Installation

```bash
cd scraper
docker build -t edilengine-scraper .
```

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set your values:
   - `DATABASE_URL`: PostgreSQL connection string
   - `OPENAI_API_KEY`: Your OpenAI API key for embeddings

## Usage

### Run a Spider

```bash
# Run normattiva spider
scrapy crawl normattiva

# Run gazzetta ufficiale spider
scrapy crawl gazzetta_ufficiale

# Run incentives spider
scrapy crawl incentivi

# Run regional regulations spider
scrapy crawl regionali
```

### Run with Docker

```bash
docker run --env-file .env edilengine-scraper scrapy crawl normattiva
```

### Save Output to File

```bash
# JSON output
scrapy crawl normattiva -o output.json

# JSON Lines output
scrapy crawl normattiva -o output.jsonl

# CSV output
scrapy crawl normattiva -o output.csv
```

## Spiders

### NormattivaSpider

Scrapes laws from [normattiva.it](https://www.normattiva.it), the official Italian law database.

- **Name**: `normattiva`
- **Domains**: normattiva.it
- **Items**: LeggeItem

### GazzettaUfficialeSpider

Scrapes official publications from [gazzettaufficiale.it](https://www.gazzettaufficiale.it).

- **Name**: `gazzetta_ufficiale`
- **Domains**: gazzettaufficiale.it
- **Items**: LeggeItem

### IncentiviSpider

Scrapes building incentives from ENEA, GSE, and MASE websites.

- **Name**: `incentivi`
- **Domains**: enea.it, gse.it, mase.gov.it
- **Items**: IncentivoItem

### RegionaliSpider

Scrapes regional building regulations from Italian regional websites.

- **Name**: `regionali`
- **Domains**: Various regional domains
- **Items**: LeggeItem, VincoloItem

## Pipelines

The scraper uses the following processing pipelines:

1. **TextCleaningPipeline**: Cleans HTML content, normalizes whitespace, handles encoding
2. **ChunkingPipeline**: Splits text into overlapping chunks for embedding
3. **EmbeddingPipeline**: Generates OpenAI embeddings for each chunk
4. **DatabasePipeline**: Saves items to PostgreSQL database

## Items

### LeggeItem

Represents a law or regulation:
- `titolo`: Law title
- `tipo`: Law type (Legge, Decreto, etc.)
- `numero`: Law number
- `data_emanazione`: Issue date
- `data_pubblicazione`: Publication date
- `data_vigore`: Effective date
- `autorita`: Issuing authority
- `testo_completo`: Full text
- `url_fonte`: Source URL
- `categorie`: List of categories

### IncentivoItem

Represents a building incentive:
- `titolo`: Incentive title
- `descrizione`: Description
- `ente_erogatore`: Granting authority
- `tipo`: Incentive type
- `aliquota`: Percentage rate
- `scadenza`: Expiration date
- `requisiti`: Requirements
- `url_fonte`: Source URL

### VincoloItem

Represents a territorial constraint:
- `regione`: Region
- `provincia`: Province
- `comune`: Municipality
- `tipo_zona`: Zone type
- `descrizione`: Description
- `norma_riferimento`: Reference regulation
- `url_fonte`: Source URL

## Development

### Adding a New Spider

1. Create a new file in `edilengine/spiders/`
2. Extend `scrapy.Spider`
3. Define `name`, `allowed_domains`, and `start_urls`
4. Implement `parse()` method
5. Add spider to `edilengine/spiders/__init__.py`

### Testing

```bash
# Test spider without saving
scrapy crawl normattiva --loglevel=DEBUG

# Check spider output
scrapy crawl normattiva -o test_output.json
```

## Rate Limiting

The scraper implements several rate limiting mechanisms:

- **DOWNLOAD_DELAY**: 2 seconds between requests (configurable)
- **CONCURRENT_REQUESTS_PER_DOMAIN**: 2 (configurable)
- **AUTOTHROTTLE**: Enabled with adaptive delays
- **OpenAI API**: Rate limited with exponential backoff

## Error Handling

- Automatic retry with exponential backoff
- Request failures are logged but don't crash the spider
- Database errors trigger rollback

## Logging

Logs are output to console with configurable level:

```bash
# Set log level
scrapy crawl normattiva --loglevel=INFO

# Save logs to file
scrapy crawl normattiva --loglevel=INFO --logfile=scrapy.log
```

## Database Schema

The scraper writes to the following tables:
- `leggi`: Laws and regulations
- `categorie`: Categories for organizing laws
- `leggi_categorie`: Many-to-many relationship
- `incentivi`: Building incentives
- `vincoli`: Territorial constraints
- `embedding_chunks`: Text chunks with embeddings

See `db/init.sql` for full schema definition.
