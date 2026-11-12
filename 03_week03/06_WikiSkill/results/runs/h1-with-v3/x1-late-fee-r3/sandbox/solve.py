import json
import sys

# อัตราค่าปรับ 0.75% ต่อวัน เขียนเป็นเศษส่วนจำนวนเต็ม คือ 3 ต่อ 400
FEE_RATE_NUM = 3
FEE_RATE_DEN = 400
# เพดาน 15% เขียนเป็นเศษส่วนจำนวนเต็ม คือ 15 ต่อ 100
CAP_NUM = 15
CAP_DEN = 100
GRACE_DAYS = 3
MAX_DAYS = 365


def _round_half_up(num, den):
    return (2 * num + den) // (2 * den)


def _check_int(name, value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม (int)")


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์, int) ของยอดค้างชำระ amount ที่ชำระช้า days_late วัน"""
    _check_int("amount", amount)
    _check_int("days_late", days_late)
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if days_late < 0 or days_late > MAX_DAYS:
        raise ValueError("days_late ต้องอยู่ระหว่าง 0 ถึง 365")

    if days_late <= GRACE_DAYS:
        return 0

    # ค่าปรับดิบ = amount * days_late * 3 ต่อ 400 (นับทุกวันที่ช้า รวม 3 วันแรก)
    raw_num = amount * days_late * FEE_RATE_NUM
    raw_den = FEE_RATE_DEN
    # เพดาน = amount * 15 ต่อ 100
    cap_num = amount * CAP_NUM
    cap_den = CAP_DEN

    # เลือกค่าที่น้อยกว่า โดยเทียบข้ามคูณ ยังไม่ปัด
    if raw_num * cap_den > cap_num * raw_den:
        num, den = cap_num, cap_den
    else:
        num, den = raw_num, raw_den

    # ปัดครั้งเดียวที่ขั้นสุดท้าย แบบครึ่งปัดขึ้น
    return _round_half_up(num, den)


def _fail(message):
    print(json.dumps({"ok": False, "error": message}))
    return 2


def _main():
    try:
        data = json.loads(sys.stdin.read())
    except (ValueError, RecursionError) as exc:
        return _fail(f"JSON ไม่ถูกต้อง: {exc}")

    if not isinstance(data, dict):
        return _fail("input ต้องเป็น JSON object")

    missing = [key for key in ("amount", "days_late") if key not in data]
    if missing:
        return _fail("ขาด key: " + ", ".join(missing))

    try:
        result = late_fee(data["amount"], data["days_late"])
    except ValueError as exc:
        return _fail(str(exc))

    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
