import requests
import tempfile
import os
import asyncio
import threading
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
    
    def parse_pdf_from_url(self, pdf_url: str) -> str:
        """Download PDF from URL and parse it using LlamaParse in a separate thread."""
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
                # Parse PDF in a separate thread to avoid event loop issues
                logger.info("Parsing PDF with LlamaParse...")
                result = self._parse_in_thread(temp_path)
                
                logger.info(f"Successfully parsed PDF. Total length: {len(result)} characters")
                return result
                
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"Error parsing PDF: {str(e)}")
            raise Exception(f"Failed to parse PDF: {str(e)}")
    
    def _parse_in_thread(self, temp_path: str) -> str:
        """Run LlamaParse in a separate thread with its own event loop."""
        result = [None]  # Use list to store result
        
        def parse_pdf():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                documents = self.parser.load_data(temp_path)
                parsed_text = "\n\n".join([doc.text for doc in documents])
                result[0] = parsed_text
            except Exception as e:
                result[0] = f"Error: {str(e)}"
            finally:
                loop.close()
        
        # Run in thread
        thread = threading.Thread(target=parse_pdf)
        thread.start()
        thread.join()
        
        if result[0] and result[0].startswith("Error:"):
            raise Exception(result[0])
        
        return result[0]