from typing import List
from app.conf.llm_conf import LLMConf
# from langchain_core.prompts import PromptTemplate


class ChatOpenAIAgent:
    def __init__(self, llm_conf: LLMConf) -> None:
        self.client = llm_conf.llm_config

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        messages = [
            ("system", system_prompt),
            ("human", user_prompt),
        ]
        try:
            ai_msg = self.client.invoke(messages)
            return ai_msg.content
        except Exception as e:
            raise RuntimeError("LLM chat failed") from e

    def chat_stream(self, system_prompt: str, user_prompt: str):
        messages = [
            ("system", system_prompt),
            ("human", user_prompt),
        ]
        try:
            for chunk in self.client.stream(messages):
                if chunk and getattr(chunk, "content", None):
                    yield chunk.content
        except Exception as e:
            raise RuntimeError("LLM chat failed") from e
