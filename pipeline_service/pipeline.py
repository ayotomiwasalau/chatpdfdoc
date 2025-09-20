from typing import Optional
import uuid
from ingest import Ingest
from process import Process
from store import Store

class Pipeline:
    def __init__(self, filepath: str, db_path: Optional[str] = None) -> None:
        self.filepath = filepath
        self.run_id = str(uuid.uuid4())
        self._ingestor = Ingest()
        self._processor = Process()
        self._store = Store()

    def run(self) -> str:
        try:
            self._ingestor.ingest_from_filepath(self.filepath)
            docs = self._ingestor.get_documents()
            filepath = self._ingestor.get_filepath()
            print("*" * 50)
            print(f"Loaded {len(docs)} pages from: {filepath}")
            print("*" * 50)
            # Print the combined text content for visibility (truncate to keep console readable)
            # combined_text = "\n\n".join([d.page_content for d in docs])
            
            processed = self._processor.chunk_document(docs, chunk_size=100, chunk_overlap=20)
            self._store.store_embeddings_chroma(processed)
            return self.run_id
        except Exception as e:
            print(e)
