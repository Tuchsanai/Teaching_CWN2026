import json
import sys

RATE_NUM = 75        # อัตราค่าปรับ 75 ต่อ 10000 ของยอดค้างชำระต่อวัน
RATE_DEN = 10000
CAP_NUM = 15         # เพดานค่าปรับ 15 ต่อ 100 ของยอดค้างชำระ
CAP_DEN = 100
GRACE_DAYS = 3       # ช้าไม่เกินนี้ไม่คิดค่าปรับ
MAX_DAYS = 365


def _check_int(name, value):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม (int)")
    return value


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) ของยอดค้างชำระ amount ที่ชำระช้า days_late วัน"""
    amount = _check_int("amount", amount)
    days_late = _check_int("days_late", days_late)
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= MAX_DAYS:
        raise ValueError("days_late ต้องอยู่ระหว่าง 0 ถึง 365")
    if days_late <= GRACE_DAYS:
        return 0

    # เก็บทุกขั้นเป็นเศษ/ตัวส่วนโดยไม่ปัด แล้วเลือกค่าที่น้อยกว่าระหว่างค่าปรับกับเพดาน
    fee_num = amount * RATE_NUM * days_late
    fee_den = RATE_DEN
    cap_num = amount * CAP_NUM
    cap_den = CAP_DEN
    if fee_num * cap_den <= cap_num * fee_den:
        num, den = fee_num, fee_den
    else:
        num, den = cap_num, cap_den

    # ปัดครึ่งขึ้น (half-up) ครั้งเดียวที่ขั้นสุดท้าย
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input ต้องเป็น JSON object")
        if "amount" not in data or "days_late" not in data:
            raise ValueError("ต้องมี key amount และ days_late")
        result = late_fee(data["amount"], data["days_late"])
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
