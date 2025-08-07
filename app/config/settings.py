import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # Vector Database
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str
    
    # LLM Providers
    groq_api_key: str
    
    # LlamaParse
    llama_parse_api_key: str
    
    # Authentication
    bearer_token: str
    
    # App Settings
    environment: str = "development"
    log_level: str = "INFO"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 5
    
    class Config:
        env_file = "LLM-Powered-Intelligent-Query-Retrieval-System/.env"

settings = Settings()