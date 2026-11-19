"""Tests of the AI gateway (ai/gateway/main.py) without a real RabbitMQ.

Run from the app root:  python -m pytest ai/gateway/tests -q
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import hashlib
import json
import logging
import sys
import threading
import time
import types
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

APP_ROOT = Path(__file__).resolve().parents[3]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from ai.gateway import main as gw  # noqa: E402

API_KEY = "test-key-5f1c9a7e2b"
WRONG_KEY = "wrong-key-0d3e8b44"
AUTH = {"X-API-Key": API_KEY}
JPEG = b"\xff\xd8\xff\xe0" + b"\x00\x10JFIF" + b"x" * 64
PNG = b"\x89PNG\r\n\x1a\n" + b"y" * 64


# ---------------------------------------------------------------------------
# Fixtures and fakes
# ---------------------------------------------------------------------------


class FakeClock:
    def __init__(self, start: float = 1_795_000_000.0):
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class FakeBroker:
    """Stands in for RabbitMQ: records publishes, can nack / fail / block."""

    def __init__(self):
        self.published: list[dict] = []
        self.mode = "ack"  # ack | nack | unavailable | error
        self.ok = True
        self.workers = 1
        self.gate: threading.Event | None = None
        self.on_result = None
        self.on_dead = None

    async def start(self, on_result, on_dead):
        self.on_result, self.on_dead = on_result, on_dead

    async def publish_job(self, body: bytes, job_id: str) -> None:
        if self.gate is not None:  # wait for the "confirm"
            while not self.gate.is_set():
                await asyncio.sleep(0.01)
        if self.mode == "nack":
            raise gw.QueueFull("nack")
        if self.mode == "unavailable":
            raise gw.QueueUnavailable("no confirm")
        if self.mode == "error":
            raise TimeoutError("confirm timeout")
        self.published.append(json.loads(body))

    async def status(self):
        return gw.BrokerStatus(self.ok, self.workers if self.ok else 0)

    async def close(self):
        pass


class Env:
    def __init__(self, client: TestClient, broker: FakeBroker, clock: FakeClock, settings: gw.Settings):
        self.client, self.broker, self.clock, self.settings = client, broker, clock, settings

    @property
    def gateway(self) -> gw.Gateway:
        return self.client.app.state.gateway

    def call(self, fn, *args):
        """Run on the app's event loop thread (the thread that owns jobs.db)."""
        return self.client.portal.call(fn, *args)

    def deliver(self, payload, queue: str = "results"):
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        handler = self.broker.on_result if queue == "results" else self.broker.on_dead
        self.call(handler, body)

    def depth(self) -> int:
        return self.call(self.gateway.db.depth)

    def seed_active(self, count: int, status: str = "QUEUED") -> list[str]:
        ids = [str(uuid.uuid4()) for _ in range(count)]

        def insert():
            for job_id in ids:
                self.gateway.db.insert(job_id, self.clock(), "", "0" * 64)
                if status == "PROCESSING":
                    self.gateway.db.mark_started(job_id, self.clock())

        self.call(insert)
        return ids

    def post(self, job_id: str | None = None, data: bytes = JPEG, *, sha: str | None = None,
             headers=AUTH, filename: str = "photo.jpg"):
        job_id = job_id or str(uuid.uuid4())
        fields = {"job_id": job_id, "sha256": sha if sha is not None else hashlib.sha256(data).hexdigest()}
        return self.client.post("/v1/jobs", data=fields, files={"image": (filename, data, "image/jpeg")},
                                headers=headers)


@pytest.fixture
def make_env(tmp_path):
    opened: list[TestClient] = []

    def factory(**overrides) -> Env:
        base = dict(
            api_key=API_KEY,
            rabbitmq_url="amqp://sitesafe:rabbit-secret-pw@localhost:5672/",
            jobs_db_path=str(tmp_path / f"jobs-{len(opened)}.db"),
            images_dir=str(tmp_path / f"images-{len(opened)}"),
            gpu_name="NVIDIA L4",
            cleanup_interval_s=3600,
        )
        base.update(overrides)
        settings = gw.Settings(**base)
        broker, clock = FakeBroker(), FakeClock()
        client = TestClient(gw.create_app(settings, broker=broker, clock=clock))
        client.__enter__()
        opened.append(client)
        return Env(client, broker, clock, settings)

    yield factory
    for client in opened:
        client.__exit__(None, None, None)


@pytest.fixture
def env(make_env) -> Env:
    return make_env()


def done_result(h=1, v=0, **extra):
    result = {
        "h": h, "v": v,
        "detections": [{"cls": "NO_HARDHAT", "confidence": 0.87, "box": [412, 130, 596, 380]}] * h,
        "image_w": 4000, "image_h": 3000, "model_version": "ppe-yolo-v1",
        "conf_threshold": 0.5, "infer_ms": 41,
    }
    result.update(extra)
    return result


