#!/usr/bin/env python3
"""cyolo.py - เรียก Codex CLI ของบัญชี cyolo1..cyoloN แบบไม่โต้ตอบ (ไลบรารีมาตรฐานเท่านั้น)

คำสั่ง:
  ask <account> "<prompt>" [-m MODEL] [--effort E] [--difficulty 1-6] [--output-schema FILE]
                           [--cwd DIR] [--timeout S] [--persist] [--json]
  image <account> "<รายละเอียดภาพ>" <absolute path .png> [--timeout S]
  check [accounts...] [--json]         ตรวจความพร้อม (login status + เรียกจริง low)
  quota [accounts...] [--refresh] [--json]   rate_limits จาก rollout ล่าสุด (พร้อมเวลาของข้อมูล)
  models [account]                      รุ่นและ effort ที่รองรับ จาก models_cache.json
  accounts

ทุกการเรียกเพิ่ม 1 แถวใน /workspace/.agent-team/ledger.jsonl (ไม่เก็บ prompt/secret)
ห้ามอ่าน auth.json - สคริปต์นี้ไม่แตะไฟล์นั้น
"""
import argparse
import datetime as _dt
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

BASE = os.environ.get("MA_BASE", "/root/ai-accounts")
CODEX_ROOT = os.path.join(BASE, ".Codex")
LEDGER_DIR = os.environ.get("MA_LEDGER_DIR", "/workspace/.agent-team")

LEVELS = ["low", "medium", "high", "xhigh", "max", "ultra"]
DIFFICULTY = {1: "low", 2: "medium", 3: "high", 4: "xhigh", 5: "max", 6: "ultra"}
PNG_SIG = b"\x89PNG\r\n\x1a\n"

AUTH_PAT = re.compile(r"(401|Unauthorized|Not logged in|login|authentication|bearer)", re.I)
QUOTA_PAT = re.compile(r"(usage limit|rate limit|rate_limit|429|quota|limit reached|"
                       r"Too Many Requests|insufficient credits)", re.I)


def now_iso():
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def classify_error(text):
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
    line = json.dumps(row, ensure_ascii=False)
    try:
        _append_line(os.path.join(LEDGER_DIR, "ledger.jsonl"), line)
    except OSError as e:
        print("cyolo: เขียน ledger ไม่ได้: %s" % e, file=sys.stderr)
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


# ---------------------------------------------------------------- accounts / models
def list_accounts():
    if not os.path.isdir(CODEX_ROOT):
        return []
    out = [n for n in os.listdir(CODEX_ROOT) if re.fullmatch(r"cyolo\d+", n)
           and os.path.isdir(os.path.join(CODEX_ROOT, n))]
    return sorted(out, key=lambda s: int(s[5:]))


def home(account):
    return os.path.join(CODEX_ROOT, account)


def base_cmd(account):
    env = os.environ.copy()
    if shutil.which(account):
        return [account], env
    env["CODEX_HOME"] = home(account)
    return ["codex", "--dangerously-bypass-approvals-and-sandbox",
            "-c", 'cli_auth_credentials_store="file"'], env


def load_models(account=None):
    """[{slug, efforts[], default}] ของรุ่นที่ไม่ซ่อน เรียงตาม priority (ไม่อ่านส่วน identity)"""
    accs = [account] if account else list_accounts()
    for a in accs:
        f = os.path.join(home(a), "models_cache.json")
        if os.path.isfile(f):
            try:
                with open(f, encoding="utf-8") as fh:
                    d = json.load(fh)
            except ValueError:
                continue
            out = []
            for m in d.get("models") or []:
                if m.get("visibility") == "hide":
                    continue
                out.append({"slug": m.get("slug"),
                            "efforts": [x.get("effort") for x in m.get("supported_reasoning_levels") or []],
                            "default": m.get("default_reasoning_level"),
                            "priority": m.get("priority") or 999,
                            "name": m.get("display_name")})
            out.sort(key=lambda x: x["priority"])
            if out:
                return out
    return []


