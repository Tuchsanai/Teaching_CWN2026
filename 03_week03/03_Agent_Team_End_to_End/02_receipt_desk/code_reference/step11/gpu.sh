#!/bin/bash
# Step 11 · control the serving stack on the rented machine (label e2e-receipt) from this PC.
# usage: gpu.sh push            copy ./app/ai + svc.sh + secrets to the GPU machine
#        gpu.sh start|stop|restart|status|log <svc...|all>
#        svc = rabbitmq vllm0 vllm1 nginx gateway worker0 worker1   (each worker separately)
#        gpu.sh sh '<command>'  run any command there (e.g. nvidia-smi)
# Goes through the container multi-account (remote.sh = SSH with the devtoolSSH key). Keys never printed.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/.." && pwd)"
W=/workspace/vastapp_lab/e2e_receipt; R=/workspace/e2e_receipt/step11
dx() { MSYS_NO_PATHCONV=1 docker exec multi-account bash -c "$1"; }
rx() { MSYS_NO_PATHCONV=1 docker exec -i multi-account bash -c "$W/remote.sh bash -s"; }   # stdin = script
winpath() { command -v cygpath >/dev/null && cygpath -m "$1" || echo "$1"; }
case "$1" in
  push)
    tar -C "$ROOT/app" --exclude=__pycache__ --exclude=train/runs -czf "$HERE/.ai.tgz" ai
    MSYS_NO_PATHCONV=1 docker cp "$(winpath "$HERE/.ai.tgz")" multi-account:$W/step11/ai.tgz
    MSYS_NO_PATHCONV=1 docker cp "$(winpath "$HERE/svc.sh")" multi-account:$W/step11/svc.sh
    rm -f "$HERE/.ai.tgz"
    MSYS_NO_PATHCONV=1 docker cp "$(winpath "$HERE/push_c.sh")" multi-account:$W/step11/push_c.sh
    dx "bash $W/step11/push_c.sh" ;;
  start|stop|restart|status|log) a=$1; shift; echo "bash $R/svc.sh $a ${*:-all}" | rx ;;
  sh) shift; printf '%s
' "$*" | rx ;;
  *) echo "usage: $0 push | start|stop|restart|status|log <svc|all> | sh CMD"; exit 1 ;;
esac
