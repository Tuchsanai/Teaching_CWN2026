# Chat app container: FastAPI + its own Claude Code / Codex CLIs + yoloN/cyoloN launchers.
# No credentials, tokens or web page are baked in: logins live in a named volume
# (synced by scripts/deploy.sh), the API token is a 0400 file in that volume, web/ is mounted read-only.
FROM node:22-bookworm-slim AS runtime

# Same CLI versions as the working yolo1/cyolo1 in devtools (checked with --version).
ARG CLAUDE_CODE_VERSION=2.1.281
ARG CODEX_VERSION=0.156.1

RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-venv ca-certificates tini \
 && rm -rf /var/lib/apt/lists/*

RUN npm install -g --no-fund --no-audit \
      "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" "@openai/codex@${CODEX_VERSION}" \
 && npm cache clean --force \
 && claude --version && codex --version

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt

COPY docker/ai-account-launch /usr/local/bin/ai-account-launch
RUN chmod 755 /usr/local/bin/ai-account-launch \
 && for n in 1 2 3 4 5; do \
      ln -s ai-account-launch /usr/local/bin/yolo$n; ln -s ai-account-launch /usr/local/bin/cyolo$n; \
    done \
 && useradd --uid 10001 --create-home --home-dir /home/app --shell /usr/sbin/nologin app \
 && mkdir -p /data/accounts/.Claude /data/accounts/.Codex /app/web \
 && chown -R app:app /data \
 && chmod 700 /data/accounts

WORKDIR /app
COPY app /app/app

ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AI_ACCOUNTS_BASE=/data/accounts \
    WEB_DIR=/app/web \
    API_TOKEN_FILE=/data/secrets/api_token \
    LISTEN_PORT=8004

EXPOSE 8004
USER app
VOLUME ["/data"]
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python3 -c "import os,urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"LISTEN_PORT\"]}/health', timeout=4)"
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["sh", "-c", "exec uvicorn app.main:build --factory --host 0.0.0.0 --port \"$LISTEN_PORT\" --timeout-keep-alive 5 --timeout-graceful-shutdown 10 --no-server-header --log-level info"]

# Test image: same runtime plus pytest; the tests use fake CLIs and never call a model.
FROM runtime AS test
USER root
COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements-dev.txt
COPY tests /app/tests
RUN chmod +x /app/tests/fake_bin/*
USER app
CMD ["python3", "-m", "pytest", "-q", "/app/tests"]

FROM runtime
