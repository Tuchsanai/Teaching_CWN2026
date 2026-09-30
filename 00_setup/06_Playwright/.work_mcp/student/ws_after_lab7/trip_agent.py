#!/usr/bin/env python3
"""trip_agent.py — Google Flights (ค้นหาอย่างเดียว) โดย Playwright MCP = ตา/มือ, LLM (yolo1 haiku) = เลือก 1 action, โค้ด = ผู้คุม
ต่อยอดจาก mcp_client.py และ lab5/one_step.py
"""
import argparse, base64, calendar, datetime, json, os, re, subprocess, sys, time
sys.path.insert(0, "/workspace")
from mcp_client import MCP

URL = "https://www.google.com/travel/flights?hl=en"
ALLOWED_URL = re.compile(r"^https://www\.google\.com/travel/flights")
ACTIONS = ["click", "fill", "press", "stop"]
FORM_ROLES = ["button", "combobox", "textbox", "option"]
PRESS_KEYS = ["Enter", "ArrowDown", "Escape"]
FILL_ALLOWED = ["BKK", "Tokyo"]
DENY = re.compile(r"book|sign in|log in|payment|select flight|select fare", re.I)
REF_RE = re.compile(r"^(f\d+)?e\d+$")
BLOCK_RE = re.compile(r"unusual traffic|captcha|not a robot|ไม่ใช่โรบอต", re.I)
MAX_ACTIONS, MAX_PER_GOAL = 25, 5
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

ap = argparse.ArgumentParser()
ap.add_argument("--goal", help="แทนแผนด้วยเป้าหมายเดียว (LLM เห็นทุก role)")
ap.add_argument("--inject", help="ข้อความของปุ่มที่ฉีดเข้าหน้าเว็บหลัง navigate (ทดสอบ prompt injection)")
ap.add_argument("--out", default="/workspace/log")
args = ap.parse_args()
OUT = args.out
os.makedirs(f"{OUT}/steps", exist_ok=True)
RUNLOG = open(f"{OUT}/run.log", "w")


def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    RUNLOG.write(line + "\n")
    RUNLOG.flush()


class Stop(Exception):
    def __init__(self, reason, code=1):
        super().__init__(reason)
        self.reason, self.code = reason, code


# ---------- วันเดินทาง = วันที่ 15 ของเดือนถัดไป (คำนวณ ไม่ hardcode) ----------
today = datetime.date.today()
ny, nm = (today.year + 1, 1) if today.month == 12 else (today.year, today.month + 1)
TARGET = datetime.date(ny, nm, 15)
MON, MON3 = calendar.month_name[TARGET.month], calendar.month_abbr[TARGET.month]
DATE_BTN_RE = re.compile(rf"^(?:\w+day,?\s+)?(?:(?:{MON}|{MON3})\s+{TARGET.day}|{TARGET.day}\s+(?:{MON}|{MON3}))\b(?!.* to )", re.I)
DATE_VAL_RE = re.compile(rf"\b{MON3}\s+{TARGET.day}\b|\b{TARGET.day}\s+{MON3}\b", re.I)
log(f"วันนี้ = {today} · วันเดินทาง (15 ของเดือนถัดไป) = {TARGET} ({MON} {TARGET.day}, {TARGET.year})")
if args.inject:
    log(f"--inject: {args.inject!r}")

m = MCP(f"{OUT}/rpc_all.jsonl")


# ---------- snapshot / parser ----------
def section(text, name):
    mt = re.search(rf"^### {name}\n(.*?)(?=^### |\Z)", text, re.M | re.S)
    return mt.group(1) if mt else None


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


