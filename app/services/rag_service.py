from typing import List, Dict, Any
import time
from app.services.pdf_parser import PDFParser
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.llm_service import LLMService
from app.models.database import SessionLocal, DocumentQuery
from app.utils.logger import logger

class RAGService:
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.llm_service = LLMService()
    
    def document_exists_in_db(self, document_url: str) -> bool:
        """Check if document already exists in PostgreSQL database."""
        db = SessionLocal()
        try:
            existing_query = db.query(DocumentQuery).filter(
                DocumentQuery.document_url == document_url
            ).first()
            return existing_query is not None
        finally:
            db.close()
    
    def get_existing_document_data(self, document_url: str) -> Dict[str, Any]:
        """Get existing document data from PostgreSQL database."""
        db = SessionLocal()
        try:
            existing_query = db.query(DocumentQuery).filter(
                DocumentQuery.document_url == document_url
            ).first()
            
            if existing_query:
                return {
                    "document_url": existing_query.document_url,
                    "document_name": existing_query.document_name,
                    "questions": existing_query.questions,
                    "retrieved_chunks": existing_query.retrieved_chunks,
                    "answers": existing_query.answers,
                    "processing_time": existing_query.processing_time
                }
            return None
        finally:
            db.close()
    
    def process_document_and_questions(self, document_url: str, questions: List[str]) -> Dict[str, Any]:
        """Main RAG pipeline."""
        start_time = time.time()
        doc_name = self._extract_document_name(document_url)
        
        try:
            logger.info(f"Starting RAG pipeline for document: {document_url}")
            logger.info(f"Questions to process: {len(questions)}")
            
            # Check if document already exists in PostgreSQL
            if self.document_exists_in_db(document_url):
                logger.info(f"Document already exists in database. Skipping parsing and storage.")
                # Use existing data from database
                existing_data = self.get_existing_document_data(document_url)
                
                # Check if the same questions were already processed
                if set(existing_data["questions"]) == set(questions):
                    logger.info("Same questions already processed. Returning cached results.")
                    return {
                        "answers": existing_data["answers"],
                        "retrieved_chunks": existing_data["retrieved_chunks"],
                        "processing_time": existing_data["processing_time"],
                        "document_name": existing_data["document_name"],
                        "cached": True
                    }
                else:
                    # Different questions, but document already processed
                    logger.info("Document exists but different questions. Processing new questions only.")
                    # We'll need to re-process since we don't have the original chunks stored
                    # This is a limitation - we could enhance this by storing chunks in PostgreSQL too
                    all_chunks = []
            else:
                # Step 1: Parse PDF
                logger.info("Step 1: Parsing PDF...")
                parsed_text = self.pdf_parser.parse_pdf_from_url(document_url)
                
                # Step 2: Chunk text
                logger.info("Step 2: Chunking text...")
                chunks = self.embedding_service.chunk_text(parsed_text)
                
                # Step 3: Generate embeddings for chunks
                logger.info("Step 3: Generating embeddings for chunks...")
                chunk_embeddings = self.embedding_service.embed_batch(chunks)
                
                # Step 4: Store in vector database
                logger.info("Step 4: Storing embeddings...")
                chunk_ids = self.vector_store.store_embeddings(
                    chunks, chunk_embeddings, document_url
                )
                all_chunks = self.vector_store.get_document_chunks(document_url)
            
            # Step 5: Process questions
            logger.info("Step 5: Processing questions...")
            answers = []
            all_retrieved_chunks = []
            
            for question in questions:
                # Generate question embedding
                question_embedding = self.embedding_service.embed_text(question)
                
                # Retrieve relevant chunks
                retrieved_chunks = self.vector_store.search_similar(question_embedding)
                all_retrieved_chunks.append({
                    "question": question,
                    "chunks": retrieved_chunks
                })
                
                # Generate answer
                answer = self.llm_service.generate_answer(question, retrieved_chunks)
                answers.append(answer)
            
            processing_time = int((time.time() - start_time) * 1000)  # milliseconds
            
            # Store results in PostgreSQL database
            self._store_query_results(document_url, doc_name, questions, all_retrieved_chunks, answers, processing_time)
            
            return {
                "answers": answers,
                "retrieved_chunks": all_retrieved_chunks,
                "processing_time": processing_time,
                "document_name": doc_name,
                "cached": False
            }
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {str(e)}")
            raise
    
    def _store_query_results(self, document_url: str, document_name: str, questions: List[str], retrieved_chunks: List[Dict], answers: List[str], processing_time: int):
        """Store query results in PostgreSQL database."""
        db = SessionLocal()
        try:
            # Check if record already exists
            existing_query = db.query(DocumentQuery).filter(
                DocumentQuery.document_url == document_url
            ).first()
            
            if existing_query:
                # Update existing record
                existing_query.questions = questions
                existing_query.retrieved_chunks = retrieved_chunks
                existing_query.answers = answers
                existing_query.processing_time = processing_time
            else:
                # Create new record
                new_query = DocumentQuery(
                    document_url=document_url,
                    document_name=document_name,
                    questions=questions,
                    retrieved_chunks=retrieved_chunks,
                    answers=answers,
                    processing_time=processing_time
                )
                db.add(new_query)
            
            db.commit()
            logger.info("Query results stored in database")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing query results: {str(e)}")
        finally:
            db.close()
    
    def _extract_document_name(self, url: str) -> str:
        """Extract document name from URL."""
        try:
            return url.split('/')[-1].split('?')[0]
        except:
            return "unknown_document.pdf"