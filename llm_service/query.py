from chatOAagent import ChatOpenAIAgent
from chroma_db import ChromaDB
class Query:
    def __init__(self) -> None:
        self.chroma_db = ChromaDB("geo_rag")
        self.llm = ChatOpenAIAgent(
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=148,
            timeout=10,
            max_retries=2
        )
        
        self.system_prompt = """
            You are a meticulous data answering and retriving agent.
            Your task is to answer the user's question based on the provided context.
            Feel free to quote the context in your answer.
            If you don't know the answer, say you don't know.
            Think step by step
        """

    def query(self, user_prompt: str) -> str:
        # Get similar documents from ChromaDB
        similar_docs = self.chroma_db.similarity_search(user_prompt, k=1)

        # Extract content from documents and create context
        context = "\n\n".join([doc.page_content for doc in similar_docs])
        
        # Create the full prompt with context
        full_prompt = f"{user_prompt}\n\nContext:\n{context}"
        
        # Use ChatOpenAIAgent to generate response
        return self.llm.chat(self.system_prompt, full_prompt)

