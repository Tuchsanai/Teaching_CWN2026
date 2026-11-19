"""Gateway + RabbitMQ + worker end to end, with a fake detector (no GPU).

Skipped unless RABBITMQ_TEST_URL is set:

    docker run -d --name rabbit-test -p 127.0.0.1:56720:5672 rabbitmq:4-management
    docker exec rabbit-test rabbitmqctl add_user t t
    docker exec rabbit-test rabbitmqctl set_permissions -p / t ".*" ".*" ".*"
    RABBITMQ_TEST_URL=amqp://t:t@127.0.0.1:56720/ python -m pytest ai/worker/tests -q

The real ``ai.worker.worker.run_worker`` (pika) and the real gateway (aio-pika) both
declare the queues through ``ai/common/queues.py``.  The test deletes the three
ppe.* queues first, so use a throw-away broker.
"""

from __future__ import annotations

import hashlib
import io
import os
import sys
import threading
import time
import uuid
from pathlib import Path

import pytest
from PIL import Image

APP_ROOT = Path(__file__).resolve().parents[3]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from ai.common import queues  # noqa: E402
from ai.gateway import main as gw  # noqa: E402
from ai.worker import worker as wk  # noqa: E402

URL = os.environ.get("RABBITMQ_TEST_URL", "")
pytestmark = pytest.mark.skipif(not URL, reason="RABBITMQ_TEST_URL not set")

API_KEY = "pipeline-key-5c1e"
AUTH = {"X-API-Key": API_KEY}
POISON_SIZE = (13, 7)


class SizeDetector:
    """1 NO_HARDHAT + 2 NO_VEST on every image; crashes on POISON_SIZE images."""

    def __init__(self):
        self.calls = 0

    def detect(self, image, threshold):
        self.calls += 1
        if image.size == POISON_SIZE:
            raise RuntimeError("simulated CUDA failure")
        w, h = image.size
        return [
            wk.Detection("NO_HARDHAT", 0.91, (0, 0, w / 2, h / 2)),
            wk.Detection("NO_VEST", 0.80, (w / 2, 0, w, h / 2)),
            wk.Detection("NO_VEST", 0.70, (0, h / 2, w / 2, h)),
            wk.Detection("NO_VEST", 0.10, (0, 0, 1, 1)),  # below the threshold
        ]


def jpeg(size) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, (90, 160, 30)).save(buf, "JPEG")
    return buf.getvalue()


def wait_for(predicate, timeout=30.0, step=0.1):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(step)
    raise AssertionError("condition not reached in time")


@pytest.fixture
def pipeline(tmp_path, monkeypatch):
    import pika
    from fastapi.testclient import TestClient

    monkeypatch.setenv("MAX_QUEUE_DEPTH", "50")
    monkeypatch.setenv("MAX_DELIVERY", "2")
    with pika.BlockingConnection(pika.URLParameters(URL)) as connection:
        channel = connection.channel()
        for name in (queues.JOBS_QUEUE, queues.RESULTS_QUEUE, queues.DEAD_QUEUE):
            channel.queue_delete(name)

    settings = gw.Settings(
        api_key=API_KEY, rabbitmq_url=URL, max_queue_depth=50, max_delivery=2,
        jobs_db_path=str(tmp_path / "jobs.db"), images_dir=str(tmp_path / "images"),
        gpu_name="fake-gpu", model_version="ppe-yolo-fake", cleanup_interval_s=3600,
    )
    app = gw.create_app(settings, broker=gw.RabbitBroker(settings, gw.load_queue_spec(settings)))
    detector = SizeDetector()
    stop = threading.Event()
    errors = []

    def worker():
        try:
            wk.run_worker(detector, 0.5, "ppe-yolo-fake", stop, URL)
        except Exception as exc:  # pragma: no cover - reported by the test below
            errors.append(exc)

    with TestClient(app) as client:
        wait_for(lambda: client.app.state.gateway.broker._ready)
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        wait_for(lambda: client.get("/v1/health", headers=AUTH).status_code == 200)
        try:
            yield client, settings, detector
        finally:
            stop.set()
            thread.join(10)
    assert not errors, errors


def submit(client, data, job_id=None, filename="photo.jpg"):
    job_id = job_id or str(uuid.uuid4())
    response = client.post(
        "/v1/jobs",
        data={"job_id": job_id, "sha256": hashlib.sha256(data).hexdigest()},
        files={"image": (filename, data, "image/jpeg")},
        headers=AUTH,
    )
    return job_id, response


def final(client, job_id, timeout=30.0):
    def done():
        body = client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()
        return body if body.get("status") in ("DONE", "FAILED") else None

    return wait_for(done, timeout)


def test_health_reports_one_worker(pipeline):
    client, _, _ = pipeline
    body = client.get("/v1/health", headers=AUTH).json()
    assert body["status"] == "ok" and body["rabbitmq"] == "ok" and body["workers"] == 1
    assert body["gpu"] == "fake-gpu" and body["max_queue_depth"] == 50


def test_job_goes_through_queue_and_worker_to_done(pipeline):
    client, settings, _ = pipeline
    job_id, response = submit(client, jpeg((320, 240)))
    assert response.status_code == 202 and response.json()["status"] == "QUEUED"
    body = final(client, job_id)
    assert body["status"] == "DONE" and body["error"] is None
    result = body["result"]
    assert (result["h"], result["v"]) == (1, 2)
    assert len(result["detections"]) == 3
    assert result["detections"][0] == {"cls": "NO_HARDHAT", "confidence": 0.91, "box": [0, 0, 160, 120]}
    assert (result["image_w"], result["image_h"]) == (320, 240)
    assert result["model_version"] == "ppe-yolo-fake" and result["conf_threshold"] == 0.5
    assert body["queued_at"] and body["started_at"] and body["finished_at"]
    # the temporary image is deleted once the job is finished (DESIGN 10)
    assert wait_for(lambda: not any(Path(settings.images_dir).glob(f"{job_id}.*")))
    # the same job_id again: no new job (D-05)
    again = submit(client, jpeg((320, 240)), job_id=job_id)[1]
    assert again.status_code == 200 and again.json()["status"] == "DONE"


def test_unreadable_image_is_failed_image_unreadable(pipeline):
    client, _, _ = pipeline
    good = jpeg((640, 480))
    job_id, response = submit(client, good[: len(good) // 2], filename="corrupt_half.jpg")
    assert response.status_code == 202
    body = final(client, job_id)
    assert body["status"] == "FAILED" and body["error"]["code"] == "IMAGE_UNREADABLE"


def test_poison_job_is_dead_lettered_after_delivery_limit(pipeline):
    client, _, detector = pipeline
    job_id, response = submit(client, jpeg(POISON_SIZE))
    assert response.status_code == 202
    body = final(client, job_id, timeout=60)
    assert body["status"] == "FAILED" and body["error"]["code"] == "MAX_RETRIES"
    assert detector.calls >= 2
    # the worker is still alive afterwards
    job_id, _ = submit(client, jpeg((64, 48)))
    assert final(client, job_id)["status"] == "DONE"


def test_many_jobs_all_finish_once(pipeline):
    client, _, _ = pipeline
    ids = [submit(client, jpeg((32 + i, 24)))[0] for i in range(20)]
    for job_id in ids:
        assert final(client, job_id)["status"] == "DONE"
    listed = client.get("/v1/jobs", params={"ids": ",".join(ids)}, headers=AUTH).json()
    assert len(listed["jobs"]) == 20 and listed["not_found"] == []
