# here is myllmservice.py


import logging


logger = logging.getLogger(__name__)
import asyncio
from llmservice.base_service import BaseLLMService
from llmservice.generation_engine import GenerationRequest, GenerationResult
from typing import Optional, Union





class MyLLMService(BaseLLMService):
    def __init__(self, logger=None, max_concurrent_requests=200):
        super().__init__(
            logger=logging.getLogger(__name__),
            default_model_name="gpt-4o",
            # default_model_name="gpt-4.1-nano",
            max_rpm=500,
            max_concurrent_requests=max_concurrent_requests,
        )
        # No need for a semaphore here, it's handled in BaseLLMService
    
    def ask_llm_to_enrich(self, input_object, model=None) -> GenerationResult:
        

        if input_object.use_thinking:
            model="o3"

        
        formatted_prompt=f"""
            Here is original search query from user  {input_object.query}

            here is what user is trying to do {input_object.search_reason_context}

            here is identifier context user explicitly set {input_object.identifier_context}

            here are the text rules given by user {input_object.text_rules}


            Your job is to understand the task context and what user is trying to find via search engines and use the original query and 

            generate {input_object.how_many_advanced} variations, usually as added relevant keywords. 


             For each variation, assign:
                    • an "explanation" describing what kind of info or links this query is intended to surface and how it serves the user’s goal,  
                    • a relevance score from 0.0–1.0 reflecting its estimated search potential, be harsh about the scores unless you think query is perfect.
            
            
            
            
            SOOOO IMPORTANT RULES FOR YOU:
                        Keep each enriched query concise and naturally phrased—avoid forcing in keywords like “life story” unless they truly match how someone would search.
                        Mimic real user searches: use minimal stop-words, focus on core nouns/phrases, and do not combine multiple intents in one query.  
                        Do not include generic filler terms (e.g., “personal background”)—opt for specific, high-value modifiers (e.g., “projects,” “publications”).
                        generate indirect phrases, for example to find digital presence, you can use social media websites keywords rather than using presence
   

           
           Output format (strict JSON array):
                [
                {{
                    "enriched_query": "first enriched query example",
                    "explanation": "explanation about what types of information and links this query seeks to uncover", 
                    "score": 0.85
                }},
                {{
                    "enriched_query": "second enriched query example",
                    "explanation": "explanation about what types of information and links this query seeks to uncover", 
                    "score": 0.78
                }}
                // … repeat until you have {input_object.how_many_advanced} items
                ]

         

        """


        
        pipeline_config = [
        
            {
                'type': 'ConvertToDict',
                'params': {}
            },
           
        ]

        if model is None:
            model= "gpt-4o"
        
        generation_request = GenerationRequest(
            
            formatted_prompt=formatted_prompt,
            model=model,
            output_type="str",
            operation_name="categorize_simple",
            pipeline_config= pipeline_config,
        
        )

      
        generation_result = self.execute_generation(generation_request)

        return generation_result
    


    def async_ask_llm_to_enrich(self, input_object, model=None) -> GenerationResult:
        

        if input_object.use_thinking:
            model="o3"

        
        formatted_prompt=f"""
            Here is original search query from user  {input_object.query}

            here is what user is trying to do {input_object.search_reason_context}

            here is identifier context user explicitly set {input_object.identifier_context}

            here are the text rules given by user {input_object.text_rules}


            Your job is to understand the task context and what user is trying to find via search engines and use the original query and 

            generate {input_object.how_many_advanced} variations, usually as added relevant keywords. 


             For each variation, assign:
                    • an "explanation" describing what kind of info or links this query is intended to surface and how it serves the user’s goal,  
                    • a relevance score from 0.0–1.0 reflecting its estimated search potential, be harsh about the scores unless you think query is perfect.
            
            
            
            
            SOOOO IMPORTANT RULES FOR YOU:
                        Keep each enriched query concise and naturally phrased—avoid forcing in keywords like “life story” unless they truly match how someone would search.
                        Mimic real user searches: use minimal stop-words, focus on core nouns/phrases, and do not combine multiple intents in one query.  
                        Do not include generic filler terms (e.g., “personal background”)—opt for specific, high-value modifiers (e.g., “projects,” “publications”).
                        generate indirect phrases, for example to find digital presence, you can use social media websites keywords rather than using presence
   

           
           Output format (strict JSON array):
                [
                {{
                    "enriched_query": "first enriched query example",
                    "explanation": "explanation about what types of information and links this query seeks to uncover", 
                    "score": 0.85
                }},
                {{
                    "enriched_query": "second enriched query example",
                    "explanation": "explanation about what types of information and links this query seeks to uncover", 
                    "score": 0.78
                }}
                // … repeat until you have {input_object.how_many_advanced} items
                ]

         

        """


        
        pipeline_config = [
        
            {
                'type': 'ConvertToDict',
                'params': {}
            },
           
        ]

        if model is None:
            model= "gpt-4o"
        
        generation_request = GenerationRequest(
            
            formatted_prompt=formatted_prompt,
            model=model,
            output_type="str",
            operation_name="categorize_simple",
            pipeline_config= pipeline_config,
        
        )

      
        generation_result = self.execute_generation_async(generation_request)

        return generation_result
    
    


     
    def ask_llm_to_generate_platforms_and_entitiy_lists(self, input_object, model=None) -> GenerationResult:
        

      
        if input_object.use_thinking:
            model="o3"



        formatted_prompt = f"""
Here is original search query from user  {input_object.query}

here is what user is trying to do {input_object.search_reason_context}

here is identifier context user explicitly set {input_object.identifier_context}

here are the text rules given by user {input_object.text_rules}


“Target” = the specific entity (person, organisation, project, product, dataset, event, …) that the user is trying to investigate in this search task.
It is the real-world subject whose information you want the search engine to surface. Everything else in the query—platform names, modifiers, dates—acts only as context or filters around that focal entity.

Your job:
  1. Analyse the context and output three lists in JSON: "identifiers", "platforms" and "entities".
  2. Each list item must contain:
        "name"   : string (platform or entity),
        "score"  : float 0.0–1.0 estimating usefulness for finding information,

"identifiers" are the shortest textual expressions that distinguish the target sufficiently for the task at hand.

"platforms" → **exactly 20** sites/apps most likely to host relevant information about this specific target type. Consider what platforms are most relevant based on what you're researching:

For PEOPLE: LinkedIn, GitHub, X, BlueSky, Instagram, TikTok, Reddit, personal websites, ResearchGate, company pages, 
For PRODUCTS: manufacturer websites, Amazon, review sites (CNET, TechCrunch), YouTube, Reddit
For COMPANIES: company website, LinkedIn company page, news sites, Crunchbase, financial platforms
For TECHNOLOGIES: GitHub, Stack Overflow, documentation sites, developer blogs, conference sites
For RESEARCH/ACADEMIC: Google Scholar, arXiv, university websites, ResearchGate, academic databases
 
"entities"  → every canonical name, alias, project, role, etc. derived from the context.

Output (strict JSON, no commentary):
{{
  "platforms": [
    {{ "name": "...", "score": 0.88 }},
    …
  ],
  "entities": [
    {{ "name": "...", "score": 0.97 }},
    …
  ], 
"identifiers": [
    {{ "name": "...", "score": 0.97 }},
    …
  ]
}}
"""



        
        pipeline_config = [
           
            {
                'type': 'ConvertToDict',
                'params': {}
            },
          
        ]

        if model is None:
            model= "gpt-4o"
        

        
        generation_request = GenerationRequest(
            
            formatted_prompt=formatted_prompt,
            model=model,
            output_type="str",
            operation_name="categorize_simple",
            pipeline_config= pipeline_config,
         
        )

      

        generation_result = self.execute_generation(generation_request)

        return generation_result
    


    def async_ask_llm_to_generate_platforms_and_entitiy_lists(self, input_object, model=None) -> GenerationResult:
        

      
        if input_object.use_thinking:
            model="o3"



        formatted_prompt = f"""
Here is original search query from user  {input_object.query}

here is what user is trying to do {input_object.search_reason_context}

here is identifier context user explicitly set {input_object.identifier_context}

here are the text rules given by user {input_object.text_rules}


“Target” = the specific entity (person, organisation, project, product, dataset, event, …) that the user is trying to investigate in this search task.
It is the real-world subject whose information you want the search engine to surface. Everything else in the query—platform names, modifiers, dates—acts only as context or filters around that focal entity.

Your job:
  1. Analyse the context and output three lists in JSON: "identifiers", "platforms" and "entities".
  2. Each list item must contain:
        "name"   : string (platform or entity),
        "score"  : float 0.0–1.0 estimating usefulness for finding information,

"identifiers" are the shortest textual expressions that distinguish the target sufficiently for the task at hand.

"platforms" → **exactly 20** sites/apps most likely to host relevant information about this specific target type. Consider what platforms are most relevant based on what you're researching:

For PEOPLE: LinkedIn, GitHub, X, BlueSky, Instagram, TikTok, Reddit, personal websites, ResearchGate, company pages, 
For PRODUCTS: manufacturer websites, Amazon, review sites (CNET, TechCrunch), YouTube, Reddit
For COMPANIES: company website, LinkedIn company page, news sites, Crunchbase, financial platforms
For TECHNOLOGIES: GitHub, Stack Overflow, documentation sites, developer blogs, conference sites
For RESEARCH/ACADEMIC: Google Scholar, arXiv, university websites, ResearchGate, academic databases
 
"entities"  → every canonical name, alias, project, role, etc. derived from the context.

Output (strict JSON, no commentary):
{{
  "platforms": [
    {{ "name": "...", "score": 0.88 }},
    …
  ],
  "entities": [
    {{ "name": "...", "score": 0.97 }},
    …
  ], 
"identifiers": [
    {{ "name": "...", "score": 0.97 }},
    …
  ]
}}
"""



        
        pipeline_config = [
           
            {
                'type': 'ConvertToDict',
                'params': {}
            },
          
        ]

        if model is None:
            model= "gpt-4o"
        

        
        generation_request = GenerationRequest(
            
            formatted_prompt=formatted_prompt,
            model=model,
            output_type="str",
            operation_name="categorize_simple",
            pipeline_config= pipeline_config,
         
        )

      

        generation_result = self.execute_generation_async(generation_request)

        return generation_result




def main():
    """
    Main function to test the categorize_simple method of MyLLMService.
    """
    # Initialize the service
    my_llm_service = MyLLMService()

    # Sample data for testing
    sample_search_title_and_metadescription = "BAV99 Fast Switching Speed. • Surface-Mount Package Ideally Suited for Automated Insertion. • For General-Purpose Switching Applications."
   
   
    try:
        # Perform categorization
        result = my_llm_service.categorize_simple(
            semantic_filter_text=sample_search_title_and_metadescription,
    
        )

        # Print the result
        print("Generation Result:", result)
        if result.success:
            print("Filtered Content:", result.content)
        else:
            print("Error:", result.error_message)
    except Exception as e:
        print(f"An exception occurred: {e}")


if __name__ == "__main__":
    main()
