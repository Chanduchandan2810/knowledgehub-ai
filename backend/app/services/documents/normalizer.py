import re

def normalize_text(text: str) -> str:
    """
    Cleans and normalizes extracted text.
    - Removes null bytes
    - Normalizes excessive whitespace/newlines
    - Trims leading/trailing whitespace
    """
    if not text:
        return ""
        
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Normalize unicode spaces to standard space
    text = text.replace('\xa0', ' ')
    
    # Collapse multiple spaces into one
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Collapse multiple newlines into max two (preserves paragraph breaks)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()
