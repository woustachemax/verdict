from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import Session
from sqlalchemy import text
from src.database import create_db_and_tables, get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Verdict", lifespan=lifespan)


@app.get('/health')
def health():
    return {"status": "ok"}


@app.get('/db-ping')
def db_ping(session: Session = Depends(get_session)):
    session.execute(text("SELECT 1"))
    return {"db": "ok"}