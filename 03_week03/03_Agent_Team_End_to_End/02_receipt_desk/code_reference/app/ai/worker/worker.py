"""ReceiptDesk GPU worker: reads one receipt at a time and returns 5 fields plus total confidence.

The loop follows B06 section 3.5, DESIGN 6.3 and 7:

    loop:
      wait until vLLM answers through NGINX     (so attempts aren't used up while the GPU is down)
      d = I4 POST /internal/workers/{id}/next   -> urgent | normal | none   (BR-10 4:1, counted system-wide)
      none -> sleep IDLE_POLL_SECONDS
      msg = basic.get(receipts.<d.queue>, manual ack)   (one unacked message at most; no basic.consume)
      empty -> ask I4 again
      c = I1 POST /internal/receipts/{ref}/claim {worker_id, queue, msg_priority, inline_image}
        skip -> ack · wait -> nack(requeue) + sleep · dead -> reject(requeue=False) -> receipts.dlq
        go   -> read through NGINX (least_conn over vLLM 0/1) with a hard 60 s limit
              -> I2 POST /internal/receipts/{ref}/result
              -> topology.settle_delivery(msg, outcome): done/skip ack · queued/wait nack(requeue)
                                                        · dead reject -> receipts.dlx -> receipts.dlq
    background: I3 heartbeat every 5 s while connected to RabbitMQ.

Why no receipt is lost (DESIGN 7):
  * The message is acked only after the gateway answers I2. If the worker dies first, the
    AMQP connection drops and RabbitMQ puts the unacked message back in its queue.
  * The gateway counts the attempt at claim (I1). When the heartbeat goes silent for 15 s, it
    releases the lease (B06 3.6), so the other worker can claim the redelivered message.
    A receipt that keeps crashing workers therefore reaches 3 attempts and goes to the DLQ.
  * The gateway keeps only the first result. A late result from a stalled worker gets
    outcome "skip" and is acked, so a receipt never has 2 results.

A read counts as one failure (DESIGN 6.3) when the model answers {"unreadable": true}, the
answer isn't valid 5-field JSON, the read takes over 60 s, or vLLM/NGINX keeps failing until
the time runs out. The gateway decides queued vs dead (BR-07) and the worker settles the
AMQP message with that outcome.

Prompt, answer format, parser and total_confidence come from ai/train/receipt_common.py (B10),
so production matches training and evaluation. The request is the same as
ai/train/evaluate.py VLLMClient: OpenAI chat completions, image before text, temperature 0,
logprobs on, and confidence = exp(sum of logprobs of the tokens of the "total" value).

Logs carry only receipt references, decisions, outcomes and times. They never include
image content or receipt fields (NFR-07). Images come inline from I1 and stay in memory;
nothing is written to disk.

Run (one process per GPU worker; WORKER_ID must be unique and stable across restarts):
    WORKER_ID=worker0 python -m ai.worker.worker
    WORKER_ID=worker1 python -m ai.worker.worker
Self-test (real gateway app in memory, in-memory broker, fake vLLM; needs fastapi):
    python -B -m ai.worker.worker --self-test
NGINX config (least_conn over the 2 vLLM servers, 60 s, next upstream on error or timeout):
    python -m ai.worker.worker --nginx-conf > ai/nginx/nginx.conf

Environment
  WORKER_ID                 worker0 | worker1 ...  (default: worker-<hostname>)
  GATEWAY_URL               http://127.0.0.1:8000  (https://... if the gateway uses TLS)
  GATEWAY_INTERNAL_TOKEN    sent as X-Internal-Token when set (must match the gateway)
  GATEWAY_TLS_VERIFY        1 | 0 | path to a CA bundle  (default 1)
  RABBITMQ_URL              amqp://guest:guest@127.0.0.1:5672/
  VLLM_URL                  http://127.0.0.1:8080  (NGINX, never a vLLM port directly)
  VLLM_API_KEY              Bearer key for vLLM (--api-key), optional
  VLLM_HEALTH_PATH          /health  ("" disables the check before each pick)
  SERVED_MODEL              receipt-vlm
  READ_TIMEOUT_SECONDS      60   (hard limit per read, DESIGN 6.3; capped at 60)
  MAX_NEW_TOKENS=512 IMAGE_MAX_SIDE=1600 HEARTBEAT_SECONDS=5 IDLE_POLL_SECONDS=1
  WAIT_BACKOFF_SECONDS=1 WORKER_INLINE_IMAGE=1 (0 = open image_path on a shared disk)
  LOG_LEVEL=INFO
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import io
import json
import logging
import os
import re
import signal
import socket
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable, Optional

import httpx

try:
    from ai.queue import topology
    from ai.train import receipt_common as rc
except ImportError:  # started as a plain script from inside ai/worker
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from ai.queue import topology
    from ai.train import receipt_common as rc


log = logging.getLogger("receiptdesk.worker")

MAX_READ_SECONDS = 60.0  # DESIGN 6.3: a read that takes longer counts as one failure
WORKER_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,64}$")  # same rule as the gateway
RETRYABLE_VLLM_STATUS = {429, 500, 502, 503, 504}


# --------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------


def _env_float(name: str, default: float) -> float:
    value = os.environ.get(name, "").strip()
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        raise SystemExit(f"{name} must be a number, got {value!r}")


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name, "").strip().lower()
    if not value:
        return default
    return value not in ("0", "false", "no", "off")


def _default_worker_id() -> str:
    host = re.sub(r"[^A-Za-z0-9_.:-]", "-", socket.gethostname())[:50] or "host"
    return f"worker-{host}"


@dataclass
class Settings:
    worker_id: str = field(default_factory=_default_worker_id)
    gateway_url: str = "http://127.0.0.1:8000"
    internal_token: str = ""
    gateway_verify: Any = True  # bool or CA bundle path
    rabbitmq_url: str = "amqp://guest:guest@127.0.0.1:5672/"
    vllm_url: str = "http://127.0.0.1:8080"
    vllm_api_key: str = ""
    vllm_health_path: str = "/health"
    served_model: str = rc.SERVED_MODEL_NAME
    read_timeout: float = MAX_READ_SECONDS
    max_new_tokens: int = 512
    image_max_side: int = 1600
    heartbeat_seconds: float = 5.0
    idle_poll_seconds: float = 1.0
    wait_backoff_seconds: float = 1.0
    empty_backoff_seconds: float = 0.2
    health_cache_seconds: float = 5.0
    reconnect_seconds: float = 3.0
    result_retry_seconds: float = 90.0  # keep retrying I2 for one lease
    inline_image: bool = True

    def __post_init__(self) -> None:
        if not WORKER_ID_RE.match(self.worker_id):
            raise ValueError(f"WORKER_ID must match {WORKER_ID_RE.pattern}")
        if not 0 < self.read_timeout <= MAX_READ_SECONDS:
            raise ValueError("READ_TIMEOUT_SECONDS must be in (0, 60] (DESIGN 6.3)")

    @classmethod
    def from_env(cls) -> "Settings":
        verify_raw = os.environ.get("GATEWAY_TLS_VERIFY", "1").strip()
        verify: Any = verify_raw
        if verify_raw.lower() in ("1", "true", "yes", "on", ""):
            verify = True
        elif verify_raw.lower() in ("0", "false", "no", "off"):
            verify = False
        return cls(
            worker_id=os.environ.get("WORKER_ID", "").strip() or _default_worker_id(),
            gateway_url=os.environ.get("GATEWAY_URL", cls.gateway_url).rstrip("/"),
            internal_token=os.environ.get("GATEWAY_INTERNAL_TOKEN", ""),
            gateway_verify=verify,
            rabbitmq_url=os.environ.get("RABBITMQ_URL", cls.rabbitmq_url),
            vllm_url=os.environ.get("VLLM_URL", cls.vllm_url).rstrip("/"),
            vllm_api_key=os.environ.get("VLLM_API_KEY", ""),
            vllm_health_path=os.environ.get("VLLM_HEALTH_PATH", cls.vllm_health_path),
            served_model=os.environ.get("SERVED_MODEL", cls.served_model),
            read_timeout=_env_float("READ_TIMEOUT_SECONDS", MAX_READ_SECONDS),
            max_new_tokens=int(_env_float("MAX_NEW_TOKENS", 512)),
            image_max_side=int(_env_float("IMAGE_MAX_SIDE", 1600)),
            heartbeat_seconds=_env_float("HEARTBEAT_SECONDS", 5.0),
            idle_poll_seconds=_env_float("IDLE_POLL_SECONDS", 1.0),
            wait_backoff_seconds=_env_float("WAIT_BACKOFF_SECONDS", 1.0),
            inline_image=_env_bool("WORKER_INLINE_IMAGE", True),
        )


# --------------------------------------------------------------------------
# Gateway client (I1 – I4)
# --------------------------------------------------------------------------


class GatewayError(RuntimeError):
    """The gateway could not be reached or answered with an unexpected status."""


class GatewayClient:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self.s = settings
        headers = {"X-Internal-Token": settings.internal_token} if settings.internal_token else {}
        self.http = client or httpx.AsyncClient(
            base_url=settings.gateway_url,
            verify=settings.gateway_verify,
            timeout=httpx.Timeout(15.0, connect=5.0),
        )
        self.http.headers.update(headers)

    async def _post(self, path: str, body: dict[str, Any], timeout: float | None = None) -> dict[str, Any]:
        try:
            kwargs: dict[str, Any] = {"json": body}
            if timeout is not None:
                kwargs["timeout"] = timeout
            response = await self.http.post(path, **kwargs)
        except httpx.HTTPError as exc:
            raise GatewayError(f"{path}: {type(exc).__name__}") from exc
        if response.status_code != 200:
            raise GatewayError(f"{path}: HTTP {response.status_code}")
        try:
            return response.json()
        except ValueError as exc:
            raise GatewayError(f"{path}: invalid JSON") from exc

    async def next(self) -> dict[str, Any]:
        return await self._post(f"/internal/workers/{self.s.worker_id}/next", {})

    async def claim(self, receipt_ref: str, queue: str, msg_priority: str | None) -> dict[str, Any]:
        body: dict[str, Any] = {
            "worker_id": self.s.worker_id,
            "queue": queue,
            "inline_image": self.s.inline_image,
        }
        if msg_priority in ("urgent", "normal"):
            body["msg_priority"] = msg_priority
        # inline images up to 10 MB: allow a slower answer than the other routes
        return await self._post(f"/internal/receipts/{receipt_ref}/claim", body, timeout=60.0)

    async def result(self, receipt_ref: str, body: dict[str, Any]) -> dict[str, Any]:
        return await self._post(f"/internal/receipts/{receipt_ref}/result", body)

    async def heartbeat(self, vllm_ok: bool | None) -> dict[str, Any]:
        return await self._post(
            f"/internal/workers/{self.s.worker_id}/heartbeat", {"vllm_ok": vllm_ok}, timeout=5.0
        )

    async def close(self) -> None:
        await self.http.aclose()


# --------------------------------------------------------------------------
# vLLM through NGINX
# --------------------------------------------------------------------------


@dataclass
class ReadOutcome:
    ok: bool
    result: dict[str, Any] | None = None
    error: str | None = None
    seconds: float = 0.0


def prepare_png(data: bytes | None, mime_type: str, path: str | None, max_side: int) -> bytes:
    """Same image steps as receipt_common.load_image (RGB, PDF at 200 dpi, longest side <= max_side).

    Inline bytes are decoded in memory, so no receipt image is written to the worker's disk.
    """
    if data is None:
        if not path:
            raise ValueError("no image")
        img = rc.load_image(path, max_side)
    else:
        from PIL import Image

        if mime_type == "application/pdf" or data[:5] == b"%PDF-":
            import pypdfium2 as pdfium  # optional dependency, as in receipt_common

            img = pdfium.PdfDocument(data)[0].render(scale=200 / 72).to_pil()
        else:
            img = Image.open(io.BytesIO(data))
            img.load()
        img = img.convert("RGB")
        if max_side and max(img.size) > max_side:
            scale = max_side / max(img.size)
            img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class VLLMClient:
    """OpenAI-compatible chat completions through NGINX (least_conn over vLLM 0 and 1)."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None):
        self.s = settings
        headers = {"Authorization": f"Bearer {settings.vllm_api_key}"} if settings.vllm_api_key else {}
        self.http = client or httpx.AsyncClient(
            base_url=settings.vllm_url,
            timeout=httpx.Timeout(settings.read_timeout, connect=3.0),
        )
        self.http.headers.update(headers)
        self._health_at = float("-inf")
        self.healthy: bool | None = None

    def payload(self, png: bytes) -> dict[str, Any]:
        data_url = "data:image/png;base64," + base64.b64encode(png).decode("ascii")
        return {
            "model": self.s.served_model,
            "messages": [
                {"role": "system", "content": rc.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_url}},
                        {"type": "text", "text": rc.USER_PROMPT},
                    ],
                },
            ],
            "temperature": 0,
            "max_tokens": self.s.max_new_tokens,
            "logprobs": True,
        }

    async def ready(self) -> bool:
        """Cached GET /health through NGINX. The check is skipped when VLLM_HEALTH_PATH is empty."""
        if not self.s.vllm_health_path:
            return True
        now = time.monotonic()
        if now - self._health_at < self.s.health_cache_seconds and self.healthy is not None:
            return self.healthy
        try:
            response = await self.http.get(self.s.vllm_health_path, timeout=3.0)
            ok = response.status_code == 200
        except httpx.HTTPError:
            ok = False
        if ok != self.healthy:
            (log.info if ok else log.warning)("vLLM via NGINX %s", "ready" if ok else "not ready")
        self.healthy, self._health_at = ok, now
        return ok

    def mark_unhealthy(self) -> None:
        self.healthy, self._health_at = False, time.monotonic()

    async def complete(self, png: bytes, deadline: float) -> dict[str, Any]:
        """POST /v1/chat/completions, retrying 5xx/connection errors until the deadline.

        NGINX already moves on to the other vLLM after an error or timeout. This retry covers
        the short gap while both upstreams are briefly marked down.
        """
        body = self.payload(png)
        delay = 0.5
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise asyncio.TimeoutError()
            try:
                response = await self.http.post("/v1/chat/completions", json=body, timeout=remaining)
            except httpx.ConnectTimeout:
                response = None  # NGINX not answering: retry like a connection error
            except httpx.TimeoutException as exc:
                raise asyncio.TimeoutError() from exc
            except httpx.TransportError:
                response = None
            if response is not None and response.status_code == 200:
                return response.json()
            if response is not None and response.status_code not in RETRYABLE_VLLM_STATUS:
                raise VLLMRejected(response.status_code)
            if deadline - time.monotonic() <= delay:
                self.mark_unhealthy()
                raise VLLMUnavailable(response.status_code if response is not None else None)
            await asyncio.sleep(delay)
            delay = min(delay * 2, 4.0)

    async def close(self) -> None:
        await self.http.aclose()


