#!/usr/bin/env python3
"""Grader ของชุดโจทย์ money-coder: python3 grade.py <sandbox> <task.json> -> JSON บรรทัดเดียว

ตรวจ "ผลงาน" ใน sandbox (solve.py + test_solve.py) กับมาตรฐานคิดเงินของร้าน BaanKafe 10 ข้อ
คำตอบที่ถูกคำนวณด้วยเศษส่วน (Fraction) ในไฟล์นี้ · Agent ที่ถูกวัดต้องไม่เห็นไฟล์นี้
"""
import json, os, re, subprocess, sys
from fractions import Fraction as F


def half_up(x):
    return int((F(x) * 2 + 1) // 2)


# ------------------------------------------------------------ คำตอบที่ถูก (oracle)
def o_cafe_bill(items, member):
    sub = sum(i["price"] * i["qty"] for i in items)
    x = F(sub)
    if sub >= 50000:
        x *= F(95, 100)
    if member:
        x *= F(90, 100)
    return half_up(x * F(107, 100))


def o_split_bill(total, people, tip_percent):
    grand = half_up(F(total * (100 + tip_percent), 100))
    base, rem = divmod(grand, people)
    return [base + 1] * rem + [base] * (people - rem)


def o_shipping_fee(weight_g, distance_km, express):
    if weight_g <= 1000:
        x = F(4000)
    elif weight_g <= 5000:
        x = F(8000)
    else:
        x = F(8000) + F(15 * (weight_g - 5000), 10)
    if distance_km > 100:
        x *= F(12, 10)
    if express:
        x *= F(15, 10)
    return half_up(x)


RATE = {"silver": F(15, 1000), "gold": F(25, 1000), "platinum": F(4, 100)}


def o_cashback(amount, tier, birthday):
    if amount < 10000:
        return 0
    x = amount * RATE[tier]
    if birthday:
        x *= 2
    return min(20000, half_up(x))


def o_parking_fee(minutes, member):
    if minutes <= 30:
        return 0
    hours = -(-minutes // 60)
    x = F(min(hours * 2500, 25000))
    if member:
        x *= F(85, 100)
    return half_up(x * F(107, 100))


def o_net_pay(hours, rate, has_sso):
    gross = F(rate * min(hours, 40)) + F(rate * 3 * max(hours - 40, 0), 2)
    tax = gross * F(3, 100)
    sso = min(gross * F(5, 100), F(75000)) if has_sso else 0
    return half_up(gross - tax - sso)

def o_late_fee(amount, days_late):
    if days_late <= 3:
        return 0
    return half_up(min(amount * F(75, 10000) * days_late, amount * F(15, 100)))


def o_refund(paid, used_percent, restock):
    if used_percent > 80:
        return 0
    x = paid * F(100 - used_percent, 100)
    if restock:
        x *= F(875, 1000)
    return half_up(x)


def o_bulk_price(unit_price, qty, coupon):
    x = F(unit_price * qty)
    if qty >= 50:
        x *= F(925, 1000)
    elif qty >= 10:
        x *= F(965, 1000)
    if coupon:
        x *= F(975, 1000)
    return half_up(x * F(107, 100))


def it(*pq):
    return [{"price": p, "qty": q} for p, q in pq]


# ------------------------------------------------------------ กรณีทดสอบ (ซ่อนจาก Agent)
# basic = กรณีปกติ · half_up = ผลลงท้าย .5 สตางค์ · no_drift = ปัดระหว่างทางแล้วผลเพี้ยน
# boundary = ค่าขอบของเงื่อนไข · bad_value / bad_type = input ที่ต้องถูกปฏิเสธด้วย ValueError
TASKS = {
    "t1-cafe-bill": {
        "func": "cafe_bill", "oracle": o_cafe_bill, "args": ["items", "member"],
        "basic": [[it((4500, 2)), False], [it((4500, 2)), True], [it((12000, 1), (6500, 2)), False], [it((20000, 3)), True]],
        "half_up": [[it((1150, 1)), False], [it((750, 2)), True], [it((2350, 1)), False]],
        "no_drift": [[it((4505, 1)), True], [it((25075, 2)), True], [it((16750, 3)), False]],
        "boundary": [[it((50000, 1)), False], [it((49999, 1)), False], [it((0, 1), (4500, 1)), False]],
        "bad_value": [[it((4500, 0)), False], [it((4500, -1)), False], [it((-100, 1)), False]],
        "bad_type": [[it((4500.0, 1)), False], [it((4500, "2")), False], [it((4500, True)), False],
                     [it((4500, 1)), "yes"], [None, False]],
        "cli_ok": [[it((4500, 2)), False], [it((20000, 3)), True]],
        "cli_err": [it((4500, 0)), False],
    },
    "t2-split-bill": {
        "func": "split_bill", "oracle": o_split_bill, "args": ["total", "people", "tip_percent"],
        "basic": [[30000, 3, 0], [30000, 4, 10], [12000, 2, 5]],
        "half_up": [[1010, 1, 5], [1030, 1, 15], [1050, 2, 5]],
        "no_drift": [[10000, 3, 0], [10000, 7, 10], [5000, 6, 0]],
        "boundary": [[0, 3, 10], [2, 3, 0], [9999, 1, 0], [1000, 2, 100]],
        "bad_value": [[10000, 0, 0], [10000, -2, 0], [-1, 2, 0], [10000, 2, -5], [10000, 2, 101]],
        "bad_type": [[10000.0, 2, 0], [10000, "3", 0], [10000, True, 0], [10000, 2, None]],
        "cli_ok": [[10000, 3, 0], [30000, 4, 10]],
        "cli_err": [10000, 0, 0],
    },
    "t3-shipping-fee": {
        "func": "shipping_fee", "oracle": o_shipping_fee, "args": ["weight_g", "distance_km", "express"],
        "basic": [[500, 20, False], [3000, 20, False], [3000, 150, False], [500, 20, True], [7000, 20, False], [7000, 150, True]],
        "half_up": [[5019, 50, False], [5026, 50, True], [5075, 150, True]],
        "no_drift": [[5106, 150, True], [5217, 50, True], [5439, 150, False], [5328, 150, True]],
        "boundary": [[1000, 0, False], [1001, 0, False], [5000, 0, False], [3000, 100, False], [3000, 101, False],
                     [30000, 0, False], [1, 0, False]],
        "bad_value": [[0, 10, False], [-5, 10, False], [30001, 10, False], [1000, -1, False]],
        "bad_type": [[1000.0, 10, False], ["1000", 10, False], [True, 10, False], [1000, 10, "yes"], [1000, None, False]],
        "cli_ok": [[3000, 150, False], [7000, 150, True]],
        "cli_err": [0, 10, False],
    },
    "t4-cashback": {
        "func": "cashback", "oracle": o_cashback, "args": ["amount", "tier", "birthday"],
        "basic": [[20000, "silver", False], [20000, "gold", False], [20000, "platinum", True], [100000, "gold", True]],
        "half_up": [[10020, "gold", False], [10300, "silver", False], [10100, "gold", False]],
        "no_drift": [[10020, "silver", True], [10020, "gold", True], [10010, "platinum", True]],
        "boundary": [[9999, "gold", False], [10000, "silver", False], [500000, "platinum", False],
                     [500100, "platinum", False], [800000, "gold", True], [0, "gold", False]],
        "bad_value": [[-1, "gold", False], [20000, "bronze", False], [20000, "", False]],
        "bad_type": [[20000.0, "gold", False], ["20000", "gold", False], [True, "gold", False],
                     [20000, None, False], [20000, "gold", "yes"]],
        "cli_ok": [[20000, "gold", False], [100000, "gold", True]],
        "cli_err": [20000, "bronze", False],
    },
    "v1-parking-fee": {
        "func": "parking_fee", "oracle": o_parking_fee, "args": ["minutes", "member"],
        "basic": [[45, False], [120, False], [60, True], [480, True]],
        "half_up": [[360, True], [310, True]],
        "no_drift": [[180, True], [300, True], [420, True]],
        "boundary": [[30, False], [31, False], [60, False], [61, False], [0, False], [600, False], [660, False], [1440, False]],
        "bad_value": [[-1, False], [1441, False]],
        "bad_type": [[90.0, False], ["90", False], [True, False], [90, "no"], [90, None]],
        "cli_ok": [[120, False], [480, True]],
        "cli_err": [-1, False],
    },
    "v2-net-pay": {
        "func": "net_pay", "oracle": o_net_pay, "args": ["hours", "rate", "has_sso"],
        "basic": [[40, 10000, False], [40, 10000, True], [45, 10000, False], [20, 8000, True]],
        "half_up": [[41, 5100, False], [45, 5500, False], [41, 5900, False]],
        "no_drift": [[38, 5005, True], [41, 5005, True], [45, 5055, False]],
        "boundary": [[0, 10000, False], [40, 12345, False], [41, 10000, False], [80, 10000, False],
                     [40, 37500, True], [40, 50000, True]],
        "bad_value": [[-1, 10000, False], [81, 10000, False], [40, -100, False]],
        "bad_type": [[40.0, 10000, False], ["40", 10000, False], [True, 10000, False], [40, 100.5, False], [40, 10000, "yes"]],
        "cli_ok": [[40, 10000, True], [45, 10000, False]],
        "cli_err": [81, 10000, False],
    },
    # ---- Test Set: ไม่ถูกใช้ระหว่างการปรับสกิล ใช้วัดครั้งเดียวตอนจบ
    "x1-late-fee": {
        "func": "late_fee", "oracle": o_late_fee, "args": ["amount", "days_late"],
        "basic": [[100000, 4], [100000, 10], [250000, 7], [80000, 30]],
        "half_up": [[100, 6], [120, 5], [200, 7], [10, 30]],
        "no_drift": [[1234, 7], [5555, 15], [10030, 4], [1234, 19]],
        "boundary": [[100000, 3], [100000, 0], [100000, 20], [100000, 21], [0, 10], [100000, 365]],
        "bad_value": [[-1, 5], [100000, -1], [100000, 366]],
        "bad_type": [[100000.0, 5], ["100000", 5], [True, 5], [100000, 5.0], [100000, None]],
        "cli_ok": [[100000, 10], [250000, 7]],
        "cli_err": [100000, 366],
    },
    "x2-refund": {
        "func": "refund", "oracle": o_refund, "args": ["paid", "used_percent", "restock"],
        "basic": [[100000, 0, False], [100000, 25, False], [100000, 50, True], [240000, 10, True]],
        "half_up": [[150, 25, False], [100, 40, True], [200, 10, True]],
        "no_drift": [[5551, 13, True], [3992, 66, True], [7980, 7, True], [11968, 45, True]],
        "boundary": [[100000, 80, False], [100000, 81, False], [100000, 100, False], [0, 0, True], [1, 0, False]],
        "bad_value": [[-1, 10, False], [100000, -1, False], [100000, 101, False]],
        "bad_type": [[100000.0, 10, False], ["100000", 10, False], [True, 10, False], [100000, 10.0, False],
                     [100000, 10, "yes"]],
        "cli_ok": [[100000, 25, False], [240000, 10, True]],
        "cli_err": [100000, 101, False],
    },
    "x3-bulk-price": {
        "func": "bulk_price", "oracle": o_bulk_price, "args": ["unit_price", "qty", "coupon"],
        "basic": [[25000, 1, False], [25000, 10, False], [25000, 50, False], [25000, 20, True]],
        "half_up": [[50, 1, False], [100, 60, False], [800, 100, True]],
        "no_drift": [[4989, 50, True], [7980, 13, True], [8977, 13, False], [9974, 50, True]],
        "boundary": [[25000, 9, False], [25000, 49, False], [25000, 1000, False], [0, 5, True], [1, 1, False]],
        "bad_value": [[25000, 0, False], [25000, 1001, False], [-1, 5, False]],
        "bad_type": [[25000.0, 5, False], ["25000", 5, False], [25000, True, False], [25000, 5.0, False],
                     [25000, 5, None]],
        "cli_ok": [[25000, 10, False], [25000, 20, True]],
        "cli_err": [25000, 0, False],
    },
}

HARNESS = r'''
import json, sys, io
sys.path.insert(0, ".")
spec = json.load(open(sys.argv[1], encoding="utf-8"))
out = {"import_error": None, "results": []}
try:
    import solve
    fn = getattr(solve, spec["func"])
except BaseException as e:
    out["import_error"] = "%s: %s" % (type(e).__name__, str(e)[:200])
    fn = None
def is_int(v):
    if isinstance(v, list):
        return all(type(x) is int for x in v)
    return type(v) is int
for c in spec["cases"] if fn else []:
    r = {}
    try:
        v = fn(*c["args"])
        try:
            same = bool(v == c["exp"]) if "exp" in c else False
        except Exception:
            same = False
        r = {"value": repr(v)[:120], "same": same, "is_int": is_int(v)}
    except BaseException as e:
        r = {"exc": type(e).__name__, "value_error": isinstance(e, ValueError), "msg": str(e)[:80]}
    out["results"].append(r)
print("\n@@RESULT@@" + json.dumps(out))
'''


def run_cases(sb, rdir, func, cases):
    """รันทุกกรณีใน subprocess เดียว (cwd = sandbox) · cases = [{"args": [...], "exp": ...}]"""
    spec = os.path.join(rdir, "_spec.json")
    hfile = os.path.join(rdir, "_harness.py")
    json.dump({"func": func, "cases": cases}, open(spec, "w", encoding="utf-8"))
    open(hfile, "w", encoding="utf-8").write(HARNESS)
    try:
        p = subprocess.run([sys.executable, hfile, spec], cwd=sb, capture_output=True, text=True, timeout=60,
                           stdin=subprocess.DEVNULL)
        m = re.search(r"@@RESULT@@(.*)", p.stdout)
        res = json.loads(m.group(1)) if m else {"import_error": "ไม่มีผลจาก harness: " + (p.stderr or "")[-200:], "results": []}
    except subprocess.TimeoutExpired:
        res = {"import_error": "import หรือเรียกฟังก์ชันค้างเกิน 60 วินาที (อาจอ่าน stdin ตอน import)", "results": []}
    finally:
        for f in (spec, hfile):
            try:
                os.remove(f)
            except OSError:
                pass
    return res


def show(args):
    return json.dumps(args, ensure_ascii=False)


def cli(sb, payload):
    try:
        p = subprocess.run([sys.executable, "solve.py"], cwd=sb, input=payload, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return None, "", "timeout"
    return p.returncode, p.stdout.strip(), p.stderr


def main():
    sb, task = sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8"))
    rdir = os.path.dirname(os.path.abspath(sys.argv[2]))
    T = TASKS[task["id"]]
    checks = []

    def add(cid, ok, note=""):
        checks.append({"id": cid, "pass": bool(ok), "note": "" if ok else note})

    groups = ["basic", "half_up", "no_drift", "boundary", "bad_value", "bad_type"]
    cases, index = [], {}
    for g in groups:
        for a in T[g]:
            c = {"args": a}
            if not g.startswith("bad"):
                c["exp"] = T["oracle"](*a)
            index.setdefault(g, []).append(len(cases))
            cases.append(c)
    have = os.path.isfile(os.path.join(sb, "solve.py"))
    res = run_cases(sb, rdir, T["func"], cases) if have else {"import_error": "ไม่มีไฟล์ solve.py", "results": []}
    R, err = res["results"], res["import_error"]

    # 1 contract: มีไฟล์ มีฟังก์ชัน และคืนค่าเป็น int สตางค์
    if err:
        add("contract", False, "ใช้ฟังก์ชัน %s ไม่ได้: %s" % (T["func"], err))
    else:
        r0 = R[index["basic"][0]]
        add("contract", r0.get("is_int"), "ฟังก์ชันต้องคืน int สตางค์ แต่ได้ %s" % (r0.get("value") or r0.get("exc")))

    # 2-5 ค่าที่คำนวณ
    for g in ("basic", "half_up", "no_drift", "boundary"):
        if err:
            add(g, False, "ใช้ฟังก์ชันไม่ได้")
            continue
        bad = [(cases[i], R[i]) for i in index[g] if not R[i].get("same")]
        add(g, not bad, "" if not bad else "%s(%s) คาด %s ได้ %s · พลาด %d จาก %d กรณี" % (
            T["func"], show(bad[0][0]["args"])[1:-1], bad[0][0]["exp"], bad[0][1].get("value") or bad[0][1].get("exc"),
            len(bad), len(index[g])))

    # 6-7 input ผิดต้อง raise ValueError
    for g, cid in (("bad_value", "reject_value"), ("bad_type", "reject_type")):
        if err:
            add(cid, False, "ใช้ฟังก์ชันไม่ได้")
            continue
        bad = [(cases[i], R[i]) for i in index[g] if not R[i].get("value_error")]
        add(cid, not bad, "" if not bad else "%s(%s) ต้อง raise ValueError แต่%s · พลาด %d จาก %d กรณี" % (
            T["func"], show(bad[0][0]["args"])[1:-1],
            "คืนค่า %s" % bad[0][1]["value"] if "value" in bad[0][1] else " raise %s" % bad[0][1].get("exc"),
            len(bad), len(index[g])))

    # 8 cli_ok: python3 solve.py < JSON -> {"ok": true, "result": ...} exit 0
    note = ""
    for a in T["cli_ok"] if have else []:
        exp = T["oracle"](*a)
        rc, out, _ = cli(sb, json.dumps(dict(zip(T["args"], a))))
        try:
            d = json.loads(out)
        except ValueError:
            d = None
        if rc != 0 or not isinstance(d, dict) or d.get("ok") is not True or d.get("result") != exp:
            note = 'stdin %s ต้องได้ {"ok": true, "result": %s} exit 0 แต่ได้ exit %s stdout %s' % (
                show(dict(zip(T["args"], a))), json.dumps(exp), rc, out[:120] or "(ว่าง)")
            break
    add("cli_ok", have and not note, note or "ไม่มีไฟล์ solve.py")

    # 9 cli_error: input ผิด หรือ JSON อ่านไม่ได้ -> {"ok": false, "error": "..."} exit 2 ไม่มี traceback
    note = ""
    for payload in ([json.dumps(dict(zip(T["args"], T["cli_err"]))), "{bad json"] if have else []):
        rc, out, se = cli(sb, payload)
        try:
            d = json.loads(out)
        except ValueError:
            d = None
        good = rc == 2 and isinstance(d, dict) and d.get("ok") is False and isinstance(d.get("error"), str) \
            and d["error"].strip() and "Traceback" not in se
        if not good:
            note = 'stdin %s ต้องได้ {"ok": false, "error": "..."} exit 2 ไม่มี traceback แต่ได้ exit %s stdout %s%s' % (
                payload[:80], rc, out[:100] or "(ว่าง)", " · stderr มี Traceback" if "Traceback" in se else "")
            break
    add("cli_error", have and not note, note or "ไม่มีไฟล์ solve.py")

    # 10 tests: test_solve.py (unittest) >= 6 เทสต์ รันผ่าน และมีเทสต์ของ input ผิด
    tf = os.path.join(sb, "test_solve.py")
    if not os.path.isfile(tf):
        add("tests", False, "ไม่มีไฟล์ test_solve.py ข้าง solve.py")
    else:
        src = open(tf, encoding="utf-8", errors="replace").read()
        try:
            p = subprocess.run([sys.executable, "-m", "unittest", "-q", "test_solve"], cwd=sb, capture_output=True,
                               text=True, timeout=120, stdin=subprocess.DEVNULL)
            o, rc = p.stdout + p.stderr, p.returncode
        except subprocess.TimeoutExpired:
            o, rc = "timeout", 1
        m = re.search(r"Ran (\d+) test", o)
        n = int(m.group(1)) if m else 0
        if rc != 0:
            add("tests", False, "python3 -m unittest -q test_solve ไม่ผ่าน: %s" % o.strip()[-160:])
        elif n < 6:
            add("tests", False, "unittest พบ %d เทสต์ (ต้องมีอย่างน้อย 6)" % n)
        elif "assertRaises" not in src or "ValueError" not in src:
            add("tests", False, "ไม่มีเทสต์ของ input ผิด (assertRaises ValueError)")
        else:
            add("tests", True)

    score = sum(1 for c in checks if c["pass"]) / len(checks)
    print(json.dumps({"score": round(score, 4), "checks": checks}, ensure_ascii=False))


if __name__ == "__main__":
    main()
