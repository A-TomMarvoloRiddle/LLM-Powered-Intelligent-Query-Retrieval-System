from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Any, Optional
from datetime import datetime

class EvaluationRequest(BaseModel):
    documents: str  # PDF URL
    questions: List[str]

class EvaluationResponse(BaseModel):
    answers: List[str]

class DocumentQueryCreate(BaseModel):
    document_url: str
    document_name: Optional[str]
    questions: List[str]
    retrieved_chunks: List[Dict[str, Any]]
    answers: List[str]
    processing_time: Optional[int]

class DocumentQueryResponse(BaseModel):
    id: int
    document_url: str
    document_name: Optional[str]
    questions: List[str]
    retrieved_chunks: List[Dict[str, Any]]
    answers: List[str]
    processing_time: Optional[int]
    created_at: datetime