class VLLMRejected(RuntimeError):
    def __init__(self, status: int):
        super().__init__(f"vLLM HTTP {status}")
        self.status = status


class VLLMUnavailable(RuntimeError):
    def __init__(self, status: int | None):
        super().__init__(f"vLLM unavailable ({status})")
        self.status = status


def read_choice(body: dict[str, Any]) -> tuple[str, float | None]:
    """Text and total_confidence from a chat completion (same as evaluate.VLLMClient)."""
    choice = body["choices"][0]
    text = (choice.get("message") or {}).get("content") or ""
    pieces: list[tuple[bytes | str, float]] = []
    for tok in (choice.get("logprobs") or {}).get("content") or []:
        piece = bytes(tok["bytes"]) if tok.get("bytes") is not None else tok["token"]
        pieces.append((piece, float(tok["logprob"])))
    conf = rc.confidence_from_token_spans(text, rc.spans_from_token_pieces(pieces))
    if conf is not None:
        conf = min(1.0, max(0.0, conf))
    return text, conf


def to_result(text: str, confidence: float | None, model: str) -> ReadOutcome:
    """Map the model text onto the I2 body (DESIGN 6.3 failure reasons)."""
    parsed = rc.parse_model_output(text)
    if parsed.unreadable:
        return ReadOutcome(ok=False, error="model_unreadable")
    if not parsed.valid:
        return ReadOutcome(ok=False, error=f"invalid_output:{parsed.error or 'unknown'}"[:64])
    return ReadOutcome(
        ok=True,
        result={
            "merchant": parsed.merchant,
            "date": parsed.date,
            "items": [
                {"name": it["name"], "price": rc.satang_to_str(it["price_satang"])}
                for it in parsed.items
            ],
            "total": rc.satang_to_str(parsed.total_satang),
            # None is allowed: the web counts a missing confidence as BR-04 flagged
            "total_confidence": confidence,
            "model": model,
        },
    )


