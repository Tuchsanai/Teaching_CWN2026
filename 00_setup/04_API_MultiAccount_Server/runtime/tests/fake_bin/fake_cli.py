#!/usr/bin/env python3
"""Stand-in for the claude / codex CLIs in tests. Never contacts any model.

Behaviour is chosen by a marker in the last user message; every call is recorded to
<account config dir>/last_call.json so tests can check argv, env and stdin.
"""

import json
import os
import re
import sys
import time

tool = os.path.basename(sys.argv[0])  # "claude" or "codex"
argv = sys.argv[1:]
stdin = sys.stdin.read()
home = os.environ.get("CLAUDE_CONFIG_DIR") if tool == "claude" else os.environ.get("CODEX_HOME")

m = re.search(r"<conversation>\n(.*)\n</conversation>", stdin, re.S)
messages = json.loads(m.group(1)) if m else []
last = next((x["content"] for x in reversed(messages) if x["role"] == "user"), "")

with open(os.path.join(home, "last_call.json"), "w") as f:
    json.dump({"argv": argv, "stdin": stdin, "cwd": os.getcwd(),
               "env": {k: os.environ[k] for k in os.environ
                       if k in ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "HOME", "ANTHROPIC_API_KEY",
                                "OPENAI_API_KEY", "API_TOKEN", "IS_SANDBOX")}}, f)

def arg(flag):
    return argv[argv.index(flag) + 1] if flag in argv else None

model = arg("--model") or arg("-m")
effort = arg("--effort") or next((a.split("=", 1)[1].strip('"') for a in argv
                                  if a.startswith("model_reasoning_effort=")), None)
answer = f"FAKE-{tool.upper()} model={model} effort={effort} n={len(messages)} last={last}"

if "__SLEEP__" in last:
    time.sleep(30)
if "__HUGE__" in last:
    sys.stdout.write("x" * (6 * 1024 * 1024))
    sys.exit(0)

if tool == "claude":
    if "__AUTH_FAIL__" in last:
        print(json.dumps({"type": "result", "is_error": True, "result": "Not logged in · Please run /login"}))
        print("SECRET-STDERR-DETAIL", file=sys.stderr)
        sys.exit(1)
    if "__RATE__" in last:
        print(json.dumps({"type": "result", "is_error": True, "result": "Claude usage limit reached"}))
        sys.exit(1)
    if "__EMPTY__" in last:
        answer = ""
    print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": answer,
                      "usage": {"input_tokens": 11, "output_tokens": 7}}))
    sys.exit(0)

# codex exec
if "__AUTH_FAIL__" in last:
    print("ERROR: unexpected status 401 Unauthorized SECRET-STDERR-DETAIL", file=sys.stderr)
    sys.exit(1)
if "__EMPTY__" in last:
    answer = ""
with open(arg("--output-last-message"), "w") as f:
    f.write(answer)
print("codex progress noise on stdout")
