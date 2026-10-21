"""
sentence_bert.py

Implementation of Phase 5 semantic matching using Sentence-BERT.
Calculates semantic similarity between processed resume text and job description text.
Handles chunking of long documents to respect model token limits.
Supports lazy loading and graceful degradation if offline.
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False
    logger.warning("sentence-transformers or scikit-learn is not installed.")


class SemanticMatcher:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', lazy: bool = True):
        """
        Initializes the Sentence-BERT matcher.
        'all-MiniLM-L6-v2' is chosen for its excellent balance of speed, 
        small memory footprint, and robust performance on semantic similarity.
        By default, lazy=True defers model weight loading until first inference.
        """
        self.model_name = model_name
        self.model = None
        self.max_seq_length = 256
        self._load_error = None

        if not lazy and ST_AVAILABLE:
            self.load_model()

    def load_model(self) -> bool:
        """Loads the SentenceTransformer model if not already loaded."""
        if self.model is not None:
            return True

        if not ST_AVAILABLE:
            self._load_error = "sentence-transformers library is not installed."
            return False

        try:
            self.model = SentenceTransformer(self.model_name)
            self.max_seq_length = getattr(self.model, "max_seq_length", 256)
            self._load_error = None
            return True
        except Exception as e:
            self.model = None
            self._load_error = str(e)
            logger.warning(f"Failed to load SentenceTransformer ({self.model_name}): {e}")
            return False

    def is_ready(self) -> bool:
        """Returns True if the underlying model is ready for inference."""
        return self.model is not None

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
        if not text.strip():
            return np.zeros((1, 384))

        if self.model is None:
            # Attempt lazy load
            self.load_model()
            if self.model is None:
                return np.zeros((1, 384))
            
        chunks = self.chunk_text(text)
        if not chunks:
            return np.zeros((1, 384))
        
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
        if not resume_text.strip() or not job_text.strip():
            return 0.0

        if self.model is None:
            self.load_model()
            if self.model is None:
                return 0.0
            
        resume_vec = self.embed_document(resume_text)
        job_vec = self.embed_document(job_text)
        
        # Scikit-learn cosine_similarity expects 2D arrays
        if resume_vec.ndim == 1:
            resume_vec = resume_vec.reshape(1, -1)
        if job_vec.ndim == 1:
            job_vec = job_vec.reshape(1, -1)
            
        similarity = cosine_similarity(resume_vec, job_vec)[0][0]
        return float(similarity)

    def classify_fit(self, similarity_score: float, threshold_potential: float = 0.45, threshold_good: float = 0.65) -> str:
        """
        Maps a continuous similarity score to the project's categorical fit classes.
        """
        if similarity_score >= threshold_good:
            return "Good Fit"
        elif similarity_score >= threshold_potential:
            return "Potential Fit"
        else:
            return "No Fit"
