"""LAB 004 · FastAPI front for Claude Code / Codex CLI accounts.

Endpoints
  GET  /health               public liveness + CLI availability (no account info)
  GET  /v1/models            Bearer token; models, effort levels, accounts, limits
  POST /v1/chat/completions  Bearer token; OpenAI-like request, one CLI call per request

Nothing here logs message content, CLI output, tokens or credentials.
"""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
import hmac
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from . import __version__
from .catalog import KNOWN_UNSUPPORTED_FIELDS, MODELS, PROVIDERS, SUPPORTED_FIELDS
from .config import CREDENTIAL_FILES, Settings, load_settings
from .runner import CLIError, cli_version, run_chat
from .transcript import build_prompt

log = logging.getLogger("lab04")


# ---------------------------------------------------------------- errors ---

class APIError(Exception):
    def __init__(self, status: int, type_: str, message: str, param: str | None = None):
        super().__init__(message)
        self.status, self.type, self.message, self.param = status, type_, message, param


def error_body(type_: str, message: str, request_id: str, param: str | None = None) -> dict:
    err = {"type": type_, "message": message, "request_id": request_id}
    if param:
        err["param"] = param
    return {"error": err}


# ------------------------------------------------------------ concurrency ---

class Limiter:
    """Global cap plus a per-(provider, account) cap. Busy -> 429, not an endless queue."""

    def __init__(self, s: Settings):
        self.wait = s.queue_wait_s
        self.global_sem = asyncio.Semaphore(s.max_concurrency)
        self.per_account = {
            (p, a): asyncio.Semaphore(s.per_account_concurrency)
            for p, names in s.accounts.items() for a in names
        }

    async def _acquire(self, sem: asyncio.Semaphore, what: str) -> None:
        try:
            await asyncio.wait_for(sem.acquire(), timeout=max(self.wait, 0.001))
        except asyncio.TimeoutError:
            raise APIError(429, "busy", f"{what} is busy with another request; try again shortly.") from None

    @contextlib.asynccontextmanager
    async def slot(self, provider: str, account: str):
        acc = self.per_account[(provider, account)]
        await self._acquire(acc, f"Account {provider}/{account}")
        try:
            await self._acquire(self.global_sem, "The server")
            try:
                yield
            finally:
                self.global_sem.release()
        finally:
            acc.release()


# ---------------------------------------------------------------- schema ---

