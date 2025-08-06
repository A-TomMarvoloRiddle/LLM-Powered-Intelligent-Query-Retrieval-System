import requests
import tempfile
import os
from llama_parse import LlamaParse
from typing import List
from app.config.settings import settings
from app.utils.logger import logger

class PDFParser:
    def __init__(self):
        self.parser = LlamaParse(
            api_key=settings.llama_parse_api_key,
            result_type="markdown",
            verbose=True
        )
    
    async def parse_pdf_from_url(self, pdf_url: str) -> str:
        """Download PDF from URL and parse it using LlamaParse."""
        try:
            logger.info(f"Downloading PDF from URL: {pdf_url}")
            
            # Download PDF
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            try:
                # Parse PDF
                logger.info("Parsing PDF with LlamaParse...")
                documents = self.parser.load_data(temp_path)
                
                # Combine all text
                parsed_text = "\n\n".join([doc.text for doc in documents])
                logger.info(f"Successfully parsed PDF. Total length: {len(parsed_text)} characters")
                
                return parsed_text
                
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            raise Exception(f"Failed to parse PDF: {str(e)}")