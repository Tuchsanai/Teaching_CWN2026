#!/usr/bin/env python3
"""Code-in-control web agent: Playwright MCP = ตาและมือ, LLM = ผู้ตัดสินใจ, ไฟล์นี้ = MCP client + ผู้คุม flow

ต่อเป้าหมาย: Observe (browser_snapshot) → ผ่านแล้วข้าม → Decide (LLM ไม่มี tool, prompt → JSON)
→ Validate (โค้ด) → Act (tools/call) → Verify (browser_snapshot ใหม่ ตรวจด้วยโค้ด)
หลักฐานต่อ action: steps/NN_<goal>-<action>/ snapshot.yml prompt.txt decision.json page.png act.txt verify.yml rpc.jsonl
"""
import argparse, datetime as dt, json, re, shutil, subprocess, sys, time
from pathlib import Path

from mcp_client import MCP, page_url, snapshot_yaml, write_config

LLM = "yolo1"
MODEL = "haiku"
URL = "https://www.google.com/travel/flights?hl=en"

MAX_STEPS = 25                    # action สูงสุดทั้ง run
MAX_TRIES = 5                     # action สูงสุดต่อเป้าหมาย
ALLOWED_ACTIONS = {"click", "fill", "press", "stop"}
ALLOWED_KEYS = {"Enter", "Escape", "Tab"}
TOOL_OF = {"click": "browser_click", "fill": "browser_type", "press": "browser_press_key"}
ACTIONABLE = {"button", "combobox", "textbox", "option", "link", "checkbox", "radio",
              "tab", "menuitem", "searchbox", "spinbutton", "gridcell"}
FORM_ROLES = {"button", "combobox", "textbox", "option"}      # step ฟอร์ม: ไม่ให้เห็น link (พาออกนอกหน้าได้)
DENY = re.compile(r"\b(book|booking|sign ?in|log ?in|continue to book|payment|pay|purchase|"
                  r"checkout|credit card|select fare|select flight)\b", re.I)
REF_RX = re.compile(r"^(f\d+)?e\d+$")                        # MCP target รับ selector ได้ด้วย → บังคับรูปแบบ ref
URL_OK = re.compile(r"^https://www\.google\.com/travel/flights(/search)?\?")
BLOCKED = re.compile(r"unusual traffic|recaptcha|not a robot|/sorry/", re.I)
MAX_LINES_TO_LLM = 60

SCHEMA = json.dumps({
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": sorted(ALLOWED_ACTIONS)},
        "ref": {"type": "string"},
        "value": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": ["action", "ref", "value", "reason"],
    "additionalProperties": False,
})
# --tools "" ไม่ตัด tool ของ MCP ที่ wrapper yolo1 ส่งมา (--mcp-config ส่วนกลาง) → ต้องห้าม mcp__playwright เพิ่ม
LLM_CMD = [LLM, "-p", "--model", MODEL, "--effort", "low", "--output-format", "json", "--json-schema", SCHEMA,
           "--no-session-persistence", "--strict-mcp-config", "--tools", "", "--disallowedTools", "mcp__playwright"]

PROMPT = """คุณคือผู้ตัดสินใจ action ถัดไป 1 action บนหน้าเว็บ (คุณไม่ได้กดเอง โค้ดจะตรวจแล้วกดให้)

เป้าหมายของ step นี้:
{goal}

สิ่งที่ทำไปแล้วใน step นี้:
{history}

หน้าเว็บตอนนี้ (snapshot ตัดเหลือเฉพาะ element ที่กดหรือกรอกได้ แต่ละตัวมี [ref=...]):
{snapshot}

กติกา:
- เลือก ref ที่อยู่ใน snapshot ข้างบนเท่านั้น
- action ได้แค่ click, fill, press, stop
- fill ต้องใส่ value = ข้อความที่จะกรอก, press ต้องใส่ value = ชื่อปุ่ม เช่น Enter, click ให้ value = ""
- ถ้าทำเป้าหมายจาก snapshot นี้ไม่ได้ หรือเป้าหมายสำเร็จแล้ว ให้ตอบ action = stop พร้อมเหตุผล

ตอบเป็น JSON อย่างเดียว: {{"action": "...", "ref": "...", "value": "...", "reason": "..."}}
"""


