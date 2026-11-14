from fastapi import FastAPI

api = FastAPI(title="FinDoc AI")


@api.get("/health")
def health():
    return {"status": "ok"}
from config import MODEL_NAME


@api.get("/info")
def info():
    return {"name": "FinDoc AI", "model": MODEL_NAME}