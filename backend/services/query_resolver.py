import json
import logging

logger = logging.getLogger("rag_pipeline")

class QueryResolver:

    def __init__(self, llm_service):
        self.llm_service = llm_service

    def resolve(self, query: str, history: str = "") -> dict:

        if not history or not history.strip():
            return {
                "is_follow_up": False,
                "search_query": query.strip()
            }

        prompt = f"""You are a search query resolver for a document retrieval system.
Given the conversation history and a user query:
1. Determine if the user query is a FOLLOW-UP that depends on context or pronouns (e.g., "it", "they", "that", "how many heads does it have?", "explain more about its architecture").
2. If it is a follow-up, reformulate it into a self-contained, standalone search query by replacing pronouns/references with the explicit subject from history.
3. If it is a NEW TOPIC or already standalone, do NOT alter the core query.

<conversation_history>
{history}
</conversation_history>

<user_query>
{query}
</user_query>

Return ONLY valid JSON (no explanation, no markdown ticks):
{{"is_follow_up": true_or_false, "search_query": "standalone search query string"}}"""

        try:
            raw_response = self.llm_service.generate_response(
                system_prompt="You are a query resolution assistant. Output strictly JSON.",
                user_prompt=prompt
            ).strip()

            if raw_response.startswith("```json"):
                raw_response = raw_response[7:]
            if raw_response.startswith("```"):
                raw_response = raw_response[3:]
            if raw_response.endswith("```"):
                raw_response = raw_response[:-3]
            raw_response = raw_response.strip()

            data = json.loads(raw_response)
            is_follow_up = bool(data.get("is_follow_up", False))
            search_query = str(data.get("search_query", query)).strip()

            if not search_query:
                search_query = query.strip()

            logger.info(f"Query resolved | is_follow_up={is_follow_up} | search_query='{search_query}'")
            return {
                "is_follow_up": is_follow_up,
                "search_query": search_query
            }

        except Exception as e:
            logger.warning(f"Query resolution parsing failed ({e}), falling back to original query")
            return {
                "is_follow_up": False,
                "search_query": query.strip()
            }
