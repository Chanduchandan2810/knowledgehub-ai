import asyncio
import io
import pymupdf
from typing import List, Dict, Any
from app.core.config import settings

def _extract_pdf_sync(file_bytes: bytes) -> List[Dict[str, Any]]:
    pages_data = []
    
    # Open PDF from bytes
    with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
        if doc.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported")
            
        if len(doc) > settings.MAX_PAGE_COUNT:
            raise ValueError(f"Document exceeds maximum page limit ({settings.MAX_PAGE_COUNT})")
            
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            
            pages_data.append({
                "page_number": page_num + 1,
                "text": text
            })
            
    return pages_data

async def extract_pdf(file_bytes: bytes) -> List[Dict[str, Any]]:
    """Extracts text from PDF bytes asynchronously by offloading to a thread pool."""
    return await asyncio.to_thread(_extract_pdf_sync, file_bytes)

async def extract_txt(file_bytes: bytes) -> List[Dict[str, Any]]:
    """Extracts text from TXT bytes."""
    try:
        text = file_bytes.decode('utf-8')
        return [{"page_number": 1, "text": text}]
    except UnicodeDecodeError:
        raise ValueError("Invalid text file. Must be UTF-8 encoded text.")
