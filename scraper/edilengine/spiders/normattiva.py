"""
Spider for Normattiva.it - Italian official law database.

Scrapes laws and regulations related to building and construction.
NOTE: This is a skeleton spider - structure is complete but needs
actual selectors based on current site structure.
"""

import logging
from datetime import datetime
from typing import Any, Generator

import scrapy
from scrapy.http import Response

from edilengine.items import LeggeItem

logger = logging.getLogger(__name__)


class NormattivaSpider(scrapy.Spider):
    """
    Spider for scraping laws from Normattiva.it.
    
    Normattiva is the official database of Italian laws maintained
    by the Italian government.
    """
    
    name = "normattiva"
    allowed_domains = ["normattiva.it"]
    
    # Base URLs for searching building-related laws
    # These are example URLs - adjust based on actual search needs
    start_urls = [
        "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:legge:edilizia",
        "https://www.normattiva.it/ricerca/formasemplice?query1=edilizia&campo1=titolo",
    ]
    
    # Custom settings for this spider
    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "ROBOTSTXT_OBEY": True,
    }
    
    def __init__(self, *args, **kwargs):
        """Initialize spider with optional parameters."""
        super().__init__(*args, **kwargs)
        self.stats = {
            "laws_found": 0,
            "laws_scraped": 0,
            "errors": 0,
        }
    
    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        """Generate initial requests."""
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_search,
                errback=self.handle_error,
                meta={"page": 1},
            )
    
    def parse_search(self, response: Response) -> Generator[scrapy.Request | LeggeItem, None, None]:
        """
        Parse search results page.
        
        Extracts links to individual laws and follows pagination.
        
        Args:
            response: Search results page response
            
        Yields:
            Requests to law detail pages or LeggeItems
        """
        logger.info(f"Parsing search results from {response.url}")
        
        # Extract law links from search results
        # NOTE: These selectors need to be updated based on actual site structure
        law_links = response.css(
            "div.risultato a::attr(href), "
            "li.risultato a::attr(href), "
            ".law-item a::attr(href)"
        ).getall()
        
        for link in law_links:
            if link and "/dettaglio" in link or "/legge" in link:
                full_url = response.urljoin(link)
                self.stats["laws_found"] += 1
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_legge,
                    errback=self.handle_error,
                    meta={"source": "normattiva"},
                )
        
        # Handle pagination
        next_page = response.css(
            "a.next::attr(href), "
            ".pagination .next a::attr(href), "
            "a[rel='next']::attr(href)"
        ).get()
        
        if next_page:
            current_page = response.meta.get("page", 1)
            next_page_url = response.urljoin(next_page)
            logger.info(f"Following pagination to page {current_page + 1}: {next_page_url}")
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse_search,
                errback=self.handle_error,
                meta={"page": current_page + 1},
            )
    
    def parse_legge(self, response: Response) -> Generator[LeggeItem, None, None]:
        """
        Parse individual law page.
        
        Extracts all relevant fields from the law detail page.
        
        Args:
            response: Law detail page response
            
        Yields:
            LeggeItem with extracted data
        """
        logger.info(f"Parsing law from {response.url}")
        
        try:
            item = LeggeItem()
            
            # Extract title
            item["titolo"] = self._extract_title(response)
            
            # Extract law type and number
            tipo, numero = self._extract_tipo_numero(response)
            item["tipo"] = tipo
            item["numero"] = numero
            
            # Extract dates
            item["data_emanazione"] = self._extract_date(
                response, "data_emanazione"
            )
            item["data_pubblicazione"] = self._extract_date(
                response, "data_pubblicazione"
            )
            item["data_vigore"] = self._extract_date(
                response, "data_vigore"
            )
            
            # Extract authority
            item["autorita"] = self._extract_autorita(response)
            
            # Extract full text
            item["testo_completo"] = self._extract_testo(response)
            
            # Source URL
            item["url_fonte"] = response.url
            
            # Categories (can be extracted from breadcrumbs or tags)
            item["categorie"] = self._extract_categorie(response)
            
            self.stats["laws_scraped"] += 1
            logger.info(f"Successfully scraped law: {item['titolo'][:50]}...")
            
            yield item
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error parsing law {response.url}: {e}", exc_info=True)
    
    def _extract_title(self, response: Response) -> str:
        """Extract law title from response."""
        # Try multiple selectors
        title = (
            response.css("h1::text").get()
            or response.css(".titolo::text").get()
            or response.css("title::text").get()
            or ""
        )
        return title.strip()
    
    def _extract_tipo_numero(self, response: Response) -> tuple[str, str]:
        """Extract law type and number."""
        # Try to parse from title or metadata
        tipo = ""
        numero = ""
        
        # Look for patterns like "Legge 10 gennaio 2020, n. 1"
        metadata = response.css(
            ".metadata::text, "
            ".legge-info::text, "
            "meta[name='tipo']::attr(content)"
        ).getall()
        
        for text in metadata:
            if text:
                # Simple pattern matching
                if "legge" in text.lower():
                    tipo = "Legge"
                elif "decreto" in text.lower():
                    if "legislativo" in text.lower():
                        tipo = "Decreto Legislativo"
                    elif "ministeriale" in text.lower():
                        tipo = "Decreto Ministeriale"
                    else:
                        tipo = "Decreto"
                elif "dpr" in text.lower():
                    tipo = "DPR"
                
                # Extract number
                import re
                match = re.search(r"n\.?\s*(\d+)", text, re.IGNORECASE)
                if match:
                    numero = match.group(1)
        
        return tipo, numero
    
    def _extract_date(self, response: Response, date_type: str) -> str | None:
        """Extract date from response."""
        # Try multiple selectors based on date type
        selectors = {
            "data_emanazione": [
                ".data-emanazione::text",
                "meta[name='dataEmanazione']::attr(content)",
            ],
            "data_pubblicazione": [
                ".data-pubblicazione::text",
                "meta[name='dataPubblicazione']::attr(content)",
            ],
            "data_vigore": [
                ".data-vigore::text",
                "meta[name='dataVigore']::attr(content)",
            ],
        }
        
        for selector in selectors.get(date_type, []):
            value = response.css(selector).get()
            if value:
                return self._parse_date(value)
        
        return None
    
    def _parse_date(self, date_string: str) -> str | None:
        """Parse date string to ISO format."""
        if not date_string:
            return None
        
        # Try common Italian date formats
        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d %B %Y",
            "%d %b %Y",
            "%Y-%m-%d",
        ]
        
        date_string = date_string.strip()
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_string, fmt)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # Return original if parsing fails
        return date_string
    
    def _extract_autorita(self, response: Response) -> str:
        """Extract issuing authority."""
        autorita = (
            response.css(".autorita::text").get()
            or response.css("meta[name='autorita']::attr(content)").get()
            or "Stato Italiano"
        )
        return autorita.strip()
    
    def _extract_testo(self, response: Response) -> str:
        """Extract full law text."""
        # Try to get text from main content area
        testo_parts = response.css(
            ".testo p::text, "
            ".articolo::text, "
            "#contenuto p::text, "
            "article p::text"
        ).getall()
        
        # Join paragraphs
        testo = "\n\n".join(p.strip() for p in testo_parts if p.strip())
        
        # If no paragraphs, get all text from content area
        if not testo:
            testo = response.css(
                "#contenuto::text, "
                ".testo::text, "
                "article::text"
            ).get()
        
        return testo.strip() if testo else ""
    
    def _extract_categorie(self, response: Response) -> list[str]:
        """Extract categories/tags from page."""
        categorie = []
        
        # Try breadcrumbs
        breadcrumbs = response.css(
            ".breadcrumb li a::text, "
            "nav.breadcrumb a::text"
        ).getall()
        
        for crumb in breadcrumbs:
            if crumb and crumb.lower() not in ["home", "normattiva"]:
                categorie.append(crumb.strip())
        
        # Try tags
        tags = response.css(
            ".tag::text, "
            ".categoria::text, "
            "meta[name='keywords']::attr(content)"
        ).getall()
        
        for tag in tags:
            if tag:
                # Split comma-separated tags
                for t in tag.split(","):
                    t = t.strip()
                    if t and t not in categorie:
                        categorie.append(t)
        
        return categorie
    
    def handle_error(self, failure: scrapy.RequestFailure):
        """Handle request failures."""
        self.stats["errors"] += 1
        logger.error(f"Request failed: {failure.request.url} - {failure.value}")
    
    def closed(self, reason: str):
        """Called when spider closes."""
        logger.info(f"Spider closed: {reason}")
        logger.info(f"Stats: {self.stats}")
