import types
import pytest

from app.services.upload_service import UploadService


class DummyPipeline:
    def __init__(self, should_fail: bool = False):
        self.should_fail = should_fail

    def run(self, filepath: str) -> str:
        if self.should_fail:
            raise RuntimeError("processing error")
        return "run-123"


class DummyUploadFile:
    def __init__(self, filename: str, content: bytes, content_type: str):
        self.filename = filename
        self._content = content
        self._idx = 0
        self.content_type = content_type

    async def read(self, n: int):
        if self._idx >= len(self._content):
            return b""
        chunk = self._content[self._idx:self._idx + n]
        self._idx += len(chunk)
        return chunk

    async def close(self):
        return None


class DummyLog:
    def add_log(self, log: str):
        pass


class _AsyncWriter:
    def __init__(self):
        self.buffer = bytearray()

    async def write(self, data: bytes):
        self.buffer.extend(data)


class _AsyncOpen:
    def __init__(self):
        self.writer = _AsyncWriter()

    async def __aenter__(self):
        return self.writer

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_upload_service_valid_pdf(monkeypatch):
    svc = UploadService(pipeline=DummyPipeline(), log_data=DummyLog())

    # Patch aiofiles.open to no-op async writer
    import aiofiles
    monkeypatch.setattr(aiofiles, "open", lambda *args, **kwargs: _AsyncOpen(), raising=True)

    # Avoid os.remove call by reporting file does not exist
    import os
    monkeypatch.setattr(os.path, "exists", lambda p: False, raising=True)

    upload = DummyUploadFile(filename="test.pdf", content=b"%PDF-1.4\nDATA", content_type="application/pdf")
    run_id = await svc.upload_svc(upload)
    assert run_id == "run-123"


@pytest.mark.asyncio
async def test_upload_service_validation_errors():
    svc = UploadService(pipeline=DummyPipeline(), log_data=DummyLog())

    with pytest.raises(Exception):
        await svc.upload_svc(None)  # type: ignore

    upload = DummyUploadFile(filename=" ", content=b"", content_type="application/pdf")
    with pytest.raises(Exception):
        await svc.upload_svc(upload)

    upload = DummyUploadFile(filename="doc.txt", content=b"x", content_type="text/plain")
    with pytest.raises(Exception):
        await svc.upload_svc(upload)


@pytest.mark.asyncio
async def test_upload_service_pipeline_failure(monkeypatch):
    svc = UploadService(pipeline=DummyPipeline(should_fail=True), log_data=DummyLog())

    import aiofiles
    monkeypatch.setattr(aiofiles, "open", lambda *args, **kwargs: _AsyncOpen(), raising=True)

    import os
    monkeypatch.setattr(os.path, "exists", lambda p: False, raising=True)

    upload = DummyUploadFile(filename="bad.pdf", content=b"%PDF-1.4\nDATA", content_type="application/pdf")
    with pytest.raises(Exception) as ei:
        await svc.upload_svc(upload)


