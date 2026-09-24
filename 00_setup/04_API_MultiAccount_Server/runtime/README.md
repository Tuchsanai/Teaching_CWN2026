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

## Deploy (outer Docker host, from devtools)
All connection values are in `.env` (names in `.env.example`); nothing is hard-coded in the scripts.

    scripts/deploy.sh --check          # verify daemon (refuses devtools' inner Docker), list existing objects, check port
    scripts/deploy.sh                  # build + copy source/web/logins + start + smoke test + record URLs
    scripts/deploy.sh --refresh-logins # copy login files from devtools again (otherwise kept)

- `docker` reaches `DOCKER_HOST=ssh://...` through `scripts/ssh-shim/ssh`, which reuses the open
  ControlMaster (`SSH_CONTROL_PATH`, `SSH_KNOWN_HOSTS`). The shim is put in PATH only for docker
  calls (`scripts/remote-env.sh`); global SSH config is not changed.
- The daemon does not share the control host's filesystem, so nothing is bind-mounted:
  `index.html` goes into the named volume `WEB_VOLUME` (mounted read-only), logins and the token
  into `ACCOUNTS_VOLUME`, both through pipes. The complete source is copied to `REMOTE_SOURCE_DIR`.
- Token: `cat secrets/api_token` (0600 file in devtools; 0400 file in the volume; never printed).

## Operate (this app only)
    scripts/app.sh status | stop | start | restart | logs [N] | health

## Tests
    scripts/test.sh                    # unit tests with fake CLIs, --network none
    python3 tests/e2e/api_check.py     # real API checks against APP_TEST_URL
    node tests/e2e/chat_e2e.js         # real Chromium, real page, real models (10 rounds)
Artifacts (screenshots, conversation JSON, logs; no secrets) go to `tests/artifacts/`.
