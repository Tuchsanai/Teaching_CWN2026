"""ตรวจ solve.py ก่อนส่ง:  python3 ./skills/baankafe-solve/check_solve.py solve.py <ชื่อฟังก์ชัน> '<JSON อาร์กิวเมนต์ตัวอย่างที่ถูกต้อง>'
เช่น python3 ./skills/baankafe-solve/check_solve.py solve.py cashback '{"amount":10000,"tier":"gold","birthday":true}'
ตรวจ: (1) import ได้ ไม่มี side effect (2) มีฟังก์ชันชื่อนั้น (3) รันผ่าน CLI (stdin JSON) แล้วได้ {"ok": true, ...}
(4) ไม่มี my_function/NotImplementedError ค้างในไฟล์ (5) input เป็น object ว่างแล้วไม่ crash"""
import importlib.util, subprocess, sys

path, fn, sample = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(path, encoding="utf-8").read()
bad = False
for w in ("my_function", "NotImplementedError"):
    if w in src:
        print("FAIL: ยังมี", w, "ค้างอยู่ใน", path); bad = True
spec = importlib.util.spec_from_file_location("solve_mod", path)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
if not callable(getattr(m, fn, None)):
    print("FAIL: ไม่พบฟังก์ชัน", fn); bad = True
for label, inp in (("ตัวอย่างถูกต้อง", sample), ("object ว่าง", "{}")):
    r = subprocess.run([sys.executable, path], input=inp, capture_output=True, text=True)
    print(f"CLI[{label}] rc={r.returncode} out={r.stdout.strip()[:200]} err={r.stderr.strip()[-200:]}")
    if "Traceback" in r.stderr:
        print("FAIL: CLI crash"); bad = True
    if label == "ตัวอย่างถูกต้อง" and '"ok": true' not in r.stdout:
        print("FAIL: ตัวอย่างถูกต้องควรได้ ok true"); bad = True
print("FAILED" if bad else "PASS")
sys.exit(1 if bad else 0)
