# LLM-Powered Intelligent Query-Retrieval System Prototype (HackRx 6.0)

This project is a prototype for the Bajaj Finserv Health HackRx 6.0 competition, focusing on designing an LLM-Powered Intelligent Query-Retrieval System. The system aims to process large documents (PDFs, DOCX, emails) and make contextual decisions based on natural language queries.

## Project Components & Current Implementation

### 1. Input Documents
**Requirement:** Process PDFs, DOCX, and email documents.
**Current Implementation:**
- **`document_processor.py`**: Contains a function `extract_text_from_pdf` that uses `PyPDF2` to extract text content from PDF files. This is the initial step for handling input documents.
- **Future Work:** Extend `document_processor.py` to handle DOCX and email formats.

### 2. LLM Parser (Simulated)
**Requirement:** Extract structured query.
**Current Implementation:**
- **`main.py`**: The `evaluate_logic` function acts as a simulated LLM parser. It uses simple keyword matching between the user's question and the retrieved document clause to formulate a more direct answer. This is a placeholder for a real LLM (like GPT-4) that would perform advanced natural language understanding and query structuring.

### 3. Embedding Search (Simulated In-Memory)
**Requirement:** Use embeddings (FAISS/Pinecone) for semantic search.
**Current Implementation:**
- **`embedding_search.py`**: Implements an `EmbeddingSearch` class that uses `TfidfVectorizer` from `scikit-learn` to convert document chunks and queries into numerical vectors. `cosine_similarity` is then used to find the most semantically similar document chunks (clauses) to a given query. This serves as an in-memory simulation of a vector database like FAISS or Pinecone.

### 4. Clause Matching
**Requirement:** Semantic similarity.
**Current Implementation:**
- Handled by the `EmbeddingSearch` class in `embedding_search.py` through `cosine_similarity` between query embeddings and document chunk embeddings.

### 5. Logic Evaluation
**Requirement:** Decision processing.
**Current Implementation:**
- **`main.py`**: The `evaluate_logic` function performs a basic form of decision processing by applying simple `if-elif` conditions based on keywords in the question and the retrieved clause. This simulates how an LLM might make a decision or extract specific information.

### 6. JSON Output
**Requirement:** Structured JSON responses.
**Current Implementation:**
- **`main.py`**: The FastAPI endpoint `/hackrx/run` is configured to return responses in a structured JSON format, adhering to the `AnswerResponse` Pydantic model.

## System Architecture & Workflow

1.  **Input Documents:** A PDF file path is provided in the request.
2.  **Document Processing:** `document_processor.py` extracts raw text from the PDF.
3.  **Embedding Indexing:** The extracted text is chunked (currently by sentence) and indexed by `embedding_search.py` using TF-IDF vectorization.
4.  **Query Reception:** Natural language questions are received via the API.
5.  **Semantic Search:** For each question, `embedding_search.py` performs a semantic search against the indexed document chunks to retrieve the most relevant clause.
6.  **Logic Evaluation:** The `evaluate_logic` function in `main.py` takes the question and the retrieved clause to formulate a more direct and contextually relevant answer (simulated decision-making).
7.  **JSON Output:** The final answers are returned in a structured JSON response.

## How to Run and Test

1.  **Navigate to the project directory:**
    ```bash
    cd llm_query_system
    ```
2.  **Activate the virtual environment:**
    ```bash
    source venv/bin/activate
    ```
3.  **Install dependencies (if not already installed):**
    ```bash
    pip install fastapi uvicorn PyPDF2 scikit-learn numpy
    ```
4.  **Create a dummy PDF for testing (if you don't have one):**
    ```bash
    python3 -c "from reportlab.pdfgen import canvas; c = canvas.Canvas('sample_policy.pdf'); c.drawString(100, 750, 'This is a sample policy document.'); c.drawString(100, 730, 'It covers basic health insurance terms.'); c.drawString(100, 710, 'The grace period for premium payment is 30 days.'); c.save()"
    ```
5.  **Run the FastAPI application (for API testing):**
    ```bash
    uvicorn main:app --reload
    ```
    (Access the API documentation at `http://127.0.0.1:8000/docs`)

6.  **Run the direct test script (to get results in `output/test_results.json`):**
    ```bash
    python3 run_test.py
    ```
    This will process the `Arogya Sanjeevani Policy - CIN - U10200WB1906GOI001713 1.pdf` document and save the answers to `output/test_results.json`.

## Output

Test results are saved in `llm_query_system/output/test_results.json`.

## Future Enhancements

-   **Integration with Real LLMs:** Replace the simulated LLM parser and logic evaluation with actual API calls to models like GPT-4.
-   **Advanced Document Parsing:** Implement robust parsing for DOCX and email formats, handling complex layouts and tables.
-   **Production-Ready Vector Store:** Integrate with external vector databases like Pinecone or FAISS for scalable semantic search.
-   **Improved Chunking Strategy:** Implement more intelligent document chunking techniques (e.g., based on headings, paragraphs, or LLM-aware chunking).
-   **Error Handling and Logging:** Enhance error handling and add comprehensive logging.
-   **Authentication:** Implement proper authentication for API endpoints.
-   **Explainability Refinement:** Develop more sophisticated methods for generating explainable decision rationales, potentially highlighting exact text spans from the document.
