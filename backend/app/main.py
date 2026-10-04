from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from sqlalchemy import text
from app.db.session import AsyncSessionLocal
from app.models.document import DocumentStatus
from app.core.config import settings
from app.api.v1 import organizations

logger = logging.getLogger(__name__)

async def cleanup_stale_processing():
    """Resets documents stuck in PROCESSING for longer than timeout."""
    try:
        async with AsyncSessionLocal() as session:
            stmt = text(f"""
                UPDATE documents
                SET status = :failed_status,
                    error_message = 'Processing timed out after {settings.PROCESSING_TIMEOUT_MINUTES} minutes.'
                WHERE status = :processing_status
                  AND processing_started_at < NOW() - INTERVAL '{settings.PROCESSING_TIMEOUT_MINUTES} minutes'
            """).bindparams(
                failed_status=DocumentStatus.FAILED.value,
                processing_status=DocumentStatus.PROCESSING.value
            )
            result = await session.execute(stmt)
            await session.commit()
            if result.rowcount > 0:
                logger.warning(f"Reset {result.rowcount} stale processing documents to FAILED.")
    except Exception as e:
        logger.error(f"Failed to cleanup stale processing: {e}")

async def seed_demo_sandbox():
    """Seeds the deterministic demo organization, admin, and employee if missing."""
    try:
        from app.models.organization import Organization
        from app.models.admin import Admin
        from app.models.employee import Employee
        from sqlalchemy import select
        from supabase import create_client
        
        # 1. Ensure Auth users exist using Admin API
        admin_supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        demo_admin_email = "admin@demo.knowledgehub.local"
        demo_emp_email = "employee@demo.knowledgehub.local"
        
        admin_auth_user_id = None
        emp_auth_user_id = None
        
        users_resp = admin_supabase.auth.admin.list_users()
        for u in users_resp:
            if u.email == demo_admin_email:
                admin_auth_user_id = u.id
            elif u.email == demo_emp_email:
                emp_auth_user_id = u.id
                
        if not admin_auth_user_id:
            res = admin_supabase.auth.admin.create_user({
                "email": demo_admin_email,
                "password": "SecureDemoPassword123!",
                "email_confirm": True
            })
            admin_auth_user_id = res.user.id
            
        if not emp_auth_user_id:
            res = admin_supabase.auth.admin.create_user({
                "email": demo_emp_email,
                "password": "SecureDemoPassword123!",
                "email_confirm": True
            })
            emp_auth_user_id = res.user.id
        
        async with AsyncSessionLocal() as session:
            # Upsert Org
            org_res = await session.execute(select(Organization).where(Organization.id == settings.DEMO_ORG_ID))
            org = org_res.scalar_one_or_none()
            if not org:
                org = Organization(id=settings.DEMO_ORG_ID, name="Demo Environment")
                session.add(org)
                await session.flush()
                
            # Upsert Admin
            admin_res = await session.execute(select(Admin).where(Admin.id == settings.DEMO_ADMIN_ID))
            admin = admin_res.scalar_one_or_none()
            if not admin:
                admin = Admin(
                    id=settings.DEMO_ADMIN_ID,
                    auth_user_id=admin_auth_user_id,
                    organization_id=settings.DEMO_ORG_ID,
                    email=demo_admin_email,
                    full_name="Demo Admin"
                )
                session.add(admin)
            elif str(admin.auth_user_id) != admin_auth_user_id:
                admin.auth_user_id = admin_auth_user_id
                
            # Upsert Employee
            emp_res = await session.execute(select(Employee).where(Employee.id == settings.DEMO_EMPLOYEE_ID))
            emp = emp_res.scalar_one_or_none()
            if not emp:
                emp = Employee(
                    id=settings.DEMO_EMPLOYEE_ID,
                    auth_user_id=emp_auth_user_id,
                    organization_id=settings.DEMO_ORG_ID,
                    email=demo_emp_email,
                    full_name="Demo Employee"
                )
                session.add(emp)
            elif str(emp.auth_user_id) != emp_auth_user_id:
                emp.auth_user_id = emp_auth_user_id
                
            await session.commit()
    except Exception as e:
        logger.error(f"Failed to seed demo sandbox: {e}")

async def lifespan(app: FastAPI):
    # Startup
    await seed_demo_sandbox()
    await cleanup_stale_processing()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="KnowledgeHub AI API",
    description="Backend API for KnowledgeHub AI - B2B Multi-Tenant GenAI Knowledge Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "KnowledgeHub AI API is running"}

app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["organizations"])

from app.api.v1 import auth
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

from app.api.v1 import employees
app.include_router(employees.router, prefix="/api/v1/employees", tags=["employees"])

from app.api.v1 import documents
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])

from app.api.v1 import retrieval
app.include_router(retrieval.router, prefix="/api/v1/retrieval", tags=["retrieval"])

from app.api.v1 import conversations
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["conversations"])

from fastapi.responses import JSONResponse
import traceback
import logging

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logging.error(f"Global exception: {exc}")
    traceback.print_exc()
    # Return a safe, generic message to the client, but keep the real stacktrace in server logs
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal server error occurred."}
    )

