from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import organizations

app = FastAPI(
    title="KnowledgeHub AI API",
    description="Backend API for KnowledgeHub AI - B2B Multi-Tenant GenAI Knowledge Platform",
    version="1.0.0",
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

