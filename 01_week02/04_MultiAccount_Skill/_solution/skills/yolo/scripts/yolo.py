#!/usr/bin/env python3
"""yolo.py - เรียก Claude Code ของบัญชี yolo1..yoloN แบบไม่โต้ตอบ (ไลบรารีมาตรฐานเท่านั้น)

คำสั่ง:
  ask <account> "<prompt>" [--model M] [--effort E] [--difficulty 1-6] [--json-schema S]
                           [--cwd DIR] [--timeout S] [--json]
  check [accounts...] [--json]      ตรวจความพร้อมด้วยการเรียกจริง (haiku/low "ตอบ OK")
  quota [accounts...] [--json]      อ่าน /usage (ไม่เรียกโมเดล ไม่เสียโทเค็น)
  accounts                          รายชื่อบัญชีที่มีโฟลเดอร์
  pick --difficulty N               ดูรุ่น/effort ตามตารางความยาก

ทุกการเรียกเพิ่ม 1 แถวใน /workspace/.agent-team/ledger.jsonl (ไม่เก็บข้อความ prompt หรือ secret)
ห้ามอ่าน .credentials.json / .claude.json - สคริปต์นี้ไม่แตะสองไฟล์นั้น
"""
import argparse
import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
import time

BASE = os.environ.get("MA_BASE", "/root/ai-accounts")
CLAUDE_ROOT = os.path.join(BASE, ".Claude")
LEDGER_DIR = os.environ.get("MA_LEDGER_DIR", "/workspace/.agent-team")

MODELS = ["opus", "sonnet", "haiku", "fable"]
EFFORTS = ["low", "medium", "high", "xhigh", "max"]
# difficulty -> (model, effort)  (ตารางเดียวกับ cyolo / agent-team)
DIFFICULTY = {1: ("haiku", "low"), 2: ("sonnet", "medium"), 3: ("opus", "high"),
              4: ("opus", "xhigh"), 5: ("opus", "max"), 6: ("opus", "max")}

AUTH_PAT = re.compile(r"(Failed to authenticate|OAuth|not logged in|Please run /login|401|"
                      r"Invalid API key|authentication)", re.I)
QUOTA_PAT = re.compile(r"(usage limit|rate limit|rate_limit|429|quota|limit reached|"
                       r"hit your limit|out of extra usage|overloaded)", re.I)


def now_iso():
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def classify_error(text):
    """'quota' | 'auth' | 'timeout' | 'other' จากข้อความผิดพลาด"""
    t = text or ""
    if "simulated" in t.lower() and "limit" in t.lower():
        return "quota"
    if QUOTA_PAT.search(t):
        return "quota"
    if AUTH_PAT.search(t):
        return "auth"
    if "timeout" in t.lower():
        return "timeout"
    return "other"


# ---------------------------------------------------------------- ledger
def _append_line(path, line):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        try:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX)
        except Exception:
            pass
        f.write(line + "\n")


def ledger_append(row, run_dir=None):
    """เพิ่มแถวใน ledger รวม (และของ run ถ้ามี) - row ต้องไม่มี prompt/secret"""
    line = json.dumps(row, ensure_ascii=False)
    try:
        _append_line(os.path.join(LEDGER_DIR, "ledger.jsonl"), line)
    except OSError as e:
        print("yolo: เขียน ledger ไม่ได้: %s" % e, file=sys.stderr)
    if run_dir:
        _append_line(os.path.join(run_dir, "ledger.jsonl"), line)


def ledger_row(**kw):
    row = {k: None for k in ("ts_start", "ts_end", "run_id", "node", "account", "cli", "model",
                             "effort", "duration_s", "input_tokens", "cached_input_tokens",
                             "cache_write_tokens", "output_tokens", "reasoning_tokens",
                             "cost_usd", "status", "error", "prompt_chars", "result_chars")}
    row["event"] = "call"
    row.update(kw)
    return row


# ---------------------------------------------------------------- accounts
def list_accounts():
    if not os.path.isdir(CLAUDE_ROOT):
        return []
    out = [n for n in os.listdir(CLAUDE_ROOT) if re.fullmatch(r"yolo\d+", n)
           and os.path.isdir(os.path.join(CLAUDE_ROOT, n))]
    return sorted(out, key=lambda s: int(s[4:]))


def base_cmd(account):
    """คำสั่งเริ่มต้นของบัญชี: ใช้ wrapper ถ้ามี ไม่มี (N>5) เรียก claude ตรงด้วย env ชุดเดียวกัน"""
    env = os.environ.copy()
    if shutil.which(account):
        return [account], env
    env["CLAUDE_CONFIG_DIR"] = os.path.join(CLAUDE_ROOT, account)
    if os.geteuid() == 0:
        env["IS_SANDBOX"] = "1"
    cmd = ["claude", "--dangerously-skip-permissions"]
    mcp = os.path.join(CLAUDE_ROOT, "shared", "mcp", "mcp.json")
    if os.path.isfile(mcp):
        cmd.append("--mcp-config=" + mcp)
    return cmd, env


