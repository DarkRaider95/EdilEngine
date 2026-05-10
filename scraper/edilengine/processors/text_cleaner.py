"""
Text cleaning utilities for EdilEngine scraper.

Provides functions for cleaning HTML content, normalizing text,
and handling Italian language specific encoding issues.
"""

import html
import logging
import re
from typing import Optional

from bs4 import BeautifulSoup, NavigableString, Tag

logger = logging.getLogger(__name__)


def remove_html_tags(html_content: str) -> str:
    """
    Remove all HTML tags from content.
    
    Args:
        html_content: HTML string to clean
        
    Returns:
        Plain text without HTML tags
    """
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, "lxml")
    
    # Remove script and style elements
    for element in soup(["script", "style", "noscript", "iframe"]):
        element.decompose()
    
    # Get text content
    text = soup.get_text(separator=" ")
    return text


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text.
    
    - Replace multiple spaces with single space
    - Replace multiple newlines with double newline
    - Strip leading/trailing whitespace
    
    Args:
        text: Text to normalize
        
    Returns:
        Text with normalized whitespace
    """
    if not text:
        return ""
    
    # Replace tabs with spaces
    text = text.replace("\t", " ")
    
    # Replace multiple spaces with single space
    text = re.sub(r" +", " ", text)
    
    # Replace multiple newlines with double newline (paragraph break)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    
    # Remove spaces at start/end of lines
    text = re.sub(r" *\n *", "\n", text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def decode_html_entities(text: str) -> str:
    """
    Decode HTML entities in text.
    
    Args:
        text: Text with HTML entities
        
    Returns:
        Text with decoded entities
    """
    if not text:
        return ""
    
    return html.unescape(text)


def remove_noise(text: str) -> str:
    """
    Remove common noise patterns from text.
    
    - Remove page numbers
    - Remove header/footer artifacts
    - Remove excessive punctuation
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove page numbers (e.g., "- 5 -", "Pagina 5", etc.)
    text = re.sub(r"-\s*\d+\s*-", "", text)
    text = re.sub(r"\bPagina\s*\d+\b", "", text, flags=re.IGNORECASE)
    
    # Remove excessive punctuation
    text = re.sub(r"([.,;:!?])\1{2,}", r"\1", text)
    
    # Remove lines that are just numbers or dashes
    lines = text.split("\n")
    lines = [
        line for line in lines
        if not re.match(r"^\s*[-=_]+\s*$", line)
        and not re.match(r"^\s*\d+\s*$", line)
    ]
    text = "\n".join(lines)
    
    return text


def fix_italian_encoding(text: str) -> str:
    """
    Fix common Italian encoding issues.
    
    - Fix accented characters
    - Fix apostrophes
    
    Args:
        text: Text with potential encoding issues
        
    Returns:
        Text with fixed encoding
    """
    if not text:
        return ""
    
    # Common encoding fixes for Italian
    replacements = {
        "Ã ": "À",
        "Ã ": "È",
        "Ã©": "É",
        "Ã¬": "Ì",
        "Ã²": "Ò",
        "Ã¹": "Ù",
        "à": "à",
        "è": "è",
        "é": "é",
        "ì": "ì",
        "ò": "ò",
        "ù": "ù",
        "â€œ": '"',
        "â€": '"',
        "â€™": "'",
        "â€˜": "'",
    }
    
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    
    return text


def clean_html_text(
    html_content: str,
    remove_tags: bool = True,
    normalize: bool = True,
    decode_entities: bool = True,
    remove_noise_text: bool = True,
    fix_encoding: bool = True,
) -> str:
    """
    Complete text cleaning pipeline for HTML content.
    
    Args:
        html_content: Raw HTML content
        remove_tags: Whether to remove HTML tags
        normalize: Whether to normalize whitespace
        decode_entities: Whether to decode HTML entities
        remove_noise_text: Whether to remove noise patterns
        fix_encoding: Whether to fix encoding issues
        
    Returns:
        Cleaned text
    """
    if not html_content:
        return ""
    
    text = html_content
    
    try:
        if remove_tags:
            text = remove_html_tags(text)
        
        if decode_entities:
            text = decode_html_entities(text)
        
        if fix_encoding:
            text = fix_italian_encoding(text)
        
        if remove_noise_text:
            text = remove_noise(text)
        
        if normalize:
            text = normalize_whitespace(text)
        
    except Exception as e:
        logger.warning(f"Error cleaning text: {e}")
        # Return basic cleanup if full pipeline fails
        text = re.sub(r"<[^>]+>", " ", html_content)
        text = normalize_whitespace(text)
    
    return text


def extract_paragraphs(html_content: str) -> list[str]:
    """
    Extract paragraphs from HTML content.
    
    Args:
        html_content: HTML content
        
    Returns:
        List of paragraph texts
    """
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, "lxml")
    
    # Remove script and style elements
    for element in soup(["script", "style", "noscript", "iframe"]):
        element.decompose()
    
    paragraphs = []
    for p in soup.find_all(["p", "div", "article", "section"]):
        text = p.get_text(separator=" ", strip=True)
        if text and len(text) > 10:  # Filter out very short paragraphs
            paragraphs.append(text)
    
    return paragraphs


def extract_sections(html_content: str) -> dict[str, str]:
    """
    Extract sections from HTML content based on headings.
    
    Args:
        html_content: HTML content
        
    Returns:
        Dictionary mapping section titles to content
    """
    if not html_content:
        return {}
    
    soup = BeautifulSoup(html_content, "lxml")
    
    # Remove script and style elements
    for element in soup(["script", "style", "noscript", "iframe"]):
        element.decompose()
    
    sections = {}
    current_section = "introduction"
    current_content = []
    
    for element in soup.descendants:
        if isinstance(element, Tag):
            if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                # Save previous section
                if current_content:
                    sections[current_section] = " ".join(current_content)
                    current_content = []
                
                # Start new section
                current_section = element.get_text(strip=True)
            
            elif element.name in ["p", "div", "article", "section"]:
                text = element.get_text(separator=" ", strip=True)
                if text:
                    current_content.append(text)
    
    # Save last section
    if current_content:
        sections[current_section] = " ".join(current_content)
    
    return sections
