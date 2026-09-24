"""Allowed providers, models and reasoning-effort levels.

This is the single source of truth for what the API accepts. Anything not
listed here is rejected with HTTP 400 before any CLI is started.

Effort levels come from LAB 003 (verified by running every cell):
  * Claude Code `--effort` accepts low, medium, high, xhigh, max (claude --help).
  * Codex `-c model_reasoning_effort=...`: gpt-6-astra rejects `none`;
    gpt-6-sol / gpt-6-luna accept `none`; `minimal` failed on all three,
    so it is intentionally NOT offered.
"""

from __future__ import annotations

from dataclasses import dataclass

FIVE_LEVELS: tuple[str, ...] = ("low", "medium", "high", "xhigh", "max")


@dataclass(frozen=True)
class ModelSpec:
    id: str
    provider: str  # "claude" | "codex"
    label: str
    efforts: tuple[str, ...]
    default_effort: str = "medium"


MODELS: dict[str, ModelSpec] = {
    m.id: m
    for m in (
        ModelSpec("fable", "claude", "Claude Fable", FIVE_LEVELS),
        ModelSpec("opus", "claude", "Claude Opus", FIVE_LEVELS),
        ModelSpec("gpt-6-astra", "codex", "Codex Astra", FIVE_LEVELS),
        ModelSpec("gpt-6-sol", "codex", "Codex Sol", ("none",) + FIVE_LEVELS),
        ModelSpec("gpt-6-luna", "codex", "Codex Luna", ("none",) + FIVE_LEVELS),
    )
}

PROVIDERS: dict[str, str] = {
    "claude": "Claude Code CLI (claude -p)",
    "codex": "Codex CLI (codex exec)",
}

# Request fields this API understands. Everything else is rejected, so a
# client can never believe an option (e.g. max_completion_tokens) took effect.
SUPPORTED_FIELDS: frozenset[str] = frozenset(
    {"model", "messages", "reasoning_effort", "account", "provider", "stream"}
)

# Common OpenAI-style fields that clients often send. They get a specific
# "not supported by this CLI-backed API" message instead of a generic one.
KNOWN_UNSUPPORTED_FIELDS: frozenset[str] = frozenset(
    {
        "max_tokens",
        "max_completion_tokens",
        "temperature",
        "top_p",
        "n",
        "stop",
        "seed",
        "presence_penalty",
        "frequency_penalty",
        "logit_bias",
        "logprobs",
        "top_logprobs",
        "tools",
        "tool_choice",
        "functions",
        "function_call",
        "response_format",
        "user",
        "stream_options",
        "parallel_tool_calls",
        "reasoning",
        "metadata",
        "store",
        "modalities",
        "audio",
        "prediction",
        "service_tier",
    }
)
