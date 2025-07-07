# casqe/schemes.py

from typing import List
from dataclasses import dataclass


from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass

class SearchQueryEnrichmentRequestObject:
    
    query: str
    identifier_context: Optional[str] = None 
    search_reason_context: Optional[str] = None 
    text_rules: Optional[str] = None 
    score_filter: Optional[Any] = None 
    how_many: Optional[Any] = None 
    use_thinking: Optional[Any] = None 
    use_basic_enrichment: bool = False
    use_advanced_enrichment: bool = False


class SearchQueryEnrichmentResultObject:
    
    enriched_query: str
    explanation: Optional[str] = None 
    rank: Optional[Any] = None 
    score: Optional[Any] = None 


class SearchQueryEnrichmentOperation:
    
    queries: str
    query_object: Optional[str] = None 
    generation_result: Optional[Any] = None 
    elapsed_time: Optional[Any] = None 




@dataclass
class UnifiedQueryCandidate:
    query: str
    score: float
    explanation: Optional[str] = None
    origin: str = "basic"          # "basic" | "advanced"
    
    def __str__(self) -> str:
        return f"[{self.origin}] {self.query}  (score={self.score:.3f})"

@dataclass
class AdvancedEnrichedQueryCandidate:
    enriched_query: str          # ← renamed
    score: float
    explanation: Optional[str] = None

    def __str__(self):
        return f"{self.enriched_query}, score={self.score:.3f}"
    __repr__ = __str__
  

    
    def __str__(self) -> str:
        return f"{self.query}, score={self.score:.3f}, explanation={self.explanation}"
    __repr__ = __str__

    


@dataclass
class BasicEnrichedQueryCandidate:
    # ── core pieces ─────────────────────────────────────────────
    identifier: str
    identifier_score: float

    platform: Optional[str] = None
    platform_score: Optional[float] = None

    entity: Optional[str] = None
    entity_score: Optional[float] = None

    # ── derived (populated by combine) ─────────────────────────
    combined: str | None = field(init=False, default=None)
    combined_score: float | None = field(init=False, default=None)

    # -----------------------------------------------------------
    def combine(self) -> "BasicEnrichmentDataElement":
        """Generate the final query and score in one pass."""
        parts = [self.identifier]
        if self.platform:
            parts.append(self.platform)
        if self.entity:
            parts.append(self.entity)

        # ready-made string
        self.combined = " ".join(parts)

        # simple product of available scores
        score = self.identifier_score
        if self.platform_score is not None:
            score *= self.platform_score
        if self.entity_score is not None:
            score *= self.entity_score
        self.combined_score = round(score, 3)

        return self  # enables inline use

    # friendly printout
    def __str__(self) -> str:
        return (
            f"{self.combined}, combined_scr={self.combined_score:.3f}, "
            f"identifier={self.identifier}, platform={self.platform}, entity={self.entity}, "
            f"identifier_scr={self.identifier_score:.2f}, "
            f"platform_scr={self.platform_score}, entity_scr={self.entity_score}"
        )

    __repr__ = __str__

