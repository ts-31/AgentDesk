import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import verify_db_connection, init_db, SessionLocal
from models import Customer
from seed import seed_database

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: connects to DB, initialises tables, and auto-seeds if empty."""
    logger.info("Starting application...")
    is_connected = verify_db_connection()
    if not is_connected:
        logger.warning("Database connection failed, but the application will continue starting.")
    else:
        logger.info("Initialising database tables...")
        init_db()
        logger.info("Database tables initialised.")

        # Auto-seed if the database is empty
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
