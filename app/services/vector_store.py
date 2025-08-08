from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any, Tuple
from app.config.settings import settings
from app.utils.logger import logger
import uuid
import time

class VectorStore:
    def __init__(self):
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index_name = settings.pinecone_index_name
        
        # Check if index exists before creating
        existing_indexes = self.pc.list_indexes()
        index_names = [index['name'] for index in existing_indexes]
        
        if self.index_name not in index_names:
            logger.info(f"Creating Pinecone index: {self.index_name}")
            self.pc.create_index(
                name=self.index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )

            # Wait for index to be ready
            time.sleep(5)
        
        self.index = self.pc.Index(self.index_name)
    
    def store_embeddings(self, chunks: List[str], embeddings: List[List[float]], 
                        document_url: str) -> List[str]:
        """Store embeddings in Pinecone."""
        try:
            vectors = []
            chunk_ids = []
            
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = f"{document_url}_{i}_{uuid.uuid4().hex[:8]}"
                chunk_ids.append(chunk_id)
                
                vectors.append({
                    "id": chunk_id,
                    "values": embedding,
                    "metadata": {
                        "chunk_text": chunk,
                        "document_url": document_url,
                        "chunk_index": i
                    }
                })
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
            
            logger.info(f"Stored {len(vectors)} embeddings in Pinecone")
            return chunk_ids
            
        except Exception as e:
            logger.error(f"Error storing embeddings: {str(e)}")
            raise
    
    def search_similar(self, query_embedding: List[float], top_k: int = None) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        try:
            top_k = top_k or settings.top_k
            
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            retrieved_chunks = []
            for match in results.matches:
                retrieved_chunks.append({
                    "text": match.metadata["chunk_text"],
                    "score": float(match.score),
                    "document_url": match.metadata["document_url"],
                    "chunk_index": match.metadata["chunk_index"]
                })
            
            logger.info(f"Retrieved {len(retrieved_chunks)} similar chunks")
            return retrieved_chunks
            
        except Exception as e:
            logger.error(f"Error searching vectors: {str(e)}")
            raise