"""FastAPI app: static index page, health, model catalog and OpenAI-style chat completions."""

from __future__ import annotations

import hmac
import logging
import time
import uuid
from typing import Any, Literal

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import catalog
from .config import Settings
from .runner import CliError, Runner
from .transcript import build_prompt

log = logging.getLogger("chat-api")

MISSING_PAGE = """<!doctype html>
<html lang="th"><head><meta charset="utf-8"><title>Web page not installed</title></head>
<body style="font-family:sans-serif;max-width:40em;margin:3em auto">
<h1>ยังไม่มีหน้าเว็บ</h1>
<p>ไม่พบไฟล์ <code>index.html</code> ในโฟลเดอร์หน้าเว็บที่ mount เข้ามา
ให้สร้างไฟล์ <code>web/index.html</code> ในโปรเจกต์ แล้วโหลดหน้านี้ใหม่ (ไม่ต้อง build image ใหม่)</p>
<p>The web page is not installed yet: <code>index.html</code> was not found in the mounted
web folder. Add <code>web/index.html</code> to the project and reload.</p>
<p>API: <code>GET /health</code>, <code>GET /v1/models</code>, <code>POST /v1/chat/completions</code></p>
</body></html>"""


class ApiError(HTTPException):
    # Subclassing FastAPI's HTTPException lets it pass through body parsing unchanged.
    def __init__(self, status: int, code: str, message: str, headers: dict[str, str] | None = None):
        super().__init__(status, message, headers)
        self.status, self.code, self.message = status, code, message


def error_response(status: int, code: str, message: str, headers: dict[str, str] | None = None) -> JSONResponse:
    kind = "invalid_request_error" if status < 500 else "server_error"
    return JSONResponse({"error": {"message": message, "type": kind, "code": code}},
                        status_code=status, headers=headers)


