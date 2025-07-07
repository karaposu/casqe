
from .schemes import SearchQueryEnrichmentRequestObject, SearchQueryEnrichmentResultObject, SearchQueryEnrichmentOperation, BasicEnrichedQueryCandidate, AdvancedEnrichedQueryCandidate,UnifiedQueryCandidate
from .myllmservice import MyLLMService
from typing import List, Dict, Callable, Optional
from dataclasses import dataclass, field



def merge_candidates(
    basic: List[BasicEnrichedQueryCandidate],
    advanced: List[AdvancedEnrichedQueryCandidate],
    top_n: Optional[int] = None
) -> List[UnifiedQueryCandidate]:
    """
    Merge and deduplicate candidates from basic and advanced enrichment.
    Returns unified list sorted by score.
    """
    merged: dict[str, UnifiedQueryCandidate] = {}

    # ---------- basic ------------------------------------------------------
    for b in basic:
        q = b.combined
        if not q:  # skip filtered-out items
            continue
        cand = UnifiedQueryCandidate(
            query=q,
            score=b.combined_score,
            explanation=None,
            origin="basic",
        )
        key = q.lower()
        merged[key] = max(cand, merged.get(key, cand), key=lambda x: x.score)

    # ---------- advanced ---------------------------------------------------
    for a in advanced:
        q = a.query
        if not q:
            continue
        cand = UnifiedQueryCandidate(
            query=q,
            score=a.score,
            explanation=a.explanation,
            origin="advanced",
        )
        key = q.lower()
        merged[key] = max(cand, merged.get(key, cand), key=lambda x: x.score)

    # ---------- final list -------------------------------------------------
    result = sorted(merged.values(), key=lambda x: x.score, reverse=True)
    if top_n:
        result = result[:top_n]
    return result