# ---------------------------------------------------------------------------
# The 4 APIs of DESIGN 5.1
# ---------------------------------------------------------------------------


def test_post_job_202_and_queue_message(env):
    job_id = str(uuid.uuid4())
    response = env.post(job_id)
    assert response.status_code == 202
    assert response.json() == {"job_id": job_id, "status": "QUEUED", "queue_depth": 1}

    assert len(env.broker.published) == 1
    message = env.broker.published[0]
    assert set(message) == {"job_id", "image_path", "queued_at"}
    assert message["job_id"] == job_id
    assert message["queued_at"].endswith("Z")
    assert Path(message["image_path"]).read_bytes() == JPEG  # temp copy for the worker
    assert Path(message["image_path"]).parent == Path(env.settings.images_dir)


def test_get_job_shape_through_lifecycle(env):
    job_id = str(uuid.uuid4())
    env.post(job_id)
    body = env.client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()
    assert body == {
        "job_id": job_id, "status": "QUEUED", "queued_at": gw.iso_utc(env.clock()),
        "started_at": None, "finished_at": None, "result": None, "error": None,
    }

    env.clock.advance(3)
    env.deliver({"job_id": job_id, "event": "STARTED", "result": None, "error": None})
    body = env.client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()
    assert body["status"] == "PROCESSING" and body["started_at"] == gw.iso_utc(env.clock())

    env.clock.advance(1)
    env.deliver({"job_id": job_id, "event": "DONE", "result": done_result(), "error": None})
    body = env.client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()
    assert body["status"] == "DONE"
    assert body["finished_at"] == gw.iso_utc(env.clock())
    assert body["result"] == done_result()
    assert body["error"] is None


def test_get_job_unknown_or_invalid_is_404(env):
    for job_id in (str(uuid.uuid4()), "not-a-uuid", "..%2E%2E"):
        response = env.client.get(f"/v1/jobs/{job_id}", headers=AUTH)
        assert response.status_code == 404
        assert response.json()["error"] == "JOB_NOT_FOUND"
    # "/" decoded inside the id leaves the job route: still a JSON 404
    response = env.client.get("/v1/jobs/..%2F..%2Fetc", headers=AUTH)
    assert response.status_code == 404 and response.json()["error"] == "NOT_FOUND"


def test_get_jobs_many(env):
    a, b = str(uuid.uuid4()), str(uuid.uuid4())
    env.post(a)
    env.post(b)
    missing = str(uuid.uuid4())
    response = env.client.get(f"/v1/jobs?ids={a},{missing},{b},garbage", headers=AUTH)
    assert response.status_code == 200
    body = response.json()
    assert [job["job_id"] for job in body["jobs"]] == [a, b]
    assert body["not_found"] == [missing, "garbage"]


def test_get_jobs_limit_100(env):
    hundred = ",".join(str(uuid.uuid4()) for _ in range(100))
    assert env.client.get(f"/v1/jobs?ids={hundred}", headers=AUTH).status_code == 200
    response = env.client.get(f"/v1/jobs?ids={hundred},{uuid.uuid4()}", headers=AUTH)
    assert response.status_code == 400
    assert response.json()["error"] == "BAD_REQUEST"
    assert env.client.get("/v1/jobs", headers=AUTH).status_code == 400


def test_health_ok(env):
    env.seed_active(37)
    response = env.client.get("/v1/health", headers=AUTH)
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok", "rabbitmq": "ok", "workers": 1, "queue_depth": 37,
        "max_queue_depth": 200, "gpu": "NVIDIA L4", "model_version": "unknown",
    }


def test_health_model_version_from_latest_result(env):
    job_id = str(uuid.uuid4())
    env.post(job_id)
    env.deliver({"job_id": job_id, "event": "DONE", "result": done_result(model_version="ppe-yolo-v2")})
    assert env.client.get("/v1/health", headers=AUTH).json()["model_version"] == "ppe-yolo-v2"


def test_health_503_without_rabbitmq_or_workers(env):
    env.broker.workers = 0
    response = env.client.get("/v1/health", headers=AUTH)
    assert response.status_code == 503
    assert response.json()["workers"] == 0 and response.json()["rabbitmq"] == "ok"

    env.broker.ok = False
    response = env.client.get("/v1/health", headers=AUTH)
    assert response.status_code == 503
    assert response.json()["rabbitmq"] == "down"


# ---------------------------------------------------------------------------
# API key: 401 on every path, constant-time, never logged
# ---------------------------------------------------------------------------

