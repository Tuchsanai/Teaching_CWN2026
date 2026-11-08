#!/usr/bin/env python3
"""dagplan.py — แตกโจทย์เป็นบล็อกงาน (แต่ละบล็อกใช้สกิลบท 04) → DAG → แผน KC-QUEST + Gantt → รันจริงด้วย agent-team → รายงานแผน vs จริง

  dagplan.py doctor                                   ตรวจ python · สกิล agent-team/yolo/cyolo · ตัววาด PNG · บัญชีพร้อม
  dagplan.py dag    NAME [--blocks FILE|-]            ตรวจไฟล์บล็อก → rank · สายวิกฤต → dag.svg/png
  dagplan.py plan   NAME [--max-agents 6] [--accounts yolo1,cyolo1:40]
                                                      โควตาจริง (team.py check/quota) หรือค่าสมมติ → KC-QUEST
                                                      → gantt-plan.svg/png · dag.svg/png (มีป้ายบัญชี) · PLAN.md · plan.json
  dagplan.py export NAME                              → graph.json ของ agent-team (ตรวจกับ graph.md + add_node จริง)
  dagplan.py run    NAME [--detach]                   team.py run graph.json · เก็บ run_id ใน run.json
  dagplan.py report NAME [--run RUN_ID]               state.json + ledger → gantt-actual · compare · REPORT.md · calib.json

แผนอยู่ที่ /workspace/plans/<NAME>/ (blocks.json · ภาพ · รายงาน) · ไฟล์งานของทีมอยู่ที่ /workspace/plans/<NAME>/app/
Python 3.8+ ไลบรารีมาตรฐานเท่านั้น · เรียกภายนอกเฉพาะ team.py ของสกิล agent-team ข้างเคียง
"""
import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import kcquest as K  # noqa: E402
import render as R  # noqa: E402

SKILLS_DIR = os.path.dirname(os.path.dirname(HERE))
TEAM = next((p for p in (os.path.join(SKILLS_DIR, "agent-team", "scripts", "team.py"),
                         "/root/ai-accounts/.Claude/shared/skills/agent-team/scripts/team.py") if os.path.isfile(p)),
            os.path.join(SKILLS_DIR, "agent-team", "scripts", "team.py"))
GRAPH_MD = os.path.join(os.path.dirname(os.path.dirname(TEAM)), "references", "graph.md")
PLANS = os.environ.get("DAGPLAN_DIR") or "/workspace/plans"
TEAM_DIR = os.environ.get("MA_TEAM_DIR") or "/workspace/.agent-team"
ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
ROLE_TH = {"worker": "ทำ", "reviewer": "ตรวจ", "candidate": "ตอบ", "judge": "ตัดสิน"}