class Message(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str
    messages: list[Message] = Field(min_length=1)
    reasoning_effort: str | None = None
    account: str | None = None
    provider: str | None = None
    stream: bool | None = None


# ------------------------------------------------------------------- app ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    s: Settings = app.state.settings
    app.state.limiter = Limiter(s)
    # Probe through the default account's wrapper (yolo1 / cyolo1 by default).
    claude_v, codex_v = await asyncio.gather(cli_version(s, s.accounts["claude"][0]),
                                             cli_version(s, s.accounts["codex"][0]))
    app.state.cli = {"claude": claude_v, "codex": codex_v}
    log.info(json.dumps({"event": "startup", "cli": app.state.cli,
                         "accounts": {p: list(a) for p, a in s.accounts.items()},
                         "cors_origins": list(s.cors_origins)}))
    yield


def create_app(settings: Settings | None = None) -> FastAPI:
    s = settings or load_settings()
    app = FastAPI(title="LAB 004 Multi-Account CLI API", version=__version__,
                  docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.state.settings = s

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(s.cors_origins),
        allow_credentials=False,          # token travels in a header, never in cookies
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
        expose_headers=["X-Request-ID"],
        max_age=600,
    )

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        rid = uuid.uuid4().hex[:16]
        request.state.rid = rid
        clen = request.headers.get("content-length")
        if clen is not None and (not clen.isdigit() or int(clen) > s.max_body_bytes):
            resp = JSONResponse(error_body("request_too_large",
                                           f"Body exceeds {s.max_body_bytes} bytes.", rid), 413)
        else:
            resp = await call_next(request)
        resp.headers["X-Request-ID"] = rid
        resp.headers["Cache-Control"] = "no-store"
        resp.headers["X-Content-Type-Options"] = "nosniff"
        return resp

    @app.exception_handler(APIError)
    async def api_error(request: Request, exc: APIError):
        return JSONResponse(error_body(exc.type, exc.message, request.state.rid, exc.param), exc.status)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        # Never echo input values back (they may be message content).
        return JSONResponse(error_body("invalid_request", _describe(exc.errors()), request.state.rid), 400)

    @app.exception_handler(404)
    async def not_found(request: Request, exc):
        return JSONResponse(error_body("not_found", "No such endpoint.", request.state.rid), 404)

    @app.exception_handler(405)
    async def bad_method(request: Request, exc):
        return JSONResponse(error_body("method_not_allowed", "Method not allowed.", request.state.rid), 405)

    def require_token(request: Request) -> None:
        auth = request.headers.get("authorization", "")
        scheme, _, token = auth.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            raise APIError(401, "unauthorized", "Missing Bearer token.")
        digest = hashlib.sha256(token.strip().encode("utf-8")).hexdigest()
        if not hmac.compare_digest(digest, s.api_token_sha256):
            raise APIError(401, "unauthorized", "Invalid API token.")

    def credential_present(provider: str, account: str) -> bool:
        # Existence and non-empty size only. The file is never opened.
        f = s.account_dir(provider, account) / CREDENTIAL_FILES[provider]
        try:
            return f.is_file() and f.stat().st_size > 0
        except OSError:
            return False

    @app.get("/health")
    async def health():
        cli = app.state.cli
        return {
            "status": "ok",
            "service": "lab04-api",
            "version": __version__,
            "cli": {p: {"available": v is not None, "version": v} for p, v in cli.items()},
            "note": "Liveness only. It does not prove any account is logged in; "
                    "only a successful /v1/chat/completions call proves that.",
        }

    @app.get("/v1/models")
    async def models(request: Request):
        require_token(request)
        return {
            "object": "list",
            "data": [
                {"id": m.id, "object": "model", "owned_by": m.provider, "provider": m.provider,
                 "label": m.label, "reasoning_efforts": list(m.efforts),
                 "default_reasoning_effort": m.default_effort}
                for m in MODELS.values()
            ],
            "providers": [
                {"id": p, "label": PROVIDERS[p], "cli_available": app.state.cli.get(p) is not None,
                 "cli_version": app.state.cli.get(p),
                 "accounts": [{"id": a, "default": i == 0,
                               "credential_file_present": credential_present(p, a)}
                              for i, a in enumerate(s.accounts[p])]}
                for p in PROVIDERS
            ],
            "supported_parameters": sorted(SUPPORTED_FIELDS),
            "rejected_parameters_examples": sorted(KNOWN_UNSUPPORTED_FIELDS),
            "limits": {
                "max_messages": s.max_messages,
                "max_message_chars": s.max_message_chars,
                "max_transcript_chars": s.max_transcript_chars,
                "max_output_chars": s.max_output_chars,
                "cli_timeout_s": s.cli_timeout_s,
                "per_account_concurrency": s.per_account_concurrency,
            },
            "semantics": "Each request runs one fresh CLI process. Follow-up context exists only "
                         "because the client re-sends the full text history in `messages`.",
        }

    @app.post("/v1/chat/completions")
    async def chat(request: Request):
        require_token(request)
        rid = request.state.rid
        t0 = time.monotonic()
        meta: dict = {"event": "chat", "rid": rid}
        try:
            req = await _parse_chat(request, s.max_body_bytes)
            spec = MODELS.get(req.model)
            if spec is None:
                raise APIError(400, "unsupported_model", f"Model must be one of: {', '.join(MODELS)}.", "model")
            if req.provider is not None and req.provider != spec.provider:
                raise APIError(400, "provider_model_mismatch",
                               f"Model {spec.id} belongs to provider {spec.provider}.", "provider")
            effort = req.reasoning_effort or spec.default_effort
            if effort not in spec.efforts:
                raise APIError(400, "unsupported_reasoning_effort",
                               f"{spec.id} accepts reasoning_effort: {', '.join(spec.efforts)}.",
                               "reasoning_effort")
            names = s.accounts[spec.provider]
            account = req.account or names[0]
            if account not in names:
                raise APIError(400, "unknown_account",
                               f"Account for {spec.provider} must be one of: {', '.join(names)}.", "account")
            if req.stream:
                raise APIError(400, "unsupported_parameter",
                               "stream=true is not supported; the CLI reply is returned in one response.",
                               "stream")
            msgs = [m.model_dump() for m in req.messages]
            _check_messages(s, msgs)
            meta.update(provider=spec.provider, model=spec.id, effort=effort, account=account,
                        n_messages=len(msgs), transcript_chars=sum(len(m["content"]) for m in msgs))
            if app.state.cli.get(spec.provider) is None:
                raise APIError(503, "cli_not_installed", f"The {spec.provider} CLI is not available.")
            if not credential_present(spec.provider, account):
                raise APIError(503, "account_not_provisioned",
                               f"No credential copy found for {spec.provider}/{account} in the API container.",
                               "account")

            async with app.state.limiter.slot(spec.provider, account):
                result = await run_chat(s, spec.provider, spec.id, effort, account, build_prompt(msgs))

            meta.update(status=200, reply_chars=len(result.text), truncated=result.truncated)
            return {
                "id": f"chatcmpl-{rid}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": spec.id,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": result.text},
                    "finish_reason": "length" if result.truncated else "stop",
                }],
                "usage": None,  # the CLIs are not asked for token accounting; we do not invent it
                "x_backend": {
                    "provider": spec.provider, "account": account, "reasoning_effort": effort,
                    "cli_version": app.state.cli.get(spec.provider),
                    "duration_ms": result.duration_ms, "output_truncated": result.truncated,
                    "history_messages_sent": len(msgs),
                },
            }
        except APIError as e:
            meta.update(status=e.status, error=e.type)
            raise
        except CLIError as e:
            meta.update(status=e.status, error=e.type)
            return JSONResponse(error_body(e.type, e.message, rid), e.status)
        except Exception as exc:
            # Type name only: a traceback or str(exc) could contain message content.
            meta.update(status=500, error="internal_error", exc_type=type(exc).__name__)
            return JSONResponse(error_body("internal_error", "Internal server error.", rid), 500)
        finally:
            meta["duration_ms"] = int((time.monotonic() - t0) * 1000)
            log.info(json.dumps(meta))

    return app


