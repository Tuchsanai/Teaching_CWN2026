"""ReceiptDesk API gateway on the GPU machine (FastAPI + SQLite).

Public routes (DESIGN 5.2 – 5.7, header X-API-Key except G1):
  G1 GET    /healthz
  G2 POST   /v1/receipts
  G3 GET    /v1/receipts/{receipt_ref}
  G4 GET    /v1/jobs/{job_ref}
  G5 POST   /v1/jobs/{job_ref}/urgent
  G6 GET    /v1/queue
  G7 DELETE /v1/receipts/{receipt_ref}

Internal routes for GPU workers (DESIGN 5.8 + B06 3.2; loopback/private
networks only, plus X-Internal-Token when GATEWAY_INTERNAL_TOKEN is set):
  I1 POST /internal/receipts/{receipt_ref}/claim
  I2 POST /internal/receipts/{receipt_ref}/result
  I3 POST /internal/workers/{worker_id}/heartbeat
  I4 POST /internal/workers/{worker_id}/next

State lives in SQLite (gateway.db) next to a temporary image folder. Queue
rules come from ai/queue/topology.py (B07). The gateway never receives shop or
client names or original file names (NFR-07): only the image bytes, random
UUID references, priority and accepted_at. Logs carry references, statuses and
times only. Images are deleted as soon as a receipt finishes; results are
deleted by G7 or 60 minutes after the receipt finished.

Run:   uvicorn ai.gateway.main:app --host 0.0.0.0 --port 8000 \
           --ssl-certfile cert.pem --ssl-keyfile key.pem
  or   python -m ai.gateway.main            (reads GATEWAY_TLS_CERT / _KEY)
Test:  python -B -m ai.gateway.main --self-test   (in-memory broker, no RabbitMQ)

Environment
  GATEWAY_API_KEYS        comma-separated accepted keys (or GATEWAY_API_KEY)
  GATEWAY_DATA_DIR        folder for gateway.db and images/ (default ./gateway-data)
  RABBITMQ_URL            amqp://user:pass@127.0.0.1:5672/
  GATEWAY_INTERNAL_TOKEN  optional shared secret for /internal/* (X-Internal-Token)
  INTERNAL_ALLOW_CIDRS    default loopback + RFC 1918 ranges ("*" = any)
  VLLM_HEALTH_URLS        default http://127.0.0.1:8001/health,http://127.0.0.1:8002/health
  LEASE_SECONDS=90 HEARTBEAT_TIMEOUT_SECONDS=15 RETENTION_MINUTES=60
  GUARD_MINUTES=115 SECONDS_PER_RECEIPT=15 URGENT_JOB_LIMIT=10
"""

from __future__ import annotations

import asyncio
import base64
import hmac
import io
import ipaddress
import json
import logging
import os
import re
import sqlite3
import sys
import time
import uuid
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterator, Literal, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field, ValidationError

try:
    from ai.queue import topology
except ImportError:  # started as a plain script from inside ai/gateway
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from ai.queue import topology


log = logging.getLogger("receiptdesk.gateway")
decision_log = logging.getLogger("receiptdesk.gateway.decisions")

PUBLIC_STATUS = {
    "accepting": "queued",
    "queued": "queued",
    "processing": "processing",
    "done": "done",
    "dead": "dead",
}
FINISHED = ("done", "dead")
WORKER_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,64}$")
DEFAULT_INTERNAL_CIDRS = "127.0.0.0/8,::1/128,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
BROKER_RETRY_AFTER = 10
RESERVATION_TTL_SECONDS = 30
MULTIPART_OVERHEAD = 64 * 1024


# --------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name, "").strip()
    return int(value) if value else default


@dataclass
class Settings:
    api_keys: tuple[str, ...]
    data_dir: Path
    rabbitmq_url: str = "amqp://guest:guest@127.0.0.1:5672/"
    internal_token: str = ""
    internal_cidrs: str = DEFAULT_INTERNAL_CIDRS
    vllm_health_urls: tuple[str, ...] = ()
    vllm_api_key: str = ""
    max_file_bytes: int = 10 * 1024 * 1024
    lease_seconds: int = 90
    heartbeat_timeout_seconds: int = 15
    retention_minutes: int = 60
    guard_minutes: int = 115
    seconds_per_receipt: int = 15
    urgent_job_limit: int = 10
    background_tasks: bool = True

    @classmethod
    def from_env(cls) -> "Settings":
        raw = os.environ.get("GATEWAY_API_KEYS") or os.environ.get("GATEWAY_API_KEY", "")
        keys = tuple(k.strip() for k in raw.split(",") if k.strip())
        vllm = os.environ.get(
            "VLLM_HEALTH_URLS",
            "http://127.0.0.1:8001/health,http://127.0.0.1:8002/health",
        )
        return cls(
            api_keys=keys,
            data_dir=Path(os.environ.get("GATEWAY_DATA_DIR", "./gateway-data")),
            rabbitmq_url=os.environ.get("RABBITMQ_URL", cls.rabbitmq_url),
            internal_token=os.environ.get("GATEWAY_INTERNAL_TOKEN", ""),
            internal_cidrs=os.environ.get("INTERNAL_ALLOW_CIDRS", DEFAULT_INTERNAL_CIDRS),
            vllm_health_urls=tuple(u.strip() for u in vllm.split(",") if u.strip()),
            vllm_api_key=os.environ.get("VLLM_API_KEY", ""),
            lease_seconds=_env_int("LEASE_SECONDS", 90),
            heartbeat_timeout_seconds=_env_int("HEARTBEAT_TIMEOUT_SECONDS", 15),
            retention_minutes=_env_int("RETENTION_MINUTES", 60),
            guard_minutes=_env_int("GUARD_MINUTES", 115),
            seconds_per_receipt=_env_int("SECONDS_PER_RECEIPT", 15),
            urgent_job_limit=_env_int("URGENT_JOB_LIMIT", 10),
        )


# --------------------------------------------------------------------------
# Errors and small helpers
# --------------------------------------------------------------------------


class ApiError(Exception):
    def __init__(self, status: int, body: dict[str, Any], headers: dict[str, str] | None = None):
        super().__init__(body.get("error", "error"))
        self.status = status
        self.body = body
        self.headers = headers or {}


class BrokerUnavailable(Exception):
    pass


def bad_request(detail: str) -> ApiError:
    return ApiError(400, {"error": "bad_request", "detail": detail})


def broker_unavailable() -> ApiError:
    return ApiError(
        503, {"error": "broker_unavailable"}, {"Retry-After": str(BROKER_RETRY_AFTER)}
    )


def queue_full(body: topology.QueueFull) -> ApiError:
    return ApiError(429, dict(body), {"Retry-After": str(body["retry_after_seconds"])})


