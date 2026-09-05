import unittest
import sys
import os
import numpy as np

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.matching.sentence_bert import SemanticMatcher

class DummyModel:
    """A dummy model that returns random embeddings for testing without downloading actual weights."""
    def __init__(self):
        self.max_seq_length = 256
        
    def encode(self, sentences, convert_to_numpy=True):
        # Return a deterministic "random" array based on length for consistency
        embeddings = []
        for s in sentences:
            np.random.seed(len(s))
            embeddings.append(np.random.rand(384))
        return np.array(embeddings)

class TestSentenceBert(unittest.TestCase):
    def setUp(self):
        self.matcher = SemanticMatcher()
        # Inject the dummy model to prevent downloads during tests
        self.matcher.model = DummyModel()

    def test_chunk_text(self):
        text = "This is a simple test document meant to be chunked into pieces."
        chunks = self.matcher.chunk_text(text, chunk_size=5, overlap=2)
        # "This is a simple test" (5)
        # "simple test document meant to" (5)
        # "meant to be chunked into" (5)
        # "chunked into pieces." (3)
        self.assertTrue(len(chunks) > 1)
        self.assertEqual(chunks[0], "This is a simple test")
        
    def test_empty_text_handling(self):
        chunks = self.matcher.chunk_text("")
        self.assertEqual(chunks, [])
        
        sim = self.matcher.compute_similarity("", "Job desc")
        self.assertEqual(sim, 0.0)

    def test_embedding_dimensions(self):
        text = "A short resume"
        embedding = self.matcher.embed_document(text)
        self.assertEqual(embedding.shape, (1, 384))
        
    def test_cosine_similarity(self):
        resume = "I am a software engineer."
        job = "Looking for a software engineer."
        sim = self.matcher.compute_similarity(resume, job)
        self.assertTrue(-1.0 <= sim <= 1.0)
        
    def test_threshold_classification(self):
        self.assertEqual(self.matcher.classify_fit(0.7, 0.45, 0.65), "Good Fit")
        self.assertEqual(self.matcher.classify_fit(0.5, 0.45, 0.65), "Potential Fit")
        self.assertEqual(self.matcher.classify_fit(0.2, 0.45, 0.65), "No Fit")

if __name__ == '__main__':
    unittest.main()
