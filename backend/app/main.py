from sqlalchemy import text
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, HTTPException, UploadFile

from app import rag
from app.db import engine
from app.config import CORS_ORIGINS
from app.loaders import extract_text


app = FastAPI(title="Ask My Docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    question: str = Field(min_length=1)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/health/db")
def health_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"database": "ok"}

@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    data = await file.read()
    try:
        content = extract_text(file.filename, data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    if not content.strip():
        raise HTTPException(status_code=400, detail="No readable text found in file")
    chunks = rag.ingest_text(content, source=file.filename)
    return {"filename": file.filename, "chunks": chunks}


@app.post("/ask")
def ask_question(body: AskRequest):
    try:
        return rag.ask(body.question)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error))