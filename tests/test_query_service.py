import pytest
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from app.services.query_service import QueryService


class FakeQuery:
    def __init__(self, answer: str = "ok", tokens=None, raise_runtime: bool = False):
        self._answer = answer
        self._tokens = tokens or ["a", "b", "c"]
        self._raise_runtime = raise_runtime

    def query(self, user_prompt: str) -> str:
        if self._raise_runtime:
            raise RuntimeError("upstream failed")
        return self._answer

    def query_stream(self, user_prompt: str):
        if self._raise_runtime:
            raise RuntimeError("upstream failed")
        for t in self._tokens:
            yield t


class FakeLog:
    def __init__(self):
        self.logs = []

    def add_log(self, log: str, level: str = "info"):
        self.logs.append(log)

    def get_log(self):
        return list(self.logs)


def test_query_service_validation_error():
    svc = QueryService(query=FakeQuery(), log_data=FakeLog())
    with pytest.raises(HTTPException) as ei:
        svc.query_svc("   ", stream_mode=False)
    assert ei.value.status_code == 422


def test_query_service_success_non_stream():
    logger = FakeLog()
    svc = QueryService(query=FakeQuery(answer="answer"), log_data=logger)
    res = svc.query_svc("hi", stream_mode=False)
    assert res.answer == "answer"
    assert any("Query successful" in x for x in logger.get_log())


def test_query_service_success_stream():
    logger = FakeLog()
    svc = QueryService(query=FakeQuery(tokens=["x", "y"]), log_data=logger)
    res = svc.query_svc("hi", stream_mode=True)
    assert isinstance(res, StreamingResponse)


def test_query_service_runtime_error_mapped():
    logger = FakeLog()
    svc = QueryService(query=FakeQuery(raise_runtime=True), log_data=logger)
    with pytest.raises(HTTPException) as ei:
        svc.query_svc("hi", stream_mode=False)
    assert ei.value.status_code == 502
    assert any("Upstream LLM error" in x for x in logger.get_log())
