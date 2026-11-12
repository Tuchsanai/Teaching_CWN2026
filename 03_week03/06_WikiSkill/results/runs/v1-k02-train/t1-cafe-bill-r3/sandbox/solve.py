import json, sys


def _int(name, v, lo=None, hi=None):
    if type(v) is not int:
        raise ValueError(f"{name} must be int")
    if (lo is not None and v < lo) or (hi is not None and v > hi):
        raise ValueError(f"{name} out of range")
    return v


def cafe_bill(items, member):
    if type(items) is not list:
        raise ValueError("items must be list")
    if type(member) is not bool:
        raise ValueError("member must be bool")
    total = 0
    for it in items:
        if type(it) is not dict:
            raise ValueError("item must be dict")
        if "price" not in it or "qty" not in it:
            raise ValueError("item missing key")
        price = _int("price", it["price"], 0)
        qty = _int("qty", it["qty"], 1)
        total += price * qty

    n, d = total, 1
    if total >= 50000:  # 500 baht
        n *= 95
        d *= 100
    if member:
        n *= 90
        d *= 100
    n *= 107
    d *= 100
    return (2 * n + d) // (2 * d)  # half-up, rounded once


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
