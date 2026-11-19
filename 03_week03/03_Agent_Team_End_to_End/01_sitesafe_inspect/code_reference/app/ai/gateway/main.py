"""SiteSafe Inspect · AI gateway (DESIGN 5.1, 6, 10, 11).

Run from the app root (the folder that contains ``ai/``)::

    uvicorn ai.gateway.main:app --host 0.0.0.0 --port 8000

What this service does

* 4 APIs, all behind ``X-API-Key`` (constant-time compare, 401 on every path
  including ``/v1/health``):
  ``POST /v1/jobs`` · ``GET /v1/jobs/{job_id}`` · ``GET /v1/jobs?ids=`` · ``GET /v1/health``.
* ``POST /v1/jobs`` checks the file (size ≤ 15 MB counted from the bytes
  received, JPG/PNG magic bytes, sha256), refuses with 429 when
  ``queue_depth ≥ MAX_QUEUE_DEPTH`` (DESIGN 6.3), keeps a temporary copy of the
  image, inserts the job into ``jobs.db`` (SQLite) and publishes a persistent
  message to ``ppe.jobs``.  202 is returned only after RabbitMQ confirms the
  publish; no confirm → 503 and the job is not kept.
* Consumers: ``ppe.results`` (STARTED / DONE / FAILED from the worker, written
  only while the job is still QUEUED/PROCESSING, so one result set per job) and
  ``ppe.jobs.dead`` (→ FAILED ``MAX_RETRIES``).
* A job that is PROCESSING with no new event for ``PROCESSING_TIMEOUT_S`` is
  reported as QUEUED (the worker died and the message went back to the queue).
* The temporary image is deleted when the job ends; finished jobs are kept for
  ``RESULT_TTL_S`` (24 h) and then purged.

Queue names and arguments come from ``ai/common/queues.py`` (shared with the
worker).  The module may expose ``QUEUE_ARGUMENTS`` (dict name → arguments),
``queue_arguments()`` returning that dict, or only a pika-style
``declare_queues(channel)``.  When the module is missing, the arguments of
DESIGN 6.1 below are used (see ``fallback_queue_arguments``).

Environment (DESIGN 11): ``GATEWAY_API_KEY`` · ``RABBITMQ_URL`` ·
``MAX_QUEUE_DEPTH`` (200) · ``MAX_DELIVERY`` (3) · ``PROCESSING_TIMEOUT_S`` (120) ·
``JOBS_DB_PATH`` (/data/jobs.db) · ``IMAGES_DIR`` (/data/images, shared with the
worker) · ``RESULT_TTL_S`` (86400) · ``PUBLISH_TIMEOUT_S`` (5) ·
``DEFAULT_INFER_S`` (2) · ``CLEANUP_INTERVAL_S`` (60) · ``GPU_NAME`` and
``MODEL_VERSION`` (optional, for /v1/health).
"""

from __future__ import annotations

import asyncio
import contextlib
import hashlib
import hmac
import importlib
import json
import logging
import math
import os
import re
import sqlite3
import subprocess
import sys
import time
from collections.abc import Awaitable, Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any, BinaryIO, Protocol
from urllib.parse import urlsplit

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.datastructures import FormData, UploadFile
from starlette.exceptions import HTTPException as StarletteHTTPException

# ``ai.common.queues`` must be importable when started from ai/gateway as well.
_APP_ROOT = Path(__file__).resolve().parents[2]
if str(_APP_ROOT) not in sys.path:
    sys.path.append(str(_APP_ROOT))

LOG = logging.getLogger("sitesafe.gateway")

# ---------------------------------------------------------------------------
# Constants of the API contract (DESIGN 5.1, 6.3)
# ---------------------------------------------------------------------------

#: Upload limit of API 1 (``413 FILE_TOO_LARGE``): 15 × 1,048,576 bytes.
MAX_IMAGE_BYTES = 15 * 1024 * 1024
#: Whole multipart body may be a little larger than the image (other fields, boundaries).
MAX_BODY_BYTES = MAX_IMAGE_BYTES + 1024 * 1024
#: ``GET /v1/jobs?ids=`` accepts at most this many ids.
MAX_IDS_PER_QUERY = 100
#: Retry-After = max(5, ceil((queue_depth − MAX_QUEUE_DEPTH + 10) × average inspect time)).
RETRY_AFTER_MIN_S = 5
RETRY_AFTER_HEADROOM_JOBS = 10
#: The average inspect time comes from the latest 50 finished jobs.
AVERAGE_OVER_JOBS = 50
#: Orphan temp files younger than this are left alone by the cleanup sweep.
ORPHAN_FILE_MIN_AGE_S = 600

ACTIVE_STATUSES = ("QUEUED", "PROCESSING")
FINAL_STATUSES = ("DONE", "FAILED")

DEFAULT_JOBS_QUEUE = "ppe.jobs"
DEFAULT_RESULTS_QUEUE = "ppe.results"
DEFAULT_DEAD_QUEUE = "ppe.jobs.dead"

_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
_CHUNK = 1024 * 1024


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