# ---------------------------------------------------------------- utils
def jload(p, default=None):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def jsave(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(p + ".tmp", p)


def wtext(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def pdir(name, *a):
    if not ID_RE.match(name or ""):
        sys.exit(f"ERROR ชื่อแผนต้องเป็น [A-Za-z0-9_.-]: {name!r}")
    return os.path.join(PLANS, name, *a)


def team(*args, timeout=600, capture=True):
    if not os.path.isfile(TEAM):
        sys.exit(f"ERROR ไม่พบ team.py ของสกิล agent-team ({TEAM}) — ติดตั้ง agent-team ใน shared/skills เดียวกัน")
    return subprocess.run([sys.executable, TEAM, *args], capture_output=capture, text=True, timeout=timeout)


def save_img(svg_text, path_svg):
    wtext(path_svg, svg_text)
    png = R.to_png(path_svg)
    return png or path_svg, bool(png)


# ---------------------------------------------------------------- blocks
def load_blocks(name, src=None):
    path = pdir(name, "blocks.json")
    if src:
        raw = sys.stdin.read() if src == "-" else open(src, encoding="utf-8").read()
        try:
            json.loads(raw)
        except ValueError as e:
            sys.exit(f"ERROR blocks ไม่ใช่ JSON: {e}")
        os.makedirs(pdir(name), exist_ok=True)
        wtext(path, raw)
    doc = jload(path)
    if doc is None:
        sys.exit(f"ERROR ไม่พบหรืออ่านไม่ได้: {path} (ส่งเข้ามาด้วย --blocks FILE หรือ --blocks - < blocks.json)")
    return doc


def validate(doc):
    """→ (errors, warnings) · errors = id ซ้ำ · อ้าง id ไม่มี · วงวน · skill ไม่รู้จัก · ฟิลด์ผิด"""
    errs, warns = [], []
    blocks = doc.get("blocks") if isinstance(doc, dict) else None
    if not isinstance(blocks, list) or not blocks:
        return ["ไม่มี blocks (ต้องเป็น {\"goal\", \"name\", \"blocks\": [...]})"], warns
    if not str(doc.get("goal") or "").strip():
        errs.append("ไม่มี goal (โจทย์รวม)")
    ids = [str(b.get("id")) for b in blocks]
    seen = set()
    for i in ids:
        if i in seen:
            errs.append(f"id ซ้ำ: {i}")
        seen.add(i)
    for b in blocks:
        i = b.get("id")
        if not ID_RE.match(str(i or "")):
            errs.append(f"{i!r}: id ต้องเป็น [A-Za-z0-9_.-]")
        if not str(b.get("title") or "").strip():
            errs.append(f"{i}: ไม่มี title")
        if b.get("size") not in ("S", "M", "L"):
            errs.append(f"{i}: size {b.get('size')!r} ต้องเป็น S/M/L (ใหญ่กว่า L ต้องแบ่งบล็อก)")
        if b.get("skill") not in K.SKILLS:
            errs.append(f"{i}: skill ไม่รู้จัก {b.get('skill')!r} (ใช้ได้: {', '.join(K.SKILLS)})")
        d = b.get("difficulty", 2)
        if not isinstance(d, int) or not 1 <= d <= 6:
            errs.append(f"{i}: difficulty ต้องเป็นจำนวนเต็ม 1–6")
        out = str(b.get("output") or "")
        if not out or out.startswith("/") or ".." in out.split("/"):
            errs.append(f"{i}: output ต้องเป็น path ภายใน app/ (ไม่ขึ้นต้น / ไม่มี ..)")
        if b.get("skill") == "image" and not out.lower().endswith(".png"):
            errs.append(f"{i}: บล็อก image ต้องมี output เป็น .png")
        if not str(b.get("done") or "").strip():
            errs.append(f"{i}: ไม่มีเกณฑ์ done")
        if b.get("skill") == "best_of" and not 2 <= int(b.get("n") or 2) <= 4:
            errs.append(f"{i}: best_of ต้องมี n 2–4")
        if b.get("worker") not in (None, "yolo", "cyolo"):
            errs.append(f"{i}: worker ต้องเป็น yolo หรือ cyolo")
        deps = b.get("depends_on", [])
        if not isinstance(deps, list):
            errs.append(f"{i}: depends_on ต้องเป็น list")
            continue
        for dd in deps:
            if dd == i:
                errs.append(f"{i}: depends_on อ้างตัวเอง")
            elif dd not in ids:
                errs.append(f"{i}: depends_on อ้าง id ที่ไม่มีจริง {dd!r}")
    # วงวน: DFS หาเส้นทางวน
    by = {}
    for b in blocks:                      # id ซ้ำ: ใช้ตัวแรกหาวง (ตัวซ้ำรายงานแยกแล้ว)
        by.setdefault(b.get("id"), b)
    st, stack, cycles = {}, [], []

    def dfs(i):
        st[i] = 1
        stack.append(i)
        for d in by[i].get("depends_on", []) if isinstance(by[i].get("depends_on", []), list) else []:
            if d not in by or d == i:
                continue
            if st.get(d) == 1:
                cyc = stack[stack.index(d):] + [d]
                cycles.append(" → ".join(reversed(cyc)))
            elif not st.get(d):
                dfs(d)
        stack.pop()
        st[i] = 2
    for i in by:
        if not st.get(i):
            dfs(i)
    errs += [f"วงวน (dependency cycle): {c}" for c in cycles]
    if not errs:
        if not 6 <= len(blocks) <= 14:
            warns.append(f"มี {len(blocks)} บล็อก (กติกาแนะนำ 6–14 บล็อกสำหรับโจทย์จริง)")
        if blocks[0].get("depends_on"):
            warns.append("บล็อกแรกควรเป็นโครงโปรเจกต์ (ไม่มี depends_on)")
        if not blocks[-1].get("exclusive"):
            warns.append("บล็อกสุดท้ายควรเป็นรวม + ทดสอบ และ exclusive: true")
        multi = [b["id"] for b in blocks if b["skill"] in ("review", "debate", "best_of")]
        if len(multi) > max(3, len(blocks) // 3):
            warns.append(f"ใช้ review/debate/best_of {len(multi)} บล็อก ({', '.join(multi)}) — กินหลายบัญชี ใช้เฉพาะที่จำเป็น")
        outs = [b["output"] for b in blocks]
        dup = sorted({o for o in outs if outs.count(o) > 1})
        if dup:
            warns.append(f"output ซ้ำกันหลายบล็อก: {', '.join(dup)} (แต่ละบล็อกควรมีไฟล์ผลของตัวเอง)")
    return errs, warns


def analyse(doc):
    blocks = doc["blocks"]
    for b in blocks:
        b.setdefault("depends_on", [])
        b.setdefault("difficulty", 2)
    cost = {b["id"]: K.CFG["size_mtok"][b["size"]] for b in blocks}
    rank, succ, calc = K.ranks(blocks, cost)
    crit = K.critical_path(blocks, rank, succ)
    return blocks, cost, rank, succ, calc, crit


def checked(name, src):
    doc = load_blocks(name, src)
    errs, warns = validate(doc)
    if errs:
        print(f"ERROR ไฟล์บล็อกของแผน {name} มีข้อผิดพลาด {len(errs)} ข้อ:")
        for e in errs:
            print(f"  ✗ {e}")
        sys.exit(1)
    for w in warns:
        print(f"  ⚠ {w}")
    return doc


# ---------------------------------------------------------------- doctor
def cmd_doctor(a):
    ok, rows = True, []

    def row(good, what, fix=""):
        nonlocal ok
        ok &= good is not False
        rows.append(("✅" if good else ("⚠️" if good is None else "❌")) + f" {what}" + (f"\n     → {fix}" if fix and not good else ""))
    row(sys.version_info >= (3, 8), f"Python {sys.version.split()[0]}", "ต้องใช้ Python 3.8+")
    for sk, f in (("agent-team", TEAM), ("yolo", os.path.join(SKILLS_DIR, "yolo", "scripts", "yolo.py")),
                  ("cyolo", os.path.join(SKILLS_DIR, "cyolo", "scripts", "cyolo.py"))):
        row(os.path.isfile(f), f"สกิล {sk}: {f}", f"ติดตั้งสกิล {sk} ใน {SKILLS_DIR}")
    row(os.path.isfile(GRAPH_MD), f"agent-team references/graph.md (ใช้ตรวจ export)")
    try:
        os.makedirs(PLANS, exist_ok=True)
        wtext(os.path.join(PLANS, ".doctor"), "ok")
        os.remove(os.path.join(PLANS, ".doctor"))
        row(True, f"โฟลเดอร์แผน {PLANS} เขียนได้")
    except OSError as e:
        row(False, f"โฟลเดอร์แผน {PLANS} เขียนไม่ได้ ({e})", "ตั้ง DAGPLAN_DIR หรือแก้สิทธิ์")
    chrome = R.find_chrome()
    png = None
    if chrome:
        t = os.path.join(PLANS, ".doctor.svg")
        wtext(t, '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="30"><text y="20">ทดสอบ ภาษาไทย</text></svg>')
        png = R.to_png(t)
        for f in (t, t[:-4] + ".png"):
            if os.path.exists(f):
                os.remove(f)
    row(bool(png) or None, f"ตัววาด PNG: {chrome or 'ไม่พบ headless Chromium'}" + ("" if png else " → ใช้ SVG แทน"),
        "ติดตั้ง Playwright Chromium หรือตั้ง DAGPLAN_CHROME")
    ready = []
    if os.path.isfile(TEAM):
        r = team("check", timeout=300)
        rd = jload(os.path.join(TEAM_DIR, "readiness.json"), {}) or {}
        ready = sorted([k for k, v in rd.items() if v.get("state") == "ready"], key=lambda x: (K.kind_of(x), x))
        row(r.returncode == 0 and bool(ready) or (None if r.returncode == 0 else False),
            "บัญชีพร้อม (team.py check): " + (", ".join(ready) or "ไม่มี"),
            "ให้ผู้ใช้ล็อกอินเอง (! yoloN auth login / ! cyoloN login) — สกิลนี้ไม่ล็อกอินแทน")
        print(r.stdout.strip())
        kinds = {K.kind_of(x) for x in ready}
        if ready and kinds != {"yolo", "cyolo"}:
            rows.append("⚠️ มีบัญชีพร้อมแค่ฝั่งเดียว → บล็อก review/debate/image (หรือ yolo) จะไม่มีใครรับ")
    plans = sorted(d for d in os.listdir(PLANS) if os.path.isfile(os.path.join(PLANS, d, "blocks.json"))) if os.path.isdir(PLANS) else []
    rows.append(f"📁 แผนใน {PLANS}: {', '.join(plans) or 'ยังไม่มี'}")
    print("dag-planner doctor\n" + "\n".join(rows))
    print("\nพร้อมใช้ ✅" if ok else "\nยังไม่พร้อม ❌ แก้ตามลูกศรด้านบน")
    return 0 if ok else 1


# ---------------------------------------------------------------- dag
def cmd_dag(a):
    doc = checked(a.name, a.blocks)
    blocks, cost, rank, succ, calc, crit = analyse(doc)
    title = f"DAG · {doc.get('name') or a.name} · {len(blocks)} บล็อก"
    img, png = save_img(R.render_dag(blocks, cost, rank, crit, title), pdir(a.name, "dag.svg"))
    jsave(pdir(a.name, "dag.json"), {"critical_path": crit, "rank": rank, "calc": calc,
                                    "skills": {b["id"]: b["skill"] for b in blocks}})
    print(f"OK {len(blocks)} บล็อก · สายวิกฤต {' → '.join(crit)} · ยาว {rank[crit[0]]:g}M tok")
    for b in sorted(blocks, key=lambda b: -rank[b["id"]]):
        print(f"  {b['id']:<6} {b['skill']:<8} rank {rank[b['id']]:<6g} {calc[b['id']]}")
    print(f"ภาพ: {img}" + ("" if png else "  (ไม่มี Chromium → SVG)"))
    return 0


# ---------------------------------------------------------------- plan
def parse_accounts(s):
    only, left = [], {}
    for x in (x.strip() for x in (s or "").replace(" ", ",").split(",")):
        if not x:
            continue
        n, _, pct = x.partition(":")
        if not re.match(r"^c?yolo[1-9][0-9]*$", n):
            sys.exit(f"ERROR ชื่อบัญชีไม่ถูกต้อง {n!r}")
        only.append(n)
        if pct:
            left[n] = max(0, min(100, int(float(pct.rstrip("%")))))
    return only, left


def real_snaps(only, left):
    """บัญชีที่ team.py check บอกว่าพร้อม + โควตาจาก team.py quota (แคชของ agent-team)"""
    r = team("check", *only, timeout=300)
    if r.returncode != 0:
        print("WARN team.py check ล้ม: " + (r.stderr or r.stdout).strip()[-300:])
    rd = jload(os.path.join(TEAM_DIR, "readiness.json"), {}) or {}
    ready = [x for x, v in rd.items() if v.get("state") == "ready" and (not only or x in only)]
    if ready:
        team("quota", *ready, timeout=300)
    qc = jload(os.path.join(TEAM_DIR, "quota.json"), {}) or {}
    snaps, notes = [], []
    for acc in sorted(set(ready) | set(left), key=lambda x: (K.kind_of(x), int(re.sub(r"\D", "", x)))):
        hint = str((rd.get(acc) or {}).get("detail") or "").split(" ")[0] if K.kind_of(acc) == "yolo" else None
        if acc in left:
            plan = (qc.get(acc) or {}).get("plan") or (hint if hint in ("max", "team", "pro") else "default")
            snaps.append(K.assumed(acc, left[acc], plan))
            if acc not in ready:
                notes.append(f"{acc} ไม่พร้อมตาม team.py check → ใช้ได้แค่ในแผนสมมติ (รันจริงไม่ได้)")
        else:
            snaps.append(K.snap_from_team(acc, qc.get(acc), hint if hint in ("max", "team", "pro") else None))
    skipped = [x for x in only if x not in ready and x not in left]
    if skipped:
        notes.append("ข้ามบัญชีที่ไม่พร้อม: " + ", ".join(f"{x} ({(rd.get(x) or {}).get('state', 'ไม่รู้จัก')})" for x in skipped))
    return K.score_accounts(snaps), notes


def fmt_quota(snaps):
    rows = ["| บัญชี | แพลน | ใช้ไป 5 ชม. | ใช้ไปสัปดาห์ | headroom | รีเซ็ต/หมดอายุ (ชม.) | U | slot | ที่มา |",
            "|---|---|---|---|---|---|---|---|---|"]
    for q in snaps:
        rows.append(f"| {q['account']} | {q.get('plan')} | {q.get('session_used'):g}% | "
                    f"{max(q.get('week_used') or 0, q.get('week_model_used') or 0):g}% | **{q['headroom']:g}%** | "
                    f"{q['hours_left']} | {q['use_first']} | {q['slots']} | {'สมมติ (--accounts)' if q.get('assumed') else 'team.py quota'} |")
    return "\n".join(rows)


def plan_bars(assign):
    bars = []
    for rec in assign.values():
        if rec.get("status") != "planned":
            continue
        for p in rec["accounts"]:
            bars.append({"block": rec["id"], "account": p["account"], "start": rec["start"] * 60, "end": rec["end"] * 60,
                         "role": p["role"], "skill": rec["skill"]})
    return bars


def acc_colors(accs):
    return {x: R.ACC_PALETTE[k % len(R.ACC_PALETTE)] for k, x in enumerate(accs)}


def cmd_plan(a):
    doc = checked(a.name, a.blocks)
    blocks, cost, rank, succ, calc, crit = analyse(doc)
    only, left = parse_accounts(a.accounts)
    snaps, notes = real_snaps(only, left)
    for n in notes:
        print(f"  ⚠ {n}")
    if not snaps:
        sys.exit("ERROR ไม่มีบัญชีที่พร้อม (team.py check) — ให้ผู้ใช้ล็อกอินเอง หรือทดลองด้วย --accounts yolo1:50,cyolo1:50")
    cfg = dict(K.CFG, max_agents=a.max_agents)
    cal = (jload(os.path.join(PLANS, "calib.json"), {}) or {}).get("k", {})
    assign, rounds, peak = K.simulate(blocks, snaps, cost, rank, cfg, cal)
    for b in blocks:                                 # บล็อกที่รอบล็อกที่ไม่มีใครรับ
        if b["id"] not in assign:
            assign[b["id"]] = {"id": b["id"], "skill": b["skill"], "accounts": [], "account": None, "status": "blocked",
                               "why": "รอบล็อกที่ไม่มีบัญชีรับ"}
    accs = [q["account"] for q in snaps]
    colors = acc_colors(accs)
    name = doc.get("name") or a.name
    dag_img, _ = save_img(R.render_dag(blocks, cost, rank, crit, f"DAG + บัญชีที่ได้งาน · {name} · MAX_AGENTS={a.max_agents}",
                                       assign, colors), pdir(a.name, "dag.svg"))
    span = max([r["end"] for r in assign.values() if r.get("status") == "planned"] + [0]) * 60
    g_img, png = save_img(R.render_gantt(plan_bars(assign), accs, crit, f"Gantt แผน · {name}",
                                         f"แถว = บัญชี · แท่ง = บล็อก (สีตามสกิล) · เวลา = โทเคนประเมิน ÷ ความเร็ว CLI × k"
                                         f" · KC-QUEST · MAX_AGENTS={a.max_agents}", {b["id"]: b["skill"] for b in blocks}),
                          pdir(a.name, "gantt-plan.svg"))
    by = {b["id"]: b for b in blocks}
    L = [f"# PLAN · {name}", "", f"**โจทย์:** {doc.get('goal')}", "",
         f"วางแผนเมื่อ {K.now().strftime('%d/%m/%Y %H:%M')} · MAX_AGENTS {a.max_agents} · บัญชี {', '.join(accs)}"
         f" · ตัวปรับเวลา k {json.dumps(cal, ensure_ascii=False) if cal else '(ยังไม่มี calib.json → k=1)'}", "",
         "> แผนนี้ยังไม่ได้รันจริง — KC-QUEST เลือกบัญชีจากโควตา แล้วจำลองเวลาตาม dependency", "",
         "## 1) โควตาของแต่ละบัญชี", "", fmt_quota(snaps), ""]
    L += [f"- ⚠ {n}" for n in notes]
    L += ["", "## 2) DAG + สกิล + บัญชี", "", f"![DAG]({os.path.basename(dag_img)})", "",
          f"**สายวิกฤต:** {' → '.join(crit)} · ยาว {rank[crit[0]]:g}M tok", "",
          "## 3) ตารางแจกงาน (เหตุผล KC-QUEST ทุกบล็อก)", "",
          "| บล็อก | สกิล | ชื่อ | ขนาด · c | รอ | rank | บัญชี (บทบาท) | เริ่ม–จบ (นาที) | เหตุผล KC-QUEST |",
          "|---|---|---|---|---|---|---|---|---|"]
    for b in sorted(blocks, key=lambda b: (assign[b["id"]].get("start", 1e9), -rank[b["id"]])):
        p, i = assign[b["id"]], b["id"]
        who = ", ".join(f"{x['account']} ({ROLE_TH[x['role']]})" for x in p.get("accounts", [])) or "❌"
        when = f"{p['start'] * 60:.1f}–{p['end'] * 60:.1f}" if p.get("status") == "planned" else p.get("status")
        why = " <br> ".join(f"{ROLE_TH[x['role']]}: {x['why']}" for x in p.get("accounts", [])) or p.get("why", "")
        L.append(f"| {'**' + i + '**' if i in crit else i} | {R.SKILL_STYLE[b['skill']][1]} {b['skill']} | {b['title']} | "
                 f"{b['size']} · {cost[i]:g} | {', '.join(b['depends_on']) or '–'} | {rank[i]:g} | {who} | {when} | {why} |")
    L += ["", "## 4) Gantt แผน", "", f"![Gantt]({os.path.basename(g_img)})", "",
          "## 5) รอบแจกงาน", "", "| นาทีที่ | บล็อกที่เริ่ม |", "|---|---|"]
    L += [f"| {r['t_min']:g} | " + ", ".join(f"{i}→{'+'.join(x['account'] for x in assign[i]['accounts'])}" for i in r["start"]) + " |"
          for r in rounds]
    bad = [i for i, p in assign.items() if p.get("status") != "planned"]
    L += ["", "## 6) สรุป", "", f"- บล็อก {len(blocks)} · แจกได้ {len(blocks) - len(bad)} · agent พร้อมกันสูงสุด {peak}/{a.max_agents}",
          f"- เวลาประมาณ {span:.1f} นาที (แท่ง Gantt) · ไฟล์ผลของทีม: `{pdir(a.name, 'app')}/`"]
    if bad:
        L.append(f"- ⚠ บล็อกที่ไม่มีบัญชีรับ: {', '.join(bad)} → แบ่งให้เล็กลง / เพิ่มบัญชี / ลด n")
    L += ["", f"ต่อไป: `dagplan.py export {a.name}` → `dagplan.py run {a.name}` → `dagplan.py report {a.name}`"]
    wtext(pdir(a.name, "PLAN.md"), "\n".join(L) + "\n")
    jsave(pdir(a.name, "plan.json"), {"name": a.name, "goal": doc.get("goal"), "created": K.iso(K.now()),
                                      "max_agents": a.max_agents, "accounts": snaps, "notes": notes, "calib_k": cal,
                                      "critical_path": crit, "rank": rank, "peak_agents": peak, "rounds": rounds,
                                      "assign": assign})
    print(f"OK แผน {a.name} · {len(blocks)} บล็อก · สายวิกฤต {' → '.join(crit)} · agent พร้อมกันสูงสุด {peak}/{a.max_agents} · ≈ {span:.1f} นาที")
    for b in blocks:
        p = assign[b["id"]]
        print(f"  {b['id']:<6} {b['skill']:<8} → {', '.join(x['account'] + '(' + ROLE_TH[x['role']] + ')' for x in p['accounts']) or '❌ ' + p['status']}"
              + (f"  {p['start'] * 60:.1f}–{p['end'] * 60:.1f} นาที" if p.get("status") == "planned" else ""))
    print(f"ผลลัพธ์: {pdir(a.name, 'PLAN.md')} · {dag_img} · {g_img}" + ("" if png else "  (ไม่มี Chromium → SVG)"))
    return 0 if not bad else 2


# ---------------------------------------------------------------- export
def graph_fields():
    """ชื่อฟิลด์ของ node ที่ agent-team รองรับ อ่านจาก references/graph.md จริง (ตาราง 'ฟิลด์ของ node')"""
    try:
        txt = open(GRAPH_MD, encoding="utf-8").read()
    except OSError:
        return None
    sec = txt.split("## ฟิลด์ของ node", 1)[-1].split("\n## ", 1)[0]
    names = set()
    for line in sec.splitlines():
        if line.startswith("|") and not line.startswith("|---"):
            names |= set(re.findall(r"`([a-z_]+)`", line.split("|")[1]))
            first = line.split("|")[1].strip()
            if first in ("review", "debate", "best_of"):         # แถวชนิด: ฟิลด์อยู่คอลัมน์ที่ 2 (ค่าในวงเล็บไม่ใช่ฟิลด์)
                names |= set(re.findall(r"`([a-z_]+)`", re.sub(r"\([^)]*\)", "", line.split("|")[2])))
    return names


def topo(blocks, assign):
    by, done, out = {b["id"]: b for b in blocks}, set(), []
    while len(out) < len(blocks):
        ready = [b for b in blocks if b["id"] not in done and all(d in done for d in b["depends_on"])]
        ready.sort(key=lambda b: ((assign.get(b["id"]) or {}).get("start", 1e9), b["id"]))
        out.append(ready[0])
        done.add(ready[0]["id"])
    return out


def node_prompt(doc, b, by, app, n_total):
    multi_answer = b["skill"] in ("debate", "best_of")
    lines = [f"เป้าหมายรวมของโปรเจกต์: {doc['goal']}",
             f"คุณรับผิดชอบบล็อก {b['id']} (1 ใน {n_total} บล็อก): {b['title']}"]
    if b.get("detail"):
        lines.append(f"รายละเอียดงาน: {b['detail']}")
    target = os.path.join(app, b["output"])
    if multi_answer:
        lines.append(f"ผลของบล็อกนี้คือเนื้อหาของไฟล์ {target} — ตอบเป็นเนื้อหาไฟล์ฉบับเต็มในคำตอบ ไม่ต้องเขียนไฟล์เอง "
                     f"(ระบบบันทึกคำตอบที่{'ถูก' if b['skill'] == 'debate' else 'ชนะ'}ลงไฟล์นี้ให้)")
    else:
        lines.append(f"ไฟล์ผลที่ต้องเขียน: {target} (โฟลเดอร์ทำงานร่วมของทีม = {app})")
    lines.append(f"เกณฑ์เสร็จ (ต้องตรวจได้): {b['done']}")
    deps = b["depends_on"]
    if deps:
        lines.append("ไฟล์ของบล็อกก่อนหน้าที่ต้องอ่านก่อนเริ่ม (อ่านเองจากไฟล์ ไม่ต้องให้ใครส่งเนื้อหามา):")
        for d in deps:
            db = by[d]
            path = "{{file:%s}}" % d if db["skill"] in ("debate", "best_of") else os.path.join(app, db["output"])
            lines.append(f"- {path} (ผลของ {d}: {db['title']})")
    if b.get("exclusive"):
        lines.append("บล็อกนี้เป็นบล็อกรวมระบบ/ทดสอบสุดท้าย (รันคนเดียว) แก้ไฟล์ของบล็อกอื่นได้เท่าที่จำเป็นเพื่อรวมและทดสอบ")
    else:
        lines.append(f"ห้ามแก้หรือลบไฟล์ของบล็อกอื่น เขียนเฉพาะ {b['output']}" if not multi_answer else
                     "ห้ามแก้หรือลบไฟล์ใด ๆ ใน app/")
    lines.append("ห้ามทำงานนอกโฟลเดอร์ app/ ของแผนนี้" if not multi_answer else "")
    lines.append("ตอบเนื้อหาไฟล์ฉบับเต็มเท่านั้น" if multi_answer else
                 "เมื่อเสร็จ ตอบสั้น ๆ 1–2 บรรทัดว่าเขียนไฟล์อะไร (path) และผ่านเกณฑ์เสร็จหรือไม่")
    return "\n".join(x for x in lines if x)


def build_graph(name, doc, plan):
    blocks, cost, rank, succ, calc, crit = analyse(doc)
    by = {b["id"]: b for b in blocks}
    assign = (plan or {}).get("assign") or {}
    app = pdir(name, "app")
    side = lambda acc, dflt: K.kind_of(acc) if acc else dflt   # noqa: E731
    nodes = []
    for b in topo(blocks, assign):
        picks = (assign.get(b["id"]) or {}).get("accounts") or []
        role = lambda r: [p["account"] for p in picks if p["role"] == r]   # noqa: E731
        n = {"id": b["id"], "depends_on": list(b["depends_on"]), "difficulty": int(b.get("difficulty", 2)),
             "cwd": app, "timeout": int(b.get("timeout") or 600), "expect": "text"}
        sk = b["skill"]
        if sk == "image":
            n.update(account="cyolo", image=os.path.join(app, b["output"]), kind="image",
                     prompt=f"{b['title']}. {b.get('detail') or ''} (ภาพสำหรับโปรเจกต์: {doc['goal']}) "
                            f"เงื่อนไขที่ต้องครบ: {b['done']}".replace("  ", " "))
            n.pop("expect")
        else:
            n["prompt"] = node_prompt(doc, b, by, app, len(blocks))
            if sk in ("yolo", "cyolo"):
                n["account"] = sk
            elif sk == "review":
                w = (role("worker") or [None])[0]
                n.update(type="review", account=side(w, b.get("worker") or "yolo"),
                         criteria=f"{b['done']} · ไฟล์ {os.path.join(app, b['output'])} มีอยู่จริงและตรงโจทย์ (เปิดไฟล์ตรวจเอง)",
                         max_rounds=int(b.get("max_rounds") or 2), review_difficulty=n["difficulty"])
                n["reviewer"] = "cyolo" if n["account"] == "yolo" else "yolo"
            elif sk == "debate":
                j = (role("judge") or [None])[0]
                n.update(type="debate", candidates=["yolo", "cyolo"], judge=side(j, "any"), judge_difficulty=n["difficulty"])
                n.pop("expect")
            elif sk == "best_of":
                c = role("candidate") or []
                k = int(b.get("n") or 2)
                n.update(type="best_of", candidates=[K.kind_of(x) for x in c] if len(c) == k else ["yolo", "cyolo"][:k] + ["any"] * max(0, k - 2),
                         judge=side((role("judge") or [None])[0], "any"), criteria=b["done"], judge_difficulty=n["difficulty"])
                n.pop("expect")
        nodes.append(n)
    return {"goal": doc["goal"], "defaults": {"difficulty": 1, "timeout": 600}, "nodes": nodes}


def verify_graph(g):
    """ตรวจ 2 ชั้น: ① ฟิลด์ตาม references/graph.md ② ให้ add_node() ของ team.py จริงรับทุก node (ไม่สร้าง run)"""
    errs = []
    fields = graph_fields()
    if fields is None:
        errs.append(f"อ่าน {GRAPH_MD} ไม่ได้")
    else:
        for n in g["nodes"]:
            extra = sorted(set(n) - fields)
            if extra:
                errs.append(f"{n['id']}: ฟิลด์ที่ graph.md ไม่รู้จัก {extra}")
    for n in g["nodes"]:
        if n.get("image") and not (n["image"].startswith("/") and n["image"].endswith(".png")):
            errs.append(f"{n['id']}: image ต้องเป็น absolute path .png")
        if n.get("cwd") and not n["cwd"].startswith("/"):
            errs.append(f"{n['id']}: cwd ต้องเป็น absolute path")
    code = ("import json,sys; sys.dont_write_bytecode=True; sys.path.insert(0, sys.argv[1]); import team; "
            "g=json.load(sys.stdin); st={'nodes':{},'order':[]}\n"
            "for n in g['nodes']:\n"
            "    n=dict(n); [n.setdefault(k,v) for k,v in g.get('defaults',{}).items()]; team.add_node(st,n)\n"
            "print('accepted', len(st['order']))")
    r = subprocess.run([sys.executable, "-c", code, os.path.dirname(TEAM)], input=json.dumps(g), capture_output=True,
                       text=True, timeout=60)
    if r.returncode != 0:
        errs.append("team.py add_node ไม่ยอมรับ: " + (r.stderr.strip().splitlines() or ["?"])[-1])
    return errs, r.stdout.strip()


def cmd_export(a):
    doc = checked(a.name, None)
    plan = jload(pdir(a.name, "plan.json"))
    if not plan:
        print("  ⚠ ยังไม่มี plan.json → ใช้ฝั่งตามสกิลของบล็อก (แนะนำ dagplan.py plan ก่อน)")
    g = build_graph(a.name, doc, plan)
    errs, ok = verify_graph(g)
    if errs:
        print("ERROR graph.json ไม่ผ่าน:")
        for e in errs:
            print(f"  ✗ {e}")
        return 1
    os.makedirs(pdir(a.name, "app"), exist_ok=True)
    jsave(pdir(a.name, "graph.json"), g)
    print(f"OK {pdir(a.name, 'graph.json')} · {len(g['nodes'])} node · ตรวจกับ graph.md + team.add_node: {ok}")
    for n in g["nodes"]:
        extra = n.get("reviewer") or n.get("candidates") or ""
        print(f"  {n['id']:<6} {n.get('type', 'task'):<8} account={n['account'] if 'account' in n else '-'} {extra or ''}"
              + (f" judge={n['judge']}" if n.get("judge") else "") + (f" image={n['image']}" if n.get("image") else ""))
    return 0


# ---------------------------------------------------------------- run
def cmd_run(a):
    gpath = pdir(a.name, "graph.json")
    if not os.path.isfile(gpath) or (os.path.isfile(pdir(a.name, "plan.json")) and
                                     os.path.getmtime(pdir(a.name, "plan.json")) > os.path.getmtime(gpath)):
        print("export ใหม่ (graph.json ไม่มีหรือเก่ากว่า plan.json)")
        if cmd_export(a):
            return 1
    plan = jload(pdir(a.name, "plan.json"), {}) or {}
    accs = [q["account"] for q in plan.get("accounts", []) if not q.get("assumed")]
    rid = f"{a.name}-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    os.makedirs(pdir(a.name, "app"), exist_ok=True)
    args = ["run", gpath, "--run", rid] + (["--accounts", ",".join(accs)] if accs else []) + (["--detach"] if a.detach else [])
    info = jload(pdir(a.name, "run.json"), {}) or {}
    info.setdefault("history", []).append({"run_id": rid, "started": K.iso(K.now()), "detach": a.detach, "accounts": accs})
    info["run_id"] = rid
    jsave(pdir(a.name, "run.json"), info)
    print(f"run_id {rid} (บันทึกใน {pdir(a.name, 'run.json')}) · บัญชี {', '.join(accs) or 'ทุกบัญชี'}", flush=True)
    r = team(*args, timeout=None, capture=False)
    print(f"\nต่อไป: dagplan.py report {a.name}" + ("  (รอให้ run จบก่อน: team.py status --run " + rid + ")" if a.detach else ""))
    return r.returncode


# ---------------------------------------------------------------- report
def ledger_rows(path):
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    except OSError:
        pass
    return out


def tokens_used(r):
    return int(r.get("input_tokens") or 0) + int(r.get("output_tokens") or 0)


def block_of(node_tag, ids):
    if node_tag in ids:
        return node_tag
    head = str(node_tag or "").rsplit(".", 1)[0]
    return head if head in ids else None


def cmd_report(a):
    doc = checked(a.name, None)
    blocks, cost, rank, succ, calc, crit = analyse(doc)
    ids = [b["id"] for b in blocks]
    by = {b["id"]: b for b in blocks}
    plan = jload(pdir(a.name, "plan.json"), {}) or {}
    assign = plan.get("assign") or {}
    rid = a.run or (jload(pdir(a.name, "run.json"), {}) or {}).get("run_id")
    if not rid:
        sys.exit("ERROR ยังไม่มี run (dagplan.py run ก่อน หรือระบุ --run RUN_ID)")
    rdir = os.path.join(TEAM_DIR, rid)
    st = jload(os.path.join(rdir, "state.json"))
    if not st:
        sys.exit(f"ERROR ไม่พบ {rdir}/state.json")
    nodes = st.get("nodes", {})
    rows = [r for r in ledger_rows(os.path.join(rdir, "ledger.jsonl")) if r.get("event") == "call"]
    calls = [r for r in rows if block_of(r.get("node"), ids)]
    probes = [r for r in rows if not block_of(r.get("node"), ids)]
    running = [i for i, n in nodes.items() if n.get("status") in ("running", "pending", "waiting_approval")]
    times = [K.parse_iso(r["ts_start"]) for r in calls if r.get("ts_start")] + \
            [K.parse_iso(n["started"]) for n in nodes.values() if n.get("started")]
    t0 = min(times) if times else K.parse_iso(st.get("created"))
    mins = lambda ts: (K.parse_iso(ts) - t0).total_seconds() / 60 if ts else None   # noqa: E731
    # แท่งจริง: (บล็อก, บัญชี, บทบาท) → ช่วง ts_start..ts_end ใน ledger
    seg = {}
    for r in calls:
        k = (block_of(r["node"], ids), r["account"], r.get("role") or "worker")
        s, e = mins(r.get("ts_start")), mins(r.get("ts_end") or r.get("ts_start"))
        cur = seg.get(k)
        seg[k] = (min(cur[0], s), max(cur[1], e)) if cur else (s, e)
    bars = [{"block": b, "account": acc, "start": s, "end": max(e, s + 0.05), "role": role, "skill": by[b]["skill"]}
            for (b, acc, role), (s, e) in seg.items()]
    order_acc = [x for x in st.get("accounts", {}) if any(br["account"] == x for br in bars)]
    order_acc += sorted({br["account"] for br in bars} - set(order_acc))
    name = doc.get("name") or a.name
    ga, png1 = save_img(R.render_gantt(bars, order_acc, crit, f"Gantt จริง · {name} · run {rid}",
                                       "แถว = บัญชีที่ทำจริง (จาก ledger) · แท่ง = ช่วงที่บัญชีนั้นเรียกโมเดลให้บล็อก · ขอบส้ม = สายวิกฤตตามแผน",
                                       {b["id"]: b["skill"] for b in blocks}), pdir(a.name, "gantt-actual.svg"))
    table, comp, by_skill = [], [], {}
    for b in blocks:
        i = b["id"]
        n = nodes.get(i, {})
        p = assign.get(i, {})
        rs = [r for r in calls if block_of(r["node"], ids) == i]
        tok = sum(tokens_used(r) for r in rs)
        a0, a1 = mins(n.get("started")), mins(n.get("ended"))
        if a0 is None and rs:
            a0 = min(mins(r["ts_start"]) for r in rs)
        if a1 is None and rs and n.get("status") in ("done", "failed"):
            a1 = max(mins(r.get("ts_end") or r["ts_start"]) for r in rs)
        p0 = p.get("start") * 60 if p.get("status") == "planned" else None
        p1 = p.get("end") * 60 if p.get("status") == "planned" else None
        acc_real = []
        for r in rs:
            lab = f"{r['account']}({ROLE_TH.get(r.get('role'), r.get('role'))})"
            if lab not in acc_real:
                acc_real.append(lab)
        out_file = os.path.join(pdir(a.name, "app"), b["output"])
        if n.get("status") == "done" and b["skill"] in ("debate", "best_of") and not os.path.exists(out_file):
            os.makedirs(os.path.dirname(out_file), exist_ok=True)          # คำตอบที่ชนะ/ที่ถูก → ไฟล์ผลของบล็อก (คัดลอกข้อความ ไม่รัน)
            wtext(out_file, str(n.get("value") or "") + "\n")
        exists = os.path.exists(out_file)
        table.append({"id": i, "skill": b["skill"], "plan_acc": ", ".join(f"{x['account']}({ROLE_TH[x['role']]})" for x in p.get("accounts", [])) or "-",
                      "real_acc": ", ".join(acc_real) or (n.get("assigned") or "-"), "p_min": (p1 - p0) if p0 is not None else None,
                      "a_min": (a1 - a0) if (a0 is not None and a1 is not None) else None, "tokens": tok, "calls": len(rs),
                      "in": sum(int(r.get("input_tokens") or 0) for r in rs), "out": sum(int(r.get("output_tokens") or 0) for r in rs),
                      "status": n.get("status", "ไม่อยู่ใน run"), "file": exists, "error": (n.get("error") or "")[:120],
                      "base_min": (p.get("dur_base_h") or 0) * 60})
        comp.append({"block": i, "skill": b["skill"], "p0": p0, "p1": p1, "a0": a0 if a1 is not None else None, "a1": a1,
                     "status": n.get("status")})
        if n.get("status") == "done" and table[-1]["a_min"] is not None and table[-1]["base_min"]:
            s = by_skill.setdefault(b["skill"], [0.0, 0.0])
            s[0] += table[-1]["a_min"]
            s[1] += table[-1]["base_min"]
    cp, png2 = save_img(R.render_compare(comp, f"แผน vs จริง · {name}", f"run {rid} · ซ้าย = แผน KC-QUEST · ขวา = ที่ agent-team รันจริง"),
                        pdir(a.name, "compare.svg"))
    # ⑥ เรียนรู้: k = เวลาจริง ÷ เวลาแผน (ก่อนคูณ k) แยกตามสกิล → /workspace/plans/calib.json
    cal_path = os.path.join(PLANS, "calib.json")
    cal = jload(cal_path, {}) or {}
    ks = dict(cal.get("k") or {})
    new = {sk: round(v[0] / v[1], 4) for sk, v in by_skill.items() if v[1] > 0}
    if new and not running:
        ks.update(new)
        tot = [sum(v[0] for v in by_skill.values()), sum(v[1] for v in by_skill.values())]
        ks["*"] = round(tot[0] / tot[1], 4)
        cal = {"updated": K.iso(K.now()), "k": ks, "history": (cal.get("history") or [])[-49:] +
               [{"plan": a.name, "run_id": rid, "at": K.iso(K.now()), "k": new,
                 "minutes": {sk: [round(v[0], 2), round(v[1], 2)] for sk, v in by_skill.items()}}]}
        jsave(cal_path, cal)
    tot_tok = sum(t["tokens"] for t in table)
    led_tok = sum(tokens_used(r) for r in calls)
    plan_span = max([c["p1"] for c in comp if c["p1"] is not None] + [0])
    real_span = max([c["a1"] for c in comp if c["a1"] is not None] + [0])
    L = [f"# REPORT · {name}", "", f"**run:** `{rid}` · `{rdir}` · โจทย์: {doc.get('goal')}", ""]
    if running:
        L += [f"> ⚠ run ยังไม่จบ ({', '.join(running)} ยังรัน/รอ) — รายงานนี้เป็นภาพชั่วคราว ยังไม่เขียน calib.json", ""]
    L += ["## ตารางบล็อก (แผน vs จริง)", "",
          "| บล็อก | สกิล | บัญชีแผน | บัญชีจริง | นาทีแผน | นาทีจริง | tokens (in+out) | ครั้ง | สถานะ | ไฟล์ผล |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for t in table:
        f = lambda v: "-" if v is None else f"{v:.2f}"   # noqa: E731
        L.append(f"| {'**' + t['id'] + '**' if t['id'] in crit else t['id']} | {R.SKILL_STYLE[t['skill']][1]} {t['skill']} | {t['plan_acc']} | "
                 f"{t['real_acc']} | {f(t['p_min'])} | {f(t['a_min'])} | {t['tokens']:,} ({t['in']:,}+{t['out']:,}) | {t['calls']} | "
                 f"{t['status']}{(' — ' + t['error']) if t['error'] and t['status'] != 'done' else ''} | {'✅' if t['file'] else '❌'} {by[t['id']]['output']} |")
    L += ["", f"- tokens รวมของบล็อก **{tot_tok:,}** = ผลรวมจาก ledger ของ run ({len(calls)} การเรียก) **{led_tok:,}**"
          + (" ✅ ตรงกัน" if tot_tok == led_tok else " ❌ ไม่ตรง"),
          f"- การเรียกที่ไม่ใช่บล็อก (ตรวจความพร้อม ฯลฯ): {len(probes)} ครั้ง · {sum(tokens_used(r) for r in probes):,} tokens (ไม่นับในตาราง)",
          f"- เวลารวม: แผน {plan_span:.1f} นาที · จริง {real_span:.1f} นาที",
          f"- บล็อกเสร็จ {sum(t['status'] == 'done' for t in table)}/{len(table)}", "",
          "## ภาพ", "", f"![Gantt จริง]({os.path.basename(ga)})", "", f"![แผน vs จริง]({os.path.basename(cp)})", "",
          "## ความต่างระหว่างแผนกับของจริง", ""]
    diff = [t for t in table if t["plan_acc"] != "-" and
            {x.split("(")[0] for x in t["plan_acc"].split(", ")} != {x.split("(")[0] for x in t["real_acc"].split(", ")}]
    L += [f"- {t['id']}: แผน {t['plan_acc']} → จริง {t['real_acc']}" for t in diff] or ["- บัญชีจริงตรงกับแผนทุกบล็อก"]
    L.append("- (export ส่งเป็นฝั่ง yolo/cyolo ไม่ผูกบัญชี เพื่อให้ failover ของ agent-team ทำงาน → agent-team เลือกบัญชีในฝั่งเองตามโหลด/โควตา ดู references/run.md)")
    for e in st.get("events") or []:
        L.append(f"- event {e.get('event')}: {e.get('text')}")
    L += ["", "## ตัวปรับเวลา k (calib.json)", "",
          f"`{cal_path}`: " + (json.dumps(new, ensure_ascii=False) if new and not running else "ไม่อัปเดต (ไม่มีบล็อกที่เสร็จ หรือ run ยังไม่จบ)"),
          "", "k = นาทีจริง ÷ นาทีแผน (ก่อนคูณ k) แยกตามสกิล · `plan` ครั้งถัดไปคูณเวลาแต่ละบล็อกด้วย k ของสกิลนั้น"]
    wtext(pdir(a.name, "REPORT.md"), "\n".join(L) + "\n")
    print(f"OK REPORT {pdir(a.name, 'REPORT.md')} · {ga} · {cp}" + ("" if png1 and png2 else "  (ไม่มี Chromium → SVG)"))
    print(f"  tokens บล็อก {tot_tok:,} · ledger {led_tok:,} · เสร็จ {sum(t['status'] == 'done' for t in table)}/{len(table)}"
          + (f" · k ใหม่ {new}" if new and not running else ""))
    return 0 if not running else 3


# ---------------------------------------------------------------- main
def main():
    for f in (sys.stdout, sys.stderr):
        try:
            f.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("doctor")
    for c in ("dag", "plan", "export", "run", "report"):
        p = sub.add_parser(c)
        p.add_argument("name")
        if c in ("dag", "plan"):
            p.add_argument("--blocks", help="ไฟล์ blocks.json (หรือ - = stdin) → คัดลอกเป็น <แผน>/blocks.json")
        if c == "plan":
            p.add_argument("--max-agents", type=int, default=6)
            p.add_argument("--accounts", default="", help="yolo1,cyolo1:40 (:40 = สมมติเหลือ 40%%)")
        if c == "run":
            p.add_argument("--detach", action="store_true")
        if c == "report":
            p.add_argument("--run")
    a = ap.parse_args()
    if not a.cmd:
        print(__doc__)
        return 0
    if not hasattr(a, "blocks"):
        a.blocks = None
    return {"doctor": cmd_doctor, "dag": cmd_dag, "plan": cmd_plan, "export": cmd_export, "run": cmd_run,
            "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
