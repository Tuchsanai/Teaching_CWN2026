import json, os, re
from mcp_client import MCPClient

class Probe:
    """ห่อ MCPClient: เรียก tool แล้วเขียนสรุป (args, เวลา, bytes, isError, content types, ข้อความเต็ม) ลง <name>.md"""
    def __init__(self, name, extra_args=None, config="mcp.config.json"):
        os.makedirs(f"{name}_img", exist_ok=True)
        cmd = ["/usr/bin/playwright-mcp", "--config", config] + (extra_args or [])
        self.c = MCPClient(cmd, f"{name}.jsonl", img_dir=f"{name}_img")
        self.md = open(f"{name}.md", "w")
        self.md.write(f"# {name}\ncmd: `{' '.join(cmd)}`\n\n")
        self.n = 0
        init = self.c.initialize()
        self.md.write(f"initialize → {json.dumps(init['result'], ensure_ascii=False)}\n\n")

    def call(self, tool, args=None, note="", maxtext=None, timeout=120):
        self.n += 1
        r = self.c.call(tool, args or {}, timeout=timeout)
        res = r.get("result")
        err = r.get("error")
        text = MCPClient.text(r) if res else ""
        types = [c.get("type") for c in (res or {}).get("content", [])]
        lines = text.count("\n") + 1 if text else 0
        self.md.write(f"## {self.n:02d} {tool} {note}\n")
        self.md.write(f"args: `{json.dumps(args or {}, ensure_ascii=False)}`\n\n")
        self.md.write(f"elapsed={r['_elapsed']}s · response_bytes={r['_bytes']} · text_bytes={len(text.encode())} · "
                      f"text_lines={lines} · content={types} · isError={(res or {}).get('isError')} · "
                      f"jsonrpc_error={json.dumps(err) if err else None} · images={r['_saved']}\n\n")
        shown = text if maxtext is None or len(text) <= maxtext else text[:maxtext] + f"\n...[ตัด เหลือ {maxtext}/{len(text)} ตัวอักษร]"
        self.md.write("```text\n" + shown + "\n```\n\n")
        self.md.flush()
        with open(f"{self.c.log_path[:-6]}_{self.n:02d}_{tool}.txt", "w") as f:
            f.write(text)
        r["_text"] = text
        return r

    def close(self):
        rc = self.c.close()
        self.md.write(f"process exit code: {rc}\n")
        self.md.close()

def snap_yaml(text):
    m = re.search(r"### Snapshot\n```yaml\n(.*?)\n```", text, re.S)
    return m.group(1) if m else None

def find_ref(text, pattern):
    for line in text.splitlines():
        if re.search(pattern, line):
            m = re.search(r"\[ref=([^\]]+)\]", line)
            if m:
                return m.group(1), line.strip()
    return None, None