def next_month_15(today):
    y, m = (today.year + 1, 1) if today.month == 12 else (today.year, today.month + 1)
    return dt.date(y, m, 15)


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


# ---------- ตา: browser_snapshot แบบ inline + box ----------
def observe(m):
    r = m.call("browser_snapshot", {"boxes": True})
    if r["is_error"]:
        raise RuntimeError(r["text"][:300])
    return snapshot_yaml(r["text"]), page_url(r["text"])


ELEM = re.compile(r"^(\s*)- '?(\w+)(?: \"((?:[^\"\\]|\\.)*)\")?(.*?)\[ref=((?:f\d+)?e\d+)\]")


def index(snap):
    """ref -> {role, name, line, box} ของทุก element ที่มี ref"""
    idx = {}
    for n, line in enumerate(snap.splitlines(), 1):
        mm = ELEM.match(line)
        if mm:
            box = re.search(r"\[box=(-?\d+),(-?\d+),(\d+),(\d+)\]", line)
            idx[mm.group(5)] = {"role": mm.group(2), "name": mm.group(3) or "", "line": n,
                                "box": [int(x) for x in box.groups()] if box else None}
    return idx


def trim(snap, hint, roles):
    """สิ่งที่ LLM เห็น: เฉพาะ role ที่อนุญาต + มีชื่อ, ไม่มี box/cursor; ยาวเกินใช้คำใบ้ของ step"""
    keep = []
    for line in snap.splitlines():
        mm = ELEM.match(line)
        if not mm or mm.group(2) not in roles or not mm.group(3):
            continue
        line = re.sub(r" \[(box=[^\]]*|cursor=pointer)\]", "", line).strip()
        keep.append(line[:200])
    if len(keep) > MAX_LINES_TO_LLM and hint:
        rx = re.compile(hint, re.I)
        keep = [l for l in keep if rx.search(l) or "[expanded]" in l or "[active]" in l]
    return keep[:80]


# ---------- ผู้ตัดสินใจ: LLM (ไม่มี tool, plain text เข้า JSON ออก) ----------
def decide(prompt):
    t = time.time()
    p = subprocess.run(LLM_CMD, input=prompt, capture_output=True, text=True, timeout=240, cwd="/tmp")
    secs = round(time.time() - t, 1)
    try:
        d = json.loads(p.stdout)
        raw = {k: d.get(k) for k in ("structured_output", "is_error", "num_turns", "duration_ms", "total_cost_usd")}
        return d.get("structured_output") or json.loads(d["result"]), secs, raw
    except Exception:
        tail = (p.stdout + p.stderr)[-300:]
        return {"action": "invalid", "ref": "", "value": "", "reason": tail}, secs, {"error": tail}


# ---------- ผู้คุม: ตรวจก่อนเรียก tool ทุกครั้ง ----------
def validate(d, idx, sent_refs, allowed_values, roles, url, budget, only_name=None):
    """คืน (verdict, checks) verdict: ok | invalid (ถามใหม่) | deny / stop (หยุดทั้ง run)"""
    a, ref, val = d.get("action"), d.get("ref", ""), d.get("value", "")
    checks = []

    def check(name, ok, detail):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})
        return ok

    if not check("action in allowlist", a in ALLOWED_ACTIONS, f"{a} ∈ {sorted(ALLOWED_ACTIONS)}"):
        return "invalid", checks
    if a == "stop":
        return "stop", checks
    if not check("action budget", budget["run"] < MAX_STEPS and budget["goal"] < MAX_TRIES,
                 f"run {budget['run']}/{MAX_STEPS}, goal {budget['goal']}/{MAX_TRIES}"):
        return "stop", checks
    if not check("ref format (not a selector)", REF_RX.match(ref or ""), repr(ref)):
        return "invalid", checks
    if not check("ref exists in latest snapshot", ref in idx, ref):
        return "invalid", checks
    el = idx[ref]
    if not check("element not in denylist", not (DENY.search(el["name"]) or DENY.search(val)),
                 f'{el["role"]} "{el["name"][:90]}"'):
        return "deny", checks
    if not check("role allowed for this step", el["role"] in roles, f"{el['role']} ∈ {sorted(roles)}"):
        return "invalid", checks
    if not check("ref was in the list sent to LLM", ref in sent_refs, ref):
        return "invalid", checks
    if only_name and not check("element allowed for this step", re.search(only_name, el["name"]), f'"{el["name"][:60]}" ~ {only_name}'):
        return "invalid", checks
    if a == "fill" and not check("fill value allowed for this step", val in allowed_values, f"{val!r} ∈ {allowed_values}"):
        return "invalid", checks
    if a == "press" and not check("key allowed", val in ALLOWED_KEYS, f"{val!r} ∈ {sorted(ALLOWED_KEYS)}"):
        return "invalid", checks
    if not check("page URL in allowlist", URL_OK.search(url or ""), url):
        return "deny", checks
    return "ok", checks


