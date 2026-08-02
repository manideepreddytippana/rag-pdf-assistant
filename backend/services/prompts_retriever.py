import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
PROMPTS_DIR = os.path.join(PROJECT_ROOT, "prompts")

def get_prompt(prompt : str):
    file_path = os.path.join(PROMPTS_DIR, prompt)
    with open(file_path , 'r') as f:
        return f.read().strip()