#!/usr/bin/env python3
"""MCP client แบบ stdio (JSON-RPC 2.0, 1 ข้อความ = 1 บรรทัด) — Python stdlib ล้วน
spawn /usr/bin/playwright-mcp เอง, handshake, เรียก tool, บันทึกทุกข้อความลง jsonl
ข้อมูลภาพ base64 ใน log ถูกแทนด้วย "<base64 N chars>" และบันทึกเป็นไฟล์ .png แยก"""
import base64, json, os, subprocess, sys, threading, time, queue

PROTOCOL_VERSION = "2025-06-18"


def _redact(obj, img_dir=None, tag="img"):
    """คืน copy ของข้อความที่ตัด base64 ออก (ถ้ามี img_dir จะเขียนภาพลงไฟล์)"""
    saved = []
    def walk(o):
        if isinstance(o, dict):
            if o.get("type") == "image" and isinstance(o.get("data"), str):
                raw = o["data"]
                n = dict(o)
                n["data"] = f"<base64 {len(raw)} chars>"
                if img_dir:
                    ext = {"image/png": "png", "image/jpeg": "jpg"}.get(o.get("mimeType"), "bin")
                    p = os.path.join(img_dir, f"{tag}_{len(saved)+1}.{ext}")
                    with open(p, "wb") as f:
                        f.write(base64.b64decode(raw))
                    saved.append(p)
                    n["saved_to"] = p
                return n
            return {k: walk(v) for k, v in o.items()}
        if isinstance(o, list):
            return [walk(v) for v in o]
        return o
    return walk(obj), saved


class MCPClient:
    def __init__(self, cmd, log_path, stderr_path=None, env=None, img_dir=None):
        self.log_path = log_path
        self.img_dir = img_dir
        self._id = 0
        self._log = open(log_path, "a", encoding="utf-8")
        self._stderr = open(stderr_path or (log_path + ".stderr"), "a")
        self.t0 = time.time()
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=self._stderr, env=env, bufsize=0)
        self._q = queue.Queue()
        self.notifications = []
        threading.Thread(target=self._reader, daemon=True).start()
        self.log("spawn", {"cmd": cmd, "pid": self.proc.pid})

    # ---------- log ----------
    def log(self, direction, msg, raw_len=None, extra=None):
        red, saved = _redact(msg, self.img_dir if direction == "recv" else None,
                             tag=f"rpc{msg.get('id', 'x') if isinstance(msg, dict) else 'x'}")
        rec = {"t": round(time.time() - self.t0, 3), "dir": direction}
        if raw_len is not None:
            rec["bytes"] = raw_len
        if extra:
            rec.update(extra)
        rec["msg"] = red
        self._log.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self._log.flush()
        return saved

    # ---------- transport ----------
    def _reader(self):
        for line in self.proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except Exception:
                self.log("recv-nonjson", {"raw": line[:500].decode("utf-8", "replace")})
                continue
            self._q.put((msg, len(line)))
        self._q.put((None, 0))

    def _send(self, msg):
        data = (json.dumps(msg, ensure_ascii=False) + "\n").encode()
        self.log("send", msg, raw_len=len(data))
        self.proc.stdin.write(data)
        self.proc.stdin.flush()

    def request(self, method, params=None, timeout=120):
        self._id += 1
        rid = self._id
        msg = {"jsonrpc": "2.0", "id": rid, "method": method}
        if params is not None:
            msg["params"] = params
        t = time.time()
        self._send(msg)
        while True:
            try:
                resp, n = self._q.get(timeout=timeout)
            except queue.Empty:
                raise TimeoutError(f"{method} timeout {timeout}s")
            if resp is None:
                raise EOFError("server closed stdout")
            if "id" in resp and "method" in resp:          # server -> client request
                self.log("recv", resp, raw_len=n)
                self._answer_server_request(resp)
                continue
            if "id" not in resp:                            # notification
                self.log("recv", resp, raw_len=n)
                self.notifications.append(resp)
                continue
            if resp["id"] != rid:
                self.log("recv-unexpected", resp, raw_len=n)
                continue
            dt = round(time.time() - t, 3)
            saved = self.log("recv", resp, raw_len=n, extra={"elapsed_s": dt})
            resp["_bytes"], resp["_elapsed"], resp["_saved"] = n, dt, saved
            return resp

    def notify(self, method, params=None):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        self._send(msg)

    def _answer_server_request(self, req):
        if req["method"] == "roots/list":
            out = {"jsonrpc": "2.0", "id": req["id"], "result": {"roots": []}}
        elif req["method"] == "ping":
            out = {"jsonrpc": "2.0", "id": req["id"], "result": {}}
        else:
            out = {"jsonrpc": "2.0", "id": req["id"],
                   "error": {"code": -32601, "message": "Method not found"}}
        self._send(out)

    # ---------- MCP ----------
    def initialize(self, name="probe-client", version="0.1"):
        r = self.request("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": name, "version": version}})
        self.notify("notifications/initialized")
        return r

    def list_tools(self):
        return self.request("tools/list", {})

    def call(self, name, args=None, timeout=120):
        return self.request("tools/call", {"name": name, "arguments": args or {}}, timeout=timeout)

    @staticmethod
    def text(resp):
        res = resp.get("result") or {}
        return "\n".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")

    def close(self):
        try:
            self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        self.log("exit", {"returncode": self.proc.returncode})
        self._log.close()
        return self.proc.returncode


if __name__ == "__main__":
    # ทดสอบเร็ว: python3 mcp_client.py <log.jsonl> [args ของ playwright-mcp ...]
    c = MCPClient(["/usr/bin/playwright-mcp"] + sys.argv[2:], sys.argv[1])
    print(json.dumps(c.initialize()["result"], indent=1))
    print([t["name"] for t in c.list_tools()["result"]["tools"]])
    print("exit", c.close())
