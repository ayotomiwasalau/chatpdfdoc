import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def _test_env():
    os.environ.setdefault("OPENAI_API_KEY", "test")


@pytest.fixture()
def client():
    from app.controllers import app
    return TestClient(app)


