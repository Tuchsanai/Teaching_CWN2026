#!/usr/bin/env python3
"""Grader Validation: ตรวจ Grader ก่อนใช้โทเคน  ·  python3 check_grader.py

1. รัน Grader กับเฉลยอ้างอิง (ref/)                 -> ต้องผ่านครบทุกข้อของงานนั้น (10 หรือ 11 ข้อ)
2. รัน Grader กับเฉลยที่จงใจใส่ความผิด 1 จุด          -> ต้องไม่ผ่านเฉพาะข้อนั้น ข้ออื่นผ่าน
   ความผิดบางแบบใช้ได้เฉพาะบางงาน (เช่น ข้ามนโยบายธุรกิจ) งานอื่นแสดง "–"
exit 0 = Grader ใช้ได้ · exit 1 = ต้องแก้ Grader ก่อน
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from grade import TASKS  # noqa: E402

ALL = None
MUTANTS = [  # (ชื่อ, ข้อที่ต้องไม่ผ่าน, ข้อความเดิม, ข้อความที่ผิด, งานที่ใช้ได้)
    ("ปัดแบบ round() ของ Python (Banker's Rounding)", "half_up",
     "return int((Fraction(x) * 2 + 1) // 2)", "return round(float(Fraction(x)))",
     [t for t in TASKS if "half_up" in TASKS[t]]),
    ("ยอมรับ True เป็นจำนวนเต็ม", "reject_type",
     "if type(value) is not int:", "if not isinstance(value, int):", ALL),
    ("input ผิดแล้ว exit 1 แทน exit 2", "cli_error",
     "        return 2", "        return 1", ALL),
    ("ข้าม S1: คิดค่าส่งแม้ลูกค้ารับเอง", "policy",
     "    if distance_km == 0:", "    if False:", ["t3-shipping-fee"]),
    ("ข้าม S2: ส่งด่วนเกิน 20 กก. ได้", "policy",
     "    if express and weight_g > 20000:", "    if False:", ["t3-shipping-fee"]),
    ("ข้าม C1: silver ได้ 2 เท่าในเดือนเกิด", "policy",
     'if birthday and tier in ("gold", "platinum"):', "if birthday:", ["t4-cashback"]),
    ("ข้าม C2: ปัดครึ่งขึ้นแทนปัดลง", "policy",
     "return int(Fraction(x) // 1)", "return int((Fraction(x) * 2 + 1) // 2)", ["t4-cashback"]),
]


def n_checks(tid):
    """จำนวนข้อตรวจของงาน: 10 ข้อมาตรฐาน · ไม่มี half_up ลด 1 · มี policy เพิ่ม 1"""
    T = TASKS[tid]
    return 10 - ("half_up" not in T) + ("policy" in T)


def grade(sandbox, task):
    tf = os.path.join(os.path.dirname(sandbox), "task.json")
    json.dump(task, open(tf, "w", encoding="utf-8"), ensure_ascii=False)
    r = subprocess.run([sys.executable, os.path.join(HERE, "grade.py"), sandbox, tf], capture_output=True,
                       text=True, encoding="utf-8")
    return json.loads(r.stdout)


def main():
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    suite = json.load(open(os.path.join(HERE, "suite.json"), encoding="utf-8"))
    ok = True
    print("| Task | เฉลยอ้างอิง | " + " | ".join("ผิด: %s" % m[0] for m in MUTANTS) + " |")
    print("|---|---|" + "---|" * len(MUTANTS))
    for task in suite["tasks"]:
        ref = os.path.join(HERE, "ref", task["id"])
        row = [task["id"]]
        with tempfile.TemporaryDirectory() as tmp:
            sb = os.path.join(tmp, "sandbox")
            shutil.copytree(ref, sb)
            g = grade(sb, task)
            failed = [c["id"] for c in g["checks"] if not c["pass"]]
            n = n_checks(task["id"])
            good = not failed and len(g["checks"]) == n
            ok &= good
            row.append("✅ %d/%d" % (n, n) if good else "❌ ไม่ผ่าน " + (",".join(failed) or "จำนวนข้อตรวจไม่ใช่ %d" % n))
            src = open(os.path.join(ref, "solve.py"), encoding="utf-8").read()
            for name, target, old, new, only in MUTANTS:
                if only is not None and task["id"] not in only:
                    row.append("–")
                    continue
                assert old in src, "ไม่พบข้อความที่จะแก้ใน %s: %s" % (ref, old)
                shutil.rmtree(sb)
                shutil.copytree(ref, sb)
                open(os.path.join(sb, "solve.py"), "w", encoding="utf-8").write(src.replace(old, new))
                g = grade(sb, task)
                failed = [c["id"] for c in g["checks"] if not c["pass"]]
                good = failed == [target]
                ok &= good
                row.append(("✅ ไม่ผ่านเฉพาะ `%s`" % target) if good else "❌ ไม่ผ่าน " + (",".join(failed) or "(ไม่มี)"))
        print("| " + " | ".join(row) + " |")
    print("\nผล: %s" % ("Grader ใช้ได้ ✅" if ok else "Grader ยังไม่ถูกต้อง ❌ แก้ก่อนรัน Trial"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
