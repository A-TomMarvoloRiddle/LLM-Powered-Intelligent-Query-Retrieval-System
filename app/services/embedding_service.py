from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.config.settings import settings
from app.utils.logger import logger

class EmbeddingService:
    def __init__(self):
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        self.model = SentenceTransformer(settings.embedding_model)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        print(f"Generating embeddings for {len(texts)} texts")
        """Generate embeddings for multiple texts."""
        try:
            print("Starting batch embedding generation...")
            embeddings = self.model.encode(texts)
            print(f"Generated embeddings for {len(embeddings)} texts")
            if len(embeddings) == 0:
                raise ValueError("No embeddings generated. Check input texts.")
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
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