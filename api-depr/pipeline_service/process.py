from langchain.text_splitter import CharacterTextSplitter
from typing import List
from langchain_core.documents import Document
from db.log_data import LogData
class Process:
    def __init__(self) -> None:
        self.text = None
        self.log_data = LogData()
    def chunk_document(self, docs: List[Document], chunk_size: int, chunk_overlap: int) -> List[Document]:
        if not docs:
            raise ValueError("No documents to process")
        self.text = docs
        splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        split_docs = splitter.split_documents(self.text)
        self.log_data.add_log(f"Documents chunked successfully: {len(split_docs)}")
        return split_docs

    