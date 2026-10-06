import re
from typing import List, Dict, Any

def calculate_hit_rate(retrieved_chunks: List[Any], expected_substrings: List[str]) -> float:
    if not expected_substrings:
        return 1.0 if not retrieved_chunks else 0.0
    for chunk in retrieved_chunks:
        if hasattr(chunk, 'content'):
            content = chunk.content
        else:
            content = chunk.chunk_text if hasattr(chunk, 'chunk_text') else ''
        for expected in expected_substrings:
            if expected.lower() in content.lower():
                return 1.0
    return 0.0

def calculate_chunk_recall(retrieved_chunks: List[Any], expected_substrings: List[str]) -> float:
    if not expected_substrings:
        return 1.0 if not retrieved_chunks else 0.0
    found = set()
    for chunk in retrieved_chunks:
        if hasattr(chunk, 'content'):
            content = chunk.content
        else:
            content = chunk.chunk_text if hasattr(chunk, 'chunk_text') else ''
        for expected in expected_substrings:
            if expected.lower() in content.lower():
                found.add(expected)
    return len(found) / len(expected_substrings)

def calculate_fact_coverage(answer: str, expected_facts: List[str]) -> float:
    if not expected_facts:
        return 1.0
    found = 0
    answer_lower = answer.lower()
    for fact in expected_facts:
        if fact.lower() in answer_lower:
            found += 1
    return found / len(expected_facts)

def calculate_groundedness(answer: str, expected_facts: List[str], retrieved_chunks: List[Any]) -> Dict[str, float]:
    if not expected_facts:
        return {"supported_fact_ratio": 1.0, "hallucination_rate": 0.0}
    facts_in_answer = [f for f in expected_facts if f.lower() in answer.lower()]
    if not facts_in_answer:
        return {"supported_fact_ratio": 0.0, "hallucination_rate": 0.0}
    
    combined_context = ""
    for c in retrieved_chunks:
        if hasattr(c, 'content'):
            combined_context += c.content.lower() + " "
        else:
            combined_context += getattr(c, 'chunk_text', '').lower() + " "
    
    supported = 0
    for fact in facts_in_answer:
        if fact.lower() in combined_context:
            supported += 1
    supported_ratio = supported / len(facts_in_answer)
    return {"supported_fact_ratio": supported_ratio, "hallucination_rate": 1.0 - supported_ratio}

def evaluate_citations(has_extraction: bool, raw_citations_text: str, valid_chunk_map: Dict[str, Any], retrieved_chunks: List[Any], expected_substrings: List[str]) -> Dict[str, float]:
    extraction_success_rate = 1.0 if has_extraction else 0.0
    if not has_extraction:
        return {
            "extraction_success_rate": extraction_success_rate,
            "structural_validity_rate": 0.0,
            "authorization_validity_rate": 0.0,
            "citation_support_rate": 0.0
        }
    
    # Structural validity
    raw_citations_list = [c.strip(" []") for c in raw_citations_text.replace(',', ' ').split() if c.strip(" []")]
    if not raw_citations_list:
        return {
            "extraction_success_rate": extraction_success_rate,
            "structural_validity_rate": 0.0,
            "authorization_validity_rate": 0.0,
            "citation_support_rate": 0.0
        }
    
    # 36 char UUID length check
    structurally_valid = [c for c in raw_citations_list if len(c) == 36]
    structural_validity_rate = len(structurally_valid) / len(raw_citations_list)
    
    if not structurally_valid:
        return {
            "extraction_success_rate": extraction_success_rate,
            "structural_validity_rate": structural_validity_rate,
            "authorization_validity_rate": 0.0,
            "citation_support_rate": 0.0
        }
    
    authorized = [c for c in structurally_valid if c in valid_chunk_map]
    auth_validity_rate = len(authorized) / len(structurally_valid)
    
    if not authorized:
        return {
            "extraction_success_rate": extraction_success_rate,
            "structural_validity_rate": structural_validity_rate,
            "authorization_validity_rate": auth_validity_rate,
            "citation_support_rate": 0.0
        }
    
    supported_citations = 0
    for cit in authorized:
        chunk_obj = valid_chunk_map[cit]
        content = chunk_obj.content if hasattr(chunk_obj, 'content') else getattr(chunk_obj, 'chunk_text', '')
        for expected in expected_substrings:
            if expected.lower() in content.lower():
                supported_citations += 1
                break
    
    support_rate = supported_citations / len(authorized)
    return {
        "extraction_success_rate": extraction_success_rate,
        "structural_validity_rate": structural_validity_rate,
        "authorization_validity_rate": auth_validity_rate,
        "citation_support_rate": support_rate
    }