# --------------------------------------------------------------------------
# RabbitMQ (basic.get with manual ack, one message at a time)
# --------------------------------------------------------------------------


class AmqpSource:
    """Pulls one message at a time with basic.get (B06: never basic.consume)."""

    def __init__(self, url: str):
        self.url = url
        self.connection = None
        self.channel = None
        self.queues: dict[str, Any] = {}

    @property
    def connected(self) -> bool:
        return self.connection is not None and not self.connection.is_closed

    async def connect(self) -> None:
        import aio_pika

        self.connection = await aio_pika.connect(self.url)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=1)
        self.queues = await topology.declare_topology(self.channel)

    async def get(self, priority: str):
        return await self.queues[priority].get(no_ack=False, fail=False)

    async def close(self) -> None:
        connection, self.connection, self.channel, self.queues = self.connection, None, None, {}
        if connection is not None:
            try:
                await connection.close()
            except Exception:
                pass


# --------------------------------------------------------------------------
# Worker
# --------------------------------------------------------------------------


class Worker:
    def __init__(
        self,
        settings: Settings,
        *,
        gateway: GatewayClient | None = None,
        vllm: VLLMClient | None = None,
        amqp: Any = None,
        sleep: Callable[[float], Awaitable[None]] | None = None,
    ):
        self.s = settings
        self.gateway = gateway or GatewayClient(settings)
        self.vllm = vllm or VLLMClient(settings)
        self.amqp = amqp or AmqpSource(settings.rabbitmq_url)
        self.stopping = asyncio.Event()
        self._sleep_fn = sleep
        self.stats = {"done": 0, "failed": 0, "dead": 0, "skip": 0, "wait": 0}

    # helpers ---------------------------------------------------------------
    async def _sleep(self, seconds: float) -> None:
        if self._sleep_fn is not None:
            await self._sleep_fn(seconds)
            return
        try:
            await asyncio.wait_for(self.stopping.wait(), timeout=seconds)
        except asyncio.TimeoutError:
            pass

    @staticmethod
    async def _settle(message: Any, outcome: str, ref: str) -> None:
        try:
            await topology.settle_delivery(message, outcome)
        except Exception as exc:
            # The channel is gone, so RabbitMQ has already put the message back.
            # The gateway keeps only the first result, so a repeat read stores nothing new.
            log.warning("settle %s for receipt=%s failed: %s", outcome, ref, type(exc).__name__)

    # one pick --------------------------------------------------------------
    async def step(self) -> str:
        """Do one pick (B06 3.5). Returns a short label used in logs and tests."""
        if not await self.vllm.ready():
            await self._sleep(self.s.idle_poll_seconds)
            return "vllm_down"
        try:
            decision = await self.gateway.next()
        except GatewayError as exc:
            log.warning("I4 next failed: %s", exc)
            await self._sleep(self.s.wait_backoff_seconds)
            return "gateway_error"
        queue = decision.get("queue")
        if queue not in ("urgent", "normal"):
            await self._sleep(self.s.idle_poll_seconds)
            return "idle"

        message = await self.amqp.get(queue)
        if message is None:
            # Another worker took it first. Ask again; I4 drops our old reservation.
            await self._sleep(self.s.empty_backoff_seconds)
            return "empty"

        try:
            body = json.loads(message.body)
            ref = str(body["receipt_ref"])
            msg_priority = body.get("priority")
        except (ValueError, KeyError, TypeError):
            log.error("malformed message on %s, sent to DLQ", topology.QUEUE_NAMES[queue])
            await self._settle(message, "dead", "-")
            return "malformed"

        try:
            claim = await self.gateway.claim(ref, queue, msg_priority)
        except GatewayError as exc:
            log.warning("I1 claim receipt=%s failed: %s", ref, exc)
            await self._settle(message, "queued", ref)
            await self._sleep(self.s.wait_backoff_seconds)
            return "gateway_error"

        verdict = claim.get("decision")
        reason = claim.get("reason", "")
        if verdict == "skip":
            log.info("receipt=%s skip (%s)", ref, reason)
            self.stats["skip"] += 1
            await self._settle(message, "skip", ref)
            return "skip"
        if verdict == "dead":
            log.warning("receipt=%s dead at claim (%s) -> DLQ", ref, reason)
            self.stats["dead"] += 1
            await self._settle(message, "dead", ref)
            return "dead"
        if verdict != "go":
            log.info("receipt=%s wait (%s)", ref, reason)
            self.stats["wait"] += 1
            await self._settle(message, "wait", ref)
            await self._sleep(self.s.wait_backoff_seconds)
            return "wait"

        return await self._process(message, ref, queue, claim)

    async def _process(self, message: Any, ref: str, queue: str, claim: dict[str, Any]) -> str:
        attempts = claim.get("attempts")
        log.info("receipt=%s go queue=%s attempt=%s", ref, queue, attempts)
        started = time.monotonic()
        try:
            outcome = await asyncio.wait_for(self._read(claim), timeout=self.s.read_timeout)
        except asyncio.TimeoutError:
            outcome = ReadOutcome(ok=False, error="timeout_60s")
        outcome.seconds = round(time.monotonic() - started, 3)

        body: dict[str, Any] = {
            "worker_id": self.s.worker_id,
            "ok": outcome.ok,
            "read_seconds": min(outcome.seconds, 3600.0),
        }
        if outcome.ok:
            body["result"] = outcome.result
        else:
            body["error"] = outcome.error

        answer = await self._send_result(ref, body)
        if answer is None:
            # The gateway is unreachable. Put the message back. The lease runs out and the
            # next claim counts a new attempt.
            await self._settle(message, "queued", ref)
            return "gateway_error"
        result_outcome = answer.get("outcome")
        if result_outcome not in ("done", "skip", "queued", "wait", "dead"):
            log.error("receipt=%s unknown I2 outcome %r, requeued", ref, result_outcome)
            result_outcome = "queued"
        log.info(
            "receipt=%s read ok=%s error=%s seconds=%.1f -> %s (%s)",
            ref, outcome.ok, outcome.error or "-", outcome.seconds, result_outcome, answer.get("reason", ""),
        )
        if outcome.ok:
            self.stats["done"] += 1
        else:
            self.stats["failed"] += 1
        if result_outcome == "dead":
            self.stats["dead"] += 1
        await self._settle(message, result_outcome, ref)
        return result_outcome

    async def _read(self, claim: dict[str, Any]) -> ReadOutcome:
        image_b64 = claim.get("image_b64")
        data = base64.b64decode(image_b64) if image_b64 else None
        try:
            png = await asyncio.to_thread(
                prepare_png, data, claim.get("mime_type") or "", claim.get("image_path"),
                self.s.image_max_side,
            )
        except Exception as exc:  # broken or truncated image: the model can't read it either
            log.warning("receipt=%s image decode failed: %s", claim.get("receipt_ref"), type(exc).__name__)
            return ReadOutcome(ok=False, error="bad_image")
        deadline = time.monotonic() + self.s.read_timeout
        try:
            body = await self.vllm.complete(png, deadline)
            text, confidence = read_choice(body)
        except asyncio.TimeoutError:
            return ReadOutcome(ok=False, error="timeout_60s")
        except VLLMRejected as exc:
            return ReadOutcome(ok=False, error=f"vllm_http_{exc.status}")
        except VLLMUnavailable:
            return ReadOutcome(ok=False, error="vllm_unavailable")
        except (KeyError, IndexError, TypeError, ValueError):
            return ReadOutcome(ok=False, error="vllm_bad_response")
        return to_result(text, confidence, body.get("model") or self.s.served_model)

    async def _send_result(self, ref: str, body: dict[str, Any]) -> dict[str, Any] | None:
        """I2 with retries. The AMQP message stays unacked until the gateway answers."""
        give_up = time.monotonic() + self.s.result_retry_seconds
        delay = 0.5
        while True:
            try:
                return await self.gateway.result(ref, body)
            except GatewayError as exc:
                if time.monotonic() + delay > give_up:
                    log.error("I2 result receipt=%s failed for good: %s", ref, exc)
                    return None
                log.warning("I2 result receipt=%s failed, retrying: %s", ref, exc)
                await asyncio.sleep(delay)
                delay = min(delay * 2, 5.0)

    # background --------------------------------------------------------------
    async def heartbeat_loop(self) -> None:
        while not self.stopping.is_set():
            if self.amqp.connected:
                try:
                    await self.gateway.heartbeat(self.vllm.healthy)
                except GatewayError as exc:
                    log.warning("I3 heartbeat failed: %s", exc)
            await self._sleep(self.s.heartbeat_seconds)

    async def run(self) -> None:
        log.info(
            "worker %s starting: gateway=%s vllm=%s timeout=%ss",
            self.s.worker_id, self.s.gateway_url, self.s.vllm_url, self.s.read_timeout,
        )
        beat = asyncio.create_task(self.heartbeat_loop())
        try:
            while not self.stopping.is_set():
                try:
                    if not self.amqp.connected:
                        await self.amqp.connect()
                        log.info("connected to RabbitMQ")
                    while not self.stopping.is_set():
                        await self.step()
                except asyncio.CancelledError:
                    raise
                except Exception as exc:  # broker gone, channel closed, ...
                    log.error("worker loop error: %s: %s", type(exc).__name__, exc)
                    await self.amqp.close()
                    await self._sleep(self.s.reconnect_seconds)
        finally:
            self.stopping.set()
            beat.cancel()
            await asyncio.gather(beat, return_exceptions=True)
            await self.amqp.close()
            await self.gateway.close()
            await self.vllm.close()
            log.info("worker %s stopped %s", self.s.worker_id, self.stats)


