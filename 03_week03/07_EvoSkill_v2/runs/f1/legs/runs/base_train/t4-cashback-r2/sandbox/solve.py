# อัตราเงินคืนเป็นหน่วย 1/1000 (หลีกเลี่ยง float)
_RATES = {"silver": 15, "gold": 25, "platinum": 40}
_MIN_AMOUNT = 100 * 100   # 100 บาท = 10,000 สตางค์
_CAP = 200 * 100          # 200 บาท = 20,000 สตางค์


def cashback(amount, tier, birthday):
    """คืนเงินคืนเป็นจำนวนเต็มสตางค์ (ปัดเศษลง)"""
    if tier not in _RATES:
        raise ValueError(f"unknown tier: {tier!r}")
    if amount < _MIN_AMOUNT:
        return 0
    mult = 2 if birthday else 1
    result = amount * _RATES[tier] * mult // 1000
    return min(result, _CAP)
