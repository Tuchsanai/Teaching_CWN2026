#!/bin/bash
# Step 11 · runs INSIDE the container multi-account (called by gpu.sh push).
# Copies ai.tgz + svc.sh to the GPU machine and writes secrets.env there (chmod 600). No key is printed.
set -e
W=${W:-/workspace/vastapp_lab/e2e_receipt}; R=${R:-/workspace/e2e_receipt/step11}
. $W/ssh_target; K=/workspace/vastai_lab/Devtool_SSH/devtoolSSH
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
umask 077; T=$(mktemp -d)
GK=$(grep -E '^GATEWAY_API_KEY=' $W/.env | cut -d= -f2- | tr -d '\r')
# keep the vLLM key if the GPU machine already has one, else make a new one
$W/remote.sh "grep -s '^VLLM_API_KEY=' $R/secrets.env" > $T/vk || true
grep -q . $T/vk || echo "VLLM_API_KEY=$(python3 -c 'import secrets;print(secrets.token_hex(24))')" > $T/vk
{ echo "GATEWAY_API_KEYS=$GK"; cat $T/vk; } > $T/secrets.env
scp -q -i $K $O -P $SSH_PORT $W/step11/ai.tgz $W/step11/svc.sh $T/secrets.env root@$SSH_HOST:$R/
rm -rf $T
$W/remote.sh "cd $R && chmod 600 secrets.env && rm -rf app/ai && mkdir -p app && tar -C app -xzf ai.tgz && chmod +x svc.sh && awk -F= '{print \"  \" \$1 \" (\" length(\$2) \" chars)\"}' secrets.env && ls app/ai"