ROUTES = [
    ("POST", "/v1/jobs"),
    ("GET", "/v1/jobs/{id}"),
    ("GET", "/v1/jobs?ids={id}"),
    ("GET", "/v1/health"),
    ("GET", "/v1/does-not-exist"),
]


@pytest.mark.parametrize("method,path", ROUTES)
@pytest.mark.parametrize("headers", [{}, {"X-API-Key": ""}, {"X-API-Key": WRONG_KEY},
                                     {"X-API-Key": API_KEY.upper()}, {"X-API-Key": API_KEY + " "},
                                     {"Authorization": f"Bearer {API_KEY}"}],
                         ids=["none", "empty", "wrong", "case", "suffix", "other-header"])
def test_401_on_every_route(env, method, path, headers):
    job_id = str(uuid.uuid4())
    url = path.format(id=job_id)
    if method == "POST":
        response = env.post(job_id, headers=headers)
    else:
        response = env.client.request(method, url, headers=headers)
    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"
    assert env.broker.published == []
    assert env.depth() == 0  # Q-1: no new job


def test_empty_configured_key_rejects_everything(make_env):
    env = make_env(api_key="")
    assert env.client.get("/v1/health", headers={"X-API-Key": ""}).status_code == 401
    assert env.client.get("/v1/health").status_code == 401


def test_key_compared_in_constant_time(env, monkeypatch):
    calls = []
    real = gw.hmac.compare_digest

    def spy(a, b):
        calls.append((len(a), len(b)))
        return real(a, b)

    monkeypatch.setattr(gw.hmac, "compare_digest", spy)
    assert env.client.get("/v1/health", headers=AUTH).status_code == 200
    assert env.client.get("/v1/health", headers={"X-API-Key": "x"}).status_code == 401
    assert calls[:2] == [(32, 32), (32, 32)]  # sha256 digests: equal length whatever the input


def test_key_never_in_logs(make_env, caplog):
    caplog.set_level(logging.DEBUG)
    env = make_env()
    job_id = str(uuid.uuid4())
    env.post(job_id)
    env.post(job_id)
    env.client.get(f"/v1/jobs/{job_id}", headers=AUTH)
    env.client.get(f"/v1/jobs?ids={job_id}", headers=AUTH)
    env.client.get("/v1/health", headers=AUTH)
    env.client.get("/v1/health", headers={"X-API-Key": WRONG_KEY})
    env.post(headers={"X-API-Key": WRONG_KEY})
    env.broker.mode = "unavailable"
    env.post()
    # even a careless log call with the key is redacted
    gw.LOG.warning("debug key=%s url=%s", API_KEY, env.settings.rabbitmq_url)

    text = caplog.text + "".join(str(r.__dict__) for r in caplog.records)
    assert caplog.records, "expected some log lines"
    assert API_KEY not in text
    assert "rabbit-secret-pw" not in text
    assert "[REDACTED]" in text


# ---------------------------------------------------------------------------
# Duplicate job_id (D-05, Q-6)
# ---------------------------------------------------------------------------


def test_duplicate_job_id_200_no_new_job(env):
    env.seed_active(2)
    job_id = str(uuid.uuid4())
    assert env.post(job_id).status_code == 202
    assert env.depth() == 3

    again = env.post(job_id, data=PNG)
    assert again.status_code == 200
    assert again.json()["job_id"] == job_id and again.json()["status"] == "QUEUED"
    assert set(again.json()) == {"job_id", "status", "queued_at", "started_at", "finished_at", "result", "error"}
    assert env.depth() == 3
    assert len(env.broker.published) == 1


def test_duplicate_of_finished_job_returns_current_status(env):
    job_id = str(uuid.uuid4())
    env.post(job_id)
    env.deliver({"job_id": job_id, "event": "DONE", "result": done_result(h=2)})
    again = env.post(job_id)
    assert again.status_code == 200
    assert again.json()["status"] == "DONE" and again.json()["result"]["h"] == 2
    assert len(env.broker.published) == 1


def test_duplicate_while_queue_full_is_still_200(make_env):
    env = make_env(max_queue_depth=5)
    job_id = str(uuid.uuid4())
    env.post(job_id)
    env.seed_active(4)
    assert env.post().status_code == 429
    assert env.post(job_id).status_code == 200


def test_uppercase_job_id_is_the_same_job(env):
    job_id = str(uuid.uuid4())
    env.post(job_id)
    assert env.post(job_id.upper()).status_code == 200
    assert env.client.get(f"/v1/jobs/{job_id.upper()}", headers=AUTH).json()["job_id"] == job_id


# ---------------------------------------------------------------------------
# Publisher confirm (DESIGN 6.2)
# ---------------------------------------------------------------------------


