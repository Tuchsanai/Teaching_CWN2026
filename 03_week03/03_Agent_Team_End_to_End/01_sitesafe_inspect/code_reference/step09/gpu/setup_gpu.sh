#!/bin/bash
# One-time setup on the rented GPU machine (a Docker container itself: no docker, no systemd).
# Installs RabbitMQ + Python packages, makes a self-signed TLS certificate for the gateway,
# and writes deploy/.env. The gateway API key arrives on stdin (never on the command line).
# Usage: setup_gpu.sh <public-ip>  < api_key
set -e
D=/workspace/e2e_sitesafe/deploy; PUBLIC_IP=$1
mkdir -p $D/tls $D/data/images $D/logs; chmod 700 $D/tls
read -r API_KEY || true
[ -n "$API_KEY" ] || { echo "no API key on stdin"; exit 1; }

echo "== packages $(date -u +%T)"
export DEBIAN_FRONTEND=noninteractive
if ! command -v rabbitmq-server >/dev/null; then
  apt-get update -qq && apt-get install -y -qq rabbitmq-server >/dev/null
fi
/venv/main/bin/pip install -q "fastapi>=0.115" "python-multipart>=0.0.18" "aio-pika>=9.4" "uvicorn[standard]>=0.30" "pika>=1.3" "pillow>=10"

echo "== rabbitmq config"
# AMQP only on loopback: the gateway and the worker are on this machine.
cat > /etc/rabbitmq/rabbitmq.conf <<CONF
listeners.tcp.local = 127.0.0.1:5672
CONF
chmod 644 /etc/rabbitmq/rabbitmq.conf   # must be readable by user rabbitmq

echo "== TLS certificate (self-signed, SAN = public IP)"
if [ ! -f $D/tls/gateway.crt ]; then
  openssl req -x509 -newkey rsa:2048 -nodes -days 30 -keyout $D/tls/gateway.key -out $D/tls/gateway.crt \
    -subj "/CN=sitesafe-gateway" -addext "subjectAltName=IP:$PUBLIC_IP,IP:127.0.0.1,DNS:localhost" 2>/dev/null
  chmod 600 $D/tls/gateway.key
fi

echo "== deploy/.env"
if [ -f $D/.env ]; then MQ_PW=$(grep ^RABBITMQ_PASSWORD= $D/.env | cut -d= -f2); fi
[ -n "$MQ_PW" ] || MQ_PW=$(openssl rand -hex 24)
CONF=$(/venv/main/bin/python -c "import json;print(json.load(open('/workspace/e2e_sitesafe/model/threshold.json'))['conf_threshold'])")
umask 077
cat > $D/.env <<ENV
GATEWAY_API_KEY=$API_KEY
RABBITMQ_USER=sitesafe
RABBITMQ_PASSWORD=$MQ_PW
RABBITMQ_URL=amqp://sitesafe:$MQ_PW@127.0.0.1:5672/
MAX_QUEUE_DEPTH=200
MAX_DELIVERY=3
PROCESSING_TIMEOUT_S=120
JOBS_DB_PATH=$D/data/jobs.db
IMAGES_DIR=$D/data/images
MODEL_PATH=/workspace/e2e_sitesafe/model/best.pt
CONF_THRESHOLD=$CONF
MODEL_VERSION=ppe-yolo-v1
YOLO_OFFLINE=true
ENV
echo "SETUP_DONE conf=$CONF $(date -u +%T)"
