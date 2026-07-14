import pytest
from unittest.mock import patch, MagicMock
import rate_limiter
from chat_core import handle_chat, NoSupportedProviderError, AllModelsRateLimitedError


@pytest.fixture(autouse=True)
def clear_rate_limiter():
    rate_limiter._calls.clear()
    yield
    rate_limiter._calls.clear()


def test_no_keys_raises_no_supported_provider():
    with pytest.raises(NoSupportedProviderError):
        handle_chat("hi", {})


def test_unmatched_provider_raises_no_supported_provider():
    with pytest.raises(NoSupportedProviderError):
        handle_chat("hi", {"unknown": "x"})


@patch("chat_core.litellm.completion")
@patch("chat_core.select_model")
def test_valid_key_returns_response(mock_select, mock_completion):
    mock_select.return_value = "groq/compound-beta"
    resp_obj = MagicMock()
    resp_obj.choices[0].message.content = "Paris."
    mock_completion.return_value = resp_obj

    result = handle_chat("capital of France?", {"groq": "fake-key"})
    assert result == {"model_used": "groq/compound-beta", "content": "Paris."}


@patch("chat_core.litellm.completion")
@patch("chat_core.select_model")
def test_completion_error_propagates(mock_select, mock_completion):
    mock_select.return_value = "groq/compound-beta"
    mock_completion.side_effect = Exception("provider down")

    with pytest.raises(Exception, match="provider down"):
        handle_chat("hi", {"groq": "fake-key"})


@patch("chat_core.litellm.completion")
@patch("chat_core.select_model")
@patch("chat_core.rate_limiter.is_available")
def test_rate_limited_choice_falls_back_to_next_model(mock_available, mock_select, mock_completion):
    mock_select.return_value = "groq/compound-beta"
    mock_available.side_effect = lambda entry: entry["id"] != "groq/compound-beta"
    resp_obj = MagicMock()
    resp_obj.choices[0].message.content = "fallback response"
    mock_completion.return_value = resp_obj

    result = handle_chat("hi", {"groq": "fake-key"})
    assert result["model_used"] == "groq/llama-3.3-70b-versatile"


@patch("chat_core.select_model")
@patch("chat_core.rate_limiter.is_available")
def test_all_models_rate_limited_raises(mock_available, mock_select):
    mock_select.return_value = "groq/compound-beta"
    mock_available.return_value = False

    with pytest.raises(AllModelsRateLimitedError):
        handle_chat("hi", {"groq": "fake-key"})


@patch("chat_core.litellm.completion")
@patch("chat_core.select_model")
@patch("chat_core.rate_limiter.is_available")
def test_rate_limited_choice_prefers_same_family_other_provider(mock_available, mock_select, mock_completion):
    mock_select.return_value = "openrouter/openai/gpt-oss-20b:free"
    mock_available.side_effect = lambda entry: entry["id"] != "openrouter/openai/gpt-oss-20b:free"
    resp_obj = MagicMock()
    resp_obj.choices[0].message.content = "fallback response"
    mock_completion.return_value = resp_obj

    result = handle_chat("hi", {"groq": "fake-groq-key", "openrouter": "fake-or-key"})
    assert result["model_used"] == "groq/openai/gpt-oss-20b"
