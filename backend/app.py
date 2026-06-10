import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import verify_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify database connectivity during application startup
    logger.info("Starting application...")
    is_connected = verify_db_connection()
    if not is_connected:
        logger.warning("Database connection failed, but the application will continue starting.")
    yield
    logger.info("Shutting down application...")

app = FastAPI(title="AgentDesk API", lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "ok"}
