#!/usr/bin/env python3
"""แปลง shared/mcp/mcp.json ({"mcpServers": {...}}) เป็นค่า -c ของ Codex ทีละบรรทัด

    mcp_servers.<name>={command="...", args=[...], env={...}}

ค่า -c ของ Codex ถูก parse เป็น TOML จึงแปลงเป็น TOML inline table (ไม่มีขึ้นบรรทัดใหม่)
ข้าม key "type" (รูปแบบของ Claude) ที่ Codex ไม่ใช้
"""
import json
import re
import sys

BARE = re.compile(r"^[A-Za-z0-9_-]+$")


def key(k):
    return k if BARE.match(k) else json.dumps(k)


def toml(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return json.dumps(v)
    if isinstance(v, str):
        return json.dumps(v)  # JSON string escape ใช้เป็น TOML basic string ได้
    if isinstance(v, list):
        return "[" + ", ".join(toml(x) for x in v) + "]"
    if isinstance(v, dict):
        return "{" + ", ".join(f"{key(k)} = {toml(x)}" for k, x in v.items()) + "}"
    raise TypeError(f"unsupported value: {v!r}")


def main(path):
    with open(path, encoding="utf-8") as f:
        servers = json.load(f).get("mcpServers", {})
    for name, cfg in servers.items():
        cfg = {k: v for k, v in cfg.items() if k != "type"}
        print(f"mcp_servers.{key(name)}={toml(cfg)}")


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except Exception as e:  # noqa: BLE001
        print(f"mcp_json_to_codex: {e}", file=sys.stderr)
        sys.exit(1)
