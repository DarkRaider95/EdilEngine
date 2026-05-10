"""
Spider for Gazzetta Ufficiale - Italian official gazette.

Scrapes official publications related to building regulations.
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


class GazzettaUfficialeSpider(scrapy.Spider):
    """
    Spider for scraping laws from Gazzetta Ufficiale.
    
    Gazzetta Ufficiale is the official journal of the Italian Republic
    where laws and regulations are published.
    """
    
    name = "gazzetta_ufficiale"
    allowed_domains = ["gazzettaufficiale.it"]
    
    # Base URLs for searching building-related publications
    start_urls = [
        "https://www.gazzettaufficiale.it/atto/ricerca?query=edilizia",
        "https://www.gazzettaufficiale.it/do/atto/ricerca/avanzata?p1=edilizia",
    ]
    
    # Custom settings for this spider
    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "ROBOTSTXT_OBEY": True,
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }
    
    def __init__(self, *args, **kwargs):
        """Initialize spider with optional parameters."""
        super().__init__(*args, **kwargs)
        self.stats = {
            "publications_found": 0,
            "publications_scraped": 0,
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
        
        Extracts links to individual publications and follows pagination.
        
        Args:
            response: Search results page response
            
        Yields:
            Requests to publication detail pages or LeggeItems
        """
        logger.info(f"Parsing search results from {response.url}")
        
        # Extract publication links
        # NOTE: These selectors need to be updated based on actual site structure
        pub_links = response.css(
            "li.risultato a::attr(href), "
            ".atto-item a::attr(href), "
            ".result a::attr(href)"
        ).getall()
        
        for link in pub_links:
            if link and "/atto/" in link:
                full_url = response.urljoin(link)
                self.stats["publications_found"] += 1
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_pubblicazione,
                    errback=self.handle_error,
                    meta={"source": "gazzetta_ufficiale"},
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
            logger.info(f"Following pagination to page {current_page + 1}")
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse_search,
                errback=self.handle_error,
                meta={"page": current_page + 1},
            )
    
    def parse_pubblicazione(self, response: Response) -> Generator[LeggeItem, None, None]:
        """
        Parse individual publication page.
        
        Extracts all relevant fields from the publication detail page.
        
        Args:
            response: Publication detail page response
            
        Yields:
            LeggeItem with extracted data
        """
        logger.info(f"Parsing publication from {response.url}")
        
        try:
            item = LeggeItem()
            
            # Extract title
            item["titolo"] = self._extract_title(response)
            
            # Extract publication type and number
            tipo, numero = self._extract_tipo_numero(response)
            item["tipo"] = tipo
            item["numero"] = numero
            
            # Extract dates
            item["data_pubblicazione"] = self._extract_date_pubblicazione(response)
            item["data_vigore"] = self._extract_date_vigore(response)
            
            # Authority is always Gazzetta Ufficiale for these
            item["autorita"] = "Gazzetta Ufficiale della Repubblica Italiana"
            
            # Extract full text
            item["testo_completo"] = self._extract_testo(response)
            
            # Source URL
            item["url_fonte"] = response.url
            
            # Categories
            item["categorie"] = self._extract_categorie(response)
            
            self.stats["publications_scraped"] += 1
            logger.info(f"Successfully scraped publication: {item['titolo'][:50]}...")
            
            yield item
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error parsing publication {response.url}: {e}", exc_info=True)
    
    def _extract_title(self, response: Response) -> str:
        """Extract publication title."""
        title = (
            response.css("h1::text").get()
            or response.css(".titolo::text").get()
            or response.css("title::text").get()
            or ""
        )
        return title.strip()
    
    def _extract_tipo_numero(self, response: Response) -> tuple[str, str]:
        """Extract publication type and number."""
        tipo = ""
        numero = ""
        
        # Look for metadata
        metadata = response.css(
            ".metadata::text, "
            ".info-atto::text"
        ).getall()
        
        for text in metadata:
            if text:
                text_lower = text.lower()
                if "legge" in text_lower:
                    tipo = "Legge"
                elif "decreto legislativo" in text_lower:
                    tipo = "Decreto Legislativo"
                elif "decreto ministeriale" in text_lower:
                    tipo = "Decreto Ministeriale"
                elif "decreto" in text_lower:
                    tipo = "Decreto"
                elif "dpr" in text_lower:
                    tipo = "DPR"
                
                # Extract number
                import re
                match = re.search(r"n\.?\s*(\d+)", text, re.IGNORECASE)
                if match:
                    numero = match.group(1)
        
        return tipo, numero
    
    def _extract_date_pubblicazione(self, response: Response) -> str | None:
        """Extract publication date."""
        date_selectors = [
            ".data-pubblicazione::text",
            ".data::text",
            "meta[name='dataPubblicazione']::attr(content)",
        ]
        
        for selector in date_selectors:
            value = response.css(selector).get()
            if value:
                return self._parse_date(value)
        
        return None
    
    def _extract_date_vigore(self, response: Response) -> str | None:
        """Extract effective date."""
        date_selectors = [
            ".data-vigore::text",
            ".entrata-vigore::text",
            "meta[name='dataVigore']::attr(content)",
        ]
        
        for selector in date_selectors:
            value = response.css(selector).get()
            if value:
                return self._parse_date(value)
        
        return None
    
    def _parse_date(self, date_string: str) -> str | None:
        """Parse date string to ISO format."""
        if not date_string:
            return None
        
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
        
        return date_string
    
    def _extract_testo(self, response: Response) -> str:
        """Extract full publication text."""
        # Try to get text from main content area
        testo_parts = response.css(
            ".testo p::text, "
            ".articolo::text, "
            "#contenuto p::text, "
            "article p::text, "
            ".pdf-content::text"
        ).getall()
        
        testo = "\n\n".join(p.strip() for p in testo_parts if p.strip())
        
        if not testo:
            testo = response.css(
                "#contenuto::text, "
                ".testo::text, "
                "article::text"
            ).get()
        
        return testo.strip() if testo else ""
    
    def _extract_categorie(self, response: Response) -> list[str]:
        """Extract categories from page."""
        categorie = []
        
        # Try breadcrumbs
        breadcrumbs = response.css(
            ".breadcrumb li a::text, "
            "nav.breadcrumb a::text"
        ).getall()
        
        for crumb in breadcrumbs:
            if crumb and crumb.lower() not in ["home", "gazzetta ufficiale"]:
                categorie.append(crumb.strip())
        
        return categorie
    
    def handle_error(self, failure: scrapy.RequestFailure):
        """Handle request failures."""
        self.stats["errors"] += 1
        logger.error(f"Request failed: {failure.request.url} - {failure.value}")
    
    def closed(self, reason: str):
        """Called when spider closes."""
        logger.info(f"Spider closed: {reason}")
        logger.info(f"Stats: {self.stats}")
