"""BaanKafe cashback calculator.

หน่วยทั้งหมดเป็นสตางค์ (1 บาท = 100 สตางค์) และคำนวณด้วยจำนวนเต็มล้วน
ไม่ใช้ float เพื่อกันค่าคลาดเคลื่อน

ลำดับการคิด:
1. ยอดต่ำกว่า 100 บาท (10,000 สตางค์) -> เงินคืน 0
2. เงินคืนฐาน = ยอด x อัตรา tier (ปัดลงเป็นสตางค์ทีเดียวที่ขั้นสุดท้าย)
3. ถ้าเป็นเดือนเกิด -> คูณ 2 (ก่อนปัด)
4. ปัดลงเป็นสตางค์ครั้งเดียวที่ขั้นสุดท้าย
5. ตัดเพดาน 200 บาท (20,000 สตางค์) ต่อบิล

การปัดเศษ: ปัดลง (ตัดเศษสตางค์ทิ้ง) ตามค่าเริ่มต้นของร้าน
"""

# อัตราเงินคืนเป็น basis point (1 bp = 0.01%) เพื่อให้เป็นจำนวนเต็มล้วน
# silver 1.5% = 150 bp, gold 2.5% = 250 bp, platinum 4% = 400 bp
_RATE_BP = {
    "silver": 150,
    "gold": 250,
    "platinum": 400,
}

_MIN_AMOUNT = 10_000       # 100 บาท ในหน่วยสตางค์
_MAX_CASHBACK = 20_000     # 200 บาท ในหน่วยสตางค์
_BP_DENOM = 10_000         # 100% = 10,000 bp


def cashback(amount, tier, birthday):
    """คืนค่าเงินคืนเป็นจำนวนเต็มสตางค์

    amount   : ยอดซื้อ หน่วยสตางค์ (int, >= 0)
    tier     : "silver" | "gold" | "platinum"
    birthday : True ถ้าซื้อในเดือนเกิด (ได้เงินคืน 2 เท่า)
    """
    if isinstance(amount, bool) or not isinstance(amount, int):
        raise TypeError("amount ต้องเป็นจำนวนเต็มสตางค์")
    if amount < 0:
        raise ValueError("amount ต้องไม่ต่ำกว่า 0")
    if tier not in _RATE_BP:
        raise ValueError(f"tier ไม่ถูกต้อง: {tier!r} (ต้องเป็น silver, gold หรือ platinum)")

    # ขั้นที่ 1: ยอดต่ำกว่า 100 บาท ไม่ได้เงินคืน
    if amount < _MIN_AMOUNT:
        return 0

    # ขั้นที่ 2: เดือนเกิดได้ 2 เท่า (คูณกับค่าที่ยังไม่ปัด)
    multiplier = 2 if birthday else 1

    # ขั้นที่ 3: ปัดลงเป็นสตางค์ครั้งเดียวที่ขั้นสุดท้ายของการคำนวณ
    cb = amount * _RATE_BP[tier] * multiplier // _BP_DENOM

    # ขั้นที่ 4: เพดานต่อบิล 200 บาท
    return min(cb, _MAX_CASHBACK)
