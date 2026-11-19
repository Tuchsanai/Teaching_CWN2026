"""ReceiptDesk AMQP declarations and queue rules shared by gateway and workers.

Run the broker simulation with python -B -m ai.queue.topology.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from aio_pika.abc import AbstractChannel, AbstractIncomingMessage, AbstractQueue


Priority = Literal["urgent", "normal"]
QueueName = Literal["urgent", "normal", "none"]
DeliveryOutcome = Literal["done", "skip", "queued", "wait", "dead"]

URGENT_QUEUE = "receipts.urgent"
NORMAL_QUEUE = "receipts.normal"
DLQ = "receipts.dlq"
DLX = "receipts.dlx"
QUEUE_NAMES = {"urgent": URGENT_QUEUE, "normal": NORMAL_QUEUE}
QUEUE_LIMITS = {"urgent": 50, "normal": 400}
URGENT_STREAK_MAX = 4
MAX_ATTEMPTS = 3
MIN_RATE_PER_WORKER = 4  # receipts per minute


class QueueFull(TypedDict):
    error: Literal["queue_full"]
    queue: Priority
    pending: int
    limit: int
    workers_alive: int
    retry_after_minutes: int
    retry_after_seconds: int


class QueueDecision(TypedDict):
    queue: QueueName
    reason: str


async def declare_topology(channel: AbstractChannel) -> dict[str, AbstractQueue]:
    """Declare RabbitMQ resources and return handles keyed by urgent, normal, dlq."""
    dlx = await channel.declare_exchange(DLX, type="direct", durable=True)
    dlq = await channel.declare_queue(DLQ, durable=True)
    await dlq.bind(dlx, routing_key=DLQ)

    queues = {"dlq": dlq}
    # G5 leaves old normal messages in RabbitMQ. Gateway counts logical receipts.
    for priority, name in QUEUE_NAMES.items():
        queues[priority] = await channel.declare_queue(
            name,
            durable=True,
            arguments={
                "x-dead-letter-exchange": DLX,
                "x-dead-letter-routing-key": DLQ,
            },
        )
    return queues


async def publish_receipt(
    channel: AbstractChannel,
    *,
    receipt_ref: str,
    job_ref: str,
    priority: Priority,
) -> None:
    """Publish persistent work through the default exchange and require a confirm.

    Open the gateway channel with publisher_confirms=True and on_return_raises=True.
    """
    from aio_pika import DeliveryMode, Message
    from aiormq import spec

    message = Message(
        json.dumps(
            {"receipt_ref": receipt_ref, "job_ref": job_ref, "priority": priority},
        ).encode("utf-8"),
        content_type="application/json",
        delivery_mode=DeliveryMode.PERSISTENT,
    )
    confirm = await channel.default_exchange.publish(
        message, routing_key=QUEUE_NAMES[priority], mandatory=True
    )
    if not isinstance(confirm, spec.Basic.Ack):
        raise RuntimeError("RabbitMQ did not confirm the receipt publish")


def check_capacity(
    priority: Priority,
    pending: int,
    *,
    incoming: int = 1,
    workers_alive: int = 0,
) -> QueueFull | None:
    """Return the G2/G5 HTTP 429 body if admission would exceed the queue limit.

    Count logical pending receipts and admit them under the same gateway lock or
    transaction. For G5, incoming is the number of receipts still to promote.
    The caller sets Retry-After to retry_after_seconds when returning HTTP 429.
    """
    if min(pending, incoming, workers_alive) < 0:
        raise ValueError("Receipt and worker counts must be non-negative")
    limit = QUEUE_LIMITS[priority]
    excess = pending + incoming - limit
    if incoming == 0 or excess <= 0:
        return None

    rate = MIN_RATE_PER_WORKER * max(1, workers_alive)
    minutes = (excess + rate - 1) // rate
    return {
        "error": "queue_full",
        "queue": priority,
        "pending": pending,
        "limit": limit,
        "workers_alive": workers_alive,
        "retry_after_minutes": minutes,
        "retry_after_seconds": minutes * 60,
    }


def can_claim_urgent(
    *, normal_pending: int, urgent_streak: int, deadline_guard: bool = False
) -> bool:
    """Recheck at I1 if normal work arrived since I4 granted an urgent slot."""
    return normal_pending == 0 or (
        not deadline_guard and urgent_streak < URGENT_STREAK_MAX
    )


def choose_next_queue(
    *,
    urgent_pending: int,
    normal_pending: int,
    urgent_streak: int,
    urgent_reserved: int = 0,
    deadline_guard: bool = False,
) -> QueueDecision:
    """Choose the I4 response using gateway state per the B06 urgent policy.

    Pass counts of queued receipts and the number of other workers holding
    urgent reservations. Clear this worker's old reservation and record any
    new one atomically with selection. Use the same lock for claim, where the
    reservation is released and only go changes the streak.
    The worker uses basic.get on the selected queue with manual acknowledgement.
    """
    if normal_pending > 0 and deadline_guard:
        return {"queue": "normal", "reason": "deadline_guard"}

    urgent_available = urgent_pending > urgent_reserved
    if urgent_available and can_claim_urgent(
        normal_pending=normal_pending,
        urgent_streak=urgent_streak + urgent_reserved,
    ):
        reason = "urgent_first" if normal_pending else "no_normal_waiting"
        return {"queue": "urgent", "reason": reason}
    if normal_pending > 0:
        reason = "ratio_4_1" if urgent_available else "fifo"
        return {"queue": "normal", "reason": reason}
    return {"queue": "none", "reason": "empty"}


def streak_after_claim(urgent_streak: int, priority: Priority) -> int:
    """Compute the next persisted streak for an I1 go, including a retry."""
    return urgent_streak + 1 if priority == "urgent" else 0


def status_after_failure(attempts: int) -> Literal["queued", "dead"]:
    """Apply BR-07 to the attempt count persisted by the gateway at claim."""
    if attempts < 1:
        raise ValueError("A read failure requires at least one attempt")
    return "dead" if attempts >= MAX_ATTEMPTS else "queued"


async def settle_delivery(
    message: AbstractIncomingMessage, outcome: DeliveryOutcome
) -> None:
    """Settle an AMQP delivery using the gateway's recorded outcome."""
    if outcome in ("done", "skip"):
        await message.ack()
    elif outcome in ("queued", "wait"):
        await message.nack(requeue=True)
    elif outcome == "dead":
        await message.reject(requeue=False)
    else:
        raise ValueError(f"Unknown delivery outcome: {outcome!r}")


