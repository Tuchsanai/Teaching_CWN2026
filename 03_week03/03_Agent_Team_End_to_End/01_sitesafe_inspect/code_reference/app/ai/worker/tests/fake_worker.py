"""Run the real worker loop (ai.worker.worker.run_worker) with a fake detector — no GPU, no model.

For checking the AI stack (gateway + RabbitMQ + queue messages + shared /data volume) on a
machine without a GPU.  Needs pika and pillow.  Every readable image gets FAKE_H NO_HARDHAT
boxes and FAKE_V NO_VEST boxes; unreadable images are reported as IMAGE_UNREADABLE by the
real worker code.

    RABBITMQ_URL=amqp://… FAKE_H=1 FAKE_V=0 python -m ai.worker.tests.fake_worker
"""

from __future__ import annotations

import logging
import os
import signal
import sys
from pathlib import Path
from threading import Event

APP_ROOT = Path(__file__).resolve().parents[3]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from ai.worker.worker import Detection, run_worker  # noqa: E402


class FixedDetector:
    def __init__(self, h: int, v: int):
        self.h, self.v = h, v

    def detect(self, image, threshold):
        w, ht = image.size
        step = max(1, w // max(1, self.h + self.v))
        for i in range(self.h + self.v):
            cls = "NO_HARDHAT" if i < self.h else "NO_VEST"
            yield Detection(cls, 0.9, (i * step, 0, min(w, (i + 1) * step), ht))


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    stop = Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())
    detector = FixedDetector(int(os.environ.get("FAKE_H", "0")), int(os.environ.get("FAKE_V", "0")))
    threshold = float(os.environ.get("CONF_THRESHOLD", "0.5"))
    run_worker(detector, threshold, os.environ.get("MODEL_VERSION", "ppe-fake"), stop, os.environ["RABBITMQ_URL"])


if __name__ == "__main__":
    main()
