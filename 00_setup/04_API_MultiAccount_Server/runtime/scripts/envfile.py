#!/usr/bin/env python3
"""Tiny .env editor for the deploy scripts. It never prints secret values.

  envfile.py get FILE KEY           print value (refused for secret keys)
  envfile.py set FILE KEY VALUE     set/replace KEY
  envfile.py ensure-token FILE      generate API_TOKEN if empty (value is not printed)
  envfile.py has-token FILE         exit 0 if API_TOKEN is set
"""

from __future__ import annotations

import os
import re
import secrets
import sys
from pathlib import Path

SECRET_KEYS = {"API_TOKEN"}
LINE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(.*)$")


def read(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def get(lines: list[str], key: str) -> str | None:
    for line in lines:
        m = LINE.match(line)
        if m and m.group(1) == key:
            return m.group(2).strip().strip('"').strip("'")
    return None


def write(path: Path, lines: list[str], key: str, value: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_.,:/@+-]*", value):
        sys.exit(f"refusing to write unsafe characters into {key}")
    out, done = [], False
    for line in lines:
        m = LINE.match(line)
        if m and m.group(1) == key:
            if not done:
                out.append(f"{key}={value}")
                done = True
            continue
        out.append(line)
    if not done:
        out.append(f"{key}={value}")
    tmp = path.with_name(path.name + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    os.replace(tmp, path)
    os.chmod(path, 0o600)


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, path = sys.argv[1], Path(sys.argv[2])
    lines = read(path)
    if cmd == "get":
        key = sys.argv[3]
        if key in SECRET_KEYS:
            sys.exit(f"{key} is secret and is never printed")
        print(get(lines, key) or "")
    elif cmd == "set":
        write(path, lines, sys.argv[3], sys.argv[4])
    elif cmd == "ensure-token":
        if len(get(lines, "API_TOKEN") or "") < 16:
            write(path, lines, "API_TOKEN", secrets.token_urlsafe(32))
            print("generated a new API_TOKEN in .env (not shown)")
        else:
            print("API_TOKEN already set in .env (not shown)")
    elif cmd == "has-token":
        sys.exit(0 if len(get(lines, "API_TOKEN") or "") >= 16 else 1)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