class TextPart(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["text"]
    text: str


class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    role: Literal["system", "developer", "user", "assistant"]
    content: str | list[TextPart]

    def text(self) -> str:
        if isinstance(self.content, str):
            return self.content
        return "\n".join(p.text for p in self.content)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")  # tolerate other OpenAI fields (temperature, ...)
    messages: list[Message] = Field(min_length=1)
    model: str | None = None
    reasoning_effort: str | None = None
    account: str | None = None
    provider: str | None = None
    stream: bool | None = None


class BodyLimit:
    """Reject request bodies over the limit before they are buffered (works without Content-Length)."""

    def __init__(self, app, max_bytes: int):
        self.app, self.max_bytes = app, max_bytes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        too_big = error_response(413, "request_too_large",
                                 f"Request body is larger than {self.max_bytes} bytes.")
        for name, value in scope.get("headers", []):
            if name == b"content-length" and value.isdigit() and int(value) > self.max_bytes:
                return await too_big(scope, receive, send)
        seen, rejected = 0, False

        async def limited_receive():
            nonlocal seen, rejected
            if rejected:
                return {"type": "http.disconnect"}
            message = await receive()
            if message["type"] == "http.request":
                seen += len(message.get("body", b""))
                if seen > self.max_bytes:
                    # Answer 413 now; the app sees a disconnect and its own response is dropped.
                    rejected = True
                    await too_big(scope, receive, send)
                    return {"type": "http.disconnect"}
            return message

        async def guarded_send(message):
            if not rejected:
                await send(message)

        await self.app(scope, limited_receive, guarded_send)


def create_app(settings: Settings | None = None, runner: Runner | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    runner = runner or Runner(settings)
    app = FastAPI(title="Multi-account chat API", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.settings = settings

    @app.middleware("http")
    async def headers_and_log(request: Request, call_next):
        started = time.monotonic()
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Cache-Control", "no-store")
        if request.url.path.startswith("/v1/"):
            log.info("%s %s -> %s in %.1fs", request.method, request.url.path, response.status_code,
                     time.monotonic() - started)
        return response

    app.add_middleware(BodyLimit, max_bytes=settings.max_body_bytes)

    @app.exception_handler(ApiError)
    async def on_api_error(_: Request, exc: ApiError):
        return error_response(exc.status, exc.code, exc.message, exc.headers)

    @app.exception_handler(RequestValidationError)
    async def on_validation(_: Request, exc: RequestValidationError):
        problems = []
        for err in exc.errors()[:5]:
            where = ".".join(str(p) for p in err.get("loc", ()) if p != "body") or "body"
            problems.append(f"{where}: {err.get('msg', 'invalid value')}")
        return error_response(400, "invalid_request", "Invalid request. " + "; ".join(problems))

    @app.exception_handler(StarletteHTTPException)
    async def on_http(_: Request, exc: StarletteHTTPException):
        messages = {404: "Not found.", 405: "Method not allowed."}
        return error_response(exc.status_code, "http_error", messages.get(exc.status_code, "Request failed."))

    @app.exception_handler(Exception)
    async def on_unexpected(_: Request, exc: Exception):
        log.error("unexpected error: %s", type(exc).__name__)
        return error_response(500, "internal_error", "Internal server error.")

    def require_token(request: Request) -> None:
        if len(settings.api_token) < 16:
            raise ApiError(503, "server_not_configured", "The server has no API token configured.")
        header = request.headers.get("authorization", "")
        scheme, _, token = header.partition(" ")
        if scheme.lower() != "bearer" or not hmac.compare_digest(token.strip().encode(), settings.api_token.encode()):
            raise ApiError(401, "invalid_token", "Missing or invalid Bearer token.",
                           {"WWW-Authenticate": "Bearer"})

    @app.get("/", include_in_schema=False)
    async def index():
        page = settings.web_dir / "index.html"
        if page.is_file():
            return FileResponse(page, media_type="text/html; charset=utf-8")
        return HTMLResponse(MISSING_PAGE, status_code=503)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/v1/models", dependencies=[Depends(require_token)])
    async def models():
        return catalog.models_payload(settings)

    @app.post("/v1/chat/completions", dependencies=[Depends(require_token)])
    async def chat(body: ChatRequest) -> dict[str, Any]:
        if body.stream:
            raise ApiError(400, "stream_not_supported", "Streaming is not supported; send stream=false.")
        if len(body.messages) > settings.max_messages:
            raise ApiError(400, "too_many_messages",
                           f"Too many messages: {len(body.messages)} (limit {settings.max_messages}).")
        messages = [{"role": m.role, "content": m.text()} for m in body.messages]
        for i, m in enumerate(messages):
            if len(m["content"]) > settings.max_message_chars:
                raise ApiError(400, "message_too_long",
                               f"messages[{i}] is longer than {settings.max_message_chars} characters.")
        if sum(len(m["content"]) for m in messages) > settings.max_total_chars:
            raise ApiError(400, "conversation_too_long",
                           f"The conversation is longer than {settings.max_total_chars} characters in total.")
        if messages[-1]["role"] != "user":
            raise ApiError(400, "last_message_not_user", "The last message must have role 'user'.")
        if not messages[-1]["content"].strip():
            raise ApiError(400, "empty_message", "The last user message is empty.")

        try:
            sel = catalog.resolve(settings, body.model, body.reasoning_effort, body.account, body.provider)
        except catalog.CatalogError as exc:
            raise ApiError(400, "unsupported_selection", str(exc)) from None

        request_id = uuid.uuid4().hex
        started = time.monotonic()
        try:
            result = await runner.run(sel, build_prompt(messages))
        except CliError as exc:
            log.warning("call %s %s/%s/%s failed: %s (%s)", request_id[:8], sel.provider, sel.model.id,
                        sel.account, exc.code, exc.detail)
            raise ApiError(exc.status, exc.code, exc.message) from None
        log.info("call %s %s/%s/%s effort=%s ok in %.1fs", request_id[:8], sel.provider, sel.model.id,
                 sel.account, sel.effort, time.monotonic() - started)
        return {
            "id": f"chatcmpl-{request_id}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": sel.model.id,
            "provider": sel.provider,
            "account": sel.account,
            "reasoning_effort": sel.effort,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": result.text},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": result.prompt_tokens, "completion_tokens": result.completion_tokens,
                      "total_tokens": result.prompt_tokens + result.completion_tokens},
        }

    return app


def build() -> FastAPI:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    return create_app()
