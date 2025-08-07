from typing import List, Dict, Any
import time
from app.services.pdf_parser import PDFParser
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore
from app.services.llm_service import LLMService
from app.utils.logger import logger

class RAGService:
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        self.llm_service = LLMService()
    
    def process_document_and_questions(self, document_url: str, 
                                     questions: List[str]) -> Dict[str, Any]:
        """Main RAG pipeline."""
        start_time = time.time()
        
        try:
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
            
            return {
                "answers": answers,
                "retrieved_chunks": all_retrieved_chunks,
                "processing_time": processing_time,
                "document_name": self._extract_document_name(document_url)
            }
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {str(e)}")
            raise
    
    def _extract_document_name(self, url: str) -> str:
        """Extract document name from URL."""
        try:
            return url.split('/')[-1].split('?')[0]
        except:
            return "unknown_document.pdf"