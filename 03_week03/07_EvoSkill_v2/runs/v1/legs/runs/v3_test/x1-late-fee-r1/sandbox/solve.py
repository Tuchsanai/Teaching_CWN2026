import json
import sys
from fractions import Fraction


def need_int(v, name, low=None, high=None):
    if type(v) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and v < low) or (high is not None and v > high):
        raise ValueError(f"{name} อยู่นอกช่วง")
    return v


def late_fee(amount, days_late):
    """ค่าปรับชำระช้า (สตางค์).

    สมมติฐาน: ค่าปรับเป็นเงินที่ลูกค้าจ่าย -> ปัดครึ่งขึ้นครั้งเดียว
    แล้วจึงใช้เพดาน 15% (เพดานเป็นสตางค์เต็ม ปัดครึ่งขึ้นเช่นกัน)
    """
    need_int(amount, "amount", low=0)
    need_int(days_late, "days_late", low=0, high=365)
    if days_late <= 3:
        return 0
    fee = Fraction(amount * 75 * days_late, 10000)
    fee = int((fee * 2 + 1) // 2)
    cap = int((Fraction(amount * 15, 100) * 2 + 1) // 2)
    return min(cap, fee)


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
