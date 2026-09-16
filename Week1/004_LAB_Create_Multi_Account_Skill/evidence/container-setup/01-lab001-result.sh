#!/bin/bash
# Inside the lab container: reproduce the OUTCOME of LAB 001 step 2 (what the learner's Claude built):
#   BASE_PATH=$HOME/ai-accounts, per-account config roots, shared skills/mcp, wrappers yolo1..5 / cyolo1..5.
# No login is performed here (LAB 001 leaves login to the account owner).
set -eu
BASE_PATH="${BASE_PATH:-$HOME/ai-accounts}"
mkdir -p "$BASE_PATH/.Claude/shared/skills" "$BASE_PATH/.Claude/shared/mcp" \
         "$BASE_PATH/.Codex/shared/skills"  "$BASE_PATH/.Codex/shared/mcp"
for n in 1 2 3 4 5; do
  a="$BASE_PATH/.Claude/yolo$n"; mkdir -p "$a"; chmod 700 "$a"
  [ -e "$a/skills" ] || ln -s "$BASE_PATH/.Claude/shared/skills" "$a/skills"
  c="$BASE_PATH/.Codex/cyolo$n"; mkdir -p "$c"; chmod 700 "$c"
  [ -e "$c/skills" ] || ln -s "$BASE_PATH/.Codex/shared/skills" "$c/skills"
done
cat > /usr/local/bin/ai-account-launcher <<'SH'
#!/bin/bash
# Multi-account launcher from LAB 001. Called through symlinks yolo1..yolo5 / cyolo1..cyolo5.
#   yoloN  -> CLAUDE_CONFIG_DIR=$BASE_PATH/.Claude/yoloN  claude --dangerously-skip-permissions
#   cyoloN -> CODEX_HOME=$BASE_PATH/.Codex/cyoloN         codex  --dangerously-bypass-approvals-and-sandbox
# $HOME is never changed. IS_SANDBOX=1 is required to run claude --dangerously-skip-permissions as root.
set -eu
export PATH="$HOME/.local/bin:$PATH"
: "${BASE_PATH:=$HOME/ai-accounts}"
name="$(basename "$0")"
need() { [ -d "$1" ] || { echo "$name: account folder $1 is missing (run the LAB 001 installer first)" >&2; exit 1; }; }
case "$name" in
  yolo[1-5])  dir="$BASE_PATH/.Claude/$name"; need "$dir"
              exec env IS_SANDBOX=1 CLAUDE_CONFIG_DIR="$dir" claude --dangerously-skip-permissions "$@" ;;
  cyolo[1-5]) dir="$BASE_PATH/.Codex/$name"; need "$dir"
              exec env CODEX_HOME="$dir" codex --dangerously-bypass-approvals-and-sandbox "$@" ;;
  *) echo "unknown wrapper name: $name" >&2; exit 2 ;;
esac
SH
chmod +x /usr/local/bin/ai-account-launcher
for n in 1 2 3 4 5; do ln -sfn /usr/local/bin/ai-account-launcher /usr/local/bin/yolo$n; ln -sfn /usr/local/bin/ai-account-launcher /usr/local/bin/cyolo$n; done
echo "LAB001 layout ready under $BASE_PATH"
find "$BASE_PATH" -maxdepth 3 | sort
