from litellm import acompletion

from src.settings import MODEL_NAME, SYSTEM_MESSAGE


async def query_summary(text: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {"role": "user", "content": text},
    ]
    response = await acompletion(MODEL_NAME, messages, reasoning_effort="none")
    response_content = response["choices"][0]["message"]["content"]

    return response_content
