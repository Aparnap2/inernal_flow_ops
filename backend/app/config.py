import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Application settings are loaded from environment variables.
    Default values are provided for development.
    """
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/orchestrator_dev")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    HUBSPOT_CLIENT_ID: str = os.getenv("HUBSPOT_CLIENT_ID", "your-hubspot-client-id")
    HUBSPOT_CLIENT_SECRET: str = os.getenv("HUBSPOT_CLIENT_SECRET", "your-hubspot-client-secret")
    HUBSPOT_WEBHOOK_SECRET: str = os.getenv("HUBSPOT_WEBHOOK_SECRET", "your-webhook-secret")
    
    # OpenRouter/OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "openai/gpt-4o")
    SITE_URL: str = os.getenv("SITE_URL", "https://your-site.com")
    SITE_NAME: str = os.getenv("SITE_NAME", "HubSpot Operations Orchestrator")
    
    INNGEST_EVENT_KEY: str = os.getenv("INNGEST_EVENT_KEY", "your-inngest-event-key")
    INNGEST_SIGNING_KEY: str = os.getenv("INNGEST_SIGNING_KEY", "your-inngest-signing-key")
    
    AIRTABLE_API_KEY: str = os.getenv("AIRTABLE_API_KEY", "your-airtable-api-key")
    NOTION_API_KEY: str = os.getenv("NOTION_API_KEY", "your-notion-api-key")
    
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "your-google-client-id")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "your-google-client-secret")

    class Config:
        case_sensitive = True

settings = Settings()
