"""verify.py <bench> <metrics.json> : independent checks of a benchmark run (reads the test container), prints JSON."""
import json, re, subprocess, sys, os

os.environ["MSYS_NO_PATHCONV"] = "1"
bench, mf = sys.argv[1], sys.argv[2]
m = json.load(open(mf, encoding="utf-8"))
C = "multi-account"


def sh(cmd):
    r = subprocess.run(["docker", "exec", C, "bash", "-lc", cmd], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout


def ledger_rows():
    out = sh("cat /workspace/.agent-team/ledger.jsonl 2>/dev/null")
    rows = []
    for l in out.splitlines():
        try:
            rows.append(json.loads(l))
        except ValueError:
            pass
    return rows


def all_run_text():
    return sh("cat /workspace/.agent-team/*/state.json /workspace/.agent-team/*/ledger.jsonl /workspace/.agent-team/ledger.jsonl /workspace/.agent-team/*/board.md 2>/dev/null")


checks = {}
rows = ledger_rows()
calls = [r for r in rows if r.get("account")]
checks["ledger_calls"] = len(calls)
checks["ledger_has_both_cli"] = len({str(r.get("cli")) for r in calls}) >= 2
checks["no_credential_touch"] = not m["credential_touch"]
checks["app_ok"] = m["is_error"] is False

if bench == "B1":
    py = r'''
import sys, json
sys.path.insert(0, "/workspace/team-demo")
res = {}
try:
    from final import parse_duration as f
    cases = {"1h30m": 5400, "45s": 45, "2h": 7200, "1h1m1s": 3661, "90m": 5400, "2h0m5s": 7205}
    res["final_cases_ok"] = sum(1 for k, v in cases.items() if f(k) == v)
except Exception as e:
    res["final_cases_ok"] = 0; res["err"] = repr(e)
import os
res["a_files"] = all(os.path.exists("/workspace/team-demo/" + n) for n in ("a_claude.py", "a_codex.py"))
print(json.dumps(res))'''
    r = json.loads(sh(f"python3 - <<'EOF'\n{py}\nEOF") or "{}")
    checks.update(r)
    checks["pass"] = checks.get("final_cases_ok") == 6 and checks.get("a_files") and checks["no_credential_touch"] and checks["app_ok"]
elif bench == "B2":
    t = sh("cat /workspace/demo/table.md 2>/dev/null").replace("`", "").replace("**", "")
    ok = set()
    for a, b, c in re.findall(r"(\d+)\s*(?:x|×|\*|\\times)\s*(\d+)\s*(?:=|\|)\s*(\d+)", t):
        a, b, c = int(a), int(b), int(c)
        if 2 <= a <= 9 and a * b == c:
            ok.add((a, b))
    if len(ok) < 96:  # markdown rows "| a | b | c |"
        for a, b, c in re.findall(r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|", t):
            a, b, c = int(a), int(b), int(c)
            if 2 <= a <= 9 and a * b == c:
                ok.add((a, b))
    checks["table_correct_pairs"] = len(ok)
    txt = all_run_text()
    checks["lead_switch_mentions"] = txt.count("lead_switch")
    checks["worker_switch_mentions"] = txt.count("worker_switch")
    checks["pass"] = len(ok) >= 96 and checks["lead_switch_mentions"] >= 2 and checks["worker_switch_mentions"] >= 1 and checks["no_credential_touch"] and checks["app_ok"]
elif bench == "B3":
    res = m["result"]
    checks["words_total_in_answer"] = "3607" in res.replace(",", "")
    checks["primes_95_in_answer"] = bool(re.search(r"\b95\b", res))
    sig = sh("head -c 8 /workspace/held-out/robot.png | od -An -tx1").split()
    checks["png_ok"] = sig[:4] == ["89", "50", "4e", "47"]
    checks["pass"] = checks["words_total_in_answer"] and checks["primes_95_in_answer"] and checks["png_ok"] and checks["no_credential_touch"] and checks["app_ok"]

out = {k: m[k] for k in ("wall_s", "tool_calls", "tool_errors", "num_turns", "cost_usd")}
out["checks"] = checks
print(json.dumps(out, ensure_ascii=False))
