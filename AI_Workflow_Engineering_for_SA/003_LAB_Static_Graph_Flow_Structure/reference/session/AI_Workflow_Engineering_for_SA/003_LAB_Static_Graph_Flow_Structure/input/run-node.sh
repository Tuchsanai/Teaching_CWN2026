# Source from the LAB directory: source input/run-node.sh
# Student chooses CLI_KIND=codex or CLI_KIND=claude; each call starts a fresh session.
run_node() (
  set -eu
  id="$1"
  prompt_file="$2"
  case "${CLI_KIND:-codex}" in codex|claude) ;; *) echo 'Unknown CLI_KIND' >&2; exit 1;; esac
  case "$id" in
    customer|kitchen-front|manager|state-machine|structure|merge)
      python3 input/validate.py --ready "$id"
      ;;
    prepare) python3 input/validate.py --input ;;
    improve|fix) test -s work/review-record.md ;;
    *) echo 'Unknown node' >&2; exit 1 ;;
  esac
  test -s "$prompt_file"
  mkdir -p work/logs
  # Prevent reruns from truncating prior evidence, including unsuccessful runs.
  if [ -e "work/logs/$id.prompt.md" ]; then
    echo 'Existing run: archive the entire work set before a new run' >&2
    exit 1
  fi
  python3 - "$id" <<'CHECK'
import json,sys
from pathlib import Path
nodes=json.loads(Path('input/graph.json').read_text())['nodes']
for n in nodes:
    if n['id']==sys.argv[1]:
        for p in n['outputs']:
            if Path(p).exists(): raise SystemExit('Existing output: '+p)
CHECK
  cp "$prompt_file" "work/logs/$id.prompt.md"
  if [ "${CLI_KIND:-codex}" = codex ]; then
    codex exec --sandbox workspace-write --json \
      -o "work/logs/$id.summary.md" "$(cat "$prompt_file")" \
      < /dev/null > "work/logs/$id.jsonl" 2> "work/logs/$id.stderr.txt"
  else
    claude -p --permission-mode acceptEdits "$(cat "$prompt_file")" \
      < /dev/null > "work/logs/$id.summary.md" 2> "work/logs/$id.stderr.txt"
  fi
  case "$id" in
    customer|kitchen-front|manager|state-machine|structure|merge)
      python3 input/validate.py --node "$id" ;;
    prepare) test -s work/input-audit.md ;;
    improve) test -s work/prompt-variant.md; test -s work/prompt-experiment-plan.md ;;
    fix) echo 'Inspect the versioned repair files specified in work/fix-request.md' ;;
  esac
)
