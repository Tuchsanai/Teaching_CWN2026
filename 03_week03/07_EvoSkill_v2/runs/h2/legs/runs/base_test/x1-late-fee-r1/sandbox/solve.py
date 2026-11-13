"""ค่าปรับการชำระเงินล่าช้าของลูกค้าขายส่ง BaanKafe."""

GRACE_DAYS = 3          # ช้าไม่เกินกี่วันถึงไม่คิดค่าปรับ
DAILY_RATE_BP = 75      # 0.75%ต่อวัน (หน่วยเป็น basis point: 1 bp = 0.01%)
MAX_RATE_PCT = 15       # ค่าปรับสูงสุด 15% ของยอดค้างชำระ
MAX_DAYS_LATE = 365


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับ (สตางค์, จำนวนเต็ม) สำหรับยอดค้างชำระ `amount` สตางค์ที่ช้า `days_late` วัน

    - ช้าไม่เกิน 3 วัน: ไม่มีค่าปรับ
    - ช้าเกิน 3 วัน: คิด 0.75% ต่อวันของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
    - ค่าปรับสูงสุดไม่เกิน 15% ของยอดค้างชำระ
    - การคำนวณใช้จำนวนเต็มล้วน ปัดเศษ 0.5 ขึ้น (half up) และปัดค่าเพดานลง

    ตัวอย่าง: late_fee(10000, 5) == 375  (100.00 บาท ช้า 5 วัน -> 3.75 บาท)
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise TypeError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= MAX_DAYS_LATE:
        raise ValueError(f"days_late ต้องอยู่ระหว่าง 0 ถึง {MAX_DAYS_LATE}")

    if days_late <= GRACE_DAYS:
        return 0

    # fee = amount * 0.75% * days  ->  amount * 75 * days / 10000 (ปัดครึ่งขึ้น)
    fee = (amount * DAILY_RATE_BP * days_late + 5000) // 10000

    # เพดาน 15% ของยอดค้าง; ค่าเพดานเป็นจำนวนเต็มจึงใช้การหารปัดลง
    cap = amount * MAX_RATE_PCT // 100
    return min(fee, cap)


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        print(late_fee(int(sys.argv[1]), int(sys.argv[2])))
    else:
        print("usage: python solve.py <amount_satang> <days_late>")
