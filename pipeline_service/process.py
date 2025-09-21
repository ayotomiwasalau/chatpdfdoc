from langchain.text_splitter import CharacterTextSplitter
from typing import List
from langchain_core.documents import Document
from app.conf.config import Config


class Process:
    def __init__(self, config: Config) -> None:
        self.text = None
        self.config = config

    def chunk_document(self, docs: List[Document]) -> List[Document]:
        if not docs:
            raise ValueError("No documents to process")
        self.text = docs
        splitter = CharacterTextSplitter(
            chunk_size=self.config.chunk_size, chunk_overlap=self.config.chunk_overlap)
        split_docs = splitter.split_documents(self.text)
        return split_docs