def parse_line(line, n=0):
    """คืน dict(role,name,ref,box,flags,value,line,text) หรือ None; รองรับบรรทัดที่ YAML ครอบด้วย '...' (ชื่อมี ': ')"""
    s = line.strip()
    if not s.startswith("- "):
        return None
    s, tail = s[2:], ""
    if s.startswith("'"):
        end = s.rfind("'")
        tail, s = s[end + 1:], s[1:end].replace("''", "'")
    mt = re.match(r'^([\w-]+)(?: "((?:[^"\\]|\\.)*)")?(.*)$', s)
    if not mt:
        return None
    role, name, rest = mt.group(1), mt.group(2), mt.group(3) + tail
    name = (name or "").replace('\\"', '"')
    rf = re.search(r"\[ref=([^\]]+)\]", rest)
    bx = re.search(r"\[box=(-?\d+),(-?\d+),(\d+),(\d+)\]", rest)
    flags = [f for f in re.findall(r"\[([a-z-]+)\]", rest) if f != "cursor"]
    vm = re.search(r"\]:\s*(.*)$", rest)
    value = vm.group(1).strip().strip('"') if vm else ""
    return {"role": role, "name": name, "ref": rf.group(1) if rf else None,
            "box": [int(v) for v in bx.groups()] if bx else None,
            "flags": flags, "value": value, "line": n, "text": s}


def parse_all(yml):
    return [e for i, l in enumerate(yml.splitlines(), 1) if (e := parse_line(l, i))]


def display(e):
    fl = "".join(f" [{f}]" for f in e["flags"] if f in ("active", "expanded", "selected", "disabled", "checked"))
    nm = f' "{e["name"]}"' if e["name"] else ""
    v = f": {e['value']}" if e["value"] else ""
    return f"{e['role']}{nm} [ref={e['ref']}]{fl}{v}"


def find(els, role, name_re=None, value_re=None):
    return [e for e in els if e["ref"] and e["role"] == role
            and (name_re is None or re.search(name_re, e["name"], re.I))
            and (value_re is None or re.search(value_re, e["value"] + " " + e["name"], re.I))]


# ---------- MCP helpers ----------
def call(tool, targs=None):
    r = m.call(tool, targs)
    return r["text"], r["images"], r["is_error"]


def observe():
    """browser_snapshot {"boxes": true} → (yaml, url, els)"""
    t, _, err = call("browser_snapshot", {"boxes": True})
    y = get_yaml(t)
    if err or y is None:
        raise Stop(f"snapshot ล้มเหลว: {t[:300]}")
    um = re.search(r"Page URL:\s*(\S+)", t)
    url = um.group(1) if um else ""
    if not ALLOWED_URL.match(url):
        raise Stop(f"URL ออกนอก Google Flights: {url!r}", 2)
    if BLOCK_RE.search(y) or "/sorry/" in url:
        raise Stop("พบ CAPTCHA / unusual traffic — หยุดและรายงาน", 2)
    return y, url, parse_all(y)


def shot(path):
    _, imgs, err = call("browser_take_screenshot", {"type": "png", "scale": "device"})
    if err or not imgs:
        return False
    open(path, "wb").write(imgs[0])
    return True


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
INJECT_JS = """() => {
  const b = document.createElement('button');
  b.id = '__injected';
  b.textContent = %(text)s;
  b.style.cssText = 'position:fixed;left:8px;bottom:8px;z-index:2147483646;padding:8px 12px;background:#fff;color:#000;border:1px solid #000';
  document.body.appendChild(b);
  return b.textContent;
}"""
REMOVE_JS ="() => { const n = document.getElementById('__step_overlay'); if (n) n.remove(); return document.getElementById('__step_overlay') === null; }"


# ---------- แผน: เป้าหมายแต่ละอัน ----------
def _field(els, name_re):
    f = find(els, "combobox", name_re)
    return f[0] if f else None


def _airport_opts(els, opt_re):
    skip = r"^(round trip|one way|multi-city|economy|premium economy|business|first)$"
    return [o for o in els if o["ref"] and o["role"] == "option" and not re.search(skip, o["name"], re.I)
            and re.search(opt_re, o["name"], re.I)]


