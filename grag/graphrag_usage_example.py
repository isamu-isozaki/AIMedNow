import asyncio
import os
from graphrag_search import GraphRAGSearchEngine

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

async def main():
    
    # Option 1: Use the simple helper function
    from graphrag_search import query_graphrag
    
    # question = "Hot oil fell on my arm and burned me. I have a blister on my arm. What should I do?"
    # response = await query_graphrag(question)
    # print(f"Response: {response}")
    
    # Option 2: Create an instance with custom configuration
    engine = GraphRAGSearchEngine(
        input_dir="~/AIMed/AIMedNow/grag/docs/output-us-emt",
        community_level=2,
        # Uncomment these lines if you don't want to use environment variables
        api_key=os.getenv("GRAPHRAG_API_KEY"),
        llm_model=os.getenv("GRAPHRAG_LLM_MODEL"),  
        embedding_model=os.getenv("GRAPHRAG_EMBEDDING_MODEL"),
        use_covariates=False
    )
    
    # Update search parameters if needed
    engine.update_search_params(
        context_params={
            "text_unit_prop": 0.6,
            "max_tokens": 10_000,
        },
        model_params={
            "temperature": 0.1,
        },
        response_type="detailed explanation"
    )
    
    # Search with a question
    response = await engine.search("How do I treat a minor burn at home?")
    print(f"Custom search response: {response}")
    
    # You can reuse the same engine instance for multiple queries
    response = await engine.search("What to do if i was bitten by a snake")
    print(f"Follow-up query response: {response}")

if __name__ == "__main__":
    asyncio.run(main())