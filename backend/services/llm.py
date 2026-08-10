import logging
from openai import OpenAI
from config import settings

logger = logging.getLogger("rag_pipeline")

class LLMService:
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        self.api_key = api_key or settings.api_key
        self.base_url = base_url or settings.api_base_url
        self.model = model or settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens

        if not self.api_key:
            raise ValueError("API_KEY (or HF_TOKEN) not configured in .env or settings")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate_response(self, system_prompt: str, user_prompt: str):

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_completion_tokens=self.max_tokens,
                stream=False
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM API call failed: {e}", exc_info=True)
            raise
