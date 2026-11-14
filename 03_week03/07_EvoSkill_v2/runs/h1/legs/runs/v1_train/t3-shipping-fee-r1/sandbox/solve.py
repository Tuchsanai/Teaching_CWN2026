"""คิดค่าส่งเมล็ดกาแฟ BaanKafe

กติกา
1. น้ำหนัก weight_g เป็นจำนวนเต็มกรัม ช่วง 1–30,000
   - ไม่เกิน 1,000 กรัม          : 40 บาท
   - ไม่เกิน 5,000 กรัม          : 80 บาท
   - เกิน 5,000 กรัม             : 80 บาท + ส่วนที่เกิน 5,000 กรัม กิโลกรัมละ 15 บาท (คิดตามสัดส่วนกรัม)
2. ระยะทาง distance_km ตั้งแต่ 0 ขึ้นไป ถ้าเกิน 100 กม. คิดเพิ่ม 20%
3. express = True คิดเพิ่ม 50% โดยคูณต่อจากข้อ 2
4. ผลลัพธ์เป็นจำนวนเต็มสตางค์ คำนวณด้วย Fraction ตลอดทาง ปัดครึ่งขึ้นครั้งเดียวตอนท้ายสุด
"""
from fractions import Fraction
from math import floor, isfinite
import json
import sys


# ---------- ตรวจชนิด input (เข้มงวด: bool/float/str ไม่ผ่านตรวจ int) ----------

def _need_int(value, name, low=None, high=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def _need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def _need_distance(value):
    if type(value) not in (int, float):
        raise ValueError("distance_km ต้องเป็นตัวเลข")
    if type(value) is float and not isfinite(value):
        raise ValueError("distance_km ต้องเป็นจำนวนจำกัด")
    if value < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")
    return Fraction(value)  # float แปลงเป็น Fraction ได้แบบตรงตัว ไม่มีการปัด


# ---------- ตัวช่วยปัด ----------

def _half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ): 2.4 -> 2, 2.5 -> 3"""
    return floor(Fraction(x) + Fraction(1, 2))


# ---------- ฟังก์ชันหลัก ----------

def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    weight = _need_int(weight_g, "weight_g", 1, 30000)
    distance = _need_distance(distance_km)
    is_express = _need_bool(express, "express")

    # 1) ค่าส่งตามน้ำหนัก (หน่วยสตางค์ เป็น Fraction เพื่อคิดส่วนเกินตามสัดส่วนกรัม)
    if weight <= 1000:
        fee = Fraction(40 * 100)
    elif weight <= 5000:
        fee = Fraction(80 * 100)
    else:
        # ส่วนเกิน 5,000 กรัม กรัมละ 0.015 บาท = 1.5 สตางค์
        fee = Fraction(80 * 100) + Fraction((weight - 5000) * 15 * 100, 1000)

    # 2) ระยะทางเกิน 100 กม. คิดเพิ่ม 20%
    if distance > 100:
        fee *= Fraction(120, 100)

    # 3) ส่งด่วน คิดเพิ่ม 50% (คูณต่อจากข้อ 2)
    if is_express:
        fee *= Fraction(150, 100)

    # ปัดครั้งเดียวตอนท้ายสุด
    return _half_up(fee)


# ---------- CLI: รับ JSON object ทาง stdin ----------

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
