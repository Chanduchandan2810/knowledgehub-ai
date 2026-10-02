import os
import uuid
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "KnowledgeHub AI"
    API_V1_STR: str = "/api/v1"
    
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    NEXT_PUBLIC_SUPABASE_ANON_KEY: str
    SUPABASE_JWT_SECRET: str
    
    DATABASE_URL: str
    MIGRATION_DATABASE_URL: str
    
    # Phase 4 Document Processing Config
    EMBEDDING_PROVIDER: str = "local"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSIONS: int = 384
    EMBEDDING_BATCH_SIZE: int = 32
    
    # These chunking values are defaults but the processor will dynamically 
    # adjust based on the model's actual max_seq_length.
    CHUNK_SIZE_TOKENS: int = 200
    CHUNK_OVERLAP_PERCENT: float = 0.15

    # Phase 5 Retrieval Config
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_THRESHOLD_COSINE_DISTANCE: float = 0.65
    
    MAX_PAGE_COUNT: int = 500
    MAX_CHUNK_COUNT: int = 5000
    PROCESSING_TIMEOUT_MINUTES: int = 30
    MIN_CONTENT_LENGTH: int = 50

    # Demo Sandbox Config
    DEMO_ORG_ID: uuid.UUID = uuid.UUID("00000000-0000-0000-0000-000000000001")
    DEMO_ADMIN_ID: uuid.UUID = uuid.UUID("00000000-0000-0000-0000-000000000002")
    DEMO_EMPLOYEE_ID: uuid.UUID = uuid.UUID("00000000-0000-0000-0000-000000000003")

    model_config = SettingsConfigDict(env_file=str(ROOT_DIR / ".env"), case_sensitive=True, extra="ignore")

settings = Settings()


