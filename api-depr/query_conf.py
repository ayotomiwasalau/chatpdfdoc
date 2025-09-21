from dataclasses import dataclass
from config import Config
from db.chroma_db import ChromaDB
from llm_service.chatOAagent import ChatOpenAIAgent
from db.log_data import LogData
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

@dataclass(slots=True)
class QueryConf:
    config: type[Config]
    chroma_db: ChromaDB
    llm: ChatOpenAIAgent
    log_data: LogData

    @classmethod
    def create(cls) -> "QueryConf":
        cfg = Config  # use class-level config
        return cls(
            config=cfg,
            chroma_db=ChromaDB(db_client=Chroma(
                    collection_name=cfg.collection,
                    embedding_function=OpenAIEmbeddings(model=cfg.embedding_model),
                    persist_directory=cfg.persist_directory,
                )),
            llm=ChatOpenAIAgent(
                    client=ChatOpenAI(
                        model=cfg.model,
                        temperature=cfg.temperature,
                        max_tokens=cfg.max_tokens,
                        timeout=cfg.timeout,
                        max_retries=cfg.max_retries,
                    )
            ),
            log_data=LogData(log_file=cfg.log_file),
        )


query_conf = QueryConf.create()