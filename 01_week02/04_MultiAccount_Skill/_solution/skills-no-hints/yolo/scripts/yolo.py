#!/usr/bin/env python3
"""เรียก Claude Code ทุกบัญชี (yoloN) แบบไม่โต้ตอบ: run / check / quota / stats"""
import sys
sys.dont_write_bytecode = True
import argparse
import json
import os
import re
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import ma_common as mc  # noqa: E402


def _env():
    return mc.clean_env("CLAUDE_CODE_")


def _parse(stdout):
    for line in reversed(stdout.strip().splitlines()):
        try:
            data = json.loads(line)
        except ValueError:
            continue
        if isinstance(data, dict):
            return data
    return None


def usage_of(data):
    usage = (data or {}).get("usage") or {}
    details = usage.get("output_tokens_details") or {}
    return {
        "input": usage.get("input_tokens", 0) or 0,
        "cached": usage.get("cache_read_input_tokens", 0) or 0,
        "cache_write": usage.get("cache_creation_input_tokens", 0) or 0,
        "output": usage.get("output_tokens", 0) or 0,
        "reasoning": details.get("thinking_tokens", 0) or 0,
    }


def resolve(difficulty=None, model=None, effort=None):
    level = mc.DIFFICULTY[int(difficulty or 1)]
    return model or level[0], effort or level[1]


def invoke(account, prompt, model="haiku", effort="low", cwd=None, timeout=600, schema=None,
           run_id=None, node=None, run_dir=None, simulate=False, extra_args=None):
    """เรียกครั้งเดียว คืน dict(ok, result, structured, error, error_kind, usage, row)"""
    started = mc.now_iso()
    clock = time.time()
    if simulate or mc.simulated_limit(account):
        message = "simulated limit: usage limit reached"
        row = mc.make_row(started, account, model, effort, "error", error=message, run_id=run_id,
                          node=node, duration=time.time() - clock, prompt_chars=len(prompt), cost=0)
        mc.ledger_append(row, run_dir)
        return dict(ok=False, result="", structured=None, error=message, error_kind="quota",
                    usage={}, row=row, account=account, model=model, effort=effort, simulated=True)
    # prompt ต้องมาก่อน flag ที่รับหลายค่า
    cmd = [account, "-p", prompt, "--model", model, "--effort", effort, "--output-format", "json",
           "--no-session-persistence", "--strict-mcp-config"]
    if schema:
        cmd += ["--json-schema", schema if isinstance(schema, str) else json.dumps(schema)]
    if extra_args:
        cmd += list(extra_args)
    proc = mc.run_process(cmd, timeout=timeout, cwd=cwd, env=_env())
    data = _parse(proc["stdout"])
    usage = usage_of(data)
    result = (data or {}).get("result") or ""
    structured = (data or {}).get("structured_output")
    if proc["timed_out"]:
        ok, status, error, kind = False, "timeout", "timeout %ss" % timeout, "timeout"
    elif data is None:
        ok, status, error, kind = False, "error", mc.short(proc["stderr"] or proc["stdout"] or "no json output"), None
        kind = mc.classify_error(error)
    elif data.get("is_error"):
        ok, status, error = False, "error", mc.short(result or data.get("subtype") or "is_error=true")
        kind = mc.classify_error(error)
    elif not result and structured is None:
        ok, status, error, kind = False, "error", "คำตอบว่าง", "other"
    else:
        ok, status, error, kind = True, "ok", None, None
    usage_models = list(((data or {}).get("modelUsage") or {}).keys())
    real_model = usage_models[0] if usage_models else model
    row = mc.make_row(started, account, real_model, effort, status, usage=usage, error=error,
                      run_id=run_id, node=node, cost=(data or {}).get("total_cost_usd"),
                      duration=proc["duration"], prompt_chars=len(prompt),
                      result_chars=len(result) if result else len(json.dumps(structured)) if structured else 0)
    mc.ledger_append(row, run_dir)
    return dict(ok=ok, result=result, structured=structured, error=error, error_kind=kind,
                usage=usage, row=row, account=account, model=real_model, effort=effort,
                session_id=(data or {}).get("session_id"))


def check(account, run_dir=None):
    """ตรวจด้วยการเรียกจริงที่สั้นที่สุด"""
    res = invoke(account, "ตอบ OK", "haiku", "low", timeout=90, run_dir=run_dir, node="_check")
    if res["ok"]:
        status = "ready"
    else:
        err = (res["error"] or "").lower()
        if "not logged in" in err:
            status = "not_logged_in"
        elif re.search(r"expired|could not be refreshed|oauth|invalid.*token|authenticat", err):
            status = "expired"
        elif res["error_kind"] in ("quota", "rate_limit"):
            status = "limit"
        else:
            status = "error"
    return dict(account=account, cli="claude", status=status, label=mc.STATUS_TH[status],
                detail=mc.short(res["error"], 120) if res["error"] else "OK",
                checked_at=mc.now_iso(), duration_s=res["row"]["duration_s"])