def pick(difficulty=None, model=None, effort=None):
    d = int(difficulty) if difficulty else 2
    d = min(max(d, 1), 6)
    m, e = DIFFICULTY[d]
    return (model or m), (effort or e)


def simulated(account):
    sims = [s.strip() for s in os.environ.get("MA_SIMULATE_LIMIT", "").split(",") if s.strip()]
    return account in sims


# ---------------------------------------------------------------- call
def call(account, prompt, model=None, effort=None, difficulty=None, json_schema=None,
         cwd=None, timeout=600, run_id=None, node=None, run_dir=None, event="call",
         extra_args=None, stream_cb=None, popen_cb=None, env_extra=None):
    """เรียก Claude 1 ครั้ง คืน dict: ok, result, error, error_kind, usage..., structured_output
    exit code 0 ไม่ได้แปลว่าสำเร็จ: ตัดสินจาก is_error + result
    stream_cb(event_dict) - ถ้าให้มา จะใช้ --output-format stream-json แล้วส่งทุก event
    """
    model, effort = pick(difficulty, model, effort)
    ts_start = now_iso()
    t0 = time.time()
    res = {"ok": False, "result": "", "error": None, "error_kind": None, "account": account,
           "cli": "claude", "model": model, "effort": effort, "input_tokens": 0,
           "cached_input_tokens": 0, "cache_write_tokens": 0, "output_tokens": 0,
           "reasoning_tokens": 0, "cost_usd": 0.0, "structured_output": None,
           "model_real": None, "num_turns": 0, "returncode": None}
    if simulated(account):
        time.sleep(0.05)
        res.update(error="simulated: usage limit reached (MA_SIMULATE_LIMIT)", error_kind="quota")
    else:
        cmd, env = base_cmd(account)
        if env_extra:
            env.update(env_extra)
        fmt = "stream-json" if stream_cb else "json"
        # prompt ต้องอยู่หลัง -p ทันที และก่อน flag ที่รับหลายค่า
        cmd += ["-p", prompt, "--model", model, "--effort", effort, "--output-format", fmt,
                "--no-session-persistence", "--strict-mcp-config"]
        if stream_cb:
            cmd.append("--verbose")
        if json_schema:
            cmd += ["--json-schema", json_schema if isinstance(json_schema, str)
                    else json.dumps(json_schema)]
        if extra_args:
            cmd += list(extra_args)
        data = None
        try:
            p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, cwd=cwd or None, env=env,
                                 start_new_session=True, text=True, encoding="utf-8",
                                 errors="replace")
            if popen_cb:
                popen_cb(p)
            if stream_cb:
                import threading
                err_buf = []
                th = threading.Thread(target=lambda: err_buf.append(p.stderr.read()), daemon=True)
                th.start()
                deadline = t0 + timeout
                seen, live = set(), {"in": 0, "out": 0, "cr": 0, "cw": 0}
                for line in p.stdout:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        ev = json.loads(line)
                    except ValueError:
                        continue
                    if ev.get("type") == "result":
                        data = ev
                    elif ev.get("type") == "assistant":
                        msg = ev.get("message") or {}
                        u = msg.get("usage") or {}
                        if msg.get("id") and msg["id"] not in seen:
                            seen.add(msg["id"])
                            live["in"] += int(u.get("input_tokens") or 0)
                            live["cr"] += int(u.get("cache_read_input_tokens") or 0)
                            live["cw"] += int(u.get("cache_creation_input_tokens") or 0)
                            live["out"] += int(u.get("output_tokens") or 0)
                    try:
                        stream_cb(ev)
                    except Exception:
                        pass
                    if time.time() > deadline:
                        _kill(p)
                        break
                try:
                    p.wait(timeout=max(1, deadline - time.time()))
                except subprocess.TimeoutExpired:
                    _kill(p)
                    p.wait()
                    res["error"], res["error_kind"] = "timeout %ss" % timeout, "timeout"
                stderr = "".join(err_buf)
                if data is None and seen:
                    # ถูก kill ก่อนมี result: ใช้ usage ที่สะสมจาก stream ให้ ledger ไม่ขาด
                    res["input_tokens"] = live["in"] + live["cr"] + live["cw"]
                    res["cached_input_tokens"], res["cache_write_tokens"] = live["cr"], live["cw"]
                    res["output_tokens"] = live["out"]
            else:
                try:
                    out, stderr = p.communicate(timeout=timeout)
                except subprocess.TimeoutExpired:
                    _kill(p)
                    out, stderr = p.communicate()
                    res["error"], res["error_kind"] = "timeout %ss" % timeout, "timeout"
                try:
                    data = json.loads(out) if out.strip() else None
                except ValueError:
                    data = None
                    for ln in out.splitlines()[::-1]:
                        try:
                            data = json.loads(ln)
                            break
                        except ValueError:
                            pass
            res["returncode"] = p.returncode
            if data:
                u = data.get("usage") or {}
                res["input_tokens"] = int(u.get("input_tokens") or 0) + \
                    int(u.get("cache_read_input_tokens") or 0) + int(u.get("cache_creation_input_tokens") or 0)
                res["cached_input_tokens"] = int(u.get("cache_read_input_tokens") or 0)
                res["cache_write_tokens"] = int(u.get("cache_creation_input_tokens") or 0)
                res["output_tokens"] = int(u.get("output_tokens") or 0)
                res["reasoning_tokens"] = int((u.get("output_tokens_details") or {}).get("thinking_tokens") or 0)
                res["cost_usd"] = float(data.get("total_cost_usd") or 0.0)
                res["num_turns"] = data.get("num_turns") or 0
                mu = data.get("modelUsage") or {}
                res["model_real"] = ",".join(mu.keys()) or None
                res["result"] = data.get("result") or ""
                res["structured_output"] = data.get("structured_output")
                if data.get("is_error") or res["error"]:
                    res["error"] = res["error"] or (res["result"] or "is_error")[:300]
                else:
                    res["ok"] = True
            elif not res["error"]:
                msg = (stderr or "").strip().splitlines()
                res["error"] = (msg[-1] if msg else "no JSON output (exit %s)" % p.returncode)[:300]
            if res["error"] and not res["error_kind"]:
                res["error_kind"] = classify_error(res["error"])
        except FileNotFoundError as e:
            res["error"], res["error_kind"] = "ไม่พบคำสั่ง: %s" % e, "other"
    res["duration_s"] = round(time.time() - t0, 2)
    ledger_append(ledger_row(
        ts_start=ts_start, ts_end=now_iso(), run_id=run_id, node=node, account=account,
        cli="claude", model=model, effort=effort, duration_s=res["duration_s"],
        input_tokens=res["input_tokens"], cached_input_tokens=res["cached_input_tokens"],
        cache_write_tokens=res["cache_write_tokens"], output_tokens=res["output_tokens"],
        reasoning_tokens=res["reasoning_tokens"], cost_usd=round(res["cost_usd"], 6),
        status="ok" if res["ok"] else "error", error=(res["error"] or None) and res["error"][:160],
        prompt_chars=len(prompt), result_chars=len(res["result"] or ""), event=event), run_dir)
    return res


