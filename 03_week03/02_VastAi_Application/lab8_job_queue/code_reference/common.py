"""LAB 8 shared RabbitMQ settings (gateway.py and worker.py must declare queues the same way)."""
import os

import pika

AMQP_URL = os.environ.get("LAB8_AMQP_URL", "amqp://guest:guest@127.0.0.1:5672/%2F")
JOB_QUEUE = "receipts.jobs"          # work queue (durable, max 1000 jobs)
DLQ = "receipts.jobs.dlq"            # jobs that crashed a worker
EVENT_QUEUE = "receipts.events"      # worker -> gateway: started / done / failed / heartbeat
MAX_QUEUE = int(os.environ.get("LAB8_MAX_QUEUE", "1000"))

JOB_QUEUE_ARGS = {
    "x-max-length": MAX_QUEUE,
    "x-overflow": "reject-publish",           # broker nacks the publish -> gateway answers 503
    "x-dead-letter-exchange": "",
    "x-dead-letter-routing-key": DLQ,
}

PERSISTENT = pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent,
                                  content_type="application/json")


def connect(name):
    params = pika.URLParameters(AMQP_URL)
    params.heartbeat = 60
    params.blocked_connection_timeout = 30
    params.client_properties = {"connection_name": name}
    return pika.BlockingConnection(params)


def declare(ch):
    ch.queue_declare(DLQ, durable=True)
    ch.queue_declare(JOB_QUEUE, durable=True, arguments=JOB_QUEUE_ARGS)
    ch.queue_declare(EVENT_QUEUE, durable=True)
