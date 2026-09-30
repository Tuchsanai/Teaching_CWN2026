import sys, re, json, time, os, base64, subprocess
sys.path.insert(0, "/workspace")
from mcp_client import MCP

OUT = "/workspace/lab5/step"
URL = "https://www.google.com/travel/flights?hl=en"
GOAL = "เปิดรายการประเภทตั๋ว (Change ticket type) เพื่อจะเลือก One way"
ACTIONS = ["click", "fill", "press", "stop"]
ROLES = ["button", "combobox", "textbox", "option"]
DENY = re.compile(r"book|sign in|log in|payment|select flight|select fare", re.I)
REF_RE = re.compile(r"^(f\d+)?e\d+$")
SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ACTIONS},
        "ref": {"type": "string"},
        "value": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": ["action", "ref", "value", "reason"],
    "additionalProperties": False,
}

os.makedirs(OUT, exist_ok=True)
m = MCP(f"{OUT}/rpc.jsonl")


def section(text, name):
    mt = re.search(rf"^### {name}\n(.*?)(?=^### |\Z)", text, re.M | re.S)
    return mt.group(1) if mt else None


def call(tool, args=None):
    """ส่ง tools/call ผ่าน MCP client; คืน (text, images, isError)"""
    args = args or {}
    r = m._request("tools/call", {"name": tool, "arguments": args})
    if "error" in r:
        res = {"content": [{"type": "text", "text": r["error"].get("message", "")}], "isError": True}
    else:
        res = r["result"]
    content = res.get("content", [])
    text = "\n".join(c["text"] for c in content if c.get("type") == "text")
    images = [base64.b64decode(c["data"]) for c in content if c.get("type") == "image"]
    return text, images, bool(res.get("isError"))


def get_yaml(text):
    s = section(text, "Snapshot")
    if s is None:
        return None
    f = re.search(r"```(?:yaml)?\n(.*?)```", s, re.S)
    if f:
        return f.group(1)
    lk = re.search(r"\]\(([^)]+)\)", s)
    if lk:
        p = lk.group(1)
        if not os.path.isabs(p):
            p = next((c for c in (os.path.join("/workspace", p), os.path.join("/workspace/mcp-out", p)) if os.path.exists(c)), p)
        return open(p).read()
    return s


def snap(name):
    t, _, err = call("browser_snapshot", {"boxes": True})
    y = get_yaml(t)
    if err or y is None:
        raise SystemExit(f"snapshot {name} failed: {t[:300]}")
    open(f"{OUT}/{name}", "w").write(y)
    return y


def shot(name):
    _, imgs, err = call("browser_take_screenshot", {"type": "png", "scale": "device"})
    if err or not imgs:
        raise SystemExit(f"screenshot {name} failed")
    open(f"{OUT}/{name}", "wb").write(imgs[0])


def parse_line(line):
    """คืน dict(role,name,ref,box,text) หรือ None; รองรับบรรทัดที่ YAML ครอบด้วย '...' (ชื่อมี ': ')"""
    s = line.strip()
    if not s.startswith("- "):
        return None
    s = s[2:]
    if s.startswith("'"):
        end = s.rfind("'")
        s = s[1:end].replace("''", "'")
    mt = re.match(r'^(\w+) "(.*)" (.*)$', s)
    if not mt or mt.group(1) not in ROLES:
        return None
    role, name, rest = mt.groups()
    rf = re.search(r"\[ref=([^\]]+)\]", rest)
    if not rf or not name:
        return None
    bx = re.search(r"\[box=(-?\d+),(-?\d+),(\d+),(\d+)\]", rest)
    return {"role": role, "name": name, "ref": rf.group(1),
            "box": [int(v) for v in bx.groups()] if bx else None}


def trim(line):
    t = re.sub(r" \[box=[^\]]*\]| \[cursor=pointer\]", "", line.rstrip())
    return t[:-1] if t.endswith(":") else t


def elements(yml):
    els, kept = {}, []
    for l in yml.splitlines():
        e = parse_line(l)
        if e:
            els[e["ref"]] = e
            kept.append(trim(l))
    return els, kept


