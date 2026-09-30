import base64, json, os, queue, subprocess, threading


class MCP:
    def __init__(self, log_path):
        env = dict(os.environ, PLAYWRIGHT_BROWSERS_PATH="/ms-playwright")
        self.proc = subprocess.Popen(
            ["/usr/bin/playwright-mcp", "--config", "/workspace/mcp.config.json"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=env)
        self.log = open(log_path, "w")
        self.lock = threading.Lock()
        self.pending = {}
        self.next_id = 1
        self.protocol_version = None
        threading.Thread(target=self._reader, daemon=True).start()

    def _record(self, direction, msg):
        def scrub(o):
            if isinstance(o, dict):
                if o.get("type") == "image" and isinstance(o.get("data"), str):
                    n = len(base64.b64decode(o["data"]))
                    return {**{k: scrub(v) for k, v in o.items() if k != "data"},
                            "data": f"<{n} bytes {o.get('mimeType', 'image/png')}>"}
                return {k: scrub(v) for k, v in o.items()}
            if isinstance(o, list):
                return [scrub(v) for v in o]
            return o
        with self.lock:
            self.log.write(json.dumps({"dir": direction, "msg": scrub(msg)}, ensure_ascii=False) + "\n")
            self.log.flush()

    def _reader(self):
        for line in self.proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except ValueError:
                continue
            self._record("recv", msg)
            mid = msg.get("id")
            if mid is None or "method" in msg:  # notification / server request
                continue
            q = self.pending.get(mid)
            if q:
                q.put(msg)

    def _send(self, msg):
        self._record("send", msg)
        self.proc.stdin.write((json.dumps(msg) + "\n").encode())
        self.proc.stdin.flush()

    def _request(self, method, params=None, timeout=120):
        with self.lock:
            rid = self.next_id
            self.next_id += 1
        q = self.pending[rid] = queue.Queue()
        msg = {"jsonrpc": "2.0", "id": rid, "method": method}
        if params is not None:
            msg["params"] = params
        self._send(msg)
        try:
            return q.get(timeout=timeout)
        finally:
            del self.pending[rid]

    def initialize(self):
        r = self._request("initialize", {
            "protocolVersion": "2025-06-18", "capabilities": {},
            "clientInfo": {"name": "lab1-client", "version": "0.1"}})
        res = r["result"]
        self.protocol_version = res.get("protocolVersion")
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        tools = self._request("tools/list", {})["result"]["tools"]
        return res.get("serverInfo"), [t["name"] for t in tools]

    def call(self, tool, args=None):
        r = self._request("tools/call", {"name": tool, "arguments": args or {}})
        if "error" in r:
            return {"text": r["error"].get("message", ""), "images": [], "is_error": True}
        res = r["result"]
        content = res.get("content", [])
        return {
            "text": "\n".join(c["text"] for c in content if c.get("type") == "text"),
            "images": [base64.b64decode(c["data"]) for c in content if c.get("type") == "image"],
            "is_error": bool(res.get("isError")),
        }

    def close(self):
        try:
            self.proc.stdin.close()
        except OSError:
            pass
        try:
            code = self.proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            code = self.proc.wait()
        self.log.close()
        return code
