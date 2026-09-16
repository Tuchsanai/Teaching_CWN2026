#!/usr/bin/env bash
set -euo pipefail

base=/root/workspace/CWN/Teaching/A
readme="$base/004_LAB_Parallel_Stakeholders/README.md"
prompt_dir="$base/004_LAB_Parallel_Stakeholders/prompts"
evidence_dir="$base/evidence/lab004"
extract="$evidence_dir/.prompt-extract.$$"
trap 'rm -f "$extract"' EXIT

set -- step-01.md step-02a.md step-02b.md step-03.md step-04.md step-05.md
awk '
  /^```text$/ { inside=1; block++; next }
  /^```$/ && inside { inside=0; next }
  inside { print block "\t" $0 }
' "$readme" > "$extract.all"
trap 'rm -f "$extract" "$extract.all"' EXIT

block=1
for file do
  awk -F '\t' -v block="$block" '$1 == block { sub(/^[^\t]*\t/, ""); print }' "$extract.all" > "$extract"
  if cmp -s "$extract" "$prompt_dir/$file"; then
    printf '%s MATCH\n' "${file%.md}"
  else
    printf '%s DIFF\n' "${file%.md}"
  fi
  block=$((block + 1))
done
