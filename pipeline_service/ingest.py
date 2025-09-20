from langchain_community.document_loaders import PyPDFLoader
from typing import List


class Ingest:
    def __init__(self) -> None:
        self._filepath = None
        self._documents = None

    def ingest_from_filepath(self, filepath: str) -> None:
        # Store path and synchronously load PDF pages into Document objects
        self._filepath = filepath
        loader = PyPDFLoader(self._filepath)
        # Using synchronous load to avoid async pitfalls here
        pages = loader.load()
        self._documents = pages

    def get_documents(self):
        return self._documents

    def get_filepath(self):
        return self._filepath