def default_model(account=None):
    env = os.environ.get("MA_CODEX_MODEL")
    if env:
        return env
    ms = load_models(account)
    return ms[0]["slug"] if ms else "gpt-6.1-sol"


def resolve_effort(model, effort, account=None):
    """คืน (effort ที่ใช้จริง, note) - ระดับที่รุ่นไม่รองรับลดเป็นระดับสูงสุดที่รองรับ"""
    ms = {m["slug"]: m for m in load_models(account)}
    m = ms.get(model)
    if not m or not m["efforts"]:
        return effort, None
    if effort in m["efforts"]:
        return effort, None
    want = LEVELS.index(effort) if effort in LEVELS else 0
    cands = [e for e in m["efforts"] if e in LEVELS and LEVELS.index(e) <= want]
    new = max(cands, key=LEVELS.index) if cands else m["efforts"][0]
    return new, "ลด effort จาก %s เป็น %s (%s ไม่รองรับ)" % (effort, new, model)


def pick(difficulty=None, model=None, effort=None, account=None):
    d = min(max(int(difficulty or 2), 1), 6)
    model = model or default_model(account)
    effort = effort or DIFFICULTY[d]
    effort, note = resolve_effort(model, effort, account)
    return model, effort, note


def simulated(account):
    sims = [s.strip() for s in os.environ.get("MA_SIMULATE_LIMIT", "").split(",") if s.strip()]
    return account in sims


# ---------------------------------------------------------------- call
def call(account, prompt, model=None, effort=None, difficulty=None, output_schema=None,
         cwd=None, timeout=600, run_id=None, node=None, run_dir=None, event="call",
         ephemeral=True, popen_cb=None, env_extra=None, stream_cb=None):
    """เรียก Codex 1 ครั้ง คำตอบอ่านจากไฟล์ -o, usage จาก turn.completed
    exit 0 ไม่ได้แปลว่าสำเร็จ (บัญชีไม่ล็อกอิน retry 401 ได้) ตัดสินจาก turn.failed/error"""
    model, effort, note = pick(difficulty, model, effort, account)
    ts_start = now_iso()
    t0 = time.time()
    res = {"ok": False, "result": "", "error": None, "error_kind": None, "account": account,
           "cli": "codex", "model": model, "effort": effort, "effort_note": note,
           "input_tokens": 0, "cached_input_tokens": 0, "cache_write_tokens": 0,
           "output_tokens": 0, "reasoning_tokens": 0, "cost_usd": None, "thread_id": None,
           "returncode": None}
    if simulated(account):
        time.sleep(0.05)
        res.update(error="simulated: usage limit reached (MA_SIMULATE_LIMIT)", error_kind="quota")
    else:
        cmd, env = base_cmd(account)
        if env_extra:
            env.update(env_extra)
        fd, ans = tempfile.mkstemp(prefix="cyolo-", suffix=".txt")
        os.close(fd)
        cmd += ["exec", "--skip-git-repo-check"]
        if ephemeral:
            cmd.append("--ephemeral")
        cmd += ["-m", model, "-c", "model_reasoning_effort=%s" % effort, "--json", "-o", ans]
        if cwd:
            cmd += ["-C", cwd]
        if output_schema:
            cmd += ["--output-schema", output_schema]
        cmd.append(prompt)
        errors, failed, usage = [], None, None
        try:
            p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                 stderr=subprocess.DEVNULL, cwd=cwd or None, env=env,
                                 start_new_session=True, text=True, encoding="utf-8",
                                 errors="replace")
            if popen_cb:
                popen_cb(p)
            import threading
            timer = threading.Timer(timeout, lambda: _kill(p))
            timer.start()
            last_msg = ""
            for line in p.stdout:
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if stream_cb:
                    try:
                        stream_cb(ev)
                    except Exception:
                        pass
                t = ev.get("type")
                if t == "thread.started":
                    res["thread_id"] = ev.get("thread_id")
                elif t == "turn.completed":
                    usage = ev.get("usage") or {}
                elif t == "turn.failed":
                    failed = ((ev.get("error") or {}).get("message") or "turn.failed")
                elif t == "error":
                    errors.append(ev.get("message") or "")
                elif t == "item.completed":
                    it = ev.get("item") or {}
                    if it.get("type") == "agent_message":
                        last_msg = it.get("text") or last_msg
            p.wait()
            timed_out = not timer.is_alive() and usage is None and failed is None
            timer.cancel()
            res["returncode"] = p.returncode
            if usage:
                res["input_tokens"] = int(usage.get("input_tokens") or 0)  # รวม cached แล้ว
                res["cached_input_tokens"] = int(usage.get("cached_input_tokens") or 0)
                res["cache_write_tokens"] = int(usage.get("cache_write_input_tokens") or 0)
                res["output_tokens"] = int(usage.get("output_tokens") or 0)
                res["reasoning_tokens"] = int(usage.get("reasoning_output_tokens") or 0)
            try:
                with open(ans, encoding="utf-8", errors="replace") as fh:
                    res["result"] = fh.read().strip()
            except OSError:
                pass
            if not res["result"]:
                res["result"] = last_msg
            if failed:
                res["error"] = failed[:300]
            elif timed_out:
                res["error"], res["error_kind"] = "timeout %ss" % timeout, "timeout"
            elif usage is None:
                res["error"] = (errors[-1] if errors else "ไม่มี turn.completed (exit %s)" % p.returncode)[:300]
            else:
                res["ok"] = True
            if res["error"] and not res["error_kind"]:
                res["error_kind"] = classify_error(res["error"])
        except FileNotFoundError as e:
            res["error"], res["error_kind"] = "ไม่พบคำสั่ง: %s" % e, "other"
        finally:
            try:
                os.unlink(ans)
            except OSError:
                pass
    res["duration_s"] = round(time.time() - t0, 2)
    ledger_append(ledger_row(
        ts_start=ts_start, ts_end=now_iso(), run_id=run_id, node=node, account=account,
        cli="codex", model=model, effort=effort, duration_s=res["duration_s"],
        input_tokens=res["input_tokens"], cached_input_tokens=res["cached_input_tokens"],
        cache_write_tokens=res["cache_write_tokens"], output_tokens=res["output_tokens"],
        reasoning_tokens=res["reasoning_tokens"], cost_usd=None,
        status="ok" if res["ok"] else "error", error=(res["error"] or None) and res["error"][:160],
        prompt_chars=len(prompt), result_chars=len(res["result"] or ""), event=event,
        effort_note=note), run_dir)
    return res


