from sqlalchemy import text
from sqlmodel import create_engine, Session, SQLModel

from src.config import settings


def _build_engine():
    if settings.DATABASE_URL.startswith("sqlite"):
        return create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return engine
    except Exception:
        if settings.ENV == "production":
            raise
        return create_engine("sqlite:///./app.db", connect_args={"check_same_thread": False})


engine = _build_engine()


def create_db_and_tables():
    from src.models import user
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session