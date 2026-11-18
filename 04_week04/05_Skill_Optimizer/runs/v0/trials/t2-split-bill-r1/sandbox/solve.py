import json
import sys


def _check_int(name, value, lo, hi=None):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} ต้องเป็นจำนวนเต็ม")
    if value < lo or (hi is not None and value > hi):
        rng = f"ตั้งแต่ {lo}" if hi is None else f"{lo}–{hi}"
        raise ValueError(f"{name} ต้องอยู่ในช่วง {rng}")


def split_bill(total, people, tip_percent):
    """หารบิล (หน่วยสตางค์) คืน list ยอดที่แต่ละคนจ่าย"""
    _check_int("total", total, 0)
    _check_int("people", people, 1)
    _check_int("tip_percent", tip_percent, 0, 100)

    # ทิป = total * tip_percent / 100 ปัดครึ่งขึ้น (จำนวนเต็มล้วน)
    tip = (total * tip_percent + 50) // 100
    grand = total + tip
    base, extra = divmod(grand, people)
    return [base + 1 if i < extra else base for i in range(people)]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        raw = argv[0] if argv else sys.stdin.read()
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("input ต้องเป็น JSON object")
        missing = [k for k in ("total", "people", "tip_percent") if k not in data]
        if missing:
            raise ValueError("ขาดฟิลด์: " + ", ".join(missing))
        result = split_bill(data["total"], data["people"], data["tip_percent"])
    except (ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
