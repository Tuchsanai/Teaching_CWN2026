import json
import sys


def _is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def refund(paid, used_percent, restock):
    if not _is_int(paid) or paid < 0:
        raise ValueError("paid must be an int >= 0")
    if not _is_int(used_percent) or used_percent < 0 or used_percent > 100:
        raise ValueError("used_percent must be an int between 0 and 100")
    if not isinstance(restock, bool):
        raise ValueError("restock must be a bool")
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
        if not isinstance(data, dict):
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
