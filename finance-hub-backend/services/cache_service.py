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
    """Return the cached value for key, or None if missing/expired."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{_REDIS_URL}/get/{key}", headers=_HEADERS)
        data = resp.json()
        if data.get("result") is None:
            return None
        return json.loads(data["result"])


async def cache_set(key: str, value: Any, ttl_seconds: int = 3600) -> None:
    """Store value as JSON under key with a TTL."""
    serialized = json.dumps(value)
    async with httpx.AsyncClient() as client:
        await client.get(
            f"{_REDIS_URL}/set/{key}/{serialized}/EX/{ttl_seconds}",
            headers=_HEADERS,
        )


async def cache_delete(key: str) -> None:
    """Remove a cache key."""
    async with httpx.AsyncClient() as client:
        await client.get(f"{_REDIS_URL}/del/{key}", headers=_HEADERS)
