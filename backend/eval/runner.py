"""
Phase 8 evaluation runner.

Evaluation pipeline:
  1. Seed is handled by eval.seed (isolated KnowledgeHub Evaluation Organization).
  2. For each dataset case:
     a. Retrieve chunks via _vector_retrieve (baseline).
     b. Retrieve chunks via hybrid_retrieve_chunks (production Phase 7 path).
     c. Generate RAG answer via eval.rag_eval_helper.eval_generate_answer_with_raw,
        which uses the EXACT same production RAG prompt, ContextBuilder, and LLM
        configuration as RAGService.generate_answer — but also returns the raw LLM
        JSON string for citation metric evaluation.
     d. Score retrieval, answer quality, groundedness, and citation pipeline.

Production equivalence:
  - The generation helper imports SYSTEM_PROMPT, ContextBuilder, NO_CONTEXT_MESSAGE
    directly from rag_service.py. No prompt duplication.
  - Retrieval uses hybrid_retrieve_chunks (same function called by production).
  - LLM call uses generate_chat with response_format='json' (same as production).

Evaluation-only additions (not present in production):
  - raw_llm_output capture for genuine citation extraction measurement.
  - explicit DocumentPermission rows in the Eval Org (required because of the
    known hybrid_service.py INNER JOIN behavior — see eval_report.md).
"""
import json
import os
import asyncio
import uuid
import re
from typing import Dict, Any, List

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.api.deps import UserContext
from app.services.retrieval.hybrid_service import _vector_retrieve, hybrid_retrieve_chunks
from app.services.documents.embeddings import get_embedding_service
from app.models.admin import Admin
from app.models.employee import Employee

from eval.seed import EVAL_ORG_ID
from eval.rag_eval_helper import eval_generate_answer_with_raw
from eval.metrics import (
    calculate_hit_rate,
    calculate_chunk_recall,
    calculate_fact_coverage,
    calculate_groundedness,
    evaluate_citations,
)

DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset.json")


async def run_evaluation():
    with open(DATASET_PATH, "r") as f:
        dataset = json.load(f)

    results = []
    embed_svc = get_embedding_service()

    async with AsyncSessionLocal() as db:
        # Resolve Eval Org user IDs
        admin_res = await db.execute(select(Admin.id).where(Admin.organization_id == EVAL_ORG_ID))
        eval_admin_id = admin_res.scalar_one()
        emp_res = await db.execute(select(Employee.id).where(Employee.organization_id == EVAL_ORG_ID))
        eval_emp_id = emp_res.scalar_one()

        for case in dataset:
            print(f"Running eval case: {case['case_id']}")

            # Build UserContext for this case using Eval Org identities
            user_id = eval_admin_id if case["role_required"] == "ADMIN" else eval_emp_id
            ctx = UserContext(
                user_id=user_id,
                auth_user_id=user_id,
                organization_id=EVAL_ORG_ID,
                role=case["role_required"],
                email="eval@local",
                full_name="Eval User",
            )

            # ---- 1. Baseline: Vector-only retrieval ----
            embeddings = await embed_svc.generate_embeddings([case["query"]])
            q_emb = embeddings[0]
            vector_tuples = await _vector_retrieve(q_emb, ctx, db, limit=5)
            vector_chunks = [t[0] for t in vector_tuples]
            vector_hit_rate = calculate_hit_rate(vector_chunks, case["expected_chunk_substrings"])
            vector_recall = calculate_chunk_recall(vector_chunks, case["expected_chunk_substrings"])

            # ---- 2. Production Phase 7: Hybrid retrieval ----
            hybrid_res = await hybrid_retrieve_chunks(case["query"], ctx, db)
            hybrid_chunks = hybrid_res.results
            hybrid_hit_rate = calculate_hit_rate(hybrid_chunks, case["expected_chunk_substrings"])
            hybrid_recall = calculate_chunk_recall(hybrid_chunks, case["expected_chunk_substrings"])

            # ---- 3. RAG Generation via production-equivalent helper ----
            # eval_generate_answer_with_raw uses the EXACT same production:
            #   - SYSTEM_PROMPT (from rag_service.py)
            #   - ContextBuilder.build_context() (from rag_service.py)
            #   - user_prompt template (identical to RAGService.generate_answer)
            #   - llm_service.generate_chat(response_format="json")
            # It adds ONLY: raw_llm_output exposure before JSON parsing.
            gen_result = await eval_generate_answer_with_raw(hybrid_chunks, case["query"])
            raw_llm_output = gen_result["raw_llm_output"]
            answer = gen_result["answer"]
            raw_citations_from_llm = gen_result["raw_citations"]
            valid_chunk_map = gen_result["valid_chunk_map"]

            # ---- 4. Answer quality metrics ----
            fact_coverage = calculate_fact_coverage(answer, case["expected_facts"])

            # ---- 5. Groundedness (deterministic string matching) ----
            groundedness_metrics = calculate_groundedness(answer, case["expected_facts"], hybrid_chunks)

            # ---- 6. No-Context Abstention ----
            abstention_success = 0.0
            if case["must_reject"]:
                no_ctx_phrases = [
                    "I couldn't find enough information",
                    "insufficient",
                    "not found in the available documents",
                    "could not be found",
                ]
                if any(p.lower() in answer.lower() for p in no_ctx_phrases):
                    abstention_success = 1.0

            # ---- 7. Citation pipeline metrics (genuine, from raw LLM output) ----
            # Determine if the LLM emitted citation_ids at all in the JSON output
            has_extraction = bool(raw_citations_from_llm) if isinstance(raw_citations_from_llm, list) else False

            # Raw citation text: the LLM-emitted IDs before any validation
            raw_citations_text = ", ".join(str(c) for c in raw_citations_from_llm) if raw_citations_from_llm else ""

            cit_metrics = evaluate_citations(
                has_extraction,
                raw_citations_text,
                valid_chunk_map,
                hybrid_chunks,
                case["expected_chunk_substrings"],
            )

            results.append({
                "case_id": case["case_id"],
                "category": case["category"],
                "vector_hit_rate": vector_hit_rate,
                "vector_recall": vector_recall,
                "hybrid_hit_rate": hybrid_hit_rate,
                "hybrid_recall": hybrid_recall,
                "fact_coverage": fact_coverage,
                "supported_fact_ratio": groundedness_metrics["supported_fact_ratio"],
                "hallucination_rate": groundedness_metrics["hallucination_rate"],
                "abstention_success": abstention_success,
                "citation_metrics": cit_metrics,
                "must_reject": case["must_reject"],
                "raw_citation_count": len(raw_citations_from_llm) if isinstance(raw_citations_from_llm, list) else 0,
            })

    return results


if __name__ == "__main__":
    asyncio.run(run_evaluation())
