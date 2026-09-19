#!/bin/bash
# Inside the lab container: install the two CLIs the way LAB 001 step 1/2 does.
set -u
export DEBIAN_FRONTEND=noninteractive
echo "== $(date -u +%FT%TZ) start bootstrap"
echo "== claude: official installer"
curl -fsSL https://claude.ai/install.sh | bash 2>&1 | tail -5
export PATH="$HOME/.local/bin:$PATH"
echo "== claude --version"; claude --version
echo "== codex: npm -g"
npm install -g @openai/codex 2>&1 | tail -3
echo "== codex --version"; codex --version
echo "== $(date -u +%FT%TZ) bootstrap done"
echo "== ttyd (for browser terminal screenshots only)"
apt-get update -qq >/dev/null 2>&1 && apt-get install -y -qq ttyd >/dev/null 2>&1 && ttyd --version || echo "ttyd install failed"
echo "== $(date -u +%FT%TZ) all done"