def test_202_is_sent_only_after_confirm(env):
    env.broker.gate = threading.Event()
    job_id = str(uuid.uuid4())
    with concurrent.futures.ThreadPoolExecutor(1) as pool:
        future = pool.submit(env.post, job_id)
        time.sleep(0.3)
        assert not future.done(), "answered before RabbitMQ confirmed"
        env.broker.gate.set()
        response = future.result(timeout=5)
    assert response.status_code == 202
    assert env.broker.published[0]["job_id"] == job_id


@pytest.mark.parametrize("mode", ["unavailable", "error"])
def test_no_confirm_is_503_and_job_not_kept(env, mode):
    env.broker.mode = mode
    job_id = str(uuid.uuid4())
    response = env.post(job_id)
    assert response.status_code == 503
    assert response.json()["error"] == "QUEUE_UNAVAILABLE"
    assert env.client.get(f"/v1/jobs/{job_id}", headers=AUTH).status_code == 404
    assert env.depth() == 0
    assert list(Path(env.settings.images_dir).iterdir()) == []  # temp file removed

    env.broker.mode = "ack"  # the web sends again later with the same job_id
    assert env.post(job_id).status_code == 202


def test_broker_not_connected_is_503(env):
    env.broker.ok = False
    env.broker.mode = "unavailable"
    assert env.post().status_code == 503


# ---------------------------------------------------------------------------
# Backpressure (DESIGN 6.3, TEST-DATA Q-3 … Q-5)
# ---------------------------------------------------------------------------


def test_queue_depth_199_accepted_200_rejected(env):
    assert env.settings.max_queue_depth == 200
    env.seed_active(150)
    env.seed_active(49, status="PROCESSING")  # PROCESSING counts too
    assert env.depth() == 199

    accepted = env.post()
    assert accepted.status_code == 202
    assert accepted.json()["queue_depth"] == 200

    rejected_id = str(uuid.uuid4())
    rejected = env.post(rejected_id)
    assert rejected.status_code == 429
    assert rejected.headers["Retry-After"] == "20"  # max(5, ceil((200-200+10) × 2 s)) with no history
    assert rejected.json() == {
        "error": "QUEUE_FULL", "message": rejected.json()["message"],
        "queue_depth": 200, "max_queue_depth": 200, "retry_after_s": 20,
    }
    # not stored, not created, not published
    assert env.client.get(f"/v1/jobs/{rejected_id}", headers=AUTH).status_code == 404
    assert len(env.broker.published) == 1
    assert env.depth() == 200
    assert len(list(Path(env.settings.images_dir).iterdir())) == 1


def test_q3_q4_q5_with_max_depth_5(make_env):
    env = make_env(max_queue_depth=5)
    env.seed_active(4)
    q3 = env.post()
    assert q3.status_code == 202 and q3.json()["queue_depth"] == 5  # Q-3

    q4_id = str(uuid.uuid4())
    q4 = env.post(q4_id)
    assert q4.status_code == 429 and "Retry-After" in q4.headers  # Q-4
    assert env.client.get(f"/v1/jobs/{q4_id}", headers=AUTH).status_code == 404
    assert env.depth() == 5

    # Q-5: the worker drains the queue, then the same job_id is accepted
    for message in env.broker.published:
        env.deliver({"job_id": message["job_id"], "event": "DONE", "result": done_result(h=0)})
    env.call(env.gateway.db._db.execute, "UPDATE jobs SET status = 'DONE' WHERE status = 'QUEUED'")
    assert env.depth() == 0
    q5 = env.post(q4_id)
    assert q5.status_code == 202
    env.deliver({"job_id": q4_id, "event": "DONE", "result": done_result(h=0)})
    assert env.client.get(f"/v1/jobs/{q4_id}", headers=AUTH).json()["status"] == "DONE"


def test_rabbitmq_reject_publish_is_429(env):
    env.broker.mode = "nack"  # second layer: x-max-length + reject-publish
    job_id = str(uuid.uuid4())
    response = env.post(job_id)
    assert response.status_code == 429
    assert response.json()["error"] == "QUEUE_FULL"
    assert int(response.headers["Retry-After"]) >= 5
    assert env.client.get(f"/v1/jobs/{job_id}", headers=AUTH).status_code == 404
    assert list(Path(env.settings.images_dir).iterdir()) == []


@pytest.mark.parametrize(
    "depth,maximum,samples,default,expected",
    [
        (200, 200, [], 2.0, 20),
        (5, 5, [], 2.0, 20),
        (200, 200, [3000] * 50, 2.0, 30),
        (200, 200, [100] * 50, 2.0, 5),  # 10 × 0.1 s = 1 → at least 5
        (200, 200, [1234] * 50, 2.0, 13),  # ceil(12.34)
        (200, 200, [300] * 10, 2.0, 5),
        (210, 200, [700] * 50, 2.0, 14),  # ceil(20 × 0.7) exactly 14, no float drift
        (150, 200, [], 2.0, 5),  # second-layer refusal below the threshold
    ],
)
def test_retry_after_formula(depth, maximum, samples, default, expected):
    assert gw.compute_retry_after(depth, maximum, samples, default) == expected


