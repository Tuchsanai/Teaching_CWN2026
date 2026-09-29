#!/usr/bin/env python3
"""ทดสอบ MCP server จาก shared mcp.json ผ่าน stdio จริง (ไม่ต้องล็อกอิน ไม่ผ่าน AI)

    initialize → notifications/initialized → tools/list → browser_navigate
    → browser_take_screenshot → browser_close

ใช้: python3 mcp_stdio_probe.py --config ~/ai-accounts/.Codex/shared/mcp/mcp.json \
        --screenshot /tmp/shot.png --transcript /tmp/transcript.jsonl
ผลสรุปพิมพ์เป็น JSON; transcript เก็บทุกข้อความ JSON-RPC (ตัด base64 ของรูปออก)
"""
import argparse, base64, json, os, queue, subprocess, sys, threading, time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--server", default="playwright")
    ap.add_argument("--url", default="https://example.com")
    ap.add_argument("--screenshot", required=True, help="absolute path ของไฟล์ png")
    ap.add_argument("--transcript", default="")
    ap.add_argument("--timeout", type=float, default=120)
    a = ap.parse_args()

    cfg = json.load(open(a.config, encoding="utf-8"))["mcpServers"][a.server]
    argv = [cfg["command"], *cfg.get("args", [])]
    env = dict(os.environ, **cfg.get("env", {}))
    tr = open(a.transcript, "w") if a.transcript else None

    def rec(direction, msg):
        if not tr:
            return
        m = json.loads(json.dumps(msg))
        for c in (m.get("result") or {}).get("content", []) if isinstance(m.get("result"), dict) else []:
            if c.get("type") == "image" and "data" in c:
                c["data"] = f"<base64 {len(c['data'])} chars>"
        tr.write(json.dumps({"t": round(time.time(), 3), "dir": direction, "msg": m}, ensure_ascii=False) + "\n")
        tr.flush()

    if tr:
        tr.write(json.dumps({"argv": argv, "env": cfg.get("env", {})}) + "\n")
    p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=env, text=True, bufsize=1)
    q = queue.Queue()
    threading.Thread(target=lambda: [q.put(l) for l in p.stdout], daemon=True).start()
    errs = []
    threading.Thread(target=lambda: [errs.append(l) for l in p.stderr], daemon=True).start()
    ids = iter(range(1, 10**6))

    def send(msg):
        rec(">>", msg)
        p.stdin.write(json.dumps(msg) + "\n"); p.stdin.flush()

    def call(method, params):
        i = next(ids)
        send({"jsonrpc": "2.0", "id": i, "method": method, "params": params})
        end = time.time() + a.timeout
        while time.time() < end:
            try:
                line = q.get(timeout=max(0.1, end - time.time()))
            except queue.Empty:
                break
            try:
                m = json.loads(line)
            except ValueError:
                continue
            rec("<<", m)
            if m.get("id") == i:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m["result"]
        raise TimeoutError(f"{method}: no response in {a.timeout}s")

    out = {"argv": argv}
    try:
        init = call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                   "clientInfo": {"name": "mcp_stdio_probe", "version": "1"}})
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        out["serverInfo"] = init.get("serverInfo")
        tools = [t["name"] for t in call("tools/list", {}).get("tools", [])]
        out["tools_count"] = len(tools)
        out["has_navigate"] = "browser_navigate" in tools
        nav = call("tools/call", {"name": "browser_navigate", "arguments": {"url": a.url}})
        nav_txt = "\n".join(c.get("text", "") for c in nav.get("content", []) if c.get("type") == "text")
        out["navigate_isError"] = bool(nav.get("isError"))
        out["page_title_line"] = next((l.strip() for l in nav_txt.splitlines() if "Page Title" in l), "")
        # ชื่อไฟล์ต้องเป็น absolute path (relative จะถูกบันทึกเทียบกับ cwd ของ MCP)
        shot = call("tools/call", {"name": "browser_take_screenshot",
                                   "arguments": {"filename": a.screenshot, "type": "png"}})
        out["screenshot_isError"] = bool(shot.get("isError"))
        if not os.path.exists(a.screenshot):
            for c in shot.get("content", []):
                if c.get("type") == "image":
                    open(a.screenshot, "wb").write(base64.b64decode(c["data"]))
                    out["screenshot_from"] = "inline image"
        out["screenshot_bytes"] = os.path.getsize(a.screenshot) if os.path.exists(a.screenshot) else 0
        call("tools/call", {"name": "browser_close", "arguments": {}})
        out["ok"] = (out["has_navigate"] and not out["navigate_isError"]
                     and "Example Domain" in out["page_title_line"] and out["screenshot_bytes"] > 0)
    except Exception as e:  # noqa: BLE001
        out["ok"] = False
        out["error"] = str(e)
        out["stderr_tail"] = "".join(errs[-20:])
    finally:
        p.terminate()
        try:
            p.wait(10)
        except subprocess.TimeoutExpired:
            p.kill()
    print(json.dumps(out, ensure_ascii=False, indent=2))
    sys.exit(0 if out["ok"] else 1)


if __name__ == "__main__":
    main()
