"""คำนวณค่าปรับการชำระเงินล่าช้าของลูกค้าขายส่ง BaanKafe."""

GRACE_DAYS = 3          # ช้าไม่เกินกี่วันไม่คิดค่าปรับ
DAILY_RATE_BP = 75      # 0.75% ต่อวัน ในหน่วย basis point (1 bp = 0.01%)
CAP_PERCENT = 15        # ค่าปรับสูงสุดเป็นเปอร์เซ็นต์ของยอดค้างชำระ
MAX_DAYS_LATE = 365


def late_fee(amount: int, days_late: int) -> int:
    """คืนค่าปรับเป็นจำนวนเต็มสตางค์

    amount     ยอดค้างชำระ (สตางค์ ตั้งแต่ 0)
    days_late  จำนวนวันที่ช้า (จำนวนเต็ม 0–365)

    กติกา:
      - ช้าไม่เกิน 3 วัน ไม่คิดค่าปรับ
      - ช้าเกิน 3 วัน คิดวันละ 0.75% ของยอดค้างชำระ นับทุกวันที่ช้า (รวม 3 วันแรก)
      - ค่าปรับสูงสุด 15% ของยอดค้างชำระ

    การปัดเศษ: ปัดครึ่งขึ้นเป็นสตางค์ที่ใกล้ที่สุด (คำนวณด้วยจำนวนเต็มล้วน ไม่มีค่าทศนิยม)
    เพดาน 15% ปัดลง เพื่อไม่ให้ค่าปรับเกินเพดานจริง
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็ม (สตางค์)")
    if isinstance(days_late, bool) or not isinstance(days_late, int):
        raise TypeError("days_late ต้องเป็นจำนวนเต็ม")
    if amount < 0:
        raise ValueError("amount ต้องไม่ติดลบ")
    if not 0 <= days_late <= MAX_DAYS_LATE:
        raise ValueError(f"days_late ต้องอยู่ระหว่าง 0–{MAX_DAYS_LATE}")

    if days_late <= GRACE_DAYS:
        return 0

    # ค่าปรับดิบ = amount * 0.75% * days_late  ->  amount * 75 * days / 10000 (ปัดครึ่งขึ้น)
    raw_fee = (amount * DAILY_RATE_BP * days_late + 5000) // 10000

    # เพดาน = 15% ของ amount (ปัดลงเป็นสตางค์)
    cap = amount * CAP_PERCENT // 100

    return min(raw_fee, cap)


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        print(late_fee(int(sys.argv[1]), int(sys.argv[2])))
    else:
        print("usage: python solve.py <amount_satang> <days_late>")
