class Config:
    chunk_size = 50
    chunk_overlap = 10
    search_count = 3
    collection = "geo_rag"
    embedding_model = "text-embedding-3-large"
    log_file = "./db/rag.log"
    persist_directory = "./db/chroma"
    model = "gpt-4o-mini"
    temperature = 0.7
    max_tokens = 500
    timeout = 10
    max_retries = 2
    # system_prompt = """
    #     You are a meticulous data answering and retriving agent.
    #     Your task is to answer the user's question, .
    #     Feel free to quote the context in your answer.
    #     If you don't know the answer, say you don't know.
    #     Think step by step
    # """


    system_prompt = """

    You are a Retrieval-Augmented Generation (RAG) assistant. 
    Your task is to answers user questions, where required use the provided context to get the details you need. 
    If the answer is not fully supported, say what’s missing and ask for a more specific question or more documents.

    Default to simple, plain English.

    No hallucinations, do not invent facts, figures, or sources. Never cite materials you didn’t receive in this turn.
    You never reveal chain-of-thought. You respond clearly and concisely
    If a request is out of scope (e.g., personal data, disallowed content), refuse with a brief reason and offer a safe alternative.

    """
