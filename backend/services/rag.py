import logging
import time

from services.prompts_retriever import get_prompt
from services.query_resolver import QueryResolver
from config import settings

logger = logging.getLogger("rag_pipeline")

system_prompt = get_prompt("system_prompt.txt")

class RagService:

    def __init__(self, retriever, llmservice, memory, query_resolver: QueryResolver = None):
    
        self.retriever = retriever
        self.llmservice = llmservice
        self.memory = memory
        self.query_resolver = query_resolver or QueryResolver(llmservice)

    def build_context(self, results: list[dict]):

        context_parts = []

        for result in results:

            context_parts.append(
                f"""
                'SOURCE': {result['source']},
                'PAGE_NO': {result['page_no']},
                'CONTENT': {result['text']}
                """.strip()
            )

        return "\n---\n".join(context_parts)

    def build_prompt(self, query: str, context: str, history: str = ""):

        return f"""<conversation_history>
{history}
</conversation_history>

<retrieved_context>
{context}
</retrieved_context>

<question>
{query}
</question>

Provide a precise answer based solely on the retrieved context above.""".strip()

    def get_answer(self, query: str, session_id: str = "session_id", top_k: int = None):

        start_time = time.time()
        target_top_k = top_k if top_k is not None else settings.top_k
        logger.info(f"Query received | session={session_id} | query={query[:100]}")

        history = self.memory.get_history(session_id)

        if history.strip():
            condensed_history = self.memory.condense_history_xml(history)
            resolution_start = time.time()
            resolution = self.query_resolver.resolve(query, condensed_history)
            search_query = resolution.get("search_query", query)
            resolution_time = time.time() - resolution_start
        else:
            search_query = query
            resolution_time = 0.0

        retrieval_start = time.time()
        results = self.retriever.query(search_query, top_k=target_top_k)
        retrieval_time = time.time() - retrieval_start
        logger.info(f"Retrieved {len(results)} chunks in {retrieval_time:.2f}s | session={session_id}")

        context = self.build_context(results)

        llm_start = time.time()
        prompt = self.build_prompt(query, context, history)
        answer = self.llmservice.generate_response(system_prompt, prompt)
        llm_time = time.time() - llm_start
        logger.info(f"LLM response generated in {llm_time:.2f}s | session={session_id}")

        sources = [ 
            {
                'source': result['source'],
                'page_no': result['page_no'],
                'score': result.get('rerank_score', result.get('score')),
            }
            for result in results 
        ]

        self.memory.add_message(session_id, query, answer)

        total_time = time.time() - start_time
        logger.info(
            f"Total pipeline: {total_time:.2f}s "
            f"(resolver={resolution_time:.2f}s, retrieval={retrieval_time:.2f}s, llm={llm_time:.2f}s) "
            f"| session={session_id}"
        )

        return {
            "question": query,
            "answer": answer,
            "sources": sources
        }
