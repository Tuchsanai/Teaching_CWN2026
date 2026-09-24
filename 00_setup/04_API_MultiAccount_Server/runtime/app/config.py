"""Runtime settings, read once from environment variables (see .env.example)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _int(name: str, default: int, minimum: int = 1) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        raise RuntimeError(f"setting {name} must be an integer") from None
    if value < minimum:
        raise RuntimeError(f"setting {name} must be >= {minimum}")
    return value


def _list(name: str, default: str) -> tuple[str, ...]:
    raw = os.environ.get(name, default)
    return tuple(dict.fromkeys(x.strip() for x in raw.split(",") if x.strip()))


def _read_token() -> str:
    """Token comes from a mounted secret file; API_TOKEN env is a fallback for local runs/tests."""
    path = os.environ.get("API_TOKEN_FILE", "/data/secrets/api_token")
    try:
        token = Path(path).read_text(encoding="utf-8").strip()
    except OSError:
        token = ""
    return token or os.environ.get("API_TOKEN", "").strip()


@dataclass(frozen=True)
class Settings:
    api_token: str = field(repr=False)
    web_dir: Path
    accounts_base: Path
    launcher_dir: Path
    work_root: Path
    claude_accounts: tuple[str, ...]
    codex_accounts: tuple[str, ...]
    default_claude_account: str
    default_codex_account: str
    default_model: str
    default_effort: str
    max_body_bytes: int
    max_messages: int
    max_message_chars: int
    max_total_chars: int
    cli_timeout_seconds: int
    cli_cpu_seconds: int
    cli_max_output_bytes: int
    cli_max_file_bytes: int
    max_concurrent_calls: int
    queue_timeout_seconds: int

    @classmethod
    def from_env(cls) -> "Settings":
        timeout = _int("CLI_TIMEOUT_SECONDS", 240)
        return cls(
            api_token=_read_token(),
            web_dir=Path(os.environ.get("WEB_DIR", "/app/web")),
            accounts_base=Path(os.environ.get("AI_ACCOUNTS_BASE", "/data/accounts")),
            launcher_dir=Path(os.environ.get("LAUNCHER_DIR", "/usr/local/bin")),
            work_root=Path(os.environ.get("WORK_ROOT", "/tmp/chat-work")),
            claude_accounts=_list("CLAUDE_ACCOUNTS", "yolo1"),
            codex_accounts=_list("CODEX_ACCOUNTS", "cyolo1"),
            default_claude_account=os.environ.get("DEFAULT_CLAUDE_ACCOUNT", "yolo1").strip(),
            default_codex_account=os.environ.get("DEFAULT_CODEX_ACCOUNT", "cyolo1").strip(),
            default_model=os.environ.get("DEFAULT_MODEL", "fable").strip(),
            default_effort=os.environ.get("DEFAULT_REASONING_EFFORT", "medium").strip(),
            max_body_bytes=_int("MAX_BODY_BYTES", 262_144),
            max_messages=_int("MAX_MESSAGES", 100),
            max_message_chars=_int("MAX_MESSAGE_CHARS", 32_000),
            max_total_chars=_int("MAX_TOTAL_CHARS", 120_000),
            cli_timeout_seconds=timeout,
            cli_cpu_seconds=_int("CLI_CPU_SECONDS", timeout * 2),
            cli_max_output_bytes=_int("CLI_MAX_OUTPUT_BYTES", 4 * 1024 * 1024),
            cli_max_file_bytes=_int("CLI_MAX_FILE_BYTES", 256 * 1024 * 1024),
            max_concurrent_calls=_int("MAX_CONCURRENT_CALLS", 2),
            queue_timeout_seconds=_int("QUEUE_TIMEOUT_SECONDS", 30),
        )
