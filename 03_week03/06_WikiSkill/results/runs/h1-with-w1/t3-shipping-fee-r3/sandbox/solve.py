"""BaanKafe shipping fee calculator.

หน่วยเงินเป็นสตางค์ (จำนวนเต็ม) ปัดเศษแบบ half-up ครั้งเดียวตอนท้าย

กติกา:
- น้ำหนัก 1–30,000 กรัม
  - ไม่เกิน 1,000 g  -> 40 บาท
  - ไม่เกิน 5,000 g  -> 80 บาท
  - เกิน 5,000 g     -> 80 บาท + (ส่วนที่เกิน 5,000 g) * 15 บาท/กก. (คิดตามสัดส่วนกรัม)
- ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
- ส่งด่วน (express=True) คิดเพิ่ม 50% (คูณต่อจากข้อก่อน)
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


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (int)."""
    weight_g = _int(weight_g, 'weight_g', 1, 30000)
    distance_km = _int(distance_km, 'distance_km', 0)
    express = _bool(express, 'express')

    # ฐานราคาตามน้ำหนัก (สตางค์, เก็บเป็น Fraction เพื่อไม่ให้มีค่าคลาดเคลื่อน)
    if weight_g <= 1000:
        base = Fraction(4000)
    elif weight_g <= 5000:
        base = Fraction(8000)
    else:
        # 15 บาท/กก. = 1500 สตางค์/1000 g = 3/2 สตางค์ต่อกรัม
        base = Fraction(8000) + Fraction((weight_g - 5000) * 3, 2)

    # ตัวคูณ: ระยะไกลเกิน 100 กม. +20%, ส่งด่วน +50% (คูณต่อกัน)
    total = base
    if distance_km > 100:
        total *= Fraction(6, 5)
    if express:
        total *= Fraction(3, 2)

    # half-up ครั้งเดียว (ค่าไม่ติดลบ)
    return (2 * total.numerator + total.denominator) // (2 * total.denominator)


def main():
    try:
        data = json.loads(sys.stdin.read())
        result = shipping_fee(data['weight_g'], data['distance_km'], data['express'])
    except (ValueError, KeyError, TypeError) as e:
        print(json.dumps({'ok': False, 'error': str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({'ok': True, 'result': result}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
