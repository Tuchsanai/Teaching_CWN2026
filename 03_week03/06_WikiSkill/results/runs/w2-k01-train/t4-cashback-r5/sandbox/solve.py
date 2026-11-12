# อัตราเงินคืนเป็นหน่วย basis point (1% = 100) เพื่อหลีกเลี่ยง float
_RATE_BP = {"silver": 150, "gold": 250, "platinum": 400}
_MIN_AMOUNT = 10_000   # 100 บาท (สตางค์)
_CAP = 20_000          # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if tier not in _RATE_BP:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < _MIN_AMOUNT:
        return 0
    value = amount * _RATE_BP[tier] * (2 if birthday else 1) // 10_000  # ปัดลงเป็นสตางค์
    return min(value, _CAP)