def tool_args(d):
    a, ref, val = d["action"], d["ref"], d["value"]
    return {"click": {"target": ref}, "fill": {"target": ref, "text": val}, "press": {"key": val}}[a]


# ---------- หลักฐาน: overlay (สร้างด้วย DOM API ผ่าน browser_evaluate) + screenshot 2x ----------
OVERLAY_JS = r"""() => {
  const marks = %s;
  document.getElementById('__cic_overlay')?.remove();
  const W = innerWidth, H = innerHeight, root = document.createElement('div');
  root.id = '__cic_overlay';
  root.style.cssText = 'position:fixed;inset:0;z-index:2147483647;pointer-events:none;font-family:Loma,Waree,"Noto Sans Thai",sans-serif';
  const NS = 'http://www.w3.org/2000/svg', svg = document.createElementNS(NS, 'svg');  // Google บล็อก innerHTML (Trusted Types)
  svg.setAttribute('width', W); svg.setAttribute('height', H); svg.style.cssText = 'position:absolute;inset:0';
  const shape = (tag, attrs) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); svg.appendChild(e); };
  const placed = [];
  for (const m of marks) {
    const [x, y, w, h] = m.box, p = m.pad ?? 12, cx0 = x+w/2, cy0 = y+h/2, rx = w/2+p+8, ry = h/2+p;
    shape('ellipse', {cx: cx0, cy: cy0, rx, ry, fill: 'none', stroke: '#e00000', 'stroke-width': 4});
    const cw = Math.min(460, Math.max(260, m.text.length * 8.5)), ch = 64;
    const cands = [[x+w/2-cw/2, y-p-36-ch], [x+w+p+40, y+h/2-ch/2], [x+w/2-cw/2, y+h+p+36], [x-p-40-cw, y+h/2-ch/2], [Math.max(8, x-cw/2), y-p-36-ch]];
    if (m.prefer === 'right') cands.unshift(cands.splice(1, 1)[0]);
    const hit = (a, b) => a[0] < b[0]+b[2] && b[0] < a[0]+a[2] && a[1] < b[1]+b[3] && b[1] < a[1]+a[3];
    let pos = cands.find(([cx, cy]) => cx >= 8 && cy >= 8 && cx+cw <= W-8 && cy+ch <= H-8 &&
        !hit([cx, cy, cw, ch], [x-p, y-p, w+2*p, h+2*p]) && !placed.some(q => hit([cx, cy, cw, ch], q)));
    if (!pos) pos = [Math.min(Math.max(8, x), W-cw-8), Math.min(H-ch-8, y+h+p+36)];
    placed.push([pos[0], pos[1], cw, ch]);
    const ax = pos[0] > x+w ? pos[0] : pos[0]+cw < x ? pos[0]+cw : pos[0]+cw/2;
    const ay = pos[1] > y+h ? pos[1] : pos[1]+ch < y ? pos[1]+ch : pos[1]+ch/2;
    const t = Math.atan2((ay-cy0)/ry, (ax-cx0)/rx);
    shape('line', {x1: ax, y1: ay, x2: cx0+rx*Math.cos(t), y2: cy0+ry*Math.sin(t), stroke: '#e00000', 'stroke-width': 3, 'stroke-dasharray': '6 4'});
    const div = document.createElement('div');
    div.textContent = m.text;
    div.style.cssText = `position:absolute;left:${pos[0]}px;top:${pos[1]}px;width:${cw}px;min-height:${ch}px;box-sizing:border-box;`
      + 'padding:8px 12px;background:#fff8e1;border:3px solid #e00000;border-radius:10px;color:#111;'
      + 'font-size:18px;line-height:1.35;font-weight:600;box-shadow:0 4px 14px rgba(0,0,0,.25)';
    root.appendChild(div);
  }
  root.prepend(svg);
  document.body.appendChild(root);
  return marks.length;
}"""
REMOVE_JS = "() => { document.getElementById('__cic_overlay')?.remove(); return true }"


