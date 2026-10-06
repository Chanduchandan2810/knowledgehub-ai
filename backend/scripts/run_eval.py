"""
Phase 8 evaluation entry point.

Usage:
    cd backend
    PYTHONPATH=. python scripts/run_eval.py

This script:
  1. Seeds the isolated KnowledgeHub Evaluation Organization (idempotent).
  2. Runs the evaluation suite against all dataset cases.
  3. Writes eval_report.md at the project root.

IMPORTANT: This script does not modify any production code paths.
"""
import asyncio
import os
import datetime

from eval.seed import seed_eval_db
from eval.runner import run_evaluation

REPORT_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'eval_report.md')


async def main():
    print('Seeding evaluation database...')
    await seed_eval_db()

    print('Running evaluation suite...')
    results = await run_evaluation()

    print('Calculating aggregates...')
    total_cases = len(results)

    categories = {}
    for r in results:
        categories[r['category']] = categories.get(r['category'], 0) + 1

    cat_str = '\n'.join([f'- {k}: {v} case(s)' for k, v in categories.items()])

    sum_v_hit = sum(r['vector_hit_rate'] for r in results)
    sum_v_rec = sum(r['vector_recall'] for r in results)
    sum_h_hit = sum(r['hybrid_hit_rate'] for r in results)
    sum_h_rec = sum(r['hybrid_recall'] for r in results)

    avg_v_hit = sum_v_hit / total_cases
    avg_v_rec = sum_v_rec / total_cases
    avg_h_hit = sum_h_hit / total_cases
    avg_h_rec = sum_h_rec / total_cases
    delta_hit = avg_h_hit - avg_v_hit
    delta_rec = avg_h_rec - avg_v_rec

    valid_facts_cases = [r for r in results if not r['must_reject']]
    rejection_cases = [r for r in results if r['must_reject']]

    sum_fact_cov = sum(r['fact_coverage'] for r in valid_facts_cases)
    sum_supported = sum(r['supported_fact_ratio'] for r in valid_facts_cases)
    sum_hallucination = sum(r['hallucination_rate'] for r in valid_facts_cases)
    avg_fact_cov = sum_fact_cov / max(1, len(valid_facts_cases))
    avg_supported = sum_supported / max(1, len(valid_facts_cases))
    avg_hallucination = sum_hallucination / max(1, len(valid_facts_cases))

    sum_abstention = sum(r['abstention_success'] for r in rejection_cases)
    avg_abstention = sum_abstention / max(1, len(rejection_cases))

    sum_cit_ext = sum(r['citation_metrics']['extraction_success_rate'] for r in results)
    sum_cit_struct = sum(r['citation_metrics']['structural_validity_rate'] for r in results)
    sum_cit_auth = sum(r['citation_metrics']['authorization_validity_rate'] for r in results)
    sum_cit_sup = sum(r['citation_metrics']['citation_support_rate'] for r in results)
    avg_cit_ext = sum_cit_ext / total_cases
    avg_cit_struct = sum_cit_struct / total_cases
    avg_cit_auth = sum_cit_auth / total_cases
    avg_cit_sup = sum_cit_sup / total_cases

    report = f'''# KnowledgeHub AI — Phase 8 Evaluation Report
Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Branch: phase-8

---

## Dataset Disclaimer

> **This evaluation uses {total_cases} manually curated cases.** Results are
> deterministic proofs of pipeline behavior for these specific cases. They are
> NOT statistically representative of production traffic at scale and must not
> be cited as aggregate performance statistics without a larger dataset.

## Dataset Composition
Total Cases: {total_cases}
{cat_str}

---

## Production RAG Path Being Evaluated

The evaluation exercises the **exact same production code paths** used in
`RAGService.generate_answer()`:

| Step | Production (rag_service.py) | Evaluation (rag_eval_helper.py) |
|------|----------------------------|----------------------------------|
| Retrieval | `hybrid_retrieve_chunks()` | Same function |
| Context builder | `ContextBuilder.build_context()` | Same import |
| System prompt | `SYSTEM_PROMPT` | Same import |
| User prompt template | Hard-coded in `generate_answer` | Identical copy |
| LLM call | `llm_service.generate_chat(response_format="json")` | Same call |
| Citation parsing | JSON parse → `citation_ids` field | Same parse logic |
| Evaluation addition | — | Raw JSON string captured before parse |

`rag_service.py` was **not modified**.

---

## 1. Retrieval Metrics (Vector Baseline vs Hybrid Phase 7)
- **Vector Hit Rate @5**: {avg_v_hit:.2%} ({sum_v_hit:.0f}/{total_cases})
- **Vector Recall @5**: {avg_v_rec:.2%} ({sum_v_rec:.0f}/{total_cases})
- **Hybrid Hit Rate @5**: {avg_h_hit:.2%} ({sum_h_hit:.0f}/{total_cases})
- **Hybrid Recall @5**: {avg_h_rec:.2%} ({sum_h_rec:.0f}/{total_cases})
- **Delta (Hybrid − Vector)**: {delta_hit:+.2%} Hit Rate, {delta_rec:+.2%} Recall

## 2. Answer Quality & Groundedness
*(Excluding must-reject cases: {len(valid_facts_cases)} answerable cases)*
- **Fact Coverage Rate**: {avg_fact_cov:.2%} ({sum_fact_cov:.0f}/{len(valid_facts_cases)})
- **Supported Fact Ratio**: {avg_supported:.2%} ({sum_supported:.0f}/{len(valid_facts_cases)}) — facts grounded in retrieved context
- **Hallucination Rate**: {avg_hallucination:.2%} ({sum_hallucination:.0f}/{len(valid_facts_cases)}) — facts in answer NOT found in context

*(No-context cases: {len(rejection_cases)} rejection cases)*
- **No-Context Abstention Rate**: {avg_abstention:.2%} ({sum_abstention:.0f}/{len(rejection_cases)})

## 3. Granular Citation Metrics
*Measured from raw LLM JSON output (citation_ids field), before validation.*
- **Citation Extraction Success** (LLM emitted non-empty citation_ids): {avg_cit_ext:.2%} ({sum_cit_ext:.0f}/{total_cases})
- **Citation Structural Validity** (IDs are 36-char UUIDs): {avg_cit_struct:.2%} ({sum_cit_struct:.0f}/{total_cases})
- **Citation Authorization Validity** (IDs match retrieved authorized chunks): {avg_cit_auth:.2%} ({sum_cit_auth:.0f}/{total_cases})
- **Citation Support Rate** (Authorized citations actually reference expected content): {avg_cit_sup:.2%} ({sum_cit_sup:.0f}/{total_cases})

*Note: The 1B model (`llama3.2:1b`) consistently truncates 36-character UUIDs,
causing structural validity failures. Production citation validation correctly
rejects these. This is a model capability limitation, not a validation defect.*

---

## Detailed Case Results

'''
    for r in results:
        report += f'''### Case: {r["case_id"]} ({r["category"]})
- Vector Recall: {r["vector_recall"]:.2%}
- Hybrid Recall: {r["hybrid_recall"]:.2%}
- Fact Coverage: {r["fact_coverage"]:.2%}
- Supported Fact Ratio: {r["supported_fact_ratio"]:.2%}
- Abstention Required: {r["must_reject"]} | Abstained: {"Yes" if r["abstention_success"] > 0 else "No"}
- LLM Emitted Citation IDs: {r["raw_citation_count"]} | Extracted: {"Yes" if r["citation_metrics"]["extraction_success_rate"] > 0 else "No"}

'''

    report += '''---

## Known Limitations / Findings

### 1. Dataset Size
The evaluation dataset contains 5 cases across 5 categories. Results are
deterministically correct for these cases but statistically insufficient to
characterize production performance.

### 2. LLM Citation ID Truncation (llama3.2:1b)
The local `llama3.2:1b` model cannot reliably emit full 36-character UUID
citation IDs. It typically emits 8-character truncated variants. Production
citation validation (strict UUID match) correctly rejects these. This is a
model limitation, not a defect in the citation validation pipeline.

### 3. hybrid_service.py INNER JOIN and AccessScope.ORGANIZATION
**Finding (Phase 8 — Evaluation):** The production `hybrid_retrieve_chunks`
function uses an `INNER JOIN` on the `document_permissions` table. As a result,
documents with `access_scope = ORGANIZATION` that do not have an explicit
`DocumentPermission` row are excluded from retrieval results, even though the
intent of `ORGANIZATION` scope is "visible to all members."

**Impact:** The current implementation only retrieves documents that have an
explicit permission row — effectively treating all documents as `RESTRICTED`
unless a permission row exists.

**Evaluation accommodation:** The evaluation seeder (`eval/seed.py`)
explicitly creates `DocumentPermission` rows for all evaluation documents,
matching the permission model that is currently supported by the retrieval
pipeline. This ensures the evaluation exercises a real, working permission
path and that retrieval results are meaningful.

**What has NOT been validated:** The `AccessScope.ORGANIZATION` scope behavior
("accessible to all org members without explicit rows") has not been validated,
because the current retrieval implementation does not support it. This is
documented here as a known Phase 7/8 finding for future remediation.

**Scope:** `hybrid_service.py` was NOT modified in Phase 8 per standing
directive.

'''

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f'Report generated at {REPORT_PATH}')


if __name__ == '__main__':
    asyncio.run(main())
