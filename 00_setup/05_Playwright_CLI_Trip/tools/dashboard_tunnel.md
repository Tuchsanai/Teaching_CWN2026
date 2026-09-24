# dashboard_tunnel.py

A small transport helper for Windows. It forwards the container's dashboard/DevTools port to your own
machine so a local browser or client can reach it. It passes raw bytes through (HTTP and WebSocket) and does not parse them.

Path: `127.0.0.1:9230` (Windows, loopback only) → SSH `root@127.0.0.1:22022` → `docker exec -i devtools python3` relay → `127.0.0.1:9230` (inside the `devtools` container).

## Environment variables (all required)

| Name | Meaning |
|---|---|
| `LAB05_SSH_PASSWORD` | SSH password for `root` on port 22022 |
| `LAB05_SSH_HOSTKEY` | Expected server host key, base64 (the 2nd field of a `known_hosts` / `ssh-keyscan` line) |
| `LAB05_SSH_KEYTYPE` | Host key type, e.g. `ssh-ed25519` |

The script saves no credentials. The host key is pinned as `[127.0.0.1]:22022`, and any other key is rejected (`RejectPolicy`).

## Run (PowerShell)

```powershell
$env:LAB05_SSH_PASSWORD = Read-Host   # do not commit
$env:LAB05_SSH_HOSTKEY  = "<base64>"
$env:LAB05_SSH_KEYTYPE  = "ssh-ed25519"
python tools\dashboard_tunnel.py
```

When the listener is up, the script prints `READY http://127.0.0.1:9230/`. Press Ctrl+C to close the listener and the SSH session.
Requires `paramiko`. Everything else is from the standard library.