def _kill(p):
    try:
        os.killpg(p.pid, 9)
    except Exception:
        try:
            p.kill()
        except Exception:
            pass


# ---------------------------------------------------------------- auth / quota
def auth_logged_in(account):
    """อ่านเฉพาะ loggedIn / subscriptionType จาก auth status (ไม่พิมพ์ email/orgId)"""
    cmd, env = base_cmd(account)
    try:
        p = subprocess.run(cmd + ["auth", "status", "--json"], stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, timeout=30, env=env)
        d = json.loads(p.stdout)
        return bool(d.get("loggedIn")), d.get("subscriptionType")
    except Exception:
        return None, None


def check_account(account, run_id=None, run_dir=None):
    """เรียกจริงด้วยงานสั้นที่สุด แยก ready / expired / not_logged_in"""
    logged, sub = auth_logged_in(account)
    r = call(account, "ตอบ OK", model="haiku", effort="low", timeout=90, run_id=run_id,
             node="_check", run_dir=run_dir, event="check")
    if r["ok"]:
        state = "ready"
    elif r["error_kind"] == "auth" and (logged or "expired" in (r["error"] or "").lower()):
        # auth status อาจบอก loggedIn: true แต่ token หมดอายุ / หรือมี credential เก่าที่ refresh ไม่ได้
        state = "expired"
    elif r["error_kind"] == "quota":
        state = "quota"
    elif logged is False:
        state = "not_logged_in"
    else:
        state = "error"
    return {"account": account, "cli": "claude", "state": state, "logged_in": logged,
            "plan": sub, "duration_s": r["duration_s"], "error": r["error"],
            "ts": now_iso()}


STATE_TH = {"ready": "พร้อม", "expired": "ล็อกอินแล้วแต่หมดอายุ", "not_logged_in": "ไม่ได้ล็อกอิน",
            "quota": "โควตาหมด/ติด rate limit", "error": "ใช้ไม่ได้ (ข้อผิดพลาดอื่น)"}

USAGE_PAT = re.compile(r"^(Current (?:session|week[^:]*)):\s*(\d+(?:\.\d+)?)% used(?:\s*·\s*resets\s*(.+))?$")


