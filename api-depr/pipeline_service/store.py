from db.chroma_db import ChromaDB
from typing import List
from config import Config
from db.log_data import LogData
class Store:
    def __init__(self) -> None:
        self.chroma_db = ChromaDB(Config.collection)
        self.log_data = LogData()
    def store_embeddings_chroma(self, document: List[str]) -> None:
        if not document:
            raise ValueError("No documents to store")
        try:
            self.chroma_db.load_chroma(document)
            self.log_data.add_log(f"Embeddings stored successfully")
        except Exception as e:
            self.log_data.add_log(f"Failed to store embeddings")
            raise RuntimeError(f"Failed to store embeddings") from e