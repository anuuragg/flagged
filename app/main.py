from fastapi import FastAPI
from .core.config import settings

app = FastAPI()

@app.get("/")
def root():
    return {"welcome to flagged api!"}

@app.get("/health")
def healh():
    return {"status": "ok", "env": settings.ENVIRONMENT}