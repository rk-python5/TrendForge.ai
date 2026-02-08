"""
Configuration settings for the LinkedIn AI Agent
"""

import os
from typing import Optional, ClassVar, List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    
    # Database
    database_url: str = "sqlite:///./data/agent.db"
    
    # Agent Settings
    default_post_type: str = "insight"
    max_post_length: int = 3000
    min_post_length: int = 100
    
    # User Preferences
    user_name: str = "Your Name"
    user_industry: str = "Your Industry"
    user_expertise: str = "Your Expertise Area"
    tone: str = "professional"
    
    # API Keys (for future use)
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None
    groq_api_key: Optional[str] = None
    
    # Post Types (ClassVar means these are class-level constants, not fields)
    POST_TYPES: ClassVar[List[str]] = ["insight", "tip", "story", "question", "achievement", "opinion"]
    
    # Tones
    TONES: ClassVar[List[str]] = ["professional", "casual", "inspirational", "educational", "thought-provoking"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
