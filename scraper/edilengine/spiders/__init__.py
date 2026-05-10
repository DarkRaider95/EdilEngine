"""
Spiders package for EdilEngine scraper.

Contains spiders for various Italian legal and regulatory sources.
"""

from edilengine.spiders.normattiva import NormattivaSpider
from edilengine.spiders.gazzetta_ufficiale import GazzettaUfficialeSpider
from edilengine.spiders.incentivi import IncentiviSpider
from edilengine.spiders.regionali import RegionaliSpider

__all__ = [
    "NormattivaSpider",
    "GazzettaUfficialeSpider",
    "IncentiviSpider",
    "RegionaliSpider",
]