def test_retry_after_uses_latest_50_jobs(make_env):
    env = make_env(max_queue_depth=60)
    ids = [str(uuid.uuid4()) for _ in range(60)]
    for index, job_id in enumerate(ids):
        assert env.post(job_id).status_code == 202
    # 10 older jobs took 10 s each, the latest 50 took 1.5 s each
    for index, job_id in enumerate(ids):
        env.deliver({"job_id": job_id, "event": "STARTED"})
        env.clock.advance(10 if index < 10 else 1.5)
        env.deliver({"job_id": job_id, "event": "DONE", "result": done_result(h=0, infer_ms=40)})
    env.seed_active(60)
    response = env.post()
    assert response.status_code == 429
    assert response.json()["retry_after_s"] == 15  # ceil(10 × 1.5)
    assert response.headers["Retry-After"] == "15"


# ---------------------------------------------------------------------------
# ppe.results: one result set, PROCESSING timeout, temp file deletion
# ---------------------------------------------------------------------------


def test_one_result_set_only(env):
    job_id = str(uuid.uuid4())
    env.post(job_id)
    image_path = Path(env.broker.published[0]["image_path"])
    env.deliver({"job_id": job_id, "event": "STARTED"})
    env.deliver({"job_id": job_id, "event": "DONE", "result": done_result(h=1, v=0)})
    assert not image_path.exists()  # deleted when the job ended

    # worker died after publishing but before ack → the job runs again
    env.deliver({"job_id": job_id, "event": "STARTED"})
    env.deliver({"job_id": job_id, "event": "DONE", "result": done_result(h=3, v=2)})
    env.deliver({"job_id": job_id, "event": "FAILED", "error": {"code": "IMAGE_UNREADABLE", "message": "x"}})
    env.deliver({"job_id": job_id}, queue="dead")

    body = env.client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()
    assert body["status"] == "DONE"
    assert (body["result"]["h"], body["result"]["v"]) == (1, 0)
    assert body["error"] is None


def test_failed_image_unreadable(env):
    job_id = str(uuid.uuid4())
    env.post(job_id)
    image_path = Path(env.broker.published[0]["image_path"])
    env.deliver({"job_id": job_id, "event": "STARTED"})
    env.deliver({"job_id": job_id, "event": "FAILED", "result": None,
                 "error": {"code": "IMAGE_UNREADABLE", "message": "Unable to open or decode image"}})
    body = env.client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()
    assert body["status"] == "FAILED" and body["result"] is None
    assert body["error"] == {"code": "IMAGE_UNREADABLE", "message": "Unable to open or decode image"}
    assert not image_path.exists()


def test_malformed_or_unknown_results_are_ignored(env):
    job_id = str(uuid.uuid4())
    env.post(job_id)
    env.deliver(b"not json")
    env.deliver(b"[1,2]")
    env.deliver({"job_id": "nope", "event": "DONE", "result": done_result()})
    env.deliver({"job_id": str(uuid.uuid4()), "event": "DONE", "result": done_result()})
    env.deliver({"job_id": job_id, "event": "DONE", "result": {"h": "1", "v": 0}})
    env.deliver({"job_id": job_id, "event": "DONE", "result": None})
    env.deliver({"job_id": job_id, "event": "WHATEVER"})
    assert env.client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()["status"] == "QUEUED"


def test_processing_timeout_reported_as_queued(env):
    assert env.settings.processing_timeout_s == 120
    job_id = str(uuid.uuid4())
    env.post(job_id)
    env.deliver({"job_id": job_id, "event": "STARTED"})
    env.clock.advance(120)
    assert env.client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()["status"] == "PROCESSING"
    env.clock.advance(1)
    assert env.client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()["status"] == "QUEUED"
    listed = env.client.get(f"/v1/jobs?ids={job_id}", headers=AUTH).json()["jobs"][0]
    assert listed["status"] == "QUEUED"
    assert env.depth() == 1  # still counted in queue_depth

    # redelivered to the restarted worker: a new event makes it PROCESSING again
    env.deliver({"job_id": job_id, "event": "STARTED"})
    assert env.client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()["status"] == "PROCESSING"
    env.deliver({"job_id": job_id, "event": "DONE", "result": done_result()})
    assert env.client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()["status"] == "DONE"


# ---------------------------------------------------------------------------
# ppe.jobs.dead → FAILED MAX_RETRIES
# ---------------------------------------------------------------------------


