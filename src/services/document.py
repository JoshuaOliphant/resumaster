import uuid
from typing import Dict
import logfire

class DocumentProcessor:
    def __init__(self):
        self.documents: Dict[str, dict] = {}
        logfire.debug("DocumentProcessor initialized")

    def process_document(self, content: bytes, filename: str) -> str:
        """Process an uploaded markdown document and return document ID"""
        with logfire.span("process_document") as span:
            try:
                logfire.debug("Processing document", 
                            filename=filename,
                            content_length=len(content))
                
                doc_id = str(uuid.uuid4())
                logfire.debug("Generated document ID", doc_id=doc_id)
                
                try:
                    decoded_content = content.decode('utf-8')
                    logfire.debug("Content decoded successfully", 
                                content_length=len(decoded_content))
                except UnicodeDecodeError as e:
                    logfire.error("Failed to decode content",
                                error=str(e),
                                content_length=len(content))
                    raise
                
                # Store the document
                document = {
                    "id": doc_id,
                    "filename": filename,
                    "content": decoded_content
                }
                self.documents[doc_id] = document
                logfire.debug("Document stored", 
                            doc_id=doc_id,
                            document=document)
                
                return doc_id
            except Exception as e:
                logfire.error("Error processing document", 
                            error=str(e),
                            error_type=type(e).__name__,
                            filename=filename,
                            exc_info=True)
                raise

    def get_document(self, doc_id: str) -> dict:
        """Retrieve a document by ID"""
        with logfire.span("get_document") as span:
            doc = self.documents.get(doc_id)
            if doc:
                logfire.debug("Document retrieved", 
                            doc_id=doc_id,
                            filename=doc.get("filename"))
            else:
                logfire.warning("Document not found", doc_id=doc_id)
            return doc

document_processor = DocumentProcessor()
