"""Run the SiteSafe PPE worker with ``python -m ai.worker.worker``."""

import json
import logging
import os
import signal
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from threading import Event
from time import perf_counter
from typing import Protocol

from PIL import Image


LOGGER = logging.getLogger(__name__)
PPE_CLASSES = ("NO_HARDHAT", "NO_VEST")
CLASSES_PATH = Path(__file__).with_name("classes.json")
BROKER_POLL_S = 0.05


@dataclass(frozen=True)
class Detection:
    cls: str
    confidence: float
    box: tuple[float, float, float, float]


class Detector(Protocol):
    def detect(self, image: Image.Image, threshold: float) -> Iterable[Detection]:
        """Return canonical class names and boxes in original-image pixels."""
        ...


class YoloDetector:
    def __init__(self, model_path: Path, classes_path: Path = CLASSES_PATH):
        model_path = model_path.resolve(strict=True)
        if not model_path.is_file():
            raise ValueError("MODEL_PATH must point to a local model file")

        # Use the same class-name aliases as the validation tool.
        try:
            with classes_path.open(encoding="utf-8") as file:
                class_names = json.load(file)
        except FileNotFoundError:
            class_names = {name: name for name in PPE_CLASSES}
        if not isinstance(class_names, dict):
            raise ValueError("classes.json must be an object keyed by NO_HARDHAT and NO_VEST")
        canonical_names = {}
        for category in PPE_CLASSES:
            aliases = class_names.get(category)
            if isinstance(aliases, str):
                aliases = [aliases]
            if not isinstance(aliases, list) or not aliases or any(
                not isinstance(alias, str) or not alias.strip() for alias in aliases
            ):
                raise ValueError(f"classes.json needs a model class name or list of names for {category}")
            for alias in aliases:
                name = alias.strip().casefold()
                if canonical_names.setdefault(name, category) != category:
                    raise ValueError(f"classes.json assigns {alias!r} to both PPE classes")

        from ultralytics import YOLO

        self.model = YOLO(str(model_path), task="detect")
        # Initialize the predictor and its GPU before accepting jobs, including for exported weights.
        with Image.new("RGB", (32, 32)) as sample:
            self.model.predict(source=sample, device=0, verbose=False)
        self.classes_by_id = {
            class_id: canonical_names[name]
            for class_id, model_name in self.model.names.items()
            if (name := model_name.strip().casefold()) in canonical_names
        }
        if set(self.classes_by_id.values()) != set(PPE_CLASSES):
            raise ValueError("The model is missing PPE classes configured in classes.json")

    def detect(self, image: Image.Image, threshold: float) -> Iterable[Detection]:
        # YOLO uses a strict comparison. Leave room for scores equal to the cutoff.
        predictions = self.model.predict(
            source=image,
            device=0,
            conf=max(0.0, threshold - 1e-7),
            classes=list(self.classes_by_id),
            verbose=False,
        )
        boxes = predictions[0].boxes.cpu()
        for class_id, confidence, box in zip(
            boxes.cls.tolist(), boxes.conf.tolist(), boxes.xyxy.tolist()
        ):
            yield Detection(self.classes_by_id[int(class_id)], confidence, tuple(box))


class ImageUnreadable(Exception):
    pass


def inspect_image(detector: Detector, image_path: str, threshold: float, model_version: str) -> dict:
    try:
        with Image.open(image_path) as source:
            image = source.convert("RGB")
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as exc:
        raise ImageUnreadable from exc

    with image:
        width, height = image.size
        started = perf_counter()
        detections = [
            {
                "cls": detection.cls,
                "confidence": detection.confidence,
                "box": [round(coordinate) for coordinate in detection.box],
            }
            for detection in detector.detect(image, threshold)
            if detection.cls in PPE_CLASSES and detection.confidence >= threshold
        ]
        infer_ms = round((perf_counter() - started) * 1000)

    return {
        "h": sum(detection["cls"] == "NO_HARDHAT" for detection in detections),
        "v": sum(detection["cls"] == "NO_VEST" for detection in detections),
        "detections": detections,
        "image_w": width,
        "image_h": height,
        "model_version": model_version,
        "conf_threshold": threshold,
        "infer_ms": infer_ms,
    }


