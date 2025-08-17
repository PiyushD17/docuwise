# app/api/routes/query.py
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class QueryIn(BaseModel):
    question: str


class Source(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None


class QueryOut(BaseModel):
    answer: str
    sources: List[Source] = []


@router.post("/query", response_model=QueryOut)
def query_endpoint(payload: QueryIn) -> dict:
    # TODO: plug in retriever + LLM; this is a stub
    return {"answer": f"(stub) You asked: {payload.question}", "sources": []}
