"""ค่าปรับการชำระเงินช้าของลูกค้าขายส่ง BaanKafe

กฎ:
- amount     = ยอดค้างชำระ (สตางค์ ตั้งแต่ 0)
- days_late  = จำนวนวันที่ชำระช้า (จำนวนเต็ม 0–365)
- ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
- ช้าเกิน 3 วัน คิดวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
- ค่าปรับสูงสุดไม่เกิน 15% ของยอดค้างชำระ
- คืนค่าปรับเป็นจำนวนเต็มสตางค์ (ปัดเศษครึ่งขึ้น)
"""

GRACE_DAYS = 3
DAILY_RATE_BP = 75        # 0.75% = 75 basis points (หน่วยเป็น 1/10000)
MAX_RATE_PERCENT = 15     # เพดาน 15%
MAX_DAYS = 365


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) สำหรับยอดค้างชำระ amount และจำนวนวันที่ช้า days_late."""
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise TypeError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= MAX_DAYS:
        raise ValueError(f"days_late ต้องอยู่ระหว่าง 0–{MAX_DAYS}")

    if days_late <= GRACE_DAYS:
        return 0

    # ค่าปรับดิบ = amount * 0.75% * days_late  (คำนวณด้วยจำนวนเต็มล้วนเพื่อไม่ให้เกิดทศนิยมคลาดเคลื่อน)
    # หารด้วย 10000 แล้วปัดครึ่งขึ้น: floor((x + 5000) / 10000)
    raw_fee = (amount * DAILY_RATE_BP * days_late + 5000) // 10000

    # เพดาน 15% ของยอดค้างชำระ; เนื่องจากค่าปรับเป็นจำนวนเต็ม
    # fee <= 0.15*amount  <=>  fee <= floor(0.15*amount)
    cap = amount * MAX_RATE_PERCENT // 100

    return min(raw_fee, cap)


if __name__ == "__main__":
    # ตัวอย่างการใช้งานอย่างรวดเร็ว
    examples = [
        (100_000, 0),   # 0 วัน -> 0
        (100_000, 3),   # ช้า 3 วัน (ยังไม่เกินเกณฑ์) -> 0
        (100_000, 4),   # 4 วัน -> 3,000 สตางค์ (0.75% * 4)
        (100_000, 10),  # 10 วัน -> 7,500
        (100_000, 20),  # 20 วัน -> 15,000 (ถึงเพดาน 15%)
        (100_000, 365), # เกินเพดาน -> 15,000
        (101, 4),       # 101 * 0.0075 * 4 = 3.03 -> 3
    ]
    for amt, d in examples:
        print(f"amount={amt:>7}  days_late={d:>3}  fee={late_fee(amt, d)}")
