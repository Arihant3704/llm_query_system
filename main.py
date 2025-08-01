from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Dict, Any
import os
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

    document_path = request.documents
    extracted_text = ""

    if not os.path.exists(document_path):
        raise HTTPException(status_code=404, detail=f"Document not found at {document_path}")

    if document_path.lower().endswith('.pdf'):
        extracted_text = extract_text_from_pdf(document_path)
    elif document_path.lower().endswith('.docx'):
        extracted_text = extract_text_from_docx(document_path)
    elif document_path.lower().endswith('.eml'):
        extracted_text = extract_text_from_eml(document_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported document type. Only PDF, DOCX, and EML are supported.")

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