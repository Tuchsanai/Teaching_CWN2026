# Deploy notes (2026-09-24)

- Target: the outer Docker Desktop daemon, not devtools' inner `dockerd`. devtools' default
  `docker` talks to its own inner daemon, and no route to the outer one could be found from
  devtools (no socket, no TCP 2375/2376, no SSH on the usual ports).
- **For this deploy the user had to provide environment details**: SSH to the control host
  through an already-open ControlMaster (socket + known_hosts file), `DOCKER_HOST=ssh://...`, the
  allowed remote source folder, and the rule that the control host filesystem is not the Docker
  Desktop filesystem (so named volumes instead of bind mounts). These are stored in `.env`
  (`DOCKER_HOST`, `SSH_CONTROL_PATH`, `SSH_KNOWN_HOSTS`, `REMOTE_SOURCE_DIR`, `WEB_VOLUME`).
- The control host's own `.env` was read for key names only; none of its values were needed.
- The ControlMaster socket lives in `/tmp` of devtools; if it is gone, deploy.sh stops with
  "SSH ControlMaster socket not found" and it has to be reopened by the user.
- Browser test: the first run was cut off in round 10 ("Target page, context or browser has been
  closed") because the assistant ended its turn while the test ran in the background, which closed
  the browser. It was re-run in full and waited for to the end: 10/10 rounds, 70/70 checks
  (`tests/artifacts/e2e-run.log`).
