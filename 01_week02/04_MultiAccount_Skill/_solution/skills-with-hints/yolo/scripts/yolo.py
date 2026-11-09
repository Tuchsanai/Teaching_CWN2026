#!/usr/bin/env python3
"""ควบคุม Claude Code ทุกบัญชี (yoloN): ถามงานเดียว ตรวจความพร้อมจริง โควตา สถิติ

ไม่อ่าน .credentials.json / .claude.json และไม่พิมพ์อีเมลหรือ orgId
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import ma_ledger as L  # noqa: E402

BASE = os.environ.get("MA_BASE", "/root/ai-accounts")
ROOT = os.path.join(BASE, ".Claude")
MODELS = ["opus", "sonnet", "haiku", "fable"]
EFFORTS = ["low", "medium", "high", "xhigh", "max"]
DIFFICULTY = {1: ("haiku", "low"), 2: ("sonnet", "medium"), 3: ("opus", "high"),
              4: ("opus", "xhigh"), 5: ("opus", "max"), 6: ("opus", "max")}
MAX_PROMPT = 100000
PROBE = "ตอบ OK"


def accounts():
    if not os.path.isdir(ROOT):
        return []
    names = [d for d in os.listdir(ROOT) if re.fullmatch(r"yolo\d+", d)]
    return sorted(names, key=lambda n: int(n[4:]))


def invocation(account):
    """คืน (argv นำหน้า, env) ใช้ wrapper ถ้ามี ไม่มีเรียก claude ตรงด้วย env ชุดเดียวกัน"""
    env = os.environ.copy()
    if shutil.which(account):
        return [account], env
    env["CLAUDE_CONFIG_DIR"] = os.path.join(ROOT, account)
    env["IS_SANDBOX"] = "1"
    argv = ["claude", "--dangerously-skip-permissions"]
    mcp = os.path.join(ROOT, "shared", "mcp", "mcp.json")
    if os.path.isfile(mcp):
        argv.append("--mcp-config=" + mcp)
    return argv, env


def classify(text):
    t = (text or "").lower()
    if "not logged in" in t or "please run /login" in t:
        return "not_logged_in"
    if "oauth session expired" in t or "could not be refreshed" in t or "failed to authenticate" in t:
        return "auth_expired"
    if "rate limit" in t or "429" in t or "overloaded" in t:
        return "rate_limit"
    if "usage limit" in t or "limit reached" in t or "hit your" in t or "quota" in t:
        return "quota"
    return "error"


def simulated(account):
    return account in [a.strip() for a in os.environ.get("MA_SIMULATE_LIMIT", "").split(",")]


def _row(account, model, effort, prompt, run_id, node):
    return {"ts_start": L.now_iso(), "run_id": run_id, "node": node, "account": account,
            "cli": "claude", "model": model, "effort": effort, "prompt_chars": len(prompt)}


def call(account, prompt, model="haiku", effort="low", timeout=600, cwd=None, schema=None,
         run_id="", node="", run_ledger=None, extra=None, probe=False):
    """เรียกงานเดียว คืน dict: ok, status, result, error, และตัวเลขสถิติ"""
    row = _row(account, model, effort, prompt, run_id, node)
    started = time.time()
    res = {"ok": False, "status": "error", "result": "", "error": "", "account": account,
           "model": model, "effort": effort, "structured": None}

    def finish():
        row.update(status=res["status"], error=res["error"][:200], result_chars=len(res["result"]),
                   ts_end=L.now_iso(), duration_s=round(time.time() - started, 2))
        res.update(ledger=L.record(row, run_ledger))
        return res

    if not probe and simulated(account):
        res.update(status="quota", error="simulated: usage limit reached (MA_SIMULATE_LIMIT)")
        return finish()
    if len(prompt) > MAX_PROMPT:
        res.update(error="prompt ยาวเกิน %d ตัวอักษร ให้ส่งเป็น path ไฟล์แทน" % MAX_PROMPT)
        return finish()
    # prompt ต้องอยู่ก่อน flag ที่รับหลายค่า และห้ามขึ้นต้นด้วย - (จะถูกอ่านเป็น option)
    text = " " + prompt if prompt.startswith("-") else prompt
    prefix, env = invocation(account)
    argv = prefix + ["-p", text, "--model", model, "--effort", effort, "--output-format", "json",
                     "--no-session-persistence", "--strict-mcp-config"]
    if schema:
        argv += ["--json-schema", json.dumps(schema) if not isinstance(schema, str) else schema]
    if extra:
        argv += list(extra)
    try:
        p = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           timeout=timeout, env=env, cwd=cwd)
    except subprocess.TimeoutExpired:
        res.update(status="timeout", error="timeout %ss" % timeout)
        return finish()
    except OSError as e:
        res.update(error=str(e))
        return finish()
    try:
        j = json.loads(p.stdout)
    except ValueError:
        res.update(status=classify(p.stdout + p.stderr), error=(p.stderr or p.stdout).strip()[:200] or "exit %d" % p.returncode)
        return finish()
    u = j.get("usage") or {}
    row.update(input_tokens=u.get("input_tokens", 0) or 0,
               cached_input_tokens=u.get("cache_read_input_tokens", 0) or 0,
               cache_write_tokens=u.get("cache_creation_input_tokens", 0) or 0,
               output_tokens=u.get("output_tokens", 0) or 0,
               reasoning_tokens=(u.get("output_tokens_details") or {}).get("thinking_tokens", 0) or 0,
               cost_usd=j.get("total_cost_usd"))
    used = list((j.get("modelUsage") or {}).keys())
    if used:
        res["real_model"] = used[0]
    text = j.get("result") if isinstance(j.get("result"), str) else ""
    res["structured"] = j.get("structured_output")
    if res["structured"] is not None and not text:
        text = json.dumps(res["structured"], ensure_ascii=False)
    if j.get("is_error"):  # exit 0 ไม่ได้แปลว่าสำเร็จ ต้องดู is_error
        res.update(status=classify(text), error=text.strip()[:200] or "is_error", result=text)
        return finish()
    if not text.strip():
        res.update(status="error", error="ผลลัพธ์ว่าง")
        return finish()
    res.update(ok=True, status="ok", result=text)
    return finish()


STATE = {"ok": "พร้อม", "auth_expired": "ล็อกอินแล้วแต่หมดอายุ", "not_logged_in": "ไม่ได้ล็อกอิน",
         "quota": "โควตาหมด", "rate_limit": "ถูกจำกัดอัตรา", "timeout": "หมดเวลา", "error": "ผิดพลาด"}


def check(account, run_id="", run_ledger=None):
    """ตรวจด้วยการเรียกจริงงานสั้นที่สุด (haiku/low) `auth status` เชื่อไม่ได้"""
    r = call(account, PROBE, "haiku", "low", timeout=120, run_id=run_id, node="__check__",
             run_ledger=run_ledger, probe=True)
    return {"account": account, "cli": "claude", "ready": r["ok"], "status": r["status"],
            "state": STATE.get(r["status"], r["status"]),
            "detail": r["error"] if not r["ok"] else "",
            "duration_s": r["ledger"]["duration_s"]}


USAGE_LINE = re.compile(r"^(Current [^:]+):\s*(\d+(?:\.\d+)?)%\s*used\s*·\s*resets\s*(.+)$", re.M)


def quota(account, run_id="", run_ledger=None):
    """อ่าน /usage (คำสั่งในตัว ไม่เรียกโมเดล) รายงานเฉพาะข้อมูลจริง ไม่เดา"""
    row = _row(account, "/usage", "-", "/usage", run_id, "__quota__")
    started = time.time()
    out = {"account": account, "cli": "claude", "has_data": False, "used_pct": None, "text": "ไม่มีข้อมูล",
           "ts": L.now_iso(), "windows": []}
    prefix, env = invocation(account)
    argv = prefix + ["-p", "/usage", "--output-format", "json", "--no-session-persistence",
                     "--strict-mcp-config"]
    status, err = "ok", ""
    try:
        p = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           timeout=60, env=env)
        text = json.loads(p.stdout).get("result") or ""
    except (subprocess.TimeoutExpired, OSError, ValueError) as e:
        text, status, err = "", "error", str(e)[:200]
    found = USAGE_LINE.findall(text)
    if found:
        windows = [{"name": n, "used_pct": float(v), "resets": r.strip()} for n, v, r in found]
        out["windows"] = windows
        out["has_data"] = True
        main = [w["used_pct"] for w in windows if "Fable" not in w["name"]]  # เพดานเฉพาะรุ่นไม่นับ
        out["used_pct"] = max(main) if main else None
        short = {"Current session": "session", "Current week (all models)": "week"}
        out["text"] = " · ".join("%s %g%%" % (short.get(w["name"], w["name"].replace("Current ", "")),
                                              w["used_pct"]) for w in windows)
    row.update(status=status, error=err, ts_end=L.now_iso(), duration_s=round(time.time() - started, 2))
    L.record(row, run_ledger)
    return out


def parallel(fn, items):
    items = list(items)
    if not items:
        return []
    with ThreadPoolExecutor(max_workers=min(10, len(items))) as ex:
        return list(ex.map(fn, items))


def main():
    ap = argparse.ArgumentParser(description="คุม Claude Code หลายบัญชี (yoloN)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("ask", help="เรียกงานเดียว")
    a.add_argument("account")
    a.add_argument("prompt")
    a.add_argument("--model", choices=MODELS)
    a.add_argument("--effort", choices=EFFORTS)
    a.add_argument("--difficulty", type=int, choices=list(DIFFICULTY), help="1–6 เลือกรุ่นและ effort ตามตาราง")
    a.add_argument("--timeout", type=int, default=600)
    a.add_argument("--cwd")
    a.add_argument("--json-schema", help="schema เป็น JSON string")
    a.add_argument("--json", action="store_true", help="พิมพ์ผลเต็มเป็น JSON")
    for name, helptext in (("check", "ตรวจความพร้อมด้วยการเรียกจริง"), ("quota", "โควตาจาก /usage")):
        s = sub.add_parser(name, help=helptext)
        s.add_argument("accounts", nargs="*", help="เว้นว่าง = ทุกบัญชี")
        s.add_argument("--json", action="store_true")
    s = sub.add_parser("stats", help="สถิติจาก ledger")
    s.add_argument("--run")
    s.add_argument("--json", action="store_true")
    sub.add_parser("models", help="รุ่น effort และตารางความยาก")
    args = ap.parse_args()

    if args.cmd == "models":
        print(L.table(["difficulty", "model", "effort"],
                      [[d, m, e] for d, (m, e) in DIFFICULTY.items()]))
        print("\nalias: %s · effort: %s" % (" ".join(MODELS), " ".join(EFFORTS)))
        return 0
    if args.cmd == "stats":
        return L.stats_cli(args.run, args.json, "claude")
    if args.cmd in ("check", "quota"):
        names = args.accounts or accounts()
        rows = parallel(check if args.cmd == "check" else quota, names)
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=1))
        elif args.cmd == "check":
            print(L.table(["บัญชี", "สถานะ", "เวลา s", "รายละเอียด"],
                          [[r["account"], r["state"], r["duration_s"], r["detail"]] for r in rows]))
        else:
            print(L.table(["บัญชี", "โควตาที่ใช้ไป", "เวลาของข้อมูล"],
                          [[r["account"], r["text"], r["ts"]] for r in rows]))
        return 0
    model, effort = DIFFICULTY[args.difficulty] if args.difficulty else ("haiku", "low")
    model, effort = args.model or model, args.effort or effort
    r = call(args.account, args.prompt, model, effort, args.timeout, args.cwd, args.json_schema)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        print(r["result"] if r["ok"] else "ล้ม [%s]: %s" % (r["status"], r["error"]))
        d = r["ledger"]
        print("[%s %s/%s %ss in=%d cached=%d out=%d $%s]" % (args.account, model, effort, d["duration_s"],
              d["input_tokens"], d["cached_input_tokens"], d["output_tokens"], d["cost_usd"]), file=sys.stderr)
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
