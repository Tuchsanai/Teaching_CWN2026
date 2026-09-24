# syntax=docker/dockerfile:1
# LAB 004 API image: FastAPI + Claude Code CLI + Codex CLI.
# Contains NO credentials. Account copies arrive later in a named volume
# (/data/accounts) via deploy/lab04.sh creds.
ARG NODE_IMAGE=node:22.23.3-bookworm-slim@sha256:43ac6c60b8f89723f746e8a92ce91abd5017e627ce1ddfe4238355d3a30b772c
FROM ${NODE_IMAGE}

# Same CLI versions as the devtools container used to write this lab.
ARG CLAUDE_CODE_VERSION=2.1.281
ARG CODEX_VERSION=0.156.1

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DISABLE_AUTOUPDATER=1 \
    NPM_CONFIG_UPDATE_NOTIFIER=false

# bubblewrap: Codex's Linux sandbox helper (it warns and falls back to a bundled copy otherwise).
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 python3-venv ca-certificates tini bubblewrap \
 && rm -rf /var/lib/apt/lists/*

RUN npm install -g --no-fund --no-audit \
      "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" \
      "@openai/codex@${CODEX_VERSION}" \
 && npm cache clean --force \
 && claude --version && codex --version

COPY requirements.txt /opt/lab04/requirements.txt
RUN python3 -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir -r /opt/lab04/requirements.txt

RUN useradd --uid 10001 --user-group --create-home --home-dir /home/app --shell /usr/sbin/nologin app \
 && mkdir -p /data/accounts/claude /data/accounts/codex \
 && chown -R app:app /data/accounts && chmod -R 0700 /data/accounts

# Container-local constrained wrappers yolo1..5 / cyolo1..5 (NOT the devtools wrappers).
COPY --chmod=0755 wrappers/lab04-cli /opt/lab04/bin/lab04-cli
RUN cd /opt/lab04/bin \
 && for n in 1 2 3 4 5; do ln -s lab04-cli "yolo$n"; ln -s lab04-cli "cyolo$n"; done

COPY app /opt/lab04/app
WORKDIR /opt/lab04
USER app

# HOME is fixed; lab04.sh mounts a writable tmpfs there because the rootfs is read-only.
ENV HOME=/home/app \
    ACCOUNTS_ROOT=/data/accounts \
    WORK_ROOT=/tmp/lab04-work \
    WRAPPER_DIR=/opt/lab04/bin \
    CLAUDE_BIN=/usr/local/bin/claude \
    CODEX_BIN=/usr/local/bin/codex

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["/opt/venv/bin/python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status == 200 else 1)"]

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/opt/venv/bin/uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "1", "--no-server-header", "--no-access-log", "--timeout-keep-alive", "5"]
