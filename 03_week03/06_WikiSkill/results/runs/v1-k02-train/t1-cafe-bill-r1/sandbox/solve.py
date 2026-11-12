import json, sys


def _int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def cafe_bill(items, member):
    if type(items) is not list or not items:
        raise ValueError("items must be a non-empty list")
    if type(member) is not bool:
        raise ValueError("member must be bool")
    subtotal = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("invalid item")
        subtotal += _int("price", it["price"], 0) * _int("qty", it["qty"], 1)

    n, d = subtotal, 1
    if subtotal >= 50000:  # 500 baht
        n, d = n * 95, d * 100
    if member:
        n, d = n * 90, d * 100
    n, d = n * 107, d * 100  # VAT last
    return (2 * n + d) // (2 * d)  # half-up, single rounding


def _main():
    try:
        data = json.loads(sys.stdin.read())
        result = cafe_bill(**data)
    except (ValueError, TypeError, KeyError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
