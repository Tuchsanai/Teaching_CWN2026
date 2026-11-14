import json
import sys


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def shipping_fee(weight_g, distance_km, express):
    """คืนค่าส่งเป็นจำนวนเต็มสตางค์"""
    if not _is_int(weight_g) or not 1 <= weight_g <= 30000:
        raise ValueError("weight_g must be int in 1..30000")
    if not _is_int(distance_km) or distance_km < 0:
        raise ValueError("distance_km must be int >= 0")
    if not isinstance(express, bool):
        raise ValueError("express must be bool")

    # หน่วย: สตางค์ x1000 (ส่วนเกิน 1 กรัม = 1500 สตางค์/1000 กรัม)
    if weight_g <= 1000:
        fee = 4000 * 1000
    elif weight_g <= 5000:
        fee = 8000 * 1000
    else:
        fee = 8000 * 1000 + (weight_g - 5000) * 1500

    # คูณด้วยเศษส่วนแท้ ๆ: +20% = 6/5, +50% = 3/2
    num = fee * (6 if distance_km > 100 else 5) * (3 if express else 2)
    den = 1000 * 5 * 2
    # ปัดครึ่งขึ้น ครั้งเดียวตอนท้าย
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        for k in ("weight_g", "distance_km", "express"):
            if k not in data:
                raise ValueError("missing key: " + k)
        result = shipping_fee(data["weight_g"], data["distance_km"], data["express"])
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
