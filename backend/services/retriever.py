class Retriever:
    
    def __init__(self,collection, embedding_service, reranker_service = None):
        self.collection = collection
        self.embedding_service = embedding_service
        self.reranker_service = reranker_service

    def query(self, query: str, top_k: int = 5, initial_top_k : int = 20):

        query_embedding = self.embedding_service.embed_query(query)

        fetch_k = initial_top_k if self.reranker_service else top_k
        
        chroma_results = self.collection.query(
            query_embeddings = query_embedding,
            n_results=fetch_k
        )

        results = []

        if chroma_results['ids'] and len(chroma_results['ids'])> 0:

            ids = chroma_results['ids'][0]
            documents = chroma_results['documents'][0]
            metadatas = chroma_results['metadatas'][0]
            distances = chroma_results['distances'][0]

            for i in range(len(ids)):
                
                results.append({
                    "chunk_id": metadatas[i]["chunk_id"],
                    "source": metadatas[i]["source"],
                    "page_no": metadatas[i]["page_no"],
                    "text": documents[i],
                    "score": float(distances[i])
                })

        if self.reranker_service and results:
            results = self.reranker_service.reranker(query, results, top_k = top_k)

        return results[:top_k]
            