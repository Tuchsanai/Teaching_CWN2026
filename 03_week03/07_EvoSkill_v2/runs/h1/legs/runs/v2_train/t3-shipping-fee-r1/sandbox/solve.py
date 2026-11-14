"""คิดค่าส่งเมล็ดกาแฟ BaanKafe

กติกา (หน่วยภายในเป็นสตางค์ทั้งหมด):
1. ฐานตามน้ำหนัก (weight_g, 1–30,000 กรัม)
   - ไม่เกิน 1,000 กรัม          -> 40 บาท
   - ไม่เกิน 5,000 กรัม          -> 80 บาท
   - เกิน 5,000 กรัม             -> 80 บาท + ส่วนที่เกิน 5,000 กรัม คิดตามสัดส่วน กิโลกรัมละ 15 บาท
2. ระยะทางเกิน 100 กม. คิดเพิ่ม 20% (คูณ 1.2) จากยอดข้อ 1
3. ส่งด่วน (express=True) คิดเพิ่ม 50% (คูณ 1.5) ต่อจากยอดข้อ 2
4. ปัดครึ่งขึ้น เป็นจำนวนเต็มสตางค์ ปัดครั้งเดียวตอนท้ายสุด

การคำนวณใช้ Fraction ตลอดทาง ไม่ใช้ float
"""
import json
import sys
from fractions import Fraction
from math import floor


# ---------- ตัวตรวจ input ----------

def need_int(value, name, low=None, high=None):
    # bool และ float ไม่ถือเป็น int ในที่นี้
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def need_bool(value, name):
    if type(value) is not bool:
        raise ValueError(f"{name} ต้องเป็น True หรือ False")
    return value


def half_up(x):
    """ปัดครึ่งขึ้นเป็นจำนวนเต็ม (x ไม่ติดลบ)"""
    return floor(Fraction(x) + Fraction(1, 2))


# ---------- ฟังก์ชันหลัก ----------

def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    weight_g = need_int(weight_g, "weight_g", 1, 30000)
    distance_km = need_int(distance_km, "distance_km", 0)
    express = need_bool(express, "express")

    # ข้อ 1: ฐานตามน้ำหนัก (สตางค์)
    if weight_g <= 1000:
        fee = Fraction(40 * 100)
    elif weight_g <= 5000:
        fee = Fraction(80 * 100)
    else:
        # 15 บาท/กก. = 1500 สตางค์/กก. ; ส่วนเกินเป็นกรัม หาร 1000 เป็นกิโลกรัม
        fee = Fraction(80 * 100) + Fraction(weight_g - 5000, 1000) * 1500

    # ข้อ 2: ระยะทางเกิน 100 กม. เพิ่ม 20%
    if distance_km > 100:
        fee *= Fraction(120, 100)

    # ข้อ 3: ส่งด่วนเพิ่ม 50% ต่อจากข้อก่อน
    if express:
        fee *= Fraction(150, 100)

    # ข้อ 4: ปัดครั้งเดียวตอนท้าย
    return half_up(fee)


# ---------- CLI (stdin JSON -> stdout JSON) ----------

def main():
    try:
        raw = sys.stdin.read()
        args = json.loads(raw)
        if not isinstance(args, dict):
            raise ValueError("input ต้องเป็น JSON object")
        result = shipping_fee(**args)
    except (ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    except json.JSONDecodeError as exc:
        print(json.dumps({"ok": False, "error": f"JSON ไม่ถูกต้อง: {exc}"}, ensure_ascii=False))
        return 2
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
