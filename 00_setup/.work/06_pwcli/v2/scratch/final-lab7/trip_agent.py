#!/usr/bin/env python3
"""trip_agent: agent เต็มรูปแบบแบบ code-in-control (ต่อยอด lab5/one_step.py)

playwright-cli = ตาและมือ · LLM (yolo1 haiku, ไม่มี tool) = เลือก 1 action ต่อครั้ง · โค้ด = ผู้คุม
แผน = ลำดับเป้าหมาย แต่ละเป้าหมายวน Observe -> (ผ่านแล้วข้าม) -> Decide -> Validate -> Act -> Verify
ค้นหาอย่างเดียว ห้ามล็อกอิน ห้ามจอง

ใช้: python3 trip_agent.py [--goal "<ข้อความ>"] [--out /workspace/log]
"""
import argparse, json, os, re, shutil, subprocess, sys, time
from datetime import date

URL = "https://www.google.com/travel/flights?hl=en"
SITE_PREFIX = "https://www.google.com/travel/flights"
MAX_ACTIONS = 25
MAX_PER_GOAL = 5
ALLOW = {"click", "fill", "press", "stop"}
FORM_ROLES = {"button", "combobox", "textbox", "option"}
FREE_KEYS = {"Enter", "Escape", "ArrowDown", "ArrowUp", "Tab"}
DENY = re.compile(r"book|sign in|payment|select flight|select fare", re.I)
CAPTCHA = re.compile(r"captcha|unusual traffic|not a robot", re.I)
SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": sorted(ALLOW)},
        "ref": {"type": "string"},
        "value": {"type": "string"},
        "reason": {"type": "string"},
    },
    "required": ["action", "ref", "value", "reason"],
    "additionalProperties": False,
}

OUT = "/workspace/log"
_log_fh = None


def log(msg=""):
    print(msg, flush=True)
    if _log_fh:
        _log_fh.write(msg + "\n")
        _log_fh.flush()


def pw(*args, quiet=False):
    r = subprocess.run(["playwright-cli", *args], capture_output=True, text=True)
    out = r.stdout.strip()
    r.ok = r.returncode == 0 and "### Error" not in out
    if not quiet:
        log(f"$ playwright-cli {' '.join(args)[:160]}\n{out[:300]}")
        if r.returncode != 0:
            log(r.stderr.strip()[:300])
    return r


def target_date(today):
    y, m = (today.year + 1, 1) if today.month == 12 else (today.year, today.month + 1)
    return date(y, m, 15)


# ---------- snapshot parser ----------
NODE_RE = re.compile(r'^([\w-]+)(?: "((?:[^"\\]|\\.)*)")?((?: \[[^\]]*\])*)\s*(?::\s*(.*))?$')
BOX_RE = re.compile(r"box=(-?[\d.]+),(-?[\d.]+),([\d.]+),([\d.]+)")


def _split_quoted(s):
    """'key ...': value  (YAML single-quoted, '' = ') -> (key, tail)"""
    i = 1
    while i < len(s):
        if s[i] == "'":
            if i + 1 < len(s) and s[i + 1] == "'":
                i += 2
                continue
            return s[1:i].replace("''", "'"), s[i + 1:]
        i += 1
    return s[1:], ""


def parse_snapshot(path):
    """คืน list ของ element dict: line, indent, role, name, value, attrs, ref, box"""
    els = []
    for n, ln in enumerate(open(path, encoding="utf-8").read().splitlines(), 1):
        st = ln.lstrip()
        if not st.startswith("- "):
            continue
        indent = len(ln) - len(st)
        s, tail = st[2:], ""
        if s.startswith("'"):
            s, tail = _split_quoted(s)
            tail = tail.lstrip(":").strip()
        m = NODE_RE.match(s)
        if not m:
            continue
        role, name, attrs, value = m.groups()
        value = (tail or value or "").strip()
        if len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1]
        ref = re.search(r"\[ref=(e\d+)\]", attrs or "")
        box = BOX_RE.search(attrs or "")
        els.append({
            "line": n, "indent": indent, "role": role,
            "name": (name or "").replace('\\"', '"'), "value": value,
            "attrs": re.findall(r"\[([^\]=]+)\]", attrs or ""),
            "ref": ref.group(1) if ref else None,
            "box": [float(x) for x in box.groups()] if box else None,
        })
    return els


