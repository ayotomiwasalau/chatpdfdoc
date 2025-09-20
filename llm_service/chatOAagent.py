from langchain_openai import ChatOpenAI
from typing import List
# from langchain_core.prompts import PromptTemplate

class ChatOpenAIAgent:
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7, max_tokens: int = None, timeout: int = None, max_retries: int = 2) -> None:
        self.client = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            max_retries=max_retries
        )

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            (
                "system",
                system_prompt,
            ),
            ("human", user_prompt),
        ]
        print(messages)
        ai_msg = self.client.invoke(messages)
        return ai_msg.content