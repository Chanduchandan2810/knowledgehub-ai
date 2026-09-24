import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "KnowledgeHub AI"
    API_V1_STR: str = "/api/v1"
    
    SUPABASE_URL: str
    SUPABASE_KEY: str
    NEXT_PUBLIC_SUPABASE_ANON_KEY: str
    SUPABASE_JWT_SECRET: str
    
    DATABASE_URL: str
    MIGRATION_DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=str(ROOT_DIR / ".env"), case_sensitive=True, extra="ignore")

settings = Settings()
