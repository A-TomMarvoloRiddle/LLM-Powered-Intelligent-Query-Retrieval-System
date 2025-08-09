from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
import time
from app.config.settings import settings
from app.utils.logger import logger

class EmbeddingService:
    def __init__(self):
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        try:
            start_time = time.time()
            self.model = SentenceTransformer(settings.embedding_model)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            load_time = time.time() - start_time
            logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
            logger.info(f"Embedding dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            logger.error("This might be due to network issues or insufficient memory")
            raise
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        logger.info(f"Starting batch embedding generation for {len(texts)} texts")
        try:
            if not texts:
                raise ValueError("Empty text list provided")
            
            start_time = time.time()
            embeddings = self.model.encode(texts, show_progress_bar=True)
            process_time = time.time() - start_time
            
            logger.info(f"Generated {len(embeddings)} embeddings in {process_time:.2f} seconds")
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            logger.error(f"Input texts count: {len(texts)}")
            logger.error(f"First few texts: {texts[:2] if texts else 'None'}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Split text into chunks."""
        chunk_size = chunk_size or settings.chunk_size
        overlap = overlap or settings.chunk_overlap
        
        # Simple sentence-based chunking
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"Text split into {len(chunks)} chunks")
        return chunks