"""
Embedding and similarity vectorizer for RAG knowledge base.
Uses scikit-learn TF-IDF + Cosine similarity for deterministic, zero-latency local retrieval.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Tuple
import numpy as np

class DocumentIndex:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        self.documents: List[Dict[str, Any]] = []
        self.tfidf_matrix = None

    def build_index(self, docs: List[Dict[str, Any]]):
        self.documents = docs
        corpus = [f"{d['title']} {d['symptoms']} {d['root_cause']} {d['content']}" for d in docs]
        if corpus:
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.documents or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []

        for idx in top_indices:
            score = float(similarities[idx])
            doc = self.documents[idx].copy()
            doc["similarity_score"] = round(score, 4)
            doc["confidence_percentage"] = f"{round(score * 100, 1)}%"
            results.append(doc)

        return results