def test_dead_letter_marks_failed_max_retries(env):
    job_id = str(uuid.uuid4())
    env.post(job_id)
    message = env.broker.published[0]
    for _ in range(3):
        env.deliver({"job_id": job_id, "event": "STARTED"})
    env.deliver(json.dumps(message).encode(), queue="dead")

    body = env.client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()
    assert body["status"] == "FAILED"
    assert body["error"]["code"] == "MAX_RETRIES"
    assert body["result"] is None and body["finished_at"] is not None
    assert not Path(message["image_path"]).exists()
    assert env.depth() == 0

    # a late result after dead-lettering does not change the outcome
    env.deliver({"job_id": job_id, "event": "DONE", "result": done_result()})
    assert env.client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()["status"] == "FAILED"


def test_dead_letter_garbage_is_ignored(env):
    env.deliver(b"\x00garbage", queue="dead")
    env.deliver({"image_path": "/x"}, queue="dead")


# ---------------------------------------------------------------------------
# Input checks of API 1
# ---------------------------------------------------------------------------


def test_missing_fields_400(env):
    data = JPEG
    sha = hashlib.sha256(data).hexdigest()
    job_id = str(uuid.uuid4())
    cases = [
        ({"sha256": sha}, {"image": ("a.jpg", data, "image/jpeg")}),
        ({"job_id": job_id}, {"image": ("a.jpg", data, "image/jpeg")}),
        ({"job_id": job_id, "sha256": sha}, None),
        ({"job_id": "not-a-uuid", "sha256": sha}, {"image": ("a.jpg", data, "image/jpeg")}),
        ({"job_id": job_id, "sha256": "abc"}, {"image": ("a.jpg", data, "image/jpeg")}),
        ({"job_id": job_id, "sha256": sha, "image": "plain text"}, None),
    ]
    for fields, files in cases:
        response = env.client.post("/v1/jobs", data=fields, files=files, headers=AUTH)
        assert response.status_code == 400, fields
        assert response.json()["error"] == "BAD_REQUEST"
    assert env.client.post("/v1/jobs", content=b"{}", headers={**AUTH, "Content-Type": "application/json"}).status_code == 400
    assert env.depth() == 0 and env.broker.published == []


def test_sha256_mismatch_400(env):
    response = env.post(sha=hashlib.sha256(b"other").hexdigest())
    assert response.status_code == 400
    assert env.depth() == 0


def test_sha256_is_case_insensitive(env):
    assert env.post(sha=hashlib.sha256(JPEG).hexdigest().upper()).status_code == 202


@pytest.mark.parametrize("data", [b"GIF89a....", b"%PDF-1.7", b"", b"\xff\xd8", b"hello.jpg"])
def test_unsupported_type_415(env, data):
    response = env.post(data=data, filename="photo.jpg")
    assert response.status_code == 415
    assert response.json()["error"] == "UNSUPPORTED_TYPE"
    assert env.depth() == 0


def test_png_accepted(env):
    assert env.post(data=PNG, filename="x.png").status_code == 202
    assert env.broker.published[0]["image_path"].endswith(".png")


def test_size_limit_15_mib(env):
    limit = 15 * 1_048_576
    assert limit == 15_728_640
    exact = b"\xff\xd8\xff" + b"a" * (limit - 3)
    assert env.post(data=exact).status_code == 202

    over = exact + b"b"
    response = env.post(data=over)
    assert response.status_code == 413
    assert response.json()["error"] == "FILE_TOO_LARGE"
    assert env.depth() == 1


def test_large_body_cut_off(env):
    big = b"\xff\xd8\xff" + b"a" * (20 * 1_048_576)
    response = env.post(data=big)
    assert response.status_code == 413


def test_streamed_body_without_length_cut_off(env):
    """No Content-Length (chunked): reading stops once the body passes the cap.

    Driven at the ASGI level because TestClient buffers the whole body first."""
    boundary = "b05boundary"
    job_id = str(uuid.uuid4())
    head = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"job_id\"\r\n\r\n{job_id}\r\n"
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"a.jpg\"\r\n"
        "Content-Type: image/jpeg\r\n\r\n"
    ).encode() + b"\xff\xd8\xff"
    chunks = iter([head] + [b"z" * 1_048_576] * 40 + [f"\r\n--{boundary}--\r\n".encode()])
    pulled = {"bytes": 0}

    async def receive():
        chunk = next(chunks, None)
        if chunk is None:
            return {"type": "http.request", "body": b"", "more_body": False}
        pulled["bytes"] += len(chunk)
        return {"type": "http.request", "body": chunk, "more_body": True}

    sent = []

    async def send(message):
        sent.append(message)

    scope = {
        "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": "POST",
        "scheme": "http", "path": "/v1/jobs", "raw_path": b"/v1/jobs", "root_path": "",
        "query_string": b"", "client": ("test", 1), "server": ("testserver", 80),
        "headers": [(b"x-api-key", API_KEY.encode()),
                    (b"content-type", f"multipart/form-data; boundary={boundary}".encode())],
    }
    env.call(env.client.app, scope, receive, send)
    status = next(m["status"] for m in sent if m["type"] == "http.response.start")
    assert status == 413
    assert env.depth() == 0
    assert pulled["bytes"] < 18 * 1_048_576  # stopped near the 16 MiB cap, not at 40 MiB