def _pct(text):
    match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
    return float(match.group(1)) if match else None


def quota(account, run_dir=None):
    """/usage เป็นคำสั่งในตัว ไม่เรียกโมเดล บรรทัดที่ไม่มีให้รายงานว่าไม่มี"""
    started = mc.now_iso()
    proc = mc.run_process([account, "-p", "/usage", "--no-session-persistence", "--strict-mcp-config"],
                          timeout=60, env=_env())
    res = dict(account=account, cli="claude", session_pct=None, week_pct=None, session_resets=None,
               week_resets=None, as_of=mc.now_iso(), source="/usage", has_data=False)
    for line in proc["stdout"].splitlines():
        if line.startswith("Current session"):
            res["session_pct"] = _pct(line)
            res["session_resets"] = mc.short(line.split("resets", 1)[-1], 60) if "resets" in line else None
            res["has_data"] = True
        elif line.startswith("Current week (all"):
            res["week_pct"] = _pct(line)
            res["week_resets"] = mc.short(line.split("resets", 1)[-1], 60) if "resets" in line else None
            res["has_data"] = True
    mc.ledger_append(mc.make_row(started, account, "-", "-", "ok" if proc["rc"] == 0 else "error",
                                 node="_quota", duration=proc["duration"]), run_dir)
    return res


def _print_check(rows, as_json):
    if as_json:
        print(json.dumps(rows, ensure_ascii=False))
    else:
        print(mc.md_table(["บัญชี", "สถานะ", "รายละเอียด", "เวลาเรียก s", "ตรวจเมื่อ"],
                          [[r["account"], r["label"], r["detail"], r["duration_s"], r["checked_at"]] for r in rows]))


def quota_cell(row):
    if not row or not row.get("has_data"):
        return "ไม่มีข้อมูล"
    parts = []
    if row.get("session_pct") is not None:
        parts.append("session %g%%" % row["session_pct"])
    if row.get("week_pct") is not None:
        parts.append("week %g%%" % row["week_pct"])
    return " · ".join(parts) or "ไม่มีข้อมูล"


def main():
    mc.setup_io()
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="เรียกงานเดียว")
    run.add_argument("--account", default="yolo1")
    run.add_argument("--difficulty", type=int, choices=range(1, 7), default=1)
    run.add_argument("--model")
    run.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"])
    run.add_argument("--schema", help="JSON schema สำหรับ structured_output")
    run.add_argument("--cwd")
    run.add_argument("--timeout", type=int, default=600)
    run.add_argument("--prompt-file")
    run.add_argument("--json", action="store_true")
    run.add_argument("prompt", nargs="?")
    for name, text in (("check", "ตรวจความพร้อมด้วยการเรียกจริง"), ("quota", "อ่านโควตาจาก /usage")):
        cmd = sub.add_parser(name, help=text)
        cmd.add_argument("--account", help="ไม่ระบุ = ทุกบัญชี")
        cmd.add_argument("--json", action="store_true")
    stats = sub.add_parser("stats", help="สรุป ledger ตามบัญชี รุ่น run")
    stats.add_argument("--run")
    stats.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.cmd == "run":
        prompt = mc.read_prompt(args)
        model, effort = resolve(args.difficulty, args.model, args.effort)
        schema = args.schema
        res = invoke(args.account, prompt, model, effort, cwd=args.cwd, timeout=args.timeout, schema=schema)
        if args.json:
            out = {k: res.get(k) for k in ("ok", "result", "structured", "error", "error_kind", "account", "model", "effort")}
            out["usage"] = res["usage"]
            print(json.dumps(out, ensure_ascii=False))
        else:
            if res["ok"]:
                print(json.dumps(res["structured"], ensure_ascii=False) if res["structured"] is not None else res["result"])
            else:
                print("ERROR: %s" % res["error"], file=sys.stderr)
        return 0 if res["ok"] else 1
    names = [args.account] if getattr(args, "account", None) else mc.accounts("yolo") if args.cmd in ("check", "quota") else []
    if args.cmd == "check":
        _print_check([check(n) for n in names], args.json)
        return 0
    if args.cmd == "quota":
        rows = [quota(n) for n in names]
        if args.json:
            print(json.dumps(rows, ensure_ascii=False))
        else:
            print(mc.md_table(["บัญชี", "โควตา", "resets", "เวลาของข้อมูล"],
                              [[r["account"], quota_cell(r), r.get("week_resets"), r["as_of"]] for r in rows]))
        return 0
    return mc.stats_main(args)


if __name__ == "__main__":
    sys.exit(main())
