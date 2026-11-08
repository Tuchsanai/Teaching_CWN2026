#!/usr/bin/env python3
"""yolo.py - call Claude Code accounts (yolo1..yoloN) the right way, non-interactively.

  yolo.py run   -a yolo1 [-d 1-6 | -m MODEL -e EFFORT] [--schema JSON] [--cwd DIR] [--json] PROMPT|-
  yolo.py check [ACCOUNT ...]     real call (haiku/low "ตอบ OK"): พร้อม / ล็อกอินแล้วแต่หมดอายุ / ไม่ได้ล็อกอิน
  yolo.py quota [ACCOUNT ...]     Current session / Current week from "/usage" (no model call)
  yolo.py accounts                account dirs + auth status (no tokens)

Every call appends one row to the ledger (macore.GLOBAL_LEDGER). Exit code 0 = verified OK.
"""
import argparse
import json
import os
import re
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import macore as M  # noqa: E402


def pick(difficulty=None, model=None, effort=None):
    """Explicit model/effort win; otherwise the shared difficulty table (default 2)."""
    dm, de, _ = M.DIFFICULTY[int(difficulty or 2)]
    model, effort = model or dm, effort or de
    if effort == "ultra":                  # Claude has no ultra
        effort = "max"
    if effort not in M.CLAUDE_EFFORTS:
        raise ValueError(f"effort {effort!r} ใช้กับ Claude ไม่ได้ (ใช้ {M.CLAUDE_EFFORTS})")
    return model, effort


def _usage(d):
    u = d.get("usage") or {}
    rd, wr = int(u.get("cache_read_input_tokens") or 0), int(u.get("cache_creation_input_tokens") or 0)
    return {"input_tokens": int(u.get("input_tokens") or 0) + rd + wr, "cached_input_tokens": rd,
            "cache_write_tokens": wr, "output_tokens": int(u.get("output_tokens") or 0),
            "reasoning_tokens": int((u.get("output_tokens_details") or {}).get("thinking_tokens") or 0)}


def call(acct, prompt, model="haiku", effort="low", schema=None, cwd=None, timeout=600,
         ctx=None, watch=None, env_extra=None):
    """One non-interactive call. Never trusts the exit code: checks is_error and result.
    -> dict(ok, status ok|auth|limit|timeout|error, result, structured, error, usage..., cost_usd)"""
    ctx = ctx or {}
    row = M.base_row(ctx, acct, model, effort, prompt)
    t0 = time.time()
    res = {"ok": False, "account": acct, "cli": "claude", "model": model, "effort": effort,
           "result": "", "structured": None, "error": "", "status": "error", "model_used": None}
    sim = M.simulate_failure(acct, ctx.get("run_dir"))
    if sim:
        res.update(status="limit", error=sim)
    else:
        cmd, env = M.launch(acct)
        env.update(env_extra or {})
        cmd += ["-p", M.safe_prompt(prompt), "--model", model, "--effort", effort,
                "--output-format", "json", "--no-session-persistence", "--strict-mcp-config"]
        if schema is not None:
            cmd += ["--json-schema", schema if isinstance(schema, str) else json.dumps(schema)]
        rc, out, err, stop = M.run_proc(cmd, env, cwd, timeout, watch)
        try:
            d = json.loads(out)
        except ValueError:
            d = None
        if stop:
            res.update(status="timeout" if stop == "timeout" else "killed", error=stop)
        elif not isinstance(d, dict):
            msg = (err or out).strip()[-300:] or f"exit {rc}, no JSON"
            res.update(status=M.classify(msg), error=msg)
        else:
            res.update(_usage(d))
            res["cost_usd"] = d.get("total_cost_usd")
            res["model_used"] = ",".join((d.get("modelUsage") or {}).keys()) or None
            res["result"] = str(d.get("result") or "").strip()
            res["structured"] = d.get("structured_output")
            if d.get("is_error"):
                res.update(status=M.classify(res["result"]), error=res["result"][:300])
            elif schema is not None and res["structured"] is None:
                res.update(status="error", error="no structured_output")
            elif schema is None and not res["result"]:
                res.update(status="error", error="empty result")
            else:
                res.update(ok=True, status="ok")
                if schema is not None:
                    res["result"] = json.dumps(res["structured"], ensure_ascii=False)
    res["duration_s"] = round(time.time() - t0, 2)
    row.update({k: res.get(k, row.get(k)) for k in ("input_tokens", "cached_input_tokens",
               "cache_write_tokens", "output_tokens", "reasoning_tokens", "cost_usd")})
    row.update(ts_end=M.now_iso(), duration_s=res["duration_s"], status=res["status"],
               error=res["error"][:200], result_chars=len(res["result"]), model_used=res["model_used"])
    M.ledger_append(row, ctx.get("run_dir"))
    return res


def login_status(acct):
    """-> (logged_in, subscriptionType). Reads only the two fields; never email/orgId."""
    cmd, env = M.launch(acct)
    rc, out, err, _ = M.run_proc(cmd + ["auth", "status", "--json"], env, timeout=60)
    try:
        d = json.loads(out)
    except ValueError:
        M.ledger_event("auth_status", acct, "error")
        return False, (err or out).strip()[-120:] or "no output"
    M.ledger_event("auth_status", acct, "logged_in" if d.get("loggedIn") else "not_logged_in")
    return bool(d.get("loggedIn")), str(d.get("subscriptionType") or "-")


