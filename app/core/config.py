from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

class Settings(BaseModel):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Commerce Agent"
    
    # Security
    API_KEY: str = os.getenv("API_KEY", "your-api-key-here")
    
    # AI Models
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    GPT_MODEL: str = "gpt-4"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # Vector Database
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    PINECONE_ENV: str = os.getenv("PINECONE_ENV")
    PINECONE_INDEX_NAME: str = os.getenv("PINECONE_INDEX_NAME", "commerce-agent")
    
    # AWS Settings
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET: str = os.getenv("S3_BUCKET")
    
    # Memory Settings
    CONVERSATION_MEMORY_K: int = 5
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow",
    }

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 