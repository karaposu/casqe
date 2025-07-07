# casqe/query_enricher.py
# to run python -m casqe.query_enricher

from __future__ import annotations
from typing import List, Dict, Callable, Optional
from dataclasses import dataclass, field
import asyncio

from .schemes import SearchQueryEnrichmentRequestObject, SearchQueryEnrichmentResultObject, SearchQueryEnrichmentOperation, BasicEnrichedQueryCandidate, AdvancedEnrichedQueryCandidate,UnifiedQueryCandidate
from .myllmservice import MyLLMService


def merge_candidates(
    basic: List[BasicEnrichedQueryCandidate],
    advanced: List[AdvancedEnrichedQueryCandidate],
    top_n: Optional[int] = None
) -> List[UnifiedQueryCandidate]:
    merged: dict[str, UnifiedQueryCandidate] = {}

    # ---------- basic ------------------------------------------------------
    for b in basic:
        q = b.combined
        if not q:                     # skip filtered-out items
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
        # accept either "query" or "enriched_query"
        q = a.query or getattr(a, "enriched_query", None)
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
    """High-level orchestrator that chains FilterHero → LLM parse phase."""

    def __init__(self, llm: MyLLMService | None = None):
        
        self.llm = llm or MyLLMService()



    def get_platforms_and_entities(
        self,
        request_object
    ) -> Dict[str, List[Dict[str, float]]]:
        """
        Calls the LLM and returns a dict with keys
        'platforms' and 'entities'. Falls back to empty
        lists if the call fails or returns malformed data.
        """
        result = self.llm.ask_llm_to_generate_platforms_and_entitiy_lists(request_object)
        if not getattr(result, "success", False):
            return {"platforms": [], "entities": [],  "identifiers": []}
        
        payload = result.content if isinstance(result.content, dict) else {}
        return {
            "platforms": payload.get("platforms", []),
            "entities":  payload.get("entities",  []),
            "identifiers":  payload.get("identifiers",  [])
        }
    

    def combine_for_basic_enrichment(self, payload) -> list[BasicEnrichedQueryCandidate]:
        ids   = payload.get("identifiers", [])
        plats = payload.get("platforms", [])
        ents  = payload.get("entities", [])
        
        out: list[BasicEnrichedQueryCandidate] = []
        
        for i in ids:
            for p in plats:                # identifiers × platforms
                out.append(
                    BasicEnrichedQueryCandidate(
                        identifier=i["name"], identifier_score=i["score"],
                        platform=p["name"],   platform_score=p["score"],
                    ).combine()
                )
            for e in ents:                 # identifiers × entities
                out.append(
                    BasicEnrichedQueryCandidate(
                        identifier=i["name"], identifier_score=i["score"],
                        entity=e["name"],     entity_score=e["score"],
                    ).combine()
                )
            for p in plats:                # identifiers × platforms × entities
                for e in ents:
                    out.append(
                        BasicEnrichedQueryCandidate(
                            identifier=i["name"], identifier_score=i["score"],
                            platform=p["name"],   platform_score=p["score"],
                            entity=e["name"],     entity_score=e["score"],
                        ).combine()
                    )
        return out
        
   
    
    def run_advanced_enrichment(
        self,
        request_object,
        min_spec: float = 0.75
    ) -> List[str]:
        
        elems: list[AdvancedEnrichedQueryCandidate] = []
        generation_result=self.llm. ask_llm_to_enrich(request_object)

        if generation_result.success:
            # print("------------")
         

            data= generation_result.content

            for d in data:
                aeqc= AdvancedEnrichedQueryCandidate(enriched_query=d.get("enriched_query"), 
                                               explanation=d.get("explanation"),
                                               score=d.get("score"), 
                                               )
                
                elems.append(aeqc)

        # elems =[]
        # for e in elems:
        #     print(e)

        return elems


    def run_basic_enrichment(
        self,
        request_object,
        min_spec: float = 0.75
    ) -> List[str]:
        

        data_dict = self.get_platforms_and_entities(request_object) 

        print("data: ",data_dict)


        if not data_dict["platforms"] or not data_dict["entities"]:
            return []           # nothing useful returned by the LLM
        

        elems = self.combine_for_basic_enrichment(data_dict)
        for e in elems:
            print(e)

        return elems


    # def run_basic_enrichment(self, request_object):
        
    #     generation_result=self.llm.ask_llm_to_generate_platforms_and_entitiy_lists(request_object)
    #     if generation_result.success:
    #             print(generation_result.content)

    

    def enrich(self, request_object ):

        # always define the two lists
        basic_elems:  List[BasicEnrichedQueryCandidate]   = []
        advanced_elems: List[AdvancedEnrichedQueryCandidate] = []
            
        print("inside enrich ")
        if request_object.use_basic_enrichment:
            basic_elems =self.run_basic_enrichment(request_object)
            
        if request_object.use_advanced_enrichment:

            advanced_elems =self.run_advanced_enrichment(request_object)


        unified = merge_candidates(
        basic=basic_elems,
        advanced=advanced_elems,
        top_n=request_object.how_many   # honour the caller’s limit
        )


        return unified 
        

           


if __name__ == "__main__":
   
    query= "Enes Kuzucu"
    
    identifier_context= "He is data scientist in EETECH, his nickname in web is karaposu"
    search_reason_context= "I am trying to understand and gather his life story "
    
    sqer=SearchQueryEnrichmentRequestObject( query=query ,
                                       identifier_context= identifier_context, 
                                       search_reason_context=search_reason_context,
                                       text_rules= None,
                                       how_many= 10,
                                       use_thinking=False, 
                                       use_basic_enrichment=False,
                                       use_advanced_enrichment=True)
    

    
                           
    
    sqe = SearchQueryEnricher()
    
    list_of_query_objects = sqe.enrich(request_object=sqer)
    
    print(" ")
    print(" ")
    print(list_of_query_objects)

     