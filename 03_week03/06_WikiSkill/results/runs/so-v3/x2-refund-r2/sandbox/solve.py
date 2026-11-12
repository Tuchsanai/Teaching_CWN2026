import json
import sys


def _check_int(value, name, low, high):
    if type(value) is not int:
        raise ValueError(name + " must be int")
    if value < low or value > high:
        raise ValueError(name + " out of range")


def refund(paid, used_percent, restock):
    _check_int(paid, "paid", 0, 10 ** 18)
    _check_int(used_percent, "used_percent", 0, 100)
    if type(restock) is not bool:
        raise ValueError("restock must be bool")
    if used_percent > 80:
        return 0
    num = paid * (100 - used_percent)
    den = 100
    if restock:
        num = num * (1000 - 125)
        den = den * 1000
    return (2 * num + den) // (2 * den)


def main():
    try:
        data = json.loads(sys.stdin.read())
        if type(data) is not dict:
            raise ValueError("input must be a JSON object")
        for key in ("paid", "used_percent", "restock"):
            if key not in data:
                raise ValueError("missing key: " + key)
        result = refund(data["paid"], data["used_percent"], data["restock"])
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2
    print(json.dumps({"ok": True, "result": result}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
