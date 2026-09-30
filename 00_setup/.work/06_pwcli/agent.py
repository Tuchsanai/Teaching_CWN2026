#!/usr/bin/env python3
"""Code-in-control web agent: Playwright CLI = eyes & hands, LLM = decider, this file = flow controller.

Per sub-goal: Observe (snapshot) -> Verify (already done?) -> Decide (LLM, plain-text prompt -> JSON)
-> Validate (code) -> Act (playwright-cli) -> Verify (new snapshot).
Evidence per step: snapshot.yml, prompt.txt, decision.json, act.txt, page.png (red circle + callout overlay).
"""
import argparse, datetime as dt, json, os, re, shlex, subprocess, sys, time
from pathlib import Path

PWCLI = os.environ.get("PWCLI", "playwright-cli")
LLM = os.environ.get("LLM_CMD", "yolo1")
MODEL = os.environ.get("LLM_MODEL", "claude-haiku-4-5-20251001")
URL = "https://www.google.com/travel/flights?hl=en"

MAX_STEPS = 25            # hard cap for the whole run
MAX_TRIES = 5             # actions per sub-goal
ALLOWED_ACTIONS = {"click", "fill", "press", "stop"}
ALLOWED_KEYS = {"Enter", "Escape", "Tab"}
ACTIONABLE = {"button", "combobox", "textbox", "option", "link", "checkbox", "radio",
              "tab", "menuitem", "searchbox", "spinbutton", "gridcell"}
DENY = re.compile(r"\b(book|booking|sign ?in|log ?in|continue to book|payment|pay|purchase|"
                  r"checkout|credit card|select fare|select flight)\b", re.I)
FORM_ROLES = {"button", "combobox", "textbox", "option"}          # form steps: no links (a link may leave the page)
URL_OK = re.compile(r"^https://www\.google\.com/travel/flights(/search)?\?")
BLOCKED = re.compile(r"unusual traffic|recaptcha|not a robot|/sorry/", re.I)

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
SYSTEM = "You are a web-action decider. Reply only with JSON that matches the given schema."

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
- ถ้าทำเป้าหมายจาก snapshot นี้ไม่ได้ ให้ตอบ action = stop พร้อมเหตุผล

