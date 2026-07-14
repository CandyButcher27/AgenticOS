from mcp.server.fastmcp import FastMCP

from chat_core import handle_chat, NoSupportedProviderError, AllModelsRateLimitedError, PromptTooLargeError

mcp = FastMCP("token-router")


@mcp.tool()
def delegate_task(prompt: str, keys: dict[str, str] | None = None, task_type: str | None = None) -> dict:
    """Delegate a task to the best available LLM, chosen from whichever provider keys are available.

    Args:
        prompt: The task/prompt to send to the model.
        keys: Optional provider API keys, e.g. {"groq": "..."}. Any provider not
            listed here falls back to the server's own .env keys, if configured.
        task_type: Optional hint (e.g. "code") to narrow model selection.

    Returns:
        {"model_used": <model id>, "content": <model response>}
    """
    try:
        return handle_chat(prompt, keys, task_type)
    except NoSupportedProviderError as e:
        return {"error": str(e)}
    except AllModelsRateLimitedError as e:
        return {"error": str(e)}
    except PromptTooLargeError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    mcp.run()