def subtree(els, role):
    """element ทั้งหมดใต้ node แรกที่มี role นี้ (ตาม indent)"""
    for i, e in enumerate(els):
        if e["role"] == role:
            out = []
            for x in els[i + 1:]:
                if x["indent"] <= e["indent"]:
                    break
                out.append(x)
            return out
    return []


def view_line(e):
    s = f'- {e["role"]} "{e["name"]}" [ref={e["ref"]}]'
    for f in ("expanded", "selected", "disabled"):
        if f in e["attrs"]:
            s += f" [{f}]"
    return s + (f': {e["value"]}' if e["value"] else "")


# ---------- goals ----------
class Goal:
    def __init__(self, name, text, passed, cands, fill=None):
        self.name, self.text, self.passed, self.cands, self.fill = name, text, passed, cands, fill


def form_els(els):
    return [e for e in subtree(els, "search")]


def pick(els, role_set, name_re):
    rx = re.compile(name_re)
    return [e for e in form_els(els)
            if e["role"] in role_set and e["ref"] and e["box"] and e["name"] and rx.search(e["name"])]


def dialog_open(els):
    return any(e["role"] == "dialog" for e in form_els(els))


def build_plan(tgt):
    tgt_btn = f"{tgt:%A}, {tgt:%B} {tgt.day}, {tgt.year}"
    dep_val = f"{tgt:%a}, {tgt:%b} {tgt.day}"

    def has(els, role, pred):
        return any(e["role"] == role and pred(e) for e in form_els(els))

    def ticket_ok(els):
        return has(els, "combobox", lambda e: e["name"].startswith("Change ticket type") and e["name"].endswith("One way"))

    def class_ok(els):
        return (has(els, "combobox", lambda e: e["name"].startswith("Change seating class") and e["name"].endswith("Economy"))
                and has(els, "button", lambda e: e["name"].startswith("1 passenger")))

    def origin_ok(els):
        return has(els, "combobox", lambda e: e["name"].startswith("Where from?") and "BKK" in e["name"]) and not dialog_open(els)

    def dest_ok(els):
        return (has(els, "combobox", lambda e: e["name"].startswith("Where to?") and "Tokyo" in e["value"]
                    and "expanded" not in e["attrs"]) and not dialog_open(els))

    def dep(els):
        return next((e for e in form_els(els) if e["role"] == "textbox" and e["name"] == "Departure"), None)

    def date_ok(els):
        d = dep(els)
        return bool(d and dep_val in d["value"]) and not any(e["role"] == "grid" for e in form_els(els)) and not dialog_open(els)

    def date_cands(els):
        if any(e["role"] == "grid" for e in form_els(els)):  # ปฏิทินเปิดอยู่
            d = dep(els)
            if d and dep_val in d["value"]:
                return pick(els, {"button"}, r"^Done")
            return pick(els, {"button"}, "^" + re.escape(tgt_btn))  # เห็นแค่ปุ่มวันที่เป้าหมาย
        return pick(els, {"textbox"}, r"^Departure$")

    def results_ok(els):
        return any(e["role"] == "link" and e["name"].startswith("From ") and e["name"].endswith("Select flight") for e in els)

    return [
        Goal("ticket", "เลือกประเภทตั๋วเป็น One way (ถ้าลิสต์ยังไม่เปิดให้เปิด combobox ประเภทตั๋วก่อน แล้วเลือก option One way)",
             ticket_ok, lambda els: pick(els, FORM_ROLES, r"Change ticket type|^(Round trip|One way|Multi-city)$")),
        Goal("check", "ตรวจว่าชั้นโดยสารเป็น Economy และผู้โดยสาร 1 คน",
             class_ok, lambda els: pick(els, FORM_ROLES, r"seating class|passenger|^(Economy|Premium economy|Business|First)$")),
        Goal("origin", "ตั้งต้นทางเป็น Suvarnabhumi Airport (BKK) (เปิดช่อง Where from, พิมพ์ BKK แล้วเลือก option Suvarnabhumi Airport (BKK))",
             origin_ok, lambda els: pick(els, {"combobox", "textbox", "option"}, r"^(Where from|Where else)|^Suvarnabhumi Airport \(BKK\)$"),
             fill="BKK"),
        Goal("dest", "ตั้งปลายทางเป็น Tokyo, Japan (เปิดช่อง Where to, พิมพ์ Tokyo แล้วเลือก option \"Tokyo, Japan\" จากลิสต์)",
             dest_ok, lambda els: pick(els, {"combobox", "textbox", "option"}, r"^Where to|^Tokyo, Japan$"), fill="Tokyo"),
        Goal("date", f"ตั้งวันเดินทางเป็น {tgt_btn} (เปิดช่อง Departure, กดปุ่มวันที่ แล้วกด Done)",
             date_ok, date_cands),
        Goal("search", "กดปุ่ม Search เพื่อค้นหาเที่ยวบิน",
             results_ok, lambda els: pick(els, {"button"}, r"^Search$")),
    ]


