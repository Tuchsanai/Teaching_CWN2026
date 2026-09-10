#!/usr/bin/env bash
# Never expose auth output, CLI logs, or shell tracing.
set +x
set +e
exec 2>/dev/null
umask 077
work=''
cleanup() {
    if [[ -n "$work" ]]; then rm -rf -- "$work"; fi
    exit 0
}
trap cleanup EXIT
trap 'exit 0' HUP INT TERM
if [[ $# -lt 1 || -z "$1" ]]; then
    printf '%s\n' '{"error":"missing question"}'
    exit 0
fi
for dependency in python3 timeout mktemp; do
    if ! command -v "$dependency" >/dev/null 2>&1; then
        printf '%s\n' '{"error":"missing runtime dependency"}'
        exit 0
    fi
done
question=$1
claude_model=${2:-opus}
claude_effort=${3:-high}
codex_model=${4:-gpt-6-astra}
codex_effort=${5:-medium}
work=$(mktemp -d /tmp/second-opinion-ai.XXXXXXXX) || exit 0
cd "$work" || exit 0
ask_claude() {
    if ! command -v yolo2 >/dev/null 2>&1; then
        printf 'command_missing' > claude.status
    elif ! timeout 30 yolo2 auth status --text </dev/null >/dev/null 2>&1; then
        printf 'not_logged_in' > claude.status
    elif timeout 300 yolo2 -p --model "$claude_model" --effort "$claude_effort" "$question" </dev/null >claude.answer 2>/dev/null; then
        printf 'ok' > claude.status
    else
        printf 'call_failed' > claude.status
    fi
}
ask_codex() {
    if ! command -v cyolo1 >/dev/null 2>&1; then
        printf 'command_missing' > codex.status
    elif ! timeout 30 cyolo1 login status </dev/null 2>&1 | python3 -c 'import sys; sys.exit(0 if "Logged in" in sys.stdin.read() else 1)'; then
        printf 'not_logged_in' > codex.status
    elif timeout 300 cyolo1 exec --skip-git-repo-check -m "$codex_model" -c "model_reasoning_effort=$codex_effort" -o "$work/codex.answer" "$question" </dev/null >/dev/null 2>&1; then
        printf 'ok' > codex.status
    else
        printf 'call_failed' > codex.status
    fi
}
ask_claude &
claude_pid=$!
ask_codex &
codex_pid=$!
wait "$claude_pid"
wait "$codex_pid"
python3 - "$claude_model" "$claude_effort" "$codex_model" "$codex_effort" <<'PY'
import json
import pathlib
import re
import sys

def redact(value):
    value = re.sub(r'-----BEGIN [^-]*PRIVATE KEY-----.*?-----END [^-]*PRIVATE KEY-----', '[REDACTED]', value, flags=re.S)
    value = re.sub(r'\b(?:sk-|sk-ant-|ghp_|github_pat_)[A-Za-z0-9_-]{12,}', '[REDACTED]', value)
    value = re.sub(r'(?i)\bBearer\s+\S+', 'Bearer [REDACTED]', value)
    value = re.sub(r'(?i)(["\x27]?(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|client[_-]?secret)["\x27]?\s*[:=]\s*)(["\x27][^"\x27\n]*["\x27]|[^\s,}]+)', r'\1[REDACTED]', value)
    return value

results = []
for provider, model, effort in [('claude', sys.argv[1], sys.argv[2]), ('codex', sys.argv[3], sys.argv[4])]:
    status_file = pathlib.Path(provider + '.status')
    status = status_file.read_text() if status_file.exists() else 'call_failed'
    answer = ''
    if status == 'ok':
        answer_file = pathlib.Path(provider + '.answer')
        answer = answer_file.read_text(errors='replace').strip() if answer_file.exists() else ''
        if not answer:
            status = 'empty_answer'
    if status != 'ok':
        answer = {'not_logged_in': 'ข้าม (ยังไม่ล็อกอิน)', 'command_missing': 'ข้าม (ไม่พบคำสั่ง)', 'call_failed': 'เรียกไม่สำเร็จหรือหมดเวลา', 'empty_answer': 'ไม่ได้รับคำตอบ'}.get(status, 'เรียกไม่สำเร็จ')
    results.append(dict(provider=provider, model=redact(model), effort=redact(effort), status=status, answer=redact(answer)))
print(json.dumps({'results': results}, ensure_ascii=False))
PY
exit 0
