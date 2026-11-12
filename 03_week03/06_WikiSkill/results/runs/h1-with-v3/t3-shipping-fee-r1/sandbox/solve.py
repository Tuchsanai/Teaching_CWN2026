import json
import sys

PARAMS = ("weight_g", "distance_km", "express")


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์ (ปัดครึ่งขึ้นครั้งเดียวที่ขั้นสุดท้าย)"""
    if type(weight_g) is not int:
        raise ValueError("weight_g ต้องเป็นจำนวนเต็ม")
    if not 1 <= weight_g <= 30000:
        raise ValueError("weight_g ต้องอยู่ระหว่าง 1 ถึง 30000 กรัม")
    if type(distance_km) is not int:
        raise ValueError("distance_km ต้องเป็นจำนวนเต็ม")
    if distance_km < 0:
        raise ValueError("distance_km ต้องไม่ต่ำกว่า 0")
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น true หรือ false")

    # ค่าส่งเก็บเป็นเศษ num และตัวส่วน den (หน่วยสตางค์) ยังไม่ปัดเศษ
    if weight_g <= 1000:
        num, den = 4000, 1  # 40 บาท
    elif weight_g <= 5000:
        num, den = 8000, 1  # 80 บาท
    else:
        # 80 บาท + ส่วนเกิน 5,000 กรัม คิด 15 บาทต่อกิโลกรัม (= 1500 สตางค์ ต่อ 1000 กรัม)
        num = 8000 * 1000 + (weight_g - 5000) * 1500
        den = 1000

    if distance_km > 100:  # เพิ่ม 20%
        num *= 120
        den *= 100

    if express:  # เพิ่ม 50%
        num *= 3
        den *= 2

    # ปัดครึ่งขึ้น (half-up) ครั้งเดียว
    return (2 * num + den) // (2 * den)


def _emit(obj, code):
    sys.stdout.write(json.dumps(obj) + "\n")
    return code


def _fail(message):
    return _emit({"ok": False, "error": message}, 2)


def main():
    try:
        data = json.loads(sys.stdin.read())
    except ValueError as exc:
        return _fail(f"JSON ไม่ถูกต้อง: {exc}")

    if not isinstance(data, dict):
        return _fail("input ต้องเป็น JSON object")

    missing = [key for key in PARAMS if key not in data]
    if missing:
        return _fail("ขาด key: " + ", ".join(missing))

    try:
        result = shipping_fee(**{key: data[key] for key in PARAMS})
    except ValueError as exc:
        return _fail(str(exc))

    return _emit({"ok": True, "result": result}, 0)


if __name__ == "__main__":
    sys.exit(main())
