"""
Text chunking utilities for EdilEngine scraper.

Provides functions for splitting text into overlapping chunks
suitable for embedding generation.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


def count_tokens(text: str) -> int:
    """
    Estimate token count for text.
    
    Uses a simple approximation: ~4 characters per token
    for Italian text.
    
    Args:
        text: Text to count tokens
        
    Returns:
        Estimated token count
    """
    if not text:
        return 0
    
    # Simple approximation for Italian text
    # Average Italian word is ~5-6 characters + space
    # OpenAI tokenizer averages ~4 chars per token
    return len(text) // 4


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences.
    
    Handles Italian punctuation and common abbreviations.
    
    Args:
        text: Text to split
        
    Returns:
        List of sentences
    """
    if not text:
        return []
    
    # Protect common abbreviations
    abbreviations = [
        "Sig.", "Sig.ra", "Spett.", "Egr.", "Gent.",
        "Prof.", "Prof.ssa", "Dott.", "Dott.ssa",
        "Ing.", "Arch.", "Avv.", "Rag.",
        "art.", "comm.", "lett.", "n.", "nr.",
        "D.Lgs.", "D.P.R.", "D.M.", "L.", "c.", "co.",
    ]
    
    protected_text = text
    for i, abbr in enumerate(abbreviations):
        protected_text = protected_text.replace(abbr, f"__ABBR{i}__")
    
    # Split on sentence boundaries
    # Italian sentences end with . ! ? followed by space or newline
    sentences = re.split(r"(?<=[.!?])\s+", protected_text)
    
    # Restore abbreviations
    sentences = [
        sentence.replace(f"__ABBR{i}__", abbr)
        for sentence in sentences
        for i, abbr in enumerate(abbreviations)
    ]
    
    # Filter empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences


def split_into_paragraphs(text: str) -> list[str]:
    """
    Split text into paragraphs.
    
    Args:
        text: Text to split
        
    Returns:
        List of paragraphs
    """
    if not text:
        return []
    
    # Split on double newlines
    paragraphs = re.split(r"\n\s*\n", text)
    
    # Filter empty paragraphs
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    return paragraphs


