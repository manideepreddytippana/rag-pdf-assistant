import json

class QueryDecomposer:

    def __init__(self, llm_service):
        self.llm_service = llm_service

    def decompose(self, query):
        query_decomposer_prompt = """
        You are a query decomposition assistant.
        
        Split the following user request into independent questions.
        
        Rules:
        1. Return ONLY valid JSON.
        2. Output format:
        {
          "questions": [
              "...",
              "...",
              "..."
          ]
        }
        3. If the user asks only ONE question,
           return a list containing only that question.
        4. Never explain.
        5. Never return markdown.
        """.strip()

        response = self.llm_service.generate_response(system_prompt = query_decomposer_prompt,user_prompt =  query)

        try:
            data = json.loads(response)
            questions = data["questions"]

            if len(questions) == 0:
                return [query]
            return questions

        except Exception:
            # fallback mech
            return [query]