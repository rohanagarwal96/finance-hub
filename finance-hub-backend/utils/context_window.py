"""Sliding context window management for chat conversations."""
from __future__ import annotations

import tiktoken

_ENCODING = tiktoken.get_encoding("cl100k_base")
_MAX_TOKENS = 3000


def count_tokens(text: str) -> int:
    """Count tokens in a string using cl100k_base encoding."""
    return len(_ENCODING.encode(text))


def messages_token_count(messages: list[dict]) -> int:
    """Count total tokens across a list of {role, content} dicts."""
    return sum(count_tokens(m["content"]) for m in messages)


def trim_messages_to_window(
    messages: list[dict],
    summary: str = "",
) -> tuple[list[dict], str]:
    """Return messages trimmed to fit within _MAX_TOKENS.

    When the history exceeds the limit, the oldest messages are dropped
    and a summary string is returned to be prepended as context.
    The summary is passed in from a prior summarization call.
    Returns (trimmed_messages, existing_summary).
    """
    if messages_token_count(messages) <= _MAX_TOKENS:
        return messages, summary

    # Drop oldest messages until we're under the limit
    trimmed = list(messages)
    while trimmed and messages_token_count(trimmed) > _MAX_TOKENS:
        trimmed.pop(0)

    return trimmed, summary


def build_context_prompt(messages: list[dict], summary: str = "") -> str:
    """Build a prompt string from message history with optional summary prefix."""
    parts = []
    if summary:
        parts.append(f"[Earlier conversation summary: {summary}]\n")
    for m in messages:
        role = m["role"].capitalize()
        parts.append(f"{role}: {m['content']}")
    return "\n".join(parts)
