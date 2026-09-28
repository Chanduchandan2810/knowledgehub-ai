# KnowledgeHub AI

KnowledgeHub AI is a B2B multi-tenant AI knowledge platform.

## 1. What is KnowledgeHub AI?
KnowledgeHub AI enables organizations to securely upload internal knowledge documents and allows employees to ask natural-language questions against authorized company knowledge using permission-aware Retrieval-Augmented Generation (RAG) with grounded answers and source citations.

## 2. The Real-World Problem It Solves
Modern organizations struggle with knowledge silos and information retrieval. Employees spend hours searching through handbooks, policies, and internal wikis. Public AI tools cannot be securely used with confidential data, and existing enterprise solutions often lack strict, document-level access controls. KnowledgeHub AI provides a secure, private, permission-aware AI assistant that answers questions based on data the specific employee is authorized to see.

## 3. Who Uses It?
KnowledgeHub AI is built for internal corporate teams (HR, IT, Engineering, Operations) that need instant, accurate access to company policies, documentation, and institutional knowledge.

## 4. Current Architecture
- **Frontend**: Next.js App Router, React, TypeScript, Tailwind CSS.
- **Backend**: Python, FastAPI, SQLAlchemy (async), asyncpg, Alembic.
- **Database & Platform**: Supabase (PostgreSQL, Supabase Auth).
- **Style**: Modular monolith (One Next.js frontend, one FastAPI backend, managed PostgreSQL/Auth).

## 5. Current Roles
There are exactly two application roles:
- **ADMIN**: Manages the organization, manages employees, uploads/manages company documents (planned), manages document access/permissions (planned), and accesses organization-level administrative features.
- **EMPLOYEE**: Belongs to an organization, accesses authorized company knowledge via the employee chat interface (planned), and manages their own profile/settings.

## 6. Technology Stack
**Current**:
- **Web Frameworks**: Next.js, FastAPI
- **Database**: PostgreSQL (via Supabase)
- **Authentication**: Supabase Auth (JWT)
- **ORM**: SQLAlchemy (async) + Alembic

**Planned**:
- pgvector, PyMuPDF, embeddings, LLM provider, RAG, hybrid search.

## 7. Current Project Status
**Current State: Phase 2 (Authentication + Organizations) Completed.**
The project has a multi-tenant database schema, working Supabase authentication, functional Next.js routing for both Admin and Employee portals, and a secured FastAPI backend.

*Note: Document upload, Vector Search, and RAG capabilities are explicitly planned for future phases and are not yet implemented.*

## 8. Repository Structure
``text
backend/
├── alembic/              # Database migration scripts
├── app/                  # FastAPI application code
│   ├── api/v1/           # API Routers (auth, employees, organizations)
│   ├── core/             # Security and configuration
│   ├── db/               # Database session management
│   ├── models/           # SQLAlchemy models (admin, employee, organization)
│   ├── schemas/          # Pydantic validation schemas
│   └── main.py           # Application entrypoint
├── tests/                # Pytest test suite
├── alembic.ini           # Alembic configuration
└── requirements.txt      # Python dependencies

frontend/
├── app/
│   ├── (auth)/           # /login, /register
│   ├── (authenticated)/
│   │   ├── admin/        # Admin portal (/admin/dashboard, etc.)
│   │   └── employee/     # Employee portal (/employee/profile, etc.)
│   ├── (demo)/           # /demo
│   └── (marketing)/      # Public landing page (/)
├── components/           # Shared UI components and navigation
├── middleware.ts         # Next.js API proxy
└── package.json          # Node dependencies
``

## 9. Security Approach
- **Multi-tenant isolation**: Every backend request is scoped to the user's organization.
- **Authentication**: Handled via Supabase Auth.
- **Backend Authorization**: FastAPI dependencies strictly enforce role-based access control (Admin vs. Employee).
- **Database Level**: PostgreSQL Row Level Security (RLS) policies currently enforce tenant isolation on the active tables (organizations, dmins, employees).
- **Environment Secrets**: Database URLs and API keys are managed via .env.
- **Planned**: Document-level permissions and prompt injection defense for the upcoming RAG pipeline.

## 10. Development Roadmap
- [x] Phase 0 — Product + Architecture
- [x] Phase 1 — Project Setup
- [x] Phase 2 — Authentication + Organizations
- [ ] **Phase 3 — Document Management (NEXT)**
- [ ] Phase 4 — Document Processing + Embeddings
- [ ] Phase 5 — Vector Search + RAG
- [ ] Phase 6 — Chat + Citations
- [ ] Phase 7 — Hybrid Search
- [ ] Phase 8 — AI Evaluation
- [ ] Phase 9 — Security Hardening
- [ ] Phase 10 — Observability
- [ ] Phase 11 — Agents
- [ ] Phase 12 — Docker
- [ ] Phase 13 — CI/CD
- [ ] Phase 14 — Testing + Security Testing
- [ ] Phase 15 — Portfolio Documentation

## 11. How to Run Locally

### Environment Setup
1. Clone the repository.
2. Copy the environment template: cp .env.example .env
3. Fill in your .env file using the exact keys expected by the application (SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY, DATABASE_URL). *Do not commit this file.*

### Backend
``bash
cd backend
python -m venv venv311
source venv311/bin/activate  # Or .\venv311\Scripts\activate on Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
``

### Frontend
``bash
cd frontend
npm install
npm run dev
``

## 12. Testing
To run the backend test suite:
``bash
cd backend
python -m pytest tests/
``
