import os


def call_llm(prompt: str) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return f"[STUB OUTPUT — no ANTHROPIC_API_KEY set]\nPrompt was:\n{prompt}"

    import anthropic

    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text
