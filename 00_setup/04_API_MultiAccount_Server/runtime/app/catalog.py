"""Which provider/model/effort/account combinations are allowed."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .config import Settings

FIVE = ("low", "medium", "high", "xhigh", "max")
SIX = ("none",) + FIVE


@dataclass(frozen=True)
class ModelSpec:
    id: str
    provider: str
    owned_by: str
    efforts: tuple[str, ...]


MODELS: dict[str, ModelSpec] = {
    m.id: m
    for m in (
        ModelSpec("fable", "claude", "anthropic", FIVE),
        ModelSpec("opus", "claude", "anthropic", FIVE),
        ModelSpec("gpt-6-astra", "codex", "openai", FIVE),
        ModelSpec("gpt-6-sol", "codex", "openai", SIX),
        ModelSpec("gpt-6-luna", "codex", "openai", SIX),
    )
}

PROVIDERS = ("claude", "codex")
# Account names are tied to one provider: yoloN is always Claude, cyoloN is always Codex.
ACCOUNT_PATTERN = {"claude": re.compile(r"yolo[1-5]"), "codex": re.compile(r"cyolo[1-5]")}
# Login file each CLI needs inside the account folder; its presence means "ready".
CREDENTIAL_FILE = {"claude": ".credentials.json", "codex": "auth.json"}
ACCOUNT_SUBDIR = {"claude": ".Claude", "codex": ".Codex"}


class CatalogError(ValueError):
    """Rejected combination; message is safe to show to the client."""


def provider_of_account(name: str) -> str | None:
    for provider, pattern in ACCOUNT_PATTERN.items():
        if pattern.fullmatch(name):
            return provider
    return None


def account_dir(settings: Settings, provider: str, name: str) -> Path:
    return settings.accounts_base / ACCOUNT_SUBDIR[provider] / name


def account_ready(settings: Settings, provider: str, name: str) -> bool:
    try:
        return (account_dir(settings, provider, name) / CREDENTIAL_FILE[provider]).stat().st_size > 0
    except OSError:
        return False


def enabled_accounts(settings: Settings, provider: str) -> tuple[str, ...]:
    configured = settings.claude_accounts if provider == "claude" else settings.codex_accounts
    # Silently drop names that belong to the other provider or are malformed.
    return tuple(a for a in configured if ACCOUNT_PATTERN[provider].fullmatch(a))


def default_account(settings: Settings, provider: str) -> str:
    return settings.default_claude_account if provider == "claude" else settings.default_codex_account


@dataclass(frozen=True)
class Selection:
    provider: str
    model: ModelSpec
    effort: str
    account: str


def resolve(
    settings: Settings,
    model: str | None,
    effort: str | None,
    account: str | None,
    provider: str | None,
) -> Selection:
    model_id = (model or settings.default_model).strip()
    spec = MODELS.get(model_id)
    if spec is None:
        raise CatalogError(f"unknown model '{model_id}'. Supported models: {', '.join(MODELS)}")

    if provider is not None:
        provider = provider.strip().lower()
        if provider not in PROVIDERS:
            raise CatalogError(f"unknown provider '{provider}'. Supported providers: claude, codex")
        if provider != spec.provider:
            raise CatalogError(f"model '{spec.id}' belongs to provider '{spec.provider}', not '{provider}'")

    level = (effort or settings.default_effort).strip().lower()
    if level not in spec.efforts:
        raise CatalogError(
            f"reasoning_effort '{level}' is not supported by model '{spec.id}'. "
            f"Allowed: {', '.join(spec.efforts)}"
        )

    name = (account or default_account(settings, spec.provider)).strip()
    owner = provider_of_account(name)
    if owner is None:
        raise CatalogError(f"unknown account '{name}'")
    if owner != spec.provider:
        raise CatalogError(
            f"account '{name}' is a {owner} account and cannot be used with {spec.provider} model '{spec.id}'"
        )
    if name not in enabled_accounts(settings, spec.provider):
        raise CatalogError(f"account '{name}' is not enabled on this server")
    if not account_ready(settings, spec.provider, name):
        raise CatalogError(f"account '{name}' has no login data on this server yet; run the deploy sync first")

    return Selection(spec.provider, spec, level, name)


def models_payload(settings: Settings) -> dict:
    accounts = {}
    for provider in PROVIDERS:
        default = default_account(settings, provider)
        accounts[provider] = [
            {"name": a, "default": a == default, "ready": account_ready(settings, provider, a)}
            for a in enabled_accounts(settings, provider)
        ]
    data = []
    for spec in MODELS.values():
        ready = [a["name"] for a in accounts[spec.provider] if a["ready"]]
        default_effort = settings.default_effort if settings.default_effort in spec.efforts else "medium"
        data.append(
            {
                "id": spec.id,
                "object": "model",
                "owned_by": spec.owned_by,
                "provider": spec.provider,
                "reasoning_efforts": list(spec.efforts),
                "default_reasoning_effort": default_effort,
                "accounts": ready,
                "default_account": default_account(settings, spec.provider),
                "available": bool(ready),
            }
        )
    default_model = settings.default_model if settings.default_model in MODELS else "fable"
    limits = {
        "max_messages": settings.max_messages,
        "max_message_chars": settings.max_message_chars,
        "max_total_chars": settings.max_total_chars,
        "max_body_bytes": settings.max_body_bytes,
        "timeout_seconds": settings.cli_timeout_seconds,
    }
    return {"object": "list", "data": data, "accounts": accounts, "default_model": default_model,
            "limits": limits}
