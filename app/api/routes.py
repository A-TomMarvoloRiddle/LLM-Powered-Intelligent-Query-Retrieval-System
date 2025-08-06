from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import time

from app.models.database import get_db, DocumentQuery
from app.models.schemas import EvaluationRequest, EvaluationResponse, DocumentQueryCreate
from app.services.rag_service import RAGService
from app.api.auth import verify_token
from app.utils.logger import logger

router = APIRouter()
rag_service = RAGService()

@router.post("/hackrx/run", response_model=EvaluationResponse)
async def evaluate_document(
    request: EvaluationRequest,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    """Main endpoint for document evaluation."""
    try:
        # Validate input
        if not request.questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Questions list cannot be empty"
            )
        
        if len(request.questions) > 20:  # Reasonable limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many questions. Maximum 20 questions allowed."
            )
        
        logger.info(f"Processing document: {request.documents}")
        logger.info(f"Number of questions: {len(request.questions)}")
        
        # Process document and questions
        result = await rag_service.process_document_and_questions(
            request.documents, request.questions
        )
        
        # Save to database
        db_record = DocumentQuery(
            document_url=request.documents,
            document_name=result["document_name"],
            questions=request.questions,
            retrieved_chunks=result["retrieved_chunks"],
            answers=result["answers"],
            processing_time=result["processing_time"]
        )
        db.add(db_record)
        db.commit()
        
        logger.info(f"Successfully processed document. Processing time: {result['processing_time']}ms")
        
        return EvaluationResponse(answers=result["answers"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": time.time()}

@router.get("/queries", response_model=List[dict])
async def get_queries(
    db: Session = Depends(get_db),
    token: str = Depends(verify_token),
    limit: int = 10
):
    """Get recent queries (for debugging/monitoring)."""
    queries = db.query(DocumentQuery).order_by(
        DocumentQuery.created_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": q.id,
            "document_url": q.document_url,
            "questions_count": len(q.questions),
            "processing_time": q.processing_time,
            "created_at": q.created_at
        }
        for q in queries
    ]