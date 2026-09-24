"""Runtime settings, read once from environment variables.

The server fails closed: it refuses to start without an API token hash or with
a wildcard CORS origin.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

# Account names are wrapper names: yolo1..yolo5 (Claude), cyolo1..cyolo5 (Codex).
ACCOUNT_NAME_RE = {"claude": re.compile(r"^yolo[1-5]$"), "codex": re.compile(r"^cyolo[1-5]$")}
SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")


class ConfigError(RuntimeError):
    pass


def _int(name: str, default: int, lo: int, hi: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer") from exc
    if not lo <= value <= hi:
        raise ConfigError(f"{name} must be between {lo} and {hi}")
    return value


def _accounts(name: str, default: str, provider: str) -> tuple[str, ...]:
    items = [a.strip() for a in os.environ.get(name, default).split(",") if a.strip()]
    if not items:
        raise ConfigError(f"{name} must list at least one account")
    for a in items:
        if not ACCOUNT_NAME_RE[provider].match(a):
            raise ConfigError(f"{name}: invalid account name {a!r} "
                              f"(allowed: {'yolo1..yolo5' if provider == 'claude' else 'cyolo1..cyolo5'})")
    if len(set(items)) != len(items):
        raise ConfigError(f"{name}: duplicate account names")
    return tuple(items)


@dataclass(frozen=True)
class Settings:
    api_token_sha256: str
    cors_origins: tuple[str, ...]
    accounts: dict[str, tuple[str, ...]]  # provider -> account names (first = default)
    accounts_root: Path
    work_root: Path      # per-request cwd + TMPDIR live here
    app_home: Path       # fixed HOME for every CLI call (writable tmpfs in the container)
    wrapper_dir: Path    # holds the container-local yoloN / cyoloN wrappers
    claude_bin: str      # real CLIs, called only by the wrappers
    codex_bin: str
    codex_sandbox: str
    cli_timeout_s: int
    max_messages: int
    max_message_chars: int
    max_transcript_chars: int
    max_output_chars: int
    max_stdout_bytes: int
    max_body_bytes: int
    per_account_concurrency: int
    max_concurrency: int
    queue_wait_s: int

    def account_dir(self, provider: str, account: str) -> Path:
        return self.accounts_root / provider / account


# File inside each account dir whose *presence* (never content) is reported.
CREDENTIAL_FILES = {"claude": ".credentials.json", "codex": "auth.json"}


def load_settings() -> Settings:
    token_hash = os.environ.get("API_TOKEN_SHA256", "").strip().lower()
    if not SHA256_HEX_RE.match(token_hash):
        raise ConfigError(
            "API_TOKEN_SHA256 must be set to the hex SHA-256 of the API token "
            "(deploy/lab04.sh generates it)"
        )

    origins = tuple(
        o.strip().rstrip("/")
        for o in os.environ.get(
            "CORS_ORIGINS", "http://127.0.0.1:8005,http://localhost:8005"
        ).split(",")
        if o.strip()
    )
    for o in origins:
        if o == "*" or o == "null" or not re.match(r"^https?://[A-Za-z0-9.\-\[\]:]+$", o):
            raise ConfigError(f"CORS_ORIGINS: refusing origin {o!r} (explicit http(s) origins only)")

    codex_sandbox = os.environ.get("CODEX_SANDBOX", "read-only").strip()
    if codex_sandbox not in ("read-only", "workspace-write"):
        # danger-full-access is deliberately not allowed from config.
        raise ConfigError("CODEX_SANDBOX must be read-only or workspace-write")

    return Settings(
        api_token_sha256=token_hash,
        cors_origins=origins,
        accounts={
            "claude": _accounts("CLAUDE_ACCOUNTS", "yolo1", "claude"),
            "codex": _accounts("CODEX_ACCOUNTS", "cyolo1", "codex"),
        },
        accounts_root=Path(os.environ.get("ACCOUNTS_ROOT", "/data/accounts")),
        work_root=Path(os.environ.get("WORK_ROOT", "/tmp/lab04-work")),
        app_home=Path(os.environ.get("HOME") or "/home/app"),
        wrapper_dir=Path(os.environ.get("WRAPPER_DIR", "/opt/lab04/bin")),
        claude_bin=os.environ.get("CLAUDE_BIN", "claude"),
        codex_bin=os.environ.get("CODEX_BIN", "codex"),
        codex_sandbox=codex_sandbox,
        cli_timeout_s=_int("CLI_TIMEOUT_S", 300, 10, 900),
        max_messages=_int("MAX_MESSAGES", 40, 1, 200),
        max_message_chars=_int("MAX_MESSAGE_CHARS", 8000, 100, 100_000),
        max_transcript_chars=_int("MAX_TRANSCRIPT_CHARS", 48_000, 1000, 100_000),
        max_output_chars=_int("MAX_OUTPUT_CHARS", 24_000, 1000, 200_000),
        max_stdout_bytes=_int("MAX_STDOUT_BYTES", 1_048_576, 65_536, 8_388_608),
        max_body_bytes=_int("MAX_BODY_BYTES", 262_144, 4096, 2_097_152),
        per_account_concurrency=_int("PER_ACCOUNT_CONCURRENCY", 1, 1, 8),
        max_concurrency=_int("MAX_CONCURRENCY", 4, 1, 32),
        queue_wait_s=_int("QUEUE_WAIT_S", 3, 0, 60),
    )