if __name__ == "__main__":
    import unittest
    from collections import deque
    from types import SimpleNamespace
    from unittest.mock import AsyncMock

    class QueueTests(unittest.IsolatedAsyncioTestCase):
        async def test_topology(self):
            channel = SimpleNamespace(
                declare_exchange=AsyncMock(),
                declare_queue=AsyncMock(
                    side_effect=lambda *_args, **_kwargs: SimpleNamespace(
                        bind=AsyncMock()
                    )
                ),
            )
            queues = await declare_topology(channel)
            channel.declare_exchange.assert_awaited_once_with(
                "receipts.dlx", type="direct", durable=True
            )
            channel.declare_queue.assert_any_await("receipts.dlq", durable=True)
            queues["dlq"].bind.assert_awaited_once_with(
                channel.declare_exchange.return_value, routing_key="receipts.dlq"
            )
            for priority in ("urgent", "normal"):
                channel.declare_queue.assert_any_await(
                    f"receipts.{priority}",
                    durable=True,
                    arguments={
                        "x-dead-letter-exchange": "receipts.dlx",
                        "x-dead-letter-routing-key": "receipts.dlq",
                    },
                )
            self.assertEqual(channel.declare_queue.await_count, 3)

        def test_capacity(self):
            for priority, limit in (("normal", 400), ("urgent", 50)):
                with self.subTest(priority=priority):
                    self.assertIsNone(check_capacity(priority, limit - 1))
                    self.assertIsNone(check_capacity(priority, limit, incoming=0))
                    self.assertEqual(
                        check_capacity(priority, limit),
                        {
                            "error": "queue_full",
                            "queue": priority,
                            "pending": limit,
                            "limit": limit,
                            "workers_alive": 0,
                            "retry_after_minutes": 1,
                            "retry_after_seconds": 60,
                        },
                    )
            full = check_capacity("normal", 400, incoming=9, workers_alive=2)
            self.assertEqual(full["retry_after_minutes"], 2)

        async def test_br07_read_attempts_and_dlq(self):
            for priority in ("urgent", "normal"):
                for failures in (1, 2, 3):
                    with self.subTest(priority=priority, failures=failures):
                        ready = deque(["receipt"])
                        dlq = deque()
                        attempts = 0
                        status = "queued"
                        while ready:
                            receipt = ready.popleft()
                            attempts += 1
                            self.assertLessEqual(attempts, 3)
                            message = SimpleNamespace(
                                ack=AsyncMock(),
                                nack=AsyncMock(),
                                reject=AsyncMock(),
                            )
                            status = (
                                status_after_failure(attempts)
                                if attempts <= failures
                                else "done"
                            )
                            await settle_delivery(message, status)
                            if message.nack.await_args:
                                message.nack.assert_awaited_once_with(requeue=True)
                                ready.append(receipt)
                            elif message.reject.await_args:
                                message.reject.assert_awaited_once_with(requeue=False)
                                dlq.append(receipt)
                            else:
                                message.ack.assert_awaited_once_with()
                        self.assertEqual(attempts, min(failures + 1, 3))
                        self.assertEqual(status, "dead" if failures == 3 else "done")
                        self.assertEqual(list(dlq), ["receipt"] if failures == 3 else [])

        def test_br10_fifo_order(self):
            cases = [
                (3, 2, "U1 U2 U3 N1 N2"),
                (4, 2, "U1 U2 U3 U4 N1 N2"),
                (5, 2, "U1 U2 U3 U4 N1 U5 N2"),
                (5, 0, "U1 U2 U3 U4 U5"),
            ]
            for urgent, normal, expected in cases:
                with self.subTest(urgent=urgent, normal=normal):
                    queues = {
                        "urgent": deque(f"U{i}" for i in range(1, urgent + 1)),
                        "normal": deque(f"N{i}" for i in range(1, normal + 1)),
                    }
                    order = []
                    streak = 0
                    for _ in range(urgent + normal):
                        decision = choose_next_queue(
                            urgent_pending=len(queues["urgent"]),
                            normal_pending=len(queues["normal"]),
                            urgent_streak=streak,
                        )
                        priority = decision["queue"]
                        order.append(queues[priority].popleft())
                        streak = streak_after_claim(streak, priority)
                    self.assertEqual(" ".join(order), expected)

        def test_br10_shared_reservation_and_deadline_guard(self):
            state = dict(urgent_pending=2, normal_pending=2, urgent_streak=3)
            self.assertEqual(choose_next_queue(**state)["queue"], "urgent")
            self.assertEqual(
                choose_next_queue(**state, urgent_reserved=1),
                {"queue": "normal", "reason": "ratio_4_1"},
            )
            self.assertEqual(
                choose_next_queue(**state, deadline_guard=True),
                {"queue": "normal", "reason": "deadline_guard"},
            )
            self.assertTrue(can_claim_urgent(normal_pending=0, urgent_streak=4))
            self.assertFalse(can_claim_urgent(normal_pending=1, urgent_streak=4))
            self.assertEqual(
                choose_next_queue(
                    urgent_pending=1,
                    normal_pending=0,
                    urgent_streak=4,
                    urgent_reserved=1,
                )["queue"],
                "none",
            )

    unittest.main()
