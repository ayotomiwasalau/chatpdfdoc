from langchain.embeddings.openai import OpenAIEmbeddings
import uuid
from langchain_chroma import Chroma
from typing import List
from langchain_core.documents import Document
class ChromaDB:
    def __init__(self, collection: str) -> None:
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma(
                    collection_name=collection,
                    embedding_function=self.embeddings,
                    persist_directory="./db/chroma",
                )
    def load_chroma(self, document: str) -> None:
        uuids = [str(uuid.uuid4()) for _ in range(len(document))]
        self.vector_store.add_documents(documents=document, ids=uuids)

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        return self.vector_store.similarity_search(query, k)



