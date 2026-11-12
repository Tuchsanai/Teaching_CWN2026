import json
import sys


def _round_div(num, den):
    """จำนวนเต็ม num/den ปัดครึ่งขึ้น (num >= 0)"""
    return (num * 2 + den) // (den * 2)


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def cafe_bill(items, member):
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if not isinstance(member, bool):
        raise ValueError("member must be a bool")
    total = 0
    for i, it in enumerate(items):
        if not isinstance(it, dict) or "price" not in it or "qty" not in it:
            raise ValueError(f"items[{i}] must be a dict with price and qty")
        p, q = it["price"], it["qty"]
        if not _is_int(p) or p < 0:
            raise ValueError(f"items[{i}].price must be a non-negative integer (satang)")
        if not _is_int(q) or q < 1:
            raise ValueError(f"items[{i}].qty must be an integer >= 1")
        total += p * q

    if total >= 50000:  # 500 บาท
        total = _round_div(total * 95, 100)
    if member:
        total = _round_div(total * 90, 100)
    return _round_div(total * 107, 100)  # VAT 7%


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = cafe_bill(data.get("items"), data.get("member", False))
        print(json.dumps({"total": result}))
    except (ValueError, json.JSONDecodeError) as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
