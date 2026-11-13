# นโยบายปัดเศษ r2: ปัดครึ่งขึ้นเป็นสตางค์เต็มทุกครั้งที่ขั้นตอนให้ผลเป็นเงินใหม่
_RATES = {"silver": (15, 1000), "gold": (25, 1000), "platinum": (4, 100)}
_MIN_AMOUNT = 10000  # 100 บาท
_CAP = 20000         # 200 บาท


def _div_half_up(n, d):
    return (2 * n + d) // (2 * d)


def cashback(amount, tier, birthday):
    if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
        raise ValueError("amount must be an int >= 0")
    if not isinstance(tier, str) or tier not in _RATES:
        raise ValueError("invalid tier")
    if not isinstance(birthday, bool):
        raise ValueError("birthday must be bool")
    if amount < _MIN_AMOUNT:
        return 0
    num, den = _RATES[tier]
    result = _div_half_up(amount * num, den)  # เงินคืนพื้นฐาน ปัดเป็นสตางค์
    if birthday:
        result *= 2
    return min(result, _CAP)
