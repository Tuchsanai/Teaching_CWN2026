#!/usr/bin/env bash
# Run one immutable prompt in the prepared session and retain execution evidence.
set -u
ref_dir=$(cd "$(dirname "$0")" && pwd)
node=$1
case "$node" in
  customer) step=step-01-fanout/customer ;;
  kitchen-front) step=step-01-fanout/kitchen-front ;;
  manager) step=step-01-fanout/manager ;;
  state-machine) step=step-02-state-machine ;;
  structure) step=step-03-structure ;;
  merge) step=step-04-merge ;;
  *) exit 2 ;;
esac
dest="$ref_dir/$step"
runtime="$ref_dir/session/AI_Workflow_Engineering_for_SA/003_LAB_Static_Graph_Flow_Structure"
test ! -e "$dest/log.jsonl" || { echo 'Existing evidence: create a new attempt directory first'; exit 2; }
cd "$runtime" || exit 2
s=$(date +%s.%N)
extra=()
if [ "${USE_EXECUTION_CONTEXT:-0}" = 1 ]; then
  extra=(-c "developer_instructions=$(cat "$ref_dir/execution-context.txt")")
fi
"${CODEX_CMD:-codex}" exec --json -m gpt-6-astra -c model_reasoning_effort="high" "${extra[@]}" -o "$dest/final-response.md" "$(cat "$dest/prompt.md")" </dev/null > "$dest/log.jsonl" 2> "$dest/stderr.txt"
rc=$?
e=$(date +%s.%N)
python3 "$ref_dir/record-run.py" "$node" "$dest" "$s" "$e" "$rc"
exit "$rc"
