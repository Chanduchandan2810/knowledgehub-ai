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
        
        async with AsyncSessionLocal() as session:
            # Upsert Org
            org_res = await session.execute(select(Organization).where(Organization.id == settings.DEMO_ORG_ID))
            org = org_res.scalar_one_or_none()
            if not org:
                org = Organization(id=settings.DEMO_ORG_ID, name="Demo Environment")
                session.add(org)
                
            # Upsert Admin
            admin_res = await session.execute(select(Admin).where(Admin.id == settings.DEMO_ADMIN_ID))
            admin = admin_res.scalar_one_or_none()
            if not admin:
                admin = Admin(
                    id=settings.DEMO_ADMIN_ID,
                    auth_user_id=settings.DEMO_ADMIN_ID,
                    organization_id=settings.DEMO_ORG_ID,
                    email="admin@demo.knowledgehub.local",
                    full_name="Demo Admin"
                )
                session.add(admin)
                
            # Upsert Employee
            emp_res = await session.execute(select(Employee).where(Employee.id == settings.DEMO_EMPLOYEE_ID))
            emp = emp_res.scalar_one_or_none()
            if not emp:
                emp = Employee(
                    id=settings.DEMO_EMPLOYEE_ID,
                    auth_user_id=settings.DEMO_EMPLOYEE_ID,
                    organization_id=settings.DEMO_ORG_ID,
                    email="employee@demo.knowledgehub.local",
                    full_name="Demo Employee"
                )
                session.add(emp)
                
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

# Demo Sandbox Isolated Routes
# Mounted separately so Next.js can proxy /api/v1/demo/... securely bypassing normal auth
app.include_router(organizations.router, prefix="/api/v1/demo/organizations", tags=["demo-organizations"])
app.include_router(employees.router, prefix="/api/v1/demo/employees", tags=["demo-employees"])
app.include_router(documents.router, prefix="/api/v1/demo/documents", tags=["demo-documents"])
app.include_router(retrieval.router, prefix="/api/v1/demo/retrieval", tags=["demo-retrieval"])
app.include_router(auth.router, prefix="/api/v1/demo/auth", tags=["demo-auth"])

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

