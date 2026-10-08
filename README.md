# KnowledgeHub AI

KnowledgeHub AI is a B2B multi-tenant AI knowledge platform.

## 1. What is KnowledgeHub AI?
KnowledgeHub AI enables organizations to securely upload internal knowledge documents and allows employees to ask natural-language questions against authorized company knowledge using permission-aware Retrieval-Augmented Generation (RAG) with grounded answers and source citations.

## 2. The Real-World Problem It Solves
Modern organizations struggle with knowledge silos and information retrieval. Employees spend hours searching through handbooks, policies, and internal wikis. Public AI tools cannot be securely used with confidential data, and existing enterprise solutions often lack strict, document-level access controls. KnowledgeHub AI provides a secure, private, permission-aware AI assistant that answers questions based on data the specific employee is authorized to see.

## 3. Features
- **Multi-tenant Organization Isolation:** Backend-enforced organization/tenant isolation through authenticated user context, authorization dependencies, and permission-aware queries.
- **Role-Based Access Control (RBAC):** Distinct portals and capabilities for Admin and Employee roles.
- **Document Management:** Upload and manage company files directly through the web interface.
- **Document Processing Pipeline:** Automated chunking and embedding generation using local sentence-transformer models.
- **pgvector Integration:** Highly efficient vector search and storage natively in PostgreSQL.
- **Hybrid Retrieval:** Fuses vector semantic search with exact keyword match searching (BM25-style) for optimal accuracy.
- **Retrieval-Augmented Generation (RAG):** Context-aware LLM answers powered by local open-source models (Ollama).
- **Citations:** Every AI claim is grounded and cited to the exact document chunks it used.
- **Document Permissions:** Granular control over whether a document is accessible to all employees, specific roles, or restricted entirely.
- **Prompt Injection Protection:** Dedicated validation models to sanitize and reject adversarial attacks.
- **Rate Limiting:** Protects expensive AI endpoints from abuse.
- **Observability:** Custom health checks and structured logging for debugging AI pipelines.
- **Demo Sandbox:** A deterministic test environment built-in for rapid testing and demonstrations.

## 4. Current Roles
- **ADMIN**: Manages the organization, manages employees, uploads/manages company documents, assigns document access permissions, and accesses organization-level administrative features.
- **EMPLOYEE**: Belongs to an organization, accesses authorized company knowledge via the employee chat interface, and manages their own profile/settings.

## 5. Technology Stack & Deployment Architecture
**Frontend**: Next.js App Router, React, TypeScript, Tailwind CSS, Lucide Icons.
**Backend**: Python, FastAPI, SQLAlchemy (async), asyncpg, Alembic.
**Database & Platform**: Supabase (PostgreSQL with pgvector, Supabase Auth).
**AI & Search**: sentence-transformers (local embeddings), Ollama (local generation).
**Infrastructure**: Fully dockerized modular monolith (Next.js container, FastAPI container, Ollama container).

## 6. Repository Structure
```text
backend/
├── alembic/              # Database migration scripts
├── app/                  # FastAPI application code
│   ├── api/v1/           # API Routers (auth, employees, organizations, documents, chat)
│   ├── core/             # Security and configuration
│   ├── db/               # Database session management
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic validation schemas
│   ├── services/         # Business logic (RAG, documents, embeddings, hybrid search)
│   └── main.py           # Application entrypoint
├── tests/                # 90+ Pytest security/integration tests
├── Dockerfile            # Container configuration
└── requirements.txt      # Python dependencies

frontend/
├── app/
│   ├── (auth)/           # /login, /register
│   ├── (authenticated)/  # /admin and /employee layouts and portals
│   ├── (demo)/           # /demo sandbox
│   └── (marketing)/      # Public landing page (/)
├── components/           # Shared UI components and navigation
├── middleware.ts         # Next.js API proxy and middleware
├── Dockerfile            # Next.js standalone container build
└── package.json          # Node dependencies
```

## 7. Development Roadmap & Status
**Current State: Phase 14 Completed. The project core is fully implemented.**

- [x] Phase 0 - Product + Architecture
- [x] Phase 1 - Project Setup
- [x] Phase 2 - Authentication + Organizations
- [x] Phase 3 - Document Management
- [x] Phase 4 - Document Processing + Embeddings
- [x] Phase 5 - Vector Search + RAG
- [x] Phase 6 - Chat + Citations
- [x] Phase 7 - Hybrid Search
- [x] Phase 8 - AI Evaluation
- [x] Phase 9 - Security Hardening
- [x] Phase 10 - Observability
- [x] Phase 11 - Agents
- [x] Phase 12 - Docker
- [x] Phase 13 - CI/CD
- [x] Phase 14 - Testing + Security Testing
- [ ] Phase 15 - Portfolio Documentation (In Progress)

## 8. How to Run Locally (Docker Recommended)

### Option A: Docker Compose (Easiest)
1. Clone the repository.
2. Copy the environment template: `cp .env.example .env`
3. Fill in your `.env` file using the exact keys expected. You MUST provide Supabase keys.
4. Run the cluster:
   ```bash
   docker compose up --build
   ```
   This spins up the Next.js frontend (port 3000), FastAPI backend (port 8000), and automatically initializes Ollama, pulling required models on startup.

### Option B: Local Development Native
**Backend**
```bash
cd backend
python -m venv venv311
source venv311/bin/activate  # Or .\venv311\Scripts\activate on Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## 9. Testing & CI/CD
The project features a comprehensive Continuous Integration pipeline (`ci.yml`) ensuring high security and stability:
- **Backend Testing**: 90+ `pytest` security integration tests running against ephemeral `pgvector` instances.
- **Frontend Validation**: ESLint and Next.js standalone production build checks.
- **Docker Validation**: Build checks for deployment images.
To run backend tests locally: `cd backend && pytest tests/ -v`
