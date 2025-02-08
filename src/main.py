import logfire
logfire.configure(console=logfire.ConsoleOptions(min_log_level='debug'))
logfire.instrument_pydantic()

from fastapi import FastAPI, UploadFile, Request, HTTPException, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .services.document import document_processor
from .services.anthropic import anthropic_service
from .models.document import DocumentResponse, DocumentMetadata, CustomizationRequest

app = FastAPI()
logfire.instrument_fastapi(app)
templates = Jinja2Templates(directory="src/templates")

# Serve static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Get the raw request body
    try:
        raw_body = await request.body()
        raw_body_str = raw_body.decode() if raw_body else None
        logfire.error("Validation error on {method} {url}", 
                     method=request.method,
                     url=str(request.url),
                     raw_body=raw_body_str,
                     headers=dict(request.headers))
        
        # Log each validation error separately
        for error in exc.errors():
            logfire.error("Validation error: {msg} at {loc} ({type})",
                         msg=error.get("msg", ""),
                         loc=".".join(str(x) for x in error.get("loc", [])),
                         type=error.get("type", ""))
    except Exception as e:
        logfire.error("Failed to read request body: {error}", 
                     error=str(e),
                     exc_info=True)
    
    # If this is an HTMX request, return an error message as HTML
    if "HX-Request" in request.headers:
        return HTMLResponse(
            """<div class="bg-red-50 border-l-4 border-red-400 p-4">
                   <div class="flex">
                       <div class="ml-3">
                           <p class="text-sm text-red-700">
                               Failed to upload file. Please try again.
                           </p>
                       </div>
                   </div>
               </div>""",
            status_code=422
        )
    
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_document(
    request: Request,
    resume_file: UploadFile = File(...),
    job_description_file: UploadFile = File(...),
    github_file: Optional[UploadFile] = File(None),
    personal_file: Optional[UploadFile] = File(None)
):
    with logfire.span("Processing file upload and customization"):
        if not resume_file or not resume_file.filename:
            logfire.error("No resume file provided in upload request")
            raise HTTPException(status_code=400, detail="No resume file provided")
        
        logfire.debug("Received file upload request", 
                     filename=resume_file.filename,
                     content_type=resume_file.content_type)
        
        if not resume_file.filename.lower().endswith('.md'):
            logfire.warning("Invalid resume file type: {filename}", 
                          filename=resume_file.filename)
            raise HTTPException(status_code=400, detail="Only markdown (.md) files are supported for resumes")
        
        try:
            # Read all files
            resume_content = await resume_file.read()
            job_description_content = await job_description_file.read() if job_description_file else None
            github_content = await github_file.read() if github_file else None
            personal_content = await personal_file.read() if personal_file else None
            
            logfire.debug("Read all file contents", 
                         resume_length=len(resume_content),
                         job_desc_length=len(job_description_content) if job_description_content else 0)
            
            with logfire.span("Processing document"):
                doc_id = document_processor.process_document(resume_content, resume_file.filename)
                logfire.debug("Document processed with ID: {doc_id}", doc_id=doc_id)
                
                doc = document_processor.get_document(doc_id)
                if not doc:
                    logfire.error("Document {doc_id} not found after processing", 
                                doc_id=doc_id)
                    raise HTTPException(status_code=500, detail="Error storing document")
                
                # Customize the resume if job description is provided
                customized_content = None
                if job_description_content:
                    logfire.debug("Customizing resume with job description")
                    customized_content = anthropic_service.customize_resume(
                        doc["content"],
                        job_description_content.decode(),
                        github_content.decode() if github_content else "",
                        personal_content.decode() if personal_content else ""
                    )
                
                # If this is an HTMX request, return the results as HTML
                if "HX-Request" in request.headers:
                    if customized_content:
                        return HTMLResponse(f"""
                            <div class="mb-8 p-6 bg-white rounded-lg shadow-md">
                                <h2 class="text-xl font-semibold mb-4">Original Resume</h2>
                                <div class="prose prose-sm sm:prose lg:prose-lg xl:prose-xl mx-auto">
                                    <pre><code class="whitespace-pre-wrap">{doc["content"]}</code></pre>
                                </div>
                            </div>
                            <div class="mb-8 p-6 bg-white rounded-lg shadow-md">
                                <h2 class="text-xl font-semibold mb-4">Customized Resume</h2>
                                <div class="prose prose-sm sm:prose lg:prose-lg xl:prose-xl mx-auto">
                                    <pre><code class="whitespace-pre-wrap">{customized_content}</code></pre>
                                </div>
                            </div>
                            """)
                    else:
                        return HTMLResponse(f"""
                            <div class="mb-8 p-6 bg-white rounded-lg shadow-md">
                                <h2 class="text-xl font-semibold mb-4">Resume Content</h2>
                                <div class="prose prose-sm sm:prose lg:prose-lg xl:prose-xl mx-auto">
                                    <pre><code class="whitespace-pre-wrap">{doc["content"]}</code></pre>
                                </div>
                            </div>
                            """)
                
                # Otherwise return JSON response
                response = DocumentResponse(
                    metadata=DocumentMetadata(
                        id=doc["id"],
                        filename=doc["filename"]
                    ),
                    content=doc["content"],
                    customized_content=customized_content
                )
                logfire.debug("Created response for document {doc_id}", 
                            doc_id=doc_id,
                            filename=doc["filename"])
                return response
        except Exception as e:
            logfire.error("Failed to process document: {error}",
                         error=str(e),
                         error_type=type(e).__name__,
                         exc_info=True)
            if "HX-Request" in request.headers:
                return HTMLResponse(
                    """<div class="bg-red-50 border-l-4 border-red-400 p-4">
                           <div class="flex">
                               <div class="ml-3">
                                   <p class="text-sm text-red-700">
                                       Failed to process document. Please try again.
                                   </p>
                               </div>
                           </div>
                       </div>""",
                    status_code=500
                )
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/customize", response_model=DocumentResponse)
async def customize_resume(request: CustomizationRequest):
    with logfire.span("Customizing resume"):
        try:
            doc = document_processor.get_document(request.document_id)
            if not doc:
                logfire.error("Document {doc_id} not found", 
                            doc_id=request.document_id)
                raise HTTPException(status_code=404, detail="Document not found")
            
            logfire.debug("Customizing document {doc_id}", 
                         doc_id=request.document_id)
            
            customized_content = anthropic_service.customize_resume(
                doc["content"],
                request.job_description,
                request.github_info,
                request.personal_writeup
            )
            
            return DocumentResponse(
                metadata=DocumentMetadata(
                    id=doc["id"],
                    filename=doc["filename"]
                ),
                content=doc["content"],
                customized_content=customized_content
            )
        except Exception as e:
            logfire.error("Failed to customize resume: {error}",
                         error=str(e),
                         error_type=type(e).__name__,
                         exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))