# SQLAlchemy function to create a database engine (connection factory)
from sqlalchemy import create_engine, text

# SQLAlchemy session management
from sqlalchemy.orm import sessionmaker

# Base class that holds all ORM models (tables)
from common.models import Base


# =========================
# DATABASE CONFIGURATION
# =========================

# PostgreSQL connection string
# Format:
# postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME
DATABASE_URL = "postgresql://jobuser:jobpass@localhost:5432/jobdb"


# =========================
# DATABASE ENGINE SETUP
# =========================

# Create SQLAlchemy engine
# The engine manages database connections
engine = create_engine(DATABASE_URL)


# Create a session factory
# autocommit=False → transactions must be committed manually
# autoflush=False → changes are flushed only when explicitly committed
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# =========================
# DATABASE HEALTH CHECK
# =========================

def test_connection():
    """
    Verifies that the database is reachable.

    - Opens a database connection
    - Executes a simple query
    - Closes the connection automatically

    If this function runs without error,
    PostgreSQL is alive and accessible.
    """
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


# =========================
# TABLE CREATION
# =========================

def create_tables():
    """
    Creates all database tables defined by ORM models.

    - Reads all models inheriting from Base
    - Creates missing tables only
    - Safe to run multiple times

    Used at API startup to ensure schema exists.
    """
    Base.metadata.create_all(bind=engine)
