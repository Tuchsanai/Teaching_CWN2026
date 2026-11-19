"""ai/common/queues.py: the gateway and the worker declare identical queues (DESIGN 6.1)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parents[3]
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from ai.common import queues  # noqa: E402
from ai.gateway import main as gw  # noqa: E402


def test_queue_names_follow_design():
    assert (queues.JOBS_QUEUE, queues.RESULTS_QUEUE, queues.DEAD_QUEUE) == ("ppe.jobs", "ppe.results", "ppe.jobs.dead")


def test_default_arguments():
    args = queues.queue_arguments({})
    assert args["ppe.jobs"] == {
        "x-queue-type": "quorum",
        "x-delivery-limit": 3,
        "x-dead-letter-exchange": "",
        "x-dead-letter-routing-key": "ppe.jobs.dead",
        "x-max-length": 200,
        "x-overflow": "reject-publish",
    }
    assert args["ppe.results"] == {"x-queue-type": "quorum"}
    assert args["ppe.jobs.dead"] == {"x-queue-type": "quorum"}


@pytest.mark.parametrize("depth, delivery", [(200, 3), (5, 3), (17, 4)])
def test_gateway_loads_the_same_arguments(monkeypatch, depth, delivery):
    monkeypatch.setenv("MAX_QUEUE_DEPTH", str(depth))
    monkeypatch.setenv("MAX_DELIVERY", str(delivery))
    settings = gw.Settings.from_env()
    spec = gw.load_queue_spec(settings)
    assert spec.source.startswith("ai.common.queues")
    assert (spec.jobs, spec.results, spec.dead) == (queues.JOBS_QUEUE, queues.RESULTS_QUEUE, queues.DEAD_QUEUE)
    assert spec.arguments == queues.queue_arguments()
    # …and they equal the gateway's own DESIGN 6.1 fallback for the same settings.
    assert spec.arguments == gw.fallback_queue_arguments(
        spec.jobs, spec.results, spec.dead,
        max_queue_depth=settings.max_queue_depth, max_delivery=settings.max_delivery,
    )


def test_declare_queues_declares_dead_letter_target_first():
    declared = []

    class Channel:
        def queue_declare(self, queue, durable, arguments):
            declared.append((queue, durable, arguments))

    queues.declare_queues(Channel(), {"MAX_QUEUE_DEPTH": "5"})
    assert [name for name, _, _ in declared] == ["ppe.jobs.dead", "ppe.results", "ppe.jobs"]
    assert all(durable for _, durable, _ in declared)
    assert declared[2][2]["x-max-length"] == 5


@pytest.mark.parametrize("raw", ["0", "-1", "abc"])
def test_invalid_numbers_are_refused(raw):
    with pytest.raises(ValueError):
        queues.queue_arguments({"MAX_QUEUE_DEPTH": raw})
