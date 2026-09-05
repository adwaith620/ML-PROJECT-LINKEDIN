"""
sentence_bert.py

Implementation of Phase 5 semantic matching using Sentence-BERT.
Calculates semantic similarity between processed resume text and job description text.
Handles chunking of long documents to respect model token limits.
"""

import numpy as np
import logging

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False
    logging.warning("sentence-transformers or scikit-learn is not installed.")

class SemanticMatcher:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the Sentence-BERT matcher.
        'all-MiniLM-L6-v2' is chosen for its excellent balance of speed, 
        small memory footprint, and robust performance on semantic similarity.
        """
        self.model_name = model_name
        self.model = None
        
        if ST_AVAILABLE:
            self.model = SentenceTransformer(self.model_name)
            self.max_seq_length = self.model.max_seq_length
        else:
            self.max_seq_length = 256

    def chunk_text(self, text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
        """
        Splits a long text string into overlapping word chunks.
        Chunking by words is a fast heuristic proxy for token length.
        """
        if not text:
            return []
            
        words = text.split()
        if len(words) <= chunk_size:
            return [text]
            
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            # Break if we've consumed the end of the text
            if i + chunk_size >= len(words):
                break
                
        return chunks

    def embed_document(self, text: str) -> np.ndarray:
        """
        Generates a document-level embedding.
        If the document is long, it splits it into chunks, embeds each chunk, 
        and performs mean pooling over the chunk embeddings.
        """
        if not text.strip() or not self.model:
            return np.zeros((1, 384)) # Default for MiniLM
            
        chunks = self.chunk_text(text)
        
        # sentence-transformers encodes lists of strings efficiently
        chunk_embeddings = self.model.encode(chunks, convert_to_numpy=True)
        
        # Mean pooling across chunks to get a single document vector
        if len(chunks) == 1:
            doc_embedding = chunk_embeddings
        else:
            doc_embedding = np.mean(chunk_embeddings, axis=0, keepdims=True)
            
        return doc_embedding

    def compute_similarity(self, resume_text: str, job_text: str) -> float:
        """
        Computes cosine similarity between a resume and a job description.
        Returns a continuous score between -1 and 1.
        """
        if not resume_text.strip() or not job_text.strip() or not self.model:
            return 0.0
            
        resume_vec = self.embed_document(resume_text)
        job_vec = self.embed_document(job_text)
        
        # Scikit-learn cosine_similarity expects 2D arrays
        # If shape is (384,), reshape it. embed_document returns (1, 384)
        if resume_vec.ndim == 1:
            resume_vec = resume_vec.reshape(1, -1)
        if job_vec.ndim == 1:
            job_vec = job_vec.reshape(1, -1)
            
        similarity = cosine_similarity(resume_vec, job_vec)[0][0]
        return float(similarity)

    def classify_fit(self, similarity_score: float, threshold_potential: float = 0.45, threshold_good: float = 0.65) -> str:
        """
        Maps a continuous similarity score to the project's categorical fit classes.
        Note: Thresholds should be derived empirically from the validation set!
        These defaults are arbitrary placeholders.
        """
        if similarity_score >= threshold_good:
            return "Good Fit"
        elif similarity_score >= threshold_potential:
            return "Potential Fit"
        else:
            return "No Fit"
