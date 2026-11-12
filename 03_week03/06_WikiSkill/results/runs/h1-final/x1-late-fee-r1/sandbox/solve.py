import sys
import json
from fractions import Fraction

FREE_DAYS = 3                      # ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
DAILY_RATE = Fraction(75, 10000)   # 0.75% ต่อวัน
CAP_RATE = Fraction(15, 100)       # เพดาน 15% ของยอดค้างชำระ


def _half_up(x: Fraction) -> int:
    return (2 * x.numerator + x.denominator) // (2 * x.denominator)


def _int(v, name, lo=None, hi=None):
    if isinstance(v, bool) or not isinstance(v, int):
        raise ValueError(f"{name} must be an integer")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def late_fee(amount, days_late):
    amount = _int(amount, "amount", lo=0)
    days_late = _int(days_late, "days_late", lo=0, hi=365)

    if days_late <= FREE_DAYS:
        return 0

    # นับทุกวันที่ช้า (รวม 3 วันแรก) เก็บเป็นเศษส่วนก่อน ยังไม่ปัด
    raw_fee = amount * DAILY_RATE * days_late
    cap = amount * CAP_RATE

    # ปัดครั้งเดียว half up แล้วจึงเทียบเพดาน
    return min(_half_up(raw_fee), _half_up(cap))


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = late_fee(**data)
        out = json.dumps({"ok": True, "result": result})
    except Exception as e:  # รวม JSON เสีย, key เกิน/ขาด, ValueError
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