def free_goal(text):
    def cands(els):
        return [e for e in els if e["ref"] and e["name"] and e["role"] not in ("generic", "heading", "paragraph")]
    return Goal("free", text, lambda els: False, cands)


# ---------- overlay (แบบ LAB 5) ----------
def overlay_js(box, label):
    x, y, w, h = box
    return """() => {
  const [x, y, w, h] = %s, label = %s, NS = 'http://www.w3.org/2000/svg';
  const vw = window.innerWidth, vh = window.innerHeight, p = 8;
  const svg = document.createElementNS(NS, 'svg');
  svg.id = '__step_overlay';
  svg.setAttribute('width', vw); svg.setAttribute('height', vh);
  svg.style.cssText = 'position:fixed;left:0;top:0;z-index:2147483647;pointer-events:none';
  const el = document.createElementNS(NS, 'ellipse');
  el.setAttribute('cx', x + w / 2); el.setAttribute('cy', y + h / 2);
  el.setAttribute('rx', w / 2 * 1.4142 + p); el.setAttribute('ry', h / 2 * 1.4142 + p);
  el.setAttribute('fill', 'none'); el.setAttribute('stroke', 'red'); el.setAttribute('stroke-width', 3);
  svg.appendChild(el);
  document.body.appendChild(svg);
  const t = document.createElement('div');
  t.id = '__step_label'; t.textContent = label;
  t.style.cssText = 'position:fixed;z-index:2147483647;pointer-events:none;background:#fff;color:#c00;border:2px solid red;border-radius:6px;padding:4px 10px;font:bold 16px sans-serif;white-space:nowrap';
  document.body.appendChild(t);
  const tw = t.offsetWidth, th = t.offsetHeight, ry = h / 2 * 1.4142 + p;
  const cy = y + h / 2;
  let ty = cy - ry - th - 6;
  if (ty < 4) ty = cy + ry + 6;
  let tx = Math.min(Math.max(x + w / 2 - tw / 2, 4), vw - tw - 4);
  t.style.left = tx + 'px'; t.style.top = ty + 'px';
  return 'ok';
}""" % (json.dumps([x, y, w, h]), json.dumps(label))


REMOVE_JS = "() => { for (const id of ['__step_overlay','__step_label']) document.getElementById(id)?.remove(); return 'removed'; }"


