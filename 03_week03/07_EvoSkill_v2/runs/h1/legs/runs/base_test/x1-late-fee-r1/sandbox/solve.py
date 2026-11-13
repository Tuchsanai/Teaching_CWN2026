"""ค่าปรับการชำระเงินล่าช้าของลูกค้าขายส่ง BaanKafe

กฎ:
- ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน คิดค่าปรับวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุด 15% ของยอดค้างชำระ
- คืนค่าปรับเป็นจำนวนเต็มสตางค์

การคำนวณใช้จำนวนเต็มล้วน (ไม่ใช้ float) เพื่อหลีกเลี่ยงความคลาดเคลื่อนของทศนิยม
- 0.75% = 75 / 10000
- 15%   = 15 / 100
- การปัดเศษ: ปัดครึ่งขึ้นเป็นสตางค์ที่ใกล้ที่สุด
"""

GRACE_DAYS = 3
DAILY_RATE_BP = 75        # 0.75% ต่อวัน หน่วยเป็น 1/10000
MAX_RATE_PCT = 15         # เพดาน 15%
MAX_DAYS = 365


def late_fee(amount: int, days_late: int) -> int:
    """คำนวณค่าปรับ (สตางค์, จำนวนเต็ม)

    amount    : ยอดค้างชำระ หน่วยสตางค์ (>= 0)
    days_late : จำนวนวันที่ชำระช้า (0–365)
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise TypeError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= MAX_DAYS:
        raise ValueError(f"days_late ต้องอยู่ในช่วง 0–{MAX_DAYS}")

    if days_late <= GRACE_DAYS:
        return 0

    # ค่าปรับดิบ = amount * 0.75% * days_late, ปัดครึ่งขึ้นเป็นสตางค์
    raw_fee = (amount * DAILY_RATE_BP * days_late + 5000) // 10000

    # เพดาน 15% ของยอดค้างชำระ (ค่าปรับเป็นจำนวนเต็ม จึงใช้การหารปัดลงได้ถูกต้อง)
    cap = amount * MAX_RATE_PCT // 100

    return min(raw_fee, cap)


if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    examples = [
        (100_000, 0),    # 1,000.00 บาท ไม่ช้า -> 0
        (100_000, 3),    # ช้า 3 วัน ยังไม่คิด -> 0
        (100_000, 4),    # ช้า 4 วัน -> 3,000 สตางค์ (30.00 บาท)
        (100_000, 10),   # ช้า 10 วัน -> 7,500 สตางค์
        (100_000, 20),   # ถึงเพดาน 15% -> 15,000 สตางค์
        (100_000, 365),  # ยังคงเพดาน 15% -> 15,000 สตางค์
        (1, 4),          # ปัดเศษ 0.0075 -> 0
    ]
    for amt, d in examples:
        print(f"amount={amt:>10} days_late={d:>3} -> fee={late_fee(amt, d)}")
