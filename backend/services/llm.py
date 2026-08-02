import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

class LLMService:
    def __init__(self):

        token = os.getenv("HF_TOKEN_2")

        if not token:
            raise ValueError("HF_TOKEN not set")

        self.client = InferenceClient(token=token)

    def generate_response(self, system_prompt, user_prompt):

        response = self.client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature = 0.2,
            stream = False
        )
        return response.choices[0].message.content
