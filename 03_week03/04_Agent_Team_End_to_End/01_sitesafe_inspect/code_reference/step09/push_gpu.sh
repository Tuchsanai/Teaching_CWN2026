#!/bin/bash
# Run from the lesson folder in Git Bash: copy ./app/ai and ./code_step09/gpu to the GPU machine
# through the multi-account container (which holds the SSH key).
export MSYS_NO_PATHCONV=1
W=/workspace/vastapp_lab/e2e_sitesafe; S=$W/step09
tar --exclude=__pycache__ --exclude=.pytest_cache --exclude='.env*' -czf - -C app ai -C ../code_step09 gpu \
 | docker exec -i multi-account bash -c "rm -rf $S/push && mkdir -p $S/push && tar -xzf - -C $S/push && cd $W && . ./ssh_target && \
   tar -czf - -C $S/push . | ./remote.sh 'mkdir -p /workspace/e2e_sitesafe/deploy/app /workspace/e2e_sitesafe/deploy/bin && cd /workspace/e2e_sitesafe/deploy && tar -xzf - -C /tmp --one-top-level=ss_push && rm -rf app/ai && cp -r /tmp/ss_push/ai app/ai && cp /tmp/ss_push/gpu/* bin/ && chmod +x bin/*.sh; rm -rf /tmp/ss_push; ls app/ai bin'"
