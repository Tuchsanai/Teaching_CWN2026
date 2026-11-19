"""Queue names and arguments shared by the gateway and the GPU worker (DESIGN 6.1).

RabbitMQ refuses ``queue_declare`` with arguments that differ from the existing
queue (PRECONDITION_FAILED), so the gateway and the worker must declare the
three queues with exactly the same arguments.  Both read them from here, and
both containers get the same ``MAX_QUEUE_DEPTH`` / ``MAX_DELIVERY`` from
``ai/docker-compose.yml``.

* ``ppe.jobs``      gateway → worker · ``{"job_id","image_path","queued_at"}``
* ``ppe.results``   worker → gateway · ``{"job_id","event":"STARTED|DONE|FAILED","result","error"}``
* ``ppe.jobs.dead`` RabbitMQ → gateway · a job delivered ``MAX_DELIVERY`` times

Changing ``MAX_QUEUE_DEPTH`` or ``MAX_DELIVERY`` later needs ``ppe.jobs`` to be
deleted while it is empty: RabbitMQ keeps the arguments of an existing queue.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

JOBS_QUEUE = "ppe.jobs"
RESULTS_QUEUE = "ppe.results"
DEAD_QUEUE = "ppe.jobs.dead"

DEFAULT_MAX_QUEUE_DEPTH = 200
DEFAULT_MAX_DELIVERY = 3


def _env_int(env: Mapping[str, str], name: str, default: int) -> int:
    raw = env.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if value < 1:
        raise ValueError(f"{name} must be ≥ 1")
    return value


def queue_arguments(env: Mapping[str, str] | None = None) -> dict[str, dict[str, Any]]:
    """Queue name → ``x-arguments`` for ``queue_declare`` (all three are quorum + durable)."""
    env = os.environ if env is None else env
    max_queue_depth = _env_int(env, "MAX_QUEUE_DEPTH", DEFAULT_MAX_QUEUE_DEPTH)
    max_delivery = _env_int(env, "MAX_DELIVERY", DEFAULT_MAX_DELIVERY)
    quorum = {"x-queue-type": "quorum"}
    return {
        JOBS_QUEUE: {
            **quorum,
            "x-delivery-limit": max_delivery,
            "x-dead-letter-exchange": "",
            "x-dead-letter-routing-key": DEAD_QUEUE,
            "x-max-length": max_queue_depth,
            "x-overflow": "reject-publish",
        },
        RESULTS_QUEUE: dict(quorum),
        DEAD_QUEUE: dict(quorum),
    }


def declare_queues(channel: Any, env: Mapping[str, str] | None = None) -> None:
    """Declare the three queues on a pika channel (dead-letter target first)."""
    arguments = queue_arguments(env)
    for name in (DEAD_QUEUE, RESULTS_QUEUE, JOBS_QUEUE):
        channel.queue_declare(queue=name, durable=True, arguments=arguments[name])
