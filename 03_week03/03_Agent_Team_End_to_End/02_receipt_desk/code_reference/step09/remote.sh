#!/bin/bash
# run a command on the rented machine over SSH (host/port saved in ssh_target after the instance is running)
W=/workspace/vastapp_lab/e2e_receipt; . $W/ssh_target
exec ssh -i /workspace/vastai_lab/Devtool_SSH/devtoolSSH -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=20 -p $SSH_PORT root@$SSH_HOST "$@"
