# AI gateway (DESIGN §5.1, §6) · build context: ai/  (see ai/docker-compose.yml)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JOBS_DB_PATH=/data/jobs.db \
    IMAGES_DIR=/data/images

WORKDIR /app
COPY gateway/requirements.txt /app/ai/gateway/requirements.txt
RUN pip install --no-cache-dir -r /app/ai/gateway/requirements.txt

# main.py imports ai.common.queues, so the code keeps the ai/ package layout under /app.
COPY common /app/ai/common
COPY gateway /app/ai/gateway

# uid 10001 owns /data in both AI images (gateway writes, worker reads).
RUN useradd --system --uid 10001 --no-create-home sitesafe \
 && mkdir -p /data/images && chown -R 10001:10001 /data
USER 10001
EXPOSE 8000
CMD ["uvicorn", "ai.gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
