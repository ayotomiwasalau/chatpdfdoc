from langchain.text_splitter import CharacterTextSplitter
from typing import List
from langchain_core.documents import Document
class Process:
    def __init__(self) -> None:
        self.text = None
        
    def chunk_document(self, text: List[str], chunk_size: int, chunk_overlap: int) -> List[Document]:
        self.text = text
        splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        split_docs = splitter.split_documents(self.text)
        return split_docs

    