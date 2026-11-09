#!/usr/bin/env python3
"""ควบคุม Codex CLI ทุกบัญชี (cyoloN): ถามงานเดียว เลือกรุ่น/effort สร้างภาพ ตรวจล็อกอิน โควตา สถิติ

ไม่อ่าน auth.json · จาก models_cache.json อ่านเฉพาะ slug/effort/default/visibility
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import ma_ledger as L  # noqa: E402

BASE = os.environ.get("MA_BASE", "/root/ai-accounts")
ROOT = os.path.join(BASE, ".Codex")
EFFORTS = ["low", "medium", "high", "xhigh", "max", "ultra"]
DIFFICULTY = {1: "low", 2: "medium", 3: "high", 4: "xhigh", 5: "max", 6: "ultra"}
PREFERRED = "gpt-6.1-sol"
MAX_PROMPT = 100000
PROBE = "ตอบ OK"
PNG = b"\x89PNG\r\n\x1a\n"


def accounts():
    if not os.path.isdir(ROOT):
        return []
    names = [d for d in os.listdir(ROOT) if re.fullmatch(r"cyolo\d+", d)]
    return sorted(names, key=lambda n: int(n[5:]))


def home(account):
    return os.path.join(ROOT, account)


def invocation(account):
    env = os.environ.copy()
    if shutil.which(account):
        return [account], env
    env["CODEX_HOME"] = home(account)
    return ["codex", "--dangerously-bypass-approvals-and-sandbox",
            "-c", 'cli_auth_credentials_store="file"'], env


def models(account=None):
    """อ่านเฉพาะฟิลด์ที่ต้องใช้ ไม่พิมพ์ส่วน identity"""
    names = [account] if account else accounts()
    for name in names:
        path = os.path.join(home(name), "models_cache.json")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return [{"slug": m.get("slug"),
                     "efforts": [e.get("effort") for e in m.get("supported_reasoning_levels", [])],
                     "default": m.get("default_reasoning_level"),
                     "visibility": m.get("visibility")} for m in data.get("models", [])]
    return []


def default_model(account=None):
    ms = [m["slug"] for m in models(account) if m["visibility"] == "list"]
    if PREFERRED in ms or not ms:
        return PREFERRED
    return ms[0]


def cheapest_model(account=None):
    ms = [m["slug"] for m in models(account) if m["visibility"] == "list"]
    luna = [s for s in ms if "luna" in s]
    return luna[0] if luna else default_model(account)


def resolve_effort(model, effort, account=None):
    """ลดเป็นระดับสูงสุดที่รุ่นรองรับ คืน (effort ที่ใช้, effort เดิมถ้าถูกลด ไม่งั้น None)"""
    info = [m for m in models(account) if m["slug"] == model]
    supported = info[0]["efforts"] if info else []
    if not supported or effort in supported:
        return effort, None
    rank = EFFORTS.index(effort) if effort in EFFORTS else len(EFFORTS) - 1
    lower = [e for e in supported if e in EFFORTS and EFFORTS.index(e) <= rank]
    use = max(lower, key=EFFORTS.index) if lower else supported[-1]
    return use, effort


def classify(text):
    t = (text or "").lower()
    if "usage limit" in t or "limit reached" in t or "quota" in t:
        return "quota"
    if "429" in t or "rate limit" in t or "rate_limit" in t or "too many requests" in t:
        return "rate_limit"
    if "401" in t or "unauthorized" in t or "not logged in" in t or "authentication" in t or "refresh token" in t:
        return "auth_expired"
    return "error"


def simulated(account):
    return account in [a.strip() for a in os.environ.get("MA_SIMULATE_LIMIT", "").split(",")]


def _usage_row(account, model, effort, prompt, run_id, node, effort_from):
    return {"ts_start": L.now_iso(), "run_id": run_id, "node": node, "account": account, "cli": "codex",
            "model": model, "effort": effort, "prompt_chars": len(prompt), "effort_from": effort_from}


def call(account, prompt, model=None, effort="low", timeout=600, cwd=None, schema=None, run_id="", node="",
         run_ledger=None, ephemeral=True, probe=False):
    """เรียกงานเดียว คืน dict: ok, status, result, error, และตัวเลขสถิติ"""
    model = model or default_model(account)
    use, reduced = resolve_effort(model, effort, account)
    row = _usage_row(account, model, use, prompt, run_id, node, reduced)
    started = time.time()
    res = {"ok": False, "status": "error", "result": "", "error": "", "account": account, "model": model,
           "effort": use, "effort_from": reduced, "structured": None}

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
    tmp = tempfile.mkdtemp(prefix="cyolo-")
    answer = os.path.join(tmp, "answer.txt")
    prefix, env = invocation(account)
    argv = prefix + ["exec", "--skip-git-repo-check"] + (["--ephemeral"] if ephemeral else []) + \
        ["-m", model, "-c", "model_reasoning_effort=" + use, "--json", "-o", answer]
    if schema:
        path = os.path.join(tmp, "schema.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(schema if isinstance(schema, str) else json.dumps(schema))
        argv += ["--output-schema", path]
    argv.append(" " + prompt if prompt.startswith("-") else prompt)
    try:
        p = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           timeout=timeout, env=env, cwd=cwd)
    except subprocess.TimeoutExpired:
        res.update(status="timeout", error="timeout %ss" % timeout)
        shutil.rmtree(tmp, ignore_errors=True)
        return finish()
    except OSError as e:
        res.update(error=str(e))
        shutil.rmtree(tmp, ignore_errors=True)
        return finish()
    completed, failed, last_err, last_msg, usage = False, None, "", "", {}
    for line in p.stdout.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        kind = ev.get("type")
        if kind == "turn.completed":
            completed, usage = True, ev.get("usage") or {}
        elif kind == "turn.failed":
            failed = (ev.get("error") or {}).get("message", "turn.failed")
        elif kind == "error":
            last_err = ev.get("message", "")
        elif kind == "item.completed" and (ev.get("item") or {}).get("type") == "agent_message":
            last_msg = ev["item"].get("text", "")
    text = ""
    if os.path.isfile(answer):
        with open(answer, encoding="utf-8", errors="replace") as f:
            text = f.read()
    shutil.rmtree(tmp, ignore_errors=True)
    text = text or last_msg
    row.update(input_tokens=usage.get("input_tokens", 0) or 0,
               cached_input_tokens=usage.get("cached_input_tokens", 0) or 0,
               cache_write_tokens=usage.get("cache_write_input_tokens", 0) or 0,
               output_tokens=usage.get("output_tokens", 0) or 0,
               reasoning_tokens=usage.get("reasoning_output_tokens", 0) or 0)
    if completed and not failed and text.strip():
        res.update(ok=True, status="ok", result=text)
        if schema:
            try:
                res["structured"] = json.loads(text)
            except ValueError:
                pass
        return finish()
    msg = failed or last_err or p.stderr.strip()[-200:] or "ไม่มีคำตอบ"
    res.update(status=classify(msg), error=msg[:200], result=text)
    return finish()


STATE = {"ok": "พร้อม", "auth_expired": "ล็อกอินแล้วแต่หมดอายุ", "not_logged_in": "ไม่ได้ล็อกอิน",
         "quota": "โควตาหมด", "rate_limit": "ถูกจำกัดอัตรา", "timeout": "หมดเวลา", "error": "ผิดพลาด"}


def login_state(account):
    """อ่านจากข้อความ ไม่ใช่ exit code"""
    prefix, env = invocation(account)
    try:
        p = subprocess.run(prefix + ["login", "status"], stdin=subprocess.DEVNULL, capture_output=True,
                           text=True, timeout=30, env=env)
    except (subprocess.TimeoutExpired, OSError):
        return "unknown"
    text = p.stdout + p.stderr
    if "Not logged in" in text:
        return "not_logged_in"
    return "logged_in" if "Logged in" in text else "unknown"


def check(account, run_id="", run_ledger=None):
    if login_state(account) == "not_logged_in":
        return {"account": account, "cli": "codex", "ready": False, "status": "not_logged_in",
                "state": STATE["not_logged_in"], "detail": "login status: Not logged in", "duration_s": 0}
    r = call(account, PROBE, default_model(account), "low", timeout=120, run_id=run_id, node="__check__",
             run_ledger=run_ledger, probe=True)
    return {"account": account, "cli": "codex", "ready": r["ok"], "status": r["status"],
            "state": STATE.get(r["status"], r["status"]),
            "detail": r["error"] if not r["ok"] else "",
            "duration_s": r["ledger"]["duration_s"]}


def _window(w, now):
    if not w:
        return None
    resets = w.get("resets_at")
    pct = float(w.get("used_percent") or 0)
    if resets and resets < now:  # รอบหมดแล้ว ตัวเลขเก่าไม่มีผล
        pct = 0.0
    return {"used_pct": pct, "window_minutes": w.get("window_minutes"), "resets_at": resets,
            "resets": datetime.fromtimestamp(resets).astimezone().isoformat(timespec="minutes") if resets else ""}


def quota(account, run_id="", run_ledger=None, refresh=False):
    """อ่าน token_count ล่าสุดจาก rollout ที่ไม่ใช่ ephemeral (--refresh เรียกสั้น 1 ครั้งให้สร้างข้อมูลใหม่)"""
    if refresh and login_state(account) != "not_logged_in":
        call(account, PROBE, cheapest_model(account), "low", timeout=120, run_id=run_id, node="__quota__",
             run_ledger=run_ledger, ephemeral=False, probe=True)
    out = {"account": account, "cli": "codex", "has_data": False, "used_pct": None, "text": "ไม่มีข้อมูล",
           "ts": "", "windows": []}
    files = sorted(glob.glob(os.path.join(home(account), "sessions", "*", "*", "*", "rollout-*.jsonl")))
    now = time.time()
    for path in reversed(files[-20:]):
        found = None
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if '"token_count"' not in line:
                    continue
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                pl = ev.get("payload") or {}
                if pl.get("type") == "token_count" and pl.get("rate_limits"):
                    found = (ev.get("timestamp", ""), pl["rate_limits"])
        if found:
            ts, rl = found
            wins = [("primary", _window(rl.get("primary"), now)), ("secondary", _window(rl.get("secondary"), now))]
            wins = [dict(w, name=n) for n, w in wins if w]
            if wins:
                out.update(has_data=True, ts=ts, windows=wins, used_pct=max(w["used_pct"] for w in wins),
                           text=" · ".join("%g%% (%sm)" % (w["used_pct"], w["window_minutes"]) for w in wins))
                break
    return out


def image(account, prompt, path, timeout=300, run_id="", node="", run_ledger=None):
    """สร้างภาพ (Codex เท่านั้น) ใช้ effort low แล้วตรวจ PNG signature"""
    if not os.path.isabs(path):
        raise ValueError("path ต้องเป็น absolute")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = "สร้างภาพ (image generation): %s\nบันทึกเป็น PNG ที่ %s\nตอบ path อย่างเดียว" % (prompt, path)
    r = call(account, text, default_model(account), "low", timeout=timeout, run_id=run_id, node=node,
             run_ledger=run_ledger)
    if r["ok"]:
        valid = os.path.isfile(path) and open(path, "rb").read(8) == PNG
        if valid:
            r["result"] = path
        else:
            r.update(ok=False, status="error", error="ไม่พบไฟล์ PNG ที่ถูกต้องที่ " + path)
    return r


def parallel(fn, items):
    items = list(items)
    if not items:
        return []
    with ThreadPoolExecutor(max_workers=min(10, len(items))) as ex:
        return list(ex.map(fn, items))


def main():
    ap = argparse.ArgumentParser(description="คุม Codex CLI หลายบัญชี (cyoloN)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("ask", help="เรียกงานเดียว")
    a.add_argument("account")
    a.add_argument("prompt")
    a.add_argument("--model")
    a.add_argument("--effort", choices=EFFORTS)
    a.add_argument("--difficulty", type=int, choices=list(DIFFICULTY), help="1–6 เลือก effort ตามตาราง")
    a.add_argument("--timeout", type=int, default=600)
    a.add_argument("--cwd")
    a.add_argument("--json", action="store_true")
    i = sub.add_parser("image", help="สร้างภาพ PNG")
    i.add_argument("account")
    i.add_argument("prompt")
    i.add_argument("path", help="absolute path ของไฟล์ PNG")
    i.add_argument("--timeout", type=int, default=300)
    s = sub.add_parser("check", help="ตรวจล็อกอินและเรียกจริง")
    s.add_argument("accounts", nargs="*")
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("quota", help="โควตาจาก rollout ล่าสุด")
    s.add_argument("accounts", nargs="*")
    s.add_argument("--refresh", action="store_true", help="เรียกสั้น 1 ครั้งแบบไม่ ephemeral เพื่อให้ข้อมูลใหม่")
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("stats", help="สถิติจาก ledger")
    s.add_argument("--run")
    s.add_argument("--json", action="store_true")
    s = sub.add_parser("models", help="รุ่นและ effort ที่รองรับ")
    s.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.cmd == "models":
        ms = models()
        if args.json:
            print(json.dumps(ms, ensure_ascii=False, indent=1))
        else:
            print(L.table(["model", "effort ที่รองรับ", "default", "visibility"],
                          [[m["slug"], " ".join(m["efforts"]), m["default"], m["visibility"]] for m in ms]))
            print("\ndifficulty → effort: " + " · ".join("%d=%s" % kv for kv in DIFFICULTY.items()))
        return 0
    if args.cmd == "stats":
        return L.stats_cli(args.run, args.json, "codex")
    if args.cmd in ("check", "quota"):
        names = args.accounts or accounts()
        fn = check if args.cmd == "check" else (lambda n: quota(n, refresh=args.refresh))
        rows = parallel(fn, names)
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=1))
        elif args.cmd == "check":
            print(L.table(["บัญชี", "สถานะ", "เวลา s", "รายละเอียด"],
                          [[r["account"], r["state"], r["duration_s"], r["detail"]] for r in rows]))
        else:
            print(L.table(["บัญชี", "โควตาที่ใช้ไป", "เวลาของข้อมูล"],
                          [[r["account"], r["text"], r["ts"] or "-"] for r in rows]))
        return 0
    if args.cmd == "image":
        r = image(args.account, args.prompt, args.path, args.timeout)
        print(r["result"] if r["ok"] else "ล้ม [%s]: %s" % (r["status"], r["error"]))
        return 0 if r["ok"] else 1
    effort = args.effort or (DIFFICULTY[args.difficulty] if args.difficulty else "low")
    r = call(args.account, args.prompt, args.model, effort, args.timeout, args.cwd)
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        print(r["result"] if r["ok"] else "ล้ม [%s]: %s" % (r["status"], r["error"]))
        d = r["ledger"]
        note = " (ลดจาก %s)" % r["effort_from"] if r.get("effort_from") else ""
        print("[%s %s/%s%s %ss in=%d cached=%d out=%d reasoning=%d]" % (args.account, d["model"], d["effort"], note,
              d["duration_s"], d["input_tokens"], d["cached_input_tokens"], d["output_tokens"], d["reasoning_tokens"]),
              file=sys.stderr)
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
