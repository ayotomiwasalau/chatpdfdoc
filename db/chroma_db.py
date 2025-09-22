import uuid
from typing import List
from langchain_core.documents import Document
from app.conf.db_conf import ChromaDBConf


class ChromaDB:
    def __init__(self, chroma_db_conf: ChromaDBConf) -> None:
        self.vector_store = chroma_db_conf.db_client

    def load_chroma(self, document: str, run_id: str) -> None:
        uuids = [str(uuid.uuid4()) for _ in range(len(document))]
        for d in document:
            d.metadata = d.metadata or {}
            d.metadata["run_id"] = run_id
        self.vector_store.add_documents(documents=document, ids=uuids)

    def similarity_search(self, query: str, k: int) -> List[Document]:
        return self.vector_store.similarity_search(query, k)

    def delete_documents(self, run_ids: List[str]) -> None:
        if not run_ids:
            return
        query = {"run_id": {"$in": run_ids}}
        try:
            self.vector_store.delete(filter=query)
        except TypeError:
            self.vector_store.delete(where=query)
