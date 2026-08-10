from sentence_transformers import SentenceTransformer
from config import settings

class EmbeddingService:
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.embedding_model
        self.model = SentenceTransformer(self.model_name)

    def embed_documents(self, chunks: list[dict]):

        texts = [chunk['text'] for chunk in chunks]
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, query: str):

        prefixed = f"Represent this sentence for searching relevant passages: {query}"
        return self.model.encode([prefixed], normalize_embeddings=True).tolist()
