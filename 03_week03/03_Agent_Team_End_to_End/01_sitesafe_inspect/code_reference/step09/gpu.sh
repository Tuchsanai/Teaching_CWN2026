#!/bin/bash
# Run a command on the GPU machine from Git Bash on this PC:  code_step09/gpu.sh "<command>"
export MSYS_NO_PATHCONV=1
exec docker exec -i multi-account bash -c 'cd /workspace/vastapp_lab/e2e_sitesafe && exec ./remote.sh "$1"' _ "$1"
