"""Run one Claude Code / Codex CLI call per HTTP request, safely.

Rules enforced here:
  * argv list only (asyncio.create_subprocess_exec), never a shell string.
  * The prompt goes through stdin, not argv, so it never shows up in `ps`
    and is not limited by the per-argument size cap.
  * Every call goes through the container-local wrapper yoloN / cyoloN, which
    selects the copied account dir (CLAUDE_CONFIG_DIR / CODEX_HOME) and adds
    the fixed no-tools / read-only flags.
  * Each request gets its own empty cwd and TMPDIR, deleted afterwards. HOME is
    the app user's fixed home. The CLI sees a minimal environment, not the server's.
  * Wall-clock timeout; the whole process group is killed on timeout/cancel.
  * stdout/stderr are read with a byte cap. stderr is used only to classify
    the failure and is never logged or returned (Codex echoes the prompt there).
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
import shutil
import signal
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from .config import Settings

STDERR_CAP = 65_536


class CLIError(Exception):
    """A failure that is safe to show to the client (fixed text, no CLI output)."""

    def __init__(self, status: int, type_: str, message: str):
        super().__init__(message)
        self.status = status
        self.type = type_
        self.message = message


def _err(kind: str, timeout_s: int = 0) -> CLIError:
    table = {
        "auth": (502, "upstream_auth_error",
                 "The selected account is not authenticated inside the API container "
                 "(credential copy missing, expired or revoked). Re-transfer this account's credentials."),
        "rate_limit": (429, "upstream_rate_limited",
                       "The selected account reported a usage or rate limit. Wait, or switch account."),
        "model": (400, "upstream_model_error",
                  "The CLI rejected this model or reasoning effort for the selected account."),
        "timeout": (504, "cli_timeout", f"The CLI did not finish within {timeout_s} s."),
        "too_large": (502, "cli_output_too_large", "The CLI produced more output than the server allows."),
        "empty": (502, "cli_empty_output", "The CLI finished but returned no reply text."),
        "missing": (500, "cli_not_installed", "The CLI binary for this provider is not available in the container."),
        "failed": (502, "upstream_error",
                   "The CLI exited with an error. Details are withheld to protect prompts and credentials."),
    }
    status, type_, msg = table[kind]
    return CLIError(status, type_, msg)


_AUTH = ("not logged in", "/login", "401", "unauthorized", "invalid api key", "authentication",
         "token has expired", "token expired", "refresh token", "invalid_grant", "sign in again")
_RATE = ("429", "rate limit", "rate_limit", "usage limit", "too many requests", "quota", "limit reached")
_MODEL = ("model not found", "unknown model", "invalid model", "model is not supported",
          "not supported for this model", "unsupported value", "does not exist or you do not have access",
          "model_not_found", "reasoning.effort", "reasoning_effort")


def classify(text: str) -> str:
    t = text.lower()
    if any(p in t for p in _AUTH):
        return "auth"
    if any(p in t for p in _RATE):
        return "rate_limit"
    if any(p in t for p in _MODEL):
        return "model"
    return "failed"


def _codex_error_lines(stderr: str) -> str:
    # Codex prints the user's prompt to stderr as part of its session header.
    # Only look at its own error lines so user text cannot steer classification.
    return "\n".join(
        line for line in stderr.splitlines()
        if line.startswith("ERROR") or " ERROR " in line[:40]
    )


@dataclass
class CLIResult:
    text: str
    truncated: bool
    duration_ms: int


@dataclass
class _Proc:
    returncode: int
    stdout: bytes
    stderr: str


async def _read_capped(stream: asyncio.StreamReader, cap: int, on_overflow=None) -> tuple[bytes, bool]:
    buf = bytearray()
    overflow = False
    while True:
        chunk = await stream.read(65_536)
        if not chunk:
            break
        if len(buf) + len(chunk) > cap:
            buf.extend(chunk[: cap - len(buf)])
            if not overflow:
                overflow = True
                if on_overflow:
                    on_overflow()
            continue  # keep draining so the child never blocks on a full pipe
        buf.extend(chunk)
    return bytes(buf), overflow


def _kill_group(proc: asyncio.subprocess.Process) -> None:
    if proc.returncode is None:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(proc.pid, signal.SIGKILL)


async def _run(argv: list[str], env: dict[str, str], cwd: Path, stdin: bytes,
               timeout_s: int, stdout_cap: int | None) -> _Proc:
    try:
        proc = await asyncio.create_subprocess_exec(
            *argv,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE if stdout_cap else asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(cwd),
            env=env,
            start_new_session=True,  # own process group -> killpg reaches CLI children too
        )
    except FileNotFoundError:
        raise _err("missing") from None

    too_large = False

    def overflow() -> None:
        nonlocal too_large
        too_large = True
        _kill_group(proc)

    async def feed() -> None:
        assert proc.stdin is not None
        with contextlib.suppress(BrokenPipeError, ConnectionResetError):
            proc.stdin.write(stdin)
            await proc.stdin.drain()
        proc.stdin.close()

    async def collect() -> tuple[bytes, bytes]:
        tasks = [asyncio.create_task(feed())]
        err_t = asyncio.create_task(_read_capped(proc.stderr, STDERR_CAP))
        out_t = (asyncio.create_task(_read_capped(proc.stdout, stdout_cap, overflow))
                 if stdout_cap else None)
        await asyncio.gather(*tasks)
        err, _ = await err_t
        out = (await out_t)[0] if out_t else b""
        await proc.wait()
        return out, err

    try:
        out, err = await asyncio.wait_for(collect(), timeout=timeout_s)
    except asyncio.TimeoutError:
        _kill_group(proc)
        raise _err("timeout", timeout_s) from None
    finally:
        _kill_group(proc)
        with contextlib.suppress(Exception):
            await asyncio.wait_for(proc.wait(), timeout=5)

    if too_large:
        raise _err("too_large")
    return _Proc(proc.returncode or 0, out, err.decode("utf-8", "replace"))


def cli_env(s: Settings, tmpdir: Path) -> dict[str, str]:
    """Minimal environment for a wrapper call. HOME stays the app user's home;
    only TMPDIR (and cwd) are per request. The wrapper picks the account dir."""
    allowed = ",".join(a for names in s.accounts.values() for a in names)
    return {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": str(s.app_home),
        "TMPDIR": str(tmpdir),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "NO_COLOR": "1",
        "TERM": "dumb",
        "LAB04_ACCOUNTS_ROOT": str(s.accounts_root),
        "LAB04_ALLOWED_ACCOUNTS": allowed,
        "LAB04_CLAUDE_BIN": s.claude_bin,
        "LAB04_CODEX_BIN": s.codex_bin,
        "LAB04_CODEX_SANDBOX": s.codex_sandbox,
    }


def wrapper_argv(s: Settings, account: str, model: str, effort: str,
                 out_file: Path | None = None) -> list[str]:
    """argv for the container-local yoloN / cyoloN wrapper (api/wrappers/lab04-cli).
    The wrapper adds the fixed safety flags; see that file for the exact CLI flags."""
    argv = [str(s.wrapper_dir / account), "--model", model, "--effort", effort]
    if out_file is not None:
        argv += ["--output-last-message", str(out_file)]
    return argv


async def run_chat(s: Settings, provider: str, model: str, effort: str, account: str,
                   prompt: str) -> CLIResult:
    s.work_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    req = Path(tempfile.mkdtemp(prefix="req-", dir=s.work_root))
    started = time.monotonic()
    try:
        for sub in ("cwd", "tmp"):
            (req / sub).mkdir(mode=0o700)
        env = cli_env(s, req / "tmp")
        data = prompt.encode("utf-8")

        if provider == "claude":
            p = await _run(wrapper_argv(s, account, model, effort), env, req / "cwd", data,
                           s.cli_timeout_s, s.max_stdout_bytes)
            try:
                doc = json.loads(p.stdout.decode("utf-8", "replace"))
            except ValueError:
                raise _err(classify(p.stderr) if p.returncode else "failed") from None
            result = doc.get("result") if isinstance(doc, dict) else None
            if not isinstance(result, str):
                raise _err("failed")
            if doc.get("is_error") or doc.get("subtype") != "success" or p.returncode:
                raise _err(classify(result + "\n" + p.stderr))
            text = result
        else:
            out_file = req / "tmp" / "last-message.txt"
            p = await _run(wrapper_argv(s, account, model, effort, out_file), env, req / "cwd",
                           data, s.cli_timeout_s, None)
            if p.returncode:
                raise _err(classify(_codex_error_lines(p.stderr)))
            if not out_file.is_file():
                raise _err("empty")
            if out_file.stat().st_size > s.max_stdout_bytes:
                raise _err("too_large")
            text = out_file.read_text("utf-8", "replace")

        text = text.strip()
        if not text:
            raise _err("empty")
        truncated = len(text) > s.max_output_chars
        if truncated:
            text = text[: s.max_output_chars]
        return CLIResult(text, truncated, int((time.monotonic() - started) * 1000))
    finally:
        shutil.rmtree(req, ignore_errors=True)


async def cli_version(s: Settings, account: str) -> str | None:
    """`<wrapper> --version` for /health: proves the wrapper and the CLI behind it run.
    Says nothing about login state."""
    s.work_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    d = Path(tempfile.mkdtemp(prefix="ver-", dir=s.work_root))
    try:
        p = await _run([str(s.wrapper_dir / account), "--version"], cli_env(s, d), d, b"", 30, 4096)
    except CLIError:
        return None
    finally:
        shutil.rmtree(d, ignore_errors=True)
    if p.returncode:
        return None
    line = p.stdout.decode("utf-8", "replace").strip().splitlines()
    return line[0][:80] if line else None