def screenshot(m, png):
    """browser_take_screenshot scale=device (3840x2160) ไม่ใส่ filename → ได้ image block (base64) เขียนไฟล์เอง"""
    r = m.call("browser_take_screenshot", {"type": "png", "scale": "device"})
    if r["images"]:
        Path(png).write_bytes(r["images"][0])
    return r


def shoot(m, png, marks):
    """marks = [{box:[x,y,w,h] css px, text}] → page.png พร้อม overlay แล้วลบ overlay"""
    marks = [k for k in marks if k.get("box")]
    if marks:
        m.call("browser_evaluate", {"function": OVERLAY_JS % json.dumps(marks, ensure_ascii=False)})
    screenshot(m, png)
    if marks:
        m.call("browser_evaluate", {"function": REMOVE_JS})


def visible_box(m, ref, box):
    """box จาก snapshot; ถ้าอยู่นอกจอ เลื่อนเข้ามาแล้ววัดใหม่ด้วย getBoundingClientRect บน ref"""
    if box and 0 <= box[1] and box[1] + box[3] <= 1080:
        return box
    r = m.call("browser_evaluate", {"target": ref, "function": "(el) => { el.scrollIntoView({block:'center'});"
               " const r = el.getBoundingClientRect(); return [r.x, r.y, r.width, r.height].map(Math.round) }"})
    try:
        return json.loads(r["text"].split("### Result", 1)[1].split("###")[0].strip())
    except Exception:
        return box


class Run:
    def __init__(self, out):
        self.out = Path(out)
        (self.out / "steps").mkdir(parents=True, exist_ok=True)
        self.logf = open(self.out / "run.log", "a")
        self.n = 0

    def log(self, msg):
        line = f"{dt.datetime.now():%H:%M:%S} {msg}"
        print(line, flush=True)
        self.logf.write(line + "\n"); self.logf.flush()

    def pending(self, m, label):
        """โฟลเดอร์ชั่วคราวของรอบนี้ (เก็บ rpc.jsonl ตั้งแต่ observe) ตั้งชื่อจริงเมื่อรู้ว่ามี action"""
        d = self.out / "steps" / "_pending"
        shutil.rmtree(d, ignore_errors=True); d.mkdir()
        m.set_step_log(d / "rpc.jsonl", label)
        return d

    def commit(self, name):
        self.n += 1
        d = self.out / "steps" / f"{self.n:02d}_{name}"
        (self.out / "steps" / "_pending").rename(d)       # ไฟล์ rpc.jsonl ที่เปิดอยู่เขียนต่อได้ (inode เดิม)
        return d


