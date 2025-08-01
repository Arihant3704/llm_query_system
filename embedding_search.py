from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class EmbeddingSearch:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.document_embeddings = None
        self.document_chunks = []

    def index_document(self, document_text: str):
        # For simplicity, we'll split the document into sentences or paragraphs
        # In a real system, more sophisticated chunking would be used
        self.document_chunks = [chunk.strip() for chunk in document_text.split('\n\n') if chunk.strip()]
        if not self.document_chunks:
            return
        self.document_embeddings = self.vectorizer.fit_transform(self.document_chunks)

    def search(self, query: str, top_k: int = 3) -> list[str]:
        if self.document_embeddings is None:
            return []

        query_embedding = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_embedding, self.document_embeddings).flatten()

        # Get top_k most similar chunks
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for i in top_indices:
            if similarities[i] > 0: # Only return chunks with positive similarity
                results.append(self.document_chunks[i])
        return results
