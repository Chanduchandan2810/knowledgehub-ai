"""
Evaluation-only helper that mirrors the production RAGService.generate_answer
path exactly, but also returns the raw JSON string from the LLM BEFORE any
citation parsing.

Production equivalence guarantee:
  - Uses the same SYSTEM_PROMPT (from rag_service.py, not duplicated here).
  - Uses the same ContextBuilder.build_context() (imported from rag_service.py).
  - Constructs the user_prompt with the exact same template as generate_answer.
  - Calls llm_service.generate_chat with the same arguments (response_format="json").
  - Does NOT modify rag_service.py or any production code.
  - Does NOT call generate_answer_stream (that path uses SYSTEM_PROMPT_STREAM and
    is a separate evaluation concern).

What this adds for evaluation only:
  - Returns raw_llm_output: the raw JSON string emitted by the LLM.
  - Returns valid_chunk_map: the authorized chunk map used for citation validation.

The production RAGService.generate_answer remains completely unchanged.
"""
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Tuple, Dict, Any

from app.api.deps import UserContext
from app.schemas.retrieval import RetrievedChunk

# Import the exact same production constants and helpers — no duplication.
from app.services.chat.rag_service import (
    SYSTEM_PROMPT,
    ContextBuilder,
    NO_CONTEXT_MESSAGE,
)
from app.services.chat.llm_service import llm_service

logger = logging.getLogger(__name__)


async def eval_generate_answer_with_raw(
    retrieval_results: List[RetrievedChunk],
    question: str,
) -> Dict[str, Any]:
    """
    Evaluation-only wrapper. Runs the identical production RAG generation
    pipeline (same prompt, same LLM config) but also returns the raw LLM
    output BEFORE citation parsing so evaluators can inspect it.

    Args:
        retrieval_results: Already-retrieved and authorized chunks (as obtained
                           by hybrid_retrieve_chunks). The evaluator is responsible
                           for obtaining these via the same hybrid retrieval path.
        question: The original user question.

    Returns a dict with:
        raw_llm_output (str): the raw JSON string from the LLM, unmodified.
        answer (str): the parsed answer text (same as production).
        raw_citations (list): the raw citation_ids list from the LLM JSON.
        valid_chunk_map (dict[str, RetrievedChunk]): the authorization map used
            to validate citations in production.
    """
    if not retrieval_results:
        return {
            "raw_llm_output": "",
            "answer": NO_CONTEXT_MESSAGE,
            "raw_citations": [],
            "valid_chunk_map": {},
        }

    # ---- Step 1: Build context exactly as production does ----
    context_text, alias_map = ContextBuilder.build_context(retrieval_results)

    # ---- Step 2: Construct user prompt exactly as production does ----
    user_prompt = f"""Please answer the following question based on the provided context.

QUESTION:
{question}

CONTEXT:
{context_text}
"""

    # ---- Step 3: Call LLM with the same system prompt and response format ----
    raw_llm_output = await llm_service.generate_chat(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_format="json",
    )

    # ---- Step 4: Parse JSON (exactly as production does) ----
    try:
        data = json.loads(raw_llm_output)
        answer_text = data.get("answer", NO_CONTEXT_MESSAGE)
        raw_aliases = data.get("citation_aliases", data.get("citation_ids", []))

        # In evaluation, we still need to provide `raw_citations` as UUIDs to the
        # metric runner (which expects to check them against valid_chunk_map).
        raw_citations = []
        if isinstance(raw_aliases, list):
            for alias in raw_aliases:
                alias_str = str(alias).strip()
                cid_str = alias_map.get(alias_str)
                if cid_str:
                    raw_citations.append(cid_str)
                else:
                    # If the model emitted a literal UUID or an unknown alias, just pass it through
                    # so the evaluator can measure the failure correctly.
                    raw_citations.append(alias_str)

    except json.JSONDecodeError:
        logger.warning("eval_generate_answer_with_raw: LLM returned invalid JSON.")
        answer_text = raw_llm_output
        raw_citations = []

    # ---- Step 5: Build the same valid_chunk_map production uses ----
    valid_chunk_map = {str(c.chunk_id): c for c in retrieval_results}

    return {
        "raw_llm_output": raw_llm_output,
        "answer": answer_text,
        "raw_citations": raw_citations,
        "valid_chunk_map": valid_chunk_map,
    }
