# casqe/enrichment_engine.py

from __future__ import annotations
from typing import List, Dict, Any
import asyncio

from .schemes import BasicEnrichedQueryCandidate, AdvancedEnrichedQueryCandidate
from .myllmservice import MyLLMService


class EnrichmentEngine:
    """Core enrichment logic and LLM interactions."""
    
    def __init__(self, llm: MyLLMService):
        self.llm = llm
    
    # ========== COMPONENT EXTRACTION ==========
    
    def extract_components(self, request_object) -> Dict[str, List[Dict[str, float]]]:
        """
        Extract identifiers, platforms, and entities from LLM.
        Returns a dict with keys 'platforms', 'entities', 'identifiers'.
        """
        result = self.llm.ask_llm_to_generate_platforms_and_entitiy_lists(request_object)
        if not getattr(result, "success", False):
            return {"platforms": [], "entities": [], "identifiers": []}
        
        payload = result.content if isinstance(result.content, dict) else {}
        return {
            "platforms": payload.get("platforms", []),
            "entities": payload.get("entities", []),
            "identifiers": payload.get("identifiers", [])
        }
    
    async def extract_components_async(self, request_object) -> Dict[str, List[Dict[str, float]]]:
        """Async version of component extraction."""
        result = await self.llm.async_ask_llm_to_generate_platforms_and_entitiy_lists(request_object)
        if not getattr(result, "success", False):
            return {"platforms": [], "entities": [], "identifiers": []}
        
        payload = result.content if isinstance(result.content, dict) else {}
        return {
            "platforms": payload.get("platforms", []),
            "entities": payload.get("entities", []),
            "identifiers": payload.get("identifiers", [])
        }
    
    # ========== BASIC ENRICHMENT ==========
    
    def combine_components(self, components: Dict[str, List[Dict]]) -> List[BasicEnrichedQueryCandidate]:
        """
        Generate all combinations of identifiers × platforms × entities.
        Includes deduplication logic to prevent redundant combinations.
        """
        ids = components.get("identifiers", [])
        plats = components.get("platforms", [])
        ents = components.get("entities", [])
        
        out: List[BasicEnrichedQueryCandidate] = []
        
        for i in ids:
            for p in plats:  # identifiers × platforms
                # Skip if platform same as identifier
                if p["name"].lower() != i["name"].lower():
                    out.append(
                        BasicEnrichedQueryCandidate(
                            identifier=i["name"], identifier_score=i["score"],
                            platform=p["name"], platform_score=p["score"],
                        ).combine()
                    )
                    
            for e in ents:  # identifiers × entities
                # Skip if entity same as identifier
                if e["name"].lower() != i["name"].lower():
                    out.append(
                        BasicEnrichedQueryCandidate(
                            identifier=i["name"], identifier_score=i["score"],
                            entity=e["name"], entity_score=e["score"],
                        ).combine()
                    )
                    
            for p in plats:  # identifiers × platforms × entities
                for e in ents:
                    # Skip if any duplicates
                    if (p["name"].lower() != i["name"].lower() and 
                        e["name"].lower() != i["name"].lower() and
                        e["name"].lower() != p["name"].lower()):
                        out.append(
                            BasicEnrichedQueryCandidate(
                                identifier=i["name"], identifier_score=i["score"],
                                platform=p["name"], platform_score=p["score"],
                                entity=e["name"], entity_score=e["score"],
                            ).combine()
                        )
        return out
    
    def run_basic_enrichment(self, request_object) -> Dict[str, Any]:
        """
        Complete basic enrichment pipeline.
        Returns dict with 'candidates' and 'generation_results'.
        """
        generation_result = self.llm.ask_llm_to_generate_platforms_and_entitiy_lists(request_object)
        components = self.extract_components(request_object)
        
        if not components["platforms"] or not components["entities"]:
            candidates = []
        else:
            candidates = self.combine_components(components)
            
            # Apply basic-specific limit
            if request_object.how_many_basic:
                candidates.sort(key=lambda x: x.combined_score, reverse=True)
                candidates = candidates[:request_object.how_many_basic]
        
        return {
            'candidates': candidates,
            'generation_results': [generation_result]
        }
    
    async def run_basic_enrichment_async(self, request_object) -> Dict[str, Any]:
        """Async version of basic enrichment pipeline."""
        generation_result = await self.llm.async_ask_llm_to_generate_platforms_and_entitiy_lists(request_object)
        components = await self.extract_components_async(request_object)
        
        if not components["platforms"] or not components["entities"]:
            candidates = []
        else:
            candidates = self.combine_components(components)
            
            # Apply basic-specific limit
            if request_object.how_many_basic:
                candidates.sort(key=lambda x: x.combined_score, reverse=True)
                candidates = candidates[:request_object.how_many_basic]
        
        return {
            'candidates': candidates,
            'generation_results': [generation_result]
        }
    
    # ========== ADVANCED ENRICHMENT ==========
    
    def run_advanced_enrichment(self, request_object) -> Dict[str, Any]:
        """
        Complete advanced enrichment pipeline.
        Returns dict with 'candidates' and 'generation_results'.
        """
        generation_result = self.llm.ask_llm_to_enrich(request_object)
        
        elems: List[AdvancedEnrichedQueryCandidate] = []
        
        if generation_result.success:
            data = generation_result.content
            for d in data:
                aeqc = AdvancedEnrichedQueryCandidate(
                    query=d.get("enriched_query"), 
                    explanation=d.get("explanation"),
                    score=d.get("score"), 
                )
                elems.append(aeqc)
        
        # Apply advanced-specific limit
        if request_object.how_many_advanced and len(elems) > request_object.how_many_advanced:
            elems.sort(key=lambda x: x.score, reverse=True)
            elems = elems[:request_object.how_many_advanced]
        
        return {
            'candidates': elems,
            'generation_results': [generation_result]
        }
    
    async def run_advanced_enrichment_async(self, request_object) -> Dict[str, Any]:
        """Async version of advanced enrichment pipeline."""
        generation_result = await self.llm.async_ask_llm_to_enrich(request_object)
        
        elems: List[AdvancedEnrichedQueryCandidate] = []
        
        if generation_result.success:
            data = generation_result.content
            for d in data:
                aeqc = AdvancedEnrichedQueryCandidate(
                    query=d.get("enriched_query"), 
                    explanation=d.get("explanation"),
                    score=d.get("score"), 
                )
                elems.append(aeqc)
        
        # Apply advanced-specific limit
        if request_object.how_many_advanced and len(elems) > request_object.how_many_advanced:
            elems.sort(key=lambda x: x.score, reverse=True)
            elems = elems[:request_object.how_many_advanced]
        
        return {
            'candidates': elems,
            'generation_results': [generation_result]
        }