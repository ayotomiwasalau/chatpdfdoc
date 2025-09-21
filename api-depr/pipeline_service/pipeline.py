from typing import Optional
import uuid
from .ingest import Ingest
from .process import Process
from .store import Store
from config import Config
from db.log_data import LogData

class Pipeline:
    def __init__(self, filepath: str, db_path: Optional[str] = None) -> None:
        self.filepath = filepath
        self.run_id = str(uuid.uuid4())
        self._ingestor = Ingest()
        self._processor = Process()
        self._store = Store()
        self.log_data = LogData()

    def run(self) -> str:
        try:
            self._ingestor.ingest_from_filepath(self.filepath)
            docs = self._ingestor.get_documents()

            self.log_data.add_log(f"Loaded {len(docs)} pages from: {self.filepath}")
            
            processed = self._processor.chunk_document(
                docs, chunk_size=Config.chunk_size, chunk_overlap=Config.chunk_overlap
            )
            self._store.store_embeddings_chroma(processed)
            return self.run_id
        except (FileNotFoundError, ValueError) as e:
            self.log_data.add_log(f"Pipeline failed (run_id={self.run_id})"+str(e))
            raise  # 400-class client problems
        except Exception as e:
            self.log_data.add_log(f"Pipeline failed (run_id={self.run_id})"+str(e))
            raise RuntimeError(f"Pipeline failed (run_id={self.run_id})"+str(e))
