#!/usr/bin/env python3
"""cyolo.py - call Codex CLI accounts (cyolo1..cyoloN) the right way, non-interactively.

  cyolo.py run    -a cyolo1 [-d 1-6 | -m MODEL -e EFFORT] [--schema JSON] [--cwd DIR] [--json] PROMPT|-
  cyolo.py image  -a cyolo1 --out /abs/path.png "<what to draw>"      (effort low, PNG verified)
  cyolo.py models [-a cyolo1]       models + supported efforts from models_cache.json
  cyolo.py check  [ACCOUNT ...]     login status text + real call: พร้อม / หมดอายุ / ไม่ได้ล็อกอิน
  cyolo.py quota  [ACCOUNT ...] [--refresh]   rate_limits from the newest non-ephemeral rollout

Every call appends one row to the ledger (macore.GLOBAL_LEDGER). Exit code 0 = verified OK.
"""
import argparse
import glob
import json
import os
import sys
import time
import uuid

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import macore as M  # noqa: E402

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def models(acct):
    """[{slug, efforts, default, visibility}] from <CODEX_HOME>/models_cache.json."""
    try:
        with open(os.path.join(M.account_dir(acct), "models_cache.json"), encoding="utf-8") as f:
            cache = json.load(f)
    except (OSError, ValueError):
        return []
    return [{"slug": m.get("slug"),
             "efforts": [x.get("effort") for x in m.get("supported_reasoning_levels") or []],
             "default": m.get("default_reasoning_level"), "visibility": m.get("visibility")}
            for m in cache.get("models") or []]


def pick(acct, difficulty=None, model=None, effort=None):
    """-> (model, effort, note). Unsupported level is lowered to the highest supported one
    and the note says from what (e.g. ultra on a model without ultra -> max)."""
    want = effort or M.DIFFICULTY[int(difficulty or 2)][2]
    if want not in M.CODEX_EFFORTS:
        raise ValueError(f"effort {want!r} ไม่รู้จัก (ใช้ {M.CODEX_EFFORTS})")
    ms = models(acct)
    model = model or (M.CODEX_DEFAULT_MODEL if any(m["slug"] == M.CODEX_DEFAULT_MODEL for m in ms)
                      else next((m["slug"] for m in ms if m["visibility"] == "list"), M.CODEX_DEFAULT_MODEL))
    ok = next((m["efforts"] for m in ms if m["slug"] == model), None)
    if not ok or want in ok:
        return model, want, ""
    lower = [e for e in M.CODEX_EFFORTS[:M.CODEX_EFFORTS.index(want)] if e in ok]
    got = lower[-1] if lower else ok[0]
    return model, got, f"ลดจาก {want} เป็น {got} ({model} ไม่รองรับ {want})"


def _parse_jsonl(out):
    usage, failed, last_err, thread = None, None, None, None
    for line in out.splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        t = e.get("type")
        if t == "thread.started":
            thread = e.get("thread_id")
        elif t == "turn.completed":
            usage = e.get("usage") or {}
        elif t == "turn.failed":
            failed = (e.get("error") or {}).get("message") or "turn.failed"
        elif t == "error":
            last_err = e.get("message")
    return usage, failed, last_err, thread


