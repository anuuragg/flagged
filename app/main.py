from fastapi import FastAPI
from app.core.config import settings

from app.db.session import engine, get_db
from app.db.base import Base
from fastapi import Depends
from sqlalchemy import text

from contextlib import asynccontextmanager

from app.api.routes.auth import router as auth_router
from app.api.routes.login import router as login_router
from app.api.routes.games import router as games_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    import app.models
    Base.metadata.create_all(bind = engine)

    yield

app = FastAPI(lifespan = lifespan)

app.include_router(auth_router)
app.include_router(login_router)
app.include_router(games_router)



@app.get("/")
def root():
    return {"welcome to flagged api!"}

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.ENVIRONMENT}

@app.get("/health/db")
def db_health(db = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"db": "ok"}