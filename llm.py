from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()


def ask_llm(system_prompt: str, chat_history: list[dict[str, str]]) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.responses.create(
        model="gpt-4.1",
        input="Write a one-sentence bedtime story about a unicorn."
    )

    print(response.output_text)
    