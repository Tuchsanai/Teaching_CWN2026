"""Run one text-only chat turn through the yoloN / cyoloN launcher inside this container."""

from __future__ import annotations

import asyncio
import json
import os
import resource
import shutil
import signal
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .catalog import Selection
from .config import Settings
from .transcript import SYSTEM_PROMPT

CODEX_INSTRUCTIONS_FILE = Path(__file__).parent / "prompts" / "codex_instructions.md"

# Built-in Codex features that give the model tools (shell, files, browser, images, agents...).
# Every name was checked against `codex features list` of the installed version, and the
# command is run with --strict-config so a renamed key fails loudly instead of being ignored.
CODEX_DISABLED_FEATURES = (
    "shell_tool", "unified_exec", "shell_snapshot", "code_mode_host", "view_image",
    "image_generation", "browser_use", "browser_use_external", "in_app_browser",
    "computer_use", "apps", "plugins", "remote_plugin", "multi_agent", "goals", "hooks",
    "sleep_tool", "skill_search", "tool_suggest", "workspace_dependencies",
    "skill_mcp_dependency_install",
)

AUTH_HINTS = ("not logged in", "/login", "unauthorized", "401", "invalid_grant", "authentication",
              "refresh token", "token expired", "login again", "please log in")
RATE_HINTS = ("rate limit", "rate_limit", "429", "usage limit", "limit reached", "quota", "overloaded")


@dataclass
class CliResult:
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0


class CliError(Exception):
    """Failure that is safe to report; `detail` is for server logs only and never contains content."""

    def __init__(self, status: int, code: str, message: str, detail: str = ""):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message
        self.detail = detail


def _classify(text: str, fallback_detail: str) -> CliError:
    low = text.lower()
    if any(h in low for h in AUTH_HINTS):
        return CliError(503, "account_auth_failed",
                        "The selected account is not logged in or its login expired. "
                        "Re-sync the login data from devtools and try again.", fallback_detail)
    if any(h in low for h in RATE_HINTS):
        return CliError(429, "upstream_rate_limited",
                        "The selected account is rate limited or out of quota. Try again later "
                        "or pick another account.", fallback_detail)
    return CliError(502, "model_call_failed", "The model did not return an answer. Try again.",
                    fallback_detail)


def claude_command(settings: Settings, sel: Selection) -> list[str]:
    return [
        str(settings.launcher_dir / sel.account), "-p",
        "--output-format", "json",
        "--model", sel.model.id,
        "--effort", sel.effort,
        "--tools", "",                       # no built-in tools at all (Bash, Edit, Read, Web...)
        "--strict-mcp-config",               # no MCP servers (none are passed)
        "--disable-slash-commands",          # no skills
        "--setting-sources", "",             # ignore user/project settings (hooks, allow-lists)
        "--safe-mode",                       # no plugins, hooks, CLAUDE.md, custom agents
        "--permission-mode", "dontAsk",      # anything not pre-approved is denied
        "--permission-prompts", "none",
        "--no-session-persistence",
        "--system-prompt", SYSTEM_PROMPT,
    ]


def codex_command(settings: Settings, sel: Selection, out_file: Path) -> list[str]:
    cmd = [
        str(settings.launcher_dir / sel.account), "exec",
        "--strict-config", "--ignore-user-config", "--ignore-rules",
        "--ephemeral", "--skip-git-repo-check",
        "--sandbox", "read-only",
        "--color", "never",
        "-m", sel.model.id,
        "-c", f'model_reasoning_effort="{sel.effort}"',
        "-c", 'cli_auth_credentials_store="file"',
        "-c", f'model_instructions_file="{CODEX_INSTRUCTIONS_FILE}"',
        "-c", 'web_search="disabled"',
        "-c", "project_doc_max_bytes=0",
        "-c", 'history.persistence="none"',
    ]
    for feature in CODEX_DISABLED_FEATURES:
        cmd += ["--disable", feature]
    return cmd + ["--output-last-message", str(out_file), "-"]


def _limits(settings: Settings):
    def apply() -> None:
        resource.setrlimit(resource.RLIMIT_CPU, (settings.cli_cpu_seconds, settings.cli_cpu_seconds))
        resource.setrlimit(resource.RLIMIT_FSIZE, (settings.cli_max_file_bytes, settings.cli_max_file_bytes))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        resource.setrlimit(resource.RLIMIT_NOFILE, (1024, 1024))
    return apply


async def _read_capped(stream: asyncio.StreamReader, cap: int) -> bytes:
    buf = bytearray()
    while chunk := await stream.read(65536):
        buf += chunk
        if len(buf) > cap:
            raise CliError(502, "model_output_too_large", "The model answer was too large.", "output cap")
    return bytes(buf)


