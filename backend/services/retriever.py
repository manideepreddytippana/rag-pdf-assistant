from config import settings

class Retriever:
    
    def __init__(self, collection, embedding_service, reranker_service = None):
        self.collection = collection
        self.embedding_service = embedding_service
        self.reranker_service = reranker_service

    def query(
        self,
        query: str,
        top_k: int = None,
        initial_top_k: int = None,
        embedding_threshold: float = None
    ) -> list[dict]:
       
        target_top_k = top_k if top_k is not None else settings.top_k
        target_initial_top_k = initial_top_k if initial_top_k is not None else settings.initial_top_k
        target_embedding_threshold = (
            embedding_threshold if embedding_threshold is not None else settings.embedding_threshold
        )

        query_embedding = self.embedding_service.embed_query(query)
        fetch_k = target_initial_top_k if self.reranker_service else target_top_k
        
        chroma_results = self.collection.query(
            query_embeddings = query_embedding,
            n_results=fetch_k
        )

        results = []

        if chroma_results['ids'] and len(chroma_results['ids']) > 0:

            ids = chroma_results['ids'][0]
            documents = chroma_results['documents'][0]
            metadatas = chroma_results['metadatas'][0]
            distances = chroma_results['distances'][0]

            for i in range(len(ids)):
                similarity = 1 - float(distances[i])
                if similarity >= target_embedding_threshold:
                    results.append({
                        "chunk_id": metadatas[i]["chunk_id"],
                        "source": metadatas[i]["source"],
                        "page_no": metadatas[i]["page_no"],
                        "text": documents[i],
                        "score": similarity
                    })

        if self.reranker_service and results:
            results = self.reranker_service.rerank(query, results, top_k=target_top_k)

        return results[:target_top_k]