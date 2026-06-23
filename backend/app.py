import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.lifespan import lifespan
from routers import (
    auth_router,
    customers_router,
    users_router,
    subscriptions_router,
    invoices_router,
    tickets_router,
    knowledge_base_router,
    agent_router,
)

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AgentDesk API", lifespan=lifespan)

# Allow requests from the frontend origin.
# Override ALLOWED_ORIGINS in production (comma-separated list of origins).
_allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(customers_router)
app.include_router(users_router)
app.include_router(subscriptions_router)
app.include_router(invoices_router)
app.include_router(tickets_router)
app.include_router(knowledge_base_router)
app.include_router(agent_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
