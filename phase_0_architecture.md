# KnowledgeHub AI - Phase 0 Architecture (Final)

## 1. Final Repository Architecture
- **What it is**: A monorepo structure containing both frontend and backend codebases.
- **How it works**:
  ```text
  knowledgehub-ai/
  ├── frontend/       # Next.js app (All 3 Portals)
  ├── backend/        # FastAPI app
  ├── docker/         # Shared docker configs
  └── .github/        # CI/CD workflows
  ```
- **Why we need it**: Avoids the complexity of managing multiple git repositories for a tightly coupled product.

## 2. Final System Architecture
- **What it is**: A modular monolith.
- **How it works**: The Next.js frontend handles UI and client state. It communicates via REST to the FastAPI backend. FastAPI orchestrates all business logic, AI operations, and communicates with Supabase (Auth, Postgres `pgvector`, Storage).

## 3. Three-Portal Architecture
KnowledgeHub AI features three distinct portals within the single Next.js application, separated logically by route groups and access controls:
- **PORTAL 1: Public Portal**: Marketing site explaining the product, features, architecture, and providing entry points for Login, Register, and Demo. Exposes zero private data.
- **PORTAL 2: Organization / Admin Portal**: Accessible to `ADMIN` and `KNOWLEDGE_MANAGER` roles. Provides dashboards for managing members, document ingestion, permissions, organization settings, and AI analytics.
- **PORTAL 3: Employee Portal**: Accessible to `MEMBER` roles. A focused interface dedicated entirely to the AI knowledge assistant, chat history, and authorized document search.

## 4. Database / Entity Model
- **Core Entities**:
  - `organizations` (id, name, settings)
  - `users` (id, email, linked to Supabase Auth UUID)
  - `memberships` (id, user_id, organization_id, role)
  - `documents` (id, organization_id, name, storage_path, status)
  - `document_permissions` (id, document_id, granted_to_role, granted_to_user_id)
  - `document_chunks` (id, document_id, content, embedding [vector], metadata)
  - `conversations` (id, user_id, organization_id, title)
  - `messages` (id, conversation_id, role, content)
  - `citations` (id, message_id, chunk_id)

## 5. Multi-Tenancy Model
- **Model**: Logical isolation (row-level) within a shared database schema.
- **Enforcement**: Every core table requires an `organization_id`. PostgreSQL Row Level Security (RLS) policies and strict FastAPI dependency injections guarantee that queries only touch data belonging to the authenticated user's organization.

## 6. Authentication
- **Mechanism**: Supabase Auth (JWT).
- **Flow**: Next.js and FastAPI independently verify the cryptographic signature of the Supabase JWT to establish "who" the user is.

## 7. Authorization
- **Mechanism**: Custom DB logic via the `memberships` table.
- **Flow**: Before any API action, FastAPI verifies the user has an active membership in the target `organization_id` and possesses the required role. Portal visibility in the frontend is not a security boundary; the backend strictly enforces all access.

## 8. RBAC (Role-Based Access Control)
- **Roles**:
  - `ADMIN`: Full organization, user, and security control.
  - `KNOWLEDGE_MANAGER`: Can upload, manage, and configure access for documents.
  - `MEMBER`: Standard employee, restricted to querying authorized knowledge.

## 9. Document Permissions
- **Enforcement**: Access control applied *before* AI retrieval.
- **ADMIN Access Policy**: An `ADMIN` has full access to manage members and organization settings. However, an `ADMIN` does **not** automatically bypass document-level reading permissions. If a document is restricted to a specific user or department, the `ADMIN` cannot query it via the AI or read its contents unless they explicitly alter the document's permission configuration to include themselves (which would be audit-logged). This ensures strict separation of administrative privileges and sensitive data access.
- **Mechanism**: Permissions are stored in the normalized `document_permissions` table. During vector search, a SQL `JOIN` and `WHERE` clause explicitly filters out any `document_chunks` the user is not authorized to read. The LLM is never trusted to filter restricted information.

## 10. Document Ingestion Architecture
- **Pipeline**: Upload -> Supabase Storage -> Python Text Extraction (`PyMuPDF`, etc.) -> Semantic Chunking -> Embedding Model -> Insert to PostgreSQL (`pgvector`).
- **Processing**: Handled exclusively via FastAPI `BackgroundTasks` to prevent blocking the web server. We will not introduce Redis or Celery for the MVP to maintain architectural simplicity.

## 11. RAG Architecture
- **Pipeline**: Question -> Embedding -> Permission-filtered Vector Search -> Context Construction -> LLM -> Grounded Answer.
- **Control**: Custom built in FastAPI (no LangChain/LlamaIndex) to maintain absolute control over multi-tenant filtering, prompt injection defense, and citation extraction.

## 12. Hybrid Search Architecture
- **What it is**: Combining semantic meaning with exact keyword matching.
- **How it works**: Queries hit `pgvector` for semantic similarity and PostgreSQL's native Full-Text Search (`to_tsvector`) for keywords. Results are merged and ranked using Reciprocal Rank Fusion (RRF) before context construction.

## 13. Citation Architecture
- **Mechanism**: The context injected into the LLM includes explicit chunk markers (e.g., `[CHUNK_ID: 123]`). The LLM is prompted via structured output (JSON) to return an array of `chunk_id`s it utilized. The backend verifies these IDs belong to the authorized context, and the frontend renders them as clickable links to the source document page/section.

