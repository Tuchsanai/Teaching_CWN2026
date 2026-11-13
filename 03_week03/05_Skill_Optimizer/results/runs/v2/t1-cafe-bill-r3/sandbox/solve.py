import json
import sys


def _check_int(v, name, minimum):
    if type(v) is not int:
        raise ValueError(name + " must be an int")
    if v < minimum:
        raise ValueError(name + " must be >= " + str(minimum))


def cafe_bill(items, member):
    if type(items) is not list or len(items) == 0:
        raise ValueError("items must be a non-empty list")
    if type(member) is not bool:
        raise ValueError("member must be a bool")
    total = 0
    for it in items:
        if type(it) is not dict or "price" not in it or "qty" not in it:
            raise ValueError("each item must be a dict with price and qty")
        _check_int(it["price"], "price", 0)
        _check_int(it["qty"], "qty", 1)
        total += it["price"] * it["qty"]

    num, den = total, 1
    if total >= 50000:  # 500 baht = 50000 satang
        num, den = num * 95, den * 100
    if member:
        num, den = num * 90, den * 100
    num, den = num * 107, den * 100  # VAT 7%
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("input must be a JSON object")
        if "items" not in data or "member" not in data:
            raise ValueError("missing key")
        result = cafe_bill(data["items"], data["member"])
    except (ValueError, RecursionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    print(json.dumps({"ok": True, "result": result}))


if __name__ == "__main__":
    main()