def canonical_uuid(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        return str(uuid.UUID(value.strip()))
    except (ValueError, AttributeError):
        return None


def iso(ts: float | None) -> str | None:
    if ts is None:
        return None
    return (
        datetime.fromtimestamp(ts, tz=timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def parse_time(value: str) -> float:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    moment = datetime.fromisoformat(text)
    if moment.tzinfo is None:
        raise ValueError("accepted_at needs a time zone")
    return moment.timestamp()


def money(value: Any) -> str | None:
    """Return a 2-decimal string such as "100.00" or None if not a number."""
    if value is None or isinstance(value, bool):
        return None
    try:
        amount = Decimal(str(value).replace(",", "").strip())
    except (InvalidOperation, ValueError):
        return None
    if not amount.is_finite():
        return None
    return str(amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def sniff_file(data: bytes) -> tuple[str, str] | None:
    """Return (mime_type, extension) for JPG, PNG or a 1-page PDF."""
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg", ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png", ".png"
    if data.startswith(b"%PDF-") and pdf_has_one_page(data):
        return "application/pdf", ".pdf"
    return None


def pdf_has_one_page(data: bytes) -> bool:
    try:
        from pypdf import PdfReader
    except ImportError:
        PdfReader = None  # type: ignore[assignment]
    if PdfReader is not None:
        try:
            reader = PdfReader(io.BytesIO(data))
            if reader.is_encrypted:
                return False
            return len(reader.pages) == 1
        except Exception:
            return False
    # Fallback without pypdf: reject what is clearly wrong, trust the web check
    # (BR-03 in web/lib/rules.ts) when page objects sit in compressed streams.
    if b"/Encrypt" in data:
        return False
    pages = len(re.findall(rb"/Type\s*/Page(?![A-Za-z])", data))
    return pages <= 1


# --------------------------------------------------------------------------
# SQLite store
# --------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS gw_jobs (
    job_ref     TEXT PRIMARY KEY,
    priority    TEXT NOT NULL CHECK (priority IN ('normal', 'urgent')),
    created_at  REAL NOT NULL,
    urgent_at   REAL
);
CREATE TABLE IF NOT EXISTS gw_receipts (
    receipt_ref  TEXT PRIMARY KEY,
    job_ref      TEXT NOT NULL,
    priority     TEXT NOT NULL CHECK (priority IN ('normal', 'urgent')),
    status       TEXT NOT NULL
                 CHECK (status IN ('accepting', 'queued', 'processing', 'done', 'dead')),
    attempts     INTEGER NOT NULL DEFAULT 0,
    mime_type    TEXT NOT NULL,
    image_path   TEXT,
    accepted_at  REAL NOT NULL,
    queued_at    REAL NOT NULL,
    worker_id    TEXT,
    lease_until  REAL,
    claimed_at   REAL,
    claim_seq    INTEGER,
    finished_at  REAL,
    result_json  TEXT,
    error        TEXT
);
CREATE INDEX IF NOT EXISTS gw_receipts_queue ON gw_receipts (status, priority, queued_at);
CREATE INDEX IF NOT EXISTS gw_receipts_job ON gw_receipts (job_ref);
CREATE TABLE IF NOT EXISTS gw_state (
    key    TEXT PRIMARY KEY,
    value  INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS gw_workers (
    worker_id  TEXT PRIMARY KEY,
    last_seen  REAL NOT NULL,
    alive      INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS gw_reads (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    worker_id    TEXT NOT NULL,
    finished_at  REAL NOT NULL,
    seconds      REAL,
    ok           INTEGER NOT NULL
);
INSERT OR IGNORE INTO gw_state (key, value) VALUES ('urgent_streak', 0), ('claim_seq', 0);
"""


class Store:
    def __init__(self, path: Path):
        self.db = sqlite3.connect(str(path), isolation_level=None, check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript(SCHEMA)

    @contextmanager
    def tx(self) -> Iterator[sqlite3.Connection]:
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield self.db
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        else:
            self.db.execute("COMMIT")

    def close(self) -> None:
        self.db.close()

    # reads -------------------------------------------------------------
    def receipt(self, ref: str) -> sqlite3.Row | None:
        return self.db.execute(
            "SELECT * FROM gw_receipts WHERE receipt_ref = ?", (ref,)
        ).fetchone()

    def job(self, ref: str) -> sqlite3.Row | None:
        return self.db.execute("SELECT * FROM gw_jobs WHERE job_ref = ?", (ref,)).fetchone()

    def job_receipts(self, ref: str) -> list[sqlite3.Row]:
        return self.db.execute(
            "SELECT * FROM gw_receipts WHERE job_ref = ? ORDER BY queued_at, receipt_ref",
            (ref,),
        ).fetchall()

    def pending(self, priority: str) -> int:
        """Logical receipts held against the queue limit (B07 check_capacity)."""
        return self.db.execute(
            "SELECT count(*) FROM gw_receipts WHERE priority = ?"
            " AND status IN ('accepting', 'queued', 'processing')",
            (priority,),
        ).fetchone()[0]

    def waiting(self, priority: str) -> int:
        """Receipts really waiting in a queue (nq / uq of B06 3.1)."""
        return self.db.execute(
            "SELECT count(*) FROM gw_receipts WHERE priority = ? AND status = 'queued'",
            (priority,),
        ).fetchone()[0]

    def state(self, key: str) -> int:
        return self.db.execute("SELECT value FROM gw_state WHERE key = ?", (key,)).fetchone()[0]

    def set_state(self, key: str, value: int) -> None:
        self.db.execute("UPDATE gw_state SET value = ? WHERE key = ?", (value, key))

    def workers_alive(self, now: float, timeout: int) -> int:
        return self.db.execute(
            "SELECT count(*) FROM gw_workers WHERE last_seen >= ?", (now - timeout,)
        ).fetchone()[0]

    def dead_count(self) -> int:
        return self.db.execute(
            "SELECT count(*) FROM gw_receipts WHERE status = 'dead'"
        ).fetchone()[0]


# --------------------------------------------------------------------------
# RabbitMQ publisher (through topology.py)
# --------------------------------------------------------------------------


class AmqpBroker:
    """Publisher channel with confirms. Reconnects on demand."""

    def __init__(self, url: str):
        self.url = url
        self.connection: Any = None
        self.channel: Any = None
        self._connect_lock = asyncio.Lock()

    @property
    def ready(self) -> bool:
        return self.channel is not None and not self.channel.is_closed

    async def ensure(self) -> bool:
        if self.ready:
            return True
        async with self._connect_lock:
            if self.ready:
                return True
            await self.close()
            try:
                import aio_pika

                self.connection = await asyncio.wait_for(
                    aio_pika.connect(self.url, timeout=5), timeout=8
                )
                self.channel = await self.connection.channel(
                    publisher_confirms=True, on_return_raises=True
                )
                await topology.declare_topology(self.channel)
                log.info("rabbitmq connected")
                return True
            except Exception as exc:  # broker down, auth, network
                log.warning("rabbitmq unavailable: %s", type(exc).__name__)
                await self.close()
                return False

    async def publish(self, *, receipt_ref: str, job_ref: str, priority: str) -> None:
        if not await self.ensure():
            raise BrokerUnavailable()
        try:
            await asyncio.wait_for(
                topology.publish_receipt(
                    self.channel, receipt_ref=receipt_ref, job_ref=job_ref, priority=priority
                ),
                timeout=10,
            )
        except Exception as exc:
            log.warning("publish failed receipt=%s: %s", receipt_ref, type(exc).__name__)
            await self.close()
            raise BrokerUnavailable() from exc

    async def dlq_count(self) -> int | None:
        if not await self.ensure():
            return None
        try:
            queue = await self.channel.declare_queue(topology.DLQ, durable=True)
            return int(queue.declaration_result.message_count)
        except Exception:
            await self.close()
            return None

    async def close(self) -> None:
        connection, self.connection, self.channel = self.connection, None, None
        if connection is not None:
            try:
                await connection.close()
            except Exception:
                pass


# --------------------------------------------------------------------------
# Gateway core
# --------------------------------------------------------------------------


@dataclass
class Gateway:
    settings: Settings
    broker: Any
    clock: Any = time.time
    store: Store | None = None
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    reserved: dict[str, float] = field(default_factory=dict)  # worker_id -> time
    vllm_up: int | None = None
    _tasks: list[asyncio.Task] = field(default_factory=list)
    _last_purge: float = 0.0

    @property
    def images(self) -> Path:
        return self.settings.data_dir / "images"

    @property
    def db(self) -> Store:
        assert self.store is not None, "gateway not started"
        return self.store

    # lifecycle -----------------------------------------------------------
    async def start(self) -> None:
        self.images.mkdir(parents=True, exist_ok=True)
        self.store = Store(self.settings.data_dir / "gateway.db")
        self._recover()
        if self.settings.background_tasks:
            self._tasks = [
                asyncio.create_task(self._loop(self.monitor_once, 1.0)),
                asyncio.create_task(self._loop(self.probe_vllm, 5.0)),
                asyncio.create_task(self.broker.ensure()),
            ]

    async def stop(self) -> None:
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        await self.broker.close()
        if self.store is not None:
            self.store.close()
            self.store = None

    def _recover(self) -> None:
        """A 202 was never sent for rows left in 'accepting': drop them."""
        rows = self.db.db.execute(
            "SELECT receipt_ref, image_path FROM gw_receipts WHERE status = 'accepting'"
        ).fetchall()
        with self.db.tx() as db:
            db.execute("DELETE FROM gw_receipts WHERE status = 'accepting'")
            self._drop_empty_jobs(db)
        for row in rows:
            self._remove_file(row["image_path"])

    async def _loop(self, fn, every: float) -> None:
        while True:
            try:
                await fn()
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("background task failed")
            await asyncio.sleep(every)

    # helpers -------------------------------------------------------------
    def now(self) -> float:
        return float(self.clock())

    def workers_alive(self) -> int:
        return self.db.workers_alive(self.now(), self.settings.heartbeat_timeout_seconds)

    def _remove_file(self, path: str | None) -> None:
        if path:
            try:
                Path(path).unlink(missing_ok=True)
            except OSError:
                log.warning("could not delete image file")

    @staticmethod
    def _drop_empty_jobs(db: sqlite3.Connection) -> None:
        db.execute(
            "DELETE FROM gw_jobs WHERE job_ref NOT IN (SELECT DISTINCT job_ref FROM gw_receipts)"
        )

    def seconds_per_receipt(self) -> float:
        rows = self.db.db.execute(
            "SELECT seconds FROM gw_reads WHERE seconds IS NOT NULL"
            " ORDER BY id DESC LIMIT 20"
        ).fetchall()
        measured = sum(r[0] for r in rows) / len(rows) if len(rows) >= 3 else 0.0
        return max(float(self.settings.seconds_per_receipt), measured)

    def deadline_guard(self) -> bool:
        """B06 3.3: true if a waiting normal receipt would finish after GUARD_MINUTES."""
        rows = self.db.db.execute(
            "SELECT accepted_at FROM gw_receipts WHERE status = 'queued'"
            " AND priority = 'normal' ORDER BY queued_at, receipt_ref"
        ).fetchall()
        if not rows:
            return False
        now = self.now()
        per = self.seconds_per_receipt() / max(1, self.workers_alive())
        worst = max(now - row[0] + i * per for i, row in enumerate(rows, start=1))
        return worst >= self.settings.guard_minutes * 60

    def view(self, row: sqlite3.Row, *, with_job: bool = False) -> dict[str, Any]:
        item: dict[str, Any] = {"receipt_ref": row["receipt_ref"]}
        if with_job:
            item["job_ref"] = row["job_ref"]
        item.update(
            status=PUBLIC_STATUS[row["status"]],
            priority=row["priority"],
            attempts=row["attempts"],
            queued_at=iso(row["queued_at"]),
        )
        if row["status"] in FINISHED:
            item["finished_at"] = iso(row["finished_at"])
        if row["status"] == "done" and row["result_json"]:
            item["result"] = json.loads(row["result_json"])
        if row["status"] == "dead":
            item["error"] = row["error"] or "unreadable_image"
        return item

    def _log_decision(self, worker: str, queue: str, result: str, reason: str, ref: str = "-") -> None:
        decision_log.info(
            "ts=%s worker=%s queue=%s result=%s streak=%d nq=%d uq=%d reason=%s receipt=%s",
            iso(self.now()), worker, queue, result, self.db.state("urgent_streak"),
            self.db.waiting("normal"), self.db.waiting("urgent"), reason, ref,
        )

    async def _promote_rows(self, rows: list[sqlite3.Row]) -> int:
        """Publish urgent copies then switch rows to urgent. Caller holds self.lock.

        Old normal messages stay in RabbitMQ and are answered "skip" at I1
        because msg_priority no longer matches (B06 3.4).
        """
        for row in rows:
            await self.broker.publish(
                receipt_ref=row["receipt_ref"], job_ref=row["job_ref"], priority="urgent"
            )
        with self.db.tx() as db:
            db.executemany(
                "UPDATE gw_receipts SET priority = 'urgent' WHERE receipt_ref = ?",
                [(row["receipt_ref"],) for row in rows],
            )
        return len(rows)

    async def _maybe_promote_requeued(self, ref: str) -> bool:
        """A receipt of an urgent job went back to the queue as normal."""
        row = self.db.receipt(ref)
        if row is None or row["status"] != "queued" or row["priority"] != "normal":
            return False
        job = self.db.job(row["job_ref"])
        if job is None or job["priority"] != "urgent":
            return False
        full = topology.check_capacity(
            "urgent", self.db.pending("urgent"), workers_alive=self.workers_alive()
        )
        if full:
            return False
        try:
            await self._promote_rows([row])
        except BrokerUnavailable:
            return False
        return True

    # background ----------------------------------------------------------
    async def monitor_once(self) -> None:
        """Heartbeat watchdog (B06 3.6), stale reservations and retention."""
        now = self.now()
        timeout = self.settings.heartbeat_timeout_seconds
        async with self.lock:
            for worker, since in list(self.reserved.items()):
                if now - since > RESERVATION_TTL_SECONDS:
                    self.reserved.pop(worker, None)
            silent = [
                r["worker_id"]
                for r in self.db.db.execute(
                    "SELECT worker_id FROM gw_workers WHERE alive = 1 AND last_seen < ?",
                    (now - timeout,),
                )
            ]
            released: list[str] = []
            for worker in silent:
                self.reserved.pop(worker, None)
                refs = [
                    r[0]
                    for r in self.db.db.execute(
                        "SELECT receipt_ref FROM gw_receipts"
                        " WHERE status = 'processing' AND worker_id = ?",
                        (worker,),
                    )
                ]
                with self.db.tx() as db:
                    db.execute("UPDATE gw_workers SET alive = 0 WHERE worker_id = ?", (worker,))
                    db.execute(
                        "UPDATE gw_receipts SET status = 'queued', worker_id = NULL,"
                        " lease_until = NULL WHERE status = 'processing' AND worker_id = ?",
                        (worker,),
                    )
                log.warning("worker %s silent > %ss, released %d receipt(s)", worker, timeout, len(refs))
                released.extend(refs)
            for ref in released:
                await self._maybe_promote_requeued(ref)

        if now - self._last_purge >= 60:
            self._last_purge = now
            await self.purge(now)

    async def purge(self, now: float | None = None) -> int:
        """Delete results 60 minutes after finish (NFR-07) and orphan images."""
        now = self.now() if now is None else now
        cutoff = now - self.settings.retention_minutes * 60
        async with self.lock:
            rows = self.db.db.execute(
                "SELECT receipt_ref, image_path FROM gw_receipts"
                " WHERE status IN ('done', 'dead') AND finished_at < ?",
                (cutoff,),
            ).fetchall()
            with self.db.tx() as db:
                db.executemany(
                    "DELETE FROM gw_receipts WHERE receipt_ref = ?",
                    [(r["receipt_ref"],) for r in rows],
                )
                self._drop_empty_jobs(db)
                db.execute("DELETE FROM gw_reads WHERE finished_at < ?", (now - 3600,))
            for row in rows:
                self._remove_file(row["image_path"])
            known = {
                r[0]
                for r in self.db.db.execute(
                    "SELECT image_path FROM gw_receipts WHERE image_path IS NOT NULL"
                )
            }
        for path in self.images.glob("*"):
            try:
                if str(path) not in known and path.stat().st_mtime < now - 600:
                    path.unlink(missing_ok=True)
            except OSError:
                pass
        return len(rows)

    async def probe_vllm(self) -> None:
        urls = self.settings.vllm_health_urls
        if not urls:
            self.vllm_up = None
            return

        def check(url: str) -> bool:
            import urllib.request

            request = urllib.request.Request(url)
            if self.settings.vllm_api_key:
                request.add_header("Authorization", f"Bearer {self.settings.vllm_api_key}")
            try:
                with urllib.request.urlopen(request, timeout=2) as response:  # noqa: S310
                    return 200 <= response.status < 300
            except Exception:
                return False

        results = await asyncio.gather(*(asyncio.to_thread(check, u) for u in urls))
        self.vllm_up = sum(results)


# --------------------------------------------------------------------------
# Request bodies for internal routes
# --------------------------------------------------------------------------


class ClaimBody(BaseModel):
    worker_id: str
    queue: Optional[Literal["urgent", "normal"]] = None
    msg_priority: Optional[Literal["urgent", "normal"]] = None
    inline_image: bool = False


class Item(BaseModel):
    name: Optional[str] = None
    price: Any = None


class ReadResult(BaseModel):
    merchant: Optional[str] = None
    date: Optional[str] = None
    items: list[Item] = Field(default_factory=list)
    total: Any = None
    total_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    model: Optional[str] = None


class ResultBody(BaseModel):
    worker_id: str
    ok: bool
    result: Optional[ReadResult] = None
    error: Optional[str] = Field(default=None, max_length=64)
    read_seconds: Optional[float] = Field(default=None, ge=0.0, le=3600.0)


class HeartbeatBody(BaseModel):
    vllm_ok: Optional[bool] = None


def parse_body(model: type[BaseModel], raw: bytes) -> Any:
    try:
        data = json.loads(raw or b"{}")
        return model.model_validate(data)
    except (ValueError, ValidationError) as exc:
        raise bad_request(str(exc).splitlines()[0][:200]) from exc


# --------------------------------------------------------------------------
# App
# --------------------------------------------------------------------------


def create_app(
    settings: Settings | None = None, broker: Any = None, clock: Any = None
) -> FastAPI:
    settings = settings or Settings.from_env()
    gw = Gateway(
        settings=settings,
        broker=broker if broker is not None else AmqpBroker(settings.rabbitmq_url),
        clock=clock or time.time,
    )
    allowed_nets = (
        None
        if settings.internal_cidrs.strip() == "*"
        else [
            ipaddress.ip_network(c.strip(), strict=False)
            for c in settings.internal_cidrs.split(",")
            if c.strip()
        ]
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if not settings.api_keys:
            log.warning("GATEWAY_API_KEYS is empty: every /v1 request will be refused")
        await gw.start()
        try:
            yield
        finally:
            await gw.stop()

    app = FastAPI(title="ReceiptDesk gateway", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.gateway = gw

    @app.exception_handler(ApiError)
    async def api_error(_: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(exc.body, status_code=exc.status, headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse({"error": "bad_request", "detail": "invalid request"}, status_code=400)

    # -- guards -------------------------------------------------------------
    def require_api_key(request: Request) -> None:
        key = request.headers.get("x-api-key")
        if not key:
            raise ApiError(401, {"error": "missing_api_key"})
        supplied = key.encode()
        if not any(hmac.compare_digest(supplied, k.encode()) for k in settings.api_keys):
            raise ApiError(403, {"error": "invalid_api_key"})

    def require_internal(request: Request) -> None:
        if allowed_nets is not None:
            host = request.client.host if request.client else ""
            try:
                address = ipaddress.ip_address(host)
            except ValueError:
                raise ApiError(403, {"error": "internal_only"})
            if not any(address in net for net in allowed_nets):
                raise ApiError(403, {"error": "internal_only"})
        if settings.internal_token:
            token = request.headers.get("x-internal-token", "")
            if not hmac.compare_digest(token.encode(), settings.internal_token.encode()):
                raise ApiError(403, {"error": "internal_only"})

    def worker_name(worker_id: str) -> str:
        if not WORKER_ID_RE.match(worker_id):
            raise bad_request("worker_id must match [A-Za-z0-9_.:-]{1,64}")
        return worker_id

    # -- G1 -----------------------------------------------------------------
    @app.get("/healthz")
    async def healthz() -> JSONResponse:
        try:
            gw.db.db.execute("SELECT 1").fetchone()
            db_ok = True
        except Exception:
            db_ok = False
        broker_ok = await gw.broker.ensure()
        workers = gw.workers_alive() if db_ok else 0
        vllm = gw.vllm_up
        ready = db_ok and broker_ok and workers > 0 and (vllm is None or vllm > 0)
        body = {
            "status": "ok" if ready else "degraded",
            "gateway": db_ok,
            "rabbitmq": broker_ok,
            "workers_alive": workers,
            "vllm_up": vllm,
        }
        return JSONResponse(body, status_code=200 if ready else 503)

    # -- G2 -----------------------------------------------------------------
    @app.post("/v1/receipts")
    async def submit_receipt(request: Request) -> JSONResponse:
        require_api_key(request)
        length = request.headers.get("content-length")
        if length and length.isdigit() and int(length) > settings.max_file_bytes + MULTIPART_OVERHEAD:
            raise ApiError(413, {"error": "file_too_large", "limit_bytes": settings.max_file_bytes})
        if not request.headers.get("content-type", "").startswith("multipart/form-data"):
            raise bad_request("multipart/form-data required")
        try:
            form = await request.form(max_files=1, max_fields=10)
        except Exception as exc:
            raise bad_request("unreadable multipart body") from exc

        try:
            receipt_ref = canonical_uuid(form.get("receipt_ref"))
            job_ref = canonical_uuid(form.get("job_ref"))
            priority = form.get("priority")
            upload = form.get("file")
            if receipt_ref is None:
                raise bad_request("receipt_ref must be a UUID")
            if job_ref is None:
                raise bad_request("job_ref must be a UUID")
            if priority not in ("normal", "urgent"):
                raise bad_request("priority must be normal or urgent")
            if upload is None or isinstance(upload, str):
                raise bad_request("file is required")
            accepted_raw = form.get("accepted_at")
            accepted_at: float | None = None
            if isinstance(accepted_raw, str) and accepted_raw.strip():
                try:
                    accepted_at = parse_time(accepted_raw)
                except ValueError:
                    raise bad_request("accepted_at must be ISO 8601 with a time zone")

            existing = gw.db.receipt(receipt_ref)
            if existing is not None:
                return JSONResponse(gw.view(existing, with_job=True), status_code=200)

            data = await upload.read(settings.max_file_bytes + 1)
        finally:
            await form.close()

        if len(data) > settings.max_file_bytes:
            raise ApiError(413, {"error": "file_too_large", "limit_bytes": settings.max_file_bytes})
        kind = sniff_file(data)
        if kind is None:
            raise ApiError(415, {"error": "unsupported_file"})
        mime_type, extension = kind

        if not await gw.broker.ensure():
            raise broker_unavailable()

        now = gw.now()
        async with gw.lock:
            existing = gw.db.receipt(receipt_ref)
            if existing is not None:
                return JSONResponse(gw.view(existing, with_job=True), status_code=200)
            job = gw.db.job(job_ref)
            effective = "urgent" if priority == "urgent" or (job and job["priority"] == "urgent") else "normal"
            full = topology.check_capacity(
                effective, gw.db.pending(effective), workers_alive=gw.workers_alive()
            )
            if full:
                log.info("queue full receipt=%s queue=%s", receipt_ref, effective)
                raise queue_full(full)
            image_path = gw.images / f"{receipt_ref}{extension}"
            with gw.db.tx() as db:
                if job is None:
                    db.execute(
                        "INSERT INTO gw_jobs (job_ref, priority, created_at, urgent_at)"
                        " VALUES (?, ?, ?, ?)",
                        (job_ref, effective, now, now if effective == "urgent" else None),
                    )
                db.execute(
                    "INSERT INTO gw_receipts (receipt_ref, job_ref, priority, status,"
                    " mime_type, image_path, accepted_at, queued_at)"
                    " VALUES (?, ?, ?, 'accepting', ?, ?, ?, ?)",
                    (receipt_ref, job_ref, effective, mime_type, str(image_path),
                     accepted_at if accepted_at is not None else now, now),
                )

        try:
            await asyncio.to_thread(_write_durably, image_path, data)
            await gw.broker.publish(receipt_ref=receipt_ref, job_ref=job_ref, priority=effective)
        except (BrokerUnavailable, OSError) as exc:
            async with gw.lock:
                with gw.db.tx() as db:
                    db.execute("DELETE FROM gw_receipts WHERE receipt_ref = ?", (receipt_ref,))
                    gw._drop_empty_jobs(db)
            gw._remove_file(str(image_path))
            if isinstance(exc, OSError):
                log.error("could not store image receipt=%s", receipt_ref)
                raise ApiError(507, {"error": "storage_unavailable"})
            raise broker_unavailable()

        async with gw.lock:
            with gw.db.tx() as db:
                db.execute(
                    "UPDATE gw_receipts SET status = 'queued'"
                    " WHERE receipt_ref = ? AND status = 'accepting'",
                    (receipt_ref,),
                )
            row = gw.db.receipt(receipt_ref)
        log.info("accepted receipt=%s job=%s priority=%s", receipt_ref, job_ref, row["priority"])
        return JSONResponse(
            {"receipt_ref": receipt_ref, "job_ref": job_ref, "status": "queued", "priority": row["priority"]},
            status_code=202,
        )

    # -- G3 -----------------------------------------------------------------
    @app.get("/v1/receipts/{receipt_ref}")
    async def get_receipt(receipt_ref: str, request: Request) -> JSONResponse:
        require_api_key(request)
        ref = canonical_uuid(receipt_ref)
        row = gw.db.receipt(ref) if ref else None
        if row is None:
            raise ApiError(404, {"error": "unknown_receipt"})
        return JSONResponse(gw.view(row, with_job=True))

    # -- G4 -----------------------------------------------------------------
    @app.get("/v1/jobs/{job_ref}")
    async def get_job(job_ref: str, request: Request) -> JSONResponse:
        require_api_key(request)
        ref = canonical_uuid(job_ref)
        job = gw.db.job(ref) if ref else None
        rows = gw.db.job_receipts(ref) if job else []
        if job is None or not rows:
            raise ApiError(404, {"error": "unknown_job"})
        counts = {"queued": 0, "processing": 0, "done": 0, "dead": 0}
        receipts = []
        for row in rows:
            counts[PUBLIC_STATUS[row["status"]]] += 1
            receipts.append(gw.view(row))
        return JSONResponse(
            {"job_ref": ref, "priority": job["priority"], "counts": counts, "receipts": receipts}
        )

    # -- G5 -----------------------------------------------------------------
    @app.post("/v1/jobs/{job_ref}/urgent")
    async def make_urgent(job_ref: str, request: Request) -> JSONResponse:
        require_api_key(request)
        ref = canonical_uuid(job_ref)
        async with gw.lock:
            job = gw.db.job(ref) if ref else None
            rows = gw.db.job_receipts(ref) if job else []
            if job is None or not rows:
                raise ApiError(404, {"error": "unknown_job"})
            if len(rows) > settings.urgent_job_limit:
                raise ApiError(422, {"error": "urgent_too_large", "limit": settings.urgent_job_limit})
            to_move = [
                r for r in rows if r["status"] in ("accepting", "queued") and r["priority"] == "normal"
            ]
            processing = sum(1 for r in rows if r["status"] == "processing" and r["priority"] == "normal")
            finished = sum(1 for r in rows if r["status"] in FINISHED)
            if to_move:
                full = topology.check_capacity(
                    "urgent", gw.db.pending("urgent"),
                    incoming=len(to_move), workers_alive=gw.workers_alive(),
                )
                if full:
                    raise queue_full(full)
                try:
                    moved = await gw._promote_rows(to_move)
                except BrokerUnavailable:
                    raise broker_unavailable()
            else:
                moved = 0
            if job["priority"] != "urgent":
                with gw.db.tx() as db:
                    db.execute(
                        "UPDATE gw_jobs SET priority = 'urgent', urgent_at = ? WHERE job_ref = ?",
                        (gw.now(), ref),
                    )
        log.info("job=%s urgent moved=%d", ref, moved)
        return JSONResponse(
            {"job_ref": ref, "priority": "urgent", "moved": moved,
             "already_processing": processing, "already_finished": finished}
        )

    # -- G6 -----------------------------------------------------------------
    @app.get("/v1/queue")
    async def queue_view(request: Request) -> JSONResponse:
        require_api_key(request)
        now = gw.now()
        dlq = await gw.broker.dlq_count()
        reads = gw.db.db.execute(
            "SELECT count(*) FROM gw_reads WHERE finished_at >= ?", (now - 300,)
        ).fetchone()[0]
        return JSONResponse(
            {
                "normal": {"pending": gw.db.pending("normal"), "limit": topology.QUEUE_LIMITS["normal"]},
                "urgent": {"pending": gw.db.pending("urgent"), "limit": topology.QUEUE_LIMITS["urgent"]},
                "dead_letter": {"count": dlq if dlq is not None else gw.db.dead_count()},
                "workers_alive": gw.workers_alive(),
                "vllm_up": gw.vllm_up,
                "rate_per_minute": round(reads / 5, 1),
            }
        )

    # -- G7 -----------------------------------------------------------------
    @app.delete("/v1/receipts/{receipt_ref}")
    async def delete_receipt(receipt_ref: str, request: Request) -> Response:
        require_api_key(request)
        ref = canonical_uuid(receipt_ref)
        async with gw.lock:
            row = gw.db.receipt(ref) if ref else None
            if row is None:
                raise ApiError(404, {"error": "unknown_receipt"})
            with gw.db.tx() as db:
                db.execute("DELETE FROM gw_receipts WHERE receipt_ref = ?", (ref,))
                gw._drop_empty_jobs(db)
        gw._remove_file(row["image_path"])
        log.info("deleted receipt=%s", ref)
        return Response(status_code=204)

    # -- I4 -----------------------------------------------------------------
    @app.post("/internal/workers/{worker_id}/next")
    async def next_queue(worker_id: str, request: Request) -> JSONResponse:
        require_internal(request)
        worker = worker_name(worker_id)
        async with gw.lock:
            now = gw.now()
            _touch_worker(gw, worker, now)
            gw.reserved.pop(worker, None)
            nq, uq = gw.db.waiting("normal"), gw.db.waiting("urgent")
            streak = gw.db.state("urgent_streak")
            decision = topology.choose_next_queue(
                urgent_pending=uq,
                normal_pending=nq,
                urgent_streak=streak,
                urgent_reserved=len(gw.reserved),
                deadline_guard=nq > 0 and gw.deadline_guard(),
            )
            if decision["queue"] == "urgent":
                gw.reserved[worker] = now
            gw._log_decision(worker, decision["queue"], "next", decision["reason"])
        body = dict(decision)
        body["amqp_queue"] = topology.QUEUE_NAMES.get(decision["queue"])
        return JSONResponse(body)

    # -- I1 -----------------------------------------------------------------
    @app.post("/internal/receipts/{receipt_ref}/claim")
    async def claim(receipt_ref: str, request: Request) -> JSONResponse:
        require_internal(request)
        body = parse_body(ClaimBody, await request.body())
        worker = worker_name(body.worker_id)
        ref = canonical_uuid(receipt_ref)
        async with gw.lock:
            now = gw.now()
            _touch_worker(gw, worker, now)
            had_slot = gw.reserved.pop(worker, None) is not None
            row = gw.db.receipt(ref) if ref else None

            def answer(decision: str, reason: str, **extra: Any) -> JSONResponse:
                gw._log_decision(worker, body.queue or "-", decision, reason, ref or receipt_ref)
                return JSONResponse({"decision": decision, "reason": reason, "receipt_ref": ref, **extra})

            if row is None:
                return answer("skip", "unknown_receipt")
            if row["status"] in FINISHED:
                return answer("skip", "already_finished", status=row["status"])
            if body.msg_priority and body.msg_priority != row["priority"]:
                return answer("skip", "stale_copy")
            if row["status"] == "accepting":
                return answer("wait", "not_yet_accepted")
            if row["status"] == "processing":
                lease = row["lease_until"] or 0
                if row["worker_id"] != worker and lease > now:
                    return answer("wait", "leased", lease_until=iso(lease))
                # The previous holder crashed or its lease ran out: that attempt
                # already counted at its claim (DESIGN 6.3).
            if row["attempts"] >= topology.MAX_ATTEMPTS:
                with gw.db.tx() as db:
                    db.execute(
                        "UPDATE gw_receipts SET status = 'dead', worker_id = NULL, lease_until = NULL,"
                        " finished_at = ?, error = COALESCE(error, 'max_attempts'), image_path = NULL"
                        " WHERE receipt_ref = ?",
                        (now, ref),
                    )
                gw._remove_file(row["image_path"])
                return answer("dead", "max_attempts", attempts=row["attempts"])

            streak = gw.db.state("urgent_streak")
            if row["priority"] == "urgent":
                nq = gw.db.waiting("normal")
                others = 0 if had_slot else len(gw.reserved)
                if not topology.can_claim_urgent(
                    normal_pending=nq,
                    urgent_streak=streak + others,
                    deadline_guard=nq > 0 and gw.deadline_guard(),
                ):
                    return answer("wait", "ratio_4_1")

            image = Path(row["image_path"]) if row["image_path"] else None
            if image is None or not image.exists():
                # Without the image nobody can read it; dropping the row makes the
                # dispatcher send the receipt again (G4/G3 answer unknown).
                with gw.db.tx() as db:
                    db.execute("DELETE FROM gw_receipts WHERE receipt_ref = ?", (ref,))
                    gw._drop_empty_jobs(db)
                log.error("image missing receipt=%s, dropped for resend", ref)
                return answer("skip", "image_missing")

            attempts = row["attempts"] + 1
            seq = gw.db.state("claim_seq") + 1
            lease_until = now + settings.lease_seconds
            with gw.db.tx() as db:
                db.execute(
                    "UPDATE gw_receipts SET status = 'processing', attempts = ?, worker_id = ?,"
                    " lease_until = ?, claimed_at = ?, claim_seq = ? WHERE receipt_ref = ?",
                    (attempts, worker, lease_until, now, seq, ref),
                )
                gw.db.set_state("claim_seq", seq)
                gw.db.set_state(
                    "urgent_streak", topology.streak_after_claim(streak, row["priority"])
                )
            extra: dict[str, Any] = {
                "attempts": attempts,
                "priority": row["priority"],
                "claim_seq": seq,
                "lease_seconds": settings.lease_seconds,
                "lease_until": iso(lease_until),
                "mime_type": row["mime_type"],
                "image_path": str(image),
            }
            response = answer("go", "claimed", **extra)
        if body.inline_image:
            data = await asyncio.to_thread(image.read_bytes)
            payload = json.loads(response.body)
            payload["image_b64"] = base64.b64encode(data).decode("ascii")
            return JSONResponse(payload)
        return response

    # -- I2 -----------------------------------------------------------------
    @app.post("/internal/receipts/{receipt_ref}/result")
    async def result(receipt_ref: str, request: Request) -> JSONResponse:
        require_internal(request)
        body = parse_body(ResultBody, await request.body())
        worker = worker_name(body.worker_id)
        ref = canonical_uuid(receipt_ref)
        if body.ok and body.result is None:
            raise bad_request("result is required when ok is true")
        async with gw.lock:
            now = gw.now()
            _touch_worker(gw, worker, now)
            row = gw.db.receipt(ref) if ref else None

            def answer(outcome: str, reason: str, **extra: Any) -> JSONResponse:
                gw._log_decision(worker, "-", f"result:{outcome}", reason, ref or receipt_ref)
                return JSONResponse({"outcome": outcome, "reason": reason, "receipt_ref": ref, **extra})

            if row is None:
                return answer("skip", "unknown_receipt")
            if row["status"] in FINISHED:
                return answer("skip", "already_finished", status=row["status"])  # first result only
            if row["status"] == "processing" and row["worker_id"] != worker:
                return answer("skip", "held_by_other_worker")
            if row["status"] != "processing" and not (row["status"] == "queued" and row["attempts"] > 0):
                return answer("wait", "not_claimed")

            seconds = body.read_seconds
            if seconds is None and row["claimed_at"]:
                seconds = max(0.0, now - row["claimed_at"])
            if body.ok:
                stored = _clean_result(body.result)
                with gw.db.tx() as db:
                    db.execute(
                        "INSERT INTO gw_reads (worker_id, finished_at, seconds, ok) VALUES (?, ?, ?, 1)",
                        (worker, now, seconds),
                    )
                    db.execute(
                        "UPDATE gw_receipts SET status = 'done', result_json = ?, finished_at = ?,"
                        " worker_id = NULL, lease_until = NULL, error = NULL, image_path = NULL"
                        " WHERE receipt_ref = ?",
                        (json.dumps(stored, ensure_ascii=False), now, ref),
                    )
                gw._remove_file(row["image_path"])
                return answer("done", "stored", status="done", attempts=row["attempts"])

            status = topology.status_after_failure(max(1, row["attempts"]))
            reason = body.error or "unreadable_image"
            with gw.db.tx() as db:
                db.execute(
                    "INSERT INTO gw_reads (worker_id, finished_at, seconds, ok) VALUES (?, ?, ?, 0)",
                    (worker, now, seconds),
                )
                if status == "dead":
                    db.execute(
                        "UPDATE gw_receipts SET status = 'dead', error = ?, finished_at = ?,"
                        " worker_id = NULL, lease_until = NULL, image_path = NULL"
                        " WHERE receipt_ref = ?",
                        (reason, now, ref),
                    )
                else:
                    db.execute(
                        "UPDATE gw_receipts SET status = 'queued', error = ?,"
                        " worker_id = NULL, lease_until = NULL WHERE receipt_ref = ?",
                        (reason, ref),
                    )
            if status == "dead":
                gw._remove_file(row["image_path"])
                return answer("dead", reason, status="dead", attempts=row["attempts"])
            if await gw._maybe_promote_requeued(ref):
                # An urgent copy now carries the receipt; ack the old normal one.
                return answer("skip", "requeued_as_urgent", status="queued", attempts=row["attempts"])
            return answer("queued", reason, status="queued", attempts=row["attempts"])

    # -- I3 -----------------------------------------------------------------
    @app.post("/internal/workers/{worker_id}/heartbeat")
    async def heartbeat(worker_id: str, request: Request) -> JSONResponse:
        require_internal(request)
        worker = worker_name(worker_id)
        parse_body(HeartbeatBody, await request.body())
        async with gw.lock:
            now = gw.now()
            _touch_worker(gw, worker, now)
            alive = gw.workers_alive()
        return JSONResponse(
            {"ok": True, "workers_alive": alive, "interval_seconds": 5,
             "timeout_seconds": settings.heartbeat_timeout_seconds}
        )

    return app


def _touch_worker(gw: Gateway, worker: str, now: float) -> None:
    with gw.db.tx() as db:
        db.execute(
            "INSERT INTO gw_workers (worker_id, last_seen, alive) VALUES (?, ?, 1)"
            " ON CONFLICT (worker_id) DO UPDATE SET last_seen = excluded.last_seen, alive = 1",
            (worker, now),
        )


def _clean_result(result: ReadResult) -> dict[str, Any]:
    return {
        "merchant": result.merchant,
        "date": result.date,
        "items": [{"name": item.name, "price": money(item.price)} for item in result.items],
        "total": money(result.total),
        "total_confidence": result.total_confidence,
        "model": result.model or "receipt-vlm",
    }


def _write_durably(path: Path, data: bytes) -> None:
    tmp = path.with_suffix(path.suffix + ".part")
    with open(tmp, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


# --------------------------------------------------------------------------
# Lazy module-level app for "uvicorn ai.gateway.main:app"
# --------------------------------------------------------------------------


def __getattr__(name: str) -> Any:
    if name == "app":
        application = create_app()
        globals()["app"] = application
        return application
    raise AttributeError(name)


# --------------------------------------------------------------------------
# Self-test (in-memory broker, fake clock): python -B -m ai.gateway.main --self-test
# --------------------------------------------------------------------------


def _self_test() -> int:  # pragma: no cover - executed manually / in CI
    import tempfile
    import unittest
    from collections import deque

    from fastapi.testclient import TestClient

    KEY = "test-key"
    TOKEN = "worker-token"
    JPG = b"\xff\xd8\xff\xe0" + b"0" * 100
    PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100

    class MemoryBroker:
        def __init__(self) -> None:
            self.queues = {"urgent": deque(), "normal": deque()}
            self.dlq: deque = deque()
            self.up = True

        async def ensure(self) -> bool:
            return self.up

        async def publish(self, *, receipt_ref: str, job_ref: str, priority: str) -> None:
            if not self.up:
                raise BrokerUnavailable()
            self.queues[priority].append(
                {"receipt_ref": receipt_ref, "job_ref": job_ref, "priority": priority}
            )

        async def dlq_count(self) -> int | None:
            return len(self.dlq) if self.up else None

        async def close(self) -> None:
            pass

    class Clock:
        def __init__(self) -> None:
            self.t = 1_800_000_000.0

        def __call__(self) -> float:
            return self.t

    def ref() -> str:
        return str(uuid.uuid4())

    class GatewayTests(unittest.TestCase):
        def setUp(self) -> None:
            self.tmp = tempfile.TemporaryDirectory()
            self.broker = MemoryBroker()
            self.clock = Clock()
            settings = Settings(
                api_keys=(KEY, "old-key"), data_dir=Path(self.tmp.name),
                internal_token=TOKEN, internal_cidrs="*", vllm_health_urls=(),
                background_tasks=False,
            )
            self.app = create_app(settings, broker=self.broker, clock=self.clock)
            self.client = TestClient(self.app)
            self.client.__enter__()
            self.gw: Gateway = self.app.state.gateway
            self.h = {"X-API-Key": KEY}
            self.i = {"X-Internal-Token": TOKEN}

        def tearDown(self) -> None:
            self.client.__exit__(None, None, None)
            self.tmp.cleanup()

        # helpers
        def submit(self, rref=None, jref=None, priority="normal", data=JPG, name="ร้านสมใจ ลูกค้าก.jpg", **extra):
            rref, jref = rref or ref(), jref or ref()
            fields = {"receipt_ref": rref, "job_ref": jref, "priority": priority, **extra}
            return self.client.post(
                "/v1/receipts", headers=self.h, data=fields,
                files={"file": (name, data, "image/jpeg")},
            ), rref, jref

        def call(self, coro):
            return self.client.portal.call(lambda: coro)

        def next_(self, worker="w0"):
            return self.client.post(f"/internal/workers/{worker}/next", headers=self.i).json()

        def claim(self, msg, worker="w0", queue=None):
            return self.client.post(
                f"/internal/receipts/{msg['receipt_ref']}/claim", headers=self.i,
                json={"worker_id": worker, "queue": queue, "msg_priority": msg["priority"]},
            ).json()

        def result(self, rref, worker="w0", ok=True, **extra):
            body = {"worker_id": worker, "ok": ok, **extra}
            if ok:
                body.setdefault("result", {
                    "merchant": "ร้านตัวอย่าง", "date": "2026-11-18",
                    "items": [{"name": "ข้าว", "price": "45"}], "total": 100,
                    "total_confidence": 0.93,
                })
            return self.client.post(f"/internal/receipts/{rref}/result", headers=self.i, json=body).json()

        def worker_step(self, worker="w0"):
            """One loop of the B06 3.5 worker: next → basic.get → claim → read."""
            d = self.next_(worker)
            if d["queue"] == "none":
                return None
            q = self.broker.queues[d["queue"]]
            if not q:
                return "empty"
            msg = q.popleft()
            c = self.claim(msg, worker, d["queue"])
            if c["decision"] == "go":
                self.result(msg["receipt_ref"], worker)
                return msg
            if c["decision"] == "wait":
                q.appendleft(msg)
            return c["decision"]

        # tests
        def test_api_key(self):
            self.assertEqual(self.client.get("/v1/queue").status_code, 401)
            self.assertEqual(self.client.get("/v1/queue").json(), {"error": "missing_api_key"})
            r = self.client.get("/v1/queue", headers={"X-API-Key": "nope"})
            self.assertEqual((r.status_code, r.json()), (403, {"error": "invalid_api_key"}))
            self.assertEqual(self.client.get("/v1/queue", headers={"X-API-Key": "old-key"}).status_code, 200)
            self.assertIn(self.client.get("/healthz").status_code, (200, 503))
            self.assertEqual(self.client.post("/internal/workers/w0/next").status_code, 403)

        def test_submit_idempotent_and_validation(self):
            r, rref, jref = self.submit(accepted_at="2026-11-19T02:00:00Z")
            self.assertEqual(r.status_code, 202)
            self.assertEqual(r.json(), {"receipt_ref": rref, "job_ref": jref, "status": "queued", "priority": "normal"})
            self.assertEqual(len(self.broker.queues["normal"]), 1)
            again, _, _ = self.submit(rref, jref)
            self.assertEqual((again.status_code, again.json()["status"]), (200, "queued"))
            self.assertEqual(len(self.broker.queues["normal"]), 1)
            self.assertEqual(self.submit(priority="high")[0].status_code, 400)
            self.assertEqual(self.submit(rref="x")[0].status_code, 400)
            self.assertEqual(self.client.post("/v1/receipts", headers=self.h, data={"receipt_ref": ref()}).status_code, 400)
            big = self.submit(data=JPG + b"0" * (10 * 1024 * 1024))[0]
            self.assertEqual((big.status_code, big.json()), (413, {"error": "file_too_large", "limit_bytes": 10485760}))
            self.assertEqual(self.submit(data=b"GIF89a....")[0].json(), {"error": "unsupported_file"})
            self.assertEqual(self.submit(data=PNG)[0].status_code, 202)

        def test_nfr07_no_names_stored(self):
            r, rref, _ = self.submit(name="ร้านสมใจ_ลูกค้าก.jpg", client_name="ลูกค้าก", shop="ร้านสมใจ")
            self.assertEqual(r.status_code, 202)
            dump = "\n".join(self.gw.db.db.iterdump())
            for secret in ("ร้านสมใจ", "ลูกค้าก", "client_name"):
                self.assertNotIn(secret, dump)
            self.assertEqual([p.name for p in self.gw.images.iterdir()], [f"{rref}.jpg"])
            msg = self.broker.queues["normal"][0]
            self.assertEqual(set(msg), {"receipt_ref", "job_ref", "priority"})

        def test_queue_full_429(self):
            limit = topology.QUEUE_LIMITS["normal"]
            with self.gw.db.tx() as db:
                db.executemany(
                    "INSERT INTO gw_receipts (receipt_ref, job_ref, priority, status, mime_type,"
                    " accepted_at, queued_at) VALUES (?, ?, 'normal', 'queued', 'image/jpeg', 0, 0)",
                    [(ref(), "j") for _ in range(limit)],
                )
            for w in ("w0", "w1"):
                self.client.post(f"/internal/workers/{w}/heartbeat", headers=self.i, json={})
            r, rref, _ = self.submit()
            self.assertEqual(r.status_code, 429)
            self.assertEqual(r.headers["Retry-After"], "60")
            self.assertEqual(r.json(), {"error": "queue_full", "queue": "normal", "pending": 400, "limit": 400,
                                        "workers_alive": 2, "retry_after_minutes": 1, "retry_after_seconds": 60})
            self.assertIsNone(self.gw.db.receipt(rref))
            self.assertEqual(list(self.gw.images.iterdir()), [])
            self.assertEqual(self.client.get("/v1/queue", headers=self.h).json()["normal"], {"pending": 400, "limit": 400})

        def test_broker_down_503(self):
            self.broker.up = False
            r, rref, _ = self.submit()
            self.assertEqual((r.status_code, r.headers["Retry-After"], r.json()), (503, "10", {"error": "broker_unavailable"}))
            self.assertIsNone(self.gw.db.receipt(rref))

        def test_job_status_delete_and_404(self):
            _, r1, job = self.submit()
            _, r2, _ = self.submit(jref=job)
            self.assertEqual(self.worker_step()["receipt_ref"], r1)
            body = self.client.get(f"/v1/jobs/{job}", headers=self.h).json()
            self.assertEqual(body["counts"], {"queued": 1, "processing": 0, "done": 1, "dead": 0})
            done = next(x for x in body["receipts"] if x["receipt_ref"] == r1)
            self.assertEqual(done["result"], {"merchant": "ร้านตัวอย่าง", "date": "2026-11-18",
                                              "items": [{"name": "ข้าว", "price": "45.00"}], "total": "100.00",
                                              "total_confidence": 0.93, "model": "receipt-vlm"})
            self.assertEqual(self.client.get(f"/v1/receipts/{r1}", headers=self.h).json()["status"], "done")
            self.assertEqual(self.client.delete(f"/v1/receipts/{r1}", headers=self.h).status_code, 204)
            self.assertEqual(self.client.get(f"/v1/receipts/{r1}", headers=self.h).json(), {"error": "unknown_receipt"})
            self.assertEqual(self.client.delete(f"/v1/receipts/{r1}", headers=self.h).status_code, 404)
            self.assertEqual(self.client.get(f"/v1/jobs/{ref()}", headers=self.h).json(), {"error": "unknown_job"})

        def test_br07_attempts_and_dead(self):
            _, rref, job = self.submit()
            for n in (1, 2, 3):
                msg = self.broker.queues["normal"].popleft()
                c = self.claim(msg)
                self.assertEqual((c["decision"], c["attempts"]), ("go", n))
                out = self.result(rref, ok=False, error="unreadable_image")
                if n < 3:
                    self.assertEqual(out["outcome"], "queued")
                    self.broker.queues["normal"].append(msg)  # nack(requeue=True)
                else:
                    self.assertEqual(out["outcome"], "dead")
            row = self.client.get(f"/v1/receipts/{rref}", headers=self.h).json()
            self.assertEqual((row["status"], row["attempts"], row["error"]), ("dead", 3, "unreadable_image"))
            self.assertEqual(self.claim(msg)["decision"], "skip")  # no 4th attempt

        def test_br07_success_after_two_failures(self):
            _, rref, _ = self.submit()
            msg = self.broker.queues["normal"].popleft()
            for _ in range(2):
                self.claim(msg)
                self.result(rref, ok=False)
            self.assertEqual(self.claim(msg)["attempts"], 3)
            self.assertEqual(self.result(rref)["outcome"], "done")
            self.assertEqual(self.result(rref)["outcome"], "skip")  # second result dropped

        def test_br10_td_cases(self):
            cases = [(3, 2, "U1 U2 U3 N1 N2"), (4, 2, "U1 U2 U3 U4 N1 N2"),
                     (5, 2, "U1 U2 U3 U4 N1 U5 N2"), (5, 0, "U1 U2 U3 U4 U5")]
            for urgent, normal, expected in cases:
                with self.subTest(expected=expected):
                    self.tearDown(); self.setUp()
                    names = {}
                    for i in range(1, urgent + 1):
                        names[self.submit(priority="urgent")[1]] = f"U{i}"
                    for i in range(1, normal + 1):
                        names[self.submit()[1]] = f"N{i}"
                    order = []
                    while (msg := self.worker_step()) is not None:
                        order.append(names[msg["receipt_ref"]])
                    self.assertEqual(" ".join(order), expected)

        def test_two_workers_share_streak(self):
            for _ in range(2):
                self.submit(priority="urgent")
                self.submit()
            self.gw.db.set_state("urgent_streak", 3)
            self.assertEqual(self.next_("w0")["queue"], "urgent")
            self.assertEqual(self.next_("w1"), {"queue": "normal", "reason": "ratio_4_1", "amqp_queue": "receipts.normal"})

        def test_deadline_guard(self):
            # E = age + 1 x 15 s / W(=1) must reach 115 min (B06 3.3)
            self.submit(accepted_at=iso(self.clock.t - 114 * 60 - 50))
            for _ in range(4):
                self.submit(priority="urgent")
            self.assertEqual(self.next_()["reason"], "deadline_guard")

        def test_g5_promote_stale_copy_and_limits(self):
            job = ref()
            refs = [self.submit(jref=job)[1] for _ in range(5)]
            r = self.client.post(f"/v1/jobs/{job}/urgent", headers=self.h)
            self.assertEqual(r.json(), {"job_ref": job, "priority": "urgent", "moved": 5,
                                        "already_processing": 0, "already_finished": 0})
            old = self.broker.queues["normal"].popleft()  # pre-G5 copy, row still queued
            self.assertEqual(self.claim(old)["reason"], "stale_copy")  # skip, no attempt
            again = self.client.post(f"/v1/jobs/{job}/urgent", headers=self.h).json()
            self.assertEqual(again["moved"], 0)
            self.assertEqual(self.client.get(f"/v1/jobs/{job}", headers=self.h).json()["priority"], "urgent")
            seen = []
            while (step := self.worker_step()) is not None:
                if isinstance(step, dict):
                    seen.append(step["receipt_ref"])
            self.assertEqual(sorted(seen), sorted(refs))  # each read once
            # old normal copies were skipped without counting an attempt
            jobs = self.client.get(f"/v1/jobs/{job}", headers=self.h).json()
            self.assertTrue(all(x["attempts"] == 1 for x in jobs["receipts"]))
            self.assertEqual(self.gw.db.state("urgent_streak"), 5)
            big = ref()
            for _ in range(11):
                self.submit(jref=big)
            self.assertEqual(self.client.post(f"/v1/jobs/{big}/urgent", headers=self.h).json(),
                             {"error": "urgent_too_large", "limit": 10})
            self.assertEqual(self.client.post(f"/v1/jobs/{ref()}/urgent", headers=self.h).status_code, 404)

        def test_g5_queue_full(self):
            with self.gw.db.tx() as db:
                db.executemany(
                    "INSERT INTO gw_receipts (receipt_ref, job_ref, priority, status, mime_type,"
                    " accepted_at, queued_at) VALUES (?, 'j', 'urgent', 'queued', 'image/jpeg', 0, 0)",
                    [(ref(),) for _ in range(48)],
                )
            job = ref()
            for _ in range(3):
                self.submit(jref=job)
            r = self.client.post(f"/v1/jobs/{job}/urgent", headers=self.h)
            self.assertEqual((r.status_code, r.json()["queue"], r.headers["Retry-After"]), (429, "urgent", "60"))

        def test_worker_crash_releases_lease(self):
            _, rref, _ = self.submit()
            msg = self.broker.queues["normal"].popleft()
            self.client.post("/internal/workers/w0/heartbeat", headers=self.i, json={})
            self.assertEqual(self.claim(msg, "w0")["decision"], "go")
            self.assertEqual(self.claim(msg, "w1")["decision"], "wait")
            self.client.post("/internal/workers/w1/heartbeat", headers=self.i, json={})
            self.clock.t += 16
            self.client.post("/internal/workers/w1/heartbeat", headers=self.i, json={})
            self.call(self.gw.monitor_once())
            self.assertEqual(self.client.get("/v1/queue", headers=self.h).json()["workers_alive"], 1)
            c = self.claim(msg, "w1")
            self.assertEqual((c["decision"], c["attempts"]), ("go", 2))
            self.assertEqual(self.result(rref, "w1")["outcome"], "done")
            self.assertEqual(self.result(rref, "w0")["outcome"], "skip")  # late result ignored

        def test_retention_purge(self):
            _, rref, _ = self.submit()
            self.worker_step()
            self.assertEqual(list(self.gw.images.iterdir()), [])  # image dropped on finish
            self.clock.t += 61 * 60
            self.assertEqual(self.call(self.gw.purge()), 1)
            self.assertIsNone(self.gw.db.receipt(rref))

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GatewayTests)
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if outcome.wasSuccessful() else 1


def main() -> None:
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"), format="%(asctime)s %(name)s %(levelname)s %(message)s")
    if "--self-test" in sys.argv:
        for name in ("receiptdesk", "httpx"):
            logging.getLogger(name).setLevel(logging.ERROR)
        raise SystemExit(_self_test())
    import uvicorn

    uvicorn.run(
        create_app(),
        host=os.environ.get("GATEWAY_HOST", "0.0.0.0"),
        port=_env_int("GATEWAY_PORT", 8000),
        ssl_certfile=os.environ.get("GATEWAY_TLS_CERT") or None,
        ssl_keyfile=os.environ.get("GATEWAY_TLS_KEY") or None,
        access_log=False,  # NFR-07: logs carry only what the gateway logs itself
    )


if __name__ == "__main__":
    main()