async def _read_body_capped(request: Request, cap: int) -> bytes:
    """Read the body with a hard byte cap. The Content-Length check in the middleware
    does not cover chunked uploads (no Content-Length), so count bytes as they arrive."""
    buf = bytearray()
    async for chunk in request.stream():
        buf.extend(chunk)
        if len(buf) > cap:
            raise APIError(413, "request_too_large", f"Body exceeds {cap} bytes.")
    return bytes(buf)


async def _parse_chat(request: Request, cap: int) -> ChatRequest:
    raw = await _read_body_capped(request, cap)
    try:
        body = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise APIError(400, "invalid_json", "Body must be a JSON object.") from None
    if not isinstance(body, dict):
        raise APIError(400, "invalid_json", "Body must be a JSON object.")
    unknown = sorted(set(body) - SUPPORTED_FIELDS)
    if unknown:
        known = [k for k in unknown if k in KNOWN_UNSUPPORTED_FIELDS]
        shown = ", ".join(k[:40] for k in unknown[:10])
        msg = (f"Unsupported parameter(s): {shown}. This CLI-backed API cannot honour them "
               f"and rejects them instead of ignoring them."
               if known else f"Unknown parameter(s): {shown}.")
        raise APIError(400, "unsupported_parameter", msg, unknown[0][:40])
    try:
        return ChatRequest.model_validate(body)
    except ValidationError as e:
        raise APIError(400, "invalid_request", _describe(e.errors())) from None


def _check_messages(s: Settings, msgs: list[dict]) -> None:
    if len(msgs) > s.max_messages:
        raise APIError(400, "too_many_messages", f"At most {s.max_messages} messages per request.", "messages")
    seen_non_system = False
    for i, m in enumerate(msgs):
        if m["role"] == "system":
            if seen_non_system:
                raise APIError(400, "invalid_messages", "system messages are only allowed at the start.",
                               f"messages[{i}]")
        else:
            seen_non_system = True
        if not m["content"].strip():
            raise APIError(400, "invalid_messages", "Message content must not be empty.", f"messages[{i}]")
        if len(m["content"]) > s.max_message_chars:
            raise APIError(400, "message_too_long",
                           f"Each message is limited to {s.max_message_chars} characters.", f"messages[{i}]")
    if msgs[-1]["role"] != "user":
        raise APIError(400, "invalid_messages", "The last message must have role 'user'.", "messages")
    total = sum(len(m["content"]) for m in msgs)
    if total > s.max_transcript_chars:
        raise APIError(400, "transcript_too_long",
                       f"The history is {total} characters; the limit is {s.max_transcript_chars}. "
                       "Clear the chat or start a new one.", "messages")


def _describe(errors: list[dict]) -> str:
    parts = []
    for e in errors[:5]:
        loc = ".".join(str(x) for x in e.get("loc", ()) if x != "body")
        parts.append(f"{loc or 'body'}: {e.get('type', 'invalid')}")
    return "Invalid request: " + "; ".join(parts)


def _configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


_configure_logging()
