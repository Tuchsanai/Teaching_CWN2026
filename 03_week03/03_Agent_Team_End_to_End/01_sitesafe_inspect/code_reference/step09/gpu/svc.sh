#!/bin/bash
# Start / stop / status of the 3 GPU-side services as plain processes in tmux sessions
# (they survive a dropped SSH connection).
#   svc.sh start|stop|kill|status  rabbitmq|gateway|worker|all
# "stop" = SIGTERM (graceful) · "kill" = SIGKILL (used by the worker-stop test)
D=/workspace/e2e_sitesafe/deploy; PY=/venv/main/bin/python
# RabbitMQ tools run as user rabbitmq but keep HOME=/root (unreadable .erlang.cookie) unless HOME is set.
rabbitmqctl(){ (cd /tmp && runuser -u rabbitmq -- env HOME=/var/lib/rabbitmq /usr/lib/rabbitmq/bin/rabbitmqctl "$@"); }
pids(){ case $1 in
  rabbitmq) pgrep -u rabbitmq -f beam.smp;;
  gateway)  pgrep -f "uvicorn ai.gateway.main:app";;
  worker)   pgrep -f "ai.worker.worker";;
esac; }
start(){ case $1 in
  rabbitmq)
    [ -n "$(pids rabbitmq)" ] && { echo "rabbitmq already running"; return; }
    tmux new-session -d -s ss-rabbitmq "HOME=/var/lib/rabbitmq runuser -u rabbitmq -- rabbitmq-server >> $D/logs/rabbitmq.log 2>&1"
    for i in $(seq 30); do rabbitmqctl -q await_startup >/dev/null 2>&1 && break; sleep 2; done
    . <(grep -E '^RABBITMQ_(USER|PASSWORD)=' $D/.env)
    if ! rabbitmqctl -q list_users | grep -q "^$RABBITMQ_USER"; then
      rabbitmqctl -q add_user "$RABBITMQ_USER" "$RABBITMQ_PASSWORD"
      rabbitmqctl -q set_permissions -p / "$RABBITMQ_USER" ".*" ".*" ".*"
      rabbitmqctl -q delete_user guest
    fi
    echo "rabbitmq started";;
  gateway)
    [ -n "$(pids gateway)" ] && { echo "gateway already running"; return; }
    tmux new-session -d -s ss-gateway "cd $D/app && set -a && . $D/.env && set +a && exec $PY -m uvicorn ai.gateway.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile $D/tls/gateway.key --ssl-certfile $D/tls/gateway.crt >> $D/logs/gateway.log 2>&1"
    echo "gateway started";;
  worker)
    [ -n "$(pids worker)" ] && { echo "worker already running"; return; }
    tmux new-session -d -s ss-worker "cd $D/app && set -a && . $D/.env && set +a && exec $PY -m ai.worker.worker >> $D/logs/worker.log 2>&1"
    echo "worker started";;
esac; }
stop(){ sig=$1; svc=$2
  if [ $svc = rabbitmq ]; then rabbitmqctl -q stop >/dev/null 2>&1; echo "rabbitmq stopped"; return; fi
  p=$(pids $svc); [ -n "$p" ] && kill -$sig $p; echo "$svc: sent SIG$sig to ${p:-nothing}"; }
status(){ for s in rabbitmq gateway worker; do p=$(pids $s | tr '\n' ' '); echo "$s: ${p:+running pid $p}${p:-STOPPED}"; done; }
all(){ [ "$2" = all ] && set -- $1 rabbitmq gateway worker; echo "${@:2}"; }
case $1 in
  start)  for s in $(all "$@"); do start $s; done;;
  stop)   for s in $(all "$@" | tr ' ' '\n' | tac); do stop TERM $s; done;;
  kill)   stop KILL $2;;
  status) status;;
  *) echo "usage: svc.sh start|stop|kill|status rabbitmq|gateway|worker|all"; exit 1;;
esac