def call(acct, prompt, model=None, effort="low", schema=None, cwd=None, timeout=600,
         ctx=None, watch=None, env_extra=None, ephemeral=True, effort_note=""):
    """One `codex exec` call. The answer comes from the -o file; failure from turn.failed
    (exit code is not trusted). --ephemeral is ~3.5x faster but does not refresh quota data."""
    ctx = ctx or {}
    model = model or M.CODEX_DEFAULT_MODEL
    row = M.base_row(ctx, acct, model, effort, prompt)
    if effort_note:
        row["effort_from"] = effort_note
    t0 = time.time()
    res = {"ok": False, "account": acct, "cli": "codex", "model": model, "effort": effort,
           "effort_from": effort_note, "result": "", "structured": None, "error": "", "status": "error"}
    sim = M.simulate_failure(acct, ctx.get("run_dir"))
    if sim:
        res.update(status="limit", error=sim)
    else:
        tmp = os.path.join(M.TEAM_DIR, "tmp")
        os.makedirs(tmp, exist_ok=True)
        out_file = os.path.join(tmp, f"cx-{uuid.uuid4().hex}.out")
        cmd, env = M.launch(acct)
        env.update(env_extra or {})
        cmd += ["exec", "--skip-git-repo-check", "-m", model,
                "-c", f'model_reasoning_effort="{effort}"', "--json", "-o", out_file]
        if ephemeral:
            cmd.append("--ephemeral")
        schema_file = None
        if schema is not None:
            schema_file = out_file + ".schema.json"
            with open(schema_file, "w", encoding="utf-8") as f:
                f.write(schema if isinstance(schema, str) else json.dumps(schema))
            cmd += ["--output-schema", schema_file]
        cmd.append(M.safe_prompt(prompt))
        rc, out, err, stop = M.run_proc(cmd, env, cwd, timeout, watch)
        usage, failed, last_err, _ = _parse_jsonl(out)
        try:
            with open(out_file, encoding="utf-8") as f:
                res["result"] = f.read().strip()
        except OSError:
            pass
        for p in (out_file, schema_file):
            if p and os.path.exists(p):
                os.remove(p)
        if usage:
            res.update(input_tokens=int(usage.get("input_tokens") or 0),
                       cached_input_tokens=int(usage.get("cached_input_tokens") or 0),
                       cache_write_tokens=int(usage.get("cache_write_input_tokens") or 0),
                       output_tokens=int(usage.get("output_tokens") or 0),
                       reasoning_tokens=int(usage.get("reasoning_output_tokens") or 0))
        if stop:
            res.update(status="timeout" if stop == "timeout" else "killed", error=stop)
        elif failed or (not usage and (last_err or rc)):
            msg = failed or last_err or err.strip()[-300:] or f"exit {rc}"
            res.update(status=M.classify(msg), error=msg[:300])
        elif not res["result"]:
            res.update(status="error", error="empty -o answer file")
        else:
            res.update(ok=True, status="ok")
            if schema is not None:
                try:
                    res["structured"] = json.loads(res["result"])
                except ValueError:
                    res.update(ok=False, status="error", error="answer is not JSON for --output-schema")
    res["duration_s"] = round(time.time() - t0, 2)
    row.update({k: res.get(k, row.get(k)) for k in ("input_tokens", "cached_input_tokens",
               "cache_write_tokens", "output_tokens", "reasoning_tokens")})
    row.update(ts_end=M.now_iso(), duration_s=res["duration_s"], status=res["status"],
               error=res["error"][:200], result_chars=len(res["result"]), ephemeral=ephemeral)
    M.ledger_append(row, ctx.get("run_dir"))
    return res


def image(acct, desc, out_path, model=None, timeout=600, ctx=None):
    """Image generation (Codex only). effort low: higher effort is slower, not better."""
    out_path = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    prompt = (f"สร้างภาพ (image generation): {desc}\n\nใช้เครื่องมือสร้างภาพ แล้วบันทึกเป็นไฟล์ PNG ที่ "
              f"{out_path} ตอบกลับเป็น path ของไฟล์อย่างเดียว")
    model, effort, note = pick(acct, 1, model, "low")
    r = call(acct, prompt, model, effort, cwd=os.path.dirname(out_path), timeout=timeout,
             ctx=ctx, effort_note=note)
    if r["ok"]:
        try:
            with open(out_path, "rb") as f:
                head = f.read(8)
            if head != PNG_MAGIC:
                r.update(ok=False, status="error", error=f"{out_path} ไม่ใช่ PNG (signature {head!r})")
            else:
                r["image_bytes"] = os.path.getsize(out_path)
        except OSError:
            r.update(ok=False, status="error", error=f"ไม่พบไฟล์ภาพ {out_path}")
    return r


def login_status(acct):
    """Text of `login status` decides, not the exit code."""
    cmd, env = M.launch(acct)
    rc, out, err, _ = M.run_proc(cmd + ["login", "status"], env, timeout=60)
    lines = (out + "\n" + err).strip().splitlines()
    last = lines[-1].strip() if lines else ""
    M.ledger_event("login_status", acct, "logged_in" if last.startswith("Logged in") else "not_logged_in")
    return last.startswith("Logged in"), last or "no output"


def check(acct, run_dir=None):
    li, detail = login_status(acct)
    if not li:
        st = {"state": "not_logged_in", "detail": detail[:120]}
    else:
        model, effort, _ = pick(acct, 1)
        r = call(acct, "ตอบ OK", model, effort, timeout=120,
                 ctx={"node": "_check", "role": "check", "run_dir": run_dir})
        if r["ok"]:
            st = {"state": "ready", "detail": f"{detail} · {r['duration_s']}s"}
        elif r["status"] == "auth":
            st = {"state": "expired", "detail": r["error"][:120]}
        else:
            st = {"state": "error", "detail": f"{r['status']}: {r['error'][:120]}"}
    st["ts"] = M.now_iso()
    M.cache_update(M.READINESS_FILE, acct, st)
    return st


