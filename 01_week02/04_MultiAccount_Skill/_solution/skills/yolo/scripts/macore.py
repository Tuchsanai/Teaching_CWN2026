"""macore.py - shared core of the yolo / cyolo / agent-team skills.

An identical copy lives in yolo/scripts/ and cyolo/scripts/ so each skill works on its own.
install.sh refuses to install if the two copies differ. Python 3.8+ stdlib only.

Holds: account discovery, how to launch an account, the ledger (one JSON line per call,
never the prompt text or a secret), error classification, the difficulty table,
the readiness/quota caches and the failure simulator (MA_SIMULATE_LIMIT).
"""
import datetime as dt
import fcntl
import json
import os
import re
import shutil
import signal
import subprocess
import time

BASE = os.environ.get("AI_ACCOUNTS_BASE") or os.path.expanduser("~/ai-accounts")
ROOT = {"yolo": os.path.join(BASE, ".Claude"), "cyolo": os.path.join(BASE, ".Codex")}
CLI = {"yolo": "claude", "cyolo": "codex"}
ACCT_RE = re.compile(r"^(c?yolo)([1-9][0-9]*)$")
SIDES = ("yolo", "cyolo")

TEAM_DIR = os.environ.get("MA_TEAM_DIR") or (
    "/workspace/.agent-team" if os.path.isdir("/workspace") else os.path.expanduser("~/.agent-team"))
GLOBAL_LEDGER = os.path.join(TEAM_DIR, "ledger.jsonl")
READINESS_FILE = os.path.join(TEAM_DIR, "readiness.json")
QUOTA_FILE = os.path.join(TEAM_DIR, "quota.json")

# difficulty -> (claude model, claude effort, codex effort)   [spec table, shared by all skills]
DIFFICULTY = {1: ("haiku", "low", "low"), 2: ("sonnet", "medium", "medium"),
              3: ("opus", "high", "high"), 4: ("opus", "xhigh", "xhigh"),
              5: ("opus", "max", "max"), 6: ("opus", "max", "ultra")}
CLAUDE_MODELS = ("opus", "sonnet", "haiku", "fable")
CLAUDE_EFFORTS = ["low", "medium", "high", "xhigh", "max"]
CODEX_EFFORTS = ["low", "medium", "high", "xhigh", "max", "ultra"]
CODEX_DEFAULT_MODEL = "gpt-6.1-sol"

READY_LABEL = {"ready": "พร้อม", "expired": "ล็อกอินแล้วแต่หมดอายุ",
               "not_logged_in": "ไม่ได้ล็อกอิน", "error": "ใช้ไม่ได้"}

LEDGER_FIELDS = ["ts_start", "ts_end", "run_id", "node", "account", "cli", "model", "effort",
                 "duration_s", "input_tokens", "cached_input_tokens", "cache_write_tokens",
                 "output_tokens", "reasoning_tokens", "cost_usd", "status", "error",
                 "prompt_chars", "result_chars"]


def now_iso():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def side_of(acct):
    m = ACCT_RE.match(acct or "")
    if not m:
        raise ValueError(f"ชื่อบัญชีไม่ถูกต้อง {acct!r} (ต้องเป็น yoloN หรือ cyoloN)")
    return m.group(1)


def is_account(name):
    return bool(ACCT_RE.match(name or ""))


def accounts(side=None):
    """Account dirs that exist on this machine, e.g. ['yolo1', ..., 'cyolo5']."""
    out = []
    for s in ([side] if side else SIDES):
        try:
            names = os.listdir(ROOT[s])
        except OSError:
            continue
        found = [n for n in names if ACCT_RE.match(n) and side_of(n) == s
                 and os.path.isdir(os.path.join(ROOT[s], n))]
        out += sorted(found, key=lambda n: int(ACCT_RE.match(n).group(2)))
    return out


def account_dir(acct):
    return os.path.join(ROOT[side_of(acct)], acct)


def launch(acct):
    """-> (argv prefix, env). Prefer the yoloN/cyoloN wrapper (it links shared skills and
    MCP); fall back to the bare CLI with CLAUDE_CONFIG_DIR / CODEX_HOME when there is none."""
    env = os.environ.copy()
    if shutil.which(acct):
        return [acct], env
    d = account_dir(acct)
    if side_of(acct) == "yolo":
        env.update(CLAUDE_CONFIG_DIR=d, IS_SANDBOX="1")
        return ["claude", "--dangerously-skip-permissions"], env
    env["CODEX_HOME"] = d
    return ["codex", "--dangerously-bypass-approvals-and-sandbox",
            "-c", 'cli_auth_credentials_store="file"'], env


def safe_prompt(p):
    """A prompt that starts with '-' would be parsed as a flag."""
    return " " + p if p.startswith("-") else p


