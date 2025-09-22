from typing import Optional, List
import uuid
from .ingest import Ingest
from .process import Process
from .store import Store
from db.log_db import LogData


class Pipeline:
    def __init__(self, ingestor: Ingest, processor: Process, store: Store, log_data: LogData) -> None:
        self.run_id = None
        self.ingestor = ingestor
        self.processor = processor
        self.store = store
        self.log_data = log_data

    def run(self, filepath: str) -> str:
        self.run_id = str(uuid.uuid4())
        try:
            docs = self.ingestor.ingest_from_filepath(filepath)
            self.log_data.add_log(f"Ingested {len(docs)} pages from: {filepath}", "info")

            processed = self.processor.chunk_document(docs)
            self.log_data.add_log(f"Chunked {filepath}", "info")

            self.store.store_embeddings_chroma(processed, self.run_id)
            self.log_data.add_log(f"Stored embeddings for {filepath}", "info")
            return self.run_id
        except (FileNotFoundError, ValueError) as e:
            self.log_data.add_log(
                f"Pipeline failed (run_id={self.run_id})"+str(e), "error")
            raise
        except Exception as e:
            self.log_data.add_log(
                f"Pipeline failed (run_id={self.run_id})"+str(e), "error")
            raise RuntimeError(
                f"Pipeline failed (run_id={self.run_id})"+str(e))

    
    def delete_documents(self, run_ids: List[str]):
        self.store.delete_documents(run_ids)