def _kill(p):
    try:
        os.killpg(p.pid, 9)
    except Exception:
        try:
            p.kill()
        except Exception:
            pass


# ---------------------------------------------------------------- image
def image_prompt(desc, path):
    return ("สร้างภาพ (image generation) ตามเงื่อนไขทุกข้อ:\n%s\n"
            "บันทึกเป็นไฟล์ PNG ที่ %s (absolute path) แล้วตอบ path อย่างเดียว" % (desc.strip(), path))


def is_png(path):
    try:
        with open(path, "rb") as f:
            return f.read(8) == PNG_SIG
    except OSError:
        return False


def image(account, desc, path, timeout=300, **kw):
    """สร้างภาพ (Codex เท่านั้น) effort low เสมอ (effort สูงไม่ทำให้ภาพดีขึ้น) ตรวจ PNG signature"""
    path = os.path.abspath(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    kw.setdefault("cwd", os.path.dirname(path))
    r = call(account, image_prompt(desc, path), effort="low", timeout=timeout, **kw)
    r["image_path"] = path
    r["is_png"] = is_png(path)
    if r["ok"] and not r["is_png"]:
        r["ok"] = False
        r["error"] = "ไม่พบไฟล์ PNG ที่ %s" % path
        r["error_kind"] = "other"
    return r


# ---------------------------------------------------------------- login / quota
def login_status(account):
    """อ่านจากข้อความ ไม่ใช่ exit code"""
    cmd, env = base_cmd(account)
    try:
        p = subprocess.run(cmd + ["login", "status"], stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, timeout=30, env=env)
        txt = (p.stdout + "\n" + p.stderr)
        if "Not logged in" in txt:
            return False
        if "Logged in" in txt:
            return True
    except Exception:
        pass
    return None


def check_account(account, run_id=None, run_dir=None, deep=False):
    logged = login_status(account)
    if logged is False and not deep:
        # exec จริงของบัญชีที่ไม่ล็อกอินจะ retry 401 ~15 s แล้ว turn.failed: ข้ามเพื่อประหยัดเวลา
        return {"account": account, "cli": "codex", "state": "not_logged_in", "logged_in": False,
                "duration_s": 0.0, "error": "login status: Not logged in", "ts": now_iso()}
    r = call(account, "ตอบ OK", effort="low", timeout=120, run_id=run_id, node="_check",
             run_dir=run_dir, event="check")
    if r["ok"]:
        state = "ready"
    elif r["error_kind"] == "quota":
        state = "quota"
    elif logged and r["error_kind"] == "auth":
        state = "expired"
    elif logged is False:
        state = "not_logged_in"
    else:
        state = "error"
    return {"account": account, "cli": "codex", "state": state, "logged_in": logged,
            "duration_s": r["duration_s"], "error": r["error"], "ts": now_iso()}


STATE_TH = {"ready": "พร้อม", "expired": "ล็อกอินแล้วแต่หมดอายุ", "not_logged_in": "ไม่ได้ล็อกอิน",
            "quota": "โควตาหมด/ติด rate limit", "error": "ใช้ไม่ได้ (ข้อผิดพลาดอื่น)"}


def _fmt_reset(ts):
    try:
        return _dt.datetime.fromtimestamp(int(ts)).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    except Exception:
        return None


def quota(account, refresh=False):
    """rate_limits จาก event token_count ล่าสุดใน sessions/ (งาน ephemeral ไม่อัปเดต)"""
    info = {"account": account, "cli": "codex", "ts": None, "primary_pct": None,
            "secondary_pct": None, "lines": [], "available": False, "error": None,
            "source": None}
    if refresh:
        call(account, "ตอบ OK", effort="low", timeout=120, node="_quota", event="quota_refresh",
             ephemeral=False)
    files = glob.glob(os.path.join(home(account), "sessions", "*", "*", "*", "rollout-*.jsonl"))
    files.sort(key=lambda f: os.path.basename(f))
    for f in reversed(files[-30:]):
        last = None
        try:
            with open(f, encoding="utf-8", errors="replace") as fh:
                for ln in fh:
                    if '"token_count"' not in ln:
                        continue
                    try:
                        ev = json.loads(ln)
                    except ValueError:
                        continue
                    pl = ev.get("payload") or {}
                    if pl.get("type") == "token_count" and pl.get("rate_limits"):
                        last = (ev.get("timestamp"), pl["rate_limits"])
        except OSError:
            continue
        if last:
            ts, rl = last
            try:
                ts = _dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().isoformat(timespec="seconds")
            except Exception:
                pass
            info["ts"] = ts
            info["source"] = os.path.basename(f)
            for k in ("primary", "secondary"):
                w = rl.get(k)
                if w:
                    info[k + "_pct"] = float(w.get("used_percent") or 0)
                    info["lines"].append("%s: %s%% used · window %s min · resets %s" % (
                        k, w.get("used_percent"), w.get("window_minutes"), _fmt_reset(w.get("resets_at"))))
            if rl.get("rate_limit_reached_type"):
                info["lines"].append("rate_limit_reached: %s" % rl.get("rate_limit_reached_type"))
            info["available"] = bool(info["lines"])
            break
    if not info["available"]:
        info["error"] = "ไม่มีข้อมูล (ยังไม่มี rollout ที่ไม่ใช่ ephemeral; ใช้ --refresh)"
    return info


# ---------------------------------------------------------------- CLI
def _par(fn, items):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max(1, len(items))) as ex:
        return list(ex.map(fn, items))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="cyolo.py", description="เรียก Codex CLI หลายบัญชี (cyoloN)")
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("ask")
    a.add_argument("account")
    a.add_argument("prompt")
    a.add_argument("-m", "--model")
    a.add_argument("--effort", choices=LEVELS)
    a.add_argument("--difficulty", type=int)
    a.add_argument("--output-schema", help="ไฟล์ JSON schema แบบ strict")
    a.add_argument("--cwd")
    a.add_argument("--timeout", type=int, default=600)
    a.add_argument("--persist", action="store_true", help="ไม่ใส่ --ephemeral (อัปเดตข้อมูลโควตา)")
    a.add_argument("--json", action="store_true")
    im = sub.add_parser("image")
    im.add_argument("account")
    im.add_argument("desc")
    im.add_argument("path")
    im.add_argument("--timeout", type=int, default=300)
    im.add_argument("--json", action="store_true")
    c = sub.add_parser("check")
    c.add_argument("accounts", nargs="*")
    c.add_argument("--deep", action="store_true", help="เรียก exec จริงแม้ login status = Not logged in")
    c.add_argument("--json", action="store_true")
    q = sub.add_parser("quota")
    q.add_argument("accounts", nargs="*")
    q.add_argument("--refresh", action="store_true", help="เรียกสั้น 1 ครั้งแบบไม่ ephemeral ก่อนอ่าน")
    q.add_argument("--json", action="store_true")
    m = sub.add_parser("models")
    m.add_argument("account", nargs="?")
    sub.add_parser("accounts")
    args = ap.parse_args(argv)

    if args.cmd == "ask":
        r = call(args.account, args.prompt, args.model, args.effort, args.difficulty,
                 args.output_schema, args.cwd, args.timeout, ephemeral=not args.persist)
        if args.json:
            print(json.dumps(r, ensure_ascii=False, indent=1))
        else:
            if r["ok"]:
                print(r["result"])
            print("[%s %s/%s %.1fs in=%d (cached %d) out=%d reasoning=%d %s%s]" % (
                args.account, r["model"], r["effort"], r["duration_s"], r["input_tokens"],
                r["cached_input_tokens"], r["output_tokens"], r["reasoning_tokens"],
                "ok" if r["ok"] else "ERROR: " + str(r["error"]),
                (" · " + r["effort_note"]) if r["effort_note"] else ""), file=sys.stderr)
        return 0 if r["ok"] else 1
    if args.cmd == "image":
        r = image(args.account, args.desc, args.path, args.timeout)
        if args.json:
            print(json.dumps(r, ensure_ascii=False, indent=1))
        else:
            print(r["image_path"] if r["ok"] else "ERROR: %s" % r["error"])
            print("[%s %.1fs png=%s in=%d out=%d]" % (args.account, r["duration_s"], r["is_png"],
                  r["input_tokens"], r["output_tokens"]), file=sys.stderr)
        return 0 if r["ok"] else 1
    if args.cmd == "check":
        accs = args.accounts or list_accounts()
        rows = _par(lambda a: check_account(a, deep=args.deep), accs)
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=1))
        else:
            print("| บัญชี | สถานะ | login status | เวลา (s) | หมายเหตุ |\n|---|---|---|---|---|")
            for r in rows:
                print("| %s | %s | %s | %.1f | %s |" % (r["account"], STATE_TH[r["state"]],
                      r["logged_in"], r["duration_s"], (r["error"] or "")[:70]))
        return 0
    if args.cmd == "quota":
        accs = args.accounts or list_accounts()
        rows = _par(lambda a: quota(a, args.refresh), accs)
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=1))
        else:
            for r in rows:
                print("%s (ข้อมูล ณ %s):" % (r["account"], r["ts"] or "-"))
                for ln in r["lines"] or ["ไม่มีข้อมูล: %s" % r["error"]]:
                    print("  " + ln)
        return 0
    if args.cmd == "models":
        for mm in load_models(args.account):
            print("%-16s default=%-7s efforts=%s" % (mm["slug"], mm["default"], ",".join(mm["efforts"])))
        return 0
    if args.cmd == "accounts":
        print("\n".join(list_accounts()))
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
