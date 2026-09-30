from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

supabase_client: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY if settings.SUPABASE_SERVICE_ROLE_KEY else settings.SUPABASE_KEY
)

DOCUMENT_BUCKET = "documents"

def ensure_bucket_exists():
    try:
        buckets = supabase_client.storage.list_buckets()
        bucket_names = [b.name for b in buckets]
        if DOCUMENT_BUCKET not in bucket_names:
            logger.info(f"Creating bucket {DOCUMENT_BUCKET}")
            supabase_client.storage.create_bucket(DOCUMENT_BUCKET, options={"public": False})
    except Exception as e:
        logger.error(f"Error checking/creating bucket: {e}")

# Try to ensure bucket at startup
try:
    ensure_bucket_exists()
except:
    pass

async def upload_document_to_storage(file_bytes: bytes, storage_path: str, mime_type: str) -> str:
    """Uploads a document to Supabase storage."""
    try:
        result = supabase_client.storage.from_(DOCUMENT_BUCKET).upload(
            storage_path, 
            file_bytes,
            file_options={"content-type": mime_type}
        )
        return storage_path
    except Exception as e:
        logger.error(f"Failed to upload document to {storage_path}: {e}")
        raise e

async def delete_document_from_storage(storage_path: str):
    """Deletes a document from Supabase storage."""
    try:
        supabase_client.storage.from_(DOCUMENT_BUCKET).remove([storage_path])
    except Exception as e:
        logger.error(f"Failed to delete document from {storage_path}: {e}")
        raise e
