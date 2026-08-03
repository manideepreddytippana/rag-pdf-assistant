from sentence_transformers import CrossEncoder
import math

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

class RerankerService:

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def reranker(self, query : str, results, top_k : int = 5, threshold: float = 0.65):

        if not results:
            return []

        pairs = [(query, doc['text']) for doc in results]

        scores = self.model.predict(pairs)

        reranked_results = []
        for idx, result in enumerate(results):
            
            prob_score = sigmoid(float(scores[idx]))
            result['rerank_score'] = prob_score

            if prob_score > threshold:
                reranked_results.append(result)

        reranked_results = sorted(
            reranked_results,
            key = lambda x: x['rerank_score'],
            reverse = True
        )

        return reranked_results[:top_k]

            

        
