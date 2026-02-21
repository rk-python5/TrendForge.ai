"""
Application configuration loaded from environment variables.
"""

import os
from typing import Optional, ClassVar, List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    # Agent Settings
    default_post_type: str = "insight"
    max_post_length: int = 3000
    min_post_length: int = 100

    # User Preferences
    user_name: str = "Rehaan Khatri"
    user_industry: str = "Tech/AI/Data Science/ML/Software/Programming/Engineering/finance/cryptocurrency"
    user_expertise: str = "Agentic AI, RAG Systems & FinTech Applications"
    tone: str = "professional"

    # Frontend
    frontend_url: str = "http://localhost:3000"

    # API Keys (future phases)
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    groq_api_key: Optional[str] = None
    huggingface_token: Optional[str] = None
    reddit_client_id: Optional[str] = None
    reddit_client_secret: Optional[str] = None

    # Post Types & Tones
    POST_TYPES: ClassVar[List[str]] = [
        "insight", "tip", "story", "question", "achievement", "opinion"
    ]
    TONES: ClassVar[List[str]] = [
        "professional", "casual", "inspirational", "educational", "thought-provoking"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
