# Клиент для работы с LLM (Large Language Model) через OpenAI API
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Клиент для работы с OpenAI"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        return response.choices[0].message.content
