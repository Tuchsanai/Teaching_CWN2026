#!/usr/bin/env python3
"""1 step แบบ code-in-control: Observe -> Decide -> Validate -> Act -> Verify"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
URL = "https://www.google.com/travel/flights?hl=en"
D = "lab5/step"
GOAL = 'เปิดรายการประเภทตั๋ว (Change ticket type) เพื่อจะเลือก One way'
ALLOW = {"click", "fill", "press", "stop"}
DENY = re.compile(r"book|sign in|payment|select flight|select fare", re.I)
ROLES = ("button", "combobox", "textbox", "option")
LINE = re.compile(r'^\s*-\s*(\w+)\s+"([^"]*)".*?\[ref=(\w+)\]')
BOX = re.compile(r'\s*\[box=([\d.,-]+)\]')
SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["click", "fill", "press", "stop"]},
        "ref": {"type": "string"},
        "value": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": ["action", "ref", "value", "reason"],
    "additionalProperties": False,
}


def pw(*args):
    r = subprocess.run(["playwright-cli", *args], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    print(f"$ playwright-cli {' '.join(args)[:120]}\n  -> rc={r.returncode} {out[:200]!r}")
    return r.returncode, out


def parse(path):
    """คืน dict ref -> (role, name, box|None) จากทุกบรรทัดใน snapshot"""
    items = {}
    for ln in open(path, encoding="utf-8"):
        m = LINE.match(ln)
        if m:
            b = BOX.search(ln)
            box = [float(x) for x in b.group(1).split(",")] if b else None
            items[m.group(3)] = (m.group(1), m.group(2), box)
    return items


def stop(msg, code=1):
    print("STOP:", msg)
    pw("close")
    sys.exit(code)


# ---------- 1. Observe ----------
pw("open", URL)
rc, _ = pw("snapshot", "--boxes", f"--filename={D}/snapshot.yml")
if rc:
    stop("snapshot ไม่สำเร็จ")
items = parse(f"{D}/snapshot.yml")

# ---------- 2. Decide ----------
kept = []
for ln in open(f"{D}/snapshot.yml", encoding="utf-8"):
    m = LINE.match(ln)
    if m and m.group(1) in ROLES:
        kept.append(BOX.sub("", ln.rstrip()))
prompt = f"""เป้าหมาย: {GOAL}

ด้านล่างคือรายการ element ที่ตัดมาจาก snapshot ของหน้า {URL}:
{chr(10).join(kept)}

กติกา:
- เลือก ref จากรายการข้างบนเท่านั้น ห้ามคิด ref เอง
- action ต้องเป็นหนึ่งใน click / fill / press / stop (stop = ไม่มี element ที่เหมาะสม)
- ทำเพียง 1 การกระทำที่ใกล้เป้าหมายที่สุด

ตอบเป็น JSON เท่านั้น รูปแบบ: {{"action": "...", "ref": "...", "value": "...", "reason": "..."}}
(ถ้าไม่ใช้ value ให้เป็นสตริงว่าง)
"""
open(f"{D}/prompt.txt", "w", encoding="utf-8").write(prompt)
r = subprocess.run(
    ["yolo1", "-p", "--model", "haiku", "--effort", "low", "--output-format", "json",
     "--json-schema", json.dumps(SCHEMA), "--no-session-persistence",
     "--strict-mcp-config", "--tools", ""],
    input=prompt, capture_output=True, text=True)
try:
    ans = json.loads(r.stdout)["structured_output"]
except Exception as e:
    stop(f"อ่านคำตอบ LLM ไม่ได้: {e}; stdout={r.stdout[:300]!r} stderr={r.stderr[:300]!r}")
print("LLM:", ans)

# ---------- 3. Validate ----------
action, ref = ans.get("action"), ans.get("ref")
role, name, box = items.get(ref, (None, "", None))
checks = {
    "action_in_allowlist": action in ALLOW,
    "ref_in_snapshot": ref in items,
    "name_not_denylisted": not DENY.search(name or ""),
}
ok = all(checks.values())
json.dump({"llm_answer": ans, "element": {"role": role, "name": name, "box": box},
           "checks": {k: "pass" if v else "fail" for k, v in checks.items()},
           "approved": ok},
          open(f"{D}/decision.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
if not ok:
    stop(f"validate ไม่ผ่าน: {checks}")
if action != "click":
    stop(f"step นี้รองรับเฉพาะ click (LLM ตอบ {action})")

if box:
    label = f"Step 1 · click {ref}"
    x, y, w, h = box
    js = """() => {
      const [x, y, w, h] = %s, label = %s;
      const root = document.createElement('div');
      root.id = '__step_overlay';
      root.style.cssText = 'position:fixed;left:0;top:0;width:0;height:0;z-index:2147483647;pointer-events:none';
      const ns = 'http://www.w3.org/2000/svg';
      const svg = document.createElementNS(ns, 'svg');
      svg.setAttribute('width', window.innerWidth); svg.setAttribute('height', window.innerHeight);
      svg.style.cssText = 'position:fixed;left:0;top:0';
      const c = document.createElementNS(ns, 'circle');
      c.setAttribute('cx', x + w / 2); c.setAttribute('cy', y + h / 2);
      c.setAttribute('r', Math.max(w, h) / 2 + 8);
      c.setAttribute('fill', 'none'); c.setAttribute('stroke', 'red'); c.setAttribute('stroke-width', '4');
      svg.appendChild(c);
      const t = document.createElement('div');
      t.textContent = label;
      t.style.cssText = 'position:fixed;background:red;color:#fff;font:bold 14px sans-serif;padding:4px 8px;border-radius:4px;left:' + x + 'px;top:' + Math.max(0, y - Math.max(w, h) / 2 - 36) + 'px';
      root.appendChild(svg); root.appendChild(t);
      document.body.appendChild(root);
      return 'ok';
    }""" % (json.dumps([x, y, w, h]), json.dumps(label))
    pw("eval", js)
    pw("screenshot", "--hires", f"--filename={D}/page.png")
    pw("eval", "() => { const e = document.getElementById('__step_overlay'); if (e) e.remove(); return 'removed'; }")

# ---------- 4. Act ----------
act_cmd = f"playwright-cli click {ref}"
rc, act_out = pw("click", ref)

# ---------- 5. Verify ----------
pw("snapshot", "--boxes", f"--filename={D}/verify.yml")
vlines = open(f"{D}/verify.yml", encoding="utf-8").read().splitlines()
opt = next(((i + 1, l.strip()) for i, l in enumerate(vlines)
            if re.search(r'option\s+"One way"', l)), None)
ref_still = next(((i + 1, l.strip()) for i, l in enumerate(vlines)
                  if f"[ref={ref}]" in l), None)
passed = opt is not None
with open(f"{D}/act.txt", "w", encoding="utf-8") as f:
    f.write(f"command: {act_cmd}\nexit code: {rc}\noutput: {act_out[:300]}\n\n")
    f.write(f"target: {role} \"{name}\" [ref={ref}]\n\n")
    f.write(f"VERIFY (ต้องมี option \"One way\"): {'PASS' if passed else 'FAIL'}\n")
    if opt:
        f.write(f"  evidence: verify.yml:{opt[0]}: {opt[1]}\n")
    f.write(f"ref เดิม {ref} ยังอยู่ใน snapshot ใหม่: {'ใช่' if ref_still else 'ไม่'}\n")
    if ref_still:
        f.write(f"  evidence: verify.yml:{ref_still[0]}: {ref_still[1]}\n")
print(open(f"{D}/act.txt", encoding="utf-8").read())
pw("close")
sys.exit(0 if passed else 1)
