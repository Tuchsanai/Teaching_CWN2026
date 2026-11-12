"""BaanKafe shipping fee calculator.

หน่วยเงินเป็นสตางค์ (จำนวนเต็ม) คำนวณด้วย fractions.Fraction แล้วปัดครึ่งขึ้น (half-up)
ครั้งเดียวตอนท้าย เพื่อไม่ให้เกิดความคลาดเคลื่อนจากทศนิยม
"""
import json
import sys
from fractions import Fraction


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


def _round_half_up(q):
    """ปัด Fraction ไม่ติดลบให้เป็นจำนวนเต็ม (ครึ่งขึ้น)."""
    num, den = q.numerator, q.denominator
    return (2 * num + den) // (2 * den)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นสตางค์ (จำนวนเต็ม)

    - weight_g: น้ำหนักเป็นกรัม 1–30,000
    - distance_km: ระยะทางเป็นกิโลเมตร ตั้งแต่ 0
    - express: True = ส่งด่วน
    """
    weight_g = _int(weight_g, 'weight_g', 1, 30000)
    distance_km = _int(distance_km, 'distance_km', 0)
    express = _bool(express, 'express')

    # ค่าส่งฐานเป็นสตางค์ (1 บาท = 100 สตางค์)
    if weight_g <= 1000:
        base = Fraction(40 * 100)
    elif weight_g <= 5000:
        base = Fraction(80 * 100)
    else:
        # เกิน 5,000 กรัม: 80 บาท + 15 บาทต่อกิโลกรัมของส่วนที่เกิน (คิดตามสัดส่วนกรัม)
        excess_g = weight_g - 5000
        base = Fraction(80 * 100) + Fraction(excess_g, 1000) * (15 * 100)

    fee = base

    # ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance_km > 100:
        fee *= Fraction(120, 100)

    # ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
    if express:
        fee *= Fraction(150, 100)

    return _round_half_up(fee)


def main():
    try:
        data = json.loads(sys.stdin.read())
        result = shipping_fee(data['weight_g'], data['distance_km'], data['express'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}))
        return 2
    print(json.dumps({'ok': True, 'result': result}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
