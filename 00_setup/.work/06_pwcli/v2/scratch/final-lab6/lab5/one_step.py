#!/usr/bin/env python3
"""1 step แบบ code-in-control: Observe -> Decide -> Validate -> Act -> Verify"""
import json, os, re, subprocess, sys

URL = "https://www.google.com/travel/flights?hl=en"
GOAL = "เปิดรายการประเภทตั๋ว (Change ticket type) เพื่อจะเลือก One way"
D = "lab5/step"
ALLOW = {"click", "fill", "press", "stop"}
DENY = re.compile(r"book|sign in|payment|select flight|select fare", re.I)
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
LINE_RE = re.compile(r'^\s*-\s*(button|combobox|textbox|option)\s+"([^"]+)".*?\[ref=(e\d+)\]')
BOX_RE = re.compile(r"\s*\[box=[^\]]*\]")


def pw(*args):
    r = subprocess.run(["playwright-cli", *args], capture_output=True, text=True)
    print(f"$ playwright-cli {' '.join(args)[:150]}\n{r.stdout.strip()[:300]}")
    if r.returncode != 0:
        print(r.stderr.strip()[:300])
    return r


def parse(path):
    """คืน {ref: (role, name, box|None)} และบรรทัดที่ตัดแล้ว"""
    els, kept = {}, []
    for ln in open(path, encoding="utf-8"):
        m = LINE_RE.match(ln)
        if not m:
            continue
        role, name, ref = m.groups()
        b = re.search(r"\[box=(-?[\d.]+),(-?[\d.]+),([\d.]+),([\d.]+)\]", ln)
        els[ref] = (role, name, [float(x) for x in b.groups()] if b else None)
        kept.append(BOX_RE.sub("", ln.rstrip()).strip())
    return els, kept


def overlay_js(box, ref):
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
  // วางเหนือวงรีถ้าพอ ไม่งั้นวางใต้วงรี
  let ty = cy - ry - th - 6;
  if (ty < 4) ty = cy + ry + 6;
  let tx = Math.min(Math.max(x + w / 2 - tw / 2, 4), vw - tw - 4);
  t.style.left = tx + 'px'; t.style.top = ty + 'px';
  return 'ok';
}""" % (json.dumps([x, y, w, h]), json.dumps(label_text(ref)))


def label_text(ref):
    return f"Step 1 · click {ref}"


REMOVE_JS = "() => { for (const id of ['__step_overlay','__step_label']) document.getElementById(id)?.remove(); return 'removed'; }"


def main():
    os.makedirs(D, exist_ok=True)
    snap, verify = f"{D}/snapshot.yml", f"{D}/verify.yml"
    try:
        # 1. Observe
        print("== Observe ==")
        pw("open", URL)
        pw("snapshot", "--boxes", f"--filename={snap}")
        pw("screenshot", "--hires", f"--filename={D}/observe.png")

        # 2. Decide
        print("== Decide ==")
        els, kept = parse(snap)
        prompt = (
            f"เป้าหมาย: {GOAL}\n\n"
            "รายการ element บนหน้าเว็บ (button/combobox/textbox/option) พร้อม ref:\n"
            + "\n".join(kept) + "\n\n"
            "กติกา:\n"
            "- เลือก ref จากรายการข้างบนเท่านั้น ห้ามคิด ref เอง\n"
            "- action ต้องเป็น click, fill, press หรือ stop เท่านั้น\n"
            "- ตัดสินใจเพียง 1 การกระทำที่ใกล้เป้าหมายที่สุด\n"
            "- ถ้าไม่มี element ที่เหมาะสมให้ใช้ action=stop และ ref เป็นสตริงว่าง\n"
            "- ถ้าไม่ใช้ value ให้ใส่สตริงว่าง\n\n"
            'รูปแบบคำตอบ JSON: {"action": "...", "ref": "...", "value": "...", "reason": "..."}\n'
        )
        open(f"{D}/prompt.txt", "w", encoding="utf-8").write(prompt)
        r = subprocess.run(
            ["yolo1", "-p", "--model", "haiku", "--effort", "low", "--output-format", "json",
             "--json-schema", json.dumps(SCHEMA), "--no-session-persistence",
             "--strict-mcp-config", "--tools", ""],
            input=prompt, capture_output=True, text=True)
        if r.returncode != 0:
            print("yolo1 ล้มเหลว:", r.stderr[:300]); return 1
        ans = json.loads(r.stdout).get("structured_output")
        print("LLM:", ans)

        # 3. Validate
        print("== Validate ==")
        ans = ans or {}
        ref, action = ans.get("ref", ""), ans.get("action")
        el = els.get(ref)
        checks = {
            "action_in_allowlist": action in ALLOW,
            "ref_in_snapshot": el is not None,
            "name_not_denylisted": el is not None and not DENY.search(el[1]),
            "action_is_executable_click": action == "click",
            "has_box": bool(el and el[2]),
        }
        ok = all(checks.values())
        json.dump({"llm_answer": ans,
                   "element": {"role": el[0], "name": el[1], "box": el[2]} if el else None,
                   "checks": {k: "pass" if v else "fail" for k, v in checks.items()},
                   "result": "pass" if ok else "fail"},
                  open(f"{D}/decision.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print(checks)
        if not ok:
            print("Validate ไม่ผ่าน -> หยุดโดยไม่รันคำสั่ง"); return 2

        pw("eval", overlay_js(el[2], ref))
        pw("screenshot", "--hires", f"--filename={D}/page.png")
        pw("eval", REMOVE_JS)

        # 4. Act
        print("== Act ==")
        cmd = ["click", ref]
        ra = pw(*cmd)

        # 5. Verify
        print("== Verify ==")
        pw("snapshot", "--boxes", f"--filename={verify}")
        lines = open(verify, encoding="utf-8").read().splitlines()
        hit = [(i + 1, l.strip()) for i, l in enumerate(lines) if re.search(r'option\s+"One way"', l)]
        same = [(i + 1, l.strip()) for i, l in enumerate(lines) if f"[ref={ref}]" in l]
        passed = bool(hit)
        out = [f"คำสั่งที่รัน: playwright-cli {' '.join(cmd)}  (exit={ra.returncode})",
               f"output ย่อ: {ra.stdout.strip()[:400]}",
               f"ผล verify: {'PASS' if passed else 'FAIL'} — {'พบ' if passed else 'ไม่พบ'} option \"One way\" ใน verify.yml"]
        out += [f"  หลักฐาน verify.yml:{n}: {l}" for n, l in hit[:3]]
        out.append(f"ref เดิม {ref} ใน snapshot ใหม่: {'ยังอยู่' if same else 'ไม่อยู่แล้ว'}")
        out += [f"  verify.yml:{n}: {l}" for n, l in same[:3]]
        open(f"{D}/act.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
        print("\n".join(out))
        return 0 if passed else 3
    finally:
        pw("close")


if __name__ == "__main__":
    sys.exit(main())
