"""
wire_capture.py — "ตัวดักฟัง" ข้อความ JSON-RPC บนสาย stdio
========================================================
วางตัวเองคั่นระหว่าง MCP client (เช่น Claude Code หรือ client_test.py) กับ MCP server จริง
ส่งต่อทุกบรรทัดโดยไม่แก้ไข และบันทึกสำเนาลงไฟล์ jsonl เพื่อให้นักศึกษาเห็นว่า
"บนสายจริง ๆ มีข้อความอะไรวิ่งไปมา"

วิธีใช้:
    python wire_capture.py --log wire.jsonl -- /opt/venv/bin/python hello_server.py

รูปแบบแต่ละบรรทัดใน log:
    {"ts": "...Z", "dir": "client->server" | "server->client", "msg": {...json-rpc...}}
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
import time


def _ts() -> str:
    now = time.time()
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(now)) + f".{int((now % 1) * 1000):03d}Z"


def main() -> int:
    ap = argparse.ArgumentParser(description="stdio proxy that logs every JSON-RPC line")
    ap.add_argument("--log", required=True, help="jsonl file to append to")
    ap.add_argument("cmd", nargs=argparse.REMAINDER, help="-- real server command")
    args = ap.parse_args()
    cmd = args.cmd[1:] if args.cmd and args.cmd[0] == "--" else args.cmd
    if not cmd:
        ap.error("missing server command after --")

    logf = open(args.log, "a", encoding="utf-8", buffering=1)
    lock = threading.Lock()

    def log(direction: str, raw: bytes) -> None:
        line = raw.decode("utf-8", "replace").rstrip("\r\n")
        if not line:
            return
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            msg = line
        with lock:
            logf.write(json.dumps({"ts": _ts(), "dir": direction, "msg": msg}, ensure_ascii=False) + "\n")

    # stderr ของ server ปล่อยผ่านไปยัง stderr ของเรา (host จะเห็น log ของ server ตามปกติ)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, bufsize=0)
    assert proc.stdin and proc.stdout

    def pump_in() -> None:  # client (stdin ของเรา) → server
        try:
            for raw in iter(sys.stdin.buffer.readline, b""):
                log("client->server", raw)
                proc.stdin.write(raw)
                proc.stdin.flush()
        except (BrokenPipeError, ValueError):
            pass
        finally:
            try:
                proc.stdin.close()
            except Exception:
                pass

    def pump_out() -> None:  # server → client (stdout ของเรา)
        out = sys.stdout.buffer
        try:
            for raw in iter(proc.stdout.readline, b""):
                log("server->client", raw)
                out.write(raw)
                out.flush()
        except (BrokenPipeError, ValueError):
            pass

    t_in = threading.Thread(target=pump_in, daemon=True)
    t_out = threading.Thread(target=pump_out, daemon=True)
    t_in.start()
    t_out.start()
    t_out.join()
    rc = proc.wait()
    logf.close()
    return rc


if __name__ == "__main__":
    sys.exit(main())
