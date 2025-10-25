import os
import uuid
import shutil
from typing import List
from langchain_core.documents import Document
from app.conf.db_conf import ChromaDBConf
from app.conf.config import Config

class ChromaDB:
    def __init__(self, chroma_db_conf: ChromaDBConf) -> None:
        self.vector_store = chroma_db_conf.db_client

    def _dir_size_mb(self, path: str) -> float:
        total = 0
        for root, _, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except FileNotFoundError:
                    continue
        return total / (1024 * 1024)

    def _maybe_purge_chroma(self) -> None:
        persist_dir = os.path.abspath(Config.persist_directory)
        max_mb = getattr(Config, "max_chroma_dir_mb", None)
        if not max_mb:
            return
        if not os.path.exists(persist_dir):
            return
        if self._dir_size_mb(persist_dir) >= max_mb:
            shutil.rmtree(persist_dir, ignore_errors=True)
            os.makedirs(persist_dir, exist_ok=True)
            # Reinitialize the vector store to point to the fresh directory
            self.vector_store = ChromaDBConf(Config).db_client

    def load_chroma(self, document: List[Document], run_id: str) -> None:
        self._maybe_purge_chroma()
        uuids = [str(uuid.uuid4()) for _ in range(len(document))]
        for d in document:
            d.metadata = d.metadata or {}
            d.metadata["run_id"] = run_id
        self.vector_store.add_documents(documents=document, ids=uuids)

    def similarity_search(self, query: str, k: int, run_ids: List[str]) -> List[Document]:
        if not run_ids:
            return []
        meta = {"run_id": {"$in": run_ids}}
        try:
            return self.vector_store.similarity_search(query, k=k, filter=meta)
        except TypeError:
            return self.vector_store.similarity_search(query, k=k, where=meta)

    def delete_documents(self, run_ids: List[str]) -> None:
        if not run_ids:
            return
        query = {"run_id": {"$in": run_ids}}
        try:
            self.vector_store.delete(filter=query)
        except TypeError:
            self.vector_store.delete(where=query)