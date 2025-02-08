from pydantic import BaseModel
from typing import Optional

class DocumentMetadata(BaseModel):
    id: str
    filename: str

class DocumentResponse(BaseModel):
    metadata: DocumentMetadata
    content: str
    customized_content: Optional[str] = None
    github_info: Optional[str] = None
    personal_writeup: Optional[str] = None

class CustomizationRequest(BaseModel):
    document_id: str
    job_description: str
    github_info: Optional[str] = None
    personal_writeup: Optional[str] = None