class Runner:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._slots = asyncio.Semaphore(settings.max_concurrent_calls)

    def _env(self, workdir: Path) -> dict[str, str]:
        env = {
            "PATH": "/usr/local/bin:/usr/bin:/bin",
            "HOME": str(workdir),
            "LANG": "C.UTF-8",
            "NO_COLOR": "1",
            "AI_ACCOUNTS_BASE": str(self.settings.accounts_base),
            "DISABLE_AUTOUPDATER": "1",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        }
        for name in ("CLAUDE_BIN", "CODEX_BIN"):  # only used to point tests at fake CLIs
            if os.environ.get(name):
                env[name] = os.environ[name]
        return env

    async def run(self, sel: Selection, prompt: str) -> CliResult:
        try:
            await asyncio.wait_for(self._slots.acquire(), timeout=self.settings.queue_timeout_seconds)
        except asyncio.TimeoutError:
            raise CliError(429, "server_busy", "The server is busy with other requests. Try again shortly.",
                           "queue timeout") from None
        try:
            return await self._run(sel, prompt)
        finally:
            self._slots.release()

    async def _run(self, sel: Selection, prompt: str) -> CliResult:
        self.settings.work_root.mkdir(parents=True, exist_ok=True, mode=0o700)
        workdir = Path(tempfile.mkdtemp(prefix="call-", dir=self.settings.work_root))
        out_file = workdir / "answer.txt"
        if sel.provider == "claude":
            cmd = claude_command(self.settings, sel)
        else:
            cmd = codex_command(self.settings, sel, out_file)
        try:
            code, stdout, stderr = await self._exec(cmd, prompt, workdir)
            if sel.provider == "claude":
                return self._parse_claude(code, stdout, stderr)
            answer = out_file.read_text(encoding="utf-8", errors="replace").strip() if out_file.exists() else ""
            if code == 0 and answer:
                return CliResult(answer)
            raise _classify(stderr.decode("utf-8", "replace"), f"codex exit={code} answer_len={len(answer)}")
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    async def _exec(self, cmd: list[str], prompt: str, workdir: Path) -> tuple[int, bytes, bytes]:
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, cwd=workdir, env=self._env(workdir),
                stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE, start_new_session=True,
                preexec_fn=_limits(self.settings),
            )
        except OSError as exc:
            raise CliError(503, "cli_unavailable", "The model CLI is not available on this server.",
                           f"spawn failed: {type(exc).__name__}") from None

        async def talk() -> tuple[bytes, bytes]:
            cap = self.settings.cli_max_output_bytes
            readers = [asyncio.create_task(_read_capped(proc.stdout, cap)),
                       asyncio.create_task(_read_capped(proc.stderr, cap))]
            try:
                try:
                    proc.stdin.write(prompt.encode("utf-8"))
                    await proc.stdin.drain()
                except (BrokenPipeError, ConnectionResetError):
                    pass
                finally:
                    proc.stdin.close()
                out, err = await asyncio.gather(*readers)
                await proc.wait()
                return out, err
            finally:
                for task in readers:  # stop readers before _reap drains the same pipes
                    task.cancel()
                await asyncio.gather(*readers, return_exceptions=True)

        try:
            stdout, stderr = await asyncio.wait_for(talk(), timeout=self.settings.cli_timeout_seconds)
        except asyncio.TimeoutError:
            await self._reap(proc)
            raise CliError(504, "model_timeout",
                           f"The model did not answer within {self.settings.cli_timeout_seconds} seconds.",
                           "timeout") from None
        except BaseException:
            await asyncio.shield(self._reap(proc))
            raise
        return proc.returncode, stdout, stderr

    @staticmethod
    async def _reap(proc: asyncio.subprocess.Process) -> None:
        """Kill the whole process group, then drain the pipes: asyncio only reports the exit
        once every pipe is closed, and a pipe paused on a full buffer would never close."""
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass

        async def drain(stream: asyncio.StreamReader | None) -> None:
            while stream is not None and await stream.read(65536):
                pass

        try:
            await asyncio.wait_for(asyncio.gather(drain(proc.stdout), drain(proc.stderr), proc.wait()), 10)
        except (asyncio.TimeoutError, OSError, ValueError):
            pass

    @staticmethod
    def _parse_claude(code: int, stdout: bytes, stderr: bytes) -> CliResult:
        try:
            data = json.loads(stdout.decode("utf-8", "replace").strip().splitlines()[-1])
        except (ValueError, IndexError):
            raise _classify(stderr.decode("utf-8", "replace"), f"claude exit={code} unparsable output") from None
        if not isinstance(data, dict):
            raise _classify(stderr.decode("utf-8", "replace"), f"claude exit={code} unexpected output")
        text = data.get("result")
        if data.get("is_error") or data.get("type") != "result" or not isinstance(text, str):
            reason = f"{text or ''} {data.get('api_error_status') or ''} {stderr.decode('utf-8', 'replace')}"
            raise _classify(reason, f"claude exit={code} is_error terminal={data.get('terminal_reason')}")
        if code != 0 or not text.strip():
            raise _classify(stderr.decode("utf-8", "replace"), f"claude exit={code} empty={not text.strip()}")
        usage = data.get("usage") or {}
        prompt_tokens = sum(int(usage.get(k) or 0) for k in
                            ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        return CliResult(text.strip(), prompt_tokens, int(usage.get("output_tokens") or 0))
