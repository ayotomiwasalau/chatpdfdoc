from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import QueryResponse
from db.log_db import LogData
from llm_service.query import Query
from typing import List


class QueryService:
    def __init__(self, query: Query, log_data: LogData):
        self.query = query
        self.log_data = log_data

    def query_svc(self, query: str, stream_mode: bool, run_ids: List[str] = []):
        if not query or not query.strip():
            raise HTTPException(
                status_code=422, detail="Query must not be empty")

        try:
            llm = self.query
            if stream_mode:
                def token_gen():
                    for token in llm.query_stream(query, run_ids):
                        yield token
                self.log_data.add_log(
                    f"Query streaming started successfully for query", "info")

                return StreamingResponse(
                    token_gen(),
                    media_type="text/plain",
                    headers={
                        "Cache-Control": "no-cache",
                        "X-Accel-Buffering": "no",
                    },
                )
            else:
                answer = llm.query(query)
                self.log_data.add_log(f"Query successful for query", "info")
                return QueryResponse(answer=answer)
        except RuntimeError as e:
            self.log_data.add_log(f"Upstream LLM error in query_svc: {e}", "error")
            raise HTTPException(status_code=502, detail=str(e))
        except Exception as e:
            self.log_data.add_log(f"Unexpected error in query_svc: {e}", "error")
            raise HTTPException(
                status_code=500, detail=f"Internal server error : {e}")
