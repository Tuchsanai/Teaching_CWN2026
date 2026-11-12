import json
import sys

# อัตราค่าปรับ 0.75% ต่อวัน เขียนเป็นเศษส่วน 3 ส่วน 400
RATE_NUM = 3
# ตัวส่วนร่วมของอัตรา
RATE_DEN = 400
# เพดาน 15% เขียนเป็นตัวเศษ 60 ส่วน 400
CAP_NUM = 60
# ช้าไม่เกินจำนวนวันนี้ ไม่คิดค่าปรับ
GRACE_DAYS = 3


def _check_int(name, value, low, high):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if value < low or (high is not None and value > high):
        if high is None:
            raise ValueError(f"{name} ต้องไม่น้อยกว่า {low}")
        raise ValueError(f"{name} ต้องอยู่ระหว่าง {low} ถึง {high}")
    return value


def late_fee(amount, days_late):
    amount = _check_int("amount", amount, 0, None)
    days_late = _check_int("days_late", days_late, 0, 365)
    if days_late <= GRACE_DAYS:
        return 0
    # อัตรารวมก่อนปัด (ตัวเศษ) ถูกจำกัดด้วยเพดาน 15%
    rate_num = min(RATE_NUM * days_late, CAP_NUM)
    num = amount * rate_num
    # ปัดครึ่งขึ้นครั้งเดียวที่ขั้นสุดท้าย
    return (2 * num + RATE_DEN) // (2 * RATE_DEN)


def _fail(message):
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    return 2


def main():
    try:
        data = json.loads(sys.stdin.read())
    except ValueError:
        return _fail("JSON ไม่ถูกต้อง")
    if not isinstance(data, dict):
        return _fail("input ต้องเป็น JSON object")
    missing = [k for k in ("amount", "days_late") if k not in data]
    if missing:
        return _fail("ขาด key: " + ", ".join(missing))
    try:
        result = late_fee(data["amount"], data["days_late"])
    except ValueError as exc:
        return _fail(str(exc))
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
