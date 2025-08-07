from typing import List, Dict, Any
from groq import Groq
from app.config.settings import settings
from app.utils.logger import logger

class LLMService:
    def __init__(self):
        if not settings.groq_api_key:
            raise ValueError("No Groq API key found")
        self.groq_client = Groq(api_key=settings.groq_api_key)

    def generate_answer(self, question: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Generate answer based on question and context."""
        try:
            # Prepare context
            context = "\n\n".join([chunk["text"] for chunk in context_chunks])
            
            # Create prompt
            prompt = f"""Based on the following context from a policy document, answer the question accurately and concisely. 
Only use information that is explicitly stated in the context. If the answer cannot be found in the context, state that clearly.

Context:
{context}

Question: {question}

Answer:"""
            
            # Generate response using Groq
            response = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context from policy documents. Always ground your answers in the provided context."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            answer = response.choices[0].message.content.strip()
            
            logger.info(f"Generated answer for question: {question[:50]}...")
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise Exception(f"Failed to generate answer: {str(e)}")