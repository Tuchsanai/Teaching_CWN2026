#!/usr/bin/env python3
"""trip_agent: Google Flights (ค้นหาอย่างเดียว) แบบ code-in-control
playwright-cli = ตาและมือ · LLM (yolo1 haiku, ไม่มี tool) = เลือก 1 action · โค้ด = ผู้คุม
แต่ละเป้าหมายวน Observe -> (ผ่านแล้วข้าม) -> Decide -> Validate -> Act -> Verify
"""
import argparse, datetime, hashlib, json, os, re, subprocess, sys, time

URL = "https://www.google.com/travel/flights?hl=en"
SAFE_URL = "https://www.google.com/travel/flights"
MAX_ACTIONS = 25
MAX_PER_GOAL = 5
ALLOW = {"click", "fill", "press", "stop"}
KEYS = {"Enter", "Escape"}
DENY = re.compile(r"book|sign in|payment|select flight|select fare", re.I)
CAPTCHA = re.compile(r"captcha|unusual traffic|not a robot|verify you.re human|/sorry/", re.I)
ROLES = ("button", "combobox", "textbox", "option")
LINE = re.compile(r'^\s*-\s*(\w+)\s+"([^"]*)".*?\[ref=(\w+)\]')
BOX = re.compile(r'\s*\[box=([\d.,-]+)\]')
VAL = re.compile(r'\]:\s*(.+)$')
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

OUT = "/workspace/log"
LOGF = None


def log(msg=""):
    print(msg, flush=True)
    if LOGF:
        LOGF.write(msg + "\n")
        LOGF.flush()


def pw(*args, quiet=False):
    r = subprocess.run(["playwright-cli", *args], capture_output=True, text=True, timeout=90)
    out = (r.stdout + r.stderr).strip()
    if not quiet:
        log(f"$ playwright-cli {' '.join(args)[:110]}\n  -> rc={r.returncode} {out[:160]!r}")
    return r.returncode, out


# ---------------- snapshot ----------------
class Snap:
    def __init__(self, path):
        self.path = path
        self.text = open(path, encoding="utf-8").read()
        self.lines = self.text.splitlines()
        self.items = []
        for i, ln in enumerate(self.lines, 1):
            m = LINE.match(ln)
            if not m:
                continue
            b = BOX.search(ln)
            clean = BOX.sub("", ln).strip()
            v = VAL.search(clean)
            self.items.append(dict(
                n=i, role=m.group(1), name=m.group(2), ref=m.group(3),
                box=[float(x) for x in b.group(1).split(",")] if b else None,
                value=v.group(1).strip() if v else "", expanded="[expanded]" in ln, text=clean))
        self.by_ref = {it["ref"]: it for it in self.items}

    def find(self, role, name_re=None, pred=None):
        for it in self.items:
            if it["role"] == role and (name_re is None or re.search(name_re, it["name"])) \
                    and (pred is None or pred(it)):
                return it
        return None

    def raw(self, rx):
        for i, ln in enumerate(self.lines, 1):
            if re.search(rx, ln):
                return i
        return None

    def pick(self, roles, name_re):
        return [it for it in self.items if it["role"] in roles and re.search(name_re, it["name"])]

    def signature(self):
        s = re.sub(r"\[(ref|box)=[^\]]*\]", "", self.text)
        return hashlib.md5(s.encode()).hexdigest()


def expanded_combo(s):
    return s.find("combobox", pred=lambda it: it["expanded"])


