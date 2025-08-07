from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import httpx
import tempfile
import google.generativeai as genai
from dotenv import load_dotenv
import logging

from .document_processor import extract_text_from_pdf, extract_text_from_docx, extract_text_from_eml
from .embedding_search import EmbeddingSearch

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="LLM-Powered Intelligent Query-Retrieval System Prototype",
    description="Prototype for HackRx 6.0 problem statement.",
    version="0.1.0"
)

# API Key Authentication
API_KEY = os.environ.get("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

# Configure Gemini API
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=gemini_api_key)

# Initialize EmbeddingSearch globally (or per request, depending on scale)
embedding_search_instance = EmbeddingSearch()

class DocumentRequest(BaseModel):
    documents: str # Assuming this will be a local file path for now
    questions: List[str]

class AnswerResponse(BaseModel):
    answers: List[str]

@app.post("/hackrx/run", response_model=AnswerResponse, dependencies=[Depends(get_api_key)])
async def run_submission(request: DocumentRequest):
    logging.info(f"Received request for document: {request.documents}")
    logging.info(f"Questions: {request.questions}")

    document_source = request.documents
    extracted_text = ""
    temp_file_path = None

    try:
        if document_source.startswith("http://") or document_source.startswith("https://"):
            logging.info(f"Attempting to download document from URL: {document_source}")
            async with httpx.AsyncClient() as client:
                response = await client.get(document_source, follow_redirects=True, timeout=30.0)
                response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

            # Determine file extension from URL or content type
            file_extension = ""
            if 'content-disposition' in response.headers:
                cd = response.headers['content-disposition']
                fname = cd.split('filename=')[-1].strip("'")
                file_extension = os.path.splitext(fname)[1]
            elif 'content-type' in response.headers:
                content_type = response.headers['content-type']
                if 'pdf' in content_type:
                    file_extension = ".pdf"
                elif 'word' in content_type or 'document' in content_type:
                    file_extension = ".docx"
                elif 'message/rfc822' in content_type:
                    file_extension = ".eml"
            
            if not file_extension:
                # Fallback to checking the URL path itself for an extension
                file_extension = os.path.splitext(document_source.split('?')[0])[1]

            if not file_extension:
                raise HTTPException(status_code=400, detail="Could not determine file type from URL or headers.")

            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            logging.info(f"Document downloaded to temporary file: {temp_file_path}")
            document_path_to_process = temp_file_path
        else:
            document_path_to_process = document_source
            if not os.path.exists(document_path_to_process):
                raise HTTPException(status_code=404, detail=f"Document not found at {document_path_to_process}")

        if document_path_to_process.lower().endswith('.pdf'):
            extracted_text = extract_text_from_pdf(document_path_to_process)
        elif document_path_to_process.lower().endswith('.docx'):
            extracted_text = extract_text_from_docx(document_path_to_process)
        elif document_path_to_process.lower().endswith('.eml'):
            extracted_text = extract_text_from_eml(document_path_to_process)
        else:
            raise HTTPException(status_code=400, detail="Unsupported document type. Only PDF, DOCX, and EML are supported.")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logging.info(f"Cleaned up temporary file: {temp_file_path}")

    if not extracted_text:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from {document_path}")

    logging.info(f"Extracted text (first 500 chars):\n{extracted_text[:500]}...")

    # Index the document for semantic search
    embedding_search_instance.index_document(extracted_text)

    answers = []
    for q in request.questions:
        # Perform semantic search for relevant clauses
        relevant_clauses = embedding_search_instance.search(q, top_k=1) # Get top 1 most relevant clause
        
        if relevant_clauses:
            context = relevant_clauses[0]
            
            # Construct prompt for LLM
            prompt = f"""
            You are an intelligent query-retrieval system. 
            Based on the following document excerpt, answer the question. 
            If the document excerpt does not contain enough information to answer the question, state that.

            Document Excerpt:
            {context}

            Question:
            {q}

            Provide a concise answer.
            """
            
            try:
                # Make API call to Gemini using the correct model name
                model = genai.GenerativeModel('models/gemini-1.5-flash-latest') 
                response = model.generate_content(prompt)
                llm_answer = response.text.strip()
                answers.append(llm_answer)
            except Exception as e:
                logging.error(f"Error processing question with LLM: {e}")
                answers.append(f"Error processing question with LLM: {e}")
        else:
            answers.append(f"No relevant clause found for: {q}")

    return {"answers": answers}

@app.get("/")
async def read_root():
    return {"message": "LLM-Powered Intelligent Query-Retrieval System Prototype is running!"}