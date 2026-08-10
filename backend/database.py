import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

logger = logging.getLogger("rag_pipeline")

_engine = None
Base = declarative_base()


def _get_engine():
    """Lazily create the engine using centralized settings."""
    global _engine
    if _engine is None:
        if not settings.database_url:
            raise ValueError("DATABASE_URL is not set in configuration")
        _engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow
        )
    return _engine


def SessionLocal():
    """Get a new database session."""
    engine = _get_engine()
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return session_factory()


def init_db():
    """Create all tables if they don't exist."""
    engine = _get_engine()
    Base.metadata.create_all(bind=engine)