def quota(account):
    """/usage ส่งเป็น prompt: คำสั่งในตัว ไม่เรียกโมเดล ไม่เสียโทเค็น (ไม่บันทึก ledger เพราะไม่ใช่การเรียกโมเดล)"""
    cmd, env = base_cmd(account)
    info = {"account": account, "cli": "claude", "ts": now_iso(), "session_pct": None,
            "week_pct": None, "lines": [], "available": False, "error": None}
    # MA_SIMULATE_LIMIT ไม่แตะโควตา: บัญชีดูปกติจนเรียกจริงแล้วล้ม (ทดสอบ failover เชิงรับ)
    try:
        p = subprocess.run(cmd + ["-p", "/usage", "--output-format", "json",
                                  "--no-session-persistence", "--strict-mcp-config"],
                           stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           timeout=60, env=env)
        d = json.loads(p.stdout)
        text = d.get("result") or ""
        if d.get("is_error"):
            info["error"] = text[:200]
            return info
        for ln in text.splitlines():
            m = USAGE_PAT.match(ln.strip())
            if m:
                info["lines"].append(ln.strip())
                pct = float(m.group(2))
                if m.group(1) == "Current session":
                    info["session_pct"] = pct
                elif m.group(1).startswith("Current week (all models)"):
                    info["week_pct"] = pct
        info["available"] = bool(info["lines"])
        if not info["available"]:
            info["error"] = "ไม่มีข้อมูลโควตาใน /usage"
    except Exception as e:
        info["error"] = "อ่าน /usage ไม่ได้: %s" % str(e)[:120]
    return info


def quota_pct(info):
    """% ที่ใช้ไปแล้วที่ใช้ตัดสิน (session ก่อน ถ้าไม่มีใช้ week)"""
    if not info:
        return None
    for k in ("session_pct", "week_pct", "primary_pct", "secondary_pct"):
        if info.get(k) is not None:
            return info[k]
    return None


# ---------------------------------------------------------------- CLI
def _par(fn, items):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max(1, len(items))) as ex:
        return list(ex.map(fn, items))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="yolo.py", description="เรียก Claude Code หลายบัญชี (yoloN)")
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("ask", help="เรียกงานเดียว")
    a.add_argument("account")
    a.add_argument("prompt")
    a.add_argument("--model", choices=MODELS)
    a.add_argument("--effort", choices=EFFORTS)
    a.add_argument("--difficulty", type=int)
    a.add_argument("--json-schema")
    a.add_argument("--cwd")
    a.add_argument("--timeout", type=int, default=600)
    a.add_argument("--json", action="store_true", help="พิมพ์ผล+สถิติเป็น JSON")
    c = sub.add_parser("check", help="ตรวจความพร้อมด้วยการเรียกจริง")
    c.add_argument("accounts", nargs="*")
    c.add_argument("--json", action="store_true")
    q = sub.add_parser("quota", help="โควตาจาก /usage")
    q.add_argument("accounts", nargs="*")
    q.add_argument("--json", action="store_true")
    sub.add_parser("accounts")
    pk = sub.add_parser("pick")
    pk.add_argument("--difficulty", type=int, default=2)
    args = ap.parse_args(argv)

    if args.cmd == "ask":
        r = call(args.account, args.prompt, args.model, args.effort, args.difficulty,
                 args.json_schema, args.cwd, args.timeout)
        if args.json:
            print(json.dumps(r, ensure_ascii=False, indent=1))
        else:
            if r["ok"]:
                print(r["result"])
            print("[%s %s/%s %.1fs in=%d out=%d $%.4f %s]" % (
                args.account, r["model"], r["effort"], r["duration_s"], r["input_tokens"],
                r["output_tokens"], r["cost_usd"], "ok" if r["ok"] else "ERROR: " + str(r["error"])),
                file=sys.stderr)
        return 0 if r["ok"] else 1
    if args.cmd == "check":
        accs = args.accounts or list_accounts()
        rows = _par(check_account, accs)
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=1))
        else:
            print("| บัญชี | สถานะ | auth status | เวลา (s) | หมายเหตุ |\n|---|---|---|---|---|")
            for r in rows:
                print("| %s | %s | %s | %.1f | %s |" % (r["account"], STATE_TH[r["state"]],
                      r["logged_in"], r["duration_s"], (r["error"] or "")[:70]))
        return 0
    if args.cmd == "quota":
        accs = args.accounts or list_accounts()
        rows = _par(quota, accs)
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=1))
        else:
            for r in rows:
                print("%s (ข้อมูล ณ %s):" % (r["account"], r["ts"]))
                for ln in r["lines"] or ["  ไม่มีข้อมูล: %s" % r["error"]]:
                    print("  " + ln)
        return 0
    if args.cmd == "accounts":
        print("\n".join(list_accounts()))
        return 0
    if args.cmd == "pick":
        print("%s / %s" % pick(args.difficulty))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
