"""Unit tests of ai/worker/worker.py with a fake detector and a fake pika (no GPU, no RabbitMQ).

    python -m pytest ai/worker/tests -q
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from threading import Event

import pytest
from PIL import Image

APP_ROOT = Path(__file__).resolve().parents[3]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from ai.common import queues  # noqa: E402
from ai.worker import worker as wk  # noqa: E402


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


class FakeDetector:
    """Returns fixed detections; raises for images of a given size (a 'poison' image)."""

    def __init__(self, detections=(), poison_size=None):
        self.detections = list(detections)
        self.poison_size = poison_size
        self.calls = []

    def detect(self, image, threshold):
        self.calls.append((image.size, threshold))
        if self.poison_size is not None and image.size == self.poison_size:
            raise RuntimeError("CUDA error: device-side assert")
        return list(self.detections)


def write_jpeg(path: Path, size=(40, 30)) -> Path:
    Image.new("RGB", size, (200, 120, 40)).save(path, "JPEG")
    return path


class FakeChannel:
    def __init__(self, messages, stop: Event, publish_ok=True):
        self.messages = messages
        self.stop = stop
        self.publish_ok = publish_ok
        self.log = []  # ordered: ("declare", name, args) / ("publish", event) / ("ack", tag) / ("reject", tag, requeue)
        self.published = []
        self.qos = None
        self.confirms = False

    def queue_declare(self, queue, durable, arguments):
        assert durable is True
        self.log.append(("declare", queue, arguments))

    def basic_qos(self, prefetch_count):
        self.qos = prefetch_count

    def confirm_delivery(self):
        self.confirms = True

    def consume(self, queue, auto_ack, inactivity_timeout):
        assert queue == queues.JOBS_QUEUE and auto_ack is False
        for tag, body in enumerate(self.messages, 1):
            yield types.SimpleNamespace(delivery_tag=tag), None, body
        yield None, None, None  # inactivity tick
        self.stop.set()
        yield None, None, None

    def basic_publish(self, exchange, routing_key, body, properties, mandatory):
        assert exchange == "" and routing_key == queues.RESULTS_QUEUE and mandatory is True
        assert properties.delivery_mode == 2
        message = json.loads(body)
        self.published.append(message)
        self.log.append(("publish", message["event"]))
        return self.publish_ok

    def basic_ack(self, delivery_tag):
        self.log.append(("ack", delivery_tag))

    def basic_reject(self, delivery_tag, requeue):
        self.log.append(("reject", delivery_tag, requeue))


@pytest.fixture
def fake_pika(monkeypatch):
    """Install a fake ``pika`` module; returns a holder whose ``.channel`` is set per test."""
    holder = types.SimpleNamespace(channel=None, url=None)

    class URLParameters:
        def __init__(self, url):
            holder.url = url

    class BasicProperties:
        def __init__(self, content_type, delivery_mode):
            self.content_type, self.delivery_mode = content_type, delivery_mode

    class BlockingConnection:
        def __init__(self, parameters):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def channel(self):
            return holder.channel

        def process_data_events(self, time_limit):
            pass

    module = types.ModuleType("pika")
    module.URLParameters = URLParameters
    module.BasicProperties = BasicProperties
    module.BlockingConnection = BlockingConnection
    monkeypatch.setitem(sys.modules, "pika", module)
    return holder


def run(fake_pika, detector, messages, publish_ok=True, threshold=0.5):
    stop = Event()
    channel = FakeChannel(messages, stop, publish_ok)
    fake_pika.channel = channel
    wk.run_worker(detector, threshold, "ppe-yolo-test", stop, "amqp://u:p@rabbitmq:5672/")
    return channel


def job(job_id, image_path):
    return json.dumps({"job_id": job_id, "image_path": str(image_path), "queued_at": "2026-11-18T03:00:01Z"}).encode()


# ---------------------------------------------------------------------------
# inspect_image
# ---------------------------------------------------------------------------


def test_inspect_counts_h_and_v_at_or_above_threshold(tmp_path):
    image = write_jpeg(tmp_path / "a.jpg", (400, 300))
    detector = FakeDetector([
        wk.Detection("NO_HARDHAT", 0.87, (412.4, 130.6, 596.5, 380.0)),
        wk.Detection("NO_VEST", 0.5, (1, 2, 3, 4)),        # equal to the threshold → counted
        wk.Detection("NO_VEST", 0.4999, (1, 2, 3, 4)),     # below → ignored
        wk.Detection("PERSON", 0.99, (1, 2, 3, 4)),        # not a PPE class → ignored
    ])
    result = wk.inspect_image(detector, str(image), 0.5, "ppe-yolo-v1")
    assert (result["h"], result["v"]) == (1, 1)
    assert [d["cls"] for d in result["detections"]] == ["NO_HARDHAT", "NO_VEST"]
    assert result["detections"][0]["box"] == [412, 131, 596, 380]
    assert (result["image_w"], result["image_h"]) == (400, 300)
    assert result["model_version"] == "ppe-yolo-v1" and result["conf_threshold"] == 0.5
    assert isinstance(result["infer_ms"], int)


def test_inspect_without_detection_gives_zero(tmp_path):
    result = wk.inspect_image(FakeDetector(), str(write_jpeg(tmp_path / "a.jpg")), 0.5, "m")
    assert (result["h"], result["v"], result["detections"]) == (0, 0, [])


@pytest.mark.parametrize("content", [b"not an image at all", None])
def test_inspect_unreadable_image(tmp_path, content):
    path = tmp_path / "corrupt.jpg"
    if content is None:  # a JPEG cut in half (TEST-DATA F-10)
        good = write_jpeg(tmp_path / "good.jpg", (640, 480)).read_bytes()
        content = good[: len(good) // 2]
    path.write_bytes(content)
    with pytest.raises(wk.ImageUnreadable):
        wk.inspect_image(FakeDetector(), str(path), 0.5, "m")


def test_inspect_missing_file_is_unreadable(tmp_path):
    with pytest.raises(wk.ImageUnreadable):
        wk.inspect_image(FakeDetector(), str(tmp_path / "gone.jpg"), 0.5, "m")


# ---------------------------------------------------------------------------
# run_worker (queue protocol of DESIGN 6.1 / 6.2)
# ---------------------------------------------------------------------------


def test_worker_declares_shared_queues_prefetch_1_and_confirms(fake_pika, tmp_path):
    channel = run(fake_pika, FakeDetector(), [])
    declared = [entry for entry in channel.log if entry[0] == "declare"]
    expected = queues.queue_arguments()
    assert [name for _, name, _ in declared] == [queues.DEAD_QUEUE, queues.RESULTS_QUEUE, queues.JOBS_QUEUE]
    assert all(args == expected[name] for _, name, args in declared)
    assert channel.qos == 1 and channel.confirms is True
    assert fake_pika.url == "amqp://u:p@rabbitmq:5672/"


def test_worker_publishes_started_then_done_then_acks(fake_pika, tmp_path):
    image = write_jpeg(tmp_path / "a.jpg", (64, 48))
    detector = FakeDetector([
        wk.Detection("NO_HARDHAT", 0.9, (1, 2, 30, 40)),
        wk.Detection("NO_VEST", 0.8, (5, 6, 20, 30)),
        wk.Detection("NO_VEST", 0.7, (7, 8, 21, 31)),
    ])
    channel = run(fake_pika, detector, [job("5b0e0000-0000-4000-8000-000000000001", image)])
    assert [e for e in channel.log if e[0] != "declare"] == [("publish", "STARTED"), ("publish", "DONE"), ("ack", 1)]
    started, done = channel.published
    assert started == {"job_id": "5b0e0000-0000-4000-8000-000000000001", "event": "STARTED", "result": None, "error": None}
    result = done["result"]
    assert done["error"] is None
    assert (result["h"], result["v"], len(result["detections"])) == (1, 2, 3)
    assert set(result) == {"h", "v", "detections", "image_w", "image_h", "model_version", "conf_threshold", "infer_ms"}
    assert set(result["detections"][0]) == {"cls", "confidence", "box"}
    assert (result["image_w"], result["image_h"], result["model_version"]) == (64, 48, "ppe-yolo-test")


def test_worker_reports_unreadable_image_as_failed_and_acks(fake_pika, tmp_path):
    bad = tmp_path / "corrupt.jpg"
    bad.write_bytes(b"\xff\xd8\xff" + b"x" * 50)
    channel = run(fake_pika, FakeDetector(), [job("j-1", bad)])
    assert [e for e in channel.log if e[0] != "declare"] == [("publish", "STARTED"), ("publish", "FAILED"), ("ack", 1)]
    failed = channel.published[1]
    assert failed["result"] is None and failed["error"]["code"] == "IMAGE_UNREADABLE"


def test_worker_rejects_with_requeue_when_inference_crashes(fake_pika, tmp_path):
    """basic_reject (not nack) so the quorum queue counts the delivery toward x-delivery-limit."""
    poison = write_jpeg(tmp_path / "p.jpg", (13, 7))
    channel = run(fake_pika, FakeDetector(poison_size=(13, 7)), [job("j-2", poison)])
    assert [e for e in channel.log if e[0] != "declare"] == [("publish", "STARTED"), ("reject", 1, True)]


def test_worker_dead_letters_malformed_message(fake_pika):
    channel = run(fake_pika, FakeDetector(), [b"{not json", json.dumps({"job_id": "x"}).encode()])
    assert [e for e in channel.log if e[0] != "declare"] == [("reject", 1, False), ("reject", 2, False)]
    assert channel.published == []


def test_worker_does_not_ack_when_result_publish_is_rejected(fake_pika, tmp_path):
    image = write_jpeg(tmp_path / "a.jpg")
    with pytest.raises(RuntimeError):
        run(fake_pika, FakeDetector(), [job("j-3", image)], publish_ok=False)
    # The job stays unacknowledged, so RabbitMQ delivers it again after the restart.
    assert not any(entry[0] == "ack" for entry in fake_pika.channel.log)


def test_worker_keeps_order_for_several_jobs(fake_pika, tmp_path):
    a = write_jpeg(tmp_path / "a.jpg")
    b = tmp_path / "b.jpg"
    b.write_bytes(b"garbage")
    channel = run(fake_pika, FakeDetector(), [job("a", a), job("b", b)])
    events = [e for e in channel.log if e[0] != "declare"]
    assert events == [
        ("publish", "STARTED"), ("publish", "DONE"), ("ack", 1),
        ("publish", "STARTED"), ("publish", "FAILED"), ("ack", 2),
    ]


# ---------------------------------------------------------------------------
# YoloDetector with a fake ultralytics (class-name mapping)
# ---------------------------------------------------------------------------


class _Boxes:
    def __init__(self, cls, conf, xyxy):
        self.cls, self.conf, self.xyxy = _T(cls), _T(conf), _T(xyxy)

    def cpu(self):
        return self


class _T(list):
    def tolist(self):
        return list(self)


@pytest.fixture
def fake_ultralytics(monkeypatch):
    calls = []

    class YOLO:
        names = {0: "helmet", 1: "No-Helmet", 2: "no_vest", 3: "person"}

        def __init__(self, path, task):
            assert task == "detect"

        def predict(self, source, device, verbose, conf=None, classes=None):
            calls.append({"device": device, "conf": conf, "classes": classes})
            return [types.SimpleNamespace(boxes=_Boxes([1, 2], [0.91, 0.55], [[1.2, 2.6, 30.4, 40.5], [5, 6, 7, 8]]))]

    module = types.ModuleType("ultralytics")
    module.YOLO = YOLO
    monkeypatch.setitem(sys.modules, "ultralytics", module)
    return calls


def test_yolo_detector_maps_model_names_through_classes_json(tmp_path, fake_ultralytics):
    model = tmp_path / "best.pt"
    model.write_bytes(b"weights")
    classes = tmp_path / "classes.json"
    classes.write_text(json.dumps({"NO_HARDHAT": ["no-helmet", "no_hardhat"], "NO_VEST": "NO_VEST"}))
    detector = wk.YoloDetector(model, classes)
    with Image.new("RGB", (64, 48)) as image:
        found = list(detector.detect(image, 0.5))
    assert [d.cls for d in found] == ["NO_HARDHAT", "NO_VEST"]
    assert found[0].box == (1.2, 2.6, 30.4, 40.5)
    warmup, predict = fake_ultralytics
    assert warmup["device"] == 0 and predict["device"] == 0
    assert sorted(predict["classes"]) == [1, 2]
    assert 0.4999 < predict["conf"] < 0.5  # leaves room for scores equal to the threshold


def test_yolo_detector_refuses_model_without_ppe_classes(tmp_path, fake_ultralytics):
    model = tmp_path / "best.pt"
    model.write_bytes(b"weights")
    classes = tmp_path / "classes.json"
    classes.write_text(json.dumps({"NO_HARDHAT": "no-helmet", "NO_VEST": "missing-class"}))
    with pytest.raises(ValueError):
        wk.YoloDetector(model, classes)


def test_yolo_detector_needs_a_local_model_file(tmp_path, fake_ultralytics):
    with pytest.raises(FileNotFoundError):
        wk.YoloDetector(tmp_path / "missing.pt")


def test_main_rejects_threshold_outside_0_to_1(monkeypatch, tmp_path):
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "best.pt"))
    monkeypatch.setenv("CONF_THRESHOLD", "1.5")
    monkeypatch.setenv("RABBITMQ_URL", "amqp://localhost/")
    monkeypatch.setattr(wk.signal, "signal", lambda *args: None)
    with pytest.raises(ValueError):
        wk.main()
