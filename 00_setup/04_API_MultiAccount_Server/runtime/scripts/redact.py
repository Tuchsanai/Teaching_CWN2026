#!/usr/bin/env python3
"""Filter stdin -> stdout, masking secrets. Usage: redact.py [TOKEN_FILE ...]"""
import re
import sys

secrets = []
for path in sys.argv[1:]:
    try:
        value = open(path, encoding="utf-8").read().strip()
    except OSError:
        continue
    if len(value) >= 8:
        secrets.append(value)

PATTERNS = [
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+"), r"\1[REDACTED]"),
    (re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}"), "[REDACTED_JWT]"),
    (re.compile(r"sk-[A-Za-z0-9_-]{16,}"), "[REDACTED_KEY]"),
    (re.compile(r'(?i)("?(?:access|refresh|id)_?token"?\s*[:=]\s*"?)[^"\s,}]+'), r"\1[REDACTED]"),
]

for line in sys.stdin:
    for s in secrets:
        line = line.replace(s, "[REDACTED_API_TOKEN]")
    for pattern, repl in PATTERNS:
        line = pattern.sub(repl, line)
    sys.stdout.write(line)