# ---------- LLM ----------
def decide(goal, view, feedback, free):
    rules = [
        "เลือก ref จากรายการข้างบนเท่านั้น ห้ามคิด ref เอง",
        "action ต้องเป็น click, fill, press หรือ stop เท่านั้น",
        "ตัดสินใจเพียง 1 การกระทำที่ใกล้เป้าหมายที่สุด",
        "ห้ามกดปุ่มที่เกี่ยวกับการจอง การล็อกอิน หรือการชำระเงิน",
    ]
    if goal.fill:
        rules.append(f'ถ้าใช้ fill ให้ value เป็น "{goal.fill}" เท่านั้น และ fill ได้เฉพาะช่องพิมพ์ (combobox/textbox)')
    elif not free:
        rules.append("ห้ามใช้ fill และ press")
    else:
        rules.append("press ใส่ชื่อปุ่มใน value เช่น Enter, Escape")
    rules += ["ถ้าไม่มี element ที่เหมาะสมให้ใช้ action=stop และ ref เป็นสตริงว่าง", "ถ้าไม่ใช้ value ให้ใส่สตริงว่าง"]
    prompt = (f"เป้าหมาย: {goal.text}\n\n"
              "รายการ element บนหน้าเว็บ พร้อม ref:\n" + "\n".join(view) + "\n\n"
              + ("ผลการลองครั้งก่อน (ถ้าซ้ำให้เปลี่ยนวิธี): " + feedback + "\n\n" if feedback else "")
              + "กติกา:\n" + "\n".join(f"- {r}" for r in rules) + "\n\n"
              'รูปแบบคำตอบ JSON: {"action": "...", "ref": "...", "value": "...", "reason": "..."}\n')
    return prompt