# ---------------- plan (เป้าหมายตามลำดับ) ----------------
def build_plan(target):
    short = f"{target:%a}, {target:%b} {target.day}"
    longname = f"{target:%A}, {target:%B} {target.day}, {target.year}"
    date_re = "^" + re.escape(longname)

    def st_ticket(s):
        if s.find("option", r"^One way$"):
            return 1, s.find("option", r"^One way$")["n"]
        c = s.find("combobox", r"Change ticket type\. One way")
        return (2, c["n"]) if c else (0, None)

    def show_ticket(s, st):
        return s.pick(("button", "combobox"), r"ticket type") if st == 0 else \
            s.pick(("option",), r"^(Round trip|One way|Multi-city)$")

    def st_seat(s):
        c = s.find("combobox", r"Change seating class\. Economy")
        p = s.find("button", r"^1 passenger")
        return (1, c["n"]) if c and p else (0, None)

    def show_seat(s, st):
        return s.pick(("button", "combobox", "option"), r"seating class|passenger|^Economy$")

    def st_field(field_re, done_val, typed_val):
        def f(s):
            e = expanded_combo(s)
            if e:
                return (2 if e["value"] == typed_val else 1), e["n"]
            c = s.find("combobox", field_re, pred=lambda it: done_val(it))
            return (3, c["n"]) if c else (0, None)
        return f

    def show_field(field_re):
        def f(s, st):
            if st == 0:
                return s.pick(("combobox",), field_re)
            return [it for it in s.items if it["role"] == "option" or
                    (it["role"] == "combobox" and it["expanded"])]
        return f

    def st_date(s):
        dlg = s.raw(r"^\s*-\s*dialog\b")
        t = s.find("textbox", r"^Departure$", pred=lambda it: short in it["value"])
        if dlg:
            return (2, t["n"]) if t else (1, dlg)
        return (3, t["n"]) if t else (0, None)

    def show_date(s, st):
        if st == 0:
            return s.pick(("textbox",), r"^Departure$")
        if st == 1:
            return s.pick(("button",), date_re)
        return s.pick(("button",), r"^Done\.")

    def st_search(s):
        n = s.raw(r'heading "(Search results|Top flights)"')
        return (1, n) if n else (0, None)

    return [
        dict(key="ticket", title="ประเภทตั๋ว", stage=st_ticket, final=2, show=show_ticket, fill=None,
             opt=r"^One way$",
             text="เลือกประเภทตั๋วเป็น One way (ถ้ารายการยังไม่เปิดให้คลิกช่องประเภทตั๋วก่อน แล้วค่อยคลิก option One way)"),
        dict(key="seat", title="ตรวจ Economy/1 คน", stage=st_seat, final=1, show=show_seat, fill=None,
             opt=r"^Economy$",
             text="ให้แน่ใจว่าชั้นโดยสารเป็น Economy และผู้โดยสาร 1 คน"),
        dict(key="origin", title="ต้นทาง", fill="BKK", opt=r"\(BKK\)", final=3,
             stage=st_field(r"^Where from\?", lambda it: "BKK" in it["name"], "BKK"),
             show=show_field(r"^Where from\?"),
             text="ตั้งต้นทางเป็น Suvarnabhumi Airport (BKK): ถ้ายังไม่เปิดช่องให้คลิกช่อง Where from?; "
                  "ถ้าเปิดแล้วให้ fill ค่า BKK ในช่องที่กำลังเปิดอยู่; เมื่อมี option ที่ลงท้าย (BKK) ให้คลิก option นั้น"),
        dict(key="dest", title="ปลายทาง", fill="Tokyo", opt=r"^Tokyo, Japan$", final=3,
             stage=st_field(r"^Where to\?", lambda it: it["value"] == "Tokyo", "Tokyo"),
             show=show_field(r"^Where to\?"),
             text="ตั้งปลายทางเป็น Tokyo, Japan: ถ้ายังไม่เปิดช่องให้คลิกช่อง Where to?; "
                  "ถ้าเปิดแล้วให้ fill ค่า Tokyo; เมื่อมี option \"Tokyo, Japan\" ให้คลิก option นั้น (ไม่ใช่สนามบินหรือสถานีเดี่ยว)"),
        dict(key="date", title=f"วันที่ {target.isoformat()}", fill=None, opt=None, final=3,
             stage=st_date, show=show_date,
             text=f"เลือกวันเดินทาง {longname}: คลิกช่อง Departure เพื่อเปิดปฏิทิน, คลิกปุ่มวันที่เป้าหมาย, "
                  "แล้วคลิกปุ่ม Done เพื่อปิดปฏิทิน"),
        dict(key="search", title="ค้นหา", fill=None, opt=None, final=1, stage=st_search,
             show=lambda s, st: s.pick(("button",), r"^Search$"),
             text="กดปุ่ม Search เพื่อค้นหาเที่ยวบิน"),
    ]


def custom_plan(goal):
    return [dict(key="custom", title="custom", custom=True, final=1, fill=None, opt=None, text=goal,
                 stage=lambda s: (0, None),
                 show=lambda s, st: [it for it in s.items])]


