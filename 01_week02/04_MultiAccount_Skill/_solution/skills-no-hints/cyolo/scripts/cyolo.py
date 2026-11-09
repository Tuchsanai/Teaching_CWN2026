#!/usr/bin/env python3
"""เรียก Codex CLI ทุกบัญชี (cyoloN) แบบไม่โต้ตอบ: run / image / check / quota / models / stats"""
import sys
sys.dont_write_bytecode = True
import argparse
import glob
import json
import os
import re
import shutil
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import ma_common as mc  # noqa: E402

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
EFFORT_ORDER = ["low", "medium", "high", "xhigh", "max", "ultra"]


def _home(account):
    return os.path.join(mc.BASE, ".Codex", account)


def models_cache(account):
    """คืนรายการรุ่นจาก models_cache.json หรือ [] ถ้าไม่มี"""
    try:
        with open(os.path.join(_home(account), "models_cache.json"), encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return []
    models = data.get("models") if isinstance(data, dict) else data
    return models or []


def default_model(account):
    """รุ่นที่แสดงในรายการและมี priority ดีสุด"""
    listed = [m for m in models_cache(account) if m.get("visibility") == "list"]
    listed.sort(key=lambda m: m.get("priority", 999))
    return listed[0]["slug"] if listed else None


def clamp_effort(account, model, effort):
    """ลดระดับที่รุ่นไม่รองรับเป็นระดับสูงสุดที่รองรับ คืน (effort, note)"""
    entry = next((m for m in models_cache(account) if m.get("slug") == model), None)
    if not entry:
        return effort, None
    supported = [x.get("effort") for x in entry.get("supported_reasoning_levels", [])]
    if not supported or effort in supported:
        return effort, None
    usable = [e for e in EFFORT_ORDER if e in supported]
    wanted = EFFORT_ORDER.index(effort) if effort in EFFORT_ORDER else len(EFFORT_ORDER)
    lower = [e for e in usable if EFFORT_ORDER.index(e) <= wanted]
    chosen = lower[-1] if lower else usable[0]
    return chosen, "ลดจาก %s เป็น %s (รุ่น %s ไม่รองรับ)" % (effort, chosen, model)


def resolve(account, difficulty=None, model=None, effort=None):
    level = mc.DIFFICULTY[int(difficulty or 1)]
    model = model or default_model(account)
    return model, effort or level[2]


def parse_events(stdout):
    usage, failure = {}, None
    for line in stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        kind = event.get("type")
        if kind == "turn.completed":
            raw = event.get("usage") or {}
            usage = {
                "input": raw.get("input_tokens", 0) or 0,
                "cached": raw.get("cached_input_tokens", 0) or 0,
                "cache_write": raw.get("cache_write_input_tokens", 0) or 0,
                "output": raw.get("output_tokens", 0) or 0,
                "reasoning": raw.get("reasoning_output_tokens", 0) or 0,
            }
        elif kind == "turn.failed":
            failure = ((event.get("error") or {}).get("message")) or "turn.failed"
        elif kind == "error" and not failure:
            failure = event.get("message") or "error"
    return usage, failure


def invoke(account, prompt, model=None, effort="low", cwd=None, timeout=600, ephemeral=True,
           run_id=None, node=None, run_dir=None, simulate=False, extra_args=None):
    """เรียกครั้งเดียว คืน dict(ok, result, error, error_kind, usage, row)"""
    started = mc.now_iso()
    clock = time.time()
    model = model or default_model(account)
    note = None
    if model:
        effort, note = clamp_effort(account, model, effort)
    extra = {"effort_note": note} if note else None
    if simulate or mc.simulated_limit(account):
        message = "simulated limit: usage limit reached"
        row = mc.make_row(started, account, model or "-", effort, "error", error=message, run_id=run_id,
                          node=node, duration=time.time() - clock, prompt_chars=len(prompt), extra=extra)
        mc.ledger_append(row, run_dir)
        return dict(ok=False, result="", error=message, error_kind="quota", usage={}, row=row,
                    account=account, model=model, effort=effort, effort_note=note, simulated=True)
    workdir = tempfile.mkdtemp(prefix="cyolo-")
    out_file = os.path.join(workdir, "answer.txt")
    cmd = [account, "exec", "--skip-git-repo-check"]
    if ephemeral:
        cmd.append("--ephemeral")
    if model:
        cmd += ["-m", model]
    cmd += ["-c", "model_reasoning_effort=%s" % effort, "--json", "-o", out_file]
    if cwd:
        cmd += ["-C", cwd]
    if extra_args:
        cmd += list(extra_args)
    cmd.append(prompt)
    proc = mc.run_process(cmd, timeout=timeout, env=mc.clean_env())
    usage, failure = parse_events(proc["stdout"])
    answer = ""
    try:
        with open(out_file, encoding="utf-8", errors="replace") as handle:
            answer = handle.read().strip()
    except OSError:
        pass
    shutil.rmtree(workdir, ignore_errors=True)
    if proc["timed_out"]:
        ok, status, error, kind = False, "timeout", "timeout %ss" % timeout, "timeout"
    elif failure:
        ok, status, error = False, "error", mc.short(failure)
        kind = mc.classify_error(failure)
    elif proc["rc"] != 0:
        ok, status, error = False, "error", mc.short(proc["stderr"] or "exit %s" % proc["rc"])
        kind = mc.classify_error(error)
    elif not answer:
        # ไม่ใช่ทุกกรณีที่ exit 0 คือสำเร็จ: 401 บางแบบ retry แล้วจบโดยไม่มีคำตอบ
        ok, status, error = False, "error", mc.short(proc["stderr"][-300:] or "ไม่มีคำตอบในไฟล์ -o")
        kind = mc.classify_error(proc["stderr"])
    else:
        ok, status, error, kind = True, "ok", None, None
    row = mc.make_row(started, account, model or "default", effort, status, usage=usage, error=error,
                      run_id=run_id, node=node, duration=proc["duration"], prompt_chars=len(prompt),
                      result_chars=len(answer), extra=extra)
    mc.ledger_append(row, run_dir)
    return dict(ok=ok, result=answer, error=error, error_kind=kind, usage=usage, row=row,
                account=account, model=model, effort=effort, effort_note=note)


def login_status(account, run_dir=None):
    """อ่านจากข้อความ ไม่ใช่ exit code"""
    started = mc.now_iso()
    proc = mc.run_process([account, "login", "status"], timeout=40, env=mc.clean_env())
    text = proc["stdout"] + proc["stderr"]
    mc.ledger_append(mc.make_row(started, account, "-", "-", "ok", node="_login_status",
                                 duration=proc["duration"]), run_dir)
    if "Logged in" in text and "Not logged in" not in text:
        return "logged_in"
    return "not_logged_in"


def check(account, run_dir=None):
    started = time.time()
    if login_status(account, run_dir) != "logged_in":
        return dict(account=account, cli="codex", status="not_logged_in", label=mc.STATUS_TH["not_logged_in"],
                    detail="Not logged in", checked_at=mc.now_iso(), duration_s=round(time.time() - started, 3))
    res = invoke(account, "ตอบ OK", None, "low", timeout=120, run_dir=run_dir, node="_check")
    if res["ok"]:
        status = "ready"
    elif res["error_kind"] == "auth":
        status = "expired"
    elif res["error_kind"] in ("quota", "rate_limit"):
        status = "limit"
    else:
        status = "error"
    return dict(account=account, cli="codex", status=status, label=mc.STATUS_TH[status],
                detail=mc.short(res["error"], 120) if res["error"] else "OK",
                checked_at=mc.now_iso(), duration_s=res["row"]["duration_s"])


def quota(account, refresh=False, run_dir=None):
    """อ่านจาก rollout ล่าสุดที่ไม่ใช่ ephemeral รายงานเวลาของข้อมูลเสมอ"""
    if refresh:
        invoke(account, "ตอบ OK", None, "low", timeout=120, ephemeral=False, run_dir=run_dir, node="_quota_refresh")
    res = dict(account=account, cli="codex", session_pct=None, week_pct=None, session_resets=None,
               week_resets=None, as_of=None, source="rollout token_count", has_data=False)
    started = mc.now_iso()
    files = sorted(glob.glob(os.path.join(_home(account), "sessions", "*", "*", "*", "*.jsonl")),
                   key=lambda p: os.path.getmtime(p), reverse=True)
    for path in files[:15]:
        last = None
        with open(path, "rb") as handle:
            handle.seek(max(0, os.path.getsize(path) - 2000000))
            for raw in handle:
                if b'"token_count"' not in raw:
                    continue
                try:
                    event = json.loads(raw.decode("utf-8", "replace"))
                except ValueError:
                    continue
                limits = (event.get("payload") or {}).get("rate_limits")
                if limits:
                    last = (event.get("timestamp"), limits)
        if not last:
            continue
        stamp, limits = last
        res["as_of"], res["has_data"] = stamp, True
        for name in ("primary", "secondary"):
            window = limits.get(name)
            if not window:
                continue
            minutes = window.get("window_minutes") or 0
            pct, reset = window.get("used_percent"), window.get("resets_at")
            res.setdefault("windows", []).append(dict(name=name, window_minutes=minutes, used_percent=pct, resets_at=reset))
            key = "week" if minutes >= 1440 else "session"
            res[key + "_pct"], res[key + "_resets"] = pct, reset
        break
    mc.ledger_append(mc.make_row(started, account, "-", "-", "ok", node="_quota"), run_dir)
    return res


def quota_cell(row):
    if not row or not row.get("has_data"):
        return "ไม่มีข้อมูล"
    parts = []
    if row.get("session_pct") is not None:
        parts.append("session %g%%" % row["session_pct"])
    if row.get("week_pct") is not None:
        parts.append("week %g%%" % row["week_pct"])
    return " · ".join(parts) or "ไม่มีข้อมูล"


def make_image(account, description, out_path, cwd=None, timeout=600, run_id=None, node=None, run_dir=None, simulate=False):
    """สร้างภาพแล้วตรวจ PNG signature คืน dict(invoke, valid_png)"""
    out_path = os.path.abspath(out_path)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    prompt = "สร้างภาพ (image generation): %s\nบันทึกเป็น PNG ที่ %s\nเมื่อเสร็จตอบ path ของไฟล์เท่านั้น" % (description, out_path)
    res = invoke(account, prompt, None, "low", cwd=cwd, timeout=timeout, run_id=run_id, node=node,
                 run_dir=run_dir, simulate=simulate)
    valid = False
    try:
        with open(out_path, "rb") as handle:
            valid = handle.read(8) == PNG_SIGNATURE
    except OSError:
        pass
    if res["ok"] and not valid:
        res["ok"], res["error"], res["error_kind"] = False, "ไฟล์ไม่ใช่ PNG หรือไม่ถูกสร้าง", "other"
    res["valid_png"] = valid
    res["path"] = out_path
    return res


def main():
    mc.setup_io()
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="เรียกงานเดียว")
    run.add_argument("--account", default="cyolo1")
    run.add_argument("--difficulty", type=int, choices=range(1, 7), default=1)
    run.add_argument("--model")
    run.add_argument("--effort", choices=EFFORT_ORDER)
    run.add_argument("--cwd")
    run.add_argument("--timeout", type=int, default=600)
    run.add_argument("--no-ephemeral", action="store_true", help="เขียน sessions/ เพื่อให้โควตาอัปเดต (ช้ากว่า)")
    run.add_argument("--prompt-file")
    run.add_argument("--json", action="store_true")
    run.add_argument("prompt", nargs="?")
    img = sub.add_parser("image", help="สร้างภาพ PNG (ใช้ effort low เสมอ)")
    img.add_argument("--account", default="cyolo1")
    img.add_argument("--out", required=True, help="absolute path ของไฟล์ PNG")
    img.add_argument("--timeout", type=int, default=600)
    img.add_argument("--json", action="store_true")
    img.add_argument("description")
    for name, text in (("check", "ตรวจความพร้อมด้วยการเรียกจริง"), ("quota", "โควตาจาก rollout พร้อมเวลาของข้อมูล")):
        cmd = sub.add_parser(name, help=text)
        cmd.add_argument("--account", help="ไม่ระบุ = ทุกบัญชี")
        cmd.add_argument("--json", action="store_true")
        if name == "quota":
            cmd.add_argument("--refresh", action="store_true", help="เรียกโมเดลหนึ่งครั้งแบบไม่ ephemeral เพื่ออัปเดตข้อมูล")
    models = sub.add_parser("models", help="รุ่นและ effort ที่รองรับจาก models_cache.json")
    models.add_argument("--account", default="cyolo1")
    models.add_argument("--json", action="store_true")
    stats = sub.add_parser("stats", help="สรุป ledger ตามบัญชี รุ่น run")
    stats.add_argument("--run")
    stats.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.cmd == "run":
        prompt = mc.read_prompt(args)
        model, effort = resolve(args.account, args.difficulty, args.model, args.effort)
        res = invoke(args.account, prompt, model, effort, cwd=args.cwd, timeout=args.timeout, ephemeral=not args.no_ephemeral)
        if args.json:
            print(json.dumps({k: res.get(k) for k in ("ok", "result", "error", "error_kind", "account", "model", "effort", "effort_note", "usage")}, ensure_ascii=False))
        else:
            if res["ok"]:
                print(res["result"])
            else:
                print("ERROR: %s" % res["error"], file=sys.stderr)
            if res.get("effort_note"):
                print("NOTE: %s" % res["effort_note"], file=sys.stderr)
        return 0 if res["ok"] else 1
    if args.cmd == "image":
        res = make_image(args.account, args.description, args.out, timeout=args.timeout)
        info = {k: res.get(k) for k in ("ok", "path", "valid_png", "error", "account", "model", "effort", "usage")}
        print(json.dumps(info, ensure_ascii=False) if args.json else ("PNG OK: %s" % res["path"] if res["ok"] else "ERROR: %s" % res["error"]))
        return 0 if res["ok"] else 1
    if args.cmd == "models":
        rows = [{"slug": m.get("slug"), "default": m.get("default_reasoning_level"),
                 "efforts": [x.get("effort") for x in m.get("supported_reasoning_levels", [])],
                 "visibility": m.get("visibility")} for m in models_cache(args.account)]
        if args.json:
            print(json.dumps(rows, ensure_ascii=False))
        elif rows:
            print(mc.md_table(["slug", "default effort", "efforts", "visibility"],
                              [[r["slug"], r["default"], ",".join(r["efforts"]), r["visibility"]] for r in rows]))
        else:
            print("ไม่มี models_cache.json สำหรับ %s (ยังไม่ได้ล็อกอิน?)" % args.account)
        return 0
    if args.cmd == "stats":
        return mc.stats_main(args)
    names = [args.account] if args.account else mc.accounts("cyolo")
    if args.cmd == "check":
        rows = [check(n) for n in names]
        if args.json:
            print(json.dumps(rows, ensure_ascii=False))
        else:
            print(mc.md_table(["บัญชี", "สถานะ", "รายละเอียด", "เวลาเรียก s", "ตรวจเมื่อ"],
                              [[r["account"], r["label"], r["detail"], r["duration_s"], r["checked_at"]] for r in rows]))
        return 0
    rows = [quota(n, refresh=args.refresh) for n in names]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False))
    else:
        print(mc.md_table(["บัญชี", "โควตา", "เวลาของข้อมูล", "ที่มา"],
                          [[r["account"], quota_cell(r), r.get("as_of") or "ไม่มีข้อมูล", r["source"]] for r in rows]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
