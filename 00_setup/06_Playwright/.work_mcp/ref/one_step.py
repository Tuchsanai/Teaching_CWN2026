#!/usr/bin/env python3
"""LAB 5 (อ้างอิง): 1 step แบบ code-in-control ผ่าน Playwright MCP ครบ Observe → Decide → Validate → Act → Verify
เป้าหมาย: เปิดรายการประเภทตั๋ว (Change ticket type) เพื่อจะเลือก One way
ผล: runs/lab5/step/ snapshot.yml observe.png prompt.txt decision.json page.png act.txt verify.yml rpc.jsonl"""
import json, sys, time
from pathlib import Path

import agent as A
from mcp_client import MCP, write_config

GOAL = "เปิดรายการประเภทตั๋ว (Change ticket type) เพื่อจะเลือก One way"
out = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/lab5/step").resolve()
out.mkdir(parents=True, exist_ok=True)
m = MCP(write_config(out.parent / "mcp.config.json", out.parent / "mcp-out"), out.parent / "rpc_all.jsonl", cwd=str(out.parent))
m.set_step_log(out / "rpc.jsonl", "step1")
m.initialize()
m.call("browser_navigate", {"url": A.URL})
time.sleep(2)

# ① Observe
snap, url = A.observe(m)
(out / "snapshot.yml").write_text(snap)
A.screenshot(m, out / "observe.png")
# ② Decide
sent = A.trim(snap, "", A.FORM_ROLES)
prompt = A.PROMPT.format(goal=GOAL, history="(ยังไม่มี)", snapshot="\n".join(sent))
(out / "prompt.txt").write_text(prompt)
dec, secs, raw = A.decide(prompt)
# ③ Validate → Act
idx = A.index(snap)
sent_refs = {mm.group(5) for mm in map(A.ELEM.match, sent) if mm}
verdict, checks = A.validate(dec, idx, sent_refs, [], A.FORM_ROLES, url, {"run": 0, "goal": 0})
el = idx.get(dec.get("ref", ""), {})
rec = {"goal": GOAL, "snapshot_lines": len(snap.splitlines()), "lines_sent_to_llm": len(sent),
       "llm_seconds": secs, "llm_raw": raw, "llm_decision": dec,
       "element": {k: el.get(k) for k in ("role", "name", "line", "box")} if el else None,
       "validate": {"verdict": verdict, "checks": checks}}
if verdict == "ok":
    A.shoot(m, out / "page.png", [{"box": el["box"], "text": f"Step 1 · {dec['action']} {dec['ref']}"}])
    tool, targs = A.TOOL_OF[dec["action"]], A.tool_args(dec)
    r = m.call(tool, targs)
    time.sleep(1.5)
    # ④ Verify
    m.label = "step1-verify"
    after, _ = A.observe(m)
    (out / "verify.yml").write_text(after)
    hit = next(((n, l.strip()) for n, l in enumerate(after.splitlines(), 1) if 'option "One way"' in l), None)
    alive = f"[ref={dec['ref']}]" in after
    rec["act"] = {"tool": tool, "arguments": targs, "is_error": r["is_error"]}
    rec["verify"] = {"pass": bool(hit), "proof": hit, "old_ref_still_in_new_snapshot": alive}
    short = "\n".join(l for l in r["text"].splitlines() if l.startswith(("await ", "- Page URL", "Error")))
    (out / "act.txt").write_text(
        f"→ tools/call {tool} {json.dumps(targs)}\n← isError={str(r['is_error']).lower()} · {r['seconds']}s\n{short}\n\n"
        +
        ("ผล verify: PASS — พบ option \"One way\" ใน verify.yml\n" if hit else "ผล verify: FAIL — ไม่พบ option One way\n")
        + (f"  หลักฐาน verify.yml:{hit[0]}: {hit[1]}\n" if hit else "")
        + f"ref เดิม {dec['ref']} ใน snapshot ใหม่: {'ยังอยู่' if alive else 'ไม่อยู่แล้ว'}\n")
else:
    (out / "act.txt").write_text(f"# ไม่เรียก tool: validate = {verdict}\n")
A.dump(out / "decision.json", rec)
print(json.dumps({"decision": dec, "verdict": verdict, "verify": rec.get("verify")}, ensure_ascii=False))
print("exit", m.close())
