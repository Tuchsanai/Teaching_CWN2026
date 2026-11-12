# อัตราเงินคืนเป็นหน่วย 1/1000 ของยอดซื้อ (1.5% = 15/1000)
_RATES = {"silver": 15, "gold": 25, "platinum": 40}
_MIN_AMOUNT = 10_000   # 100 บาท (สตางค์)
_CAP = 20_000          # 200 บาท (สตางค์)


def cashback(amount, tier, birthday):
    if tier not in _RATES:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < _MIN_AMOUNT:
        return 0
    rate = _RATES[tier] * (2 if birthday else 1)
    # คำนวณด้วยจำนวนเต็ม ปัดเศษลง (ไม่มีปัญหา float)
    return min(int(amount) * rate // 1000, _CAP)
