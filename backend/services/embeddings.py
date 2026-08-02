import os
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    
    def __init__(self, model_name = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, chunks):
        texts = [chunk['text'] for chunk in chunks]
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self,query: str):
        return self.model.encode([query], normalize_embeddings = True).tolist()
