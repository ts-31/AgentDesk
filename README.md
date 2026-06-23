# TeamFlow — AI-Powered Customer Support Platform

A full-stack, production-grade agentic AI application. TeamFlow is an internal customer support tool where support agents interact with a **LangGraph-orchestrated ReAct agent** that can answer questions from a knowledge base, look up live CRM data, and take actions — all decided dynamically by the LLM in a single unified reasoning loop.

---

## ✨ Key Features

- **ReAct Agent Loop** — A LangGraph graph where the LLM reasons at every step and decides which tools to call — or whether to answer directly — with no upfront intent classification.
- **RAG as a Tool** — Knowledge base retrieval (`retrieve_kb`) is just another tool available to the agent. It internally handles query rewriting for multi-turn follow-ups before hitting `pgvector`. The LLM can call it alongside CRM tools in the same turn.
- **Live CRM Tool Calling** — The agent can look up customers, subscriptions, invoices, and tickets, and create new tickets in real time against a PostgreSQL database.
- **Multi-Turn Conversational Memory** — Conversation state is persisted per `thread_id` using `langgraph-checkpoint-postgres`, enabling fully context-aware multi-turn chat.
- **JWT Authentication** — Stateless access + refresh token flow (HS256). The agent's CRM tools are automatically scoped to the logged-in user's workspace via claims in the JWT — no user ID prompting needed.
- **React Frontend** — Clean chat UI (Vite + React + TypeScript + Tailwind) with silent token refresh, session persistence, and a Vite dev proxy.

---

## 🏗️ Architecture

```mermaid
graph TD
    subgraph Frontend ["Frontend (React + Vite)"]
        UI["Chat UI"]
        AC["AuthContext + API Client\n(JWT + silent refresh)"]
    end

    subgraph Backend ["Backend (FastAPI)"]
        API["POST /agent/ask\n(JWT-protected)"]

        subgraph LangGraph ["LangGraph ReAct Agent"]
            AGT["agent\nreact_agent_node"]
            TN["tools\nToolNode"]
            AGT -- "tool_calls present" --> TN
            TN -- "loop" --> AGT
            AGT -- "no tool_calls" --> DONE(["END"])
        end

        API --> LangGraph
    end

    subgraph Data ["Data Layer (PostgreSQL)"]
        PG["CRM Tables\nCustomers · Tickets · Invoices · Subscriptions"]
        VEC["pgvector\nKnowledge Base Embeddings"]
        MEM["Checkpoint Tables\nConversation Memory"]
    end

    UI --> AC --> API
    TN --> PG
    TN --> VEC
    LangGraph --> MEM
```

### How the agent decides what to do

There is no intent classifier. The LLM receives a system prompt listing all available tools and reasons at each step about what to call next:

| Scenario | What happens |
|---|---|
| *"How do I reset my password?"* | LLM calls `retrieve_kb` → reads KB chunks from `ToolMessage` → synthesizes answer |
| *"Show me my invoices"* | LLM calls `get_customer_invoices` → reads DB result → synthesizes answer |
| *"What plan am I on and what are its API limits?"* | LLM calls `get_customer_subscriptions` **and** `retrieve_kb` in one turn → synthesizes unified answer |
| *"Create a bug ticket"* | LLM calls `create_ticket` → confirms to user |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Grok (`langchain-xai`) |
| **Agent Orchestration** | LangGraph |
| **Embeddings** | `sentence-transformers` (local) |
| **Vector Store** | PostgreSQL + `pgvector` |
| **Memory / Checkpointing** | `langgraph-checkpoint-postgres` |
| **Backend API** | FastAPI + SQLAlchemy |
| **Authentication** | JWT (`python-jose`) + bcrypt |
| **Frontend** | React 19 + TypeScript + Vite + Tailwind CSS |
| **Database** | PostgreSQL (Docker) |

---

## 🚀 Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker Desktop

### 1. Start the database

```bash
cd backend
docker-compose up -d
```

### 2. Set up & run the backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows PowerShell
pip install -r requirements.txt
```

Create a `backend/.env` file:
```env
DATABASE_URL=postgresql://agentdesk:agentdesk_password@127.0.0.1:5433/agentdesk_db
XAI_API_KEY=your_xai_api_key_here
XAI_MODEL=grok-4.3
RAG_SIMILARITY_THRESHOLD=0.70
```

Then start the server:
```bash
bash start.sh   # seeds DB, indexes KB, starts uvicorn on port 8000
```

### 3. Set up & run the frontend

```bash
cd frontend
npm install
npm run dev     # opens http://localhost:3000
```

Log in with any user seeded by `backend/seed.py`.

---

## 📁 Project Structure

```
TeamFlow/
├── backend/
│   ├── agent/                  # LangGraph agent (graph, nodes, tools, memory)
│   │   └── tools/              # CRM tool functions (tickets, invoices, subscriptions)
│   ├── auth/                   # JWT creation, decoding, and FastAPI dependencies
│   ├── indexing/               # KB chunker and embedder
│   ├── knowledge_base/         # Source Markdown documents
│   ├── models/                 # SQLAlchemy ORM models
│   ├── routers/                # FastAPI route handlers
│   ├── schemas/                # Pydantic request/response models
│   ├── search/                 # pgvector similarity search
│   ├── docs/                   # Architecture documentation
│   ├── app.py                  # FastAPI app entry point (CORS configured)
│   └── seed.py                 # Database seeder with mock CRM data
└── frontend/
    ├── src/
    │   ├── api/                # client.ts · auth.ts · agent.ts
    │   ├── context/            # AuthContext (JWT session management)
    │   └── components/         # LoginScreen · SupportScreen
    └── vite.config.ts          # Dev proxy: /api → localhost:8000
```