# --------------------------------------------------------------------------
# NGINX config (DESIGN 1.1 / 7: least_conn, next upstream on error or timeout)
# --------------------------------------------------------------------------


def nginx_conf(
    upstreams: tuple[str, ...] = ("127.0.0.1:8001", "127.0.0.1:8002"),
    listen: str = "8080",
    read_seconds: int = int(MAX_READ_SECONDS),
) -> str:
    servers = "\n".join(f"        server {u} max_fails=1 fail_timeout=10s;" for u in upstreams)
    return f"""# ReceiptDesk NGINX in front of vLLM 0 (GPU 0) and vLLM 1 (GPU 1).
# Generated by: python -m ai.worker.worker --nginx-conf
# Workers call http://127.0.0.1:{listen}/v1/chat/completions and never a vLLM port directly.
worker_processes auto;
events {{ worker_connections 1024; }}

http {{
    access_log off;            # NFR-07: request bodies hold receipt images; keep no log of them
    error_log /dev/stderr warn;

    upstream vllm {{
        least_conn;            # the less busy GPU gets the next receipt
{servers}
        keepalive 16;
    }}

    server {{
        listen {listen};       # internal only (DESIGN 1.2): not published outside the GPU machine
        allow 127.0.0.0/8;
        allow 10.0.0.0/8;
        allow 172.16.0.0/12;
        allow 192.168.0.0/16;
        deny all;

        client_max_body_size 32m;              # 10 MB receipt as base64 PNG + prompt
        client_body_buffer_size 32m;           # keep images in memory, not in temp files

        location / {{
            proxy_pass http://vllm;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
            proxy_buffering off;
            proxy_connect_timeout 3s;
            proxy_send_timeout {read_seconds}s;
            proxy_read_timeout {read_seconds}s;  # DESIGN 6.3: 60 s per read
            # vLLM down or hung -> try the other one (completions are stateless, so POST is safe)
            proxy_next_upstream error timeout http_502 http_503 http_504 non_idempotent;
            proxy_next_upstream_tries 2;
            proxy_next_upstream_timeout {read_seconds}s;
        }}
    }}
}}
"""