OVERLAY_JS = """() => {
  const [x, y, w, h] = %(box)s;
  const label = %(label)s;
  const NS = 'http://www.w3.org/2000/svg';
  const vw = window.innerWidth, vh = window.innerHeight;
  const root = document.createElement('div');
  root.id = '__step_overlay';
  root.style.cssText = 'position:fixed;left:0;top:0;width:100vw;height:100vh;pointer-events:none;z-index:2147483647';
  const cx = x + w / 2, cy = y + h / 2, pad = 3;
  const rx = w / 2 * Math.SQRT2 + pad, ry = h / 2 * Math.SQRT2 + pad;
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('width', vw); svg.setAttribute('height', vh);
  svg.style.cssText = 'position:absolute;left:0;top:0';
  const el = document.createElementNS(NS, 'ellipse');
  el.setAttribute('cx', cx); el.setAttribute('cy', cy);
  el.setAttribute('rx', rx); el.setAttribute('ry', ry);
  el.setAttribute('fill', 'none'); el.setAttribute('stroke', '#ff0000'); el.setAttribute('stroke-width', '4');
  svg.appendChild(el); root.appendChild(svg);
  const box = document.createElement('div');
  box.textContent = label;
  box.style.cssText = 'position:absolute;left:0;top:0;background:#ff0000;color:#fff;font:bold 18px sans-serif;padding:6px 12px;border-radius:6px;white-space:nowrap';
  root.appendChild(box);
  document.body.appendChild(root);
  const lw = box.offsetWidth, lh = box.offsetHeight, gap = 10;
  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));
  const cands = {
    below: [clamp(cx - lw / 2, 4, vw - lw - 4), cy + ry + gap],
    above: [clamp(cx - lw / 2, 4, vw - lw - 4), cy - ry - gap - lh],
    right: [cx + rx + gap, clamp(cy - lh / 2, 4, vh - lh - 4)],
    left: [cx - rx - gap - lw, clamp(cy - lh / 2, 4, vh - lh - 4)],
  };
  const items = [...document.querySelectorAll('a,button,input,select,textarea,[role],[tabindex]')]
    .filter(n => !root.contains(n)).map(n => n.getBoundingClientRect()).filter(r => r.width > 0 && r.height > 0);
  let best = null;
  for (const [k, [lx, ly]] of Object.entries(cands)) {
    if (lx < 0 || ly < 0 || lx + lw > vw || ly + lh > vh) continue;
    if (lx < cx + rx && lx + lw > cx - rx && ly < cy + ry && ly + lh > cy - ry) continue;
    const hits = items.filter(r => lx < r.right && lx + lw > r.left && ly < r.bottom && ly + lh > r.top).length;
    if (!best || hits < best.hits) best = {k, lx, ly, hits};
  }
  if (!best) best = {k: 'below', lx: cands.below[0], ly: cands.below[1], hits: -1};
  box.style.left = best.lx + 'px'; box.style.top = best.ly + 'px';
  return JSON.stringify({placement: best.k, overlapping_elements: best.hits, label_box: [best.lx, best.ly, lw, lh],
                         ellipse: {cx, cy, rx, ry}});
}"""
REMOVE_JS = "() => { const n = document.getElementById('__step_overlay'); if (n) n.remove(); return document.getElementById('__step_overlay') === null; }"


def close_and_exit(msg=None):
    call("browser_close")
    m.close()
    if msg:
        print(msg)


m.initialize()

# ---------- 1. Observe ----------
call("browser_navigate", {"url": URL})
call("browser_wait_for", {"time": 2})
snapshot_yml = snap("snapshot.yml")
shot("observe.png")

# ---------- 2. Decide ----------
els, kept = elements(snapshot_yml)
prompt = f"""บทบาท: คุณเป็นผู้ช่วยตัดสินใจสำหรับการทำงานอัตโนมัติบนหน้าเว็บ คุณไม่ได้กดเอง โค้ดของผู้ใช้จะเป็นฝ่ายตรวจคำตอบของคุณแล้วลงมือกดเอง

เป้าหมายของ step นี้: {GOAL}
หน้าเว็บ: {URL}

รายการ element ที่โต้ตอบได้บนหน้าตอนนี้ (snapshot ที่ตัดแล้ว รูปแบบ role "ชื่อ" [ref=...]):
{chr(10).join(kept)}

กติกา:
- เลือก ref จากรายการข้างบนเท่านั้น ห้ามคิด ref เอง ห้ามใช้ CSS selector
- action ต้องเป็นหนึ่งใน click, fill, press, stop
- ถ้าไม่มี element ที่ตรงกับเป้าหมาย ให้ตอบ action = stop และ ref เป็นสตริงว่าง
- ถ้า action ไม่ใช่ fill/press ให้ value เป็นสตริงว่าง
- 1 step = 1 action เท่านั้น

รูปแบบคำตอบ: JSON เท่านั้น {{"action": "click|fill|press|stop", "ref": "...", "value": "...", "reason": "เหตุผลสั้น ๆ"}}
"""
open(f"{OUT}/prompt.txt", "w").write(prompt)
cp = subprocess.run(
    ["yolo1", "-p", "--model", "haiku", "--effort", "low", "--output-format", "json",
     "--json-schema", json.dumps(SCHEMA), "--no-session-persistence", "--strict-mcp-config",
     "--tools", "", "--disallowedTools", "mcp__playwright"],
    input=prompt, capture_output=True, text=True, timeout=300)