def goals(date):
    d_short = f"{date:%a}, {date:%b} {date.day}"          # Thu, Oct 15
    d_long = f"{date:%B} {date.day}, {date.year}"          # October 15, 2026

    def has(*rxs):        # ทุก regex ต้องเจอ → คืนบรรทัดหลักฐาน ไม่เจอ → None
        def f(s, u):
            out = []
            for rx in rxs:
                hit = next(((n, l.strip()) for n, l in enumerate(s.splitlines(), 1) if re.search(rx, l)), None)
                if not hit:
                    return None
                out.append(hit)
            return out
        return f

    def expanded_closed_and(*rxs):
        return lambda s, u: None if "[expanded]" in s else has(*rxs)(s, u)

    return [
        dict(key="consent", th="ปิด cookie/consent",
             goal="ถ้ามีหน้าต่าง cookie/consent ให้ click ปุ่ม 'Reject all' เท่านั้น",
             done=lambda s, u: [] if not re.search(r'button "(Reject all|Accept all)"', s) else None,
             values=[], hint="Reject all", only_name=r"^Reject all$"),
        dict(key="ticket", th="ประเภทตั๋ว",
             goal="ประเภทตั๋วต้องเป็น 'One way' — ถ้าเห็น option 'One way' ให้ click; ถ้าไม่เห็น ให้ click combobox ประเภทตั๋ว (Change ticket type) เพื่อเปิดรายการ",
             done=has(r'combobox "Change ticket type\. One way"'), values=[], hint="ticket type|One way"),
        dict(key="class_pax", th="ชั้นโดยสาร/ผู้โดยสาร", check_only=True,
             done=has(r'combobox "Change seating class\. Economy"', r'button "1 passenger')),
        dict(key="origin", th="ต้นทาง",
             goal="ต้นทางต้องเป็น Suvarnabhumi Airport (BKK) — ถ้าเห็น option 'Suvarnabhumi Airport (BKK)' ให้ click; "
                  "ถ้าเห็นช่องต้นทางที่ [expanded] ('Where from?' หรือ 'Where else?') ให้ fill ด้วย BKK; ไม่อย่างนั้นให้ click combobox 'Where from?'",
             done=expanded_closed_and(r'combobox "Where from\?[^"]*BKK"'), values=["BKK"], hint="Where from|Where else|BKK"),
        dict(key="destination", th="ปลายทาง",
             goal="ปลายทางต้องเป็น 'Tokyo, Japan' — ถ้าเห็น option 'Tokyo, Japan' ให้ click; "
                  "ถ้าเห็นช่อง 'Where to?' ที่ [expanded] ให้ fill ด้วย Tokyo; ไม่อย่างนั้นให้ click combobox 'Where to?'",
             done=expanded_closed_and(r'combobox "Where to\?[^\n]*: Tokyo'), values=["Tokyo"], hint="Where to|Tokyo"),
        dict(key="date", th="วันเดินทาง",
             goal=f"วันเดินทาง (Departure) ต้องเป็น {d_long} — ถ้าเห็นปุ่มวันที่ {d_long} ให้ click; ไม่อย่างนั้นให้ click ช่อง 'Departure' เพื่อเปิดปฏิทิน",
             done=has(r'textbox "Departure"[^\n]*: ' + re.escape(d_short)), values=[], hint=f"Departure|{d_long}"),
        dict(key="search", th="ค้นหา",
             goal="กดค้นหาเที่ยวบิน — ถ้าเห็นปุ่ม 'Done' ของปฏิทินให้ click ก่อน; ไม่อย่างนั้นให้ click ปุ่ม 'Search'",
             done=lambda s, u: ([(0, "URL: " + u)] + has(r'Thai baht.*Select flight')(s, u))
             if "/travel/flights/search" in u and len(re.findall(r'Thai baht.*Select flight', s)) >= 3 else None,
             values=[], hint="Search|Done"),
    ], d_short


RESULT = re.compile(r'- link "(From ([\d,]+) Thai baht\. (.*?)Select flight)"(?: \[ref=\w+\])? \[box=(-?\d+),(-?\d+),(\d+),(\d+)\]')


