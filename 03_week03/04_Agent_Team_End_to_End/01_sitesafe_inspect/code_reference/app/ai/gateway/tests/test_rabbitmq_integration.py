"""Gateway against a real RabbitMQ (skipped unless RABBITMQ_TEST_URL is set).

    docker run -d --name rabbit-test -p 127.0.0.1:56720:5672 rabbitmq:4-management
    docker exec rabbit-test rabbitmqctl add_user t t
    docker exec rabbit-test rabbitmqctl set_permissions -p / t ".*" ".*" ".*"
    RABBITMQ_TEST_URL=amqp://t:t@127.0.0.1:56720/ python -m pytest ai/gateway/tests -q

The test deletes and re-creates the three ppe.* queues, so use a throw-away broker.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

APP_ROOT = Path(__file__).resolve().parents[3]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from ai.gateway import main as gw  # noqa: E402

URL = os.environ.get("RABBITMQ_TEST_URL", "")
pytestmark = pytest.mark.skipif(not URL, reason="RABBITMQ_TEST_URL not set")

API_KEY = "integration-key-77aa"
AUTH = {"X-API-Key": API_KEY}
JPEG = b"\xff\xd8\xff\xe0" + b"q" * 128


def _wait(predicate, timeout=20.0, step=0.1):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(step)
    raise AssertionError("condition not reached in time")


@pytest.fixture
def real(tmp_path):
    import aio_pika

    async def reset_queues():
        connection = await aio_pika.connect(URL)
        async with connection:
            channel = await connection.channel()
            for name in ("ppe.jobs", "ppe.results", "ppe.jobs.dead"):
                await channel.queue_delete(name)

    asyncio.run(reset_queues())
    settings = gw.Settings(
        api_key=API_KEY, rabbitmq_url=URL, max_queue_depth=3, max_delivery=2,
        jobs_db_path=str(tmp_path / "jobs.db"), images_dir=str(tmp_path / "images"),
        gpu_name="test-gpu", cleanup_interval_s=3600,
    )
    spec = gw.load_queue_spec(settings, module_name="no.such.module")  # DESIGN 6.1 arguments
    client = TestClient(gw.create_app(settings, broker=gw.RabbitBroker(settings, spec)))
    with client:
        _wait(lambda: client.app.state.gateway.broker._ready)
        yield client, settings


def _post(client, job_id, data=JPEG):
    return client.post(
        "/v1/jobs",
        data={"job_id": job_id, "sha256": hashlib.sha256(data).hexdigest()},
        files={"image": ("a.jpg", data, "image/jpeg")},
        headers=AUTH,
    )


def _status(client, job_id):
    return client.get(f"/v1/jobs/{job_id}", headers=AUTH).json().get("status")


class FakeWorker:
    """A worker on the app's loop: prefetch 1, manual ack, results to ppe.results.

    ``crash`` closes its consuming channel without ack after STARTED (like a worker
    process dying mid-job) and starts consuming again on a new channel."""

    def __init__(self, client, behaviour):
        self.client, self.behaviour, self.seen = client, behaviour, []

    def start(self):
        self.client.portal.call(self._start)

    async def _start(self):
        import aio_pika

        self.connection = await aio_pika.connect(URL)
        self.publish_channel = await self.connection.channel(publisher_confirms=True)
        await self._consume()

    async def _consume(self):
        channel = await self.connection.channel()
        await channel.set_qos(prefetch_count=1)
        queue = await channel.declare_queue("ppe.jobs", passive=True)

        async def on_job(message):
            await self._on_job(channel, message)

        await queue.consume(on_job)

    async def _publish(self, payload):
        import aio_pika

        await self.publish_channel.default_exchange.publish(
            aio_pika.Message(json.dumps(payload).encode(), delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
            routing_key="ppe.results",
        )

    async def _on_job(self, channel, message):
        job = json.loads(message.body)
        self.seen.append(job)
        assert Path(job["image_path"]).read_bytes() == JPEG
        await self._publish({"job_id": job["job_id"], "event": "STARTED", "result": None, "error": None})
        if self.behaviour == "crash":
            asyncio.get_running_loop().create_task(self._crash_and_restart(channel))
            return
        result = {"h": 1, "v": 0, "detections": [], "image_w": 10, "image_h": 10,
                  "model_version": "ppe-yolo-test", "conf_threshold": 0.5, "infer_ms": 5}
        await self._publish({"job_id": job["job_id"], "event": "DONE", "result": result, "error": None})
        await message.ack()

    async def _crash_and_restart(self, channel):
        await channel.close()  # unacked message returns to ppe.jobs, delivery count + 1
        await asyncio.sleep(0.2)
        await self._consume()

    def stop(self):
        self.client.portal.call(self.connection.close)


def test_full_round_trip_with_real_rabbitmq(real):
    client, _ = real
    # no worker yet: health 503, workers 0
    health = client.get("/v1/health", headers=AUTH)
    assert health.status_code == 503 and health.json()["rabbitmq"] == "ok" and health.json()["workers"] == 0

    worker = FakeWorker(client, "ok")
    worker.start()
    health = client.get("/v1/health", headers=AUTH)
    assert health.status_code == 200 and health.json()["workers"] == 1

    job_id = str(uuid.uuid4())
    response = _post(client, job_id)
    assert response.status_code == 202, response.text
    _wait(lambda: _status(client, job_id) == "DONE")
    body = client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()
    assert body["result"]["h"] == 1 and body["result"]["model_version"] == "ppe-yolo-test"
    assert not Path(worker.seen[0]["image_path"]).exists()
    assert _post(client, job_id).status_code == 200
    worker.stop()


def test_poison_job_goes_to_dead_letter_and_fails(real):
    client, settings = real
    worker = FakeWorker(client, "crash")
    worker.start()
    job_id = str(uuid.uuid4())
    assert _post(client, job_id).status_code == 202
    _wait(lambda: _status(client, job_id) == "FAILED")
    body = client.get(f"/v1/jobs/{job_id}", headers=AUTH).json()
    assert body["error"]["code"] == "MAX_RETRIES"
    # x-delivery-limit = MAX_DELIVERY (2) → RabbitMQ delivered it limit + 1 times, then dead-lettered
    assert len(worker.seen) == settings.max_delivery + 1
    worker.stop()


def test_reject_publish_from_rabbitmq_is_429(real):
    """Second layer: the queue already holds x-max-length messages the gateway does not know about."""
    import aio_pika

    client, settings = real

    async def fill():
        """Publish until RabbitMQ itself refuses (quorum queues accept x-max-length + 1)."""
        from aiormq.exceptions import DeliveryError

        connection = await aio_pika.connect(URL)
        async with connection:
            channel = await connection.channel(publisher_confirms=True)
            for _ in range(settings.max_queue_depth + 5):
                try:
                    await channel.default_exchange.publish(
                        aio_pika.Message(b'{"job_id":"filler"}', delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
                        routing_key="ppe.jobs",
                    )
                except DeliveryError:
                    return
        raise AssertionError("RabbitMQ never applied reject-publish")

    asyncio.run(fill())
    job_id = str(uuid.uuid4())
    response = _post(client, job_id)
    assert response.status_code == 429, response.text
    assert response.json()["error"] == "QUEUE_FULL" and "Retry-After" in response.headers
    assert client.get(f"/v1/jobs/{job_id}", headers=AUTH).status_code == 404


def test_gateway_depth_check_with_real_rabbitmq(real):
    client, settings = real
    accepted = [_post(client, str(uuid.uuid4())) for _ in range(settings.max_queue_depth)]
    assert [r.status_code for r in accepted] == [202] * settings.max_queue_depth
    assert accepted[-1].json()["queue_depth"] == settings.max_queue_depth
    refused = _post(client, str(uuid.uuid4()))
    assert refused.status_code == 429
    assert refused.json()["queue_depth"] == settings.max_queue_depth
