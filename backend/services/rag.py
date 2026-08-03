from services.query_decomposer import QueryDecomposer
from services.prompts_retriever import get_prompt

system_prompt = get_prompt("system_prompt.txt")

class RagService:

    def __init__(self, retriever, llmservice, memory):
    
        self.retriever = retriever
        self.llmservice = llmservice
        self.memory = memory
        self.query_decomposer = QueryDecomposer(llmservice)

    def contextualize_query(self, query, history):

        if not history:
            return query
        prompt = f"""
        Given a chat history and the latest user question, formulate a standalone question 
                that can be understood without the chat history. Do NOT answer the question, 
                just reformulate it.
                
                Chat History:
                {history}
                
                User Question: {query}
                
                Standalone Question:
        """.strip()
\
        return self.llmservice.generate_response("You are a helpful query rewriter", prompt).strip()
    
        
    def build_context(self, results : list[dict]):

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

    def build_prompt(self, query, context, history=""):

        return f"""
Answer the question using ONLY the context below.

Rules:
- Match response length/format to question type: factual → 1-3 sentences, no lists; how/why/process → numbered steps; comparison/multi-part → bullets/table; otherwise → shortest complete answer.
- Don't add structure (headings, bullets, numbering) unless the question or content needs it.
- If context is insufficient, say clearly what's missing instead of guessing.
- Never hallucinate or fabricate facts.

<history>
{history}
</history>
<context>
{context}
</context>

<question>
{query}
</question>

Answer:
""".strip()

    def get_single_answer(self, query, history, top_k: int = 5):
        # rewritten the query with history context
        search_query = self.contextualize_query(query, history)

        results = self.retriever.query(search_query, top_k=top_k)
        context = self.build_context(results)
        prompt = self.build_prompt(query, context, history)
        
        answer = self.llmservice.generate_response(system_prompt, prompt)
        sources = [ 
            {
                'source': result['source'],
                'page_no': result['page_no'],
                'score': result.get('rerank_score', result.get('score')),
            }
            for result in results 
        ]
        return {
            "question": query,
            "answer": answer,
            "sources": sources
        }
  
    def get_answer(self, query, session_id = "session_id",top_k: int = 5):

        # get history for the db
        history = self.memory.get_history(session_id)
        

        questions = self.query_decomposer.decompose(query)

        results = []
        for question in questions:
            result = self.get_single_answer(question, history= history, top_k=top_k)
            results.append(result)

        if len(results) == 1:
            self.memory.add_message(session_id, query, results[0]['answer'])
            return results[0]

        else:
            combined_answer = "\n\n".join(
                f"{i+1}th Answer. {result['answer']}\n"
                for i,result in enumerate(results)
            )
            seen = set()
            unique_sources = []
            for result in results:
                for source in result['sources']:
                    key = (source['source'], source['page_no'])
                    if key not in seen:
                        seen.add(key)
                        unique_sources.append(source)
                

            

        self.memory.add_message(session_id, query, combined_answer)
        return {
            "question": query,
            "answer": combined_answer,
            "sources": unique_sources
        }
