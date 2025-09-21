from .chatOAagent import ChatOpenAIAgent
from db.chroma_db import ChromaDB
from app.conf.config import Config


class Query:
    def __init__(self, chat_openai_agent: ChatOpenAIAgent, chroma_db: ChromaDB, config: Config) -> None:
        self.llm = chat_openai_agent
        self.chroma_db = chroma_db
        self.config = config

    def _build_prompt(self, user_prompt: str) -> str:
        similar_docs = self.chroma_db.similarity_search(
            user_prompt, k=self.config.search_count)
        context = "\n\n".join([doc.page_content for doc in similar_docs])
        return f"{user_prompt}\n\nContext:\n{context}"

    def query(self, user_prompt: str) -> str:
        full_prompt = self._build_prompt(user_prompt)
        return self.llm.chat(self.config.system_prompt, full_prompt)

    def query_stream(self, user_prompt: str):
        full_prompt = self._build_prompt(user_prompt)
        for token in self.llm.chat_stream(self.config.system_prompt, full_prompt):
            yield token
