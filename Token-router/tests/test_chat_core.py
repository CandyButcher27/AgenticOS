import pytest
from unittest.mock import patch, MagicMock
import rate_limiter
from chat_core import handle_chat, NoSupportedProviderError, AllModelsRateLimitedError, PromptTooLargeError


@pytest.fixture(autouse=True)
def clear_rate_limiter():
    rate_limiter._calls.clear()
    yield
    rate_limiter._calls.clear()


@patch("chat_core.SERVER_KEYS", {})
def test_no_keys_and_no_server_keys_raises_no_supported_provider():
    with pytest.raises(NoSupportedProviderError):
        handle_chat("hi", {})


@patch("chat_core.SERVER_KEYS", {})
def test_unmatched_provider_and_no_server_keys_raises_no_supported_provider():
    with pytest.raises(NoSupportedProviderError):
        handle_chat("hi", {"unknown": "x"})


@patch("chat_core.litellm.completion")
@patch("chat_core.select_model")
@patch("chat_core.SERVER_KEYS", {"groq": "server-side-key"})
def test_missing_caller_keys_fall_back_to_server_keys(mock_select, mock_completion):
    mock_select.return_value = "groq/compound-beta"
    resp_obj = MagicMock()
    resp_obj.choices[0].message.content = "Paris."
    mock_completion.return_value = resp_obj

    result = handle_chat("capital of France?")
    assert result == {"model_used": "groq/compound-beta", "content": "Paris."}
    assert mock_completion.call_args.kwargs["api_key"] == "server-side-key"


@patch("chat_core.litellm.completion")
@patch("chat_core.select_model")
@patch("chat_core.SERVER_KEYS", {"groq": "server-side-key"})
def test_caller_supplied_key_overrides_server_key(mock_select, mock_completion):
    mock_select.return_value = "groq/compound-beta"
    resp_obj = MagicMock()
    resp_obj.choices[0].message.content = "Paris."
    mock_completion.return_value = resp_obj

    handle_chat("capital of France?", {"groq": "caller-key"})
    assert mock_completion.call_args.kwargs["api_key"] == "caller-key"


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
    # Simulate: available during pre-filter, but select_model's choice becomes rate-limited (race)
    models_seen = {}

    def mock_available_impl(entry):
        eid = entry["id"]
        if eid not in models_seen:
            models_seen[eid] = 0
        models_seen[eid] += 1

        # Compound-beta: available on first call (pre-filter), unavailable on second+ (post-pick, race)
        if eid == "groq/compound-beta":
            return models_seen[eid] == 1
        return True

    mock_available.side_effect = mock_available_impl
    mock_select.return_value = "groq/compound-beta"
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
    # Simulate: available during pre-filter, but select_model's choice becomes rate-limited (race)
    models_seen = {}

    def mock_available_impl(entry):
        eid = entry["id"]
        if eid not in models_seen:
            models_seen[eid] = 0
        models_seen[eid] += 1

        # openrouter gpt-oss-20b: available on first call (pre-filter), unavailable on second+ (post-pick, race)
        if eid == "openrouter/openai/gpt-oss-20b:free":
            return models_seen[eid] == 1
        return True

    mock_available.side_effect = mock_available_impl
    mock_select.return_value = "openrouter/openai/gpt-oss-20b:free"
    resp_obj = MagicMock()
    resp_obj.choices[0].message.content = "fallback response"
    mock_completion.return_value = resp_obj

    result = handle_chat("hi", {"groq": "fake-groq-key", "openrouter": "fake-or-key"})
    assert result["model_used"] == "groq/openai/gpt-oss-20b"


@patch("chat_core.litellm.completion")
@patch("chat_core.litellm.token_counter")
@patch("chat_core.select_model")
@patch("chat_core.SERVER_KEYS", {"groq": "server-key"})
def test_model_exceeding_tpm_excluded_from_router_candidates(mock_select, mock_token_counter, mock_completion):
    # All groq models with real tpm caps have tpm <= 30000.
    # Make every prompt "cost" 100000 tokens, so all tpm-capped models are excluded,
    # while groq/compound-beta (tpm: null) still fits.
    mock_token_counter.return_value = 100000
    mock_select.return_value = "groq/compound-beta"
    resp_obj = MagicMock()
    resp_obj.choices[0].message.content = "ok"
    mock_completion.return_value = resp_obj

    result = handle_chat("hi", {"groq": "fake-key"})
    assert result["model_used"] == "groq/compound-beta"
    # select_model should only have been offered compound-beta (tpm: null), not
    # any tpm-capped models (excluded by the 100000-token estimate)
    offered_ids = {e["id"] for e in mock_select.call_args.args[1]}
    assert offered_ids == {"groq/compound-beta"}


@patch("chat_core.litellm.token_counter")
@patch("chat_core.SERVER_KEYS", {"groq": "server-key"})
def test_all_candidates_exceed_tpm_raises_prompt_too_large(mock_token_counter):
    # groq/llama-3.3-70b-versatile: tpm 12000. Force every model's estimate over its tpm cap
    # by returning a huge number, but keep groq/compound-beta's tpm null case excluded too
    # by scoping keys to a provider whose only tpm-capped entry we force to fail.
    mock_token_counter.return_value = 999999
    # Use gemini, whose only catalog entry (gemini-2.5-flash) has tpm: null (always fits) --
    # so instead scope to a request where the only matching entries all have a real tpm cap.
    # groq has both null-tpm (compound-beta) and real-tpm entries, so force task_type to a
    # tag that only matches tpm-capped entries: use qwen3-32b via task_type "reasoning" is
    # too broad (also matches compound-beta's... no, compound-beta has no reasoning tag).
    with pytest.raises(PromptTooLargeError):
        handle_chat("hi", {"groq": "fake-key"}, task_type="reasoning")


@patch("chat_core.litellm.completion")
@patch("chat_core.select_model")
@patch("chat_core.rate_limiter.is_available")
def test_prefilter_excludes_rate_limited_before_router_sees_them(mock_available, mock_select, mock_completion):
    mock_available.side_effect = lambda entry: entry["id"] != "groq/compound-beta"
    mock_select.return_value = "groq/llama-3.3-70b-versatile"
    resp_obj = MagicMock()
    resp_obj.choices[0].message.content = "ok"
    mock_completion.return_value = resp_obj

    handle_chat("hi", {"groq": "fake-key"})
    offered_ids = {e["id"] for e in mock_select.call_args.args[1]}
    assert "groq/compound-beta" not in offered_ids


@patch("chat_core.rate_limiter.is_available")
def test_all_candidates_rate_limited_raises_all_models_rate_limited_not_prompt_too_large(mock_available):
    mock_available.return_value = False
    with pytest.raises(AllModelsRateLimitedError):
        handle_chat("hi", {"groq": "fake-key"})
