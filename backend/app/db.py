from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import DATABASE_URL
from app.models import Base

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Turn on pgvector and build the tables if they don't exist."""
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)