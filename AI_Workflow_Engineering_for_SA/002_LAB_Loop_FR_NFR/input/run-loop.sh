#!/usr/bin/env bash
# Every invocation is a fresh session: codex exec or claude -p; never resume.
set -u
set -o pipefail
LAB_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd) || exit 2
cd "$LAB_DIR" || exit 2
MAX_ROUNDS=${MAX_ROUNDS:-3}
MAX_SECONDS=${MAX_SECONDS:-1800}
MAX_TOKENS=${MAX_TOKENS:-0}
AI_CMD=${AI_CMD:-codex exec}
for value in "$MAX_ROUNDS" "$MAX_SECONDS" "$MAX_TOKENS"; do
  [[ "$value" =~ ^(0|[1-9][0-9]{0,8})$ ]] || { echo 'Limits must be nonnegative integers' >&2; exit 2; }
done
(( MAX_ROUNDS >= 1 && MAX_ROUNDS <= 3 && MAX_SECONDS >= 1 )) || { echo 'MAX_ROUNDS must be 1..3; MAX_SECONDS >= 1' >&2; exit 2; }
read -r -a ai_parts <<< "$AI_CMD"
if [[ ${ai_parts[0]:-} == codex && ${ai_parts[1]:-} == exec && ${#ai_parts[@]} == 2 ]]; then
  engine=codex
elif [[ ${ai_parts[0]:-} == claude && ${ai_parts[1]:-} == -p && ${#ai_parts[@]} == 2 ]]; then
  engine=claude
else
  echo 'AI_CMD supports exactly "codex exec" or "claude -p" (no eval)' >&2; exit 2
fi
for executable in python3 date timeout "${ai_parts[0]}"; do
  command -v "$executable" >/dev/null || { echo "Missing: $executable" >&2; exit 2; }
done
for required in work/fr-nfr-v0.md work/baseline-source.txt input/user-stories-lab002.md prompts/checker-criteria.md; do
  [[ -s "$required" ]] || { echo "Missing input: $required" >&2; exit 2; }
done
# Preserve all previous evidence; do not silently resume or overwrite it.
shopt -s nullglob
existing=(work/fr-nfr-v[1-9]*.md work/check-round-*.md work/loop-log.json work/loop-log.json.tmp work/logs)
for previous in "${existing[@]}"; do
  [[ ! -e "$previous" ]] || { echo 'Archive the existing work set before starting a new loop; see input/README.md' >&2; exit 2; }
done
mkdir -p work/logs || exit 2
helper=(python3 input/loop-support.py)
start_epoch=$(date +%s)
"${helper[@]}" init "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$start_epoch" "$MAX_ROUNDS" "$MAX_SECONDS" "$MAX_TOKENS" "$AI_CMD" || exit 2
reason=interrupted
finish() {
  "${helper[@]}" finish "$reason" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(date +%s)"
}
trap finish EXIT
trap 'reason=interrupted; exit 130' INT TERM
budget() {
  local why
  why=$("${helper[@]}" budget "$(date +%s)") || { reason=log_error; return 1; }
  if [[ -n "$why" ]]; then reason=$why; return 1; fi
}
run_ai() {
  local phase=$1 n=$2 out=$3 prompt log err t0 t1 utc0 utc1 remaining rc
  budget || return 1
  prompt="work/logs/${phase}-${n}.prompt.md"
  log="work/logs/${phase}-${n}.jsonl"
  err="work/logs/${phase}-${n}.stderr.txt"
  "${helper[@]}" payload "$phase" "$n" "$out" > "$prompt" || { reason=input_error; return 1; }
  t0=$(date +%s); utc0=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  remaining=$((MAX_SECONDS - (t0 - start_epoch)))
  (( remaining > 0 )) || { reason=time_limit; return 1; }
  if [[ "$engine" == codex ]]; then
    timeout --kill-after=5s "${remaining}s" "${ai_parts[@]}" --json -o "$out" - < "$prompt" > "$log" 2> "$err"
    rc=$?
  else
    timeout --kill-after=5s "${remaining}s" "${ai_parts[@]}" --verbose --output-format stream-json < "$prompt" > "$log" 2> "$err"
    rc=$?
    if (( rc == 0 )); then
      "${helper[@]}" extract "$log" "$out" 2>> "$err" || rc=1
    fi
  fi
  t1=$(date +%s); utc1=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  if ! "${helper[@]}" call "$phase" "$n" "$utc0" "$utc1" "$t0" "$t1" "$rc" "$log" "$out"; then
    if (( rc == 124 || rc == 137 )); then reason=time_limit; else reason=ai_error; fi
    return 1
  fi
}
run_ai generator 1 work/fr-nfr-v1.md || exit 2
for (( round=1; round<=MAX_ROUNDS; round++ )); do
  check="work/check-round-${round}.md"
  run_ai checker "$round" "$check" || exit 2
  # Validate table/score first, then read RESULT from the check file itself.
  streak=$("${helper[@]}" check "$round" "$check") || { reason=checker_invalid; exit 2; }
  result=$(grep -E '^RESULT: (PASS|FAIL)$' "$check")
  if [[ "$result" == 'RESULT: PASS' ]]; then reason=pass; exit 0; fi
  if (( streak >= 2 )); then reason=no_improvement; exit 1; fi
  if (( round == MAX_ROUNDS )); then reason=max_rounds; exit 1; fi
  run_ai fixer "$round" "work/fr-nfr-v$((round+1)).md" || exit 2
done
