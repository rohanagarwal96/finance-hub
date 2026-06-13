"""Upstash Redis REST client for caching API responses."""
import json
import os
from typing import Any, Optional

import httpx
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

_REDIS_URL = os.environ["UPSTASH_REDIS_REST_URL"].strip().strip('"')
_REDIS_TOKEN = os.environ["UPSTASH_REDIS_REST_TOKEN"].strip().strip('"')
_HEADERS = {"Authorization": f"Bearer {_REDIS_TOKEN}"}


async def cache_get(key: str) -> Optional[Any]:
    """Return the cached value for key, or None if missing/expired/corrupt."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{_REDIS_URL}/get/{key}", headers=_HEADERS)
        data = resp.json()
        if data.get("result") is None:
            return None
        try:
            return json.loads(data["result"])
        except (json.JSONDecodeError, TypeError):
            return None


async def cache_set(key: str, value: Any, ttl_seconds: int = 3600) -> None:
    """Store value as JSON under key with a TTL."""
    serialized = json.dumps(value)
    # Use POST with a command array so arbitrary JSON is sent in the body,
    # not embedded in the URL path where special characters corrupt the value.
    async with httpx.AsyncClient() as client:
        await client.post(
            _REDIS_URL,
            headers={**_HEADERS, "Content-Type": "application/json"},
            content=json.dumps(["SET", key, serialized, "EX", str(ttl_seconds)]),
        )


async def cache_delete(key: str) -> None:
    """Remove a cache key."""
    async with httpx.AsyncClient() as client:
        await client.get(f"{_REDIS_URL}/del/{key}", headers=_HEADERS)