def ask_llm(prompt):
    r = subprocess.run(
        ["yolo1", "-p", "--model", "haiku", "--effort", "low", "--output-format", "json",
         "--json-schema", json.dumps(SCHEMA), "--no-session-persistence",
         "--strict-mcp-config", "--tools", ""],
        input=prompt, capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        return None, "yolo1 ล้มเหลว: " + r.stderr[:300]
    try:
        ans = json.loads(r.stdout).get("structured_output")
    except json.JSONDecodeError:
        return None, "yolo1 ตอบไม่ใช่ JSON"
    return (ans, "") if isinstance(ans, dict) else (None, "ไม่มี structured_output")


# ---------- results ----------
def extract_top3(path):
    els = parse_snapshot(path)
    rows = []
    for e in els:
        n = e["name"]
        if e["role"] != "link" or not n.startswith("From ") or not n.endswith("Select flight"):
            continue
        def g(rx):
            m = re.search(rx, n)
            return m.group(1) if m else None
        stops = "Nonstop" if re.search(r"\bNonstop flight", n) else (g(r"(\d+ stops?) flight"))
        price = g(r"^From ([\d,]+) Thai baht")
        dep = re.search(r"Leaves (.+?) at (\d+:\d+ [AP]M) on (.+?) and arrives at (.+?) at (\d+:\d+ [AP]M) on (.+?)\. Total duration", n)
        rows.append({
            "source_line": e["line"],
            "airline": g(r"flight with (.+?)\. Leaves"),
            "price_thb": int(price.replace(",", "")) if price else None,
            "stops": stops,
            "duration": g(r"Total duration (.+?)\."),
            "layover": g(r"(Layover.+?)(?: Select flight)$"),
            "depart_airport": dep.group(1) if dep else None,
            "depart_time": dep.group(2) if dep else None,
            "depart_date": dep.group(3) if dep else None,
            "arrive_airport": dep.group(4) if dep else None,
            "arrive_time": dep.group(5) if dep else None,
            "arrive_date": dep.group(6) if dep else None,
            "raw": n,
        })
        if len(rows) == 3:
            break
    return rows


# ---------- main loop ----------
def current_url():
    r = pw("eval", "() => location.href", quiet=True)
    m = re.search(r'"(https?://[^"]+)"', r.stdout)
    return m.group(1) if m else ""


def snap_to(path):
    pw("snapshot", "--boxes", f"--filename={path}", quiet=True)
    return parse_snapshot(path) if os.path.exists(path) else []


def run(args):
    global OUT, _log_fh
    OUT = args.out
    os.makedirs(f"{OUT}/steps", exist_ok=True)
    _log_fh = open(f"{OUT}/run.log", "w", encoding="utf-8")
    today = date.today()
    tgt = target_date(today)
    log(f"== trip_agent เริ่ม {time.strftime('%Y-%m-%d %H:%M:%S')} ==")
    log(f"วันนี้ = {today.isoformat()} -> วันเดินทาง (วันที่ 15 ของเดือนถัดไป) = {tgt.isoformat()} ({tgt:%A, %B} {tgt.day}, {tgt.year})")
    free = bool(args.goal)
    plan = [free_goal(args.goal)] if free else build_plan(tgt)
    log("แผน: " + " -> ".join(g.name for g in plan))

    rows, n = [], 0          # rows: ตารางสรุป step
    status, reason = "DONE", ""
    tmp = f"{OUT}/_observe.yml"
    els = []
    pw("open", URL)
    if args.inject:
        time.sleep(3)
        js = ("() => { const b = document.createElement('button'); b.textContent = %s; "
              "b.style.cssText = 'position:fixed;left:10px;top:10px;z-index:99999;padding:8px'; "
              "document.body.appendChild(b); return 'injected'; }") % json.dumps(args.inject)
        log("[inject] " + pw("eval", js).stdout.strip()[:100])
    try:
        for goal in plan:
            attempts, feedback = 0, ""
            log(f"\n##### เป้าหมาย: {goal.name} — {goal.text}")
            while True:
                # 1. Observe
                url = current_url()
                els = snap_to(tmp)
                text = open(tmp, encoding="utf-8").read() if os.path.exists(tmp) else ""
                log(f"[observe] url={url[:100]} elements={len(els)}")
                if CAPTCHA.search(text):
                    status, reason = "STOP", "พบ CAPTCHA/unusual traffic"; break
                if not url.startswith(SITE_PREFIX):
                    status, reason = "STOP", f"ออกนอกหน้า Google Flights: {url[:100]}"; break
                if goal.passed(els):
                    log(f"[{goal.name}] ผ่านแล้ว" + (" (ข้าม ไม่ต้องทำอะไร)" if attempts == 0 else ""))
                    if attempts == 0:
                        rows.append({"step": "-", "goal": goal.name, "action": "-", "target": "-",
                                     "validate": "-", "verify": "SKIP", "note": "ผ่านอยู่แล้ว"})
                    break
                if attempts >= MAX_PER_GOAL:
                    status, reason = "STOP", f"ติดเป้าหมาย {goal.name} เกิน {MAX_PER_GOAL} ครั้ง"; break
                if n >= MAX_ACTIONS:
                    status, reason = "STOP", f"ครบ {MAX_ACTIONS} action แล้ว"; break

                n += 1
                attempts += 1
                D = f"{OUT}/steps/{n:02d}_{goal.name}"
                os.makedirs(D, exist_ok=True)
                shutil.copy(tmp, f"{D}/snapshot.yml")
                row = {"step": n, "goal": goal.name, "action": "-", "target": "-", "validate": "-", "verify": "-", "note": ""}
                rows.append(row)
                log(f"\n--- step {n:02d} [{goal.name}] ครั้งที่ {attempts}/{MAX_PER_GOAL} ---")

                cands = goal.cands(els)
                by_ref = {e["ref"]: e for e in cands}
                view = [view_line(e) for e in cands][:400]
                if not cands:
                    feedback = "ไม่พบ element ที่เกี่ยวข้องบนหน้า"
                    row.update(validate="FAIL", verify="FAIL", note=feedback)
                    open(f"{D}/prompt.txt", "w").write("(ไม่มี candidate จึงไม่เรียก LLM)\n")
                    json.dump({"result": "fail", "reason": feedback}, open(f"{D}/decision.json", "w"), ensure_ascii=False, indent=2)
                    open(f"{D}/act.txt", "w").write("ไม่ได้รันคำสั่ง: " + feedback + "\n")
                    log(feedback); time.sleep(1.5)
                    continue

                # 2. Decide
                prompt = decide(goal, view, feedback, free)
                open(f"{D}/prompt.txt", "w", encoding="utf-8").write(prompt)
                ans, err = ask_llm(prompt)
                log(f"[decide] LLM: {ans} {err}")
                if ans is None:
                    feedback = err
                    row.update(validate="FAIL", verify="FAIL", note=err)
                    json.dump({"result": "fail", "reason": err}, open(f"{D}/decision.json", "w"), ensure_ascii=False, indent=2)
                    open(f"{D}/act.txt", "w").write("ไม่ได้รันคำสั่ง: " + err + "\n")
                    continue

                # 3. Validate
                action, ref, value = ans.get("action"), ans.get("ref", ""), ans.get("value", "")
                el = by_ref.get(ref)
                checks = {"action_in_allowlist": action in ALLOW}
                if action == "stop":
                    pass
                elif action in ("click", "fill"):
                    checks["ref_in_snapshot"] = any(e["ref"] == ref for e in els)
                    checks["ref_in_candidates"] = el is not None
                    checks["has_box"] = bool(el and el["box"])
                    if action == "fill":
                        checks["fill_target_is_input"] = bool(el and el["role"] in ("combobox", "textbox"))
                        checks["fill_value_allowed"] = (len(value) <= 80 and bool(value)) if free else value == goal.fill
                elif action == "press":
                    checks["press_key_allowed"] = free and value in FREE_KEYS
                deny_txt = " | ".join(filter(None, [el["name"] if el else "", value, ref if not el else ""]))
                deny_hit = bool(DENY.search(deny_txt))
                checks["not_denylisted"] = not deny_hit
                ok = all(checks.values())
                row.update(action=action or "?", target=f'{ref} "{el["name"][:40]}"' if el else ref,
                           validate="PASS" if ok else "FAIL")
                json.dump({"llm_answer": ans,
                           "element": {"role": el["role"], "name": el["name"], "box": el["box"]} if el else None,
                           "checks": {k: "pass" if v else "fail" for k, v in checks.items()},
                           "result": "pass" if ok else "fail"},
                          open(f"{D}/decision.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
                log(f"[validate] {checks}")
                if deny_hit:
                    row.update(verify="FAIL", note="DENYLIST")
                    open(f"{D}/act.txt", "w").write("ไม่ได้รันคำสั่ง: denylist\n")
                    status, reason = "STOP", f"Validate พบ denylist ใน step {n}: {deny_txt[:80]}"; break
                if action == "stop":
                    row.update(verify="-", note="LLM สั่ง stop: " + ans.get("reason", "")[:60])
                    open(f"{D}/act.txt", "w").write("LLM เลือก stop\n")
                    status, reason = "STOP", "LLM เลือก stop: " + ans.get("reason", "")
                    if free:
                        status, reason = "DONE", "LLM สั่ง stop (ถือว่าจบ): " + ans.get("reason", "")
                    break
                if not ok:
                    bad = [k for k, v in checks.items() if not v]
                    feedback = f"action {action} ref {ref} ไม่ผ่านการตรวจ: {bad}"
                    row.update(verify="FAIL", note="validate ไม่ผ่าน " + ",".join(bad))
                    open(f"{D}/act.txt", "w").write("ไม่ได้รันคำสั่ง: " + feedback + "\n")
                    log("Validate ไม่ผ่าน -> ไม่รันคำสั่ง แล้วตัดสินใหม่")
                    continue

                # หลักฐานภาพ: วงกลมแดง + callout
                if el:
                    lbl = f"Step {n} · {action} {ref}" + (f' "{value}"' if action == "fill" else "")
                    pw("eval", overlay_js(el["box"], lbl), quiet=True)
                pw("screenshot", "--hires", f"--filename={D}/page.png", quiet=True)
                pw("eval", REMOVE_JS, quiet=True)

                # 4. Act
                cmd = [action] + ([ref] if ref and action != "press" else []) + ([value] if action in ("fill", "press") else [])
                before_sig = {(e["role"], e["name"]) for e in cands}
                ra = pw(*cmd)
                is_search = goal.name == "search"
                time.sleep(4 if is_search else 1.2)

                # 5. Verify (ด้วยโค้ดจาก snapshot ใหม่)
                vp = f"{D}/verify.yml"
                vels = snap_to(vp)
                for _ in range(3 if is_search else 0):
                    if goal.passed(vels):
                        break
                    time.sleep(2.5)
                    vels = snap_to(vp)
                passed = goal.passed(vels)
                after_sig = {(e["role"], e["name"]) for e in goal.cands(vels)}
                progressed = after_sig != before_sig
                if action == "fill":
                    progressed = any(e["role"] == "option" for e in goal.cands(vels)) or passed
                v_ok = ra.ok and (passed or (progressed and not free) or (free and progressed))
                ref_after = [e for e in vels if e["ref"] == ref]
                ref_txt = "ไม่อยู่แล้ว"
                if ref_after:
                    ra0 = ref_after[0]
                    ref_txt = "ยังอยู่ %s '%s' (verify.yml:%d)" % (ra0["role"], ra0["name"][:50], ra0["line"])
                out = [f"คำสั่งที่รัน: playwright-cli {' '.join(cmd)}  (exit={ra.returncode}, ok={ra.ok})",
                       f"output ย่อ: {ra.stdout.strip()[:400]}",
                       f"เป้าหมาย {goal.name} ผ่านหรือยัง: {'PASS' if passed else 'ยัง'}",
                       f"candidate เปลี่ยนไปจากก่อน act: {'ใช่' if progressed else 'ไม่'}",
                       f"ผล verify: {'PASS' if v_ok else 'FAIL'}",
                       f"ref เดิม {ref} ใน snapshot ใหม่: {ref_txt}"]
                open(f"{D}/act.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
                log("[act/verify]\n" + "\n".join(out))
                row.update(verify="PASS" if v_ok else "FAIL",
                           note=("goal ผ่าน" if passed else ("ความคืบหน้า" if v_ok else "ไม่เห็นผล")))
                feedback = "" if v_ok else f"{action} {ref} แล้วหน้าไม่เปลี่ยนตามคาด"
                els = vels
                if not ra.ok:
                    feedback = "คำสั่งล้มเหลว: " + ra.stdout.strip()[-150:]
                # วนกลับไป Observe ใหม่
            if status == "STOP" or (free and status == "DONE" and reason):
                break

        # ผลลัพธ์: 3 เที่ยวบินแรก
        top3 = []
        if status == "DONE":
            n += 1
            D = f"{OUT}/steps/{n:02d}_results"
            os.makedirs(D, exist_ok=True)
            pw("snapshot", "--boxes", f"--filename={D}/snapshot.yml", quiet=True)
            pw("screenshot", "--hires", f"--filename={D}/page.png", quiet=True)
            top3 = extract_top3(f"{D}/snapshot.yml")
            json.dump({"target_date": tgt.isoformat(), "top3": top3}, open(f"{D}/top3.json", "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
            ok3 = len(top3) == 3 and all(t["price_thb"] for t in top3)
            rows.append({"step": n, "goal": "results", "action": "extract", "target": f"{len(top3)} flights",
                         "validate": "-", "verify": "PASS" if ok3 else "FAIL",
                         "note": "top3.json"})
            if not top3 and not free:
                status, reason = "STOP", "ไม่พบเที่ยวบินใน snapshot ผลค้นหา"
    finally:
        pw("close")
        if os.path.exists(tmp):
            os.remove(tmp)

    # ---------- รายงาน ----------
    log(f"\n== สรุป: {status} {reason} ==")
    hdr = f'{"step":<5}{"goal":<9}{"action":<8}{"target":<48}{"validate":<9}{"verify":<7}note'
    log(hdr)
    log("-" * len(hdr))
    for r in rows:
        log(f'{str(r["step"]):<5}{r["goal"]:<9}{r["action"]:<8}{r["target"][:46]:<48}{r["validate"]:<9}{r["verify"]:<7}{r["note"]}')
    log(f"\nวันเดินทางที่ค้นหา: {tgt.isoformat()}")
    if top3:
        log("Top 3 เที่ยวบิน (อ่านจาก snapshot; บรรทัดที่มาอยู่ใน top3.json):")
        for i, t in enumerate(top3, 1):
            log(f'{i}. {t["airline"]} | {t["depart_time"]} -> {t["arrive_time"]} | {t["duration"]} | {t["stops"]} | '
                f'{t["price_thb"]:,} THB | snapshot.yml:{t["source_line"]}' if t["price_thb"] else f"{i}. {t['raw']}")
    _log_fh.close()
    return 0 if status == "DONE" else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--goal", help="เป้าหมายเดียวแบบอิสระ (แทนแผน) ให้ LLM เห็นทุก role")
    ap.add_argument("--inject", help="ใส่ปุ่มที่มีข้อความนี้ลงในหน้าหลัง open (ทดสอบ prompt injection)")
    ap.add_argument("--out", default="/workspace/log", help="โฟลเดอร์เก็บ log/steps")
    sys.exit(run(ap.parse_args()))
