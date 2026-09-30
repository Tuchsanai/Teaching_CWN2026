#!/usr/bin/env python3
"""MCP client แบบ stdio สำหรับ Playwright MCP — Python stdlib ล้วน

- spawn /usr/bin/playwright-mcp เอง (ด้วย --config ที่เฟส 1 ยืนยันแล้ว) คุยผ่าน stdin/stdout
  JSON-RPC 2.0 หนึ่งข้อความต่อหนึ่งบรรทัด
- handshake: initialize → notifications/initialized → tools/list
- call(tool, args) คืน {"text", "images", "is_error", "seconds", "bytes"}
- ทุกข้อความที่ส่ง/รับเขียนลง rpc.jsonl (ไฟล์ของ step ปัจจุบัน ตั้งด้วย set_step_log)
  และลง rpc_all.jsonl ของทั้ง run; ข้อมูลภาพ base64 ถูกแทนด้วย "<N bytes image/png>"
"""
import base64, json, os, queue, subprocess, threading, time
from pathlib import Path

PROTOCOL_VERSION = "2025-06-18"
SERVER = "/usr/bin/playwright-mcp"
BROWSERS = "/ms-playwright"          # ตำแหน่ง Chromium ใน image (เฟส 1: /opt/ms-playwright ใช้ไม่ได้)


def write_config(path, output_dir):
    """config ที่เฟส 1 ยืนยัน: chromium, headless, isolated, 1920x1080 @2x, en-US"""
    cfg = {
        "browser": {
            "browserName": "chromium",
            "isolated": True,
            "launchOptions": {"headless": True, "chromiumSandbox": False},
            "contextOptions": {"viewport": {"width": 1920, "height": 1080},
                               "deviceScaleFactor": 2, "locale": "en-US"},
        },
        "outputDir": str(output_dir),
    }
    Path(path).write_text(json.dumps(cfg, indent=2) + "\n")
    return str(path)


