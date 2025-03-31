import os
import pandas as pd
import tiktoken
from typing import Dict, Any, Optional, Union

from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
from graphrag.query.indexer_adapters import (
    read_indexer_covariates,
    read_indexer_entities,
    read_indexer_relationships,
    read_indexer_reports,
    read_indexer_text_units,
)
from graphrag.query.structured_search.local_search.mixed_context import (
    LocalSearchMixedContext,
)
from graphrag.query.structured_search.local_search.search import LocalSearch
from graphrag.vector_stores.lancedb import LanceDBVectorStore
from graphrag.config.enums import ModelType
from graphrag.config.models.language_model_config import LanguageModelConfig
from graphrag.language_model.manager import ModelManager

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

class GraphRAGSearchEngine:
    """
    A wrapper library for the GraphRAG search engine that simplifies the setup and query process.
    """

    def __init__(
        self,
        input_dir: str = "./output",
        lancedb_uri: Optional[str] = None,
        community_level: int = 2,
        api_key: Optional[str] = None,
        llm_model: Optional[str] = None,
        embedding_model: Optional[str] = None,
        use_covariates: bool = False,
    ):
        """
        Initialize the GraphRAG search engine.

        Args:
            input_dir: Directory containing the indexed data
            lancedb_uri: URI for the LanceDB database (defaults to {input_dir}/lancedb)
            community_level: Community level to use for entity and report selection
            api_key: API key for LLM and embedding services (defaults to GRAPHRAG_API_KEY env var)
            llm_model: LLM model to use (defaults to GRAPHRAG_LLM_MODEL env var)
            embedding_model: Embedding model to use (defaults to GRAPHRAG_EMBEDDING_MODEL env var)
            use_covariates: Whether to use covariates (if available)
        """
        self.input_dir = input_dir
        self.lancedb_uri = lancedb_uri or f"{input_dir}/lancedb"
        self.community_level = community_level
        self.api_key = api_key or os.environ.get("GRAPHRAG_API_KEY")
        self.llm_model = llm_model or os.environ.get("GRAPHRAG_LLM_MODEL")
        self.embedding_model = embedding_model or os.environ.get("GRAPHRAG_EMBEDDING_MODEL")
        self.use_covariates = use_covariates
        
        # Table names
        self.COMMUNITY_REPORT_TABLE = "community_reports"
        self.ENTITY_TABLE = "entities"
        self.COMMUNITY_TABLE = "communities"
        self.RELATIONSHIP_TABLE = "relationships"
        self.COVARIATE_TABLE = "covariates"
        self.TEXT_UNIT_TABLE = "text_units"
        
        # Initialize the search engine
        self.search_engine = self._setup_search_engine()
    
    def _setup_search_engine(self) -> LocalSearch:
        """
        Set up the GraphRAG search engine with all necessary components.
        
        Returns:
            LocalSearch: The configured search engine
        """
        # Load entity and community data
        entity_df = pd.read_parquet(f"{self.input_dir}/{self.ENTITY_TABLE}.parquet")
        community_df = pd.read_parquet(f"{self.input_dir}/{self.COMMUNITY_TABLE}.parquet")
        entities = read_indexer_entities(entity_df, community_df, self.community_level)
        
        # Set up entity embedding store
        description_embedding_store = LanceDBVectorStore(
            collection_name="default-entity-description",
        )
        description_embedding_store.connect(db_uri=self.lancedb_uri)
        
        # Load relationships
        relationship_df = pd.read_parquet(f"{self.input_dir}/{self.RELATIONSHIP_TABLE}.parquet")
        relationships = read_indexer_relationships(relationship_df)
        
        # Load covariates if needed
        covariates = None
        if self.use_covariates:
            covariate_df = pd.read_parquet(f"{self.input_dir}/{self.COVARIATE_TABLE}.parquet")
            claims = read_indexer_covariates(covariate_df)
            covariates = {"claims": claims}
        
        # Load reports and text units
        report_df = pd.read_parquet(f"{self.input_dir}/{self.COMMUNITY_REPORT_TABLE}.parquet")
        reports = read_indexer_reports(report_df, community_df, self.community_level)
        
        text_unit_df = pd.read_parquet(f"{self.input_dir}/{self.TEXT_UNIT_TABLE}.parquet")
        text_units = read_indexer_text_units(text_unit_df)
        
        # Set up language model components
        chat_config = LanguageModelConfig(
            api_key=self.api_key,
            type=ModelType.OpenAIChat,
            model=self.llm_model,
            max_retries=20,
        )
        chat_model = ModelManager().get_or_create_chat_model(
            name="local_search",
            model_type=ModelType.OpenAIChat,
            config=chat_config,
        )
        
        token_encoder = tiktoken.encoding_for_model(self.llm_model)
        
        embedding_config = LanguageModelConfig(
            api_key=self.api_key,
            type=ModelType.OpenAIEmbedding,
            model=self.embedding_model,
            max_retries=20,
        )
        
        text_embedder = ModelManager().get_or_create_embedding_model(
            name="local_search_embedding",
            model_type=ModelType.OpenAIEmbedding,
            config=embedding_config,
        )
        
        # Set up context builder
        context_builder = LocalSearchMixedContext(
            community_reports=reports,
            text_units=text_units,
            entities=entities,
            relationships=relationships,
            covariates=covariates,
            entity_text_embeddings=description_embedding_store,
            embedding_vectorstore_key=EntityVectorStoreKey.ID,
            text_embedder=text_embedder,
            token_encoder=token_encoder,
        )
        
        # Configure search parameters
        local_context_params = {
            "text_unit_prop": 0.5,
            "community_prop": 0.1,
            "conversation_history_max_turns": 5,
            "conversation_history_user_turns_only": True,
            "top_k_mapped_entities": 10,
            "top_k_relationships": 10,
            "include_entity_rank": True,
            "include_relationship_weight": True,
            "include_community_rank": False,
            "return_candidate_context": False,
            "embedding_vectorstore_key": EntityVectorStoreKey.ID,
            "max_tokens": 12_000,
        }
        
        model_params = {
            "max_tokens": 2_000,
            "temperature": 0.0,
        }
        
        # Create and return the search engine
        return LocalSearch(
            model=chat_model,
            context_builder=context_builder,
            token_encoder=token_encoder,
            model_params=model_params,
            context_builder_params=local_context_params,
            response_type="single paragraph",
        )
    
    async def search(self, query: str) -> str:
        """
        Search the GraphRAG knowledge base with the given query.
        
        Args:
            query: The user's question
            
        Returns:
            str: The response from the search engine
        """
        result = await self.search_engine.search(query)
        return result.response
    
    def update_search_params(
        self, 
        context_params: Optional[Dict[str, Any]] = None,
        model_params: Optional[Dict[str, Any]] = None,
        response_type: Optional[str] = None
    ) -> None:
        """
        Update the search parameters.
        
        Args:
            context_params: Parameters for the context builder
            model_params: Parameters for the language model
            response_type: The desired response format
        """
        if context_params:
            self.search_engine.context_builder_params.update(context_params)
        
        if model_params:
            self.search_engine.model_params.update(model_params)
            
        if response_type:
            self.search_engine.response_type = response_type


# Example usage
async def query_graphrag(question: str) -> str:
    """
    Query the GraphRAG search engine with a question.
    
    Args:
        question: The user's question
        
    Returns:
        str: The response from the search engine
    """
    engine = GraphRAGSearchEngine()
    response = await engine.search(question)
    return response