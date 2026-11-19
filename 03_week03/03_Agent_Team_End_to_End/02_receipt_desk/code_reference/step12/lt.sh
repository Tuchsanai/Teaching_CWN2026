#!/bin/bash
# Step 12 · drive the load generator from this PC (through the container multi-account -> SSH).
# usage: lt.sh push            copy loadgen.py to the container and the GPU machine, make the venv
#        lt.sh run <test...>   run "loadgen.py <test...>" on the GPU machine in tmux session "lt" (detached)
#        lt.sh log             last lines of the running test
#        lt.sh pull            copy results/*.json back to ./results/capacity/raw
# Keys are never printed (loadgen.py reads secrets.env on the GPU machine itself).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; ROOT="$(cd "$HERE/.." && pwd)"
W=/workspace/vastapp_lab/e2e_receipt; R=/workspace/e2e_receipt/loadtest
dx() { MSYS_NO_PATHCONV=1 docker exec -i multi-account bash -c "$1"; }
winpath() { command -v cygpath >/dev/null && cygpath -m "$1" || echo "$1"; }
case "$1" in
  push)
    dx "mkdir -p $W/loadtest"
    MSYS_NO_PATHCONV=1 docker cp "$(winpath "$HERE/loadgen.py")" multi-account:$W/loadtest/loadgen.py
    MSYS_NO_PATHCONV=1 docker cp "$(winpath "$HERE/lt.sh")" multi-account:$W/loadtest/lt.sh
    dx "$W/remote.sh 'mkdir -p $R && cat > $R/loadgen.py' < $W/loadtest/loadgen.py"
    dx "$W/remote.sh '[ -x $R/venv/bin/python ] || (python3 -m venv $R/venv && $R/venv/bin/pip -q install httpx pyarrow pillow)'" ;;
  run) shift
    dx "$W/remote.sh 'tmux kill-session -t lt 2>/dev/null; cd $R && tmux new -d -s lt \"venv/bin/python -u loadgen.py $* > run.log 2>&1; echo EXIT=\\\$? >> run.log\"'" ;;
  log) dx "$W/remote.sh 'tail -n ${2:-25} $R/run.log'" ;;
  pull)
    mkdir -p "$ROOT/results/capacity/raw"
    dx "$W/remote.sh 'cd $R && tar czf - results' > $W/loadtest/results.tgz"
    dx "cd $W/loadtest && rm -rf results && tar xzf results.tgz"
    MSYS_NO_PATHCONV=1 docker cp multi-account:$W/loadtest/results/. "$(winpath "$ROOT/results/capacity/raw")"
    ls "$ROOT/results/capacity/raw" ;;
  *) echo "usage: $0 push | run <test> | log | pull"; exit 1 ;;
esac
