# TeamFlow Backend

## Overview
TeamFlow is a customer support backend built with FastAPI, PostgreSQL, `pgvector`, and a Markdown-based knowledge base with semantic search.

## Project Structure
```text
backend/
├── agent/              # Grok-based RAG answer generation logic
├── auth/               # JWT authentication and hashing utilities
├── core/               # Core configurations and application setup
├── docs/               # API examples and documentation
├── indexing/           # Knowledge base document processing and embedding logic
├── init/               # DB initialization scripts (e.g., pgvector setup)
├── knowledge_base/     # Source Markdown files for the knowledge base
├── models/             # SQLAlchemy database models
├── routers/            # FastAPI route handlers (API endpoints)
├── schemas/            # Pydantic validation schemas
├── search/             # Vector similarity search and retrieval implementation
├── app.py              # FastAPI application initialization (CORS configured for frontend)
├── database.py         # Database connection and session management
├── docker-compose.yml  # PostgreSQL database container configuration
└── start.sh            # Entrypoint script to handle Docker, DB, and server startup
```

## Integration with Frontend
The backend is configured with `CORSMiddleware` in `app.py` to accept requests from the frontend at `http://localhost:3000` by default. You can override the allowed origins in production by setting the `ALLOWED_ORIGINS` environment variable (e.g. `ALLOWED_ORIGINS=https://app.teamflow.io,https://admin.teamflow.io`).

## Setup & Run

**1. Clone the repository**
```bash
git clone <repository_url>
cd TeamFlow/backend
```

**2. Create and activate a virtual environment**
```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash
# or: .venv\Scripts\activate   # Windows PowerShell
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Start Docker services**
```bash
docker-compose up -d
```

**5. Run the application**
```bash
bash start.sh
```
