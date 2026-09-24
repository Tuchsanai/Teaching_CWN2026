# Multi-account chat API (FastAPI + Claude Code / Codex CLIs)

One container (`ai-chat-app`) runs FastAPI plus its own `claude` 2.1.281 and `codex` 0.156.1
(same versions as devtools), and its own `yolo1..5` / `cyolo1..5` launchers
(`docker/ai-account-launch`). Devtools only builds and deploys it; models are never called
through devtools.

| Path | What it is |
|---|---|
| `app/main.py` | routes, Bearer auth, limits, error format |
| `app/catalog.py` | allowed provider / model / effort / account combinations |
| `app/runner.py` | runs one CLI call: safe flags, timeout, rlimits, output cap, error mapping |
| `app/transcript.py` | full `messages` history -> one prompt (JSON, so roles can't be forged) |
| `docker/ai-account-launch` | in-container yoloN/cyoloN: own config folder per account under `/data/accounts`, refuses bypass flags |
| `web/index.html` | the whole chat page in one file (no external resources, no build); mounted read-only at `/app/web`, not in the image. Edit and reload, no rebuild needed |
| `scripts/deploy.sh` | detect accounts, build, check port, copy login files into the volume, start |
| `scripts/port.sh` | port check on the Docker host (`--write` saves APP_PORT) |
| `scripts/test.sh` | run tests in the image with `--network none` (fake CLIs) |

## Endpoints
- `GET /` – `web/index.html`, or a readable 503 page if it doesn't exist yet
- `GET /health` – no token
- `GET /v1/models` – Bearer; models, efforts, accounts (for the page's dropdowns)
- `POST /v1/chat/completions` – Bearer; `{messages, model?, reasoning_effort?, account?, provider?}`,
  non-streaming, OpenAI shape, answer in `choices[0].message.content`

The page calls the API at its own origin by default (no host/port inside the file; the URL can be
changed in the sidebar). The port is `APP_PORT` in `.env`; the page URL is `http://localhost:$APP_PORT/`.
The token is typed into the page and kept in memory only. `/v1/models` also returns `limits`,
which the page uses for its message/size counters.

## Deploy
    scripts/deploy.sh            # first time / updates (keeps logins already in the volume)
    scripts/deploy.sh --refresh-logins   # copy login files from devtools again