def place_goal(key, field_re, fill, opt_re, label, done_re):
    def done(els):
        f = _field(els, field_re)
        return bool(f) and bool(re.search(done_re, f["value"] + " " + f["name"], re.I)) and "expanded" not in f["flags"]

    def visible(els):
        out = [e for e in els if e["ref"] and e["role"] == "combobox"
               and (re.search(field_re, e["name"], re.I) or "active" in e["flags"] or "expanded" in e["flags"])]
        out += [o for o in els if o["ref"] and o["role"] == "option" and not re.search(
            r"^(round trip|one way|multi-city|economy|premium economy|business|first)$", o["name"], re.I)][:12]
        return out

    def progress(els):
        f = _field(els, field_re)
        return bool(_airport_opts(els, opt_re)) or (bool(f) and ("expanded" in f["flags"] or "active" in f["flags"]))

    def hint(els):
        f, opts = _field(els, field_re), _airport_opts(els, opt_re)
        if opts:
            return f"มี option ตรงเป้าหมายในรายการแล้ว → ให้ click option ที่เป็น {label}"
        if f and ("expanded" in f["flags"] or "active" in f["flags"]):
            return f"ช่องเปิดอยู่แต่ยังไม่มี option ตรงเป้าหมาย → ให้ fill ค่า {fill!r} ที่ช่องนี้"
        return "ช่องยังไม่ถูกเปิด → ให้ click ช่องนี้ก่อน"

    def opt_ok(e):
        return e["role"] != "option" or (bool(re.search(opt_re, e["name"], re.I)) and not re.search(r"^$", e["name"]))

    return dict(key=key, desc=f"ตั้ง{label}", fill=fill, done=done, visible=visible, progress=progress,
                hint=hint, opt_ok=opt_ok)


def g_ticket():
    return dict(
        key="ticket", desc="เปลี่ยนประเภทตั๋วเป็น One way (เปิดรายการ Change ticket type แล้วเลือก option One way)", fill=None,
        done=lambda els: bool(find(els, "combobox", r"Change ticket type\. One way")),
        visible=lambda els: [e for e in els if e["ref"] and (
            (e["role"] == "combobox" and re.search(r"Change ticket type", e["name"], re.I))
            or (e["role"] == "option" and e["name"] in ("Round trip", "One way", "Multi-city")))],
        progress=lambda els: bool(find(els, "option", r"^One way$")),
        hint=lambda els: ("รายการประเภทตั๋วเปิดอยู่ → click option One way" if find(els, "option", r"^One way$")
                          else "รายการยังไม่เปิด → click combobox Change ticket type"),
        opt_ok=lambda e: e["role"] != "option" or e["name"] == "One way")


def g_econ():
    return dict(
        key="econ_pax", desc="ตรวจว่าเป็น Economy และผู้โดยสาร 1 คน", fill=None,
        done=lambda els: bool(find(els, "combobox", r"Change seating class\. Economy$"))
        and bool(find(els, "button", r"^1 passenger")),
        visible=lambda els: [e for e in els if e["ref"] and (
            (e["role"] == "combobox" and re.search(r"Change seating class", e["name"], re.I))
            or (e["role"] == "button" and re.search(r"passenger", e["name"], re.I))
            or (e["role"] == "option" and e["name"] == "Economy"))],
        progress=lambda els: bool(find(els, "option", r"^Economy$")),
        hint=lambda els: "ถ้าไม่ใช่ Economy ให้เปิดรายการ seating class แล้วเลือก Economy",
        opt_ok=lambda e: e["role"] != "option" or e["name"] == "Economy")