def _publish_event(channel, queue, properties, job_id, event, *, result=None, error=None):
    confirmed = channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps({"job_id": job_id, "event": event, "result": result, "error": error}),
        properties=properties,
        mandatory=True,
    )
    # With confirm_delivery enabled, Pika normally raises on a rejected publish.
    if confirmed is False:
        raise RuntimeError(f"RabbitMQ rejected {event} for job {job_id}")


def run_worker(detector: Detector, threshold: float, model_version: str, stop: Event, amqp_url: str):
    import pika

    from ai.common.queues import JOBS_QUEUE, RESULTS_QUEUE, declare_queues

    parameters = pika.URLParameters(amqp_url)
    parameters.blocked_connection_timeout = 30
    properties = pika.BasicProperties(content_type="application/json", delivery_mode=2)

    # Close the broker connection before waiting for any in-flight inference on shutdown.
    with ThreadPoolExecutor(max_workers=1) as executor, pika.BlockingConnection(parameters) as connection:
        channel = connection.channel()
        declare_queues(channel)
        channel.basic_qos(prefetch_count=1)
        channel.confirm_delivery()

        for delivery, _, body in channel.consume(
            JOBS_QUEUE, auto_ack=False, inactivity_timeout=BROKER_POLL_S
        ):
            if stop.is_set():
                break
            if delivery is None:
                continue

            try:
                job = json.loads(body)
                job_id, image_path = job["job_id"], job["image_path"]
                if not isinstance(job_id, str) or not job_id or not isinstance(image_path, str):
                    raise ValueError("Invalid job_id or image_path")
            except (ValueError, KeyError, TypeError):
                LOGGER.warning("Dead-lettering malformed PPE job")
                channel.basic_reject(delivery_tag=delivery.delivery_tag, requeue=False)
                continue

            _publish_event(channel, RESULTS_QUEUE, properties, job_id, "STARTED")
            if stop.is_set():
                break
            task = executor.submit(inspect_image, detector, image_path, threshold, model_version)
            while not task.done() and not stop.is_set():
                # Service RabbitMQ heartbeats while image decoding and inference run.
                connection.process_data_events(time_limit=BROKER_POLL_S)
            if stop.is_set():
                break

            result = error = None
            try:
                result = task.result()
            except ImageUnreadable:
                error = {"code": "IMAGE_UNREADABLE", "message": "Unable to open or decode image"}
            except Exception:
                LOGGER.exception("Inference failed for job %s", job_id)
                if not stop.is_set():
                    # Count this failed delivery toward the quorum queue's retry limit.
                    channel.basic_reject(delivery_tag=delivery.delivery_tag, requeue=True)
                continue

            if stop.is_set():
                break
            _publish_event(
                channel,
                RESULTS_QUEUE,
                properties,
                job_id,
                "DONE" if error is None else "FAILED",
                result=result,
                error=error,
            )
            if not stop.is_set():
                channel.basic_ack(delivery_tag=delivery.delivery_tag)


def main():
    logging.basicConfig(level=logging.INFO)
    stop = Event()

    def request_stop(signum, frame):
        stop.set()

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    model_path = Path(os.environ["MODEL_PATH"])
    threshold = float(os.environ["CONF_THRESHOLD"])
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("CONF_THRESHOLD must be between 0 and 1")
    model_version = os.environ.get("MODEL_VERSION", model_path.stem)
    detector = YoloDetector(model_path)
    if not stop.is_set():
        run_worker(detector, threshold, model_version, stop, os.environ["RABBITMQ_URL"])


if __name__ == "__main__":
    main()
