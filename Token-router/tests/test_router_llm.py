from unittest.mock import patch, MagicMock
from router_llm import select_model

CATALOG = [
    {"id": "groq/compound-beta", "provider": "groq", "tags": ["fast"], "description": "x"},
    {"id": "groq/llama-3.3-70b-versatile", "provider": "groq", "tags": ["reasoning"], "description": "y"},
]


def _mock_response(content: str):
    resp = MagicMock()
    resp.choices[0].message.content = content
    return resp


@patch("router_llm.litellm.completion")
def test_valid_model_id_parsed(mock_completion):
    mock_completion.return_value = _mock_response("groq/llama-3.3-70b-versatile")
    assert select_model("explain recursion", CATALOG, "fake-key") == "groq/llama-3.3-70b-versatile"


@patch("router_llm.litellm.completion")
def test_hallucinated_id_falls_back(mock_completion):
    mock_completion.return_value = _mock_response("gpt-5-imaginary")
    assert select_model("hi", CATALOG, "fake-key") == CATALOG[0]["id"]


@patch("router_llm.litellm.completion")
def test_completion_error_falls_back(mock_completion):
    mock_completion.side_effect = Exception("network error")
    assert select_model("hi", CATALOG, "fake-key") == CATALOG[0]["id"]