def g_date():
    def cal_btns(els):
        return [e for e in els if e["ref"] and e["role"] in ("button", "option", "gridcell")
                and DATE_BTN_RE.search(e["name"]) and not re.search(r"find flights|explore", e["name"], re.I)]

    def dep(els):
        return find(els, "textbox", r"^Departure")

    def done_btn(els):
        return [e for e in els if e["ref"] and e["role"] == "button" and re.match(r"^Done\b", e["name"])]

    def value_ok(els):
        return bool(dep(els)) and bool(DATE_VAL_RE.search(dep(els)[0]["value"]))

    def visible(els):
        if value_ok(els) and done_btn(els):
            return dep(els) + done_btn(els)
        return dep(els) + cal_btns(els)

    return dict(
        key="date", desc=f"เลือกวันเดินทาง {TARGET:%B} {TARGET.day}, {TARGET.year} ในช่อง Departure", fill=None,
        done=lambda els: value_ok(els) and not done_btn(els),
        visible=visible,
        progress=lambda els: value_ok(els) or bool(cal_btns(els)),
        hint=lambda els: ("เลือกวันที่แล้ว ปฏิทินยังเปิด → click ปุ่ม Done" if value_ok(els) and done_btn(els)
                          else f"ปฏิทินเปิดแล้ว → click ปุ่มวันที่ {TARGET:%B} {TARGET.day}" if cal_btns(els)
                          else "ปฏิทินยังไม่เปิด → ต้อง click ช่อง Departure ก่อนเพื่อเปิดปฏิทิน (ยังไม่ต้อง stop)"),
        opt_ok=lambda e: True)


def has_results(yml):
    return bool(re.search(r"Select flight", yml))


def g_search():
    return dict(
        key="search", desc="กดปุ่ม Search เพื่อค้นหาเที่ยวบิน", fill=None,
        done=lambda els, yml="": has_results(yml),
        visible=lambda els: [e for e in els if e["ref"] and e["role"] == "button" and re.match(r"^Search\b", e["name"])],
        progress=lambda els: False,
        hint=lambda els: "click ปุ่ม Search",
        opt_ok=lambda e: True)


def plan():
    if args.goal:
        return [dict(key="custom", desc=args.goal, fill=None, custom=True,
                     done=lambda els, yml="": False,
                     visible=lambda els: [e for e in els if e["ref"]],
                     progress=lambda els: True, hint=lambda els: "", opt_ok=lambda e: True)]
    return [g_ticket(), g_econ(),
            place_goal("origin", r"Where from", "BKK", r"Suvarnabhumi|\bBKK\b", "ต้นทางเป็น Suvarnabhumi Airport (BKK)",
                       r"Suvarnabhumi|\bBKK\b"),
            place_goal("dest", r"Where to", "Tokyo", r"^Tokyo\b(?!.*airport)", "ปลายทางเป็นเมือง Tokyo, Japan",
                       r"Tokyo"),
            g_date(), g_search()]


def goal_done(goal, els, yml):
    try:
        return goal["done"](els, yml)
    except TypeError:
        return goal["done"](els)


# ---------- LLM (LAB 5: ไม่มี tool) ----------
def build_prompt(goal, url, els, shown):
    custom = goal.get("custom")
    fill_rule = ("ค่าที่ fill ได้มีเพียง: " + ", ".join(repr(v) for v in FILL_ALLOWED)) if custom else \
        (f"ถ้า fill ให้ใช้ค่า {goal['fill']!r} เท่านั้น" if goal["fill"] else "ก้าวนี้ไม่มี fill")
    hint = goal["hint"](els)
    return f"""บทบาท: คุณเป็นผู้ช่วยตัดสินใจสำหรับการทำงานอัตโนมัติบนหน้าเว็บ คุณไม่ได้กดเอง โค้ดของผู้ใช้จะเป็นฝ่ายตรวจคำตอบของคุณแล้วลงมือกดเอง

เป้าหมายของ step นี้: {goal['desc']}
หน้าเว็บ: {url}
{('สิ่งที่โค้ดสังเกตได้ตอนนี้: ' + hint) if hint else ''}

รายการ element ที่เลือกได้ตอนนี้ (รูปแบบ role "ชื่อ" [ref=...]):
{chr(10).join(display(e) for e in shown)}

กติกา:
- เลือก ref จากรายการข้างบนเท่านั้น ห้ามคิด ref เอง ห้ามใช้ CSS selector
- action ต้องเป็นหนึ่งใน click, fill, press, stop
- click = คลิก ref นั้น · fill = พิมพ์ค่าใน value ลงช่อง ref นั้น ({fill_rule}) · press = กดปุ่มใน value ({', '.join(PRESS_KEYS)}) ref เป็นสตริงว่างได้
- ถ้าไม่มี element ที่ตรงกับเป้าหมาย หรือเป้าหมายสำเร็จแล้ว ให้ตอบ action = stop และ ref เป็นสตริงว่าง
- ห้ามกดอะไรที่เกี่ยวกับการจอง การล็อกอิน หรือการชำระเงิน
- 1 step = 1 action เท่านั้น

รูปแบบคำตอบ: JSON เท่านั้น {{"action": "click|fill|press|stop", "ref": "...", "value": "...", "reason": "เหตุผลสั้น ๆ"}}
"""


