"""
Spider for regional building regulations.

Scrapes building regulations from Italian regional websites.
NOTE: This is a skeleton spider - structure is complete but needs
actual selectors based on current site structure.
"""

import logging
from datetime import datetime
from typing import Any, Generator

import scrapy
from scrapy.http import Response

from edilengine.items import LeggeItem, VincoloItem

logger = logging.getLogger(__name__)


class RegionaliSpider(scrapy.Spider):
    """
    Spider for scraping regional building regulations.
    
    Scrapes regulations and constraints from Italian regional
    government websites.
    """
    
    name = "regionali"
    
    # Regional domains to scrape
    allowed_domains = [
        "regione.lombardia.it",
        "regione.emilia-romagna.it",
        "regione.veneto.it",
        "regione.piemonte.it",
        "regione.toscana.it",
        "regione.lazio.it",
        "regione.campania.it",
        "regione.sicilia.it",
    ]
    
    # Start URLs for different regions
    start_urls = [
        "https://www.regionelombardia.it/web/regione-lombardia/edilizia",
        "https://www.regione.emilia-romagna.it/temi/territorio-edilizia",
        "https://www.regione.veneto.it/web/territorio",
        "https://www.regione.piemonte.it/web/temi/territorio-ambiente",
        "https://www.regione.toscana.it/territorio",
        "https://www.regione.lazio.it/territorio",
    ]
    
    # Custom settings
    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "ROBOTSTXT_OBEY": True,
    }
    
    def __init__(self, *args, **kwargs):
        """Initialize spider with optional parameters."""
        super().__init__(*args, **kwargs)
        self.stats = {
            "regulations_found": 0,
            "regulations_scraped": 0,
            "constraints_found": 0,
            "constraints_scraped": 0,
            "errors": 0,
        }
        self.regions = {
            "lombardia": "Lombardia",
            "emilia-romagna": "Emilia-Romagna",
            "veneto": "Veneto",
            "piemonte": "Piemonte",
            "toscana": "Toscana",
            "lazio": "Lazio",
            "campania": "Campania",
            "sicilia": "Sicilia",
        }
    
    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        """Generate initial requests."""
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_region,
                errback=self.handle_error,
                meta={"region": self._get_region_name(url)},
            )
    
    def _get_region_name(self, url: str) -> str:
        """Get region name from URL."""
        for key, name in self.regions.items():
            if key in url.lower():
                return name
        return "Unknown"
    
    def parse_region(self, response: Response) -> Generator[scrapy.Request | LeggeItem | VincoloItem, None, None]:
        """
        Parse regional page.
        
        Extracts links to regulations and constraints.
        
        Args:
            response: Regional page response
            
        Yields:
            Requests to detail pages or items
        """
        logger.info(f"Parsing regional page: {response.url}")
        region = response.meta["region"]
        
        # Extract regulation links
        regulation_links = response.css(
            "a[href*='legge'], "
            "a[href*='regolamento'], "
            "a[href*='norma'], "
            "a[href*='delibera'], "
            ".normativa-item a::attr(href)"
        ).getall()
        
        for link in regulation_links:
            if link:
                full_url = response.urljoin(link)
                self.stats["regulations_found"] += 1
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_regolamento,
                    errback=self.handle_error,
                    meta={"region": region, "type": "regulation"},
                )
        
        # Extract constraint links
        constraint_links = response.css(
            "a[href*='vincolo'], "
            "a[href*='piano'], "
            "a[href*='paesaggio'], "
            "a[href*='sismica'], "
            ".vincolo-item a::attr(href)"
        ).getall()
        
        for link in constraint_links:
            if link:
                full_url = response.urljoin(link)
                self.stats["constraints_found"] += 1
                yield scrapy.Request(
                    url=full_url,
                    callback=self.parse_vincolo,
                    errback=self.handle_error,
                    meta={"region": region, "type": "constraint"},
                )
        
        # Follow internal links
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
                    callback=self.parse_region,
                    errback=self.handle_error,
                    meta={"region": region},
                )
    
    def parse_regolamento(self, response: Response) -> Generator[LeggeItem, None, None]:
        """
        Parse regional regulation page.
        
        Args:
            response: Regulation detail page response
            
        Yields:
            LeggeItem with extracted data
        """
        logger.info(f"Parsing regulation from {response.url}")
        region = response.meta["region"]
        
        try:
            item = LeggeItem()
            
            # Extract title
            item["titolo"] = self._extract_title(response)
            
            # Type is regional regulation
            item["tipo"] = self._extract_tipo_regionale(response)
            item["numero"] = self._extract_numero(response)
            
            # Extract dates
            item["data_emanazione"] = self._extract_date(response)
            item["data_pubblicazione"] = self._extract_date(response)
            
            # Authority is the region
            item["autorita"] = f"Regione {region}"
            
            # Extract full text
            item["testo_completo"] = self._extract_testo(response)
            
            # Source URL
            item["url_fonte"] = response.url
            
            # Categories include the region
            item["categorie"] = [region, "Normativa Regionale", "Edilizia"]
            
            self.stats["regulations_scraped"] += 1
            logger.info(f"Successfully scraped regulation: {item['titolo'][:50]}...")
            
            yield item
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error parsing regulation {response.url}: {e}", exc_info=True)
    
    def parse_vincolo(self, response: Response) -> Generator[VincoloItem, None, None]:
        """
        Parse regional constraint page.
        
        Args:
            response: Constraint detail page response
            
        Yields:
            VincoloItem with extracted data
        """
        logger.info(f"Parsing constraint from {response.url}")
        region = response.meta["region"]
        
        try:
            item = VincoloItem()
            
            # Region
            item["regione"] = region
            
            # Try to extract province
            item["provincia"] = self._extract_provincia(response)
            
            # Try to extract municipality
            item["comune"] = self._extract_comune(response)
            
            # Constraint type
            item["tipo_zona"] = self._extract_tipo_zona(response)
            
            # Description
            item["descrizione"] = self._extract_descrizione_vincolo(response)
            
            # Reference regulation
            item["norma_riferimento"] = self._extract_norma_riferimento(response)
            
            # Source URL
            item["url_fonte"] = response.url
            
            self.stats["constraints_scraped"] += 1
            logger.info(f"Successfully scraped constraint: {item['tipo_zona']} - {item['regione']}")
            
            yield item
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Error parsing constraint {response.url}: {e}", exc_info=True)
    
    def _extract_title(self, response: Response) -> str:
        """Extract regulation title."""
        title = (
            response.css("h1::text").get()
            or response.css(".titolo::text").get()
            or response.css("title::text").get()
            or ""
        )
        return title.strip()
    
    def _extract_tipo_regionale(self, response: Response) -> str:
        """Extract regional regulation type."""
        tipo_indicators = response.css(
            ".tipo::text, "
            ".categoria::text"
        ).getall()
        
        for text in tipo_indicators:
            if text:
                text_lower = text.lower()
                if "legge regionale" in text_lower:
                    return "Legge Regionale"
                elif "delibera" in text_lower:
                    return "Delibera Regionale"
                elif "regolamento" in text_lower:
                    return "Regolamento Regionale"
                elif "dgr" in text_lower:
                    return "DGR"
        
        return "Norma Regionale"
    
    def _extract_numero(self, response: Response) -> str | None:
        """Extract regulation number."""
        import re
        
        numero_indicators = response.css(
            ".numero::text, "
            ".metadata::text"
        ).getall()
        
        for text in numero_indicators:
            if text:
                match = re.search(r"n\.?\s*(\d+)", text, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        return None
    
    def _extract_date(self, response: Response) -> str | None:
        """Extract regulation date."""
        date_selectors = [
            ".data::text, "
            ".data-approvazione::text, "
            "meta[name='data']::attr(content)",
        ]
        
        for selector in date_selectors:
            value = response.css(selector).get()
            if value:
                return self._parse_date(value)
        
        return None
    
    def _extract_testo(self, response: Response) -> str:
        """Extract regulation text."""
        testo_parts = response.css(
            ".testo p::text, "
            ".content p::text, "
            "article p::text"
        ).getall()
        
        testo = "\n\n".join(p.strip() for p in testo_parts if p.strip())
        
        if not testo:
            testo = response.css(
                ".testo::text, "
                ".content::text, "
                "article::text"
            ).get()
        
        return testo.strip() if testo else ""
    
    def _extract_provincia(self, response: Response) -> str | None:
        """Extract province from constraint page."""
        provincia = response.css(
            ".provincia::text, "
            "meta[name='provincia']::attr(content)"
        ).get()
        
        return provincia.strip() if provincia else None
    
    def _extract_comune(self, response: Response) -> str | None:
        """Extract municipality from constraint page."""
        comune = response.css(
            ".comune::text, "
            "meta[name='comune']::attr(content)"
        ).get()
        
        return comune.strip() if comune else None
    
    def _extract_tipo_zona(self, response: Response) -> str:
        """Extract constraint zone type."""
        tipo_indicators = response.css(
            ".tipo-zona::text, "
            ".categoria::text, "
            ".tipo-vincolo::text"
        ).getall()
        
        for text in tipo_indicators:
            if text:
                return text.strip()
        
        # Default based on page content
        title = self._extract_title(response).lower()
        if "sismica" in title:
            return "Zona Sismica"
        elif "idrogeologica" in title:
            return "Zona Idrogeologica"
        elif "paesaggio" in title or "paesaggistica" in title:
            return "Zona Paesaggistica"
        elif "piano" in title:
            return "Piano Regolatore"
        
        return "Vincolo Territoriale"
    
    def _extract_descrizione_vincolo(self, response: Response) -> str:
        """Extract constraint description."""
        description_parts = response.css(
            ".descrizione p::text, "
            ".content p::text, "
            "article p::text"
        ).getall()
        
        description = "\n\n".join(p.strip() for p in description_parts if p.strip())
        
        if not description:
            description = response.css(
                ".descrizione::text, "
                ".content::text"
            ).get()
        
        return description.strip() if description else ""
    
    def _extract_norma_riferimento(self, response: Response) -> str:
        """Extract reference regulation."""
        norma = response.css(
            ".norma-riferimento::text, "
            ".riferimento::text, "
            ".legge::text"
        ).get()
        
        return norma.strip() if norma else ""
    
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
