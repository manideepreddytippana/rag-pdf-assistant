class Retriever:
    
    def __init__(self,collection, embedding_service):
        self.collection = collection
        self.embedding_service = embedding_service

    def query(self,query: str, top_k: int = 5):

        query_embedding = self.embedding_service.embed_query(query)
        chroma_results = self.collection.query(
            query_embeddings = query_embedding,
            n_results=top_k
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

        return results
            