def top3(snap):
    """อ่าน 3 อันดับแรกจากบรรทัด link ผลค้นหา (ลิงก์ไม่มี ref) — โค้ดอ่าน ไม่ใช่ LLM"""
    lines = snap.splitlines()
    res = []
    for n, line in enumerate(lines, 1):
        mm = RESULT.search(line)
        if not mm:
            continue
        txt = mm.group(3)
        air = re.search(r"flight with (.*?)\.", txt)
        leave = re.search(r"at (\d+:\d+ [AP]M) on", txt)
        arr = re.search(r"arrives at (.*?) at (\d+:\d+ [AP]M) on (\w+)", txt)
        dur = re.search(r"Total duration (.*?)\.", txt)
        stops = re.search(r"(Nonstop|\d+ stops?) flight", txt)
        res.append({"rank": len(res) + 1, "airline": air.group(1) if air else "?",
                    "depart": leave.group(1) if leave else "?",
                    "arrive": f"{arr.group(2)} ({arr.group(3)}) {arr.group(1)}" if arr else "?",
                    "duration": dur.group(1) if dur else "?", "stops": stops.group(1) if stops else "?",
                    "price_thb": int(mm.group(2).replace(",", "")), "snapshot_line": n,
                    "source": line.strip()[:400],
                    "box": [int(mm.group(i)) for i in range(4, 8)]})
        if len(res) == 3:
            break
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="log")
    ap.add_argument("--goal", help="แทนแผนด้วยเป้าหมายเดียว (ให้ LLM เห็นทุก role) — ใช้ทดสอบ guardrail")
    ap.add_argument("--inject", help="ใส่ปุ่มปลอมที่มีข้อความนี้ลงในหน้า หลัง navigate ก่อน observe แรก")
    args = ap.parse_args()
    R = Run(args.out)
    date = next_month_15(dt.date.today())
    plan, d_short = goals(date)
    if args.goal:
        plan = [dict(key="goal", th="เป้าหมายที่ส่งมา", goal=args.goal, done=lambda s, u: None,
                     values=[], hint="", roles=ACTIONABLE)]
    R.log(f"START today={dt.date.today()} departure={date} ({d_short}) llm={LLM} --model {MODEL} max_steps={MAX_STEPS} max_tries={MAX_TRIES}")

    out = R.out.resolve()
    m = MCP(write_config(out / "mcp.config.json", out / "mcp-out"), out / "rpc_all.jsonl", cwd=str(out))
    info = m.initialize()
    R.log(f"MCP {m.cmd[0]} server={info['serverInfo']['name']} {info['serverInfo']['version']} protocol={info['protocolVersion']} tools={len(m.tools)}")
    code = 1
    try:
        code = run_plan(R, m, plan, date, args)
    finally:
        rc = m.close()
        R.log(f"MCP closed (stdin closed) exit={rc}")
    return code


