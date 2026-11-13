#!/usr/bin/env python3
"""Grader Validation: ตรวจ Grader ก่อนใช้โทเคน  ·  python3 check_grader.py

1. รัน Grader กับเฉลยอ้างอิง (ref/)                 -> ต้องผ่านครบ 10 ข้อ
2. รัน Grader กับเฉลยที่จงใจใส่ความผิด 1 จุด          -> ต้องไม่ผ่านเฉพาะข้อนั้น ข้ออื่นผ่าน
exit 0 = Grader ใช้ได้ · exit 1 = ต้องแก้ Grader ก่อน
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MUTANTS = [  # (ชื่อ, ข้อที่ต้องไม่ผ่าน, ข้อความเดิม, ข้อความที่ผิด)
    ("ปัดแบบ round() ของ Python (Banker's Rounding)", "half_up",
     "return int((Fraction(x) * 2 + 1) // 2)", "return round(float(Fraction(x)))"),
    ("ยอมรับ True เป็นจำนวนเต็ม", "reject_type",
     "if type(value) is not int:", "if not isinstance(value, int):"),
    ("input ผิดแล้ว exit 1 แทน exit 2", "cli_error",
     "        return 2", "        return 1"),
]


def grade(sandbox, task):
    tf = os.path.join(os.path.dirname(sandbox), "task.json")
    json.dump(task, open(tf, "w", encoding="utf-8"), ensure_ascii=False)
    r = subprocess.run([sys.executable, os.path.join(HERE, "benchmark_grader.py"), sandbox, tf], capture_output=True,
                       text=True, encoding="utf-8")
    return json.loads(r.stdout)


def main():
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8", errors="replace")
    tdir = os.path.join(HERE, "data", "baankafe", "tasks")
    suite = {"tasks": [json.load(open(os.path.join(tdir, f), encoding="utf-8")) for f in sorted(os.listdir(tdir))]}
    ok = True
    print("| Task | เฉลยอ้างอิง | " + " | ".join("ผิด: %s" % m[0] for m in MUTANTS) + " |")
    print("|---|---|" + "---|" * len(MUTANTS))
    for task in suite["tasks"]:
        ref = os.path.join(HERE, "data", "baankafe", "answers", task["id"])
        row = [task["id"]]
        with tempfile.TemporaryDirectory() as tmp:
            sb = os.path.join(tmp, "sandbox")
            shutil.copytree(ref, sb)
            g = grade(sb, task)
            failed = [c["id"] for c in g["checks"] if not c["pass"]]
            good = not failed and len(g["checks"]) == 10
            ok &= good
            row.append("✅ 10/10" if good else "❌ ไม่ผ่าน " + ",".join(failed))
            src = open(os.path.join(ref, "solve.py"), encoding="utf-8").read()
            for name, target, old, new in MUTANTS:
                assert old in src, "ไม่พบข้อความที่จะแก้ใน %s" % ref
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
