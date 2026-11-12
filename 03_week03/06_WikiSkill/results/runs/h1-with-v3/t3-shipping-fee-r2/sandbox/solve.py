import json
import sys

MAX_WEIGHT_G = 30000
BASE_SATANG_UP_TO_1000G = 4000
BASE_SATANG_UP_TO_5000G = 8000
EXTRA_SATANG_PER_1000G = 1500  # 15 บาทต่อกิโลกรัม
LONG_DISTANCE_KM = 100


def _require_int(name, value, low, high=None):
    if type(value) is not int:
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if value < low or (high is not None and value > high):
        raise ValueError(f"{name} อยู่นอกช่วงที่กำหนด")
    return value


def shipping_fee(weight_g, distance_km, express):
    weight_g = _require_int("weight_g", weight_g, 1, MAX_WEIGHT_G)
    distance_km = _require_int("distance_km", distance_km, 0)
    if type(express) is not bool:
        raise ValueError("express ต้องเป็น true หรือ false")

    if weight_g <= 1000:
        base = BASE_SATANG_UP_TO_1000G
    else:
        base = BASE_SATANG_UP_TO_5000G
    extra_g = max(0, weight_g - 5000)

    # เก็บทุกขั้นเป็นเศษส่วน num/den แล้วปัดครั้งเดียวตอนท้าย (ครึ่งปัดขึ้น)
    num = base * 1000 + extra_g * EXTRA_SATANG_PER_1000G
    den = 1000
    if distance_km > LONG_DISTANCE_KM:
        num *= 120
        den *= 100
    if express:
        num *= 150
        den *= 100
    return (2 * num + den) // (2 * den)


def _fail(message):
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    return 2


def main():
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except ValueError:
        return _fail("input ไม่ใช่ JSON ที่ถูกต้อง")
    if not isinstance(data, dict):
        return _fail("input ต้องเป็น JSON object")
    try:
        result = shipping_fee(data["weight_g"], data["distance_km"], data["express"])
    except KeyError as exc:
        return _fail(f"ขาด key: {exc.args[0]}")
    except ValueError as exc:
        return _fail(str(exc))
    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
