"""LLM text generation — backed by Groq Llama 3.3 70B."""
import logging
import os

from dotenv import load_dotenv
from fastapi import HTTPException
from groq import AsyncGroq

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

logger = logging.getLogger(__name__)

_client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"].strip().strip('"'))
_MODEL = "llama-3.3-70b-versatile"


async def llm_generate(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> str:
    """Generate a response via Groq. Raises HTTPException(503) on failure."""
    try:
        response = await _client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as exc:
        logger.error("LLM generation error: %s", exc)
        raise HTTPException(status_code=503, detail=f"LLM service unavailable: {exc}")
