"""
Scrapy Items for EdilEngine project.

Defines the data structures for scraped items from various sources.
"""

import scrapy


class LeggeItem(scrapy.Item):
    """
    Item representing a law/regulation from Italian legal sources.
    
    Fields:
        titolo: Title of the law
        tipo: Type of law (e.g., "Legge", "Decreto Legislativo", "DPR")
        numero: Law number
        data_emanazione: Date when the law was issued
        data_pubblicazione: Date when the law was published
        data_vigore: Date when the law came into effect
        autorita: Authority that issued the law
        testo_completo: Full text of the law
        url_fonte: Source URL
        categorie: List of categories associated with the law
        chunks: List of text chunks (added by ChunkingPipeline)
        embeddings: List of embeddings (added by EmbeddingPipeline)
    """
    titolo = scrapy.Field()
    tipo = scrapy.Field()
    numero = scrapy.Field()
    data_emanazione = scrapy.Field()
    data_pubblicazione = scrapy.Field()
    data_vigore = scrapy.Field()
    autorita = scrapy.Field()
    testo_completo = scrapy.Field()
    url_fonte = scrapy.Field()
    categorie = scrapy.Field()
    chunks = scrapy.Field()
    embeddings = scrapy.Field()


class IncentivoItem(scrapy.Item):
    """
    Item representing a building incentive/bonus.
    
    Fields:
        titolo: Title of the incentive
        descrizione: Description of the incentive
        ente_erogatore: Granting authority (e.g., "ENEA", "GSE", "MASE")
        tipo: Type of incentive (e.g., "Detrazione", "Conto Termico", "Superbonus")
        aliquota: Percentage rate if applicable
        scadenza: Expiration date
        requisiti: Requirements to access the incentive
        url_fonte: Source URL
    """
    titolo = scrapy.Field()
    descrizione = scrapy.Field()
    ente_erogatore = scrapy.Field()
    tipo = scrapy.Field()
    aliquota = scrapy.Field()
    scadenza = scrapy.Field()
    requisiti = scrapy.Field()
    url_fonte = scrapy.Field()


class VincoloItem(scrapy.Item):
    """
    Item representing a building constraint/restriction.
    
    Fields:
        regione: Region name
        provincia: Province name
        comune: Municipality name
        tipo_zona: Type of zone (e.g., "Sismica", "Idrogeologica", "Paesaggistica")
        descrizione: Description of the constraint
        norma_riferimento: Reference regulation
        url_fonte: Source URL
    """
    regione = scrapy.Field()
    provincia = scrapy.Field()
    comune = scrapy.Field()
    tipo_zona = scrapy.Field()
    descrizione = scrapy.Field()
    norma_riferimento = scrapy.Field()
    url_fonte = scrapy.Field()


class CategoriaItem(scrapy.Item):
    """
    Item representing a category for organizing laws.
    
    Fields:
        nome: Category name
        descrizione: Category description
        parent: Parent category (for hierarchical categories)
    """
    nome = scrapy.Field()
    descrizione = scrapy.Field()
    parent = scrapy.Field()
