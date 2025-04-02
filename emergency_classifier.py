import os
import json
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
from grag.graphrag_search import GraphRAGSearchEngine

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("GRAPHRAG_API_KEY"))

class EmergencyResponseSystem:
    """System to classify and route questions to either GraphRAG (for emergencies) 
    or general LLM responses."""
    
    def __init__(self):
        self.client = client
        # Initialize GraphRAG engine lazily when needed
        self._engine = None
    
    @property
    def engine(self):
        """Lazy initialization of GraphRAG engine"""
        if self._engine is None:
            # Use absolute path for input_dir
            input_dir = os.path.expanduser("~/AIMed/AIMedNow/grag/docs/output-us-emt")
            # print(f"Initializing GraphRAG engine with input_dir: {input_dir}")
            print(f"Answering with grounded EMT data at {input_dir} (GraphRAG search engine)")
            
            self._engine = GraphRAGSearchEngine(
                input_dir=input_dir,
                community_level=2,
                api_key=os.getenv("GRAPHRAG_API_KEY"),
                llm_model=os.getenv("GRAPHRAG_LLM_MODEL", "gpt-4"),
                embedding_model=os.getenv("GRAPHRAG_EMBEDDING_MODEL", "text-embedding-ada-002"),
                use_covariates=False
            )
            
            # Update search parameters
            self._engine.update_search_params(
                context_params={
                    "text_unit_prop": 0.6,
                    "max_tokens": 10_000,
                },
                model_params={
                    "temperature": 0.1,
                },
                response_type="detailed explanation"
            )
        return self._engine
    
    async def classify_emergency(self, question):
        """Classify if a question is emergency-related."""
        try:
            response = client.chat.completions.create(
                model=os.getenv("MODEL_NAME", "gpt-4"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical triage assistant. Your task is to classify whether a question is related to a medical emergency that requires immediate or urgent care. Only classify as emergency questions about injuries, severe symptoms, or situations requiring first aid or emergency treatment. Respond with ONLY one word: 'emergency' or 'non-emergency'."
                    },
                    {"role": "user", "content": question}
                ],
                temperature=0.0,
                max_tokens=20
            )
            # print(response)
            classification = response.choices[0].message.content.strip().lower()
            
            # Make sure we only get one of the two valid classifications
            if "non-emergency" in classification:
                return "non-emergency"
            else:
                return "emergency"
                
        except Exception as e:
            print(f"Error classifying emergency: {e}")
            # Default to non-emergency in case of errors
            return "non-emergency"
    
    async def get_emergency_response(self, question):
        """Get response from GraphRAG for emergency questions."""
        try:
            # Use GraphRAG for emergency responses
            search_result = await self.engine.search(question)
            return {
                'answer': search_result.response,
                'source': search_result.context_text,
                'classification': 'emergency'
            }
        except Exception as e:
            print(f"Error getting emergency response: {e}")
            # Fallback to general response if GraphRAG fails
            return await self.get_general_response(question, is_fallback=True)
    
    async def get_general_response(self, question, is_fallback=False):
        """Get response from general LLM for non-emergency questions."""
        try:
            response = client.chat.completions.create(
                model=os.getenv("MODEL_NAME", "gpt-4"),
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful assistant answering general health questions." + 
                                  (" NOTE: This is a fallback response because the emergency system failed. Add appropriate caution." if is_fallback else "")
                    },
                    {"role": "user", "content": question}
                ],
                temperature=0.7
            )
            return {
                'answer': response.choices[0].message.content,
                'source': 'general_llm',
                'classification': 'non-emergency' if not is_fallback else 'emergency-fallback'
            }
        except Exception as e:
            print(f"Error getting general response: {e}")
            return {
                'answer': "I apologize, but I'm having trouble providing a response at the moment. Please try again later.",
                'source': 'error',
                'classification': 'error'
            }
    
    async def process_question(self, question):
        """Process a question by classifying and routing to appropriate response system."""
        # Classify if the question is emergency-related
        classification = await self.classify_emergency(question)
        
        if classification == "emergency":
            print("This question is classified as an emergency. Please contact emergency services if you think you need medical assistance. (USA: Call 911)")
            return await self.get_emergency_response(question)
        else:
            return await self.get_general_response(question)

# Create a singleton instance
emergency_system = EmergencyResponseSystem()

# Function to handle async operation in sync context
def process_question_sync(question):
    """Synchronous wrapper for processing questions."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()  # Allow nested event loops
    except RuntimeError:
        # No event loop exists yet, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        # Use the current event loop
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(emergency_system.process_question(question))
        return result
    except RuntimeError as e:
        if "already running" in str(e):
            print("Using alternate approach due to nested event loops")
            import nest_asyncio
            nest_asyncio.apply()
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(emergency_system.process_question(question))
        else:
            raise
            
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        question = sys.argv[1]
    else:
        question = "What should I do if I'm having chest pain?"
    
    print(f"Processing question: {question}")
    result = process_question_sync(question)
    print(f"Classification: {result['classification']}")
    print(f"Source: {result['source']}")
    print(f"Answer: {result['answer']}")