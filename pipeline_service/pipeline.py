from typing import Optional
import uuid
from .ingest import Ingest
from .process import Process
from .store import Store
from db.log_db import LogData
class Pipeline:
    def __init__(self, ingestor: Ingest, processor: Process, store: Store, log_data: LogData) -> None:
        self.run_id = str(uuid.uuid4())
        self.ingestor = ingestor
        self.processor = processor
        self.store = store
        self.log_data = log_data


    def run(self, filepath: str) -> str:
        try:
            docs = self.ingestor.ingest_from_filepath(filepath)
            self.log_data.add_log(f"Loaded {len(docs)} pages from: {filepath}")
            processed = self.processor.chunk_document(docs)
            self.store.store_embeddings_chroma(processed)
            return self.run_id
        except (FileNotFoundError, ValueError) as e:
            self.log_data.add_log(f"Pipeline failed (run_id={self.run_id})"+str(e))
            raise  
        except Exception as e:
            self.log_data.add_log(f"Pipeline failed (run_id={self.run_id})"+str(e))
            raise RuntimeError(f"Pipeline failed (run_id={self.run_id})"+str(e))
