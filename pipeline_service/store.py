from chroma_db import ChromaDB
from typing import List
class Store:
    def __init__(self) -> None:
        self.chroma_db = ChromaDB("geo_rag")
        
    def store_embeddings_chroma(self, document: List[str]) -> None:
        self.chroma_db.load_chroma(document)