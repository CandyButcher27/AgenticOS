from unittest.mock import patch
from fastapi.testclient import TestClient
from app import app
from chat_core import NoSupportedProviderError, AllModelsRateLimitedError

client = TestClient(app)


@patch("app.handle_chat")
def test_success_returns_200(mock_handle_chat):
    mock_handle_chat.return_value = {"model_used": "groq/compound-beta", "content": "Paris."}
    resp = client.post("/chat", json={"prompt": "hi", "keys": {"groq": "fake-key"}})
    assert resp.status_code == 200
    assert resp.json() == {"model_used": "groq/compound-beta", "content": "Paris."}


@patch("app.handle_chat")
def test_no_supported_provider_returns_400(mock_handle_chat):
    mock_handle_chat.side_effect = NoSupportedProviderError("no supported provider keys")
    resp = client.post("/chat", json={"prompt": "hi", "keys": {}})
    assert resp.status_code == 400


@patch("app.handle_chat")
def test_all_rate_limited_returns_429(mock_handle_chat):
    mock_handle_chat.side_effect = AllModelsRateLimitedError("all matching models are rate-limited, try again later")
    resp = client.post("/chat", json={"prompt": "hi", "keys": {"groq": "fake-key"}})
    assert resp.status_code == 429


@patch("app.handle_chat")
def test_completion_error_returns_502(mock_handle_chat):
    mock_handle_chat.side_effect = Exception("provider down")
    resp = client.post("/chat", json={"prompt": "hi", "keys": {"groq": "fake-key"}})
    assert resp.status_code == 502
