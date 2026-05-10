"""
Processors package for EdilEngine scraper.

Provides text cleaning, chunking, and embedding utilities.
"""

from edilengine.processors.text_cleaner import clean_html_text
from edilengine.processors.chunker import chunk_text
from edilengine.processors.embedder import Embedder

__all__ = [
    "clean_html_text",
    "chunk_text",
    "Embedder",
]
