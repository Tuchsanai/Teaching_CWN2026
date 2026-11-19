# GPU Worker (YOLO) · build context: ai/  (see ai/docker-compose.yml)
# Needs the NVIDIA Container Toolkit on the GPU machine. The model file is mounted read-only
# (MODEL_PATH); the worker never downloads anything at run time (DESIGN §10).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    YOLO_OFFLINE=true \
    YOLO_CONFIG_DIR=/tmp/ultralytics

RUN apt-get update \
 && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY worker/requirements.txt /app/ai/worker/requirements.txt
RUN pip install --no-cache-dir -r /app/ai/worker/requirements.txt

COPY common /app/ai/common
COPY worker /app/ai/worker

RUN useradd --system --uid 10001 --no-create-home sitesafe \
 && mkdir -p /data/images && chown -R 10001:10001 /data
USER 10001
CMD ["python", "-m", "ai.worker.worker"]
