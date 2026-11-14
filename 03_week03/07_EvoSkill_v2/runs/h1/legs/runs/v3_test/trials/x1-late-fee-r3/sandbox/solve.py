from fractions import Fraction

GRACE_DAYS = 3                 # ช้าไม่เกินนี้ไม่คิดค่าปรับ
DAILY_RATE = Fraction(75, 10000)  # 0.75% ต่อวัน
MAX_RATE = Fraction(15, 100)      # เพดาน 15% ของยอดค้างชำระ
MAX_DAYS = 365


def _require_int(value, name, low, high):
    # ปฏิเสธ bool, float, str, None และค่านอกช่วง (ไม่แปลงค่าเงียบ ๆ)
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if value < low or value > high:
        raise ValueError(f"{name} ต้องอยู่ระหว่าง {low} ถึง {high}")
    return value


def _half_up(x):
    """ปัดครึ่งขึ้นเป็น int, x ไม่ติดลบ (Fraction)"""
    return int((x * 2 + 1) // 2)


def late_fee(amount, days_late):
    """คืนค่าปรับ (สตางค์, int) สำหรับยอดค้างชำระ amount ที่ช้า days_late วัน"""
    amount = _require_int(amount, "amount", 0, 10**18)
    days_late = _require_int(days_late, "days_late", 0, MAX_DAYS)

    if days_late <= GRACE_DAYS:
        return 0

    # นับทุกวันที่ช้า (รวม 3 วันแรก) คูณก่อนแล้วปัดครั้งเดียว
    # ค่าปรับเป็นเงินที่ลูกค้าจ่ายให้ร้าน จึงปัดครึ่งขึ้น
    exact_fee = Fraction(amount) * DAILY_RATE * days_late
    fee = _half_up(exact_fee)

    # เพดาน 15% ของยอดค้างชำระ ปัดลงเพื่อไม่ให้เกินเพดานหลังปัด
    cap = int(Fraction(amount) * MAX_RATE // 1)
    return min(fee, cap)


if __name__ == "__main__":
    print(late_fee(100_000, 3))   # 0
    print(late_fee(100_000, 4))   # 3000
    print(late_fee(100_000, 30))  # 15000 (22.5% ติดเพดาน 15%)
    print(late_fee(100_000, 365)) # 15000 (ติดเพดาน)
