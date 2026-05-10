"""
Spider for building incentives from ENEA, GSE, MASE.

Scrapes information about tax deductions, bonuses, and incentives
for building renovations and energy efficiency.
NOTE: This is a skeleton spider - structure is complete but needs
actual selectors based on current site structure.
"""

import logging
from datetime import datetime
from typing import Any, Generator

import scrapy
from scrapy.http import Response

from edilengine.items import IncentivoItem

logger = logging.getLogger(__name__)


class IncentiviSpider(scrapy.Spider):
    """
    Spider for scraping building incentives from multiple sources.
    
    Sources include:
    - ENEA (Agenzia nazionale per le nuove tecnologie)
    - GSE (Gestore Servizi Energetici)
    - MASE (Ministero Ambiente e Sicurezza Energetica)
    """
    
    name = "incentivi"
    
    # Multiple domains for different sources
    allowed_domains = [
        "enea.it",
        "gse.it",
        "mase.gov.it",
    ]
    
    # Start URLs for different sources
    start_urls = [
        # ENEA
        "https://www.enea.it/it/seguici/per-l-azienda/agli-edifici",
        "https://www.enea.it/it/seguici/per-l-azienda/detrazioni-fiscali",
        # GSE
        "https://www.gse.it/servizi-per-te/efficienza-energetica",
        "https://www.gse.it/servizi-per-te/conto-termico",
        # MASE
        "https://www.mase.gov.it/it/notizie/agevolazioni-edilizia",
    ]
    
    # Custom settings
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "ROBOTSTXT_OBEY": True,
    }
    
    def __init__(self, *args, **kwargs):
        """Initialize spider with optional parameters."""
        super().__init__(*args, **kwargs)
        self.stats = {
            "incentives_found": 0,
            "incentives_scraped": 0,
            "errors": 0,
        }
        self.source_urls = {
            "enea.it": "ENEA",
            "gse.it": "GSE",
            "mase.gov.it": "MASE",
        }
    
    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        """Generate initial requests."""
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_source,
                errback=self.handle_error,
                meta={"source": self._get_source_name(url)},
            )
    
    def _get_source_name(self, url: str) -> str:
        """Get source name from URL."""
        for domain, name in self.source_urls.items():
            if domain in url:
                return name
        return "Unknown"
    
    def parse_source(self, response: Response) -> Generator[scrapy.Request | IncentivoItem, None, None]:
        """
        Parse source landing page.
        
        Extracts links to incentive pages.
        
        Args:
            response: Source page response
            
        Yields:
            Requests to incentive detail pages or IncentivoItems
        """
        logger.info(f"Parsing source page: {response.url}")
        
        # Extract incentive links
        incentive_links = response.css(
            "a[href*='incentiv'], "
            "a[href*='detraz'], "
            "a[href*='bonus'], "
            "a[href*='agevol'], "
            ".incentivo-item a::attr(href), "
            ".bonus-item a::attr(href)"
        ).getall()
        
        for link in incentive_links:
            if link:
                full_url = response.urljoin(link)
                self.stats["incentives_found"] += 1
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_incentivo,
                    errback=self.handle_error,
                    meta={"source": response.meta["source"]},
                )
        
        # Follow internal links for more incentives
        internal_links = response.css(
            "nav a::attr(href), "
            ".menu a::attr(href), "
            ".sidebar a::attr(href)"
        ).getall()
        
        for link in internal_links:
            if link and any(domain in link for domain in self.allowed_domains):
                full_url = response.urljoin(link)
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_source,
                    errback=self.handle_error,
                    meta={"source": response.meta["source"]},
                )
    
    def parse_incentivo(self, response: Response) -> Generator[IncentivoItem, None, None]:
        """
        Parse individual incentive page.
        
        Extracts all relevant fields from the incentive detail page.
        
        Args:
            response: Incentive detail page response
            
        Yields:
            IncentivoItem with extracted data
        """
        logger.info(f"Parsing incentive from {response.url}")
        
        try:
            item = IncentivoItem()
            
            # Extract title
            item["titolo"] = self._extract_title(response)
            
            # Extract description
            item["descrizione"] = self._extract_descrizione(response)
            
            # Extract granting authority
            item["ente_erogatore"] = response.meta["source"]
            
            # Extract incentive type
            item["tipo"] = self._extract_tipo(response)
            
            # Extract rate/percentage
            item["aliquota"] = self._extract_aliquota(response)
            
            # Extract deadline
            item["scadenza"] = self._extract_scadenza(response)
            
            # Extract requirements
            item["requisiti"] = self._extract_requisiti(response)
            
            # Source URL
            item["url_fonte"] = response.url
            
            self.stats["incentives_scraped"] += 1
            logger.info(f"Successfully scraped incentive: {item['titolo'][:50]}...")
            
            yield item
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error parsing incentive {response.url}: {e}", exc_info=True)
    
    def _extract_title(self, response: Response) -> str:
        """Extract incentive title."""
        title = (
            response.css("h1::text").get()
            or response.css(".titolo::text").get()
            or response.css("title::text").get()
            or ""
        )
        return title.strip()
    
    def _extract_descrizione(self, response: Response) -> str:
        """Extract incentive description."""
        description_parts = response.css(
            ".descrizione p::text, "
            ".content p::text, "
            "article p::text, "
            ".intro::text"
        ).getall()
        
        description = "\n\n".join(p.strip() for p in description_parts if p.strip())
        
        if not description:
            description = response.css(
                ".descrizione::text, "
                ".content::text, "
                "article::text"
            ).get()
        
        return description.strip() if description else ""
    
    def _extract_tipo(self, response: Response) -> str:
        """Extract incentive type."""
        # Look for type indicators in the page
        tipo_indicators = response.css(
            ".tipo::text, "
            ".categoria::text, "
            "meta[name='tipo']::attr(content)"
        ).getall()
        
        for text in tipo_indicators:
            if text:
                text_lower = text.lower()
                if "detrazione" in text_lower:
                    return "Detrazione fiscale"
                elif "conto termico" in text_lower:
                    return "Conto Termico"
                elif "superbonus" in text_lower:
                    return "Superbonus"
                elif "ecobonus" in text_lower:
                    return "Ecobonus"
                elif "sismabonus" in text_lower:
                    return "Sismabonus"
                elif "bonus facciate" in text_lower:
                    return "Bonus Facciate"
        
        # Default based on title
        title = self._extract_title(response).lower()
        if "detrazione" in title:
            return "Detrazione fiscale"
        elif "conto" in title:
            return "Conto Termico"
        elif "bonus" in title:
            return "Bonus"
        
        return "Incentivo"
    
    def _extract_aliquota(self, response: Response) -> str | None:
        """Extract incentive rate/percentage."""
        # Look for percentage values
        percentages = response.css(
            ".aliquota::text, "
            ".percentuale::text, "
            ".rate::text"
        ).getall()
        
        import re
        for text in percentages:
            if text:
                match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
                if match:
                    return f"{match.group(1)}%"
        
        # Also search in full text
        full_text = response.get()
        matches = re.findall(r"(\d+(?:\.\d+)?)\s*%", full_text)
        if matches:
            return f"{matches[0]}%"
        
        return None
    
    def _extract_scadenza(self, response: Response) -> str | None:
        """Extract deadline/expiration date."""
        date_selectors = [
            ".scadenza::text, "
            ".deadline::text, "
            ".data-scadenza::text",
        ]
        
        for selector in date_selectors:
            value = response.css(selector).get()
            if value:
                return self._parse_date(value)
        
        return None
    
    def _extract_requisiti(self, response: Response) -> str:
        """Extract requirements."""
        requirements_parts = response.css(
            ".requisiti li::text, "
            ".requirements li::text, "
            ".requisiti p::text, "
            "#requisiti p::text"
        ).getall()
        
        requirements = "\n".join(r.strip() for r in requirements_parts if r.strip())
        
        if not requirements:
            # Try to find requirements section
            requirements = response.css(
                ".requisiti::text, "
                "#requisiti::text"
            ).get()
        
        return requirements.strip() if requirements else ""
    
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
    
    def handle_error(self, failure: scrapy.RequestFailure):
        """Handle request failures."""
        self.stats["errors"] += 1
        logger.error(f"Request failed: {failure.request.url} - {failure.value}")
    
    def closed(self, reason: str):
        """Called when spider closes."""
        logger.info(f"Spider closed: {reason}")
        logger.info(f"Stats: {self.stats}")