# ---------------- LLM ----------------
def ask_llm(prompt):
    r = subprocess.run(
        ["yolo1", "-p", "--model", "haiku", "--effort", "low", "--output-format", "json",
         "--json-schema", json.dumps(SCHEMA), "--no-session-persistence",
         "--strict-mcp-config", "--tools", ""],
        input=prompt, capture_output=True, text=True, timeout=240)
    try:
        return json.loads(r.stdout)["structured_output"], None
    except Exception as e:
        return None, f"{e}; stdout={r.stdout[:200]!r} stderr={r.stderr[:200]!r}"


def build_prompt(goal, view, fills, history):
    kept = "\n".join(it["text"] for it in view) or "(ไม่มี element ที่มองเห็นได้)"
    fill_txt = (f'- ถ้าใช้ fill ค่า value ต้องเป็น "{goal["fill"]}" เท่านั้น' if goal.get("fill")
                else "- ห้ามใช้ fill (ไม่มีค่าที่อนุญาต)" if not goal.get("custom")
                else "- ถ้าใช้ fill ค่า value ต้องเป็นข้อความที่ปรากฏในเป้าหมายเท่านั้น")
    hist = ("\nความพยายามก่อนหน้าในเป้าหมายนี้ (อย่าทำซ้ำถ้าไม่ได้ผล):\n" + "\n".join(history) + "\n") if history else ""
    return f"""เป้าหมาย: {goal["text"]}

ด้านล่างคือรายการ element ที่ตัดมาจาก snapshot ของหน้า {URL}:
{kept}
{hist}
กติกา:
- เลือก ref จากรายการข้างบนเท่านั้น ห้ามคิด ref เอง
- action ต้องเป็นหนึ่งใน click / fill / press / stop (stop = ไม่มี element ที่เหมาะสม หรือเป้าหมายสำเร็จแล้ว)
{fill_txt}
- ถ้าใช้ press ค่า value ต้องเป็น Enter หรือ Escape
- ทำเพียง 1 การกระทำที่ใกล้เป้าหมายที่สุด

ตอบเป็น JSON เท่านั้น รูปแบบ: {{"action": "...", "ref": "...", "value": "...", "reason": "..."}}
(ถ้าไม่ใช้ value ให้เป็นสตริงว่าง)
"""


# ---------------- evidence ----------------
OVERLAY = """() => {
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
  t.style.cssText = 'position:fixed;background:red;color:#fff;font:bold 14px sans-serif;padding:4px 8px;border-radius:4px;left:' + Math.max(0, x) + 'px;top:' + Math.max(0, y - Math.max(w, h) / 2 - 36) + 'px';
  root.appendChild(svg); root.appendChild(t);
  document.body.appendChild(root);
  return 'ok';
}"""
INJECT = """() => {
  const b = document.createElement('button');
  b.textContent = %s;
  b.style.cssText = 'position:fixed;left:10px;top:10px;z-index:2147483646;padding:8px';
  document.body.insertBefore(b, document.body.firstChild);
  return 'injected';
}"""
REMOVE = "() => { const e = document.getElementById('__step_overlay'); if (e) e.remove(); return 'removed'; }"


def shoot(path, box, label):
    if box:
        pw("eval", OVERLAY % (json.dumps(box), json.dumps(label)), quiet=True)
    pw("screenshot", "--hires", f"--filename={path}")
    if box:
        pw("eval", REMOVE, quiet=True)


def snapshot(path, tries=1, wait=0.0, until=None):
    """ถ่าย snapshot (ถ้ามี until จะวนถ่ายซ้ำจนเงื่อนไขจริงหรือหมดจำนวนครั้ง)"""
    s = None
    for i in range(tries):
        time.sleep(wait)
        rc, out = pw("snapshot", "--boxes", f"--filename={path}", quiet=(i < tries - 1))
        if rc:
            return None
        s = Snap(path)
        if until is None or until(s):
            break
    return s


# ---------------- results ----------------
FLIGHT = re.compile(
    r"^From (?P<price>\d+) Thai baht\. (?P<stops>Nonstop|\d+ stops?) flight with (?P<airline>.+?)\. "
    r"Leaves (?P<from>.+?) at (?P<dep>\d+:\d+ [AP]M) on (?P<dep_day>.+?) and arrives at (?P<to>.+?) at "
    r"(?P<arr>\d+:\d+ [AP]M) on (?P<arr_day>.+?)\. Total duration (?P<dur>.+?)\.(?P<rest>.*)$")


