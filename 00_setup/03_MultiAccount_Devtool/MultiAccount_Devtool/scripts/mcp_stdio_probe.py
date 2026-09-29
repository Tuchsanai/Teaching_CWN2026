#!/usr/bin/env python3
"""เปิด MCP server จาก shared mcp.json ผ่าน stdio จริง แล้วคุย JSON-RPC โดยไม่ผ่าน AI

    initialize → notifications/initialized → tools/list → tools/call browser_navigate
    → tools/call browser_take_screenshot → tools/call browser_close

พิมพ์ผลเป็น JSON หนึ่งก้อน (ไม่มี secret) — ai-accounts-check อ่านผลนี้
"""
import argparse
import json
import os
import queue
import subprocess
import sys
import threading
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--server", default="playwright")
    ap.add_argument("--url", default="https://example.com/")
    ap.add_argument("--screenshot", default="")
    ap.add_argument("--timeout", type=float, default=90)
    a = ap.parse_args()

    out = {"server": a.server, "config": a.config, "url": a.url}
    with open(a.config, encoding="utf-8") as f:
        cfg = json.load(f)["mcpServers"][a.server]
    env = dict(os.environ, **cfg.get("env", {}))
    p = subprocess.Popen([cfg["command"], *cfg.get("args", [])], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True, bufsize=1)
    q = queue.Queue()
    threading.Thread(target=lambda: [q.put(l) for l in p.stdout], daemon=True).start()
    err_tail = []
    threading.Thread(target=lambda: [err_tail.append(l) for l in p.stderr], daemon=True).start()
    ids = iter(range(1, 1000))

    def send(msg):
        p.stdin.write(json.dumps(msg) + "\n")
        p.stdin.flush()

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
            if m.get("id") == i:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m["result"]
        raise TimeoutError(f"{method}: no response in {a.timeout}s")

    def text_of(res):
        return "\n".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")

    try:
        init = call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                   "clientInfo": {"name": "ai-accounts-check", "version": "1"}})
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        out["initialize"] = {"ok": True, "serverInfo": init.get("serverInfo"),
                             "protocolVersion": init.get("protocolVersion")}
        tools = [t["name"] for t in call("tools/list", {}).get("tools", [])]
        out["tools_list"] = {"ok": "browser_navigate" in tools, "count": len(tools),
                             "has": [t for t in ("browser_navigate", "browser_take_screenshot",
                                                 "browser_snapshot") if t in tools]}
        nav = call("tools/call", {"name": "browser_navigate", "arguments": {"url": a.url}})
        txt = text_of(nav)
        title = next((l.split(":", 1)[1].strip() for l in txt.splitlines()
                      if "Page Title" in l or l.strip().lower().startswith("- page title")), "")
        out["browser_navigate"] = {"ok": not nav.get("isError") and bool(txt), "title": title,
                                   "isError": bool(nav.get("isError")),
                                   "excerpt": txt[:300] if nav.get("isError") else ""}
        if a.screenshot:
            shot = call("tools/call", {"name": "browser_take_screenshot",
                                       "arguments": {"filename": a.screenshot, "type": "png"}})
            st = text_of(shot)
            path = next((w.strip("`()[]'\",") for w in st.split() if w.strip("`()[]'\",").endswith(".png")), "")
            out["browser_take_screenshot"] = {"ok": not shot.get("isError"), "reported": path}
        try:
            call("tools/call", {"name": "browser_close", "arguments": {}})
        except Exception:  # noqa: BLE001
            pass
        out["ok"] = out["tools_list"]["ok"] and out["browser_navigate"]["ok"]
    except Exception as e:  # noqa: BLE001
        out["ok"] = False
        out["error"] = str(e)
        out["stderr_tail"] = "".join(err_tail[-5:])[-500:]
    finally:
        try:
            p.stdin.close()
            p.terminate()
            p.wait(timeout=10)
        except Exception:  # noqa: BLE001
            p.kill()
    print(json.dumps(out, ensure_ascii=False))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
