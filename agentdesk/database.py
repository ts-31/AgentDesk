import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from config import settings

DATABASE_URL = settings.database_url

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=False)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)

def verify_db_connection():
    logger = logging.getLogger(__name__)
    try:
        connection = engine.connect()
        connection.close()
        logger.info("Successfully connected to the database!")
        return True
    except OperationalError as e:
        logger.error(f"Failed to connect to the database. Error: {e}")
        return False

def enable_pgvector():
    """Create the pgvector extension if it does not already exist."""
    logger = logging.getLogger(__name__)
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        logger.info("pgvector extension enabled.")
    except Exception as e:
        logger.error(f"Failed to enable pgvector extension: {e}")

def verify_pgvector():
    """Return True if the pgvector extension is active in the database."""
    logger = logging.getLogger(__name__)
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            )
            row = result.fetchone()
            if row:
                logger.info(f"pgvector is active (version: {row[0]}).")
                return True
            else:
                logger.warning("pgvector extension is NOT active.")
                return False
    except Exception as e:
        logger.error(f"Failed to verify pgvector: {e}")
        return False

