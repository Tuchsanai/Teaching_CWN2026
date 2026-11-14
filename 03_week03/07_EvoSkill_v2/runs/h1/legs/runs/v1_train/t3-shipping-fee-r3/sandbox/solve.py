"""คิดค่าส่งเมล็ดกาแฟ BaanKafe

กติกา (อ่านตามตัวอักษร):
1. weight_g: จำนวนเต็ม 1–30,000 กรัม
   distance_km: ตั้งแต่ 0 ขึ้นไป (รับ int หรือ Fraction)
   express: True = ส่งด่วน
2. ฐานตามน้ำหนัก
   - ไม่เกิน 1,000 กรัม           : 40 บาท
   - 1,001–5,000 กรัม             : 80 บาท
   - เกิน 5,000 กรัม              : 80 บาท + ส่วนที่เกิน 5,000 กรัม กิโลกรัมละ 15 บาท (คิดตามสัดส่วนกรัม)
3. ระยะทางเกิน 100 กม. (> 100)   : คิดเพิ่ม 20% จากยอดที่ได้
4. ส่งด่วน (express = True)     : คิดเพิ่ม 50% จากยอดที่ได้ (คูณต่อจากข้อ 3)
5. ผลลัพธ์เป็นจำนวนเต็มสตางค์ คำนวณทั้งหมดด้วย Fraction แล้วปัดครึ่งขึ้นครั้งเดียวตอนท้าย
"""
import json
import sys
from fractions import Fraction
from math import floor

SATANG_PER_BAHT = 100
MIN_WEIGHT_G = 1
MAX_WEIGHT_G = 30_000
TIER1_MAX_G = 1_000
TIER2_MAX_G = 5_000
BASE_TIER1 = 40 * SATANG_PER_BAHT
BASE_TIER2 = 80 * SATANG_PER_BAHT
OVER_RATE_PER_KG_BAHT = 15
LONG_DISTANCE_KM = 100
LONG_DISTANCE_MULT = Fraction(120, 100)
EXPRESS_MULT = Fraction(150, 100)


def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x >= 0)"""
    return floor(Fraction(x) + Fraction(1, 2))


def _check_weight(weight_g):
    if type(weight_g) is not int:
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม")
    if not MIN_WEIGHT_G <= weight_g <= MAX_WEIGHT_G:
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1–30,000 กรัม")
    return weight_g


def _check_distance(distance_km):
    if type(distance_km) not in (int, Fraction):
        raise ValueError("distance_km ต้องเป็นจำนวนเต็มหรือ Fraction")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")
    return distance_km


def _check_express(express):
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น True หรือ False")
    return express


def _base_satang(weight_g):
    """ค่าส่งฐานตามน้ำหนัก เป็นสตางค์ (Fraction เพราะส่วนเกินคิดเป็นทศนิยมสตางค์)"""
    if weight_g <= TIER1_MAX_G:
        return Fraction(BASE_TIER1)
    if weight_g <= TIER2_MAX_G:
        return Fraction(BASE_TIER2)
    excess_g = weight_g - TIER2_MAX_G
    # 15 บาท/กก. = 1,500 สตางค์/1,000 กรัม
    return Fraction(BASE_TIER2) + Fraction(excess_g * OVER_RATE_PER_KG_BAHT * SATANG_PER_BAHT, 1000)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    weight_g = _check_weight(weight_g)
    distance_km = _check_distance(distance_km)
    express = _check_express(express)

    fee = _base_satang(weight_g)
    if distance_km > LONG_DISTANCE_KM:
        fee *= LONG_DISTANCE_MULT
    if express:
        fee *= EXPRESS_MULT
    return _half_up(fee)


def main():
    try:
        args = json.loads(sys.stdin.read())
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = shipping_fee(**args)
    except (ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