# ---------------------------------------------------------------------------
# Retention: results kept 24 h
# ---------------------------------------------------------------------------


def test_results_kept_24_hours(env):
    done_id, active_id = str(uuid.uuid4()), str(uuid.uuid4())
    env.post(done_id)
    env.deliver({"job_id": done_id, "event": "DONE", "result": done_result()})
    env.clock.advance(23 * 3600)
    env.post(active_id)
    env.call(env.gateway.purge)
    assert env.client.get(f"/v1/jobs/{done_id}", headers=AUTH).status_code == 200

    env.clock.advance(3600 + 1)
    env.call(env.gateway.purge)
    assert env.client.get(f"/v1/jobs/{done_id}", headers=AUTH).status_code == 404
    assert env.client.get(f"/v1/jobs/{active_id}", headers=AUTH).status_code == 200
    # once purged, the same job_id can be sent again as a new job
    assert env.post(done_id).status_code == 202


def test_orphan_temp_files_swept(env, tmp_path):
    images = Path(env.settings.images_dir)
    job_id = str(uuid.uuid4())
    env.post(job_id)
    orphan = images / f"{uuid.uuid4()}.jpg"
    orphan.write_bytes(b"x")
    old = time.time() - 3600
    import os
    os.utime(orphan, (old, old))
    os.utime(env.broker.published[0]["image_path"], (old, old))
    env.call(env.gateway.purge)
    assert not orphan.exists()
    assert Path(env.broker.published[0]["image_path"]).exists()  # active job keeps its file


def test_jobs_survive_gateway_restart(make_env, tmp_path):
    first = make_env()
    job_id = str(uuid.uuid4())
    first.post(job_id)
    first.client.__exit__(None, None, None)
    second = make_env(jobs_db_path=first.settings.jobs_db_path, images_dir=first.settings.images_dir)
    assert second.client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()["status"] == "QUEUED"
    assert second.depth() == 1


# ---------------------------------------------------------------------------
# Real RabbitBroker with fake aio-pika objects
# ---------------------------------------------------------------------------


def _settings(**kw):
    base = dict(api_key=API_KEY, publish_timeout_s=0.2)
    base.update(kw)
    return gw.Settings(**base)


def test_fallback_queue_arguments_design_6_1():
    spec = gw.load_queue_spec(_settings(max_queue_depth=200, max_delivery=3), module_name="no.such.module")
    assert (spec.jobs, spec.results, spec.dead) == ("ppe.jobs", "ppe.results", "ppe.jobs.dead")
    assert spec.arguments["ppe.jobs"] == {
        "x-queue-type": "quorum",
        "x-delivery-limit": 3,
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": "ppe.jobs.dead",
        "x-max-length": 200,
        "x-overflow": "reject-publish",
    }
    assert spec.arguments["ppe.results"] == {"x-queue-type": "quorum"}
    assert spec.arguments["ppe.jobs.dead"] == {"x-queue-type": "quorum"}


def test_queue_spec_from_common_module(monkeypatch):
    module = types.ModuleType("fake_common_queues")
    module.JOBS_QUEUE, module.RESULTS_QUEUE, module.DEAD_QUEUE = "ppe.jobs", "ppe.results", "ppe.jobs.dead"
    module.QUEUE_ARGUMENTS = {
        "ppe.jobs": {"x-queue-type": "quorum", "x-max-length": 7},
        "ppe.results": {"x-queue-type": "quorum"},
        "ppe.jobs.dead": {"x-queue-type": "quorum"},
    }
    monkeypatch.setitem(sys.modules, "fake_common_queues", module)
    spec = gw.load_queue_spec(_settings(), module_name="fake_common_queues")
    assert spec.arguments["ppe.jobs"]["x-max-length"] == 7 and spec.declarer is None

    del module.QUEUE_ARGUMENTS
    module.declare_queues = lambda channel: None
    spec = gw.load_queue_spec(_settings(), module_name="fake_common_queues")
    assert spec.arguments is None and spec.declarer is module.declare_queues