ตอบเป็น JSON อย่างเดียว: {{"action": "...", "ref": "...", "value": "...", "reason": "..."}}
"""


def next_month_15(today):
    y, m = (today.year + 1, 1) if today.month == 12 else (today.year, today.month + 1)
    return dt.date(y, m, 15)


# ---------- eyes & hands: Playwright CLI ----------
def cli(*args):
    p = subprocess.run([PWCLI, *args], capture_output=True, text=True, timeout=90)
    return p.returncode, (p.stdout + p.stderr).strip()


def observe(path):
    rc, out = cli("snapshot", "--boxes", f"--filename={path}")
    if rc != 0:
        raise RuntimeError(out)
    return Path(path).read_text()


def page_url():
    return cli("--raw", "eval", "() => location.href")[1].strip().strip('"')


ELEM = re.compile(r"^(\s*)- '?(\w+)(?: \"((?:[^\"\\]|\\.)*)\")?(.*?)\[ref=(\w+)\]")


def index(snap):
    """ref -> {role, name, line, box} for every element that has a ref."""
    idx = {}
    for n, line in enumerate(snap.splitlines(), 1):
        m = ELEM.match(line)
        if m:
            box = re.search(r"\[box=(-?\d+),(-?\d+),(\d+),(\d+)\]", line)
            idx[m.group(5)] = {"role": m.group(2), "name": m.group(3) or "", "line": n,
                               "box": [int(x) for x in box.groups()] if box else None}
    return idx


def trim(snap, hint, roles):
    """What the LLM sees: named elements of the allowed roles only, no boxes; filter by hint when big."""
    keep = []
    for line in snap.splitlines():
        m = ELEM.match(line)
        if not m or m.group(2) not in roles or not m.group(3):
            continue
        line = re.sub(r" \[(box=[^\]]*|cursor=pointer)\]", "", line).strip()
        keep.append(line[:200])
    if len(keep) > 60 and hint:
        rx = re.compile(hint, re.I)
        keep = [l for l in keep if rx.search(l) or "[expanded]" in l or "[active]" in l]
    return "\n".join(keep[:80])


# ---------- decider: LLM (no tools, plain-text prompt in, JSON out) ----------
def decide(prompt):
    cmd = [LLM, "-p", "--model", MODEL, "--effort", "low", "--output-format", "json",
           "--json-schema", SCHEMA, "--no-session-persistence", "--strict-mcp-config",
           "--system-prompt", SYSTEM, "--tools", ""]
    t = time.time()
    p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=180, cwd="/tmp")
    secs = round(time.time() - t, 1)
    try:
        d = json.loads(p.stdout)
        return d.get("structured_output") or json.loads(d["result"]), secs
    except Exception:
        return {"action": "invalid", "ref": "", "value": "", "reason": (p.stdout + p.stderr)[-300:]}, secs


# ---------- flow controller: validate before any CLI call ----------
def validate(d, idx, allowed_values, roles):
    """Return (verdict, checks). verdict: ok | invalid (re-ask) | deny / stop (halt run)."""
    a, ref, val = d.get("action"), d.get("ref", ""), d.get("value", "")
    checks = []

    def check(name, ok, detail):
        checks.append({"check": name, "pass": ok, "detail": detail})
        return ok

    if not check("action in allowlist", a in ALLOWED_ACTIONS, f"{a} ∈ {sorted(ALLOWED_ACTIONS)}"):
        return "invalid", checks
    if a == "stop":
        return "stop", checks
    if not check("ref exists in latest snapshot", ref in idx, ref):
        return "invalid", checks
    el = idx[ref]
    if not check("element not in denylist", not (DENY.search(el["name"]) or DENY.search(val)),
                 f'{el["role"]} "{el["name"][:90]}"'):
        return "deny", checks
    if not check("role allowed for this step", el["role"] in roles, f"{el['role']} ∈ {sorted(roles)}"):
        return "invalid", checks
    if a == "fill" and not check("fill value allowed for this step", val in allowed_values, f"{val!r} ∈ {allowed_values}"):
        return "invalid", checks
    if a == "press" and not check("key allowed", val in ALLOWED_KEYS, val):
        return "invalid", checks
    return "ok", checks


def act_args(d):
    a, ref, val = d["action"], d["ref"], d["value"]
    return {"click": ["click", ref], "fill": ["fill", ref, val], "press": ["press", val]}[a]


# ---------- evidence: overlay (HTML/SVG injected with eval) + 2x screenshot ----------
OVERLAY_JS = r"""() => {
  const marks = %s;
  document.getElementById('__cic_overlay')?.remove();
  const W = innerWidth, H = innerHeight, root = document.createElement('div');
  root.id = '__cic_overlay';
  root.style.cssText = 'position:fixed;inset:0;z-index:2147483647;pointer-events:none;font-family:"Noto Sans Thai","Noto Sans",sans-serif';
  const NS = 'http://www.w3.org/2000/svg', svg = document.createElementNS(NS, 'svg');  // DOM API: Google pages block innerHTML (Trusted Types)
  svg.setAttribute('width', W); svg.setAttribute('height', H); svg.style.cssText = 'position:absolute;inset:0';
  const shape = (tag, attrs) => { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); svg.appendChild(e); };
  const placed = [];
  for (const m of marks) {
    const [x, y, w, h] = m.box, p = m.pad ?? 12, cx0 = x+w/2, cy0 = y+h/2, rx = w/2+p+8, ry = h/2+p;
    shape('ellipse', {cx: cx0, cy: cy0, rx, ry, fill: 'none', stroke: '#e00000', 'stroke-width': 4});
    const cw = Math.min(460, Math.max(260, m.text.length * 8.5)), ch = 64;
    // try right, left, below, above of the element; keep clear of the element and earlier callouts
    const cands = [[x+w/2-cw/2, y-p-36-ch], [x+w+p+40, y+h/2-ch/2], [x+w/2-cw/2, y+h+p+36], [x-p-40-cw, y+h/2-ch/2], [Math.max(8, x-cw/2), y-p-36-ch]];
    if (m.prefer === 'right') cands.unshift(cands.splice(1, 1)[0]);
    const hit = (a, b) => a[0] < b[0]+b[2] && b[0] < a[0]+a[2] && a[1] < b[1]+b[3] && b[1] < a[1]+a[3];
    let pos = cands.find(([cx, cy]) => cx >= 8 && cy >= 8 && cx+cw <= W-8 && cy+ch <= H-8 &&
        !hit([cx, cy, cw, ch], [x-p, y-p, w+2*p, h+2*p]) && !placed.some(q => hit([cx, cy, cw, ch], q)));
    if (!pos) pos = [Math.min(Math.max(8, x), W-cw-8), Math.min(H-ch-8, y+h+p+36)];
    placed.push([pos[0], pos[1], cw, ch]);
    const ax = pos[0] > x+w ? pos[0] : pos[0]+cw < x ? pos[0]+cw : pos[0]+cw/2;
    const ay = pos[1] > y+h ? pos[1] : pos[1]+ch < y ? pos[1]+ch : pos[1]+ch/2;
    const t = Math.atan2((ay-cy0)/ry, (ax-cx0)/rx);          // connector stops at the ellipse edge
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


def shoot(png, marks):
    """marks = [{box:[x,y,w,h] css px, text:str}] -> page.png (2x) with overlay, overlay removed after."""
    marks = [m for m in marks if m.get("box")]
    if marks:
        cli("eval", OVERLAY_JS % json.dumps(marks, ensure_ascii=False))
    rc, out = cli("screenshot", "--hires", f"--filename={png}")
    cli("eval", "() => { document.getElementById('__cic_overlay')?.remove(); return true }")
    try:
        from PIL import Image          # optional: shrink PNG (not installed in the LAB 03 image)
    except ImportError:
        return
    if rc == 0:
        im = Image.open(png).convert("RGB")
        im.quantize(colors=160, method=Image.Quantize.MEDIANCUT).save(png, optimize=True)


def visible_box(ref, box):
    """Box from snapshot --boxes; if outside the viewport, scroll it in and re-measure."""
    if box and 0 <= box[1] and box[1] + box[3] <= 1080:
        return box
    rc, out = cli("--raw", "eval", "el => { el.scrollIntoView({block:'center'}); const r = el.getBoundingClientRect();"
                  " return [r.x, r.y, r.width, r.height].map(Math.round) }", ref)
    try:
        return json.loads(out)
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

    def stepdir(self, name):
        self.n += 1
        d = self.out / "steps" / f"{self.n:02d}_{name}"
        d.mkdir(parents=True, exist_ok=True)
        return d


def goals(date):
    d_short = f"{date:%a}, {date:%b} {date.day}"          # e.g. Thu, Oct 15
    d_long = f"{date:%B} {date.day}, {date.year}"          # e.g. October 15, 2026
    has = lambda rx: (lambda s, u: re.search(rx, s) is not None)
    return [
        dict(key="consent", th="ปิด cookie/consent",
             goal="ถ้ามีหน้าต่าง cookie/consent ให้กด 'Reject all' (หรือ 'Accept all') ถ้าไม่มีให้ stop",
             done=lambda s, u: not re.search(r'button "(Reject all|Accept all)"', s), values=[], hint="Reject all|Accept all"),
        dict(key="oneway", th="ประเภทตั๋ว",
             goal="ประเภทตั๋วต้องเป็น 'One way' — ถ้าเห็น option 'One way' ให้ click; ถ้าไม่เห็น ให้ click combobox ประเภทตั๋ว (Change ticket type) เพื่อเปิดรายการ",
             done=has(r'combobox "Change ticket type\. One way"'), values=[], hint="ticket type|One way"),
        dict(key="class_pax", th="ชั้นโดยสาร/ผู้โดยสาร",
             goal="ชั้นโดยสารต้องเป็น Economy และผู้โดยสาร 1 คน (ถ้าไม่ใช่ให้ stop)",
             done=lambda s, u: bool(re.search(r'seating class\. Economy', s) and re.search(r'button "1 passenger', s)),
             values=[], hint="seating class|passenger"),
        dict(key="origin", th="ต้นทาง",
             goal="ต้นทางต้องเป็น Suvarnabhumi Airport (BKK) — ถ้าเห็น option 'Suvarnabhumi Airport (BKK)' ให้ click; "
                  "ถ้าเห็นช่องต้นทางที่ [expanded] ('Where from?' หรือ 'Where else?') ให้ fill ด้วย BKK; ไม่อย่างนั้นให้ click combobox 'Where from?'",
             done=has(r'combobox "Where from\?[^"]*BKK"'), values=["BKK"], hint="Where from|Where else|BKK"),
        dict(key="destination", th="ปลายทาง",
             goal="ปลายทางต้องเป็น 'Tokyo, Japan' — ถ้าเห็น option 'Tokyo, Japan' ให้ click; "
                  "ถ้าเห็นช่อง 'Where to?' ที่ [expanded] ให้ fill ด้วย Tokyo; ไม่อย่างนั้นให้ click combobox 'Where to?'",
             done=lambda s, u: bool(re.search(r'combobox "Where to\?[^\n]*: Tokyo', s)) and "[expanded]" not in s,
             values=["Tokyo"], hint="Where to|Tokyo"),   # dropdown closed = an option was really chosen
        dict(key="date", th="วันเดินทาง",
             goal=f"วันเดินทาง (Departure) ต้องเป็น {d_long} — ถ้าเห็นปุ่มวันที่ {d_long} ให้ click; ไม่อย่างนั้นให้ click ช่อง 'Departure' เพื่อเปิดปฏิทิน",
             done=has(r'textbox "Departure"[^\n]*: ' + re.escape(d_short)), values=[], hint=f"Departure|{d_long}"),
        dict(key="search", th="ค้นหา",
             goal="กดค้นหาเที่ยวบิน — ถ้าเห็นปุ่ม 'Done' ของปฏิทินให้ click ก่อน; ไม่อย่างนั้นให้ click ปุ่ม 'Search'",
             done=lambda s, u: "/travel/flights/search" in u and len(re.findall(r'Thai baht.*Select flight', s)) >= 3,
             values=[], hint="Search|Done"),
    ], d_short


def top3(snap):
    lines = snap.splitlines()
    res = []
    for n, line in enumerate(lines, 1):
        m = re.search(r'- link "(From (\d+) Thai baht\. (.*?)Select flight)" \[box=(\d+),(\d+),(\d+),(\d+)\]', line)
        if not m:
            continue
        txt = m.group(3)
        air = re.search(r"flight with (.*?)\.", txt)
        leave = re.search(r"at (\d+:\d+ [AP]M) on", txt)
        arr = re.search(r"arrives at (.*?) at (\d+:\d+ [AP]M) on (\w+)", txt)
        dur = re.search(r"Total duration (.*?)\.", txt)
        stops = re.search(r"(Nonstop|\d+ stops?) flight", txt)
        child = ELEM.match(lines[n]) if n < len(lines) else None
        res.append({"rank": len(res) + 1, "airline": air.group(1) if air else "?",
                    "depart": leave.group(1) if leave else "?",
                    "arrive": f"{arr.group(2)} ({arr.group(3)}) {arr.group(1)}" if arr else "?",
                    "duration": dur.group(1) if dur else "?", "stops": stops.group(1) if stops else "?",
                    "price_thb": int(m.group(2)), "snapshot_line": n,
                    "card_ref": child.group(5) if child else None,
                    "box": [int(m.group(i)) for i in range(4, 8)]})
        if len(res) == 3:
            break
    return res


def dump(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--trick", help="guardrail test: replace the plan with this one goal")
    args = ap.parse_args()
    R = Run(args.out)
    date = next_month_15(dt.date.today())
    plan, d_short = goals(date)
    if args.trick:
        plan = [dict(key="trick", th="ทดสอบ guardrail", goal=args.trick, done=lambda s, u: False, values=[], hint="", roles=ACTIONABLE)]
    R.log(f"START today={dt.date.today()} departure={date} ({d_short}) model={MODEL} max_steps={MAX_STEPS}")

    rc, out = cli("open", URL)
    if rc != 0:
        R.log("FAIL open: " + out[:200]); return 2
    time.sleep(2)
    tmp = Path(__file__).resolve().parent / "tmp"; tmp.mkdir(exist_ok=True)
    steps = 0
    for g in plan:
        history = []
        for attempt in range(MAX_TRIES + 1):
            snap = observe(tmp / "obs.yml"); url = page_url()
            if BLOCKED.search(snap) or BLOCKED.search(url):
                d = R.stepdir(f"{g['key']}-BLOCKED"); (d / "snapshot.yml").write_text(snap); shoot(d / "page.png", [])
                R.log(f"STOP blocked/CAPTCHA at goal={g['key']} evidence=steps/{d.name}"); cli("close"); return 3
            if g["done"](snap, url):
                R.log(f"PASS {g['key']} (verified from snapshot)"); break
            if g["key"] == "consent":
                break
            if attempt == MAX_TRIES or steps >= MAX_STEPS:
                d = R.stepdir(f"{g['key']}-STUCK"); (d / "snapshot.yml").write_text(snap); shoot(d / "page.png", [])
                R.log(f"STOP stuck at goal={g['key']} after {attempt} actions evidence=steps/{d.name}"); cli("close"); return 4
            idx = index(snap)
            roles = g.get("roles", FORM_ROLES)
            prompt = PROMPT.format(goal=g["goal"], history="\n".join(history) or "(ยังไม่มี)", snapshot=trim(snap, g["hint"], roles))
            dec, secs = decide(prompt)
            verdict, checks = validate(dec, idx, g["values"], roles)
            steps += 1
            d = R.stepdir(f"{g['key']}-{dec.get('action', 'x')}")
            (d / "snapshot.yml").write_text(snap)
            (d / "prompt.txt").write_text(f"[system]\n{SYSTEM}\n\n[user]\n{prompt}\n[json-schema]\n{SCHEMA}\n")
            el = idx.get(dec.get("ref", ""), {})
            rec = {"step": R.n, "goal_key": g["key"], "llm_model": MODEL, "llm_seconds": secs,
                   "llm_decision": dec, "validate": {"verdict": verdict, "checks": checks},
                   "target": {k: el.get(k) for k in ("role", "name", "line", "box")} if el else None}
            what = f"{dec.get('action')} {dec.get('ref')}" + (f" = {dec.get('value')}" if dec.get("value") else "")
            label = f"Step {R.n} · {what} ({el.get('role', '?')} \"{el.get('name', '')[:40]}\")"
            if verdict != "ok":
                label += f" ✋ {verdict.upper()}"
            box = visible_box(dec.get("ref"), el.get("box")) if el else None
            shoot(d / "page.png", [{"box": box, "text": label}] if box else [])
            fails = [c for c in checks if not c["pass"]]
            R.log(f"STEP {R.n:02d} {g['key']}: {what} -> validate {verdict}"
                  + (f" ({fails[0]['check']}: {fails[0]['detail']})" if fails else ""))
            if verdict in ("deny", "stop", "invalid"):
                rec["result"] = "HALT" if verdict in ("deny", "stop") else "REJECTED → observe again"
                dump(d / "decision.json", rec)
                (d / "act.txt").write_text(f"# ไม่รันคำสั่งใด ๆ: validate = {verdict}\n# {rec['result']}\n")
                if verdict in ("deny", "stop"):
                    R.log(f"HALT {verdict}: " + (fails[0]["detail"] if fails else dec.get("reason", ""))); cli("close"); return 5
                continue
            argv = act_args(dec)
            rc, out = cli(*argv)
            time.sleep(4 if g["key"] == "search" else 1.5)
            after = observe(tmp / "after.yml"); url2 = page_url()
            reached = g["done"](after, url2)
            if not URL_OK.search(url2):             # guard: an action must never take us off the search pages
                (d / "act.txt").write_text(f"$ playwright-cli {' '.join(argv)}\nexit code: {rc}\n\n# verify: URL นอก allowlist → หยุด\n{url2}\n")
                rec["result"] = "HALT (left allowed URL)"; dump(d / "decision.json", rec)
                R.log(f"HALT left allowed URL: {url2}"); cli("close"); return 5
            history.append(f"- {what} ({el['role']} \"{el['name'][:60]}\")" + (" → CLI error" if rc else ""))
            short = "\n".join(l for l in out.splitlines() if l.startswith(("await ", "- Page URL", "Error")))
            (d / "act.txt").write_text(
                f"$ playwright-cli {' '.join(shlex.quote(a) for a in argv)}\n{short}\nexit code: {rc}\n\n"
                f"# verify (snapshot ใหม่): {g['th']} → {'ผ่าน ✅' if reached else 'ยังไม่ถึงเป้าหมาย → วนรอบใหม่'}\n")
            rec["act"] = {"argv": ["playwright-cli", *argv], "exit_code": rc}
            rec["verify_after"] = "goal reached" if reached else "not yet"
            dump(d / "decision.json", rec)
            if rc:
                R.log(f"  CLI error: {out[:160]}")
    # results: extracted by code from the real snapshot, never by the LLM
    time.sleep(2)
    d = R.stepdir("results")
    snap = observe(d / "snapshot.yml")
    t3 = top3(snap)
    shoot(d / "page.png", [{"box": r["box"], "prefer": "right", "pad": 0, "text": f"#{r['rank']} {r['airline']} · บรรทัด {r['snapshot_line']}"} for r in t3])
    dump(d / "top3.json", {"url": page_url(), "departure": str(date), "top3": t3})
    for r in t3:
        R.log(f"TOP{r['rank']} {r['airline']} {r['depart']} -> {r['arrive']} | {r['duration']} | {r['stops']} | THB {r['price_thb']:,} (snapshot.yml line {r['snapshot_line']}, card ref {r['card_ref']})")
    R.log(f"DONE llm_steps={steps} evidence=steps/")
    cli("close")
    return 0 if len(t3) == 3 else 6


if __name__ == "__main__":
    sys.exit(main())
