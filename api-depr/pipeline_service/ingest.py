from langchain_community.document_loaders import PyPDFLoader
from typing import List
import os
from db.log_data import LogData

class Ingest:
    def __init__(self) -> None:
        self._filepath = None
        self._documents = None
        self.log_data = LogData()

    def get_documents(self):
        return self._documents

    def get_filepath(self):
        return self._filepath

    def ingest_from_filepath(self, filepath: str) -> None:
        # Store path and synchronously load PDF pages into Document objects
        self._filepath = filepath
        if not os.path.exists(self._filepath):
            self.log_data.add_log(f"File not found: {self._filepath}")
            raise FileNotFoundError(f"File not found: {self._filepath}")
        try:
            loader = PyPDFLoader(self._filepath)
            # Using synchronous load to avoid async pitfalls here
            pages = loader.load()
        except Exception as e:
            raise ValueError(f"Failed to load PDF: {self._filepath}") from e
        if not pages:
            raise ValueError(f"No pages found in: {self._filepath}")
        self._documents = pages
        self.log_data.add_log(f"PDF loaded successfully: {self._filepath}")


