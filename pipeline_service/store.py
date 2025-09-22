from db.chroma_db import ChromaDB
from typing import List
from app.conf.config import Config


class Store:
    def __init__(self, chroma_db: ChromaDB) -> None:
        self.chroma_db = chroma_db

    def store_embeddings_chroma(self, document: List[str], run_id: str) -> None:
        if not document:
            raise ValueError("No documents to store")
        try:
            self.chroma_db.load_chroma(document, run_id)
        except Exception as e:
            raise RuntimeError(f"Failed to store embeddings") from e

    def delete_documents(self, run_ids: List[str]) -> None:
        if not run_ids:
            raise ValueError("No run ids to delete")
        try:
            self.chroma_db.delete_documents(run_ids)
        except Exception as e:
            raise RuntimeError("Failed to delete embeddings") from e