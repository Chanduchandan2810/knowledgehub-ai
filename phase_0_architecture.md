# Technical Architecture

## 1. Product Concept
KnowledgeHub AI is a B2B multi-tenant AI knowledge platform. Organizations can securely upload internal knowledge documents, and employees can ask natural-language questions against authorized company knowledge using permission-aware RAG (Retrieval-Augmented Generation) with grounded answers and source citations.

## 2. System Architecture
- **Architecture Style**: Modular Monolith.
- **Frontend**: Next.js App Router (React, TypeScript, Tailwind CSS).
- **Backend**: FastAPI (Python, SQLAlchemy async).
- **Platform**: Supabase handles PostgreSQL, Authentication, and Storage.

## 3. Frontend/Backend Relationship
The frontend and backend are separate applications. The Next.js application communicates with the FastAPI backend through the configured API proxy. The Next.js middleware handles and proxies frontend API requests under /api/v1/* to the FastAPI backend.

## 4. Supabase Architecture
- **Auth**: Supabase handles all user registration, login, and JWT generation via uth.users. Passwords are not handled by the backend application directly.
- **Database**: Managed PostgreSQL hosting application schemas.
- **Storage**: Supabase Storage is planned for securely housing PDF/text uploads before processing.

## 5. Authentication Architecture
- **Mechanism**: JWT token issued by Supabase Auth.
- **Validation**: The FastAPI backend receives the token, validates the cryptographic signature (pp.core.security.verify_token), and extracts the sub (user UUID).
- **Role Deduction**: pp.api.deps.get_current_user_context checks the application tables (dmins, then employees) for the user UUID to determine organizational affiliation and role.

## 6. Tenant Model
- **Organizations**: The root entity for multi-tenancy (organizations table).
- **Isolation**: Every API request is verified against the user's mapped organization_id.
- **Database Level**: PostgreSQL local parameters (pp.current_tenant) are set per request, and active Row Level Security (RLS) policies on current application tables currently enforce tenant data isolation.

## 7. Current Roles
There are exactly two application roles:
- **ADMIN**: Has full control over the organization, employees, and configuration. (Document uploads and document access configuration are planned functionality).
- **EMPLOYEE**: Restricted to managing personal settings. (Querying the knowledge base via the chat interface is planned functionality).

## 8. Current Database Model
**Active Application Tables:**
- organizations: Id, name, settings, timestamps.
- dmins: Id, auth_user_id (links to Supabase auth), organization_id, email, full_name, timestamps.
- employees: Id, auth_user_id, organization_id, email, full_name, is_active, timestamps.

**Historical Context:**
Earlier phases of development included tables for users, memberships, and organization_memberships. These obsolete tables appear in historical Alembic migrations because they are part of migration history and are retained for database migration integrity. However, those old tables are NOT part of the current active application schema.

## 9. Current API Structure
``text
backend/app/api/v1/
├── auth.py            # Authentication routes (/api/v1/auth/me)
├── employees.py       # Employee management routes
└── organizations.py   # Organization data routes
``

## 10. Planned Document/RAG Architecture (Future Phases)
The project intentionally avoids unnecessary infrastructure for the MVP.
**Pipeline (Planned)**:
1. Document Upload -> Supabase Storage.
2. Text Extraction (PyMuPDF) -> Semantic Chunking.
3. Embeddings -> Insert to PostgreSQL (pgvector).
4. Permission-aware Retrieval (filtering by organization and future document-level access).
5. RAG -> LLM -> Grounded Answer with Source Citations.

## 11. Security Architecture
- **Multi-tenant isolation**: Enforced heavily in the backend via FastAPI dependencies (get_current_user_context).
- **Database Policies**: Row Level Security (RLS) is currently implemented and active on organizations, dmins, and employees.
- **Authentication**: Offloaded to Supabase for secure password management.
- **Input/File Validation**: Pydantic validates all incoming JSON structures.
- **Planned RAG Security**: Document-level RBAC filters applied *before* vector search to prevent LLM prompt injection and unauthorized data leakage.

## 12. Development Phases
**Completed:**
- Phase 0 — Product + Architecture
- Phase 1 — Project Setup
- Phase 2 — Authentication + Organizations

**Current/Next:**
- Phase 3 — Document Management (NEXT)

**Planned Future Phases:**
- Phase 4 — Document Processing + Embeddings
- Phase 5 — Vector Search + RAG
- Phase 6 — Chat + Citations
- Phase 7 — Hybrid Search
- Phase 8 — AI Evaluation
- Phase 9 — Security Hardening
- Phase 10 — Observability
- Phase 11 — Agents
- Phase 12 — Docker
- Phase 13 — CI/CD
- Phase 14 — Testing + Security Testing
- Phase 15 — Portfolio Documentation

## 13. Architectural Constraints & Technology Decisions
- **SQLAlchemy + asyncpg**: Essential for non-blocking database I/O within the FastAPI asynchronous event loop.
- **Postgres**: Keeps relational data (tenants, roles) in the exact same database.