class FakeChannel:
    def __init__(self):
        self.declared = []

    async def declare_queue(self, name, **kwargs):
        self.declared.append((name, kwargs))
        return types.SimpleNamespace(name=name, declaration_result=types.SimpleNamespace(consumer_count=1))


def test_rabbit_broker_declares_three_durable_quorum_queues():
    settings = _settings(max_queue_depth=200, max_delivery=3)
    broker = gw.RabbitBroker(settings, gw.load_queue_spec(settings, module_name="no.such.module"))
    channel = FakeChannel()
    asyncio.run(broker.declare(channel))
    names = [name for name, _ in channel.declared]
    assert names == ["ppe.jobs.dead", "ppe.results", "ppe.jobs"]  # dead-letter target first
    for _, kwargs in channel.declared:
        assert kwargs["durable"] is True
        assert kwargs["arguments"]["x-queue-type"] == "quorum"
    jobs_args = dict(channel.declared)["ppe.jobs"]["arguments"]
    assert jobs_args["x-delivery-limit"] == 3
    assert jobs_args["x-dead-letter-routing-key"] == "ppe.jobs.dead"
    assert jobs_args["x-max-length"] == 200
    assert jobs_args["x-overflow"] == "reject-publish"


class FakeExchange:
    def __init__(self, outcome):
        self.outcome = outcome
        self.calls = []

    async def publish(self, message, routing_key, *, mandatory, timeout):
        self.calls.append((message, routing_key, mandatory, timeout))
        if isinstance(self.outcome, BaseException):
            raise self.outcome
        if self.outcome == "hang":
            await asyncio.sleep(10)
        return self.outcome


def _publish_with(outcome):
    import aiormq

    settings = _settings()
    broker = gw.RabbitBroker(settings, gw.load_queue_spec(settings, module_name="no.such.module"))
    broker._ready = True
    broker._exchange = FakeExchange(outcome)

    async def run():
        await broker.publish_job(b'{"job_id":"x"}', "x")

    asyncio.run(run())
    return broker._exchange, aiormq


def test_rabbit_publish_ack_is_success_and_persistent():
    import aio_pika
    import aiormq

    exchange, _ = _publish_with(aiormq.spec.Basic.Ack(delivery_tag=1))
    message, routing_key, mandatory, timeout = exchange.calls[0]
    assert routing_key == "ppe.jobs" and mandatory is True and timeout == 0.2
    assert message.delivery_mode == aio_pika.DeliveryMode.PERSISTENT
    assert message.body == b'{"job_id":"x"}'


def test_rabbit_publish_nack_is_queue_full():
    import aiormq

    with pytest.raises(gw.QueueFull):
        _publish_with(aiormq.exceptions.DeliveryError(None, aiormq.spec.Basic.Nack(delivery_tag=1)))


@pytest.mark.parametrize("outcome", ["hang", None, "returned", TimeoutError(), ConnectionError("gone")])
def test_rabbit_publish_without_confirm_is_unavailable(outcome):
    from aiormq.exceptions import PublishError

    if outcome == "returned":
        outcome = PublishError.__new__(PublishError)
    with pytest.raises(gw.QueueUnavailable):
        _publish_with(outcome)


def test_rabbit_publish_when_not_connected():
    settings = _settings()
    broker = gw.RabbitBroker(settings, gw.load_queue_spec(settings, module_name="no.such.module"))
    with pytest.raises(gw.QueueUnavailable):
        asyncio.run(broker.publish_job(b"{}", "x"))
    assert asyncio.run(broker.status()) == gw.BrokerStatus(False, 0)


def test_rabbit_consumer_acks_after_handler_and_requeues_on_error():
    events = []

    class Message:
        body = b"{}"

        async def ack(self):
            events.append("ack")

        async def nack(self, requeue):
            events.append(("nack", requeue))

    async def ok(body):
        events.append("handled")

    async def boom(body):
        raise RuntimeError("db locked")

    async def run():
        await gw.RabbitBroker._wrap(ok, "ppe.results")(Message())
        await gw.RabbitBroker._wrap(boom, "ppe.results")(Message())

    asyncio.run(run())
    assert events == ["handled", "ack", ("nack", True)]


def test_settings_from_env_defaults_design_11():
    settings = gw.Settings.from_env({"GATEWAY_API_KEY": "k"})
    assert settings.max_queue_depth == 200
    assert settings.max_delivery == 3
    assert settings.processing_timeout_s == 120
    assert settings.result_ttl_s == 24 * 3600
    settings = gw.Settings.from_env({"MAX_QUEUE_DEPTH": "5", "PROCESSING_TIMEOUT_S": "30"})
    assert settings.max_queue_depth == 5 and settings.processing_timeout_s == 30
    with pytest.raises(ValueError):
        gw.Settings.from_env({"MAX_QUEUE_DEPTH": "0"})
