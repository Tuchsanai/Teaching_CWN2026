import json
import sys

REQUIRED_KEYS = ("paid", "used_percent", "restock")


def _check_int(name, value):
    # type(...) is int ปฏิเสธ bool, ทศนิยม, str, None และชนิดอื่นทั้งหมด
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม (int)")


def refund(paid, used_percent, restock):
    _check_int("paid", paid)
    _check_int("used_percent", used_percent)
    if type(restock) is not bool:
        raise ValueError("restock ต้องเป็น true หรือ false")
    if paid < 0:
        raise ValueError("paid ต้องไม่ติดลบ")
    if used_percent < 0 or used_percent > 100:
        raise ValueError("used_percent ต้องอยู่ระหว่าง 0 ถึง 100")

    # เรียนไปแล้วเกิน 80% ไม่คืนเงิน
    if used_percent > 80:
        return 0

    # ยอดคืนก่อนหักค่าดำเนินการ = paid * (100 - used_percent) ส่วน 100 เก็บเป็นตัวเศษ num และตัวส่วน den โดยไม่ปัด
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        # หักค่าดำเนินการ 12.5% คือ 125 ส่วน 1000 ของยอดคืน เหลือ 875 ส่วน 1000
        num = num * 875
        den = den * 1000
    # ปัดครึ่งขึ้น (half-up) ครั้งเดียวที่ขั้นสุดท้าย
    return (2 * num + den) // (2 * den)


REQUIRED_KEYS_SET = set(REQUIRED_KEYS)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("input ต้องเป็น JSON object")
        missing = [k for k in REQUIRED_KEYS if k not in data]
        if missing:
            raise ValueError("ขาด key: " + ", ".join(missing))
        extra = [str(k) for k in data if k not in REQUIRED_KEYS_SET]
        if extra:
            raise ValueError("key ไม่รู้จัก: " + ", ".join(extra))
        result = refund(**{k: data[k] for k in REQUIRED_KEYS})
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
