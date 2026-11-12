"""คิดเงินคืนคอร์สสอนชงกาแฟของร้าน BaanKafe

หน่วยเป็นสตางค์ทั้งหมด ใช้จำนวนเต็มล้วน ไม่มี float
เก็บทุกขั้นเป็นเศษ num/den แล้วปัดครั้งเดียวที่ขั้นสุดท้าย แบบครึ่งปัดขึ้น
"""

import json
import sys

PARAMS = ("paid", "used_percent", "restock")

MAX_USED_PERCENT_REFUNDABLE = 80
HANDLING_FEE_NUM = 125    # ค่าดำเนินการ 12.5% เป็นเศษส่วนจำนวนเต็ม 125 ต่อ 1000
HANDLING_FEE_DEN = 1000


def refund(paid, used_percent, restock):
    if type(paid) is not int:
        raise ValueError("paid ต้องเป็นจำนวนเต็ม (int) หน่วยสตางค์")
    if paid < 0:
        raise ValueError("paid ต้องไม่ติดลบ")
    if type(used_percent) is not int:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็ม (int)")
    if not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องอยู่ระหว่าง 0 ถึง 100")
    if type(restock) is not bool:
        raise ValueError("restock ต้องเป็น true หรือ false")

    if used_percent > MAX_USED_PERCENT_REFUNDABLE:
        return 0

    # ยอดคืนก่อนหักค่าดำเนินการ = paid * (100 - used_percent) / 100 เก็บเป็นเศษ
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        # หักค่าดำเนินการ 12.5% ของยอดคืน เหลือ (1000 - 125) ส่วน 1000
        num = num * (HANDLING_FEE_DEN - HANDLING_FEE_NUM)
        den = den * HANDLING_FEE_DEN
    # ปัดครึ่งขึ้นครั้งเดียวที่ขั้นสุดท้าย
    return (2 * num + den) // (2 * den)


def _fail(message):
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    sys.exit(2)


def main():
    try:
        data = json.loads(sys.stdin.read())
    except (ValueError, RecursionError):
        _fail("input ไม่ใช่ JSON ที่ถูกต้อง")
    if not isinstance(data, dict):
        _fail("input ต้องเป็น JSON object")
    missing = [key for key in PARAMS if key not in data]
    if missing:
        _fail("ขาด key: " + ", ".join(missing))
    try:
        result = refund(**{key: data[key] for key in PARAMS})
    except ValueError as exc:
        _fail(str(exc))
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
