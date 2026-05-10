"""
Scrapy settings for EdilEngine project.

Configuration for scraping Italian building regulations from various sources.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BOT_NAME = "edilengine"

SPIDER_MODULES = ["edilengine.spiders"]
NEWSPIDER_MODULE = "edilengine.spiders"

# Crawl responsibly by identifying yourself
USER_AGENT = "EdilEngine/1.0 (+https://github.com/edilengine; scraper@edilengine.it)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy
CONCURRENT_REQUESTS = 4

# Configure a delay for requests for the same website
DOWNLOAD_DELAY = 2

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 2
CONCURRENT_REQUESTS_PER_IP = 2

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console
TELNETCONSOLE_ENABLED = False

# Override the default request headers
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# Enable or disable spider middlewares
SPIDER_MIDDLEWARES = {
    "edilengine.middlewares.EdilengineSpiderMiddleware": 543,
}

# Enable or disable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    "edilengine.middlewares.EdilengineDownloaderMiddleware": 543,
    "edilengine.middlewares.UserAgentMiddleware": 400,
    "edilengine.middlewares.RetryMiddleware": 550,
}

# Enable or disable extensions
EXTENSIONS = {
    "scrapy.extensions.telnet.TelnetConsole": None,
}

# Configure item pipelines
ITEM_PIPELINES = {
    "edilengine.pipelines.TextCleaningPipeline": 100,
    "edilengine.pipelines.ChunkingPipeline": 200,
    "edilengine.pipelines.EmbeddingPipeline": 300,
    "edilengine.pipelines.DatabasePipeline": 400,
}

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://edilengine:edilengine@localhost:5432/edilengine")

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
OPENAI_EMBEDDING_DIMENSIONS = int(os.getenv("OPENAI_EMBEDDING_DIMENSIONS", "1536"))

# Chunking configuration
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Rate limiting for OpenAI API
OPENAI_RATE_LIMIT = int(os.getenv("OPENAI_RATE_LIMIT", "10"))  # requests per second

# AutoThrottle configuration
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 1 day
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [500, 502, 503, 504, 408, 429]
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Retry configuration
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
LOG_DATEFORMAT = "%Y-%m-%d %H:%M:%S"

# Custom settings for specific spiders
NORMATTIVA_BASE_URL = "https://www.normattiva.it"
GAZZETTA_BASE_URL = "https://www.gazzettaufficiale.it"
