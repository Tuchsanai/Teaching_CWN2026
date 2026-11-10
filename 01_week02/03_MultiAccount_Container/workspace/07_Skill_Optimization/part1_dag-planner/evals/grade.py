#!/usr/bin/env python3
"""grade.py <sandbox> <task.json> : ตรวจแผนที่เอเจนต์สร้างด้วยสกิล dag-planner (ไม่ใช้โทเคน)

ไม่เชื่อคำตอบของเอเจนต์: อ่าน blocks.json ที่ได้ แล้วให้สคริปต์ dag-planner รุ่นอ้างอิง (v0 = สกิลจากบท 05)
วางแผนซ้ำด้วยเงื่อนไขของโจทย์ (จำนวน agent สูงสุด + บัญชีที่มี) ทุกข้อตรวจได้ผ่าน/ไม่ผ่าน คะแนน = สัดส่วนข้อที่ผ่าน
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.normpath(os.path.join(HERE, "../../../05_DAG_Planner/base_skills"))          # agent-team · yolo · cyolo
REF_DAG = os.path.normpath(os.path.join(HERE, "../versions/v0/scripts/dagplan.py"))   # dag-planner รุ่นอ้างอิง (v0)
NEED = {"yolo": 1, "cyolo": 1, "image": 1, "review": 2, "debate": 3}
SIZE = {"S": 0.6, "M": 1.5, "L": 3.0}


def main(sb, task):
    C = []

    def chk(i, ok, note=""):
        C.append({"id": i, "pass": bool(ok), "note": note})
    pdir = os.path.join(sb, "plans", task["id"])
    have = set(os.listdir(pdir)) if os.path.isdir(pdir) else set()
    miss = [f for f in ("blocks.json", "PLAN.md", "plan.json") if f not in have]
    miss += [n for n in ("dag", "gantt-plan") if not ({n + ".png", n + ".svg"} & have)]
    chk("files", not miss, "ขาด " + ", ".join(miss) if miss else "")
    try:
        doc = json.load(open(os.path.join(pdir, "blocks.json"), encoding="utf-8"))
        B = doc["blocks"]
        assert isinstance(B, list) and B
    except Exception as e:
        for i in ("dag_valid", "block_count", "structure", "output_done", "constraints", "all_scheduled", "selective", "parallel") + (("image_data",) if task.get("content_images") else ()):
            chk(i, False, "อ่าน blocks.json ไม่ได้: %s" % str(e)[:80])
        return C
    env = dict(os.environ, DAGPLAN_BASE_SKILLS=REF)
    D = REF_DAG
    with tempfile.TemporaryDirectory() as td:
        env["DAGPLAN_DIR"] = td
        r = subprocess.run([sys.executable, D, "dag", "g", "--blocks", os.path.join(pdir, "blocks.json")],
                           capture_output=True, text=True, env=env)
        ok_dag = r.returncode == 0 and "ERROR" not in r.stdout
        chk("dag_valid", ok_dag, "" if ok_dag else (r.stdout + r.stderr)[-200:])
        plan = None
        if ok_dag:
            subprocess.run([sys.executable, D, "plan", "g", "--max-agents", str(task["max_agents"]),
                            "--accounts", task["accounts"]], capture_output=True, text=True, env=env)
            try:
                plan = json.load(open(os.path.join(td, "g", "plan.json"), encoding="utf-8"))
            except Exception:
                plan = None
    ids = [b.get("id") for b in B]
    by = {b.get("id"): b for b in B}
    chk("block_count", 8 <= len(B) <= 12, "%d บล็อก (โจทย์ขอ 8–12)" % len(B))
    # โครง: มีบล็อกเริ่มที่ไม่รอใคร · ปลายทางเดียว เป็น exclusive · ทุกบล็อกไปถึงปลายทาง
    deps = {i: set(by[i].get("depends_on") or []) for i in ids}
    waited = set().union(*deps.values()) if deps else set()
    sinks = [i for i in ids if i not in waited]
    roots = [i for i in ids if not deps[i]]
    ok = bool(roots) and len(sinks) == 1 and bool(by[sinks[0]].get("exclusive"))
    if ok:
        anc, stack = set(), [sinks[0]]
        while stack:
            x = stack.pop()
            for d in deps.get(x, ()):
                if d not in anc:
                    anc.add(d)
                    stack.append(d)
        ok = anc | {sinks[0]} == set(ids)
    chk("structure", ok, "roots=%s sinks=%s exclusive=%s" % (roots, sinks, [by[s].get("exclusive") for s in sinks]))
    outs = [b.get("output") for b in B]
    ok = all(outs) and len(set(outs)) == len(outs) and all((b.get("done") or "").strip() for b in B)
    chk("output_done", ok, "" if ok else "output ว่าง/ซ้ำ หรือไม่มี done")
    # เงื่อนไขของโจทย์: แผนของเอเจนต์ใช้จำนวน agent และบัญชีตามที่สั่ง
    want = sorted(x.split(":")[0] for x in task["accounts"].split(","))
    try:
        mine = json.load(open(os.path.join(pdir, "plan.json"), encoding="utf-8"))
        got = sorted(x["account"] for x in mine.get("accounts", []))
        ok = mine.get("max_agents") == task["max_agents"] and got == want
        note = "max_agents=%s บัญชี=%s" % (mine.get("max_agents"), ",".join(got))
    except Exception as e:
        ok, note = False, "ไม่มี plan.json ของเอเจนต์"
    chk("constraints", ok, note)
    # ทุกบล็อกมีบัญชีรับจริง (วางแผนซ้ำด้วยตัวอ้างอิง)
    if plan:
        bad = sorted(i for i in ids if (plan["assign"].get(i) or {}).get("status") != "planned")
        chk("all_scheduled", not bad, "ไม่มีบัญชีรับ/ถูกบล็อก: " + ", ".join(bad) if bad else "")
    else:
        chk("all_scheduled", False, "วางแผนซ้ำไม่ได้")
    multi = [b["id"] for b in B if b.get("skill") in ("review", "debate", "best_of")]
    chk("selective", len(multi) <= len(B) / 3.0, "บล็อกหลายบัญชี %d/%d (ควร ≤ 1/3)" % (len(multi), len(B)))
    # ขนานได้จริง: สายวิกฤตไม่เกิน 60% ของงานทั้งหมด
    try:
        cost = {i: SIZE[by[i]["size"]] for i in ids}
        memo = {}

        def rank(i):
            if i not in memo:
                succ = [j for j in ids if i in deps[j]]
                memo[i] = cost[i] + max([rank(j) for j in succ] or [0])
            return memo[i]
        crit, total = max(rank(i) for i in ids), sum(cost.values())
        chk("parallel", crit <= 0.6 * total, "สายวิกฤต %.1f / งานรวม %.1f = %.0f%%" % (crit, total, 100 * crit / total))
    except Exception as e:
        chk("parallel", False, "คำนวณไม่ได้: %s" % str(e)[:60])
    # ภาพของรายการ (สินค้า/เมนู) ต้องรอบล็อกข้อมูลที่กำหนดรายการนั้น (บทเรียนรูปไม่ตรงชื่อสินค้าของบท 05)
    # ตรวจเฉพาะโจทย์ที่ระบุ content_images · ผ่านเมื่อบล็อกภาพทุกบล็อกรอบล็อกอื่นที่ไม่ใช่บล็อกโครงโปรเจกต์ (บล็อกแรก)
    if task.get("content_images"):
        first = ids[0]
        # โลโก้ ไอคอน และแบนเนอร์ ไม่ใช่ภาพของรายการ จึงไม่ต้องรอบล็อกข้อมูล (ตัวตรวจรุ่นแรกนับรวมจนตัดสินผิด ดู ISSUES.md ข้อ 2)
        generic = ("โลโก้", "logo", "ไอคอน", "icon", "แบนเนอร์", "banner", "favicon")
        bad = [b["id"] for b in B if b.get("skill") == "image"
               and not any(w in (str(b.get("title")) + " " + str(b.get("output"))).lower() for w in generic)
               and not (set(b.get("depends_on") or []) - {first})]
        chk("image_data", not bad, "บล็อกภาพที่ไม่รอบล็อกข้อมูล: " + ", ".join(bad) if bad else "")
    return C


if __name__ == "__main__":
    task = json.load(open(sys.argv[2], encoding="utf-8"))
    C = main(sys.argv[1], task)
    print(json.dumps({"score": round(sum(c["pass"] for c in C) / len(C), 4), "checks": C}, ensure_ascii=False))