def redact(obj):
    """copy ของข้อความที่ตัด base64 ของภาพออก → "<N bytes image/png>" """
    if isinstance(obj, dict):
        if obj.get("type") == "image" and isinstance(obj.get("data"), str):
            n = len(base64.b64decode(obj["data"]))
            return {**obj, "data": f"<{n} bytes {obj.get('mimeType', '?')}>"}
        return {k: redact(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact(v) for v in obj]
    return obj


class MCP:
    def __init__(self, config, all_log, cwd=None):
        env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH=BROWSERS)
        self.cmd = [SERVER, "--config", config]
        self.proc = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=open(str(all_log) + ".stderr", "a"), env=env, cwd=cwd, bufsize=0)
        self.t0 = time.time()
        self._id = 0
        self._q = queue.Queue()
        self._all = open(all_log, "a", encoding="utf-8")
        self._step = None
        self.label = "setup"
        threading.Thread(target=self._reader, daemon=True).start()

    # ---------- บันทึก ----------
    def set_step_log(self, path, label):
        if self._step:
            self._step.close()
        self._step = open(path, "a", encoding="utf-8") if path else None
        self.label = label

    def _log(self, direction, msg, nbytes, extra=None):
        rec = {"t": round(time.time() - self.t0, 3), "step": self.label, "dir": direction, "bytes": nbytes}
        rec.update(extra or {})
        rec["msg"] = redact(msg)
        line = json.dumps(rec, ensure_ascii=False) + "\n"
        for f in (self._all, self._step):
            if f:
                f.write(line); f.flush()

    # ---------- transport ----------
    def _reader(self):
        for raw in self.proc.stdout:
            raw = raw.strip()
            if raw:
                self._q.put((json.loads(raw), len(raw)))
        self._q.put((None, 0))

    def _send(self, msg):
        data = (json.dumps(msg, ensure_ascii=False) + "\n").encode()
        self._log("send", msg, len(data))
        self.proc.stdin.write(data)
        self.proc.stdin.flush()

    def request(self, method, params=None, timeout=120):
        self._id += 1
        rid, t = self._id, time.time()
        self._send({"jsonrpc": "2.0", "id": rid, "method": method, **({"params": params} if params is not None else {})})
        while True:
            msg, n = self._q.get(timeout=timeout)
            if msg is None:
                raise EOFError("MCP server ปิด stdout")
            if "method" in msg and "id" in msg:          # server ขอ client (เฟส 1 ไม่เคยเจอ)
                self._log("recv", msg, n)
                self._send({"jsonrpc": "2.0", "id": msg["id"], "result": {"roots": []} if msg["method"] == "roots/list" else {}})
                continue
            if "id" not in msg:                           # notification เช่น notifications/tools/list_changed
                self._log("recv", msg, n)
                continue
            secs = round(time.time() - t, 3)
            self._log("recv", msg, n, {"elapsed_s": secs})
            if msg["id"] == rid:
                return msg, n, secs

    def initialize(self):
        r, _, _ = self.request("initialize", {"protocolVersion": PROTOCOL_VERSION, "capabilities": {},
                                              "clientInfo": {"name": "cic-agent", "version": "1.0"}})
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        tools, _, _ = self.request("tools/list", {})
        self.tools = [t["name"] for t in tools["result"]["tools"]]
        return r["result"]

    def call(self, tool, args=None, timeout=120):
        """tools/call → {"text", "images" (list ของ bytes), "is_error", "seconds", "bytes"}"""
        msg, n, secs = self.request("tools/call", {"name": tool, "arguments": args or {}}, timeout)
        if "error" in msg:                                # JSON-RPC error (method ผิด ฯลฯ)
            return {"text": json.dumps(msg["error"]), "images": [], "is_error": True, "seconds": secs, "bytes": n}
        res = msg["result"]
        return {"text": "\n".join(c["text"] for c in res.get("content", []) if c.get("type") == "text"),
                "images": [base64.b64decode(c["data"]) for c in res.get("content", []) if c.get("type") == "image"],
                "is_error": bool(res.get("isError")), "seconds": secs, "bytes": n}

    def close(self):
        """ปิด stdin → server จบเอง และปิดเบราว์เซอร์ตาม (เฟส 1: exit 0, chromium เหลือ 0)"""
        self.set_step_log(None, "close")
        try:
            self.proc.stdin.close()
            self.proc.wait(timeout=15)
        except Exception:
            self.proc.kill(); self.proc.wait()
        self._log("exit", {"returncode": self.proc.returncode}, 0)
        self._all.close()
        return self.proc.returncode


def section(text, name):
    """ดึงเนื้อหาส่วน '### <name>' จากข้อความ response"""
    parts = {}
    for chunk in ("\n" + text).split("\n### ")[1:]:
        head, _, body = chunk.partition("\n")
        parts[head.strip()] = body.strip()
    return parts.get(name, "")


def snapshot_yaml(text):
    """ข้อความ browser_snapshot → YAML ใน ```yaml ... ``` """
    body = section(text, "Snapshot")
    if body.startswith("```yaml"):
        body = body[len("```yaml"):]
    return body.rsplit("```", 1)[0].strip("\n") + "\n"


def page_url(text):
    for line in section(text, "Page").splitlines():
        if line.startswith("- Page URL: "):
            return line[len("- Page URL: "):].strip()
    return ""


if __name__ == "__main__":
    # ทดสอบเร็ว: python3 mcp_client.py → handshake + navigate example.com + snapshot
    import sys, tempfile
    d = Path(tempfile.mkdtemp())
    m = MCP(write_config(d / "cfg.json", d / "out"), d / "rpc_all.jsonl")
    print(m.initialize()["serverInfo"], len(m.tools), "tools")
    print(m.call("browser_navigate", {"url": "https://example.com"})["text"][:300])
    s = m.call("browser_snapshot", {"boxes": True})
    print(page_url(s["text"]), snapshot_yaml(s["text"])[:300])
    print("exit", m.close(), d, file=sys.stderr)
