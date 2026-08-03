from sentence_transformers import CrossEncoder

class RerankerService:

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def reranker(self, query : str, results, top_k : int = 5):

        if not results:
            return []

        pairs = [(query, doc['text']) for doc in results]

        scores = self.model.predict(pairs)

        for idx, result in enumerate(results):

            result['rerank_score'] = float(scores[idx])

        reranked_results = sorted(
            results,
            key = lambda x: x['rerank_score'],
            reverse = True
        )

        return reranked_results[:top_k]

            

        
