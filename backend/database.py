import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agentdesk:agentdesk_password@127.0.0.1:5433/agentdesk_db")

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
        # Try to connect to the database to verify the connection
        connection = engine.connect()
        connection.close()
        logger.info("Successfully connected to the database!")
        return True
    except OperationalError as e:
        logger.error(f"Failed to connect to the database. Error: {e}")
        return False
