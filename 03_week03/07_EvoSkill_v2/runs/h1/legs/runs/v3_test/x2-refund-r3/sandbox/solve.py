"""คิดเงินคืนคอร์สสอนชงกาแฟ BaanKafe

กติกา (ตามโจทย์):
- paid          : เงินที่ลูกค้าจ่ายมา เป็นสตางค์ จำนวนเต็ม >= 0
- used_percent  : เรียนไปแล้วกี่เปอร์เซ็นต์ จำนวนเต็ม 0–100
- restock       : True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน, False = ไม่หัก
- คืนเงินตามสัดส่วนที่ยังไม่ได้เรียน = paid * (100 - used_percent) / 100
- เรียนไปแล้วเกิน 80% (used_percent > 80) = ไม่คืนเงิน (0)
- ผลลัพธ์เป็นจำนวนเต็มสตางค์ ปัดลง (เงินที่ร้านจ่ายคืนลูกค้า ไม่จ่ายเกิน)
- คำนวณทั้งหมดด้วย Fraction ปัดครั้งเดียวตอนท้าย

การตีความที่เลือกเอง:
- used_percent = 80 ยังได้คืนเงิน (เกิน 80 เท่านั้นที่ไม่คืน)
- ค่าดำเนินการคิดจากยอดคืนก่อนหัก (12.5% ของ pre-fee refund)
"""
import json
import sys
from fractions import Fraction
from math import floor


def _need_int(value, name, low=None, high=None):
    # bool เป็นคลาสย่อยของ int และ float/str ไม่ใช่ int จึงใช้ type() ตรวจแบบเข้มงวด
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def _need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _round_down(x):
    """ปัดลงเป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return floor(Fraction(x))


REFUND_CUTOFF_PERCENT = 80
HANDLING_FEE = Fraction(125, 1000)  # 12.5%


def refund(paid, used_percent, restock):
    """คืนค่าเงินคืนเป็นจำนวนเต็มสตางค์"""
    paid = _need_int(paid, "paid", low=0)
    used_percent = _need_int(used_percent, "used_percent", low=0, high=100)
    restock = _need_bool(restock, "restock")

    if used_percent > REFUND_CUTOFF_PERCENT:
        return 0

    amount = Fraction(paid) * Fraction(100 - used_percent, 100)
    if restock:
        amount = amount * (1 - HANDLING_FEE)
    return _round_down(amount)


def main():
    try:
        args = json.loads(sys.stdin.read())
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = refund(**args)
    except (ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
