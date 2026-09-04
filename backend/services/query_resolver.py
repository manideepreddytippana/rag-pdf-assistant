import re
import logging

logger = logging.getLogger("rag_pipeline")

_FOLLOW_UP_PRONOUNS = re.compile(
    r'\b(it|its|they|them|their|theirs|this|that|these|those'
    r'|he|she|him|her|his|hers)\b',
    re.IGNORECASE
)

_FOLLOW_UP_PHRASES = re.compile(
    r'\b(explain more|tell me more|elaborate|go on|continue'
    r'|expand on that|what about|how about|why is that'
    r'|and also|more details|can you clarify|what else'
    r'|anything else|in more detail|give me more'
    r'|compared to|versus|same thing|the above'
    r'|mentioned earlier|you said|you mentioned)\b',
    re.IGNORECASE
)

class QueryResolver:
    """
    Resolves follow-up queries using local regex-based detection avoiding unnecessary LLM calls.
    """

    def __init__(self, llm_service=None):
        self.llm_service = llm_service

    def _extract_last_user_topic(self, history: str) -> str | None:
        """Extract the last user message from condensed history like user, assistant."""
        if not history:
            return None

        lines = history.strip().split("\n")
        for line in reversed(lines):
            if line.startswith("User: "):
                topic = line[6:].strip()
                return topic if topic else None

        return None

    def _is_follow_up(self, query: str) -> bool:
        """Detect if the query is a follow-up using regex patterns."""
        if _FOLLOW_UP_PRONOUNS.search(query):
            return True

        if _FOLLOW_UP_PHRASES.search(query):
            return True

        words = query.strip().split()
        if len(words) <= 3:

            has_named_entity = any(
                w[0].isupper() and i > 0
                for i, w in enumerate(words)
                if len(w) > 1
            )
            if not has_named_entity:
                return True

        return False

    def resolve(self, query: str, history: str = "") -> dict:
        """
        Resolve follow-up queries using local regex patterns 
        and return followup intent and enriched search query.
        """
        if not history or not history.strip():
            return {
                "is_follow_up": False,
                "search_query": query.strip()
            }

        is_follow_up = self._is_follow_up(query)

        if not is_follow_up:
            logger.info(
                f"Query resolved (local) | is_follow_up=False | "
                f"search_query='{query.strip()[:80]}'"
            )
            return {
                "is_follow_up": False,
                "search_query": query.strip()
            }

        last_topic = self._extract_last_user_topic(history)

        if last_topic:

            search_query = f"{query.strip()} — context: {last_topic}"
        else:
            search_query = query.strip()

        logger.info(
            f"Query resolved (local) | is_follow_up=True | "
            f"search_query='{search_query[:100]}'"
        )
        return {
            "is_follow_up": True,
            "search_query": search_query
        }
