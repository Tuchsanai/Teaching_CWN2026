"""
BaanKafe: คิดเงินคืนคอร์สสอนชงกาแฟ

กติกา (จากโจทย์)
1. paid       = เงินที่ลูกค้าจ่าย เป็นสตางค์ (int, >= 0)
2. used_percent = เรียนไปแล้วกี่เปอร์เซ็นต์ (int, 0-100)
3. คืนเงินตามสัดส่วนที่ยังไม่ได้เรียน: paid * (100 - used_percent) / 100
4. เรียนไปแล้วเกิน 80% (used_percent > 80) ไม่คืนเงิน -> 0
5. restock = True หักค่าดำเนินการ 12.5% ของยอดที่จะคืน
6. ผลเป็นจำนวนเต็มสตางค์

การตีความที่เลือกเอง (โจทย์ไม่ได้ระบุ)
- ทิศทางการปัด: ปัดลง (floor) เพราะเป็นเงินที่ร้านคืนให้ลูกค้า จะได้ไม่จ่ายเกิน
- ลำดับ: คำนวณทั้งหมดใน Fraction แล้วปัดครั้งเดียวตอนท้าย
- restock ใช้กับยอดหลังคำนวณสัดส่วนแล้ว และไม่ใช้เมื่อไม่คืนเงิน (ผลเป็น 0 อยู่แล้ว)
"""

import json
import sys
from fractions import Fraction
from math import floor

REFUND_CUTOFF_PERCENT = 80
RESTOCK_FEE = Fraction(125, 1000)  # 12.5%


def refund(paid, used_percent, restock):
    # ตรวจชนิดแบบเข้มงวด: type(...) is int ทำให้ bool และ float ถูก reject
    if type(paid) is not int:
        raise ValueError("paid ต้องเป็นจำนวนเต็ม (สตางค์)")
    if paid < 0:
        raise ValueError("paid ต้องไม่ติดลบ")

    if type(used_percent) is not int:
        raise ValueError("used_percent ต้องเป็นจำนวนเต็ม")
    if not 0 <= used_percent <= 100:
        raise ValueError("used_percent ต้องอยู่ระหว่าง 0 ถึง 100")

    if type(restock) is not bool:
        raise ValueError("restock ต้องเป็น True หรือ False")

    # เรียนเกิน 80% ไม่คืนเงิน
    if used_percent > REFUND_CUTOFF_PERCENT:
        return 0

    amount = Fraction(paid) * Fraction(100 - used_percent, 100)
    if restock:
        amount *= 1 - RESTOCK_FEE

    # ปัดลงครั้งเดียวที่ปลายสุด
    return floor(amount)


def main():
    try:
        payload = json.loads(sys.stdin.read())
        if not isinstance(payload, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = refund(**payload)
    except (ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
