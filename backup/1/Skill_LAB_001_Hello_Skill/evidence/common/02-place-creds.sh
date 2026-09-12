#!/bin/bash
# Put the borrowed credential files into the LAB 001 layout (never print them).
set -eu
B=/root/ai-accounts
install -m 600 /root/creds/yolo1.credentials.json $B/.Claude/yolo1/.credentials.json
install -m 600 /root/creds/yolo2.credentials.json $B/.Claude/yolo2/.credentials.json
install -m 600 /root/creds/cyolo1.auth.json $B/.Codex/cyolo1/auth.json
rm -rf /root/creds
# skip onboarding prompts for the instructor's screenshots (theme/trust are shown in LAB 001 already)
for n in 1 2; do
  f=$B/.Claude/yolo$n/.claude.json
  [ -e "$f" ] || printf '{"hasCompletedOnboarding":true,"theme":"dark","bypassPermissionsModeAccepted":true}\n' > "$f"
done
echo "credentials placed"
