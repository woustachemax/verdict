from sqlmodel import create_engine, Session, SQLModel
from src.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True, 
    pool_recycle=300
)

def create_db_and_tables():
    from src.models import user
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session