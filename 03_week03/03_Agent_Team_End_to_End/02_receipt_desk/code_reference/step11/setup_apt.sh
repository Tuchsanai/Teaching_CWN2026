#!/bin/bash
# Step 11 · NGINX + RabbitMQ packages on the GPU machine (tmux "aptset"). Log: step11/apt.log
set -x
export DEBIAN_FRONTEND=noninteractive
dpkg --configure -a
apt-get install -y -q -o Dpkg::Use-Pty=0 nginx rabbitmq-server && echo APT_DONE
