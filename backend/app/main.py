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