# --------------------------------------------------------------------------
# Self-test: real gateway (create_app) + in-memory broker + fake vLLM
# --------------------------------------------------------------------------


def _self_test() -> int:  # pragma: no cover - executed manually / in CI
    import tempfile
    import unittest
    import uuid
    from collections import deque

    from PIL import Image

    from ai.gateway import main as gwmain

    TOKEN = "worker-token"
    KEY = "test-key"

    def png_bytes(width: int) -> bytes:
        buf = io.BytesIO()
        Image.new("RGB", (width, 8), (255, 255, 255)).save(buf, format="PNG")
        return buf.getvalue()

    class Msg:
        def __init__(self, broker: "Broker", queue: str, body: bytes):
            self.broker, self.queue, self.body = broker, queue, body
            self.owner: Any = None
            self.settled: str | None = None

        def _release(self) -> None:
            if self.owner is not None:
                self.owner.unacked.discard(self)
                self.owner = None

        async def ack(self) -> None:
            self._release()
            self.settled = "ack"

        async def nack(self, requeue: bool = True) -> None:
            self._release()
            self.settled = "nack"
            if requeue:
                self.broker.queues[self.queue].appendleft(self)
            else:
                self.broker.dlq.append(self)

        async def reject(self, requeue: bool = False) -> None:
            self._release()
            self.settled = "reject"
            (self.broker.queues[self.queue].appendleft if requeue else self.broker.dlq.append)(self)

    class Broker:
        """Stands in for RabbitMQ for the gateway (publish) and for each worker (basic.get)."""

        def __init__(self) -> None:
            self.queues: dict[str, deque] = {"urgent": deque(), "normal": deque()}
            self.dlq: deque = deque()

        async def ensure(self) -> bool:
            return True

        async def publish(self, *, receipt_ref: str, job_ref: str, priority: str) -> None:
            body = json.dumps({"receipt_ref": receipt_ref, "job_ref": job_ref, "priority": priority})
            self.queues[priority].append(Msg(self, priority, body.encode()))

        async def dlq_count(self) -> int:
            return len(self.dlq)

        async def close(self) -> None:
            pass

    class Conn:
        """One worker's AMQP connection; crash() returns unacked messages like RabbitMQ does."""

        def __init__(self, broker: Broker):
            self.broker = broker
            self.unacked: set = set()
            self.connected = True

        async def connect(self) -> None:
            self.connected = True

        async def get(self, priority: str):
            q = self.broker.queues[priority]
            if not q:
                return None
            msg = q.popleft()
            msg.owner = self
            self.unacked.add(msg)
            return msg

        def crash(self) -> None:
            self.connected = False
            for msg in list(self.unacked):
                msg.owner = None
                self.broker.queues[msg.queue].appendleft(msg)
            self.unacked.clear()

        async def close(self) -> None:
            pass

    class FakeVLLM:
        """OpenAI-compatible answers with per-token bytes, like vLLM with logprobs on."""

        def __init__(self) -> None:
            self.calls: list[int] = []  # image width = receipt number
            self.requests: list[httpx.Request] = []
            self.script: dict[int, Any] = {}  # width -> "unreadable" | "garbage" | "hang" | list
            self.healthy = True
            self.hang = asyncio.Event()

        def answer(self, width: int) -> str:
            return json.dumps(
                {"merchant": "ร้านตัวอย่าง", "date": "2026-11-18",
                 "items": [{"name": "ข้าว", "price": "45.00"}, {"name": "น้ำ", "price": "55.00"}],
                 "total": "100.00"},
                ensure_ascii=False,
            )

        async def __call__(self, request: httpx.Request) -> httpx.Response:
            if request.url.path == "/health":
                return httpx.Response(200 if self.healthy else 503)
            assert request.url.path == "/v1/chat/completions", request.url.path
            self.requests.append(request)
            payload = json.loads(request.content)
            url = payload["messages"][1]["content"][0]["image_url"]["url"]
            img = Image.open(io.BytesIO(base64.b64decode(url.split(",", 1)[1])))
            width = img.width
            self.calls.append(width)
            action = self.script.get(width)
            if isinstance(action, list):
                action = action.pop(0) if action else None
            if action == "hang":
                await self.hang.wait()
            if action == "http503":
                return httpx.Response(503)
            text = {
                "unreadable": '{"unreadable": true}',
                "garbage": '{"merchant": "x"}',
            }.get(action, self.answer(width))
            # token pieces: split Thai bytes mid-character to exercise the bytes path
            raw = text.encode("utf-8")
            span = rc.total_value_span(text)
            lo, hi = (len(text[: span[0]].encode()), len(text[: span[1]].encode())) if span else (-1, -1)
            tokens = []
            for i in range(0, len(raw), 3):
                chunk = raw[i : i + 3]
                lp = -0.02 if i < hi and i + len(chunk) > lo else -0.5 if i == 0 else 0.0
                tokens.append({"token": chunk.decode("utf-8", "replace"), "bytes": list(chunk), "logprob": lp})
            return httpx.Response(200, json={
                "model": "receipt-vlm",
                "choices": [{"message": {"role": "assistant", "content": text},
                             "logprobs": {"content": tokens}}],
            })

    def make_settings(worker_id: str, **kw: Any) -> Settings:
        base = dict(
            worker_id=worker_id, gateway_url="http://gateway", internal_token=TOKEN,
            vllm_url="http://nginx:8080", vllm_api_key="vk", read_timeout=60.0,
            idle_poll_seconds=0, wait_backoff_seconds=0, empty_backoff_seconds=0,
            health_cache_seconds=0, result_retry_seconds=2,
        )
        base.update(kw)
        return Settings(**base)

    async def no_sleep(_: float) -> None:
        await asyncio.sleep(0)

    class WorkerTests(unittest.IsolatedAsyncioTestCase):
        async def asyncSetUp(self) -> None:
            self.tmp = tempfile.TemporaryDirectory()
            self.broker = Broker()
            self.now = 1_800_000_000.0
            settings = gwmain.Settings(
                api_keys=(KEY,), data_dir=Path(self.tmp.name), internal_token=TOKEN,
                internal_cidrs="*", vllm_health_urls=(), background_tasks=False,
            )
            self.app = gwmain.create_app(settings, broker=self.broker, clock=lambda: self.now)
            self.lifespan = self.app.router.lifespan_context(self.app)
            await self.lifespan.__aenter__()
            self.gw = self.app.state.gateway
            self.public = httpx.AsyncClient(
                transport=httpx.ASGITransport(app=self.app), base_url="http://gateway",
                headers={"X-API-Key": KEY},
            )
            self.vllm = FakeVLLM()
            self.refs: dict[int, str] = {}
            self.workers: list[Worker] = []

        async def asyncTearDown(self) -> None:
            self.vllm.hang.set()
            for w in self.workers:
                await w.gateway.close()
                await w.vllm.close()
            await self.public.aclose()
            await self.lifespan.__aexit__(None, None, None)
            self.tmp.cleanup()

        def worker(self, worker_id: str, gateway_transport: Any = None, **kw: Any) -> Worker:
            s = make_settings(worker_id, **kw)
            gw_http = httpx.AsyncClient(
                transport=gateway_transport or httpx.ASGITransport(app=self.app),
                base_url=s.gateway_url,
            )
            v_http = httpx.AsyncClient(transport=httpx.MockTransport(self.vllm), base_url=s.vllm_url)
            w = Worker(s, gateway=GatewayClient(s, gw_http), vllm=VLLMClient(s, v_http),
                       amqp=Conn(self.broker), sleep=no_sleep)
            self.workers.append(w)
            return w

        async def submit(self, n: int, priority: str) -> str:
            ref = str(uuid.uuid4())
            r = await self.public.post(
                "/v1/receipts",
                data={"receipt_ref": ref, "job_ref": str(uuid.uuid4()), "priority": priority},
                files={"file": ("x.png", png_bytes(n), "image/png")},
            )
            self.assertEqual(r.status_code, 202, r.text)
            self.refs[n] = ref
            return ref

        async def status(self, n: int) -> dict[str, Any]:
            return (await self.public.get(f"/v1/receipts/{self.refs[n]}")).json()

        async def drain(self, *workers: Worker, limit: int = 500) -> None:
            idle = 0
            for _ in range(limit):
                labels = [await w.step() for w in workers]
                idle = idle + 1 if all(x == "idle" for x in labels) else 0
                if idle >= 2:
                    return
            self.fail("workers never went idle")

        # --- tests -----------------------------------------------------------
        async def test_request_shape_and_result(self):
            await self.submit(10, "normal")
            w = self.worker("worker0")
            self.assertEqual(await w.step(), "done")
            req = self.vllm.requests[0]
            self.assertEqual(str(req.url), "http://nginx:8080/v1/chat/completions")
            self.assertEqual(req.headers["authorization"], "Bearer vk")
            p = json.loads(req.content)
            self.assertEqual((p["model"], p["temperature"], p["logprobs"]), ("receipt-vlm", 0, True))
            self.assertEqual(p["messages"][0], {"role": "system", "content": rc.SYSTEM_PROMPT})
            self.assertEqual([c["type"] for c in p["messages"][1]["content"]], ["image_url", "text"])
            self.assertEqual(p["messages"][1]["content"][1]["text"], rc.USER_PROMPT)
            st = await self.status(10)
            self.assertEqual((st["status"], st["attempts"]), ("done", 1))
            res = st["result"]
            self.assertEqual((res["merchant"], res["total"]), ("ร้านตัวอย่าง", "100.00"))
            self.assertEqual(res["items"][0], {"name": "ข้าว", "price": "45.00"})
            # "100.00" straddles 3 of the 3-byte tokens (-0.02 each); the -0.5 first token is not counted
            self.assertAlmostEqual(res["total_confidence"], 2.718281828459045 ** -0.06, places=9)
            self.assertEqual(len(self.broker.queues["normal"]) + len(self.broker.dlq), 0)

        async def test_br10_td_order_single_worker(self):
            cases = [((3, 2), "U1 U2 U3 N1 N2"), ((4, 2), "U1 U2 U3 U4 N1 N2"),
                     ((5, 2), "U1 U2 U3 U4 N1 U5 N2"), ((5, 0), "U1 U2 U3 U4 U5")]
            for (u, n), expected in cases:
                with self.subTest(urgent=u, normal=n):
                    self.vllm.calls.clear()
                    names = {}
                    for i in range(1, n + 1):
                        names[100 + i] = f"N{i}"
                        await self.submit(100 + i, "normal")
                    for i in range(1, u + 1):
                        names[200 + i] = f"U{i}"
                        await self.submit(200 + i, "urgent")
                    w = self.worker(f"w-{u}-{n}")
                    await self.drain(w)
                    self.assertEqual(" ".join(names[x] for x in self.vllm.calls), expected)

        async def test_br10_two_workers_never_more_than_4_urgent_in_a_row(self):
            for i in range(1, 9):
                await self.submit(100 + i, "normal")
            for i in range(1, 11):
                await self.submit(200 + i, "urgent")
            w0, w1 = self.worker("worker0"), self.worker("worker1")
            await self.drain(w0, w1)
            seq = "".join("U" if x > 200 else "N" for x in self.vllm.calls)
            self.assertEqual(len(seq), 18)
            first_n = seq.rfind("N")
            self.assertNotIn("UUUUU", seq[: first_n + 1], seq)  # while normal work waits
            self.assertEqual(sorted(self.vllm.calls), sorted(self.refs))  # each read once

        async def test_br07_three_failures_go_to_dlq(self):
            await self.submit(11, "normal")
            self.vllm.script[11] = "unreadable"
            w = self.worker("worker0")
            self.assertEqual([await w.step() for _ in range(3)], ["queued", "queued", "dead"])
            self.assertEqual(self.vllm.calls, [11, 11, 11])
            st = await self.status(11)
            self.assertEqual((st["status"], st["attempts"]), ("dead", 3))
            self.assertEqual(len(self.broker.dlq), 1)
            self.assertEqual(self.broker.dlq[0].settled, "reject")
            self.assertEqual(await w.step(), "idle")  # never comes back

        async def test_br07_two_failures_then_success(self):
            await self.submit(12, "urgent")
            self.vllm.script[12] = ["garbage", "unreadable", None]
            w = self.worker("worker0")
            self.assertEqual([await w.step() for _ in range(3)], ["queued", "queued", "done"])
            st = await self.status(12)
            self.assertEqual((st["status"], st["attempts"]), ("done", 3))
            self.assertEqual(len(self.broker.dlq), 0)

        async def test_timeout_counts_as_failure(self):
            await self.submit(13, "normal")
            self.vllm.script[13] = ["hang", None]
            w = self.worker("worker0", read_timeout=0.3)
            t0 = time.monotonic()
            self.assertEqual(await w.step(), "queued")
            self.assertLess(time.monotonic() - t0, 2.0)
            self.vllm.hang.set()
            self.assertEqual(await w.step(), "done")
            self.assertEqual((await self.status(13))["attempts"], 2)

        async def test_vllm_down_burns_no_attempt(self):
            await self.submit(14, "normal")
            self.vllm.healthy = False
            w = self.worker("worker0")
            self.assertEqual(await w.step(), "vllm_down")
            self.assertEqual((await self.status(14))["attempts"], 0)
            self.assertEqual(len(self.broker.queues["normal"]), 1)
            self.vllm.healthy = True
            self.assertEqual(await w.step(), "done")

        async def test_vllm_503_is_retried_inside_the_attempt(self):
            await self.submit(15, "normal")
            self.vllm.script[15] = ["http503", None]
            w = self.worker("worker0")
            self.assertEqual(await w.step(), "done")
            self.assertEqual(self.vllm.calls, [15, 15])
            self.assertEqual((await self.status(15))["attempts"], 1)

        async def test_malformed_message_goes_to_dlq(self):
            self.broker.queues["normal"].append(Msg(self.broker, "normal", b"not json"))
            await self.submit(16, "normal")
            w = self.worker("worker0")
            # I4 says normal (1 waiting receipt); the junk message is first in the queue
            self.assertEqual(await w.step(), "malformed")
            self.assertEqual(await w.step(), "done")
            self.assertEqual(len(self.broker.dlq), 1)

        async def test_result_retried_until_gateway_answers(self):
            await self.submit(17, "normal")
            asgi = httpx.ASGITransport(app=self.app)
            fails = {"left": 2}

            class Flaky(httpx.AsyncBaseTransport):
                async def handle_async_request(self, request):
                    if request.url.path.endswith("/result") and fails["left"]:
                        fails["left"] -= 1
                        raise httpx.ConnectError("gateway restarting")
                    return await asgi.handle_async_request(request)

            w = self.worker("worker0", gateway_transport=Flaky())
            self.assertEqual(await w.step(), "done")
            self.assertEqual(fails["left"], 0)
            self.assertEqual((await self.status(17))["status"], "done")

        async def test_worker_crash_loses_nothing(self):
            """DESIGN 7 / NFR-06: kill a worker mid-read; every receipt ends with exactly one result."""
            for i in range(1, 21):
                await self.submit(300 + i, "normal")
            self.vllm.script[305] = ["hang", None]
            w0, w1 = self.worker("worker0"), self.worker("worker1")
            # w0 reads 301..304, then hangs on 305
            for _ in range(4):
                self.assertEqual(await w0.step(), "done")
            crashed = asyncio.create_task(w0.step())
            while 305 not in self.vllm.calls:
                await asyncio.sleep(0.01)
            crashed.cancel()  # the process dies mid-read ...
            await asyncio.gather(crashed, return_exceptions=True)
            w0.amqp.crash()  # ... RabbitMQ requeues its unacked message
            self.assertEqual(self.broker.queues["normal"][0].body.decode().count(self.refs[305]), 1)

            # w1 meets the redelivered 305 while w0's lease still holds -> wait, message goes back
            self.assertEqual(await w1.step(), "wait")
            self.now += 16  # heartbeat silent > 15 s
            await w1.gateway.heartbeat(True)
            await self.gw.monitor_once()  # gateway releases w0's lease (B06 3.6)
            alive = (await self.public.get("/v1/queue")).json()
            self.assertEqual(alive.get("workers_alive"), 1, alive)
            await self.drain(w1)

            statuses = [await self.status(300 + i) for i in range(1, 21)]
            self.assertTrue(all(s["status"] == "done" for s in statuses), statuses)
            self.assertEqual((await self.status(305))["attempts"], 2)
            reads = [c for c in self.vllm.calls if c != 305]
            self.assertEqual(sorted(reads), list(range(301, 305)) + list(range(306, 321)))
            self.assertEqual(len(self.broker.queues["normal"]) + len(self.broker.dlq), 0)
            # w0's late result (it hung, not died) is dropped: first result only
            late = await w0.gateway.result(self.refs[305], {"worker_id": "worker0", "ok": False,
                                                            "error": "timeout_60s"})
            self.assertEqual(late["outcome"], "skip")
            self.assertEqual((await self.status(305))["status"], "done")

        async def test_crash_on_same_receipt_three_times_goes_to_dlq(self):
            await self.submit(18, "normal")
            self.vllm.script[18] = ["hang", "hang", "hang"]
            for k in range(3):
                w = self.worker(f"crashy{k}")
                task = asyncio.create_task(w.step())
                while self.vllm.calls.count(18) < k + 1:
                    await asyncio.sleep(0.01)
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
                w.amqp.crash()
                self.now += 16
                await self.gw.monitor_once()
            last = self.worker("survivor")
            self.assertEqual(await last.step(), "dead")
            self.assertEqual(len(self.broker.dlq), 1)
            st = await self.status(18)
            self.assertEqual((st["status"], st["attempts"]), ("dead", 3))

        async def test_g5_stale_copy_acked_without_read(self):
            job = str(uuid.uuid4())
            ref = str(uuid.uuid4())
            r = await self.public.post(
                "/v1/receipts", data={"receipt_ref": ref, "job_ref": job, "priority": "normal"},
                files={"file": ("x.png", png_bytes(19), "image/png")},
            )
            self.assertEqual(r.status_code, 202)
            r = await self.public.post(f"/v1/jobs/{job}/urgent")
            self.assertIn(r.status_code, (200, 202), r.text)
            w = self.worker("worker0")
            await self.drain(w)
            self.assertEqual(self.vllm.calls, [19])  # read once, from the urgent copy
            self.assertEqual(len(self.broker.queues["normal"]), 1)  # stale copy waits for a normal turn
            await self.submit(20, "normal")
            await self.drain(w)
            self.assertEqual(self.vllm.calls, [19, 20])
            self.assertEqual(w.stats["skip"], 1)  # stale copy acked, not read
            self.assertEqual(len(self.broker.queues["normal"]) + len(self.broker.queues["urgent"]), 0)

        async def test_heartbeat_only_while_connected(self):
            w = self.worker("worker0", heartbeat_seconds=0)
            calls = []
            orig = w.gateway.heartbeat

            async def hb(ok):
                calls.append(ok)
                if len(calls) >= 2:
                    w.stopping.set()
                return await orig(ok)

            w.gateway.heartbeat = hb
            await w.heartbeat_loop()
            self.assertEqual(len(calls), 2)
            w.stopping.clear()
            w.amqp.connected = False
            w._sleep_fn = None
            w.s.heartbeat_seconds = 0.01
            task = asyncio.create_task(w.heartbeat_loop())
            await asyncio.sleep(0.05)
            w.stopping.set()
            await task
            self.assertEqual(len(calls), 2)

        def test_nginx_conf(self):
            conf = nginx_conf()
            for needle in ("least_conn;", "server 127.0.0.1:8001", "server 127.0.0.1:8002",
                           "listen 8080;", "proxy_read_timeout 60s;", "non_idempotent",
                           "proxy_next_upstream error timeout"):
                self.assertIn(needle, conf)

        def test_settings_guard(self):
            with self.assertRaises(ValueError):
                Settings(worker_id="w0", read_timeout=61)
            with self.assertRaises(ValueError):
                Settings(worker_id="bad id")

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(WorkerTests)
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if outcome.wasSuccessful() else 1


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="ReceiptDesk GPU worker (B09)")
    parser.add_argument("--self-test", action="store_true", help="run the built-in tests and exit")
    parser.add_argument("--nginx-conf", action="store_true", help="print ai/nginx/nginx.conf and exit")
    parser.add_argument("--upstreams", default="127.0.0.1:8001,127.0.0.1:8002",
                        help="vLLM servers for --nginx-conf")
    parser.add_argument("--listen", default="8080", help="NGINX listen for --nginx-conf")
    args = parser.parse_args()

    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)  # one line per request is noise
    if args.nginx_conf:
        ups = tuple(u.strip() for u in args.upstreams.split(",") if u.strip())
        sys.stdout.write(nginx_conf(ups, args.listen))
        return
    if args.self_test:
        logging.getLogger().setLevel(logging.WARNING)
        raise SystemExit(_self_test())

    try:
        settings = Settings.from_env()
    except ValueError as exc:
        raise SystemExit(str(exc))

    async def runner() -> None:
        worker = Worker(settings)
        loop = asyncio.get_running_loop()
        task = asyncio.current_task()

        def on_signal() -> None:
            if worker.stopping.is_set():
                assert task is not None
                task.cancel()  # second signal: stop now; RabbitMQ requeues the open message
            else:
                log.info("stopping after the current receipt")
                worker.stopping.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, on_signal)
            except NotImplementedError:  # pragma: no cover - Windows
                pass
        await worker.run()

    try:
        asyncio.run(runner())
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass


if __name__ == "__main__":
    main()
