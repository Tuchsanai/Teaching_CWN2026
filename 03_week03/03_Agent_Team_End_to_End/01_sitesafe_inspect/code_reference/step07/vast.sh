#!/bin/bash
# wrapper: load keys from .env (never printed) and run vastai with them
W=/workspace/vastapp_lab/e2e_sitesafe
set -a; . <(tr -d '\r' < $W/.env); set +a
export PATH=/root/.local/bin:$PATH
exec vastai --api-key "$VAST_API_KEY" "$@"
