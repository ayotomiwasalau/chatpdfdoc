from .chatOAagent import ChatOpenAIAgent
from db.chroma_db import ChromaDB
from config import Config
class Query:
    def __init__(self) -> None:
        self.chroma_db = ChromaDB("geo_rag")
        self.llm = ChatOpenAIAgent(
            model=Config.model,
            temperature=Config.temperature,
            max_tokens=Config.max_tokens,
            timeout=Config.timeout,
            max_retries=Config.max_retries
        )
        # self.chroma_db = chroma_db
        # self.llm = llm
        
        self.system_prompt = Config.system_prompt

    def query(self, user_prompt: str, stream_mode: bool) -> str:
        try:
            similar_docs = self.chroma_db.similarity_search(user_prompt, k=Config.search_count)
            context = "\n\n".join([doc.page_content for doc in similar_docs])
            full_prompt = f"{user_prompt}\n\nContext:\n{context}"
            if stream_mode:
                for token in self.llm.chat(self.system_prompt, full_prompt, stream_mode):
                    yield token
            else:
                return self.llm.chat(self.system_prompt, full_prompt, stream_mode)
        except Exception as e:
            print(e)
            raise RuntimeError("RAG query failed") from e

