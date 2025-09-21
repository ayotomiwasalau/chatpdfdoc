from db.chroma_db import ChromaDB
from typing import List
from app.conf.config import Config


class Store:
    def __init__(self, chroma_db: ChromaDB) -> None:
        self.chroma_db = chroma_db

    def store_embeddings_chroma(self, document: List[str]) -> None:
        if not document:
            raise ValueError("No documents to store")
        try:
            self.chroma_db.load_chroma(document)
        except Exception as e:
            raise RuntimeError(f"Failed to store embeddings") from e