llm_raw = cp.stdout
try:
    llm = json.loads(llm_raw).get("structured_output")
except ValueError:
    llm = None
if not isinstance(llm, dict):
    llm = {}

# ---------- 3. Validate ----------
action, ref = llm.get("action"), llm.get("ref")
ref_s = ref if isinstance(ref, str) else ""
el = els.get(ref_s)
checks = []


def chk(name, ok, detail):
    checks.append({"check": name, "result": "pass" if ok else "fail", "detail": detail})


chk("action_in_allowlist", action in ACTIONS, f"action={action!r} allowlist={ACTIONS}")
chk("ref_format", bool(REF_RE.match(ref_s)), f"ref={ref!r} pattern=^(f\\d+)?e\\d+$")
chk("ref_in_latest_snapshot", el is not None, f"ref {ref_s!r} {'พบ' if el else 'ไม่พบ'} ใน snapshot.yml")
chk("role_allowed", bool(el) and el["role"] in ROLES, f"role จาก snapshot={el['role'] if el else None} allowed={ROLES}")
chk("name_not_denylisted", bool(el) and not DENY.search(el["name"]),
    f"name จาก snapshot={el['name'] if el else None!r} denylist={DENY.pattern}")
chk("action_executable_in_this_step", action == "click", f"step นี้ทำได้เฉพาะ click; action={action!r}")
passed = all(c["result"] == "pass" for c in checks)
decision = {"goal": GOAL, "llm_answer": llm, "element_from_snapshot": el, "checks": checks, "passed": passed}

if not passed:
    json.dump(decision, open(f"{OUT}/decision.json", "w"), ensure_ascii=False, indent=2)
    print("validation FAILED -> ไม่เรียก tool เพิ่ม")
    for c in checks:
        print(c)
    if not llm:
        print("yolo1 raw:", llm_raw[:500], cp.stderr[:500])
    close_and_exit()
    raise SystemExit(1)

# overlay + หลักฐานก่อนกด
label = f"Step 1 · click {ref}"
t, _, err = call("browser_evaluate", {"function": OVERLAY_JS % {"box": json.dumps(el["box"]), "label": json.dumps(label)}})
decision["overlay"] = {"isError": err, "result": (section(t, "Result") or t).strip()}
shot("page.png")
t2, _, err2 = call("browser_evaluate", {"function": REMOVE_JS})
decision["overlay_removed"] = {"isError": err2, "result": (section(t2, "Result") or t2).strip()}
json.dump(decision, open(f"{OUT}/decision.json", "w"), ensure_ascii=False, indent=2)

# ---------- 4. Act ----------
click_args = {"target": ref}
ct, _, cerr = call("browser_click", click_args)
ran = [l for l in (section(ct, "Ran Playwright code") or "").splitlines() if l.startswith("await page")]

# ---------- 5. Verify ----------
verify_yml = snap("verify.yml")
vlines = verify_yml.splitlines()
one_way = [(i + 1, l.strip()) for i, l in enumerate(vlines) if re.search(r'option "One way"|option .*One way', l)]
old_ref = [(i + 1, l.strip()) for i, l in enumerate(vlines) if f"[ref={ref}]" in l]
ok = bool(one_way) and not cerr
with open(f"{OUT}/act.txt", "w") as f:
    f.write(f"→ tools/call browser_click {json.dumps(click_args, ensure_ascii=False)}\n")
    f.write(f"isError: {str(cerr).lower()}\n")
    for l in ran:
        f.write(f"{l}\n")
    f.write("\nVerify (verify.yml):\n")
    if one_way:
        for n, l in one_way:
            f.write(f'  PASS พบ option "One way" ที่ verify.yml:{n}: {l}\n')
    else:
        f.write('  FAIL ไม่พบ option "One way" ใน verify.yml\n')
    if old_ref:
        for n, l in old_ref:
            f.write(f"  ref เดิม {ref} ยังอยู่ใน snapshot ใหม่ที่ verify.yml:{n}: {l}\n")
    else:
        f.write(f"  ref เดิม {ref} ไม่อยู่ใน snapshot ใหม่แล้ว\n")
    f.write(f"ผล: {'PASS' if ok else 'FAIL'}\n")

close_and_exit()
print(open(f"{OUT}/act.txt").read())
print(json.dumps(decision, ensure_ascii=False, indent=2))