def check(acct, run_dir=None):
    """Readiness by a real minimal call. auth status alone is not enough: it can say
    loggedIn=true while the OAuth session is already expired."""
    li, sub = login_status(acct)
    if not li:
        st = {"state": "not_logged_in", "detail": "auth status: loggedIn=false"}
    else:
        r = call(acct, "ตอบ OK", "haiku", "low", timeout=120,
                 ctx={"node": "_check", "role": "check", "run_dir": run_dir})
        if r["ok"]:
            st = {"state": "ready", "detail": f"{sub} · {r['duration_s']}s"}
        elif r["status"] == "auth":
            st = {"state": "expired", "detail": r["error"][:120]}
        else:
            st = {"state": "error", "detail": f"{r['status']}: {r['error'][:120]}"}
    st["ts"] = M.now_iso()
    M.cache_update(M.READINESS_FILE, acct, st)
    return st


QUOTA_LINE = re.compile(r"^(Current [^:]+):\s*(\d+(?:\.\d+)?)% used(?:\s*·\s*resets (.+))?$")


def quota(acct):
    """Usage % from '/usage' (a local command: no model call). Missing lines -> no data."""
    cmd, env = M.launch(acct)
    rc, out, err, stop = M.run_proc(cmd + ["-p", "/usage", "--strict-mcp-config",
                                           "--no-session-persistence"], env, timeout=90)
    wins = []
    for line in (out or "").splitlines():
        m = QUOTA_LINE.match(line.strip())
        if m:
            wins.append({"name": m.group(1), "used_percent": float(m.group(2)), "resets": m.group(3)})
    q = {"ts": M.now_iso(), "source": "/usage", "windows": wins}
    M.ledger_event("quota", acct, "ok" if wins else "no_data")
    if not wins:
        q["note"] = "ไม่มีข้อมูลโควตา: " + ((out or err).strip().splitlines() or ["(ว่าง)"])[0][:100]
    M.cache_update(M.QUOTA_FILE, acct, q)
    return q


def quota_text(q):
    if not q or not q.get("windows"):
        return (q or {}).get("note") or "ไม่มีข้อมูล"
    w = " · ".join(f"{x['name'].replace('Current ', '')} {x['used_percent']:g}%" for x in q["windows"])
    return f"{w} (ข้อมูล ณ {q['ts'][11:16]})"


def stats_line(r):
    return (f"[{r['account']} {r['model']}/{r['effort']} → {r.get('model_used') or '-'}] "
            f"{r['status']} · {r['duration_s']}s · in {r.get('input_tokens', 0)} "
            f"(cache read {r.get('cached_input_tokens', 0)}, write {r.get('cache_write_tokens', 0)}) "
            f"· out {r.get('output_tokens', 0)} · ${r.get('cost_usd') or 0:.4f} (list price)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("prompt", help="prompt text, or - to read stdin")
    r.add_argument("-a", "--account", default="yolo1")
    r.add_argument("-d", "--difficulty", type=int, choices=range(1, 7))
    r.add_argument("-m", "--model")
    r.add_argument("-e", "--effort")
    r.add_argument("--schema", help="JSON schema -> result is structured_output")
    r.add_argument("--cwd")
    r.add_argument("--timeout", type=int, default=600)
    r.add_argument("--json", action="store_true", help="print the full result dict")
    for name in ("check", "quota"):
        sub.add_parser(name).add_argument("accounts", nargs="*")
    sub.add_parser("accounts")
    a = ap.parse_args()

    if a.cmd == "run":
        if M.side_of(a.account) != "yolo":
            sys.exit("yolo.py ใช้กับ yoloN เท่านั้น (Codex ใช้ cyolo.py)")
        prompt = sys.stdin.read() if a.prompt == "-" else a.prompt
        model, effort = pick(a.difficulty, a.model, a.effort)
        res = call(a.account, prompt, model, effort, a.schema, a.cwd, a.timeout, {"node": "_single"})
        if a.json:
            print(json.dumps(res, ensure_ascii=False, indent=1))
        else:
            print(res["result"] if res["ok"] else f"ERROR ({res['status']}): {res['error']}")
            print(stats_line(res), file=sys.stderr)
        return 0 if res["ok"] else 1

    accts = getattr(a, "accounts", None) or M.accounts("yolo")
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max(1, len(accts))) as ex:
        if a.cmd == "accounts":
            for acct, (li, sub_) in zip(accts, ex.map(login_status, accts)):
                print(f"{acct:7} {M.account_dir(acct)}  {'logged in (' + sub_ + ')' if li else 'not logged in'}")
        elif a.cmd == "check":
            res = list(ex.map(check, accts))
            print(M.table([(x, M.READY_LABEL[s["state"]], s["detail"]) for x, s in zip(accts, res)],
                          ["บัญชี", "สถานะ", "รายละเอียด"]))
        else:
            res = list(ex.map(quota, accts))
            print(M.table([(x, quota_text(q)) for x, q in zip(accts, res)], ["บัญชี", "โควตาที่ใช้ไป"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
