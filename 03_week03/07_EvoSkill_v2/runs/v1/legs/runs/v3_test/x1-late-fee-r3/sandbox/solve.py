import json
import sys
from fractions import Fraction


def need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def _round_half_up(x):
    # x เป็น Fraction ไม่ติดลบ
    return int((x * 2 + 1) // 2)


def late_fee(amount, days_late):
    # สมมติฐาน: ค่าปรับเป็นเงินที่ลูกค้าจ่าย -> ปัดครึ่งขึ้นหนึ่งครั้งตอนจบ
    # เพดาน 15% ปัดครึ่งขึ้นเช่นกัน แล้วใช้ min หลังปัดเสร็จ
    need_int(amount, "amount", low=0)
    need_int(days_late, "days_late", low=0, high=365)
    if days_late <= 3:
        return 0
    fee = _round_half_up(Fraction(75, 10000) * amount * days_late)
    cap = _round_half_up(Fraction(15, 100) * amount)
    return min(fee, cap)


def main():
    try:
        args = json.load(sys.stdin)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = late_fee(**args)
    except (ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