## 14. API Architecture
- **Structure**: RESTful JSON APIs built with FastAPI, grouped by domain (`/api/v1/auth`, `/api/v1/documents`, `/api/v1/chat`).

## 15. Security Architecture
- **Defense-in-depth**: DB RLS -> Backend Route Dependencies -> Strict UI routing.
- **Data Protection**: Document instructions are treated purely as untrusted data strings, cleanly separated from system-level instructions in the LLM prompt to prevent prompt injection attacks.

## 16. Environment Configuration
- **Management**: `pydantic-settings` validates `.env` files on backend startup. Secrets (DB URLs, API keys) are never committed.

## 17. Development Workflow
- **Process**: GitHub feature branch workflow (`main` is protected). PRs require CI checks to pass before merging.

## 18. Testing Strategy
- **Coverage**: `pytest` for backend API endpoints, tenant isolation checks, and RAG logic (using mocked LLM responses to keep CI fast and free). Next.js component tests for critical UI flows.

## 19. Initial Dependencies
- **Frontend**: Next.js, React, Tailwind CSS, `lucide-react`, `@supabase/supabase-js`.
- **Backend**: FastAPI, `pydantic`, `SQLAlchemy[asyncio]`, `asyncpg` (async DB driver), `pgvector`, `PyMuPDF`, `openai` (or abstract LLM client).

## 20. Technology Decisions
- **SQLAlchemy + asyncpg**: Since FastAPI is an asynchronous framework, using standard synchronous `psycopg2` would block the event loop during database I/O, destroying concurrency. We will use `SQLAlchemy` with the `asyncpg` driver for fully non-blocking database interactions.
- **Postgres + pgvector**: Keeps relational metadata (permissions, tenant IDs) and vectors in the *same database*, enabling highly secure `JOIN` and `WHERE` filtering in a single query.
- **Supabase**: Consolidates Auth, DB, and Storage.
- **Next.js + FastAPI**: Industry standard separation of interactive UI and heavy AI/Data processing.

## 21. Portal Routing & Frontend Structure
```text
frontend/
├── app/
│   ├── (public)/              # PORTAL 1
│   │   ├── page.tsx
│   │   ├── features/
│   │   ├── security/
│   │   └── demo/
│   │
│   ├── (authenticated)/
│   │   ├── admin/             # PORTAL 2
│   │   │   ├── dashboard/
│   │   │   ├── documents/
│   │   │   ├── members/
│   │   │   ├── permissions/
│   │   │   └── settings/
│   │   │
│   │   └── employee/          # PORTAL 3
│   │       ├── chat/
│   │       ├── conversations/
│   │       └── profile/
```

## 22. Portal Access Matrix

| Feature | Public | Admin | Knowledge Manager | Member |
| :--- | :--- | :--- | :--- | :--- |
| Landing/Features | ✓ | ✓ | ✓ | ✓ |
| Login/Register | ✓ | ✓ | ✓ | ✓ |
| Org Dashboard | ✗ | ✓ | Limited | ✗ |
| Documents List | ✗ | ✓ | ✓ | Authorized only |
| Upload Documents | ✗ | ✓ | ✓ | ✗ |
| Members / Roles | ✗ | ✓ | ✗ | ✗ |
| Permissions Config | ✗ | ✓ | Limited | ✗ |
| AI Chat | Demo | ✓ | ✓ | ✓ |
| Conversations | ✗ | Own | Own | Own |
| AI Analytics | ✗ | ✓ | Limited | ✗ |
| Org Settings | ✗ | ✓ | ✗ | ✗ |
| Profile | ✗ | ✓ | ✓ | ✓ |

## 23. Demo Architecture
- **Setup**: A dedicated sample organization (e.g., "KnowledgeHub Demo Org") populated with non-sensitive sample documents (e.g., standard Employee Handbooks).
- **Access**: Demo users are configured with specific roles to safely demonstrate capabilities (like permission-aware chat) without exposing any real corporate data.

## 24. Phase-by-Phase Implementation Plan
- **PHASE 0**: Product + Architecture (Completed)
- **PHASE 1**: Project Setup (Repo, Next.js, FastAPI initialization)
- **PHASE 2**: Authentication + Organizations (Supabase Auth, DB schema)
- **PHASE 3**: Document Management (UI + Storage)
- **PHASE 4**: Document Processing + Embeddings (Parsing, Chunking, pgvector)
- **PHASE 5**: Vector Search + Basic RAG (Retrieval pipeline, LLM connection)
- **PHASE 6**: Chat + Citations (Employee Portal UI, streaming, source links)
- **PHASE 7**: Hybrid Search (Postgres Full-Text integration)
- **PHASE 8**: AI Evaluation (Metrics for retrieval/generation)
- **PHASE 9**: Multi-Tenant Security Hardening (Audit and RLS checks)
- **PHASE 10**: AI Observability (Logging request traces and latencies)
- **PHASE 11**: Controlled AI Agents (Adding tool calling to RAG)
- **PHASE 12**: Docker + Deployment (Containerization)
- **PHASE 13**: CI/CD (GitHub Actions)
- **PHASE 14**: Testing + Security Testing
- **PHASE 15**: GitHub Portfolio Documentation (README, architecture diagrams)