def quota(acct, refresh=False):
    """rate_limits of the newest token_count event in sessions/ (ephemeral calls write none).
    refresh=True first makes one tiny non-ephemeral call (uses a few tokens)."""
    if refresh:
        model, effort, _ = pick(acct, 1)
        call(acct, "ตอบ OK", model, effort, timeout=120, ephemeral=False,
             ctx={"node": "_quota", "role": "check"})
    home = M.account_dir(acct)
    files = sorted(glob.glob(os.path.join(home, "sessions", "*", "*", "*", "*.jsonl")),
                   key=os.path.getmtime, reverse=True)
    for fpath in files[:20]:
        last = None
        with open(fpath, encoding="utf-8", errors="replace") as f:
            for line in f:
                if '"token_count"' not in line:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                p = e.get("payload") or {}
                if p.get("type") == "token_count" and p.get("rate_limits"):
                    last = (e.get("timestamp"), p["rate_limits"])
        if last:
            ts, rl = last
            wins = []
            for key in ("primary", "secondary"):
                w = rl.get(key)
                if w:
                    resets = w.get("resets_at")
                    wins.append({"name": f"{key} ({w.get('window_minutes')} นาที)",
                                 "used_percent": float(w.get("used_percent") or 0),
                                 "resets": M.dt.datetime.fromtimestamp(resets).astimezone()
                                 .isoformat(timespec="minutes") if resets else None})
            try:
                data_ts = M.dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone() \
                    .isoformat(timespec="seconds")
            except (AttributeError, ValueError):
                data_ts = ts
            q = {"ts": data_ts, "source": "sessions rollout", "windows": wins,
                 "plan": rl.get("plan_type"), "limit_reached": rl.get("rate_limit_reached_type")}
            M.cache_update(M.QUOTA_FILE, acct, q)
            return q
    q = {"ts": M.now_iso(), "source": "sessions rollout", "windows": [],
         "note": "ไม่มีข้อมูลโควตาใน sessions/ (ใช้ --refresh เพื่อเรียกสั้น ๆ แบบไม่ ephemeral)"}
    M.cache_update(M.QUOTA_FILE, acct, q)
    return q


def quota_text(q):
    if not q or not q.get("windows"):
        return (q or {}).get("note") or "ไม่มีข้อมูล"
    w = " · ".join(f"{x['name']} {x['used_percent']:g}%" for x in q["windows"])
    return f"{w} (ข้อมูล ณ {q['ts'][:16].replace('T', ' ')})"


def stats_line(r):
    extra = f" · {r['effort_from']}" if r.get("effort_from") else ""
    return (f"[{r['account']} {r['model']}/{r['effort']}{extra}] {r['status']} · {r['duration_s']}s · "
            f"in {r.get('input_tokens', 0)} (cached {r.get('cached_input_tokens', 0)}) · out "
            f"{r.get('output_tokens', 0)} (reasoning {r.get('reasoning_tokens', 0)})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "image"):
        r = sub.add_parser(name)
        r.add_argument("prompt", help="prompt text, or - to read stdin")
        r.add_argument("-a", "--account", default="cyolo1")
        r.add_argument("-m", "--model")
        r.add_argument("--timeout", type=int, default=600)
        r.add_argument("--json", action="store_true")
        if name == "run":
            r.add_argument("-d", "--difficulty", type=int, choices=range(1, 7))
            r.add_argument("-e", "--effort")
            r.add_argument("--schema")
            r.add_argument("--cwd")
        else:
            r.add_argument("--out", required=True, help="absolute .png path")
    sub.add_parser("models").add_argument("-a", "--account", default="cyolo1")
    sub.add_parser("check").add_argument("accounts", nargs="*")
    q = sub.add_parser("quota")
    q.add_argument("accounts", nargs="*")
    q.add_argument("--refresh", action="store_true")
    a = ap.parse_args()

    if a.cmd in ("run", "image"):
        if M.side_of(a.account) != "cyolo":
            sys.exit("cyolo.py ใช้กับ cyoloN เท่านั้น (Claude ใช้ yolo.py)")
        prompt = sys.stdin.read() if a.prompt == "-" else a.prompt
        if a.cmd == "image":
            res = image(a.account, prompt, a.out, a.model, a.timeout, {"node": "_image"})
        else:
            model, effort, note = pick(a.account, a.difficulty, a.model, a.effort)
            res = call(a.account, prompt, model, effort, a.schema, a.cwd, a.timeout,
                       {"node": "_single"}, effort_note=note)
        if a.json:
            print(json.dumps(res, ensure_ascii=False, indent=1))
        else:
            print(res["result"] if res["ok"] else f"ERROR ({res['status']}): {res['error']}")
            print(stats_line(res), file=sys.stderr)
        return 0 if res["ok"] else 1
    if a.cmd == "models":
        print(M.table([(m["slug"], " ".join(m["efforts"]), m["default"], m["visibility"])
                       for m in models(a.account)], ["model", "efforts", "default", "visibility"]))
        return 0
    accts = a.accounts or M.accounts("cyolo")
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max(1, len(accts))) as ex:
        if a.cmd == "check":
            res = list(ex.map(check, accts))
            print(M.table([(x, M.READY_LABEL[s["state"]], s["detail"]) for x, s in zip(accts, res)],
                          ["บัญชี", "สถานะ", "รายละเอียด"]))
        else:
            res = list(ex.map(lambda x: quota(x, a.refresh), accts))
            print(M.table([(x, quota_text(q)) for x, q in zip(accts, res)], ["บัญชี", "โควตาที่ใช้ไป"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
