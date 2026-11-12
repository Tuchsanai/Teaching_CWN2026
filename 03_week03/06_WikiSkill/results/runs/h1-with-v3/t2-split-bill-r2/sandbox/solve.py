"""หารบิลร้าน BaanKafe ทุกค่าเงินเป็นจำนวนเต็มหน่วยสตางค์"""
import json
import sys

PARAM_NAMES = ("total", "people", "tip_percent")


def _check_int(name, value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    return value


def split_bill(total, people, tip_percent):
    total = _check_int("total", total)
    people = _check_int("people", people)
    tip_percent = _check_int("tip_percent", tip_percent)

    if total < 0:
        raise ValueError("total ต้องไม่ติดลบ")
    if people < 1:
        raise ValueError("people ต้องอย่างน้อย 1")
    if not 0 <= tip_percent <= 100:
        raise ValueError("tip_percent ต้องอยู่ระหว่าง 0 ถึง 100")

    # ยอดที่ต้องหาร = total * (100 + tip_percent) เทียบกับ 100
    # ปัดครึ่งขึ้นครั้งเดียวที่ขั้นสุดท้าย (ไม่ปัดทิปแยก)
    num = total * (100 + tip_percent)
    den = 100
    amount = (2 * num + den) // (2 * den)

    base, extra = divmod(amount, people)
    return [base + 1 if i < extra else base for i in range(people)]


def _fail(message):
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    return 2


def _main():
    try:
        data = json.loads(sys.stdin.read())
    except ValueError as exc:
        return _fail(f"JSON ไม่ถูกต้อง: {exc}")

    if not isinstance(data, dict):
        return _fail("input ต้องเป็น JSON object")

    missing = [name for name in PARAM_NAMES if name not in data]
    if missing:
        return _fail(f"ขาด key: {', '.join(missing)}")

    extra = [key for key in data if key not in PARAM_NAMES]
    if extra:
        return _fail(f"key ไม่รู้จัก: {', '.join(str(k) for k in extra)}")

    try:
        result = split_bill(*(data[name] for name in PARAM_NAMES))
    except ValueError as exc:
        return _fail(str(exc))

    print(json.dumps({"ok": True, "result": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
