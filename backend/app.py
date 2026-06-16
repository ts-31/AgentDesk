import logging
from fastapi import FastAPI
from core.lifespan import lifespan
from routers import (
    customers_router,
    users_router,
    subscriptions_router,
    invoices_router,
    tickets_router,
    knowledge_base_router,
)

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="AgentDesk API", lifespan=lifespan)

app.include_router(customers_router)
app.include_router(users_router)
app.include_router(subscriptions_router)
app.include_router(invoices_router)
app.include_router(tickets_router)
app.include_router(knowledge_base_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