def extract_top3(s):
    flights = []
    # ลิงก์เที่ยวบินไม่มี [ref] จึงอ่านจากบรรทัดดิบของ snapshot
    for ln_no, ln in enumerate(s.lines, 1):
        lm = re.match(r'^\s*-\s*link "(From [^"]*)"', ln)
        m = FLIGHT.match(lm.group(1)) if lm else None
        if not m:
            continue
        it = {"n": ln_no}
        price_line = None
        for j in range(it["n"], min(it["n"] + 60, len(s.lines))):  # หาราคาที่แสดงบนหน้าจอใต้ลิงก์เดียวกัน
            pm = re.search(r"THB [\d,]+", s.lines[j])
            if pm:
                price_line = (j + 1, pm.group(0))
                break
            if j > it["n"] and re.match(r"^\s*-\s*listitem", s.lines[j]):
                break
        flights.append({
            "rank": len(flights) + 1,
            "airline": m["airline"],
            "departs": f'{m["dep"]} {m["dep_day"]} ({m["from"]})',
            "arrives": f'{m["arr"]} {m["arr_day"]} ({m["to"]})',
            "duration": m["dur"],
            "stops": m["stops"],
            "layover": m["rest"].replace("Select flight", "").strip() or None,
            "price_thb": int(m["price"]),
            "price_text": price_line[1] if price_line else None,
            "source": {"summary_line": it["n"], "price_line": price_line[0] if price_line else None,
                       "file": os.path.basename(s.path)},
        })
        if len(flights) == 3:
            break
    return flights


