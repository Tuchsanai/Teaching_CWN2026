#!/bin/bash
# Prepare the rented machine: work dir, packages, HF token (sent over stdin, stored 600, never printed),
# then start the download in tmux. Run from the container: ./remote_setup.sh
W=/workspace/vastapp_lab/e2e_receipt
$W/remote.sh "mkdir -p /workspace/e2e_receipt /root/.cache/huggingface"
grep '^HF_TOKEN=' $W/.env | cut -d= -f2- | tr -d '\r"' | $W/remote.sh "cat > /root/.cache/huggingface/token; chmod 600 /root/.cache/huggingface/token"
scp -q -i /workspace/vastai_lab/Devtool_SSH/devtoolSSH -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -P $(. $W/ssh_target; echo $SSH_PORT) $W/download_and_count.py $W/make_samples.py root@$(. $W/ssh_target; echo $SSH_HOST):/workspace/e2e_receipt/
$W/remote.sh "cd /workspace/e2e_receipt && /venv/main/bin/pip install -q datasets hf_transfer > pip.log 2>&1; \
  tmux new -d -s dl 'HF_HUB_ENABLE_HF_TRANSFER=1 /venv/main/bin/python download_and_count.py > download.log 2>&1'; tmux ls"
