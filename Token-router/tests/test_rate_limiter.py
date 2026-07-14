import pytest
import rate_limiter


@pytest.fixture(autouse=True)
def clear_state():
    rate_limiter._calls.clear()
    yield
    rate_limiter._calls.clear()


def test_no_limits_always_available():
    entry = {"id": "groq/compound-beta", "provider": "groq", "rate_limits": {"rpm": None, "rpd": None}}
    for _ in range(100):
        assert rate_limiter.is_available(entry)
        rate_limiter.record_call(entry)


def test_rpm_limit_blocks_after_threshold():
    entry = {"id": "groq/llama-3.3-70b-versatile", "provider": "groq", "rate_limits": {"rpm": 2, "rpd": None}}
    assert rate_limiter.is_available(entry)
    rate_limiter.record_call(entry)
    assert rate_limiter.is_available(entry)
    rate_limiter.record_call(entry)
    assert not rate_limiter.is_available(entry)


def test_openrouter_free_models_share_one_bucket():
    entry_a = {"id": "openrouter/tencent/hy3:free", "provider": "openrouter", "rate_limits": {"rpm": 1, "rpd": None}}
    entry_b = {"id": "openrouter/cohere/north-mini-code:free", "provider": "openrouter", "rate_limits": {"rpm": 1, "rpd": None}}
    assert rate_limiter.is_available(entry_a)
    rate_limiter.record_call(entry_a)
    assert not rate_limiter.is_available(entry_b)


def test_different_groq_models_have_independent_buckets():
    entry_a = {"id": "groq/compound-beta", "provider": "groq", "rate_limits": {"rpm": 1, "rpd": None}}
    entry_b = {"id": "groq/llama-3.3-70b-versatile", "provider": "groq", "rate_limits": {"rpm": 1, "rpd": None}}
    rate_limiter.record_call(entry_a)
    assert not rate_limiter.is_available(entry_a)
    assert rate_limiter.is_available(entry_b)