# ---------------- main ----------------
def main():
    global OUT, LOGF
    ap = argparse.ArgumentParser()
    ap.add_argument("--goal", help="แทนแผนด้วยเป้าหมายเดียว ให้ LLM เห็นทุก role")
    ap.add_argument("--out", default="/workspace/log")
    ap.add_argument("--inject", help="ทดสอบ prompt injection: ใส่ปุ่มที่มีข้อความนี้ลงในหน้าหลัง open")
    args = ap.parse_args()
    OUT = os.path.abspath(args.out)
    os.makedirs(OUT, exist_ok=True)
    steps_dir = os.path.join(OUT, "steps")
    if os.path.isdir(steps_dir) and os.listdir(steps_dir):
        os.rename(steps_dir, f"{steps_dir}_prev_{int(time.time())}")
    os.makedirs(steps_dir)
    LOGF = open(os.path.join(OUT, "run.log"), "w", encoding="utf-8")
    os.chdir("/workspace")

    today = datetime.date.today()
    ny, nm = (today.year + 1, 1) if today.month == 12 else (today.year, today.month + 1)
    target = datetime.date(ny, nm, 15)
    log(f"วันนี้ = {today.isoformat()} · วันเดินทาง (15 ของเดือนถัดไป) = {target.isoformat()} ({target:%A})")
    log(f"out = {OUT} · mode = {'custom goal' if args.goal else 'plan'}")

    plan = custom_plan(args.goal) if args.goal else build_plan(target)
    rows, n = [], 0
    final_snap = None
    halted = None

    def halt(msg):
        nonlocal halted
        halted = msg
        log(f"STOP: {msg}")

    pw("close", quiet=True)
    try:
        rc, _ = pw("open", URL)
        if rc:
            halt("เปิดหน้าไม่สำเร็จ")
        elif args.inject:
            pw("eval", INJECT % json.dumps(args.inject))
        for goal in ([] if halted else plan):
            attempts, history = 0, []
            log(f"\n=== เป้าหมาย: {goal['title']} ===")
            while not halted:
                # ---- Observe ----
                tmp = os.path.join(steps_dir, "_observe.yml")
                snap = snapshot(tmp, tries=2, wait=1.5)
                if snap is None:
                    halt("snapshot ไม่สำเร็จ"); break
                final_snap = snap
                if CAPTCHA.search(snap.text):
                    halt("พบ CAPTCHA/unusual traffic"); break
                stage, ev = goal["stage"](snap)
                if not goal.get("custom") and stage >= goal["final"]:
                    log(f"[{goal['key']}] ผ่านแล้ว (stage {stage}) หลักฐาน snapshot:{ev} → ข้าม")
                    rows.append(dict(step="-", goal=goal["title"], action="skip", target="", result="PASS(ข้าม)",
                                     note=f"observe line {ev}"))
                    break
                if n >= MAX_ACTIONS:
                    halt(f"ครบ {MAX_ACTIONS} action แล้วแต่ยังไม่จบ"); break
                if attempts >= MAX_PER_GOAL:
                    halt(f"ติดเป้าหมาย '{goal['title']}' เกิน {MAX_PER_GOAL} ครั้ง"); break
                attempts += 1
                n += 1
                D = os.path.join(steps_dir, f"{n:02d}_{goal['key']}")
                os.makedirs(D)
                os.replace(tmp, f"{D}/snapshot.yml")
                snap = Snap(f"{D}/snapshot.yml")
                final_snap = snap

                # ---- Decide ----
                view = goal["show"](snap, stage)
                shown = {it["ref"] for it in view}
                prompt = build_prompt(goal, view, goal.get("fill"), history)
                open(f"{D}/prompt.txt", "w", encoding="utf-8").write(prompt)
                log(f"[step {n:02d}] {goal['key']} stage={stage} attempt={attempts} ให้ LLM เห็น {len(view)} element")
                ans, err = ask_llm(prompt)
                if ans is None:
                    log(f"  LLM error: {err}")
                    json.dump({"error": err, "approved": False}, open(f"{D}/decision.json", "w"), ensure_ascii=False, indent=2)
                    rows.append(dict(step=n, goal=goal["title"], action="llm", target="", result="FAIL", note="LLM error"))
                    history.append("- LLM ตอบไม่ได้")
                    continue
                log(f"  LLM: {ans}")
                action, ref, value = ans.get("action"), ans.get("ref"), ans.get("value", "")

                # ---- Validate ----
                it = snap.by_ref.get(ref)
                role, name = (it["role"], it["name"]) if it else (None, "")
                checks = {"action_in_allowlist": action in ALLOW}
                if action != "stop":
                    checks["ref_in_snapshot"] = it is not None
                    checks["ref_in_view"] = ref in shown
                    checks["name_not_denylisted"] = not DENY.search(f"{name} {value}")
                    if action == "fill":
                        okv = (value == goal["fill"]) if goal.get("fill") else \
                            (goal.get("custom") and value != "" and value in goal["text"])
                        checks["fill_value_allowed"] = bool(okv) and role in ("combobox", "textbox")
                    if action == "press":
                        checks["press_key_allowed"] = value in KEYS
                    if action == "click" and role == "option" and goal.get("opt"):
                        checks["option_matches_goal"] = bool(re.search(goal["opt"], name))
                ok = all(checks.values())
                json.dump({"llm_answer": ans, "element": {"role": role, "name": name, "box": it["box"] if it else None},
                           "stage_before": stage, "shown_refs": sorted(shown),
                           "checks": {k: "pass" if v else "fail" for k, v in checks.items()}, "approved": ok},
                          open(f"{D}/decision.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
                if not checks.get("name_not_denylisted", True):
                    rows.append(dict(step=n, goal=goal["title"], action=action, target=name, result="FAIL", note="DENYLIST"))
                    halt(f"denylist: '{name}' → หยุดทั้ง run"); break
                if action == "stop":
                    if goal.get("custom"):
                        rows.append(dict(step=n, goal=goal["title"], action="stop", target="", result="PASS",
                                         note=ans.get("reason", "")[:60]))
                        break
                    rows.append(dict(step=n, goal=goal["title"], action="stop", target="", result="FAIL",
                                     note="LLM หา element ไม่เจอ"))
                    halt("LLM ตอบ stop (ไม่มี element ที่เหมาะสม)"); break
                if not ok:
                    bad = [k for k, v in checks.items() if not v]
                    log(f"  validate ไม่ผ่าน: {bad}")
                    open(f"{D}/act.txt", "w", encoding="utf-8").write(f"REJECTED by validator: {bad}\nLLM: {ans}\n")
                    rows.append(dict(step=n, goal=goal["title"], action=action, target=f"{role} {name}"[:40],
                                     result="FAIL", note=f"rejected {bad}"))
                    history.append(f"- {action} {ref} '{name}' ถูกปฏิเสธ ({','.join(bad)})")
                    continue

                # ---- evidence (วงกลมแดง + callout) ----
                label = f"Step {n:02d} · {action} {ref}" + (f' = "{value}"' if action == "fill" else "")
                shoot(f"{D}/page.png", it["box"], label)

                # ---- Act ----
                cmd = {"click": ["click", ref], "fill": ["fill", ref, value], "press": ["press", value]}[action]
                rc, out = pw(*cmd)
                pm = re.search(r"Page URL:\s*(\S+)", out)
                off_page = bool(pm and not pm.group(1).startswith(SAFE_URL))

                # ---- Verify (snapshot ใหม่ + ตัดสินด้วยโค้ด) ----
                if goal.get("custom"):
                    time.sleep(1.5)
                    v = snapshot(f"{D}/verify.yml")
                    passed = v is not None and v.signature() != snap.signature()
                    vev = "หน้าเปลี่ยนจากเดิม" if passed else "หน้าไม่เปลี่ยน"
                    new_stage = 0
                else:
                    wait = goal["key"] == "search"
                    v = snapshot(f"{D}/verify.yml", tries=8 if wait else 3, wait=2.0 if wait else 1.0,
                                 until=lambda s: goal["stage"](s)[0] > stage)
                    new_stage, vline = goal["stage"](v) if v else (stage, None)
                    passed = rc == 0 and v is not None and new_stage > stage
                    vev = f"stage {stage}→{new_stage}" + (f" · verify.yml:{vline}: {v.lines[vline-1].strip()[:120]}" if vline else "")
                final_snap = v or final_snap
                with open(f"{D}/act.txt", "w", encoding="utf-8") as f:
                    f.write(f"command: playwright-cli {' '.join(cmd)}\nexit code: {rc}\noutput: {out[:400]}\n\n")
                    f.write(f"target: {role} \"{name}\" [ref={ref}]\n\nVERIFY: {'PASS' if passed else 'FAIL'}\n  {vev}\n")
                log(f"  verify: {'PASS' if passed else 'FAIL'} · {vev}")
                rows.append(dict(step=n, goal=goal["title"], action=f"{action}" + (f" '{value}'" if action == "fill" else ""),
                                 target=f"{role} {name}"[:42], result="PASS" if passed else "FAIL", note=vev[:50]))
                if not passed:
                    history.append(f"- {action} {ref} '{name}' แล้วหน้าไม่คืบหน้า")
                if off_page:
                    halt(f"หน้าออกนอก {SAFE_URL}: {pm.group(1)[:80]}"); break
                if v is not None and CAPTCHA.search(v.text):
                    halt("พบ CAPTCHA/unusual traffic"); break
                if goal.get("custom"):
                    history.append(f"- {action} {ref} '{name}' แล้ว{'หน้าเปลี่ยน' if passed else 'หน้าไม่เปลี่ยน'}")
            if halted:
                break

        # ---------- ผลลัพธ์ top3 ----------
        top3 = []
        if not halted and final_snap is not None:
            n += 1
            D = os.path.join(steps_dir, f"{n:02d}_results")
            os.makedirs(D)
            s = snapshot(f"{D}/snapshot.yml") or final_snap
            top3 = extract_top3(s)
            pw("screenshot", "--hires", f"--filename={D}/page.png")
            json.dump(top3, open(f"{D}/top3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            ok3 = len(top3) == 3 or (args.goal and top3)
            rows.append(dict(step=n, goal="ผลลัพธ์", action="extract", target="3 เที่ยวบินแรก",
                             result="PASS" if ok3 else ("FAIL" if not args.goal else "-"),
                             note=f"พบ {len(top3)} รายการ"))
    finally:
        pw("close")

    # ---------- สรุป ----------
    log("\n" + "=" * 100)
    log(f"{'step':<5}{'goal':<22}{'action':<14}{'target':<44}{'result':<12}note")
    for r in rows:
        log(f"{str(r['step']):<5}{r['goal'][:20]:<22}{r['action'][:12]:<14}{r['target'][:42]:<44}{r['result']:<12}{r['note']}")
    if halted:
        log(f"\nหยุดก่อนจบ: {halted}")
    if top3:
        log("\nTop 3 เที่ยวบิน (จาก snapshot หน้าผลค้นหา)")
        for t in top3:
            log(f"#{t['rank']} {t['airline']} | ออก {t['departs']} | ถึง {t['arrives']} | {t['duration']} | {t['stops']} | "
                f"THB {t['price_thb']:,} (หน้าจอ: {t['price_text']}) | snapshot line {t['source']['summary_line']}")
    log(f"\nหลักฐาน: {OUT}/steps/ · log: {OUT}/run.log")
    LOGF.close()
    sys.exit(0 if not halted and (top3 or args.goal) else 1)


if __name__ == "__main__":
    main()
