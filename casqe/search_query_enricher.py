# casqe/search_query_enricher.py
# to run python -m casqe.search_query_enricher

from __future__ import annotations
from typing import List, Dict, Optional, Any
import time
import asyncio

from .schemes import (
    SearchQueryEnrichmentRequestObject, 
    SearchQueryEnrichmentOperation, 
    BasicEnrichedQueryCandidate, 
    AdvancedEnrichedQueryCandidate,
    UnifiedQueryCandidate
)
from .enrichment_engine import EnrichmentEngine
from .myllmservice import MyLLMService


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


class SearchQueryEnricher:
    """High-level orchestrator for query enrichment workflows."""

    def __init__(self, llm: MyLLMService = None):
        self.engine = EnrichmentEngine(llm or MyLLMService())

    # ========== METADATA AND UTILITY METHODS ==========

    def _calculate_usage(self, generation_results) -> Dict[str, Any]:
        """Merge usage dictionaries from all generation results."""
        merged_usage = {}
        
        for result in generation_results:
            if hasattr(result, 'usage') and result.usage:
                for key, value in result.usage.items():
                    if isinstance(value, (int, float)):
                        # Sum numeric values
                        merged_usage[key] = merged_usage.get(key, 0) + value
                    else:
                        # For non-numeric, just keep the last value or make a list
                        if key in merged_usage:
                            if not isinstance(merged_usage[key], list):
                                merged_usage[key] = [merged_usage[key]]
                            if value not in merged_usage[key]:
                                merged_usage[key].append(value)
                        else:
                            merged_usage[key] = value
        
        return merged_usage

    def _build_operation_result(
        self, 
        unified: List[UnifiedQueryCandidate], 
        generation_results: List[Any], 
        elapsed_time: float
    ) -> SearchQueryEnrichmentOperation:
        """Build final operation object with metadata."""
        return SearchQueryEnrichmentOperation(
            objects=unified,
            generation_results=generation_results,
            elapsed_time=elapsed_time,
            usage=self._calculate_usage(generation_results)
        )

    # ========== SYNC ENRICHMENT API ==========

    def enrich(self, request_object: SearchQueryEnrichmentRequestObject) -> SearchQueryEnrichmentOperation:
        """
        Main enrichment method that orchestrates the workflow.
        Returns SearchQueryEnrichmentOperation with all metadata.
        """
        start_time = time.time()
        
        # Track generation results
        generation_results = []
        
        # Initialize result lists
        basic_elems: List[BasicEnrichedQueryCandidate] = []
        advanced_elems: List[AdvancedEnrichedQueryCandidate] = []
        
        # Run basic enrichment if requested
        if request_object.use_basic_enrichment:
            basic_result = self.engine.run_basic_enrichment(request_object)
            basic_elems = basic_result['candidates']
            generation_results.extend(basic_result['generation_results'])
            
        # Run advanced enrichment if requested
        if request_object.use_advanced_enrichment:
            advanced_result = self.engine.run_advanced_enrichment(request_object)
            advanced_elems = advanced_result['candidates']
            generation_results.extend(advanced_result['generation_results'])

        # Merge and rank results
        unified = merge_candidates(
            basic=basic_elems,
            advanced=advanced_elems,
            top_n=request_object.how_many_total
        )
        
        elapsed_time = time.time() - start_time
        
        # Build and return operation result
        return self._build_operation_result(unified, generation_results, elapsed_time)

    # ========== ASYNC ENRICHMENT API ==========

    async def async_enrich(self, request_object: SearchQueryEnrichmentRequestObject) -> SearchQueryEnrichmentOperation:
        """
        Async version of enrichment with concurrent execution.
        Runs basic and advanced enrichment in parallel when both are enabled.
        """
        start_time = time.time()
        
        # Track generation results
        generation_results = []
        
        # Initialize result lists
        basic_elems: List[BasicEnrichedQueryCandidate] = []
        advanced_elems: List[AdvancedEnrichedQueryCandidate] = []
        
        # Prepare concurrent tasks
        tasks = []
        task_types = []
        
        if request_object.use_basic_enrichment:
            tasks.append(self.engine.run_basic_enrichment_async(request_object))
            task_types.append('basic')
            
        if request_object.use_advanced_enrichment:
            tasks.append(self.engine.run_advanced_enrichment_async(request_object))
            task_types.append('advanced')
        
        # Execute tasks concurrently
        if tasks:
            results = await asyncio.gather(*tasks)
            
            # Process results based on task types
            for i, task_type in enumerate(task_types):
                result = results[i]
                if task_type == 'basic':
                    basic_elems = result['candidates']
                    generation_results.extend(result['generation_results'])
                elif task_type == 'advanced':
                    advanced_elems = result['candidates']
                    generation_results.extend(result['generation_results'])

        # Merge and rank results
        unified = merge_candidates(
            basic=basic_elems,
            advanced=advanced_elems,
            top_n=request_object.how_many_total
        )
        
        elapsed_time = time.time() - start_time
        
        # Build and return operation result
        return self._build_operation_result(unified, generation_results, elapsed_time)


# ========== EXAMPLE USAGE ==========

if __name__ == "__main__":
    query = "Enes Kuzucu"
    
    identifier_context = "He is data scientist in EETECH, his nickname in web is karaposu"
    search_reason_context = "I am trying to understand and gather his life story "
    
    sqer = SearchQueryEnrichmentRequestObject(
        query=query,
        identifier_context=identifier_context, 
        search_reason_context=search_reason_context,
        text_rules=None,
        how_many_basic=20,
        how_many_advanced=20,
        how_many_total=40,
        use_thinking=False, 
        use_basic_enrichment=True,
        use_advanced_enrichment=False
    )
    
    sqe = SearchQueryEnricher()
    
    # Sync usage
    operation = sqe.enrich(request_object=sqer)
    
    print(f"Generated {len(operation)} enriched queries in {operation.elapsed_time:.2f}s")
    print(f"Usage: {operation.usage}")
    print("")
    
    for e in operation:
        print(e)
    
    print("\n--- Just the query strings ---")
    for query in operation.all_queries():
        print(f"'{query}'")

    # Example of async usage (commented out)
    """
    # To use async version:
    async def main_async():
        operation = await sqe.async_enrich(request_object=sqer)
        print(f"Async: Generated {len(operation)} queries in {operation.elapsed_time:.2f}s")
        for e in operation:
            print(e)
    
    # asyncio.run(main_async())
    """