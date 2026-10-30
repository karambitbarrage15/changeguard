"""
ChangeGuard RAG (Retrieval-Augmented Generation) Engine API.
Provides semantic retrieval over historical post-mortems and incident playbooks.
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from app.retriever import RAGRetriever

logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "rag-engine", "message": "%(message)s"}'
)
logger = logging.getLogger("changeguard.rag")

KB_DIR = os.getenv("KB_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../knowledge_base")))
retriever = RAGRetriever(KB_DIR)

app = FastAPI(
    title="ChangeGuard - RAG Knowledge Engine",
    description="Historical incident matching & playbook retrieval using vectorized semantic search",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str = Field(..., description="Alert description, error stack trace, or incident symptoms")
    top_k: Optional[int] = Field(default=3, ge=1, le=10)

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "rag-engine",
        "indexed_documents": len(retriever.get_all())
    }

@app.post("/rag/query")
def query_knowledge_base(req: QueryRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    logger.info(f"RAG query received: '{req.query}' (top_k={req.top_k})")
    matches = retriever.retrieve(req.query, top_k=req.top_k)

    return {
        "query": req.query,
        "total_matches": len(matches),
        "matches": matches
    }

@app.get("/rag/postmortems")
def list_postmortems():
    return {
        "count": len(retriever.get_all()),
        "postmortems": [
            {
                "id": doc["id"],
                "title": doc["title"],
                "severity": doc["severity"],
                "root_cause": doc["root_cause"][:150] + "..." if len(doc["root_cause"]) > 150 else doc["root_cause"]
            }
            for doc in retriever.get_all()
        ]
    }
