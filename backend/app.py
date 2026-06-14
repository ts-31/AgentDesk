import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import verify_db_connection, init_db, SessionLocal
from models import Customer
from seed import seed_database
from routers import customers_router, users_router, subscriptions_router, invoices_router, tickets_router
from seed import seed_database

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
    else:
        logger.info("Initializing database tables...")
        init_db()
        logger.info("Database tables initialized.")
        
        # Check if database is empty and auto-seed
        db = SessionLocal()
        try:
            customer_count = db.query(Customer).count()
            if customer_count == 0:
                logger.info("Database is empty. Automatically running seed process...")
                seed_database()
            else:
                logger.info(f"Database contains data ({customer_count} customers). Skipping seed process.")
        except Exception as e:
            logger.error(f"Failed to check or seed database: {e}")
        finally:
            db.close()
            
    yield
    logger.info("Shutting down application...")

app = FastAPI(title="AgentDesk API", lifespan=lifespan)

app.include_router(customers_router)
app.include_router(users_router)
app.include_router(subscriptions_router)
app.include_router(invoices_router)
app.include_router(tickets_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
