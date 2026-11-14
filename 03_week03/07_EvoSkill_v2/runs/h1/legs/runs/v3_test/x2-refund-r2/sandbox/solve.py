"""คิดเงินคืนคอร์สสอนชงกาแฟ BaanKafe

กติกา:
- paid = เงินที่ลูกค้าจ่ายมา (สตางค์ ตั้งแต่ 0, จำนวนเต็ม)
- used_percent = เรียนไปแล้วกี่เปอร์เซ็นต์ (จำนวนเต็ม 0–100)
- restock = True คือหักค่าดำเนินการ, False คือไม่หัก
- คืนเงินตามสัดส่วนที่ยังไม่ได้เรียน: paid * (100 - used_percent) / 100
- เรียนไปแล้วเกิน 80% (used_percent > 80) ไม่คืนเงิน (คืน 0)
- ถ้า restock = True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
- คำนวณทั้งหมดด้วย Fraction แล้วปัดลงเป็นจำนวนเต็มสตางค์ครั้งเดียวตอนท้าย
  (เงินที่ร้านจ่ายคืนลูกค้า ปัดลงเพื่อไม่ให้จ่ายเกิน ตามแนวทางของสกิล money-rounding-satang)
- input ผิดชนิดหรือนอกช่วง raise ValueError
"""
import json
import sys
from fractions import Fraction
from math import floor


def _need_int(value, name, low=None, high=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def _need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def refund(paid, used_percent, restock):
    """คืนค่าเงินคืนเป็นจำนวนเต็มสตางค์"""
    paid = _need_int(paid, "paid", low=0)
    used_percent = _need_int(used_percent, "used_percent", low=0, high=100)
    restock = _need_bool(restock, "restock")

    if used_percent > 80:
        return 0

    amount = Fraction(paid) * Fraction(100 - used_percent, 100)
    if restock:
        amount = amount * (1 - Fraction(125, 1000))  # หักค่าดำเนินการ 12.5%

    return floor(amount)


def main():
    try:
        raw = sys.stdin.read()
        args = json.loads(raw)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = refund(**args)
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
