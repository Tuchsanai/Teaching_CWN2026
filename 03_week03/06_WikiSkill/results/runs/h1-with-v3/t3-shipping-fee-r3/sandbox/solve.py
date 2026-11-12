"""คิดค่าส่งเมล็ดกาแฟของร้าน BaanKafe หน่วยสตางค์ ทุกการคำนวณเป็นจำนวนเต็ม"""
import json
import sys

MAX_WEIGHT_G = 30000
LIGHT_LIMIT_G = 1000
MID_LIMIT_G = 5000
DISTANCE_LIMIT_KM = 100

LIGHT_FEE_SATANG = 4000  # 40 บาท
MID_FEE_SATANG = 8000    # 80 บาท

EXPECTED_KEYS = ("weight_g", "distance_km", "express")


def _require_int(name, value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็มเท่านั้น")


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ ปัดครึ่งขึ้นครั้งเดียวที่ขั้นสุดท้าย"""
    _require_int("weight_g", weight_g)
    _require_int("distance_km", distance_km)
    if not isinstance(express, bool):
        raise ValueError("express ต้องเป็น true หรือ false")
    if not 1 <= weight_g <= MAX_WEIGHT_G:
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1 ถึง 30000 กรัม")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ติดลบ")

    # ค่าฐานเก็บเป็นเศษส่วน num ต่อ den เพื่อไม่ปัดระหว่างทาง
    if weight_g <= LIGHT_LIMIT_G:
        num, den = LIGHT_FEE_SATANG, 1
    elif weight_g <= MID_LIMIT_G:
        num, den = MID_FEE_SATANG, 1
    else:
        # ส่วนเกินกิโลกรัมละ 15 บาท = 3 สตางค์ต่อ 2 กรัม
        num = 2 * MID_FEE_SATANG + 3 * (weight_g - MID_LIMIT_G)
        den = 2

    if distance_km > DISTANCE_LIMIT_KM:
        # เพิ่มร้อยละ 20 คือคูณ 6 แล้วเอา 5 เป็นตัวหาร
        num *= 6
        den *= 5

    if express:
        # เพิ่มร้อยละ 50 คือคูณ 3 แล้วเอา 2 เป็นตัวหาร
        num *= 3
        den *= 2

    return (2 * num + den) // (2 * den)


def _fail(message):
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    sys.exit(2)


def main():
    try:
        payload = json.loads(sys.stdin.read())
    except (ValueError, OSError, RecursionError):
        _fail("JSON ไม่ถูกต้อง")

    if not isinstance(payload, dict):
        _fail("input ต้องเป็น JSON object")
    missing = [key for key in EXPECTED_KEYS if key not in payload]
    if missing:
        _fail("ขาด key: " + ", ".join(missing))
    unknown = [key for key in payload if key not in EXPECTED_KEYS]
    if unknown:
        _fail("key ไม่รู้จัก: " + ", ".join(str(key) for key in unknown))

    try:
        result = shipping_fee(payload["weight_g"], payload["distance_km"], payload["express"])
    except ValueError as exc:
        _fail(str(exc))

    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    sys.exit(0)


if __name__ == "__main__":
    main()
