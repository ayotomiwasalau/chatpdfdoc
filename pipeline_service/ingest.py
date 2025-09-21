from langchain_community.document_loaders import PyPDFLoader
from typing import List
import os
from langchain_core.documents import Document

class Ingest:
    def __init__(self) -> None:
        self._filepath = None

    def get_filepath(self):
        return self._filepath

    def ingest_from_filepath(self, filepath: str) -> List[Document]:
        self._filepath = filepath
        if not os.path.exists(self._filepath):
            raise FileNotFoundError(f"File not found: {self._filepath}")
        try:
            loader = PyPDFLoader(self._filepath)
            pages = loader.load()
        except Exception as e:
            raise ValueError(f"Failed to load PDF: {self._filepath}")
        if not pages:
            raise ValueError(f"No pages found in: {self._filepath}")
        return pages