def _env_number(env: Mapping[str, str], name: str, default: float, *, minimum: float, integer: bool) -> Any:
    raw = env.get(name, "").strip()
    if not raw:
        return int(default) if integer else float(default)
    try:
        value = int(raw) if integer else float(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be a number") from exc
    if value < minimum:
        raise ValueError(f"{name} must be ≥ {minimum}")
    return value


@dataclass(frozen=True)
class Settings:
    api_key: str = ""
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672/"
    jobs_db_path: str = "/data/jobs.db"
    images_dir: str = "/data/images"
    max_queue_depth: int = 200
    max_delivery: int = 3
    processing_timeout_s: float = 120.0
    result_ttl_s: float = 24 * 3600.0
    publish_timeout_s: float = 5.0
    default_infer_s: float = 2.0
    cleanup_interval_s: float = 60.0
    gpu_name: str = ""
    model_version: str = ""

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        env = os.environ if env is None else env
        return cls(
            api_key=env.get("GATEWAY_API_KEY", ""),
            rabbitmq_url=env.get("RABBITMQ_URL", "").strip() or cls.rabbitmq_url,
            jobs_db_path=env.get("JOBS_DB_PATH", "").strip() or cls.jobs_db_path,
            images_dir=env.get("IMAGES_DIR", "").strip() or cls.images_dir,
            max_queue_depth=_env_number(env, "MAX_QUEUE_DEPTH", 200, minimum=1, integer=True),
            max_delivery=_env_number(env, "MAX_DELIVERY", 3, minimum=1, integer=True),
            processing_timeout_s=_env_number(env, "PROCESSING_TIMEOUT_S", 120, minimum=1, integer=False),
            result_ttl_s=_env_number(env, "RESULT_TTL_S", 24 * 3600, minimum=1, integer=False),
            publish_timeout_s=_env_number(env, "PUBLISH_TIMEOUT_S", 5, minimum=0.1, integer=False),
            default_infer_s=_env_number(env, "DEFAULT_INFER_S", 2, minimum=0.001, integer=False),
            cleanup_interval_s=_env_number(env, "CLEANUP_INTERVAL_S", 60, minimum=1, integer=False),
            gpu_name=env.get("GPU_NAME", "").strip(),
            model_version=env.get("MODEL_VERSION", "").strip(),
        )


# ---------------------------------------------------------------------------
# Logging: secrets never reach a log line
# ---------------------------------------------------------------------------


class SecretRedactingFilter(logging.Filter):
    """Replace known secret values (API key, RabbitMQ password) in log records."""

    def __init__(self, secrets: Iterable[str]):
        super().__init__()
        self._secrets = sorted({s for s in secrets if s and len(s) >= 4}, key=len, reverse=True)

    def filter(self, record: logging.LogRecord) -> bool:
        if not self._secrets:
            return True
        try:
            message = record.getMessage()
        except Exception:  # malformed args: leave the record alone
            return True
        redacted = message
        for secret in self._secrets:
            redacted = redacted.replace(secret, "[REDACTED]")
        if redacted != message:
            record.msg, record.args = redacted, None
        return True


def _url_password(url: str) -> str:
    with contextlib.suppress(ValueError):
        return urlsplit(url).password or ""
    return ""


def _safe_url(url: str) -> str:
    """AMQP URL without credentials, for log lines."""
    with contextlib.suppress(ValueError):
        parts = urlsplit(url)
        host = parts.hostname or "?"
        return f"{parts.scheme}://{host}:{parts.port or ''}{parts.path}"
    return "<amqp url>"


def install_log_redaction(filter_: SecretRedactingFilter) -> None:
    """Attach the filter to our logger and to every handler that already exists.

    uvicorn does not configure the root logger, so our INFO lines get a handler
    of their own when nobody else provides one (level from ``LOG_LEVEL``)."""
    if filter_ not in LOG.filters:
        LOG.addFilter(filter_)
    if not LOG.handlers and not logging.getLogger().handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        handler.addFilter(filter_)
        LOG.addHandler(handler)
        LOG.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())
    names = ("", "uvicorn", "uvicorn.error", "uvicorn.access", "aio_pika", "aiormq", "fastapi")
    for name in names:
        for handler in logging.getLogger(name).handlers:
            if filter_ not in handler.filters:
                handler.addFilter(filter_)


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def iso_utc(ts: float | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_job_id(value: Any) -> str | None:
    """Canonical lowercase UUID, or None (also keeps file names safe)."""
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value.lower() if _UUID_RE.match(value) else None


def error_response(status: int, code: str, message: str, **extra: Any) -> JSONResponse:
    headers = extra.pop("headers", None)
    return JSONResponse({"error": code, "message": message, **extra}, status_code=status, headers=headers)


def compute_retry_after(queue_depth: int, max_queue_depth: int, recent_ms: list[int], default_infer_s: float) -> int:
    """DESIGN 6.3: max(5, ceil((queue_depth − MAX_QUEUE_DEPTH + 10) × average inspect time)).

    The average comes from the latest 50 finished jobs (milliseconds, exact
    arithmetic so that e.g. 10 × 2.0 s is 20, not 21).  With no history yet the
    configured default (2 s) is used.
    """
    samples = [ms for ms in recent_ms[:AVERAGE_OVER_JOBS] if ms and ms > 0]
    if samples:
        average_s = Fraction(sum(samples), len(samples) * 1000)
    else:
        average_s = Fraction(str(default_infer_s))
    waiting = queue_depth - max_queue_depth + RETRY_AFTER_HEADROOM_JOBS
    return max(RETRY_AFTER_MIN_S, math.ceil(waiting * average_s))


def detect_image_kind(head: bytes) -> str | None:
    """File type from the first bytes (JPG ``FF D8 FF`` · PNG ``89 50 4E 47``)."""
    if head.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if head.startswith(b"\x89PNG"):
        return "png"
    return None


class _FileTooLarge(Exception):
    pass


class _BodyTooLarge(Exception):
    pass


@dataclass(frozen=True)
class _UploadScan:
    size: int
    sha256: str
    head: bytes


def _scan_upload(fileobj: BinaryIO, limit: int) -> _UploadScan:
    """Size (from bytes actually read), sha256 and first bytes; stops as soon as the limit is passed."""
    fileobj.seek(0)
    digest = hashlib.sha256()
    size, head = 0, b""
    while chunk := fileobj.read(_CHUNK):
        if len(head) < 8:
            head = (head + chunk)[:8]
        size += len(chunk)
        if size > limit:
            raise _FileTooLarge
        digest.update(chunk)
    return _UploadScan(size, digest.hexdigest(), head)


def _store_image(fileobj: BinaryIO, target: Path) -> None:
    """Write atomically (tmp + fsync + rename) so the worker never reads half a file."""
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(target.name + ".part")
    fileobj.seek(0)
    try:
        with open(partial, "wb") as out:
            while chunk := fileobj.read(_CHUNK):
                out.write(chunk)
            out.flush()
            os.fsync(out.fileno())
        os.replace(partial, target)
    except BaseException:
        _unlink_quiet(partial)
        raise


def _unlink_quiet(path: str | os.PathLike[str] | None) -> None:
    if not path:
        return
    try:
        os.unlink(path)
    except FileNotFoundError:
        pass
    except OSError as exc:
        LOG.warning("could not delete temporary image %s: %s", os.fspath(path), exc.strerror)


def _limited_receive(receive: Callable[[], Awaitable[dict]], limit: int) -> Callable[[], Awaitable[dict]]:
    """ASGI receive wrapper that stops reading the request body once it passes ``limit`` bytes."""
    received = 0

    async def wrapped() -> dict:
        nonlocal received
        message = await receive()
        if message.get("type") == "http.request":
            received += len(message.get("body", b""))
            if received > limit:
                raise _BodyTooLarge
        return message

    return wrapped


def _detect_gpu_name() -> str:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=5, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    lines = [line.strip() for line in out.stdout.splitlines() if line.strip()]
    return lines[0] if out.returncode == 0 and lines else ""


# ---------------------------------------------------------------------------
# Queue definitions (ai/common/queues.py, DESIGN 6.1)
# ---------------------------------------------------------------------------


def fallback_queue_arguments(
    jobs: str, results: str, dead: str, *, max_queue_depth: int, max_delivery: int
) -> dict[str, dict[str, Any]]:
    """DESIGN 6.1 when ``ai/common/queues.py`` gives no arguments.

    All three queues are quorum + durable.  ``ppe.jobs`` dead-letters through the
    default exchange to ``ppe.jobs.dead`` after ``MAX_DELIVERY`` deliveries and
    rejects publishes beyond ``MAX_QUEUE_DEPTH`` messages.
    """
    quorum = {"x-queue-type": "quorum"}
    return {
        jobs: {
            **quorum,
            "x-delivery-limit": max_delivery,
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": dead,
            "x-max-length": max_queue_depth,
            "x-overflow": "reject-publish",
        },
        results: dict(quorum),
        dead: dict(quorum),
    }


@dataclass(frozen=True)
class QueueSpec:
    jobs: str
    results: str
    dead: str
    #: name → arguments for ``queue_declare`` (None when only ``declarer`` is known)
    arguments: dict[str, dict[str, Any]] | None
    #: pika-style ``declare_queues(channel)`` from ai/common/queues.py
    declarer: Callable[[Any], Any] | None
    source: str


def _arguments_from_module(module: Any, names: tuple[str, str, str]) -> dict[str, dict[str, Any]] | None:
    table = getattr(module, "QUEUE_ARGUMENTS", None)
    if table is None:
        table = getattr(module, "QUEUES", None)
    if table is None and callable(getattr(module, "queue_arguments", None)):
        with contextlib.suppress(TypeError):
            table = module.queue_arguments()
    if not isinstance(table, Mapping) or not all(name in table for name in names):
        return None
    out: dict[str, dict[str, Any]] = {}
    for name in names:
        entry = table[name]
        if isinstance(entry, Mapping) and isinstance(entry.get("arguments"), Mapping):
            entry = entry["arguments"]
        if not isinstance(entry, Mapping):
            return None
        out[name] = dict(entry)
    return out


def load_queue_spec(settings: Settings, module_name: str = "ai.common.queues") -> QueueSpec:
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        LOG.warning("%s not importable (%s); using queue arguments of DESIGN 6.1", module_name, exc)
        module = None

    jobs = getattr(module, "JOBS_QUEUE", DEFAULT_JOBS_QUEUE)
    results = getattr(module, "RESULTS_QUEUE", DEFAULT_RESULTS_QUEUE)
    dead = DEFAULT_DEAD_QUEUE
    for attr in ("DEAD_QUEUE", "DEAD_LETTER_QUEUE", "JOBS_DEAD_QUEUE"):
        if isinstance(getattr(module, attr, None), str):
            dead = getattr(module, attr)
            break

    if module is not None:
        arguments = _arguments_from_module(module, (jobs, results, dead))
        if arguments is not None:
            return QueueSpec(jobs, results, dead, arguments, None, f"{module_name} (arguments)")
        declarer = getattr(module, "declare_queues", None)
        if callable(declarer):
            return QueueSpec(jobs, results, dead, None, declarer, f"{module_name}.declare_queues")

    arguments = fallback_queue_arguments(
        jobs, results, dead, max_queue_depth=settings.max_queue_depth, max_delivery=settings.max_delivery
    )
    return QueueSpec(jobs, results, dead, arguments, None, "DESIGN 6.1 fallback")


# ---------------------------------------------------------------------------
# jobs.db (SQLite, one table)
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    job_id         TEXT PRIMARY KEY,
    status         TEXT NOT NULL CHECK (status IN ('QUEUED','PROCESSING','DONE','FAILED')),
    queued_at      REAL NOT NULL,
    started_at     REAL,
    finished_at    REAL,
    result_json    TEXT,
    error_code     TEXT,
    error_message  TEXT,
    delivery_count INTEGER NOT NULL DEFAULT 0,
    image_path     TEXT,
    sha256         TEXT,
    last_event_at  REAL,
    proc_ms        INTEGER
);
CREATE INDEX IF NOT EXISTS jobs_status ON jobs (status);
CREATE INDEX IF NOT EXISTS jobs_finished ON jobs (finished_at);
"""

_ACTIVE_SQL = "status IN ('QUEUED','PROCESSING')"


class JobStore:
    """All calls run on the event-loop thread, so a check followed by a write
    without an ``await`` in between is atomic."""

    def __init__(self, path: str):
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, isolation_level=None, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        if path != ":memory:":
            self._db.execute("PRAGMA journal_mode=WAL")
        self._db.execute("PRAGMA synchronous=FULL")
        self._db.executescript(_SCHEMA)

    def close(self) -> None:
        self._db.close()

    def get(self, job_id: str) -> sqlite3.Row | None:
        return self._db.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()

    def get_many(self, job_ids: list[str]) -> dict[str, sqlite3.Row]:
        found: dict[str, sqlite3.Row] = {}
        for start in range(0, len(job_ids), 500):
            chunk = job_ids[start:start + 500]
            marks = ",".join("?" * len(chunk))
            for row in self._db.execute(f"SELECT * FROM jobs WHERE job_id IN ({marks})", chunk):
                found[row["job_id"]] = row
        return found

    def depth(self) -> int:
        return self._db.execute(f"SELECT COUNT(*) FROM jobs WHERE {_ACTIVE_SQL}").fetchone()[0]

    def insert(self, job_id: str, queued_at: float, image_path: str, sha256: str) -> None:
        self._db.execute(
            "INSERT INTO jobs (job_id, status, queued_at, image_path, sha256, last_event_at)"
            " VALUES (?, 'QUEUED', ?, ?, ?, ?)",
            (job_id, queued_at, image_path, sha256, queued_at),
        )

    def delete(self, job_id: str) -> None:
        self._db.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))

    def mark_started(self, job_id: str, now: float) -> bool:
        cur = self._db.execute(
            "UPDATE jobs SET status = 'PROCESSING', started_at = ?, last_event_at = ?,"
            f" delivery_count = delivery_count + 1 WHERE job_id = ? AND {_ACTIVE_SQL}",
            (now, now, job_id),
        )
        return cur.rowcount == 1

    def mark_done(self, job_id: str, now: float, result_json: str, infer_ms: int | None) -> str | None:
        """Write the one and only result set.  Returns the temp image path when the job changed."""
        row = self.get(job_id)
        if row is None or row["status"] not in ACTIVE_STATUSES:
            return None
        wall_ms = round((now - row["started_at"]) * 1000) if row["started_at"] is not None else 0
        proc_ms = max(wall_ms, infer_ms or 0) or None
        cur = self._db.execute(
            "UPDATE jobs SET status = 'DONE', finished_at = ?, last_event_at = ?, result_json = ?,"
            f" error_code = NULL, error_message = NULL, proc_ms = ? WHERE job_id = ? AND {_ACTIVE_SQL}",
            (now, now, result_json, proc_ms, job_id),
        )
        return (row["image_path"] or "") if cur.rowcount == 1 else None

    def mark_failed(self, job_id: str, now: float, code: str, message: str) -> str | None:
        row = self.get(job_id)
        if row is None or row["status"] not in ACTIVE_STATUSES:
            return None
        cur = self._db.execute(
            "UPDATE jobs SET status = 'FAILED', finished_at = ?, last_event_at = ?, error_code = ?,"
            f" error_message = ?, result_json = NULL WHERE job_id = ? AND {_ACTIVE_SQL}",
            (now, now, code, message, job_id),
        )
        return (row["image_path"] or "") if cur.rowcount == 1 else None

    def recent_proc_ms(self, limit: int = AVERAGE_OVER_JOBS) -> list[int]:
        rows = self._db.execute(
            "SELECT proc_ms FROM jobs WHERE status = 'DONE' AND proc_ms IS NOT NULL"
            " ORDER BY finished_at DESC LIMIT ?",
            (limit,),
        )
        return [row[0] for row in rows]

    def latest_result(self) -> dict[str, Any]:
        row = self._db.execute(
            "SELECT result_json FROM jobs WHERE status = 'DONE' AND result_json IS NOT NULL"
            " ORDER BY finished_at DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return {}
        with contextlib.suppress(ValueError, TypeError):
            value = json.loads(row[0])
            return value if isinstance(value, dict) else {}
        return {}

    def purge(self, cutoff: float) -> list[str]:
        """Remove finished jobs older than ``cutoff`` and unfinished jobs queued before it
        (an unfinished job that old is lost; the web stopped waiting long ago)."""
        where = "(status IN ('DONE','FAILED') AND finished_at < ?) OR (status IN ('QUEUED','PROCESSING') AND queued_at < ?)"
        rows = self._db.execute(f"SELECT image_path FROM jobs WHERE {where}", (cutoff, cutoff)).fetchall()
        self._db.execute(f"DELETE FROM jobs WHERE {where}", (cutoff, cutoff))
        return [row[0] for row in rows if row[0]]

    def active_ids(self) -> set[str]:
        return {row[0] for row in self._db.execute(f"SELECT job_id FROM jobs WHERE {_ACTIVE_SQL}")}


# ---------------------------------------------------------------------------
# Broker (RabbitMQ) — swappable so tests can run without RabbitMQ
# ---------------------------------------------------------------------------


class QueueFull(Exception):
    """RabbitMQ refused the publish (``x-overflow = reject-publish``)."""


class QueueUnavailable(Exception):
    """RabbitMQ is not reachable or did not confirm the publish."""


@dataclass(frozen=True)
class BrokerStatus:
    ok: bool
    workers: int


MessageHandler = Callable[[bytes], Awaitable[None]]


class Broker(Protocol):
    async def start(self, on_result: MessageHandler, on_dead: MessageHandler) -> None: ...

    async def publish_job(self, body: bytes, job_id: str) -> None:
        """Return only after the broker confirmed; raise QueueFull / QueueUnavailable otherwise."""
        ...

    async def status(self) -> BrokerStatus: ...

    async def close(self) -> None: ...


class RabbitBroker:
    """aio-pika implementation: robust connection, publisher confirms, manual ack."""

    def __init__(self, settings: Settings, spec: QueueSpec, consumer_prefetch: int = 32):
        self.settings = settings
        self.spec = spec
        self.consumer_prefetch = consumer_prefetch
        self._connection: Any = None
        self._exchange: Any = None
        self._ready = False
        self._task: asyncio.Task | None = None

    async def start(self, on_result: MessageHandler, on_dead: MessageHandler) -> None:
        self._task = asyncio.create_task(self._run(on_result, on_dead), name="rabbitmq-connect")

    async def _run(self, on_result: MessageHandler, on_dead: MessageHandler) -> None:
        import aio_pika

        delay = 1.0
        while True:
            try:
                connection = await aio_pika.connect_robust(self.settings.rabbitmq_url, timeout=10)
                try:
                    await self._setup(connection, on_result, on_dead)
                except BaseException:
                    await connection.close()
                    raise
                self._connection = connection
                self._ready = True
                LOG.info("RabbitMQ connected at %s · queues from %s",
                         _safe_url(self.settings.rabbitmq_url), self.spec.source)
                return
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # keep trying: the gateway answers 503 meanwhile
                # PRECONDITION_FAILED here usually means ppe.jobs exists with other arguments
                # (MAX_QUEUE_DEPTH / MAX_DELIVERY changed): RabbitMQ keeps the old ones until
                # the queue is deleted while empty.
                LOG.warning("RabbitMQ at %s not ready (%s: %.200s); retry in %.0f s",
                            _safe_url(self.settings.rabbitmq_url), type(exc).__name__, exc, delay)
                await asyncio.sleep(delay)
                delay = min(delay * 2, 30.0)

    async def declare(self, channel: Any) -> dict[str, Any]:
        """Declare ``ppe.jobs.dead``, ``ppe.results`` and ``ppe.jobs`` (dead-letter target first)."""
        spec = self.spec
        queues: dict[str, Any] = {}
        if spec.arguments is None and spec.declarer is not None:
            await asyncio.to_thread(self._declare_with_pika, spec.declarer)
            for name in (spec.dead, spec.results, spec.jobs):
                queues[name] = await channel.declare_queue(name, passive=True)
            return queues
        assert spec.arguments is not None
        for name in (spec.dead, spec.results, spec.jobs):
            queues[name] = await channel.declare_queue(name, durable=True, arguments=spec.arguments.get(name, {}))
        return queues

    def _declare_with_pika(self, declarer: Callable[[Any], Any]) -> None:
        import pika  # only needed when ai/common/queues.py exposes a pika declarer only

        with pika.BlockingConnection(pika.URLParameters(self.settings.rabbitmq_url)) as connection:
            declarer(connection.channel())

    async def _setup(self, connection: Any, on_result: MessageHandler, on_dead: MessageHandler) -> None:
        publish_channel = await connection.channel(publisher_confirms=True, on_return_raises=True)
        await self.declare(publish_channel)
        self._exchange = publish_channel.default_exchange

        consume_channel = await connection.channel()
        await consume_channel.set_qos(prefetch_count=self.consumer_prefetch)
        results = await consume_channel.declare_queue(self.spec.results, passive=True)
        dead = await consume_channel.declare_queue(self.spec.dead, passive=True)
        await results.consume(self._wrap(on_result, self.spec.results))
        await dead.consume(self._wrap(on_dead, self.spec.dead))

    @staticmethod
    def _wrap(handler: MessageHandler, queue_name: str) -> Callable[[Any], Awaitable[None]]:
        async def on_message(message: Any) -> None:
            try:
                await handler(message.body)
            except Exception:
                LOG.exception("handling a message from %s failed; it goes back to the queue", queue_name)
                await asyncio.sleep(1)
                with contextlib.suppress(Exception):
                    await message.nack(requeue=True)
                return
            with contextlib.suppress(Exception):  # lost ack → redelivery; handlers are idempotent
                await message.ack()

        return on_message

    async def publish_job(self, body: bytes, job_id: str) -> None:
        import aio_pika
        import aiormq
        from aiormq.exceptions import DeliveryError, PublishError

        if not self._ready or self._exchange is None:
            raise QueueUnavailable("RabbitMQ not connected")
        message = aio_pika.Message(
            body,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            content_type="application/json",
            message_id=job_id,
        )
        timeout = self.settings.publish_timeout_s
        try:
            confirmation = await asyncio.wait_for(
                self._exchange.publish(message, routing_key=self.spec.jobs, mandatory=True, timeout=timeout),
                timeout + 1,
            )
        except PublishError as exc:  # returned: no queue bound (must be checked before DeliveryError)
            raise QueueUnavailable("message returned unroutable") from exc
        except DeliveryError as exc:  # basic.nack: x-max-length + reject-publish
            raise QueueFull("publish rejected by RabbitMQ") from exc
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # timeout, closed channel, lost connection
            raise QueueUnavailable(type(exc).__name__) from exc
        if not isinstance(confirmation, aiormq.spec.Basic.Ack):
            raise QueueUnavailable("publish not confirmed")

    async def status(self) -> BrokerStatus:
        if not self._ready or self._connection is None or self._connection.is_closed:
            return BrokerStatus(False, 0)
        try:
            async with asyncio.timeout(3):
                channel = await self._connection.channel()
                try:
                    queue = await channel.declare_queue(self.spec.jobs, passive=True)
                    workers = int(queue.declaration_result.consumer_count or 0)
                finally:
                    with contextlib.suppress(Exception):
                        await channel.close()
        except Exception:
            return BrokerStatus(False, 0)
        return BrokerStatus(True, workers)

    async def close(self) -> None:
        if self._task is not None:
            self._task.cancel()
            with contextlib.suppress(BaseException):
                await self._task
        self._ready = False
        if self._connection is not None:
            with contextlib.suppress(Exception):
                await self._connection.close()


# ---------------------------------------------------------------------------
# Gateway logic
# ---------------------------------------------------------------------------


class Gateway:
    def __init__(self, settings: Settings, broker: Broker, clock: Callable[[], float] = time.time):
        self.settings = settings
        self.broker = broker
        self.clock = clock
        self.images_dir = Path(settings.images_dir)
        self.store: JobStore | None = None
        self.gpu_name = settings.gpu_name
        self._cleanup_task: asyncio.Task | None = None

    # -- lifecycle ---------------------------------------------------------

    async def startup(self) -> None:
        if not self.settings.api_key:
            LOG.error("GATEWAY_API_KEY is empty: every request will be answered 401")
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.store = JobStore(self.settings.jobs_db_path)
        if not self.gpu_name:
            self.gpu_name = await asyncio.to_thread(_detect_gpu_name)
        self.purge()
        await self.broker.start(self.handle_result, self.handle_dead)
        self._cleanup_task = asyncio.create_task(self._cleanup_loop(), name="jobs-cleanup")

    async def shutdown(self) -> None:
        if self._cleanup_task is not None:
            self._cleanup_task.cancel()
            with contextlib.suppress(BaseException):
                await self._cleanup_task
        await self.broker.close()
        if self.store is not None:
            self.store.close()
            self.store = None

    async def _cleanup_loop(self) -> None:
        while True:
            await asyncio.sleep(self.settings.cleanup_interval_s)
            try:
                self.purge()
            except Exception:
                LOG.exception("cleanup of jobs.db failed")

    @property
    def db(self) -> JobStore:
        assert self.store is not None, "gateway not started"
        return self.store

    # -- views -------------------------------------------------------------

    def job_view(self, row: sqlite3.Row) -> dict[str, Any]:
        """API 2 shape.  PROCESSING with no event for PROCESSING_TIMEOUT_S is shown as QUEUED."""
        status = row["status"]
        if status == "PROCESSING":
            last_event = row["last_event_at"] or row["started_at"] or row["queued_at"]
            if self.clock() - last_event > self.settings.processing_timeout_s:
                status = "QUEUED"
        result = None
        if row["status"] == "DONE" and row["result_json"]:
            result = json.loads(row["result_json"])
        error = None
        if row["status"] == "FAILED":
            error = {"code": row["error_code"] or "FAILED", "message": row["error_message"] or ""}
        return {
            "job_id": row["job_id"],
            "status": status,
            "queued_at": iso_utc(row["queued_at"]),
            "started_at": iso_utc(row["started_at"]),
            "finished_at": iso_utc(row["finished_at"]),
            "result": result,
            "error": error,
        }

    def queue_full_response(self, depth: int) -> JSONResponse:
        retry = compute_retry_after(
            depth, self.settings.max_queue_depth, self.db.recent_proc_ms(), self.settings.default_infer_s
        )
        return error_response(
            429, "QUEUE_FULL", "คิวเต็ม กรุณาส่งใหม่ภายหลัง",
            queue_depth=depth, max_queue_depth=self.settings.max_queue_depth, retry_after_s=retry,
            headers={"Retry-After": str(retry)},
        )

    # -- API 1 -------------------------------------------------------------

    async def submit(self, request: Request) -> JSONResponse:
        declared = request.headers.get("content-length")
        if declared is not None:
            try:
                if int(declared) > MAX_BODY_BYTES:
                    return _file_too_large()
            except ValueError:
                return error_response(400, "BAD_REQUEST", "Content-Length ไม่ถูกต้อง")
        limited = Request(request.scope, _limited_receive(request.receive, MAX_BODY_BYTES))
        try:
            form = await limited.form(max_files=1, max_fields=16)
        except _BodyTooLarge:
            return _file_too_large()
        except StarletteHTTPException as exc:
            return error_response(400, "BAD_REQUEST", f"multipart ไม่ถูกต้อง: {exc.detail}")
        try:
            return await self._submit_form(form)
        finally:
            await form.close()

    async def _submit_form(self, form: FormData) -> JSONResponse:
        job_id = normalize_job_id(form.get("job_id"))
        if job_id is None:
            return error_response(400, "BAD_REQUEST", "ต้องมี job_id เป็น UUID")

        existing = self.db.get(job_id)
        if existing is not None:  # same job_id again: no new job (D-05)
            return JSONResponse(self.job_view(existing), status_code=200)

        image = form.get("image")
        sha_field = form.get("sha256")
        if not isinstance(image, UploadFile):
            return error_response(400, "BAD_REQUEST", "ต้องมีไฟล์ในช่อง image")
        if not isinstance(sha_field, str) or not _SHA256_RE.match(sha_field.strip()):
            return error_response(400, "BAD_REQUEST", "ต้องมี sha256 (hex 64 ตัวอักษร)")

        try:
            scan = await asyncio.to_thread(_scan_upload, image.file, MAX_IMAGE_BYTES)
        except _FileTooLarge:
            return _file_too_large()
        kind = detect_image_kind(scan.head)
        if kind is None:
            return error_response(415, "UNSUPPORTED_TYPE", "รับเฉพาะไฟล์ JPG หรือ PNG")
        if not hmac.compare_digest(scan.sha256, sha_field.strip().lower()):
            return error_response(400, "BAD_REQUEST", "sha256 ไม่ตรงกับไฟล์ที่ได้รับ")

        # Admission: check + insert with no await in between → atomic on the event loop.
        existing = self.db.get(job_id)
        if existing is not None:
            return JSONResponse(self.job_view(existing), status_code=200)
        depth = self.db.depth()
        if depth >= self.settings.max_queue_depth:
            return self.queue_full_response(depth)
        now = self.clock()
        image_path = self.images_dir / f"{job_id}.{kind}"
        self.db.insert(job_id, now, str(image_path), scan.sha256)

        try:
            await asyncio.to_thread(_store_image, image.file, image_path)
        except OSError as exc:
            self.db.delete(job_id)
            _unlink_quiet(image_path)
            LOG.error("job %s: could not store temporary image (%s)", job_id, exc.strerror)
            return error_response(503, "STORAGE_UNAVAILABLE", "เก็บไฟล์ชั่วคราวไม่ได้ กรุณาส่งใหม่ภายหลัง")

        body = json.dumps(
            {"job_id": job_id, "image_path": str(image_path), "queued_at": iso_utc(now)},
            separators=(",", ":"),
        ).encode()
        try:
            await self.broker.publish_job(body, job_id)
        except QueueFull:
            self._forget(job_id, image_path)
            LOG.info("job %s refused by RabbitMQ (queue full)", job_id)
            return self.queue_full_response(self.db.depth())
        except Exception as exc:  # QueueUnavailable or anything unexpected: no confirm → 503
            self._forget(job_id, image_path)
            LOG.warning("job %s not confirmed by RabbitMQ (%s)", job_id, exc)
            return error_response(503, "QUEUE_UNAVAILABLE", "คิวใช้งานไม่ได้ กรุณาส่งใหม่ภายหลัง")

        LOG.info("job %s queued", job_id)
        return JSONResponse(
            {"job_id": job_id, "status": "QUEUED", "queue_depth": self.db.depth()}, status_code=202
        )

    def _forget(self, job_id: str, image_path: Path) -> None:
        row = self.db.get(job_id)
        if row is not None and row["status"] in ACTIVE_STATUSES:
            self.db.delete(job_id)
        _unlink_quiet(image_path)

    # -- API 2 / 3 ---------------------------------------------------------

    def get_job(self, job_id: str) -> JSONResponse:
        key = normalize_job_id(job_id)
        row = self.db.get(key) if key else None
        if row is None:
            return error_response(404, "JOB_NOT_FOUND", "ไม่พบงานนี้")
        return JSONResponse(self.job_view(row))

    def get_jobs(self, ids: str | None) -> JSONResponse:
        if ids is None:
            return error_response(400, "BAD_REQUEST", "ต้องระบุ ids")
        requested = list(dict.fromkeys(part.strip() for part in ids.split(",") if part.strip()))
        if len(requested) > MAX_IDS_PER_QUERY:
            return error_response(400, "BAD_REQUEST", f"ids ได้ไม่เกิน {MAX_IDS_PER_QUERY} รายการ")
        keys = {raw: normalize_job_id(raw) for raw in requested}
        rows = self.db.get_many([key for key in keys.values() if key])
        jobs, not_found = [], []
        for raw, key in keys.items():
            row = rows.get(key) if key else None
            if row is None:
                not_found.append(raw)
            else:
                jobs.append(self.job_view(row))
        return JSONResponse({"jobs": jobs, "not_found": not_found})

    # -- API 4 -------------------------------------------------------------

    async def health(self) -> JSONResponse:
        status = await self.broker.status()
        latest = self.db.latest_result()
        healthy = status.ok and status.workers > 0
        body = {
            "status": "ok" if healthy else "down",
            "rabbitmq": "ok" if status.ok else "down",
            "workers": status.workers,
            "queue_depth": self.db.depth(),
            "max_queue_depth": self.settings.max_queue_depth,
            "gpu": self.gpu_name or str(latest.get("gpu") or "") or "unknown",
            "model_version": self.settings.model_version or str(latest.get("model_version") or "") or "unknown",
        }
        return JSONResponse(body, status_code=200 if healthy else 503)

    # -- consumers ---------------------------------------------------------

    async def handle_result(self, body: bytes) -> None:
        """``ppe.results``: {"job_id","event":"STARTED|DONE|FAILED","result","error"}."""
        try:
            message = json.loads(body)
            job_id = normalize_job_id(message.get("job_id"))
            event = message.get("event")
        except (ValueError, AttributeError, TypeError):
            LOG.warning("dropped a result message that is not valid JSON")
            return
        if job_id is None:
            LOG.warning("dropped a result message without a valid job_id")
            return
        now = self.clock()
        if event == "STARTED":
            if not self.db.mark_started(job_id, now):
                LOG.info("job %s: STARTED ignored (unknown or already finished)", job_id)
            return
        if event == "DONE":
            result = message.get("result")
            if not _valid_result(result):
                LOG.error("job %s: DONE without a valid result was dropped", job_id)
                return
            infer_ms = result.get("infer_ms")
            changed = self.db.mark_done(
                job_id, now, json.dumps(result, ensure_ascii=False, separators=(",", ":")),
                infer_ms if isinstance(infer_ms, int) and not isinstance(infer_ms, bool) else None,
            )
            self._after_final(job_id, "DONE", changed)
            return
        if event == "FAILED":
            error = message.get("error") if isinstance(message.get("error"), dict) else {}
            code = str(error.get("code") or "IMAGE_UNREADABLE")
            text = str(error.get("message") or "เปิดไฟล์รูปไม่ได้")
            changed = self.db.mark_failed(job_id, now, code, text)
            self._after_final(job_id, "FAILED", changed)
            return
        LOG.warning("job %s: unknown result event dropped", job_id)

    async def handle_dead(self, body: bytes) -> None:
        """``ppe.jobs.dead``: the original job message after MAX_DELIVERY deliveries."""
        try:
            job_id = normalize_job_id(json.loads(body).get("job_id"))
        except (ValueError, AttributeError, TypeError):
            job_id = None
        if job_id is None:
            LOG.warning("dropped a dead-lettered message without a valid job_id")
            return
        changed = self.db.mark_failed(
            job_id, self.clock(), "MAX_RETRIES",
            f"ตรวจซ้ำครบ {self.settings.max_delivery} ครั้งแล้วไม่สำเร็จ",
        )
        self._after_final(job_id, "FAILED MAX_RETRIES", changed)

    def _after_final(self, job_id: str, what: str, image_path: str | None) -> None:
        if image_path is None:
            LOG.info("job %s: %s ignored (unknown or already finished)", job_id, what)
            return
        _unlink_quiet(image_path)
        LOG.info("job %s: %s", job_id, what)

    # -- retention ---------------------------------------------------------

    def purge(self) -> int:
        """Drop jobs older than RESULT_TTL_S and temp images that no active job owns."""
        if self.store is None:
            return 0
        paths = self.db.purge(self.clock() - self.settings.result_ttl_s)
        for path in paths:
            _unlink_quiet(path)
        active = self.db.active_ids()
        oldest_allowed = time.time() - ORPHAN_FILE_MIN_AGE_S
        with contextlib.suppress(OSError):
            for entry in os.scandir(self.images_dir):
                job_id = entry.name.split(".", 1)[0]
                with contextlib.suppress(OSError):
                    if entry.is_file() and job_id not in active and entry.stat().st_mtime < oldest_allowed:
                        _unlink_quiet(entry.path)
        return len(paths)


def _valid_result(result: Any) -> bool:
    if not isinstance(result, dict):
        return False
    for key in ("h", "v"):
        value = result.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            return False
    return isinstance(result.get("detections", []), list)


def _file_too_large() -> JSONResponse:
    return error_response(413, "FILE_TOO_LARGE", "ไฟล์ใหญ่เกิน 15 MB")


# ---------------------------------------------------------------------------
# API key (every path, constant-time)
# ---------------------------------------------------------------------------


class ApiKeyMiddleware:
    """Pure ASGI middleware: runs before routing, so unknown paths are 401 too."""

    def __init__(self, app: Any, api_key: str):
        self.app = app
        self._expected = hashlib.sha256(api_key.encode("utf-8")).digest() if api_key else None

    def is_authorized(self, provided: bytes | None) -> bool:
        if self._expected is None or provided is None:
            return False
        # Hash first so both sides have the same length, then compare in constant time.
        return hmac.compare_digest(hashlib.sha256(provided).digest(), self._expected)

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        provided = next((value for name, value in scope.get("headers", []) if name == b"x-api-key"), None)
        if not self.is_authorized(provided):
            LOG.warning("401 %s %s (missing or wrong API key)", scope.get("method"), scope.get("path"))
            response = JSONResponse(
                {"error": "UNAUTHORIZED", "message": "ต้องมี X-API-Key ที่ถูกต้อง"}, status_code=401
            )
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

_HTTP_CODES = {400: "BAD_REQUEST", 404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}


def create_app(
    settings: Settings | None = None,
    broker: Broker | None = None,
    clock: Callable[[], float] = time.time,
) -> FastAPI:
    settings = settings or Settings.from_env()
    redaction = SecretRedactingFilter([settings.api_key, _url_password(settings.rabbitmq_url)])
    LOG.addFilter(redaction)
    if broker is None:
        broker = RabbitBroker(settings, load_queue_spec(settings))
    gateway = Gateway(settings, broker, clock)

    @contextlib.asynccontextmanager
    async def lifespan(_: FastAPI):
        install_log_redaction(redaction)
        await gateway.startup()
        try:
            yield
        finally:
            await gateway.shutdown()

    app = FastAPI(title="SiteSafe AI gateway", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
    app.state.gateway = gateway
    app.add_middleware(ApiKeyMiddleware, api_key=settings.api_key)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = _HTTP_CODES.get(exc.status_code, "ERROR")
        return error_response(exc.status_code, code, str(exc.detail))

    @app.exception_handler(Exception)
    async def unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        LOG.error("unexpected error: %s", type(exc).__name__, exc_info=exc)
        return error_response(500, "INTERNAL_ERROR", "เกิดข้อผิดพลาดภายใน")

    @app.post("/v1/jobs")
    async def post_job(request: Request) -> JSONResponse:
        return await gateway.submit(request)

    @app.get("/v1/jobs")
    async def list_jobs(ids: str | None = None) -> JSONResponse:
        return gateway.get_jobs(ids)

    @app.get("/v1/jobs/{job_id}")
    async def get_job(job_id: str) -> JSONResponse:
        return gateway.get_job(job_id)

    @app.get("/v1/health")
    async def health() -> JSONResponse:
        return await gateway.health()

    return app


app = create_app()
