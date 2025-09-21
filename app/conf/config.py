class Config:
    chunk_size = 50
    chunk_overlap = 10
    search_count = 3
    collection = "geo_rag"
    embedding_model = "text-embedding-3-large"
    log_file="./db/logs.txt"
    persist_directory = "./db/chroma"
    model = "gpt-4o-mini"
    temperature = 0.7
    max_tokens = 500
    timeout = 10
    max_retries = 2
    system_prompt = """
        You are a meticulous data answering and retriving agent.
        Your task is to answer the user's question, where required, use the provided context to get the details you need.
        Feel free to quote the context in your answer.
        If you don't know the answer, say you don't know.
        Think step by step
    """