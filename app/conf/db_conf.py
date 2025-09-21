from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from app.conf.config import Config
class ChromaDBConf:
    def __init__(self, config: Config) -> None:
        self.db_client = Chroma(
            collection_name=config.collection,
            embedding_function=OpenAIEmbeddings(model=config.embedding_model),
            persist_directory=config.persist_directory,
        )


