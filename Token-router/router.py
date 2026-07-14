from litellm import completion
import os
from config import config

groq_model = config["groq"]["model"]

response = completion(
    model = groq_model,
    messages=[{"role": "user", "content": "What is the capital of France?"}]
)

print(response)