def chunk_text(
    text: str,
    chunk_size: int = 512,
    overlap: int = 50,
    min_chunk_size: int = 50,
) -> list[str]:
    """
    Split text into overlapping chunks.
    
    Uses a hierarchical approach:
    1. Split into paragraphs
    2. If paragraph is too large, split into sentences
    3. Combine sentences/paragraphs into chunks of target size
    4. Apply overlap between chunks
    
    Args:
        text: Text to chunk
        chunk_size: Target chunk size in tokens
        overlap: Number of overlapping tokens between chunks
        min_chunk_size: Minimum chunk size in tokens
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    # Estimate character sizes based on token sizes
    # ~4 chars per token for Italian
    chunk_chars = chunk_size * 4
    overlap_chars = overlap * 4
    min_chunk_chars = min_chunk_size * 4
    
    chunks = []
    
    # First, split into paragraphs
    paragraphs = split_into_paragraphs(text)
    
    if not paragraphs:
        return []
    
    # Group paragraphs into chunks
    current_chunk = []
    current_length = 0
    
    for paragraph in paragraphs:
        para_length = len(paragraph)
        
        # If single paragraph is larger than chunk_size, split it
        if para_length > chunk_chars:
            # If we have content in current chunk, save it first
            if current_chunk:
                chunk_text_item = " ".join(current_chunk)
                if len(chunk_text_item) >= min_chunk_chars:
                    chunks.append(chunk_text_item)
                current_chunk = []
                current_length = 0
            
            # Split large paragraph into sentences
            sentences = split_into_sentences(paragraph)
            
            sentence_chunk = []
            sentence_length = 0
            
            for sentence in sentences:
                sent_length = len(sentence)
                
                if sentence_length + sent_length > chunk_chars:
                    # Save current sentence chunk
                    if sentence_chunk:
                        chunk_text_item = " ".join(sentence_chunk)
                        if len(chunk_text_item) >= min_chunk_chars:
                            chunks.append(chunk_text_item)
                    
                    # Start new chunk with overlap
                    if overlap_chars > 0 and sentence_chunk:
                        # Get last part of previous chunk for overlap
                        overlap_text = " ".join(sentence_chunk[-3:])  # Last ~3 sentences
                        sentence_chunk = [overlap_text]
                        sentence_length = len(overlap_text)
                    else:
                        sentence_chunk = []
                        sentence_length = 0
                
                sentence_chunk.append(sentence)
                sentence_length += sent_length
            
            # Don't forget the last sentence chunk
            if sentence_chunk:
                chunk_text_item = " ".join(sentence_chunk)
                if len(chunk_text_item) >= min_chunk_chars:
                    chunks.append(chunk_text_item)
        
        # Normal paragraph - add to current chunk
        else:
            if current_length + para_length > chunk_chars:
                # Save current chunk
                chunk_text_item = " ".join(current_chunk)
                if len(chunk_text_item) >= min_chunk_chars:
                    chunks.append(chunk_text_item)
                
                # Start new chunk with overlap
                if overlap_chars > 0 and current_chunk:
                    # Calculate overlap in characters
                    overlap_text = " ".join(current_chunk)
                    overlap_text = overlap_text[-overlap_chars:]
                    # Try to break at word boundary
                    if " " in overlap_text:
                        overlap_text = overlap_text.split(" ", 1)[1]
                    current_chunk = [overlap_text]
                    current_length = len(overlap_text)
                else:
                    current_chunk = []
                    current_length = 0
            
            current_chunk.append(paragraph)
            current_length += para_length
    
    # Don't forget the last chunk
    if current_chunk:
        chunk_text_item = " ".join(current_chunk)
        if len(chunk_text_item) >= min_chunk_chars:
            chunks.append(chunk_text_item)
    
    # If no chunks were created, return the whole text as one chunk
    if not chunks and text:
        chunks = [text]
    
    logger.debug(f"Created {len(chunks)} chunks from {len(text)} characters")
    return chunks


def chunk_text_semantic(
    text: str,
    chunk_size: int = 512,
    overlap: int = 50,
) -> list[str]:
    """
    Split text into semantic chunks.
    
    Attempts to preserve semantic boundaries (paragraphs, sections)
    while respecting chunk size limits.
    
    Args:
        text: Text to chunk
        chunk_size: Target chunk size in tokens
        overlap: Number of overlapping tokens between chunks
        
    Returns:
        List of semantic text chunks
    """
    if not text:
        return []
    
    # Use the standard chunking for now
    # Can be enhanced with NLP-based semantic splitting
    return chunk_text(text, chunk_size=chunk_size, overlap=overlap)


def merge_small_chunks(
    chunks: list[str],
    min_size: int = 100,
    max_size: int = 512,
) -> list[str]:
    """
    Merge small consecutive chunks.
    
    Args:
        chunks: List of chunks to merge
        min_size: Minimum chunk size in tokens
        max_size: Maximum chunk size in tokens
        
    Returns:
        List of merged chunks
    """
    if not chunks:
        return []
    
    merged = []
    current_chunk = ""
    
    for chunk in chunks:
        chunk_tokens = count_tokens(chunk)
        current_tokens = count_tokens(current_chunk)
        
        if current_tokens + chunk_tokens <= max_size and current_tokens < min_size:
            # Merge with current chunk
            current_chunk = f"{current_chunk} {chunk}".strip()
        else:
            # Save current chunk and start new one
            if current_chunk:
                merged.append(current_chunk)
            current_chunk = chunk
    
    # Don't forget the last chunk
    if current_chunk:
        merged.append(current_chunk)
    
    return merged
