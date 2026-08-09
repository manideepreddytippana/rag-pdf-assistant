import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from openai import OpenAI

load_dotenv()

class LLMService:
    def __init__(self):
        api_key = os.getenv("API_KEY")
        base_url = os.getenv("API_BASE_URL")


        if not api_key:
            raise ValueError("API_KEY not set")

        self.client = OpenAI(api_key = api_key, base_url = base_url)

    def generate_response(self, system_prompt, user_prompt):

        response = self.client.chat.completions.create(
            model="sarvam-105b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature = 0.2,
            max_completion_tokens = 4096,
            stream = False
        )
        return response.choices[0].message.content
