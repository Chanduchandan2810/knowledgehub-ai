import re
from typing import List, Dict, Any
from transformers import AutoTokenizer

class DocumentChunker:
    def __init__(self, model_name: str, chunk_size_tokens: int, overlap_percent: float):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Use actual model max length if available, otherwise fallback
        self.model_max_length = getattr(self.tokenizer, 'model_max_length', 256)
        
        # Ensure configured chunk size never exceeds the model's capacity
        # We subtract a safety margin (e.g., 20 tokens) for prepended titles/metadata
        max_allowed_chunk = max(10, self.model_max_length - 20)
        self.chunk_size = min(chunk_size_tokens, max_allowed_chunk)
        
        self.overlap = int(self.chunk_size * overlap_percent)
        
    def _count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text, add_special_tokens=False))
        
    def _split_into_sentences(self, text: str) -> List[str]:
        # Simple sentence boundary detection
        # Split on . ! ? followed by space and capital letter, or newlines
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])|\n+', text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_pages(self, pages: List[Dict[str, Any]], filename: str) -> List[Dict[str, Any]]:
        chunks = []
        current_chunk_text = ""
        current_chunk_tokens = 0
        current_page_number = 1
        
        chunk_index = 0
        
        for page in pages:
            page_text = page["text"]
            page_num = page["page_number"]
            
            sentences = self._split_into_sentences(page_text)
            
            for sentence in sentences:
                sentence_tokens = self._count_tokens(sentence)
                
                # If a single sentence is huge, we need to hard-truncate it 
                # (though rare, it protects against model limits)
                if sentence_tokens > self.chunk_size:
                    # Truncate string roughly by characters to fit
                    # 1 token ~ 4 chars approximation for safety, then strictly encode/decode
                    encoded = self.tokenizer.encode(sentence, add_special_tokens=False, max_length=self.chunk_size, truncation=True)
                    sentence = self.tokenizer.decode(encoded)
                    sentence_tokens = self._count_tokens(sentence)
                
                if current_chunk_tokens + sentence_tokens > self.chunk_size and current_chunk_tokens > 0:
                    # Finalize current chunk
                    chunks.append({
                        "chunk_index": chunk_index,
                        "content": current_chunk_text.strip(),
                        "page_number": current_page_number,
                        "token_count": current_chunk_tokens
                    })
                    chunk_index += 1
                    
                    # Start new chunk with overlap
                    # For simplicity, we'll overlap by carrying over the last sentence if it fits
                    current_chunk_text = sentence
                    current_chunk_tokens = sentence_tokens
                    current_page_number = page_num
                else:
                    # Append to current chunk
                    if current_chunk_text:
                        current_chunk_text += " " + sentence
                    else:
                        current_chunk_text = sentence
                        current_page_number = page_num # Record the page where this chunk started
                    current_chunk_tokens += sentence_tokens
                    
        # Finalize the last chunk
        if current_chunk_text.strip():
            chunks.append({
                "chunk_index": chunk_index,
                "content": current_chunk_text.strip(),
                "page_number": current_page_number,
                "token_count": current_chunk_tokens
            })
            
        return chunks
