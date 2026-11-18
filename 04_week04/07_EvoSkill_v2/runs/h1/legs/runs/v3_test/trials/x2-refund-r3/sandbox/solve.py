"""คิดเงินคืนของคอร์สสอนชงกาแฟ BaanKafe

refund(paid, used_percent, restock)
    paid          เงินที่ลูกค้าจ่ายมา (สตางค์, int, >= 0)
    used_percent  เรียนไปแล้วกี่เปอร์เซ็นต์ (int, 0-100)
    restock       True = หักค่าดำเนินการ 12.5% ของยอดที่จะคืน

คืนค่า int (สตางค์) คือยอดที่ต้องคืนให้ลูกค้า
"""


def _require_int(value, name, low, high=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if value < low or (high is not None and value > high):
        raise ValueError(f"{name} ต้องอยู่ในช่วง {low}" + (f"-{high}" if high is not None else " ขึ้นไป"))
    return value


def _require_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def refund(paid, used_percent, restock):
    paid = _require_int(paid, "paid", 0)
    used_percent = _require_int(used_percent, "used_percent", 0, 100)
    restock = _require_bool(restock, "restock")

    # เรียนเกิน 80% ไม่คืนเงิน
    if used_percent > 80:
        return 0

    # ยอดคืนก่อนหักค่าดำเนินการ = paid * (100 - used) / 100
    # หักค่าดำเนินการ 12.5% (เหลือ 87.5% = 7/8) ถ้า restock = True
    # คูณทุกตัวก่อน แล้วปัดลงครั้งเดียว (เงินออกจากร้านให้ลูกค้า จึงปัดลงไม่ให้จ่ายเกินสิทธิ์)
    # ตัวส่วน 800 = 100 * 8 ทำให้คำนวณเป็นจำนวนเต็มล้วน
    unused = 100 - used_percent
    factor = 7 if restock else 8
    return (paid * unused * factor) // 800


if __name__ == "__main__":
    print(refund(10_000, 0, False))   # 10000
    print(refund(10_000, 0, True))    # 8750
    print(refund(10_000, 80, False))  # 2000
    print(refund(10_000, 81, False))  # 0
