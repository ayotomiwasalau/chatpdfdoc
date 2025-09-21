def test_health_endpoint(client):
    resp = client.get("/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")


def test_add_document_page(client):
    resp = client.get("/add-document")
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")


def test_query_endpoint_success(monkeypatch, client):
    # Patch Query.query to avoid external calls
    from llm_service import query as query_module

    def fake_query(self, user_prompt: str) -> str:
        return "test-answer"

    monkeypatch.setattr(query_module.Query, "query", fake_query, raising=True)

    resp = client.post("/v1/query", json={"query": "What is RAG?"})
    assert resp.status_code == 200
    assert resp.json() == {"answer": "test-answer"}


def test_query_endpoint_validation_error(client):
    resp = client.post("/v1/query", json={"query": "   "})
    assert resp.status_code == 422


def test_query_endpoint_streaming(monkeypatch, client):
    from llm_service import query as query_module

    def fake_query_stream(self, user_prompt: str):
        tokens = ["tok1 ", "tok2 ", "tok3"]
        for t in tokens:
            yield t

    monkeypatch.setattr(query_module.Query, "query_stream", fake_query_stream, raising=True)

    resp = client.post("/v1/query?stream_mode=true", json={"query": "stream please"})
    # StreamingResponse is consumed by TestClient into text
    assert resp.status_code == 200
    assert resp.text == "tok1 tok2 tok3"


def test_upload_endpoint_success(monkeypatch, client):
    # Patch UploadService.upload_svc to bypass file IO and pipeline
    from app import services as services_pkg
    from app.services import upload_service as upload_service_module

    async def fake_upload_svc(self, file):
        return "test-run-id"

    monkeypatch.setattr(upload_service_module.UploadService, "upload_svc", fake_upload_svc, raising=True)

    files = {"file": ("doc.pdf", b"%PDF-1.4\n...", "application/pdf")}
    resp = client.post("/v1/upload", files=files)
    assert resp.status_code == 200
    assert resp.json() == {"run_id": "test-run-id", "status": "success"}


def test_upload_endpoint_validation_error(client):
    files = {"file": ("doc.txt", b"hello", "text/plain")}
    resp = client.post("/v1/upload", files=files)
    assert resp.status_code == 422


