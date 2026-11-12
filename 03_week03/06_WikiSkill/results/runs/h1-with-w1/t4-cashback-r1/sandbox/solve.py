import json
import sys
from fractions import Fraction

# อัตราเงินคืน (ใช้ Fraction ไม่ใช้ float)
RATES = {
    'silver': Fraction(3, 200),    # 1.5%
    'gold': Fraction(1, 40),       # 2.5%
    'platinum': Fraction(1, 25),   # 4%
}
MIN_AMOUNT = 10000        # 100 บาท (หน่วยสตางค์) ต่ำกว่านี้ไม่ได้เงินคืน
BIRTHDAY_MULTIPLIER = 2   # ซื้อในเดือนเกิด ได้ 2 เท่า
CAP = 20000               # เงินคืนสูงสุด 200 บาทต่อบิล (หน่วยสตางค์)


def _int(x, name, lo=None, hi=None):
    if isinstance(x, bool) or not isinstance(x, int):
        raise ValueError(f'{name} must be int')
    if (lo is not None and x < lo) or (hi is not None and x > hi):
        raise ValueError(f'{name} out of range')
    return x


def _bool(x, name):
    if not isinstance(x, bool):
        raise ValueError(f'{name} must be bool')
    return x


def cashback(amount, tier, birthday):
    """คืนเงินคืนสมาชิก BaanKafe เป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้น)."""
    amount = _int(amount, 'amount', lo=0)
    if not (isinstance(tier, str) and tier in RATES):
        raise ValueError('tier must be one of silver, gold, platinum')
    birthday = _bool(birthday, 'birthday')

    if amount < MIN_AMOUNT:
        return 0

    value = Fraction(amount) * RATES[tier]
    if birthday:
        value *= BIRTHDAY_MULTIPLIER
    value = min(value, CAP)  # เพดานเทียบก่อนปัด (CAP เป็นจำนวนเต็ม จึงไม่กระทบผล)

    # ปัดครึ่งขึ้นครั้งเดียวตอนท้าย
    num, den = value.numerator, value.denominator
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        result = cashback(data['amount'], data['tier'], data['birthday'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({'ok': True, 'result': result}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