def run_proc(cmd, env=None, cwd=None, timeout=600, watch=None, poll=0.2):
    """Run with stdin closed, in its own process group. -> (rc, stdout, stderr, stop_reason).
    stop_reason is '' normally, 'timeout', or whatever watch() returned (then the group is killed)."""
    p = subprocess.Popen(cmd, env=env, cwd=cwd or None, stdin=subprocess.DEVNULL,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    t0, reason = time.time(), ""
    import threading
    bufs = {"out": b"", "err": b""}

    def pump(stream, key):
        bufs[key] = stream.read()
    th = [threading.Thread(target=pump, args=(p.stdout, "out"), daemon=True),
          threading.Thread(target=pump, args=(p.stderr, "err"), daemon=True)]
    for t in th:
        t.start()
    while p.poll() is None:
        if time.time() - t0 > timeout:
            reason = "timeout"
        elif watch:
            reason = watch() or ""
        if reason:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except OSError:
                pass
            break
        time.sleep(poll)
    rc = p.wait()
    for t in th:
        t.join(5)
    dec = lambda b: (b or b"").decode("utf-8", "replace")
    return rc, dec(bufs["out"]), dec(bufs["err"]), reason


AUTH_RE = re.compile(r"Failed to authenticate|OAuth|401|Unauthorized|not logged in|"
                     r"Not logged in|login required|token (has )?expired|invalid_grant", re.I)
LIMIT_RE = re.compile(r"usage limit|rate.?limit|429|limit reached|hit your limit|quota|"
                      r"Too Many Requests|out of credits|insufficient credits|simulated limit", re.I)


def classify(text):
    """Failure text -> 'auth' | 'limit' | 'error'. auth/limit failures burn no tokens,
    so agent-team may move that task to another account."""
    t = text or ""
    if LIMIT_RE.search(t):
        return "limit"
    if AUTH_RE.search(t):
        return "auth"
    return "error"


# ---------------------------------------------------------------- failure simulator
def simulate_failure(acct, run_dir=None):
    """MA_SIMULATE_LIMIT='yolo1' (every call fails) or 'yolo1:3' (from the 3rd call on),
    comma separated. The call returns at once like an exhausted quota; no tokens used."""
    spec = os.environ.get("MA_SIMULATE_LIMIT", "")
    for item in filter(None, (x.strip() for x in spec.split(","))):
        name, _, nth = item.partition(":")
        if name != acct:
            continue
        nth = int(nth or 1)
        d = os.path.join(run_dir or TEAM_DIR, ".sim")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, acct + ".count"), "a+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.seek(0)
            n = int(f.read().strip() or 0) + 1
            f.seek(0)
            f.truncate()
            f.write(str(n))
        if n >= nth:
            return f"simulated limit (MA_SIMULATE_LIMIT={item}): usage limit reached"
    return None


# ---------------------------------------------------------------- ledger
def _append_line(path, line):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(line + "\n")


def ledger_append(row, run_dir=None):
    """One line per call in the global ledger (and the run ledger when run_dir is given).
    Callers pass counts only - never prompt text or secrets."""
    row.setdefault("event", "call")
    line = json.dumps(row, ensure_ascii=False)
    _append_line(GLOBAL_LEDGER, line)
    if run_dir:
        _append_line(os.path.join(run_dir, "ledger.jsonl"), line)


def ledger_event(kind, acct, status, run_dir=None, **kw):
    """Invocations that do not call a model (auth/login status, /usage): logged with
    event=<kind> and zero tokens so they never mix into the call statistics."""
    ts = now_iso()
    ledger_append({"ts_start": ts, "ts_end": ts, "event": kind, "account": acct,
                   "cli": CLI[side_of(acct)], "status": status, **kw}, run_dir)


def ledger_read(path=GLOBAL_LEDGER):
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    rows.append(json.loads(line))
                except ValueError:
                    pass
    except OSError:
        pass
    return rows


def base_row(ctx, acct, model, effort, prompt):
    ctx = ctx or {}
    return {"ts_start": now_iso(), "ts_end": None, "run_id": ctx.get("run_id"),
            "node": ctx.get("node"), "role": ctx.get("role", "worker"), "account": acct,
            "cli": CLI[side_of(acct)], "model": model, "effort": effort, "duration_s": None,
            "input_tokens": 0, "cached_input_tokens": 0, "cache_write_tokens": 0,
            "output_tokens": 0, "reasoning_tokens": 0, "cost_usd": None, "status": None,
            "error": "", "prompt_chars": len(prompt), "result_chars": 0}


def tokens_used(row):
    """Tokens a call consumed, for budgets: all input (incl. cache) + output."""
    return int(row.get("input_tokens") or 0) + int(row.get("output_tokens") or 0)


# ---------------------------------------------------------------- caches
def cache_load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def cache_update(path, key, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".lock", "a") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        d = cache_load(path)
        d[key] = value
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        os.replace(tmp, path)


def age_s(iso):
    try:
        return time.time() - dt.datetime.fromisoformat(iso).timestamp()
    except (TypeError, ValueError):
        return float("inf")


def table(rows, headers):
    """Plain markdown table."""
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for r in rows:
        out.append("| " + " | ".join("" if c is None else str(c) for c in r) + " |")
    return "\n".join(out)
