from catalog import filter_catalog

CATALOG = [
    {"id": "groq/compound-beta", "provider": "groq", "tags": ["fast"], "description": "x"},
    {"id": "gemini/gemini-1.5-flash", "provider": "gemini", "tags": ["cheap"], "description": "y"},
]


def test_filter_returns_matching_provider():
    result = filter_catalog(CATALOG, {"groq"})
    assert result == [CATALOG[0]]


def test_filter_empty_providers_returns_empty():
    assert filter_catalog(CATALOG, set()) == []


def test_filter_no_match_returns_empty():
    assert filter_catalog(CATALOG, {"openrouter"}) == []