def run_plan(R, m, plan, date, args):
    r = m.call("browser_navigate", {"url": URL})
    if r["is_error"]:
        R.log("FAIL navigate: " + r["text"][:200]); return 2
    time.sleep(2)
    if args.inject:     # เนื้อหาหน้าเว็บที่ไม่น่าไว้ใจ พยายามคุยกับ LLM
        r = m.call("browser_evaluate", {"function": "() => { const b = document.createElement('button'); b.textContent = %s;"
                   " b.style.cssText = 'position:fixed;top:90px;left:40%%;z-index:99999;padding:14px;font:600 18px sans-serif;background:#ffeb3b;border:3px dashed #d00';"
                   " document.body.appendChild(b); return true }" % json.dumps(args.inject)})
        R.log(f"INJECT page text via browser_evaluate (isError={r['is_error']}): {args.inject}")
    steps = 0
    for g in plan:
        history = []
        tries = 0
        while True:
            d = R.pending(m, f"{g['key']}#{tries + 1}")
            snap, url = observe(m)
            if BLOCKED.search(snap) or BLOCKED.search(url):
                d = R.commit(f"{g['key']}-BLOCKED"); (d / "snapshot.yml").write_text(snap); shoot(m, d / "page.png", [])
                R.log(f"STOP blocked/CAPTCHA at goal={g['key']} url={url} evidence=steps/{d.name}"); return 3
            proof = g["done"](snap, url)
            if proof is not None:
                R.log(f"PASS {g['key']} (verified from snapshot)" + (f": {proof[0][1][:100]}" if proof else ""))
                break
            if g.get("check_only"):
                d = R.commit(f"{g['key']}-CHECK_FAIL"); (d / "snapshot.yml").write_text(snap); shoot(m, d / "page.png", [])
                R.log(f"STOP check failed: {g['key']} (ตรวจอย่างเดียว ไม่ให้ LLM แก้) evidence=steps/{d.name}"); return 4
            if tries >= MAX_TRIES or steps >= MAX_STEPS:
                d = R.commit(f"{g['key']}-STUCK"); (d / "snapshot.yml").write_text(snap); shoot(m, d / "page.png", [])
                R.log(f"STOP stuck at goal={g['key']} after {tries} actions (run total {steps}) evidence=steps/{d.name}"); return 4
            idx = index(snap)
            roles = g.get("roles", FORM_ROLES)
            sent = trim(snap, g["hint"], roles)
            sent_refs = {mm.group(5) for mm in map(ELEM.match, sent) if mm}
            prompt = PROMPT.format(goal=g["goal"], history="\n".join(history) or "(ยังไม่มี)", snapshot="\n".join(sent))
            dec, secs, raw = decide(prompt)
            verdict, checks = validate(dec, idx, sent_refs, g["values"], roles, url, {"run": steps, "goal": tries}, g.get("only_name"))
            steps += 1; tries += 1
            d = R.commit(f"{g['key']}-{dec.get('action', 'x')}")
            (d / "snapshot.yml").write_text(snap)
            screenshot(m, d / "observe.png")                    # ภาพหน้าเว็บเปล่า ไว้ทำภาพ compare
            (d / "prompt.txt").write_text(prompt)
            el = idx.get(dec.get("ref", ""), {})
            rec = {"step": R.n, "goal_key": g["key"],
                   "observe": {"tool": "browser_snapshot", "args": {"boxes": True}, "url": url,
                               "snapshot_lines": len(snap.splitlines()), "lines_sent_to_llm": len(sent)},
                   "llm_cmd": " ".join(LLM_CMD[:9]) + " '<schema>' " + " ".join(LLM_CMD[10:13]) + ' "" ' + " ".join(LLM_CMD[14:]),
                   "llm_seconds": secs, "llm_raw": raw,
                   "llm_decision": dec, "validate": {"verdict": verdict, "checks": checks},
                   "target": {k: el.get(k) for k in ("role", "name", "line", "box")} if el else None}
            what = f"{dec.get('action')} {dec.get('ref')}" + (f" = {dec.get('value')}" if dec.get("value") else "")
            label = f"Step {R.n} · {what} ({el.get('role', '?')} \"{el.get('name', '')[:40]}\")"
            if verdict != "ok":
                label += f" ✋ {verdict.upper()}"
            box = visible_box(m, dec["ref"], el.get("box")) if el else None
            shoot(m, d / "page.png", [{"box": box, "text": label}] if box else [])
            fails = [c for c in checks if not c["pass"]]
            R.log(f"STEP {R.n:02d} {g['key']}: {what} -> validate {verdict}"
                  + (f" ({fails[0]['check']}: {fails[0]['detail']})" if fails else "")
                  + f" [llm {secs}s, snapshot {len(snap.splitlines())}→{len(sent)} lines]")
            if verdict != "ok":
                rec["result"] = "HALT" if verdict in ("deny", "stop") else "REJECTED → observe again"
                dump(d / "decision.json", rec)
                (d / "act.txt").write_text(f"# ไม่เรียก tool ใด ๆ: validate = {verdict}\n# {rec['result']}\n"
                                           + (f"# เหตุผลจาก LLM: {dec.get('reason', '')}\n" if verdict == "stop" else ""))
                if verdict in ("deny", "stop"):
                    R.log(f"HALT {verdict}: " + (fails[0]["detail"] if fails else dec.get("reason", "")))
                    return 5
                history.append(f"- {what} → ถูกโค้ดปฏิเสธ ({fails[0]['check'] if fails else verdict})")
                continue
            tool, targs = TOOL_OF[dec["action"]], tool_args(dec)
            r = m.call(tool, targs)
            time.sleep(4 if g["key"] == "search" else 1.5)
            m.label = f"{g['key']}#{tries}-verify"
            after, url2 = observe(m)
            (d / "verify.yml").write_text(after)
            proof = g["done"](after, url2)
            reached = proof is not None
            old_alive = f"[ref={dec['ref']}]" in after
            short = "\n".join(l for l in r["text"].splitlines() if l.startswith(("await ", "- Page URL", "Error", "- [Snapshot]")))
            head = (f"→ tools/call {tool} {json.dumps(targs, ensure_ascii=False)}\n"
                    f"← isError={str(r['is_error']).lower()} · {r['seconds']}s · {r['bytes']} bytes\n{short}\n\n"
                    f"→ tools/call browser_snapshot {{\"boxes\": true}}   # verify (เก็บเป็น verify.yml)\n")
            rec["act"] = {"tool": tool, "arguments": targs, "is_error": r["is_error"], "seconds": r["seconds"], "response_excerpt": short}
            if not URL_OK.search(url2):             # action ต้องไม่พาออกนอกหน้าค้นหา
                (d / "act.txt").write_text(head + f"# verify: URL นอก allowlist → หยุด\n# {url2}\n")
                rec["result"] = "HALT (left allowed URL)"; dump(d / "decision.json", rec)
                R.log(f"HALT left allowed URL: {url2}"); return 5
            history.append(f"- {what} ({el['role']} \"{el['name'][:60]}\")" + (" → tool error" if r["is_error"] else ""))
            focus = next((l.strip() for l in after.splitlines() if "[expanded]" in l or ("[active]" in l and "[ref=" in l)), "")
            (d / "act.txt").write_text(
                head + f"# เป้าหมาย '{g['th']}' → {'ผ่าน' if reached else 'ยังไม่ถึง → วนรอบใหม่ (observe ใหม่)'}\n"
                + "".join(f"#   หลักฐาน verify.yml บรรทัด {n}: {l[:160]}\n" for n, l in (proof or []) if n)
                + (f"#   {proof[0][1]}\n" if proof and proof[0][0] == 0 else "")
                + (f"#   สถานะหน้าใหม่: {focus[:160]}\n" if not reached and focus else "")
                + f"# ref {dec['ref']} ใน snapshot ใหม่: {'ยังอยู่' if old_alive else 'ไม่มีแล้ว → ใช้ต่อไม่ได้'}\n")
            rec["verify"] = {"tool": "browser_snapshot", "file": "verify.yml", "url": url2, "goal_reached": reached,
                             "proof": [{"line": n, "text": l[:200]} for n, l in (proof or [])],
                             "old_ref_still_in_new_snapshot": old_alive}
            rec["result"] = "PASS" if reached else "progress → observe again"
            dump(d / "decision.json", rec)
            if r["is_error"]:
                R.log(f"  tool error: {r['text'][:160]}")
    if args.goal:
        R.log("DONE free goal (ไม่มีเงื่อนไข verify)"); return 0
    # ผลลัพธ์: โค้ดอ่านจาก snapshot จริง ไม่ใช่ LLM
    time.sleep(2)
    R.pending(m, "results")
    d = R.commit("results")
    snap, url = observe(m)
    (d / "snapshot.yml").write_text(snap)
    t3 = top3(snap)
    marks = [{"box": x["box"], "prefer": "right", "pad": 0, "text": f"#{x['rank']} {x['airline']} · บรรทัด {x['snapshot_line']}"} for x in t3]
    if t3 and max(b["box"][1] + b["box"][3] for b in marks) > 1080:        # การ์ดล้นจอ: เลื่อนหน้าแล้ววัด box ใหม่
        dy = marks[0]["box"][1] - 120
        m.call("browser_evaluate", {"function": f"() => {{ window.scrollBy(0, {dy}); return scrollY }}"})
        again = top3(observe(m)[0])
        for k, x in zip(marks, again):
            k["box"] = x["box"]
    shoot(m, d / "page.png", marks)
    dump(d / "top3.json", {"url": url, "departure": str(date), "snapshot_lines": len(snap.splitlines()), "top3": t3})
    for x in t3:
        R.log(f"TOP{x['rank']} {x['airline']} {x['depart']} -> {x['arrive']} | {x['duration']} | {x['stops']} | THB {x['price_thb']:,} (snapshot.yml line {x['snapshot_line']})")
    R.log(f"DONE llm_steps={steps} evidence=steps/")
    return 0 if len(t3) == 3 else 6


if __name__ == "__main__":
    sys.exit(main())
