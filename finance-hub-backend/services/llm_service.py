"""LLM text generation via HF Inference API — rohan1324/phi3-mini-finance-merged."""
import asyncio
import logging
import os

from dotenv import load_dotenv
from fastapi import HTTPException
from huggingface_hub import InferenceClient

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

logger = logging.getLogger(__name__)

_MODEL_ID = "rohan1324/phi3-mini-finance-merged"
_client = InferenceClient(
    model=_MODEL_ID,
    token=os.environ.get("HUGGINGFACE_API_TOKEN", "").strip().strip('"'),
)


async def llm_generate(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> str:
    """Generate text via HF Inference API. Raises HTTPException(503) on failure."""
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: _client.text_generation(
                prompt,
                max_new_tokens=max_tokens,
                temperature=max(temperature, 0.01),
                do_sample=temperature > 0,
            ),
        )
        return response
    except Exception as exc:
        logger.error("HF Inference API error: %s", exc)
        raise HTTPException(status_code=503, detail=f"LLM service unavailable: {exc}")
