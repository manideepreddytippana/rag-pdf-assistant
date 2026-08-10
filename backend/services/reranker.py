import math
from sentence_transformers import CrossEncoder
from config import settings

def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))

class RerankerService:

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.reranker_model
        self.model = CrossEncoder(self.model_name)

    def rerank(self, query: str, results: list[dict], top_k: int = None, threshold: float = None) -> list[dict]:
     
        if not results:
            return []

        target_top_k = top_k if top_k is not None else settings.top_k
        target_threshold = threshold if threshold is not None else settings.reranker_threshold

        pairs = [(query, doc['text']) for doc in results]
        scores = self.model.predict(pairs)

        reranked_results = []
        for idx, result in enumerate(results):
            prob_score = sigmoid(float(scores[idx]))
            result['rerank_score'] = prob_score

            if prob_score > target_threshold:
                reranked_results.append(result)

        reranked_results = sorted(
            reranked_results,
            key=lambda x: x['rerank_score'],
            reverse=True
        )

        return reranked_results[:target_top_k]