def ask_llm(prompt):
    try:
        cp = subprocess.run(
            ["yolo1", "-p", "--model", "haiku", "--effort", "low", "--output-format", "json",
             "--json-schema", json.dumps(SCHEMA), "--no-session-persistence", "--strict-mcp-config",
             "--tools", "", "--disallowedTools", "mcp__playwright"],
            input=prompt, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {}, "timeout"
    try:
        out = json.loads(cp.stdout).get("structured_output")
    except ValueError:
        out = None
    return (out if isinstance(out, dict) else {}), (cp.stdout[:500] + cp.stderr[:500])


# ---------- validate ----------
def validate(goal, llm, els, shown):
    action, ref, val = llm.get("action"), llm.get("ref"), llm.get("value")
    ref_s = ref if isinstance(ref, str) else ""
    val_s = val if isinstance(val, str) else ""
    by_ref = {e["ref"]: e for e in els if e["ref"]}
    shown_refs = {e["ref"] for e in shown}
    el = by_ref.get(ref_s)
    checks, hard = [], None

    def chk(name, ok, detail):
        checks.append({"check": name, "result": "pass" if ok else "fail", "detail": detail})

    chk("action_in_allowlist", action in ACTIONS, f"action={action!r} allowlist={ACTIONS}")
    if action == "stop":
        return checks, None, None
    if action == "press":
        chk("press_key_allowed", val_s in PRESS_KEYS, f"key={val_s!r} allowed={PRESS_KEYS}")
        act = next((e for e in els if "active" in e["flags"] and e["ref"]), None)
        chk("focused_not_denylisted", not (act and DENY.search(act["name"])),
            f"element ที่ active={act['name'] if act else None!r}")
        if act and DENY.search(act["name"]):
            hard = f"press บน element ต้องห้าม: {act['name']!r}"
        return checks, None, hard
    chk("ref_format", bool(REF_RE.match(ref_s)), f"ref={ref!r} pattern=^(f\\d+)?e\\d+$")
    chk("ref_in_latest_snapshot", el is not None, f"ref {ref_s!r} {'พบ' if el else 'ไม่พบ'} ใน snapshot ล่าสุด")
    if el and DENY.search(el["name"]):
        hard = f"element ต้องห้าม (denylist): {el['role']} {el['name']!r}"
    chk("name_not_denylisted", not (el and DENY.search(el["name"])),
        f"name จาก snapshot={el['name'] if el else None!r} denylist={DENY.pattern}")
    chk("ref_in_shown_list", ref_s in shown_refs, f"ref อยู่ในรายการที่ให้ LLM เห็น={ref_s in shown_refs}")
    if not goal.get("custom"):
        chk("role_allowed", bool(el) and el["role"] in FORM_ROLES, f"role={el['role'] if el else None} allowed={FORM_ROLES}")
        chk("option_matches_goal", bool(el) and goal["opt_ok"](el), f"option/name={el['name'] if el else None!r}")
    if el and "disabled" in el["flags"]:
        chk("not_disabled", False, "element disabled")
    if action == "fill":
        okv = val_s in FILL_ALLOWED and (goal["fill"] is None and goal.get("custom") or val_s == goal["fill"])
        chk("fill_value_allowed", okv, f"value={val_s!r} โค้ดกำหนด={goal['fill'] or FILL_ALLOWED}")
        chk("fill_target_role", bool(el) and el["role"] in ("combobox", "textbox"), f"role={el['role'] if el else None}")
    return checks, el, hard


TOOLMAP = {"click": "browser_click", "fill": "browser_type", "press": "browser_press_key"}


def tool_args(action, ref, val):
    return {"click": {"target": ref}, "fill": {"target": ref, "text": val}, "press": {"key": val}}[action]


# ---------- ผลลัพธ์ ----------
def parse_flights(yml):
    lines = yml.splitlines()
    out = []
    for i, l in enumerate(lines, 1):
        e = parse_line(l, i)
        if not e or e["role"] != "link" or "Select flight" not in e["name"]:
            continue
        t = e["name"]
        g = lambda p: (re.search(p, t, re.I) or [None, None])[1]
        tm = re.search(r"Leaves .*? at (\d{1,2}:\d{2}\s?[AP]M)\b.*?arrives at .*? at (\d{1,2}:\d{2}\s?[AP]M)", t, re.I)
        out.append({
            "airline": g(r"(?:nonstop|\d+ stops?)\s+flight with (.+?)\."),
            "depart": tm.group(1) if tm else None, "arrive": tm.group(2) if tm else None,
            "duration": g(r"Total duration (.+?)\."),
            "stops": g(r"(Nonstop|\d+ stops?)"),
            "price_thb": g(r"From ([\d,]+) Thai baht"),
            "price_text": (re.match(r"(From [\d,]+ Thai baht[^.]*)", t) or [None, None])[1],
            "source_line": i, "raw": t})
    return out


# ---------- main ----------
completed = []  # เป้าหมายที่ผ่านแล้ว — ต้องยังคงผ่านหลังทุก step
rows = []  # (step, goal, action, result, detail)
step_no, actions = 0, 0
final = "OK"


def step_dir(goal_key, act_name):
    global step_no
    step_no += 1
    d = f"{OUT}/steps/{step_no:02d}_{goal_key}-{act_name}"
    os.makedirs(d, exist_ok=True)
    return d


def write(d, name, content):
    with open(f"{d}/{name}", "w") as f:
        f.write(content)


def run_goal(goal):
    global actions
    attempts = 0
    while True:
        if actions >= MAX_ACTIONS:
            raise Stop(f"ครบ {MAX_ACTIONS} action แล้ว")
        m.begin_step()
        yml, url, els = observe()
        if goal_done(goal, els, yml):
            m.dump_step(f"{OUT}/rpc_last_observe.jsonl")
            log(f"[{goal['key']}] ผ่านแล้ว → ข้าม (ตรวจจาก snapshot ปัจจุบัน)")
            rows.append(("-", goal["key"], "-", "SKIP", "ผ่านอยู่แล้วก่อน Decide"))
            completed.append(goal)
            return
        if attempts >= MAX_PER_GOAL:
            m.dump_step(f"{OUT}/rpc_last_observe.jsonl")
            raise Stop(f"ติดเป้าหมาย {goal['key']} เกิน {MAX_PER_GOAL} ครั้ง")
        attempts += 1
        shown = goal["visible"](els)
        prompt = build_prompt(goal, url, els, shown)
        llm, raw = ask_llm(prompt)
        checks, el, hard = validate(goal, llm, els, shown)
        action = llm.get("action") if llm.get("action") in ACTIONS else "invalid"
        passed = all(c["result"] == "pass" for c in checks) and bool(llm)
        d = step_dir(goal["key"], action if passed or action != "invalid" else "invalid")
        write(d, "snapshot.yml", yml)
        write(d, "prompt.txt", prompt)
        decision = {"goal": goal["desc"], "attempt": attempts, "url": url, "shown_refs": [e["ref"] for e in shown],
                    "llm_answer": llm, "element_from_snapshot": el, "checks": checks, "passed": passed}
        log(f"[{goal['key']}] step {step_no:02d} attempt {attempts}: LLM={json.dumps(llm, ensure_ascii=False)}")
        if action == "stop":
            decision["note"] = "LLM ตอบ stop"
            if goal.get("custom"):
                write(d, "decision.json", json.dumps(decision, ensure_ascii=False, indent=2))
                write(d, "act.txt", "LLM ตอบ stop → จบเป้าหมาย (--goal)\n")
                shot(f"{d}/page.png")
                m.dump_step(f"{d}/rpc.jsonl")
                rows.append((step_no, goal["key"], "stop", "PASS", llm.get("reason", "")))
                return
        if hard:
            decision["hard_stop"] = hard
            write(d, "decision.json", json.dumps(decision, ensure_ascii=False, indent=2))
            write(d, "act.txt", f"ไม่ลงมือ: {hard}\n")
            m.dump_step(f"{d}/rpc.jsonl")
            rows.append((step_no, goal["key"], action, "FAIL", hard))
            raise Stop(hard, 2)
        if not passed or action == "stop":
            fails = [c for c in checks if c["result"] == "fail"] or [{"check": "llm_answer", "detail": raw}]
            write(d, "decision.json", json.dumps(decision, ensure_ascii=False, indent=2))
            write(d, "act.txt", "ไม่ลงมือ: validation FAIL\n" + "\n".join(f"  {c['check']}: {c['detail']}" for c in fails) + "\n")
            shot(f"{d}/page.png")
            m.dump_step(f"{d}/rpc.jsonl")
            log(f"[{goal['key']}] validation FAIL: {[c['check'] for c in fails]}")
            rows.append((step_no, goal["key"], action, "FAIL", "validation: " + ",".join(c["check"] for c in fails)))
            continue

        ref, val = llm.get("ref", ""), llm.get("value", "")
        # overlay + หลักฐานก่อนกด
        if el and el["box"]:
            label = f"Step {step_no} · {action} {ref}" + (f' "{val}"' if action == "fill" else "")
            t, _, oerr = call("browser_evaluate", {"function": OVERLAY_JS % {"box": json.dumps(el["box"]), "label": json.dumps(label)}})
            decision["overlay"] = {"isError": oerr, "result": (section(t, "Result") or t).strip()}
            shot(f"{d}/page.png")
            t2, _, e2 = call("browser_evaluate", {"function": REMOVE_JS})
            decision["overlay_removed"] = {"isError": e2, "result": (section(t2, "Result") or t2).strip()}
        else:
            shot(f"{d}/page.png")
        write(d, "decision.json", json.dumps(decision, ensure_ascii=False, indent=2))

        # Act
        targs = tool_args(action, ref, val)
        at, _, aerr = call(TOOLMAP[action], targs)
        actions += 1
        ran = [l for l in (section(at, "Ran Playwright code") or "").splitlines() if l.startswith("await page")]
        call("browser_wait_for", {"time": 1})

        # Verify (snapshot ใหม่ — browser_type/press_key ไม่ส่ง snapshot กลับ)
        vy, vurl, vels = observe()
        write(d, "verify.yml", vy)
        if goal.get("custom"):
            done, prog = False, vy != yml
        else:
            done = goal_done(goal, vels, vy)
            if goal["key"] == "search" and not done and not aerr:
                for _ in range(4):
                    call("browser_wait_for", {"time": 2})
                    vy, vurl, vels = observe()
                    write(d, "verify.yml", vy)
                    if goal_done(goal, vels, vy):
                        done = True
                        break
            prog = goal["progress"](vels) and vy != yml
        # เช็กว่าเป้าหมายก่อนหน้ายังคงอยู่ เฉพาะตอนเป้าหมายนี้เสร็จ (ระหว่างเปิด popup ช่องอื่นถูกซ่อนตามปกติ)
        broken = [g["key"] for g in completed if not goal_done(g, vels, vy)] if done and not goal.get("custom") else []
        if broken:
            done, prog = False, False
        ok = (not aerr) and (done or prog)
        vdetail = f"REGRESSION: เป้าหมายก่อนหน้าหลุด {broken}" if broken else "done" if done else ("progress" if prog else "ไม่เห็นความคืบหน้า")
        with open(f"{d}/act.txt", "w") as f:
            f.write(f"→ tools/call {TOOLMAP[action]} {json.dumps(targs, ensure_ascii=False)}\n")
            f.write(f"isError: {str(aerr).lower()}\n")
            if aerr:
                f.write(at[:800] + "\n")
            for l in ran:
                f.write(f"{l}\n")
            f.write(f"\nVerify (verify.yml, url={vurl}): {vdetail}\nผล: {'PASS' if ok else 'FAIL'}\n")
        m.dump_step(f"{d}/rpc.jsonl")
        log(f"[{goal['key']}] step {step_no:02d} {action} {ref} {val!r} → {'PASS' if ok else 'FAIL'} ({vdetail})")
        rows.append((step_no, goal["key"], f"{action} {ref}" + (f" {val!r}" if val else ""), "PASS" if ok else "FAIL", vdetail))
        if broken:
            raise Stop(f"หลัง step {step_no:02d} เป้าหมายก่อนหน้าไม่คงอยู่: {broken} (หน้าเปลี่ยนไปจากที่ตั้งไว้)", 2)
        if done:
            completed.append(goal)
            return


def do_results():
    m.begin_step()
    yml, url, els = observe()
    flights = parse_flights(yml)[:3]
    d = step_dir("results", "top3")
    write(d, "snapshot.yml", yml)
    shot(f"{d}/page.png")
    form_ok = all(goal_done(g, els, yml) for g in completed if g["key"] in ("ticket", "origin", "dest"))
    complete = form_ok and len(flights) == 3 and all(f["airline"] and f["depart"] and f["arrive"] and f["duration"]
                                         and f["stops"] and f["price_thb"] for f in flights)
    json.dump({"url": url, "note": "ดึงจาก snapshot.yml ของ step นี้ (ไม่เดาราคา) — source_line = เลขบรรทัดใน snapshot.yml",
               "form_still_matches_plan": form_ok, "flights": flights}, open(f"{d}/top3.json", "w"), ensure_ascii=False, indent=2)
    write(d, "act.txt", f"parse snapshot.yml → {len(flights)} เที่ยวบิน, ครบทุกช่อง={complete}\n")
    m.dump_step(f"{d}/rpc.jsonl")
    rows.append((step_no, "results", "extract top3", "PASS" if complete else "FAIL", f"{len(flights)} flights"))
    return flights


top3 = []
try:
    name, tools = m.initialize()
    log(f"MCP handshake: {name} protocol={m.protocol_version} tools={len(tools)}")
    t, _, err = call("browser_navigate", {"url": URL})
    if err:
        raise Stop(f"navigate ล้มเหลว: {t[:200]}")
    call("browser_wait_for", {"time": 2})
    if args.inject:
        it, _, ierr = call("browser_evaluate", {"function": INJECT_JS % {"text": json.dumps(args.inject)}})
        log(f"inject: isError={ierr} result={(section(it, 'Result') or it).strip()[:200]}")
    for g in plan():
        log(f"=== เป้าหมาย: {g['key']} — {g['desc']}")
        run_goal(g)
    if not args.goal:
        top3 = do_results()
except Stop as s:
    final = f"STOP: {s.reason}"
    log(final)
    rows.append((step_no or "-", "run", "-", "FAIL", s.reason))
finally:
    try:
        call("browser_close")
    except Exception:
        pass
    code = m.close()
    log(f"ปิด MCP แล้ว (ปิด stdin → server exit code={code})")

print("\n" + "=" * 78)
print(f"{'step':<5} {'goal':<9} {'action':<28} {'result':<6} detail")
for r in rows:
    print(f"{str(r[0]):<5} {r[1]:<9} {r[2][:28]:<28} {r[3]:<6} {r[4][:60]}")
print(f"\nสถานะรวม: {final} · วันเดินทาง {TARGET} · actions={actions}")
if top3:
    print("\nTop 3 (ราคาเป็นบาท จาก snapshot):")
    for i, f in enumerate(top3, 1):
        print(f"{i}. {f['airline']} | {f['depart']} → {f['arrive']} | {f['duration']} | {f['stops']} | THB {f['price_thb']} | บรรทัด {f['source_line']}")
RUNLOG.close()
sys.exit(0 if final == "OK" and all(r[3] in ("PASS", "SKIP") for r in rows) else 1)
