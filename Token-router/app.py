from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from chat_core import handle_chat, NoSupportedProviderError, AllModelsRateLimitedError

app = FastAPI()


class ChatRequest(BaseModel):
    prompt: str
    keys: dict[str, str]
    task_type: str | None = None


@app.post("/chat")
def chat(req: ChatRequest):
    try:
        return handle_chat(req.prompt, req.keys, req.task_type)
    except NoSupportedProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AllModelsRateLimitedError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
