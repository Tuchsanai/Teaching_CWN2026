#!/usr/bin/env bash
# usage: CODEX="codex" run_batch.sh <batch>   ; reads <batch>.txt -> <batch>.out (target=path lines)
set -u
cd "$(dirname "$0")"
B="$1"; CODEX_CMD="${CODEX:-codex}"
mkdir -p "work-$B"
LIST=$(cat "$B.txt")
PROMPT="You are an image generation worker. For EACH line below (format: target|aspect|prompt) use your built-in image generation tool ONCE to create that image with the given aspect ratio. Do not copy or move files. Do not write code. After all images are done, reply with ONLY lines of the form:
<target>=<absolute path of the generated image file>
one line per image, in the same order, nothing else.

$LIST"
$CODEX_CMD exec --skip-git-repo-check -m gpt-6-astra -c model_reasoning_effort="low" -C "work-$B" -o "$B.out" "$PROMPT" < /dev/null > "$B.log" 2>&1
echo "DONE $B exit=$?"
