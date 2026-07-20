from fastapi import FastAPI, Depends
from sqlmodel import Session
from contextlib import asynccontextmanager
from sqlalchemy import text
from src.database import create_db_and_tables, get_session
from src.routers import auth, agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title='Verdict', lifespan=lifespan)

app.include_router(auth.router, prefix='/auth', tags=["auth"])
app.include_router(agent.router, prefix='/agent', tags=["agent"])

@app.get('/health')
def health():
    return {"status":"ok"}

@app.get('/db-ping')
def db_ping(session: Session = Depends(get_session)):
    session.execute(text("SELECT 1"))
    return {"db":"ok"}