import asyncio
import uuid
import os
import logging
from sqlalchemy import select
from supabase import create_client

from app.db.session import AsyncSessionLocal
from app.models.organization import Organization
from app.models.admin import Admin
from app.models.employee import Employee
from app.models.document import Document, DocumentStatus, AccessScope
from app.core.storage import upload_document_to_storage
from app.services.documents.processor import process_document
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DOCS_DIR = os.path.join(os.path.dirname(__file__), "eval_docs")

EVAL_ORG_ID = uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")

async def seed_eval_db():
    logger.info("Setting up KnowledgeHub Evaluation Organization...")
    
    admin_supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    eval_admin_email = "admin@eval.knowledgehub.local"
    eval_emp_email = "employee@eval.knowledgehub.local"
    
    admin_auth_user_id = None
    emp_auth_user_id = None
    
    users_resp = admin_supabase.auth.admin.list_users()
    for u in users_resp:
        if getattr(u, 'email', None) == eval_admin_email:
            admin_auth_user_id = u.id
        elif getattr(u, 'email', None) == eval_emp_email:
            emp_auth_user_id = u.id
            
    if not admin_auth_user_id:
        res = admin_supabase.auth.admin.create_user({
            "email": eval_admin_email,
            "password": "SecureEvalPassword123!",
            "email_confirm": True
        })
        admin_auth_user_id = res.user.id
        
    if not emp_auth_user_id:
        res = admin_supabase.auth.admin.create_user({
            "email": eval_emp_email,
            "password": "SecureEvalPassword123!",
            "email_confirm": True
        })
        emp_auth_user_id = res.user.id
        
    # Now setup DB
    async with AsyncSessionLocal() as session:
        # Org
        org = await session.get(Organization, EVAL_ORG_ID)
        if not org:
            org = Organization(id=EVAL_ORG_ID, name="KnowledgeHub Evaluation Organization")
            session.add(org)
            await session.flush()
            
        # Admin
        res = await session.execute(select(Admin).where(Admin.auth_user_id == uuid.UUID(admin_auth_user_id)))
        admin = res.scalar_one_or_none()
        if not admin:
            admin = Admin(
                id=uuid.uuid4(),
                auth_user_id=uuid.UUID(admin_auth_user_id),
                organization_id=EVAL_ORG_ID,
                full_name="Evaluation Admin",
                email=eval_admin_email
            )
            session.add(admin)
            await session.flush()
            
        # Employee
        res = await session.execute(select(Employee).where(Employee.auth_user_id == uuid.UUID(emp_auth_user_id)))
        emp = res.scalar_one_or_none()
        if not emp:
            emp = Employee(
                id=uuid.uuid4(),
                auth_user_id=uuid.UUID(emp_auth_user_id),
                organization_id=EVAL_ORG_ID,
                full_name="Evaluation Employee",
                email=eval_emp_email
            )
            session.add(emp)
            await session.flush()
            
        await session.commit()
        
        # Load documents
        doc_files = ["eval_leave_policy.txt", "eval_it_policy.txt", "eval_secret_project.txt"]
        
        for filename in doc_files:
            res = await session.execute(
                select(Document).where(Document.organization_id == EVAL_ORG_ID, Document.filename == filename)
            )
            existing = res.scalar_one_or_none()
            if existing:
                if existing.status == DocumentStatus.PROCESSED:
                    logger.info(f"Document {filename} already processed.")
                    continue
                else:
                    logger.info(f"Document {filename} exists but status is {existing.status}. Reprocessing...")
                    await process_document(existing.id)
                    continue
                    
            logger.info(f"Uploading and processing {filename}...")
            filepath = os.path.join(DOCS_DIR, filename)
            with open(filepath, "rb") as f:
                content = f.read()
                
            storage_path = f"{EVAL_ORG_ID}/{uuid.uuid4()}_{filename}"
            url = await upload_document_to_storage(content, storage_path, "text/plain")
            
            scope = AccessScope.RESTRICTED if filename == "eval_secret_project.txt" else AccessScope.ORGANIZATION
            
            doc = Document(
                id=uuid.uuid4(),
                organization_id=EVAL_ORG_ID,
                uploaded_by=admin.id,
                filename=filename,
                mime_type="text/plain",
                file_size=len(content),
                storage_path=url,
                access_scope=scope,
                status=DocumentStatus.UPLOADED
            )
            session.add(doc)
            await session.flush()
            
            from app.models.document_permission import DocumentPermission
            
            # Always grant Admin explicit access to bypass the hybrid_service bug
            perm_admin = DocumentPermission(
                id=uuid.uuid4(),
                document_id=doc.id,
                admin_id=admin.id
            )
            session.add(perm_admin)
            
            # If ORGANIZATION scope, also grant Employee explicit access
            if scope == AccessScope.ORGANIZATION:
                perm_emp = DocumentPermission(
                    id=uuid.uuid4(),
                    document_id=doc.id,
                    employee_id=emp.id
                )
                session.add(perm_emp)
            
            await session.commit()
            await process_document(doc.id)
            
        logger.info("Evaluation environment seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_eval_db())
