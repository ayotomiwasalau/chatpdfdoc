from langchain_openai import ChatOpenAI
from app.conf.config import Config
class LLMConf:
    def __init__(self, config: Config) -> None:
        self.llm_config = ChatOpenAI(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )
